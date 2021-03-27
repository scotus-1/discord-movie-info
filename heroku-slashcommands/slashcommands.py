import requests

API_ENDPOINT = 'https://discord.com/api/v8'
CLIENT_ID = '811374808930975785'
CLIENT_SECRET = '61x9aHm50V2NvIE45MG2VwP6Ze_Dycgr'

#token retrieval via https requests
def get_token():
  data = {
    'grant_type': 'client_credentials',
    'scope': 'applications.commands applications.commands.update'
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
  r.raise_for_status()
  return r.json()['access_token']

url = "https://discord.com/api/v8/applications/811374808930975785/guilds/561422744840044564/commands"

json = {
    "name": "rating",
    "description": "Get information and rating of a movie or TV Show.",
    "options": [
        {
            "name": "name",
            "description": "Name of the Movie or TV Show",
            "type": 3,
            "required": True
        }
    ]
}


# or a client credentials token for your app with the applications.commmands.update scope
headers = {
    "Authorization": "Bearer " + get_token()
}

r = requests.post(url, headers=headers, json=json)
print(r.status_code)