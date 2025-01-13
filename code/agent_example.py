import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from autogen import ConversableAgent
import base64
load_dotenv()
 
deployment_name = 'gpt-4o-mini'


llm_config = {
    "model":  deployment_name,
    "api_key": os.environ.get("OPENAI_API_KEY"),
    "azure_endpoint": os.environ.get("OPENAI_API_ENDPOINT"),
    "api_type": "azure", 
    "api_version": os.environ.get("OPENAI_API_VERSION"),
    "temperature": 0.1
}

image_path = "Neue Grundrisse/D-Str/D-Str_Obergeschoss.jpg"

task = '''
       Task:  You are an experienced floor plan analyst. Your task is to analyse the given floor plan and extract the  following informations:
            What rooms are shown, give the name and the size in m² and the number of windows. 
            If the size is not mentioned estimate it using the provided measurements on the outside of the plan.
            If you can not find any measurement, try to estimate them in relation to other rooms.
            Measurements can include 4 digits, meaning half a cm.
            If a measurement is equal to 2.07m that is a door and should be ignored. Try to find other measurements.
            Always include the measurements in your answer.
            Analyse the hallways and give an exact measurement of their width.
            Analyse the doors and give the measurement of them. Every door has 2 values, the smaller one is the width and the larger one is the height.
            Where is the entrance? Is it a door or an elevator or stairs? 
            Analyse the walls and their measurements, consider a wall with the size of 11.5 as not load-bearing. Give information which walls are load-bearing.

        '''

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


base64_image = encode_image(image_path)

floor_plan_analyst = ConversableAgent(
    name = "floor_plan_analyst",
    system_message=task,
    llm_config= llm_config
)
reply = floor_plan_analyst.generate_reply(messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Analyze this floor plan image and provide the specialiced analysis as specified.",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },             
            ],
        }
    ])

print(reply)

critic = ConversableAgent(
    name = "critic",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    system_message="You are a critic. You review the work of the floor plan analyst and provide constructive feedback to help improve the quality of the provided work.",
    llm_config= llm_config
)
res = critic.initiate_chat(
    recipient=floor_plan_analyst,
    message=task,
    max_turns=2,
    summary_method="last_msg"
)
