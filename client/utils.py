import os
from dotenv import load_dotenv
import requests
import json
import pandas as pd
import ast
load_dotenv()

CACHE_NUM_ENTRY = 1
CACHE_TTL = 10

def to_pandas(out):
    if type(out) == list:
        out = pd.DataFrame(out)
    elif type(out) == dict:
        out = pd.DataFrame.from_dict(out, orient="index")

    for col in out.columns:
        if out[col].dtype == "float64":
            out[col] = out[col].round(0)

    return out

def process_output(out: str):
    # out = ast.literal_eval(str(out))
    # if type(out) == list:
    #     out = pd.DataFrame(out)
    # elif type(out) == dict:
    #     out = pd.DataFrame.from_dict(out, orient="index")

    # for col in out.columns:
    #     print(out[col].dtype)
    #     if out[col].dtype == "float64":
    #         out[col] = out[col].round(1)

    try:
        out = ast.literal_eval(str(out))
        if isinstance(out, dict) and "code" in out:
            out['data'] = to_pandas(out['data'])
            out["code"] = "import streamlit as st\n\n"+ out["code"]
            out["code"] = out["code"].replace("fig.show()", "st.plotly_chart(fig, use_container_width=True)")
        else:
            out = to_pandas(out)
    except Exception as e:
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
    return out["response"]

def get_pd(path, server_url, obj):
    out = get(path, server_url, obj)
    return process_output(out)

def get_history(path, server_url, obj):
    output = get(path, server_url, obj)
    for conv in output:
        conv["content"] = process_output(conv["content"])
    
    return output