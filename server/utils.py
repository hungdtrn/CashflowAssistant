import os
import pandas as pd
from langchain_community.utilities import SQLDatabase

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
print(data_path)
def query_data(userID):
    """
    Query the data from the database.
    """
    data = pd.read_csv(os.path.join(data_path, "data.csv"))
    data = data[data['Client_ID'] == int(userID)]
    return data

def connect_db():
    """
    Connect to the database.
    """
    print(os.path.join(data_path, "data.db"))
    print("sqlite:///data.db")
    uri = "sqlite:///data.db"
    db = SQLDatabase.from_uri(uri)
    return db

