import os
import json
import requests
from typing import Dict, Any, List
from stravalib import Client


def load_tokens(json_path: str) -> Dict[str, Any]:
    """strava_tokens.json からトークン情報を読み込む"""
    with open(json_path, "r") as f:
        return json.load(f)


def save_tokens(json_path: str, token_data: Dict[str, Any]) -> None:
    """最新のトークン情報を JSON に保存する"""
    with open(json_path, "w") as f:
        json.dump(token_data, f, indent=2)


def create_client(token_data: Dict[str, Any]) -> Client:
    """stravalib クライアントを生成"""
    client = Client(
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_expires=token_data["expires_at"],
    )
    return client


def refresh_and_save_tokens(client: Client, json_path: str) -> Dict[str, Any]:
    """
    stravalib が自動リフレッシュしたトークンを保存。
    （有効期限が切れていた場合に備えて）
    """
    new_token = {
        "access_token": client.access_token,
        "refresh_token": client.refresh_token,
        "expires_at": client.token_expires,
    }
    save_tokens(json_path, new_token)
    return new_token


def fetch_activities(access_token: str) -> List[Dict[str, Any]]:
    """Strava APIからアクティビティ一覧を取得"""
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # エラーハンドリング
    activities = response.json()

    activities_list: List[Dict[str, Any]] = []
    for activity in activities:
        activity_info = {
            "id": activity.get("id"),
            "name": activity.get("name"),
            "distance": activity.get("distance"),
            "moving_time": activity.get("moving_time"),
            "elapsed_time": activity.get("elapsed_time"),
            "total_elevation_gain": activity.get("total_elevation_gain"),
            "type": activity.get("type"),
            "start_date": activity.get("start_date"),
            "start_date_local": activity.get("start_date_local"),
            "timezone": activity.get("timezone"),
            "utc_offset": activity.get("utc_offset"),
            "average_speed": activity.get("average_speed"),
            "max_speed": activity.get("max_speed"),
            "average_cadence": activity.get("average_cadence"),
            "average_temp": activity.get("average_temp"),
            "average_heartrate": activity.get("average_heartrate"),
            "max_heartrate": activity.get("max_heartrate"),
        }
        activities_list.append(activity_info)
    return activities_list


def main() -> None:
    """エントリーポイント"""
    # ファイルパス
    json_path = os.path.join(os.getcwd(), "strava_tokens.json")

    # 1.トークン読み込み
    token_data = load_tokens(json_path)
    print("Current expires_at:", token_data["expires_at"])

    # 2.クライアント生成
    client = create_client(token_data)

    # 3.ユーザー確認
    athlete = client.get_athlete()
    print(f"Hi, {athlete.firstname} Welcome to stravalib!")

    # 4.トークン更新（必要なら）＆保存
    new_token = refresh_and_save_tokens(client, json_path)

    # 5.アクティビティ取得
    activities = fetch_activities(new_token["access_token"])

    # 6.結果出力
    print(json.dumps(activities, indent=4))


if __name__ == "__main__":
    main()
