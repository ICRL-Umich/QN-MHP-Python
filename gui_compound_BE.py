# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 09:27:13 2024

@author: wyuanc
"""


"""GUI windows used to define parameters for compound behavior elements."""

import tkinter as tk
from tkinter import ttk 
from utility import save_user_input as save
from utility import look_for_ls, has_saved_input


def _task_index(task_no):
    """Return the string task index used across the existing codebase."""
    return str(task_no)


def _load_task_dict(filename):
    if not has_saved_input(filename):
        return {}
    try:
        data = save(1).load_var(filename)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _load_task_value(filename, task_no, default=''):
    data = _load_task_dict(filename)
    key = _task_index(task_no)
    if key in data:
        return data[key]
    # Backward compatibility for files accidentally saved with integer keys.
    try:
        int_key = int(task_no)
        if int_key in data:
            return data[int_key]
    except Exception:
        pass
    return default


def _save_task_value(filename, task_no, value):
    data = _load_task_dict(filename)
    key = _task_index(task_no)
    # Normalize any old integer-key entry to the string-key format.
    try:
        int_key = int(task_no)
        if int_key in data and key not in data:
            data[key] = data.pop(int_key)
    except Exception:
        pass
    data[key] = value
    save(saved).save_var(data, filename)
    return value


def _set_combobox_from_saved(combobox, values, filename, task_no):
    saved_value = _load_task_value(filename, task_no, '')
    if saved_value in values:
        combobox.current(values.index(saved_value))


    
class GUI_BE_Lookfor:
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
        self.task_no=task_no
        self.task_key=_task_index(task_no)
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=1000    #window width
        wh=550#window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Look_For - Task ' + str(self.task_no))
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no
        global judgei_target_dic
        judgei_target_dic = _load_task_dict(path+'/judgei_target_dic.txt')
        if self.task_key not in judgei_target_dic:
            judgei_target_dic[self.task_key] = {}
        # Show the window promptly on macOS before any additional GUI work.
        self.root.update_idletasks()
        self.root.update()
        self.Lookfor()
        self.show_initial_fixation()
        self.root.update_idletasks()
        self.root.update()
        
    def Lookfor(self):

        '''
        self.list_button=tk.Button(self.root,text='1.Open the list of all the items',font=("Times New Roman",15),command=self.lookfor_list)           
        self.list_button.pack(pady=30)
        '''
        
        
        self.judge_i={}

        tk.Label(self.root,text='1. Choose the identity to be judged',font=("Times New Roman",15)).pack()        
        
        value_identity=['Text','Color']
        self.judge_i[self.task_key]=ttk.Combobox(
            master=self.root,
            width=15,
            height=5,
            state='readonly',
            cursor='arrow',
            values=value_identity, 
            font=('bold',10)
            )
        self.judge_i[self.task_key].bind('<<ComboboxSelected>>',self.judge_identity)
        self.judge_i[self.task_key].pack(pady=30)
        
        saved_target = _load_task_value(path+'/judgei_target_dic.txt', self.task_no, {})
        if isinstance(saved_target, dict) and saved_target.get('identity') in value_identity:
            self.judge_i[self.task_key].current(value_identity.index(saved_target['identity']))
            judgei_target_dic[self.task_key]['identity'] = saved_target['identity']

        tk.Button(self.root,text='2. Choose the value of the target identity:',font=("Times New Roman",15),command=self.target_button).pack(pady=30)
        
        tk.Button(self.root,text='Save',font=("Times New Roman",15),command=self.save).pack(pady=30)
        
    def show_initial_fixation(self):
        """Show the initial eye fixation and physical screen settings."""
        from eye_movement_model import (INITIAL_FIXATION_MODE, INITIAL_FIXED_POSITION,
                                        SCREEN_WIDTH_MM, SCREEN_HEIGHT_MM,
                                        VIEWING_DISTANCE_MM)
        import eye_movement_model as eye_model
        if INITIAL_FIXATION_MODE == 'center':
            x_mm, y_mm = SCREEN_WIDTH_MM / 2, SCREEN_HEIGHT_MM / 2
            location = f'({x_mm:g}, {y_mm:g}) mm (screen center)'
        elif INITIAL_FIXATION_MODE == 'fixed':
            x_norm, y_norm = INITIAL_FIXED_POSITION
            x_mm = x_norm * SCREEN_WIDTH_MM / 100
            y_mm = y_norm * SCREEN_HEIGHT_MM / 100
            location = f'({x_mm:g}, {y_mm:g}) mm (fixed)'
        else:
            location = 'Random within screen bounds (selected at simulation start)'
        tk.Label(self.root, text='Initial Eye Position: ' + location,
                 font=('Times New Roman', 13)).pack(pady=5)
        tk.Label(self.root,
                 text=(f'Screen: {SCREEN_WIDTH_MM:g} x {SCREEN_HEIGHT_MM:g} mm; '
                       f'Viewing distance: {VIEWING_DISTANCE_MM:g} mm'),
                 font=('Times New Roman', 12)).pack(pady=3)
        tk.Label(self.root,
                 text='Edit eye_movement_model.py for initial mode; '
                      'visual_search_layout.json for screen and targets.',
                 font=('Times New Roman', 10)).pack(pady=3)

    def lookfor_list(self):
        window=tk.Toplevel(self.root)
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=1000#window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        window.title('Look_For List')
        window.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        window.mainloop()
        
    def text(self):
        judgei_target_dic[self.task_key]['identity']='Text'
        self.window=tk.Toplevel(self.root)
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=200#window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.window.title('Choose Text Target')
        self.window.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.value_target=[]
        tk.Label(self.window,text='2. Choose Text Target', font=("Times New Roman",15)).pack(pady=30)
        for item in look_for_ls:
            self.value_target.append(item[1])
        self.judge_v={}
        self.judge_v[self.task_key]=ttk.Combobox(
            master=self.window,
            width=15,
            height=5,
            state='readonly',
            cursor='arrow',
            values=self.value_target, 
            font=('bold',10)
            )
        self.judge_v[self.task_key].bind('<<ComboboxSelected>>',self.judge_target_text)
        self.judge_v[self.task_key].pack()
        
        saved_target = _load_task_value(path+'/judgei_target_dic.txt', self.task_no, {})
        if isinstance(saved_target, dict) and saved_target.get('value') in self.value_target:
            self.judge_v[self.task_key].current(self.value_target.index(saved_target['value']))
            judgei_target_dic[self.task_key]['value'] = saved_target['value']
        
        ok=tk.Button(self.window, text='OK',font=("Times New Roman",15),command=self.ok)
        ok.pack(pady=30)
        
        
    def color(self):
        judgei_target_dic[self.task_key]['identity']='Color'
        self.window=tk.Toplevel(self.root)
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=200#window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.window.title('2. Choose Color Target')
        self.window.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        
        tk.Label(self.window,text='2. Choose Color Target', font=("Times New Roman",15)).pack(pady=30)
        self.value_target=[]
        for item in look_for_ls:
            self.value_target.append(item[2])
        self.judge_v={}
        self.judge_v[self.task_key]=ttk.Combobox(
            master=self.window,
            width=15,
            height=5,
            state='readonly',
            cursor='arrow',
            values=self.value_target, 
            font=('bold',10)
            )
        self.judge_v[self.task_key].bind('<<ComboboxSelected>>',self.judge_target_color)
        self.judge_v[self.task_key].pack()
        
        saved_target = _load_task_value(path+'/judgei_target_dic.txt', self.task_no, {})
        if isinstance(saved_target, dict) and saved_target.get('value') in self.value_target:
            self.judge_v[self.task_key].current(self.value_target.index(saved_target['value']))
            judgei_target_dic[self.task_key]['value'] = saved_target['value']
        
        ok=tk.Button(self.window,text='OK',font=("Times New Roman",15),command=self.ok)
        ok.pack(pady=30)
        
        
    def judge_identity(self,*arg):
        judgei_target_dic[self.task_key]['identity']=self.judge_i[self.task_key].get()
        
    
    def target_button(self):
        if judgei_target_dic[self.task_key].get('identity')=='Text':
            self.text()
        else:
            self.color()
    
    def judge_target_text(self,*arg):
   
        judgei_target_dic[self.task_key]['value']=self.judge_v[self.task_key].get()
    
    
    
    def judge_target_color(self,*arg):  
               
        judgei_target_dic[self.task_key]['value']=self.judge_v[self.task_key].get()
        
    def ok (self):
        save(saved).save_var(judgei_target_dic, path+'/judgei_target_dic.txt')
        self.window.destroy()
        
    def save (self):
        save(saved).save_var(judgei_target_dic, path+'/judgei_target_dic.txt')
        self.root.destroy()
        

class GUI_BE_track1D:
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
        self.task_no=task_no
        self.task_key=_task_index(task_no)
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=500 #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Tracking_1D - Task ' + str(self.task_no))
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no
        tk.Label(self.root,text='Enter cursor starting location: (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track1D_b_x_cursor={}
        
        self.track1D_b_x_cursor[self.task_no]=tk.Entry(self.root,width=20)
        self.track1D_b_x_cursor[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track1D_b_x_cursor[self.task_no].insert(0, str(_load_task_value(path+'/track1D_b_x_cursor.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Enter target starting location: (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track1D_b_x_target={}
        
        self.track1D_b_x_target[self.task_no]=tk.Entry(self.root,width=20)
        self.track1D_b_x_target[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track1D_b_x_target[self.task_no].insert(0, str(_load_task_value(path+'/track1D_b_x_target.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Select target movement track1D_freq:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track1D_b_freq = ['Slow','Medium','Quick']
        
        self.track1D_b_freq={}
        self.track1D_b_freq[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track1D_b_freq, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track1D_b_freq[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track1D_b_freq)):
                if _load_task_value(path+'/track1D_b_freq.txt', self.task_no, '')==value_track1D_b_freq[item]:
                    self.track1D_b_freq[self.task_no].current(item)
        
        
        tk.Label(self.root,text='Select target movement track1D_amp:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track1D_b_amp = ['Small','Medium','Large']
        self.track1D_b_amp={}
        self.track1D_b_amp[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track1D_b_amp, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track1D_b_amp[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track1D_b_amp)):
                if _load_task_value(path+'/track1D_b_amp.txt', self.task_no, '')==value_track1D_b_amp[item]:
                    self.track1D_b_amp[self.task_no].current(item)
        
        tk.Label(self.root,text='Select response method:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track1D_b_response = ['Click mouse','Press keyboard']
        
        self.track1D_b_response={}
        self.track1D_b_response[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track1D_b_response, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track1D_b_response[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track1D_b_response)):
                if _load_task_value(path+'/track1D_b_response.txt', self.task_no, '')==value_track1D_b_response[item]:
                    self.track1D_b_response[self.task_no].current(item)
        
        self.Button_ok=tk.Button(self.root,text='OK',font=16,command=self.entry_event)
        self.Button_ok.pack()
  
    def entry_event(self):
        global track1D_b_x_cursor, track1D_b_x_target, track1D_b_freq, track1D_b_amp, track1D_b_response
        try:
            track1D_b_x_cursor = int(self.track1D_b_x_cursor[self.task_no].get())
            if track1D_b_x_cursor < 0 or  track1D_b_x_cursor > 100:
                raise ValueError
            _save_task_value(path+'/track1D_b_x_cursor.txt', self.task_no, track1D_b_x_cursor)
            
            track1D_b_x_target = int(self.track1D_b_x_target[self.task_no].get())
            if track1D_b_x_target < 0 or track1D_b_x_target> 100:
                raise ValueError
            _save_task_value(path+'/track1D_b_x_target.txt', self.task_no, track1D_b_x_target)
            
            track1D_b_freq = self.track1D_b_freq[self.task_no].get()
            _save_task_value(path+'/track1D_b_freq.txt', self.task_no, track1D_b_freq)
            
            track1D_b_amp = self.track1D_b_amp[self.task_no].get()
            _save_task_value(path+'/track1D_b_amp.txt', self.task_no, track1D_b_amp)
            
            track1D_b_response = self.track1D_b_response[self.task_no].get()
            _save_task_value(path+'/track1D_b_response.txt', self.task_no, track1D_b_response)
            
            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return 
            
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_label = tk.Label(error_window, text="Please enter an integer between 1 and 100 for the cursor starting location.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()        

class GUI_BE_track1D_1w:
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
        self.task_no=task_no
        self.task_key=_task_index(task_no)
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=500 #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Tracking_1D_1W - Task ' + str(self.task_no))
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no
        tk.Label(self.root,text='Enter cursor starting location: (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track1D_1w_x_cursor={}
        
        self.track1D_1w_x_cursor[self.task_no]=tk.Entry(self.root,width=20)
        self.track1D_1w_x_cursor[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track1D_1w_x_cursor[self.task_no].insert(0, str(_load_task_value(path+'/track1D_1w_x_cursor.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Enter target starting location: (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track1D_1w_x_target={}
        
        self.track1D_1w_x_target[self.task_no]=tk.Entry(self.root,width=20)
        self.track1D_1w_x_target[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track1D_1w_x_target[self.task_no].insert(0, str(_load_task_value(path+'/track1D_1w_x_target.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Select target movement track1D_freq:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track1D_1w_freq = ['Slow','Medium','Quick']
        
        self.track1D_1w_freq={}
        self.track1D_1w_freq[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track1D_1w_freq, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track1D_1w_freq[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track1D_1w_freq)):
                if _load_task_value(path+'/track1D_1w_freq.txt', self.task_no, '')==value_track1D_1w_freq[item]:
                    self.track1D_1w_freq[self.task_no].current(item)
        
        
        tk.Label(self.root,text='Select target movement track1D_amp:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track1D_1w_amp = ['Small','Medium','Large']
        self.track1D_1w_amp={}
        self.track1D_1w_amp[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track1D_1w_amp, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track1D_1w_amp[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track1D_1w_amp)):
                if _load_task_value(path+'/track1D_1w_amp.txt', self.task_no, '')==value_track1D_1w_amp[item]:
                    self.track1D_1w_amp[self.task_no].current(item)
        
        tk.Label(self.root,text='Select response method:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track1D_1w_response = ['Click mouse','Press keyboard']
        
        self.track1D_1w_response={}
        self.track1D_1w_response[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track1D_1w_response, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track1D_1w_response[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track1D_1w_response)):
                if _load_task_value(path+'/track1D_1w_response.txt', self.task_no, '')==value_track1D_1w_response[item]:
                    self.track1D_1w_response[self.task_no].current(item)
        
        self.Button_ok=tk.Button(self.root,text='OK',font=16,command=self.entry_event)
        self.Button_ok.pack()
  
    def entry_event(self):
        global track1D_1w_x_cursor, track1D_1w_x_target, track1D_1w_freq, track1D_1w_amp, track1D_1w_response
        try:
            track1D_1w_x_cursor = int(self.track1D_1w_x_cursor[self.task_no].get())
            if track1D_1w_x_cursor < 0 or  track1D_1w_x_cursor > 100:
                raise ValueError
            _save_task_value(path+'/track1D_1w_x_cursor.txt', self.task_no, track1D_1w_x_cursor)
            
            track1D_1w_x_target = int(self.track1D_1w_x_target[self.task_no].get())
            if track1D_1w_x_target < 0 or track1D_1w_x_target> 100:
                raise ValueError
            _save_task_value(path+'/track1D_1w_x_target.txt', self.task_no, track1D_1w_x_target)
            
            track1D_1w_freq = self.track1D_1w_freq[self.task_no].get()
            _save_task_value(path+'/track1D_1w_freq.txt', self.task_no, track1D_1w_freq)
            
            track1D_1w_amp = self.track1D_1w_amp[self.task_no].get()
            _save_task_value(path+'/track1D_1w_amp.txt', self.task_no, track1D_1w_amp)
            
            track1D_1w_response = self.track1D_1w_response[self.task_no].get()
            _save_task_value(path+'/track1D_1w_response.txt', self.task_no, track1D_1w_response)
            
            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return 
            
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_label = tk.Label(error_window, text="Please enter an integer between 1 and 100 for the cursor starting location.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()        


class GUI_BE_track1D_r:
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
        self.task_no=task_no
        self.task_key=_task_index(task_no)
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=500 #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Tracking_1D_Random - Task ' + str(self.task_no))
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no
        tk.Label(self.root,text='Enter cursor starting location: (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track1D_r_x_cursor={}
        
        self.track1D_r_x_cursor[self.task_no]=tk.Entry(self.root,width=20)
        self.track1D_r_x_cursor[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track1D_r_x_cursor[self.task_no].insert(0, str(_load_task_value(path+'/track1D_r_x_cursor.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Enter target starting location: (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track1D_r_x_target={}
        
        self.track1D_r_x_target[self.task_no]=tk.Entry(self.root,width=20)
        self.track1D_r_x_target[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track1D_r_x_target[self.task_no].insert(0, str(_load_task_value(path+'/track1D_r_x_target.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Select target movement track1D_freq:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track1D_r_freq = ['Slow','Medium','Quick']
        
        self.track1D_r_freq={}
        self.track1D_r_freq[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track1D_r_freq, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track1D_r_freq[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track1D_r_freq)):
                if _load_task_value(path+'/track1D_r_freq.txt', self.task_no, '')==value_track1D_r_freq[item]:
                    self.track1D_r_freq[self.task_no].current(item)
        
        
        tk.Label(self.root,text='Select target movement track1D_amp:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track1D_r_amp = ['Small','Medium','Large']
        self.track1D_r_amp={}
        self.track1D_r_amp[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track1D_r_amp, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track1D_r_amp[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track1D_r_amp)):
                if _load_task_value(path+'/track1D_r_amp.txt', self.task_no, '')==value_track1D_r_amp[item]:
                    self.track1D_r_amp[self.task_no].current(item)
        
        tk.Label(self.root,text='Select response method:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track1D_r_response = ['Click mouse','Press keyboard']
        
        self.track1D_r_response={}
        self.track1D_r_response[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track1D_r_response, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track1D_r_response[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track1D_r_response)):
                if _load_task_value(path+'/track1D_r_response.txt', self.task_no, '')==value_track1D_r_response[item]:
                    self.track1D_r_response[self.task_no].current(item)
        
        self.Button_ok=tk.Button(self.root,text='OK',font=16,command=self.entry_event)
        self.Button_ok.pack()
  
    def entry_event(self):
        global track1D_r_x_cursor, track1D_r_x_target, track1D_r_freq, track1D_r_amp, track1D_r_response
        try:
            track1D_r_x_cursor = int(self.track1D_r_x_cursor[self.task_no].get())
            if track1D_r_x_cursor < 0 or  track1D_r_x_cursor > 100:
                raise ValueError
            _save_task_value(path+'/track1D_r_x_cursor.txt', self.task_no, track1D_r_x_cursor)
            
            track1D_r_x_target = int(self.track1D_r_x_target[self.task_no].get())
            if track1D_r_x_target < 0 or track1D_r_x_target> 100:
                raise ValueError
            _save_task_value(path+'/track1D_r_x_target.txt', self.task_no, track1D_r_x_target)
            
            track1D_r_freq = self.track1D_r_freq[self.task_no].get()
            _save_task_value(path+'/track1D_r_freq.txt', self.task_no, track1D_r_freq)
            
            track1D_r_amp = self.track1D_r_amp[self.task_no].get()
            _save_task_value(path+'/track1D_r_amp.txt', self.task_no, track1D_r_amp)
            
            track1D_r_response = self.track1D_r_response[self.task_no].get()
            _save_task_value(path+'/track1D_r_response.txt', self.task_no, track1D_r_response)
            
            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return 
            
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_label = tk.Label(error_window, text="Please enter an integer between 1 and 100 for the cursor starting location.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()        

class GUI_BE_track2D:
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
        self.task_no=task_no
        self.task_key=_task_index(task_no)
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=700 #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Tracking_2D_Bounded - Task ' + str(self.task_no))
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no
        
        tk.Label(self.root,text='Select trajectory shape:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        value_tracking2D_b_shape = ['sin','e^x','ln']
        self.tracking2D_b_shape={}
        self.tracking2D_b_shape[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracking2D_b_shape, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracking2D_b_shape[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracking2D_b_shape)):
                if _load_task_value(path+'/tracking2D_b_shape.txt', self.task_no, '')==value_tracking2D_b_shape[item]:
                    self.tracking2D_b_shape[self.task_no].current(item)
        
        tk.Label(self.root,text='Enter cursor starting location (x): (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track2D_b_x_cursor={}
        
        self.track2D_b_x_cursor[self.task_no]=tk.Entry(self.root,width=20)
        self.track2D_b_x_cursor[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track2D_b_x_cursor[self.task_no].insert(0, str(_load_task_value(path+'/track2D_b_x_cursor.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Enter initial target location (x): (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track2D_b_x_target={}
        
        self.track2D_b_x_target[self.task_no]=tk.Entry(self.root,width=20)
        self.track2D_b_x_target[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track2D_b_x_target[self.task_no].insert(0, str(_load_task_value(path+'/track2D_b_x_target.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Select target movement track2D_freq:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track2D_b_freq = ['Slow','Medium','Quick']
        
        self.track2D_b_freq ={}
        self.track2D_b_freq [self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track2D_b_freq , 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track2D_b_freq [self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track2D_b_freq )):
                if _load_task_value(path+'/track2D_b_freq.txt', self.task_no, '')==value_track2D_b_freq[item]:
                    self.track2D_b_freq [self.task_no].current(item)
        
        tk.Label(self.root,text='Select target movement track2D_amp:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track2D_b_amp = ['Small','Medium','Large']
        self.track2D_b_amp={}
        self.track2D_b_amp[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track2D_b_amp, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track2D_b_amp[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track2D_b_amp)):
                if _load_task_value(path+'/track2D_b_amp.txt', self.task_no, '')==value_track2D_b_amp[item]:
                    self.track2D_b_amp[self.task_no].current(item)
        
        tk.Label(self.root,text='Select response method:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track2D_b_response = ['Click mouse','Press keyboard']
        
        self.track2D_b_response={}
        self.track2D_b_response[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track2D_b_response, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track2D_b_response[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track2D_b_response)):
                if _load_task_value(path+'/track2D_b_response.txt', self.task_no, '')==value_track2D_b_response[item]:
                    self.track2D_b_response[self.task_no].current(item)
        
        self.Button_ok=tk.Button(self.root,text='OK',font=16,command=self.entry_event)
        self.Button_ok.pack()
     
    def entry_event(self):
        global track2D_b_x_target, track2D_b_x_cursor, track2D_b_freq, track2D_b_amp, track2D_b_response,track2D_b_shape
        try:
            track2D_b_x_target = int(self.track2D_b_x_target[self.task_no].get())
            if track2D_b_x_target < 0 or track2D_b_x_target > 100:
                raise ValueError
            _save_task_value(path+'/track2D_b_x_target.txt', self.task_no, track2D_b_x_target)
            
            track2D_b_x_cursor = int(self.track2D_b_x_cursor[self.task_no].get())
            if track2D_b_x_cursor < 0 or track2D_b_x_cursor > 100:
                raise ValueError
            _save_task_value(path+'/track2D_b_x_cursor.txt', self.task_no, track2D_b_x_cursor)
            
            track2D_b_freq = self.track2D_b_freq[self.task_no].get()
            _save_task_value(path+'/track2D_b_freq.txt', self.task_no, track2D_b_freq)
            
            track2D_b_amp = self.track2D_b_amp[self.task_no].get()
            _save_task_value(path+'/track2D_b_amp.txt', self.task_no, track2D_b_amp)
            
            track2D_b_response = self.track2D_b_response[self.task_no].get()
            _save_task_value(path+'/track2D_b_response.txt', self.task_no, track2D_b_response)
            
            track2D_b_shape = self.tracking2D_b_shape[self.task_no].get()
            _save_task_value(path+'/tracking2D_b_shape.txt', self.task_no, track2D_b_shape)
            
            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return
            
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_label = tk.Label(error_window, text="Please enter an integer between 0 and 100 for the target and cursor locations.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        
class GUI_BE_track2D_r:
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
        self.task_no=task_no
        self.task_key=_task_index(task_no)
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=700 #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Tracking_2D_Random - Task ' + str(self.task_no))
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no
        
        tk.Label(self.root,text='Enter cursor starting location (x): (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track2D_r_x_cursor={}
        
        self.track2D_r_x_cursor[self.task_no]=tk.Entry(self.root,width=20)
        self.track2D_r_x_cursor[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track2D_r_x_cursor[self.task_no].insert(0, str(_load_task_value(path+'/track2D_r_x_cursor.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Enter cursor starting location (y): (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track2D_r_y_cursor={}
        
        self.track2D_r_y_cursor[self.task_no]=tk.Entry(self.root,width=20)
        self.track2D_r_y_cursor[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track2D_r_y_cursor[self.task_no].insert(0, str(_load_task_value(path+'/track2D_r_y_cursor.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Enter initial target location (x): (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track2D_r_x_target={}
        
        self.track2D_r_x_target[self.task_no]=tk.Entry(self.root,width=20)
        self.track2D_r_x_target[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track2D_r_x_target[self.task_no].insert(0, str(_load_task_value(path+'/track2D_r_x_target.txt', self.task_no, '')))
            
        
        tk.Label(self.root,text='Enter initial target location (y): (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track2D_r_y_target={}
        
        self.track2D_r_y_target[self.task_no]=tk.Entry(self.root,width=20)
        self.track2D_r_y_target[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track2D_r_y_target[self.task_no].insert(0, str(_load_task_value(path+'/track2D_r_y_target.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Select target movement track2D_freq:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track2D_r_freq = ['Slow','Medium','Quick']
        
        self.track2D_r_freq ={}
        self.track2D_r_freq [self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track2D_r_freq , 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track2D_r_freq [self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track2D_r_freq )):
                if _load_task_value(path+'/track2D_r_freq.txt', self.task_no, '')==value_track2D_r_freq[item]:
                    self.track2D_r_freq [self.task_no].current(item)
        
        
        tk.Label(self.root,text='Select target movement track2D_amp:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track2D_r_amp = ['Small','Medium','Large']
        self.track2D_r_amp={}
        self.track2D_r_amp[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track2D_r_amp, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track2D_r_amp[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track2D_r_amp)):
                if _load_task_value(path+'/track2D_r_amp.txt', self.task_no, '')==value_track2D_r_amp[item]:
                    self.track2D_r_amp[self.task_no].current(item)
        
        tk.Label(self.root,text='Select response method:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track2D_r_response = ['Click mouse','Press keyboard']
        
        self.track2D_r_response={}
        self.track2D_r_response[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track2D_r_response, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track2D_r_response[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track2D_r_response)):
                if _load_task_value(path+'/track2D_r_response.txt', self.task_no, '')==value_track2D_r_response[item]:
                    self.track2D_r_response[self.task_no].current(item)
        
        self.Button_ok=tk.Button(self.root,text='OK',font=16,command=self.entry_event)
        self.Button_ok.pack()
     
    def entry_event(self):
        global track2D_r_x_target, track2D_r_y_target, track2D_r_x_cursor, track2D_r_y_cursor, track2D_r_freq, track2D_r_amp, track2D_r_response
        try:
            track2D_r_x_target = int(self.track2D_r_x_target[self.task_no].get())
            if track2D_r_x_target < 0 or track2D_r_x_target > 100:
                raise ValueError
            _save_task_value(path+'/track2D_r_x_target.txt', self.task_no, track2D_r_x_target)
            
            track2D_r_y_target = int(self.track2D_r_y_target[self.task_no].get())
            if track2D_r_y_target < 0 or track2D_r_y_target > 100:
                raise ValueError
            _save_task_value(path+'/track2D_r_y_target.txt', self.task_no, track2D_r_y_target)
            
            track2D_r_x_cursor = int(self.track2D_r_x_cursor[self.task_no].get())
            if track2D_r_x_cursor < 0 or track2D_r_x_cursor > 100:
                raise ValueError
            _save_task_value(path+'/track2D_r_x_cursor.txt', self.task_no, track2D_r_x_cursor)
            
            track2D_r_y_cursor = int(self.track2D_r_y_cursor[self.task_no].get())
            if track2D_r_y_cursor < 0 or track2D_r_y_cursor > 100:
                raise ValueError
            _save_task_value(path+'/track2D_r_y_cursor.txt', self.task_no, track2D_r_y_cursor)
            
            track2D_r_freq = self.track2D_r_freq[self.task_no].get()
            _save_task_value(path+'/track2D_r_freq.txt', self.task_no, track2D_r_freq)
            
            track2D_r_amp = self.track2D_r_amp[self.task_no].get()
            _save_task_value(path+'/track2D_r_amp.txt', self.task_no, track2D_r_amp)
            
            track2D_r_response = self.track2D_r_response[self.task_no].get()
            _save_task_value(path+'/track2D_r_response.txt', self.task_no, track2D_r_response)
            
            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return
            
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_label = tk.Label(error_window, text="Please enter an integer between 0 and 100 for the target and cursor locations.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()        

class GUI_BE_track2D_1w:
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
        self.task_no=task_no
        self.task_key=_task_index(task_no)
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=700 #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Tracking_2D_1W - Task ' + str(self.task_no))
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no
        
        tk.Label(self.root,text='Select trajectory shape:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        value_tracking2D_1w_shape = ['sin','e^x','ln']
        self.tracking2D_1w_shape={}
        self.tracking2D_1w_shape[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracking2D_1w_shape, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracking2D_1w_shape[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracking2D_1w_shape)):
                if _load_task_value(path+'/tracking2D_1w_shape.txt', self.task_no, '')==value_tracking2D_1w_shape[item]:
                    self.tracking2D_1w_shape[self.task_no].current(item)
        
        tk.Label(self.root,text='Enter cursor starting location (x): (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track2D_1w_x_cursor={}
        
        self.track2D_1w_x_cursor[self.task_no]=tk.Entry(self.root,width=20)
        self.track2D_1w_x_cursor[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track2D_1w_x_cursor[self.task_no].insert(0, str(_load_task_value(path+'/track2D_1w_x_cursor.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Enter cursor starting location (y): (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track2D_1w_y_cursor={}
        
        self.track2D_1w_y_cursor[self.task_no]=tk.Entry(self.root,width=20)
        self.track2D_1w_y_cursor[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track2D_1w_y_cursor[self.task_no].insert(0, str(_load_task_value(path+'/track2D_1w_y_cursor.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Enter initial target location (x): (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track2D_1w_x_target={}
        
        self.track2D_1w_x_target[self.task_no]=tk.Entry(self.root,width=20)
        self.track2D_1w_x_target[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track2D_1w_x_target[self.task_no].insert(0, str(_load_task_value(path+'/track2D_1w_x_target.txt', self.task_no, '')))
            
        
        tk.Label(self.root,text='Enter initial target location (y): (An integer in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        self.track2D_1w_y_target={}
        
        self.track2D_1w_y_target[self.task_no]=tk.Entry(self.root,width=20)
        self.track2D_1w_y_target[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.track2D_1w_y_target[self.task_no].insert(0, str(_load_task_value(path+'/track2D_1w_y_target.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Select target movement track2D_freq:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track2D_1w_freq = ['Slow','Medium','Quick']
        
        self.track2D_1w_freq ={}
        self.track2D_1w_freq [self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track2D_1w_freq , 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track2D_1w_freq [self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track2D_1w_freq )):
                if _load_task_value(path+'/track2D_1w_freq.txt', self.task_no, '')==value_track2D_1w_freq[item]:
                    self.track2D_1w_freq [self.task_no].current(item)
        
        
        tk.Label(self.root,text='Select target movement track2D_amp:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track2D_1w_amp = ['Small','Medium','Large']
        self.track2D_1w_amp={}
        self.track2D_1w_amp[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track2D_1w_amp, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track2D_1w_amp[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track2D_1w_amp)):
                if _load_task_value(path+'/track2D_1w_amp.txt', self.task_no, '')==value_track2D_1w_amp[item]:
                    self.track2D_1w_amp[self.task_no].current(item)
        
        tk.Label(self.root,text='Select response method:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_track2D_1w_response = ['Click mouse','Press keyboard']
        
        self.track2D_1w_response={}
        self.track2D_1w_response[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_track2D_1w_response, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.track2D_1w_response[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_track2D_1w_response)):
                if _load_task_value(path+'/track2D_1w_response.txt', self.task_no, '')==value_track2D_1w_response[item]:
                    self.track2D_1w_response[self.task_no].current(item)
        
        self.Button_ok=tk.Button(self.root,text='OK',font=16,command=self.entry_event)
        self.Button_ok.pack()
     
    def entry_event(self):
        global track2D_1w_x_target, track2D_1w_y_target, track2D_1w_x_cursor, track2D_1w_y_cursor, track2D_1w_freq, track2D_1w_amp, track2D_1w_response,track2D_1w_shape
        try:
            track2D_1w_x_target = int(self.track2D_1w_x_target[self.task_no].get())
            if track2D_1w_x_target < 0 or track2D_1w_x_target > 100:
                raise ValueError
            _save_task_value(path+'/track2D_1w_x_target.txt', self.task_no, track2D_1w_x_target)
            
            track2D_1w_y_target = int(self.track2D_1w_y_target[self.task_no].get())
            if track2D_1w_y_target < 0 or track2D_1w_y_target > 100:
                raise ValueError
            _save_task_value(path+'/track2D_1w_y_target.txt', self.task_no, track2D_1w_y_target)
            
            track2D_1w_x_cursor = int(self.track2D_1w_x_cursor[self.task_no].get())
            if track2D_1w_x_cursor < 0 or track2D_1w_x_cursor > 100:
                raise ValueError
            _save_task_value(path+'/track2D_r_x_cursor.txt', self.task_no, track2D_1w_x_cursor)
            
            track2D_1w_y_cursor = int(self.track2D_1w_y_cursor[self.task_no].get())
            if track2D_1w_y_cursor < 0 or track2D_1w_y_cursor > 100:
                raise ValueError
            _save_task_value(path+'/track2D_1w_y_cursor.txt', self.task_no, track2D_1w_y_cursor)
            
            track2D_1w_freq = self.track2D_1w_freq[self.task_no].get()
            _save_task_value(path+'/track2D_1w_freq.txt', self.task_no, track2D_1w_freq)
            
            track2D_1w_amp = self.track2D_1w_amp[self.task_no].get()
            _save_task_value(path+'/track2D_1w_amp.txt', self.task_no, track2D_1w_amp)
            
            track2D_1w_response = self.track2D_1w_response[self.task_no].get()
            _save_task_value(path+'/track2D_1w_response.txt', self.task_no, track2D_1w_response)
            
            track2D_1w_shape = self.tracking2D_1w_shape[self.task_no].get()
            _save_task_value(path+'/tracking2D_1w_shape.txt', self.task_no, track2D_1w_shape)
            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return
            
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_label = tk.Label(error_window, text="Please enter an integer between 0 and 100 for the target and cursor locations.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()       


class GUI_BE_tracing1D_b:
    
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
        self.task_no=task_no
        self.task_key=_task_index(task_no)
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=500 #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Tracing_1D_Bounded - Task ' + str(self.task_no))
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no


        tk.Label(self.root,text='Enter point starting location (x): (A number in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        self.tracing1D_b_loc_x={}
        
        self.tracing1D_b_loc_x[self.task_no]=tk.Entry(self.root,width=20)
        self.tracing1D_b_loc_x[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.tracing1D_b_loc_x[self.task_no].insert(0, str(_load_task_value(path+'/tracing1D_b_loc_x.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Select initial point movement direction:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_tracing1D_b_direc = ['forward','backward']
        
        self.tracing1D_b_direc={}
        self.tracing1D_b_direc[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing1D_b_direc, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing1D_b_direc[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing1D_b_direc)):
                if _load_task_value(path+'/tracing1D_b_direc.txt', self.task_no, '')==value_tracing1D_b_direc[item]:
                    self.tracing1D_b_direc[self.task_no].current(item)
        
        
        tk.Label(self.root,text='Select point movement amplitude along x axis:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_tracing1D_b_amp = ['Small','Medium','Large']
        self.tracing1D_b_amp={}
        self.tracing1D_b_amp[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing1D_b_amp, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing1D_b_amp[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing1D_b_amp)):
                if _load_task_value(path+'/tracing1D_b_amp.txt', self.task_no, '')==value_tracing1D_b_amp[item]:
                    self.tracing1D_b_amp[self.task_no].current(item)
        
        tk.Label(self.root,text='Select response method:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        value_tracing1D_b_response = ['Click mouse','Press keyboard']
        self.tracing1D_b_response={}
        self.tracing1D_b_response[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing1D_b_response, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing1D_b_response[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing1D_b_response)):
                if _load_task_value(path+'/tracing1D_b_response.txt', self.task_no, '')==value_tracing1D_b_response[item]:
                    self.tracing1D_b_response[self.task_no].current(item)
        
        self.Button_ok=tk.Button(self.root,text='OK',font=16,command=self.entry_event)
        self.Button_ok.pack()
        
    def entry_event(self):
        global tracing1D_b_loc_x, tracing1D_b_amp,tracing1D_b_direc,tracing1D_b_response
        try:
            tracing1D_b_loc_x = eval(self. tracing1D_b_loc_x[self.task_no].get())
            if  tracing1D_b_loc_x < 0 or tracing1D_b_loc_x > 100:
                raise ValueError
            _save_task_value(path+'/tracing1D_b_loc_x.txt', self.task_no, tracing1D_b_loc_x)
            
            tracing1D_b_amp = self. tracing1D_b_amp[self.task_no].get()
            _save_task_value(path+'/tracing1D_b_amp.txt', self.task_no, tracing1D_b_amp)
            
            tracing1D_b_direc = self.tracing1D_b_direc[self.task_no].get()
            _save_task_value(path+'/tracing1D_b_direc.txt', self.task_no, tracing1D_b_direc)
            
            tracing1D_b_response = self.tracing1D_b_response[self.task_no].get()
            _save_task_value(path+'/tracing1D_b_response.txt', self.task_no, tracing1D_b_response)
                    
            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return
            
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_label = tk.Label(error_window, text="Please enter a number between 0 and 100 for the point's starting location.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()        
        
class GUI_BE_tracing1D_1w:
    
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
        self.task_no=task_no
        self.task_key=_task_index(task_no)
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=500 #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Tracing_1D_1W - Task ' + str(self.task_no))
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no
        
        tk.Label(self.root,text='Enter point starting location (x): (A number in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        self.tracing1D_1w_loc_x={}
        
        self.tracing1D_1w_loc_x[self.task_no]=tk.Entry(self.root,width=20)
        self.tracing1D_1w_loc_x[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.tracing1D_1w_loc_x[self.task_no].insert(0, str(_load_task_value(path+'/tracing1D_1w_loc_x.txt', self.task_no, '')))
        

        tk.Label(self.root,text='Select point movement amplitude along x axis:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_tracing1D_1w_amp = ['Small','Medium','Large']
        self.tracing1D_1w_amp={}
        self.tracing1D_1w_amp[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing1D_1w_amp, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing1D_1w_amp[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing1D_1w_amp)):
                if _load_task_value(path+'/tracing1D_1w_amp.txt', self.task_no, '')==value_tracing1D_1w_amp[item]:
                    self.tracing1D_1w_amp[self.task_no].current(item)
        
        tk.Label(self.root,text='Select response method:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        value_tracing1D_1w_response = ['Click mouse','Press keyboard']
        self.tracing1D_1w_response={}
        self.tracing1D_1w_response[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing1D_1w_response, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing1D_1w_response[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing1D_1w_response)):
                if _load_task_value(path+'/tracing1D_1w_response.txt', self.task_no, '')==value_tracing1D_1w_response[item]:
                    self.tracing1D_1w_response[self.task_no].current(item)
        
        self.Button_ok=tk.Button(self.root,text='OK',font=16,command=self.entry_event)
        self.Button_ok.pack()
        
    def entry_event(self):
        global  tracing1D_1w_loc_x, tracing1D_1w_amp, tracing1D_1w_response
        try:
            tracing1D_1w_loc_x = eval(self. tracing1D_1w_loc_x[self.task_no].get())
            if  tracing1D_1w_loc_x < 0 or tracing1D_1w_loc_x > 100:
                raise ValueError
            _save_task_value(path+'/tracing1D_1w_loc_x.txt', self.task_no, tracing1D_1w_loc_x)
            
            tracing1D_1w_amp = self. tracing1D_1w_amp[self.task_no].get()
            _save_task_value(path+'/tracing1D_1w_amp.txt', self.task_no, tracing1D_1w_amp)
            
            tracing1D_1w_response = self.tracing1D_1w_response[self.task_no].get()
            _save_task_value(path+'/tracing1D_1w_response.txt', self.task_no, tracing1D_1w_response)

            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return
            
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_label = tk.Label(error_window, text="Please enter a number between 0 and 100 for the point's starting location.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()

class GUI_BE_tracing2D_b:
    
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
        self.task_no=task_no
        self.task_key=_task_index(task_no)
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=650 #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Tracing_2D_Bounded - Task ' + str(self.task_no))
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no
        tk.Label(self.root,text='Select trajectory shape:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        value_tracing2D_b_shape = ['sin','e^x','ln']
        self.tracing2D_b_shape={}
        self.tracing2D_b_shape[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing2D_b_shape, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing2D_b_shape[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing2D_b_shape)):
                if _load_task_value(path+'/tracing2D_b_shape.txt', self.task_no, '')==value_tracing2D_b_shape[item]:
                    self.tracing2D_b_shape[self.task_no].current(item)
        
        tk.Label(self.root,text='Enter point starting location (x): (A number in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        self.tracing2D_b_loc_x={}
        
        self.tracing2D_b_loc_x[self.task_no]=tk.Entry(self.root,width=20)
        self.tracing2D_b_loc_x[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.tracing2D_b_loc_x[self.task_no].insert(0, str(_load_task_value(path+'/tracing2D_b_loc_x.txt', self.task_no, '')))
        
        tk.Label(self.root,text='Select initial point movement direction:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_tracing2D_b_direc = ['forward','backward']
        
        self.tracing2D_b_direc={}
        self.tracing2D_b_direc[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing2D_b_direc, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing2D_b_direc[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing2D_b_direc)):
                if _load_task_value(path+'/tracing2D_b_direc.txt', self.task_no, '')==value_tracing2D_b_direc[item]:
                    self.tracing2D_b_direc[self.task_no].current(item)
        
        
        tk.Label(self.root,text='Select point movement amplitude along x axis:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_tracing2D_b_x_amp = ['Small','Medium','Large']
        self.tracing2D_b_x_amp={}
        self.tracing2D_b_x_amp[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing2D_b_x_amp, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing2D_b_x_amp[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing2D_b_x_amp)):
                if _load_task_value(path+'/tracing2D_b_x_amp.txt', self.task_no, '')==value_tracing2D_b_x_amp[item]:
                    self.tracing2D_b_x_amp[self.task_no].current(item)
        
        tk.Label(self.root,text='Select point movement amplitude along y axis:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_tracing2D_b_y_amp = ['Small','Medium','Large']
        self.tracing2D_b_y_amp={}
        self.tracing2D_b_y_amp[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing2D_b_y_amp, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing2D_b_y_amp[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing2D_b_y_amp)):
                if _load_task_value(path+'/tracing2D_b_y_amp.txt', self.task_no, '')==value_tracing2D_b_y_amp[item]:
                    self.tracing2D_b_y_amp[self.task_no].current(item)
        
         
        tk.Label(self.root,text='Select response method:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        value_tracing2D_b_response = ['Click mouse','Press keyboard']
        self.tracing2D_b_response={}
        self.tracing2D_b_response[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing2D_b_response, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing2D_b_response[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing2D_b_response)):
                if _load_task_value(path+'/tracing2D_b_response.txt', self.task_no, '')==value_tracing2D_b_response[item]:
                    self.tracing2D_b_response[self.task_no].current(item)
        
        self.Button_ok=tk.Button(self.root,text='OK',font=16,command=self.entry_event)
        self.Button_ok.pack()
        
    def entry_event(self):
        global tracing2D_b_shape, tracing2D_b_loc_x, tracing2D_b_x_amp,  tracing2D_b_y_amp,tracing2D_b_direc,tracing2D_b_response
        try:
            tracing2D_b_loc_x = eval(self. tracing2D_b_loc_x[self.task_no].get())
            if  tracing2D_b_loc_x < 0 or tracing2D_b_loc_x > 100:
                raise ValueError
            _save_task_value(path+'/tracing2D_b_loc_x.txt', self.task_no, tracing2D_b_loc_x)
            
            tracing2D_b_x_amp = self. tracing2D_b_x_amp[self.task_no].get()
            _save_task_value(path+'/tracing2D_b_x_amp.txt', self.task_no, tracing2D_b_x_amp)
            
            tracing2D_b_y_amp = self. tracing2D_b_y_amp[self.task_no].get()
            _save_task_value(path+'/tracing2D_b_y_amp.txt', self.task_no, tracing2D_b_y_amp)
            
            tracing2D_b_shape = self.tracing2D_b_shape[self.task_no].get()
            _save_task_value(path+'/tracing2D_b_shape.txt', self.task_no, tracing2D_b_shape)
            
            tracing2D_b_direc = self.tracing2D_b_direc[self.task_no].get()
            _save_task_value(path+'/tracing2D_b_direc.txt', self.task_no, tracing2D_b_direc)
            
            tracing2D_b_response = self.tracing2D_b_response[self.task_no].get()
            _save_task_value(path+'/tracing2D_b_response.txt', self.task_no, tracing2D_b_response)
                    
            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return
            
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_label = tk.Label(error_window, text="Please enter a number between 0 and 100 for the point's starting location.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()
    
class GUI_BE_tracing2D_1w:
    
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
        self.task_no=task_no
        self.task_key=_task_index(task_no)
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=500 #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Tracing_2D_1W - Task ' + str(self.task_no))
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no
        tk.Label(self.root,text='Select trajectory shape:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        value_tracing2D_1w_shape = ['sin','e^x','ln']
        self.tracing2D_1w_shape={}
        self.tracing2D_1w_shape[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing2D_1w_shape, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing2D_1w_shape[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing2D_1w_shape)):
                if _load_task_value(path+'/tracing2D_1w_shape.txt', self.task_no, '')==value_tracing2D_1w_shape[item]:
                    self.tracing2D_1w_shape[self.task_no].current(item)
        
        tk.Label(self.root,text='Enter point starting location (x): (A number in 0-100) ',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        self.tracing2D_1w_loc_x={}
        
        self.tracing2D_1w_loc_x[self.task_no]=tk.Entry(self.root,width=20)
        self.tracing2D_1w_loc_x[self.task_no].pack(anchor='w',padx=10)
        if True:
            self.tracing2D_1w_loc_x[self.task_no].insert(0, str(_load_task_value(path+'/tracing2D_1w_loc_x.txt', self.task_no, '')))
        

        tk.Label(self.root,text='Select point movement amplitude along x axis:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_tracing2D_1w_x_amp = ['Small','Medium','Large']
        self.tracing2D_1w_x_amp={}
        self.tracing2D_1w_x_amp[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing2D_1w_x_amp, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing2D_1w_x_amp[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing2D_1w_x_amp)):
                if _load_task_value(path+'/tracing2D_1w_x_amp.txt', self.task_no, '')==value_tracing2D_1w_x_amp[item]:
                    self.tracing2D_1w_x_amp[self.task_no].current(item)
        
        tk.Label(self.root,text='Select point movement amplitude along y axis:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_tracing2D_1w_y_amp = ['Small','Medium','Large']
        self.tracing2D_1w_y_amp={}
        self.tracing2D_1w_y_amp[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing2D_1w_y_amp, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing2D_1w_y_amp[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing2D_1w_y_amp)):
                if _load_task_value(path+'/tracing2D_1w_y_amp.txt', self.task_no, '')==value_tracing2D_1w_y_amp[item]:
                    self.tracing2D_1w_y_amp[self.task_no].current(item)
                 
        tk.Label(self.root,text='Select response method:',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        value_tracing2D_1w_response = ['Click mouse','Press keyboard']
        self.tracing2D_1w_response={}
        self.tracing2D_1w_response[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_tracing2D_1w_response, 
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.tracing2D_1w_response[self.task_no].pack(anchor='w',padx=10)
        
        if True:
            for item in range(len(value_tracing2D_1w_response)):
                if _load_task_value(path+'/tracing2D_1w_response.txt', self.task_no, '')==value_tracing2D_1w_response[item]:
                    self.tracing2D_1w_response[self.task_no].current(item)
        
        self.Button_ok=tk.Button(self.root,text='OK',font=16,command=self.entry_event)
        self.Button_ok.pack()
        
    def entry_event(self):
        global tracing2D_1w_shape, tracing2D_1w_loc_x, tracing2D_1w_x_amp,  tracing2D_1w_y_amp, tracing2D_1w_response
        try:
            tracing2D_1w_loc_x = eval(self. tracing2D_1w_loc_x[self.task_no].get())
            if  tracing2D_1w_loc_x < 0 or tracing2D_1w_loc_x > 100:
                raise ValueError
            _save_task_value(path+'/tracing2D_1w_loc_x.txt', self.task_no, tracing2D_1w_loc_x)
            
            tracing2D_1w_x_amp = self. tracing2D_1w_x_amp[self.task_no].get()
            _save_task_value(path+'/tracing2D_1w_x_amp.txt', self.task_no, tracing2D_1w_x_amp)
            
            tracing2D_1w_y_amp = self. tracing2D_1w_y_amp[self.task_no].get()
            _save_task_value(path+'/tracing2D_1w_y_amp.txt', self.task_no, tracing2D_1w_y_amp)
            
            tracing2D_1w_shape = self.tracing2D_1w_shape[self.task_no].get()
            _save_task_value(path+'/tracing2D_1w_shape.txt', self.task_no, tracing2D_1w_shape)
            
            tracing2D_1w_response = self.tracing2D_1w_response[self.task_no].get()
            _save_task_value(path+'/tracing2D_1w_response.txt', self.task_no, tracing2D_1w_response)

            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return
            
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_label = tk.Label(error_window, text="Please enter a number between 0 and 100 for the point's starting location.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()


def initialize_runtime_state(path_='backup/'):
    """Load saved compound-BE parameters into module globals for direct Start after Open."""
    global judgei_target_dic
    global track1D_b_x_cursor, track1D_b_x_target, track1D_b_freq, track1D_b_amp, track1D_b_response
    global track1D_1w_x_cursor, track1D_1w_x_target, track1D_1w_freq, track1D_1w_amp, track1D_1w_response
    global track1D_r_x_cursor, track1D_r_x_target, track1D_r_freq, track1D_r_amp, track1D_r_response
    global track2D_b_x_target, track2D_b_x_cursor, track2D_b_freq, track2D_b_amp, track2D_b_response, track2D_b_shape
    global track2D_r_x_target, track2D_r_y_target, track2D_r_x_cursor, track2D_r_y_cursor, track2D_r_freq, track2D_r_amp, track2D_r_response
    global track2D_1w_x_target, track2D_1w_y_target, track2D_1w_x_cursor, track2D_1w_y_cursor, track2D_1w_freq, track2D_1w_amp, track2D_1w_response, track2D_1w_shape
    global tracing1D_b_loc_x, tracing1D_b_amp, tracing1D_b_direc, tracing1D_b_response
    global tracing1D_1w_loc_x, tracing1D_1w_amp, tracing1D_1w_response
    global tracing2D_b_shape, tracing2D_b_loc_x, tracing2D_b_x_amp, tracing2D_b_y_amp, tracing2D_b_direc, tracing2D_b_response
    global tracing2D_1w_shape, tracing2D_1w_loc_x, tracing2D_1w_x_amp, tracing2D_1w_y_amp, tracing2D_1w_response

    def _safe_load(filename, default):
        try:
            return save(1).load_var(filename)
        except Exception:
            return default

    def _pick_value(filename, default=''):
        data = _safe_load(filename, {})
        if not isinstance(data, dict) or not data:
            return default
        # Prefer the lowest-numbered task when several tasks are present.
        def _sort_key(item):
            try:
                return int(item)
            except Exception:
                return str(item)
        try:
            key = sorted(data.keys(), key=_sort_key)[0]
            return data[key]
        except Exception:
            try:
                return next(iter(data.values()))
            except Exception:
                return default

    judgei_target_dic = _safe_load(path_ + '/judgei_target_dic.txt', {})

    track1D_b_x_cursor = _pick_value(path_ + '/track1D_b_x_cursor.txt', 0)
    track1D_b_x_target = _pick_value(path_ + '/track1D_b_x_target.txt', 0)
    track1D_b_freq = _pick_value(path_ + '/track1D_b_freq.txt', '')
    track1D_b_amp = _pick_value(path_ + '/track1D_b_amp.txt', '')
    track1D_b_response = _pick_value(path_ + '/track1D_b_response.txt', '')

    track1D_1w_x_cursor = _pick_value(path_ + '/track1D_1w_x_cursor.txt', 0)
    track1D_1w_x_target = _pick_value(path_ + '/track1D_1w_x_target.txt', 0)
    track1D_1w_freq = _pick_value(path_ + '/track1D_1w_freq.txt', '')
    track1D_1w_amp = _pick_value(path_ + '/track1D_1w_amp.txt', '')
    track1D_1w_response = _pick_value(path_ + '/track1D_1w_response.txt', '')

    track1D_r_x_cursor = _pick_value(path_ + '/track1D_r_x_cursor.txt', 0)
    track1D_r_x_target = _pick_value(path_ + '/track1D_r_x_target.txt', 0)
    track1D_r_freq = _pick_value(path_ + '/track1D_r_freq.txt', '')
    track1D_r_amp = _pick_value(path_ + '/track1D_r_amp.txt', '')
    track1D_r_response = _pick_value(path_ + '/track1D_r_response.txt', '')

    track2D_b_x_target = _pick_value(path_ + '/track2D_b_x_target.txt', 0)
    track2D_b_x_cursor = _pick_value(path_ + '/track2D_b_x_cursor.txt', 0)
    track2D_b_freq = _pick_value(path_ + '/track2D_b_freq.txt', '')
    track2D_b_amp = _pick_value(path_ + '/track2D_b_amp.txt', '')
    track2D_b_response = _pick_value(path_ + '/track2D_b_response.txt', '')
    track2D_b_shape = _pick_value(path_ + '/tracking2D_b_shape.txt', '')

    track2D_r_x_target = _pick_value(path_ + '/track2D_r_x_target.txt', 0)
    track2D_r_y_target = _pick_value(path_ + '/track2D_r_y_target.txt', 0)
    track2D_r_x_cursor = _pick_value(path_ + '/track2D_r_x_cursor.txt', 0)
    track2D_r_y_cursor = _pick_value(path_ + '/track2D_r_y_cursor.txt', 0)
    track2D_r_freq = _pick_value(path_ + '/track2D_r_freq.txt', '')
    track2D_r_amp = _pick_value(path_ + '/track2D_r_amp.txt', '')
    track2D_r_response = _pick_value(path_ + '/track2D_r_response.txt', '')

    track2D_1w_x_target = _pick_value(path_ + '/track2D_1w_x_target.txt', 0)
    track2D_1w_y_target = _pick_value(path_ + '/track2D_1w_y_target.txt', 0)
    track2D_1w_x_cursor = _pick_value(path_ + '/track2D_r_x_cursor.txt', 0)
    track2D_1w_y_cursor = _pick_value(path_ + '/track2D_1w_y_cursor.txt', 0)
    track2D_1w_freq = _pick_value(path_ + '/track2D_1w_freq.txt', '')
    track2D_1w_amp = _pick_value(path_ + '/track2D_1w_amp.txt', '')
    track2D_1w_response = _pick_value(path_ + '/track2D_1w_response.txt', '')
    track2D_1w_shape = _pick_value(path_ + '/tracking2D_1w_shape.txt', '')

    tracing1D_b_loc_x = _pick_value(path_ + '/tracing1D_b_loc_x.txt', 0)
    tracing1D_b_amp = _pick_value(path_ + '/tracing1D_b_amp.txt', '')
    tracing1D_b_direc = _pick_value(path_ + '/tracing1D_b_direc.txt', '')
    tracing1D_b_response = _pick_value(path_ + '/tracing1D_b_response.txt', '')

    tracing1D_1w_loc_x = _pick_value(path_ + '/tracing1D_1w_loc_x.txt', 0)
    tracing1D_1w_amp = _pick_value(path_ + '/tracing1D_1w_amp.txt', '')
    tracing1D_1w_response = _pick_value(path_ + '/tracing1D_1w_response.txt', '')

    tracing2D_b_shape = _pick_value(path_ + '/tracing2D_b_shape.txt', '')
    tracing2D_b_loc_x = _pick_value(path_ + '/tracing2D_b_loc_x.txt', 0)
    tracing2D_b_x_amp = _pick_value(path_ + '/tracing2D_b_x_amp.txt', '')
    tracing2D_b_y_amp = _pick_value(path_ + '/tracing2D_b_y_amp.txt', '')
    tracing2D_b_direc = _pick_value(path_ + '/tracing2D_b_direc.txt', '')
    tracing2D_b_response = _pick_value(path_ + '/tracing2D_b_response.txt', '')

    tracing2D_1w_shape = _pick_value(path_ + '/tracing2D_1w_shape.txt', '')
    tracing2D_1w_loc_x = _pick_value(path_ + '/tracing2D_1w_loc_x.txt', 0)
    tracing2D_1w_x_amp = _pick_value(path_ + '/tracing2D_1w_x_amp.txt', '')
    tracing2D_1w_y_amp = _pick_value(path_ + '/tracing2D_1w_y_amp.txt', '')
    tracing2D_1w_response = _pick_value(path_ + '/tracing2D_1w_response.txt', '')
