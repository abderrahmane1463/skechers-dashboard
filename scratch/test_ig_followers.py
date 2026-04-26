import requests
import json
import sys
import os
sys.path.append(os.getcwd())
from config import GRAPH_BASE_URL, ACCESS_TOKEN, INSTAGRAM_USER_ID

def test_ig_followers():
    print(f"Testing follower_count for IG User: {INSTAGRAM_USER_ID}")
    
    # Try last 7 days
    from datetime import datetime, timedelta
    until = datetime.now()
    since = until - timedelta(days=7)
    
    params = {
        "metric": "follower_count",
        "period": "day",
        "since": int(since.timestamp()),
        "until": int(until.timestamp()),
        "access_token": ACCESS_TOKEN
    }
    
    url = f"{GRAPH_BASE_URL}/{INSTAGRAM_USER_ID}/insights"
    resp = requests.get(url, params=params)
    print(f"Status Code: {resp.status_code}")
    print("Response Content:")
    print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    test_ig_followers()
