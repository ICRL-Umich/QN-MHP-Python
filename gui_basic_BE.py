# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 09:27:13 2024

@author: wyuanc
"""

"""GUI windows used to define parameters for individual basic behavior elements."""

import tkinter as tk
import math
from tkinter import ttk, messagebox 
from utility import save_user_input as save
from utility import look_for_ls,color_dic,has_saved_input

#2.3 BE Specific GUI


N=None
judgei_target_dic=None
length_count=None

def _load_saved_dict(filename):
    if not has_saved_input(filename):
        return {}
    try:
        data = save(1).load_var(filename)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _load_saved_value(filename, key, default=''):
    data = _load_saved_dict(filename)
    return data.get(key, default)


def _save_merged_dict(filename, updates):
    data = _load_saved_dict(filename)
    data.update(updates)
    save(saved).save_var(data, filename)
    return data

choice_N={}
class GUI_BE_Choice:
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
    
        self.root = tk.Tk()
        self.root.title(f'BE Specification: Choice - Task {task_no}')
        self.task_no=task_no
        self.Choice()
        self.root.update_idletasks()
        req_w = max(self.root.winfo_reqwidth() + 40, 620)
        req_h = max(self.root.winfo_reqheight() + 40, 210)
        sw=self.root.winfo_screenwidth()
        sh=self.root.winfo_screenheight()
        x=max((sw-req_w)//2,0)
        y=max((sh-req_h)//2,0)
        self.root.geometry(f'{req_w}x{req_h}+{x}+{y}')
        self.root.minsize(req_w, req_h)
        
    def Choice(self):
        self.choice={}
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        tk.Label(
            self.root,
            text='Input Choice Number (integer from 1 to 6):',
            font=("Times New Roman",20),
            wraplength=520,
            justify='left'
        ).grid(row=0,column=0,padx=20,pady=(20,10),sticky='w')
        
        self.choice[self.task_no]=tk.Entry(self.root,width=18)
        self.choice[self.task_no].grid(row=0,column=1,ipady=3,padx=(0,20),sticky='w') 
        if has_saved_input(path+'/N.txt'):
            N = _load_saved_dict(path+'/N.txt')
            if eval(self.task_no) in N:
                self.choice[self.task_no].insert(0,N[eval(self.task_no)])

        self.Button_ok=tk.Button(self.root,text='Save and Go Back',font=16,command=self.entry_event)
        self.Button_ok.grid(row=1,column=0,columnspan=2,pady=(20,20),ipady=3)
       
    def entry_event(self):
        global choice_N
        global choice_N
        try:
            choice_value = int(self.choice[self.task_no].get())
            if choice_value < 1 or choice_value > 6:
                raise ValueError
            choice_N = _load_saved_dict(path+'/N.txt')
            choice_N[eval(self.task_no)] = choice_value
            save(saved).save_var(choice_N, path+'/N.txt')
            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return
            
            
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_label = tk.Label(error_window, text="Please enter an integer from 1 to 6 for the choice number.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()

mouse_click_dimension_dic = {}
class GUI_BE_Mouseclick:
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=560   #window width
        wh=170   #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('BE Specification: Mouse_click')
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no
        self.Dimension()
        
    def Dimension(self):
        tk.Label(self.root,text='Select Mouse Click Dimension',font=("Times New Roman",15)).pack(anchor='w',pady=20,padx=10)
        
        value_mouse_click_dimension  = ['1','2','3']
    
        self.mouse_click_dimension={}
        self.mouse_click_dimension[self.task_no] = ttk.Combobox(
            master = self.root,
            state='readonly',
            cursor='arrow',
            width=22,
            values=value_mouse_click_dimension
            )
        #self.stimulitype.bind('<<ComboboxSelected>>',self.pick)
        self.mouse_click_dimension[self.task_no].pack(anchor='w',padx=10)
        
        if has_saved_input(path+'/mouse_click_dimension.txt'):
            saved_value = _load_saved_value(path+'/mouse_click_dimension.txt', eval(self.task_no), '')
            for item in range(len(value_mouse_click_dimension)):
                if saved_value == value_mouse_click_dimension[item]:
                    self.mouse_click_dimension[self.task_no].current(item)
       
        self.Button_ok=tk.Button(self.root,text='OK',font=16,command=self.entry_event)
        self.Button_ok.pack()
       
    def entry_event(self):
    
        global mouse_click_dimension_dic
        if self.mouse_click_dimension[self.task_no].get() not in ('1', '2', '3'):
            messagebox.showwarning('Missing Mouse Click Parameter', 'Select 1D, 2D or 3D before saving.', parent=self.root)
            return
        mouse_click_dimension_dic = _load_saved_dict(path+'/mouse_click_dimension.txt')
        mouse_click_dimension_dic[eval(self.task_no)] = self.mouse_click_dimension[self.task_no].get()
        save(saved).save_var(mouse_click_dimension_dic, path+'/mouse_click_dimension.txt')
        self.root.destroy()
                    


class GUI_BE_Lookat:
    """Explain automatic gaze targets; developers edit look_at_layout.json."""
    def __init__(self, task_no, saved_, path_):
        import json
        from pathlib import Path
        import eye_movement_model as eye_model
        from gui_general import task_info_dic
        self.root = tk.Tk()
        self.root.title('Look At - Automatic Target Configuration')
        config = json.loads(Path(__file__).with_name('look_at_layout.json').read_text(encoding='utf-8'))
        # Determine whether this task contains only Look At from the saved
        # task definition. Tasklist_dic is created only after Start is pressed.
        task_number = str(task_no)
        task_column = next((column for column in range(1, 6)
                            if str(task_info_dic.get((1, column), '')) == task_number), None)
        if task_column is None:
            raise ValueError('Task %s was not found in the saved task definition.' % task_number)
        elements = [task_info_dic.get((row, 2 * task_column - 1), '')
                    for row in range(2, 18)]
        elements = [element for element in elements if element]
        standalone = elements == ['Look_at']
        prefix = 'standalone' if standalone else 'combined'
        mode = config[prefix + '_target_mode']
        width, height = eye_model.SCREEN_WIDTH_MM, eye_model.SCREEN_HEIGHT_MM
        tk.Label(self.root, text='Look At - Automatic Eye Target', font=('Arial', 18, 'bold')).pack(padx=20, pady=12)
        tk.Label(self.root, text='Screen: %g × %g mm | Viewing distance: %g mm' %
                 (width, height, eye_model.VIEWING_DISTANCE_MM)).pack(padx=20, pady=6)
        tk.Label(self.root, text='Initial fixation: screen center (%g, %g) mm (default)' %
                 (width/2, height/2)).pack(padx=20, pady=6)
        if mode == 'random':
            description = 'Target: randomly generated on the screen for each stimulus.'
        else:
            key = prefix + ('_fixed_target_mm' if standalone else '_target_mm')
            pos = config[key]
            description = 'Target: fixed at (%g, %g) mm.' % (pos['x_mm'], pos['y_mm'])
        tk.Label(self.root, text=description).pack(padx=20, pady=6)
        tk.Label(self.root, text='Developers: edit look_at_layout.json to change target mode/position;\n'
                 'edit eye_movement_model.py to change the initial fixation.',
                 justify='center', fg='#444444').pack(padx=20, pady=8)
        tk.Button(self.root, text='Close', command=self.root.destroy).pack(pady=12)
        self.root.update_idletasks()
        w, h = max(660, self.root.winfo_reqwidth()+25), self.root.winfo_reqheight()+25
        self.root.geometry('%dx%d' % (w,h))


class GUI_BE_Judgei:
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
    
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500    #window width
        wh=200   #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Judge_Identity')
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.task_no=task_no
        self.Judgei()
        
    def Judgei(self):
        self.judge_i={}
        self.judge_v={}
        tk.Label(self.root,text='Choose the identity to be judged',font=("Times New Roman",15)).grid(row=0,column=0,pady=10,padx=10)
        tk.Label(self.root,text='Choose the value of the target identity',font=("Times New Roman",15)).grid(row=1,column=0,pady=10)
        
        self.identity_var = tk.StringVar(self.root)
        self.judge_i[self.task_no] = ttk.Combobox(self.root,textvariable=self.identity_var,values = ['Text','Color'])
        self.judge_i[self.task_no].grid(row=0,column=1)
        self.identity_var.trace_add('write', self.update_options)
        if has_saved_input(path+'/judgei_target_dic.txt'):
            saved_judge = _load_saved_dict(path+'/judgei_target_dic.txt')
            if self.task_no in saved_judge and saved_judge[self.task_no].get('identity') in ['Text','Color']:
                self.judge_i[self.task_no].current(['Text','Color'].index(saved_judge[self.task_no]['identity']))
        
        self.value_var = tk.StringVar(self.root)
        
        options_text = ['a', 'b', 'c']
        options_color = ['red', 'green','blue','yellow']
        
        self.judge_v[self.task_no] = ttk.Combobox(self.root,textvariable=self.value_var,values=[])
        if has_saved_input(path+'/judgei_target_dic.txt'):
            saved_judge = _load_saved_dict(path+'/judgei_target_dic.txt')
            if self.task_no in saved_judge:
                saved_identity = saved_judge[self.task_no].get('identity', '')
                if saved_identity == 'Text':
                    self.judge_v[self.task_no]['values'] = options_text
                elif saved_identity == 'Color':
                    self.judge_v[self.task_no]['values'] = options_color
        self.judge_v[self.task_no].grid(row=1,column=1)
               
        if has_saved_input(path+'/judgei_target_dic.txt'):
            saved_judge = _load_saved_dict(path+'/judgei_target_dic.txt')
            if self.task_no in saved_judge:
                saved_value = saved_judge[self.task_no].get('value', '')
                current_values = list(self.judge_v[self.task_no]['values'])
                if saved_value in current_values:
                    self.judge_v[self.task_no].current(current_values.index(saved_value))
       
        self.Button_ok=tk.Button(self.root,text='Save and Go Back',font=16,command=self.entry_event)
        self.Button_ok.grid(row=2,rowspan=3,column=4,columnspan=1,pady=30,ipady=3,ipadx=7)
            
    def update_options(self,*args):
        selected_identity = self.identity_var.get()
        self.value_var.set('')
        self.judge_v[self.task_no]['values']=[]
        if selected_identity == 'Text':
            options = ['a', 'b', 'c']
        elif selected_identity == 'Color':
            options = ['red', 'green','blue','yellow']
            
        self.judge_v[self.task_no]['values'] = options
            
    
    def pick(self,*arg):
        global judgei_target_dic
        judgei_target_dic=_load_saved_dict(path+'/judgei_target_dic.txt')
        judgei_target_dic[self.task_no]={}
        judgei_target_dic[self.task_no]['identity']=self.judge_i[self.task_no].get()
            
    def entry_event(self):
        global judgei_target_dic
        judgei_target_dic=_load_saved_dict(path+'/judgei_target_dic.txt')
        judgei_target_dic[self.task_no]={}
        judgei_target_dic[self.task_no]['identity']=self.judge_i[self.task_no].get()
        judgei_target_dic[self.task_no]['value']=self.judge_v[self.task_no].get()
        save(saved).save_var(judgei_target_dic, path+'/judgei_target_dic.txt')
        self.root.destroy()

class GUI_BE_Count:
    def __init__(self,task_no,saved_,path_):
        
        global saved,path
        saved=saved_
        path=path_
        
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=500      #window width
        wh=300      #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Define Count Parameters')
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.v=tk.IntVar()
        self.interface()
        
    def interface(self):
        #title Lable

        title_ls=['Count Length (Integer 1-10)']
        self.stimuli={}
        for r in range(1,2):
            tk.Label(self.root,text=title_ls[r-1],font=('bold',14),width=22,relief='flat',anchor='w')\
                .grid(row = r, column=0,columnspan=3,pady=20,padx=10)
                 
       
        for r in range(1,2):
            self.stimuli[(r,4)]=tk.Entry(self.root,width=22)
            self.stimuli[(r,4)].grid(row=r,column=4,columnspan=2)
            if has_saved_input(path+'/countstimuli.txt') and (r,4) in _load_saved_dict(path+'/countstimuli.txt'):
                self.stimuli[(r,4)].insert(0,_load_saved_dict(path+'/countstimuli.txt')[(r,4)])
                
        self.Button_save=tk.Button(self.root,text='Save and Go Back',font=('bold',15),bg='white',command=self.entry_event)
        
        self.Button_save.grid(row=7,column=2,columnspan=4,ipadx=5,pady=30,ipady=10)
       

    def entry_event(self):
        global length_count, n_tiral_count, mean_count, sd_count, stimuli_dic, N_count
        try:
            stimuli_dic = _load_saved_dict(path+'/countstimuli.txt')
            for r in range(1,2):
                length_count = int(self.stimuli[(r,4)].get())
                if length_count <= 0 or length_count > 10:
                    raise ValueError
                else:
                    stimuli_dic[(r,4)]=length_count
            save(saved).save_var(stimuli_dic, path+'/countstimuli.txt')
            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return #Ziqi's edition
            
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x100")
        error_label = tk.Label(error_window, text="Please enter an integer between 1 and 10 for the count length.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()

class GUI_BE_Cal_single_digit_num:
    def __init__(self,task_no,saved_,path_):  
        
        global saved,path
        saved=saved_
        path=path_
        
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=800    #window width
        wh=350   #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Define Cal_single_digit_num Parameters')
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.v=tk.IntVar()
        self.task_no=task_no
        self.interface()
        
    def interface(self):
        #title Lable
        
        arith_ls=['Choose arithmetic operations']

        self.arith={}
     
        
        value_arith=['Add (+)','Subtract (-)','Multiplication (*)','Division (/)']
        self.arith[(0,4)] = ttk.Combobox(
           master = self.root,
           state='readonly',
           cursor='arrow',
           values=value_arith, 
           )
        self.arith[(0,4)] .grid(row=0,column=4,columnspan=3)
        
        if has_saved_input(path+'/arith.txt') and (0,4) in _load_saved_dict(path+'/arith.txt'):
            saved_arith = _load_saved_dict(path+'/arith.txt')[(0,4)]
            for item in range(len(value_arith)):
                if saved_arith == value_arith[item]:
                    self.arith[(0,4)].current(item)
        
        r=0
        tk.Label(self.root,text=arith_ls[r],font=('bold',14),width=50,relief='flat',anchor='w')\
            .grid(row = r, column=0,columnspan=3,pady=20,padx=10)
        
        self.Button_next=tk.Button(self.root,text='Save and Go Back',font=('bold',15),bg='white',command=self.start_event)
        self.Button_next.grid(row=2,column=4,columnspan=1,ipadx=12,pady=15,ipady=3)
        
           
    def start_event(self):
        
        global operation
        arith_dic={}
        r=0
        arith_dic[(r,4)]=self.arith[(r,4)].get()
        save(saved).save_var(arith_dic, path+'/arith.txt')
        operation=self.arith[(0,4)].get()

        self.root.destroy()

    




def initialize_runtime_state(path_='backup/'):
    """Load saved basic-BE parameters into module globals for direct Start after Open."""
    global choice_N, judgei_target_dic, length_count, mouse_click_dimension_dic, eyeloc_ini, stimuli_dic, arith_dic, operation

    def _safe_load(filename, default):
        try:
            return save(1).load_var(filename)
        except Exception:
            return default

    choice_N = _safe_load(path_ + '/N.txt', {})
    mouse_click_dimension_dic = _safe_load(path_ + '/mouse_click_dimension.txt', {})
    eyeloc_ini = _safe_load(path_ + '/lookat.txt', {})
    judgei_target_dic = _safe_load(path_ + '/judgei_target_dic.txt', {})
    stimuli_dic = _safe_load(path_ + '/countstimuli.txt', {})
    arith_dic = _safe_load(path_ + '/arith.txt', {})

    length_count = None
    if isinstance(stimuli_dic, dict) and stimuli_dic:
        try:
            first_key = sorted(stimuli_dic.keys())[0]
            length_count = stimuli_dic[first_key]
        except Exception:
            try:
                length_count = next(iter(stimuli_dic.values()))
            except Exception:
                length_count = None

    operation = ''
    if isinstance(arith_dic, dict) and arith_dic:
        try:
            first_key = sorted(arith_dic.keys())[0]
            operation = arith_dic[first_key]
        except Exception:
            try:
                operation = next(iter(arith_dic.values()))
            except Exception:
                operation = ''
