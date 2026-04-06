from Protocol import *
from WidgetUtils import DynamicList, Ingredients,CategorizeListFrame
from PIL import Image

class Refrigerator(CTkFrame):
    def __init__(self,container,callback_home_window,callback_send_data,callback_receive_data,
                 callback_update_user_info,user_data):
        super().__init__(master=container)
        self._container=container
        self._callback_home_window=callback_home_window
        self._client_data= user_data
        self._btn_back=None

        self._callback_send_data=callback_send_data
        self._callback_receive_data=callback_receive_data
        self._callback_update_user_info=callback_update_user_info

        self._add_list_btn=None
        self._list=None

        self._ingredient_list=None
        self._btn_add_ingredient=None
        self._btn_clear_ingredients=None
        self._list_name_label=None
        self._categories_label=None
        self._categorize_lists_frame = None


        self._schedule_categorize_list=None

        self._error_frame=None
        self._error_text=None
        self._error_icon_label=None
        self._schedule_hide_error_frame=None
        self._error_icon=CTkImage(Image.open(r"Images/ErrorIcon.png"),size=(30,30))

    def create_ui(self):
        self.pack(fill="both",expand=True)
        self._btn_back = CTkButton(self, text="Back", height=30, width=80, text_color="white",
                                   hover_color="#6A3DB4", font=("Calibri", 17), fg_color="#7C4CC2",
                                   command=self.on_click_back)
        self._btn_back.place(x=915, y=10)

        self._add_list_btn=CTkButton(master=self,text="create list",font=("Calibri",17),
                                     fg_color="#7C4CC2",hover_color="#6A3DB4",height=36,corner_radius=10,
                                     command=self.on_click_add)
        self._add_list_btn.place(x=150,y=35)

        self._categories_label = CTkLabel(master=self, text="Categories", font=('Calibri', 50, "bold", "underline"),
                                          text_color="#5B5FD9")
        self._categories_label.place(x=502, y=25, anchor="center")
        self._list=DynamicList(self, self._callback_send_data, self.receive_list_confirmation_code,
                               self._callback_update_user_info, self.open_list, self.close_list,
                               self.update_list_buttons, self.destroy_categorize_frame,
                               width=350, height=410, fg_color="#232338", border_width=2, border_color="#4A50C8")

        self._list.set_internal_frame_look(width = 3, height = 52, corner_radius = 14, fg_color ="#2F337A",
                                           border_width = 1, border_color ="#6B70FF")
        self._list.configure_inner_frame(170,40,40,40)
        self._list.place(x=10,y=73)
        no_lists_text = CTkLabel(master=self,
                                 text="You don’t have any opened lists.\nCreate or open an existing one to organize and"
                                      "categorize your ingredients.", font=("Segoe UI", 20, "bold"), wraplength=300)
        no_lists_text.place(x=500,y=200)
        lists_name=CTkLabel(master=self, text="My lists", font=("Segoe UI", 20, "bold"))
        lists_name.place(x=35,y=40)
        self.after(200, self._list.initiate_first_lists,self._client_data)

    def clear_all_frames(self):
        self._list.clear_frames()
        if self._ingredient_list:
            self._ingredient_list.clear_frames()
        if self._error_frame:
            self._error_frame.after(0,self._error_frame.destroy)
            self._error_frame=None

    def initiate_existing_ui(self,data):
        self.pack(fill="both",expand=True)
        self.block_animations(False)
        self.update_idletasks()
        self._client_data=data
        self.close_list()
        self.after(200, self._list.initiate_first_lists,self._client_data)

    def update_list_buttons(self, state):
        self._add_list_btn.configure(state=state)

    def on_click_add(self):
        self._list.add_list()
        self._list.move_down()


    def create_error_specific_frame(self, message):
        def _hide():
            self._schedule_hide_error_frame = None
            if self._error_frame:
                self._error_frame.place_forget()

        if not self._error_frame:
            self._error_frame = CTkFrame(self, fg_color="#3b0d0d", border_color="#ff4d4d", border_width=2,
                                         corner_radius=12)
            self._error_icon_label = CTkLabel(master=self._error_frame, text="", image=self._error_icon)
            self._error_text = CTkLabel(master=self._error_frame,
                                        font=("Segoe UI", 20, "bold"))
        self._error_frame.place(x=500, y=250,anchor='center')
        self._error_frame.lift()
        self._error_icon_label.pack(side="left", padx=5, pady=20)
        self._error_text.configure(text=message)
        self._error_text.pack(side="left", padx=5, pady=20)
        if self._schedule_hide_error_frame is not None:
            self.after_cancel(self._schedule_hide_error_frame)
        self._schedule_hide_error_frame = self.after(1200, _hide)



    def on_click_back(self):
        self.stop_all_animations()
        self.block_animations(True)
        self.pack_forget()
        self.clear_all_frames()
        self._callback_home_window()

    def on_click_categorize(self, ingredient, ingredient_frame,list_name):
        self.destroy_categorize_frame()
        if not self._categorize_lists_frame:
            self._categorize_lists_frame = CategorizeListFrame(self, ingredient, ingredient_frame,list_name,
                                                               self.destroy_categorize_frame, self.destroy_error_frame,
                                                               self.on_click_select)
        self._categorize_lists_frame.place(x=350, y=55)
        data = list(self._client_data.keys())
        self.after(50, self._categorize_lists_frame.initiate_categorize_list_frame, data)

    def start_animating(self):
        if self._ingredient_list:
            self._ingredient_list.set_animating(True)
        self.destroy_error_frame()

    def stop_all_animations(self):
        if self._ingredient_list:
            self._ingredient_list.stop_animating()
        if self._categorize_lists_frame:
            self._categorize_lists_frame.stop_animating()
        if self._list:
            self._list.stop_animating()

    def block_animations(self,state):
        self._list.can_animation_start(not state)
        if self._categorize_lists_frame:
            self._categorize_lists_frame.can_animation_start(not state)
        if self._ingredient_list:
            self._ingredient_list.can_animation_start(not state)



    def on_click_select(self, ingredient, dst_list, ingredient_frame):
        self.stop_all_animations()
        src_list=self._ingredient_list.get_name()
        cmd = "TRANSFER"
        args=pack_transfer_data(src_list,dst_list,ingredient)
        self._callback_send_data(cmd, args)
        msg =self._callback_receive_data(need_json=True)
        #self.forget_categorize_lists_frame()
        self.destroy_categorize_frame()
        if msg["code"] == "200":
            ingredient_frame.destroy()
            self._callback_update_user_info(cmd, args)
        else:
            self.create_error_specific_frame(msg['message'])

    def receive_list_confirmation_code(self):
        msg = self._callback_receive_data(need_json=True)
        if msg['code']!="200":
            self.create_error_specific_frame(msg['message'])
        return msg['code']

    def destroy_categorize_frame(self):
        if self._categorize_lists_frame and self._categorize_lists_frame.winfo_exists():
            self._categorize_lists_frame.destroy_categorize_frame()
            self._categorize_lists_frame=None

    def destroy_error_frame(self):
        if self._error_frame:
            self.after(0, self._error_frame.destroy)
            self._error_frame=None
        if self._schedule_hide_error_frame:
            self.after_cancel(self._schedule_hide_error_frame)
            self._schedule_hide_error_frame=None

    def close_list(self,list_name=""):
        if not self._ingredient_list:
            return
        if list_name!="" and self._ingredient_list.get_name()!=list_name: #remove specific list
            return
        self.destroy_categorize_frame()
        self._ingredient_list.remove()
        self._ingredient_list=None
        if self._list_name_label:
            self._list_name_label.after(0, self._list_name_label.destroy)
            self._list_name_label=None
        if self._btn_add_ingredient:
            self._btn_add_ingredient.after(0, self._btn_add_ingredient.destroy)
            self._btn_add_ingredient=None
        if self._btn_clear_ingredients:
            self._btn_clear_ingredients.after(0, self._btn_clear_ingredients.destroy)
            self._btn_clear_ingredients = None


    def clear_cached_user_data(self):
        self._client_data={}

    def update_ingredient_buttons(self,state):
        self._btn_add_ingredient.configure(state=state)
        self._btn_clear_ingredients.configure(state=state)

    def on_click_add_ingredient(self):
        self._ingredient_list.add_ingredient()
        self._ingredient_list.move_down()

    def receive_confirmation(self):
        msg = self._callback_receive_data(need_json=True)
        if msg["code"]!="200":
            self.create_error_specific_frame(msg['message'])
        return msg["code"]

    def on_click_clear_ingredients(self,name):
        args = pack_list_data(name)
        self._callback_send_data("CLEAR_LIST", args)
        msg = self._callback_receive_data(need_json=True)
        if msg["code"] == "200":
            self._ingredient_list.clear_frames()
            self.destroy_categorize_frame()
            self._btn_add_ingredient.configure(state="normal")
            self._callback_update_user_info("CLEAR_LIST", args)

    def open_list(self,list_name):
        self.destroy_categorize_frame()
        if not self._ingredient_list:
            self._ingredient_list = Ingredients(list_name, self, self._callback_send_data,
                                                self.receive_confirmation, self.update_ingredient_buttons,
                                                self.on_click_categorize,
                                                self._callback_update_user_info,
                                                self.destroy_categorize_frame, width=500, height=375, fg_color="#1E1E2E",
                                                border_width=2, border_color="#3A3F8F")
            self._ingredient_list.set_internal_frame_look(width=80, height=40, corner_radius=28, fg_color="#5B5FD9")
            self._ingredient_list.configure_inner_frame(350, 28, 30, 30)
        else:
            self._ingredient_list.clear_frames()
            self._ingredient_list.change_name(list_name)
        self._ingredient_list.place(x=425, y=108)

        if not self._btn_add_ingredient:
            self._btn_add_ingredient = CTkButton(master=self, text="add", font=("Calibri", 17),
                                                 fg_color="#7C4CC2"
                                                 , hover_color="#6A3DB4", height=30, width=80,
                                                 command=self.on_click_add_ingredient)
        self._btn_add_ingredient.place(x=430, y=75)
        if not self._btn_clear_ingredients:
            self._btn_clear_ingredients = CTkButton(master=self, text="clear", font=("Calibri", 17),
                                                    fg_color="#7C4CC2"
                                                    , hover_color="#6A3DB4", height=30, width=80,
                                                    command= lambda name=self._ingredient_list.get_name():
                                                self.on_click_clear_ingredients(name))
        else:
            self._btn_clear_ingredients.configure(
                command= lambda name=self._ingredient_list.get_name():self.on_click_clear_ingredients(name))
        self._btn_clear_ingredients.place(x=515, y=75)
        if not self._list_name_label:
            self._list_name_label = CTkLabel(master=self,
                                             font=('Calibri',25, "underline"))
        self._list_name_label.configure(text=self._ingredient_list.get_name())
        self._list_name_label.place(x=600, y=90, anchor='w')
        self.after(200, self._ingredient_list.initiate_first_ingredients, self._client_data)




