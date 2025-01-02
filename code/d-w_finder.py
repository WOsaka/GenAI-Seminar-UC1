import roboflow
import json
from PIL import Image
import os
from dotenv import load_dotenv
load_dotenv()

def convert_to_jpg(input_path, output_path):
    # Öffne das Bild
    img = Image.open(input_path)
    
    # Konvertiere das Bild in RGB (JPG unterstützt keine Transparenz)
    rgb_img = img.convert('RGB')
    
    # Speichere das Bild als JPG
    rgb_img.save(output_path, 'JPEG')

def call_roboflow(image, confidence, overlap):
    api_key = os.environ.get("ROBOFLOW_API_KEY")
    rf = roboflow.Roboflow(api_key)

    project = rf.workspace().project("segmenting-a-floor-plan")
    model = project.version("1").model

    # predict on a local image
    # prediction = 
    return model.predict(image)

def save_json(data, path_to):
    # Writing JSON data to the file
    with open(path_to, 'w') as json_file:
        json.dump(data, json_file)

# Predict on a hosted image via file name
#prediction = model.predict("YOUR_IMAGE.jpg", hosted=True)

# Predict on a hosted image via URL
#prediction = model.predict("https://...", hosted=True)

def main(image=r"Neue Grundrisse\image.png"):
    convert_to_jpg(image, r"data\segment_floorplan.jpg")

    prediction = call_roboflow(r"data\segment_floorplan.jpg", 50, 50)

    # Plot the prediction in an interactive environment
    prediction.plot()

    # Convert predictions to JSON
    data = prediction.json()
    
    save_json(data, r"data\segment_floorplan.json")

if __name__ == "__main__":
    main()