import requests
from pprint import pprint


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
    "name": "tv",
    "description": "Get information and rating of a movie",
    "options": [
        {
            "name": "tv",
            "description": "Name of the TV Show",
            "type": 3,
            "required": True
        },
        {
            "name": "year",
            "description": "Input the closest year to the target TV Show",
            "type": 4,
            "required": False
        }
    ]
}


# or a client credentials token for your app with the applications.commands.update scope
headers = {
    "Authorization": "Bearer " + get_token()
}


r = requests.post(url, headers=headers, json=json)
# r = requests.get(url, headers=headers)
pprint(r.json())
print(r.status_code)