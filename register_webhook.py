import requests
import os
from dotenv import load_dotenv

load_dotenv("getkeys.env")

# 🔐 Erforderliche Werte
TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD_ID = os.getenv("TRELLO_BOARD_ID")
WEBHOOK_URL = "https://bsw-webhook-bot-neu.onrender.com/trello-webhook"

# 🛰️ Webhook registrieren
response = requests.post(
    "https://api.trello.com/1/webhooks/",
    params={
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN,
        "callbackURL": WEBHOOK_URL,
        "idModel": TRELLO_BOARD_ID,
        "description": "Webhook für neuen BSW GPT Bot"
    }
)

print(f"📡 Statuscode: {response.status_code}")
print(f"📬 Antwort: {response.text}")
