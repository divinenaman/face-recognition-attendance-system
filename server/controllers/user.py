import re
import base64
import bcrypt
from utils import methods

from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC

def get_embedding_from_image_string(Model, data):
    img = data["img"]
    img = re.sub(r'data:image/.*;base64,','',img)
    im_bytes = base64.b64decode(img)    
    
    face = methods.extract_face(im_bytes)[0]
    embedding = methods.get_embedding(Model, face)
    
    return embedding

def add_user(Model, con, data):
    try: 
        cur = con.cursor()
        q = "INSERT INTO user (name, reg, email, embedding) VALUES (?, ?, ?, ?)"

        embedding = get_embedding_from_image_string(Model, data)

        cur.execute(q,(data["name"], data["reg"], data["email"], embedding))
        con.commit()
        return True
    
    except Exception as e:
        print(e)
        return False

def identify_face(Model, con, data):
    try:
        embedding = get_embedding_from_image_string(Model, data)
        cur = con.cursor()
        q = "SELECT name,reg,embedding from user"
        res = cur.execute(q)
        x = []
        y = []
        for name,reg,embed in res.fetchall():
            y.append(name)
            x.append(embed)

        print(embedding, x)
        out_encoder = LabelEncoder()
        out_encoder.fit(y)
        encoded_y = out_encoder.transform(y)
        
        model_svm = SVC(kernel='linear', probability=True)
        model_svm.fit(x, encoded_y)
        
        ans = model_svm.predict(embedding)
        ans = encoded_y.inverse_transform(ans)
        
        return ans

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
    
    except:
        return False

