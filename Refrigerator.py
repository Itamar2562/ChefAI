from Protocol import *
from WidgetUtils import DynamicList, Ingredient


#IDEAS
#make this more dynamic by allowing the user to add his own lists up to 4 lists
#user can name/edit names and delete lists with 2 options delete completly or just the list with ingredients going back to main list that will be stored internally and categorize his own ingredients. if
#defaults: Produce, dairy & protein , Other
#send it as (list_id,current_ingr,prev)

#first make the system of orgenzing by id and only then think about letting user change cus that can be difficult
class Refrigerator:
    def __init__(self,container,home_window,callback_send_data,callback_receive_confirmation,callback_update_user_info,user_data):
        self._refrigerator_window=None
        self._container=container
        self._home_window=home_window
        self._client_data= user_data
        self._btn_back=None
        self._callback_send_data=callback_send_data
        self._callback_receive_confirmation=callback_receive_confirmation
        self.callback_update_user_info=callback_update_user_info
        self._new_user=False
        self._add_list_btn=None
        self.ingredient_list=None
        self.btn_add_ingredient=None
        self.list_name_label=None
        self._list=None

    def create_ui(self):
        self._refrigerator_window=CTkFrame(self._container, )
        self._refrigerator_window.pack(fill="both",expand=True)
        self._btn_back = CTkButton(self._refrigerator_window, text="Back", height=30, width=80, text_color="white",state="disabled",
                                   hover_color="#4185D0", font=("Calibri", 17), fg_color="#C850C0",command=self.on_click_back)
        self._btn_back.place(x=915, y=10)

        self._add_list_btn=CTkButton(master=self._refrigerator_window,text="add",font=("Calibri",17),state="disabled",
                                     fg_color="#C850C0",hover_color="#4185D0", height=30, width=80,command=self.on_click_add)
        self._add_list_btn.place(x=100,y=50)


        self._list=DynamicList(self._refrigerator_window,self._callback_send_data,self._callback_receive_confirmation,
                               self.callback_update_user_info,self.open_list,self.close_list,
                               self.update_buttons,
                               width=330,height=300,fg_color="#232338",border_width=2,border_color="#4A50C8")

        self._list.set_internal_ingredient_look( width = 260, height = 52, corner_radius = 14,  fg_color = "#2F337A" , border_width = 1,border_color = "#6B70FF")
        self._list.place(x=20,y=100)
        self.initiate_first_lists()
        for list_name in self._client_data.keys():
            if list_name!="Main":
                self._list.after(0,self.open_list,list_name)
                break


        # self._cooking_and_baking_list=Ingredients(self._refrigerator_window,self._client_status,self._callback_send_data,self._callback_receive_confirmation,self.update_add_cooking_and_baking_btn,width=270,height=300,fg_color="#1E1E2E",border_width=2,border_color="#3A3F8F")
        # self._sauces_list=Ingredients(self._refrigerator_window,self._client_status,self._callback_send_data,self._callback_receive_confirmation,self.update_add_sauces_btn,width=270,height=300,fg_color="#1E1E2E",border_width=2,border_color="#3A3F8F")
        # self._extras_list=Ingredients(self._refrigerator_window,self._client_status,self._callback_send_data,self._callback_receive_confirmation,self.update_add_extras_btn,width=270,height=300,fg_color="#1E1E2E",border_width=2,border_color="#3A3F8F")
    def initiate_existing_ui(self,data):
        self._refrigerator_window.pack(fill="both",expand=True)
        self._client_data=data
        if self._new_user:
            self._new_user=False
            self.initiate_first_lists()
        self.close_list()
        write_to_log(self._client_data.keys())
        lists=self._list.get_lists()
        for list_name in lists:
                self.open_list(list_name)
                break

    def update_buttons(self,state):
        self._add_list_btn.configure(state=state)
        if self.ingredient_list and not self.ingredient_list.is_animating():
            self._btn_back.configure(state=state)

    def on_click_add(self):
        self._list.add_list()
        self._list.move_down()

    def clear_frames(self):
        self._list.clear_frames()
        self._new_user=True

    def initiate_first_lists(self):
        t = threading.Thread(target=lambda: self._list.initiate_first_lists(self._client_data),daemon=True)
        t.start()


    def on_click_back(self):
        if self.ingredient_list and self.ingredient_list.is_animating():
            return
        self._refrigerator_window.pack_forget()
        self._home_window.pack(fill="both", expand=True)

    def on_click_categorize(self, ingredient, ingredient_frame):
        pass
        # self.on_click_destroy_specific_frame()
        # self._specific_frame = DraggableFrame(self._home)
        # self._specific_frame.place(x=125, y=55)
        # scrollable_frame = CTkScrollableFrame(master=self._specific_frame, width=250, height=320, corner_radius=15
        #                                       , border_color="blue", border_width=3)
        # scrollable_frame.pack()
        # btn_back = CTkButton(scrollable_frame, text="Back", height=30, width=80, text_color="white",
        #                      hover_color="#4185D0",
        #                      font=("Calibri", 17), fg_color="#C850C0", command=self.on_click_destroy_specific_frame)
        # btn_back.pack(padx=(160, 2), pady=2)
        # t = threading.Thread(target=lambda: self.initiate_list_frame(scrollable_frame, ingredient, ingredient_frame),
        #                      daemon=True)
        # t.start()
        # self._specific_frame.bind_drag_widget(self._specific_frame)
    def close_list(self,list_name=""):
        write_to_log("closed list")
        if not self.ingredient_list:
            return
        if list_name!="" and self.ingredient_list.get_name()!=list_name: #remove specific list
            return
        self.ingredient_list.remove()
        self.ingredient_list=None
        if self.list_name_label:
            self.list_name_label.after(0,self.list_name_label.destroy)
            self.list_name_label=None
        if self.btn_add_ingredient:
            self.btn_add_ingredient.after(0,self.btn_add_ingredient.destroy)
            self.btn_add_ingredient=None

    def rename_list(self):
        pass


    def open_list(self,list_name):
        def update_buttons(state):
            self.btn_add_ingredient.configure(state=state)
            if not self._list.is_animating():
                self._btn_back.configure(state=state)

        def on_click_add_ingredient():
            self.ingredient_list.add_ingredient()
            self.ingredient_list.move_down()

        write_to_log(f"opened: {list_name}")
        if not self.ingredient_list:
            self.ingredient_list = Ingredient(list_name, self._refrigerator_window, self._callback_send_data,
                                              self._callback_receive_confirmation, update_buttons,self.on_click_categorize,
                                              self.callback_update_user_info, width=270, height=300,fg_color="#1E1E2E",
                                              border_width=2, border_color="#3A3F8F")
            self.ingredient_list.set_internal_ingredient_look(width=80, height=40, corner_radius=28, fg_color="#5B5FD9")
        else:
            if self.ingredient_list.is_animating():
                return
            self.ingredient_list.clear_frames()
            self.ingredient_list.change_name(list_name)
        self.ingredient_list.place(x=500, y=100)

        if not self.btn_add_ingredient:
            self.btn_add_ingredient = CTkButton(master=self._refrigerator_window, text="add", font=("Calibri", 17),
                                                fg_color="#C850C0"
                                                , hover_color="#4185D0", height=30, width=80,
                                                command=on_click_add_ingredient)
        self.btn_add_ingredient.place(x=700,y=65)
        if not self.list_name_label:
            self.list_name_label = CTkLabel(master=self._refrigerator_window,
                                            font=('Calibri',30, "underline"))
        self.list_name_label.configure(text=self.ingredient_list.get_name())
        self.list_name_label.place(x=500,y=60)
        t = threading.Thread(target=lambda:  self.ingredient_list.initiate_first_ingredients(self._client_data), daemon=True)
        t.start()


#have 5 lists that user can orgenize to:
#Spices & Seasonings
#Liquids
#Cooking & baking Basics
#Sauces & Condiments
#Extras



