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
        Your task is: take the given floor plan in the variable image_path and transform it into a cad-file with ezdxf.
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
