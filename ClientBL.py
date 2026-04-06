from Protocol import *
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

class ClientBL:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        self.parameters={'time':10.0,'type':"general", 'preference':[],'difficulty':""}
        self.client_socket=None
        self.fernet=None
        self.user_data={}
    def reset_parameters(self):
        self.parameters['time']=60.0
        self.parameters['type']="general"
        self.parameters['difficulty']=""
        self.parameters['preference'].clear()

    def add_food_type_parameter(self,parameter):
        self.parameters['type']=parameter

    def add_difficulty_parameter(self,parameter):
        self.parameters['difficulty']=parameter


    def add_preference_parameters(self,parameter):
        if parameter in self.parameters['preference']:
            self.parameters['preference'].remove(parameter)
        else:
            self.parameters['preference'].append(parameter)

    def get_parameters(self,curr_time):
        self.parameters['time']=curr_time
        return self.parameters

    #connect to server
    def connect(self):
        try:
            self.client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.client_socket.connect((self.ip,self.port))
            write_to_log(f"[Client_BL] client {self.client_socket.getsockname()} connected")
            self.fernet=None
            self.handle_first_handshake()
            return True
        except Exception as e:
            write_to_log("[Client_BL] attempting to connect...")
            return False

    #cryptography handshake
    def handle_first_handshake(self):
        pem_public_key=self.receive_msg(need_bytes=True)
        public_key = serialization.load_pem_public_key(pem_public_key,backend=default_backend())
        session_key=Fernet.generate_key()
        encrypted_session_key = public_key.encrypt(session_key,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                                            algorithm=hashes.SHA256(),label=None))
        self.send_data("SESSION_KEY",encrypted_session_key,False)
        write_to_log(f"session key : {session_key}")
        self.fernet = Fernet(session_key)

    def encrypt(self, data):
        return self.fernet.encrypt(data)

    def decrypt(self,data):
        return self.fernet.decrypt(data)

    #function sends an empty msg to check connection
    def check_connection(self):
        try:
            if self.client_socket is not None:
                #when socket closed recv returns ""
                check=self.client_socket.recv(1, socket.MSG_PEEK)
                if len(check) == 0:
                    return False
                else:
                    return True
            else:
                return False
        except BlockingIOError:
            return True # No data available, but connection is still alive
        except: #if got any other exceptions then connection is closed
            if self.client_socket:
                self.client_socket.close()
            self.client_socket=None
            return False

    def get_ai_usage_remaining_from_server(self):
        self.send_data('AI_USAGE',"")
        used=self.receive_msg(need_json=True)
        return used['data']

    def update_user_info(self, cmd, args):
        if cmd == "ADD":
            list_name=args['list_name']
            prev = args['prev_ingredient']
            curr = args['ingredient']
            self.update_user_info_add_ingredient(list_name,prev,curr)
        elif cmd == "ADD_LIST":
            prev_name = args['prev_list']
            curr_name = args['list_name']
            self.update_user_info_add_list(prev_name,curr_name)
        elif cmd == "DELETE":
            list_name=args['list_name']
            curr = args['ingredient']
            self.update_user_info_delete_ingredient(list_name,curr)
        elif cmd=="CLEAR_LIST":
            list_name=args['list_name']
            self.update_user_info_clear_ingredient_list(list_name)
        elif cmd == "DELETE_LIST":
            list_name=args['list_name']
            self.update_user_info_delete_list(list_name)
        elif cmd=="TRANSFER":
            src_list=args['src_list']
            dst_list=args['dst_list']
            ingredient=args['ingredient']
            self.transfer_ingredient(src_list,dst_list,ingredient)

    def update_user_info_add_ingredient(self,list_name,prev,curr):
        lists=self.user_data['lists']
        if prev in self.user_data['lists'][list_name]:
            lists[list_name].remove(prev)
            lists[list_name].append(curr)
        else:
            lists[list_name].append(curr)

    def update_user_info_add_list(self,prev_name,curr_name):
        lists=self.user_data['lists']
        if prev_name in lists.keys():
            lists[curr_name] = lists[prev_name]
            del lists[prev_name]
        else:
            lists[curr_name] = []


    def update_user_info_delete_ingredient(self,list_name,curr_name):
        lists=self.user_data['lists']
        if curr_name in lists[list_name]:
            lists[list_name].remove(curr_name)

    def update_user_info_clear_ingredient_list(self,list_name):
        self.user_data['lists'][list_name] = []

    def update_user_info_delete_list(self,list_name):
        lists=self.user_data['lists']
        if lists:
            del lists[list_name]

    def transfer_ingredient(self,src_list,dst_list,ingredient):
        lists=self.user_data['lists']
        if ingredient in lists[src_list]:
            lists[src_list].remove(ingredient)
            lists[dst_list].append(ingredient)


    def receive_msg(self,need_bytes=False,need_json=False):
        if need_bytes:
            cmd, msg=receive_bytes_msg(self.client_socket)
        else:
            cmd, msg=receive_msg(self.client_socket)
            if self.fernet:
                msg=self.decrypt(msg).decode()
        if need_json:
            return json.loads(msg)
        return msg


    def send_data(self,cmd,args,verbose=True):
        write_to_log(f"data: {cmd},{args}")
        try:
            args=encode_data(args)
            cmd=encode_data(cmd)
            if self.fernet:
                args = self.encrypt(args)
                cmd=self.encrypt(cmd)
            msg= create_msg(cmd, args)
            self.client_socket.send(msg)
            if verbose:
                write_to_log(f"[Client_BL] send {msg}")
        except Exception as e:
            write_to_log(f"[Client_BL] Error {e} while sending massage")








