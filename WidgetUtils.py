from Protocol import *

class ScrollableFrameBase(CTkScrollableFrame):
    def __init__(self,home_window,client_status,callback_send_data,callback_receive_confirmation,add_btn,width=300,height=300,**kwargs):
        super().__init__(master=home_window,width=width,height=height,**kwargs)
        self.callback_add_btn = add_btn
        self.is_currently_editing = False
        self.new = False
        self._internal_ingredient_look = None
        self.client_status = client_status
        self.callback_send_data = callback_send_data
        self.callback_receive_confirmation = callback_receive_confirmation
        self.previous = ""
        self._placeholder_for_scrollbar = None  # adding a frame resets the scrollbar

    def confirm_mode(self,current_entry:CTkEntry,current_btn:CTkButton):
        #make sure there isn't any whitesspaces
        data=current_entry.get().strip()
        current_entry.delete(0,END)
        current_entry.insert(0,data)
        current_entry.configure(state="disabled")
        current_btn.configure(text="✎️", text_color="white", )
        self.callback_add_btn("normal")
        self.is_currently_editing = False
        self.new=False
        current_entry.unbind('<Return>')

    def clear_frames(self):
        self.is_currently_editing = False
        self._parent_canvas.yview_moveto(0.0)
        self._parent_canvas.update_idletasks()
        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
        for f in self.winfo_children():
            f.after(0,f.destroy)
        self._placeholder_for_scrollbar = CTkFrame(master=self, width=20, height=20, fg_color="transparent")
        self._placeholder_for_scrollbar.pack()

    def move_down(self):
        self._parent_canvas.update_idletasks()
        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
        self._parent_canvas.yview_moveto(1.0)

    def remove(self):
        self._parent_frame.destroy()
        self.destroy()

    def set_internal_ingredient_look(self,**kwargs):
        self._internal_ingredient_look=kwargs

    def destroy_frame(self, current_frame):
        current_frame.destroy()
        self.callback_add_btn("normal")
        self.is_currently_editing = False

    def is_editing(self):
        return self.is_currently_editing


