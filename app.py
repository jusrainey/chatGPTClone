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
            re = chunk.choices[0].delta.content
            yield f"data: {json.dumps({'bot_response': re})}\n\n"

    return Response(generate(), mimetype='text/event-stream')


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


@app.route('/new_session_id', methods=['GET'])
def new_session_id():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT MAX(session_id) FROM chats")
    max_id = cursor.fetchone()[0]
    next_session_id = max_id + 1 if max_id is not None else 1  # Start from 1 if table is empty
    return jsonify({'next_session_id': next_session_id})


@app.route('/get_sessions', methods=['GET'])
def get_sessions():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT MAX(session_id) FROM chats")

    max_id = cursor.fetchone()[0]
    print(max_id)
    # Format the sessions for JSON output
    session_list = [{'id': session, "name":f"Session: {session}" }
                    for session in range(1,max_id+1)]
    print(session_list)
    return jsonify({'sessions': session_list})




if __name__ == '__main__':
    app.run(debug=True)
