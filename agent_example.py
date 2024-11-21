import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from autogen import ConversableAgent
load_dotenv()
 
deployment_name = 'gpt-4o-mini'


llm_config = {
    "model":  deployment_name,
    "api_key": os.environ.get("OPENAI_API_KEY"),
    "azure_endpoint": os.environ.get("OPENAI_AZURE_ENDPOINT"),
    "api_type": "azure", 
    "api_version": os.environ.get("OPENAI_API_VERSION"),
    "temperature": 0.1
}

image_path = "GenAI-Seminar-UC1\Grundriss Beispiele\Grundriss_02_OG.jpg"

task = '''
       Task: You are a Python coding assistant tasked with generating a CAD floor plan in DXF format using the ezdxf library. Your task is to take a given image of a floor plan (manually interpreted or programmatically analyzed dimensions) and create an accurate representation in DXF format. Follow these steps:

    Input Details:
        The image of the floor plan will include rooms with approximate dimensions (e.g., width, height, and positions).
        Each room will be labeled with its name, area, and key attributes.

    Key Requirements:
        Use ezdxf to create the DXF file.
        Each room must be represented as a rectangle with its corresponding dimensions.
        Room names and other text annotations must be positioned manually at user-defined coordinates relative to the room.

    Steps for Implementation:
        Manually define room details (e.g., coordinates, dimensions, and text positions).
        Use the add_lwpolyline function to draw rectangles for each room.
        Use the add_text function to label each room, ensuring the text is placed accurately using the "insert" DXF attribute.

    Output Requirements:
        Save the generated DXF file with a user-specified filename, ensuring all dimensions and annotations are visible and correctly placed.

    Example Implementation: Here is a Python script example of how to generate the DXF file using the ezdxf library:

import ezdxf

def create_floor_plan_dxf(file_name, rooms):
    """
    Create a DXF file for a floor plan based on room details.

    Args:
        file_name (str): Name of the output DXF file.
        rooms (list): A list of dictionaries, each containing:
            - name (str): Room name
            - x, y (float): Bottom-left corner coordinates of the room
            - width, height (float): Dimensions of the room
            - text_pos (tuple): Coordinates for the room name text

    Returns:
        None
    """
    # Create a new DXF document
    doc = ezdxf.new()
    msp = doc.modelspace()

    # Draw the rooms
    for room in rooms:
        x, y = room["x"], room["y"]
        width, height = room["width"], room["height"]
        text_x, text_y = room["text_pos"]

        # Draw the room as a rectangle
        msp.add_lwpolyline([
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
            (x, y)
        ], close=True)

        # Add the room name at the specified position
        msp.add_text(
            room["name"],
            dxfattribs={'height': 0.25}  # Text height
        ).set_dxf_attrib("insert", (text_x, text_y))

    # Save the DXF file
    doc.saveas(file_name)

    Usage Example: The function create_floor_plan_dxf can be used with the following example input:

rooms = [
    {"name": "Wohnzimmer", "x": 0, "y": 4.0, "width": 4.0, "height": 6.5, "text_pos": (2.0, 7.25)},
    {"name": "Windfang", "x": 0, "y": 2.8, "width": 4.0, "height": 1.2, "text_pos": (2.0, 3.4)},
    {"name": "Flur", "x": 0, "y": 2.0, "width": 4.0, "height": 0.8, "text_pos": (2.0, 2.4)},
    {"name": "Bad", "x": 3.0, "y": 0, "width": 1.0, "height": 2.0, "text_pos": (3.5, 1.0)},
    {"name": "Küche", "x": 0, "y": 0, "width": 3.0, "height": 2.0, "text_pos": (1.5, 1.0)},
    {"name": "Esszimmer", "x": 0, "y": -3.0, "width": 4.0, "height": 3.0, "text_pos": (2.0, -1.5)},
]

create_floor_plan_dxf("floor_plan.dxf", rooms)

        '''

prompt_engineer = ConversableAgent(
    name = "prompt_engineer",
    system_message="You are a Prompt Engineer. You are able to develop a prompting strategy that is suitable for the given task. Give a clear and structured prompt that allows gpt-4o-mini to solve my task"
        "Explain the choice of prompt and how it works",
    llm_config= llm_config
)
reply = prompt_engineer.generate_reply(messages=[{"content": task, "role": "user"}])

print(reply)

critic = ConversableAgent(
    name = "critic",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    system_message="You are a critic. You review the work of the prompt engineer and provide constructive feedback to help improve the quality of the provided prompt.",
    llm_config= llm_config
)
res = critic.initiate_chat(
    recipient=prompt_engineer,
    message=task,
    max_turns=2,
    summary_method="last_msg"
)
