"""
סקריפט אימות ראשוני - מריצים פעם אחת כדי ליצור token.json.
פותח דפדפן, מבקש מהמשתמש להתחבר ולאשר הרשאות ל-Gmail ו-Calendar.
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import json

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
]

CREDENTIALS_PATH = os.path.join("credentials", "client_secret.json")
TOKEN_PATH = os.path.join("credentials", "token.json")


def main():
    creds = None

    if os.path.exists(TOKEN_PATH):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    print("Authentication successful.")
    print(f"Token saved to: {TOKEN_PATH}")
    print(f"Scopes granted: {creds.scopes}")


if __name__ == "__main__":
    main()
