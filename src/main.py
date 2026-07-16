"""
נקודת כניסה - מריץ את האורקסטרטור על מיילים אחרונים,
ושומר את התוצאות המלאות (כולל שלבי ביניים) לקובץ JSON.

שימוש:
  python main.py                     # DRY RUN על כל המיילים האחרונים
  python main.py --send               # LIVE על כל המיילים האחרונים
  python main.py --only <message_id>  # מריץ רק על מייל בודד (DRY RUN)
  python main.py --only <message_id> --send   # מריץ רק על מייל בודד (LIVE)
"""

import json
import os
import sys
from datetime import datetime

from orchestrator import run, process_email
from gmail_client import list_recent_emails

RESULTS_DIR = os.path.join("data", "results")


def main():
    take_real_actions = "--send" in sys.argv

    only_id = None
    if "--only" in sys.argv:
        idx = sys.argv.index("--only")
        if idx + 1 < len(sys.argv):
            only_id = sys.argv[idx + 1]

    if take_real_actions:
        print("WARNING: Running with --send. Real calendar events WILL be created")
        print("and actual emails WILL be sent.")
        print()
    else:
        print("Running in DRY RUN mode (no real actions). Use --send for live mode.")
        print()

    if only_id:
        print(f"Filtering to single email with id={only_id}")
        emails = list_recent_emails(days_back=2, max_results=20)
        emails = [e for e in emails if e["id"] == only_id]
        if not emails:
            print(f"No email found with id={only_id}")
            return
        results = []
        for email in emails:
            print(f"Processing: {email['subject'][:50]}...")
            result = process_email(email, take_real_actions=take_real_actions)
            results.append(result)
            if result["is_meeting_request"]:
                print("  -> Meeting request detected!")
            else:
                print("  -> Not a meeting request.")
    else:
        results = run(days_back=2, max_results=10, take_real_actions=take_real_actions)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{only_id}" if only_id else ""
    output_path = os.path.join(RESULTS_DIR, f"run_{timestamp}{suffix}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print()
    print(f"Full results saved to: {output_path}")

    meeting_requests = [r for r in results if r.get("is_meeting_request")]
    print(f"Meeting requests found: {len(meeting_requests)}")

    for mr in meeting_requests:
        print()
        print("=== Meeting Request Details ===")
        print("Subject:", mr["subject"])
        print("Extracted:", mr.get("extracted_details"))
        print("Slot available:", mr.get("slot_available"))
        print("Event created:", mr.get("event_created"))
        print("Response draft:", mr.get("response_draft"))
        print("Email sent:", mr.get("email_sent"))


if __name__ == "__main__":
    main()
