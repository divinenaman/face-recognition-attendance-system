from flask import Flask
from flask import request
from flask import jsonify

import models.Facenet as Facenet
import db.setup as db
from server.controllers import user as user_controller

Model = Facenet.load_model()
con = db.create_connection()


app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/api/face/register", methods=["POST"])
def register_face():
    data = request.get_json(silent=True)
    res = user_controller.add_user(Model, con, data)
    if res == True:
        return jsonify(
            status="success",
            msg="Face Registered"    
        )
    else:
        return jsonify(
            status="error",
            msg="Something Went Wrong"
        )

@app.route("/api/face/identify", methods=["POST"])
def identify_face():
    data = request.get_json(silent=True)
    res = user_controller.identify_face(Model, con, data)
    if res != None:
        return jsonify(
            status="success",
            msg=res    
        )
    else:
        return jsonify(
            status="error",
            msg="Not Found"
        )