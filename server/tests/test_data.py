import requests
from ..utils import connect_db
import pandas as pd
import ast
from ..ai.agents import create_analyze_agent
from langchain.chat_models import ChatOpenAI
import dotenv
import os
import warnings
# os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

warnings.filterwarnings("ignore")
# print(os.getcwd())
dotenv.load_dotenv()

def initialise():
    db = connect_db()
    return db, ChatOpenAI(model=os.environ["OPENAI_MODEL"])

def test_single_record_query():
    db, llm = initialise()
    agent = create_analyze_agent(llm=llm, userID=1, db=db)

    instruction = "What was the cashflow at 1 Random Street, VIC on 06 Feb 2024"
    target_query = 'SELECT Date, Revenue, Expenses, Revenue - Expenses as "Cashflow" FROM data WHERE "Date" = Date("2024-02-06") AND "Store_Address" = "1 Random Street, VIC" AND "Client_ID" = 1'
    target_output = db.run(target_query, include_columns=True)
    target_output = ast.literal_eval(target_output)
    target_output = pd.DataFrame(target_output) 
    target_output = target_output.iloc[:, [0, -1]].to_numpy()

    returned_output = agent.run(instruction)
    returned_output = pd.DataFrame(returned_output)
    returned_output = returned_output.iloc[:, [0, -1]].to_numpy()

    assert (target_output == returned_output).all(), "LLM should return the expected data"

def test_multiple_record_query():
    db, llm = initialise()
    agent = create_analyze_agent(llm=llm, userID=1, db=db)

    instruction = "What was the daily cashflow at 1 Random Street, VIC from 01 Feb 2024 to 06 Feb 2024"
    target_query = 'SELECT Date, Revenue, Expenses, Revenue - Expenses as "Cashflow" FROM data WHERE "Date" >= Date("2024-02-01") AND "Date" <= Date("2024-02-06") AND "Store_Address" = "1 Random Street, VIC" AND "Client_ID" = 1'
    target_output = db.run(target_query, include_columns=True)
    target_output = ast.literal_eval(target_output)
    target_output = pd.DataFrame(target_output) 
    target_output = target_output.iloc[:, [0, -1]].to_numpy()

    returned_output = agent.run(instruction)
    returned_output = pd.DataFrame(returned_output)
    returned_output = returned_output.iloc[:, [0, -1]].to_numpy()
    print(returned_output)
    print(target_output)
    assert (target_output == returned_output).all(), "LLM should return the expected data"

