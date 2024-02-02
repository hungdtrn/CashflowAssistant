import streamlit as st
import requests
import json
import pandas as pd
import datetime
import streamlit_scrollable_textbox as stx
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from utils import post, get_history, CACHE_TTL
import os
import pandas as pd

load_dotenv()
st.title("Cashflow Assistant")

st.markdown("""
 * This is a cashflow assistant that can help you with your cashflow related questions.
 * For the demo, you can use the following client IDs: 1, 2. Client with ID 1 has the cashflow data of Coles and Woolworths. Client with ID 2 has the cashflow data of Kmart and Aldi.
 * The data are not real and are used for the demo only. They are stored on one single table for simplicity. Please visit [mock data](/mock_data) to explore the mock data.
 * The components of this product are explained in the slide [here](https://docs.google.com/presentation/d/14ksVlbg3tV1rETHpiqgD1U41WMcqrPBvExYm-WMfSF4/edit?usp=sharing).
""")

#building out chat history
if "userID" not in st.session_state:
    st.session_state.userID = None
    st.session_state.messages = []
    st.session_state.disabled = False
    st.session_state.history_loaded = False

def _get_history(userID):
    output = get_history('history', os.getenv('SERVER_URL'), {"userID": userID})
    st.session_state.messages = output

def clear_history(userID):
    st.session_state.userID = None
    st.session_state.messages = []
    st.session_state.disabled = False
    st.session_state.history_loaded = False
    post('clear_history', os.getenv('SERVER_URL'), {"userID": userID})

def switch_user(userID):
    st.session_state.userID = None
    st.session_state.messages = []
    st.session_state.disabled = False
    st.session_state.history_loaded = False

def disable():
    st.session_state.disabled = True

def display_output(role, response):
    with st.chat_message(role):
        if type(response) == str:
            st.markdown(response)
        elif type(response) == pd.DataFrame:
            st.dataframe(response)

st.text_input('Please enter the ClientID', None, 
              disabled=st.session_state.disabled,
              key="userID",
              on_change=disable)

if not st.session_state.userID:
    # Need to also put in a check for a valid userID
    st.text("Enter client ID")
    st.session_state.disabled = False

else:
    st.sidebar.button("Clear session", on_click=lambda: clear_history(st.session_state.userID))
    st.sidebar.button("Switch user", on_click=lambda: switch_user(st.session_state.userID))

    if not st.session_state.history_loaded:
        with st.spinner('Please wait...'):
            _get_history(st.session_state.userID)
        st.session_state.history_loaded = True

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        display_output(message["role"], message["content"])

    prompt = st.chat_input("Type Message.......")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)
        with st.spinner('Please wait...'):
            output = post('chat', os.getenv('SERVER_URL'), {"userId": st.session_state.userID, "message": prompt})                
        st.session_state.messages.append({"role": "assistant", "content": output})
        display_output("assistant", output)