from urllib.parse import urlencode


tmdb_url = "https://api.themoviedb.org/3"
omdb_url = "http://www.omdbapi.com/?"


def tmdb_search(movie_name, api_key, year, session):
    search_query = {'query': movie_name,
                    'api_key': api_key}

    if year:
        search_query['year'] = abs(year)

    q_str = urlencode(search_query)
    url = tmdb_url + "/search/movie?" + q_str
    response = session.get(url)

    return response.json()


def tmdb_info(movie_id, api_key, session):
    search_query = {'api_key': api_key,
                    'append_to_response': "watch/providers"}

    q_str = urlencode(search_query)
    url = tmdb_url + "/movie/" + movie_id + "?" + q_str
    response = session.get(url)

    return response.json()


def omdb_info(imdb_id, api_key, session):
    search_query = {'apikey': api_key,
                    'i': imdb_id}

    q_str = urlencode(search_query)
    url = omdb_url + q_str
    response = session.get(url)

    return response.json()




