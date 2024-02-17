import re
from .base import SQLAgentBase
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from .utils import CallBackHandler
import pandas as pd

class SQLDataQuery(SQLAgentBase):
    PROMPT_PREFIX = """You are a SQLite expert {top_k}. Given an input predictive question, you need to create a syntactically correct SQLite query to run to get the appropriate data for visualization based on an input question.

The data contain the daily cashflow of multiple stores and companies. Unless specified in the questions, you must group the data by date. Avoid using the LIMIT clause. 

Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
You must include the Client_ID in the query. The Client_ID is a unique identifier for each user in the database. It is set to {userID} for the current user.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.

Use the following format:

Question: The prediction task here
Thought: How to query the data for visualization
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here
"""
    EXAMPLES = [{
        "input": "Last week's income data for the user",
        "query": 'SELECT "Date", SUM("Revenue") as  "Total Revenue" FROM data WHERE "Date" >= date("now", "-7 days") AND "Date" <= date("now") AND Client_ID = {userID} GROUP BY "Date"' 
    },  {
        "input": "The spending at Coles last two week",
        "query": 'SELECT "Date", SUM("Expenses") as "Total Expenses" FROM data WHERE "Date" >= date("now", "-14 days") AND "Date" <= date("now") AND "Company" = "Coles" AND "Client_ID" = {userID} GROUP BY "Date"',
    },]

    def format_output(self, out):
        out = super().format_output(out)
        if isinstance(out, list):
            pd_out = pd.DataFrame(out)
        elif isinstance(out, dict):
            pd_out = pd.DataFrame.from_dict(out, orient="index")
        elif isinstance(out, str):
            return out, out

        # check each col, round if col is number
        for col in pd_out.columns:
            if pd_out[col].dtype == "float64":
                pd_out[col] = pd_out[col].round(0)

        return out, pd_out

class PandasAgent:
    PROMPT_PREFIX = """You are a Python Visualization Exepert. You are working with a pandas dataframe in Python. The name of the dataframe is `df`. Given the input question and the data, you need to generate python code that best visualize the data. You must use plotly as the visualization package. Do not load the data again.""" 
    
    SUFFIX_WITH_DF = """ This is the result of `print(df.head())`: 
{df_head}

Question: {input}"""

    FORMAT_INSTRUCTIONS = """Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do. 
    Answer: the final code to the original input question. Please return the code only"""


    def __init__(self, llm, userID, **kwargs) -> None:
        self.llm = llm
        prompt = self._prepare_prompt()
        self.chain = LLMChain(llm=llm, prompt=prompt)

    def _prepare_prompt(self):
        prompt_template = "\n\n".join([self.PROMPT_PREFIX, self.FORMAT_INSTRUCTIONS, self.SUFFIX_WITH_DF])
        prompt = PromptTemplate.from_template(prompt_template)
        
        return prompt
    
    def format_output(self, code):
        pattern = r"```python\s*(.*?)\s*```"
        matches = re.findall(pattern, code, re.DOTALL)
        if matches and len(matches):
            code = matches[0]


        return code
    
    def run(self, question, df, verbose=False, **kwargs):
        config = {}
        if verbose:
            config={"callbacks": [CallBackHandler()]}
        out = self.chain.invoke({
            "input": question,
            "df_head": df.head()
        }, config=config)

        out = out["text"].split("Answer:")[-1]

        if verbose:
            print(out)

        return self.format_output(out)



class VisualizeAgent:
    def __init__(self, llm, userID, **kwargs) -> None:
        self.query_agent = SQLDataQuery(llm, userID, **kwargs)

        self.viz_agent = PandasAgent(llm, userID, **kwargs)

    def run(self, question, verbose=False, **kwargs):
        data_dict, df = self.query_agent.run(question, verbose=verbose)
        return {
            "data": data_dict,
            "code": self.viz_agent.run(question, df, verbose)
        }
    
def create_agent(llm, **kwargs):
    return VisualizeAgent(llm, **kwargs)