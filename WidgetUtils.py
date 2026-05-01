from Protocol import *
from customtkinter import *
from PIL import Image

class ScrollableFrameBase(CTkScrollableFrame):
    def __init__(self, home_window, callback_send_data, callback_receive_confirmation, callback_update_user_info,
                 callback_update_buttons,on_click_destroy_specific_frame,width=300, height=300, **kwargs):
        super().__init__(master=home_window,width=width,height=height,**kwargs)
        self._internal_frame_look = None

        self._animating=False
        self._is_currently_editing = False


        self._callback_update_buttons = callback_update_buttons
        self._callback_send_data = callback_send_data
        self._callback_receive_confirmation = callback_receive_confirmation
        self._callback_update_user_info=callback_update_user_info
        self._callback_destroy_specific_frame=on_click_destroy_specific_frame

        self._previous = ""
        self._new_inner_frame = False
        self._placeholder_for_scrollbar = None  # adding a frame resets the scrollbar
        self._scheduled_animate=None

        self._entry_width=140
        self._entry_height=28
        self._btn_width=30
        self._btn_height=30

    def configure_inner_frame(self,entry_width,entry_height,btn_width,btn_height):
        self._entry_width=entry_width
        self._entry_height=entry_height
        self._btn_width=btn_width
        self._btn_height=btn_height


    def destroy_placeholder(self):
        if self._placeholder_for_scrollbar:
            self._placeholder_for_scrollbar.destroy()
            self._placeholder_for_scrollbar = None

    def place_placeholder(self):
        self._placeholder_for_scrollbar = CTkFrame(master=self, width=1, height=1, fg_color="transparent")
        self._placeholder_for_scrollbar.pack()

    def confirm_mode(self,current_entry:CTkEntry,current_btn:CTkButton):
        data=current_entry.get().strip()
        current_entry.delete(0,END)
        current_entry.insert(0,data)
        current_entry.configure(state="disabled")
        current_btn.configure(text="✎", text_color="white")
        self._callback_update_buttons("normal")
        self._is_currently_editing = False
        self._new_inner_frame = False
        current_entry.unbind('<Return>')

    def clear_frames(self):
        self.stop_animating()
        self._parent_canvas.yview_moveto(0.0)
        self._parent_canvas.update_idletasks()
        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
        try:
            for f in self.winfo_children():
                self.after(0,f.destroy)
        except: pass
        self.place_placeholder()
        self.destroy_placeholder()

    def move_down(self):
        self._parent_canvas.update_idletasks()
        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
        self._parent_canvas.yview_moveto(1.0)


    def set_internal_frame_look(self, **kwargs):
        self._internal_frame_look=kwargs

    def destroy_frame(self, current_frame):
        current_frame.destroy()
        self._is_currently_editing = False
        self._callback_update_buttons("normal")

    def set_animating(self,state):
        self._animating=state

    def start_animating(self):
        self._is_currently_editing=False
        self.clear_frames()
        self._callback_update_buttons("disabled")
        self.set_animating(True)


    def stop_animating(self):
        self.set_animating(False)
        if self._scheduled_animate:
            self.after_cancel(self._scheduled_animate)
            self._scheduled_animate = None
    def is_editing_another(self,current_state):
        return current_state == "disabled" and self._is_currently_editing or self._animating


