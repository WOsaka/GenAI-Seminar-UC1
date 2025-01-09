import streamlit as st
from PIL import Image
import os
import converter_ai as c_ai
import converter_cv as c_cv
import atexit
import zipfile


def create_zip_file(zip_filename, files_to_zip):
    # Create a ZIP file
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for file in files_to_zip:
            zipf.write(file, os.path.basename(file))


# Funktion, die beim Schließen der App ausgeführt wird
def on_close():
    c_ai.clear_folder(r"C:\Users\Oskar\Documents\Seminar\GenAI-Seminar-UC1\uploads")


def main():
    # Registriere die Funktion zum Ausführen bei App-Schließung
    atexit.register(on_close)

    # Ensure the upload directory exists
    UPLOAD_FOLDER = "uploads"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Title of the application
    st.title("Image Upload and Processing App")

    # Upload image file
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Save the uploaded file
        filename = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(filename, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Open the uploaded image
        img = Image.open(filename)

        # Display the original image
        st.image(img, caption="Uploaded Image", use_column_width=True)

        # Convert image
        # c_ai.main(filename)
        c_cv.main(filename)

        # Create zip file for downloading
        files_to_zip = [r"uploads\output.png", r"uploads\output.dxf"]
        zip_filename = r"uploads\output.zip"
        create_zip_file(zip_filename, files_to_zip)

        # Open the processed image
        converted_img = Image.open(r"uploads\output.png")

        # Display the image in Streamlit
        st.image(converted_img, caption="Processed Image", use_column_width=True)

        # Provide a download link for the processed image
        with open(r"uploads\output.zip", "rb") as file:
            btn = st.download_button(
                label="Download Processed Image",
                data=file,
                file_name="processed_file.zip",
                mime="application/zip",
            )


if __name__ == "__main__":
    main()
