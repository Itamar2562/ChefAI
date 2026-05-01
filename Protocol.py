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


# prepare Log file
LOG_FILE = 'LOG.log'
logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

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
    data= {"list_name":list_name,'ingredient':ingredient}
    if prev_ingredient!="":
        data['prev_ingredient']=prev_ingredient
    return data

def pack_list_data(list_name,list_prev_name=""):
    data= {'list_name':list_name}
    if list_prev_name!="":
        data['prev_list']=list_prev_name
    return data

def pack_transfer_data(src_list,dst_list,ingredient):
    return {'src_list':src_list,'dst_list':dst_list,'ingredient':ingredient}


def process_for_json_loads(text: str):
    json_str = ""
    try:
        # Strip leading/trailing whitespace
        text = text.strip()

        # Find first [ and last ]
        start = text.find('[')
        end = text.rfind(']')

        if start == -1 or end == -1 or start > end:
            return json.loads(DEFAULT_AI_RESPONSE)

        json_str = text[start:end + 1]
        return json.loads(json_str)

    except json.JSONDecodeError as e:
        write_to_log(f"JSON parsing failed: {str(e)}, extracted: {json_str}")
        return json.loads(DEFAULT_AI_RESPONSE)

def process_response(text: str):
        try:
            data = json.loads(text)
            data=data["recipes"]

            #basic structure check
            if not isinstance(data, list):
                raise ValueError("Not a list")

            #validate each recipe
            required_keys = {"type", "time", "name", "description", "difficulty", "nutrition", "data"}
            valid = []
            for r in data:
                if not isinstance(r, dict):
                    continue

                if set(r.keys()) != required_keys:
                    continue

                valid.append(r)

            if not valid:
                raise ValueError("No valid recipes")

            return {"recipes":valid}

        except Exception as e:
            write_to_log(f"Processing failed: {str(e)}")
            return json.loads(DEFAULT_AI_RESPONSE)


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

def check_cmd(cmd):
    if cmd in AI_CMD:
        return 1
    if cmd in DATABASE_CMD:
        return 2
    if cmd in INGREDIENTS_CMD:
        return 3
    if cmd in LIST_CMD:
        return 4

