import os
import json
from dotenv import load_dotenv

# Add OpenAI import  pip install openai==1.13.3 python-dotenv

from openai import AzureOpenAI

# Get configuration settings
load_dotenv()
azure_oai_endpoint = os.getenv("OPENAI_API_ENDPOINT")
azure_oai_key = os.getenv("OPENAI_API_KEY")
azure_oai_deployment = "gpt-4o"
azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
azure_search_key = os.getenv("AZURE_SEARCH_KEY")
azure_search_index = os.getenv("AZURE_SEARCH_INDEX")

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    base_url=f"{azure_oai_endpoint}/openai/deployments/{azure_oai_deployment}/extensions",
    api_key=azure_oai_key,
    api_version="2023-09-01-preview",
)

# Configure your data source
extension_config = dict(
    dataSources=[
        {
            "type": "AzureCognitiveSearch",
            "parameters": {
                "endpoint": azure_search_endpoint,
                "key": azure_search_key,
                "indexName": azure_search_index,
            },
        }
    ]
)


def main(text: str):

    try:

        response = client.chat.completions.create(
            model=azure_oai_deployment,
            temperature=0.05,
            n=1,
            max_tokens=4096,
            messages=[
                {
                    "role": "system",
                    "content": """
            Beantworte Fragen zu einem Index, der Anforderungen zum barrierefreien Bauen sowie den entsprechenden Kosten und Fördermöglichkeiten enthält.

            Das Modell soll präzise, relevante und durchdachte Antworten geben, die aus den bereitgestellten Informationen zum Index hervorgehen. Falls eine Frage nicht eindeutig beantwortet werden kann, soll das Modell klarstellen, welche Informationen fehlen, und gegebenenfalls Vorschläge machen, wie die Antwort gefunden werden kann.

            # Schritte

            1. **Frage verstehen**:
            - Analysiere die Frage und identifiziere, ob sie sich auf Anforderungen, Kosten, Fördermöglichkeiten oder eine Kombination dieser Aspekte bezieht.
            - Prüfe, ob die Frage auf konkrete Daten aus dem Index verweist oder allgemeiner formuliert ist.

            2. **Daten aus dem Index extrahieren**:
            - Suche nach relevanten Informationen, um die Frage basierend auf dem Index zu beantworten.
            - Falls die fragliche Information nicht im Index vorhanden ist, notiere dies und erkläre den Mangel.

            3. **Antwort strukturieren**:
            - Beginne mit einer kurzen Kernantwort.
            - Füge eine detailliertere Erklärung hinzu, falls notwendig: z. B. Anforderungen an barrierefreies Bauen, geschätzte Kosten oder Hinweise zu Förderprogrammen.
            - Verweise gegebenenfalls auf zusätzliche Informationen oder Schritte, die folgen könnten.

            4. **Präzision sicherstellen**:
            - Überprüfe, ob die bereitgestellte Antwort eindeutig und relevant ist.
            - Vermeide Vermutungen, wenn notwendige Informationen fehlen, und bleibe faktenbasiert.

            # Ausgabeformat

            Die Antworten müssen als strukturierter, erläuternder Text formuliert sein und in klaren Abschnitten gegliedert werden:

            1. **Kernantwort**: Kurz und prägnant.
            2. **Erklärung**: Falls notwendig, Detailinformationen mit Bezug auf Anforderungen, Kosten, Fördermöglichkeiten oder Indexreferenzen.
            3. **Empfehlungen/Weiteres Vorgehen**: Vorschläge für zusätzliche Informationsquellen oder Maßnahmen, wenn die Antwort nicht vollständig gegeben werden kann.

            Beispiel:

            - **Frage**: _Welche Anforderungen gibt es an den Einbau eines barrierefreien Badezimmers, und welche Kosten sind zu erwarten?_
            - **Antwortstruktur**:
                1. **Kernantwort**: Die Anforderungen für ein barrierefreies Badezimmer umfassen unter anderem ausreichende Bewegungsflächen, Haltegriffe sowie einen bodengleichen, rutschfesten Duschbereich. 

                2. **Erklärung**: Nach dem Index (Kapitel X, Abschnitt Y) müssen Bewegungsflächen mindestens X m² umfassen, und Materialien müssen rutschfest gemäß Norm Z sein. Die geschätzten Kosten für grundlegende Maßnahmen beginnen ab [Betrag] € und können je nach Ausstattung variieren. Regionale Abweichungen sowie spezielle Anforderungen könnten hinzukommen.

                3. **Fördermöglichkeiten**: Es existieren Förderprogramme durch [Institution A] mit Zuschüssen von bis zu X %.  

                4. **Weiteres Vorgehen**: Für detaillierte Planungen oder Abstimmungen mit Förderstellen wird ein Beratungsgespräch empfohlen.

            # Beispiele

            ### Beispiel 1

            **Frage**: _Welche Fördermöglichkeiten gibt es für barrierefreies Bauen in Deutschland?_
            **Antwortstruktur**:
            1. **Kernantwort**: In Deutschland gibt es Fördermöglichkeiten durch KfW-Bank sowie regionale Programme.

            2. **Erklärung**: Die KfW-Bank bietet Kredite und Zuschüsse für umfassende Maßnahmen zur Barrierefreiheit (z. B. "Altersgerecht Umbauen"-Programm). Zuschüsse bis zu 6.250 € pro Wohneinheit sind möglich. Auf Länderebene können weitere Förderungen beantragt werden, die je nach Region und Maßnahme variieren.

            3. **Empfehlungen/Weiteres Vorgehen**: Spezielle Anforderungen und Regelungen sollten mit den zuständigen regionalen Förderstellen geprüft werden (z. B. [Institution] in [Bundesland]).

            ### Beispiel 2

            **Frage**: _Welche Anforderungen gibt es an eine barrierefreie Hauseingangstür?_
            **Antwortstruktur**:
            1. **Kernantwort**: Anforderungen umfassen eine lichte Breite von mindestens 90 cm, eine schwellenlose Gestaltung und eine einfache Bedienbarkeit.

            2. **Erklärung**: Nach dem Index werden Türen mit einem maximalen Schwellenniveau von X mm und einer automatisierten Öffnung empfohlen, insbesondere bei Personen mit eingeschränkter Mobilität. Norm [DIN/Standardname] ist hier anwendbar.

            3. **Weiteres Vorgehen**: Herstellerangaben zu zertifizierten barrierefreien Türen und Montagevorschriften könnten zusätzliche Details liefern.


            # Hinweise

            - **Grenzen**: Wenn der Index unvollständig ist, klar kommunizieren, wie laut verfügbaren Quellen Abhilfe geschaffen werden könnte (z. B. konsultieren eines Fachexperten, regionale Gesetzgebung).
            - **Flexibilität:** Antworten an spezifische Kontexte anpassen, falls in der Frage besondere Details zum Bauvorhaben angegeben sind.
                """,
                },
                {"role": "user", "content": text},
            ],
            extra_body=extension_config,
        )

        print("rag")
        return response.choices[0].message.content

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    # main("Wie kann der Zugang zu einer Wohnung verbessert werden?")
    # print(main("Welche Fördermöglichkeiten gibt es für barrierefreies Bauen in Deutschland?"))

    # print(main("Gib eine ausfühliche Zusammenfassung der Anforderungen an das barrierefreihe Bauen, gehe dabei speziell auf die vorgeschriebenen Maße ein und bilde die jede Kategorie mit den wichtigsten Kriterien ab."))
    print(
        main(
            "Gib eine ausfühliche Zusammenfassung der Fördermaßnahmen für altersgerechte oder barrierefreie Umbaumaßnahmen von Wohnbebäuden, gehe dabei auf jede genannt Kategorie ein und beschreibe die wichtigsten Punkte."
        )
    )
    # print(main("Gib eine ausfühliche Zusammenfassung der Durchschnittskosten, beziehungsweise der Preise, die bei möglichen barrierefreien Umbaumaßnahmen anfallen können. Gehe dabei auf die jede genannte Kategorien ein und beschreibe die wichtigsten Punkte."))
