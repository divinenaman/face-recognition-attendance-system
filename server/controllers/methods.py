import re
import base64
import bcrypt
from datetime import datetime
from utils import methods

from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC

async def get_embedding_from_image_string(Model, data):
    img = data["img"]
    img = re.sub(r'data:image/.*;base64,','',img)
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

        cur.execute(q,(data["name"], data["reg"], data["email"], embedding))
        con.commit()
        return True
    
    except Exception as e:
        print(e)
        return False

async def identify_face(Model, con, data):
    try:
        embedding = await get_embedding_from_image_string(Model, data)
        cur = con.cursor()
        q = "SELECT id,name,reg,embedding from user"
        res = cur.execute(q)
        x = []
        y_dict = {}
        y = []
        for idx,name,reg,embed in res.fetchall():
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

def add_login(con, data):
    try: 
        cur = con.cursor()
        hass_pass = bcrypt.hashpw(data["password"], "SECRET")

        q = "INSERT INTO login (username, password) VALUES (?, ?)"
        cur.execute(q,(data["username"], hass_pass))
        con.commit()
        return True
    
    except Exception as e:
        print(e)
        return False

def create_room(con, data):
    try:
        cur = con.cursor()
        q = "INSERT INTO room (room_name, user_id) VALUES (?, ?)"
        cur.execute(q,(data["room_name"], data["user_id"]))
        con.commit()
        return True
    except Exception as e:
        print(e)
        return False

def add_user_to_room(con, data):
    try:
        cur = con.cursor()
        q = "SELECT id FROM attendance_list WHERE user_id=?"
        rows = cur.execute(q,(data["user_id"]))
        res = rows.fetchall()

        if len(res) != 0:
            return Exception

        q = "INSERT INTO attendance_list (room_id, user_id) VALUES (?, ?)"
        cur.execute(q,(data["room_id"], data["user_id"]))
        con.commit()
        return True

    except Exception as e:
        print(e)
        return False

async def start_marking_attendance(Model, con, data):
    try:
        cur = con.cursor()
        q = "SELECT user_id FROM attendance_list WHERE room_id=?"
        rows = cur.execute(q,(data["room_id"]))
        res = rows.fetchall()

        if len(res) != 0:
            return Exception

        attendance_date = datetime.now().strftime("%Y-%m-%d")
        q = "SELECT user_id FROM attendance WHERE room_id=? AND attendance_date!=? GROUP BY user_id"
        rows = cur.execute(q,(data["room_id"], attendance_date))
        res = rows.fetchall()

        if len(res) != 0:
            q = "INSERT INTO attendance (room_id, user_id, attendance_date) VALUES (?, ?, ?)"
            vals = [(data["room_id"], i, attendance_date) for i in res]
            cur.executmany(q,vals)

        con.commit()

        identify_face_and_mark_attendance(Model, con, data)

        return True
        
    except Exception as e:
        print(e)
        return False

async def mark_user_attendance(con, data):
    try:
        cur = con.cursor()
        
        attendance_date = datetime.now().strftime("%Y-%m-%d")
        q = "UPDATE attendance SET attendance = ? WHERE room_id=? AND user_id=? AND attendace_date=?"
        d = ("present", data["room_id"], data["user_id"], attendance_date)
        cur.execute(q,d)
        
        con.commit()
        return True
        
    except Exception as e:
        print(e)
        return False

async def identify_face_and_mark_attendance(Model, con, data):
    try:
        attendance = await identify_face(Model, con, data)
        for u,n,r in attendance:
            d = {
                "user_id": u,
                "room_id": data["room_id"]
            }
            await mark_user_attendance(con, d)
        attendance_date = datetime.now().strftime("%Y-%m-%d")
        print(f'{attendance_date}: Attendance Complete for Room ID {d["room_id"]} ') 
    except Exception as e:
        print(e)
        