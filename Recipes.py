import threading
from Protocol import *
from PIL import Image

class Recipes(CTkFrame):
    def __init__(self, container, callback_initiate_existing_home,callback_receive_msg,callback_configure_make_btn):
        super().__init__(master=container)
        self._container=container
        self._callback_initiate_existing_home=callback_initiate_existing_home
        self._callback_receive_msg=callback_receive_msg
        self._callback_configure_make_button=callback_configure_make_btn
        self._recipes_scrollable_window=None
        self._received_massage=False
        self._loading_label=None
        self._headline=None
        self._btn_back=None
        self.error_text=None
        self._threads=[]
        self._specific_frame=None
        self._temporary_frame=None
        self.bottom_spacer=None
        self._error_icon=CTkImage(Image.open(r"Images/ErrorIcon.png"),size=(30,30))
        self._success_icon=CTkImage(Image.open(r"Images/success_icon.png"),size=(30,30))
        self._download_icon=CTkImage(Image.open(r"Images/download_icon.png"), size=(60, 60))
        self._schedule_hide_temporary_frame=None
        self._icon_label=None
        self._temporary_text_label=None
        self._schedule_animate=None

    def create_ui(self):
        self.pack(fill="both",expand=True)
        self._recipes_scrollable_window = CTkScrollableFrame(self,height=500,width=980)
        self._loading_label=CTkLabel(master=self, font=('Calibri', 100))
        self._headline=CTkLabel(master=self, text="Recipes",
                                font=('Calibri', 50,"bold","underline"), text_color="#5B5FD9")
        self._btn_back = CTkButton(self, text="Back", height=30, width=80, text_color="white",
                                   hover_color="#6A3DB4", font=("Calibri", 17), fg_color="#7C4CC2"
,
                                   command=self.on_click_back)
        self.error_text = CTkLabel(master=self, font=("Segoe UI", 35, "bold"), text="No recipes found!")
        t1=threading.Thread(target=self.animate, daemon=True)
        t1.start()
        t2=threading.Thread(target=self.receive_massage,daemon=True)
        t2.start()

    def initiate_existing_ui(self):
        self.pack(fill="both",expand=True)
        self._received_massage=False
        self.error_text.place_forget()
        t1=threading.Thread(target=self.animate, daemon=True)
        t1.start()
        t2=threading.Thread(target=self.receive_massage,daemon=True)
        t2.start()

    def clear_recipes(self):
        for f in self._recipes_scrollable_window.winfo_children():
            f.after(0,f.destroy)
        self.bottom_spacer=None

    def create_recipes_frame(self):
        self._recipes_scrollable_window.place(x=0,y=60)
        self._headline.place(x=410,y=0)
        self._btn_back.place( x=920,y=10)

    def on_click_back(self):
        def on_click_yes():
            self.on_click_destroy_specific_frames()
            self.clear_recipes()
            self.pack_forget()
            self._callback_initiate_existing_home()

        def on_click_no():
            self.on_click_destroy_specific_frames()
        self.on_click_destroy_specific_frames()
        self._specific_frame=CTkFrame(self,border_width=3,border_color="#D9DBF8",height=200,width=300)
        self._specific_frame.place(x=400,y=200)
        confirmation_label=CTkLabel(master=self._specific_frame,text="Are you sure?",font=('Calibri',25,"bold"))
        confirmation_label.pack(padx=20,pady=10)
        yes_btn=CTkButton(master=self._specific_frame,text="Yes",fg_color="#8E6AD9",hover_color="#7553C2",
                          height=30, width=80,text_color="black",command=on_click_yes)
        yes_btn.pack(padx=5,pady=10,side="left")
        no_btn=CTkButton(master=self._specific_frame,text="No",fg_color="#8E6AD9",hover_color="#7553C2",
                         height=30, width=80,text_color="black",command=on_click_no)
        no_btn.pack(padx=5,pady=10,side="left")

    def receive_massage(self):
        try:
            msg=self._callback_receive_msg(need_json=True)
            write_to_log(f"msg is {msg}" )
            data=msg['data']
            write_to_log(f"data is {data}")
            remaining=data['remaining']
            if remaining<=0:
                self._callback_configure_make_button("disabled",remaining)
            else:
                self._callback_configure_make_button("normal",remaining)
            self._received_massage=True
            if msg['code']!="200":
                self.create_error_frame()
                return
            self.create_recipes_frame()
            self.add_recipes(data['recipes'])
        except Exception as e:
            write_to_log(e)
            self.create_error_frame()
            self._received_massage = True



    def create_error_frame(self):
        self._headline.place(x=410, y=0)
        self._btn_back.place(x=920, y=10)
        self.error_text.place(x=350,y=250)

    def shorten(self,text,max_len):
        if len(text) <= max_len:
            return text
        return text[:max_len-3] + "..."

    def put_button_spacer(self):
        if not self.bottom_spacer:
            self.bottom_spacer = CTkFrame(self._recipes_scrollable_window, height=65, fg_color="transparent")
        self.bottom_spacer.pack(fill="x")
    def add_recipes(self,data,index=0):
        #create the frame
        if index>=len(data):
            self.put_button_spacer()
            return
        d=data[index]
        current_frame=CTkFrame(master=self._recipes_scrollable_window,width=200,
                               height=100,border_width=3,border_color="#D9DBF8",corner_radius=15)
        current_frame.pack(pady=10, padx=2, fill="x",)
        headline_text=self.shorten(d['name'],65)
        headline=CTkLabel(master=current_frame,text=headline_text, font=('Calibri',20,"bold","underline"))
        headline.place(x=10,y=5)
        description_text=self.shorten(d['description'],220)
        description=CTkLabel(master=current_frame,text=  description_text,
                             font=('Calibri',15),wraplength=550,justify="left")
        description.place(x=10,y=35)
        difficulty_and_time=CTkLabel(master=current_frame,
                                     text=f"{d['difficulty']} • {d['time']} min",font=('Calibri',25))
        difficulty_and_time.place(x=660,y=10)
        cook_btn=CTkButton(master=current_frame,text="Cook",fg_color="#5B5FD9",hover_color="#4A4EC0",
                           command=lambda user_data=d:self.on_click_cook(user_data))
        cook_btn.place(x=600,y=50)
        nutrition_btn=CTkButton(master=current_frame,text="Nutrition",fg_color="#5B5FD9",hover_color="#4A4EC0",
                                command=lambda user_data=d:self.on_click_nutrition(user_data))
        nutrition_btn.place(x=750,y=50)
        download_btn=CTkButton(master=current_frame,text="",image=self._download_icon,width=50,
                               height=50,fg_color="transparent",hover=False,
                               command=lambda user_data=d: self.save_recipe(user_data))
        download_btn.place(x=895,y=22)


        self.after(20,self.add_recipes,data,index+1)

    def on_click_cook(self,data):
        self.on_click_destroy_specific_frames()
        self._specific_frame=CTkFrame(self)
        self._specific_frame.place(x=500,y=275,anchor='center')
        scrollable_frame=CTkScrollableFrame(master=self._specific_frame,width=750,height=420,
                                            corner_radius=15,border_color="#D9DBF8",border_width=3)
        scrollable_frame.pack()
        headline = CTkLabel(master=scrollable_frame, text=data['name'],
                            font=('Calibri', 25, "bold", "underline"),wraplength=500)
        headline.pack(pady=20,padx=20)
        recipe_steps = CTkLabel(master=scrollable_frame, text=data['data'],
                                justify="left",wraplength=750, font=('Calibri', 18),anchor='w')
        description = CTkLabel(master=scrollable_frame, text=data['description'], font=('Calibri', 20), wraplength=650,
                               justify="left", )
        description.pack(pady=10,padx=(2,100),anchor='w')
        recipe_steps.pack(pady=10,padx=0,fill='x',anchor='w')
        btn_back = CTkButton(scrollable_frame, text="Back", height=30, width=80, text_color="#4F4CC2",
                            font=("Calibri", 17), fg_color="#CFCBFF",hover_color="#BEB9F8",
                             command=self.on_click_destroy_specific_frames)
        btn_back.place(relx=1.0, x=-10, y=0, anchor="ne")

    def on_click_nutrition(self,data):
        self.on_click_destroy_specific_frames()
        self._specific_frame=CTkFrame(self, width=750,border_width=3, border_color="#D9DBF8")
        self._specific_frame.place(x=500, y=275,anchor='center')
        headline = CTkLabel(master=self._specific_frame, text=data['name'],
                            font=('Calibri', 25, "bold", "underline"),wraplength=500)
        headline.pack(pady=20, padx=150)
        nutrition = CTkLabel(master=self._specific_frame, text=data['nutrition'],
                             justify="left", wraplength=730, font=('Calibri', 18))
        nutrition.pack(pady=10,padx=10,side="left")
        btn_back = CTkButton(self._specific_frame, text="Back", height=30, width=80,text_color="#4F4CC2",
                             hover_color="#BEB9F8", font=("Calibri", 17), fg_color="#CFCBFF",
                             command=self.on_click_destroy_specific_frames)
        btn_back.place(relx=1.0, x=-10, y=10, anchor="ne")

    def save_recipe(self,data):
        succeed=save_to_pdf(data)
        if succeed:
            self.create_temp_frame(True,"File saved successfully")
        else:
            self.create_temp_frame(False,"File wasn't saved")

    def create_temp_frame(self,succeed,text):
        def _hide():
            self._schedule_hide_error_frame = None
            if self._temporary_frame:
             self._temporary_frame.place_forget()
        if not self._temporary_frame:
            self._temporary_frame = CTkFrame(self, fg_color="#3b0d0d", border_color="#ff4d4d", border_width=2,
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
        self._temporary_frame.place(x=500, y=275,anchor='center')
        self._temporary_frame.lift()

        self._icon_label.pack(side="left", padx=(5,0), pady=20)
        self._temporary_text_label.pack(side="left",padx=(0,5),pady=20)

        if self._schedule_hide_temporary_frame is not None:
            self.after_cancel(self._schedule_hide_temporary_frame)
        self._schedule_hide_temporary_frame = self.after(1200, _hide)

    def on_click_destroy_specific_frames(self):
        if self._specific_frame:
            self._specific_frame.after(0,self._specific_frame.destroy)
            self._specific_frame=None

        if self._temporary_frame:
            self._temporary_frame.after(0, self._temporary_frame.destroy)
            self._temporary_frame = None

    def animate(self):
        self._loading_label.place(x=250,y=250)
        animation_list=['..', '....', '......', '........', '..........', '............']
        def initiate_animating(index):
            if index==len(animation_list):
                index=0
            if self._received_massage:
                self._loading_label.place_forget()
                self.after_cancel(self._schedule_animate)
                return
            self._loading_label.configure(text=animation_list[index])
            self._schedule_animate=self.after(50,initiate_animating,index+1)
        initiate_animating(0)







