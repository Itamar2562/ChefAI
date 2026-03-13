import logging
import socket
from datetime import datetime,timedelta
from customtkinter import *
import json
import fpdf

SERVER_IP="0.0.0.0"
CLIENT_IP="127.0.0.1"
PORT =8822
HEADER_LEN = 4
DATABASE_CMD=["SIGNIN","REG","SIGN_OUT"]
INGREDIENTS_CMD=["ADD","DELETE","DELETE_ALL","TRANSFER"]
LIST_CMD=["LIST","DELETE_LIST"]
AI_CMD=["MAKE","AI_USAGE"]
MAX_AI_USAGE_AMOUNT=100
DEFAULT_AI_RESPONSE='[{"type": "", "time": "", "name": "no available recipes", "description": "", "difficulty": "", "nutrition": "", "data": ""}]'


Codes={
    "200": "ok", #response
    "201": "created", #when creating smg
    "401": "Unauthorized", #when pw isn't right
    "409" : "conflict", #when trying to add smg that already exists
    "500" :"server error" #error
}

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

def write_to_log(msg):
    logging.info(msg)
    print(msg)

def seconds_until_midnight():
    now = datetime.now()
    tomorrow = now.date() + timedelta(days=1)
    midnight = datetime.combine(tomorrow, datetime.min.time())
    return (midnight - now).total_seconds()


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

