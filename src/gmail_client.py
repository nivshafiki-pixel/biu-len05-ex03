"""
Gmail client - עוטף את Gmail API לקריאת מיילים אחרונים ושליחת תשובות.
"""

import os
import base64
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

TOKEN_PATH = os.path.join("credentials", "token.json")


def get_gmail_service():
    """מחזיר אובייקט שירות מאומת לעבודה מול Gmail API."""
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build("gmail", "v1", credentials=creds)


def list_recent_emails(days_back: int = 2, max_results: int = 10):
    """
    מחזיר רשימת מיילים אחרונים (days_back ימים אחורה), תוך אי-הכללת
    מיילים שנשלחו על ידינו עצמנו (כדי למנוע לולאת משוב על תגובות שהסוכן שלח).
    כל פריט: dict עם id, subject, sender, snippet, body
    """
    service = get_gmail_service()

    after_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")
    query = f"after:{after_date} -from:me"

    results = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg_ref in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="full"
        ).execute()

        headers = msg["payload"].get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(no subject)")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "(unknown sender)")

        body = _extract_body(msg["payload"])

        emails.append({
            "id": msg_ref["id"],
            "subject": subject,
            "sender": sender,
            "snippet": msg.get("snippet", ""),
            "body": body,
        })

    return emails


def _extract_body(payload) -> str:
    """מחלץ טקסט פשוט מגוף ההודעה (מטפל גם במיילים מרובי-חלקים)."""
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        for part in payload["parts"]:
            if "parts" in part:
                result = _extract_body(part)
                if result:
                    return result
        return ""
    else:
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        return ""


def _extract_sender_email(sender_header: str) -> str:
    """מחלץ כתובת מייל נקייה מתוך כותרת From (שעלולה להיות בפורמט 'Name <email>')."""
    if "<" in sender_header and ">" in sender_header:
        return sender_header.split("<")[1].split(">")[0].strip()
    return sender_header.strip()


def send_reply(to: str, subject: str, body_text: str, thread_id: str = None):
    """
    שולח מייל תשובה.
    to: כתובת הנמען (יכולה לכלול שם, ינוקה אוטומטית)
    subject: נושא (אם לא מתחיל ב-"Re:", יתווסף אוטומטית)
    body_text: גוף ההודעה
    thread_id: אופציונלי - כדי לשלוח כתגובה בתוך אותה שרשור מייל קיים
    """
    service = get_gmail_service()

    clean_to = _extract_sender_email(to)
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    message = MIMEText(body_text)
    message["to"] = clean_to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    body = {"raw": raw}
    if thread_id:
        body["threadId"] = thread_id

    sent = service.users().messages().send(userId="me", body=body).execute()
    return sent


if __name__ == "__main__":
    emails = list_recent_emails(days_back=2)
    print(f"Found {len(emails)} emails in the last 2 days (excluding self-sent):")
    print()
    for email in emails:
        print("Subject:", email["subject"])
        print("From:", email["sender"])
        print("Snippet:", email["snippet"])
        print("---")
