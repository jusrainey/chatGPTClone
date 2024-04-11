from flask import Flask, request, jsonify, g
import openai
import sqlite3
import uuid
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

app = Flask(__name__)


def generate_session_id():
    return str(uuid.uuid4())
def save_chat(session_id, user_input, bot_response):
    db = get_db()

    session_db_id = db.execute('SELECT id FROM sessions WHERE session_id = ?', (session_id,)).fetchone()
    if session_db_id:

        db.execute('INSERT INTO chats (session_id, user_input, bot_response) VALUES (?, ?, ?)',
                   (session_db_id['id'], user_input, bot_response))
        db.commit()
        return jsonify({'message': 'Chat saved successfully'}), 201
    else:

        return jsonify({'error': 'Session not found'}), 404



def get_db():
    DATABASE = os.environ.get("DATABASE")
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.route('/get_response', methods=['POST'])
def bot_response():

    session_id = request.json['session_id']
    user_input = request.json['user_input']

    KEY = os.environ.get("OPENAI_KEY")
    openai_api_key = KEY



    url = 'https://api.openai.com/v1/chat/completions'

    headers = {
        "Authorization": openai_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages":
            [{"role": "system",
              "content": user_input}]

    }

    response = requests.post(url=url, headers=headers, data=json.dumps(payload))
    response = response.json()
    gpt_response = response['choices'][0]['message']['content']
    save_chat(session_id,user_input,gpt_response)

    return jsonify({'bot_response': gpt_response})


@app.route('/start_chat', methods=['POST'])
def start_session():
    db = get_db()
    session_id = generate_session_id()
    db.execute('INSERT INTO sessions (session_id) VALUES (?)', (session_id,))
    db.commit()
    return jsonify({'session_id': session_id})

@app.route('/get_history', methods=['GET'])
def get_history():
    session_id = request.json['session_id']
    db = get_db()

    chat_history = db.execute('SELECT id,user_input, bot_response FROM chats WHERE session_id = ?',
                              (session_id,)).fetchall()

    if chat_history:
        # Convert the chat history to a format suitable for the frontend and model
        formatted_history = [{'id':chat['id'],'user_input': chat['user_input'], 'bot_response': chat['bot_response']} for chat in
                             chat_history]
        return jsonify(formatted_history), 200
    else:
        return jsonify({'error': 'Chat history not found'}), 404



if __name__ == '__main__':
    app.run(debug=True)