class Ingredients(ScrollableFrameBase):
    def __init__(self, name, home_window, callback_send_data, callback_receive_confirmation, callback_update_buttons,
                 categorize_callback, callback_update_user_info,on_click_destroy_specific_frame,width=300, height=300,
                 **kwargs):

        super().__init__(home_window, callback_send_data, callback_receive_confirmation, callback_update_user_info,
                         callback_update_buttons,on_click_destroy_specific_frame,width, height, **kwargs)

        self._categorize_callback=categorize_callback
        self._name=name
    def add_ingredient(self):
        try:
            self.destroy_placeholder()
            self._callback_update_buttons("disabled")
            self._callback_destroy_specific_frame()
            self._is_currently_editing=True
            self._new_inner_frame=True
            self._previous=""
            #create the frame
            current_frame=CTkFrame(master=self, **self._internal_frame_look)
            current_frame.pack(pady=3,padx=2,fill="x",anchor='w')
            current_entry=CTkEntry(master=current_frame, width=self._entry_width, height=self._entry_height)
            current_entry.pack(padx=(4,3),pady=7,side="left")
            current_entry.focus()
            current_main_btn=CTkButton(master=current_frame, width=self._btn_width, height=self._btn_height, text="✓",
                                       text_color="green", fg_color="black", font=("Arial", 18),
                                       command=lambda: self.on_click_main_btn(current_entry,current_main_btn))
            current_main_btn.pack(padx=2,pady=5,side="left")
            current_categorize_btn = CTkButton(master=current_frame, width=self._btn_width, height=self._btn_height,
                                               text="🧺", text_color="gray",
                                               fg_color="black", font=("Ariel", 18),
                                               command=lambda: self.on_click_categorize(current_entry,current_frame))
            current_categorize_btn.pack(padx=2,pady=5,side="left")
            current_delete_btn=CTkButton(master=current_frame, width=self._btn_width, height=self._btn_height, text="🗑",
                                         text_color="red", fg_color="black", font=("Arial", 18),
                                         command=lambda: self.on_click_delete_btn(current_frame,current_entry))
            current_delete_btn.pack(padx=2,pady=5,side="left")
            current_entry.bind('<Return>',lambda event: self.on_click_main_btn(current_entry,current_main_btn))
        except Exception as e:
            write_to_log(f"exception {e}")

    def on_click_categorize(self,current_entry,current_frame):
        if self._is_currently_editing or self._animating:
            return
        self._categorize_callback(current_entry.get().strip(), current_frame, self._name)


    def get_name(self):
        return self._name

    def change_name(self,new_name):
        self._name=new_name

    def initiate_first_ingredients(self, user_data):
        self.start_animating()
        self.destroy_placeholder()
        def create_frames(i, data):
            # create the frame
            try:
                if i >= len(data) or not self._animating:
                    self.stop_animating()
                    self._callback_update_buttons("normal")
                    return
                current_frame = CTkFrame(master=self, **self._internal_frame_look)
                current_frame.pack(pady=3, padx=2, fill="x", anchor='w')
                current_entry = CTkEntry(master=current_frame, width=self._entry_width, height=self._entry_height)
                current_entry.pack(padx=(4,3),pady=7,side="left")
                current_entry.insert(0, data[i])
                current_entry.configure(state="disabled")
                current_confirm_btn = CTkButton(master=current_frame, width=self._btn_width, height=self._btn_height,
                                                text="✎", text_color="white",
                                                fg_color="black", font=("Arial", 18))
                current_confirm_btn.configure(
                    command=lambda entry=current_entry, btn=current_confirm_btn: self.on_click_main_btn(entry, btn))
                current_confirm_btn.pack(padx=2,pady=5,side="left")
                current_categorize_btn = CTkButton(master=current_frame, width=self._btn_width,
                                                   height=self._btn_height, text="🧺",
                                                   text_color="gray", fg_color="black", font=("Ariel", 18),
                                                   command=lambda entry=current_entry,
                                                                  frame=current_frame: self.on_click_categorize(entry,
                                                                                                                frame))
                current_categorize_btn.pack(padx=2,pady=5,side="left")
                current_delete_btn = CTkButton(master=current_frame, width=self._btn_width,
                                               height=self._btn_height, text="🗑",
                                               text_color="red", fg_color="black", font=("Arial", 18),
                                               command=lambda frame=current_frame,
                                                              entry=current_entry: self.on_click_delete_btn(frame,
                                                                                                            entry))
                current_delete_btn.pack(padx=2,pady=5,side="left")
                if self._animating:
                    self._scheduled_animate = self.after(40, create_frames, i + 1, data)

            except Exception as e:
                write_to_log(e)
        create_frames(0, user_data[self._name])

    def edit_mode(self, current_entry, current_btn):
        current_entry.configure(state="normal")
        current_btn.configure(text="✓", text_color="green")
        self._is_currently_editing = True
        self._callback_update_buttons("disabled")
        self._previous = current_entry.get()
        current_entry.focus()
        current_entry.bind('<Return>', lambda event: self.on_click_main_btn(current_entry, current_btn))

    def on_click_main_btn(self,current_entry:CTkEntry,current_btn:CTkButton):
        current_state = current_entry.cget("state")
        #do nothing if user is editing another button or animation is happening
        if self.is_editing_another(current_state):
            return
        #go to edit mode
        self._callback_destroy_specific_frame()
        if current_state=="disabled" and not self._is_currently_editing:
            self.edit_mode(current_entry,current_btn)
            return
        #user pressed confirm
        new_ingredient=current_entry.get().strip()
        if new_ingredient=="" or len(new_ingredient)>32:
            return
        #no changes where made
        if new_ingredient==self._previous:
            self.confirm_mode(current_entry,current_btn)
            return
        if self._previous!="":
            cmd="RENAME"
            data=pack_ingredient_data(self._name,new_ingredient,self._previous)
            self._callback_send_data(cmd, data)
        else:
            cmd="ADD"
            data=pack_ingredient_data(self._name, new_ingredient)
            self._callback_send_data(cmd, data)

        succeed=self._callback_receive_confirmation()
        if succeed=="200":
            self.confirm_mode(current_entry,current_btn)
            self._callback_update_user_info(cmd, data)



    def on_click_delete_btn(self,current_frame,current_entry):
        current_state=current_entry.cget("state")
        #do nothing if user is editing another button or animation is happening
        if self._is_currently_editing and current_state=="disabled" or self._animating:
            return
        #if the ingredient isn't saved yet in db delete locally
        if self._new_inner_frame:
            self._is_currently_editing = False
            self._new_inner_frame = False
            self.destroy_frame(current_frame)
            return
        if current_state=="disabled": #normal delete
            ingredient = current_entry.get().strip()
            data = pack_ingredient_data(self._name, ingredient)
            self._callback_send_data("DELETE", data)
            succeed=self._callback_receive_confirmation()
        else: #delete while editing
            ingredient = self._previous
            data = pack_ingredient_data(self._name, ingredient)
            self._callback_send_data("DELETE", data)
            succeed = self._callback_receive_confirmation()
        if succeed == "200":
            self._callback_destroy_specific_frame(ingredient)
            self._is_currently_editing=False
            self.destroy_frame(current_frame)
            self._callback_update_user_info("DELETE", data)

