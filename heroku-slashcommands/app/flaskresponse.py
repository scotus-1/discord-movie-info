from flask import Flask, request, jsonify
from discord_interactions import verify_key_decorator
import app.api_functions as api_functions
from iso639 import languages
from datetime import timedelta
import app.scraper as scraper
import threading
import requests
import json
import os
import re


app = Flask(__name__)

discord_endpoint = "https://discord.com/api/v8"
discord_public_key = os.environ.get("DISCORD_CLIENT_PUBLIC_KEY")
discord_client_id = os.environ.get("DISCORD_CLIENT_ID")
discord_client_secret = os.environ.get("DISCORD_CLIENT_SECRET")


tmdb_api_key = os.environ.get("TMDB_API_KEY")

omdb_api_key = os.environ.get("OMDB_API_KEY")




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


def remove_special_char(string):
    removed_apostrophes = re.sub("'", '', string).lower()
    cleanString = re.sub('\W+', ' ', removed_apostrophes).lower()
    return cleanString


def respond_info(movie_name, interaction_token, app_id, year):
    discord_url = discord_endpoint + f"/webhooks/{app_id}/{interaction_token}/messages/@original"

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

    headers = {
        "Authorization": "Bearer " + get_token()
    }

    search = api_functions.tmdb_search(movie_name, tmdb_api_key, year)

    if search is None:
        return requests.patch(discord_url, headers=headers, json={"embeds": [
            {"title": "Movie Not Found",
             "description": "Please try again with a better search query",
             "color": 16711680}]})


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

    movie = api_functions.tmdb_info(str(movie_id), tmdb_api_key)
    omdb_info = api_functions.omdb_info(movie['imdb_id'], omdb_api_key)


    release_year = movie['release_date'].split("-")[0]
    embed['title'] = movie['title'] + f" ({release_year} - {omdb_info['Rated']})"

    providers = movie['watch/providers']['results']['US']
    provider_url = providers['link']
    streaming = providers.get('flatrate')
    if streaming is not None:
        streaming = streaming[0]['provider_name']
    renting = providers.get('rent')
    if renting is not None:
        renting = renting[0]['provider_name']
    buying = providers.get('buy')
    if buying is not None:
        buying = buying[0]['provider_name']


    embed['description'] = "\n" + movie['overview'] + "\n\n" + \
                           f"[```prolog\n'Stream': {streaming} | 'Rent': {renting} | 'Buy': {buying} | 'US'```)]({provider_url})"

    embed['url'] = "https://themoviedb.org/movie/" + str(movie['id'])
    embed['image']['url'] = omdb_info['Poster']

    embed['fields'][0]['value'] = omdb_info['Genre']
    embed['fields'][1]['value'] = languages.get(alpha2=movie['original_language']).name

    run_times = str(timedelta(minutes=movie['runtime'])).split(":")
    embed['fields'][2]['value'] = f"{run_times[0]} hours and {run_times[1]} minutes"

    embed['fields'][3]['value'] = omdb_info['Director']

    imdb_url = "https://imdb.com/title/" + movie['imdb_id']
    embed['fields'][4]['value'] = f"[{omdb_info['imdbRating']} / 10 - {omdb_info['imdbVotes']} votes]({imdb_url})"

    title = remove_special_char(movie['title'])
    title_with_year = remove_special_char(movie['title'] + " " + release_year)

    metacritic_url = "https://metacritic.com/movie/" + title_with_year.replace(" ","-")
    metacritic_scores = scraper.metacritic_scrape(metacritic_url)
    if metacritic_scores == "404":
        metacritic_url = "https://metacritic.com/movie/" + title.replace(" ","-")
        metacritic_scores = scraper.metacritic_scrape(metacritic_url)

    embed['fields'][5]['value'] = f"{metacritic_scores['metascore']} | {metacritic_scores['user_score']} / 10.0"


    rotten_tomatoes_url = "https://rottentomatoes.com/m/" + title_with_year.replace(" ", "_")
    rt_value = scraper.scrape_rotten_tomatoes(rotten_tomatoes_url)
    if rt_value == "404":
        rotten_tomatoes_url = "https://rottentomatoes.com/m/" + title.replace(" ", "_")
        rt_value = scraper.scrape_rotten_tomatoes(rotten_tomatoes_url)

    embed['fields'][6]['value'] = f"{rt_value['critic_score']} | {rt_value['audience_score']} (Critic | Audience)"
    embed['thumbnail']['url'] = rt_value['critic_icon']

    return requests.patch(discord_url, headers=headers, json={"embeds": [embed]})




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

        thread = threading.Thread(target=respond_info,
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