class Ingredient(ScrollableFrameBase):
    def __init__(self,home_window,client_status,callback_send_data,callback_receive_confirmation,add_btn,categorize_callback,width=300,height=300,**kwargs):
        super().__init__(home_window,client_status,callback_send_data,callback_receive_confirmation,add_btn,width,height,**kwargs)

        self.categorize_callback=categorize_callback
    def add_ingredient(self):
        if self._placeholder_for_scrollbar:
            self._placeholder_for_scrollbar.destroy()
            self._placeholder_for_scrollbar=None
        self.callback_add_btn("disabled")
        self.is_currently_editing=True
        self.new=True
        self.previous=""
        #create the frame
        current_frame=CTkFrame(master=self,**self._internal_ingredient_look)
        current_frame.pack(pady=3,padx=2,fill="x",anchor='w')
        current_entry=CTkEntry(master=current_frame)
        current_entry.place(x=5,y=7)
        current_entry.focus()
        current_main_btn=CTkButton(master=current_frame,width=30,height=30,text="✓",text_color="green",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_main_btn(current_entry,current_main_btn))
        current_main_btn.place(x=150,y=5)
        current_categorize_btn = CTkButton(master=current_frame, width=30, height=30, text="🧺", text_color="gray",fg_color="black", font=("Ariel", 18),command=lambda: self.categorize(current_entry))
        current_categorize_btn.place(x=185, y=5)
        current_delete_btn=CTkButton(master=current_frame,width=30,height=30,text="🗑",text_color="red",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_delete_btn(current_frame,current_entry))
        current_delete_btn.place(x=220,y=5)
        current_entry.bind('<Return>',lambda event: self.on_click_main_btn(current_entry,current_main_btn))

    def categorize(self,current_entry):
        write_to_log(self.is_currently_editing)
        if not self.is_currently_editing:
            self.categorize_callback(current_entry.get().strip())

    def initiate_first_ingredients(self,ingredient):
        if self._placeholder_for_scrollbar:
            self._placeholder_for_scrollbar.destroy()
            self._placeholder_for_scrollbar=None
        # create the frame
        current_frame=CTkFrame(master=self,**self._internal_ingredient_look)
        current_frame.pack(pady=3, padx=2, fill="x",anchor='w')
        current_entry = CTkEntry(master=current_frame)
        current_entry.place(x=5, y=7)
        current_entry.insert(0,ingredient)
        current_entry.configure(state="disabled")
        current_confirm_btn = CTkButton(master=current_frame, width=30, height=30, text="✎",text_color="white", fg_color="black", font=("Arial", 18), command=lambda: self.on_click_main_btn(current_entry, current_confirm_btn))
        current_confirm_btn.place(x=150, y=5)
        current_categorize_btn = CTkButton(master=current_frame, width=30, height=30, text="🧺", text_color="gray",fg_color="black", font=("Ariel", 18),command=lambda: self.categorize(current_entry))
        current_categorize_btn.place(x=185, y=5)
        current_delete_btn = CTkButton(master=current_frame, width=30, height=30, text="🗑", text_color="red",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_delete_btn(current_frame, current_entry))
        current_delete_btn.place(x=220, y=5)

    def edit_mode(self, current_entry, current_btn):
        current_entry.configure(state="normal")
        current_btn.configure(text="✓", text_color="green")
        self.is_currently_editing = True
        self.callback_add_btn("disabled")
        self.previous = current_entry.get()
        current_entry.focus()
        current_entry.bind('<Return>', lambda event: self.on_click_main_btn(current_entry, current_btn))

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
            data=[0,self.previous,current_entry.get().strip()]
            self.callback_send_data("ADD",data)
            succeed=self.callback_receive_confirmation()
            if succeed:
                self.confirm_mode(current_entry,current_btn)

    def on_click_delete_btn(self,current_frame,current_entry):
        current_state=current_entry.cget("state")
        #Dont let user delete other frames while editing or delete while editing a current frame
        #only delete a frame if its a new one or not currently editing
        if (self.is_currently_editing and current_state=="disabled")or( not self.new and current_state=="normal"):
            return
        data=[0,current_entry.get().strip()]
        if data!="" and not self.new: #no reason to send delete on nothing or if new ingredient
            self.callback_send_data("DELETE",data)
            succeed=self.callback_receive_confirmation()
            if succeed:
                self.destroy_frame(current_frame)
        else:
            self.new=False
            self.destroy_frame(current_frame)


