from Protocol import *
from WidgetUtils import DynamicList

#IDEAS
#make this more dynamic by allowing the user to add his own lists up to 4 lists
#user can name/edit names and delete lists with 2 options delete completly or just the list with ingredients going back to main list that will be stored internally and categorize his own ingredients. if
#defaults: Produce, dairy & protein , Other
#send it as (list_id,current_ingr,prev)

#first make the system of orgenzing by id and only then think about letting user change cus that can be difficult
class Refrigerator:
    def __init__(self,container,home_window,client_status,callback_send_data,callback_receive_confirmation):
        self._refrigerator_window=None
        self._container=container
        self._home_window=home_window
        self._client_status=client_status
        self._btn_back=None
        self._callback_send_data=callback_send_data
        self._callback_receive_confirmation=callback_receive_confirmation
        self._new_user=False
        self._add_list_btn=None

        self._list=None

    def create_ui(self):
        self._refrigerator_window=CTkFrame(self._container, )
        self._refrigerator_window.pack(fill="both",expand=True)
        self._btn_back = CTkButton(self._refrigerator_window, text="Back", height=30, width=80, text_color="white",hover_color="#4185D0", font=("Calibri", 17), fg_color="#C850C0",command=self.on_click_back)
        self._btn_back.place(x=915, y=10)

        self._add_list_btn=CTkButton(master=self._refrigerator_window,text="add",font=("Calibri",17), fg_color="#C850C0",hover_color="#4185D0", height=30, width=80,command=self.on_click_add)
        self._add_list_btn.place(x=100,y=50)


        self._list=DynamicList(self._refrigerator_window,self._client_status,self._callback_send_data,self._callback_receive_confirmation,self.update_add_btn,width=270,height=300,fg_color="#1E1E2E",border_width=2,border_color="#3A3F8F")
        self._list.set_internal_ingredient_look(width=80,height=40,corner_radius=28,fg_color="#5B5FD9")
        self._list.place(x=5,y=100)

        t = threading.Thread(target=self.initiate_first_lists, daemon=True)
        t.start()

        # self._cooking_and_baking_list=Ingredients(self._refrigerator_window,self._client_status,self._callback_send_data,self._callback_receive_confirmation,self.update_add_cooking_and_baking_btn,width=270,height=300,fg_color="#1E1E2E",border_width=2,border_color="#3A3F8F")
        # self._sauces_list=Ingredients(self._refrigerator_window,self._client_status,self._callback_send_data,self._callback_receive_confirmation,self.update_add_sauces_btn,width=270,height=300,fg_color="#1E1E2E",border_width=2,border_color="#3A3F8F")
        # self._extras_list=Ingredients(self._refrigerator_window,self._client_status,self._callback_send_data,self._callback_receive_confirmation,self.update_add_extras_btn,width=270,height=300,fg_color="#1E1E2E",border_width=2,border_color="#3A3F8F")

    def initiate_existing_ui(self,data):
        self._refrigerator_window.pack(fill="both",expand=True)
        self._client_status.data=data
        if self._new_user:
            self._new_user=False
            t = threading.Thread(target=self.initiate_first_lists, daemon=True)
            t.start()
    def update_add_btn(self,state):
        self._add_list_btn.configure(state=state)

    def on_click_add(self):
        self._list.add_list()
        self._list.move_down()

    def clear_frames(self):
        self._list.clear_frames()
        self._new_user=True
        self._client_status.data=None

    def initiate_first_lists(self):
        for i in  self._client_status.data.keys():
            try:
                write_to_log(i)
                if i=="Main":
                    continue
                if self._client_status.connected and self._client_status.signed_in:
                    self._list.initiate_first_lists(i)
                    time.sleep(0.05)
            except: #if user decided to exit while adding
                return
        self._add_list_btn.configure(state="normal")
        #self._btn_clear.configure(state="normal") not yet

    def on_click_back(self):
        self._refrigerator_window.pack_forget()
        self._home_window.pack(fill="both", expand=True)

#have 5 lists that user can orgenize to:
#Spices & Seasonings
#Liquids
#Cooking & baking Basics
#Sauces & Condiments
#Extras



