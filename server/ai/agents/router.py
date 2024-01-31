from langchain.chains.router import MultiPromptChain
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate

from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from prompt_toolkit import HTML, prompt

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

def create_model(llm):
    """
    Generats the router chains from the prompt infos.
    :param prompt_infos The prompt informations generated above.
    """
    destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
    destinations_str = '\n'.join(destinations)
    router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations_str)
    router_prompt = PromptTemplate(
        template=router_template,
        input_variables=['input'],
        output_parser=RouterOutputParser()
    )

    router_chain = LLMRouterChain.from_llm(llm, router_prompt)
    return router_chain
    
    