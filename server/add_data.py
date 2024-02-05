import sqlite3
import pandas as pd
import os


import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta

def generate_mock_cash_flow(start_date='2023-01-01', end_date='2023-12-31', regions=['VIC', 'NSW', "QLD", "SA", "NT", "WA", "TAS"], companies=[['Coles']], client_ids=[1]):
    # Define the time frame
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # Define regions, stores, and other parameters
    # regions = ['VIC', 'NSW', "QLD", "SA", "NT", "WA", "TAS"]
    stores_per_region = 10
    metrics = ['Revenue', 'Expenses']
    other_metrics = ['Company', 'Company_ID', 'Client_ID']
    average_transaction_value_mean = 1000
    average_transaction_value_std = 200
    customer_traffic_mean = 500
    customer_traffic_std = 100
    inventory_levels_mean = 50000
    inventory_levels_std = 10000

    # Create an empty DataFrame
    columns = ['Store_ID', 'Store_Address', 'State', 'Date'] + metrics + other_metrics
    # df = pd.DataFrame(columns=columns)
    
    data = []
    store_id = 1
    company_id = 1
    # Generate synthetic data for each store in each region
    for cs, cid in zip(companies, client_ids):
        for company in cs: 
            for region in regions:
                for _ in range(1, stores_per_region + 1):
                    store_address = f'{store_id} Random Street, {region}'
                    store_postcode = f'{3000 + store_id}' if region == 'Victoria' else f'{2000 + store_id}'
                    
                    for date in date_range:
                        # Generate random values for metrics
                        revenue = np.random.uniform(5000, 10000)
                        expenses = np.random.uniform(3000, 7000)
                        net_cash_flow = revenue - expenses

                        # Append the data to the DataFrame
                        
                        data.append(({
                            'Store_ID': store_id,
                            'Store_Address': store_address,
                            'Region': region,
                            'Date': date,
                            'Revenue': revenue,
                            'Expenses': expenses,
                            'Company': company,
                            'Company_ID': company_id,
                            'Client_ID': cid
                        }).values())

                    store_id += 1
                    company_id += 1

        df = pd.DataFrame(data, columns=columns)

    return df

# get today in string
today = datetime.today().strftime('%Y-%m-%d')

# Generate mock cash flow for Coles in 2023
data_2023 = generate_mock_cash_flow("2023-01-01", end_date=today, regions=['VIC', 'NSW'], companies=[['Coles', "Woolworths"], ["Kmart", "Aldi"]], client_ids=[1,2])
data_2023.to_csv("./data/data.csv", index=False)

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

con = sqlite3.connect(os.path.join(data_path, "..", "data.db"))
cur = con.cursor()

pd_data = pd.read_csv(os.path.join(data_path, "data.csv"))
pd_data.to_sql("data", con, if_exists="replace")