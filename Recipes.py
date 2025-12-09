import itertools
import time
from Protocol import *

class Recipes:
    def __init__(self, container, home, client_statue,callback_receive_msg):
        self._container=container
        self._home=home
        self._client_statue=client_statue
        self._callback_receive_msg=callback_receive_msg
        self._recipes_window=None
        self._received_massage=False
        self._loading_label=None
        self._threads=[]
        self._frames=[]
        self._entries=[]

    def create_ui(self):

        self._recipes_window = CTkScrollableFrame(self._container)
        temp_frame=CTkFrame(self._container, )
        self._loading_label=CTkLabel(master=temp_frame, font=('Calibri', 100), anchor='w')
        self._loading_label.place(x=250,y=250)

        thread=threading.Thread(target=lambda: self.animate(temp_frame), daemon=True)
        thread.start()
        self._threads.append(thread)
    #return the scrollable frame in recieve massage


    def add_recipe(self):
        #create the frame
        current_frame=CTkFrame(master=self._recipes_window,width=200,height=100)
        current_entry=CTkEntry(master=current_frame)
        current_confirm_btn=CTkButton(master=current_frame,width=30,height=30,text="✓",text_color="green",fg_color="black", font=("Arial", 18))
        current_delete_btn=CTkButton(master=current_frame,width=30,height=30,text="🗑",text_color="red",fg_color="black", font=("Arial", 18))
        self._frames.append(current_frame)
        self._entries.append(current_entry)
        #place the frame
        current_confirm_btn.place(x=150,y=5)
        current_delete_btn.place(x=185,y=5)
        current_entry.place(x=0,y=7)
        current_frame.pack(pady=2, padx=2, fill="x",)


    def animate(self,temp_frame):
        temp_frame.pack(fill="both", expand=True)
        for c in itertools.cycle(['..', '....', '......', '........', '..........', '............']):
            if self._received_massage:
                temp_frame.after(0,temp_frame.destroy)
                break
            self._loading_label.configure(text=c)
            time.sleep(0.1)






