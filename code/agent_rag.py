import base64
import os

import openai
from autogen import ConversableAgent
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv

load_dotenv()

deployment_name = "gpt-4o-mini"


# Temporary commented out until Azure OpenAi API is fixed
llm_config = {
    "model": deployment_name,
    "api_key": os.environ.get("OPENAI_API_KEY"),
    # "azure_endpoint": os.environ.get("OPENAI_AZURE_ENDPOINT"),
    # "api_type": "azure",
    # "api_version": os.environ.get("OPENAI_API_VERSION"),
    "temperature": 0.8,
}

image_path = "Grundriss Beispiele/wuestermarke1969.jpg"
cad_path = "uploads.png"


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


base64_image = encode_image(image_path)
cad_image = encode_image(image_path)

task = """You are an AI assistant specialized in analyzing building floor plans and converting them into structured dictionary. Your task is to:

    1. Identify each distinct room or area in the floor plan image.
    2. Assign a name to each room based on its apparent function or any visible labels.
    3. Convert the layout into a 2D coordinate system
    - Use appropriate scale to represent the relative sizes accurately

    Output the analysis as a dict  with the following structure:

            rooms = [
        {{"name": "Wohnzimmer", "x": 0, "y": 4.0, "width": 4.0, "height": 6.5, "text_pos": (2.0, 7.25)}},
        {{"name": "Windfang", "x": 0, "y": 2.8, "width": 4.0, "height": 1.2, "text_pos": (2.0, 3.4)}},
        {{"name": "Flur", "x": 0, "y": 2.0, "width": 4.0, "height": 0.8, "text_pos": (2.0, 2.4)}},
        {{"name": "Bad", "x": 3.0, "y": 0, "width": 1.0, "height": 2.0, "text_pos": (3.5, 1.0)}},
        {{"name": "Küche", "x": 0, "y": 0, "width": 3.0, "height": 2.0, "text_pos": (1.5, 1.0)}},
        {{"name": "Esszimmer", "x": 0, "y": -3.0, "width": 4.0, "height": 3.0, "text_pos": (2.0, -1.5)}},
    ]
    Do not send ```json ... just send the text following the ouput structure
    Ensure that every room is showed. Cant happend that a room hide the rest.
    Each room should be represented by four coordinate pairs, starting from the top-left corner and moving clockwise.
    If a room has more than four corners, approximate it with four main corners.
    If you're unsure about a room name, use a descriptive term (e.g., "UnknownRoom1").
    Provide only the JSON output, no additional explanations."""


architect = ConversableAgent(
    name="architect",
    system_message=task,
    llm_config=llm_config,
)

response = architect.generate_reply(
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Analyze this floor plan image and provide the JSON representation of rooms and their coordinates as specified.",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }
    ]
)

print(response)


# define the search client (AI Search)
search_client = SearchClient(
    endpoint=os.environ.get("AI_SEARCH_ENDPOINT"),
    index_name="vector-1733605458495",
    credential=AzureKeyCredential(os.environ.get("AI_SEARCH_API_KEY")),
)


# define the embedding model
def generate_embeddings(texts):
    response = openai.embeddings.create(
        model="text-embedding-ada-002",  # Embedding model
        input=texts,
    )
    return [embedding["embedding"] for embedding in response["data"]]


# define vector search engine
def search_vector(search_client, query, top_k=5):
    query_embedding = generate_embeddings([query])[0]  # Get embedding for query
    results = search_client.search(
        search_text="*",  # Use '*' to search all documents
        vector=query_embedding,  # Pass the query embedding
        vector_configuration_name="vectorSearchConfig",
        top=top_k,  # Return top-k results
    )
    return results


# Define the user Prompt

query = "Hi, I want to know the guideline for wheelchairs"

# This prompt provides instructions to the model
GROUNDED_PROMPT = f"""
You are a supbject matter expert assistant that explains guidelines based on documentation.
Answer the query using only the sources provided below in a friendly and concise bulleted manner.
Answer ONLY with the facts listed in the list of sources below.
If there isn't enough information below, say you don't know.
Do not generate answers that don't use the sources below.
Query: {query}
"""

vectorised_query = search_vector(search_client, GROUNDED_PROMPT)

# This is where RAG starts


# Retrieve the selected fields from the search index related to the question.
search_results = search_client.search(
    search_text=vectorised_query,
    top=5,
    query_type="semantic",
    semantic_fields=["text_vector"],
)
search_results = list(search_results)

# Augment
sources_formatted = "\n".join(
    [f'{document["title"]}:{document["chunk"]}' for document in search_results]
)

# Generate
# SME aka RAG Bot called sme for subject matter expert

sme = ConversableAgent(
    name="sme",
    system_message=query,
    llm_config=llm_config,
)

print(sources_formatted)

reply = sme.generate_reply(
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": GROUNDED_PROMPT.format(
                        query=query, sources=sources_formatted
                    ),
                },
            ],
        }
    ]
)

print(reply)
