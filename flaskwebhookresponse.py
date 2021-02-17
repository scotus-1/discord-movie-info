from flask import Flask, request, jsonify
from discord_interactions import verify_key_decorator

CLIENT_PUBLIC_KEY = "d164a6f844f2d9b2026508f3e826aeac830b8131ab95d22957f681d4d15b555f"
app = Flask(__name__)

@app.route('/', methods=['POST'])
@verify_key_decorator(CLIENT_PUBLIC_KEY)
def pong():
    if request.json["type"] == 1:
        return jsonify({
            "type": 1
        })

app.run(debug=True)