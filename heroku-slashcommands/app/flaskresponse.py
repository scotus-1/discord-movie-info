from flask import Flask, request, jsonify
from discord_interactions import verify_key_decorator
from app.router.router import Router
import os


# create Flask App and router
app = Flask(__name__)
router = Router(__name__)


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
