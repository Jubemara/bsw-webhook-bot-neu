# ✅ Umbau der bisherigen `main.py` – jetzt mit ECHTEN API-Funktionen aktiv
# Funktionen: Plattformwahl, Redaktionsplan (GPT), Datei-Uploads, Trello, Feedback, Mailversand

import gradio as gr
import os
import datetime
from helpers.texttools import generiere_redaktionsplan, passe_post_an, adaptiere_mehrfach, vision_post
from helpers.storage import speichere_datei, lade_vorgaben, speichere_feedback
from helpers.trello import sende_karte_an_trello
from helpers.feedback_utils import generiere_feedback_webhook
from dotenv import load_dotenv

load_dotenv("getkeys.env")  # 🔐 API-Schlüssel aus externer Datei laden

PLATTFORMEN = ["Instagram", "Facebook"]
START_KW = datetime.date.today().isocalendar()[1] + 1

def anzeigen_redaktionsplan(woche1):
    return {"Instagram": woche1, "Facebook": woche1}

def generiere_beitrag(redaktionsplan, plattformen):
    return adaptiere_mehrfach(redaktionsplan, plattformen, "locker")

def speichere_und_sende(beitrag, plattformen, dateiname, liste):
    statusmeldungen = []
    for plattform in plattformen:
        pfad = speichere_datei(beitrag.get(plattform, ""), dateiname, plattform)
        trello_response = sende_karte_an_trello(dateiname, beitrag.get(plattform, ""), liste)
        statusmeldungen.append(f"✅ {plattform}: Gespeichert unter {pfad}\n📬 Trello: {trello_response}")
    return "\n\n".join(statusmeldungen)

def feedback_speichern(inhalt):
    return speichere_feedback(inhalt)

def feedback_webhook_ausloesen():
    return generiere_feedback_webhook()

def vision_auswerten(text, bilder, plattformen, stil):
    results = []
    for plattform in plattformen:
        for bild in bilder:
            if bild is not None:
                results.append(f"{plattform}:\n" + vision_post(text, bild, plattform, stil))
                break
        else:
            results.append(f"{plattform}:\n" + vision_post(text, None, plattform, stil))
    return "\n\n".join(results)

def uploads_an_trello(dateiname, kommentar, files, plattformen, liste):
    dateipfade = []
    os.makedirs("uploads", exist_ok=True)
    for file in files:
        if file is not None:
            ziel = f"uploads/{os.path.basename(file.name)}"
            with open(ziel, "wb") as f:
                f.write(file.read())
            dateipfade.append(ziel)

    text = f"📝 Kommentar: {kommentar}\n📎 Dateien: {', '.join(dateipfade)}"
    responses = []
    for plattform in plattformen:
        full_text = f"📌 Plattform: {plattform}\n{text}"
        trello_response = sende_karte_an_trello(dateiname, full_text, liste)
        responses.append(f"{plattform}: {trello_response}")
    return "\n".join(responses)

# ⬇️ Gradio UI-Setup

with gr.Blocks(title="BSW GPT Assistent", css="style.css") as demo:
    gr.Markdown("""# 🖌️ BSW Redaktionsassistent
    Plane, generiere und exportiere Social-Media-Beiträge mit GPT-Unterstützung.""")

    with gr.Tabs():
        with gr.Tab("🖼️ Kundenbilder hochladen"):
            gr.File(file_types=["image"], file_count="multiple", label="Bilder vom Kunden hochladen")

        with gr.Tab("1️⃣ Redaktionsplan erstellen"):
            with gr.Row():
                eingabe = gr.Textbox(label="Vorgabe / Thema")
                starte_kw = gr.Slider(label="Start-KW", value=START_KW, minimum=1, maximum=52, step=1)
            generieren_btn = gr.Button("Redaktionsplan generieren")
            redaktionsplan_out = gr.Textbox(label="Redaktionsplan", lines=10)

        with gr.Tab("2️⃣ Plattform-Beitrag ableiten"):
            mitwahl = gr.CheckboxGroup(choices=PLATTFORMEN, label="Für welche Plattformen ableiten?")
            ableiten_btn = gr.Button("Beitrag generieren")
            with gr.Row():
                insta_out = gr.Textbox(label="Instagram", lines=6)
                fb_out = gr.Textbox(label="Facebook", lines=6)

        with gr.Tab("3️⃣ Export & Trello"):
            dateiname = gr.Textbox(label="Dateiname (KW + Thema)")
            export_plattformen = gr.CheckboxGroup(choices=PLATTFORMEN, label="Plattformen für Export")
            trello_liste = gr.Textbox(label="Trello-Liste (z. B. 'Redaktionspläne')")
            export_btn = gr.Button("Beitrag speichern & an Trello senden")
            export_out = gr.Textbox(label="Rückmeldung")

        with gr.Tab("4️⃣ Feedback"):
            feedback_in = gr.Textbox(label="Feedback eingeben", lines=5)
            feedback_btn = gr.Button("Feedback speichern")
            feedback_out = gr.Textbox(label="Gespeichert unter")
            webhook_btn = gr.Button("Webhook manuell auslösen (Test)")

        with gr.Tab("🖼️ Bilder analysieren (Vision)"):
            vision_text = gr.Textbox(label="Text / Briefing", lines=4)
            vision_bilder = gr.File(file_types=["image"], file_count="multiple", label="Bis zu 5 Bilder")
            vision_plattform = gr.CheckboxGroup(choices=PLATTFORMEN, label="Plattformen")
            vision_stil = gr.Radio(["locker", "emotional", "sachlich", "Chef persönlich"], label="Tonalität", value="locker")
            vision_btn = gr.Button("Beitrag generieren")
            vision_out = gr.Textbox(label="Generierter Beitrag")

        with gr.Tab("📂 Upload & Vorschau an Trello"):
            upload_dateiname = gr.Textbox(label="Titel / Thema")
            upload_plattformen = gr.CheckboxGroup(choices=PLATTFORMEN, label="Plattformen")
            upload_kommentar = gr.Textbox(label="Kommentar oder Info", lines=3)
            upload_files = gr.File(file_types=[".pdf", ".png", ".jpg", ".jpeg", ".mp4"], file_count="multiple", label="Dateien hochladen")
            upload_liste = gr.Textbox(label="Trello-Liste")
            upload_btn = gr.Button("An Trello senden")
            upload_out = gr.Textbox(label="Status")

    # Aktionen
    generieren_btn.click(generiere_redaktionsplan, inputs=[eingabe, starte_kw], outputs=redaktionsplan_out)
    ableiten_btn.click(generiere_beitrag, inputs=[redaktionsplan_out, mitwahl], outputs=[insta_out, fb_out])
    export_btn.click(speichere_und_sende, inputs=[{"Instagram": insta_out, "Facebook": fb_out}, export_plattformen, dateiname, trello_liste], outputs=export_out)
    feedback_btn.click(feedback_speichern, inputs=feedback_in, outputs=feedback_out)
    webhook_btn.click(feedback_webhook_ausloesen, outputs=feedback_out)
    vision_btn.click(vision_auswerten, inputs=[vision_text, vision_bilder, vision_plattform, vision_stil], outputs=vision_out)
    upload_btn.click(uploads_an_trello, inputs=[upload_dateiname, upload_kommentar, upload_files, upload_plattformen, upload_liste], outputs=upload_out)

# Serverstart
if __name__ == "__main__":
    demo.launch()
