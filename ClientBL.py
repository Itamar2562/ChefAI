from Protocol import *
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

class ClientBL:
    def __init__(self,ip,port):
        self._ip = ip
        self._port = port
        self._parameters={'time':10.0, 'type': "general", 'preference':[], 'difficulty': ""}
        self._client_socket=None
        self._fernet=None
        self._user_data={}

    #connect to server
    def connect(self):
        try:
            self._client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._client_socket.connect((self._ip, self._port))
            write_to_log(f"[Client_BL] client {self._client_socket.getsockname()} connected")
            self._fernet=None
            self.handle_first_handshake()
            return True
        except:
            write_to_log("[Client_BL] attempting to connect...")
            return False

    #function sends an empty msg to check connection
    def check_connection(self):
        try:
            if self._client_socket is not None:
                #when socket closed recv returns ""
                check=self._client_socket.recv(1, socket.MSG_PEEK)
                if len(check) == 0:
                    return False
                else:
                    return True
            else:
                return False
        except BlockingIOError:
            return True # No data available, but connection is still alive
        except: #if got any other exceptions then connection is closed
            if self._client_socket:
                self._client_socket.close()
            self._client_socket=None
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
        self._fernet = Fernet(session_key)

    def reset_parameters(self):
        self._parameters['time']=60.0
        self._parameters['type']= "general"
        self._parameters['difficulty']= ""
        self._parameters['preference'].clear()


    def add_food_type_parameter(self,parameter):
        self._parameters['type']=parameter

    def add_difficulty_parameter(self,parameter):
        self._parameters['difficulty']=parameter

    def add_preference_parameters(self,parameter):
        if parameter in self._parameters['preference']:
            self._parameters['preference'].remove(parameter)
        else:
            self._parameters['preference'].append(parameter)

    def get_parameters(self,curr_time):
        self._parameters['time']=curr_time
        return self._parameters


    def get_ai_usage_remaining_data_from_server(self):
        self.send_data('AI_USAGE',"")
        msg=self.receive_msg(need_json=True)
        return msg

    def get_user_data_lists(self):
        return self._user_data['lists']

    def get_user_data_ai_remaining_usage(self):
        return self._user_data['remaining']

    def set_user_data_ai_remaining_usage(self,remaining):
        self._user_data['remaining']=remaining

    def set_user_data(self,user_data):
        self._user_data=user_data

    def delete_all_user_data(self):
        self._user_data = {}
        self.reset_parameters()

    def update_user_info(self, cmd, args):
        actions = {
            "ADD": lambda: self.update_user_info_add_ingredient(
                args['list_name'],args['ingredient']
            ),
            "RENAME":lambda: self.update_user_info_rename_ingredient(
                args['list_name'], args['prev_ingredient'], args['ingredient']
            ),
            "DELETE": lambda: self.update_user_info_delete_ingredient(
                args['list_name'], args['ingredient']
            ),
            "ADD_LIST": lambda: self.update_user_info_add_list(
                args['list_name']
            ),
            "RENAME_LIST": lambda: self.update_user_info_rename_list(
                args['prev_list'], args['list_name']
            ),
            "CLEAR_LIST": lambda: self.update_user_info_clear_ingredient_list(
                args['list_name']
            ),
            "DELETE_LIST": lambda: self.update_user_info_delete_list(
                args['list_name']
            ),
            "TRANSFER": lambda: self.transfer_ingredient(
                args['src_list'], args['dst_list'], args['ingredient']
            ),
        }
        if cmd in actions:
            action = actions.get(cmd)
            action()

    def update_user_info_add_ingredient(self,list_name,curr):
        lists = self._user_data['lists']
        lists[list_name].append(curr)

    def update_user_info_rename_ingredient(self,list_name,prev,curr):
        lists=self._user_data['lists']
        if prev in self._user_data['lists'][list_name]:
            lists[list_name].remove(prev)
            lists[list_name].append(curr)

    def update_user_info_add_list(self,curr_name):
        lists=self._user_data['lists']
        lists[curr_name] = []

    def update_user_info_rename_list(self,prev_name,curr_name):
        lists=self._user_data['lists']
        if prev_name in lists.keys():
            lists[curr_name] = lists[prev_name]
            del lists[prev_name]


    def update_user_info_delete_ingredient(self,list_name,curr_name):
        lists=self._user_data['lists']
        if curr_name in lists[list_name]:
            lists[list_name].remove(curr_name)

    def update_user_info_clear_ingredient_list(self,list_name):
        self._user_data['lists'][list_name] = []

    def update_user_info_delete_list(self,list_name):
        lists=self._user_data['lists']
        if lists:
            del lists[list_name]

    def transfer_ingredient(self,src_list,dst_list,ingredient):
        lists=self._user_data['lists']
        if ingredient in lists[src_list]:
            lists[src_list].remove(ingredient)
            lists[dst_list].append(ingredient)


    def receive_msg(self,need_bytes=False,need_json=False):
        if need_bytes:
            cmd, msg=receive_bytes_msg(self._client_socket)
        else:
            cmd, msg=receive_msg(self._client_socket)
            if self._fernet:
                msg=self.decrypt(msg).decode()
        if need_json:
            msg=json.loads(msg)
        return msg

    def encrypt(self, data):
        return self._fernet.encrypt(data)

    def decrypt(self, data):
        return self._fernet.decrypt(data)


    def send_data(self,cmd,args,verbose=True):
        write_to_log(f"data: {cmd},{args}")
        try:
            args=encode_data(args)
            cmd=encode_data(cmd)
            if self._fernet:
                args = self.encrypt(args)
                cmd=self.encrypt(cmd)
            msg= create_msg(cmd, args)
            self._client_socket.send(msg)
            if verbose:
                write_to_log(f"[Client_BL] send {msg}")
        except Exception as e:
            write_to_log(f"[Client_BL] Error {e} while sending massage")








