
from Protocol import *
from PIL import ImageSequence


# class for signin will add switching frame inside register, home button and backtoreg btn
class SignIn:
    def __init__(self, container,disconnected_home, client_statue, callback_signin , callback_register):
        self._container = container
        self._disconnected_home=disconnected_home
        self._client_status : list = client_statue
        self._username = None
        self._password = None
        self._signin_window = None
        self._username_entry = None
        self._password_entry = None
        self._btn_back = None
        self._login_text = None
        self._username_text = None
        self._password_text = None
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
        self._login_text.place(x=430, y=50)

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
                                   hover_color="#6A3DB4", font=("Calibri", 17), fg_color="#7C4CC2",
                                   command=self.on_click_back)
        self._btn_back.place(x=915, y=10)

        self._btn_register=CTkButton(self._signin_window,text="Register",height=30,width=80,text_color="white",hover_color="#6A3DB4",
                                     font=("Calibri", 17), fg_color="#7C4CC2",command=self.on_click_register)
        self._btn_register.place(x=915,y=50)
    #get back home from sign in screen
    def on_click_back(self):
        self._signin_window.pack_forget()
        self._disconnected_home.pack(fill="both", expand=True)

    #get to register from sign in screen
    def on_click_register(self):
        self._signin_window.pack_forget()
        if self._register is not None:
            self._register.initiate_existing_ui()
        else:
            self._register = Register(self._container, self._disconnected_home, self._client_status, self.callback_client_register, self.initiate_existing_ui)
            self._register.create_ui()


    def initiate_existing_ui(self):
        def clear_entry(entry):
            if len(entry.get()) != 0:
                entry.delete(0, "end")
        self._login_massage.place_forget()
        self._signin_window.pack(fill="both", expand=True)
        #remove any existing strings from the entries.
        clear_entry(self._username_entry)
        clear_entry(self._password_entry)
        self._signin_window.focus() #make sure mouse focus isn't left on the entries
        if self._password_visible:
            self.toggle_password_visibility()

    #add a forget function instead
    def forget_window(self):
        self._signin_window.pack_forget()

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
        self._username = self._username_entry.get().strip()
        self._password = self._password_entry.get()
        success = self.check_sign_in()
        if success:
            data = {
                "name": self._username,
                "password": self._password
            }
            self.callback_client_signin(data)


    def check_sign_in(self):
            if not self._client_status[0]:
                self.show_massage("Please first connect to the server")
                return False
            #because these are the username and password rules I should return false instead of waiting for server response
            elif self._username == "" or self._password == "" or " " in self._password or len(self._username) > 32:
                self.show_massage("Wrong username or password")
                return False
            else:
                return True

    def reset_info(self):
        self._username=""
        self._password=""

    def show_massage(self,msg):
        self._login_massage.configure(text=msg, text_color="red")
        self._login_massage.place(x=500,y=310,anchor='center')

    def get_username(self):
        return self._username

    def extra_cybersecurity_measures(self):
        temp = CTkFrame(self._container, )
        temp.pack(fill="both", expand=True)
        self._signin_window.pack_forget()
        gif = CTkLabel(master=temp, text="תאכל לי אותו", font=("Calibri", 40, "bold"))
        gif.place(x=275, y=50)
        # Load GIF and get frames
        gif_image = Image.open(r"Images/hello.gif")
        # Load all frames as CTkImage objects
        frames = [
            CTkImage(frame.copy().convert("RGBA"), size=(400, 400))
            for frame in ImageSequence.Iterator(gif_image)
        ]
        self._animate(0, gif, frames)

    def _animate(self, frame_idx, gif, frames):
        # Update image and schedule next frame
        gif.configure(image=frames[frame_idx])
        next_idx = (frame_idx + 1) % len(frames)
        gif.after(10, self._animate, next_idx, gif, frames)  # 50ms delay between frames


class Register:
    def __init__(self,container,disconnected_home,client_statue,callback_client_register,callback_signin_ui):
        self._container=container
        self._disconnected_home_window=disconnected_home
        self._client_status=client_statue
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
        self._btn_register=None
        self._login_massage=None
        self._btn_password_visible=None
        self._open_eye_image=None
        self._close_eye_image = None
        self._password_visible=False
        self._default_items_checkbox=None
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

        self._btn_register=CTkButton(self._register_window,text="Register",font=("Calibri",15),command=self.on_click_register,height=30, width=150)
        self._btn_register.place(x=425,y=310)
        self._default_items_checkbox = CTkCheckBox(master=self._register_window, text="Add default items",font=("Calibri", 17))
        self._default_items_checkbox.place(x=585, y=315)
        self._default_items_checkbox.select()

        self._btn_back=CTkButton(self._register_window,text="Back",height=30, width=80,text_color="white",hover_color="#6A3DB4",font=("Calibri",17),fg_color="#7C4CC2",command=self.on_click_back)
        self._btn_back.place(x=915, y=10)




        self._btn_signin=CTkButton(self._register_window,text="Sign in",height=30,width=80,text_color="white",hover_color="#6A3DB4",
                                     font=("Calibri", 17), fg_color="#7C4CC2",command=self.on_click_signin)
        self._btn_signin.place(x=915,y=50)
    #go back to home from Register
    def on_click_back(self):
        self._register_window.pack_forget()
        self._disconnected_home_window.pack(fill="both", expand=True)

    def reset_info(self):
        self._password=""
        self._username=""
        self._confirm_password=""
    #go back to sign in from register
    def on_click_signin(self):
        self._register_window.pack_forget()
        self.callback_initiate_signin_ui()

    def initiate_existing_ui(self):
        def clear_entry(entry):
            if len(entry.get()) != 0:
                entry.delete(0, "end")
        self._login_massage.place_forget()
        self._register_window.pack(fill="both", expand=True)
        #remove any existing strings in entry
        clear_entry(self._password_entry)
        clear_entry(self._username_entry)
        clear_entry(self._confirm_password_entry)
        self._default_items_checkbox.select()
        self._register_window.focus() #make sure mouse focus isn't left on the entries
        if self._password_visible:
            self.toggle_password_visibility()


    def on_click_register(self):
        self._username=self._username_entry.get().strip()
        self._password=self._password_entry.get()
        self._confirm_password=self._confirm_password_entry.get()
        default_list_items=self._default_items_checkbox.get()
        success=self.check_register()
        if success:
            data={
                "name":self._username,
                "password":self._password,
                "default":default_list_items
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

    def check_register(self)->bool:
        if not self._login_massage:
            self._login_massage = CTkLabel(master=self._register_window, text_color="red")
        if not self._client_status[0]:
            self.print_massage("Please first connect to the server")
            return False
        elif self._confirm_password!=self._password:
            self.print_massage("Passwords Dont match!")
            return False
        #make sure password and username are ok
        elif self._username == "" or self._password == "" or " " in self._password or len(self._username)>32:
            self.print_massage("Enter a valid username and password:\n"
        "•Whitespaces are not allowed in password\n"
        "•Username must be below 32 characters")
            return False
        else:
            #for future remove the success here (it should only show success if it saved it to db not if no errors)
            return True

    def print_massage(self,msg):
        if msg == "saved to database":
            self._login_massage.configure(text="Success! Your account has been created.", text_color="green")
        else:
            self._login_massage.configure(text=msg, text_color="red")
        self._login_massage.place(x=500, y=370,anchor='center')

    def get_username(self):
        return self._username



