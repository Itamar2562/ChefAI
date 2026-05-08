import logging
import socket
import json

CLIENT_IP="127.0.0.1"
PORT =8822
HEADER_LEN = 4

# Packs ingredient update data into a dictionary for sending between client and server.
def pack_ingredient_data(list_name,ingredient,prev_ingredient=""):
    data= {"list_name":list_name,'ingredient':ingredient}
    if prev_ingredient!="":
        data['prev_ingredient']=prev_ingredient
    return data

# Packs list-related data (name and optional previous name) into a dictionary format.
def pack_list_data(list_name,list_prev_name=""):
    data= {'list_name':list_name}
    if list_prev_name!="":
        data['prev_list']=list_prev_name
    return data

# Packs data required to transfer an ingredient from one list to another.
def pack_transfer_data(src_list,dst_list,ingredient):
    return {'src_list':src_list,'dst_list':dst_list,'ingredient':ingredient}

# Receives a message from a socket using a fixed-length header
# and returns raw bytes command and message.
def receive_bytes_msg(current_socket:socket):
    cmd_header=int.from_bytes(current_socket.recv(HEADER_LEN),byteorder="big")
    cmd=""
    #make sure we got the exact amount of data using a loop
    while len(cmd)<cmd_header:
        cmd+=current_socket.recv(cmd_header-len(cmd)).decode()
    msg_header=int.from_bytes(current_socket.recv(HEADER_LEN),byteorder="big")
    msg = b""
    while len(msg) < msg_header:
        msg += current_socket.recv(msg_header - len(msg))
    return cmd,msg

# Receives a message from a socket using headers
# and returns decoded string command and message.
def receive_msg(current_socket:socket):
    cmd_header = int.from_bytes(current_socket.recv(HEADER_LEN), byteorder="big")
    cmd = ""
    #make sure we got the exact amount of data using a loop
    while len(cmd) < cmd_header:
        cmd += current_socket.recv(cmd_header - len(cmd)).decode()
    msg_header = int.from_bytes(current_socket.recv(HEADER_LEN), byteorder="big")
    msg = ""
    while len(msg) < msg_header:
        msg += current_socket.recv(msg_header - len(msg)).decode()
    return cmd, msg


# Packs command and payload into a length-prefixed binary message format
# length-cmd-length-args
def create_msg(cmd,args):
    cmd_bytes=encode_data(cmd)
    cmd_length=len(cmd).to_bytes(length=4,byteorder="big")
    args=encode_data(args)
    args_length=len(args).to_bytes(length=4,byteorder="big")
    request= cmd_length+cmd_bytes+args_length+args
    return request

# Encodes data into bytes (string, bytes, or JSON-serializable objects)
def encode_data(data):
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        data = data.encode()
    else:
        # turn the json args into string end then encode
        data = json.dumps(data).encode()
    return data
