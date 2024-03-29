import json
import warnings

import pandas as pd
import statsmodels.api as sm
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, FewShotPromptTemplate

from .base import SQLAgentBase
from .utils import CallBackHandler

warnings.filterwarnings("ignore")

class SQLTrainDataQuery(SQLAgentBase):
    PROMPT_PREFIX = """You are a SQLite expert {top_k}. Given an input predictive question, you need to create a syntactically correct SQLite query to run to get the appropriate data for training a predictive model to answer the question. Ignore the date time in the query, your query should collect all data of all date and time and group the data by date. Avoid using the LIMIT clause. 
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
You must include the Client_ID in the query. The Client_ID is a unique identifier for each user in the database. It is set to {userID} for the current user.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.

Use the following format:

Question: The prediction task here
Thought: How to query the data to train a model for the prediction task
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here"""

    PERMISION_ERROR = "We cannot do that at the moment. Please try again later!"

    EXAMPLES = [{
            "input": "How much will I spend next day?",
            "thought": "Need to query the expense data of each date",
            "query": 'SELECT "DATE", SUM("Expenses") FROM data WHERE "Client_ID" = {userID} GROUP BY "Date"'
        }, {
            "input": "How will my cash flow at Coles look like in the next two months?",
            "thought": "Need to query the expense data of each date",
            "query": 'SELECT "DATE", SUM("Revenue" - "Expenses") FROM data WHERE "Client_ID" = {userID} AND "Company" = "Coles" GROUP BY "Date"'
        }, {
            "input": "How will my average revenue look like in the next two year?",
            "thought": "Need to query the expense data of each date",
            "query": 'SELECT "DATE", AVG("Revenue") FROM data WHERE "Client_ID" = {userID} GROUP BY "Date"'
        }]
    
    EXAMPLE_PROMPT = "Question: {input}\nThought: {thought}\nSQLQuery: {query}"
    
    def format_output(self, text: str):
        out_list = super().format_output(text)
        if type(out_list) == str:
            return out_list

        df = pd.DataFrame(out_list, columns =['Date', 'Out'])
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    
    def run(self, question, verbose=False, include_columns=True):
        return super().run(question, verbose, include_columns=False)

class HyperParamAgent:
    PREFIX = """You are an Coding Assistant, your task is to generate the hyperparameters for a forecasting function based on the question of the user. 
The forecasting function is defined as
```
def forecast(df, group_freq: str, forecast_period: int):
    # Group by date
    df = df.groupby(pd.Grouper(key="Date", freq=group_freq)).sum()

    mod = sm.tsa.SARIMAX(df, order=(1, 0, 0), trend='c')
    res = mod.fit()

    pred = res.forecast(forecast_period)
    return pred
```
The input is a dataframe named `df`.
The function takes two hyperparameters: `group_freq` and `forecast_period`. `group_freq` is the frequency to group the data by. `forecast_period` is the number of periods to forecast.
Generate the values for these hyperparameters based on the question of the user.

{data_format}
"""
    SUFFIX = """Begin!
Question: {input}"""
    EXAMPLES = [{
        "input": "How much will I spend next three days?",
        "thought": "Need to group the data by day and forecast for 3 days",
        "answer": '{{"group_freq": "D", "forecast_period": 3}}'
    }, {
        "input": "How will my cash flow look like in the next months?",
        "thought": "Need to group the data by month and forecast for 1 months",
        "answer": '{{"group_freq": "M", "forecast_period": 1}}'
    }] 

    DATA_FORMAT = """Use the following format: 
Question: Question of the user
Thought: How to group the data and how many periods to forecast
Answer: Final answer is a json with the format: {{"group_freq": GROUP_STR, "forecast_period": FORECAST_INT}}"""

    EXAMPLE_PROMPT = "Question: {input}\nThought: {thought}\nAnswer: {answer}"

    def __init__(self, llm, userID, **kwargs) -> None:
        self.userID = userID
        self.llm = llm
        prompt = self._prepare_prompt()
        self.chain = LLMChain(llm=llm, prompt=prompt)

    def _prepare_prompt(self):
        example_prompt = PromptTemplate.from_template(self.EXAMPLE_PROMPT)
        prompt = FewShotPromptTemplate(
            examples=self.EXAMPLES,
            example_prompt=example_prompt,
            prefix= self.PREFIX,
            suffix=self.SUFFIX,
            input_variables=["input"],
        )
        prompt = prompt.partial(data_format=self.DATA_FORMAT)
        return prompt

    def run(self, inp_dict, verbose=False):
        config = {}
        if verbose:
            config={"callbacks": [CallBackHandler()]}
        out = self.chain.invoke(inp_dict, config=config)
        out = json.loads(out["text"].split("Answer:")[-1])
        if verbose:
            print(out)

        return out
    
class ForecastAgent:
    def __init__(self, llm, userID, **kwargs) -> None:
        self.query_agent = SQLTrainDataQuery(llm, userID, **kwargs)
        self.hyperparam_agent = HyperParamAgent(llm, userID, **kwargs)

    def run(self, question, verbose=False, **kwargs):
        df = self.query_agent.run(question, verbose=verbose)
        hyperparams = self.hyperparam_agent.run(question, verbose=verbose)
                
        return self.forecast(df, **hyperparams)

    def preprocess(self, df, group_freq):
         # Group by date
        df = df.groupby(pd.Grouper(key="Date", freq=group_freq)).sum()
        return df

    def forecast(self, df: pd.DataFrame, group_freq: str, forecast_period: int):
        """ Forecast the future cash flow data based on the controlling paramaters

        Args:
            df (pd.DataFrame): The past data for computing the statistics.
            group_freq (str): The parameter controlling how the data is processed.
            forecast_period (int): The parameter controlling the forecasting period.

        Returns:
            pred (dict): the forecasted cash flow data.
        """
        # If found data error -> return the error
        if type(df) == str:
            return df
        
        # Prerocess the data
        df = self.preprocess(df, group_freq=group_freq)

        # Fit a forecasting model
        mod = sm.tsa.SARIMAX(df, order=(1, 0, 0), trend='c')
        res = mod.fit(disp=False)

        # Forecast the future data
        pred = res.forecast(forecast_period)
        pred.index = pred.index.strftime('%Y-%m-%d')
        pred.name = "Forecasted"

        pred = pd.DataFrame(pred, columns=["Forecasted"]).T
        return pred.to_dict()

def create_agent(llm, **kwargs):
    forecaster = ForecastAgent(llm, **kwargs)
    return forecaster