import streamlit as st
from PIL import Image
import os
import chat_gpt
import ezdxf_creator
import dxf_viewer

# Ensure the upload directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Title of the application
st.title('Image Upload and Processing App')

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
    st.image(img, caption='Uploaded Image', use_column_width=True)

    # Convert image to grayscale
    converted_img = img.convert('L') 
    processed_filename = os.path.join(UPLOAD_FOLDER, "processed_" + uploaded_file.name)
    converted_img.save(processed_filename)
    response = chat_gpt.chat_with_gpt(processed_filename)
        
    ezdxf_creator.create_floor_plan(chat_gpt.extract_rooms(response), "app_created_floorplan.dxf")
    dxf_viewer.convert_dxf_to_png("app_created_floorplan.dxf")

    # Display the processed image
    st.image("converted.png", caption='Generated CAD file', use_column_width=True)
    #st.image(converted_img, caption='Processed Image', use_column_width=True)

    # Provide a download link for the processed image
    with open(processed_filename, "rb") as file:
        btn = st.download_button(
            label="Download Processed Image",
            data=file,
            file_name="processed_" + uploaded_file.name,
            mime="image/png"
        )