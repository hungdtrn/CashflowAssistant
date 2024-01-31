from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

def get_tool_info_str(tools):
    str_list = []
    for tool in tools:
        str_list.append("- {}: {}".format(tool["name"], tool["description"]))
    
    return "\n".join(str_list)

class CustomStructure(BaseModel):
    input: str = Field(description="The input question")
    output: str = Field(description="The output answer")

# Set up a parser + inject instructions into the prompt template.

def create_agent(llm, **kwargs):
    def run(inp_dict, verbose=False):
        prompt_template = """You are an AI Assistant, your task is to answer general questions of the user about the system.
        Here is the list of tools that the system have: 
        {tools}

        {input}"""

        prompt = PromptTemplate(
            input_variables=["input"], template=prompt_template
        )
        partial_prompt = prompt.partial(tools=get_tool_info_str(kwargs["tool_infos"]))


        qa = LLMChain(llm=llm, prompt=partial_prompt)

        return qa.invoke(inp_dict)["text"]

    return run