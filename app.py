import streamlit as st
from PIL import Image
import plotly.graph_objects as go
import numpy as np
import fitz  # PyMuPDF für PDF-Dateien

# Überschrift
st.title("2D-Grundriss zu 3D-Darstellung")

# Datei-Upload
uploaded_file = st.file_uploader("Lade eine PDF oder JPEG Datei mit einem Grundriss hoch", type=["jpeg", "jpg", "pdf"])

# Dateiinhalt anzeigen und extrahieren
if uploaded_file is not None:
    img = None
    
    # Für PDF-Dateien extrahieren wir ein Bild der ersten Seite
    if uploaded_file.name.endswith(".pdf"):
        doc = fitz.open(uploaded_file)
        page = doc.load_page(0)  # Lade die erste Seite
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        st.image(img, caption="PDF-Grundriss als Bild", use_column_width=True)
        
    # Für JPEG-Dateien direkt das Bild anzeigen
    elif uploaded_file.name.endswith((".jpg", ".jpeg")):
        img = Image.open(uploaded_file)
        st.image(img, caption="JPEG-Grundriss", use_container_width=True)
    
    # Wenn das Bild extrahiert wurde, weiter mit der 3D-Darstellung
    if img:
        st.subheader("3D-Darstellung des Grundrisses")
        
        # Wir nehmen das Bild und fügen es auf eine 3D-Fläche, als Textur, ein
        # Konvertiere das Bild in ein Array für die Textur
        img_array = np.array(img)
        
        # Erstellen eines 3D-Modells mit Plotly
        fig = go.Figure(data=[go.Surface(
            z=np.zeros_like(img_array),  # Die Z-Achse ist 0, da wir ein flaches Bild als Grundlage verwenden
            surfacecolor=img_array[:, :, 0],  # Verwende nur die roten Farbkanalwerte als Textur (für die Farben)
            colorscale='gray',  # Farbskala für Textur
            colorbar=dict(title="Helligkeit")
        )])
        
        fig.update_layout(
            title="3D Darstellung des Grundrisses",
            scene=dict(
                xaxis_title="X-Achse",
                yaxis_title="Y-Achse",
                zaxis_title="Z-Achse"
            ),
            scene_camera=dict(
                eye=dict(x=1.5, y=1.5, z=1)
            )
        )
        
        # Zeige die 3D-Darstellung an
        st.plotly_chart(fig)

# streamlit run app.py in Terminal