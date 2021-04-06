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
# fix rotten tomatoes ep scraper


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
