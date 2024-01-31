import sqlite3
import pandas as pd
import os

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

con = sqlite3.connect(os.path.join(data_path, "..", "..", "data.db"))
cur = con.cursor()

pd_data = pd.read_csv(os.path.join(data_path, "data.csv"))
pd_data.to_sql("data", con, if_exists="replace")