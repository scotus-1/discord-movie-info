from flask import Flask, request, jsonify
from discord_interactions import verify_key_decorator
from app.movie.respond_info import respond_movie_info
import threading
import json
import os


# create Flask App
app = Flask(__name__)

@app.route('/interactions', methods=['POST'])
@verify_key_decorator(os.environ.get("DISCORD_CLIENT_PUBLIC_KEY"))
def pong():
    if request.json["type"] == 1:
        return jsonify({
            "type": 1
        })
    else:
        json_data = json.loads(request.data)
        print(json_data)

        search_query = json_data['data']['options'][0]['value']

        try:
            search_year = json_data['data']['options'][1]['value']
        except IndexError:
            search_year = None

        token = json_data['token']
        application_id = json_data['application_id']

        thread = threading.Thread(target=respond_movie_info,
                                  kwargs={
                                      "movie_name": search_query,
                                      "interaction_token": token,
                                      "app_id": application_id,
                                      "year": search_year
                                  })

        thread.start()

        return jsonify({
            "type": 5
        })