from flask import Flask, jsonify
from langchain_community.llms import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/langchain')
def langchain_example():
    api_key = os.getenv('OPENAI_API_KEY')
    llm = OpenAI(api_key=api_key)
    response = llm('What is LangSmith?')
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)