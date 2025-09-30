import streamlit as st
import pandas as pd

def show_table(title: str, df: pd.DataFrame):
    st.subheader(title)
    st.dataframe(df)

def show_title(main_title: str):
    st.title(main_title)