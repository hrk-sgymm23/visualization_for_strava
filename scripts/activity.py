import os
import requests
from dotenv import load_dotenv

load_dotenv()

import requests
import json

url = "https://www.strava.com/api/v3/athlete/activities"
access_token = os.environ["STRAVA_TOKEN"]

headers = {"Authorization": f"Bearer {access_token}"}

response = requests.get(url, headers=headers)

activities = response.json()

activities_list = []
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

print(json.dumps(activities_list, indent=4))
