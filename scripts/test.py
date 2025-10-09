import os
import requests
from dotenv import load_dotenv

def check_strava_auth() -> None:
    """Strava API 認証確認"""
    load_dotenv()

    access_token = os.getenv("STRAVA_TOKEN")
    refresh_token = os.getenv("REFRESH_TOKEN")
    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")

    # 1️⃣ 現在の access_token で認証テスト
    url = "https://www.strava.com/api/v3/athlete"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        athlete = response.json()
        print("✅ 認証成功!")
        print(f"アスリート名: {athlete.get('firstname')} {athlete.get('lastname')}")
    else:
        print("⚠️ 現在のトークンは無効です。リフレッシュを試みます...")
        print(f"status_code: {response.status_code}")
        print("レスポンス:", response.text)

        # 2️⃣ トークンをリフレッシュ
        refresh_url = "https://www.strava.com/api/v3/oauth/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        refresh_res = requests.post(refresh_url, data=data)

        if refresh_res.status_code == 200:
            new_data = refresh_res.json()
            new_token = new_data["access_token"]
            print("✅ 新しいトークンを取得しました:", new_token)

            # 3️⃣ 新しいトークンで再度確認
            headers = {"Authorization": f"Bearer {new_token}"}
            retry = requests.get(url, headers=headers)
            if retry.status_code == 200:
                athlete = retry.json()
                print("✅ 再認証成功!")
                print(f"アスリート名: {athlete.get('firstname')} {athlete.get('lastname')}")
            else:
                print("❌ 新しいトークンでも認証失敗:", retry.status_code, retry.text)
        else:
            print("❌ トークン更新失敗:", refresh_res.status_code, refresh_res.text)


if __name__ == "__main__":
    check_strava_auth()
