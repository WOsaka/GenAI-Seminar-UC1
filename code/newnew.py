import base64
import os
from openai import AzureOpenAI
import openai
from autogen import ConversableAgent
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import zipfile
import atexit

# Lade Umgebungsvariablen
load_dotenv()

# Setze den OpenAI-API-Schlüssel und Azure-API-Schlüssel
client: AzureOpenAI = AzureOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    api_version=os.environ.get("OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("OPENAI_API_ENDPOINT"),
)

# Azure Search Client für RAG
search_client = SearchClient(
    endpoint=os.environ.get("AI_SEARCH_ENDPOINT"),
    index_name="vector-1733605458495",
    credential=AzureKeyCredential(os.environ.get("AI_SEARCH_API_KEY")),
)

# Konfiguration des LLM
llm_config = {
    "model": "gpt-4o-mini",
    "api_key": os.environ.get("OPENAI_API_KEY"),
    "temperature": 0.8,
}

def create_zip_file(zip_filename, files_to_zip):
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in files_to_zip:
            zipf.write(file, os.path.basename(file))

def ask_gpt(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=4096,
            n=1,
            temperature=0.05,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fehler bei der Kommunikation mit GPT: {str(e)}"

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def generate_embeddings(texts):
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=texts,
    )
    return [embedding["embedding"] for embedding in response["data"]]

def search_vector(query, top_k=5):
    query_embedding = generate_embeddings([query])[0]
    results = search_client.search(
        search_text="*",
        vector=query_embedding,
        vector_configuration_name="vectorSearchConfig",
        top=top_k,
    )
    return results

def on_close():
    # Add logic for cleaning up resources
    pass

def main():
    atexit.register(on_close)

    UPLOAD_FOLDER = 'uploads'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    st.title('Image Upload and Chatbot App')

    tab1, tab2 = st.tabs(["Bildverarbeitung", "Chatbot"])

    with tab1:
        st.header("Bildverarbeitung")
        uploaded_file = st.file_uploader("Wählen Sie ein Bild aus...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            filename = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(filename, "wb") as f:
                f.write(uploaded_file.getbuffer())

            img = Image.open(filename)
            st.image(img, caption='Hochgeladenes Bild', use_column_width=True)

            base64_image = encode_image(filename)
            task = """Your task is to analyze the floor plan and provide the JSON representation of rooms and their coordinates."""
            
            architect = ConversableAgent(
                name="architect",
                system_message=task,
                llm_config=llm_config,
            )

            response = architect.generate_reply(
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this floor plan image and provide the JSON representation of rooms.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        }
                    ],
                }]
            )

            st.write(response)

    with tab2:
        st.header("Chatbot")
        
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "system", "content": "Du bist ein hilfreicher Assistent."}]
        
        def handle_input():
            user_input = st.session_state["user_input"]
            if user_input:
                st.session_state["messages"].append({"role": "user", "content": user_input})

                search_results = search_vector(user_input)

                sources_formatted = "\n".join(
                    [f'{document["title"]}:{document["chunk"]}' for document in search_results]
                )

                sme = ConversableAgent(
                    name="sme",
                    system_message=user_input,
                    llm_config=llm_config,
                )

                reply = sme.generate_reply(
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Answer the following using the provided sources:\n{sources_formatted}"
                            }
                        ],
                    }]
                )

                st.session_state["messages"].append({"role": "assistant", "content": reply})
                st.session_state["user_input"] = ""

        st.text_input(
            "Stellen Sie eine Frage:",
            key="user_input",
            on_change=handle_input
        )

        for message in reversed(st.session_state["messages"]):
            if message["role"] == "user":
                st.markdown(f"<div style='text-align: right;'><strong><em>Du:</em></strong> <em>{message['content']}</em></div>", unsafe_allow_html=True)
            elif message["role"] == "assistant":
                st.markdown(f"**Bot:** {message['content']}", unsafe_allow_html=True)

        if st.button("Konversation löschen"):
            st.session_state["messages"] = [{"role": "system", "content": "Du bist ein hilfreicher Assistent."}]

if __name__ == "__main__":
    main()
