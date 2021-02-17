import requests

API_ENDPOINT = 'https://discord.com/api/v8'
CLIENT_ID = '811374808930975785'
CLIENT_SECRET = '61x9aHm50V2NvIE45MG2VwP6Ze_Dycgr'

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

url = "https://discord.com/api/v8/applications/811374808930975785/commands"

json = {
    "name": "blep",
    "description": "Send a random adorable animal photo",
    "options": [
        {
            "name": "animal",
            "description": "The type of animal",
            "type": 3,
            "required": True,
            "choices": [
                {
                    "name": "Dog",
                    "value": "animal_dog"
                },
                {
                    "name": "Cat",
                    "value": "animal_cat"
                },
                {
                    "name": "Penguin",
                    "value": "animal_penguin"
                }
            ]
        },
        {
            "name": "only_smol",
            "description": "Whether to show only baby animals",
            "type": 5,
            "required": False
        }
    ]
}


# or a client credentials token for your app with the applications.commmands.update scope
headers = {
    "Authorization": "Bearer " + get_token()
}

r = requests.post(url, headers=headers, json=json)