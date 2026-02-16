import time

from Protocol import *
from WidgetUtils import DynamicList, Ingredients


#IDEAS
#make this more dynamic by allowing the user to add his own lists up to 4 lists
#user can name/edit names and delete lists with 2 options delete completly or just the list with ingredients going back to main list that will be stored internally and categorize his own ingredients. if
#defaults: Produce, dairy & protein , Other
#send it as (list_id,current_ingr,prev)

#first make the system of orgenzing by id and only then think about letting user change cus that can be difficult
class Refrigerator:
    def __init__(self,container,callback_home_window,callback_send_data,callback_receive_confirmation,callback_update_user_info,user_data):
        self._refrigerator_window=None
        self._container=container
        self._callback_home_window=callback_home_window
        self._client_data= user_data
        self._btn_back=None
        self._callback_send_data=callback_send_data
        self._callback_receive_confirmation=callback_receive_confirmation
        self.callback_update_user_info=callback_update_user_info
        self._add_list_btn=None
        self.ingredient_list=None
        self.btn_add_ingredient=None
        self.btn_clear_ingredients=None
        self.list_name_label=None
        self.categories_label=None
        self._list=None
        self._categorize_lists_frame = None
        self.no_lists_text=None

        self._schedule_categorize_list=None

        self._error_frame=None
        self._error_text=None
        self._error_icon_label=None
        self._schedule_hide_error_frame=None
        self._error_icon=CTkImage(Image.open(r"Images/ErrorIcon.png"),size=(30,30))

    def create_ui(self):
        self._refrigerator_window=CTkFrame(self._container, )
        self._refrigerator_window.pack(fill="both",expand=True)
        self._btn_back = CTkButton(self._refrigerator_window, text="Back", height=30, width=80, text_color="white",state="disabled",
                                   hover_color="#4185D0", font=("Calibri", 17), fg_color="#C850C0",command=self.on_click_back)
        self._btn_back.place(x=915, y=10)

        self._add_list_btn=CTkButton(master=self._refrigerator_window,text="create list",font=("Calibri",17),
                                     fg_color="#C850C0",hover_color="#4185D0", height=30, width=80,command=self.on_click_add)
        self._add_list_btn.place(x=100,y=65)

        self.categories_label = CTkLabel(master=self._refrigerator_window, text="Categories", font=('Calibri', 50, "bold", "underline"),
                                text_color="#5B5FD9")
        self.categories_label.place(x=502, y=25, anchor="center")
        self._list=DynamicList(self._refrigerator_window, self._callback_send_data, self.receive_list_confirmation_code,
                               self.callback_update_user_info, self.open_list, self.close_list,
                               self.update_buttons, self.destroy_categorize_lists_frame,self.update_back,
                               width=330, height=330, fg_color="#232338", border_width=2, border_color="#4A50C8")

        self.no_lists_text=CTkLabel(master=self._refrigerator_window,
                               text="You don’t have any opened lists.\nCreate or open an existing one to organizing and "
                                    "categorizing your ingredients.",font=("Segoe UI",20, "bold"),wraplength=300)
        self._list.set_internal_frame_look(width = 260, height = 52, corner_radius = 14, fg_color ="#2F337A", border_width = 1, border_color ="#6B70FF")
        self._list.place(x=20,y=100)
        time.sleep(0.05)
        self.initiate_first_lists()
        write_to_log(f"lists {self._client_data.keys()}")
        for list_name in self._client_data.keys():
            if list_name!="Main":
                self._list.after(0,self.open_list,list_name)
                break
        self.no_lists_text.place(x=500,y=200)

    def clear_all_frames(self):
        self._list.clear_frames()
        if self.ingredient_list:
            self.ingredient_list.clear_frames()
        if self._error_frame:
            self._error_frame.after(0,self._error_frame.destroy)
            self._error_frame=None

    def initiate_existing_ui(self,data):
        self._refrigerator_window.pack(fill="both",expand=True)
        time.sleep(0.05)
        self._client_data=data
        self.initiate_first_lists()
        self.close_list()
        for list_name in self._client_data.keys():
            if list_name !="Main":
                self.open_list(list_name)
                break

    def update_buttons(self,state):
        self._add_list_btn.configure(state=state)

    def update_back(self,state):
        if (self.ingredient_list and (self.ingredient_list.is_animating() or self._list.is_animating()) or
                (self.ingredient_list is None and self._list.is_animating())):
            return
        else:
            self._btn_back.configure(state=state)

    def on_click_add(self):
        self._list.add_list()
        self._list.move_down()


    def initiate_first_lists(self):
        t = threading.Thread(target=lambda: self._list.initiate_first_lists(self._client_data),daemon=True)
        t.start()

    def create_error_specific_frame(self, ingredient="", curr_list="", code=""):
        def _hide():
            self._schedule_hide_error_frame = None
            if self._error_frame:
                self._error_frame.place_forget()

        if not self._error_frame:
            self._error_frame = CTkFrame(self._refrigerator_window, fg_color="#3b0d0d", border_color="#ff4d4d", border_width=2,
                                         corner_radius=12)
            self._error_icon_label = CTkLabel(master=self._error_frame, text="", image=self._error_icon)
            self._error_text = CTkLabel(master=self._error_frame,
                                        font=("Segoe UI", 20, "bold"))
        if not self._error_frame.winfo_ismapped():
            self._error_frame.place(x=325, y=200)
            self._error_frame.lift()
        self._error_icon_label.pack(side="left",padx=5,pady=20)
        text=self.create_error_text(curr_list,ingredient,code)
        self._error_text.configure(text=text)
        self._error_text.pack(side="left",padx=5,pady=20)
        if self._schedule_hide_error_frame is not None:
            self._error_frame.after_cancel(self._schedule_hide_error_frame)
        self._schedule_hide_error_frame = self._error_frame.after(1200, _hide)

    def create_error_text(self,dst_list,ingredient,code):
        if ingredient!="":
            if code == "409":
                text = f"Ingredient: {ingredient} already in list: {dst_list}"
            else:
                text = f"Server error with ingredient: {ingredient} and list: {dst_list}"
        else:
            if code=="409":
                text=f"list {dst_list} already exists"
            else:
                text=f"server error with list {dst_list}"
        return text




    def on_click_back(self):
        self.stop_animating()
        self._refrigerator_window.pack_forget()
        self.clear_all_frames()
        self._callback_home_window()

    def on_click_categorize(self, ingredient, ingredient_frame):
        self.destroy_categorize_lists_frame()
        if not self._categorize_lists_frame:
            self._categorize_lists_frame = CTkFrame(self._refrigerator_window)
        self._categorize_lists_frame.place(x=350, y=55)
        self._categorize_lists_frame.lift()
        scrollable_frame = CTkScrollableFrame(master=self._categorize_lists_frame, width=250, height=320,
                                              corner_radius=15
                                              , border_color="blue", border_width=3)
        scrollable_frame.pack()
        ingredient_name = CTkLabel(master=scrollable_frame, text=ingredient, font=("Calibri", 30, "bold", "underline"),
                                   wraplength=150)
        ingredient_name.pack(padx=(0, 100), pady=2)
        btn_back = CTkButton(scrollable_frame, text="Back", height=30, width=80, text_color="white",
                             hover_color="#4185D0",
                             font=("Calibri", 17), fg_color="#C850C0", command=self.forget_categorize_lists_frame)
        btn_back.place(relx=1.0, x=-10, y=5, anchor="ne")
        self.initiate_categorize_list_frame(scrollable_frame, ingredient, ingredient_frame)
        # t = threading.Thread(
        #     target=lambda: self.initiate_categorize_list_frame(scrollable_frame,
        #                                                        ingredient, ingredient_frame), daemon=True)
        # t.start()


    def start_animating(self):
        if self.ingredient_list:
            self.ingredient_list.set_animating(True)
    def stop_animating(self):
        if self.ingredient_list:
            self.ingredient_list.set_animating(False)
        if self._schedule_categorize_list:
            self._categorize_lists_frame.after_cancel(self._schedule_categorize_list)
            self._schedule_categorize_list=None

    def initiate_categorize_list_frame(self, scrollable_frame, ingredient, ingredient_frame):
        try:
            def create_frames(i,data):
                if i >=len(data):
                    self.stop_animating()
                    return
                if not (self.ingredient_list and self.ingredient_list.get_name() == data[i]):
                    current_frame = CTkFrame(master=scrollable_frame, width=80, height=40, corner_radius=28,
                                             fg_color="#5B5FD9")
                    current_frame.pack(pady=3, padx=5, fill="x", anchor='w', )
                    current_entry = CTkEntry(master=current_frame)
                    current_entry.place(x=5, y=7)
                    current_entry.insert(0, data[i])
                    current_entry.configure(state="disabled")
                    current_select_btn = CTkButton(master=current_frame, width=50, height=25, text="Select",
                                                   text_color="#5B5FD9",
                                                   fg_color="black", font=("Arial", 18),
                                                   command=lambda entry=current_entry,
                                                                  frame=ingredient_frame: self.on_click_select(
                                                       ingredient, entry.get(), frame))
                    current_select_btn.place(x=150, y=7)
                self._schedule_categorize_list=self._categorize_lists_frame.after(20, lambda: create_frames(i + 1,data))
            self.start_animating()
            list_client_data=list(self._client_data.keys())
            create_frames(0,list_client_data)
        except Exception as e:  # error hereds
            self.stop_animating()
            write_to_log(e)


    def on_click_select(self, ingredient, dst_list, ingredient_frame):
        self.stop_animating()
        src_list=self.ingredient_list.get_name()
        cmd = "TRANSFER"
        args = [src_list, dst_list, ingredient]
        self._callback_send_data(cmd, args)
        msg =self._callback_receive_confirmation()
        self.forget_categorize_lists_frame()
        if msg["code"] == "200":
            ingredient_frame.destroy()
            self.callback_update_user_info(cmd, args)
        elif msg["code"]=="409" or msg["code"]=="500":
            data=msg["massage"]
            self.create_error_specific_frame(data["ingredient"],data["destination"],msg["code"])

    def receive_list_confirmation_code(self):
        msg = self._callback_receive_confirmation()
        data = msg["massage"]
        if msg["code"] == "409" or msg["code"] == "500":
            self.create_error_specific_frame("",data["list"][1], msg["code"])
        return msg['code']


    def destroy_categorize_lists_frame(self):
        self.stop_animating()
        if self._categorize_lists_frame:
            self._categorize_lists_frame.after(0, self._categorize_lists_frame.destroy)
            self._categorize_lists_frame = None

    def forget_categorize_lists_frame(self):
        self.stop_animating()
        if self._categorize_lists_frame:
            self._categorize_lists_frame.after(0, self._categorize_lists_frame.place_forget)

    def destroy_error_frame(self):
        if self._error_frame:
            self._error_frame.after(0, self._error_frame.destroy)
            self._schedule_hide_error_frame = None

    def close_list(self,list_name=""):
        if not self.ingredient_list:
            return
        if list_name!="" and self.ingredient_list.get_name()!=list_name: #remove specific list
            return
        self.destroy_categorize_lists_frame()
        self.ingredient_list.remove()
        self.ingredient_list=None
        if self.list_name_label:
            self.list_name_label.after(0,self.list_name_label.destroy)
            self.list_name_label=None
        if self.btn_add_ingredient:
            self.btn_add_ingredient.after(0,self.btn_add_ingredient.destroy)
            self.btn_add_ingredient=None
        if self.btn_clear_ingredients:
            self.btn_clear_ingredients.after(0, self.btn_clear_ingredients.destroy)
            self.btn_clear_ingredients = None


    def clear_cached_user_data(self):
        self._client_data={}

    def update_ingredient_buttons(self,state):
        self.btn_add_ingredient.configure(state=state)
        self.btn_clear_ingredients.configure(state=state)

    def on_click_add_ingredient(self):
        self.ingredient_list.add_ingredient()
        self.ingredient_list.move_down()

    def receive_confirmation(self):
        msg = self._callback_receive_confirmation()
        data = msg["massage"]
        if msg["code"] == "409" or msg["code"] == "500":
            self.create_error_specific_frame(data["ingredient"][2], data["list"], msg["code"])
        return msg["code"]

    def on_click_clear_ingredients(self,name):
        args = [name]
        self._callback_send_data("DELETE_ALL", args)
        msg = self._callback_receive_confirmation()
        if msg["code"] == "200":
            self.ingredient_list.clear_frames()
            self.destroy_categorize_lists_frame()
            self.btn_add_ingredient.configure(state="normal")
            self.callback_update_user_info("DELETE_ALL", args)

    def open_list(self,list_name):
        self.destroy_categorize_lists_frame()
        if not self.ingredient_list:
            self.ingredient_list = Ingredients(list_name, self._refrigerator_window, self._callback_send_data,
                                              self.receive_confirmation, self.update_ingredient_buttons,
                                               self.on_click_categorize,
                                               self.callback_update_user_info,
                                               self.destroy_categorize_lists_frame,self.update_back,
                                               width=270, height=300, fg_color="#1E1E2E",
                                               border_width=2, border_color="#3A3F8F")
            self.ingredient_list.set_internal_frame_look(width=80, height=40, corner_radius=28, fg_color="#5B5FD9")
        else:
            if self.ingredient_list.is_animating():
                return
            self.ingredient_list.clear_frames()
            self.ingredient_list.change_name(list_name)
        self.ingredient_list.place(x=500, y=125)

        if not self.btn_add_ingredient:
            self.btn_add_ingredient = CTkButton(master=self._refrigerator_window, text="add", font=("Calibri", 17),
                                                fg_color="#C850C0"
                                                , hover_color="#4185D0", height=30, width=80,
                                                command=self.on_click_add_ingredient)
        self.btn_add_ingredient.place(x=560,y=90)
        if not self.btn_clear_ingredients:
            self.btn_clear_ingredients = CTkButton(master=self._refrigerator_window, text="clear", font=("Calibri", 17),
                                                fg_color="#C850C0"
                                                , hover_color="#4185D0", height=30, width=80,
                                                command= lambda name=self.ingredient_list.get_name(): self.on_click_clear_ingredients(name))
        else:
            self.btn_clear_ingredients.configure(command= lambda name=self.ingredient_list.get_name(): self.on_click_clear_ingredients(name))
        self.btn_clear_ingredients.place(x=650, y=90)
        if not self.list_name_label:
            self.list_name_label = CTkLabel(master=self._refrigerator_window,
                                            font=('Calibri',25, "underline"))
        self.list_name_label.configure(text=self.ingredient_list.get_name())
        self.list_name_label.place(x=640,y=70,anchor='center')
        t = threading.Thread(target=lambda:  self.ingredient_list.initiate_first_ingredients(self._client_data), daemon=True)
        t.start()


#have 5 lists that user can orgenize to:
#Spices & Seasonings
#Liquids
#Cooking & baking Basics
#Sauces & Condiments
#Extras



