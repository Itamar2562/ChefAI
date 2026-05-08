from customtkinter import *
from Server.BL.ServerBL import *
from ClientTable import ClientTable
import threading

FONT_LABEL = ("Segoe UI", 13, "bold")

SCREEN_WIDTH = 1004
SCREEN_HEIGHT = 526

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

    # Creates and configures the GUI layout
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


        self.client_table=ClientTable(self._home, width=350, height=410, fg_color="#1E1E2E", border_width=2,
                                     border_color="#3A3F8F")
        self.client_table.set_internal_frame_look(width=80, height=40, corner_radius=28, fg_color="#5B5FD9")
        self.client_table.place(x=20,y=60)

    # Starts or stops the server based on switch state
    def toggle_switch(self):
        if self._switch.get():
            self.on_click_start()
        else:
            self.on_click_stop()

    # Adds a client to the pending queue
    def queue_client_add(self, ip, port, user_id):
        self._pending_clients.append((ip, port, user_id))
        if not self._schedule_add_client:
            self._add_next_client()

    # Processes and displays queued clients one by one
    def _add_next_client(self):
        #no clients are waiting
        if not self._pending_clients:
            self._schedule_add_client=None
            return
        ip, port, user_id = self._pending_clients.pop(0)
        self.add_client_to_table(ip, port, user_id)
        self._schedule_add_client=self._root.after(100, self._add_next_client)

    # Clears all pending queued clients
    def clear_pending_queue(self):
        if self._schedule_add_client:
            self._root.after_cancel(self._schedule_add_client)
            self._schedule_add_client=None
        self._pending_clients.clear()

    # Displays a client in the table
    def add_client_to_table(self, ip, port, user_id):
        if self.client_table:
            self.client_table.add_client_to_table(ip, port, user_id)

    # Removes a client from the table display
    def remove_client_from_table(self, ip, port):
        if self.client_table:
            self.client_table.remove_client_from_table(ip, port)

    # Updates a client's displayed ID
    def configure_client_table_id(self, ip, port, new_user_id):
        if self.client_table:
            self.client_table.configure_user_table_id(ip,port,new_user_id)

    # Starts the GUI main loop
    def run(self):
        self._root.mainloop()

    # Starts the server thread
    def on_click_start(self):
        self._server_thread=threading.Thread(target=self.server_bl.start_server, daemon=True)
        self._server_thread.start()

    # Stops the server and clears the UI
    def on_click_stop(self):
        self.server_bl.stop_server()
        self.client_table.clear_frames()
        self.clear_pending_queue()



if __name__=='__main__':
    server= ServerGUI(SERVER_IP,PORT)
    server.run()


