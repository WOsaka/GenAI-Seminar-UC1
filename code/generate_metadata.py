import base64
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import converter_cvdw as c_cv
import control_guidelines
load_dotenv()

client: AzureOpenAI = AzureOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    api_version=os.environ.get("OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("OPENAI_API_ENDPOINT")
)

def query_gpt40(
    messages: list[dict[str, str]],
) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens= 4096,
        n=1,
        temperature=0.05,
    )
    if response.choices[0].message.content:
        return response.choices[0].message.content.strip()
    return ""

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    


def extract_metadata(image_path):
    base64_image = encode_image(image_path)
    c_cv.call_vision(image_path, "metadata_ocr")
    c_cv.draw_polygons_around_words(image_path, "metadata_ocr.json","metadata_text_highlighted.png", 0.5)
    with open("metadata_ocr.json") as json_file:
        json_data = json.load(json_file)
    messages = [{
        "role": "system", "content": """
            You are an experienced floor plan analyst. Your task is to analyse the given floor plan and extract the  following informations:
            What rooms are shown, give the name and the size in m² and the number of windows. 
            If the size is not mentioned estimate it using the provided measurements on the outside of the plan.
            Every room has a length and width, retrieve one value on the horizontal scale and one on the vertical scale. The room can not have 2 measurements from the same side of the picture.
            If you can not find any measurement, try to estimate them in relation to other rooms. 
            It is possible that a combination of multiple measurements on the outside is necessary, use this for the balcony as it is wider than the living room.
            Measurements can include 4 digits, meaning half a cm.
            If a measurement is equal to 2.07m that is a door and should be ignored. Try to find other measurements.
            Always include the measurements in your answer.
            The bathroom has a measurement of 2.705m x 2.175m.
            Analyse the hallways and give an exact measurement of their width.
            Analyse the doors and give the measurement of them. Every door has 2 values, the smaller one is the width and the larger one is the height.
            Where is the entrance? Is it a door or an elevator or stairs? 
            Analyse the walls and their measurements, consider a wall with the size of 11.5 as not load-bearing. Give information which walls are load-bearing.

            Give your answer in german.
    """}, 
    {
        "role": "user", "content": [
                {"type": "text", "text": "Analyze this floor plan image and provide the information as specified."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
    }
    ]

    final_response = query_gpt40(messages)
    return final_response




# guideline_file = open("Guidelines/DIN 18040.txt", "r") 
# guidelines = guideline_file.read()
# cost_information_file = open("Guidelines/Kostenaufstellung.txt", "r")
# cost_information = cost_information_file.read()
# response = extract_metadata("Neue Grundrisse/D-Str/D-Str_Obergeschoss.jpg")
# print(f"GPT-40 response: {response}")
# evaluation = control_guidelines.control_guidelines("Neue Grundrisse/D-Str/D-Str_Obergeschoss.jpg", response)
# print(f"Guideline Evaluation: {evaluation}")
#control = control_metadata("Neue Grundrisse/D-Str/D-Str_Obergeschoss.jpg", response)

# response = extract_metadata("pipeline/2.1_text_added.png")
# control = control_metadata("pipeline/2.1_text_added.png", response)

#response = extract_metadata("Grundriss Beispiele/Beispiel_Niklas.jpg")



#print(f"GPT-40 control: {control}")

