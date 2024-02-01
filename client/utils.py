import os
from dotenv import load_dotenv
import requests
import json
import pandas as pd
import ast
load_dotenv()

CACHE_NUM_ENTRY = 1
CACHE_TTL = 10


def process_output(out: str):
    try:
        out = ast.literal_eval(str(out))
        if type(out) == list:
            out = pd.DataFrame(out)
            out = out.drop("index", axis=1)
        elif type(out) == dict:
            out = pd.DataFrame.from_dict(out, orient="index")

        # check each col, round if col is number
        for col in out.columns:
            if out[col].dtype == "float64":
                out[col] = out[col].round(1)
    except Exception as e:
        print("Error", e)
        pass
    return out

def post(path, server_url, obj, stream=False):
    """
    Funtion for POST requests. This function can also handle streaming requests.
    When streaming, set stream == True
    """
    headers = {'Content-type': 'application/json'}
    response = requests.post(f"{server_url}/{path}", data=json.dumps(obj), headers=headers, stream=stream)
    if not response.ok:
        print(response.text)
        raise Exception(f"Invalid response: {response.text}")

    # Return appropriate outputs depending on whether or not the response is streamed.
    out = json.loads(response.text)    
    return process_output(out["response"])
    
def get(path, server_url, obj):
    param_str=""
    for key in obj.keys():
        param_str += f"{key}={obj[key]}&"
        
    response = requests.get(f"{server_url}/{path}?{param_str}")
    if not response.ok:
        print(response.text)
        raise Exception(f"Invalid response: {response.text}")

    out = json.loads(response.text)    
    return process_output(out["response"])
