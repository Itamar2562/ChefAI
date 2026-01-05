import time

from ClientBL import *
from WidgetUtils import Ingredients
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

#automatic logout if disconnect *test 2 54
#do nutritional facts brodi
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

        self._food_types=None

        self._btn_reset=None
        self._btn_login=None
        self._btn_sign_out=None
        self._time_slider=None
        self._btn_make=None
        self._card=None
        self._image_for_card_area=None
        self._btn_add=None
        self._btn_clear=None
        self._cooking_time=None
        self._username=""
        self._sign_in = None


        self._ingredients=None

        self._register=None
        self._recipes=None
        self._connection = threading.Thread(target=self.connect_on_startup, daemon=True)
        self._connection.start()

        self._client_status = ClientStatue()

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
        self._greeting=CTkLabel(master=self._home, font=('Calibri', 20), anchor='w')
        self.update_greeting()
        self._greeting.place(x=5,y=0)
        self._ChefAI = CTkLabel(master=self._home, text="ChefAI", font=('Calibri', 50,"bold","underline"))
        self._ChefAI.place(x=410, y=0)

        self._card = CTkFrame(self._home,width=360,height=320,corner_radius=24,fg_color="#1E1E2E",border_width=2, border_color="#3A3F8F")
        self._image_for_card_area=CTkLabel(master=self._card,text="✨",font=("", 100))
        self._image_for_card_area.place(x=160,y=80,anchor='center')
        self._btn_make =CTkButton(self._card, text="MAKE!",font=("Segoe UI", 18, "bold"), width=300, height=80,corner_radius=28,fg_color="#5B5FD9",hover_color="#6F74FF",text_color="#E6E8FF", command=self.on_click_make)
        self._btn_make.place(x=180,y=225,anchor='center')
        #Max Time scale

        self._time_slider = CTkSlider(master=self._home,from_=10,to=120,orientation="horizontal",width=300,number_of_steps=22,command=self._change_slider_time)
        self._time_slider.set(10)
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

        self._food_types=CTkOptionMenu(master=self._home,values=["general","salad","dessert","sandwich","fried","soup","Grilled","baked"])
        self._food_types.place(x=20,y=460)

        self._btn_add=CTkButton(master=self._home,text="Add",font=("Calibri",17), fg_color="#C850C0",hover_color="#4185D0", height=30, width=80, command=self.on_click_add)
        self._btn_clear = CTkButton(master=self._home, height=30, width=80, text="Clear", fg_color="#C850C0",hover_color="#4185D0", font=("Arial",17),command=self.on_click_delete_all_btn)

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
        was_connected=False
        while True:
            if not self._client_status.connected:
                connected_text.configure(text="Not connected",text_color="red")
                if was_connected: #In order to make sure Im only initiating disconnected home if I was connected before instead of everytime.
                    self.initiate_disconnected_home()
                    write_to_log("got hee")
                    was_connected=False
                self._client_status.connected=self._client_bl.connect()
            else:
                connected_text.configure(text="connected",text_color="green")
                was_connected=True
                self._client_status.connected=self._client_bl.check_connection()

    def on_click_add(self):
        self._ingredients.add_ingredient()
        self._ingredients.move_down()

    def initiate_disconnected_home(self):
        self.forget_widget(self._btn_add)
        self.forget_widget(self._level)
        self.forget_widget(self._btn_sign_out)
        self.forget_widget(self._btn_clear)
        self.forget_widget(self._card)
        self.on_click_reset()
        if self._ingredients:
            self._ingredients.remove()
            self._ingredients=None
            #self.forget_widget(self._ingredients)
        self.update_greeting()
        self._username=""
        self._btn_login.place(x=915, y=10)

    def forget_widget(self,widget):
        if widget:
            widget.place_forget()

    def on_click_make(self):
        #only send data if client is connected maybe simply make btn disabled for furture
        self._client_bl.add_food_type_parameters(self._food_types.get())
        if not self._client_status.connected or not  self._client_status.signed_in or self._ingredients.is_editing():
            return
        cmd="MAKE"
        args=self._client_bl.get_parameters(self._time_slider.get())
        self._client_bl.send_data(cmd,args)
        self._home.pack_forget()
        self._recipes=Recipes(self._container,self._home,self._client_status,self._client_bl.receive_msg)
        self._recipes.create_ui()

    def on_click_login(self):
        def on_click_sign_in(data):
            cmd="SIGNIN"
            self._client_bl.send_data(cmd,data)
            msg=self._client_bl.receive_msg()
            self._sign_in.show_massage(msg)
            if msg == "connected":
                self._client_status.signed_in=True
                self._username=self._sign_in.get_username()
                self._sign_in.forget_window()
                self._home.pack(fill="both", expand=True)
                self.initiate_signed_in()
        def on_click_register(data):
            self._register = self._sign_in.get_register()
            cmd="REG"
            self._client_bl.send_data(cmd,data)
            msg = self._client_bl.receive_msg()
            self._register.print_massage(msg)
            #maybe create another thread that process receiving data
            #it gets data and cmd from server
            #now I just check it manually
            #also see if client status is even needed
            #also create different functions for switching frames and send them so there is a clean switching IMPORTANT (kinda did it having a problem with cleaning entry)
        self._home.pack_forget()
        #create only one login class that will hold user username and password for later use.
        if not self._sign_in:
            self._sign_in=SignIn(self._container,self._home,self._client_status,on_click_sign_in,on_click_register)
            self._sign_in.create_ui()
        else:
            self._sign_in.initiate_existing_ui()

    def on_click_sign_out(self):
        self._client_status.signed_in=False
        self._btn_sign_out.place_forget()
        self._btn_login.place(x=915, y=10)
        self.update_greeting()
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
        self._btn_add.configure(state='disabled')
        self._btn_clear.configure(state='disabled')
        self._ingredients = Ingredients(self._home, self._client_status,send_ingredient, receive_confirmation,update_add_btn,width=270,height=300,fg_color="#1E1E2E",border_width=2,border_color="#3A3F8F")
        t=threading.Thread(target=self.initiate_first_ingredients,daemon=True)
        t.start()
        self.update_greeting()
        self.forget_widget(self._btn_login)
        self._btn_sign_out.place(x=915, y=10)
        self._btn_add.place(x=10,y=60)
        self._ingredients.place(x=5,y=100)
        level_msg = self._client_bl.receive_msg()
        self._level.configure(text=Levels[level_msg])
        self._level.place(x=5,y=25)
        self._btn_clear.place(x=100,y=60)
        self._card.place(x=305,y=80)
        self.on_click_reset()

    def on_click_delete_all_btn(self):
        self._client_bl.send_data("DELETE_ALL","")
        succeed=bool(self._client_bl.receive_msg())
        if succeed:
            self._ingredients.clear_ingredients()
            self._btn_add.configure(state="normal")

    def initiate_first_ingredients(self):
        ingredient_list = self._client_bl.receive_msg()
        ingredient_list = json.loads(ingredient_list)
        for i in ingredient_list:
            try:
                self._ingredients.initiate_first_ingredients(i)
                time.sleep(0.05)
            except: #if user decided to exit while adding
                return
        self._btn_add.configure(state="normal")
        self._btn_clear.configure(state="normal")

    #do a function of update_greeting instead (it will update auto not return str)
    def update_greeting(self):
        if not self._client_status.connected or not self._client_status.signed_in:
            name= "guest"
        else:
            name=self._username
        time=get_time_greeting()
        self._greeting.configure(text=f"{time} {name}.")

    def on_click_reset(self):
        self._btn_vegetarian.configure(state="normal")
        self._btn_vegan.configure(state="normal")
        self._btn_kosher.configure(state="normal")
        self._btn_halal.configure(state="normal")
        self._food_types.configure(state="normal")
        self._time_slider.set(10)
        self._food_types.set('general')
        self._cooking_time.configure(text="Cooking time: 10.0min")
        self._client_bl.reset_parameters(self._time_slider)

    def on_click_vegetarian(self):
        self._btn_vegetarian.configure(state="disabled")
        self._client_bl.add_preference_parameters("vegetarian")
    def on_click_vegan(self):
        self._btn_vegan.configure(state="disabled")
        self._client_bl.add_preference_parameters("vegan")
    def on_click_halal(self):
        self._btn_halal.configure(state="disabled")
        self._client_bl.add_preference_parameters("halal")
    def on_click_kosher(self):
        self._btn_kosher.configure(state="disabled")
        self._client_bl.add_preference_parameters("kosher")

    def _change_slider_time(self,value):
        self._cooking_time.configure(text=f"Cooking time: {value}min")

    def run(self):
        self._root.mainloop()

if __name__=='__main__':
   Client=ClientGUI("127.0.0.1",8822)
   Client.run()
