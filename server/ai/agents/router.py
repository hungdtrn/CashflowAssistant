import json
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from prompt_toolkit import HTML, prompt
from langchain.chains.router import MultiPromptChain
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory, ConversationBufferMemory
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks import StdOutCallbackHandler
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE

from langchain.tools import StructuredTool
# Import things that are needed generically
from langchain.pydantic_v1 import BaseModel, Field
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent

from .base import AgentBase

class CallBackHandler(StdOutCallbackHandler):
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], *, run_id: UUID, parent_run_id: UUID | None = None, tags: List[str] | None = None, metadata: Dict[str, Any] | None = None, **kwargs: Any) -> Any:
        print(prompts)
        return super().on_llm_start(serialized, prompts, run_id=run_id, parent_run_id=parent_run_id, tags=tags, metadata=metadata, **kwargs)

prompt_infos = [
    {
        'name': 'data analysis',
        'description': 'Good for questions about the data of the client',
    },
    {
        'name': 'future prediction',
        'description': 'Good for questions about future prediction',
    },
    {
        'name': 'general chat',
        'description': 'Good for general chat and questions',
    }
]


class RouterSchema(BaseModel):
    query: str = Field(description="The clarified query of the human. It must not contain pronouns")

def router_fn(name):
    def run(query):
        return json.dumps({"destination": name, "next_inputs": query})
    return run

class AgentRouter(AgentBase):
    PREFIX = """You are an AI Router. Your task is to clarify the questions and route them to the best agent for answering. Make sure to clarify the query as much as possible. You have access to the following tools:"""

    SUFFIX = """ Examples:
Question: How much did I spend last week?
Thought: How much did I spend last week?
Action: data analysis
Action Input: The last week spending of the user

Question: What can you help me with?
Thought: The user want to know about the capabilities of the system. I should forward the question to the QA tool.
Action: general chat
Action Input: What can you help me with?

Begin!

{chat_history}
Question: {input}
{agent_scratchpad}"""

    def __init__(self, llm, **kwargs) -> None:
        super().__init__()

        destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
        destinations_str = '\n'.join(destinations)
        router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations_str)
        router_prompt = PromptTemplate(
            template=router_template,
            input_variables=['input', 'history'],
            output_parser=RouterOutputParser()
        )

        router_chain = LLMRouterChain.from_llm(llm, router_prompt)
        tools = []
        for infs in prompt_infos:
            tool = StructuredTool.from_function(router_fn(infs["name"]),
                                                name=infs["name"],
                                                description=infs["description"],
                                                args_schema=RouterSchema,
                                                return_direct=True)
            
            tools.append(tool)

        agent_prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=self.PREFIX,
            suffix=self.SUFFIX,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )
        # memory = ConversationBufferMemory(memory_key="chat_history")
        memory = ConversationBufferWindowMemory(memory_key="chat_history", k=10)

        llm_chain = LLMChain(llm=llm, prompt=agent_prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
        self.agent = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)

    def format_output(self, text: str) -> dict:
        return json.loads(text)


    def run(self, inp, *kwargs):
        out = self.agent.invoke(inp, config={"callbacks": [CallBackHandler()]})
        return self.format_output(out["output"])

    
def create_agent(llm, **kwargs):
    return AgentRouter(llm, **kwargs)