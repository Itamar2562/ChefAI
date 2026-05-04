import sqlite3

from ServerPRO import write_to_log, MAX_AI_USAGE_AMOUNT, check_hash

DB_NAME = "Database.db"
PANTRY_STAPLES= {"Carbs":[], "Vegetables":[], "Fruits":[], "Protein":[],
                 "Liquids":["water"], "Spices":["salt","pepper"]}

#just give conn to client handler maybe
def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_response_msg_db(conn, cmd, username, password, pantry_staples=0):
    cursor=conn.cursor()
    try:
        # connect to DB(if it doesn't exist, it will be created)
        # Create object 'curser' to execute SQL-queries
        # table creation user table
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)

        # Lists table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            is_main INTEGER DEFAULT 0,
            UNIQUE (user_id, name),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        # Ingredients table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (list_id) REFERENCES lists(id) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_usage (
    user_id TEXT,
    usage_date DATE,
    usage_count INTEGER,
    PRIMARY KEY (user_id, usage_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
        
        """)
        # INSERT DATA
        response=""
        if cmd=="SIGNIN":
           response=sign_in(conn,username,password)
        elif cmd=="REG":
           response=register(conn, username, password, pantry_staples)
        return response
    except Exception as e:
        write_to_log(f"database Error {e}")
        return "500",-1


def sign_in(conn,username,password):
    cursor=conn.cursor()
    query = "SELECT * FROM users WHERE  username = ?"
    cursor.execute(query,(username, ))
    result = cursor.fetchone()
    write_to_log(f"Result: {result}")
    if result and check_hash(password,result[2]):
        response = "200",result[0]
    else:
        response = "401",-1
    return response

def register(conn,username,password,pantry_staples):
    cursor=conn.cursor()
    try:
        if user_exists(conn,username):
            write_to_log(f"user exists worked")
            response="409",-1
            return response
        # Insert data record
        cursor.execute('''INSERT INTO users(username, password) VALUES(?,?)''', (username, password))
        user_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO lists (user_id, name, is_main) VALUES (?, ?, 1)",
            (user_id, "Main")
        )
        if pantry_staples==1:
            add_pantry_staples(conn, user_id)
        # confirm and save data to DB
        conn.commit()
        response = "200",-1
        return response
    except Exception as e:
        write_to_log(f"database Error {e}")
        response = "500",-1
        conn.rollback()
        return response



def user_exists(conn,username):
    write_to_log("got to exists")
    cursor = conn.cursor()
    # Prevent duplicate names
    cursor.execute(
        "SELECT id FROM users WHERE username=? ",
        (username, )
    )
    if cursor.fetchone():
        return True
    return False


def add_pantry_staples(conn, user_id):
    cursor=conn.cursor()
    for list_name, ingredients in PANTRY_STAPLES.items():
        # Insert the list
        cursor.execute(
            "INSERT INTO lists (user_id, name, is_main) VALUES (?, ?, 0)",
            (user_id, list_name)
        )

        # Get the ID of the list we just inserted
        list_id = cursor.lastrowid

        # Insert ingredients for this list
        for ingredient in ingredients:
            cursor.execute(
                "INSERT INTO ingredients (list_id, name) VALUES (?, ?)",
                (list_id, ingredient)
            )
    return True



def get_id(conn,username,password):
    cursor = conn.cursor()
    try:
        query = "SELECT id FROM users WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()[0]
        return result
    except Exception as e:
        write_to_log(f"[Client_BL] error {e} while getting user id from DB")
        conn.rollback()
        return -1

def handle_ai_usage(conn, user_id, today):
    cursor=conn.cursor()
    ai_usage=get_ai_usage_count(conn,user_id,today)
    if ai_usage ==0:
        cursor.execute("INSERT INTO ai_usage (user_id,usage_date,usage_count) VALUES (?,?,1)",
                     (user_id,today))
        conn.commit()
        return 1
    elif ai_usage<MAX_AI_USAGE_AMOUNT:
        cursor.execute("UPDATE  ai_usage SET usage_count=? WHERE user_id=? AND usage_date=?",
                     (ai_usage+1,user_id, today))
        conn.commit()
        return ai_usage+1
    return ai_usage+1

def get_ai_usage_count(conn,user_id,today):
    cursor = conn.cursor()
    cursor.execute("SELECT usage_count FROM ai_usage WHERE user_id = ? AND usage_date = ?", (user_id, today))
    result = cursor.fetchone()
    if result is None:
        return 0
    else:
        return result[0]

def clear_ai_usage_from_db(conn):
    cursor=conn.cursor()
    cursor.execute("DELETE FROM ai_usage WHERE usage_date < DATE('now','-30 days')")
    conn.commit()

def get_list_id_by_name(conn,user_id, list_name):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id
        FROM lists
        WHERE user_id = ? AND name = ?
        """,
        (user_id, list_name)
    )
    row = cursor.fetchone()
    return row[0] if row else None

