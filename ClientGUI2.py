from doctest import master

from ClientBL import *
from WidgetUtils import Ingredient, DraggableFrame
from Login import SignIn
from Recipes import Recipes
from Refrigerator import Refrigerator

BG_IMAGE = "./Images/GUI - BG.png"
BTN_IMAGE="./Images/GUI - button.png"
BTN_Make_IMAGE="./Images/GUI - button_make.png"
FONT="Calibri"
FONT_BUTTON=(FONT,16)
SMALL_FONT_BUTTON=(FONT,12)

#automatic logout if disconnect *test 2 54
#do nutritional facts brodi
class ClientGUI:
    def __init__(self,ip,port):
        self._client_bl=ClientBL(ip,port)
        self._ip=ip
        self._port=port
        self._root=CTk()
        self._ChefAI=None
        self._signed_out_ChefAI=None
        self._container=None
        self._home=None
        self._not_logged_in_home=None
        self._text_Received=None
        self._scroll_bar=None
        self._greeting=None
        self._default_greeting=None
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
        self._main_ingredients_label=None
        self._cooking_time=None
        self._username=""
        self._sign_in = None


        self._ingredients=None

        self.image_for_card_area=CTkImage(Image.open(r"Images/chef_hat.png"),size=(150,150))
        self.closed_refrigerator_image=CTkImage(Image.open(r"Images/Closed_refrigerator2.png"),size=(300,400))
        self.opened_refrigerator_image=CTkImage(Image.open(r"Images/Opened_refrigerator2.png"),size=(295,395))
        self._refrigerator=None

        self._btn_refrigerator=None
        self._register=None
        self._recipes=None
        self._connection = threading.Thread(target=self.connect_on_startup, daemon=True)
        self._connection.start()

        self._client_status = ClientStatue()
        self._specific_frame=None
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

        #logged out frame
        self._not_logged_in_home=CTkFrame(master=self._container)
        self._not_logged_in_home.pack(fill="both", expand=True)

        self._btn_login = CTkButton(master=self._not_logged_in_home, text="Login", font=("Calibri", 17),
                                    fg_color="#C850C0", hover_color="#4185D0",
                                    height=30, width=80,command=self.on_click_login)
        self._btn_login.place(x=915, y=10)
        #I will change greeting
        self._default_greeting=CTkLabel(master=self._not_logged_in_home, font=('Calibri', 20), anchor='w')
        self.update_default_greeting()
        self._default_greeting.place(x=5,y=0)
        self._signed_out_ChefAI = CTkLabel(master=self._not_logged_in_home, text="ChefAI", font=('Calibri', 220,"bold","underline"),
                                text_color="#5B5FD9")
        self._signed_out_ChefAI.place(x=502, y=200, anchor="center")

        #logged in frame
        self._ChefAI = CTkLabel(master=self._home, text="ChefAI", font=('Calibri', 50,"bold","underline"),
                                text_color="#5B5FD9")
        self._ChefAI.place(x=502, y=25,anchor="center")

        self._greeting = CTkLabel(master=self._home, font=('Calibri', 20), anchor='w')
        self._greeting.place(x=5,y=0)

        self._card = CTkFrame(self._home,width=360,height=320,corner_radius=24,fg_color="#1E1E2E",
                              border_width=2, border_color="#3A3F8F")
        self._card.place(x=502,y=250,anchor='center')
        self._image_for_card_area=CTkLabel(master=self._card,text="",image=self.image_for_card_area)
        self._image_for_card_area.place(x=180,y=100,anchor='center')
        self._btn_make =CTkButton(self._card, text="MAKE!✨",font=("Segoe UI", 25, "bold"), width=300,
                                  height=80,corner_radius=28,fg_color="#5B5FD9",hover_color="#6F74FF",
                                  text_color="#E6E8FF", command=self.on_click_make)
        self._btn_make.place(x=180,y=225,anchor='center')
        #Max Time scale

        self._btn_refrigerator=CTkButton(master=self._home,text="",image=self.closed_refrigerator_image,
                                         fg_color="transparent",hover=False,command=self.on_click_refrigerator)
        self._btn_refrigerator.bind('<Motion>',
                                    lambda event:self._btn_refrigerator.configure(image=self.opened_refrigerator_image),add='+')
        self._btn_refrigerator.bind('<Leave>',
                                    lambda event:self._btn_refrigerator.configure(image=self.closed_refrigerator_image),add='+')
        self._btn_refrigerator.place(x=860, y=275, anchor="center")

        self._time_slider = CTkSlider(master=self._home,from_=10,to=120,orientation="horizontal",width=300,
                                      number_of_steps=22,command=self._change_slider_time)
        self._time_slider.set(10)
        self._time_slider.place(x=502,y=465,anchor='center')

        self._cooking_time=CTkLabel(master=self._home, text="Cooking time: 10.0min",text_color="white", font=("Calibri",20))
        self._cooking_time.place(x=502,y=440,anchor='center')

        #parameters buttons
        self._btn_reset=CTkButton(master=self._home,text="Reset", font=SMALL_FONT_BUTTON, fg_color="#C850C0",
                                  hover_color="#4185D0", height=30,width=80,command=self.on_click_reset)
        self._btn_reset.place(x=502,y=490,anchor='center')
        self._btn_vegetarian=CTkButton(master=self._home,text="Vegetarian", font=SMALL_FONT_BUTTON, fg_color="#C850C0",
                                       hover_color="#4185D0", height=30,width=80,command=self.on_click_vegetarian)
        self._btn_vegetarian.place(x=300,y=485,anchor='center')
        self._btn_vegan=CTkButton(master=self._home,text="Vegan", font=SMALL_FONT_BUTTON, fg_color="#C850C0",
                                  hover_color="#4185D0", height=30,width=80,command=self.on_click_vegan)
        self._btn_vegan.place(x=300, y=450,anchor='center')
        self._btn_halal=CTkButton(master=self._home,text="Halal", font=SMALL_FONT_BUTTON, fg_color="#C850C0",
                                  hover_color="#4185D0",  height=30,width=80,command=self.on_click_halal)
        self._btn_halal.place(x=215, y=485,anchor='center')
        self._btn_kosher=CTkButton(master=self._home,text="Kosher", font=SMALL_FONT_BUTTON,fg_color="#C850C0",
                                   hover_color="#4185D0",height=30,width=80,command=self.on_click_kosher)
        self._btn_kosher.place(x=215, y=450,anchor='center')

        self._food_types=CTkOptionMenu(master=self._home,values=["general","salad","dessert","sandwich","fried","soup","Grilled","baked"])
        self._food_types.place(x=85,y=465,anchor='center')

        self._btn_add=CTkButton(master=self._home,text="Add",font=("Calibri",17), fg_color="#C850C0",
                                hover_color="#4185D0", height=30, width=80, command=self.on_click_add)
        self._btn_add.place(x=100,y=60)
        self._btn_clear = CTkButton(master=self._home, height=30, width=80, text="Clear", fg_color="#C850C0",
                                    hover_color="#4185D0", font=("Arial",17),command=self.on_click_delete_all_btn)
        self._btn_clear.place(x=190,y=60)

        self._main_ingredients_label=CTkLabel(master=self._home,text="Main", font=('Calibri',30, "underline"))
        self._main_ingredients_label.place(x=15, y=52)

        self._btn_sign_out = CTkButton(master=self._home, text="Sign out", font=("Calibri", 17), fg_color="#C850C0",
                                       hover_color="#4185D0", height=30, width=80, command=self.on_click_sign_out)
        self._btn_sign_out.place(x=915, y=10)

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
        try:
            write_to_log("got here to disconnect")
            if self._ingredients:
                self._ingredients.clear_frames()
            if self._refrigerator:
                self._refrigerator.clear_frames()
            self.forget_all_frames()
            self.on_click_destroy_specific_frame()
            self._not_logged_in_home.pack(fill="both",expand=True)
            self.on_click_reset()
            self.update_default_greeting()
            self._username = ""
            self._client_bl.user_data={}
        except Exception as e: #remove again
            write_to_log(e)
            pass

    def forget_all_frames(self):
        write_to_log("got to gorget all frames")
        for child in self._container.winfo_children():
                write_to_log(child)
                child.pack_forget()

    def on_click_refrigerator(self):
        def send_ingredient(cmd, data):
            self._client_bl.send_data(cmd, data)
        def receive_confirmation():
            msg = self._client_bl.receive_msg()
            msg=json.loads(msg)
            write_to_log(msg)
            return Codes[msg["code"]]
        self._home.pack_forget()
        if not self._refrigerator:
            self._refrigerator=Refrigerator(self._container,self._home,send_ingredient,receive_confirmation,self._client_bl.update_user_info,self._client_bl.user_data)
            self._refrigerator.create_ui()
        else:
            self._refrigerator.initiate_existing_ui(self._client_bl.user_data)

    def on_click_categorize(self,ingredient,ingredient_frame):
        self.on_click_destroy_specific_frame()
        self._specific_frame = DraggableFrame(self._home)
        self._specific_frame.place(x=225,y=55)
        scrollable_frame=CTkScrollableFrame(master=self._specific_frame,width=250,height=320,corner_radius=15
                                            ,border_color="blue",border_width=3)
        scrollable_frame.pack()
        ingredient_name = CTkLabel(master=scrollable_frame, text=ingredient, font=("Calibri", 20, "bold"))
        ingredient_name.pack(padx=(2, 2), pady=2)
        btn_back = CTkButton(scrollable_frame, text="Back", height=30, width=80, text_color="white",hover_color="#4185D0",
                             font=("Calibri", 17), fg_color="#C850C0",command=self.on_click_destroy_specific_frame)
        btn_back.pack(padx=(160,2),pady=2)
        t=threading.Thread(target=lambda: self.initiate_list_frame(scrollable_frame,ingredient,ingredient_frame),daemon=True)
        t.start()
        self._specific_frame.bind_drag_widget(self._specific_frame)


    def initiate_list_frame(self,scrollable_frame,ingredient,ingredient_frame):
        for i in self._client_bl.user_data.keys():
            if i == "Main":
                continue
            current_frame = CTkFrame(master=scrollable_frame, width=80, height=40, corner_radius=28, fg_color="#5B5FD9")
            current_frame.pack(pady=3, padx=5, fill="x", anchor='w', )
            current_entry = CTkEntry(master=current_frame)
            current_entry.place(x=5, y=7)
            current_entry.insert(0, i)
            current_entry.configure(state="disabled")
            current_select_btn = CTkButton(master=current_frame, width=50, height=25, text="Select",
                                           text_color="#5B5FD9",
                                           fg_color="black", font=("Arial", 18),
                                           command=lambda entry=current_entry,frame=ingredient_frame: self.on_click_select(ingredient, entry.get(),frame))
            current_select_btn.place(x=150, y=7)

    def on_click_select(self,ingredient,dst_list,ingredient_frame):
        data=self._client_bl.user_data["Main"]
        write_to_log(f"first: {data}")
        cmd="TRANSFER"
        args=["Main",dst_list,ingredient]
        write_to_log(args)
        self._client_bl.send_data(cmd,args)
        msg = self._client_bl.receive_msg()
        msg = json.loads(msg)
        write_to_log(msg)
        if Codes[msg["code"]]=="ok":
            self.on_click_destroy_specific_frame()
            ingredient_frame.destroy()
            write_to_log(self._client_bl.user_data["Main"])
            write_to_log(ingredient)
            self._client_bl.update_user_info(cmd,args)


    def on_click_destroy_specific_frame(self):
        if self._specific_frame:
            self._specific_frame.after(0, self._specific_frame.destroy)
            self._specific_frame = None

    def on_click_make(self):
        #only send data if client is connected maybe simply make btn disabled for furture
        self._client_bl.add_food_type_parameters(self._food_types.get())
        if not self._client_status.connected or not  self._client_status.signed_in or self._ingredients.is_editing():
            return
        cmd="MAKE"
        args=self._client_bl.get_parameters(self._time_slider.get())
        self._client_bl.send_data(cmd,args)
        self._home.pack_forget()
        if not self._recipes:
            self._recipes=Recipes(self._container,self._home,self._client_status,self._client_bl.receive_msg)
            self._recipes.create_ui()
        else:
            self._recipes.initiate_existing_ui()

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
            #also create different functions for switching frames and send them so there is a clean switching IMPORTANT (kinda did it having a problem with cleaning entry FIXED I'M DA GOAT)
        self._not_logged_in_home.pack_forget()
        #create only one login class that will hold user username and password for later use.
        if not self._sign_in:
            self._sign_in=SignIn(self._container,self._home,self._not_logged_in_home,self._client_status,on_click_sign_in,on_click_register)
            self._sign_in.create_ui()
        else:
            self._sign_in.initiate_existing_ui()

    def on_click_sign_out(self):
        self._client_status.signed_in=False
        self.initiate_disconnected_home()
        self._client_bl.send_data("SIGN_OUT","")

    def update_refrigerator_state(self,state):
        self._btn_refrigerator.after(100, lambda: self._btn_refrigerator.configure(state=state,image=self._btn_refrigerator.cget("image"),fg_color= self._btn_refrigerator.cget("fg_color")))
        if state == "disabled":
            self._btn_refrigerator.unbind('<Motion>')
        else:
            self._btn_refrigerator.bind('<Motion>', lambda event: self._btn_refrigerator.configure(
                image=self.opened_refrigerator_image), add='+')
        self._btn_refrigerator.event_generate("<Motion>")
    def initiate_signed_in(self):
        self._home.pack(fill="both",expand=True)
        def send_ingredient(cmd,data):
            self._client_bl.send_data(cmd,data)
        def receive_confirmation():
            msg = self._client_bl.receive_msg()
            msg=json.loads(msg)
            write_to_log(msg)
            return Codes[msg["code"]]
        def update_buttons(state):
            self._btn_add.configure(state=state)
            self._btn_make.configure(state=state)
            self.update_refrigerator_state(state)

        if not self._ingredients:
            self._ingredients = Ingredient("Main",self._home,send_ingredient, receive_confirmation,
                                           update_buttons,self.on_click_categorize,self._client_bl.update_user_info,width=270,height=300,
                                           fg_color="#1E1E2E",border_width=2,border_color="#3A3F8F")
            self._ingredients.set_internal_ingredient_look(width=80,height=40,corner_radius=28,fg_color="#5B5FD9")
            self._ingredients.place(x=5, y=100)
        self._btn_add.configure(state='disabled')
        self._btn_clear.configure(state='disabled')
        self.receive_user_data()
        self.initiate_first_ingredients()

        self.update_greeting()
        self.on_click_reset()

    def receive_user_data(self):
        data=self._client_bl.receive_msg()
        data=json.loads(data)
        self._client_bl.user_data=data

    def on_click_delete_all_btn(self):
        return #this is temp doesn't work
        self._client_bl.send_data("DELETE_ALL","")
        succeed=bool(self._client_bl.receive_msg())
        if succeed:
            self._ingredients.clear_frames()
            self._btn_add.configure(state="normal")

    def initiate_first_ingredients(self):
        t = threading.Thread(target=lambda: self._ingredients.initiate_first_ingredients(self._client_bl.user_data), daemon=True)
        t.start()

    #do a function of update_greeting instead (it will update auto not return str)
    def update_greeting(self):
        day_time=get_time_greeting()
        name=self._username
        self._greeting.configure(text=f"{day_time} {name}.")

    def update_default_greeting(self):
        day_time=get_time_greeting()
        self._default_greeting.configure(text=f"{day_time} guest.")

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
