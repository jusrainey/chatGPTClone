from flask import Flask, request, jsonify, g, Response
import openai
from openai import OpenAI
import sqlite3
import uuid
import os
from dotenv import load_dotenv
import requests
import json
from flask_cors import CORS


load_dotenv()

app = Flask(__name__)
CORS(app)


def generate_session_id():
    return str(uuid.uuid4())


@app.route('/save_chat', methods=['POST'])
def save_chat():

    session_id = request.json['session_id']
    user_input = request.json['user_input']
    bot_response = request.json['bot_response']


    db = get_db()
    print(f"Saving Chat for:{session_id}\n")



    db.execute('INSERT INTO chats (session_id, user_input, bot_response) VALUES (?, ?, ?)',
               (session_id, user_input, bot_response))
    db.commit()
    return jsonify({'message': 'Chat saved successfully'}), 201




def get_db():
    DATABASE = os.environ.get("DATABASE")
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.route('/get_response', methods=['GET'])
def bot_response():


    session_id = request.args.get('session_id')
    user_input = request.args.get('user_input')
    print(f"User Input:{user_input[:15]}....\n")

    KEY = os.environ.get("OPENAI_KEY2")
    openai_api_key = KEY

    def generate():
        openai.api_key = openai_api_key
        stream = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}],
            stream=True
        )

        for chunk in stream:
            print(chunk.choices[0].delta.content or "", end="")
            re = chunk.choices[0].delta.content
            yield f"data: {json.dumps({'bot_response': re})}\n\n"
    return Response(generate(), mimetype='text/event-stream')


@app.route('/start_chat', methods=['POST'])
def start_session():

    db = get_db()
    session_id = generate_session_id()
    print(f"Starting New session - Session ID:{session_id}")
    db.execute('INSERT INTO sessions (session_id) VALUES (?)', (session_id,))
    db.commit()
    return jsonify({'session_id': session_id})

@app.route('/get_history/<session_id>', methods=['GET'])
def get_history(session_id):

    print(f"GET - Chat History | Session ID: {session_id}\n")
    db = get_db()

    chat_history = db.execute(
        'SELECT id, user_input, bot_response FROM chats WHERE session_id = ?',
        (session_id,)
    ).fetchall()

    if chat_history:
        formatted_history = [
            {'id': chat['id'], 'user_input': chat['user_input'], 'bot_response': chat['bot_response']}
            for chat in chat_history
        ]
        return jsonify(formatted_history), 200
    else:
        return jsonify({'error': 'Chat history not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