class Lists(ScrollableFrameBase):
    def __init__(self, home_window, callback_send_data, callback_receive_confirmation, callback_update_user_info,
                 callback_open_list, callback_close_list,callback_update_buttons,
                 on_click_destroy_specific_frame,width=300, height=300, **kwargs):
        super().__init__(home_window, callback_send_data, callback_receive_confirmation, callback_update_user_info,
                         callback_update_buttons,on_click_destroy_specific_frame,width, height, **kwargs)

        self._callback_open_list=callback_open_list
        self._callback_close_list=callback_close_list

    def add_list(self):
        try:
            self.destroy_placeholder()
            self._callback_destroy_specific_frame()
            self._callback_update_buttons("disabled")
            self._is_currently_editing = True
            self._new_inner_frame = True
            self._previous = ""
            current_frame = CTkFrame(master=self, **self._internal_frame_look)
            current_frame.pack(pady=3, padx=2, fill="x", anchor='w')
            current_entry = CTkEntry(master=current_frame, width=self._entry_width, height=self._entry_height,
                                     font=("Calibri",17))
            current_entry.pack(padx=10,pady=7,side="left")
            current_entry.focus()
            current_main_btn = CTkButton(master=current_frame, width=self._btn_width, height=self._btn_height, text="✓",
                                         text_color="green", fg_color="black", font=("Arial", 18),
                                         command=lambda: self.on_click_main_btn(current_entry, current_main_btn))
            current_main_btn.pack(padx=3,pady=5,side="left")
            current_open_btn = CTkButton(master=current_frame, width=self._btn_width, height=self._btn_height, text="📂",
                                         text_color="gray",
                                         fg_color="black", font=("Ariel", 18),
                                         command=lambda: self.on_click_open_list(current_entry))
            current_open_btn.pack(padx=3,pady=5,side="left")
            current_delete_btn = CTkButton(master=current_frame, width=self._btn_width, height=self._btn_height,
                                           text="🗑", text_color="red", fg_color="black", font=("Arial", 18),
                                           command=lambda: self.on_click_delete_btn(current_frame, current_entry))
            current_delete_btn.pack(padx=3,pady=5,side="left")
            current_entry.bind('<Return>', lambda event: self.on_click_main_btn(current_entry,
                                                                                current_main_btn))
        except Exception as e:
            write_to_log(f"loading exception {e}")

    def initiate_first_lists(self, user_data):
        if len(user_data) == 1:
            return
        self.start_animating()
        self.destroy_placeholder()

        def create_frames(i, data):
            try:
                if i >= len(data) or not self._animating:
                    self.stop_animating()
                    self._callback_update_buttons("normal")
                    return
                if data[i] != "Main":
                    current_frame = CTkFrame(master=self, **self._internal_frame_look)
                    current_frame.pack(pady=3, padx=2, fill="x", anchor='w')
                    current_entry = CTkEntry(master=current_frame, width=self._entry_width, height=self._entry_height,
                                             font=("Calibri", 17))
                    current_entry.pack(padx=10,pady=7,side="left")
                    current_entry.insert(0, data[i])
                    current_entry.configure(state="disabled")
                    current_confirm_btn = CTkButton(master=current_frame, width=self._btn_width, height=self._btn_height,
                                                    text="✎",
                                                    text_color="white", fg_color="black", font=("Arial", 18))
                    current_confirm_btn.configure(
                        command=lambda entry=current_entry, btn=current_confirm_btn: self.on_click_main_btn(entry, btn))
                    current_confirm_btn.pack(padx=3,pady=5,side="left")
                    current_open_btn = CTkButton(master=current_frame, width=self._btn_width, height=self._btn_height,
                                                 text="📂", text_color="gray",
                                                 fg_color="black", font=("Ariel", 18),
                                                 command=lambda entry=current_entry: self.on_click_open_list(entry))
                    current_open_btn.pack(padx=3,pady=5,side="left")
                    current_delete_btn = CTkButton(master=current_frame, width=self._btn_width, height=self._btn_height,
                                                   text="🗑",
                                                   text_color="red", fg_color="black", font=("Arial", 18),
                                                   command=lambda entry=current_entry,
                                                                  frame=current_frame: self.on_click_delete_btn(frame,
                                                                                                                entry))
                    current_delete_btn.pack(padx=3,pady=5,side="left")
                if self._animating:
                    self._scheduled_animate = self.after(50, create_frames, i + 1, data)
            except Exception as e:
                write_to_log(e)

        create_frames(0, list(user_data.keys()))

    def on_click_main_btn(self,current_entry:CTkEntry,current_btn:CTkButton):
        current_state = current_entry.cget("state")
        #user pressed to edit ->go to edit mode and do nothing else
        if self.is_editing_another(current_state):
            return
            # user pressed to edit ->go to edit mode and do nothing else
        self._callback_destroy_specific_frame()
        if current_state == "disabled" and not self._is_currently_editing:
            self.edit_mode(current_entry, current_btn)
            return
        #user pressed confirm
        new_list=current_entry.get().strip()
        if new_list=="" or len(new_list)>24:
            return
        if new_list == self._previous:
            self.confirm_mode(current_entry, current_btn)
            return
        if self._previous!="":
            cmd="RENAME_LIST"
            data = pack_list_data(new_list,self._previous)
            self._callback_send_data(cmd, data)
        else:
            cmd="ADD_LIST"
            data=pack_list_data(new_list)
            self._callback_send_data(cmd, data)
        succeed=self._callback_receive_confirmation()
        if succeed=="200":
            self.confirm_mode(current_entry,current_btn)
            self._callback_update_user_info(cmd, data)
            self.on_click_open_list(current_entry)

    def edit_mode(self, current_entry, current_btn):
        self._callback_close_list()
        current_entry.configure(state="normal")
        current_btn.configure(text="✓", text_color="green")
        self._is_currently_editing = True
        self._callback_update_buttons("disabled")
        self._previous = current_entry.get()
        current_entry.focus()
        current_entry.bind('<Return>', lambda event: self.on_click_main_btn(current_entry, current_btn))

    def on_click_open_list(self,current_entry):
        if self._is_currently_editing:
            return
        list_name=current_entry.get()
        self._callback_open_list(list_name)

    def on_click_delete_btn(self, current_frame, current_entry):
        current_state = current_entry.cget("state")
        if self._is_currently_editing and current_state == "disabled" or self._animating:  # deleting another button while editing
            return
        if self._new_inner_frame:  # if not saved yet delete in client only
            self._is_currently_editing = False
            self._new_inner_frame = False
            self.destroy_frame(current_frame)
            return
        if current_state == "disabled":  # no reason to send delete on nothing or if new ingredient
            list_name=current_entry.get().strip()
            data = pack_list_data(list_name)
        else: #delete list that wasn't saved
            data = pack_list_data(self._previous)
        self._callback_send_data("DELETE_LIST", data)
        succeed = self._callback_receive_confirmation()
        if succeed == "200":
            self.destroy_frame(current_frame)
            self._callback_close_list(data['list_name'])
            self._callback_update_user_info("DELETE_LIST", data)
            self._callback_destroy_specific_frame()


