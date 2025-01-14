import base64
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import converter_cvdw as c_cv

load_dotenv()

client: AzureOpenAI = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
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

def control_guidelines(image_path, metadata):
    base64_image = encode_image(image_path)
    c_cv.call_vision(image_path, "metadata_ocr")
    c_cv.draw_polygons_around_words(image_path, "metadata_ocr.json","metadata_text_highlighted.png", 0.5)
    guideline_file = open("Guidelines/DIN 18040.txt", "r") 
    guidelines = guideline_file.read()
    cost_information_file = open("Guidelines/Kostenaufstellung.txt", "r")
    cost_information = cost_information_file.read()
    subsidy_information_file = open("Guidelines/Fördermöglichkeiten.txt", "r")
    subsidy_information = subsidy_information_file.read()

    messages = [{
        "role": "system", "content": """
            You are specialised in the analysis of age-appropiate living. You are presented a floor plan and an analysis with information about rooms, doors and measurements.
            Your task is to evaluate the apartment based on the given guidelines and point out good and bad things that might impact age-appropiate living. 
            Give recomendations of small changes, that will improve the apartment in the given aspects.
            You have the opportunity to move the non load-bearing walls if that makes rooms like the bathroom larger and more accesible.
            Give an evaluation on the meaningfullness of that approach.
             
            After that give recommendations based on the possible services mentioned in the cost information and calculate an estimated price of them.
            
            You are given information about possible subsidies, try and provide information about them in the recommendation.
            Please give your output in german.
    """}, 
    {
        "role": "user", "content": [
                {"type": "text", "text": "Analyze this floor plan image and provide the information as specified."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                {"type": "text", "text": "This is the provided information" +  metadata },
                {"type": "text", "text": "This is the provided guideline" + guidelines},
                {"type": "text", "text": "This is the provided cost information" + cost_information},
                {"type": "text", "text": "This is the provided subsidy information" + subsidy_information}
                ]
    }
    ]

    final_response = query_gpt40(messages)
    return final_response
