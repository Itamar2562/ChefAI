from Protocol import *

class ScrollableFrameBase(CTkScrollableFrame):
    def __init__(self, home_window, callback_send_data, callback_receive_confirmation, callback_update_user_info,
                 callback_update_buttons, width=300, height=300, **kwargs):
        super().__init__(master=home_window,width=width,height=height,**kwargs)
        self.callback_update_buttons = callback_update_buttons
        self.is_currently_editing = False
        self.new = False
        self._internal_ingredient_look = None
        self.callback_send_data = callback_send_data
        self.callback_receive_confirmation = callback_receive_confirmation
        self.callback_update_user_info=callback_update_user_info
        self.previous = ""
        self.animating=False
        self._placeholder_for_scrollbar = None  # adding a frame resets the scrollbar

    def confirm_mode(self,current_entry:CTkEntry,current_btn:CTkButton):
        #make sure there isn't any whitesspaces
        write_to_log("confirm mode")
        data=current_entry.get().strip()
        current_entry.delete(0,END)
        current_entry.insert(0,data)
        current_entry.configure(state="disabled")
        current_btn.configure(text="✎", text_color="white")
        self.callback_update_buttons("normal")
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
            self._parent_canvas.after(0,self._parent_frame.destroy)
            self.after(0,self.destroy)

    def set_internal_ingredient_look(self,**kwargs):
        self._internal_ingredient_look=kwargs

    def destroy_frame(self, current_frame):
        current_frame.destroy()
        self.callback_update_buttons("normal")
        self.is_currently_editing = False

    def is_editing(self):
        return self.is_currently_editing

    def is_animating(self):
        return self.animating


class Ingredient(ScrollableFrameBase):
    def __init__(self, name, home_window, callback_send_data, callback_receive_confirmation, callback_update_buttons,
                 categorize_callback, callback_update_user_info, width=300, height=300, **kwargs):
        super().__init__(home_window, callback_send_data, callback_receive_confirmation, callback_update_user_info,
                         callback_update_buttons, width, height, **kwargs)

        self.categorize_callback=categorize_callback
        self.name=name

    def add_ingredient(self):
        if self._placeholder_for_scrollbar:
            self._placeholder_for_scrollbar.destroy()
            self._placeholder_for_scrollbar=None
        self.callback_update_buttons("disabled")
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
        current_categorize_btn = CTkButton(master=current_frame, width=30, height=30, text="🧺", text_color="gray",
                                           fg_color="black", font=("Ariel", 18),
                                           command=lambda: self.on_click_categorize(current_entry,current_frame))
        current_categorize_btn.place(x=185, y=5)
        current_delete_btn=CTkButton(master=current_frame,width=30,height=30,text="🗑",text_color="red",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_delete_btn(current_frame,current_entry))
        current_delete_btn.place(x=220,y=5)
        current_entry.bind('<Return>',lambda event: self.on_click_main_btn(current_entry,current_main_btn))

    def on_click_categorize(self,current_entry,current_frame):
        if self.is_currently_editing:
            return
        self.categorize_callback(current_entry.get().strip(),current_frame)

    def get_name(self):
        return self.name
    def change_name(self,new_name):
        self.name=new_name

    def initiate_first_ingredients(self,user_data):
        if self._placeholder_for_scrollbar:
            self._placeholder_for_scrollbar.after(0,self._placeholder_for_scrollbar.destroy)
            self._placeholder_for_scrollbar = None
        try:
            self.callback_update_buttons("disabled")
            self.animating=True
            for ingredient in user_data[self.name]:
                # create the frame
                current_frame=CTkFrame(master=self,**self._internal_ingredient_look)
                current_frame.pack(pady=3, padx=2, fill="x",anchor='w')
                current_entry = CTkEntry(master=current_frame)
                current_entry.place(x=5, y=7)
                current_entry.insert(0,ingredient)
                current_entry.configure(state="disabled")
                current_confirm_btn = CTkButton(master=current_frame, width=30, height=30, text="✎",text_color="white",
                                                fg_color="black", font=("Arial", 18))
                current_confirm_btn.configure(command=lambda entry=current_entry, btn=current_confirm_btn: self.on_click_main_btn(entry, btn))
                current_confirm_btn.place(x=150, y=5)
                current_categorize_btn = CTkButton(master=current_frame, width=30, height=30, text="🧺",
                                                   text_color="gray",fg_color="black", font=("Ariel", 18),
                                                   command=lambda entry=current_entry, frame=current_frame: self.on_click_categorize(entry,frame))
                current_categorize_btn.place(x=185, y=5)
                current_delete_btn = CTkButton(master=current_frame, width=30, height=30, text="🗑",
                                               text_color="red",fg_color="black", font=("Arial", 18),
                                               command=lambda frame=current_frame,entry=current_entry: self.on_click_delete_btn(frame, entry))
                current_delete_btn.place(x=220, y=5)
                time.sleep(0.05)
            self.callback_update_buttons("normal")
            self.animating=False
        except Exception as e:
            self.animating=False
            write_to_log(f"initiate_first_ingredients_ exception: {e}")
            return

    def edit_mode(self, current_entry, current_btn):
        current_entry.configure(state="normal")
        current_btn.configure(text="✓", text_color="green")
        self.is_currently_editing = True
        self.callback_update_buttons("disabled")
        self.previous = current_entry.get()
        current_entry.focus()
        current_entry.bind('<Return>', lambda event: self.on_click_main_btn(current_entry, current_btn))

    def on_click_main_btn(self,current_entry:CTkEntry,current_btn:CTkButton):
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
        if new_ingredient==self.previous:
            self.confirm_mode(current_entry,current_btn)
            return
        data=[self.name,self.previous,new_ingredient]
        self.callback_send_data("ADD",data)
        succeed=self.callback_receive_confirmation()
        if succeed=="ok":
            self.confirm_mode(current_entry,current_btn)
            self.callback_update_user_info("ADD",data)


    def on_click_delete_btn(self,current_frame,current_entry):
        current_state=current_entry.cget("state")
        #Dont let user delete other frames while editing or delete while editing a current frame
        #only delete a frame if its a new one or not currently editing
        if (self.is_currently_editing and current_state=="disabled")or( not self.new and current_state=="normal"):
            return
        data=[self.name,current_entry.get().strip()]
        if data!="" and not self.new: #no reason to send delete on nothing or if new ingredient
            self.callback_send_data("DELETE",data)
            succeed=self.callback_receive_confirmation()
            if succeed=="ok":
                self.destroy_frame(current_frame)
                self.callback_update_user_info("DELETE",data)
        else:
            self.new=False
            self.destroy_frame(current_frame)


