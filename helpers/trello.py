# 📌 helpers/trello.py – Flexibel & stabil: Karten per Name ODER ID an Trello senden

import os
import requests
from dotenv import load_dotenv

# 🔐 Lade API-Keys und Board-ID
load_dotenv("getkeys.env")

TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.getenv("TRELLO_BOARD_ID")

# 🔁 Optionale Direkt-IDs für bestimmte Listen
LISTE_REDAKTION = os.getenv("TRELLO_LISTE_REDAKTION")
LISTE_REVIEW = os.getenv("TRELLO_LISTE_REVIEW")
LISTE_FREIGEGEBEN = os.getenv("TRELLO_LISTE_FREIGEGEBEN")


def finde_liste_id(liste_name):
    """
    Holt die ID einer Liste anhand ihres Namens.
    """
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
    params = {"key": TRELLO_KEY, "token": TRELLO_TOKEN}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return None
    for liste in r.json():
        if liste["name"].strip().lower() == liste_name.strip().lower():
            return liste["id"]
    return None


def lade_alle_listennamen():
    """
    Gibt alle Listennamen auf dem aktuellen Board zurück.
    Ideal für dynamische Dropdowns.
    """
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
    params = {"key": TRELLO_KEY, "token": TRELLO_TOKEN}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return []
    return [l["name"] for l in r.json()]


def sende_karte_an_liste_id(titel, text, list_id):
    """
    Erstellt eine Karte in einer Liste mit bekannter ID.
    """
    if not list_id:
        return "❌ Keine Listen-ID übergeben."
    url = "https://api.trello.com/1/cards"
    params = {
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN,
        "idList": list_id,
        "name": titel,
        "desc": text
    }
    r = requests.post(url, params=params)
    return f"📬 Karte erstellt (ID: {list_id}) – Status: {r.status_code}"


def sende_karte_an_trello(titel, text, listenname):
    """
    Erstellt eine Trello-Karte auf Basis des Listennamens (wird in ID umgewandelt).
    """
    list_id = finde_liste_id(listenname)
    if not list_id:
        return f"❌ Liste '{listenname}' nicht gefunden."
    return sende_karte_an_liste_id(titel, text, list_id)
