# ✅ Umbau der bisherigen `main.py` – jetzt mit ECHTEN API-Funktionen aktiv
# Funktionen: Plattformwahl, Redaktionsplan (GPT), Datei-Uploads, Trello, Feedback, Mailversand

import gradio as gr
import os
import datetime
from helpers.texttools import (
    generiere_redaktionsplan,
    generiere_redaktionsplan_3woche_plus1,
    passe_post_an,
    adaptiere_mehrfach,
    vision_post,
    tonalitaet_neuformulieren,
    check_texttools_integritaet
)
from helpers.storage import speichere_datei, lade_vorgaben, speichere_feedback
from helpers.trello import sende_karte_an_trello
from helpers.feedback_utils import generiere_feedback_webhook
from dotenv import load_dotenv

load_dotenv("getkeys.env")  # 🔐 API-Schlüssel aus externer Datei laden

PLATTFORMEN = ["Instagram", "Facebook"]
START_KW = datetime.date.today().isocalendar()[1] + 1

# 🧪 Integritätscheck für texttools
check_texttools_integritaet()

def anzeigen_redaktionsplan(woche1):
    return {"Instagram": woche1, "Facebook": woche1}

def generiere_beitrag(redaktionsplan, plattformen):
    return adaptiere_mehrfach(redaktionsplan, plattformen, "locker")

def speichere_und_sende(beitrag, plattform, dateiname, liste):
    pfad = speichere_datei(beitrag, dateiname, plattform)
    trello_response = sende_karte_an_trello(dateiname, beitrag, liste)
    return f"✅ Gespeichert unter {pfad}\n📬 Trello: {trello_response}"

def feedback_speichern(inhalt):
    return speichere_feedback(inhalt)

def feedback_webhook_ausloesen():
    return generiere_feedback_webhook()

def vision_auswerten(text, bilder, plattformen, stil):
    beitraege = {}
    for plattform in plattformen:
        for bild in bilder:
            if bild is not None:
                beitraege[plattform] = vision_post(text, bild, plattform, stil)
                break  # nur ein Bild pro Plattform verwenden
        if plattform not in beitraege:
            beitraege[plattform] = vision_post(text, None, plattform, stil)
    return beitraege.get("Instagram", ""), beitraege.get("Facebook", "")

def tonalitaet_anpassen(text, stil, plattform):
    return tonalitaet_neuformulieren(text, stil, plattform)

def uploads_an_trello(dateiname, kommentar, files, plattform, liste):
    dateipfade = []
    os.makedirs("uploads", exist_ok=True)
    for file in files:
        if file is not None:
            ziel = f"uploads/{os.path.basename(file.name)}"
            with open(ziel, "wb") as f:
                f.write(file.read())
            dateipfade.append(ziel)

    text = f"📌 Plattform: {plattform}\n📝 Kommentar: {kommentar}\n📎 Dateien: {', '.join(dateipfade)}"
    trello_response = sende_karte_an_trello(dateiname, text, liste)
    return f"✅ Hochgeladen & an Trello gesendet:\n{trello_response}"

# ⬇️ Gradio UI-Setup

