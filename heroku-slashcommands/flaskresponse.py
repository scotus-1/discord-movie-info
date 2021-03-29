from flask import Flask, request, jsonify
from discord_interactions import verify_key_decorator
import json
import requests


CLIENT_PUBLIC_KEY = "d164a6f844f2d9b2026508f3e826aeac830b8131ab95d22957f681d4d15b555f"
app = Flask(__name__)

@app.route('/interactions', methods=['POST'])
@verify_key_decorator(CLIENT_PUBLIC_KEY)
def pong():
    if request.json["type"] == 1:
        return jsonify({
            "type": 1
        })
    else:
        json_data = json.loads(request.data)
        print(json_data)
        movie_name = json_data['data']['options'][0]['value']


        return jsonify({
            "type": 5,
            # "data": {
            #     "tts": False,
            #     "content": "Congrats on sending your command!",
            #     "embeds": [
            #         {
            #             "title": "Test",
            #             "color": 4566842
            #         }
            #     ],
            #     "allowed_mentions": []
            # }
        })


def respond_info(movie_name, interaction_id):

