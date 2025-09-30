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
