from customtkinter import *
from Server.BL.ServerOP import *

FONT_LABEL = ("Segoe UI", 13, "bold")


class ClientTable(CTkScrollableFrame):
    def __init__(self, home_window, width, height, **kwargs):
        super().__init__(master=home_window, width=width, height=height, **kwargs)
        self._placeholder_for_scrollbar = None
        self._internal_frame_look=None

        self._label_width = 80
        self._label_height = 28
        self._btn_width = 30
        self._btn_height = 30

        self._client_address_to_frame_and_id_dict={}

    # Removes the temporary placeholder frame
    def destroy_placeholder(self):
            if self._placeholder_for_scrollbar:
                self._placeholder_for_scrollbar.destroy()
                self._placeholder_for_scrollbar = None

    # Adds a placeholder frame for scrollbar reset
    def place_placeholder(self):
        self._placeholder_for_scrollbar = CTkFrame(master=self, width=1, height=1, fg_color="transparent")
        self._placeholder_for_scrollbar.pack()

    # Clears all client frames from the table
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

    # Scrolls the client list to the bottom
    def move_down(self):
        self._parent_canvas.update_idletasks()
        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
        self._parent_canvas.yview_moveto(1.0)

    # Sets the style of internal frames
    def set_internal_frame_look(self, **kwargs):
        self._internal_frame_look = kwargs

    # Adds a new client to the table
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

    # Removes a client from the table
    def remove_client_from_table(self,ip,port):
        frame,_=self._client_address_to_frame_and_id_dict[(ip, port)]
        self.after(0,frame.destroy)
        del self._client_address_to_frame_and_id_dict[(ip, port)]

    # Updates the displayed user ID of a client
    def configure_user_table_id(self,ip,port,new_user_id):
        frame,id_label=self._client_address_to_frame_and_id_dict[(ip, port)]
        id_label.configure(text=f"ID: {new_user_id}")

