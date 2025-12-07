import json
import sqlite3
import json
import hashlib

from Protocol import write_to_log

DB_NAME = "MyProject.db"
TABLE_USERS = "Users"


def create_response_msg_db(cmd: str,data :str) ->str:
    conn = sqlite3.connect("MyProject.db")
    try:
        # connect to DB(if it doesn't exist, it will be created)
        # Create object 'curser' to execute SQL-queries
        curser = conn.cursor()

        # table creation user table
        curser.execute('''
                      CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY,
                      name TEXT NOT NULL UNIQUE,
                      password TEXT NOT NULL,
                      ingredients Text not NULL,
                      level TEXT not null
                      )
                  ''')
        data=json.loads(data)
        write_to_log(data)
        # INSERT DATA
        password=hash_password(data["password"])
        if cmd=="SIGNIN":
            query = "SELECT EXISTS (SELECT 1 FROM users WHERE name = ? AND password = ?)"
            curser.execute(query, (data["name"], password))
            result = curser.fetchone()[0]
            if result==1:
                response = "connected"
            else:
                response="user doesn't exists"
        elif cmd=="REG":
            # Insert data record
            curser.execute('''
            INSERT INTO users(name, password,ingredients,level) VALUES(?,?,?,?)
            ''', (data["name"],password,'[]',1))
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
            response="Error"
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
    conn = sqlite3.connect("MyProject.db")
    curser = conn.cursor()
    data = json.loads(data)
    password = hash_password(data["password"])
    try:
        query = "SELECT id FROM users WHERE name = ? AND password = ?"
        curser.execute(query, (data["name"], password))
        result = curser.fetchone()[0]
        conn.close()
        return result
    except:
        conn.rollback()
        return -1

def add_ingredient_to_db_by_id(user_id,ingredient):
    conn=sqlite3.connect("MyProject.db")
    curser = conn.cursor()
    try:
        ingredients_list=get_ingredients_list(user_id)
        ingredient=json.loads(ingredient)
        #search if the ingredient is already inside the list
        #if it is change if not append
        found=replace_in_array(ingredients_list,ingredient)
        if not found:
            ingredients_list.append(ingredient[1])
        ingredients_list=json.dumps(ingredients_list)
        query="UPDATE users SET ingredients = ? WHERE id = ?"
        curser.execute(query,(ingredients_list,user_id))
        # confirm and save data to DB
        conn.commit()
        conn.close()
        return True
    except Exception as E:
        conn.rollback()
        return False

#function receives ingredients list and a
def replace_in_array(ingredients_list,ingredient):
    for i in range(len(ingredients_list)):
        if ingredients_list[i] == ingredient[0]:
            ingredients_list[i] = ingredient[1]
            return True
    return False


def get_ingredients_list(user_id):
    conn = sqlite3.connect("MyProject.db")
    curser = conn.cursor()
    try:
        query = "SELECT ingredients FROM users WHERE id= ?"
        curser.execute(query, (user_id,))
        ingredients_list = curser.fetchone()[0]
        ingredients_list = json.loads(ingredients_list)
        conn.close()
        return ingredients_list
    except:
        conn.rollback()
        return []
def remove_ingredient(user_id,ingredient):
    conn = sqlite3.connect("MyProject.db")
    curser = conn.cursor()
    try:
        query = "SELECT ingredients FROM users WHERE id= ?"
        curser.execute(query, (user_id,))
        ingredients_list = curser.fetchone()[0]
        ingredients_list = json.loads(ingredients_list)
        ingredients_list.remove(ingredient)
        ingredients_list=json.dumps(ingredients_list)
        query = "UPDATE users SET ingredients = ? WHERE id = ?"
        curser.execute(query, (ingredients_list, user_id))
        # confirm and save data to DB
        conn.commit()
        conn.close()
        return True
    except Exception as E:
        conn.rollback()
        return False


def get_level_by_id(user_id):
    conn = sqlite3.connect("MyProject.db")
    curser = conn.cursor()
    try:
        query="SELECT level FROM users WHERE id=?"
        curser.execute(query,(user_id, ))
        level=curser.fetchone()[0]
        conn.close()
        return level
    except:
        conn.rollback()
        return -1




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
