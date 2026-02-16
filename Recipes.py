import itertools
from Protocol import *

class Recipes:
    def __init__(self, container, home, client_statue,callback_receive_msg):
        self._container=container
        self._home_window=home
        self._recipes_main_window=None
        self._client_status=client_statue
        self._callback_receive_msg=callback_receive_msg
        self._recipes_scrollable_window=None
        self._received_massage=False
        self._loading_label=None
        self._headline=None
        self._btn_back=None
        self._threads=[]
        self._specific_frame=None
        self._temporary_frame=None

        self._error_icon=CTkImage(Image.open(r"Images/ErrorIcon.png"),size=(30,30))
        self._success_icon=CTkImage(Image.open(r"Images/success_icon.png"),size=(30,30))
        self._schedule_hide_temporary_frame=None
        self._icon_label=None
        self._temporary_text_label=None
        #badges
        #🏆 High Protein
        #
        # 🏆 Balanced Meal
        #
        # 🏆 Veggie Rich
        #
        # 🏆 Comforting


    #need to do existing ui
    def create_ui(self):
        self._recipes_main_window=CTkFrame(self._container, )
        self._recipes_main_window.pack(fill="both",expand=True)
        self._recipes_scrollable_window = CTkScrollableFrame(self._recipes_main_window,height=500,width=980)
        self._loading_label=CTkLabel(master=self._recipes_main_window, font=('Calibri', 100))
        self._headline=CTkLabel(master=self._recipes_main_window, text="Recipes",
                                font=('Calibri', 50,"bold","underline"), text_color="#5B5FD9")
        self._btn_back = CTkButton(self._recipes_main_window, text="Back", height=30, width=80, text_color="white",
                                   hover_color="#6A3DB4", font=("Calibri", 17), fg_color="#7C4CC2",
                                   command=self.on_click_back)
        t1=threading.Thread(target=self.animate, daemon=True)
        t1.start()
        t2=threading.Thread(target=self.receive_massage,daemon=True)
        t2.start()

    #return the scrollable frame in recieve massage
    def clear_recipes(self):
        for f in self._recipes_scrollable_window.winfo_children():
            f.after(0,f.destroy)
    def destroy(self):
        self._recipes_main_window.after(0,self._recipes_main_window.destroy)



    def create_recipes_frame(self):
        self._recipes_scrollable_window.place(x=0,y=60)
        self._headline.place(x=410,y=0)
        self._btn_back.place( x=920,y=10)

    def on_click_back(self):
        def on_click_yes():
            self.on_click_destroy_specific_frames()
            self.clear_recipes()
            self._recipes_main_window.pack_forget()
            self._home_window.pack(fill="both", expand=True)
        def on_click_no():
            self.on_click_destroy_specific_frames()
        self.on_click_destroy_specific_frames()
        self._specific_frame=CTkFrame(self._recipes_main_window,border_width=3,border_color="blue",height=200,width=300)
       # self._specific_frame=CTkFrame(master=self._recipes_main_window,border_width=3,border_color="blue",height=200,width=300)
        confirmation_label=CTkLabel(master=self._specific_frame,text="Are you sure?",font=('Calibri',25,"bold"))
        yes_btn=CTkButton(master=self._specific_frame,text="Yes",fg_color="cyan",height=30, width=80,text_color="black",command=on_click_yes)
        no_btn=CTkButton(master=self._specific_frame,text="No",fg_color="cyan",height=30, width=80,text_color="black",command=on_click_no)
        self._specific_frame.place(x=400,y=200)
        confirmation_label.pack(padx=20,pady=10)
        yes_btn.pack(padx=10,pady=10,side="left")
        no_btn.pack(padx=10,pady=10,side="left")

    def receive_massage(self):
        try:
            msg=self._callback_receive_msg(need_json=True)
            self._received_massage=True
            if msg[1]['name']=="no available recipes":
                self.create_error_frame()
                return
            self.create_recipes_frame()
            self.add_recipes(msg)
            bottom_spacer = CTkFrame(self._recipes_scrollable_window, height=65, fg_color="transparent")
            bottom_spacer.pack(fill="x")
        except:
            self.create_error_frame()


    def create_error_frame(self):
        self._headline.place(x=410, y=0)
        self._btn_back.place(x=920, y=10)
        error_text = CTkLabel(master=self._recipes_main_window,font=("Segoe UI", 35, "bold"),text="no recipes found!")
        error_text.place(x=350,y=250)
    def add_recipes(self,data):
        #create the frame
        for d in data:
            current_frame=CTkFrame(master=self._recipes_scrollable_window,width=200,height=100,border_width=3,border_color="blue",corner_radius=15)
            headline=CTkLabel(master=current_frame,text=d['name'], font=('Calibri',20,"bold","underline"),wraplength=800)
            description=CTkLabel(master=current_frame,text=d['description'],font=('Calibri',15),wraplength=500,justify="left",)
            difficulty_and_time=CTkLabel(master=current_frame,text=f"{d['difficulty']} • {d['time']} min",font=('Calibri',25))
            cook_btn=CTkButton(master=current_frame,text="Cook",fg_color="cyan",text_color="black",command=lambda user_data=d:self.on_click_cook(user_data))
            nutrition_btn=CTkButton(master=current_frame,text="Nutrition",fg_color="cyan",text_color="black", command=lambda user_data=d:self.on_click_nutrition(user_data))
            nutrition_btn.place(x=700,y=50)
            cook_btn.place(x=550,y=50)
            headline.place(x=5,y=5)
            description.place(x=5,y=35)
            difficulty_and_time.place(x=610,y=15)
            current_frame.pack(pady=10, padx=2, fill="x",)
            time.sleep(0.05)

    def on_click_cook(self,data):
        self.on_click_destroy_specific_frames()
        self._specific_frame=CTkFrame(self._recipes_main_window)
        #self._specific_frame = CTkFrame(master=self._recipes_main_window)
        self._specific_frame.place(x=125,y=55)
        scrollable_frame=CTkScrollableFrame(master=self._specific_frame,width=750,height=420,corner_radius=15,border_color="blue",border_width=3)
        scrollable_frame.pack()
        headline = CTkLabel(master=scrollable_frame, text=data['name'],font=('Calibri', 25, "bold", "underline"),wraplength=500)
        recipe_steps = CTkLabel(master=scrollable_frame, text=data['data'], justify="left",wraplength=750, font=('Calibri', 18),anchor='w')
        headline.pack(pady=20,padx=20)
        recipe_steps.pack(pady=10,padx=0,fill='x',anchor='w')
        btn_back = CTkButton(scrollable_frame, text="Back", height=30, width=80, text_color="white", hover_color="#6A3DB4", font=("Calibri", 17), fg_color="#7C4CC2", command=self.on_click_destroy_specific_frames)
        btn_back.place(relx=1.0, x=-10, y=0, anchor="ne")
        btn_save=CTkButton(scrollable_frame, text="Save", height=30, width=80, text_color="white",hover_color="#6A3DB4", font=("Calibri", 17), fg_color="#7C4CC2",command=lambda recipe=data: self.save_recipe(recipe))
        btn_save.place(relx=1.0, x=-10, y=40, anchor="ne")

    def on_click_nutrition(self,data):
        self.on_click_destroy_specific_frames()
        self._specific_frame=CTkFrame(self._recipes_main_window, width=750,border_width=3, border_color="blue")
        #self._specific_frame = CTkFrame(master=self._recipes_main_window, width=750,border_width=3, border_color="blue")
        headline = CTkLabel(master=self._specific_frame, text=data['name'],font=('Calibri', 25, "bold", "underline"),wraplength=500)
        nutrition = CTkLabel(master=self._specific_frame, text=data['nutrition'], justify="left", wraplength=730, font=('Calibri', 18))
        btn_back = CTkButton(self._specific_frame, text="Back", height=30, width=80, text_color="white",
                             hover_color="#6A3DB4", font=("Calibri", 17), fg_color="#7C4CC2", command=self.on_click_destroy_specific_frames)
        headline.pack(pady=20, padx=150)
        btn_back.place(relx=1.0, x=-10, y=10, anchor="ne")
        nutrition.pack(pady=10,padx=10,side="left")
        self._specific_frame.place(x=125, y=130)
        #self.configure_moving_frame()

    def save_recipe(self,data):
        code=save_to_pdf(data)
        if code=="200":
            self.create_temp_frame(True,"File saved successfully")
        elif code=="409":
            self.create_temp_frame(False,"File already exists")
        else:
            self.create_temp_frame(False,"File wasn't saved")

    def create_temp_frame(self,succeed,text):
        def _hide():
            self._schedule_hide_error_frame = None
            if self._temporary_frame:
             self._temporary_frame.place_forget()
        if not self._temporary_frame:
            self._temporary_frame = CTkFrame(self._recipes_main_window, fg_color="#3b0d0d", border_color="#ff4d4d", border_width=2,
                                         corner_radius=12)
            self._temporary_text_label = CTkLabel(master=self._temporary_frame,text=text,
                                    font=("Segoe UI", 20, "bold"))
            self._icon_label = CTkLabel(master=self._temporary_frame, text="", image=self._error_icon)
        if not succeed:
            self._temporary_frame.configure(fg_color="#3b0d0d", border_color="#ff4d4d")
            self._icon_label.configure(image=self._error_icon)
        else:
            self._temporary_frame.configure(fg_color="#0d1a0d",border_color="#4dff88")
            self._icon_label.configure(image=self._success_icon)

        self._temporary_text_label.configure(text=text)
        self._temporary_frame.place(x=400, y=200)
        self._temporary_frame.lift()

        self._icon_label.pack(side="left", padx=(5,0), pady=20)
        self._temporary_text_label.pack(side="left",padx=(0,5),pady=20)

        if self._schedule_hide_temporary_frame is not None:
            self._recipes_main_window.after_cancel(self._schedule_hide_temporary_frame)
        self._schedule_hide_temporary_frame = self._recipes_main_window.after(1200, _hide)

    def on_click_destroy_specific_frames(self):
        if self._specific_frame:
            self._specific_frame.after(0,self._specific_frame.destroy)
            self._specific_frame=None

        if self._temporary_frame:
            self._temporary_frame.after(0, self._temporary_frame.destroy)
            self._temporary_frame = None




    def animate(self):
        self._loading_label.place(x=250,y=250)
        for c in itertools.cycle(['..', '....', '......', '........', '..........', '............']):
            if self._received_massage:
                self._loading_label.place_forget()
                break
            if not self._client_status[0]:
                self._recipes_main_window.pack_forget()
                break
            self._loading_label.configure(text=c)
            time.sleep(0.1)






