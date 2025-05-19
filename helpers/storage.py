# 🗃️ helpers/storage.py – Speichern von Beiträgen und Feedback lokal

import os

def speichere_datei(text, dateiname, plattform):
    pfad = f"outputs/{plattform}_{dateiname}.txt"
    os.makedirs("outputs", exist_ok=True)
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(text)
    return pfad

def speichere_feedback(inhalt):
    pfad = "feedback.jsonl"
    with open(pfad, "a", encoding="utf-8") as f:
        f.write(inhalt + "\n")
    return pfad

def lade_vorgaben():
    # Platzhalter für spätere Dropdown-Themenvorgaben
    return ["Azubi", "Projekt", "Angebot"]
