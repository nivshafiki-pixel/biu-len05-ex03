"""
אורקסטרטור - מנהל את הזרימה המלאה: קריאת מיילים, זיהוי הזמנות פגישה,
בדיקת זמינות ביומן, תגובה מתאימה (אישור/דחייה), ושליחת המייל/יצירת אירוע בפועל.
"""

import json
import subprocess
from datetime import datetime, timedelta, timezone

from gmail_client import list_recent_emails, send_reply
from calendar_client import is_slot_available, create_event, ISRAEL_TZ


def call_claude_with_skill(skill_name: str, prompt_text: str) -> str:
    """קורא ל-Claude Code CLI עם Skill ספציפי, מחזיר את הפלט הגולמי (טקסט)."""
    full_prompt = f"Use the '{skill_name}' skill. {prompt_text}"

    result = subprocess.run(
        ["claude", "-p", full_prompt, "--output-format", "json"],
        capture_output=True,
        timeout=120,
    )

    if result.returncode != 0:
        stderr_text = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"Claude Code call failed (skill={skill_name}): {stderr_text}")

    stdout_text = result.stdout.decode("utf-8", errors="replace")
    payload = json.loads(stdout_text)
    output_text = payload.get("result", "").strip()

    if not output_text:
        raise RuntimeError(f"Empty result from Claude Code (skill={skill_name})")

    return output_text


def is_meeting_request(email: dict) -> bool:
    """בודק אם מייל מכיל הזמנה לפגישה, באמצעות ה-Skill scan-gmail."""
    prompt = (
        f"Decide if this email is a meeting request.\n\n"
        f"Subject: {email['subject']}\n"
        f"Body: {email['body'][:1000]}"
    )
    answer = call_claude_with_skill("scan-gmail", prompt)
    return answer.strip().upper().startswith("YES")


def extract_meeting_details(email: dict) -> dict:
    """מחלץ פרטי פגישה מהמייל, באמצעות ה-Skill parse-meeting-request."""
    today = datetime.now(ISRAEL_TZ).strftime("%Y-%m-%d")
    prompt = (
        f"Extract meeting details from this email.\n\n"
        f"Current date: {today}\n"
        f"Subject: {email['subject']}\n"
        f"Body: {email['body'][:1000]}"
    )
    raw = call_claude_with_skill("parse-meeting-request", prompt)
    return json.loads(raw)


def draft_response(status: str, details: dict, language: str = "hebrew") -> str:
    """מנסח תגובת מייל, באמצעות ה-Skill manage-calendar."""
    prompt = (
        f"Draft a response email.\n\n"
        f"Status: {status}\n"
        f"Date: {details['date']}\n"
        f"Time: {details['time']}\n"
        f"Location: {details.get('location', '')}\n"
        f"Language: {language}"
    )
    return call_claude_with_skill("manage-calendar", prompt)


def process_email(email: dict, take_real_actions: bool = False) -> dict:
    """
    מעבד מייל בודד דרך כל השרשרת: זיהוי -> חילוץ -> בדיקת זמינות -> תגובה -> פעולה.

    take_real_actions: אם False (ברירת מחדל, DRY RUN), הפונקציה מזהה ומנתחת
    בלבד - לא יוצרת אירועים ביומן ולא שולחת מיילים. אם True, מבצעת בפועל.

    מחזיר dict עם כל השלבים לצורך תיעוד ושקיפות.
    """
    result = {
        "email_id": email["id"],
        "subject": email["subject"],
        "sender": email["sender"],
        "is_meeting_request": False,
    }

    if not is_meeting_request(email):
        return result

    result["is_meeting_request"] = True

    details = extract_meeting_details(email)
    result["extracted_details"] = details

    start_dt = datetime.strptime(f"{details['date']}T{details['time']}", "%Y-%m-%dT%H:%M")
    start_dt = start_dt.replace(tzinfo=ISRAEL_TZ)
    end_dt = start_dt + timedelta(minutes=details.get("duration_minutes", 60))

    start_iso = start_dt.isoformat()
    end_iso = end_dt.isoformat()

    available = is_slot_available(start_iso, end_iso)
    result["slot_available"] = available

    if available:
        response_text = draft_response("אושר", details)
        if take_real_actions:
            event = create_event(
                summary=details.get("subject", "פגישה"),
                start_iso=start_iso,
                end_iso=end_iso,
                location=details.get("location", ""),
            )
            result["event_created"] = event.get("id")
        else:
            result["event_created"] = None
            result["dry_run_note"] = "Event NOT created (dry run - use --send to take real actions)"
    else:
        response_text = draft_response("נדחה", details)

    result["response_draft"] = response_text

    if take_real_actions:
        sent = send_reply(
            to=email["sender"],
            subject=email["subject"],
            body_text=response_text,
        )
        result["email_sent"] = True
        result["sent_message_id"] = sent.get("id")
    else:
        result["email_sent"] = False

    return result


def run(days_back: int = 2, max_results: int = 10, take_real_actions: bool = False):
    """מריץ את התהליך המלא על מיילים אחרונים."""
    emails = list_recent_emails(days_back=days_back, max_results=max_results)
    results = []

    for email in emails:
        subject_preview = email["subject"][:50]
        print(f"Processing: {subject_preview}...")
        try:
            result = process_email(email, take_real_actions=take_real_actions)
            results.append(result)
            if result["is_meeting_request"]:
                print("  -> Meeting request detected!")
                if result.get("email_sent"):
                    print("  -> Reply email sent.")
                if result.get("event_created"):
                    print("  -> Calendar event created.")
            else:
                print("  -> Not a meeting request.")
        except Exception as e:
            print(f"  -> Error: {e}")
            results.append({
                "email_id": email["id"],
                "subject": email["subject"],
                "error": str(e),
            })

    return results


if __name__ == "__main__":
    results = run()
    print()
    print(f"Processed {len(results)} emails.")
    meeting_requests = [r for r in results if r.get("is_meeting_request")]
    print(f"Meeting requests found: {len(meeting_requests)}")
