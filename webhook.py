from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from helpers.mailer import send_mail

load_dotenv("getkeys.env")

JUDITH_MAIL = "info@raithel-design.de"
NICOLE_MAIL = "judith.raithel@icloud.com"

app = Flask(__name__)

@app.route("/trello-webhook", methods=["POST"])
def webhook_handler():
    daten = request.json
    if not daten:
        return jsonify({"status": "Verifiziert"}), 200

    action = daten.get("action", {})
    typ = action.get("type")
    karte = action.get("data", {}).get("card", {})
    titel = karte.get("name", "📝 (Unbekannt)")
    user = action.get("memberCreator", {}).get("fullName", "jemand")
    ziel = action.get("data", {}).get("listAfter", {}).get("name", "")

    print(f"📥 Webhook erkannt: Typ={typ} | Titel={titel} | Liste={ziel} | User={user}")

    if typ == "updateCard" and ziel:
        betreff = f"📦 Karte verschoben von {user}"
        text = f"{user} hat die Karte »{titel}« in die Liste »{ziel}« verschoben."

        if ziel == "Ideen / Vorschläge von BSW":
            send_mail(JUDITH_MAIL, betreff, text)
        elif ziel in ["Ideen / Vorschläge von Raithel Design", "Redaktionspläne", "Zur Überprüfung"]:
            send_mail(NICOLE_MAIL, betreff, text)
        elif ziel == "Freigegeben":
            send_mail(JUDITH_MAIL, betreff, text)

    elif typ == "commentCard":
        kommentar = action["data"].get("text", "(kein Text)")
        betreff = f"💬 Kommentar zu »{titel}«"
        text = f"{user} hat kommentiert:\n{kommentar}"
        liste = action.get("data", {}).get("list", {}).get("name", "")

        if liste == "Ideen / Vorschläge von BSW":
            send_mail(JUDITH_MAIL, betreff, text)
        elif liste in ["Zur Überprüfung", "Freigegeben"]:
            send_mail(JUDITH_MAIL, betreff, text)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(port=7880)
