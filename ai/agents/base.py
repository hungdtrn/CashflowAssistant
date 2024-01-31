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

class SQLAgentBase:
    PROMPT_SUFFIX = """Only use the following tables:
{table_info}

Question: {input}"""

    PROMPT_PREFIX = """You are a SQLite expert. Given an input question, first create a syntactically correct SQLite query to run, then look at the results of the query and return the answer to the input question.
Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per SQLite. You can order the results to return the most informative data in the database. 
Unless the user specifies by the users, return the SUM of the values in the column using the SUM clause.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
You must include the Client_ID in the query. The Client_ID is a unique identifier for each user in the database. It is set to {userID} for the current user.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use date('now') function to get the current date, if the question involves "today".

Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here"""

    EXAMPLES = [{
            "input": "How many stores do I have?",
            "query": "SELECT COUNT(DISTINCT 'Store_ID') FROM data WHERE AND Client_ID = {userID}"
        }]

    EXAMPLE_PROMPT = "User input: {input}\nSQL query: {query}"
    PERMISION_ERROR="No results found or you may not have the right permission for this query"

    def __init__(self, llm, userID, **kwargs) -> None:
        self.userID = userID
        self.db = kwargs["db"]

        prompt = self._prepare_prompt()
        self.sql_agent = create_sql_query_chain(llm, db=self.db, prompt=prompt)

    def _prepare_prompt(self):
        def _format(x):
            for k in x.keys():
                x[k] = x[k].format(userID=self.userID)

            return x
        examples = [_format(x) for x in self.EXAMPLES]

        example_prompt = PromptTemplate.from_template(self.EXAMPLE_PROMPT)
        prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix= self.PROMPT_PREFIX,
            suffix=self.PROMPT_SUFFIX,
            input_variables=["input", "top_k", "table_info"],
        )
        prompt = prompt.partial(userID=self.userID)
        return prompt


    def check_question_validity(self, question):
        # check if the question contains sql injection
        keywords = ["drop", "update", "insert", "create", "delete"]
        for keyword in keywords:
            if keyword in question:
                return False
            
        return True

    def check_query_validity(self, query: str, userID) -> bool:
        # Count how many times Client_ID is used
        if query.count(f"Client_ID") > 1:
            return False
        
        # Get the value compared with Client_ID using regex
        import re
        match = re.search(r'"*Client_ID"*\s*=\s*(\S+)', query)

        if match:
            value = match.group(1)
            value = value.replace("Client_ID =", "")
            value = int(value)

            if value != int(userID):
                return False
        else:
            return False
        
        return True
    
    def format_output(self, text: str):
        """Returns the python object from the text."""
        if not text or text is None:
            return self.PERMISION_ERROR
        
        out_list = ast.literal_eval(text)

        if len(out_list) == 1:
            out_list = out_list[0]
            
        if out_list == "None" or out_list == 0 or out_list is None:
            return self.PERMISION_ERROR

        return out_list
    
    def run(self, inp_dict, verbose=False):
        question = inp_dict["input"]

        # check if the question contains sql injection
        if not self.check_question_validity(question):
            return self.PERMISION_ERROR

        # run the sql agent
        sql_query = self.sql_agent.invoke({
            "question": inp_dict["input"]
        })

        # check if the query is valid
        if not self.check_query_validity(sql_query, self.userID):
            return self.PERMISION_ERROR

        if verbose:
            print(sql_query)

        return self.format_output(self.db.run(sql_query))