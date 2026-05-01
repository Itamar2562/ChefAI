from Protocol import *
from WidgetUtils import Lists, Ingredients,CategorizeListFrame,ErrorFrame
from customtkinter import *
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


    def create_ui(self):
        self.pack(fill="both",expand=True)
        self._btn_back = CTkButton(self, text="Back", height=30, width=80, text_color="white",
                                   hover_color="#6A3DB4", font=("Calibri", 17), fg_color="#7C4CC2",
                                   command=self.on_click_back)
        self._btn_back.place(x=915, y=10)

        self._add_list_btn=CTkButton(master=self, text="create list", font=("Calibri",17),
                                     fg_color="#7C4CC2", hover_color="#6A3DB4", height=36, corner_radius=10,
                                     command=self.on_click_add_list)
        self._add_list_btn.place(x=155,y=35)

        self._categories_label = CTkLabel(master=self, text="Categories", font=('Calibri', 50, "bold", "underline"),
                                          text_color="#5B5FD9")
        self._categories_label.place(x=502, y=25, anchor="center")
        self._list=Lists(self, self._callback_send_data, self.receive_confirmation_code,
                         self._callback_update_user_info, self.open_list, self.close_list,
                         self.update_list_buttons, self.destroy_categorize_frame,
                         width=350, height=410, fg_color="#232338", border_width=2, border_color="#4A50C8")

        self._list.set_internal_frame_look(width = 3, height = 52, corner_radius = 14, fg_color ="#2F337A",
                                           border_width = 1, border_color ="#6B70FF")
        self._list.configure_inner_frame(170,40,40,40)
        self._list.place(x=10,y=73)
        no_lists_text = CTkLabel(master=self,
                                 text="You don’t have any opened lists.\nCreate or open an existing one to organize and"
                                      " categorize your ingredients.", font=("Segoe UI", 20, "bold"), wraplength=300)
        no_lists_text.place(x=500,y=200)
        lists_name=CTkLabel(master=self, text="My lists", font=("Segoe UI", 22, "bold"))
        lists_name.place(x=35,y=40)
        self.after(200, self._list.initiate_first_lists,self._client_data)

    def initiate_existing_ui(self, data):
        self.pack(fill="both", expand=True)
        self.update_idletasks()
        self._client_data = data
        self.close_list()
        self.after(200, self._list.initiate_first_lists, self._client_data)


    def update_list_buttons(self, state):
        self._add_list_btn.configure(state=state)

    def on_click_add_list(self):
        self._list.add_list()
        self._list.move_down()


    def on_click_back(self):
        self.clear_all_lists()
        self.close_list()
        self.forget_error_frame()
        self.pack_forget()
        self._callback_home_window()

    def clear_all_lists(self):
        if self._list:
            self._list.clear_frames()
        if self._ingredient_list:
            self._ingredient_list.clear_frames()


    def receive_confirmation_code(self):
        msg = self._callback_receive_data(need_json=True)
        if msg["code"]!="200":
            self.create_error_specific_frame(msg['message'])
        return msg["code"]


    def on_click_categorize(self, ingredient, ingredient_frame,list_name):
        self.destroy_categorize_frame()
        if not self._categorize_lists_frame:
            self._categorize_lists_frame = CategorizeListFrame(self, ingredient, ingredient_frame, list_name,
                                                               self.destroy_categorize_frame, self.forget_error_frame,
                                                               self.on_click_select)
        self._categorize_lists_frame.place(x=350, y=55)
        data = list(self._client_data.keys())
        self.after(50, self._categorize_lists_frame.initiate_categorize_list_frame, data)

    def destroy_categorize_frame(self,name=""):
        if self._categorize_lists_frame:
            if name == "":
                self._categorize_lists_frame.destroy_categorize_frame()
                self._categorize_lists_frame = None
            else:
                if name == self._categorize_lists_frame.get_ingredient_name():
                    self._categorize_lists_frame.destroy_categorize_frame()
                    self._categorize_lists_frame = None

    def on_click_select(self, ingredient, dst_list, ingredient_frame):
        self._categorize_lists_frame.stop_animating()
        src_list = self._ingredient_list.get_name()
        cmd = "TRANSFER"
        args = pack_transfer_data(src_list, dst_list, ingredient)
        self._callback_send_data(cmd, args)
        msg = self._callback_receive_data(need_json=True)
        self.destroy_categorize_frame()
        if msg["code"] == "200":
            ingredient_frame.destroy()
            self._callback_update_user_info(cmd, args)
        else:
            self.create_error_specific_frame(msg['message'])

    def create_error_specific_frame(self, message):
        if not self._error_frame:  # create frame if it doesn't exists
            self._error_frame = ErrorFrame(message, master=self, fg_color="#3b0d0d", border_color="#ff4d4d",
                                           border_width=2, corner_radius=12)
        else:  # otherwise change the displayed error
            self._error_frame.change_text(message)
        self._error_frame.plan_future_hide()  # reset after timer
        self._error_frame.lift()
        self._error_frame.place(x=500, y=250, anchor='center')


    def forget_error_frame(self):
        if self._error_frame:
            self._error_frame.forget_frame()

    def update_ingredient_buttons(self,state):
        self._btn_add_ingredient.configure(state=state)
        self._btn_clear_ingredients.configure(state=state)

    def on_click_add_ingredient(self):
        self._ingredient_list.add_ingredient()
        self._ingredient_list.move_down()

    def on_click_clear_ingredients(self):
        name=self._ingredient_list.get_name()
        args = pack_list_data(name)
        self._callback_send_data("CLEAR_LIST", args)
        msg = self._callback_receive_data(need_json=True)
        if msg["code"] == "200":
            self._ingredient_list.clear_frames()
            self.destroy_categorize_frame()
            self._btn_add_ingredient.configure(state="normal")
            self._callback_update_user_info("CLEAR_LIST", args)
        else:
            self.create_error_specific_frame(msg['message'])

    def close_list(self, list_name=""):
        if not self._ingredient_list:
            return
        if list_name != "" and self._ingredient_list.get_name() != list_name:  # remove specific list
            return
        self.destroy_categorize_frame()
        self._ingredient_list.clear_frames()
        self._ingredient_list.change_name("")
        self._ingredient_list.place_forget()
        if self._list_name_label:
            self._list_name_label.place_forget()
        if self._btn_add_ingredient:
            self._btn_add_ingredient.place_forget()
        if self._btn_clear_ingredients:
            self._btn_clear_ingredients.place_forget()

    def open_list(self,list_name):
        self.destroy_categorize_frame()
        if not self._ingredient_list:
          self.create_ingredient_list(list_name)
        else:
            self._ingredient_list.clear_frames()
            self.place_existing_ingredient_list(list_name)
        self.after(200, self._ingredient_list.initiate_first_ingredients, self._client_data)

    def place_existing_ingredient_list(self,list_name):
        self._ingredient_list.change_name(list_name)
        self._ingredient_list.place(x=425, y=108)
        self._btn_add_ingredient.place(x=430, y=75)
        self._btn_clear_ingredients.place(x=515, y=75)
        self._list_name_label.place(x=600, y=90, anchor='w')
        self._list_name_label.configure(text=self._ingredient_list.get_name())


    def create_ingredient_list(self,list_name):
        self._ingredient_list = Ingredients(list_name, self, self._callback_send_data,
                                            self.receive_confirmation_code, self.update_ingredient_buttons,
                                            self.on_click_categorize,
                                            self._callback_update_user_info,
                                            self.destroy_categorize_frame, width=500, height=375,
                                            fg_color="#1E1E2E",
                                            border_width=2, border_color="#3A3F8F")
        self._ingredient_list.set_internal_frame_look(width=80, height=40, corner_radius=28, fg_color="#5B5FD9")
        self._ingredient_list.configure_inner_frame(350, 28, 30, 30)
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
                                                    command=self.on_click_clear_ingredients)

        self._btn_clear_ingredients.place(x=515, y=75)
        if not self._list_name_label:
            self._list_name_label = CTkLabel(master=self,
                                             font=('Calibri', 25, "underline"),text=self._ingredient_list.get_name())
        self._list_name_label.place(x=600, y=90, anchor='w')





