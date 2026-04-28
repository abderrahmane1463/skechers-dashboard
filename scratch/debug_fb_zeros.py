import requests
import json
import os

ACCESS_TOKEN = "EAAXdQDmFoT8BRYOvKeaEYk9az3iqKbDnlHks3hT5WZBKmMT8cXjO7D03YX3QOelqZCxHOjKmCbZBLx6rMi7vOrcRLMbYofDwfBbPd7TNOlE2ZCbnWPkEOQ9QZAIbzpNuqpFRP9OvX3LuZC4M1lZAuDszoCxwRkGfKmZBvdeZBr1fZCx41Tv9t7AZAsXhutOo7pQfPzrPSwUpZCy11mn70VINXyXwOvIZD"
PAGE_ID = "144124252311741"
VERSION = "v19.0"

def debug_fb_posts():
    # 1. Get recent posts
    url = f"https://graph.facebook.com/{VERSION}/{PAGE_ID}/posts"
    params = {
        "access_token": ACCESS_TOKEN,
        "limit": 5,
        "fields": "id,message,created_time"
    }
    
    print(f"Fetching posts for Page {PAGE_ID}...")
    resp = requests.get(url, params=params).json()
    posts = resp.get("data", [])
    
    if not posts:
        print("No posts found or error fetching posts.")
        print(resp)
        return

    for post in posts:
        p_id = post["id"]
        print(f"\n--- Checking Post: {p_id} ({post.get('created_time')}) ---")
        print(f"Message: {post.get('message', '(No caption)')[:50]}...")
        
        # 2. Try to fetch insights
        metrics = "post_impressions,post_impressions_unique,post_impressions_organic,post_impressions_paid"
        ins_url = f"https://graph.facebook.com/{VERSION}/{p_id}/insights"
        ins_params = {
            "access_token": ACCESS_TOKEN,
            "metric": metrics
        }
        
        ins_resp = requests.get(ins_url, params=ins_params).json()
        
        if "error" in ins_resp:
            print(f"ERROR: {ins_resp['error']['message']}")
        else:
            data = ins_resp.get("data", [])
            if not data:
                print("No insight data returned (empty list).")
            else:
                for item in data:
                    name = item["name"]
                    val = item["values"][0]["value"] if item.get("values") else "N/A"
                    print(f"  {name}: {val}")

if __name__ == "__main__":
    debug_fb_posts()
