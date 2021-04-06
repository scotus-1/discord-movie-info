from flask import Flask, request, jsonify
from discord_interactions import verify_key_decorator
from app.router import router
from app import channels
import os


# create Flask App
app = Flask(__name__)


# improve search results
# create manuel overrides for ratings and add table for quicker times
# add seasons and episodes
# fix rotten tomatoes tv scraper
# better availability checks
# most foreign tv shows dont work?
# MORE ROTTEN TOMATOES HANDLING AND APPARENTLY METACRITIC (if ends in underscore remove)
# remove the last comma
# fix threading issues


@app.route('/interactions', methods=['POST'])
@verify_key_decorator(os.environ.get("DISCORD_CLIENT_PUBLIC_KEY"))
def pong():
    if request.json["type"] == 1:
        return jsonify({
            "type": 1
        })
    else:
        print(request.data)
        router.run(request)

        return jsonify({
            "type": 5
        })
