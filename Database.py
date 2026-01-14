import sqlite3
import json
import hashlib

from Protocol import write_to_log
DB_NAME = "Database.db"
TABLE_USERS = "Users"

# close at end
def create_response_msg_db(cmd: str,data :str) ->str:
    conn = sqlite3.connect(DB_NAME)
    try:
        # connect to DB(if it doesn't exist, it will be created)
        # Create object 'curser' to execute SQL-queries
        cursor = conn.cursor()

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
        data=json.loads(data)
        write_to_log(data)
        # INSERT DATA
        password=hash_password(data["password"])
        if cmd=="SIGNIN":
            query = "SELECT EXISTS (SELECT 1 FROM users WHERE  username = ? AND password = ?)"
            cursor.execute(query, (data["name"], password))
            result = cursor.fetchone()[0]
            if result==1:
                response = "connected"
            else:
                response="User doesn't exists"
        elif cmd=="REG":
            # Insert data record
            cursor.execute('''
            INSERT INTO users(username, password) VALUES(?,?)
            ''', (data["name"],password))
            user_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO lists (user_id, name, is_main) VALUES (?, ?, 1)",
                (user_id, "Main")
            )
            # confirm and save data to DB
            conn.commit()
            response="saved to database"
        # close connection
        else:
            response="Error"

        conn.close()
        return response
        #response = data
    except Exception as E:
        if str(E)=="UNIQUE constraint failed: users.name":
            response = f"Username already exists"
        else:
            response=f"Error {E}"
        conn.rollback()
        return response

#def generate_key() -> bytes:
 #   return Fernet.generate_key()

def save_client_data(client_data):
    # Here should be code to save data to DB
    print("Client data saved:", client_data)

def hash_password(password):
    return str(hashlib.sha256(password.encode('utf-8')).hexdigest())

def get_id(data):
    conn = sqlite3.connect(DB_NAME)
    curser = conn.cursor()
    data = json.loads(data)
    password = hash_password(data["password"])
    try:
        query = "SELECT id FROM users WHERE username = ? AND password = ?"
        curser.execute(query, (data["name"], password))
        result = curser.fetchone()[0]
        conn.close()
        return result
    except Exception as e:
        write_to_log(e)
        conn.rollback()
        return -1

def get_list_id_by_name(user_id, list_name):
    conn = sqlite3.connect(DB_NAME)
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

def handle_ingredient_update(user_id,data):
    write_to_log("got here 2213")
    prev_name=data[1]
    curr_name=data[2]
    list_id=get_list_id_by_name(user_id,data[0])

    if not prev_name:
        return create_ingredient(user_id, list_id, curr_name)

    if prev_name != curr_name:
        return rename_ingredient(user_id, list_id, prev_name, curr_name)

    return False

def create_ingredient(user_id, list_id, name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # prevent duplicates in same list
        cursor.execute(
            """
            SELECT id FROM ingredients
            WHERE list_id=? AND name=?
            """,
            (list_id, name)
        )
        if cursor.fetchone():
            return False
        cursor.execute(
            """
            INSERT INTO ingredients (list_id, name)
            VALUES (?, ?)
            """,
            (list_id, name)
        )
        conn.commit()
        return True
    except Exception as e:
        write_to_log(e)
        conn.rollback()
        return False

def rename_ingredient(user_id, list_id, prev_name, new_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # block duplicate names in same list
    try:
        cursor.execute(
            """
            SELECT id FROM ingredients
            WHERE list_id=? AND name=?
            """,
            (list_id, new_name)
        )
        if cursor.fetchone():
            return False

        cursor.execute(
            """
            UPDATE ingredients
            SET name=?
            WHERE list_id=? AND name=?
            """,
            (new_name, list_id, prev_name)
        )

        if cursor.rowcount == 0:
            return False
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        write_to_log(e)
        conn.rollback()
        return False

def handle_db_list_update(user_id:int, data:list):
    write_to_log("im here")
    prev_name=data[0]
    curr_name=data[1]
    write_to_log(curr_name)
    if not prev_name:
        return create_list(user_id, curr_name)

    if prev_name != curr_name:
        return rename_list(user_id, prev_name, curr_name)

    return False

def create_list(user_id, list_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM lists WHERE user_id=? AND name=?",
            (user_id, list_name)
        )
        if cursor.fetchone():
            return False  # already exists

        cursor.execute(
            "INSERT INTO lists (user_id, name, is_main) VALUES (?, ?, 0)",
            (user_id, list_name)
        )
        conn.commit()
        return True
    except:
        conn.rollback()
        return False

def rename_list(user_id, prev_name, new_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Prevent duplicate names
    cursor.execute(
        "SELECT id FROM lists WHERE user_id=? AND name=?",
        (user_id, new_name)
    )
    if cursor.fetchone():
        return False

    cursor.execute(
        """
        UPDATE lists
        SET name=?
        WHERE user_id=? AND name=? AND is_main=0
        """,
        (new_name, user_id, prev_name)
    )

    if cursor.rowcount == 0:
        return False  # list not found

    conn.commit()
    return True

def get_lists_with_ingredients(user_id: int) -> dict[str, list[str]]:
    conn = sqlite3.connect(DB_NAME)
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
    conn = sqlite3.connect(DB_NAME)
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
        conn.close()
        return True
    except Exception as e:
        write_to_log(e)
        conn.rollback()
        return False

def remove_all_ingredients(user_id):
    conn = sqlite3.connect(DB_NAME)
    curser = conn.cursor()
    try:
        query = "SELECT ingredients FROM users WHERE id= ?"
        curser.execute(query, (user_id,))
        ingredients_list = curser.fetchone()[0]
        ingredients_list = json.loads(ingredients_list)
        ingredients_list.clear()
        ingredients_list = json.dumps(ingredients_list)
        query = "UPDATE users SET ingredients = ? WHERE id = ?"
        curser.execute(query, (ingredients_list, user_id))
        # confirm and save data to DB
        conn.commit()
        conn.close()
        return True
    except Exception as E:
        write_to_log(E)
        conn.rollback()
        return False

def delete_list(user_id: int, list_name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM lists
        WHERE name = ?
          AND user_id = ?
        """,
        (list_name, user_id)
    )



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
