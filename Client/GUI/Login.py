from PIL import Image
from Client.BL.ClientOP import *
from customtkinter import *

class SignIn(CTkFrame):
    def __init__(self, container,disconnected_home, client_statue, callback_signin , callback_register):
        super().__init__(master=container)
        self._container = container
        self._disconnected_home=disconnected_home

        self._client_status : list = client_statue

        self._username = None
        self._password = None

        self._username_entry = None
        self._password_entry = None
        self._username_text = None
        self._password_text = None

        self._btn_back = None
        self._login_text = None

        self._btn_login = None
        self._login_message = None
        self._btn_password_visible = None
        self._open_eye_image = None
        self._close_eye_image = None
        self._is_password_visible = False

        self._register=None
        self._btn_register=None

        self._callback_client_signin = callback_signin
        self._callback_client_register = callback_register

    def create_ui(self):
        write_to_log("ui created login")
        self.pack(fill="both", expand=True)
        self._open_eye_image = CTkImage(Image.open(r"../IMAGES/open_eye.png"), size=(25, 25))
        self._close_eye_image = CTkImage(Image.open(r"../IMAGES/close_eye.png"), size=(25, 25))

        self._login_text = CTkLabel(master=self, text="Sign in",
                                    font=('Calibri', 50,"bold","underline"),text_color="#5B5FD9")
        self._login_text.place(x=430, y=50)

        self._username_entry = CTkEntry(self, placeholder_text="enter username")
        self._username_entry.place(x=430, y=150)
        self._username_text = CTkLabel(master=self, text="Username",
                                       font=('Calibri', 15)).place(x=465, y=120)

        self._login_message = CTkLabel(master=self, text_color="red")
        self._login_message.place_forget()
        self._password_text = CTkLabel(self, text="Password", font=('Calibri', 15)).place(x=465, y=180)
        self._password_entry = CTkEntry(self, show="*", placeholder_text="enter password")
        self._password_entry.place(x=430, y=210)

        self._btn_password_visible = CTkButton(master=self, image=self._open_eye_image,
                                               text="", hover=False,
                                               text_color="white", width=30, height=30, fg_color="transparent",
                                               command=self.toggle_password_visibility)
        self._btn_password_visible.place(x=570, y=206)

        self._btn_login = CTkButton(self, text="Sign in", font=("Calibri", 15),
                                    command=self.on_click_signin,
                                    height=30, width=150)
        self._btn_login.place(x=425, y=260)
        self._btn_back = CTkButton(self, text="Back", height=30, width=80, text_color="white",
                                   hover_color="#6A3DB4", font=("Calibri", 17), fg_color="#7C4CC2",
                                   command=self.on_click_back)
        self._btn_back.place(x=915, y=10)

        self._btn_register=CTkButton(self,text="Register",height=30,
                                     width=80,text_color="white",hover_color="#6A3DB4",
                                     font=("Calibri", 17), fg_color="#7C4CC2",command=self.on_click_register)
        self._btn_register.place(x=915,y=50)


    def initiate_existing_ui(self):
        def clear_entry(entry):
            if len(entry.get()) != 0:
                entry.delete(0, "end")
        self._login_message.place_forget()
        self.pack(fill="both", expand=True)
        #remove any existing strings from the entries.
        clear_entry(self._username_entry)
        clear_entry(self._password_entry)
        self.focus() #make sure mouse focus isn't left on the entries
        if self._is_password_visible:
            self.toggle_password_visibility()

    #get back home from sign in screen
    def on_click_back(self):
        self.pack_forget()
        self._disconnected_home.pack(fill="both", expand=True)

    #get to register from sign in screen
    def on_click_register(self):
        self.pack_forget()
        if self._register is not None:
            self._register.initiate_existing_ui()
        else:
            self._register = Register(self._container, self._disconnected_home,
                                      self._client_status, self._callback_client_register, self.initiate_existing_ui)
            self._register.create_ui()

    def get_register(self):
        return self._register

    def toggle_password_visibility(self):
        # if already visible
        if self._is_password_visible:
            self._password_entry.configure(show="*")
            self._btn_password_visible.configure(image=self._open_eye_image)
            self._is_password_visible = False
        else:
            self._password_entry.configure(show="")
            self._btn_password_visible.configure(image=self._close_eye_image)
            self._is_password_visible = True
            
    def on_click_signin(self):
        self._username = self._username_entry.get().strip()
        self._password = self._password_entry.get()
        success = self.check_sign_in()
        if success:
            data = {
                "name": self._username,
                "password": self._password
            }
            self._callback_client_signin(data)


    def check_sign_in(self):
            if not self._client_status[0]:
                self.show_message("Please first connect to the server")
                return False
            #because these are the username and password rules I should return false instead of waiting for server response
            elif self._username == "" or self._password == "" or " " in self._password or len(self._username) > 32:
                self.show_message("Wrong username or password")
                return False
            else:
                return True

    def show_message(self, msg):
        self._login_message.configure(text=msg, text_color="red")
        self._login_message.place(x=500, y=310, anchor='center')

    def get_username(self):
        return self._username

