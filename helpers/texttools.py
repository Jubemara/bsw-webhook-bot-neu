# 🔧 helpers/texttools.py – GPT-4 mit System-Promptlogik, Wissensbasis, Tonalität und Content-Vorgaben inkl. Bildanalyse (Vision)

import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv("getkeys.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 📘 Hintergrundwissen laden
try:
    with open("bsw_wissensbasis.md", "r", encoding="utf-8") as f:
        bsw_context = f.read()
except FileNotFoundError:
    bsw_context = ""

# 🎯 Stilbeschreibung
def stil_beschreibung(ton):
    beschreibungen = {
        "locker": "Der Text soll leicht, sympathisch und menschlich wirken – gerne mit einem Augenzwinkern, auch humorvoll. Du darfst Emojis verwenden.",
        "emotional": "Verwende gefühlvolle, bildhafte Sprache. Sprich die Zielgruppe empathisch und verbindend an. Du darfst ruhig berühren.",
        "sachlich": "Der Text soll nüchtern, informativ und professionell klingen – ohne Floskeln, keine Emojis, kein Smalltalk.",
        "Chef persönlich": "Formuliere so, als würde der Inhaber selbst sprechen: direkt, herzlich, persönlich und authentisch – mit klarer Haltung."
    }
    return beschreibungen.get(ton, "Formuliere verständlich, authentisch und zielgruppengerecht.")

# 🧠 Systemrolle
def system_prompt(tonalitaet):
    return (
        f"Schreibe im Stil von »{tonalitaet}« – das bedeutet:\n{stil_beschreibung(tonalitaet)}\n\n"
        "Du bist ein erfahrener Social-Media-Experte und Content-Ersteller mit tiefem Know-how im Bereich Malerhandwerk sowie Trocknungstechnik. "
        "Du betreust die Social-Media-Präsenz der Firmen BSW Malerhandwerk und BSW Trocknungstechnik. "
        "Deine Hauptaufgabe ist es, strategische Redaktionspläne zu erstellen und daraus passende Inhalte für Instagram & Facebook abzuleiten. "
        "Hier ist das Hintergrundwissen:\n\n" + bsw_context
    )

# 🗓️ Redaktionsplan (4 Wochen)
def generiere_redaktionsplan(thema, start_kw):
    prompt = (
        "Erstelle einen kreativen, strategisch ausgewogenen Redaktionsplan mit 1 Social-Media-Beitrag pro Woche für 4 Wochen. "
        "Berücksichtige unterschiedliche Content-Formate: z.B. Azubi-Posts, Projektberichte, Behind the Scenes, Kundenfeedback. "
        "Integriere mindestens 1 Post aus der Kategorie 'Tipps und Tricks' und 1 aus der Kategorie 'Wussten Sie schon...?'. "
        "Zielgruppe: Endkunden, Immobilienverwaltungen, Bauherren. Ton: sympathisch, professionell, lebendig. "
        "Pro Woche: kurze Inhaltsbeschreibung + Format (Post, Story, Reel). Inhalte für Instagram & Facebook."
        f"\n\nThema: {thema}\nStart-KW: {start_kw}"
    )
    messages = [
        {"role": "system", "content": system_prompt("locker")},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

# 📲 Plattform-Anpassung (Instagram/Facebook)
def passe_post_an(text, plattform):
    prompt = (
        f"Erstelle ausschließlich einen {plattform}-Post aus folgendem Inhalt. "
        f"Beachte typische Anforderungen, Tonalität und Hashtag-Stil der Plattform.\n\n{text}"
    )
    messages = [
        {"role": "system", "content": system_prompt("locker")},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.8
    )
    return response.choices[0].message.content

# 🔁 Mehrfachadaption aus Plan-Text
def adaptiere_mehrfach(plantext, plattformen, stil):
    output = {}
    for plattform in plattformen:
        prompt = (
            f"Du sollst aus folgendem Redaktionsplan-Eintrag einen konkreten Beitrag für {plattform} machen.\n"
            f"Behalte die inhaltliche Aussage exakt bei, aber passe Länge, Stil, Tonalität und Format an {plattform} an.\n"
            f"Stil: {stil_beschreibung(stil)}\n\nRedaktionsplan-Eintrag:\n{plantext}"
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt(stil)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            output[plattform] = response.choices[0].message.content.strip()
        except Exception as e:
            output[plattform] = f"❌ Fehler bei {plattform}: {str(e)}"
    return output.get("Instagram", ""), output.get("Facebook", "")

# 🖼️ Vision-Funktion – GPT-4o mit Bild + Text
def vision_post(text, bild, plattform, stil):
    messages = [
        {"role": "system", "content": system_prompt(stil)},
        {"role": "user", "content": f"Bitte erstelle einen Social-Media-Post für {plattform}. Nutze folgenden Text als Briefing:\n{text}"}
    ]
    if bild is not None:
        messages.append({"role": "user", "content": [{"type": "image_url", "image_url": {"url": bild}}]})
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Fehler bei Bildauswertung: {str(e)}"

# 🔁 Tonalität eines bestehenden Beitrags neu formulieren
def tonalitaet_neuformulieren(text, stil, plattform):
    prompt = (
        f"Formuliere folgenden Beitrag neu – in einem anderen Ton.\n\n"
        f"Zielplattform: {plattform}\n"
        f"Neue Tonalität: {stil_beschreibung(stil)}\n\n"
        f"Text:\n{text}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt(stil)},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Fehler bei der Umformulierung: {str(e)}"

# 🧠 GPT-Redaktionsplan: 3 Wochen + 1 fester Beitrag
def generiere_redaktionsplan_3woche_plus1(eingabe, start_kw):
    prompt = (
        "Plane einen Redaktionsplan für 4 Wochen mit 1 Beitrag pro Woche.\n"
        "Ein Beitrag ist bereits vom Kunden vorgegeben – dieser soll fest im Plan enthalten sein.\n"
        "Die restlichen 3 Beiträge bitte thematisch sinnvoll ergänzen.\n\n"
        "Der vorgegebene Beitrag lautet:\n"
        f"{eingabe.strip()}\n\n"
        "Erstelle zu jeder Woche:\n"
        "- Eine Themenidee\n"
        "- Das passende Format (Post, Story, Reel)\n"
        "- Eine kurze Begründung zur Auswahl\n"
        "- Die empfohlene Kalenderwoche (ausgehend von KW " + str(start_kw) + ")\n\n"
        "Zielgruppe: Endkunden, Bauherren, Verwaltungen\n"
        "Stil: sympathisch, fachlich kompetent, mit Mehrwert"
    )

    try:
        messages = [
            {"role": "system", "content": system_prompt("locker")},
            {"role": "user", "content": prompt}
        ]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Fehler beim Erstellen des 3+1-Plans: {str(e)}"    

# 🧪 Sicherstellen, dass alle nötigen Funktionen vorhanden sind
def check_texttools_integritaet():
    required = [
        "generiere_redaktionsplan",
        "generiere_redaktionsplan_3woche_plus1",
        "passe_post_an",
        "adaptiere_mehrfach",
        "vision_post",
        "tonalitaet_neuformulieren"
    ]
    missing = [f for f in required if f not in globals()]
    if missing:
        raise ImportError(f"❌ Fehlende Funktionen in texttools.py: {', '.join(missing)}")
    print("✅ texttools.py enthält alle nötigen Funktionen.")
