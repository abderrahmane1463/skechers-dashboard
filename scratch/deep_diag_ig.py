import requests
import json
import sys
import os
sys.path.append(os.getcwd())
from config import GRAPH_BASE_URL, ACCESS_TOKEN, INSTAGRAM_USER_ID

def deep_diag_ig():
    print(f"DEEP DIAGNOSTIC for IG User: {INSTAGRAM_USER_ID}")
    
    # Test March Range (as in screenshot)
    # March 1st to March 30th (30 days)
    import datetime
    since = datetime.datetime(2026, 3, 1, 0, 0, 0)
    until = datetime.datetime(2026, 3, 30, 0, 0, 0)
    
    since_ts = int(since.timestamp())
    until_ts = int(until.timestamp())
    
    metrics = ["follower_count", "impressions", "reach", "profile_views"]
    
    for m in metrics:
        print(f"\n--- Testing Metric: {m} (period=day) ---")
        params = {
            "metric": m,
            "period": "day",
            "since": since_ts,
            "until": until_ts,
            "access_token": ACCESS_TOKEN
        }
        url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/insights"
        resp = requests.get(url, params=params)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        items = data.get("data", [])
        if not items:
            print("ERROR: No data returned for this metric.")
            if "error" in data:
                print(f"API Message: {data['error'].get('message')}")
        else:
            vals = items[0].get("values", [])
            count = len(vals)
            total = sum(v["value"] for v in vals)
            print(f"Success: Found {count} days of data. Total Sum: {total}")
            if count > 0:
                print(f"Sample: {vals[0]}")

if __name__ == "__main__":
    deep_diag_ig()
