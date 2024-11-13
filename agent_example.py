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
    "api_version": os.environ.get("OPENAI_API_VERSION")

}


task = '''
        Write a concise blogpost about the positive aspects of the job as an architect. Make sure the blogpost is within 100 words.
        '''

writer = ConversableAgent(
    name = "writer",
    system_message="You are a writer. You write engaging and concise " 
        "blogpost (with title) on given topics. You must polish your "
        "writing based on the feedback you receive and give a refined "
        "version. Only return your final work without additional comments.",
    llm_config= llm_config
)
reply = writer.generate_reply(messages=[{"content": task, "role": "user"}])

print(reply)

critic = ConversableAgent(
    name = "critic",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    system_message="You are a critic. You review the work of the writer and provide constructive feedback to help improve the quality of the content.",
    llm_config= llm_config
)
res = critic.initiate_chat(
    recipient=writer,
    message=task,
    max_turns=2,
    summary_method="last_msg"
)
