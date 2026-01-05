from Protocol import *

class Ingredients(CTkScrollableFrame):
    def __init__(self,home_window,client_status,callback_send_data,callback_receive_confirmation,add_btn,width=300,height=300,**kwargs):
        super().__init__(master=home_window,width=width,height=height,**kwargs)
        self.frames=[]
        self.entries=[]
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

    def add_ingredient(self):
        self.callback_add_btn("disabled")
        self.is_currently_editing=True
        self.new_ingredient=True
        self.previous_ingredient=""
        #create the frame
        current_frame=CTkFrame(master=self,width=80,height=40)
        current_entry=CTkEntry(master=current_frame)
        current_main_btn=CTkButton(master=current_frame,width=30,height=30,text="✓",text_color="green",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_main_btn(current_entry,current_main_btn))
        current_delete_btn=CTkButton(master=current_frame,width=30,height=30,text="🗑",text_color="red",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_delete_btn(current_frame,current_entry))

        self.frames.append(current_frame)
        self.entries.append(current_entry)
        #place the frame
        current_main_btn.place(x=150,y=5)
        current_delete_btn.place(x=185,y=5)
        current_entry.place(x=0,y=7)
        current_frame.pack(pady=2, padx=2, fill="x",)

    def initiate_first_ingredients(self,ingredient):
        # create the frame
        self.is_currently_editing=False
        self.callback_add_btn("normal")
        current_frame = CTkFrame(master=self, width=80, height=40)
        current_entry = CTkEntry(master=current_frame)
        current_entry.insert(0,ingredient)
        current_entry.configure(state="disabled")
        current_confirm_btn = CTkButton(master=current_frame, width=30, height=30, text="✎",text_color="white", fg_color="black", font=("Arial", 18), command=lambda: self.on_click_main_btn(current_entry, current_confirm_btn))
        current_delete_btn = CTkButton(master=current_frame, width=30, height=30, text="🗑", text_color="red",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_delete_btn(current_frame, current_entry))
        self.frames.append(current_frame)
        self.entries.append(current_entry)
        # place the frame
        current_confirm_btn.place(x=150, y=5)
        current_delete_btn.place(x=185, y=5)
        current_entry.place(x=0, y=7)
        current_frame.pack(pady=2, padx=2, fill="x")

    def on_click_main_btn(self,current_entry:CTkEntry,current_btn:CTkButton):
        current_state = current_entry.cget("state")
        #go to edit mode
        if current_state=="disabled" and not self.is_currently_editing:
            self.edit_mode(current_entry,current_btn)
        #dont let users press edit when already editing another ing
        elif current_state=="disabled" and self.is_currently_editing:
            pass
        #save and pass to server
        elif current_entry.get().strip()!="":
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

    def edit_mode(self,current_entry,current_btn):
        current_entry.configure(state="normal")
        current_btn.configure(text="✓", text_color="green")
        self.is_currently_editing = True
        self.callback_add_btn("disabled")
        self.previous_ingredient = current_entry.get()

    def clear_ingredients(self):
        for f in self.frames:
            f.after(0, f.destroy)
        self.frames.clear()
        self.entries.clear()
        self.is_currently_editing=False

    def destroy_frame(self,current_frame,current_entry):
        current_frame.destroy()
        self.frames.remove(current_frame)
        self.entries.remove(current_entry)
        self.callback_add_btn("normal")
        self.is_currently_editing = False

    def on_click_delete_btn(self,current_frame,current_entry):
        #dont let users delete other ingredients when editing another one or delete on edit mode
        current_state=current_entry.cget("state")
        #dont let user delete other ing when editing or
        if (self.is_currently_editing and current_state=="disabled")or( not self.new_ingredient and current_state=="normal"):
            return
        data=current_entry.get().strip()
        if data!="":
            self.callback_send_data("DELETE",data)
            succeed=self.callback_receive_confirmation()
            if succeed:
                self.destroy_frame(current_frame,current_entry)
        else:
            self.destroy_frame(current_frame, current_entry)

    def is_editing(self):
        return self.is_currently_editing

    def get_ingredients_list(self):
        ingredients_list=[]
        for f in self.entries:
            if f.get() !="":
                ingredients_list.append(f.get())
        return ingredients_list

class Ratings:
    pass




