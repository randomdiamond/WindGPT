from app.core.config import settings
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)


def generate_report(geo_metrics: dict, rule_results: dict) -> str:
    system_prompt = (
        "Du bist ein Ingenieur für Windenergieanlagen. "
        "Du bewertest Standorte sachlich und strukturiert."
    )

    user_prompt = (
        "Bewerte folgenden Standort:\n"
        f"Geo-Metriken: {geo_metrics}\n"
        f"Regel-Check: {rule_results}\n"
        "Erstelle einen strukturierten Bericht mit Überschriften und Handlungsempfehlungen."
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
