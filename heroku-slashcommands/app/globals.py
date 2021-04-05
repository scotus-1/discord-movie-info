import re
import os
import requests


# create global keys and secrets
discord_endpoint = "https://discord.com/api/v8"
discord_client_id = os.environ.get("DISCORD_CLIENT_ID")
discord_client_secret = os.environ.get("DISCORD_CLIENT_SECRET")

tmdb_api_key = os.environ.get("TMDB_API_KEY")

omdb_api_key = os.environ.get("OMDB_API_KEY")


# token retrieval
def get_token():
  data = {
    'grant_type': 'client_credentials',
    'scope': 'applications.channels applications.channels.update'
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  r = requests.post('%s/oauth2/token' % discord_endpoint,
                    data=data, headers=headers,
                    auth=(discord_client_id, discord_client_secret))


  print(r.json())
  return r.json()['access_token']


# discord auth headers
auth_headers = {
            "Authorization": "Bearer " + get_token()
        }

# special character removal function
def remove_special_char(text):
    removed_apostrophes = re.sub("'", '', text).lower()
    return re.sub('\W+', ' ', removed_apostrophes).lower()