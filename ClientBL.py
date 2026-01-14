from Protocol import *

class ClientStatue:
    def __init__(self):
        self.connected=False
        self.signed_in=False
        self.data={}

class ClientBL:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        self.parameters={'time':10.0,'type':"", 'preference':[]}
        self.client_socket=None
        self.fernet=None
    def reset_parameters(self,time_slider):
        self.parameters['time']=10.0
        self.parameters['type']=""
        self.parameters['preference'].clear()

    def add_food_type_parameters(self,parameter):
        self.parameters['type']=parameter

    def add_preference_parameters(self,parameter):
        self.parameters['preference'].append(parameter)

    def get_parameters(self,time):
        self.parameters['time']=time
        return self.parameters

    def connect(self):
        try:
            self.client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.client_socket.connect((self.ip,self.port))
            write_to_log(f"[Client_BL] client {self.client_socket.getsockname()} connected ")
            self.fernet=None
            self.handle_first_handshake()
            return True
        except Exception as e:
            write_to_log("[Client_BL] attempting to connect...")
            return False

    def handle_first_handshake(self):
        pem_public_key=self.receive_msg(True)
        public_key = serialization.load_pem_public_key(pem_public_key,backend=default_backend())
        session_key=Fernet.generate_key()
        encrypted_session_key = public_key.encrypt(session_key,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
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
            #if client_socket is none return false
            return False
        except BlockingIOError:
            # No data available, but connection is still alive
            return True
        #if got any other exceptions then connection is closed
        except:
            if self.client_socket:
                self.client_socket.close()
            self.client_socket=None
            return False

    def receive_msg(self,need_bytes=False):
        if need_bytes:
            cmd, msg=receive_bytes_msg(self.client_socket)
        else:
            cmd, msg=receive_msg(self.client_socket)
            if self.fernet:
                msg=self.decrypt(msg).decode()
        return msg


    def send_data(self,cmd,args,verbose=True):
        write_to_log(f"data: {cmd},{args}")
        try:
            args=encode_data(args)
            cmd=encode_data(cmd)
            if self.fernet: #first encrypt and then get msg length and arrange it
                args = self.encrypt(args)
                cmd=self.encrypt(cmd)
            msg= create_msg(cmd, args)
            self.client_socket.send(msg)
            if verbose:
                write_to_log(f"[Client_BL] send {msg}")
        except Exception as e:
            write_to_log(f"Error {e} while sending massage")








