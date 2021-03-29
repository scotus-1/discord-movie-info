from flask import Flask, request, jsonify
from discord_interactions import verify_key_decorator
import json
import threading
from urllib.parse import urlencode
from requests import get


CLIENT_PUBLIC_KEY = "d164a6f844f2d9b2026508f3e826aeac830b8131ab95d22957f681d4d15b555f"
app = Flask(__name__)

tmdb_url = "https://api.themoviedb.org/3"
tmdb_api_key = "d035ca2d122538bc314de1ce4b98fdd9"

omdb_url = "http://www.omdbapi.com/?"
omdb_api_key = "7a7c908e"

utelly_url = "https://utelly-tv-shows-and-movies-availability-v1.p.rapidapi.com"
utelly_api_key = "0296255ae1msh6d10fea48ea2f6dp1d77bdjsn007a5257a0e2"



def tmdb_search(movie_name, api_key):
    search_query = {'api_key': api_key,
                    'query': movie_name}

    q_str = urlencode(search_query)
    url = tmdb_url + "/search/movie?" + q_str
    response = get(url)

    return response.json()


def tmdb_info(movie_id, api_key):
    search_query = {'api_key': api_key,
                    'movie_id': movie_id,
                    }

    q_str = urlencode(search_query)
    url = tmdb_url + "/movie?" + q_str
    response = get(url)

    return response.json()

def omdb_info(imdb_id, api_key):
    search_query = {'apikey': api_key,
                    'i': imdb_id,
                    }

    q_str = urlencode(search_query)
    url = omdb_url + q_str
    response = get(url)

    return response.json()


def check_availability(imdb_id, api_key):
    search_query = {'source_id': imdb_id,
                    'source': "imdb",
                    'country': "us"
                    }

    headers = {'x-rapidapi-key': api_key,
               'x-rapidapi-host': utelly_url}

    q_str = urlencode(search_query)
    url = utelly_url + "/idlookup?" + q_str
    response = get(url, headers=headers)
    return json.loads(response.text)


def respond_info(movie_name, interaction_token, user, app_id, nickname):
    pass



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
        search_query = json_data['data']['options'][0]['value']
        token = json_data['token']
        member = json_data['member']
        application_id = json_data['id']

        # thread = threading.Thread(target=respond_info,
        #                           kwargs={
        #                               "movie_name": search_query,
        #                               "interaction_token": token,
        #                               "user": member['user'],
        #                               "app_id": application_id,
        #                               "nickname": member['nick']
        #                           })
        #
        # thread.start()
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