def create_ingredient(conn,user_id,list_name, name):
    list_id=get_list_id_by_name(conn,user_id, list_name)
    cursor = conn.cursor()
    try:
        if ingredient_exists(conn,list_id,name):
            return "409"
        cursor.execute(
            """
            INSERT INTO ingredients (list_id, name)
            VALUES (?, ?)
            """,
            (list_id, name)
        )
        conn.commit()
        return "200"
    except Exception as e:
        write_to_log(f"[Client_BL] error {e} while creating ingredient in DB")
        conn.rollback()
        return "500"

def rename_ingredient(conn,user_id,list_name, prev_name, new_name):
    list_id=get_list_id_by_name(conn,user_id, list_name)
    cursor = conn.cursor()
    # block duplicate names in same list
    try:
        if ingredient_exists(conn,list_id,new_name):
            return "409"
        cursor.execute(
            """
            UPDATE ingredients
            SET name=?
            WHERE list_id=? AND name=?
            """,
            (new_name, list_id, prev_name)
        )

        if cursor.rowcount == 0:
            return "500"
        conn.commit()
        return "200"
    except Exception as e:
        write_to_log(f"[Client_BL] error {e} while renaming ingredient in DB")
        conn.rollback()
        return "500"

def ingredient_exists(conn,dst_list_id,ingredient):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id FROM ingredients
        WHERE list_id=? AND name=?
        """, (dst_list_id, ingredient))
    if cursor.fetchone():
        return True
    return False

def delete_ingredient(conn,user_id: int, list_name: str, ingredient_name: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM ingredients
            WHERE name = ? AND list_id = ( SELECT id FROM lists WHERE user_id = ?AND name = ?)
            """,
            (ingredient_name, user_id, list_name)
        )
        conn.commit()
        return "200"
    except Exception as e:
        write_to_log(f"[Server_BL] error {e} while deleting ingredient from DB")
        conn.rollback()
        return "500"



def transfer_ingredient(conn,user_id,src_list,dst_list,ingredient):
    cursor = conn.cursor()
    try:
        src_list_id=get_list_id_by_name(conn,user_id,src_list)
        dst_list_id=get_list_id_by_name(conn,user_id,dst_list)
        #check if ingredient in dst list
        if ingredient_exists(conn,dst_list_id,ingredient):
            return "409"
        cursor.execute(
            """
            UPDATE ingredients
            SET list_id=?
            WHERE list_id=? AND name=?
            """,
            (dst_list_id, src_list_id, ingredient)
        )
        conn.commit()
        return "200"
    except:
        conn.rollback()
        return "500"


def create_list(conn,user_id, list_name):
    write_to_log("got to create list")
    cursor = conn.cursor()
    try:
        if list_exists(conn,user_id,list_name):
           return "409"
        write_to_log("doesn't exists")
        cursor.execute(
            "INSERT INTO lists (user_id, name, is_main) VALUES (?, ?, 0)",
            (user_id, list_name)
        )
        write_to_log("inserted")
        conn.commit()
        return "200"
    except Exception as e:
        write_to_log(e)
        conn.rollback()
        return "500"

def list_exists(conn,user_id,new_name):
    cursor = conn.cursor()
    # Prevent duplicate names
    cursor.execute(
        "SELECT id FROM lists WHERE user_id=? AND name=?",
        (user_id, new_name)
    )
    if cursor.fetchone():
        return True
    return False


def rename_list(conn,user_id, prev_name, new_name):
    cursor = conn.cursor()
    if list_exists(conn,user_id,new_name):
        return "409"
    cursor.execute(
        """
        UPDATE lists
        SET name=?
        WHERE user_id=? AND name=? AND is_main=0
        """,
        (new_name, user_id, prev_name)
    )

    if cursor.rowcount == 0:
        return "500"  # list not found

    conn.commit()
    return "200"

def clear_list(conn, user_id, list_name):
    cursor = conn.cursor()
    try:
        cursor.execute("""
        DELETE FROM ingredients WHERE list_id = ( SELECT id FROM lists WHERE user_id = ?AND name = ?)
        """,(user_id,list_name ))
        conn.commit()
        return "200"
    except Exception as e:
        write_to_log(f"[Server_BL] error {e} while clearing user's ingredients from DB")
        conn.rollback()
        return "500"

def delete_list(conn,user_id: int, list_name: str):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM lists
            WHERE name = ?
              AND user_id = ?
            """,
            (list_name, user_id)
        )
        conn.commit()
        return "200"
    except Exception as e:
        write_to_log(f"[Server_BL] error {e} while deleting user's list from DB")
        conn.rollback()
        return "500"


def get_lists_with_ingredients(conn,user_id: int) -> dict[str, list[str]]:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT l.name, i.name
        FROM lists l
        LEFT JOIN ingredients i ON i.list_id = l.id
        WHERE l.user_id = ?
        ORDER BY l.id
        """,
        (user_id,)
    )

    result = {}
    for list_name, ingredient_name in cursor.fetchall():
        if list_name not in result:
            result[list_name] = []
        if ingredient_name is not None:
            result[list_name].append(ingredient_name)

    return result

def close_conn(conn):
    conn.close()

