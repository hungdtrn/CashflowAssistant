import streamlit as st
import requests
import json
import pandas as pd
import datetime
import streamlit_scrollable_textbox as stx
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from utils import post
import os

load_dotenv()
st.title("Assistant")

#building out chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.disabled = False


def disable():
    st.session_state["disabled"] = True


userID = st.text_input('userID', None,
                       disabled=st.session_state.disabled,
                       on_change=disable)
checkbox_disabled = True # Disable the checkboxes by default
if not userID:
    # Need to also put in a check for a valid userID
    st.text("Enter user ID")
else:
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Type Message.......")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            st.chat_message("user").markdown(prompt)
            output = post('chat', os.getenv('SERVER_URL'), {"userId": userID, "message": prompt})
            st.session_state.messages.append({"role": "assistant", "content": output["response"]})

            st.chat_message("assistant").markdown(output["response"])
        except Exception as e:
            st.text(e)
