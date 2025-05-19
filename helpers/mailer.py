
import requests
import os
from dotenv import load_dotenv

load_dotenv("getkeys.env")

MAILERSEND_API_KEY = os.getenv("MAILERSEND_API_KEY")
ABSENDER_EMAIL = "info@raithel-design.de"
ABSENDER_NAME = "BSW - Nachricth vom Trello-Board"

def send_mail(empfaenger, betreff, inhalt):
    if not MAILERSEND_API_KEY:
        print("❌ Kein MailerSend API-Key gefunden.")
        return

    url = "https://api.mailersend.com/v1/email"
    headers = {
        "Authorization": f"Bearer {MAILERSEND_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "from": {
            "email": ABSENDER_EMAIL,
            "name": ABSENDER_NAME
        },
        "to": [{"email": empfaenger}],
        "recipients": [{"email": empfaenger}],
        "subject": betreff,
        "text": inhalt
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print("📬 Mailversand:", response.status_code)
        if response.status_code == 202:
            print("✅ Mail erfolgreich gesendet an:", empfaenger)
        else:
            print("⚠️ Antwort:", response.text)
    except Exception as e:
        print("❌ Fehler beim Mailversand:", str(e))
