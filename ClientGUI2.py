from ClientBL import *
from Ingredients import Ingredients
from Login import SignIn
from Recipes import Recipes

BG_IMAGE = "./Images/GUI - BG.png"
BTN_IMAGE="./Images/GUI - button.png"
BTN_Make_IMAGE="./Images/GUI - button_make.png"
FONT="Calibri"
FONT_BUTTON=(FONT,16)
SMALL_FONT_BUTTON=(FONT,12)

class ClientStatue:
    def __init__(self):
        self.connected=False
        self.signed_in=False

#automatic logout if disconnect *test

class ClientGUI:
    def __init__(self,ip,port):
        self._client_bl=ClientBL(ip,port)
        self._ip=ip
        self._port=port
        self._root=CTk()
        self._ChefAI=None
        self._container=None
        self._home=None
        self._text_Received=None
        self._scroll_bar=None
        self._level=None
        self._greeting=None
        self._btn_Update=None
        self._btn_Save=None


        self._btn_vegetarian=None
        self._btn_vegan=None
        self._btn_halal=None
        self._btn_kosher=None

        self._btn_soup=None
        self._btn_oven=None
        self._btn_fried=None
        self._btn_dessert=None


        self._btn_reset=None
        self._btn_login=None
        self._btn_sign_out=None
        self._time_slider=None
        self._btn_make=None
        self._btn_add=None
        self._cooking_time=None
        self._username=""
        self._login = None


        self.ingredients=None

        self._register=None
        self._recipes=None
        self._connection = threading.Thread(target=self.connect_on_startup, daemon=True)
        self._connection.start()

        #temp solution
        self.temp=0
        self._client_status = ClientStatue()

        self._ingredients_frame=None

        self.create_ui()

    def create_ui(self):
        self._root.title("Client GUI")
        img_width=1004
        img_height=526
        set_appearance_mode("dark")
        self._root.geometry(f'{img_width}x{img_height}')
        self._root.resizable(False,False)

        self._container =CTkFrame(self._root)
        self._container.pack(fill="both", expand=True)
        self._home=CTkFrame(master=self._container)
        self._home.pack(fill="both", expand=True)

        #I will change greeting
        self._greeting=CTkLabel(master=self._home,text=self.get_greeting(), font=('Calibri', 20), anchor='w')
        self._greeting.place(x=5,y=0)
        self._ChefAI = CTkLabel(master=self._home, text="ChefAI", font=('Calibri', 50))
        self._ChefAI.place(x=410, y=0)

        self._btn_make=CTkButton(master=self._home, text="Make!", font=("Calibri",30), fg_color="#FF991C", hover_color="#DB8318",height=60,width=150, command=self.on_click_make)
        self._btn_make.place(x=675,y=425)
        #Max Time scale

        self._time_slider = CTkSlider(master=self._home,from_=10,to=120,orientation="horizontal",width=300,number_of_steps=22,command=self._change_slider_time)
        self._time_slider.set(10)
        self._client_bl.parameters.append(10) #set the first parameter to cooking time
        self._time_slider.place(x=200,y=465)

        self._cooking_time=CTkLabel(master=self._home, text="Cooking time: 10.0min",text_color="white", font=("Calibri",20))
        self._cooking_time.place(x=270,y=430)

        #parameters buttons
        self._btn_reset=CTkButton(master=self._home,text="Reset", font=SMALL_FONT_BUTTON, fg_color="#C850C0", hover_color="#4185D0", height=30,width=80,command=self.on_click_reset)
        self._btn_reset.place(x=325,y=485)
        self._btn_vegetarian=CTkButton(master=self._home,text="Vegetarian", font=SMALL_FONT_BUTTON, fg_color="#C850C0", hover_color="#4185D0", height=30,width=80,command=self.on_click_vegetarian)
        self._btn_vegetarian.place(x=505,y=420)
        self._btn_vegan=CTkButton(master=self._home,text="Vegan", font=SMALL_FONT_BUTTON, fg_color="#C850C0", hover_color="#4185D0", height=30,width=80,command=self.on_click_vegan)
        self._btn_vegan.place(x=590, y=420)
        self._btn_halal=CTkButton(master=self._home,text="Halal", font=SMALL_FONT_BUTTON, fg_color="#C850C0", hover_color="#4185D0",  height=30,width=80,command=self.on_click_halal)
        self._btn_halal.place(x=505, y=460)
        self._btn_kosher=CTkButton(master=self._home,text="Kosher", font=SMALL_FONT_BUTTON,fg_color="#C850C0", hover_color="#4185D0",height=30,width=80,command=self.on_click_kosher)
        self._btn_kosher.place(x=590, y=460)

        self._btn_soup=CTkButton(master=self._home,text="Soup", font=SMALL_FONT_BUTTON,fg_color="#C850C0", hover_color="#4185D0",height=30,width=80,command=self.on_click_soup)
        self._btn_soup.place(x=20, y=465)

        self._btn_oven = CTkButton(master=self._home, text="Oven", font=SMALL_FONT_BUTTON, fg_color="#C850C0",hover_color="#4185D0", height=30, width=80, command=self.on_click_oven)
        self._btn_oven.place(x=105, y=465)

        self._btn_dessert = CTkButton(master=self._home, text="Dessert", font=SMALL_FONT_BUTTON, fg_color="#C850C0",hover_color="#4185D0", height=30, width=80, command=self.on_click_dessert)
        self._btn_dessert.place(x=20, y=425)

        self._btn_fried = CTkButton(master=self._home, text="Fried", font=SMALL_FONT_BUTTON, fg_color="#C850C0",hover_color="#4185D0", height=30, width=80, command=self.on_click_fried)
        self._btn_fried.place(x=105, y=425)


        self._btn_add=CTkButton(master=self._home,text="Add",font=("Calibri",17), fg_color="#C850C0",hover_color="#4185D0", height=30, width=80, command=self.on_click_add)
        self._ingredients_frame=CTkScrollableFrame(master=self._home, width=300, height=300)

        self._level=CTkLabel(master=self._home, font=("Calibri",25))

        self._btn_login = CTkButton(master=self._home, text="Login", font=("Calibri",17), fg_color="#C850C0",hover_color="#4185D0", height=30, width=80, command=self.on_click_login)
        self._btn_login.place(x=915, y=10)

        self._btn_sign_out = CTkButton(master=self._home, text="Sign out", font=("Calibri", 17), fg_color="#C850C0",hover_color="#4185D0", height=30, width=80, command=self.on_click_sign_out)
        self._btn_sign_out.place_forget()