class CategorizeListFrame(CTkFrame):
    def __init__(self,_home_window,ingredient,ingredient_frame,list_name,callback_destroy_categorize_frame,
                 callback_destroy_error_frame,callback_on_click_select,**kwargs):
        super().__init__(master=_home_window,**kwargs)

        self._ingredient=ingredient
        self._ingredient_frame=ingredient_frame

        self._list_name=list_name

        self._callback_destroy_categorize_frame=callback_destroy_categorize_frame
        self._callback_destroy_error_frame=callback_destroy_error_frame
        self._callback_on_click_select=callback_on_click_select

        self._is_animating=False

        self._schedule_categorize_list_frame=None
        self._scrollable_frame=None
        self.create_ui()

    def set_animating(self,state):
        self._is_animating=state
    def is_animating(self):
        return self._is_animating

    def start_animating(self):
        self._callback_destroy_error_frame()
        self.set_animating(True)

    def stop_animating(self):
        self.set_animating(False)
        if self._schedule_categorize_list_frame:
            self.after_cancel(self._schedule_categorize_list_frame)
            self._schedule_categorize_list_frame = None

    def destroy_categorize_frame(self):
        self.stop_animating()
        self.destroy()

    def create_ui(self):
        self._scrollable_frame = CTkScrollableFrame(master=self, width=250, height=320,
                                                    corner_radius=15
                                                    , border_color="blue", border_width=3)
        self._scrollable_frame.pack()
        ingredient_name = CTkLabel(master=self._scrollable_frame, text=self._ingredient,
                                   font=("Calibri", 30, "bold", "underline"),
                                   wraplength=150)
        ingredient_name.pack(padx=(0, 100), pady=2)
        btn_back = CTkButton(self._scrollable_frame, text="Back", height=30, width=80, text_color="white",
                             hover_color="#6A3DB4",
                             font=("Calibri", 17), fg_color="#7C4CC2", command=self._callback_destroy_categorize_frame)
        btn_back.place(relx=1.0, x=-10, y=5, anchor="ne")
        self.update_idletasks()

    def initiate_categorize_list_frame(self,user_data):
        try:
            if len(user_data)==1:
                return
            def create_frames(i):
                if i >= len(user_data):
                    self.stop_animating()
                    return
                if user_data[i] != self._list_name:
                    current_frame = CTkFrame(master=self._scrollable_frame, width=80, height=40, corner_radius=28,
                                             fg_color="#5B5FD9")
                    current_frame.pack(pady=3, padx=5, fill="x", anchor='w', )
                    current_entry = CTkEntry(master=current_frame)
                    current_entry.place(x=5, y=7)
                    current_entry.insert(0, user_data[i])
                    current_entry.configure(state="disabled")
                    current_select_btn = CTkButton(master=current_frame,
                                                   width=50, height=25, text="Select", text_color="#5B5FD9",
                                                   fg_color="black", font=("Arial", 18),
                                                   command=lambda entry=current_entry,
                                                                  frame=self._ingredient_frame: self._callback_on_click_select(
                                                       self._ingredient, entry.get(), frame))
                    current_select_btn.place(x=150, y=7)
                self._schedule_categorize_list_frame = self.after(20, create_frames, i + 1)

            self.start_animating()
            create_frames(0)
        except Exception as e:
            self.stop_animating()
            write_to_log(e)

    def get_ingredient_name(self):
        return self._ingredient

