from flask import Flask, request, jsonify
from discord_interactions import verify_key_decorator
import json
import app.api_functions as api_functions
import threading
import os


app = Flask(__name__)

discord_public_key = os.environ.get("DISCORD_CLIENT_PUBLIC_KEY")

tmdb_api_key = os.environ.get("TMDB_API_KEY")

omdb_api_key = os.environ.get("OMDB_API_KEY")

def respond_info(movie_name, interaction_token, app_id, year):
    embed = {
        "title": None,
        "description": None,
        "url": None,
        "color": 9442302,
        "footer": {
          "icon_url": "https://pbs.twimg.com/profile_images/1243623122089041920/gVZIvphd.jpg",
          "text": "API's by The Movie DB, Open Movie DB, and JustWatch "
        },
        "thumbnail": {
          "url": None
        },
        "image": {
          "url": None
        },
        "fields": [
          {
            "name": "Genre(s):",
            "value": None,
            "inline": False
          },
          {
            "name": "Language:",
            "value": None,
            "inline": True
          },
          {
            "name": "Runtime:",
            "value": None,
            "inline": True
          },
          {
            "name": "Director:",
            "value": None,
            "inline": True
          },
          {
            "name": "IMDB:",
            "value": None,
            "inline": True
          },
          {
            "name": "Metacritc:",
            "value": None,
            "inline": True
          },
          {
            "name": "Rotten Tomatoes:",
            "value": None,
            "inline": True
          }
        ]
      }



    search = api_functions.tmdb_search(movie_name, tmdb_api_key, year)
    movie_id = None
    best_movies = []
    popularity = 0
    year_diff = 9999999999
    if year:
        for result in search['results']:
            difference = abs(int(result['release_date'].split("-")[0]) - year)
            if difference < year_diff:
                year_diff = difference
                best_movies.clear()
                best_movies.append(result)
            elif difference == year_diff:
                best_movies.append(result)
        if len(best_movies) == 1:
            movie_id = best_movies[0]['id']
        else:
            for result in best_movies:
                if result['popularity'] > popularity:
                    popularity = result['popularity']
                    movie_id = result['id']
    else:
        for result in search['results']:
            if result['popularity'] > popularity:
                popularity = result['popularity']
                movie_id = result['id']

    movie = api_functions.tmdb_info(movie_id, tmdb_api_key)
    omdb_info = api_functions.omdb_info(movie['imdb_id'], omdb_api_key)




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
        application_id = json_data['id']

        # thread = threading.Thread(target=respond_info,
        #                           kwargs={
        #                               "movie_name": search_query,
        #                               "interaction_token": token,
        #                               "app_id": application_id,
        #                               "year": search_year
        #                           })
        #
        # thread.start()

        return jsonify({
            "type": 4,
            "data": {
                "tts": False,
                "content": None,
                "embeds": [
                    {
                        "title": "Test",
                        "color": 4566842
                    }
                ],
                "allowed_mentions": []
            }
        })