#CREATE A GOOD ONE FUNCTION RECIEVE IN CLIENT_BL THAT CHECKS
    def connect_on_startup(self):
        #the weird prob that it doesn't get removed is because home is still none so gotta remove the first build
        connected_text= CTkLabel(master=self._root, text="Not connected", font=('Calibri', 22),fg_color="#333333")
        connected_text.place(x=5,y=500)
        while True:
            if not self._client_status.connected:
                connected_text.configure(text="Not connected",text_color="red")
                self.initiate_disconnected_home()
                self._client_status.connected=self._client_bl.connect()
            else:
                connected_text.configure(text="connected",text_color="green")
                self._client_status.connected=self._client_bl.check_connection()

    def on_click_add(self):
        self.ingredients.add_ingredient()

    def initiate_disconnected_home(self):
        if self._btn_add and self._btn_add.winfo_ismapped():
            self._btn_add.place_forget()
        if self._ingredients_frame and self._ingredients_frame.winfo_ismapped():
            self.ingredients.clear_ingredients()
            self._ingredients_frame.place_forget()
        if self._level and self._level.winfo_ismapped():
            self._level.place_forget()
        self._greeting.configure(text=self.get_greeting())
        self._username=""
        self._btn_sign_out.place_forget()
        self._btn_login.place(x=915, y=10)


    def on_click_make(self):
        #only send data if client is connected
        if not self._client_status.connected or not  self._client_status.signed_in or self.ingredients.is_editing():
            return
        cmd="MAKE"
        self._client_bl.parameters[0]=self._time_slider.get()
        args=self._client_bl.parameters
        self._client_bl.send_data(cmd,args)
        self._home.pack_forget()
        self._recipes=Recipes(self._container,self._home,self._client_status,self._client_bl.receive_msg)
        self._recipes.create_ui()

    def on_click_login(self):
        def on_click_sign_in(data):
            cmd="SIGNIN"
            self._client_bl.send_data(cmd,data)
            msg=self._client_bl.receive_msg()
            self._login.print_database_msg(msg)
            if msg == "connected":
                self._client_status.signed_in=True
                self._username=self._login.get_username()
                self._login.get_signin_window().pack_forget()
                self._home.pack(fill="both", expand=True)
                self.initiate_signed_in()
        def on_click_register(data):
            self._register = self._login.get_register()
            cmd="REG"
            self._client_bl.send_data(cmd,data)
            msg = self._client_bl.receive_msg()
            self._register.print_database_msg(msg)
            #maybe create another thread that process receiving data
            #it gets data and cmd from server
            #now I just check it manually
            #also see if client status is even needed
            #also create different functions for switching frames and send them so there is a clean switching IMPORTANT (kinda did it having a problem with cleaning entry)
            self._login.print_database_msg(msg)
        self._home.pack_forget()
        #create only one login class that will hold user username and password for later use.
        if not self._login:
            self._login=SignIn(self._container,self._home,self._client_status,on_click_sign_in,on_click_register)
            self._login.create_ui()
        else:
            self._login.initiate_existing_ui()

    def on_click_sign_out(self):
        self._client_status.signed_in=False
        self._btn_sign_out.place_forget()
        self._btn_login.place(x=915, y=10)
        self._greeting.configure(text=self.get_greeting())
        self.initiate_disconnected_home()
        self._client_bl.send_data("SIGN_OUT","")

    def initiate_signed_in(self):
        def send_ingredient(cmd,data):
            self._client_bl.send_data(cmd, data)
        def receive_confirmation() ->bool:
            msg = self._client_bl.receive_msg()
            return bool(msg)
        def update_add_btn(state):
            self._btn_add.configure(state=state)
        if not self.ingredients:
            self.ingredients = Ingredients(self._home, update_add_btn, self._ingredients_frame, self._client_status,send_ingredient, receive_confirmation)
        ingredient_list = self._client_bl.receive_msg()
        ingredient_list = json.loads(ingredient_list)
        for i in ingredient_list:
            self.ingredients.initiate_first_ingredients(i)
        self._greeting.configure(text=self.get_greeting())
        self._btn_login.place_forget()
        self._btn_sign_out.place(x=915, y=10)
        self._btn_add.place(x=10,y=60)
        self._ingredients_frame.place(x=0,y=100)
        level_msg = self._client_bl.receive_msg()
        self._level.configure(text=Levels[level_msg])
        self._level.place(x=5,y=25)


    def get_greeting(self) ->str:
        if not self._client_status.connected or not self._client_status.signed_in:
            name= "guest"
        else:
            name=self._username
        time=get_time_greeting()
        return f"{time} {name}."

    def on_click_reset(self):
        self._btn_vegetarian.configure(state="normal")
        self._btn_vegan.configure(state="normal")
        self._btn_kosher.configure(state="normal")
        self._btn_halal.configure(state="normal")
        self._btn_soup.configure(state="normal")
        self._btn_oven.configure(state="normal")
        self._btn_dessert.configure(state="normal")
        self._btn_fried.configure(state="normal")
        self._time_slider.set(10)
        self._cooking_time.configure(text="Cooking time: 10.0min")
        self._client_bl.reset_parameters(self._time_slider)

    def on_click_vegetarian(self):
        self._btn_vegetarian.configure(state="disabled")
        self._client_bl.add_parameters("vegetarian")
    def on_click_vegan(self):
        self._btn_vegan.configure(state="disabled")
        self._client_bl.add_parameters("vegan")
    def on_click_halal(self):
        self._btn_halal.configure(state="disabled")
        self._client_bl.add_parameters("halal")
    def on_click_kosher(self):
        self._btn_kosher.configure(state="disabled")
        self._client_bl.add_parameters("kosher")
    def on_click_soup(self):
        self._btn_soup.configure(state="disabled")
        self._client_bl.add_parameters("soup")
    def on_click_oven(self):
        self._btn_oven.configure(state="disabled")
        self._client_bl.add_parameters("oven")
    def on_click_dessert(self):
        self._btn_dessert.configure(state="disabled")
        self._client_bl.add_parameters("dessert")
    def on_click_fried(self):
        self._btn_fried.configure(state="disabled")
        self._client_bl.add_parameters("fried")


    def _change_slider_time(self,value):
        self._cooking_time.configure(text=f"Cooking time: {value}min")

    def run(self):
        self._root.mainloop()

if __name__=='__main__':
   Client=ClientGUI("127.0.0.1",8822)
   Client.run()