with gr.Blocks(title="BSW GPT Assistent", css="style.css") as demo:
    gr.Markdown("""# 🖌️ BSW Redaktionsassistent
    Plane, generiere und exportiere Social-Media-Beiträge mit GPT-Unterstützung.""")

    with gr.Tabs():
        with gr.Tab("🖼️ Bild-Upload (Kundenfotos)"):
            bilder_upload = gr.File(file_types=["image"], file_count="multiple", label="Kundenbilder hochladen")

        with gr.Tab("1️⃣ Redaktionsplan erstellen"):
            with gr.Row():
                eingabe = gr.Textbox(label="Vorgabe / Thema")
                starte_kw = gr.Slider(label="Start-KW", value=START_KW, minimum=1, maximum=52, step=1)
            plan_typ = gr.Radio(["4 Wochen planen", "3 Wochen planen (+1 steht fest)"], label="Planungstyp", value="4 Wochen planen")
            generieren_btn = gr.Button("Redaktionsplan generieren")
            redaktionsplan_out = gr.Textbox(label="Redaktionsplan", lines=12)

        with gr.Tab("2️⃣ Plattform-Beitrag ableiten"):
            mitwahl = gr.CheckboxGroup(choices=PLATTFORMEN, label="Für welche Plattformen ableiten?")
            ableiten_btn = gr.Button("Beitrag generieren")
            with gr.Row():
                insta_out = gr.Textbox(label="Instagram", lines=6)
                fb_out = gr.Textbox(label="Facebook", lines=6)
            with gr.Row():
                neue_tonalitaet = gr.Radio(["locker", "emotional", "sachlich", "Chef persönlich"], label="Tonalität neu formulieren")
                tonal_btn = gr.Button("In neuer Tonalität umformulieren")
                insta_tonal = gr.Textbox(label="Instagram – neu formuliert", lines=5)
                fb_tonal = gr.Textbox(label="Facebook – neu formuliert", lines=5)

        with gr.Tab("3️⃣ Export & Trello"):
            dateiname = gr.Textbox(label="Dateiname (KW + Thema)")
            export_plattformen = gr.CheckboxGroup(choices=PLATTFORMEN, label="Plattform für Export")
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
            vision_plattform = gr.CheckboxGroup(PLATTFORMEN, label="Plattform")
            vision_stil = gr.Radio(["locker", "emotional", "sachlich", "Chef persönlich"], label="Tonalität", value="locker")
            vision_btn = gr.Button("Beitrag generieren")
            vision_out_insta = gr.Textbox(label="Instagram Vorschlag")
            vision_out_fb = gr.Textbox(label="Facebook Vorschlag")

        with gr.Tab("📂 Upload & Vorschau an Trello"):
            upload_dateiname = gr.Textbox(label="Titel / Thema")
            upload_plattform = gr.Radio(PLATTFORMEN, label="Plattform")
            upload_kommentar = gr.Textbox(label="Kommentar oder Info", lines=3)
            upload_files = gr.File(file_types=[".pdf", ".png", ".jpg", ".jpeg", ".mp4"], file_count="multiple", label="Dateien hochladen")
            upload_liste = gr.Textbox(label="Trello-Liste")
            upload_btn = gr.Button("An Trello senden")
            upload_out = gr.Textbox(label="Status")

    # Aktionen
    def generiere_plan_router(eingabe, starte_kw, plan_typ):
        if "3 Woche" in plan_typ:
            return generiere_redaktionsplan_3woche_plus1(eingabe, starte_kw)
        return generiere_redaktionsplan(eingabe, starte_kw)

    generieren_btn.click(generiere_plan_router, inputs=[eingabe, starte_kw, plan_typ], outputs=redaktionsplan_out)
    ableiten_btn.click(generiere_beitrag, inputs=[redaktionsplan_out, mitwahl], outputs=[insta_out, fb_out])
    # 🔁 Zwei Funktionen für Plattform-spezifische Tonalitätsanpassung
    def tonalitaet_anpassen_ig(text, stil):
        return tonalitaet_neuformulieren(text, stil, "Instagram")

    def tonalitaet_anpassen_fb(text, stil):
        return tonalitaet_neuformulieren(text, stil, "Facebook")

    # 🧩 Zwei getrennte Buttons für denselben Button – je nach Plattform
    tonal_btn.click(tonalitaet_anpassen_ig, inputs=[insta_out, neue_tonalitaet], outputs=insta_tonal)
    tonal_btn.click(tonalitaet_anpassen_fb, inputs=[fb_out, neue_tonalitaet], outputs=fb_tonal)

    export_btn.click(
    speichere_und_sende,
    inputs=[insta_out, export_plattformen, dateiname, trello_liste],
    outputs=export_out
)


    feedback_btn.click(feedback_speichern, inputs=feedback_in, outputs=feedback_out)
    webhook_btn.click(feedback_webhook_ausloesen, outputs=feedback_out)
    vision_btn.click(vision_auswerten, inputs=[vision_text, vision_bilder, vision_plattform, vision_stil], outputs=[vision_out_insta, vision_out_fb])
    upload_btn.click(uploads_an_trello, inputs=[upload_dateiname, upload_kommentar, upload_files, upload_plattform, upload_liste], outputs=upload_out)

# Serverstart
if __name__ == "__main__":
    demo.launch()
