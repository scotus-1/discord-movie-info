from urllib.parse import urlencode
from requests import get
from pprint import pprint

tmdb_url = "https://api.themoviedb.org/3"
omdb_url = "http://www.omdbapi.com/?"


def tmdb_search(movie_name, api_key, year):
    search_query = {'query': movie_name,
                    'api_key': api_key}

    if year:
        search_query['year'] = abs(year)

    q_str = urlencode(search_query)
    url = tmdb_url + "/search/movie?" + q_str
    response = get(url)

    return response.json()


def tmdb_info(movie_id, api_key):
    search_query = {'api_key': api_key,
                    'append_to_response': "watch/providers"}

    q_str = urlencode(search_query)
    url = tmdb_url + "/movie/" + movie_id + "?" + q_str
    response = get(url)

    return response.json()


def omdb_info(imdb_id, api_key):
    search_query = {'apikey': api_key,
                    'i': imdb_id}

    q_str = urlencode(search_query)
    url = omdb_url + q_str
    response = get(url)

    return response.json()




