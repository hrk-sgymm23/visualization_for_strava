import streamlit as st
import pandas as pd

def show_summary(title: str, df: pd.DataFrame):
    st.subheader(title)
    st.dataframe(df)