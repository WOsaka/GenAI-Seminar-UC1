
import streamlit as st
from PIL import Image
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import converter_ai as c_ai
import converter_cv as c_cv
import atexit
import zipfile
load_dotenv()

# Setze deinen OpenAI-API-Schlüssel hier ein
client: AzureOpenAI = AzureOpenAI(
    api_key="Dp7o9ZYn0OkoLNJOmBnBDCHq3ncTDYcwY0AYWjxC6uI13PnGtzOXJQQJ99ALACfhMk5XJ3w3AAABACOGiRbm",
    api_version="2023-03-15-preview",
    azure_endpoint="https://azure-openai-uc1.openai.azure.com/",

  #  api_key=os.environ.get("OPENAI_API_KEY"),
   # api_version=os.environ.get("OPENAI_API_VERSION"),
    #azure_endpoint=os.environ.get("OPENAI_API_ENDPOINT"),

#OPENAI_API_KEY=Dp7o9ZYn0OkoLNJOmBnBDCHq3ncTDYcwY0AYWjxC6uI13PnGtzOXJQQJ99ALACfhMk5XJ3w3AAABACOGiRbm
#OPENAI_API_ENDPOINT="https://azure-openai-uc1.openai.azure.com/"
#OPENAI_API_VERSION=2023-03-15-preview
)

def ask_gpt(messages):
    """Sendet die Unterhaltung an GPT und erhält eine Antwort."""
    try:
        response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens= 4096,
        n=1,
        temperature=0.05,
    )
   
        return response.choices[0].message.content
    except Exception as e:
        return f"Fehler bei der Kommunikation mit GPT: {str(e)}"""
    
response = ask_gpt([{"role": "system", "content": "Du bist ein hilfreicher Assistent."}])

print(response)