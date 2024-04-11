from flask import Flask, request, jsonify, g
import openai
import sqlite3
from sql_handler import *
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
KEY = os.environ.get("OPENAI_KEY")
DATABASE = os.environ.get("DATABASE")
openai.api_key = KEY


def generate_session_id():
    return str(uuid.uuid4())


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.route('/start_session', methods=['POST'])
def start_session():
    db = get_db()
    session_id = generate_session_id()
    db.execute('INSERT INTO sessions (session_id) VALUES (?)', (session_id,))
    db.commit()
    return jsonify({'session_id': session_id})


@app.route('/chats', methods=['POST'])
def save_chat():
    db = get_db()
    session_id = request.json['session_id']
    user_input = request.json['user_input']
    bot_response = request.json['bot_response']

    session_db_id = db.execute('SELECT id FROM sessions WHERE session_id = ?', (session_id,)).fetchone()
    if session_db_id:

        db.execute('INSERT INTO chats (session_id, user_input, bot_response) VALUES (?, ?, ?)',
                   (session_db_id['id'], user_input, bot_response))
        db.commit()
        return jsonify({'message': 'Chat saved successfully'}), 201
    else:

        return jsonify({'error': 'Session not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
