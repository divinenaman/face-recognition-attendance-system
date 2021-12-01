import re
import base64
import bcrypt
from threading import Thread
from datetime import datetime
from utils import methods

from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC


def get_embedding_from_image_string(Model, data):
    img = data["img"]
    img = re.sub(r'data:image/.*;base64,', '', img)
    im_bytes = base64.b64decode(img)

    face = methods.extract_face(im_bytes)
    embedding = []
    for f in face:
        embedding.append(methods.get_embedding(Model, f))

    return embedding


def add_user(Model, con, data):
    try:
        cur = con.cursor()
        q = "INSERT INTO user (name, reg, email, embedding) VALUES (?, ?, ?, ?)"

        embedding = get_embedding_from_image_string(Model, data)[0]

        cur.execute(q, (data["name"], data["reg"], data["email"], embedding))
        con.commit()
        return True

    except Exception as e:
        print(e)
        return False


def identify_face(Model, con, data):
    try:
        embedding = get_embedding_from_image_string(Model, data)
        cur = con.cursor()
        q = "SELECT id,name,reg,embedding from user"
        res = cur.execute(q)
        x = []
        y_dict = {}
        y = []
        for idx, name, reg, embed in res.fetchall():
            y.append(idx)
            y_dict[idx] = (idx, name, reg)
            x.append(embed)

        model_svm = SVC(kernel='linear', probability=True)
        model_svm.fit(x, y)

        ans = model_svm.predict(embedding)
        res = [y_dict[i] for i in ans]

        return res

    except Exception as e:
        print(e)
        return None

def login(con, data):
    try:
        cur = con.cursor()
        q = "SELECT id FROM login WHERE username=? AND password=?"
        rows = cur.execute(q, (data["username"], data["password"]))
        res = rows.fetchall()
        if len(res) > 0:
            idx, = res[0]
            return {
                "login_id": idx
            }

        else:
            return None
    except Exception as e:
        print(e)
        return None

def add_login(con, data):
    try:
        cur = con.cursor()
        #hass_pass = bcrypt.hashpw(data["password"], "SECRET")

        q = "INSERT INTO login (username, password) VALUES (?, ?)"
        cur.execute(q, (data["username"], data["password"]))
        con.commit()
        return True

    except Exception as e:
        print(e)
        return False


def create_room(con, data):
    try:
        cur = con.cursor()
        q = "INSERT INTO room (room_name, user_id) VALUES (?, ?)"
        cur.execute(q, (data["room_name"], data["login_id"]))
        con.commit()
        return True
    except Exception as e:
        print(e)
        return False


def add_user_to_room(con, data):
    try:
        cur = con.cursor()
        q = "SELECT id FROM user WHERE email=?"
        rows = cur.execute(q,(data["email"],))
        res = rows.fetchall()
        idx = None

        if len(res) == 0:
            raise Exception
        else:
            (idx,) = res[0]

        q = "SELECT id FROM attendance_list WHERE user_id=? AND room_id=?"
        rows = cur.execute(q, (idx, data["room_id"]))
        res = rows.fetchall()

        if len(res) != 0:
            raise Exception

        q = "INSERT INTO attendance_list (room_id, user_id) VALUES (?, ?)"
        cur.execute(q, (data["room_id"], idx))
        con.commit()
        return True

    except Exception as e:
        print(e)
        return False


def getAllRoomInfo(con, data):
    try:
        cur = con.cursor()
        
        q = "SELECT room.room_name, room.id, user.id, user.name, user.reg FROM room JOIN attendance_list ON attendance_list.room_id = room.id JOIN user ON user.id = attendance_list.user_id WHERE room.user_id = ?"    
        rows = cur.execute(q, (data["login_id"],))
        res = rows.fetchall()
        
        q = "SELECT room.room_name, room.id FROM room WHERE user_id = ?"    
        rows = cur.execute(q, (data["login_id"],))
        res_all_rooms = rows.fetchall()
        
        preprocess = {}
        for i in res:
            rname, rid, idx, name, reg = list(map(str, i))
            
            q = "SELECT attendance_date, attendance FROM attendance WHERE user_id = ? AND room_id = ?"
            rows = cur.execute(q, (idx,rid))
            res2 = rows.fetchall()

            if preprocess.get(rid) == None:
                preprocess[rid] = {
                    "room_name": rname,
                    "room_id": rid,
                    "attendance_list": {},
                    "attendee_list": []
                }

            preprocess[rid]["attendee_list"].append({
                "name": name,
                "reg": reg
            })

            for date,attendance in res2:
                date = str(date)
                attendance = str(attendance)

                if preprocess[rid].get("attendance_list").get(date) != None:
                    preprocess[rid]["attendance_list"][date].append({
                        "name": name,
                        "reg": reg,
                        "attendance": attendance
                    })
                else:
                    preprocess[rid]["attendance_list"][date] = [{
                        "name": name,
                        "reg": reg,
                        "attendance": attendance
                    }]

        for (name,rid) in res_all_rooms:
            name = str(name)
            rid = str(rid)

            if preprocess.get(rid) == None:
                preprocess[rid] = {
                    "room_name": name,
                    "room_id": rid,
                    "attendance_list": {},
                    "attendee_list": []
                }

        return list(preprocess.values())
    except Exception as e:
        print(e)
        return None


def mark_attendance(Model, con, data):
    try:
        cur = con.cursor()
        q = "SELECT user_id FROM attendance_list WHERE room_id=?"
        rows = cur.execute(q, (data["room_id"],))
        res1 = rows.fetchall()

        if len(res1) == 0:
            return Exception

        attendance_date = datetime.now().strftime("%Y-%m-%d")
        q = "SELECT user_id FROM attendance WHERE room_id=? AND attendance_date=?"
        rows = cur.execute(q, (data["room_id"], attendance_date))
        res2 = rows.fetchall()

        q = "INSERT INTO attendance (room_id, user_id, attendance_date) VALUES (?, ?, ?)"
        vals = [(data["room_id"], i, attendance_date)
                for i, in res1 if (i,) not in res2]
        cur.executemany(q, vals)

        con.commit()

        thread = Thread(target=identify_face_and_mark_attendance,
                        args=(Model, con, data))
        thread.daemon = True
        thread.start()

        return True

    except Exception as e:
        print(e)
        return False


def mark_user_attendance(con, data):
    try:
        cur = con.cursor()
        q = "UPDATE attendance SET attendance = ? WHERE room_id = ? AND user_id = ? AND attendance_date=?"
        d = ("present", data["room_id"], data["user_id"], data["attendance_date"])
        cur.execute(q, d)

        con.commit()
        return True

    except Exception as e:
        print(e)
        return False


def identify_face_and_mark_attendance(Model, con, data):
    try:
        print("Attendance Job Running")
        attendance = identify_face(Model, con, data)
        attendance_date = datetime.now().strftime("%Y-%m-%d")
        for u, n, r in attendance:
            print(u)
            d = {
                "user_id": u,
                "room_id": data["room_id"],
                "attendance_date": attendance_date
            }
            mark_user_attendance(con, d)
        print(
            f'{attendance_date}: Attendance Complete for Room ID {d["room_id"]} ')
    except Exception as e:
        print(e)
