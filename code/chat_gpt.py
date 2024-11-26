import base64
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
import re
import ezdxf_creator
import image_drawer
load_dotenv()
 
client: AzureOpenAI = AzureOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    api_version=os.environ.get("OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("OPENAI_API_ENDPOINT"),
)

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def query_gpt40(
    messages: list[dict[str, str]],
) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens= 4096,
        n=1,
        temperature=0.05,
    )
    if response.choices[0].message.content:
        return response.choices[0].message.content.strip()
    return ""

def extract_rooms(data_string):
    try:
        # Replace tuple-like (x, y) with JSON-compatible [x, y]
        data_string = re.sub(r'\(([^)]+)\)', r'[\1]', data_string)

        # Parse the modified string as JSON
        data = json.loads(data_string)

        # Check if "rooms" key exists and return its value
        if "rooms" in data:
            return data["rooms"]
        else:
            raise ValueError("The provided string does not contain a 'rooms' key.")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parsing error: {e}")


# def main(image_path = 'GenAI-Seminar-UC1\Grundriss Beispiele\Ziel\Beispiel_01.png'):
#     base64_image = encode_image(image_path)

#     messages = [
#         {
#             "role": "system",
#             "content": """You are an AI assistant specialized in analyzing building floor plans and converting them into structured dictionary. Your task is to:

#     1. Identify each distinct room or area in the floor plan image.
#     2. Assign a name to each room based on its apparent function or any visible labels.
#     3. Convert the layout into a 2D coordinate system
#     - Use appropriate scale to represent the relative sizes accurately

#     Output the analysis as a dict  with the following structure:
#     {
#             rooms = [
#         {"name": "Wohnzimmer", "x": 0, "y": 4.0, "width": 4.0, "height": 6.5, "text_pos": (2.0, 7.25)},
#         {"name": "Windfang", "x": 0, "y": 2.8, "width": 4.0, "height": 1.2, "text_pos": (2.0, 3.4)},
#         {"name": "Flur", "x": 0, "y": 2.0, "width": 4.0, "height": 0.8, "text_pos": (2.0, 2.4)},
#         {"name": "Bad", "x": 3.0, "y": 0, "width": 1.0, "height": 2.0, "text_pos": (3.5, 1.0)},
#         {"name": "Küche", "x": 0, "y": 0, "width": 3.0, "height": 2.0, "text_pos": (1.5, 1.0)},
#         {"name": "Esszimmer", "x": 0, "y": -3.0, "width": 4.0, "height": 3.0, "text_pos": (2.0, -1.5)},
# ]
#     }
#     Do not send ```json ... just send the text following the ouput structure
#     Ensure that every room is showed. Cant happend that a room hide the rest.
#     Each room should be represented by four coordinate pairs, starting from the top-left corner and moving clockwise.
#     If a room has more than four corners, approximate it with four main corners.
#     If you're unsure about a room name, use a descriptive term (e.g., "UnknownRoom1").
#     Provide only the JSON output, no additional explanations."""
#         },
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": "Analyze this floor plan image and provide the JSON representation of rooms and their coordinates as specified."},
#                 {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
#             ]
#         }
#     ]

#     final_response = query_gpt40(messages)
#     print(f"GPT-40 response: {final_response}")

#     ezdxf_creator.create_floor_plan(extract_rooms(final_response), "other_floor_plan.dxf")
#     image_drawer.plot_rooms(extract_rooms(final_response))
#     return final_response'



# if __name__ == "__main__":
#     main()

def chat_with_gpt(image_path):
    base64_image = encode_image(image_path)

    messages=[
            {"role": "system", "content": """You are an AI assistant specialized in analyzing building floor plans and converting them into structured dictionary. Your task is to:

    1. Identify each distinct room or area in the floor plan image.
    2. Assign a name to each room based on its apparent function or any visible labels.
    3. Convert the layout into a 2D coordinate system
    - Use appropriate scale to represent the relative sizes accurately

    Output the analysis as a dict  with the following structure:
    {
            rooms = [
        {"name": "Wohnzimmer", "x": 0, "y": 4.0, "width": 4.0, "height": 6.5, "text_pos": (2.0, 7.25)},
        {"name": "Windfang", "x": 0, "y": 2.8, "width": 4.0, "height": 1.2, "text_pos": (2.0, 3.4)},
        {"name": "Flur", "x": 0, "y": 2.0, "width": 4.0, "height": 0.8, "text_pos": (2.0, 2.4)},
        {"name": "Bad", "x": 3.0, "y": 0, "width": 1.0, "height": 2.0, "text_pos": (3.5, 1.0)},
        {"name": "Küche", "x": 0, "y": 0, "width": 3.0, "height": 2.0, "text_pos": (1.5, 1.0)},
        {"name": "Esszimmer", "x": 0, "y": -3.0, "width": 4.0, "height": 3.0, "text_pos": (2.0, -1.5)},
]
    }
    Do not send ```json ... just send the text following the ouput structure
    Ensure that every room is showed. Cant happend that a room hide the rest.
    Each room should be represented by four coordinate pairs, starting from the top-left corner and moving clockwise.
    If a room has more than four corners, approximate it with four main corners.
    If you're unsure about a room name, use a descriptive term (e.g., "UnknownRoom1").
    Provide only the JSON output, no additional explanations."""
            },
            {
                "role": "user", "content": [
                {"type": "text", "text": "Analyze this floor plan image and provide the JSON representation of rooms and their coordinates as specified."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
    ]
    
    final_response = query_gpt40(messages)
    return final_response

if __name__ == "__main__":
    response = chat_with_gpt(r"Grundriss Beispiele\Beispiel_David.png")
    print(response)
    extracted_rooms = extract_rooms(response)
    print(extracted_rooms)

"""
response = chat_with_gpt('Grundriss Beispiele\Ziel\Beispiel_02.jpg')
print(f"GPT-40 response: {response}")
    
ezdxf_creator.create_floor_plan(extract_rooms(response), "other_floor_plan2.dxf")
image_drawer.plot_rooms(extract_rooms(response))
"""