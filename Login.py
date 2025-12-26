from Protocol import *

# class for signin will add switching frame inside register, home button and backtoreg btn
class SignIn:
    def __init__(self, container, home, client_statue, callback_signin , callback_register):
        self._container = container
        self._home_window = home
        self._client_statue = client_statue
        self._username = None
        self._password = None
        self._signin_window = None
        self._username_entry = None
        self._password_entry = None
        self._btn_back = None
        self._login_text = None
        self._username_text = None
        self._password_text = None
        self._confirm_password_text = None
        self._btn_login = None
        self._login_massage = None
        self._btn_password_visible = None
        self._open_eye_image = None
        self._close_eye_image = None
        self._password_visible = False
        self._register=None
        self._btn_register=None
        self.callback_client_signin = callback_signin
        self.callback_client_register = callback_register

        # create a father class of login that has the ui pw and username

    def create_ui(self):
        self._signin_window = CTkFrame(self._container, )
        self._signin_window.pack(fill="both", expand=True)
        self._open_eye_image = CTkImage(Image.open(r"Images\open_eye.png"), size=(20, 20))
        self._close_eye_image = CTkImage(Image.open(r"Images\close_eye.png"), size=(20, 20))

        self._login_text = CTkLabel(master=self._signin_window, text="Sign in", font=('Calibri', 50,"bold","underline"))
        self._login_text.place(x=435, y=50)

        self._username_entry = CTkEntry(self._signin_window, placeholder_text="enter username")
        self._username_entry.place(x=430, y=150)
        self._username_text = CTkLabel(master=self._signin_window, text="Username", font=('Calibri', 15)).place(x=465, y=120)

        self._login_massage = CTkLabel(master=self._signin_window, text_color="red")
        self._login_massage.place_forget()
        self._password_text = CTkLabel(self._signin_window, text="Password", font=('Calibri', 15)).place(x=465, y=180)
        self._password_entry = CTkEntry(self._signin_window, show="♀", placeholder_text="enter password")
        self._password_entry.place(x=430, y=210)

        self._btn_password_visible = CTkButton(master=self._signin_window, image=self._close_eye_image, text="", hover=False,
                                               text_color="white", width=30, height=30, fg_color="transparent",
                                               command=self.toggle_password_visibility)
        self._btn_password_visible.place(x=570, y=209)

        self._btn_login = CTkButton(self._signin_window, text="Sign in", font=("Calibri", 15),
                                    command=self.on_click_signin,
                                    height=30, width=150)
        self._btn_login.place(x=425, y=260)
        self._btn_back = CTkButton(self._signin_window, text="Back", height=30, width=80, text_color="white",
                                   hover_color="#4185D0", font=("Calibri", 17), fg_color="#C850C0",
                                   command=self.on_click_back)
        self._btn_back.place(x=915, y=10)

        self._btn_register=CTkButton(self._signin_window,text="Register",height=30,width=80,text_color="white",hover_color="#4185D0",
                                     font=("Calibri", 17), fg_color="#C850C0",command=self.on_click_register)
        self._btn_register.place(x=915,y=50)
    #get back home from sign in screen
    def on_click_back(self):
        self._signin_window.pack_forget()
        self._home_window.pack(fill="both", expand=True)

    #get to register from sign in screen
    def on_click_register(self):
        self._signin_window.pack_forget()
        if self._register is not None:
            self._register.initiate_existing_ui()
        else:
            self._register = Register(self._container, self._home_window, self._client_statue,self.callback_client_register, self.initiate_existing_ui)
            self._register.create_ui()


    def initiate_existing_ui(self):
        self._login_massage.place_forget()
        self._signin_window.pack(fill="both", expand=True)
        if self._password_visible:
            self.toggle_password_visibility()

    #add a forget function instead
    def get_signin_window(self):
        return  self._signin_window

    def get_register(self):
        return self._register

    def toggle_password_visibility(self):
        # if already visible
        if self._password_visible:
            self._password_entry.configure(show="♀")
            self._btn_password_visible.configure(image=self._close_eye_image)
            self._password_visible = False
        else:
            self._password_entry.configure(show="")
            self._btn_password_visible.configure(image=self._open_eye_image)
            self._password_visible = True
            
    def on_click_signin(self):
        self._username = self._username_entry.get()
        self._password = self._password_entry.get()
        success = self.print_login_error_msg()
        if success:
            data = {
                "name": self._username,
                "password": self._password
            }
            self.callback_client_signin(data)
    def print_login_error_msg(self):
        if not self._client_statue.connected:
            self._login_massage.configure(text="Please first connect to the server", text_color="red")
            self._login_massage.place(x=410, y=300)
            return False
            # make sure password and username are ok
        else:
            # for future remove the success here (it should only show success if it saved it to db not if no errors)
            return True
    #this function prints massages *after sending to db*
    def print_database_msg(self,msg):
        self._login_massage.configure(text=msg)
        self._login_massage.place(x=440, y=300)
    def get_username(self):
        return self._username



