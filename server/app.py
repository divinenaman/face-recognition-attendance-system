from flask import Flask
from flask import request
from flask import jsonify

import models.Facenet as Facenet
import db.setup as db
from server.controllers import methods as Controllers
from flask_cors import CORS


Model = Facenet.load_model()
con = db.create_connection()


app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/api/face/register", methods=["POST"])
def register_face():
    """
        POST: {
            "name": STRING,
            "reg": STRING,
            "img": BASE64 IMAGE STRING
        }
    """
    data = request.get_json(silent=True)
    res = Controllers.add_user(Model, con, data)
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
    """
        POST: {
            "img": BASE64 IMAGE STRING
        }
    """
    data = request.get_json(silent=True)
    res = Controllers.identify_face(Model, con, data)
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

@app.route("/api/room/create", methods=["POST"])
def create_room():
    """
        POST: {
            "room_name": STRING,
            "user_id": INT
        }
    """
    data = request.get_json(silent=True)
    res = Controllers.create_room(con, data)
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

@app.route("/api/room/addUser", methods=["POST"])
def add_user_to_room():
    """
        POST: {
            "room_id": INT,
            "user_id": INT
        }
    """
    data = request.get_json(silent=True)
    res = Controllers.add_user_to_room(con, data)
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

@app.route("/api/attendance/start", methods=["POST"])
def adding_user_to_room():
    """
        POST: {
            "room_id": INT,
            "login_id": INT
        }
    """
    data = request.get_json(silent=True)
    res = Controllers.start_marking_attendance(Model, con, data)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4001)