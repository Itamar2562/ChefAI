from customtkinter import *
from ClientBL import *
from WidgetUtils import Ingredients, CategorizeListFrame, ErrorFrame
from Login import SignIn
from Recipes import Recipes
from Refrigerator import Refrigerator
import threading
from PIL import Image


SMALL_FONT_BUTTON=("Calibri",12)

BTN_NORMAL_FG_COLOR="#7C4CC2"
BTN_NORMAL_HOVER_COLOR="#6A3DB4"
BTN_NORMAL_TEXT_COLOR="white"
BTN_DISABLED_FG_COLOR="#9E7AD1"
BTN_DISABLED_TEXT_COLOR="#bbbfbf"

class ClientGUI:
    def __init__(self,ip,port):
        self._root=CTk()
        self._client_bl=ClientBL(ip,port)

        self._root.title("Client GUI")
        set_appearance_mode("dark")
        self._root.geometry(f'{SCREEN_WIDTH}x{SCREEN_HEIGHT}')
        self._root.resizable(False, False)

        self._container = CTkFrame(self._root)
        self._container.pack(fill="both",expand=True)

        self._chef_ai_headline_label=None
        self._signed_out_chef_ai_headline_label=None
        self._home=None
        self._not_logged_in_home=None
        self._greeting_label=None
        self._not_logged_in_greeting_label=None

        self._btn_vegetarian=None
        self._btn_vegan=None
        self._btn_halal=None
        self._btn_kosher=None
        self._food_types=None
        self._difficulties_options_menu=None
        self._btn_reset=None
        self._time_slider=None
        self._cooking_time_label=None

        self._username=""
        self._sign_in = None
        self._register=None
        self._btn_login=None
        self._btn_sign_out=None

        self._btn_make=None
        self._card_frame=None
        self.chef_hat_image=CTkImage(Image.open(r"Images/chef_hat.png"),size=(150,150))
        self._chef_icon_label=None

        self._btn_add=None
        self._btn_clear=None
        self._main_ingredients_label=None

        self._error_frame=None

        self._categorize_lists_frame = None

        self._ingredients=None

        self._closed_refrigerator_image=CTkImage(Image.open(r"Images/closed_refrigerator.PNG"), size=(300, 400))
        self._opened_refrigerator_image=CTkImage(Image.open(r"Images/opened_refrigerator.png"), size=(295, 395))
        self._refrigerator=None
        self._btn_refrigerator=None

        self._recipes=None

        self._connection = threading.Thread(target=self.connect_on_startup, daemon=True)
        self._connection.start()
        self._connection_status=[False]

        self.create_not_signed_in_ui()

    def connect_on_startup(self):
        connected_text = CTkLabel(master=self._root, text="Not connected", font=('Calibri', 22), fg_color="#333333")
        connected_text.place(x=5, y=500)
        was_connected = False
        while True:
            if not self._connection_status[0]:
                connected_text.configure(text="Not connected", text_color="red")
                if was_connected:
                    self.initiate_disconnected_home()
                    was_connected = False
                self._connection_status[0] = self._client_bl.connect()
            else:
                connected_text.configure(text="connected", text_color="green")
                was_connected = True
                self._connection_status[0] = self._client_bl.check_connection()

    def create_not_signed_in_ui(self):
        self._not_logged_in_home = CTkFrame(master=self._container)
        self._not_logged_in_home.pack(fill="both", expand=True)

        self._btn_login = CTkButton(master=self._not_logged_in_home, text="Login", font=("Calibri", 17),
                                    fg_color="#7C4CC2", hover_color="#6A3DB4",
                                    height=30, width=80, command=self.on_click_login)
        self._btn_login.place(x=915, y=10)
        # I will change greeting
        self._not_logged_in_greeting_label = CTkLabel(master=self._not_logged_in_home, font=('Roboto', 20), anchor='w',
                                                      text="Hi Guest!")
        self._not_logged_in_greeting_label.place(x=5, y=0)
        self._signed_out_chef_ai_headline_label = CTkLabel(master=self._not_logged_in_home, text="ChefAI",
                                                           font=('Calibri', 220, "bold", "underline"),
                                                           text_color="#5B5FD9")
        self._signed_out_chef_ai_headline_label.place(x=502, y=200, anchor="center")

    def create_signed_in_ui(self):
        self._home=CTkFrame(master=self._container)
        self._home.pack(fill="both", expand=True)
        #logged in frame
        self._chef_ai_headline_label = CTkLabel(master=self._home, text="ChefAI", font=('Calibri', 50, "bold", "underline"),
                                                text_color="#5B5FD9")
        self._chef_ai_headline_label.place(x=502, y=25, anchor="center")

        self._greeting_label = CTkLabel(master=self._home, font=('Roboto', 20), anchor='w')
        self._greeting_label.place(x=5, y=0)

        self._card_frame = CTkFrame(self._home, width=360, height=320, corner_radius=24, fg_color="#1E1E2E",
                                    border_width=2, border_color="#3A3F8F")
        self._card_frame.place(x=502, y=250, anchor='center')

        self._chef_icon_label=CTkLabel(master=self._card_frame, text="", image=self.chef_hat_image)
        self._chef_icon_label.place(x=180, y=100, anchor='center')

        self._btn_make =CTkButton(self._card_frame,
                                  text=f"MAKE!✨  Remaining: {self._client_bl.get_user_data_ai_remaining_usage()}",
                                  font=("Segoe UI", 25, "bold"), width=300,
                                  height=80, corner_radius=28, fg_color="#5B5FD9", hover_color="#6F74FF",
                                  text_color="#E6E8FF", command=self.on_click_make)
        remaining=self._client_bl.get_user_data_ai_remaining_usage()
        self.configure_make_button_state(remaining)
        self._btn_make.place(x=180,y=225,anchor='center')
        self._btn_refrigerator=CTkButton(master=self._home, text="", image=self._closed_refrigerator_image,
                                         fg_color="transparent",
                                         bg_color="transparent", hover=False, command=self.on_click_refrigerator)
        self._btn_refrigerator.bind('<Motion>',
                                    lambda event:self._btn_refrigerator.configure(image=self._opened_refrigerator_image),
                                    add='+')
        self._btn_refrigerator.bind('<Leave>',
                                    lambda event:self._btn_refrigerator.configure(image=self._closed_refrigerator_image),
                                    add='+')
        self._btn_refrigerator.place(x=860, y=275, anchor="center")

        self._time_slider = CTkSlider(master=self._home,from_=10,to=120,orientation="horizontal",width=300,
                                      number_of_steps=22,command=self.change_slider_time)
        self._time_slider.set(60)
        self._time_slider.place(x=502,y=465,anchor='center')

        self._cooking_time_label=CTkLabel(master=self._home, text="Cooking time: 60.0min", text_color="white",
                                          font=("Calibri",20))
        self._cooking_time_label.place(x=502, y=440, anchor='center')

        #parameters buttons
        self._btn_reset=CTkButton(master=self._home,text="Reset", font=SMALL_FONT_BUTTON, fg_color="#7C4CC2",
                                  hover_color="#6A3DB4", height=30,width=80,command=self.on_click_reset)
        self._btn_reset.place(x=502,y=490,anchor='center')
        self._btn_vegetarian=CTkButton(master=self._home,text="Vegetarian",
                                       font=SMALL_FONT_BUTTON,fg_color=BTN_NORMAL_FG_COLOR,
                                  text_color=BTN_NORMAL_TEXT_COLOR,
                                       hover_color="#6A3DB4", height=30,width=80,command=self.on_click_vegetarian)
        self._btn_vegetarian.place(x=300,y=485,anchor='center')
        self._btn_vegan=CTkButton(master=self._home,text="Vegan", font=SMALL_FONT_BUTTON,fg_color=BTN_NORMAL_FG_COLOR,
                                  text_color=BTN_NORMAL_TEXT_COLOR,
                                  hover_color="#6A3DB4", height=30,width=80,command=self.on_click_vegan)
        self._btn_vegan.place(x=300, y=450,anchor='center')
        self._btn_halal=CTkButton(master=self._home,text="Halal", font=SMALL_FONT_BUTTON,fg_color=BTN_NORMAL_FG_COLOR,
                                  text_color=BTN_NORMAL_TEXT_COLOR,
                                  hover_color="#6A3DB4",  height=30,width=80,command=self.on_click_halal)
        self._btn_halal.place(x=215, y=485,anchor='center')
        self._btn_kosher=CTkButton(master=self._home,text="Kosher", font=SMALL_FONT_BUTTON,fg_color=BTN_NORMAL_FG_COLOR,
                                  text_color=BTN_NORMAL_TEXT_COLOR,
                                   hover_color="#6A3DB4",height=30,width=80,command= self.on_click_kosher)
        self._btn_kosher.place(x=215, y=450,anchor='center')

        self._food_types=CTkOptionMenu(master=self._home,
                                       values=["General","Salad","Dessert","Sandwich","Fried","Soup","Grilled","Baked"])
        self._food_types.place(x=85,y=485,anchor='center')

        self._difficulties_options_menu=CTkOptionMenu(master=self._home, values=["All", "Easy", "Medium", "Hard", "Very hard"])
        self._difficulties_options_menu.place(x=85, y=450, anchor='center')


        self._btn_add=CTkButton(master=self._home,text="Add",font=("Calibri",17), fg_color="#7C4CC2",
                                hover_color="#6A3DB4", height=30, width=80, command=self.on_click_add,state="disabled")
        self._btn_add.place(x=100,y=60)
        self._btn_clear = CTkButton(master=self._home, height=30, width=80, text="Clear", fg_color="#7C4CC2",
                                    hover_color="#6A3DB4", font=("Arial",17),
                                    command=self.on_click_clear_btn, state="disabled")
        self._btn_clear.place(x=190,y=60)

        self._main_ingredients_label=CTkLabel(master=self._home,text="Main", font=('Calibri',30, "underline"))
        self._main_ingredients_label.place(x=15, y=52)

        self._btn_sign_out = CTkButton(master=self._home, text="Sign out", font=("Calibri", 17), fg_color="#7C4CC2",
                                       hover_color="#6A3DB4", height=30, width=80, command=self.on_click_sign_out)
        self._btn_sign_out.place(x=915, y=10)
        self.initiate_signed_in()

    def initiate_signed_in(self):
        self._home.pack(fill="both",expand=True)
        def receive_confirmation():
            msg = self._client_bl.receive_msg(need_json=True)
            if msg["code"]=="409" or msg["code"]=="500":
                self.create_error_specific_frame(msg['message'])
            return msg["code"]
        if not self._ingredients:
            self._ingredients = Ingredients("Main", self._home, self._client_bl.send_data, receive_confirmation,
                                            self.update_buttons, self.on_click_categorize,
                                            self._client_bl.update_user_info,
                                            self.destroy_categorize_frame, width=270, height=300,
                                            fg_color="#1E1E2E", border_width=2, border_color="#3A3F8F")
            self._ingredients.set_internal_frame_look(width=80, height=40, corner_radius=28, fg_color="#5B5FD9")
            self._ingredients.place(x=5, y=100)
        self.update_greeting()
        user_data_lists=self._client_bl.get_user_data_lists()
        self._home.after(300, self._ingredients.initiate_first_ingredients,user_data_lists)

    def initiate_disconnected_home(self):
        self._username = ""
        self._not_logged_in_home.pack(fill="both",expand=True)
        self._client_bl.delete_all_user_data()
        self.delete_all_frames()

    def delete_all_frames(self):
        if self._refrigerator:
            self._root.after(0, self._refrigerator.destroy)
            self._refrigerator=None
        if self._sign_in:
            self._root.after(0, self._sign_in.destroy)
            self._sign_in = None
        if self._register:
            self._root.after(0, self._register.destroy)
            self._register = None
        if self._recipes:
            self._root.after(0, self._recipes.destroy)
            self._recipes = None
        if self._home:
            self._root.after(0,self._home.destroy)
            self._home=None
        self._ingredients=None
        self.destroy_categorize_frame()
        self._error_frame=None

    def forget_home(self):
        self._home.pack_forget()
        if self._ingredients:
            self._ingredients.clear_frames()
        self.destroy_categorize_frame()
        self.forget_error_frame()

    def initiate_existing_home(self):
        self._ingredients.clear_frames()
        self._home.pack(fill="both",expand=True)
        self._home.update()
        user_data_lists=self._client_bl.get_user_data_lists()
        self._home.after(300,self._ingredients.initiate_first_ingredients,user_data_lists)

    def on_click_login(self):
        def on_click_sign_in(data):
            cmd="SIGNIN"
            self._client_bl.send_data(cmd,data)
            msg=self._client_bl.receive_msg(need_json=True)
            self._sign_in.show_message(msg["message"])
            if msg["code"] == "200":
                user_data=msg["data"]
                self._client_bl.set_user_data(user_data)
                self._username=self._sign_in.get_username()
                self.schedule_usage_refresh(user_data["seconds_reset"])
                self._sign_in.pack_forget()
                if not self._home:
                    self.create_signed_in_ui()
                else:
                    self.initiate_existing_home()

        def on_click_register(data):
            self._register = self._sign_in.get_register()
            cmd="REG"
            self._client_bl.send_data(cmd,data)
            msg = self._client_bl.receive_msg(need_json=True)
            self._register.print_message(msg["message"], msg['code'])

        self._not_logged_in_home.pack_forget()
        if not self._sign_in:
            self._sign_in=SignIn(self._container,self._not_logged_in_home,
                                 self._connection_status,on_click_sign_in,on_click_register)
            self._sign_in.create_ui()
        else:
            self._sign_in.initiate_existing_ui()

    def on_click_sign_out(self):
        self._client_bl.send_data("SIGN_OUT","")
        self.initiate_disconnected_home()

    def update_buttons(self, state):
        self._btn_add.configure(state=state)
        self._btn_clear.configure(state=state)

    def on_click_clear_btn(self):
        args= pack_list_data("Main")
        self._client_bl.send_data("CLEAR_LIST", args)
        msg=self._client_bl.receive_msg(need_json=True)
        if msg['code']=="200":
            self._ingredients.clear_frames()
            self.destroy_categorize_frame()
            self._btn_add.configure(state="normal")
            self._client_bl.update_user_info("CLEAR_LIST",args)
        else:
            self.create_error_specific_frame(msg['message'])

    def on_click_add(self):
        self._ingredients.add_ingredient()
        self._ingredients.move_down()

    def on_click_categorize(self, ingredient, ingredient_frame,list_name):
        self.destroy_categorize_frame()
        self._categorize_lists_frame = CategorizeListFrame(self._home, ingredient, ingredient_frame, list_name,
                                                           self.destroy_categorize_frame, self.forget_error_frame,
                                                           self.on_click_select)
        self._categorize_lists_frame.place(x=350, y=55)
        user_data_lists=self._client_bl.get_user_data_lists()
        data=list(user_data_lists.keys())
        self._home.after(50, self._categorize_lists_frame.initiate_categorize_list_frame, data)

    def destroy_categorize_frame(self,name=""):
        if self._categorize_lists_frame:
            if name=="":
                self._categorize_lists_frame.destroy_categorize_frame()
                self._categorize_lists_frame = None
            else:
                if name==self._categorize_lists_frame.get_ingredient_name():
                    self._categorize_lists_frame.destroy_categorize_frame()
                    self._categorize_lists_frame = None

    def on_click_select(self,ingredient,dst_list,ingredient_frame):
        cmd="TRANSFER"
        args=pack_transfer_data("Main",dst_list,ingredient)
        self._client_bl.send_data(cmd,args)
        msg = self._client_bl.receive_msg(need_json=True)
        self.destroy_categorize_frame()
        if msg["code"]=="200":
            ingredient_frame.destroy()
            self._client_bl.update_user_info(cmd,args)
        else:
            self.create_error_specific_frame(msg["message"])

    def create_error_specific_frame(self,message):
        if not self._error_frame: #create frame if it doesn't exists
            self._error_frame=ErrorFrame(message,master=self._home, fg_color="#3b0d0d", border_color="#ff4d4d",
                                            border_width=2,corner_radius=12)
        else: #otherwise change the displayed error
            self._error_frame.change_text(message)
        self._error_frame.plan_future_hide() # reset after timer
        self._error_frame.place(x=500, y=250,anchor='center')

    def forget_error_frame(self):
        if self._error_frame:
            self._error_frame.forget_frame()


    def on_click_make(self):
        self._client_bl.add_food_type_parameter(self._food_types.get())
        self._client_bl.add_difficulty_parameter(self._difficulties_options_menu.get())
        cmd="MAKE"
        args=self._client_bl.get_parameters(self._time_slider.get())
        self._client_bl.send_data(cmd,args)
        self.destroy_categorize_frame()
        self.forget_home()
        if not self._recipes:
            self._recipes=Recipes(self._container,self.initiate_existing_home,self._client_bl.receive_msg,
                                  self.configure_make_button_state)
            self._recipes.create_ui()
        else:
            self._recipes.initiate_existing_ui()

    def schedule_usage_refresh(self,seconds):
        self._root.after(int(seconds*1000), self.refresh_usage)

    def refresh_usage(self):
        msg = self._client_bl.get_ai_usage_remaining_data_from_server()
        data = msg["data"]
        if msg["code"]=="200":
            remaining=data["remaining"]
            self.configure_make_button_state(remaining)
        self.schedule_usage_refresh(data["seconds_reset"])  # schedule next midnight

    def configure_make_button_state(self, remaining):
        state = "normal" if remaining > 0 else "disabled"
        self._client_bl.set_user_data_ai_remaining_usage(remaining)
        if self._btn_make:
            (self._btn_make.configure(
                text=f"MAKE!✨ Remaining: {remaining}",state=state,width=300,height=80,corner_radius=28))

    def on_click_refrigerator(self):
        self.forget_home()
        self.destroy_categorize_frame()
        user_data_lists=self._client_bl.get_user_data_lists()
        if not self._refrigerator:
            self._refrigerator = Refrigerator(self._container, self.initiate_existing_home,
                                              self._client_bl.send_data, self._client_bl.receive_msg,
                                              self._client_bl.update_user_info, user_data_lists)
            self._refrigerator.create_ui()
        else:
            self._refrigerator.initiate_existing_ui(user_data_lists)

    def update_greeting(self):
        name=self._username
        self._greeting_label.configure(text=f"Hi {name}!")

    def on_click_reset(self):
        def reset_button(button):
            button.configure(fg_color=BTN_NORMAL_FG_COLOR, hover=True, text_color=BTN_NORMAL_TEXT_COLOR)
        reset_button(self._btn_vegetarian)
        reset_button(self._btn_vegan)
        reset_button(self._btn_halal)
        reset_button(self._btn_kosher)
        self._time_slider.set(60)
        self._food_types.set('General')
        self._difficulties_options_menu.set('All')
        self._cooking_time_label.configure(text="Cooking time: 60.0min")
        self._client_bl.reset_parameters()

    def switch_btn_state_color(self, button):
        fg_color=button.cget('fg_color')
        if fg_color==BTN_NORMAL_FG_COLOR:
            button.configure(fg_color=BTN_DISABLED_FG_COLOR,hover=False,text_color=BTN_DISABLED_TEXT_COLOR)
        else:
            button.configure(fg_color=BTN_NORMAL_FG_COLOR,hover=True,text_color=BTN_NORMAL_TEXT_COLOR)

    def on_click_vegetarian(self):
        self.switch_btn_state_color(self._btn_vegetarian)
        self._client_bl.add_preference_parameters("vegetarian")
    def on_click_vegan(self):
        self.switch_btn_state_color(self._btn_vegan)
        self._client_bl.add_preference_parameters("vegan")
    def on_click_halal(self):
        self.switch_btn_state_color(self._btn_halal)
        self._client_bl.add_preference_parameters("halal")
    def on_click_kosher(self):
        self.switch_btn_state_color(self._btn_kosher)
        self._client_bl.add_preference_parameters("kosher")

    def change_slider_time(self,value):
        self._cooking_time_label.configure(text=f"Cooking time: {value}min")

    def run(self):
        self._root.mainloop()

if __name__=='__main__':
   Client=ClientGUI(CLIENT_IP,PORT)
   Client.run()
