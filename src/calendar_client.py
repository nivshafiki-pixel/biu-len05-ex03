"""
Calendar client - עוטף את Google Calendar API.
בודק זמינות ויוצר אירועים חדשים.
"""

import os
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
]

TOKEN_PATH = os.path.join("credentials", "token.json")

# ישראל: UTC+3 בקיץ (שעון קיץ), UTC+2 בחורף.
# לפשטות הפרויקט נניח קבוע +03:00 (בהתאם לתאריך הנוכחי - יולי).
ISRAEL_TZ = timezone(timedelta(hours=3))


def get_calendar_service():
    """מחזיר אובייקט שירות מאומת לעבודה מול Calendar API."""
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build("calendar", "v3", credentials=creds)


def is_slot_available(start_iso: str, end_iso: str, calendar_id: str = "primary") -> bool:
    """
    בודק אם חלון הזמן הנתון פנוי ביומן.
    start_iso, end_iso: מחרוזות זמן בפורמט ISO 8601 הכולל אזור זמן,
    לדוגמה "2026-07-20T14:00:00+03:00"
    """
    service = get_calendar_service()

    body = {
        "timeMin": start_iso,
        "timeMax": end_iso,
        "items": [{"id": calendar_id}],
    }

    result = service.freebusy().query(body=body).execute()
    busy_slots = result["calendars"][calendar_id]["busy"]

    return len(busy_slots) == 0


def create_event(summary: str, start_iso: str, end_iso: str,
                  location: str = "", attendees: list = None,
                  calendar_id: str = "primary") -> dict:
    """
    יוצר אירוע חדש ביומן.
    attendees: רשימת כתובות מייל (אופציונלי)
    """
    service = get_calendar_service()

    event_body = {
        "summary": summary,
        "location": location,
        "start": {"dateTime": start_iso},
        "end": {"dateTime": end_iso},
    }

    if attendees:
        event_body["attendees"] = [{"email": email} for email in attendees]

    created_event = service.events().insert(
        calendarId=calendar_id, body=event_body
    ).execute()

    return created_event


if __name__ == "__main__":
    # בדיקה מהירה - בודק זמינות מחר ב-14:00-15:00 (שעון ישראל)
    tomorrow = datetime.now(ISRAEL_TZ) + timedelta(days=1)
    start = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)

    start_iso = start.isoformat()
    end_iso = end.isoformat()

    print(f"Checking availability: {start_iso} to {end_iso}")
    available = is_slot_available(start_iso, end_iso)
    print(f"Available: {available}")
