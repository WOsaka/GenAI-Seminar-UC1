import base64
import os
import requests
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import converter_cv as c_cv

load_dotenv()

client: AzureOpenAI = AzureOpenAI(
    api_key=os.environ.get("AZURE_OAI_KEY"),
    api_version=os.environ.get("OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("AZURE_OAI_ENDPOINT")
)

def query_gpt40(
    messages: list[dict[str, str]],
) -> str:
    response = client.chat.completions.create(
        model=os.environ.get("AZURE_OAI_DEPLOYMENT"),
        messages=messages,
        max_tokens= 4096,
        n=1,
        temperature=0.05,
    )
    if response.choices[0].message.content:
        return response.choices[0].message.content.strip()
    return ""

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def fetch_search_results(query):
    """
    Funktion, um Suchergebnisse aus Azure Search abzurufen.
    """
    # Hier sollte die Implementierung für den Abruf von Azure Search-Ergebnissen eingefügt werden.
    # Beispiel:
    # - Azure Cognitive Search SDK verwenden
    # - Suchindex abfragen
    # - Ergebnisse als Liste von Dokumenten zurückgeben
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX")

    url = f"{search_endpoint}/indexes/{index_name}/docs/search?api-version=2021-04-30-Preview"
    headers = {"Content-Type": "application/json", "api-key": search_key}
    payload = {"search": query}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    results = response.json()
    #return results.get("value", [])  # Extrahiere die Treffer aus der Antwort

    return [{"description": "Beispielbeschreibung für " + query}]


def control_guidelines(image_path, metadata):
    """
    Funktion zur Analyse eines Grundrisses basierend auf Informationen aus Azure Search.
    """

    # Konvertiere das Bild in Base64
    try:
        with open(image_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode("utf-8")
    except FileNotFoundError:
        return f"Fehler: Die Bilddatei {image_path} wurde nicht gefunden."
    except Exception as e:
        return f"Fehler beim Kodieren des Bildes: {str(e)}"

    # Rufe die Vision API auf und erstelle Hervorhebungen
    try:
        c_cv.call_vision(image_path, "metadata_ocr")
        c_cv.draw_polygons_around_words(image_path, "metadata_ocr.json", "metadata_text_highlighted.png", 0.5)
    except Exception as e:
        return f"Fehler bei der Verarbeitung mit Vision API: {str(e)}"

    # Abruf von Richtlinien aus Azure Search
    guidelines_query = "DIN 18040"
    cost_query = "Kostenaufstellung"
    
    try:
        guidelines_search_results = fetch_search_results(guidelines_query)
        cost_info_search_results = fetch_search_results(cost_query)
    except Exception as e:
        return f"Fehler beim Abrufen der Azure-Suchdaten: {str(e)}"

    # Verarbeitung der Suchergebnisse
    guidelines = "\n".join([result.get("description", "Keine Beschreibung gefunden") for result in guidelines_search_results]) or "Keine relevanten Richtlinien gefunden."
    cost_information = "\n".join([result.get("description", "Keine Beschreibung gefunden") for result in cost_info_search_results]) or "Keine relevanten Kosteninformationen gefunden."

    # Bereite die Nachricht für die Analyse vor
    messages = [
        {
            "role": "system",
            "content": """
                Du bist spezialisiert auf die Analyse altersgerechten Wohnens. Dir wird ein Grundriss zusammen mit einer Analyse 
                zu Räumen, Türen und Maßen präsentiert. Deine Aufgabe ist es, die Wohnung basierend auf den vorgegebenen 
                Richtlinien zu bewerten und Vor- sowie Nachteile hinsichtlich altersgerechtem Wohnen aufzuzeigen.
                
                Gib Empfehlungen für kleine Änderungen, um die Wohnung in den genannten Aspekten zu verbessern. 
                Beurteile, ob das Verschieben von nicht tragenden Wänden sinnvoll wäre, um z. B. das Badezimmer größer und zugänglicher zu machen.
                
                Danach gib Empfehlungen basierend auf den möglichen Dienstleistungen in den Kosteninformationen und berechne einen geschätzten Preis.
                Antworte auf Deutsch.
            """
        },
        {
            "role": "user",
            "content": f"""
                Analysiere diesen Grundriss und gib die Informationen wie spezifiziert aus.

                

                **Metadaten:** {metadata}

                **Richtlinien:** {guidelines}

                **Kosteninformationen:** {cost_information}
            """
        }
    ]

    # Führe die GPT-Analyse durch
    try:
        final_response = query_gpt40(messages)
    except Exception as e:
        return f"Fehler bei der GPT-Analyse: {str(e)}"

    return final_response
