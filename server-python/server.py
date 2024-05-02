from flask import Flask, request
from flask_socketio import SocketIO
from flask_cors import CORS
import os
from langchainModules.doc_convo import get_llm_response
from langchainModules.final_quiz_agent import get_questions
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# Define origins for CORS
origins = ["http://localhost:5173", "http://localhost:3000"]

# Initialize CORS before SocketIO
CORS(app, resources={r"/*": {"origins": origins}})

# Initialize SocketIO with correct origins
socketio = SocketIO(app, cors_allowed_origins=origins)

@socketio.on('message_from_client')
def handle_message(data):
    logging.info(f"Received message from client: {data}")
    user_message = data['message']
    response = get_llm_response( 1, user_message)
    socketio.emit('message_from_server', {'message': response}, room=request.sid)

@socketio.on('question_request')
def handle_question_request(data):
    print("request received")
    logging.info(f"Received question request from client: {data}")
    user_message = data['message']
    response = get_questions()
    socketio.emit("questions_from_server", {'message': response}, room=request.sid)
    

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
