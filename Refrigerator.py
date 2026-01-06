from Protocol import *

class Refrigerator:
    def __init__(self,container,home_window):
        self._refrigerator_window=None
        self._container=container
        self._home_window=home_window
        self._btn_back=None

    def create_ui(self):
        self._refrigerator_window=CTkFrame(self._container, )
        self._refrigerator_window.pack(fill="both",expand=True)
        self._btn_back = CTkButton(self._refrigerator_window, text="Back", height=30, width=80, text_color="white",hover_color="#4185D0", font=("Calibri", 17), fg_color="#C850C0",command=self.on_click_back)
        self._btn_back.place(x=915, y=10)

    def on_click_back(self):
        self._refrigerator_window.pack_forget()
        self._home_window.pack(fill="both", expand=True)

#have 5 lists that user can orgenize to:
#Spices & Seasonings
#Liquids
#Cooking & baking Basics
#Sauces & Condiments
#Extras



