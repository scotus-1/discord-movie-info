from selenium import webdriver
from flask import Flask, request, jsonify
from discord_interactions import verify_key_decorator
import app.api_functions as api_functions
from iso639 import languages
from datetime import timedelta
import app.scraper as scraper
from random import choice
import threading
import traceback
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



def create_driver():
    options = webdriver.ChromeOptions()
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
            'permissions.default.stylesheet': 2,
            'javascript': 2
        }
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument('headless')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    return webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)

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



def rotten_tomatoes_handler(media_type, title, title_year, embed, app_id, interaction_token, session):
    driver = create_driver()
    discord_url = discord_endpoint + f"/webhooks/{app_id}/{interaction_token}/messages/@original"
    base_url = ""
    if media_type == "tv":
        base_url = "https://rottentomatoes.com/tv/"
    elif media_type == "movie":
        base_url = "https://rottentomatoes.com/m/"


    if "the" in title.split(" ")[0]:
        words = title_year.split(" ")
        words.pop(0)
        words = " ".join(words)

        word = title.split(" ")
        word.pop(0)
        word = " ".join(word)


        rotten_tomatoes_url = base_url + words.replace(" ", "_")
        rt_value = scraper.scrape_rotten_tomatoes(rotten_tomatoes_url, session, driver)
        print(rotten_tomatoes_url)
        if rt_value == "404":
            rotten_tomatoes_url = base_url + title_year.replace(" ", "_")
            rt_value = scraper.scrape_rotten_tomatoes(rotten_tomatoes_url, session, driver)
            print(rotten_tomatoes_url)
            if rt_value == "404":
                rotten_tomatoes_url = base_url + word.replace(" ", "_")
                rt_value = scraper.scrape_rotten_tomatoes(rotten_tomatoes_url, session, driver)
                print(rotten_tomatoes_url)
                if rt_value == "404":
                    rotten_tomatoes_url = base_url + title.replace(" ", "_")
                    rt_value = scraper.scrape_rotten_tomatoes(rotten_tomatoes_url, session, driver)
                    print(rotten_tomatoes_url)
                    if rt_value == "404":
                        rt_value = {"critic_score": "N/A", "audience_score": "N/A"}
    else:
        rotten_tomatoes_url = base_url + title_year.replace(" ", "_")
        rt_value = scraper.scrape_rotten_tomatoes(rotten_tomatoes_url, session, driver)
        if rt_value == "404":
            rotten_tomatoes_url = base_url + title.replace(" ", "_")
            rt_value = scraper.scrape_rotten_tomatoes(rotten_tomatoes_url, session, driver)
            if rt_value == "404":
                rt_value = {"critic_score": "N/A", "audience_score": "N/A"}

    driver.close()
    embed['fields'][6]['value'] = f"[{rt_value['critic_score']} | {rt_value['audience_score']}]({rotten_tomatoes_url}) (Critic | Audience)"

    return session.patch(discord_url, headers=auth_headers, json={"embeds": [embed]}).text


def respond_movie_info(movie_name, interaction_token, app_id, year):
    discord_url = discord_endpoint + f"/webhooks/{app_id}/{interaction_token}/messages/@original"
    session = requests.Session()

    try:
        embed = {
            "title": None,
            "description": None,
            "url": None,
            "color": 9442302,
            "footer": {
              "icon_url": "https://pbs.twimg.com/profile_images/1243623122089041920/gVZIvphd.jpg",
              "text": "API's by The Movie DB, Open Movie DB, and JustWatch "
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
                "value": "Pending...",
                "inline": True
              }
            ]
          }


        search = api_functions.tmdb_search(movie_name, tmdb_api_key, year, session)

        if len(search['results']) == 0:
            return session.patch(discord_url, headers=auth_headers, json={"embeds": [
                {"title": "Movie Not Found",
                 "description": "Please try again with a better search query",
                 "color": 16711680}]})


        movie_id = None
        best_movies = []
        popularity = 0
        year_diff = 9999999999
        print(year)
        if year is not None:
            print(search['results'])
            for result in search['results']:
                difference = abs(int(result['release_date'].split("-")[0]) - year)
                print(str(difference) + "," + str(year_diff))
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

        movie = api_functions.tmdb_info(str(movie_id), tmdb_api_key, session)
        omdb_info = api_functions.omdb_info(movie['imdb_id'], omdb_api_key, session)


        release_year = movie['release_date'].split("-")[0]
        embed['title'] = movie['title'] + f" ({release_year} - {omdb_info['Rated']})"

        providers = movie['watch/providers']['results'].get('US')
        streaming = None
        renting = None
        buying = None
        if providers is not None:
            provider_url = providers.get('link')
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
                               f"[```md\n<Stream: {streaming}> <Rent: {renting}> <Buy: {buying}> 'US'```]({provider_url})"

        embed['url'] = "https://themoviedb.org/movie/" + str(movie['id'])
        embed['image']['url'] = choice(["https://image.tmdb.org/t/p/original" + movie['poster_path'],
                                        omdb_info['Poster'].replace("_V1_SX300", "_V1_SX3000"),
                                        "https://image.tmdb.org/t/p/original" + movie['backdrop_path']])


        embed['fields'][0]['value'] = omdb_info['Genre']
        embed['fields'][1]['value'] = languages.get(alpha2=movie['original_language']).name

        run_times = str(timedelta(minutes=movie['runtime'])).split(":")
        embed['fields'][2]['value'] = f"{run_times[0]} hours and {run_times[1]} minutes"

        embed['fields'][3]['value'] = omdb_info['Director']

        imdb_url = "https://imdb.com/title/" + movie['imdb_id']
        embed['fields'][4]['value'] = f"[{omdb_info['imdbRating']} / 10 - {omdb_info['imdbVotes']} votes]({imdb_url})"

        title = remove_special_char(movie['title']).lower()
        title_with_year = remove_special_char(movie['title'] + " " + release_year).lower()

        metacritic_url = "https://metacritic.com/movie/" + title_with_year.replace(" ","-")
        metacritic_scores = scraper.metacritic_scrape(metacritic_url, session)

        if metacritic_scores == "404":
            metacritic_url = "https://metacritic.com/movie/" + title.replace(" ","-")
            metacritic_scores = scraper.metacritic_scrape(metacritic_url, session)

            if metacritic_scores == "404":
                metacritic_scores = {"metascore": "N/A", "user_score": "N/A"}

        embed['fields'][5]['value'] = f"[{metacritic_scores['metascore']} | {metacritic_scores['user_score']} / 10.0]({metacritic_url})"
        for rating in omdb_info['Ratings']:
            if rating['Source'] == "Rotten Tomatoes":
                embed['fields'][6]['value'] = f"{rating['Value']} | Pending... (Critic | Audience)"


        rotten_tomatoes_thread = threading.Thread(target=rotten_tomatoes_handler,kwargs={
            "media_type": "movie",
            "title": title,
            "title_year": title_with_year,
            "embed": embed,
            "app_id": app_id,
            "interaction_token": interaction_token,
            "session": session})

        rotten_tomatoes_thread.start()

        return session.patch(discord_url, headers=auth_headers, json={"embeds": [embed]}).text
    except Exception as e:
        traceback.print_exc()
        return session.patch(discord_url, headers=auth_headers, json={"embeds": [
                {"title": "Internal Server Error (505) ",
                 "description": e.__doc__,
                 "color": 16711680}]})
    except:
        traceback.print_exc()
        return session.patch(discord_url, headers=auth_headers, json={"embeds": [
            {"title": "Internal Server Error (505) ",
             "description": "Unknown Error, Check Server Logs",
             "color": 16711680}]})


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