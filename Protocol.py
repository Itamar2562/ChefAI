import logging
import socket
from datetime import datetime,timedelta
from customtkinter import *
import json
import fpdf
import hashlib

SERVER_IP="0.0.0.0"
CLIENT_IP="127.0.0.1"
PORT =8822

HEADER_LEN = 4
DATABASE_CMD=["SIGNIN","REG","SIGN_OUT"]
INGREDIENTS_CMD=["ADD","DELETE","TRANSFER"]
LIST_CMD=["ADD_LIST","DELETE_LIST","CLEAR_LIST"]
AI_CMD=["MAKE","AI_USAGE"]
MAX_AI_USAGE_AMOUNT=5
DEFAULT_AI_RESPONSE='[{"type": "", "time": "", "name": "no available recipes", "description": "", "difficulty": "", "nutrition": "", "data": ""}]'
ALREADY_LOGGED_IN_MASSAGE="Your account is already logged in on another device.\n Please log out from the other session before logging in here."

IMG_WIDTH = 1004
IMG_HEIGHT = 526


Codes={
    "200": "successfully", #response
    "201": "saved to database", #when creating smg
    "401": "Wrong username or password", #when pw isn't right
    "409" : "already exists", #when trying to add smg that already exists
    "500" :"server error" #error
}

INGREDIENTS_ERROR_MSG = "Server error with ingredient: {0} and list: {1}"
INGREDIENTS_MESSAGES = {
    "ADD": {
        "200": "Ingredient: {0} added successfully to list: {1}",
        "409": "Ingredient: {0} already exists in list: {1}",
    },
    "RENAME": {
        "200": "Ingredient: {0} renamed successfully to: {1}",
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


def create_response_dict(code, message, data=None):
    response = {"code": code, "message": message}
    if data:
        response['data']=data
    return response

def get_ingredient_message(cmd,code,ingredient_name,list_name):
    template = INGREDIENTS_MESSAGES.get(cmd, {}).get(code, INGREDIENTS_ERROR_MSG)
    return template.format(ingredient_name, list_name)

def get_list_message(cmd,code,list_name,prev_list_name=""):
    template = LIST_MESSAGES.get(cmd, {}).get(code, LIST_ERROR_MSG)
    if cmd=="RENAME_LIST":
        return template.format(prev_list_name,list_name)
    return template.format(list_name)


def get_login_message(code,cmd):
    write_to_log(cmd)
    return LOGIN_MESSAGES.get(cmd,{}).get(code,LOGIN_ERROR_MSG)


# prepare Log file
LOG_FILE = 'LOG.log'
logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

def get_time_greeting():
    hour=datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    if 12 <= hour < 17:
        return "Good Afternoon"
    if 17 <= hour < 22:
        return "Good evening"
    else:
        return "Good Night"


def hash_password(password):
    return str(hashlib.sha256(password.encode('utf-8')).hexdigest())

def write_to_log(msg):
    logging.info(msg)
    print(msg)

def seconds_until_midnight():
    now = datetime.now()
    tomorrow = now.date() + timedelta(days=1)
    midnight = datetime.combine(tomorrow, datetime.min.time())
    return (midnight - now).total_seconds()


def pack_ingredient_data(list_name,ingredient,prev_ingredient=""):
    return {"list_name":list_name,'ingredient':ingredient,'prev_ingredient':prev_ingredient}

def pack_list_data(list_name,list_prev_name=""):
    return {'list_name':list_name,'prev_list':list_prev_name}
def pack_transfer_data(src_list,dst_list,ingredient):
    return {'src_list':src_list,'dst_list':dst_list,'ingredient':ingredient}


def process_for_json_loads(text: str):
    text = text.replace("```json", "").replace("```", "")
    start = None
    depth = 0
    for i, c in enumerate(text):
        if c == "[":
            if start is None:
                start = i
            depth += 1

        elif c == "]":
            if depth > 0:
                depth -= 1
                if depth == 0:
                    json_str = text[start:i + 1]
                    return json_str

    return DEFAULT_AI_RESPONSE

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

def save_to_pdf(data):
    try:
        directory=open_directory_dialog(data['name'])
        if directory=="no directory":
            return False
        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", style="BU", size=16)
        pdf.set_text_color(44, 62, 80)
        pdf.multi_cell(0, 10, data['name'], border=0,align="C")

        pdf.set_font("Arial",size=14)
        pdf.set_text_color(74, 74, 74)
        pdf.multi_cell(0, 10, data['description'], align='J')

        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, data['data'], align='J')

        pdf.set_font("Helvetica", style="BU", size=16)
        pdf.set_text_color(44, 62, 80)
        pdf.multi_cell(0, 10, 'Nutrition', border=0,align="C")

        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, data['nutrition'], align='J')
        pdf.output(directory)
        return True
    except Exception as e:
        write_to_log(f"Exception {e} while saving to pdf")
        return False

def open_directory_dialog(name):
    """Opens a directory dialog to select a folder."""
    directory_path = filedialog.asksaveasfile(
        title="Select a directory",
        initialdir="/",
        initialfile=name,
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if directory_path:
        return directory_path.name
    else:
        return "no directory"


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

#currently doesn't do anything (from natalie's code) I don't think I need it (i needed it lmao)
def check_cmd(cmd):
    if cmd in AI_CMD:
        return 1
    if cmd in DATABASE_CMD:
        return 2
    if cmd in INGREDIENTS_CMD:
        return 3
    if cmd in LIST_CMD:
        return 4

