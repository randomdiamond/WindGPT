from app.core.config import settings
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)


def generate_report(geo_metrics: dict, rule_results: dict) -> str:
    system_prompt = (
        "Du bist der analytische Kern einer professionellen Geodaten-App für Windenergie. "
        "Deine Aufgabe ist es, komplexe Geo-Metriken in eine scannbare, moderne und präzise "
        "Zusammenfassung zu übersetzen. Vermeide unnötigen Fülltext, aber stelle sicher, "
        "dass alle Informationen detailliert genug sind, um vollständig zu sein. "
        "Betone insbesondere die Wichtigkeit von Schutzgebietserkennungen und deren "
        "spezifischen Typen. Nutze Das Markdown Format für eine strukturierte und übersichtliche Darstellung."
    )

    user_prompt = (
        "Werte die folgenden Standortdaten aus und erstelle eine detaillierte Übersicht:\n\n"
        f"Geo-Metriken: {geo_metrics}\n"
        f"Regel-Check: {rule_results}\n\n"
        "Halte dich EXAKT an dieses Layout und nutze Markdown zur detaillierten Hervorhebung:\n\n"
        "### 1. Standort & Eckdaten\n"
        "   - **Ort:** [Name der Siedlung] ([Typ])\n"
        "   - **Abstand zur Siedlung:** [Distanz] (Soll: [Mindestabstand])\n"
        "   - **Schutzgebiet:** [Name und Typ, detailliert aufgelistet. Erwähne, ob es sich um ein FFH- oder LSG-Gebiet handelt]\n\n"
        "### 2. Prüfungsergebnisse\n"
        "   [Eine detaillierte Erläuterung der aufgetretenen Konflikte. "
        "Behandle den Abstandskonflikt und den Schutzgebietskonflikt jeweils in einem eigenen Absatz. "
        "Hebe Kernbegriffe wie **Mindestabstand**, **Naturschutzgebiet** oder **Vogelschutzgebiet** fett hervor.]\n\n"
        "### 3. Gutachterliches Fazit\n"
        "   [Ein prägnanter, professioneller Satz zur generellen Eignung, der alle Hauptgründe (Abstand und Schutzgebiet) nennt. "
        "Vermeide Floskeln und komm direkt zum Punkt.]"
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_output_tokens=2000,
    )
    print(response)

    text = response.output_text
    return text
