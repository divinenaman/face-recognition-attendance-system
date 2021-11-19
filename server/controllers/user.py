import bcrypt

def add_user(con, data):
    try: 
        cur = con.cursor()
        q = "INSERT INTO user (name, reg, email) VALUES (?, ?, ?)"
        cur.execute(q,(data["name"], data["reg"], data["email"]))
        con.commit()
        return True
    except:
        return False

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