class DynamicList(ScrollableFrameBase):
    def __init__(self, home_window, callback_send_data, callback_receive_confirmation, callback_update_user_info, callback_open_list, callback_close_list,callback_update_buttons, width, height, **kwargs):
        super().__init__(home_window, callback_send_data, callback_receive_confirmation, callback_update_user_info, callback_update_buttons, width, height, **kwargs)

        self.callback_open_list=callback_open_list
        self.callback_close_list=callback_close_list
        self.add_add_ingredient_btn=None
        self.lists=[]

    def add_list(self):
        if self._placeholder_for_scrollbar:
            self._placeholder_for_scrollbar.destroy()
            self._placeholder_for_scrollbar = None

        self.callback_update_buttons("disabled")
        self.is_currently_editing = True
        self.new = True
        self.previous = ""
        current_frame = CTkFrame(master=self, **self._internal_ingredient_look)
        current_frame.pack(pady=3, padx=2, fill="x", anchor='w')
        current_entry = CTkEntry(master=current_frame,width=150,height=40,font=("Calibri",17))
        current_entry.place(x=5, y=7)
        current_entry.focus()
        current_main_btn = CTkButton(master=current_frame, width=40, height=40, text="✓", text_color="green", fg_color="black", font=("Arial", 18),command=lambda: self.on_click_main_btn(current_entry, current_main_btn))
        current_main_btn.place(x=170, y=5)
        current_open_btn = CTkButton(master=current_frame, width=40, height=40, text="📂", text_color="gray",
                                     fg_color="black", font=("Ariel", 18), command=lambda: self.on_click_open_list(current_entry))
        current_open_btn.place(x=220, y=5)
        current_delete_btn = CTkButton(master=current_frame, width=40, height=40, text="🗑", text_color="red",fg_color="black", font=("Arial", 18),command=lambda: self.on_click_delete_btn(current_frame, current_entry))
        current_delete_btn.place(x=270, y=5)
        current_entry.bind('<Return>', lambda event: self.on_click_main_btn(current_entry, current_main_btn))

    def initiate_first_lists(self,user_data):
        if self._placeholder_for_scrollbar:
            self._placeholder_for_scrollbar.after(0,self._placeholder_for_scrollbar.destroy)
            self._placeholder_for_scrollbar=None
        self.callback_update_buttons("disabled")
        # create the frame
        try:
            self.animating=True
            for curr_list in user_data.keys():
                if curr_list=="Main":
                    continue
                self.lists.append(curr_list)
                current_frame=CTkFrame(master=self,**self._internal_ingredient_look)
                current_frame.pack(pady=3, padx=2, fill="x",anchor='w')
                current_entry = CTkEntry(master=current_frame,width=150,height=40,font=("Calibri",17))
                current_entry.place(x=5, y=7)
                current_entry.insert(0,curr_list)
                current_entry.configure(state="disabled")
                current_confirm_btn = CTkButton(master=current_frame, width=40, height=40, text="✎",text_color="white", fg_color="black", font=("Arial", 18))
                current_confirm_btn.configure(command=lambda entry=current_entry,btn=current_confirm_btn: self.on_click_main_btn(entry, btn))
                current_confirm_btn.place(x=170, y=5)
                current_open_btn = CTkButton(master=current_frame, width=40, height=40, text="📂", text_color="gray",
                                             fg_color="black", font=("Ariel", 18),
                                             command=lambda entry=current_entry: self.on_click_open_list(entry))
                current_open_btn.place(x=220, y=5)
                current_delete_btn = CTkButton(master=current_frame, width=40, height=40, text="🗑",
                                               text_color="red",fg_color="black", font=("Arial", 18),
                                               command=lambda entry=current_entry,frame=current_frame: self.on_click_delete_btn(frame, entry))
                current_delete_btn.place(x=270, y=5)
                time.sleep(0.05)
            self.callback_update_buttons(state="normal")
            self.animating=False
        except Exception as e:
            self.animating=False
            write_to_log(f"list animation error: {e}")
            return

    def get_lists(self):
        return self.lists

    def on_click_main_btn(self,current_entry:CTkEntry,current_btn:CTkButton):
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
        if new_list == self.previous:
            self.confirm_mode(current_entry, current_btn)
            return
        data=[self.previous,new_list]
        self.callback_send_data("LIST",data)
        succeed=self.callback_receive_confirmation()
        if succeed=="ok":
            self.confirm_mode(current_entry,current_btn)
            self.callback_update_user_info("ADD_LIST",data)
            self.on_click_open_list(current_entry)
            self.lists = [new_list if item == self.previous else item for item in self.lists]


    def edit_mode(self, current_entry, current_btn):
        self.callback_close_list()
        current_entry.configure(state="normal")
        current_btn.configure(text="✓", text_color="green")
        self.is_currently_editing = True
        self.callback_update_buttons("disabled")
        self.previous = current_entry.get()
        current_entry.focus()
        current_entry.bind('<Return>', lambda event: self.on_click_main_btn(current_entry, current_btn))


    def on_click_open_list(self,current_entry):
        if self.is_currently_editing:
            return
        list_name=current_entry.get()
        self.callback_open_list(list_name)

    def on_click_delete_btn(self, current_frame, current_entry):
        current_state = current_entry.cget("state")
        # Dont let user delete other frames while editing or delete while editing a current frame
        # only delete a frame if its a new one or not currently editing
        if (self.is_currently_editing and current_state == "disabled") or (not self.new and current_state == "normal"):
            return
        data = [current_entry.get().strip()]
        if data != "" and not self.new:  # no reason to send delete on nothing or if new ingredient
            self.callback_send_data("DELETE_LIST", data)
            succeed = self.callback_receive_confirmation()
            if succeed=="ok":
                self.lists.remove(data[0])
                self.destroy_frame(current_frame)
                self.callback_close_list(data[0])
                self.callback_update_user_info("DELETE_LIST",data)
        else: #delete list that wasn't saved
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




