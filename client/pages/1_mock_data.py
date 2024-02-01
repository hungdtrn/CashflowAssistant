import streamlit as st
import requests
import json
import pandas as pd
import datetime
import streamlit_scrollable_textbox as stx
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from utils import post, get
import os
import pandas as pd
import numpy as np

def display_dataframe_quickly(df, max_rows=50, **st_dataframe_kwargs):
    """Display a subset of a DataFrame or Numpy Array to speed up app renders.
    
    Parameters
    ----------
    df : DataFrame | ndarray
        The DataFrame or NumpyArray to render.
    max_rows : int
        The number of rows to display.
    st_dataframe_kwargs : Dict[Any, Any]
        Keyword arguments to the st.dataframe method.
    """
    n_rows = len(df)
    if n_rows <= max_rows:
        # As a special case, display small dataframe directly.
        st.write(df)
    else:
        # Slice the DataFrame to display less information.
        start_row = st.slider('Start row', 0, n_rows - max_rows)
        end_row = start_row + max_rows
        df = df[start_row:end_row]

        # Reindex Numpy arrays to make them more understadable.
        if type(df) == np.ndarray:
            df = pd.DataFrame(df)
            df.index = range(start_row,end_row)

        # Display everything.
        st.dataframe(df, **st_dataframe_kwargs)
        st.text('Displaying rows %i to %i of %i.' % (start_row, end_row - 1, n_rows))

load_dotenv()
st.title("Mock Data")
st.markdown("This is a mock data page. The data here is the mock data used for the demo. The data is not real.")
st.markdown("Please enter the ClientID")
userID = st.text_input('ClientID', None)
if not userID:
    st.text("Enter client ID")
else:
    # Display chat messages from history on app rerun
    output = get('data', os.getenv('SERVER_URL'), {"userID": userID})                
    display_dataframe_quickly(output)
