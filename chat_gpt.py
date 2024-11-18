import base64
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()
 
client: AzureOpenAI = AzureOpenAI(
    api_key=os.environ.get("5ndjVayyOA1ZVJ2ShjkY3Zl1RcJPeLfxsammQIqPs2uUl0PczN7XJQQJ99AKACfhMk5XJ3w3AAABACOGHq1N"),
    api_version=os.environ.get("2024-02-15-preview"),
    azure_endpoint=os.environ.get("OPENAI_AZURE_ENDPOINT"),
)

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

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

def main(image_path = '2-room-floor.jpg'):
    base64_image = encode_image(image_path)
    
    messages = [
        {
            "role": "system",
            "content": """You are an AI assistant specialized in analyzing building floor plans and converting them into structured dictionary. Your task is to:

    1. Identify each distinct room or area in the floor plan image.
    2. Assign a name to each room based on its apparent function or any visible labels.
    3. Convert the layout into a 2D coordinate system
    - Use appropriate scale to represent the relative sizes accurately

    Output the analysis as a dict  with the following structure:
    {
        "roomName1": [(x1, y1), (x2, y2), (x3, y3), (x4, y4)],
        "roomName2": [(x1, y1), (x2, y2), (x3, y3), (x4, y4)],
        // ... other rooms ...
    }
    Do not send ```json ... just send the text following the ouput structure
    Ensure that every room is showed. Cant happend that a room hide the rest.
    Each room should be represented by four coordinate pairs, starting from the top-left corner and moving clockwise.
    If a room has more than four corners, approximate it with four main corners.
    If you're unsure about a room name, use a descriptive term (e.g., "UnknownRoom1").
    Provide only the JSON output, no additional explanations."""
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this floor plan image and provide the JSON representation of rooms and their coordinates as specified."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }
    ]

    final_response = query_gpt40(messages)
    print(f"GPT-40 response: {final_response}")
    return final_response

if __name__ == "__main__":
    main()