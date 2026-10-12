# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 08:08:11 2024

@author: wyuanc
"""

"""Main GUI workflow for configuring tasks, entities, animation settings, and simulation time."""

#2.2 General GUI classes

import tkinter as tk
from tkinter import ttk 
from tkinter import filedialog, messagebox, simpledialog
import os

from utility import save_user_input as save
from utility import compound_BE, has_saved_input, reset_session_folder, set_active_project_dir

from gui_basic_BE import *
from gui_compound_BE import *

#Main menu UI
class GUI_User_Main:
   
    def __init__(self):
        
        global saved
        saved=0
        
        global path
        path='backup/'   
        reset_session_folder(path)
        self.current_project_dir = None
        self.run_accepted = False
        set_active_project_dir(None)
        
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=1000      #window width
        wh=500      #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Main Menu')
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.interface()
        
    def interface(self):
        #title Lable
        self.title=tk.Label(
            self.root,
            text='QN-MHP Software',
            font=('bold',30)
            )
        self.title.pack(pady=50)
        
        #open
        self.task=tk.Button(
            self.root,
            text='open...',
            font=('',15),
            relief='sunken',
            command=self.readFile
            )
        self.task.place(x=0,y=0,width=100,height=30)
        
        #save
        self.save_btn=tk.Button(
            self.root,
            text='save',
            font=('',15),
            relief='sunken',
            command=self.saveCurrentFile
            )
        self.save_btn.place(x=100,y=0,width=100,height=30)

        #save as
        self.save_as_btn=tk.Button(
            self.root,
            text='save as',
            font=('',15),
            relief='sunken',
            command=self.saveFile
            )
        self.save_as_btn.place(x=200,y=0,width=100,height=30)

        self.project_label = tk.Label(self.root, text='Current project: unsaved session', font=('',10), anchor='w')
        self.project_label.place(x=320, y=5, width=640, height=22)

        #define task button
        self.task=tk.Button(
            self.root,
            text='1. Define Task',
            font=('',20),
            command=self.task_event
            )
        self.task.place(x=270,y=150,width=450,height=50)
        
        #Define entity button

        self.entity=tk.Button(
            self.root,
            text='2. Define Entity and BE Parameters',
            font=('',20),
            command=self.entity_event
            )
        self.entity.place(x=270,y=230,width=450,height=50)
        
        #Define parameter button
        self.parameter=tk.Button(
            self.root,
            text='3. Define Simulation Parameters',
            font=('',20),
            command=self.parameter_event
            )
        self.parameter.place(x=270,y=310,width=450,height=50)

        #Start button
        self.Button_start=tk.Button(self.root,text='Start',font=('',20),command=self.start_simulation)
        self.Button_start.place(x=450,y=400,width=100,height=40)
        
    def _validate_tasks(self, tasks):
        """Check task definitions without changing the saved configuration."""
        errors = []
        task_ids = []
        for col in range(1, 6):
            task_id = str(tasks.get((1, col), '')).strip()
            pairs = [(str(tasks.get((row, 2 * col - 1), '')).strip(),
                      str(tasks.get((row, 2 * col), '')).strip()) for row in range(2, 18)]
            if not task_id:
                if any(be or order for be, order in pairs):
                    errors.append(f'Column {col}: select a task number.')
                continue
            if task_id in task_ids:
                errors.append(f'Task {task_id}: task number is duplicated.')
            task_ids.append(task_id)
            orders = []
            for row, (be, order) in enumerate(pairs, start=2):
                if bool(be) != bool(order):
                    errors.append(f'Task {task_id}, row {row}: select both BE and order.')
                if be and order:
                    try:
                        orders.append(int(order))
                    except ValueError:
                        errors.append(f'Task {task_id}, row {row}: order must be an integer.')
            if not orders:
                errors.append(f'Task {task_id}: add at least one BE.')
            elif len(set(orders)) != len(orders) or sorted(orders) != list(range(1, len(orders) + 1)):
                errors.append(f'Task {task_id}: BE orders must be unique and consecutive from 1.')
        if not task_ids:
            errors.append('Define at least one task.')
        return errors

    def _validate_be_parameters(self, tasks):
        """Check the required basic-BE parameters for each configured task."""
        from gui_basic_BE import _load_saved_dict
        requirements = {
            'Choice': ('N.txt', 'Choice number'),
            'Count': ('countstimuli.txt', 'Count length'),
            'Mouse_click': ('mouse_click_dimension.txt', 'Mouse-click dimension'),
            'Judge_identity': ('judgei_target_dic.txt', 'Judge-identity target'),
            'Cal_single_digit_num': ('arith.txt', 'Calculation operation'),
        }
        missing = []
        for col in range(1, 6):
            task_id = str(tasks.get((1, col), '')).strip()
            if not task_id:
                continue
            for row in range(2, 18):
                be = tasks.get((row, 2 * col - 1), '')
                if be not in requirements:
                    continue
                filename, label = requirements[be]
                values = _load_saved_dict(os.path.join(path, filename))
                if be == 'Count':
                    value = values.get((1, 4))
                    valid = type(value) is int and 1 <= value <= 10
                elif be == 'Choice':
                    value = values.get(int(task_id))
                    valid = type(value) is int and 1 <= value <= 6
                elif be == 'Mouse_click':
                    valid = str(values.get(int(task_id), '')) in ('1', '2', '3')
                elif be == 'Judge_identity':
                    value = values.get(task_id, values.get(int(task_id)))
                    valid = isinstance(value, dict) and bool(value.get('identity')) and bool(value.get('value'))
                else:
                    valid = bool(values) and any(v not in ('', None) for v in values.values())
                if not valid:
                    item = f'Task {task_id}: {be} — {label}'
                    if item not in missing:
                        missing.append(item)
        return missing

    def _validate_entity_parameters(self, tasks):
        """Require valid entity rows for tasks that use See or Hear."""
        from gui_basic_BE import _load_saved_dict
        errors = []
        for col in range(1, 6):
            task_id = str(tasks.get((1, col), '')).strip()
            if not task_id:
                continue
            for be in ('See', 'Hear'):
                if not any(tasks.get((row, 2 * col - 1)) == be for row in range(2, 18)):
                    continue
                data = _load_saved_dict(os.path.join(path, f'entity_dic_{be.lower()}.txt'))
                configured = False
                for row in range(2, 6):
                    kind = data.get((row, 1, task_id), '')
                    fields = [str(data.get((row, c, task_id), '')).strip() for c in (2, 3, 4)]
                    if kind or any(fields):
                        configured = True
                        if kind == 'Color':
                            text_only = [name for name in ('Count', 'Cal_single_digit_num')
                                         if any(tasks.get((r, 2 * col - 1)) == name for r in range(2, 18))]
                            for name in text_only:
                                errors.append(f'Task {task_id}: {name} does not support Color entities. Select Text.')
                        if kind not in ('Color', 'Text') or not all(v.isdigit() for v in fields):
                            errors.append(f'Task {task_id}, {be}: complete entity type, arrival, IAT and occurrences (non-negative integers).')
                if not configured:
                    errors.append(f'Task {task_id}, {be}: configure at least one entity.')
        return errors

    def start_simulation(self):
        """Run a valid saved or edited project, offering Save / Save As / Don't Save."""
        task_file = os.path.join(path, 'task_info_dic.txt')
        if not has_saved_input(task_file):
            messagebox.showwarning('Step 1: Define Task', 'Define and save at least one task.', parent=self.root)
            return
        try:
            tasks = save(1).load_var(task_file)
            if not isinstance(tasks, dict):
                raise ValueError('Task data must be a dictionary')
        except Exception:
            messagebox.showerror('Step 1: Define Task', 'Unable to read the task definition.', parent=self.root)
            return
        errors = self._validate_tasks(tasks)
        if errors:
            messagebox.showwarning('Step 1: Define Task', '\n'.join(errors), parent=self.root)
            return
        errors = self._validate_be_parameters(tasks) + self._validate_entity_parameters(tasks)
        if errors:
            messagebox.showwarning('Step 2: Entity and BE Parameters', '\n'.join(errors), parent=self.root)
            return
        try:
            simtime = save(1).load_var(os.path.join(path, 'simtime.txt'))
            animation = save(1).load_var(os.path.join(path, 'anim.txt'))
            if type(simtime) is not int or simtime <= 0 or animation not in (0, 1):
                raise ValueError
        except Exception:
            messagebox.showwarning('Step 3: Simulation Parameters',
                                   'Enter and save a positive simulation time and animation choice.', parent=self.root)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title('Save before simulation?')
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text='Would you like to save the project before running?',
                 font=('', 13), padx=22, pady=20).pack()
        buttons = tk.Frame(dialog)
        buttons.pack(padx=16, pady=(0, 18))
        choice = {'value': 'cancel'}
        def choose(value):
            choice['value'] = value
            dialog.destroy()
        for label, value in [('Save', 'save'), ('Save As', 'save_as'),
                             ("Don't Save", 'skip'), ('Cancel', 'cancel')]:
            tk.Button(buttons, text=label, width=12,
                      command=lambda v=value: choose(v)).pack(side='left', padx=4)
        dialog.protocol('WM_DELETE_WINDOW', lambda: choose('cancel'))
        self.root.wait_window(dialog)
        action = choice['value']
        if action == 'cancel':
            return
        if action in ('save', 'save_as'):
            completed = self.saveCurrentFile(show_message=False) if action == 'save' else self.saveFile(show_message=False)
            if not completed:
                return
        self.run_accepted = True
        self.root.destroy()

    def task_event(self):
        GUI_task_def_step1().root.mainloop()
        
    def parameter_event(self):
        GUI_simulation_parameter(saved).root.mainloop()
        
    def entity_event(self):
        GUI_entity_parameter(saved,path).root.mainloop()
        
    def _update_project_label(self):
        if self.current_project_dir:
            display_dir = os.path.abspath(self.current_project_dir)
            self.project_label.config(text=f'Current project: {display_dir}')
        else:
            self.project_label.config(text='Current project: unsaved session')

    def saveCurrentFile(self, show_message=True):
        if not self.current_project_dir:
            return self.saveFile(show_message=show_message)
        save(0).copy_search_file('backup/', self.current_project_dir)
        set_active_project_dir(self.current_project_dir)
        self._update_project_label()
        if show_message:
            messagebox.showinfo('Save', f'Configuration saved to:\n{self.current_project_dir}')
        return True

    def saveFile(self, show_message=True):
        parent_dir = filedialog.askdirectory(title='Select a parent folder to save the current configuration')
        if not parent_dir:
            return

        if self.current_project_dir:
            default_name = os.path.basename(self.current_project_dir.rstrip('/\\'))
        else:
            default_name = 'qn_mhp_project'

        project_name = simpledialog.askstring(
            'Save As',
            'Enter a folder name for this project:',
            initialvalue=default_name,
            parent=self.root
        )
        if not project_name:
            return

        project_name = project_name.strip()
        if not project_name:
            messagebox.showerror('Save As', 'Project folder name cannot be empty.')
            return

        target_dir = os.path.join(parent_dir, project_name)
        os.makedirs(target_dir, exist_ok=True)
        save(0).copy_search_file('backup/', target_dir)
        self.current_project_dir = target_dir
        set_active_project_dir(target_dir)
        self._update_project_label()
        if show_message:
            messagebox.showinfo('Save As', f'Configuration saved to:\n{target_dir}')
        return True
    
    def readFile(self):
        source_dir = filedialog.askdirectory(title='Select a saved configuration folder to open')
        if not source_dir:
            return
        if not save(0).folder_has_project_data(source_dir):
            messagebox.showerror('Open', 'The selected folder does not contain a saved QN-MHP configuration.')
            return
        save(0).load_search_file(source_dir, 'backup/')
        self.current_project_dir = source_dir
        set_active_project_dir(source_dir)
        global saved
        saved=0
        global path, task_info_dic
        path='backup/'
        task_info_dic = save(1).load_var(os.path.join(path, 'task_info_dic.txt'))
        self._update_project_label()
        messagebox.showinfo('Open', f'Configuration loaded from:\n{source_dir}\n\nYou can continue editing and click Save to overwrite this project folder.')


