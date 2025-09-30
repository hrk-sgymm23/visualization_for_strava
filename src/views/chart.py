import streamlit as st
import plotly.express as px
import pandas as pd

def activity_distance_bar(df: pd.DataFrame, title: str = "Each Activity Distance"):
    fig = px.bar(
        df,
        x="start_date_local",
        y="distance",
        color="name",
        title=title,
        barmode="group"
    )
    # 太さ（幅）の調整：カテゴリ/密度により見え方が変わる点に注意
    fig.update_traces(width=0.8)
    st.subheader(title)
    st.plotly_chart(fig, use_container_width=True)