from flask import Flask, jsonify
from langchain_community.llms import OpenAI
from dotenv import load_dotenv
from langchainModules import chat
import os
import time

load_dotenv()

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/chat')
def chat_endpoint():
    response = chat.chat()
    return jsonify(response)

@app.route('/langchain')
def langchain_example():
    api_key = os.getenv('OPENAI_API_KEY')
    llm = OpenAI(api_key=api_key)
    response = llm('What is LangSmith?')
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)