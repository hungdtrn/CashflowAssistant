import json
import os
from typing import Any, Dict, List
from uuid import UUID
import dotenv

dotenv.load_dotenv()

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
        query = query.split("Question:")[0]
        return json.dumps({"destination": name, "next_inputs": query})
    return run

class AgentRouter(AgentBase):
    PREFIX = """You are an AI Router. Your task is to clarify the questions and route them to the best agent for answering. Make sure to clarify the query as much as possible. You have access to the following tools:"""

    SUFFIX = """ Examples:
Question: How much did I spend last week?
Thought: The user wants to know about their spending for last week.
Action: data analysis
Action Input: The last week spending of the user

Question: What can you help me with?
Thought: The user want to know about the capabilities of the system. I should forward the question to the QA tool.
Action: general chat
Action Input: What can you help me with?

Question: Hi!
Thought: The user is greeting. I should forward it to the QA tool.
Action: general chat
Action Input: Hi!

Begin!

{chat_history}
Question: {input}
{agent_scratchpad}"""

    FORMAT_INSTRUCTIONS = """Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do. If there are pronouns in the original input, you should think what the pronouns refer to and clarify them. 
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question"""


    def __init__(self, llm, **kwargs) -> None:
        super().__init__()

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
            format_instructions=self.FORMAT_INSTRUCTIONS,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )
        # memory = ConversationBufferMemory(memory_key="chat_history")
        memory = ConversationBufferWindowMemory(memory_key="chat_history", k=10)

        llm_chain = LLMChain(llm=llm, prompt=agent_prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=os.environ.get("VERBOSE", False))
        self.agent = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=os.environ.get("VERBOSE", False), memory=memory,
                                                        stop=["Question:"])
        self.agent.handle_parsing_errors=True

    def format_output(self, text: str) -> dict:
        return json.loads(text)


    def run(self, inp, *kwargs):
        # out = self.agent.invoke(inp, config={"callbacks": [CallBackHandler()]})
        out = self.agent.invoke(inp)

        return self.format_output(out["output"])

    
def create_agent(llm, **kwargs):
    return AgentRouter(llm, **kwargs)