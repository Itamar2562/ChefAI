from Protocol import *

class Ingredients(CTkScrollableFrame):
    def __init__(self,home_window,client_status,callback_send_data,callback_receive_confirmation,add_btn,width=300,height=300,**kwargs):
        super().__init__(master=home_window,width=width,height=height,**kwargs)

        # Access the internal frame inside the scrollable frame
        self.callback_add_btn=add_btn
        self.is_currently_editing=False
        self.new_ingredient=False
        self.client_status=client_status
        self.callback_send_data=callback_send_data
        self.callback_receive_confirmation=callback_receive_confirmation
        self.previous_ingredient=""

    def move_down(self):
        self._parent_canvas.update_idletasks()
        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
        self._parent_canvas.yview_moveto(1.0)

    def remove(self):
            self._parent_frame.destroy()
            self.destroy()

    def add_ingredient(self):
        self.callback_add_btn("disabled")
        self.is_currently_editing=True
        self.new_ingredient=True
        self.previous_ingredient=""
        #create the frame
        current_frame=CTkFrame(master=self,width=80,height=40,corner_radius=28,fg_color="#5B5FD9")
        current_frame.pack(pady=3,padx=2,fill="x",anchor='w')
        current_entry=CTkEntry(master=current_frame)
        current_entry.place(x=5,y=7)
        current_entry.focus()
        current_main_btn=CTkButton(master=current_frame,width=30,height=30,text="✓",text_color="green",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_main_btn(current_entry,current_main_btn))
        current_main_btn.place(x=150,y=5)
        current_delete_btn=CTkButton(master=current_frame,width=30,height=30,text="🗑",text_color="red",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_delete_btn(current_frame,current_entry))
        current_delete_btn.place(x=185,y=5)
        current_entry.bind('<Return>',lambda event: self.on_click_main_btn(current_entry,current_main_btn))

    def initiate_first_ingredients(self,ingredient):
        # create the frame
        current_frame=CTkFrame(master=self,width=80,height=40,corner_radius=28,fg_color="#5B5FD9")
        current_frame.pack(pady=3, padx=2, fill="x",anchor='w')
        current_entry = CTkEntry(master=current_frame)
        current_entry.place(x=5, y=7)
        current_entry.insert(0,ingredient)
        current_entry.configure(state="disabled")
        current_confirm_btn = CTkButton(master=current_frame, width=30, height=30, text="✎",text_color="white", fg_color="black", font=("Arial", 18), command=lambda: self.on_click_main_btn(current_entry, current_confirm_btn))
        current_confirm_btn.place(x=150, y=5)
        current_delete_btn = CTkButton(master=current_frame, width=30, height=30, text="🗑", text_color="red",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_delete_btn(current_frame, current_entry))
        current_delete_btn.place(x=185, y=5)

    def on_click_main_btn(self,current_entry:CTkEntry,current_btn:CTkButton):
        write_to_log("got here main btn")
        current_state = current_entry.cget("state")
        #user pressed to edit ->go to edit mode and do nothing else
        if current_state=="disabled" and not self.is_currently_editing:
            self.edit_mode(current_entry,current_btn)
            return
        #user pressed other edit btn while editing->do nothing
        elif current_state=="disabled" and self.is_currently_editing:
            return
        #user pressed confirm
        new_ingredient=current_entry.get().strip()
        if new_ingredient=="" or len(new_ingredient)>32:
            return
        if self.client_status.connected:
            data=self.previous_ingredient,current_entry.get().strip()
            self.callback_send_data("ADD",data)
            succeed=self.callback_receive_confirmation()
            if succeed:
                self.confirm_mode(current_entry,current_btn)

    def confirm_mode(self,current_entry:CTkEntry,current_btn:CTkButton):
        #make sure there isn't any whitesspaces
        data=current_entry.get().strip()
        current_entry.delete(0,END)
        current_entry.insert(0,data)
        current_entry.configure(state="disabled")
        current_btn.configure(text="✎️", text_color="white", )
        self.callback_add_btn("normal")
        self.is_currently_editing = False
        self.new_ingredient=False
        current_entry.unbind('<Return>')

    def edit_mode(self,current_entry,current_btn):
        current_entry.configure(state="normal")
        current_btn.configure(text="✓", text_color="green")
        self.is_currently_editing = True
        self.callback_add_btn("disabled")
        self.previous_ingredient = current_entry.get()
        current_entry.focus()
        current_entry.bind('<Return>',lambda event: self.on_click_main_btn(current_entry,current_btn))

    def clear_ingredients(self):
        for f in self.winfo_children():
            f.destroy()
        self.is_currently_editing=False
        self._parent_canvas.yview_moveto(0.0)
        self._parent_canvas.update_idletasks()
        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))

    def destroy_frame(self,current_frame):
        current_frame.destroy()
        self.callback_add_btn("normal")
        self.is_currently_editing = False

    def on_click_delete_btn(self,current_frame,current_entry):
        current_state=current_entry.cget("state")
        #Dont let user delete other frames while editing or delete while editing a current frame
        #only delete a frame if its a new one or not currently editing
        if (self.is_currently_editing and current_state=="disabled")or( not self.new_ingredient and current_state=="normal"):
            return
        data=current_entry.get().strip()
        if data!="": #no reason to send delete on nothing
            self.callback_send_data("DELETE",data)
            succeed=self.callback_receive_confirmation()
            if succeed:
                self.destroy_frame(current_frame)
        else:
            self.destroy_frame(current_frame)

    def is_editing(self):
        return self.is_currently_editing

    # def get_ingredients_list(self):
    #     ingredients_list=[]
    #     for f in self.entries:
    #         if f.get() !="":
    #             ingredients_list.append(f.get())
    #     return ingredients_list

class Ratings:
    pass




