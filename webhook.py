from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from helpers.mailer import send_mail

load_dotenv("getkeys.env")

JUDITH_MAIL = "info@raithel-design.de"
NICOLE_MAIL = "judith.raithel@icloud.com"

app = Flask(__name__)

@app.route("/trello-webhook", methods=["GET", "POST"])
def empfang():
    if request.method == "GET":
        return "✅ Trello Webhook erreichbar (GET für Validierung)", 200

    try:
        daten = request.get_json(force=True, silent=True) or {}
    except Exception as e:
        return f"⚠️ Fehlerhafte JSON-Struktur: {str(e)}", 415

    if not daten:
        return "🟡 Leere POST-Anfrage – vermutlich Validierung durch Trello", 200

    action = daten.get("action", {})
    typ = action.get("type")
    karte = action.get("data", {}).get("card", {})
    titel = karte.get("name", "📝 (Unbekannt)")
    user = action.get("memberCreator", {}).get("fullName", "jemand")
    ziel = action.get("data", {}).get("listAfter", {}).get("name", "")
    liste = action.get("data", {}).get("list", {}).get("name", "")

    print(f"📥 Webhook erkannt: Typ={typ} | Titel={titel} | Liste={ziel or liste} | User={user}")

    # 🟢 Neue Karte
    if typ == "createCard":
        betreff = f"🆕 Neue Karte von {user}"
        text = f"{user} hat eine neue Karte »{titel}« in der Liste »{liste}« erstellt."

        if liste in ["Ideen / Vorschläge von BSW", "Freigegeben", "Zur Überprüfung"]:
            send_mail(JUDITH_MAIL, betreff, text)
        if liste in ["Zur Überprüfung", "Ideen / Vorschläge von Raithel Design", "Redaktionspläne"]:
            send_mail(NICOLE_MAIL, betreff, text)

    # 🔁 Karten verschieben
    elif typ == "updateCard" and ziel:
        betreff = f"📦 Karte verschoben von {user}"
        text = f"{user} hat die Karte »{titel}« in die Liste »{ziel}« verschoben."

        if ziel in ["Ideen / Vorschläge von BSW", "Freigegeben", "Zur Überprüfung"]:
            send_mail(JUDITH_MAIL, betreff, text)
        if ziel in ["Zur Überprüfung", "Ideen / Vorschläge von Raithel Design", "Redaktionspläne"]:
            send_mail(NICOLE_MAIL, betreff, text)

    # 💬 Kommentar
    elif typ == "commentCard":
        kommentar = action["data"].get("text", "(kein Text)")
        betreff = f"💬 Kommentar zu »{titel}«"
        text = f"{user} hat kommentiert:\n{kommentar}"

        if liste in ["Ideen / Vorschläge von BSW", "Freigegeben", "Zur Überprüfung"]:
            send_mail(JUDITH_MAIL, betreff, text)
        if liste in ["Zur Überprüfung", "Ideen / Vorschläge von Raithel Design", "Redaktionspläne"]:
            send_mail(NICOLE_MAIL, betreff, text)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
