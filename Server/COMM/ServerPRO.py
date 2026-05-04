import logging
import socket
from datetime import datetime,timedelta
import json
import bcrypt

SERVER_IP="0.0.0.0"
PORT=8822

HEADER_LEN = 4
DATABASE_CMD=["SIGNIN","REG","SIGN_OUT"]
INGREDIENTS_CMD=["ADD","RENAME","DELETE","TRANSFER"]
LIST_CMD=["ADD_LIST","RENAME_LIST","DELETE_LIST","CLEAR_LIST"]
AI_CMD=["MAKE","AI_USAGE"]
MAX_AI_USAGE_AMOUNT=500
DEFAULT_AI_RESPONSE='{"recipes": [{"type": "General","time": 0,"difficulty": "Easy","name": "no available recipes","description": "","nutrition": "","data": ""}]}'
ALREADY_LOGGED_IN_MASSAGE="Your account is already logged in on another device.\n Please log out from the other session before logging in here."
MAX_AI_RETRIES=3

SCREEN_WIDTH = 1004
SCREEN_HEIGHT = 526


Codes={
    "200": "successfully", #response
    "201": "saved to database", #when creating smg
    "401": "Wrong username or password", #when pw isn't right
    "409" : "already exists", #when trying to add smg that already exists
    "500" :"server error", #error.
    "503" : "service unavailable"
}

INGREDIENTS_ERROR_MSG = "Server error with ingredient: {0} and list: {1}"
INGREDIENTS_MESSAGES = {
    "ADD": {
        "200": "Ingredient: {0} added successfully to list: {1}",
        "409": "Ingredient: {0} already exists in list: {1}",
    },
    "RENAME": {
        "200": "Ingredient: {0} renamed successfully to: {1}",
        "409": "Ingredient: {0} already exists in list: {1}",
    },
    "DELETE": {
        "200": "Ingredient: {0} deleted successfully from list: {1}",
    },
    "TRANSFER": {
        "200": "Ingredient: {0} transferred successfully to list: {1}",
        "409": "Ingredient: {0} already exists in list: {1}",
    },
}

LIST_ERROR_MSG = "Server error with list: {0}"
LIST_MESSAGES = {
    "ADD_LIST": {
        "200": "List: {0} added successfully",
        "409": "List: {0} already exists",
    },
    "RENAME_LIST": {
        "200": "List: {0} renamed successfully to: {1}",
        "409": "List: {0} already exists",
    },
    "CLEAR_LIST": {
        "200": "List: {0} cleared successfully",
    },
    "DELETE_LIST": {
        "200": "List: {0} deleted successfully",
    },
}

LOGIN_ERROR_MSG="Server error"
LOGIN_MESSAGES={
    "SIGNIN":{
        "200": "Connected",
        "401": "Wrong username or password"
    },
    "REG":{
        "409": "Username already taken",
         "201": "Saved to database",
    },
}

#server response dictionary
def create_response_dict(code, message, data=None):
    response = {"code": code, "message": message}
    if data:
        response['data']=data
    return response

#get server ingredients response message
def get_ingredient_message(cmd,code,ingredient_name,list_name):
    template = INGREDIENTS_MESSAGES.get(cmd, {}).get(code, INGREDIENTS_ERROR_MSG)
    return template.format(ingredient_name, list_name)

#get server lists response message
def get_list_message(cmd,code,list_name,prev_list_name=""):
    template = LIST_MESSAGES.get(cmd, {}).get(code, LIST_ERROR_MSG)
    if prev_list_name!="" and code =="200":
        return template.format(prev_list_name,list_name)
    return template.format(list_name)

#get server login message
def get_login_message(code,cmd):
    write_to_log(cmd)
    return LOGIN_MESSAGES.get(cmd,{}).get(code,LOGIN_ERROR_MSG)



#gets the message with header and extracts the msg
#returns error if the msg isn't with a valid header
def receive_bytes_msg(current_socket:socket):
    cmd_header=int.from_bytes(current_socket.recv(HEADER_LEN),byteorder="big")
    cmd=""
    #make sure we got the exact amount of data
    while len(cmd)<cmd_header:
        cmd+=current_socket.recv(cmd_header-len(cmd)).decode()
    msg_header=int.from_bytes(current_socket.recv(HEADER_LEN),byteorder="big")
    msg = b""
    while len(msg) < msg_header:
        msg += current_socket.recv(msg_header - len(msg))
    return cmd,msg

def receive_msg(current_socket:socket):
    cmd_header = int.from_bytes(current_socket.recv(HEADER_LEN), byteorder="big")
    cmd = ""
    # make sure we got the exact amount of data
    while len(cmd) < cmd_header:
        cmd += current_socket.recv(cmd_header - len(cmd)).decode()
    msg_header = int.from_bytes(current_socket.recv(HEADER_LEN), byteorder="big")
    msg = ""
    while len(msg) < msg_header:
        msg += current_socket.recv(msg_header - len(msg)).decode()
    return cmd, msg


#recives cmd and args(list) from client and turns them into
#header_cmd_header_args
def create_msg(cmd,args):
    cmd_bytes=encode_data(cmd)
    cmd_length=len(cmd).to_bytes(length=4,byteorder="big")
    args=encode_data(args)
    args_length=len(args).to_bytes(length=4,byteorder="big")
    request= cmd_length+cmd_bytes+args_length+args
    return request


def encode_data(data):
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        data = data.encode()
    else:
        data = json.dumps(data).encode()  # turn the json args into string
    return data

def check_cmd(cmd):
    if cmd in AI_CMD:
        return 1
    if cmd in DATABASE_CMD:
        return 2
    if cmd in INGREDIENTS_CMD:
        return 3
    if cmd in LIST_CMD:
        return 4

