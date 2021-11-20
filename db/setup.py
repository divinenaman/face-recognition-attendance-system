import sqlite3
from sqlite3 import Error
from db.query import query_dict
import numpy as np
import io

compressor = 'zlib'  # zlib, bz2

def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    # zlib uses similar disk size that Matlab v5 .mat files
    # bz2 compress 4 times zlib, but storing process is 20 times slower.
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())  # zlib, bz2

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    out = io.BytesIO(out.read())
    return np.fromstring(out, dtype='>f2')

sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("array", convert_array)

def create_connection(path="/home/zorin/face-recognition-attendance-system/db/data/test.db"):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    create_tables(connection)
    return connection

def create_tables(con):
    cur = con.cursor()
    cur.execute(query_dict["create_user_table"])
    cur.execute(query_dict["create_attendace_table"])
    cur.execute(query_dict["create_room_table"])
    cur.execute(query_dict["create_login_table"])
    con.commit()

def test(con):
    cur = con.cursor()
    cur.execute("insert into user (name, reg) values (?,?)",("raj","123"))
    cur.execute("insert into user (name, reg) values (?,?)",("ram","124"))
    cur.execute("insert into user (name, reg) values (?,?)",("ram","125"))
    con.commit()

    a = cur.execute("SELECT * from user")
    print(a.fetchall())

    con.close()