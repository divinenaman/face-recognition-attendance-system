query_dict = {
    "create_user_table": """
        CREATE TABLE IF NOT EXISTS user (
            id integer PRIMARY KEY,
            name text NOT NULL,
            reg text NOT NULL,
            email test NOT NULL,
            embedding array NOT NULL
        );
    """,

    "create_attendace_table": """
        CREATE TABLE IF NOT EXISTS attendance_list (
            id integer PRIMARY KEY,
            room_id integer UNIQUE
        );
    """,

    "create_room_table": """
        CREATE TABLE IF NOT EXISTS room (
            id integer PRIMARY KEY,
            room_name text NOT NULL,
            user_id integer NOT NULL
        );
    """,

    "create_login_table": """
        CREATE TABLE IF NOT EXISTS login (
            id integer PRIMARY KEY,
            username text NOT NULL,
            password integer NOT NULL
        );
    """
}
