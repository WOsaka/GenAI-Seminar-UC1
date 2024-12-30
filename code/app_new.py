import streamlit as st
from PIL import Image
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import converter_ai as c_ai
import converter_cv as c_cv
import atexit
import zipfile
load_dotenv()

# Setze deinen OpenAI-API-Schlüssel hier ein
client: AzureOpenAI = AzureOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    api_version=os.environ.get("OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("OPENAI_API_ENDPOINT"),
)

def create_zip_file(zip_filename, files_to_zip):
    # Create a ZIP file
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in files_to_zip:
            zipf.write(file, os.path.basename(file))

# Funktion, die beim Schließen der App ausgeführt wird
def on_close():
    c_ai.clear_folder(r"C:\Users\Oskar\Documents\Seminar\GenAI-Seminar-UC1\uploads")

def ask_gpt(messages):
    """Sendet die Unterhaltung an GPT und erhält eine Antwort."""
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

def main():
    # Registriere die Funktion zum Ausführen bei App-Schließung
    atexit.register(on_close)

    # Ensure the upload directory exists
    UPLOAD_FOLDER = 'uploads'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Title of the application
    st.title('RePlanIt')

    # Erstelle Tabs für verschiedene Funktionen
    tab1, tab2, tab3 = st.tabs(["Anleitung", "Bildverarbeitung", "Chatbot"])

    with tab1: 
        st.header("Anleitung")

    with tab2:
        st.header("Bildverarbeitung")
        # Upload image file
        uploaded_file = st.file_uploader("Wählen Sie ein Bild aus...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            # Save the uploaded file
            filename = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(filename, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Open the uploaded image
            img = Image.open(filename)

            # Display the original image
            st.image(img, caption='Hochgeladenes Bild', use_column_width=True)

            # Convert image
            # c_ai.main(filename)
            c_cv.main(filename)

            # Create zip file for downloading
            files_to_zip = [r'uploads\output.png', r'uploads\output.dxf']
            zip_filename = r'uploads\output.zip'
            create_zip_file(zip_filename, files_to_zip)

            # Open the processed image
            converted_img = Image.open(r"uploads\output.png")

            # Display the image in Streamlit
            st.image(converted_img, caption='Verarbeitetes Bild', use_column_width=True)

            # Provide a download link for the processed image
            with open(r"uploads\output.zip", "rb") as file:
                btn = st.download_button(
                    label="Verarbeitetes Bild herunterladen",
                    data=file,
                    file_name="processed_file.zip",
                    mime="application/zip"
                )

    with tab3:
        st.header("Chatbot")
        # Chatbot-Konversation
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "system", "content": "Du bist ein hilfreicher Assistent."}]

        # Zeige die Konversation an (neueste zuerst)
        for message in (st.session_state["messages"]):
            if message["role"] == "user":
                # Benutzertext nach rechts einrücken und kursiv darstellen
                st.markdown(f"<div style='text-align: right;'><strong><em>Du:</em></strong> <em>{message['content']}</em></div>", unsafe_allow_html=True)
            elif message["role"] == "assistant":
                # Antwort des Chatbots ohne kursiv
                st.markdown(f"**Bot:** {message['content']}", unsafe_allow_html=True)

        # Eingabefeld für den Benutzer unter den Nachrichten platzieren
        def handle_input():
            user_input = st.session_state["user_input"]
            if user_input:
                # Füge Benutzer-Eingabe zu den Nachrichten hinzu
                st.session_state["messages"].append({"role": "user", "content": user_input})

                # Anfrage an GPT senden und Antwort erhalten
                response = ask_gpt(st.session_state["messages"])
                st.session_state["messages"].append({"role": "assistant", "content": response})

                # Eingabe zurücksetzen
                st.session_state["user_input"] = ""

        st.text_input(
            "Stellen Sie eine Frage:",
            key="user_input",
            on_change=handle_input
        )

        # Button, um die Konversation zurückzusetzen
        if st.button("Konversation löschen"):
            st.session_state["messages"] = [{"role": "system", "content": "Du bist ein hilfreicher Assistent."}]

if __name__ == "__main__":
    main()
