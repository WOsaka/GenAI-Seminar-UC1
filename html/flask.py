from flask import Flask, request, jsonify
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

l# Lade Umgebungsvariablen
load_dotenv()

app = Flask(__name__)

client = AzureOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    api_version=os.environ.get("OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("OPENAI_API_ENDPOINT"),
)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_message = data.get("message", "")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
                {"role": "user", "content": user_message},
            ],
            max_tokens=4096,
            temperature=0.5,
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
       return jsonify({"response": f"Fehler: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host ="http://127.0.0.1:5000/chatbot1")
