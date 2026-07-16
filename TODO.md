# TODO.md

קבוצה: biu-len05 | תרגיל: ex03

## Google Cloud
- [x] פרויקט נוצר (biu-len05-agent)
- [x] Gmail API + Calendar API מופעלים
- [x] OAuth consent screen מוגדר
- [x] Client ID נוצר והורד (credentials/client_secret.json)
- [x] Test users נוספו
- [x] תוקן: חוסר התאמה בין פרויקטים (Client נוצר מחדש בפרויקט הנכון)

## מבנה ואבטחה
- [x] מבנה תיקיות נוצר
- [x] git init
- [x] .gitignore כולל credentials/
- [x] venv נוצר
- [x] אומת שאין סודות בהיסטוריית git לפני push

## קוד
- [x] תלויות Google API הותקנו
- [x] אימות ראשוני בוצע (token.json נוצר)
- [x] gmail_client.py נכתב ונבדק (כולל שליחת מייל וסינון -from:me)
- [x] calendar_client.py נכתב ונבדק (כולל תיקון timezone)
- [x] 3 קבצי SKILL.md נכתבו ונבדקו
- [x] orchestrator.py + main.py נכתבו (כולל דגלי --send ו---only)

## בדיקה
- [x] 10 מיילים אמיתיים נבדקו - 0 false positives
- [x] זיהוי הזמנת פגישה עובד (מייל בדיקה מחבר קבוצה)
- [x] חילוץ פרטים עובד
- [x] מסלול "פנוי" נבדק (אירוע נוצר בפועל ביומן)
- [x] מסלול "תפוס" נבדק (מייל דחייה נשלח בפועל)
- [x] תוקן: feedback loop מתגובות עצמיות
- [x] תועד: אי-דטרמיניזם בהחלטות LLM (אותו מייל, תוצאות שונות)

## תיעוד והגשה
- [x] README.md מלא (כולל 3 תגליות הנדסיות)
- [x] commit סופי (וידוא שאין סודות בהיסטוריית git)
- [x] ריפו GitHub נוצר ונדחף
- [ ] PDF הגשה מולא (3 סטודנטים) ונשמר כ-biu-len05-ex03.pdf
- [ ] הוגש במודל (כל סטודנט בנפרד, אותו קישור GitHub)
