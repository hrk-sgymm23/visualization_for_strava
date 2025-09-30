import streamlit as st
import pandas as pd
import plotly.express as px

# CSVファイルを読み込み
df = pd.read_csv("tmp_csv/activities.csv")

st.title("Strava activities")


### Top 3 distance activities
top3 = df.sort_values(by="distance", ascending=False).head(3)
st.subheader("Top 3 distance activities (Latest 30 activities)")
st.dataframe(top3)


### Top 3 total_elevation_gain activities
top3_elevation = df.sort_values(by="total_elevation_gain", ascending=False).head(3)
st.subheader("Top 3 total_elevation_gain activities (Latest 30 activities)")
st.dataframe(top3_elevation)


### Each Activity Distance graph
st.subheader("Each Activity Distance")
fig = px.bar(
    df,
    x="start_date_local",
    y="distance",
    color="name",
    title="Each Activity Distance",
    barmode="group"
)
fig.update_traces(width=3.5)
st.plotly_chart(fig)


### All activities
st.subheader("Latest 30 activities")
st.dataframe(df)