from flask import Flask, jsonify, request
from flask_socketio import SocketIO  # type: ignore
from flask_cors import CORS  # Import the CORS package
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS for Socket.IO
CORS(app)  # Enable CORS for regular routes

@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    logging.info(f'Client connected: {client_id}')

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    logging.info(f'Client disconnected: {client_id}')

@socketio.on('client_event')
def handle_client_event(data):
    client_id = request.sid
    logging.info(f'Received event from client {client_id}: {data}')
    # Process the client event and emit a response if needed
    socketio.emit('custom_event', {'message': 'Hello from the server!'}, room=client_id)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    logging.info('Starting server...')
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)