# 📡 helpers/feedback_utils.py – Webhook-Trigger & Feedback-Handling

from helpers.mailer import send_mail
import requests
import os
from dotenv import load_dotenv

load_dotenv("getkeys.env")

def generiere_feedback_datei():
    """
    Gibt den Pfad zur lokalen Feedback-Datei zurück.
    """
    return "feedback.jsonl"

def generiere_feedback_webhook():
    """
    Löst einen Webhook aus, z. B. wenn Feedback in Trello landet oder verschoben wurde.
    Der Webhook-URL muss in getkeys.env als FEEDBACK_WEBHOOK definiert sein.
    """
    webhook_url = os.getenv("FEEDBACK_WEBHOOK")
    token = os.getenv("FEEDBACK_TOKEN", "TESTTOKEN")  # Optionaler echter Token

    if not webhook_url:
        return "❌ Kein Webhook gesetzt."

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        r = requests.post(webhook_url, headers=headers)
        return f"🔔 Webhook ausgelöst – Status: {r.status_code}"
    except Exception as e:
        return f"❌ Fehler beim Webhook-Aufruf: {e}"
