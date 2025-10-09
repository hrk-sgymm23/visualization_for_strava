# In this example you have stored your token refresh data in a `.json` file
import json
import os
from dotenv import load_dotenv
from stravalib import Client

# Open and access the toke_refresh data
# You will populate this when you instantiate a client object below
json_path = os.path.join(os.getcwd(), "strava_tokens.json")
with open(json_path, "r") as f:
    token_refresh = json.load(f)

# Read the STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET environment variables
load_dotenv()
print("Expires at", token_refresh["expires_at"])

# Instantiate a client object, including your access_token, refresh_token, and token_expires values
# These values, if available, will allow stravalib to check if it needs to refresh the token for you when it makes an API call using the client object
client = Client(
    access_token=token_refresh["access_token"],
    refresh_token=token_refresh["refresh_token"],
    token_expires=token_refresh["expires_at"],
)

athlete = client.get_athlete()

new_token = {
    "access_token": client.access_token,
    "refresh_token": client.refresh_token,
    "expires_at": client.token_expires,
}

with open("strava_tokens.json", "w") as f:
    json.dump(new_token, f, indent=2)