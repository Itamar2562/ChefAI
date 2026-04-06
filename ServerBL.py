import random
from Protocol import *
from Database import *
from Server_AI import *
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.fernet import Fernet
import threading
import concurrent.futures
from datetime import date
class ServerBL:
    def __init__(self, ip: str, port: int,callback_add_client,callback_remove_client,callback_configure_client_id):
        self._ip = ip
        self._port = port
        self._server_socket = None
        self._srv_is_running=True
        self._clients_list=[]
        self._connected_ids=[]
        self._stop_event=threading.Event()

        self._callback_add_client=callback_add_client
        self._callback_remove_client=callback_remove_client
        self._callback_configure_client_id=callback_configure_client_id

    def start_server(self):
        self._server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((self._ip,self._port))
        self._server_socket.setblocking(True)
        self._stop_event.clear()
        self._server_socket.listen()
        write_to_log("[Server_BL] server is listening")
        self._srv_is_running=True
        self._clients_list=[]
        self._connected_ids=[]
        while self._srv_is_running and self._server_socket is not None:
            try:
                client_socket,address=self._server_socket.accept()
                write_to_log(f"[Server_BL] Client connected: {address}")
                client_thread=ClientHandler(client_socket,address,self._stop_event,self.update_client_handler,self.add_id,
                                     self.remove_client,self.remove_id)
                client_thread.start()
                self._clients_list.append(client_thread)
                self._callback_add_client(address[0], address[1], -1)
                write_to_log(f"[Server_BL] active connections: {threading.active_count() - 2}")
            except OSError as e:
                if e.errno!=10038 or e.errno!=10054: #operation on something that isn't a socket or connected
                    # destroyed can be ignored
                    write_to_log(e)
                break
    def remove_client(self,address,user_id):
        self.remove_id(address,user_id)
        self._callback_remove_client(address[0], address[1])

    def remove_id(self,address,user_id):
        if user_id!=-1:
            self._connected_ids.remove(user_id)
            self._callback_configure_client_id(address[0], address[1], -1)

    def stop_server(self):
        self._stop_event.set()
        for client_thread in self._clients_list:
            client_thread.join()
        self._clients_list.clear()
        self._srv_is_running=False
        if self._server_socket is not None:
            self._server_socket.close()
            self._server_socket=None
        write_to_log(f"[Server_BL] Server has stopped")

    def update_client_handler(self,thread):
        if thread in self._clients_list:
            self._clients_list.remove(thread)

    def add_id(self,address,user_id):
        if user_id in self._connected_ids:
            return False
        self._connected_ids.append(user_id)
        self._callback_configure_client_id(address[0], address[1], user_id)
        return True

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, address,stop_event,update_client_handler,callback_add_id,
                 callback_remove_client,callback_remove_id):
        super().__init__()
        self._client_socket=client_socket
        self._client_address=address
        self._connected=True
        self._stop_event=stop_event

        self._callback_update_client_handler=update_client_handler
        self._callback_add_id=callback_add_id
        self._callback_remove_client=callback_remove_client
        self._callback_remove_id=callback_remove_id

        self._current_id=-1
        self._future=None
        self._fernet=None
        self._db_conn=None

        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    #an override of the standard run function inside thread that is called when a thread
    #is created
    def run(self):
        self.handle_first_handshake()
        self._db_conn=get_conn()
        self._client_socket.setblocking(0) #set to non-blocking
        #self._client_socket.settimeout(10) #set timeout to 0.5 seconds maybe not needed
        while not self._stop_event.is_set():
            try:
               cmd,data=self.receive_msg()
               write_to_log(f"cmd:{cmd}!")
               write_to_log(f"msg:{data}!")
               cmd_type=check_cmd(cmd)
               if cmd_type==1:
                   self.handle_ai(cmd,data)
               elif cmd_type==2:
                   self.handle_db_login_msg(cmd,data)
               elif cmd_type==3:
                   self.handle_ingredients(cmd,data)
               elif cmd_type==4:
                   self.handle_list(cmd,data)
            except Exception as e:
                if str(e)!="[WinError 10035] A non-blocking socket operation could not be completed immediately":
                    write_to_log(e)
                if not self.check_conn():
                    self._callback_update_client_handler(self) #send the thread to be removed
                    write_to_log(f"[Server_BL] Client: {self._client_address} disconnected")
                    self._callback_remove_client(self._client_address, self._current_id)
                    break
        if self._future:
            self._future.cancel()
        close_conn(self._db_conn)
        self._client_socket.shutdown(socket.SHUT_RDWR)
        self._client_socket.close()
        self._client_socket = None

    def handle_ai_usage(self):
        today=date.today()
        ai_usage_count=get_ai_usage_count(self._db_conn,self._current_id,today)
        response=create_response_dict("200","AI usage count",ai_usage_count)
        self.send_data("AI_COUNT", response)

    def handle_db_login_msg(self,cmd,data):
        if cmd == "SIGN_OUT":
            self.user_sign_out()
            return
        data=json.loads(data)
        username=data['name']
        password=data['password']
        write_to_log(username)
        write_to_log(password)
        password=hash_password(password)
        if cmd=="REG":
            code= create_response_msg_db(self._db_conn,cmd, username,password,data['default'])
        else:
            code=create_response_msg_db(self._db_conn,cmd, username,password)
        login_message=get_login_message(code,cmd)
        if code != "200":
            response = create_response_dict(code, login_message)
        else:
            data=self.get_user_info(username,password)
            succeed=self._callback_add_id(self._client_address, self._current_id)
            if succeed:
                response=create_response_dict(code,login_message,data)
            else:
                self._current_id=-1
                response=create_response_dict("409",ALREADY_LOGGED_IN_MASSAGE)
        self.send_data("LOGIN",response)

    def user_sign_out(self):
        self._callback_remove_id(self._client_address, self._current_id)
        self._current_id=-1

    def handle_ingredients(self,cmd,data):
        if cmd == "ADD":
            response = self.add_ingredient_to_db(data)
            self.send_data("ADD",response)
        elif cmd == "DELETE":
            response = self.remove_ingredient_from_db(data)
            self.send_data("DELETE",response)
        elif cmd=="TRANSFER":
            response=self.transfer_ingredients_from_db(data)
            self.send_data("TRANSFER",response)


    #data will look like this [10.0, 3, "fried", "oven", "soup", 3, "halal", "vegan", "kosher"] False this is goofy version
    #to separate the data I will get length and skip time with it
    #then I will run the loop for the amount+skipped parts e.g. 2+3=5 -> 2:5 will get 3 ingredients
    def handle_ai(self,cmd,data):
       if cmd=="MAKE":
           self.handle_make(data)
       elif cmd=="AI_USAGE":
           self.handle_ai_usage()

    def handle_make(self,parameters):
        parameters = json.loads(parameters)
        write_to_log(parameters['time'])
        write_to_log(parameters['type'])
        write_to_log(parameters['preference'])
        data = get_lists_with_ingredients(self._db_conn,self._current_id)
        ingredients = self.extract_all_ingredients(data)
        ingredients = json.dumps(ingredients)
        can_use_api, ai_usage = self.handle_amount_of_requests()
        self.clear_ai_usage_dates(self._db_conn,)

        if can_use_api:
            response,ai_request_code = self.request_ai_response(parameters, ingredients)
            response = process_for_json_loads(response)
        else:
            response = DEFAULT_AI_RESPONSE

        response,code=self.check_ai_response(response)
        final_response = self.add_usage_count(response, ai_usage)
        new_response=create_response_dict(code,"AI response",final_response)
        self.send_data("AI", new_response)

    def request_ai_response(self,parameters,ingredients):
        self._future=self._executor.submit(send_and_receive_ai_request,parameters['time'],parameters['type'],
                                           parameters['difficulty'],
                                               parameters['preference'], ingredients)
        while not self._stop_event.is_set():
            try:
                response = self._future.result(timeout=0.5)
                return response,"200"
            except concurrent.futures.TimeoutError:
                continue
            except Exception as e:
                write_to_log(f"[Server_BL] AI request failed: {e}")
                return DEFAULT_AI_RESPONSE,"500"

    def handle_amount_of_requests(self):
        today=date.today()
        can_use_api,ai_usage=handle_usage(self._db_conn,self._current_id,today)
        return can_use_api,ai_usage

    def check_ai_response(self,response):
        try:
            response = json.loads(response)
            if response[0]['name'] == "no available recipes":
                return DEFAULT_AI_RESPONSE,"500"
            else:
                return response,"200"

        except json.decoder.JSONDecodeError:
            return DEFAULT_AI_RESPONSE,"500"


    def add_usage_count(self,response:str,amount):
        new_response={"recipes":response,"remaining":MAX_AI_USAGE_AMOUNT-amount}
        return new_response



    def clear_ai_usage_dates(self,conn):
        rnd=random.random()
        if rnd<0.1: #10%
            clear_ai_usage_from_db(conn)


    def extract_all_ingredients(self,data):
        ingredients=[]
        for key in data.keys():
            for ing in data[key]:
                ingredients.append(ing)
        return ingredients

    def handle_list(self,cmd,data):
        if cmd == "ADD_LIST":
            response = self.add_list_to_db(data)
            self.send_data("ADD_LIST", response)
        elif cmd=="DELETE_LIST":
            response=self.remove_list_from_db(data)
            self.send_data("DELETE_LIST",response)
        elif cmd == "CLEAR_LIST":
            response = self.clear_list_in_db(data)
            self.send_data( "CLEAR_LIST", response)


    def handle_first_handshake(self):
        private_key=rsa.generate_private_key(public_exponent=65537, key_size=1024)
        public_key=private_key.public_key()
        pem_public_key = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
        self.send_data("PUBLIC_KEY",pem_public_key,False)
        cmd,data=self.receive_msg(True)
        session_key=private_key.decrypt(data,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
        write_to_log(f"session key: {session_key}")
        self._fernet=Fernet(session_key)

    def encrypt(self,data):
        return self._fernet.encrypt(data)


    def decrypt(self,data):
        return self._fernet.decrypt(data)


    def check_conn(self):
        try:
            check = self._client_socket.recv(1, socket.MSG_PEEK)
            if len(check) == 0:
                return False
            return True
        except BlockingIOError:
            # No data available, but connection is still alive
            return True
        except:
            return False



    def add_ingredient_to_db(self,data):
        data=json.loads(data)
        list_name = data['list_name']
        ingredient_name = data['ingredient']
        prev_name=data['prev_ingredient']
        code= handle_ingredient_update(self._db_conn,self._current_id, list_name,prev_name, ingredient_name)
        if prev_name=="":
            message=get_ingredient_message("ADD",code,ingredient_name,list_name)
        else:
            message=get_ingredient_message("RENAME",code,ingredient_name,prev_name)
        response=create_response_dict(code,message,data)
        return response

    def add_list_to_db(self,data):
        data=json.loads(data)
        list_name = data['list_name']
        prev_list_name = data['prev_list']
        code= handle_list_update(self._db_conn, self._current_id, list_name, prev_list_name)
        if prev_list_name=="":
            message=get_list_message("ADD_LIST",code,list_name)
        else:
            message=get_list_message("RENAME_LIST",code,list_name,prev_list_name)
        response=create_response_dict(code,message,data)
        return response

    def remove_ingredient_from_db(self,data):
        data=json.loads(data)
        list_name=data['list_name']
        ingredient_name=data['ingredient']
        code=delete_ingredient(self._db_conn,self._current_id,list_name,ingredient_name)
        message=get_ingredient_message("DELETE",code,ingredient_name,list_name)
        response=create_response_dict(code,message,data)
        return response

    #transfers ingredients between lists data is [src_list,dst_list,ingredient_name]
    def transfer_ingredients_from_db(self,data):
        data=json.loads(data)
        src_list = data['src_list']
        dst_list = data['dst_list']
        ingredient = data['ingredient']
        code=transfer_ingredient(self._db_conn,self._current_id,src_list,dst_list,ingredient)
        message=get_ingredient_message("TRANSFER",code,ingredient,dst_list)
        response=create_response_dict(code,message,data)
        return response

    def clear_list_in_db(self, data):
        data=json.loads(data)
        list_name=data['list_name']
        code=remove_all_ingredients(self._db_conn,self._current_id,list_name)
        message=get_list_message("CLEAR_LIST",code,list_name)
        response=create_response_dict(code,message,data)
        return response

    def remove_list_from_db(self,data):
        data=json.loads(data)
        list_name=data['list_name']
        code=delete_list(self._db_conn,self._current_id,list_name)
        message=get_list_message("DELETE_LIST",code,list_name)
        response=create_response_dict(code,message,data)
        return response

    def get_user_info(self,username,password):
        self._current_id = get_id(self._db_conn,username,password)
        lists=get_lists_with_ingredients(self._db_conn,self._current_id)
        today=date.today()
        ai_usage_count=get_ai_usage_count(self._db_conn,self._current_id,today)
        user_info={'lists':lists,"remaining":MAX_AI_USAGE_AMOUNT-ai_usage_count}
        return user_info

    def send_data(self,cmd,args,verbose=True):
        try:
            args=encode_data(args)
            cmd=encode_data(cmd)
            write_to_log(f"send args: {args}")
            write_to_log(f"send cmd: {cmd}")
            if self._fernet:
                args = self.encrypt(args)
                cmd=self.encrypt(cmd)
            msg=create_msg(cmd,args)
            self._client_socket.send(msg)
            if verbose:
                write_to_log(f"[Server_BL] send {msg}")
        except Exception as e:
            write_to_log(f"[Server_BL] Error {e} while sending massage")


    def receive_msg(self,need_bytes=False):
        if need_bytes:
            cmd, msg=receive_bytes_msg(self._client_socket)
        else:
            cmd, msg=receive_msg(self._client_socket)
        if self._fernet:
            msg = self.decrypt(msg).decode()
            cmd=self.decrypt(cmd).decode()
        return cmd, msg













