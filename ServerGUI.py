from customtkinter import *
from ServerBL import *
import threading

FONT_LABEL = ("Segoe UI", 13, "bold")

class ClientList(CTkScrollableFrame):
    def __init__(self, home_window, width, height, **kwargs):
        super().__init__(master=home_window, width=width, height=height, **kwargs)
        self._placeholder_for_scrollbar = None
        self._internal_frame_look=None

        self._label_width = 80
        self._label_height = 28
        self._btn_width = 30
        self._btn_height = 30

        self._client_address_to_frame_and_id_dict={}

    def destroy_placeholder(self):
            if self._placeholder_for_scrollbar:
                self._placeholder_for_scrollbar.destroy()
                self._placeholder_for_scrollbar = None

    def place_placeholder(self):
        self._placeholder_for_scrollbar = CTkFrame(master=self, width=1, height=1, fg_color="transparent")
        self._placeholder_for_scrollbar.pack()

    def clear_frames(self):
        self._client_address_to_frame_and_id_dict.clear()
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

    def add_client_to_table(self, ip, port, user_id):
        try:
            self.destroy_placeholder()
            #create the frame
            current_frame = CTkFrame(master=self, **self._internal_frame_look)
            current_frame.pack(pady=3, padx=2, fill="x", anchor='w')
            ip_label = CTkLabel(master=current_frame, width=self._label_width, text=f"IP: {ip}",
                                font=FONT_LABEL,
                                anchor="w"
                                )
            ip_label.pack(padx=15, pady=10, side="left")

            port_label = CTkLabel(master=current_frame, width=self._label_width,
                                  text=f"Port: {port}",
                                  font=FONT_LABEL,
                                  )
            port_label.pack(padx=15, pady=10, side="left")

            id_label = CTkLabel(master=current_frame, width=self._label_width, text=f"ID: {user_id}", font=FONT_LABEL)
            id_label.pack(padx=15, pady=10, side="left")
            self._client_address_to_frame_and_id_dict[(ip, port)] = current_frame,id_label
        except Exception as e:
            write_to_log(f"[Server_GUI] error {e} while displaying clients")

    def remove_client_from_table(self,ip,port):
        frame,_=self._client_address_to_frame_and_id_dict[(ip, port)]
        self.after(0,frame.destroy)
        del self._client_address_to_frame_and_id_dict[(ip, port)]


    def configure_user_table_id(self,ip,port,new_user_id):
        frame,id_label=self._client_address_to_frame_and_id_dict[(ip, port)]
        id_label.configure(text=f"ID: {new_user_id}")


class ServerGUI:

    def __init__(self, ip, port):
        self.server_bl=ServerBL(ip, port, self.queue_client_add, self.remove_client_from_table, self.configure_client_table_id)

        # Attributes
        self._server_thread = None

        self._root = None
        self._container=None
        self._home=None

        self._server_label=None

        self._client_list_label=None
        self._switch=None

        self.client_table=None
        self._pending_clients = []
        self._schedule_add_client=None

        self.create_ui()

    def create_ui(self):
        self._root = CTk()
        self._root.title("Server GUI")
        set_appearance_mode("dark")
        self._root.geometry(f'{SCREEN_WIDTH}x{SCREEN_HEIGHT}')
        self._root.resizable(False, False)

        self._container = CTkFrame(self._root)
        self._container.pack(fill="both", expand=True)

        self._home = CTkFrame(master=self._container)
        self._home.pack(fill="both", expand=True)

        self._server_label = CTkLabel(master=self._home, text="Server", font=('Calibri', 50, "bold", "underline"),
                                text_color="#5B5FD9")
        self._server_label.place(x=502, y=25, anchor="center")

        self._switch=CTkSwitch(master=self._home,switch_width=300,switch_height=150,command=self.toggle_switch,text="")
        self._switch.place(x=550,y=200)

        self._client_list_label=CTkLabel(master=self._home, text="Clients", font=('Calibri', 30, "underline"))
        self._client_list_label.place(x=150, y=20)


        self.client_table=ClientList(self._home, width=350, height=410, fg_color="#1E1E2E", border_width=2,
                                     border_color="#3A3F8F")
        self.client_table.set_internal_frame_look(width=80, height=40, corner_radius=28, fg_color="#5B5FD9")
        self.client_table.place(x=20,y=60)

    def toggle_switch(self):
        if self._switch.get():
            self.on_click_start()
        else:
            self.on_click_stop()

    def queue_client_add(self, ip, port, user_id):
        self._pending_clients.append((ip, port, user_id))
        if not self._schedule_add_client:
            self._add_next_client()

    def _add_next_client(self):
        #no clients are waiting
        if not self._pending_clients:
            self._schedule_add_client=None
            return
        ip, port, user_id = self._pending_clients.pop(0)
        self.add_client_to_table(ip, port, user_id)
        self._schedule_add_client=self._root.after(40, self._add_next_client)

    def clear_pending_queue(self):
        if self._schedule_add_client:
            self._root.after_cancel(self._schedule_add_client)
            self._schedule_add_client=None
        self._pending_clients.clear()

    def add_client_to_table(self, ip, port, user_id):
        if self.client_table:
            self.client_table.add_client_to_table(ip, port, user_id)

    def remove_client_from_table(self, ip, port):
        if self.client_table:
            self.client_table.remove_client_from_table(ip, port)

    def configure_client_table_id(self, ip, port, new_user_id):
        if self.client_table:
            self.client_table.configure_user_table_id(ip,port,new_user_id)

    def run(self):
        self._root.mainloop()

    def on_click_start(self):
        self._server_thread=threading.Thread(target=self.server_bl.start_server, daemon=True)
        self._server_thread.start()

    def on_click_stop(self):
        self.server_bl.stop_server()
        self.client_table.clear_frames()
        self.clear_pending_queue()



if __name__=='__main__':
    server= ServerGUI(SERVER_IP,PORT)
    server.run()


