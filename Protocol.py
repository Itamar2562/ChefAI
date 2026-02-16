import logging
import socket
from datetime import datetime
import time
import threading
from customtkinter import *
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import json
from PIL import Image
import re
import fpdf
import os

SERVER_IP="0.0.0.0"
CLIENT_IP="127.0.0.1"
PORT =8822
BUFFER_SIZE = 1024
HEADER_LEN = 4
FORMAT= 'utf-8'
DATABASE_CMD=["SIGNIN","REG","SIGN_OUT"]
INGREDIENTS_CMD=["ADD","DELETE","DELETE_ALL","TRANSFER"]
LIST_CMD=["LIST","DELETE_LIST"]

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

def process_for_json_loads(text: str):
    # Remove code fences if present
    text = text.strip()

    # Try direct parse first (fast path)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Regex to extract first JSON array or object
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON found in AI response")

    return json.loads(match.group(1))

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
        os.makedirs("Saved Recipes", exist_ok=True)
        if os.path.isfile(fr"Saved Recipes\{data['name']}.pdf"):
            return "409" #already exists
        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.multi_cell(0, 10, data['name'], border=0,align="C")

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, data['data'], align='J')

        pdf.set_font("Helvetica", style="B", size=16)
        pdf.multi_cell(0, 10, 'Nutrition', border=0,align="C")

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, data['nutrition'], align='J')

        pdf.output(fr"Saved Recipes\{data['name']}.pdf")
        return "200"
    except Exception as e:
        write_to_log(f"Exception {e} while saving to pdf")
        return "500"

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
    if cmd=="MAKE":
        return 1
    if cmd in DATABASE_CMD:
        return 2
    if cmd in INGREDIENTS_CMD:
        return 3
    if cmd in LIST_CMD:
        return 4

