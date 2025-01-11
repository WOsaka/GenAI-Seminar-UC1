import streamlit as st
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import fitz  # PyMuPDF für PDF-Dateien
from io import BytesIO

# Überschrift
st.title("2D-Grundriss zu 3D-Darstellung")

# Anweisung zum Hochladen
st.markdown("### Anleitung:")
st.markdown("1. Bitte lade eine PDF- oder JPEG-Datei hoch, die den Grundriss enthält.")
st.markdown(
    "2. Nach dem Upload wird das Bild angezeigt und eine 3D-Darstellung generiert."
)
st.markdown("3. Du kannst das 3D-Ergebnis anschließend herunterladen.")

# Datei-Upload
uploaded_file = st.file_uploader(
    "Lade eine PDF oder JPEG Datei mit einem Grundriss hoch",
    type=["jpeg", "jpg", "pdf"],
)

# Dateiinhalt anzeigen und extrahieren
if uploaded_file:
    img = None

    try:
        # Überprüfen, ob es sich um eine PDF handelt
        if uploaded_file.name.lower().endswith(".pdf"):
            # Für PDF-Dateien extrahieren wir ein Bild der ersten Seite
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            page = doc.load_page(0)  # Lade die erste Seite
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            st.image(img, caption="PDF-Grundriss als Bild", use_column_width=True)

        # Überprüfen, ob es sich um ein JPEG handelt
        elif uploaded_file.name.lower().endswith((".jpg", ".jpeg")):
            img = Image.open(uploaded_file)
            st.image(img, caption="JPEG-Grundriss", use_container_width=True)

        else:
            st.error(
                "Die hochgeladene Datei hat ein unbekanntes Format. Bitte lade eine PDF oder JPEG-Datei hoch."
            )

    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")
        img = None

    # Wenn das Bild erfolgreich extrahiert wurde, fahre fort
    if img:
        st.subheader("3D-Darstellung des Grundrisses")

        # Dummy-Daten erzeugen
        x = np.linspace(0, 10, 100)
        y = np.cos(x)
        data = pd.DataFrame({"x": x, "y": y})

        # Plotly-Figur erstellen
        fig = px.line(data, x="x", y="y", labels={"x": "X-Achse", "y": "Y-Achse"})

        # Figur in Streamlit anzeigen
        st.plotly_chart(fig)

        # Grafik als Datei speichern
        buffer = BytesIO()
        fig.write_image(buffer, format="png")  # Alternativ: format="svg" oder "jpeg"
        buffer.seek(0)  # Zeiger zurück zum Anfang setzen

        # Download-Button hinzufügen
        st.download_button(
            label="Download der Grafik als PNG",
            data=buffer,
            file_name="3D-Darstellung.png",
            mime="image/png",
        )

# run and streamlit run app.py in Terminal
