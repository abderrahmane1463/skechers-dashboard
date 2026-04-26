import requests
import json
import sys
import os
sys.path.append(os.getcwd())
from config import GRAPH_BASE_URL, ACCESS_TOKEN, INSTAGRAM_USER_ID

def diag_single_post():
    # Let's find one post ID first
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media?limit=5&access_token={ACCESS_TOKEN}"
    data = requests.get(url).json()
    posts = data.get("data", [])
    if not posts:
        print("No posts found.")
        return
    
    p_id = posts[0]["id"]
    print(f"DIAGNOSTIC FOR POST ID: {p_id}")
    
    # Method 1: Main media fields
    print("\n--- Method 1: Media Fields ---")
    fields = "id,like_count,comments_count,media_type,permalink"
    res1 = requests.get(f"https://graph.facebook.com/v19.0/{p_id}?fields={fields}&access_token={ACCESS_TOKEN}").json()
    print(json.dumps(res1, indent=2))
    
    # Method 2: Insights
    print("\n--- Method 2: Insights (Organic) ---")
    res2 = requests.get(f"https://graph.facebook.com/v19.0/{p_id}/insights?metric=likes,comments,shares,saved&access_token={ACCESS_TOKEN}").json()
    print(json.dumps(res2, indent=2))

if __name__ == "__main__":
    diag_single_post()