class Register(CTkFrame):
    def __init__(self,container,disconnected_home,client_statue,callback_client_register,callback_signin_ui):
        super().__init__(master=container)
        self._container=container
        self._disconnected_home_window=disconnected_home

        self._client_status=client_statue

        self._username=None
        self._password=None
        self._confirm_password=None

        self._username_entry=None
        self._password_entry=None
        self._confirm_password_entry=None

        self._username_text = None
        self._password_text = None
        self._confirm_password_text = None

        self._register_headline=None
        self._login_message=None

        self._btn_register=None
        self._btn_back=None
        self._btn_signin=None


        self._btn_password_visible=None
        self._open_eye_image=None
        self._close_eye_image = None
        self._is_password_visible=False

        self._pantry_staples_checkbox=None
        self._callback_client_register=callback_client_register
        self._callback_initiate_signin_ui=callback_signin_ui

    #create a father class of login that has the ui pw and username
    def create_ui(self):
        self.pack(fill="both", expand=True)
        self._open_eye_image=CTkImage(Image.open(r"../IMAGES/open_eye.png"), size=(25, 25))
        self._close_eye_image=CTkImage(Image.open(r"../IMAGES/close_eye.png"), size=(25, 25))

        self._register_headline=CTkLabel(master=self, text="Register", font=('Calibri', 50, "bold", "underline"), text_color="#5B5FD9")
        self._register_headline.place(x=415, y=50)

        self._username_entry=CTkEntry(self, placeholder_text="enter username")
        self._username_entry.place(x=430,y=150)
        self._username_text=CTkLabel(master=self,text="Username",font=('Calibri', 15)).place(x=465,y=120)

        self._login_message = CTkLabel(master=self, text_color="red")
        self._login_message.forget()
        self._password_text=CTkLabel(self,text="Password",font=('Calibri', 15)).place(x=465,y=180)
        self._password_entry=CTkEntry(self,show="*",placeholder_text="enter password")
        self._password_entry.place(x=430,y=210)

        self._btn_password_visible = CTkButton(master=self, image=self._open_eye_image, text="",hover=False, text_color="white",width=30, height=30,fg_color="transparent", command=self.toggle_password_visibility)
        self._btn_password_visible.place(x=570,y=206)

        self._confirm_password_text = CTkLabel(self, text="Confirm Password", font=('Calibri', 15))
        self._confirm_password_text.place(x=440, y=240)
        self._confirm_password_entry = CTkEntry(self, show="*", placeholder_text="confirm password")
        self._confirm_password_entry.place(x=430,y=270)

        self._btn_register=CTkButton(self,text="Register",font=("Calibri",15),command=self.on_click_register,height=30, width=150)
        self._btn_register.place(x=425,y=310)
        self._pantry_staples_checkbox = CTkCheckBox(master=self, text="Add pantry staples", font=("Calibri", 17))
        self._pantry_staples_checkbox.place(x=585, y=313)
        self._pantry_staples_checkbox.select()

        self._btn_back=CTkButton(self,text="Back",height=30, width=80,text_color="white",hover_color="#6A3DB4",font=("Calibri",17),fg_color="#7C4CC2",command=self.on_click_back)
        self._btn_back.place(x=915, y=10)

        self._btn_signin=CTkButton(self,text="Sign in",height=30,width=80,text_color="white",hover_color="#6A3DB4",
                                     font=("Calibri", 17), fg_color="#7C4CC2",command=self.on_click_signin)
        self._btn_signin.place(x=915,y=50)

    def initiate_existing_ui(self):
        def clear_entry(entry):
            if len(entry.get()) != 0:
                entry.delete(0, "end")

        self._login_message.place_forget()
        self.pack(fill="both", expand=True)
        # remove any existing strings in entry
        clear_entry(self._password_entry)
        clear_entry(self._username_entry)
        clear_entry(self._confirm_password_entry)
        self._pantry_staples_checkbox.select()
        self.focus()  # make sure mouse focus isn't left on the entries
        if self._is_password_visible:
            self.toggle_password_visibility()

    #go back to home from Register
    def on_click_back(self):
        self.pack_forget()
        self._disconnected_home_window.pack(fill="both", expand=True)

    #go back to sign in from register
    def on_click_signin(self):
        self.pack_forget()
        self._callback_initiate_signin_ui()

    def on_click_register(self):
        self._username=self._username_entry.get().strip()
        self._password=self._password_entry.get()
        self._confirm_password=self._confirm_password_entry.get()
        pantry_staples=self._pantry_staples_checkbox.get()
        success=self.check_register()
        if success:
            data={
                "name":self._username,
                "password":self._password,
                "pantry_staples":pantry_staples
            }
            self._callback_client_register(data)

    def toggle_password_visibility(self):
        #if already visible
        if self._is_password_visible:
            self._password_entry.configure(show="*")
            self._btn_password_visible.configure( image=self._open_eye_image)
            self._is_password_visible=False
        else:
            self._password_entry.configure(show="")
            self._btn_password_visible.configure(image=self._close_eye_image)
            self._is_password_visible=True

    def check_register(self)->bool:
        if not self._login_message:
            self._login_message = CTkLabel(master=self, text_color="red")
        if not self._client_status[0]:
            self.print_message("Please first connect to the server")
            return False
        elif self._confirm_password!=self._password:
            self.print_message("Passwords Dont match!")
            return False
        #make sure password and username are ok
        elif self._username == "" or self._password == "" or " " in self._password or len(self._username)>32:
            self.print_message("Enter a valid username and password:\n"
        "•Whitespaces are not allowed in password\n"
        "•Username must be below 32 characters")
            return False
        else:
            return True

    def print_message(self, msg, code=""):
        if code=="200":
            self._login_message.configure(text="Success! Your account has been created.", text_color="green")
        else:
            self._login_message.configure(text=msg, text_color="red")
        self._login_message.place(x=500, y=370, anchor='center')



