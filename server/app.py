from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/api/face/register", methods=["POST"])
def register_student():
    content = request.get_json(silent=True)
    print(content)
    return jsonify(
        status="face registered"
    )