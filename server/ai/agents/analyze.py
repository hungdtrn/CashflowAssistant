from typing import List
import dotenv
from langchain_core.outputs import Generation
dotenv.load_dotenv()
import os
import openai
from langchain_community.utilities import SerpAPIWrapper
from langchain.agents import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.agents.react.agent import create_react_agent
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.chains import create_sql_query_chain
from langchain.tools import BaseTool, StructuredTool, tool
from langchain import hub
# Import things that are needed generically
from langchain.pydantic_v1 import BaseModel, Field
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.output_parsers import BaseOutputParser, StrOutputParser
import ast

from .base import SQLAgentBase

PERMISION_ERROR="No results found or you may not have the right permission for this query"
def format_output(text: str) -> str:
    """Returns the python object from the text."""
    out_list = ast.literal_eval(text)
    out_list = [x[0] for x in out_list]
    if len(out_list) == 1:
        out_list = out_list[0]
        
    if out_list == "None" or out_list == 0 or out_list is None:
        return PERMISION_ERROR

    return out_list

@tool(return_direct=True)
def repeat(string: str) -> str:
    """Return the input string"""
    return string

def create_agent_pandas(llm, **kwargs):
    def prepare_input(inp_dict):
        return inp_dict
    data = kwargs["df"]
    pandas_agent = create_pandas_dataframe_agent(
        llm,
        data,
        verbose=True,
        handle_parsing_errors=True,
        extra_tools=[repeat],
        # agent_type=AgentType.OPENAI_FUNCTIONS,
    )
    pandas_agent.handle_parsing_errors=True
    return pandas_agent

def check_question_validity(question: str) -> bool:
    keywords = ["drop", "update", "insert", "create", "delete"]
    for keyword in keywords:
        if keyword in question:
            return False
        
    return True

def check_query_validity(query: str, userID) -> bool:
    # Count how many times Client_ID is used
    if query.count(f"Client_ID") > 1:
        return False
    
    # Get the value compared with Client_ID using regex
    import re
    match = re.search(r'"*Client_ID"*\s*=\s*(\S+)', query)
    print(match)
    if match:
        value = int(match.group(1))

        if value != userID:
            return False
    else:
        return False
    
    return True


class SQLAgentAnalyze(SQLAgentBase):
    def __init__(self, llm, userID, **kwargs) -> None:
        super().__init__(llm, userID, **kwargs)

def create_agent_sql(llm, **kwargs):
    analyzer = SQLAgentAnalyze(llm, **kwargs)
    def run(inp_dict, verbose=False):
        return analyzer.run(inp_dict, verbose=verbose)
    
    return run