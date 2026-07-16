# PLAN.md - תוכנית ביצוע

קבוצה: biu-len05 | תרגיל: ex03

## שלב 0: Google Cloud setup
- יצירת פרויקט ב-Google Cloud Console
- הפעלת Gmail API ו-Calendar API
- הגדרת OAuth consent screen (External, Testing mode)
- הוספת test users (כל חברי הקבוצה)
- יצירת OAuth Client ID (Desktop app), הורדת client_secret.json

## שלב 1: מבנה פרויקט + אבטחה
- מבנה תיקיות, git init
- .gitignore (credentials/, venv/, token.json)
- venv, commit ראשוני (בלי סודות!)

## שלב 2: התקנת תלויות ואימות ראשוני
- pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
- סקריפט אימות ראשוני - יצירת token.json דרך דפדפן (פעם אחת בלבד)

## שלב 3: Gmail client
- gmail_client.py - קריאת מיילים אחרונים, סינון

## שלב 4: Calendar client
- calendar_client.py - בדיקת זמינות, יצירת אירוע

## שלב 5: Skills
- scan-gmail/SKILL.md
- parse-meeting-request/SKILL.md
- manage-calendar/SKILL.md

## שלב 6: אורקסטרציה
- orchestrator.py - מחבר בין כל השלבים
- main.py - נקודת כניסה

## שלב 7: בדיקה מקצה לקצה
- שליחת מייל בדיקה עצמי
- הרצה, וידוא זיהוי נכון
- בדיקת מסלול "פנוי" ומסלול "תפוס"

## שלב 8: תיעוד
- README.md מלא (כולל הסבר תהליך ה-OAuth setup לצורך שחזור)
- עדכון PRD/PLAN/TODO

## שלב 9: הגשה
- git push לריפו חדש
- מילוי PDF הגשה (biu-len05-ex03.pdf) - 3 סטודנטים
