import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

APP_NAME = os.environ["HEROKU_APP_NAME"]
API_KEY = os.environ["HEROKU_API_KEY"]

HEADERS = {
    "Accept": "application/vnd.heroku+json; version=3",
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

bogota_now = datetime.now(ZoneInfo("America/Bogota"))
target_quantity = 1 if 8 <= bogota_now.hour < 20 else 0

response = requests.patch(
    f"https://api.heroku.com/apps/{APP_NAME}/formation/web",
    headers=HEADERS,
    json={"quantity": target_quantity},
)
response.raise_for_status()
