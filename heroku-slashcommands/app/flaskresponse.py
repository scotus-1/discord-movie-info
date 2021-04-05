from flask import Flask, request, jsonify
from discord_interactions import verify_key_decorator
from app.movie.respond_info import respond_movie_info
import threading
import requests
import json
import os
import re

# create Flask App


app = Flask(__name__)

# create global keys and secrets
discord_endpoint = "https://discord.com/api"
discord_public_key = os.environ.get("DISCORD_CLIENT_PUBLIC_KEY")
discord_client_id = os.environ.get("DISCORD_CLIENT_ID")
discord_client_secret = os.environ.get("DISCORD_CLIENT_SECRET")

tmdb_api_key = os.environ.get("TMDB_API_KEY")

omdb_api_key = os.environ.get("OMDB_API_KEY")


# token retrieval
def get_token():
  data = {
    'grant_type': 'client_credentials',
    'scope': 'applications.commands applications.commands.update'
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  r = requests.post('%s/oauth2/token' % discord_endpoint,
                    data=data, headers=headers,
                    auth=(discord_client_id, discord_client_secret))

  r.raise_for_status()
  return r.json()['access_token']


# discord auth headers
auth_headers = {
            "Authorization": "Bearer " + get_token()
        }

# special character removal function
def remove_special_char(text):
    removed_apostrophes = re.sub("'", '', text).lower()
    return re.sub('\W+', ' ', removed_apostrophes).lower()


@app.route('/interactions', methods=['POST'])
@verify_key_decorator(discord_public_key)
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