from ServerBL import *
import threading

FONT_LABEL = ("Segoe UI", 13, "bold")

class ClientList(CTkScrollableFrame):
    def __init__(self, home_window, width, height, **kwargs):
        super().__init__(master=home_window, width=width, height=height, **kwargs)

        self._placeholder_for_scrollbar = None
        self._internal_frame_look=None
        self.label_width = 80
        self.label_height = 28
        self.btn_width = 30
        self.btn_height = 30
        self.client_frame_dictionary={}
    def destroy_placeholder(self):
            if self._placeholder_for_scrollbar:
                self._placeholder_for_scrollbar.destroy()
                self._placeholder_for_scrollbar = None
    def place_placeholder(self):
        write_to_log("got to place placeholder")
        self._placeholder_for_scrollbar = CTkFrame(master=self, width=1, height=1, fg_color="transparent")
        self._placeholder_for_scrollbar.pack()
    def clear_frames(self):
        self._parent_canvas.yview_moveto(0.0)
        self._parent_canvas.update_idletasks()
        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
        try:
            for f in self.winfo_children():
                self.after(0,f.destroy)
        except: pass
        self.place_placeholder()
    def move_down(self):
        self._parent_canvas.update_idletasks()
        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
        self._parent_canvas.yview_moveto(1.0)

    def set_internal_frame_look(self, **kwargs):
        self._internal_frame_look = kwargs

    def add_client(self,ip,port,user_id):
        try:
            self.destroy_placeholder()
            #create the frame
            current_frame = CTkFrame(master=self, **self._internal_frame_look)
            current_frame.pack(pady=3, padx=2, fill="x", anchor='w')
            ip_label = CTkLabel(master=current_frame,width=self.label_width,text=f"IP: {ip}",
                font=FONT_LABEL,
                anchor="w"
            )
            ip_label.pack(padx=15, pady=10, side="left")

            port_label = CTkLabel(master=current_frame,width=self.label_width,
                text=f"Port: {port}",
                font=FONT_LABEL,
            )
            port_label.pack(padx=15, pady=10, side="left")

            id_label = CTkLabel(master=current_frame,width=self.label_width,text=f"ID: {user_id}", font=FONT_LABEL)
            id_label.pack(padx=15, pady=10, side="left")
            current_frame.id_label=id_label
            self.client_frame_dictionary[(ip, port)] = current_frame
        except Exception as e:
            write_to_log(f"exception {e}")

    def remove_client(self,ip,port):
        frame=self.client_frame_dictionary[(ip,port)]
        self.after(0,frame.destroy)
        del self.client_frame_dictionary[(ip,port)]

    def configure_user_id(self,ip,port,new_user_id):
        frame=self.client_frame_dictionary[(ip,port)]
        frame.id_label.configure(text=f"ID: {new_user_id}")


class ServerGUI:

    def __init__(self, ip, port):
        self.server_bl=ServerBL(ip,port,self.add_client,self.remove_client,self.configure_client_id)

        # Attributes
        self._server_thread = None

        self._root = None
        self._container=None
        self._home=None

        self._server_label=None
        self._btn_start = None
        self._btn_stop = None

        self._client_list=None


        self.client_table=None
        # GUI initialization
        self._root = CTk()
        self._root.title("Server GUI")
        img_width = 1004
        img_height = 526
        # Set size of the application window = image size
        set_appearance_mode("dark")
        self._root.geometry(f'{img_width}x{img_height}')
        self._root.resizable(False, False)
        self._container = CTkFrame(self._root)
        self._container.pack(fill="both",expand=True)
        self.create_ui()

    def create_ui(self):

        self._home = CTkFrame(master=self._container)
        self._home.pack(fill="both", expand=True)

        self._server_label = CTkLabel(master=self._home, text="Server", font=('Calibri', 50, "bold", "underline"),
                                text_color="#5B5FD9")
        self._server_label.place(x=502, y=25, anchor="center")
        self._btn_start = CTkButton(self._home,text="Start",
                                    height=30, width=80,
                                    command=self.on_click_start)
        self._btn_start.place(x=650,y=50)

        # Button "Stop"
        self._btn_stop = CTkButton(self._home,text="Stop",
                                   height=30, width=80,
                                   command=self.on_click_stop,state="disabled")
        self._btn_stop.place(x=650,y=130)
        self._client_list=CTkLabel(master=self._home, text="Clients", font=('Calibri', 30, "underline"))
        self._client_list.place(x=150, y=20)


        self.client_table=ClientList(self._home, width=350, height=410, fg_color="#1E1E2E", border_width=2, border_color="#3A3F8F")
        self.client_table.set_internal_frame_look(width=80, height=40, corner_radius=28, fg_color="#5B5FD9")
        self.client_table.place(x=20,y=60)

    def add_client(self,ip,port,user_id):
        if self.client_table:
            self.client_table.add_client(ip,port,user_id)
    def remove_client(self,ip,port):
        if self.client_table:
            self.client_table.remove_client(ip,port)
    def configure_client_id(self,ip,port,new_user_id):
        if self.client_table:
            self.client_table.configure_user_id(ip,port,new_user_id)

    def run(self):
        self._root.mainloop()

    def on_click_start(self):
        self._btn_start.configure(state="disabled")
        self._btn_stop.configure(state="normal")
        self._server_thread=threading.Thread(target=self.server_bl.start_server, daemon=True)
        self._server_thread.start()

    def on_click_stop(self):
        self._btn_stop.configure(state="disabled")
        self._btn_start.configure(state="normal")
        self.server_bl.stop_server()
        self.client_table.clear_frames()

if __name__=='__main__':
    server= ServerGUI("0.0.0.0",8822)
    server.run()