class Register:
    def __init__(self,container,home,client_statue,callback_client_register,callback_signin_ui):
        self._container=container
        self._home_window=home
        self._client_statue=client_statue
        self._username=None
        self._password=None
        self._confirm_password=None
        self._register_window=None
        self._username_entry=None
        self._password_entry=None
        self._confirm_password_entry=None
        self._btn_back=None
        self._login_text=None
        self._username_text=None
        self._password_text=None
        self._confirm_password_text=None
        self._btn_login=None
        self._login_massage=None
        self._btn_password_visible=None
        self._open_eye_image=None
        self._close_eye_image = None
        self._password_visible=False
        self._btn_signin=None
        self.callback_client_register=callback_client_register
        self.callback_initiate_signin_ui=callback_signin_ui

    #create a father class of login that has the ui pw and username
    def create_ui(self):
        self._register_window=CTkFrame(self._container,)
        self._register_window.pack(fill="both", expand=True)
        self._open_eye_image=CTkImage(Image.open(r"Images\open_eye.png"), size=(20, 20))
        self._close_eye_image=CTkImage(Image.open(r"Images\close_eye.png"),size=(20,20))


        self._login_text=CTkLabel(master=self._register_window,text="Register",font=('Calibri', 50,"bold","underline"))
        self._login_text.place(x=415,y=50)

        self._username_entry=CTkEntry(self._register_window, placeholder_text="enter username")
        self._username_entry.place(x=430,y=150)
        self._username_text=CTkLabel(master=self._register_window,text="Username",font=('Calibri', 15)).place(x=465,y=120)

        self._login_massage = CTkLabel(master=self._register_window, text_color="red")
        self._login_massage.forget()
        self._password_text=CTkLabel(self._register_window,text="Password",font=('Calibri', 15)).place(x=465,y=180)
        self._password_entry=CTkEntry(self._register_window,show="♀",placeholder_text="enter password")
        self._password_entry.place(x=430,y=210)

        self._btn_password_visible = CTkButton(master=self._register_window, image=self._close_eye_image, text="",hover=False, text_color="white",width=30, height=30,fg_color="transparent", command=self.toggle_password_visibility)
        self._btn_password_visible.place(x=570,y=209)

        self._confirm_password_text = CTkLabel(self._register_window, text="Confirm Password", font=('Calibri', 15))
        self._confirm_password_text.place(x=440, y=240)
        self._confirm_password_entry = CTkEntry(self._register_window, show="♀", placeholder_text="confirm password")
        self._confirm_password_entry.place(x=430,y=270)

        self._btn_login=CTkButton(self._register_window,text="Register",font=("Calibri",15),command=self.on_click_register,height=30, width=150)
        self._btn_login.place(x=425,y=310)
        self._btn_back=CTkButton(self._register_window,text="Back",height=30, width=80,text_color="white",hover_color="#4185D0",font=("Calibri",17),fg_color="#C850C0",command=self.on_click_back)
        self._btn_back.place(x=915, y=10)

        self._btn_signin=CTkButton(self._register_window,text="Sign in",height=30,width=80,text_color="white",hover_color="#4185D0",
                                     font=("Calibri", 17), fg_color="#C850C0",command=self.on_click_signin)
        self._btn_signin.place(x=915,y=50)
    #go back to home from Register
    def on_click_back(self):
        self._register_window.pack_forget()
        self._home_window.pack(fill="both", expand=True)

    #go back to sign in from register
    def on_click_signin(self):
        self._register_window.pack_forget()
        self.callback_initiate_signin_ui()

    def initiate_existing_ui(self):
        self._login_massage.place_forget()
        self._register_window.pack(fill="both", expand=True)
        if self._password_visible:
            self.toggle_password_visibility()


    def on_click_register(self):
        self._username=self._username_entry.get()
        self._password=self._password_entry.get()
        self._confirm_password=self._confirm_password_entry.get()
        success=self.print_login_error_msg()
        if success:
            data={
                "name":self._username,
                "password":self._password
            }
            self.callback_client_register(data)
            #going back to sign in immediate
            # self._register_window.pack_forget()
            # self.callback_initiate_signin_ui()

    def toggle_password_visibility(self):
        #if already visible
        if self._password_visible:
            self._password_entry.configure(show="♀")
            self._btn_password_visible.configure( image=self._close_eye_image)
            self._password_visible=False
        else:
            self._password_entry.configure(show="")
            self._btn_password_visible.configure(image=self._open_eye_image)
            self._password_visible=True

    def print_login_error_msg(self)->bool:
        if not self._login_massage:
            self._login_massage = CTkLabel(master=self._register_window, text_color="red")
        if not self._client_statue.connected:
            self._login_massage.configure(text="Please first connect to the server",text_color="red")
            self._login_massage.place(x=410, y=345)
            return False
        elif self._confirm_password!=self._password:
            self._login_massage.configure(text="Password Dont match!",text_color="red")
            self._login_massage.place(x=435,y=345)
        #make sure password and username are ok
        elif self._username == "" or self._password == "" or " " in self._password or len(self._username)>32:
            self._login_massage.configure(text=(
        "Enter a valid username and password:\n"
        "          • Whitespaces are not allowed in password\n"
        "      • Username must be below 32 characters"),text_color="red")
            self._login_massage.place(x=360, y=350)
            return False
        else:
            #for future remove the success here (it should only show success if it saved it to db not if no errors)
            return True

        # this function prints massages *after sending to db*
    def print_database_msg(self, msg):
        self._login_massage.configure(text=msg)
        if msg == "saved to database":
            self._login_massage.configure(text_color="green")
            self._login_massage.place(x=445, y=345)
        else:
            self._login_massage.configure(text_color="red")
            self._login_massage.place(x=430, y=345)

    def get_username(self):
        return self._username



