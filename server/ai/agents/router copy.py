import json
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from prompt_toolkit import HTML, prompt
from langchain.chains.router import MultiPromptChain
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks import StdOutCallbackHandler
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser

from .base import AgentBase

class CallBackHandler(StdOutCallbackHandler):
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], *, run_id: UUID, parent_run_id: UUID | None = None, tags: List[str] | None = None, metadata: Dict[str, Any] | None = None, **kwargs: Any) -> Any:
        print(prompts)
        return super().on_llm_start(serialized, prompts, run_id=run_id, parent_run_id=parent_run_id, tags=tags, metadata=metadata, **kwargs)



MULTI_PROMPT_ROUTER_TEMPLATE = """\
Given a raw text input to a language model select the model prompt best suited for \
the input. You will be given the names of the available prompts and a description of \
what the prompt is best suited for. You must revise the \ 
original input if it has has pronouns or other ambiguous references. You will be given the \
previous conversation history to help you clarify what the pronouns refer to. 

<< FORMATTING >>
Return a markdown code snippet with a JSON object formatted to look like:
```json
{{{{
    "destination": string \\ name of the prompt to use or "DEFAULT"
    "next_inputs": string \\ a potentially modified version of the original input
}}}}
```

REMEMBER: "destination" MUST be one of the candidate prompt names specified below OR \
it can be "DEFAULT" if the input is not well suited for any of the candidate prompts.
REMEMBER: Use the previous conversations clarify pronouns in the original input if possible.
REMEMBER: "next_inputs" can just be the original input if you don't think any \
<< CANDIDATE PROMPTS >>
{destinations}

<< Examples >>
User: How much did I spend last week?
You: {{{{"destination": "data analysis", "next_inputs": "{{{{"input": "How much did I spend last week?"}}}}"}}}}
User: Break it down into days
You: {{{{"destination": "data analysis", "next_inputs": "{{{{"input": "How much did I spend each day in the last week?"}}}}"}}}}

<< INPUT >>
{{history}}
User: {{input}}
You:

<< OUTPUT (must include ```json at the start of the response) >>
<< OUTPUT (must end with ```) >>
"""

class CustomMemory(ConversationBufferWindowMemory):
    output_key="str_dict"
    human_prefix="User"
    ai_prefix='"You"'
    def _get_input_output(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> Tuple[str, str]:
        outputs["str_dict"] = '{{{{"destination": "{dest}", "next_inputs": "{inp}"}}}}'.format(dest=outputs["destination"], inp=outputs["next_inputs"])
        return super()._get_input_output(inputs, outputs)

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        super().save_context(inputs, outputs)
        # self.chat_memory.add_message('next_inputs: {}'.format(str(outputs["next_inputs"])))


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
        'name': 'general question answering',
        'description': 'Good for general questions',
    }
]

class AgentRouter(AgentBase):
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

        self.chain = LLMRouterChain.from_llm(llm, router_prompt,
                                            memory=CustomMemory(k=5, memory_key="history"),)

    def run(self, inp, *kwargs):
        return self.chain.invoke(inp, config={"callbacks": [CallBackHandler()]})

    
def create_agent(llm, **kwargs):
    return AgentRouter(llm, **kwargs)