from Protocol import *
from Database import *
from Server_AI import *
class ServerBL:
    def __init__(self, ip: str, port: int):
        self._ip = ip
        self._port = port
        self._server_socket = None
        self._srv_is_running=True
        self._client_handler=[]
        self._stop_event=threading.Event()

    def start_server(self):
        self._server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((self._ip,self._port))
        self._server_socket.setblocking(True)
        self._stop_event.clear()
        self._server_socket.listen()
        write_to_log("[Server_BL] server is listening")
        self._srv_is_running=True
        while self._srv_is_running and self._server_socket is not None:
            try:
                client_socket,address=self._server_socket.accept()
                write_to_log(f"[Server_BL] Client connected: {address}")
                client=ClientHandler(client_socket,address,self._stop_event,self.update_client_handler)
                client.start()
                self._client_handler.append(client)
                write_to_log(f"[SERVER_BL] ACTIVE CONNECTION {threading.active_count() - 2}")
            except Exception as e:
                write_to_log(e)
                break

    def stop_server(self):
        self._stop_event.set()
        if len(self._client_handler)>0:
                for client_thread in self._client_handler:
                    #doesn't work cus I need to close the client_socket somehow I don't know how honestly im cooked
                    client_thread.join()
        close_conn()
        self._client_handler.clear()
        self._srv_is_running=False
        if self._server_socket is not None:
            self._server_socket.close()
            self._server_socket=None
        write_to_log(f"[Server_BL] Server has stopped")

    def update_client_handler(self,thread):
        if thread in self._client_handler:
            self._client_handler.remove(thread)

