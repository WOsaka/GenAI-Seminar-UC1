import streamlit as st
from PIL import Image
import os
import base64
from io import BytesIO
from openai import AzureOpenAI
from dotenv import load_dotenv
import converter_ai as c_ai
import converter_cv as c_cv
import atexit
import zipfile
import generate_metadata
import control_guidelines
import path_cleaner

# Page configuration
st.set_page_config(page_title="RePlanIt", layout="wide")

# Lade Umgebungsvariablen
load_dotenv()

# Setze deinen OpenAI-API-Schlüssel hier ein
client: AzureOpenAI = AzureOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    api_version=os.environ.get("OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("OPENAI_API_ENDPOINT"),
)

def create_zip_file(zip_filename, files_to_zip):
    """Erstellt eine ZIP-Datei mit angegebenen Dateien."""
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in files_to_zip:
            zipf.write(file, os.path.basename(file))

def on_close():
    """Funktion, die beim Schließen der App ausgeführt wird."""
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

def image_to_base64(img_path):
    """Konvertiert ein Bild in Base64."""
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def main():
    # Registriere die Funktion zum Ausführen bei App-Schließung
    atexit.register(on_close)

    # Ensure the upload directory exists
    UPLOAD_FOLDER = 'uploads'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    guideline_input = "Guideline ist noch nicht erstellt"
    # Logo in der oberen linken Ecke hinzufügen
    logo_path = "logo.png"  # Pfad zum Logo
    if os.path.exists(logo_path):
        base64_image = image_to_base64(logo_path)
        logo_html = f"""
        <div style="position: absolute; top: 0px; right: 10px; z-index: 1000;">
            <img src="data:image/png;base64,{base64_image}" alt="RePlanIt Logo" style="width: 150px;">
        </div>
        """
        st.markdown(logo_html, unsafe_allow_html=True)

    # Inject custom CSS to move the tabs down
    st.markdown(
        """
        <style>
        div.streamlit-tabs ul {
            margin-top: 1000px; /* Adjust the distance from the top */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Titel
    st.title('RePlanIt')

    # Tabs für die Funktionen
    tab1, tab2, tab3 = st.tabs(["Anleitung", "Bildverarbeitung", "Chatbot"])

    with tab1:
        st.header("Anleitung")
        st.write("Willkommen bei RePlanIt! Hier können Sie Bilder hochladen, um Baupläne zu erstellen, "
                 "und mit unserem Chatbot altersgerechte Anpassungen planen.")

    with tab2:
        st.header("Bildverarbeitung")
        # Upload image file
        uploaded_file = st.file_uploader("Wählen Sie ein Bild aus...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            filename = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(filename, "wb") as f:
                f.write(uploaded_file.getbuffer())

            img = Image.open(filename)
            st.image(img, caption='Hochgeladenes Bild', use_column_width=True)

            c_cv.main(filename)

            files_to_zip = [r'uploads\output.png', r'uploads\output.dxf']
            zip_filename = r'uploads\output.zip'
            create_zip_file(zip_filename, files_to_zip)

            converted_img = Image.open(r"uploads\output.png")
            st.image(converted_img, caption='Verarbeitetes Bild', use_column_width=False)

            with open(r"uploads\output.zip", "rb") as file:
                st.download_button(
                    label="Verarbeitetes Bild herunterladen",
                    data=file,
                    file_name="processed_file.zip",
                    mime="application/zip"
                )
            if st.button("Bild verbessern"):
                path_cleaner.remove_noise(r"uploads\output.dxf", r"uploads\output_cleaned.dxf", min_length= 250, max_distance=0.001)
                c_cv.dxf_to_png(r'uploads\output_cleaned.dxf', r'uploads\output_cleaned.png')
                cleaned_image = Image.open(r"uploads\output_cleaned.png")
                st.image(cleaned_image, caption="Verbessertes Bild", use_column_width=False)
          

    with tab3:
        st.header("Chatbot")
        if st.button("Guidelines verarbeiten"):
            st.session_state["messages"] = [{"role": "system", "content": "Du bist ein hilfreicher Assistent."}]
            metadata = generate_metadata.extract_metadata(filename)
            guideline_input = control_guidelines.control_guidelines(filename, metadata)
            st.session_state["messages"].append({"role": "assistant", "content": metadata})
            guideline_file = open("Guidelines/DIN 18040.txt", "r") 
            guidelines = guideline_file.read()
            cost_information_file = open("Guidelines/Kostenaufstellung.txt", "r")
            cost_information = cost_information_file.read()
            st.session_state["messages"].append({"role": "system", "content": "Hier sind einige Informationen über die Wohnung" + metadata})
            st.session_state["messages"].append({"role": "system", "content": "Hier sind die relevanten Informationen zu Guidelines" + guidelines})
            st.session_state["messages"].append({"role": "system", "content": "Hier sind die relevanten Informationen zu kosten. Versuche dich hauptsächlich darauf zu beziehen." + cost_information})
            st.session_state["messages"].append({"role": "assistant", "content": guideline_input})

            
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "system", "content": "Du bist ein hilfreicher Assistent."}]
        for message in st.session_state["messages"]:
            if message["role"] == "user":
                st.markdown(
                    f"<div style='text-align: right;'><strong><em>Du:</em></strong> <em>{message['content']}</em></div>",
                    unsafe_allow_html=True,
                )
            elif message["role"] == "assistant":
                st.markdown(f"**Bot:** {message['content']}", unsafe_allow_html=True)

        def handle_input():
            user_input = st.session_state["user_input"]
            if user_input:
                st.session_state["messages"].append({"role": "user", "content": user_input})
                response = ask_gpt(st.session_state["messages"])
                st.session_state["messages"].append({"role": "assistant", "content": response})
                st.session_state["user_input"] = ""

        st.text_input(
            "Stellen Sie eine Frage:",
            key="user_input",
            on_change=handle_input
        )

        if st.button("Konversation löschen"):
            st.session_state["messages"] = [{"role": "system", "content": "Du bist ein hilfreicher Assistent."}]

       

if __name__ == "__main__":
    main()