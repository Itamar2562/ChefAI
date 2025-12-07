from ServerBL import *
import tkinter as tk

BTN_IMAGE = "./Images/GUI - button.png"
BG_IMAGE = "./Images/GUI - BG.png"
FONT = "Calibri"
FONT_BUTTON = (FONT,16)


class ServerGUI(ServerBL):

    def __init__(self, ip, port):
        super().__init__(ip,port)

        # Attributes
        self._server_thread = None

        self._root = None
        self._canvas = None
        self._img_bg = None
        self._img_btn = None

        self._entry_IP = None
        self._entry_Port = None
        self._entry_Received = None
        self._entry_Send = None

        self._btn_start = None
        self._btn_stop = None

        # GUI initialization
        self.create_ui()

    def create_ui(self):

        self._root = tk.Tk()
        self._root.title("Server GUI")

        # Load bg image
        self._img_bg = tk.PhotoImage(file=BG_IMAGE)
        img_width = self._img_bg.width()
        img_height = self._img_bg.height()

        # Set size of the application window = image size
        self._root.geometry(f'{img_width}x{img_height}')
        self._root.resizable(False,False)

        # Create a canvas to cover the entire window
        self._canvas = tk.Canvas(self._root)
        self._canvas.config(width=img_width,height=img_height)
        self._canvas.pack(fill='both',expand=True)
        self._canvas.create_image(0,0,anchor="nw",image=self._img_bg)

        # Add labels, the same as. add text on canvas
        self._canvas.create_text(90,80,text='Server',font=('Calibri',28),fill='#808080')
        self._canvas.create_text(50,180,text='IP:',font=FONT_BUTTON,fill='#000000',anchor='w')
        self._canvas.create_text(50,230,text='Port:',font=FONT_BUTTON,fill='#000000',anchor='w')
        self._canvas.create_text(50,280,text='Send:',font=FONT_BUTTON,fill='#000000',anchor='w')
        self._canvas.create_text(50,330,text='Received:',font=FONT_BUTTON,fill='#000000',anchor='w')

        # Load button image
        self._img_btn = tk.PhotoImage(file=BTN_IMAGE)
        img_btn_w = self._img_btn.width()
        img_btn_h = self._img_btn.height()

        # Button "Start"
        self._btn_start = tk.Button(self._canvas,text="Start",font=FONT_BUTTON,fg="#c0c0c0",compound="center",
                                    width=img_btn_w,height=img_btn_h,image=self._img_btn,bd=0,
                                    command=self.on_click_start)
        self._btn_start.place(x=650,y=50)

        # Button "Stop"
        self._btn_stop = tk.Button(self._canvas,text="Stop",font=FONT_BUTTON,fg="#c0c0c0",compound="center",
                                   width=img_btn_w,height=img_btn_h,image=self._img_btn,bd=0,
                                   command=self.on_click_stop,state="disabled")
        self._btn_stop.place(x=650,y=130)

        # Create Entry boxes
        self._entry_IP = tk.Entry(self._canvas, font=('Calibri',16), fg='#808080')
        self._entry_IP.insert(0,'127.0.0.1')
        self._entry_IP.place(x=200,y=168)

        self._entry_Port = tk.Entry(self._canvas,font=('Calibri',16),fg='#808080')
        self._entry_Port.insert(0,"8822")
        self._entry_Port.place(x=200,y=218)

        self._entry_Send = tk.Entry(self._canvas,font=('Calibri',16),fg='#808080')
        self._entry_Send.insert(0,"text message")
        self._entry_Send.place(x=200,y=268)

        self._entry_Received = tk.Entry(self._canvas,font=('Calibri',16),fg='#808080')
        self._entry_Received.insert(0,"...")
        self._entry_Received.place(x=200,y=318)

    def run(self):
        self._root.mainloop()

    def on_click_start(self):
        self._btn_start.config(state="disabled")
        self._btn_stop.config(state="normal")
        self._server_thread=threading.Thread(target=self.start_server, daemon=True)
        self._server_thread.start()

    def on_click_stop(self):
        self._btn_stop.config(state="disabled")
        self._btn_start.config(state="normal")
        self.stop_server()

if __name__=='__main__':
    server= ServerGUI("0.0.0.0",8822)
    server.run()
