import streamlit as st
from models.activities import load_activities, latest_n, top3_by, prepare_chart_source
from views.tables import show_table, show_title
from views.chart import activity_distance_bar
from config import LATEST_N

# キャッシュ：I/Oコストや再計算を抑制
@st.cache_data(show_spinner=False)
def _load_df():
    return load_activities()

def main():
    show_title("Strava activities")

    # Data
    df_all = _load_df()
    df_latest = latest_n(df_all, LATEST_N)

    # Top 3 distance
    top3_distance = top3_by(df_latest, "distance")
    show_table(f"Top 3 distance activities (Latest {LATEST_N} activities)", top3_distance)

    # Top 3 elevation
    top3_elev = top3_by(df_latest, "total_elevation_gain")
    show_table(f"Top 3 total_elevation_gain activities (Latest {LATEST_N} activities)", top3_elev)

    # Top 3 max heartrate
    # max_heartrate が欠損あり得るので NaN 対策（必要なら fillna(-inf) 等）
    top3_hr = top3_by(df_latest.dropna(subset=["max_heartrate"]), "max_heartrate")
    show_table(f"Top 3 max heartrate activities (Latest {LATEST_N} activities)", top3_hr)

    # Chart
    chart_df = prepare_chart_source(df_latest)
    activity_distance_bar(chart_df, "Each Activity Distance")

    # All activities
    show_table(f"Latest {LATEST_N} activities", df_latest)

if __name__ == "__main__":
    main()
