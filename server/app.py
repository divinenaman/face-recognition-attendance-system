from flask import Flask
from flask import request
from flask import jsonify

import models.Facenet as Facenet
import db.setup as db
from server.controllers import methods as Controllers
import server.service.mqtt as mqtt
from flask_cors import CORS

from utils import methods


Model = Facenet.load_model()
con = db.create_connection()
mqtt_con = mqtt.connect_mqtt()

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/auth/login", methods=["POST"])
def user_login():
    """
        POST: {
            "username": STRING,
            "password:: STRING
        }
    """
    data = request.get_json(silent=True)
    res = Controllers.login(con, data)
    if res != None:
        return jsonify(
            status="success",
            msg=res
        )
    else:
        return jsonify(
            status="error",
            msg="Something Went Wrong"
        )

@app.route("/api/auth/signUp", methods=["POST"])
def user_signUp():
    """
        POST: {
            "username": STRING,
            "password": STRING
        }
    """
    data = request.get_json(silent=True)
    res = Controllers.add_login(con, data)
    if res == True:
        return jsonify(
            status="success",
            msg="user login added"
        )
    else:
        return jsonify(
            status="error",
            msg="Something Went Wrong"
        )


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

@app.route("/api/user/get")
def get_all_attendee_info():
    res = Controllers.getAllAttendee(con)

    if res != None:
        return jsonify(
            status="success",
            msg=res    
        )

    else:
        return jsonify(
            status="error",
            msg="Something Went Wrong"
        )

@app.route("/api/room/create", methods=["POST"])
def create_room():
    """
        POST: {
            "room_name": STRING,
            "login_id": INT
        }
    """
    data = request.get_json(silent=True)
    res = Controllers.create_room(con, data)
    if res != None:
        return jsonify(
            status="success",
            msg="Room created"    
        )
    else:
        return jsonify(
            status="error",
            msg="Something went wrong"
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
            msg="User added to Room"    
        )
    else:
        return jsonify(
            status="error",
            msg="Something went wrong"
        )

@app.route("/api/room/get", methods=["POST"])
def get_room_info():
    """
        POST: {
            "login_id": INT
        }
    """
    data = request.get_json(silent=True)
    res = Controllers.getAllRoomInfo(con, data)
    if res != None:
        return jsonify(
            status="success",
            msg=res
        )
    else:
        return jsonify(
            status="error",
            msg=None
        )
@app.route("/api/attendance/start", methods=["POST"])
def start_attendance():
    """
        POST: {
            "room_id": INT,
            "physical_room_id: STRING
        }
    """
    data = request.get_json(silent=True)
    topic = f'/room/{data["physical_room_id"]}'
    a = { "room_id": data["room_id"] }
    res = mqtt.publish(mqtt_con, topic, a)
    
    if res != None:
        return jsonify(
            status="success",
            msg="Attendace job published"    
        )
    else:
        return jsonify(
            status="error",
            msg="Something went wrong"
        )

@app.route("/api/attendance/capture", methods=["POST"])
def mark_attendance():
    """
        POST: {
            "room_id": INT,
            "img": BASE64 IMAGE STRING
        }
    """
    data = request.get_json(silent=True)
    res = Controllers.mark_attendance(Model, con, mqtt_con, data)
    if res == True:
        return jsonify(
            status="success",
            msg="Attendace job running"    
        )
    else:
        return jsonify(
            status="error",
            msg="Something went wrong"
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4001)