class ClientHandler(threading.Thread):
    _client_socket=None
    _client_address=None
    _connected=False
    _stop_event=None
    def __init__(self, client_socket, address,stop_event,update_client_handler):
        super().__init__()
        self._client_socket=client_socket
        self._client_address=address
        self._connected=True
        self._stop_event=stop_event
        self.callback_update_client_handler=update_client_handler
        self._current_id=-1
        self._fernet=None



    #an override of the standard run function inside thread that is called when a thread
    #is created
    def run(self):
        self.handle_first_handshake()
        self._client_socket.setblocking(0) #set to non-blocking
        #self._client_socket.settimeout(10) #set timeout to 0.5 seconds maybe not needed
        while not self._stop_event.is_set():
            try:
               cmd,data=self.receive_msg()
               write_to_log(f"cmd:{cmd}!")
               write_to_log(f"msg:{data}!")
               cmd_type=check_cmd(cmd)
               if cmd_type==1:
                   self.handle_make(data)
               elif cmd_type==2:
                   self.handle_db_login_msg(cmd,data)
               elif cmd_type==3:
                   write_to_log("got here2")
                   self.handle_ingredients(cmd,data)
               elif cmd_type==4:
                   self.handle_list(cmd,data)
            except Exception as e:
                if str(e)!="[WinError 10035] A non-blocking socket operation could not be completed immediately":
                    write_to_log(e)
                if not self.check_conn():
                    self.callback_update_client_handler(self) #send the thread to be removed
                    write_to_log(f"[Server_BL] Client: {self._client_address} disconnected")
                    break
        self._client_socket.shutdown(socket.SHUT_RDWR)
        self._client_socket.close()
        self._client_socket = None

    def handle_db_login_msg(self,cmd,data):
        if cmd == "SIGN_OUT":
            self._current_id = -1
            return
        data=json.loads(data)
        username=data['name']
        password=data['password']
        write_to_log(username)
        write_to_log(password)
        if cmd=="REG":
            msg = create_response_msg_db(cmd, username,password,data['default'])
        else:
            msg=create_response_msg_db(cmd, username,password)
        write_to_log(f"msg is {msg}")
        self.send_data("LOGIN",msg)
        if msg == "connected":
            self.initiate_sign_in(username,password)

    def handle_ingredients(self,cmd,data):
        write_to_log("got here maybe")
        if cmd == "ADD":
            response = self.add_ingredient_to_db(data)
            self.send_data("ADD",response)
        elif cmd == "DELETE":
            response = self.remove_ingredient_from_db(data)
            self.send_data("DELETE",response)
        elif cmd=="DELETE_ALL":
            response=self.remove_all_ingredients_from_db(data)
            self.send_data("DELETE_ALL",response)
        elif cmd=="TRANSFER":
            response=self.transfer_ingredients_from_db(data)
            self.send_data("TRANSFER",response)


    #data will look like this [10.0, 3, "fried", "oven", "soup", 3, "halal", "vegan", "kosher"] False this is goofy version
    #to separate the data I will get length and skip time with it
    #then I will run the loop for the amount+skipped parts e.g. 2+3=5 -> 2:5 will get 3 ingredients
    def handle_make(self,parameters):
        parameters=json.loads(parameters)
        write_to_log(parameters['time'])
        write_to_log(parameters['type'])
        write_to_log(parameters['preference'])
        data=get_lists_with_ingredients(self._current_id)
        ingredients=self.extract_all_ingredients(data)
        ingredients=json.dumps(ingredients)
        #in client receive create a receive loop getting it one by one
        if len(parameters['type'])==0:
            ai_response=send_and_receive_ai_request(parameters['time'],"general",parameters['difficulty'],parameters['preference'], ingredients)
            write_to_log(ai_response)
            self.send_data("AI",ai_response)
        else:
            ai_response=send_and_receive_ai_request(parameters['time'],parameters['type'],parameters['difficulty'],parameters['preference'], ingredients)
            write_to_log(ai_response)
            self.send_data("AI",ai_response)

    def extract_all_ingredients(self,data):
        write_to_log(data)
        ingredients=[]
        for key in data.keys():
            for ing in data[key]:
                ingredients.append(ing)
        write_to_log(ingredients)
        return ingredients

    def handle_list(self,cmd,data):
        write_to_log("got here maybe")
        if cmd == "LIST":
            response = self.add_list_to_db(data)
            self.send_data("ADD", response)
        if cmd=="DELETE_LIST":
            response=self.remove_list_from_db(data)
            self.send_data("DELETE_LIST",response)


    def handle_first_handshake(self):
        private_key=rsa.generate_private_key(public_exponent=65537, key_size=1024)
        public_key=private_key.public_key()
        pem_public_key = public_key.public_bytes( encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
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

    def create_response_dict(self,code,item,ingredient_list=""):
        response= {"code": code, "item": item, "list": ingredient_list}
        return response

    def add_ingredient_to_db(self,ingredient):
        ingredient=json.loads(ingredient)
        list_name = ingredient[0]
        prev_name = ingredient[1]
        curr_name = ingredient[2]
        code = handle_ingredient_update(self._current_id, list_name,prev_name, curr_name)
        response=self.create_response_dict(code,curr_name,list_name)
        return  response

    def add_list_to_db(self,curr_list):
        curr_list=json.loads(curr_list)
        code = handle_db_list_update(self._current_id,curr_list)
        response=self.create_response_dict(code,curr_list)
        return response


    def remove_ingredient_from_db(self,data):
        data=json.loads(data)
        write_to_log(data[0])
        write_to_log(data[1])
        list_name: str = data[0]
        ingredient_name: str = data[1]
        code=delete_ingredient(self._current_id,list_name,ingredient_name)
        response=self.create_response_dict(code,ingredient_name,list_name)
        return response


    def transfer_ingredients_from_db(self,data):
        data=json.loads(data)
        src_list = data[0]
        dst_list = data[1]
        ingredient = data[2]
        code=transfer_ingredient(self._current_id,src_list,dst_list,ingredient)
        response=self.create_response_dict(code,ingredient,dst_list)
        return response

    def remove_all_ingredients_from_db(self,data):
        data=json.loads(data)
        list_name=data[0]
        write_to_log(list_name)
        code=remove_all_ingredients(self._current_id,list_name)
        response=self.create_response_dict(code,list_name)
        return response

    def remove_list_from_db(self,curr_list):
        curr_list=json.loads(curr_list)[0]
        code=delete_list(self._current_id,curr_list)
        response=self.create_response_dict(code,curr_list)
        return response

    def initiate_sign_in(self,username,password):
        self._current_id = get_id(username,password)
        write_to_log(f" id is{self._current_id}")
        data=get_lists_with_ingredients(self._current_id)
        write_to_log(data)
        self.send_data("Ingredients",data)

    def send_data(self,cmd,args,verbose=True):
        try:
            args=encode_data(args)
            cmd=encode_data(cmd)
            write_to_log(f"args: {args}")
            write_to_log(f"cmd: {cmd}")
            if self._fernet:
                args = self.encrypt(args)
                cmd=self.encrypt(cmd)
            msg=create_msg(cmd,args)
            self._client_socket.send(msg)
            if verbose:
                write_to_log(f"[Server_BL] send {msg}")
        except Exception as e:
            write_to_log(f"Error {e} while sending massage")


    def receive_msg(self,need_bytes=False):
        if need_bytes:
            cmd, msg=receive_bytes_msg(self._client_socket)
        else:
            cmd, msg=receive_msg(self._client_socket)
        if self._fernet:
            msg = self.decrypt(msg).decode()
            cmd=self.decrypt(cmd).decode()
        return cmd, msg













