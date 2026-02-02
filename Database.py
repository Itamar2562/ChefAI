import sqlite3
import json
import hashlib
from cgitb import reset
from http.client import responses

from Protocol import write_to_log
DB_NAME = "Database.db"
TABLE_USERS = "Users"
DEFAULT_LISTS=["Carbs","Vegetables","Fruits","Protein","Liquids","Spices"]


def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# close at end



def create_response_msg_db(cmd: str,username,password,default_items=0) ->str:
    conn= get_conn()
    write_to_log(conn)
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
        # INSERT DATA
        password=hash_password(password)
        response=""
        if cmd=="SIGNIN":
           response=sign_in(conn,username,password)
        elif cmd=="REG":
           response=register(conn,username,password,default_items)
        return response
    except Exception as E:
        write_to_log(f"database Error {E}")
        return f"Error"


def sign_in(conn,username,password):
    write_to_log("got here")
    cursor=conn.cursor()
    query = "SELECT EXISTS (SELECT 1 FROM users WHERE  username = ? AND password = ?)"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()[0]
    if result == 1:
        response = "connected"
    else:
        response = "Wrong username or password"
    return response

def register(conn,username,password,default_items):
    write_to_log("got here")
    cursor=conn.cursor()
    try:
        if user_exists(conn,username,password):
            write_to_log(f"exists")
            response="Username already taken"
            return response
        # Insert data record
        cursor.execute('''INSERT INTO users(username, password) VALUES(?,?)''', (username, password))
        user_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO lists (user_id, name, is_main) VALUES (?, ?, 1)",
            (user_id, "Main")
        )
        if default_items==1:
            put_default_lists(conn,user_id)
        # confirm and save data to DB
        conn.commit()
        response = "saved to database"
        return response
    except Exception as E:
        write_to_log(f"error {E}")
        response = f"Error {E}"
        conn.rollback()
        return response


def user_exists(conn,username,password) -> bool:
    cursor=conn.cursor()
    """
    Checks if a user with the given username exists in the 'users' table.
    """
    # Use a placeholder '?' to safely pass the username parameter
    query = 'SELECT EXISTS(SELECT 1 FROM users WHERE username = ? AND password = ?)'
    cursor.execute(query, (username,password))

    # Fetch the result (a single row with one value: 0 or 1)
    # fetchone() returns a tuple, e.g., (1,) or (0,)
    result = cursor.fetchone()[0]
    return result == 1

def put_default_lists(conn,user_id):
    write_to_log(f"userod {user_id}")
    cursor=conn.cursor()
    for list_name in DEFAULT_LISTS:
        cursor.execute(
            "INSERT INTO lists (user_id, name, is_main) VALUES (?, ?, 0)",
            (user_id, list_name))
    conn.commit()
    return True


def hash_password(password):
    return str(hashlib.sha256(password.encode('utf-8')).hexdigest())

def get_id(username,password):
    conn = get_conn()
    cursor = conn.cursor()
    password = hash_password(password)
    try:
        query = "SELECT id FROM users WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()[0]
        return result
    except Exception as e:
        write_to_log(e)
        conn.rollback()
        return -1

def get_list_id_by_name(user_id, list_name):
    conn = get_conn()
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

def handle_ingredient_update(user_id,list_name,prev_name, curr_name):
    write_to_log("got here 2213")
    list_id=get_list_id_by_name(user_id, list_name)

    if not prev_name:
        return create_ingredient(list_id, curr_name)

    if prev_name != curr_name:
        return rename_ingredient(list_id, prev_name, curr_name)
    return False

def create_ingredient(list_id, name):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        if ingredient_exists(list_id,name):
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
        write_to_log(e)
        conn.rollback()
        return "500"

def rename_ingredient(list_id, prev_name, new_name):
    conn = get_conn()
    cursor = conn.cursor()
    # block duplicate names in same list
    try:
        ingredient_exists(list_id,prev_name)
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
        write_to_log(e)
        conn.rollback()
        return False

def ingredient_exists(dst_list_id,ingredient):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id FROM ingredients
        WHERE list_id=? AND name=?
        """, (dst_list_id, ingredient))
    if cursor.fetchone():
        return True
    return False


def transfer_ingredient(user_id,src_list,dst_list,ingredient):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        write_to_log("got to transf")
        src_list_id=get_list_id_by_name(user_id,src_list)
        dst_list_id=get_list_id_by_name(user_id,dst_list)
        #check if ingredient in dst list
        if ingredient_exists(dst_list_id,ingredient):
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


def handle_db_list_update(user_id:int, data:list):
    write_to_log("im here")
    prev_name=data[0]
    curr_name=data[1]
    write_to_log(curr_name)
    if not prev_name:
        return create_list(user_id, curr_name)

    if prev_name != curr_name:
        return rename_list(user_id, prev_name, curr_name)

    return "500"

def create_list(user_id, list_name):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        if list_exists(user_id,list_name):
           return "409"
        cursor.execute(
            "INSERT INTO lists (user_id, name, is_main) VALUES (?, ?, 0)",
            (user_id, list_name)
        )
        conn.commit()
        return "200"
    except:
        conn.rollback()
        return "500"

def list_exists(user_id,new_name):
    conn = get_conn()
    cursor = conn.cursor()
    # Prevent duplicate names
    cursor.execute(
        "SELECT id FROM lists WHERE user_id=? AND name=?",
        (user_id, new_name)
    )
    if cursor.fetchone():
        return True
    return False


def rename_list(user_id, prev_name, new_name):
    conn = get_conn()
    cursor = conn.cursor()
    if list_exists(user_id,new_name):
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

def get_lists_with_ingredients(user_id: int) -> dict[str, list[str]]:
    conn = get_conn()
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

def delete_ingredient(user_id: int, list_name: str, ingredient_name: str):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        write_to_log(user_id)
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
        write_to_log(e)
        conn.rollback()
        return "500"

def remove_all_ingredients(user_id,list_name):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        DELETE FROM ingredients WHERE list_id = ( SELECT id FROM lists WHERE user_id = ?AND name = ?)
        """,(user_id,list_name ))
        conn.commit()
        return "200"
    except Exception as E:
        write_to_log(E)
        conn.rollback()
        return "500"

def delete_list(user_id: int, list_name: str):
    conn = get_conn()
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

def close_conn():
    conn=get_conn()
    conn.close()

# def handle_registration(client_socket) :
#     data = client_socket.recv(1024).decode()
#     registration_data = json.loads(data)
#
#     login = registration_data.get('login')
#     password = registration_data.get('password')
#
#     if is_valid(login, password):
#         encryption_key = generate_key().decode()
#         client_data = {'login': login, 'encryption_key': encryption_key}
#         save_client_data(client_data)
#
#         response = {'success': True, 'encryption_key': encryption_key}
#     else:
#         response = {'success': False, 'error': 'Invalid credentials'}
#
#     client_socket.send(json.dumps(response).encode())


def is_valid(login, password):
    return len(login) > 0 and len(password) > 0
