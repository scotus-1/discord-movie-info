import threading
from iso639 import languages
from datetime import timedelta
from random import choice
from traceback import print_exc
import requests
from app.flaskresponse import omdb_api_key, tmdb_api_key, discord_endpoint, remove_special_char, auth_headers
from app import scraper, api_functions



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


        search = api_functions.tmdb_search("movie", movie_name, tmdb_api_key, year, session)

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

        movie = api_functions.tmdb_info("movie", str(movie_id), tmdb_api_key, session)
        omdb_info = api_functions.omdb_info(movie['imdb_id'], omdb_api_key, session)


        release_year = movie['release_date'].split("-")[0]
        embed['title'] = movie['title'] + f" ({release_year} - {omdb_info['Rated']})"

        providers = movie['watch/providers']['results'].get('US')
        streaming = None
        renting = None
        buying = None
        provider_url = None
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


        rotten_tomatoes_thread = threading.Thread(target=scraper.rotten_tomatoes_handler,kwargs={
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
        print_exc()
        return session.patch(discord_url, headers=auth_headers, json={"embeds": [
                {"title": "Internal Server Error (505) ",
                 "description": e.__doc__,
                 "color": 16711680}]})
    except:
        print_exc()
        return session.patch(discord_url, headers=auth_headers, json={"embeds": [
            {"title": "Internal Server Error (505) ",
             "description": "Unknown Error, Check Server Logs",
             "color": 16711680}]})