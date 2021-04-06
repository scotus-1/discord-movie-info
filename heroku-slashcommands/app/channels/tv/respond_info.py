import threading
from statistics import mean
from iso639 import languages
from random import choice
from traceback import print_exc
import requests
from app.globals import omdb_api_key, tmdb_api_key, discord_endpoint, remove_special_char, auth_headers
from app.functions import api_functions, scraper
from app.router import router



@router.register_kwargs('tv')
def respond_movie_info_kwargs(json):
    search_query = json['data']['options'][0]['value']

    try:
        search_year = json['data']['options'][1]['value']
    except IndexError:
        search_year = None

    token = json['token']
    application_id = json['application_id']

    return {
        "tv_name": search_query,
        "interaction_token": token,
        "app_id": application_id,
        "year": search_year
    }


@router.register_command('tv')
def respond_tv_info(tv_name, interaction_token, app_id, year):
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
                "inline": True
                },
              {
                "name": "Created By:",
                "value": None,
                "inline": True
                },
                {
                "name": "Seasons/Episodes (avg runtime):",
                  "value": None,
                "inline": False
                },
                {
                "name": "Language:",
                "value": None,
                "inline": True
                },
                {
                    "name": "Status | Type:",
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
              },
                {
                    "name": "Last Episode:",
                    "value": None,
                    "inline": True
                }
            ]
          }


        search = api_functions.tmdb_search("tv", tv_name, tmdb_api_key, year, session)

        if len(search['results']) == 0:
            return session.patch(discord_url, headers=auth_headers, json={"embeds": [
                {"title": "TV Show Not Found",
                 "description": "Please try again with a better search query",
                 "color": 16711680}]})


        tv_id = None
        best_tv = []
        popularity = 0
        year_diff = 9999999999
        if year is not None:
            for result in search['results']:
                if result['first_air_date'].split("-")[0].strip():
                    difference = abs(int(result['first_air_date'].split("-")[0]) - year)
                else:
                    difference = 99999999999999999999
                if difference < year_diff:
                    year_diff = difference
                    best_tv.clear()
                    best_tv.append(result)
                elif difference == year_diff:
                    best_tv.append(result)
            if len(best_tv) == 1:
                tv_id = best_tv[0]['id']
            else:
                for result in best_tv:
                    if result['popularity'] > popularity:
                        popularity = result['popularity']
                        tv_id = result['id']
        else:
            for result in search['results']:
                if result['popularity'] > popularity:
                    popularity = result['popularity']
                    tv_id = result['id']

        tv_show = api_functions.tmdb_info("tv", str(tv_id), tmdb_api_key, session)
        imdb_id = api_functions.tmdb_get_imdb_id("tv", tv_show['id'], tmdb_api_key, session)['imdb_id']
        omdb_info = api_functions.omdb_info(imdb_id, omdb_api_key, session)


        release_year = tv_show['first_air_date'].split("-")[0]
        last_year = tv_show['last_air_date'].split("-")[0]

        if tv_show['in_production']:
            embed['title'] = tv_show['name'] + f" ({release_year}-({last_year}) - {omdb_info['Rated']})"
        else:
            embed['title'] = tv_show['name'] + f" ({release_year}-{last_year} - {omdb_info['Rated']})"

        providers = tv_show['watch/providers']['results'].get('US')
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


        embed['description'] = "\n" + tv_show['overview'] + f"\n\n*{tv_show['tagline']}*\n" + \
                               f"[```md\n<Stream: {streaming}> <Rent: {renting}> <Buy: {buying}> 'US'```]({provider_url})"

        embed['url'] = "https://themoviedb.org/tv/" + str(tv_show['id'])
        embed['image']['url'] = choice(["https://image.tmdb.org/t/p/original" + tv_show['poster_path'],
                                        omdb_info['Poster'].replace("_V1_SX300", "_V1_SX3000"),
                                        "https://image.tmdb.org/t/p/original" + tv_show['backdrop_path']])


        embed['fields'][0]['value'] = omdb_info['Genre']

        created_by = ""
        if len(tv_show['created_by']) == 1:
            created_by = tv_show['created_by'][0]['name']
        else:
            for creator in tv_show["created_by"]:
                created_by = created_by + creator['name'] + ", "
        embed['fields'][1]['value'] = created_by

        average_runtime = str(round(mean(tv_show['episode_run_time'])))
        embed['fields'][2]['value'] = \
        f"{str(tv_show['number_of_seasons'])} seasons and {str(tv_show['number_of_episodes'])} episodes | {average_runtime} minutes"

        embed['fields'][3]['value'] = languages.get(alpha2=tv_show['original_language']).name


        embed['fields'][4]['value'] = f"{tv_show['status']} | {tv_show['type']}"

        imdb_url = "https://imdb.com/title/" + imdb_id
        embed['fields'][5]['value'] = f"[{omdb_info['imdbRating']} / 10 - {omdb_info['imdbVotes']} votes]({imdb_url})"

        title = remove_special_char(tv_show['name']).lower()
        title_with_year = remove_special_char(tv_show['name'] + " " + release_year).lower()

        metacritic_url = "https://metacritic.com/tv/" + title_with_year.replace(" ","-")
        metacritic_scores = scraper.metacritic_scrape(metacritic_url, session)

        if metacritic_scores == "404":
            metacritic_url = "https://metacritic.com/tv/" + title.replace(" ","-")
            metacritic_scores = scraper.metacritic_scrape(metacritic_url, session)

            if metacritic_scores == "404":
                metacritic_scores = {"metascore": "N/A", "user_score": "N/A"}

        embed['fields'][6]['value'] = f"[{metacritic_scores['metascore']} | {metacritic_scores['user_score']} / 10.0]({metacritic_url})"
        for rating in omdb_info['Ratings']:
            if rating['Source'] == "Rotten Tomatoes":
                embed['fields'][7]['value'] = f"{rating['Value']} | Pending... (Critic | Audience)"


        last_ep = tv_show['last_episode_to_air']
        episode_url = "https://tmdb.org/tv" + f"/{str(tv_id)}/season/{str(last_ep['season_number'])}/episode/{str(last_ep['episode_number'])}"
        embed['fields'][8]['value'] = f"[{last_ep['name']} | S{str(last_ep['season_number'])} EP{str(last_ep['episode_number'])}]({episode_url})"


        rotten_tomatoes_thread = threading.Thread(target=scraper.rotten_tomatoes_handler, kwargs={
            "media_type": "tv",
            "title": title,
            "title_year": title_with_year,
            "embed": embed,
            "app_id": app_id,
            "interaction_token": interaction_token,
            "session": session})

        rotten_tomatoes_thread.start()
        return print(session.patch(discord_url, headers=auth_headers, json={"embeds": [embed]}).text)
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
