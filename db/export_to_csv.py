import sqlite3
import os
import csv


def create_connection(path=os.path.join(os.getcwd(),"data","test.db")):
    connection = None
    try:
        connection = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
        print("Connection to SQLite DB successful")
    except Exception as e:
        print(f"The error '{e}' occurred")

    return connection

def serialize_to_csv(con, table, path):
    cur = con.cursor()
    cur.execute(f"select * from {table}")
    
    with open(path, "w") as csv_file:
      csv_writer = csv.writer(csv_file, delimiter="\t")
      csv_writer.writerow([i[0] for i in cur.description])
      csv_writer.writerows(cur)


tables = ["login","user","attendance_list","attendance","room"]
con = create_connection()

for t in tables:
    try:
        path = os.path.join(os.getcwd(), "data", "csv", f"{t}.csv")
        serialize_to_csv(con, t, path)
    except Exception as e:
        print(e)