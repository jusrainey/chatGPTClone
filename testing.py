from flask import Flask, request, jsonify, g
import openai
import sqlite3
import uuid
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()






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
          "content": "hello"}]

}

response = requests.post(url=url, headers=headers, data=json.dumps(payload))
print(response)
response = response.json()
gpt_response = response['choices'][0]['message']['content']


print(gpt_response)