class TemporaryFrame(CTkFrame):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self._schedule_hide = None
        self._icon_label = None
        self._icon=None
        self._text = None

    def cancel_schedule_hide(self):
        if self._schedule_hide:
            self.after_cancel(self._schedule_hide)

    def forget_frame(self):
        self.cancel_schedule_hide()
        self.place_forget()

    def hide(self):
        self._schedule_hide = None
        self.place_forget()

    def plan_future_hide(self):
        self.cancel_schedule_hide()
        self._schedule_hide = self.after(1200, self.hide)

    def change_text(self,message):
        if self._text:
            self._text.configure(text=message)


class ErrorFrame(TemporaryFrame):
    def __init__(self,message,**kwargs):
        super().__init__(**kwargs)

        self._icon= CTkImage(Image.open(r"Images\error_icon.png"), size=(30, 30))
        self.create_ui(message)

    def create_ui(self,message):
        self._icon_label = CTkLabel(master=self, text="", image=self._icon)
        self._text = CTkLabel(master=self,font=("Segoe UI", 20, "bold"),text=message)
        self.lift()
        self._icon_label.pack(side="left", padx=5, pady=20)
        self._text.pack(side="left", padx=5, pady=20)
        self.plan_future_hide()

class SuccessFrame(TemporaryFrame):
    def __init__(self,message,**kwargs):
        super().__init__(**kwargs)

        self._icon= CTkImage(Image.open(r"Images\success_icon.png"), size=(30, 30))
        self.create_ui(message)


    def create_ui(self,message):
        self._icon_label = CTkLabel(master=self, text="", image=self._icon)
        self._text = CTkLabel(master=self,font=("Segoe UI", 20, "bold"),text=message)
        self.lift()
        self._icon_label.pack(side="left", padx=5, pady=20)
        self._text.pack(side="left", padx=5, pady=20)
        self.plan_future_hide()