class DynamicList(ScrollableFrameBase):
    def __init__(self,home_window,client_status,callback_send_data,callback_receive_confirmation,add_btn,width,height,**kwargs):
        super().__init__(home_window,client_status,callback_send_data,callback_receive_confirmation,add_btn,width,height,**kwargs)

    def add_list(self):
        if self._placeholder_for_scrollbar:
            self._placeholder_for_scrollbar.destroy()
            self._placeholder_for_scrollbar = None
        self.callback_add_btn("disabled")
        self.is_currently_editing = True
        self.new = True
        self.previous = ""
        current_frame = CTkFrame(master=self, **self._internal_ingredient_look)
        current_frame.pack(pady=3, padx=2, fill="x", anchor='w')
        current_entry = CTkEntry(master=current_frame)
        current_entry.place(x=5, y=7)
        current_entry.focus()
        current_main_btn = CTkButton(master=current_frame, width=30, height=30, text="✓", text_color="green", fg_color="black", font=("Arial", 18),command=lambda: self.on_click_main_btn(current_entry, current_main_btn))
        current_main_btn.place(x=150, y=5)
        current_open_btn = CTkButton(master=current_frame, width=30, height=30, text="📂", text_color="gray",fg_color="black", font=("Ariel", 18), command=self.on_click_open_list)
        current_open_btn.place(x=185, y=5)
        current_delete_btn = CTkButton(master=current_frame, width=30, height=30, text="🗑", text_color="red",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_delete_btn(current_frame, current_entry))
        current_delete_btn.place(x=220, y=5)
        current_entry.bind('<Return>', lambda event: self.on_click_main_btn(current_entry, current_main_btn))

    def initiate_first_lists(self,ingredient):
        if self._placeholder_for_scrollbar:
            self._placeholder_for_scrollbar.destroy()
            self._placeholder_for_scrollbar=None
        # create the frame
        current_frame=CTkFrame(master=self,**self._internal_ingredient_look)
        current_frame.pack(pady=3, padx=2, fill="x",anchor='w')
        current_entry = CTkEntry(master=current_frame)
        current_entry.place(x=5, y=7)
        current_entry.insert(0,ingredient)
        current_entry.configure(state="disabled")
        current_confirm_btn = CTkButton(master=current_frame, width=30, height=30, text="✎",text_color="white", fg_color="black", font=("Arial", 18), command=lambda: self.on_click_main_btn(current_entry, current_confirm_btn))
        current_confirm_btn.place(x=150, y=5)
        current_open_btn = CTkButton(master=current_frame, width=30, height=30, text="📂", text_color="gray",fg_color="black", font=("Ariel", 18))
        current_open_btn.place(x=185, y=5)
        current_delete_btn = CTkButton(master=current_frame, width=30, height=30, text="🗑", text_color="red",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_delete_btn(current_frame, current_entry))
        current_delete_btn.place(x=220, y=5)


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
        new_list=current_entry.get().strip()
        if new_list=="" or len(new_list)>32:
            return
        if self.client_status.connected:
            data=[self.previous,current_entry.get().strip()]
            self.callback_send_data("LIST",data)
            succeed=self.callback_receive_confirmation()
            if succeed:
                self.confirm_mode(current_entry,current_btn)

    def edit_mode(self, current_entry, current_btn):
        current_entry.configure(state="normal")
        current_btn.configure(text="✓", text_color="green")
        self.is_currently_editing = True
        self.callback_add_btn("disabled")
        self.previous = current_entry.get()
        current_entry.focus()
        current_entry.bind('<Return>', lambda event: self.on_click_main_btn(current_entry, current_btn))
    def on_click_open_list(self):
        pass

    def on_click_delete_btn(self, current_frame, current_entry):
        current_state = current_entry.cget("state")
        # Dont let user delete other frames while editing or delete while editing a current frame
        # only delete a frame if its a new one or not currently editing
        if (self.is_currently_editing and current_state == "disabled") or (not self.new and current_state == "normal"):
            return
        data = [0, current_entry.get().strip()]
        if data != "" and not self.new:  # no reason to send delete on nothing or if new ingredient
            self.callback_send_data("DELETE_LIST", data)
            succeed = self.callback_receive_confirmation()
            if succeed:
                self.destroy_frame(current_frame)
        else:
            self.new = False
            self.destroy_frame(current_frame)

class DraggableFrame(CTkFrame):
    def __init__(self,home_window,width=300,height=300,**kwargs):
        super().__init__(master=home_window,width=width,height=height,**kwargs)
        self._specific_frame_drag_start_x = 0
        self._specific_frame_drag_start_y = 0
        self._specific_frame_drag_scheduled = False
        self.lift()

    # recursivly binds all widgets except a scroll bar or a button
    def bind_drag_widget(self, widget):
        # Skip binding if widget is a scrollbar
        if isinstance(widget, (CTkScrollbar, CTkButton)):
            return
        widget.bind("<ButtonPress-1>", self.specific_frame_start_move, add="+")
        widget.bind("<B1-Motion>", self.on_specific_frame_move, add="+")
        # Recursively bind children
        for child in widget.winfo_children():
            self.bind_drag_widget(child)

    def specific_frame_start_move(self, event):
        self._specific_frame_drag_start_x = event.x
        self._specific_frame_drag_start_y = event.y
        self._specific_frame_drag_scheduled = False
        self.lift()

    def on_specific_frame_move(self, event):
        def _do_drag(dx, dy):
            self.place(x=dx, y=dy)
            self._specific_frame_drag_scheduled = False

        x = self.winfo_x() + event.x - self._specific_frame_drag_start_x
        y = self.winfo_y() + event.y - self._specific_frame_drag_start_y
        # schedule placement every 2-3ms (throttling)
        if not self._specific_frame_drag_scheduled:
            self._specific_frame_drag_scheduled = True
            self.after(3, _do_drag, x, y)



class Ratings:
    pass




