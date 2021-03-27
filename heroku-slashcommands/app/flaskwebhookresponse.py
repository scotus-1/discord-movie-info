from flask import Flask, request, jsonify, render_template
from discord_interactions import verify_key_decorator

CLIENT_PUBLIC_KEY = "d164a6f844f2d9b2026508f3e826aeac830b8131ab95d22957f681d4d15b555f"
app = Flask(__name__)

@app.route('/interactions', methods=['POST'])
@verify_key_decorator(CLIENT_PUBLIC_KEY)
def pong():
    if request.json["type"] == 1:
        return jsonify({
            "type": 1
        })
    else:
        return jsonify({
            "type": 4,
            # type4 with message
            "data": {
                "tts": False,
                "content": "Congrats on sending your command!",
                "embeds": [],
                "allowed_mentions": []
            }
        })



