import itertools
import time

from PIL.ImageOps import expand

from Protocol import *

#

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

    def create_ui(self):

        self._recipes_window = CTkScrollableFrame(self._container)
        temp_frame=CTkFrame(self._container, )
        self._loading_label=CTkLabel(master=temp_frame, font=('Calibri', 100), anchor='w')
        self._loading_label.place(x=250,y=250)

        thread=threading.Thread(target=lambda: self.animate(temp_frame), daemon=True)
        thread.start()
        self._threads.append(thread)
    #return the scrollable frame in recieve massage

    def animate(self,temp_frame):
        temp_frame.pack(fill="both", expand=True)
        for c in itertools.cycle(['..', '....', '......', '........', '..........', '............']):
            if self._received_massage:
                temp_frame.after(0,temp_frame.destroy)
                break
            self._loading_label.configure(text=c)
            time.sleep(0.1)






