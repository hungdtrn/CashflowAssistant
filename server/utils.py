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

def connect_db(stage="production"):
    """
    Connect to the database.
    """
    if stage == "production":
        uri = "sqlite:///data.db"
    elif stage == "test":
        uri = "sqlite:///test_data.db"
        
    db = SQLDatabase.from_uri(uri)
    return db

