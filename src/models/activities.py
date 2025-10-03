import pandas as pd
from typing import Tuple
from config import DATA_CSV_PATH, LATEST_N

def load_activities(path: str = DATA_CSV_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    # 時系列並びを保証（start_date_local を文字列→日時に）
    df["start_date_local"] = pd.to_datetime(df["start_date_local"])
    df = df.sort_values("start_date_local", ascending=False).reset_index(drop=True)
    return df

def latest_n(df: pd.DataFrame, n: int = LATEST_N) -> pd.DataFrame:
    return df.head(n).copy()

def top3_by(df: pd.DataFrame, col: str) -> pd.DataFrame:
    return df.sort_values(by=col, ascending=False).head(3).copy()

def prepare_chart_source(df: pd.DataFrame) -> pd.DataFrame:
    # グラフに使う列だけ残すなど、将来の加工の置き場
    cols = ["start_date_local", "distance", "name"]
    return df[cols].copy()

def prepare_summary_source(df: pd.DataFrame) -> pd.DataFrame:
    now = pd.Timestamp.now(tz="Asia/Tokyo")
    # 期間フィルタ
    this_month = df[df["start_date_local"].dt.month == now.month]
    this_week = df[df["start_date_local"].dt.isocalendar().week == now.isocalendar().week]
    latest_30 = df.sort_values("start_date_local", ascending=False).head(30)

    # 単位変換（Stravaのdistanceはメートル）
    for d in (df, this_month, this_week, latest_30):
        d["distance_km"] = d["distance"] / 1000.0

    # 各集計
    summary = pd.DataFrame({
        "対象": ["直近30アクティビティ", "今月", "今週"],
        "総走行距離 (km)": [
            latest_30["distance_km"].sum(),
            this_month["distance_km"].sum(),
            this_week["distance_km"].sum(),
        ],
        "総獲得標高 (m)": [
            latest_30["total_elevation_gain"].sum(),
            this_month["total_elevation_gain"].sum(),
            this_week["total_elevation_gain"].sum(),
        ]
    })

    summary["総走行距離 (km)"] = summary["総走行距離 (km)"].round(1)
    summary["総獲得標高 (m)"] = summary["総獲得標高 (m)"].round(0)

    return summary