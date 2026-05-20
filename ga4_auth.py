"""
ga4_auth.py — Run once to authenticate with Google Analytics.
Opens a browser window, you log in with your Google account, done.
Creates ga4_token.json which the dashboard uses automatically.
"""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

flow = InstalledAppFlow.from_client_secrets_file("oauth_client.json", SCOPES)
creds = flow.run_local_server(port=0)

with open("ga4_token.json", "w") as f:
    f.write(creds.to_json())

print("✅ Authentification réussie ! ga4_token.json sauvegardé.")
print("Tu peux maintenant lancer le dashboard normalement.")
