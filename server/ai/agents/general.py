from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_core.pydantic_v1 import BaseModel, Field
from .base import AgentBase

def get_tool_info_str(tools):
    str_list = []
    for tool in tools:
        str_list.append("- {}: {}".format(tool["name"], tool["description"]))
    
    return "\n".join(str_list)

class CustomStructure(BaseModel):
    input: str = Field(description="The input question")
    output: str = Field(description="The output answer")

# Set up a parser + inject instructions into the prompt template.

class GeneralAgent(AgentBase):
    def __init__(self, llm, **kwargs) -> None:
        super().__init__()

        prompt_template = """You are an AI Assistant. Your task is to answer general questions from the user about the system. The system is built to provide insights and information about the user's cash flow. The system contains tools that the user can use to gain insight into their cash flow. The system has access to the user's cash flow data. Below is the list of tools available in the system: 
        {tools}

        {input}"""

        prompt = PromptTemplate(
            input_variables=["input"], template=prompt_template
        )
        partial_prompt = prompt.partial(tools=get_tool_info_str(kwargs["tool_infos"]))


        self.chain = LLMChain(llm=llm, prompt=partial_prompt)

    def run(self, question, **kwargs):
        return self.chain.invoke(question,)["text"]

def create_agent(llm, **kwargs):
    return GeneralAgent(llm, **kwargs)