from http.client import responses
from logging import exception

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
               if check_cmd(cmd)==1:
                   self.handle_make(data)
               elif check_cmd(cmd)==2:
                   self.handle_db_login_msg(cmd,data)
               elif check_cmd(cmd)==3:
                   write_to_log("got here2")
                   self.handle_ingredients(cmd,data)
            except:
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
        msg = create_response_msg_db(cmd, data)
        self.send_data("LOGIN",msg)
        if msg == "connected":
            self.initiate_sign_in(data)

    def handle_ingredients(self,cmd,data):
        write_to_log("got here maybe")
        if cmd == "ADD":
            response = self.add_ingredient_to_db(data)
            self.send_data("ADD",response)
        elif cmd == "DELETE":
            response = self.remove_ingredient_from_db(data)
            self.send_data("DELETE",response)
        elif cmd=="DELETE_ALL":
            response=self.remove_all_ingredients_from_db()
            self.send_data("DELETE_ALL",response)

    #data will look like this [10.0, 3, "fried", "oven", "soup", 3, "halal", "vegan", "kosher"]
    #to separate the data I will get length and skip time with it
    #then I will run the loop for the amount+skipped parts e.g. 2+3=5 -> 2:5 will get 3 ingredients
    def handle_make(self,data):
        data=json.loads(data)
        write_to_log(data['time'])
        write_to_log(data['type'])
        write_to_log(data['preference'])
        ingredients=get_ingredients_list(self._current_id)
        ingredients=json.dumps(ingredients)
        #in client receive create a receive loop getting it one by one
        if len(data['type'])==0:
            ai_response=send_and_receive_ai_request(data['time'],"general",data['preference'], ingredients)
            write_to_log(ai_response)
            self.send_data("AI",ai_response)
        else:
            ai_response=send_and_receive_ai_request(data['time'],data['type'],data['preference'], ingredients)
            write_to_log(ai_response)
            self.send_data("AI",ai_response)
        self.send_data("AI","END")






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

    def add_ingredient_to_db(self,ingredient):
        succeed = add_ingredient_to_db_by_id(self._current_id,ingredient)
        if succeed:
            return "True"
        return "False"

    def remove_ingredient_from_db(self,ingredient):
        succeed=remove_ingredient(self._current_id,ingredient)
        if succeed:
            return "True"
        return "False"

    def remove_all_ingredients_from_db(self):
        write_to_log("got here")
        succeed=remove_all_ingredients(self._current_id)
        if succeed:
            return "True"
        return "False"

    def initiate_sign_in(self,data):
        self._current_id = get_id(data)
        ingredients_list=get_ingredients_list(self._current_id)
        self.send_data("Ingredients",ingredients_list)

        level=self.get_level()
        self.send_data("LEVEL",level)

    def send_data(self,cmd,args,verbose=True):
        try:
            args=encode_data(args)
            cmd=encode_data(cmd)
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

    def get_level(self):
        user_id=self._current_id
        level=get_level_by_id(user_id)
        return level










