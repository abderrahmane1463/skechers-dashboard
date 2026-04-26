import requests
import json
import sys
import os
sys.path.append(os.getcwd())
from config import ACCESS_TOKEN

def check_ads():
    ad_acc = "act_765947885726761"
    params = {
        "level": "ad",
        "fields": "ad_id,ad_name,impressions,reach,actions,inline_post_engagement",
        "time_range": json.dumps({"since": "2026-03-01", "until": "2026-03-31"}),
        "access_token": ACCESS_TOKEN
    }
    url = f"https://graph.facebook.com/v19.0/{ad_acc}/insights"
    resp = requests.get(url, params=params)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    check_ads()
