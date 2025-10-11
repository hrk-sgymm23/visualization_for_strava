# FYI: https://qiita.com/tatsuki-tsuchiyama/items/fb15145029e5e7318bec
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()
client_id = "179010"
client_secret = os.environ["STRAVA_CLIENT_SECRET"]
redirect_uri = "http://localhost/exchange_token"

request_url = (
    f"https://www.strava.com/oauth/authorize?client_id={client_id}"
    f"&response_type=code&redirect_uri={redirect_uri}"
    f"&approval_prompt=force"
    f"&scope=profile:read_all,activity:read_all"
)

print("クリックしてください:", request_url)
print("アプリを認証し、生成されたコードを以下のURLにコピー＆ペーストしてください。")
code = input("URLからコードを貼り付ける： ")

# http://localhost/exchange_token?state=&code=ed7c4bc34a971e83bbccb194c7023d7f4c57ca19&scope=read,activity:read_all,profile:read_all

token = requests.post(
    url="https://www.strava.com/api/v3/oauth/token",
    data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
    },
)

strava_token = token.json()

with open("strava_tokens.json", "w") as f:
    json.dump(strava_token, f, indent=2)

print(".envにアクセストークンを追加する", strava_token["access_token"])