#define task UI
class GUI_task_def_step1:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Define Task step1: define task number, BE, and order')
        sw=self.root.winfo_screenwidth() 
        ww=1200
        sh=self.root.winfo_screenheight()   
        wh=800
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.interface()
        # Closing the task editor through the window close control must not
        # silently discard edits. Validate and save just like the Save button.
        self.root.protocol('WM_DELETE_WINDOW', self.save_event)

    def interface(self):
        for r in range(100):
            self.root.rowconfigure(r,weight=1)
        for c in range(100):
            self.root.columnconfigure(c,weight=1)
        #title
        tk.Label(self.root,text='Step1: set task number, choose the behavior elements in each task and their corresponding order',font=('bold',14),anchor='w')\
            .grid(row = 0,column=0,pady=10,columnspan=10,sticky='w')
        #tk.Label(self.root,text='Step2: click the Apply button, and click the b_e button in the automatically generated task list to open the setting interface of the selected b_e',font=('bold',14))\
            #.grid(row = 19,column=0,pady=3,columnspan=18,sticky='w')
        self.l_tn= tk.Label(self.root,text='Task No.',font=('bold',14),relief='ridge',width=8)
        self.l_tn.grid(row = 1,column=0,pady=1,padx=1)
        self.l_order=tk.Label(self.root,text='Behavior\n Elements\n and \n Order',font=('bold',14),relief='ridge',height=32)
        self.l_order.grid(row = 2,column=0,rowspan=16,pady=1)
        
        #Combobox
        self.combobox={}
        global tbd_list
        tbd_list=['TBD1','TBD2','TBD3']
        save(saved).save_var(tbd_list, path+'/tbd_list.txt')
        for r in range(2,18):
            for c in range(1,11):
                if c%2==0: #choose order
                    self.value = tk.StringVar()
                    
                    value_order = ['',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
                    self.combobox[(r,c)] = ttk.Combobox(
                        master = self.root,
                        width=2,
                        state='readonly',
                        cursor='arrow',
                        values=value_order,
                        #textvariable=self.value,
                        font=('bold',10)
                        )
                    self.combobox[(r,c)].bind('<<ComboboxSelected>>',self.pick)
                    self.combobox[(r,c)].grid(row=r,column=c)   
                    
                    if has_saved_input(path+'/task_info_dic.txt') and save(1).load_var(path+'/task_info_dic.txt')[(r,c)]!='':
                        self.combobox[(r,c)].current(eval(save(1).load_var(path+'/task_info_dic.txt')[(r,c)]))
                    else:
                        self.combobox[(r,c)].current(0)
                      
                        
                else: #choose behavior elements
                    self.value = tk.StringVar()
                    value_be = ['','See','Hear','Store_to_WM','Choice','Judge_identity',\
                                'Count','Cal_single_digit_num','Press_button','Mouse_click','Look_at',\
                                    'Look_for','Tracking_1D','Tracking_1D_1W','Tracking_1D_Random',\
                                        'Tracking_2D','Tracking_2D_Random','Tracking_2D_1W',\
                                        'Tracing_1D_Bounded','Tracing_1D_1W','Tracing_2D_Bounded','Tracing_2D_1W']#'UD_ST','UD_BE'
                    self.combobox[(r,c)] = ttk.Combobox(
                        master = self.root,
                        width=18,
                        state='readonly',
                        cursor='arrow',
                        values=value_be,  
                        font=('bold',10)
                        )
                    self.combobox[(r,c)].bind('<<ComboboxSelected>>',self.pick)
                    self.combobox[(r,c)].grid(row=r,column=c)
                    if has_saved_input(path+'/task_info_dic.txt') and save(1).load_var(path+'/task_info_dic.txt')[(r,c)]!='':
                        for item in range(len(value_be)):
                            if save(1).load_var(path+'/task_info_dic.txt')[(r,c)]==value_be[item]:
                                self.combobox[(r,c)].current(item)
                    else:
                        self.combobox[(r,c)].current(0)
        global sub_info_dic
        sub_info_dic={}
        save(saved).save_var(sub_info_dic, path+'/sub_info_dic.txt')           

        self.Button_save=tk.Button(self.root,text='Save and Back to Main Menu',font=16,command=self.save_event)
        self.Button_save.grid(row=18,column=7,columnspan=3,pady=30,ipady=3)

        for c in range(1,6):
            self.value = tk.StringVar()
            self.value.set('')
            value_tn = ['',1,2,3,4,5]
            self.combobox[(1,c)] = ttk.Combobox(
                master = self.root,
                state='readonly',
                cursor='arrow',
                values=value_tn, 
                width=28
                )
            self.combobox[(1,c)].bind('<<ComboboxSelected>>',self.pick)
            self.combobox[(1,c)].grid(row=1,column=2*c-1,padx=0.5,columnspan=2)
            
            if has_saved_input(path+'/task_info_dic.txt') and save(1).load_var(path+'/task_info_dic.txt')[(1,c)]!='':
                self.combobox[(1,c)].current(eval(save(1).load_var(path+'/task_info_dic.txt')[(1,c)]))
                #print(self.combobox[(1,c)].get())
            else:
                self.combobox[(1,c)].current(0)
            
 
    #get combobox user input    
    def pick(self,*arg):
        global task_info_dic,task_info_dic_f
        task_info_dic={}
        for r in range(1,18):
            if r==1:
                for c in range(1,6):
                    task_info_dic[(r,c)]=self.combobox[(r,c)].get()
            else:                    
                for c in range(1,11):
                    task_info_dic[(r,c)]=self.combobox[(r,c)].get()
        # Changes are committed only after Step 1 validation on Save.

    
    def save_event(self):
        global task_info_dic,task_info_dic_f
        task_info_dic={}
        for r in range(1,18):
            if r==1:
                for c in range(1,6):
                    task_info_dic[(r,c)]=self.combobox[(r,c)].get()
            else:                    
                for c in range(1,11):
                    task_info_dic[(r,c)]=self.combobox[(r,c)].get()
        errors = GUI_User_Main._validate_tasks(self, task_info_dic)
        if errors:
            messagebox.showwarning('Step 1: Define Task', '\n'.join(errors), parent=self.root)
            return
        task_info_dic_f=save(saved).save_var(task_info_dic,path+'/task_info_dic.txt')
        self.root.destroy()
        
                                       

#define simulation parameters           
class GUI_simulation_parameter:
    def __init__(self,saved_):
        
        global saved
        saved=saved_
        
        self.root = tk.Tk()    
        sw=self.root.winfo_screenwidth()        #screen width
        sh=self.root.winfo_screenheight()       #screen height
        ww=800      #window width
        wh=400      #window height
        x=(sw-ww)/2  #window coordinate (left_up point)
        y=(sh-wh)/2  #window coordinate
        self.root.title('Define Simulation Parameters')
        self.root.geometry('%dx%d+%d+%d'%(ww,wh,x,y))
        self.v=tk.IntVar()
        self.interface()
        self.root.protocol('WM_DELETE_WINDOW', self.event)
        
    def interface(self):
        
        #label
        self.simtime=tk.Label(
            self.root,
            text='Simulation Time (msec):',
            font=('bold',17)
            )
        self.simtime.place(x=20,y=50)

        self.animation=tk.Label(
            self.root,
            text='Animation:',
            font=('bold',17)
            )
        
        
        self.animation.place(x=20,y=200)
        
        #entry 
        self.entry_simtime=tk.Entry(self.root,font=('',15))
        self.entry_simtime.place(x=400,y=50,width=120,height=40)
        
        if has_saved_input(path+'/simtime.txt'):
            self.entry_simtime.insert(0,save(1).load_var(path+'/simtime.txt'))

        #Radiobutton  

        if has_saved_input(path+'/anim.txt'):
            if save(1).load_var(path+'/anim.txt') == 1:
                self.choose = tk.StringVar(self.root,"yes")
            else:
                self.choose = tk.StringVar(self.root,"no")
        else:
            self.choose = tk.StringVar(self.root, "yes")

        self.rb_yes=tk.Radiobutton(
            self.root,
            text='YES',
            font=('',15),
            variable=self.choose,
            value='yes',
            borderwidth=10,
            )
        self.rb_yes.place(x=2*100,y=190)
        
        self.rb_no=tk.Radiobutton(
            self.root,
            text='NO',
            font=('',15),
            variable=self.choose,
            value='no',
            borderwidth=10,
            )
        self.rb_no.place(x=3*100,y=190)       
        
        #ok button
        self.Button_ok=tk.Button(self.root,text='Save and Back to Main Menu',font=('',18),command=self.event)
        self.Button_ok.place(x=400,y=350,height=40)
        
    def event(self):
        global SIMTIME, IAT, Choice_num, anim, Presented_num
        try:
            SIMTIME = int(self.entry_simtime.get())
            if SIMTIME <= 0:
                raise ValueError
            
            if self.choose.get() == 'yes':
                anim = 1
            else:
                anim = 0
            save(saved).save_var(anim, path+'/anim.txt')
            save(saved).save_var(SIMTIME, path+'/simtime.txt')
            self.root.destroy()
        except ValueError:
            self.show_error_message()
            return 
    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("500x100")
        error_label = tk.Label(error_window, text="Please enter a positive number for simulation time.", font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack() 
   
    

entity_dic = {}
entity_dic_see = {}
entity_dic_hear = {}

class GUI_entity_parameter:
    def __init__(self, saved_, path_):
        global saved, path
        saved = saved_
        path = path_

        self.root = tk.Tk()
        sw = self.root.winfo_screenwidth()  # screen width
        sh = self.root.winfo_screenheight()  # screen height
        ww = 800  # window width
        wh = 400  # window height
        x = (sw - ww) / 2  # window coordinate (left_up point)
        y = (sh - wh) / 2  # window coordinate
        self.root.title('Define Entity and BE Parameters')
        self.root.geometry('%dx%d+%d+%d' % (ww, wh, x, y))
        self.v = tk.IntVar()
        self.entity = {}

        self.basic_1_methods = {
            'See': None,
            'Hear': None,
            'Press_button': None
        }

        self.basic_2_methods = {
            'Choice': self.choice_BE,
            'Judge_identity': self.judgei_BE,
            'Look_at': self.lookat_BE,
            'Cal_single_digit_num': self.cal_single_digit_num_BE,
            'Count': self.count_BE,
            'Mouse_click': self.mouseclick_BE
        }
        self.comp_be_methods = {
            'Look_for': self.lookfor_BE,
            'Tracking_1D': self.track1D_BE,
            'Tracking_1D_1W': self.track1D_1w_BE,
            'Tracking_1D_Random': self.track1D_r_BE,
            'Tracking_2D': self.track2D_BE,
            'Tracking_2D_Random': self.track2D_r_BE,
            'Tracking_2D_1W': self.track2D_1w_BE,
            'Tracing_1D_Bounded': self.tracing1D_b_BE,
            'Tracing_1D_1W': self.tracing1D_1w_BE,
            'Tracing_2D_Bounded': self.tracing2D_b_BE,
            'Tracing_2D_1W': self.tracing2D_1w_BE
        }

        self.interface()

    def _task_column(self, task_no):
        task_no = str(task_no)
        for c in range(1, 6):
            if task_info_dic.get((1, c), '') == task_no:
                return c
        return None

    def _task_has_be(self, task_no, be_name):
        task_col = self._task_column(task_no)
        if task_col is None:
            return False
        be_col = 2 * task_col - 1
        return any(task_info_dic.get((r, be_col), '') == be_name for r in range(2, 18))

    def _resolve_entity_label(self, task_no, label_text=None):
        if label_text in ('See', 'Hear'):
            return label_text
        has_see = self._task_has_be(task_no, 'See')
        has_hear = self._task_has_be(task_no, 'Hear')
        if has_see and not has_hear:
            return 'See'
        if has_hear and not has_see:
            return 'Hear'
        if has_see and has_hear:
            return 'See'
        return label_text

    def _entity_filename(self, label_text):
        if label_text == 'See':
            return path + '/entity_dic_see.txt'
        if label_text == 'Hear':
            return path + '/entity_dic_hear.txt'
        return None

    def _load_entity_dict(self, label_text):
        filename = self._entity_filename(label_text)
        if not filename or not has_saved_input(filename):
            return {}
        try:
            data = save(1).load_var(filename)
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    def _save_entity_dict(self, label_text, data):
        filename = self._entity_filename(label_text)
        if filename:
            save(saved).save_var(data, filename)

    def interface(self):
        tk.Label(self.root, text="Please Click Buttons to Define Entity and/or BE Parameters for Each Task",
                 font=('bold', 14)).grid(row=0, column=0, columnspan=5, padx=10, pady=10)

        for c in range(1, 6):
            if task_info_dic[(1, c)] != '':
                self.task_no = task_info_dic[(1, c)]
                tk.Label(self.root, font=16, height=1, width=12, text=f"Task {self.task_no}").grid(row=1, column=c-1, padx=5, pady=5)

                frame = tk.Frame(self.root)
                frame.grid(row=2, column=c-1, padx=5, pady=5, sticky="n")

                for r in range(2, 18):
                    label_text = task_info_dic.get((r, 2 * c - 1), '')

                    def create_command(be_method, be_name, task_no=self.task_no, row=r):
                        if row != 2:
                            return lambda t=task_no: be_method(t)
                        resolved_label = self._resolve_entity_label(task_no)
                        return lambda t=task_no, lt=resolved_label: self.event(t, step=2, be=be_name, label_text=lt)

                    if label_text in self.basic_1_methods:
                        if label_text in ('See', 'Hear') or r == 2:
                            tk.Button(
                                frame,
                                text=label_text,
                                width=15,
                                command=lambda t=self.task_no, lt=label_text: self.event(t, 1, be=None, label_text=lt)
                            ).pack(anchor='w', pady=5)
                        else:
                            tk.Label(frame, text=label_text, width=12).pack(anchor='w', pady=5)

                    elif label_text in self.basic_2_methods:
                        command = create_command(self.basic_2_methods[label_text], label_text)
                        tk.Button(frame, text=label_text, width=15, command=command).pack(anchor='w', pady=5)

                    elif label_text in self.comp_be_methods:
                        key = label_text
                        tk.Button(
                            frame,
                            text=label_text,
                            width=15,
                            command=lambda t=self.task_no, key=key: self.comp_be_methods[key](t)
                        ).pack(anchor='w', pady=5)

                    else:
                        tk.Label(frame, text=label_text, width=12).pack(anchor='w', pady=5)

        Button_ok = tk.Button(self.root, text='Save and Back to Main Menu', font=('', 18), command=self.ok_event)
        Button_ok.place(x=400, y=250, height=40)

    def ok_event(self):
        try:
            tasks = save(1).load_var(os.path.join(path, 'task_info_dic.txt'))
            errors = GUI_User_Main._validate_be_parameters(self, tasks)
            errors += GUI_User_Main._validate_entity_parameters(self, tasks)
        except Exception:
            errors = ['Unable to read the saved task or BE settings.']
        if errors:
            messagebox.showwarning('Step 2: Entity and BE Parameters', '\n'.join(errors), parent=self.root)
            return
        self.root.destroy()

    def _text_only_bes(self, task_no):
        """Return BEs in this task that require Text entities."""
        from gui_basic_BE import _load_saved_dict
        tasks = _load_saved_dict(os.path.join(path, 'task_info_dic.txt'))
        names = ('Count', 'Cal_single_digit_num')
        return [name for name in names if any(
            str(tasks.get((1, col), '')).strip() == str(task_no)
            and any(tasks.get((row, 2 * col - 1)) == name for row in range(2, 18))
            for col in range(1, 6)
        )]

    def _reject_color_for_text_only_be(self, row):
        """Warn immediately and clear Color when the task requires Text."""
        widget = self.entity[(row, 1, self.task_no)]
        text_only = self._text_only_bes(self.task_no)
        if widget.get() == 'Color' and text_only:
            widget.set('')
            name = ' and '.join(text_only)
            messagebox.showwarning(
                'Text entity required',
                f'{name} does not support Color entities. Please select Text.',
                parent=widget.winfo_toplevel(),
            )
            return True
        return False

    def event(self, task_no, step, be, label_text=None):
        self.task_no = task_no
        label_text = self._resolve_entity_label(task_no, label_text)
        saved_entity_data = self._load_entity_dict(label_text)

        new_window = tk.Toplevel(self.root)
        window_label = label_text if label_text else 'Entity'
        new_window.title(f"Define Entity Parameters: {window_label} - Task {task_no}")
        new_window.grid_columnconfigure(0, minsize=70)
        for col in range(1, 5):
            new_window.grid_columnconfigure(col, minsize=240, weight=1)

        title_text = f"Choose the entities to be processed for {window_label} and set the corresponding parameters"
        tk.Label(
            new_window,
            text=title_text,
            font=('bold', 14),
            wraplength=1100,
            justify='left'
        ).grid(row=0, column=0, pady=8, padx=10, columnspan=10, sticky='w')

        title_ls = ['Entity', 'First Arrival Time (msec)', 'IAT (msec)', 'Occurrences']
        for c in range(1, 5):
            tk.Label(new_window, text=title_ls[c - 1], font=('bold', 14), width=24, relief='sunken')                .grid(row=1, column=c, padx=4, pady=2, sticky='nsew')

        for r in range(2, 6):
            tk.Label(new_window, text=str(r - 1), font=('bold', 14), width=5, relief='sunken')                .grid(row=r, column=0, padx=4, pady=2, sticky='nsew')

        value_entity = ['', 'Color', 'Text']
        for r in range(2, 6):
            self.entity[(r, 1, self.task_no)] = ttk.Combobox(
                master=new_window,
                width=30,
                state='readonly',
                cursor='arrow',
                values=value_entity,
                font=('bold', 10)
            )
            self.entity[(r, 1, self.task_no)].bind('<<ComboboxSelected>>', lambda *args, row=r, lt=label_text: (None if self._reject_color_for_text_only_be(row) else self.pick(lt)))
            self.entity[(r, 1, self.task_no)].grid(row=r, column=1)

            saved_value = saved_entity_data.get((r, 1, self.task_no), '')
            if saved_value in value_entity:
                self.entity[(r, 1, self.task_no)].current(value_entity.index(saved_value))
            else:
                self.entity[(r, 1, self.task_no)].current(0)

        for r in range(2, 6):
            for c in range(2, 5):
                self.entity[(r, c, self.task_no)] = tk.Entry(new_window, width=30)
                self.entity[(r, c, self.task_no)].grid(row=r, column=c)
                self.entity[(r, c, self.task_no)].insert(0, saved_entity_data.get((r, c, self.task_no), ''))

        if step == 1:
            button_ok = tk.Button(new_window, text='Save and Back to Tasks', font=16, command=lambda: self.entry_event(new_window, label_text))
            button_ok.grid(row=6, rowspan=3, column=3, columnspan=2, pady=20, ipady=3)
        elif step == 2 and be in self.basic_2_methods:
            button_next = tk.Button(
                new_window,
                text=f'Next: Define {be} Parameter',
                font=16,
                command=lambda t=self.task_no, lt=label_text: self._save_then_next(new_window, lt, self.basic_2_methods[be], t)
            )
            button_next.grid(row=6, rowspan=3, column=3, columnspan=2, pady=20, ipady=3)

        new_window.update_idletasks()
        req_w = max(new_window.winfo_reqwidth() + 40, 1120)
        req_h = max(new_window.winfo_reqheight() + 40, 340)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max((sw - req_w) // 2, 0)
        y = max((sh - req_h) // 2, 0)
        new_window.geometry(f"{req_w}x{req_h}+{x}+{y}")
        new_window.minsize(req_w, req_h)

    def _save_then_next(self, window, label_text, method, task_no):
        if self.entry_event(window, label_text):
            method(task_no)

    def pick(self, label_text=None):
        global entity_dic_see, entity_dic_hear
        label_text = self._resolve_entity_label(self.task_no, label_text)
        if label_text not in ('See', 'Hear'):
            return

        current_entity_dic = self._load_entity_dict(label_text)
        for r in range(2, 6):
            current_entity_dic[(r, 1, self.task_no)] = self.entity[(r, 1, self.task_no)].get()

        if label_text == 'See':
            entity_dic_see = current_entity_dic
        elif label_text == 'Hear':
            entity_dic_hear = current_entity_dic

        self._save_entity_dict(label_text, current_entity_dic)

    def entry_event(self, window, label_text=None):
        global entity_dic, entity_dic_hear, entity_dic_see
        label_text = self._resolve_entity_label(self.task_no, label_text)
        try:
            for r in range(2, 6):
                row_filled = (bool(self.entity[(r, 1, self.task_no)].get().strip()) or
                              any(self.entity[(r, c, self.task_no)].get().strip() for c in range(2, 5)))
                if row_filled:
                    if self._reject_color_for_text_only_be(r):
                        return False
                    if not self.entity[(r, 1, self.task_no)].get().strip():
                        raise ValueError(f"Please select an entity type in row {r}.")
                    for c in range(2, 5):
                        val_str = self.entity[(r, c, self.task_no)].get().strip()
                        if val_str == "":
                            raise ValueError(f"Please fill all required fields in row {r}.")
                        if not val_str.isdigit() or int(val_str) < 0:
                            raise ValueError(f"Please enter a non-negative integer at row {r}, column {c}.")

            current_entity_dic = self._load_entity_dict(label_text)
            for r in range(2, 6):
                entity_value = self.entity[(r, 1, self.task_no)].get()
                current_entity_dic[(r, 1, self.task_no)] = entity_value
                entity_dic[(r, 1, self.task_no)] = entity_value
                for c in range(2, 5):
                    entry_value = self.entity[(r, c, self.task_no)].get().strip() if self.entity[(r, c, self.task_no)].get().strip() else ''
                    current_entity_dic[(r, c, self.task_no)] = entry_value
                    entity_dic[(r, c, self.task_no)] = entry_value

            if label_text == 'See':
                entity_dic_see = current_entity_dic
            elif label_text == 'Hear':
                entity_dic_hear = current_entity_dic

            self._save_entity_dict(label_text, current_entity_dic)
            save(saved).save_var(entity_dic, path + '/entity_dic.txt')
            window.destroy()
            return True

        except ValueError as e:
            self.show_error_message(window, str(e))
            return False

    def show_error_message(self, parent_window, message):
        error_window = tk.Toplevel(parent_window)
        error_window.title("Input Error")
        error_window.geometry("400x100")
        error_label = tk.Label(error_window, text=message, font=("Arial", 12))
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()

    def choice_BE(self,task_no):
        GUI_BE_Choice(task_no,saved,path).root.mainloop()                
    def judgei_BE(self,task_no):
        GUI_BE_Judgei(task_no,saved,path).root.mainloop()
    def lookat_BE(self,task_no):
        GUI_BE_Lookat(task_no,saved,path).root.mainloop()
    def mouseclick_BE(self,task_no):
        GUI_BE_Mouseclick(task_no,saved,path).root.mainloop()
    def lookfor_BE(self,task_no):
        GUI_BE_Lookfor(task_no,saved,path).root.mainloop()
    def cal_single_digit_num_BE(self,task_no):
        GUI_BE_Cal_single_digit_num(task_no,saved,path).root.mainloop()
    def count_BE(self,task_no):
        GUI_BE_Count(task_no,saved,path).root.mainloop()
    def track1D_BE(self,task_no):
        GUI_BE_track1D(task_no,saved,path).root.mainloop()
    def track1D_1w_BE (self,task_no):
        GUI_BE_track1D_1w(task_no,saved,path).root.mainloop()
    def track1D_r_BE (self,task_no):
        GUI_BE_track1D_r(task_no,saved,path).root.mainloop()
    def track2D_BE(self,task_no):
        GUI_BE_track2D(task_no,saved,path).root.mainloop()
    def track2D_r_BE(self,task_no):
        GUI_BE_track2D_r(task_no,saved,path).root.mainloop()
    def track2D_1w_BE(self,task_no):
        GUI_BE_track2D_1w(task_no,saved,path).root.mainloop()
    def tracing1D_1w_BE(self,task_no):
        GUI_BE_tracing1D_1w(task_no,saved,path).root.mainloop()
    def tracing1D_b_BE(self,task_no):
        GUI_BE_tracing1D_b(task_no,saved,path).root.mainloop()
    def tracing2D_b_BE(self,task_no):
        GUI_BE_tracing2D_b(task_no,saved,path).root.mainloop()
    def tracing2D_1w_BE(self,task_no):
        GUI_BE_tracing2D_1w(task_no,saved,path).root.mainloop()



def _initialize_runtime_gui_state():
    """Populate module-level GUI parameter globals from saved files so an opened
    project can be started immediately without re-clicking every Save button.
    """
    import gui_basic_BE
    import gui_compound_BE
    if hasattr(gui_basic_BE, 'initialize_runtime_state'):
        gui_basic_BE.initialize_runtime_state(path)
    if hasattr(gui_compound_BE, 'initialize_runtime_state'):
        gui_compound_BE.initialize_runtime_state(path)


def run():
    user_interface = GUI_User_Main()
    user_interface.root.mainloop()
    if not user_interface.run_accepted:
        return False
    global Tasklist_dic,anim,SIMTIME,task_info_dic
    Task_dic ={}
    tbd_list=save(saved).load_var(path+'/tbd_list.txt')
    anim=save(saved).load_var(path+'/anim.txt')
    SIMTIME=save(saved).load_var(path+'/simtime.txt')
    task_info_dic=save(saved).load_var(path+'/task_info_dic.txt')
    _initialize_runtime_gui_state()
    global entity_dic, entity_dic_see, entity_dic_hear
    from gui_basic_BE import _load_saved_dict
    entity_dic = _load_saved_dict(os.path.join(path, 'entity_dic.txt'))
    entity_dic_see = _load_saved_dict(os.path.join(path, 'entity_dic_see.txt'))
    entity_dic_hear = _load_saved_dict(os.path.join(path, 'entity_dic_hear.txt'))
    #N=save(saved).load_var(path+'/N.txt')
    
    Tasklist_dic={}
    for item in range(1,6):
        Task_dic[item]=[]
    for j in range(1,6):
        order=[]
        if task_info_dic[(1,j)]!='':
            k=eval(task_info_dic[(1,j)])
            for i in range(2,18):
                if task_info_dic[(i,2*j-1)]!='':
                    Task_dic[k].append((task_info_dic[(i,2*j-1)],eval(task_info_dic[(i,2*j)])))
            for item in Task_dic[k]:
                order.append(item[1])
            max_order=max(order)
            Tasklist_dic[k]=[[] for item in range(max_order)]
            for item in range(max_order):
                for t in Task_dic[k]:
                    if t[1]==item+1:
                        Tasklist_dic[k][item].append(t[0])
    

    return True
