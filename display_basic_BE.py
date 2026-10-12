# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 11:55:02 2024

@author: wyuanc
"""
"""Display primitives and animation support for basic behavior-element tasks."""

import time
import tkinter as tk
from tkinter import messagebox
from gui_general import task_info_dic
from qn_mhp_layout import myCanvas
from utility import color_changer, look_for_ls,color_list,text_list
from mouse_click_layout import button_geometry, button_depth

if 'Press_button' in task_info_dic.values() or 'Mouse_click' in task_info_dic.values():
    class reaction_press_button:
   
        def __init__(self,task_no):
            
            self.task_no = task_no
            from gui_basic_BE import choice_N
            self.N = choice_N[self.task_no]
            from gui_basic_BE import mouse_click_dimension_dic
            # Only Choice + Mouse_click uses dimension-specific button layouts.
            # Choice + Press_button retains its familiar horizontal layout.
            self.choice_mouse_click = False
            self.dimension = 1
            try:
                from basic_BE import Tasklist_dic, _is_choice_mouse_click
                if _is_choice_mouse_click(Tasklist_dic[self.task_no]):
                    self.choice_mouse_click = True
                    self.dimension = int(mouse_click_dimension_dic[self.task_no])
            except (KeyError, ValueError, TypeError):
                pass
        
        def background(self,sti_type):
            self.root = tk.Tk()
            self.w = self.root.winfo_screenwidth() / 2
            self.h = self.root.winfo_screenheight() / 5
            self.frame = myCanvas(self.root, self.w, self.h)  # Assuming myCanvas is defined elsewhere
            self.frame.canvas.pack(fill="both", expand=True)
            self.root.title('Mouse Click — %sD' % self.dimension if self.choice_mouse_click else 'Reaction')
            self.root.geometry('%dx%d+%d+%d' % (self.w, self.h, 0, self.root.winfo_screenheight() / 1.7))
            
            
            
            frame=self.frame
            w=self.w
            h=self.h
            N=self.N
            
            self.sti_type=sti_type
            
            if sti_type=='color':
               
                if N == 1:
                    frame.canvas.create_rectangle(w / 2 - 80, h / 2 - 18, w / 2 + 80, h / 2 + 18, fill='red', outline='red')
                else:
                    for c in range(N):
                        color = color_list[c]
                        cx, cy, bw, bh = button_geometry(c, N, w, h, self.dimension)
                        frame.canvas.create_rectangle(cx-bw/2, cy-bh/2, cx+bw/2, cy+bh/2,
                                                      fill=color_changer(color[0], color[1], color[2]))
                        if self.choice_mouse_click and self.dimension == 3:
                            frame.canvas.create_text(cx, cy + bh/2 + 12,
                                                     text=f'({cx:.0f}, {cy:.0f}, {button_depth(c, N):.0f})',
                                                     font=('Arial', 10))
            elif sti_type=='text':
                if N==1:
                    frame.canvas.create_rectangle(w/2-80,h/2-18,w/2+80,h/2+18,fill='white',outline='white')
                    frame.canvas.create_text(w/2, h/2,anchor='center',text='A',font=("Times New Roman",15,"bold"))
                else:
                    for c in range(N):
                        text=text_list[c]
                        cx, cy, bw, bh = button_geometry(c, N, w, h, self.dimension)
                        frame.canvas.create_rectangle(cx-bw/2, cy-bh/2, cx+bw/2, cy+bh/2,fill='white')
                        frame.canvas.create_text(cx, cy,anchor='center',text=text,font=("Times New Roman",15,"bold"))
                        if self.choice_mouse_click and self.dimension == 3:
                            frame.canvas.create_text(cx, cy + bh/2 + 12,
                                                     text=f'({cx:.0f}, {cy:.0f}, {button_depth(c, N):.0f})',
                                                     font=('Arial', 10))
        
            # Draw the initial targets before gray overlays are applied.
            # A one-time refresh is intentional for macOS Tk rendering.
            self.root.update_idletasks()
            self.root.update()

        def add_button(self, i):
            
            if self.sti_type=='color':
            
                if self.N == 1:
                    self.frame.canvas.create_rectangle(self.w / 2 - 80, self.h / 2 - 18, self.w / 2 + 80, self.h / 2 + 18,
                                                       fill='gray', outline='gray', tag='button_rec')
                    self.frame.canvas.update()
                    time.sleep(0.4)
                    self.frame.canvas.delete('button_rec')
                    self.frame.canvas.update()
                else:
                    for item in range(self.N):
                        if i[1]['color'] == color_list[item]:
                            cx, cy, bw, bh = button_geometry(item, self.N, self.w, self.h, self.dimension)
                            self.frame.canvas.create_rectangle(cx-bw/2, cy-bh/2,
                                                               cx+bw/2, cy+bh/2, fill='gray',
                                                               outline='gray', tag='button_rec')
                            self.frame.canvas.update()
                            break
        
                    time.sleep(0.4)
                    self.frame.canvas.delete('button_rec')
                    self.frame.canvas.update()
                    
            elif self.sti_type=='text':
                
                if self.N == 1:
                    self.frame.canvas.create_rectangle(self.w / 2 - 80, self.h / 2 - 18, self.w / 2 + 80, self.h / 2 + 18,
                                                       fill='gray', outline='gray', tag='button_rec')
                    self.frame.canvas.update()
                    time.sleep(0.4)
                    self.frame.canvas.delete('button_rec')
                    self.frame.canvas.update()
                
                
                else:
                    for item in range(self.N):
                        if i[1]['text']==text_list[item]:
                            cx, cy, bw, bh = button_geometry(item, self.N, self.w, self.h, self.dimension)
                            self.frame.canvas.create_rectangle(cx-bw/2, cy-bh/2, cx+bw/2, cy+bh/2,fill='gray',outline='gray',tag='button_rec')
                            self.frame.canvas.update()
                            break
                    time.sleep(0.4)
                    self.frame.canvas.delete('button_rec')
                    self.frame.canvas.update()
                        
if 'Count' in task_info_dic.values():
    class Reaction_count:
        """Readable Count display with separate header, trial and number rows."""
        root = tk.Tk()
        w = max(580, int(root.winfo_screenwidth() * 0.45))
        h = 260
        frame = myCanvas(root, w, h)
        frame.canvas.pack(fill='both', expand=True)
        root.title('Count')
        root.geometry('%dx%d+%d+%d' % (w, h, 0, int(root.winfo_screenheight() / 1.7)))
        frame.canvas.create_text(w/2, 105, text='Current count',
                                 font=('Arial', 17), tags='count_label')
        root.update_idletasks()
        root.update()

        def show(self, start_num, end_num):
            canvas = self.frame.canvas
            canvas.delete('count')
            canvas.create_text(self.w/2, 44,
                               text=f'Count from {start_num} to {end_num}',
                               font=('Arial', 19, 'bold'), anchor='center', tags='count')
            canvas.update_idletasks()

        def count_num(self, current):
            canvas = self.frame.canvas
            canvas.delete('current_count')
            canvas.create_text(self.w/2, 163, text=str(current),
                               font=('Arial', 34, 'bold'), fill='red',
                               anchor='center', tags='current_count')
            canvas.update()
            time.sleep(0.1)
            canvas.delete('current_count')

        def trial(self, trial):
            canvas = self.frame.canvas
            canvas.delete('trial')
            canvas.create_text(self.w/2, 78, text=f'Trial # {trial}',
                               font=('Arial', 14), anchor='center', tags='trial')
            canvas.update()

        def delete(self):
            self.frame.canvas.delete('trial')
            self.frame.canvas.delete('count')
            self.frame.canvas.delete('current_count')

if 'Cal_single_digit_num' in task_info_dic.values():
    class Reaction_calsingledig:
        root = tk.Tk()
        w=root.winfo_screenwidth()/2
        h=root.winfo_screenheight()/5
        frame=myCanvas(root,w,h)
        frame.canvas.pack(fill="both",expand=True)
        root.update_idletasks()
        root.title('Reaction')
        root.geometry('%dx%d+%d+%d'%(w,h,0,root.winfo_screenheight()/1.7))    
        
        from gui_basic_BE import operation

        if operation=='Add (+)':
            text='+'
        elif operation=='Subtract (-)':
            text='-'
        elif operation=='Multiplication (*)':
            text='*'
        else:
            text='/'
        frame.canvas.create_text(w/2,h/2,text=text,font=("Times New Roman",18,"bold"))
        root.update_idletasks()
        root.update()
            #frame.canvas.create_text(w/2,h/4,text='Current count: ',font=("Times New Roman",18))  
        
        def first_num(self,first_num):
            self.frame.canvas.delete('first_num')
            self.frame.canvas.create_text(self.w/2-20,self.h/2,text=str(first_num),font=("Times New Roman",18),fill='red',tag='first_num')
            self.frame.canvas.update()
        
        def second_num(self,second_num):
            self.frame.canvas.delete('second_num')
            self.frame.canvas.create_text(self.w/2+20,self.h/2,text=str(second_num),font=("Times New Roman",18),fill='blue',tag='second_num')
            self.frame.canvas.update()
            
        def result(self,i):
            self.frame.canvas.delete('result')
            self.frame.canvas.create_text(self.w/2+60,self.h/2,text=' = '+str(i),font=("Times New Roman",18),tag='result')
            self.frame.canvas.update()
            time.sleep(0.2)
            
        def delete(self):

            self.frame.canvas.delete('first_num')

            self.frame.canvas.delete('second_num')

            self.frame.canvas.delete('result')

if 'Look_at' in task_info_dic.values() or 'Look_for' in task_info_dic.values():
    class Reaction_general:
        root = tk.Tk()
        w=root.winfo_screenwidth()/2
        h=root.winfo_screenheight()/3
        frame=myCanvas(root,w,h)
        frame.canvas.pack(fill="both",expand=True)
        root.update_idletasks()
        root.title('Reaction')
        root.geometry('%dx%d+%d+%d'%(w,h,0,root.winfo_screenheight()/1.7))  
        # Normalized 0-100 visual-field coordinates. Items need not lie on a grid.
        rows, cols = 100, 100
        cell_width, cell_height = 1, 1
        _visual_margin = 42

        def _visual_point(self, row, column):
            # Legacy Look_at inputs use (row, column); x is the column.
            width = max(100, float(self.w) - 2 * self._visual_margin)
            height = max(100, float(self.h) - 2 * self._visual_margin)
            x = self._visual_margin + float(column) / 100.0 * width
            y = self._visual_margin + float(row) / 100.0 * height
            return x, y

        def judge_result(self,judge,result):
            # A new judgment replaces any prior judgment label.
            self.frame.canvas.delete('ji_text')
            if result=='T':
                if judge=='color':
                    self.frame.canvas.create_text(self.cell_width*self.rows+80,self.h/2,anchor='center',text='identical color',font=("Times New Roman",15,"bold"),tag='ji_text')
                elif judge=='text' :
                    self.frame.canvas.create_text(self.cell_width*self.rows+80,self.h/2,anchor='center',text='identical text',font=("Times New Roman",15,"bold"),tag='ji_text')
            elif result=='F':
                if judge=='color':
                    self.frame.canvas.create_text(self.cell_width*self.rows+80,self.h/2,anchor='center',text='different color',font=("Times New Roman",15,"bold"),tag='ji_text')
                elif judge=='text':
                    self.frame.canvas.create_text(self.cell_width*self.rows+80,self.h/2,anchor='center',text='different text',font=("Times New Roman",15,"bold"),tag='ji_text')
            self.frame.canvas.update()
            time.sleep(1)
            self.frame.canvas.delete('ji_rec')
            self.frame.canvas.delete('ji_text')
            self.frame.canvas.update()
            
        def look_at(self, standalone=False):
            """Initialize the Look At gaze display or the Look For search field."""
            self.frame.canvas.delete('visual_field')
            self.frame.canvas.delete('eye')
            self.draw_table(self.rows, self.cols, self.cell_width, self.cell_height)
            if standalone:
                from eye_movement_model import get_eye_position
                self.show_look_at(get_eye_position(), None)
            else:
                self.draw_circles(look_for_ls, self.cell_width, self.cell_height)
            self.root.update_idletasks()
            self.root.update()

        def show_look_at(self, fixation, target):
            """Display one blue fixation and one red target, never Look For items.

            Positions are (x, y) normalized to 0..100, matching the Eye Server.
            """
            self.frame.canvas.delete('look_at_gaze')
            self.frame.canvas.delete('eye')
            if fixation is not None:
                x, y = self._visual_point(fixation[1], fixation[0])
                self.frame.canvas.create_oval(x-8, y-8, x+8, y+8,
                    fill='#2563EB', outline='#1D4ED8', tags='look_at_gaze')
                self.frame.canvas.create_text(x, y+21, text='Current fixation',
                    fill='#1D4ED8', tags='look_at_gaze')
            if target is not None:
                x, y = self._visual_point(target[1], target[0])
                self.frame.canvas.create_oval(x-9, y-9, x+9, y+9,
                    fill='#DC2626', outline='#991B1B', tags='look_at_gaze')
                self.frame.canvas.create_text(x, y-22, text='Look At target',
                    fill='#991B1B', tags='look_at_gaze')
            self.root.update_idletasks()
            self.root.update()

        def show_eye(self, row, column, radius=15):
            x, y = self._visual_point(row, column)
            self.frame.canvas.delete('eye')
            self.frame.canvas.create_oval(x-radius, y-radius, x+radius, y+radius,
                                          outline='red', width=2, fill='', tag='eye')
            self.root.update_idletasks()
            self.root.update()

        def delete(self):
            self.frame.canvas.delete('eye')

        def draw_table(self, rows, cols, cell_width, cell_height):
            """Use a continuous visual field rather than a fixed nine-cell grid."""
            margin = self._visual_margin
            width, height = float(self.w), float(self.h)
            self.frame.canvas.create_rectangle(margin, margin, width-margin,
                                                height-margin, outline='#9CA3AF',
                                                width=2, tags='visual_field')
            for fraction in (0.25, 0.5, 0.75):
                x = margin + fraction * (width - 2*margin)
                y = margin + fraction * (height - 2*margin)
                self.frame.canvas.create_line(x, margin, x, height-margin,
                    fill='#E5E7EB', tags='visual_field')
                self.frame.canvas.create_line(margin, y, width-margin, y,
                    fill='#E5E7EB', tags='visual_field')
            self.frame.canvas.create_text(width/2, margin/2,
                text='Visual field (X: 0–100, Y: 0–100)',
                font=('Arial', 12), tags='visual_field')

        def draw_circles(self, items, cell_width, cell_height):
            """Render configured targets at their actual normalized coordinates."""
            for (row, col), label, color in items:
                x, y = self._visual_point(row, col)
                radius = 14
                self.frame.canvas.create_oval(x-radius, y-radius, x+radius, y+radius,
                                               fill=color, outline='#555555',
                                               tags='visual_field')
                self.frame.canvas.create_text(x, y, text=str(label),
                                               fill='black', font=('Arial', 11, 'bold'),
                                               tags='visual_field')


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from utility import max_val_click

class Reaction_click:
    
    def __init__(self, dimension):
        self.dimension = dimension
        
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand="yes")
        self.points = []  # List to store multiple points
        if self.dimension == 1:
            self.root.title("1D Visualization")
            self.fig, self.ax = plt.subplots(figsize=(12, 6))

            # Generate x values from 0 to max_click
            x_vals = list(range(0, max_val_click + 1))
            y_vals = [0 for _ in x_vals]

            self.ax.set_yticks([])  # Remove y-axis ticks for 1D
            self.ax.set_xticks(range(0, max_val_click + 1, 10))  # Set x ticks from 0 to max_click
            self.ax.set_xlim(0, max_val_click)  # Set x-axis limits from 0 to max_click
            
            # Add trial number as a label in the upper-right corner of the plot
            self.trial_label = self.ax.text(0.95, 0.95,'Trial: ', \
                                            transform=self.ax.transAxes, fontsize=12,\
                                                verticalalignment='top', horizontalalignment='right')
            #Add labels for the color of initial position and click position
            self.blue_label = self.ax.text(0.05, 0.05,'Blue: Initial Position', \
                                            transform=self.ax.transAxes, fontsize=12,color='blue',\
                                                verticalalignment='top', horizontalalignment='left')
            self.red_label = self.ax.text(0.05, 0.1,'Red: Click Position', \
                                            transform=self.ax.transAxes, fontsize=12,color='red',\
                                                verticalalignment='top', horizontalalignment='left')
        
        elif self.dimension == 2:
            self.root.title("2D Visualization")
            self.fig, self.ax = plt.subplots(figsize=(10, 10))
            # Update position for 2D scatter
            # Generate x values from 0 to max_click
            x_vals = list(range(0, max_val_click + 1))
            y_vals = list(range(0, max_val_click + 1))
            self.ax.set_xticks(range(0, max_val_click + 1, 10))  # Set x ticks from 0 to max_click
            self.ax.set_xlim(0, max_val_click)  # Set x-axis limits from 0 to max_click
            self.ax.set_yticks(range(0, max_val_click + 1, 10))  # Set x ticks from 0 to max_click
            self.ax.set_ylim(0, max_val_click)  # Set x-axis limits from 0 to max_click
        
            # Add trial number as a label in the upper-right corner of the plot
            self.trial_label = self.ax.text(0.95, 0.95,'Trial: ', \
                                            transform=self.ax.transAxes, fontsize=12,\
                                                verticalalignment='top', horizontalalignment='right')
            #Add labels for the color of initial position and click position
            self.blue_label = self.ax.text(0.05, 0.05,'Blue: Initial Position', \
                                            transform=self.ax.transAxes, fontsize=12,color='blue',\
                                                verticalalignment='top', horizontalalignment='left')
            self.red_label = self.ax.text(0.05, 0.1,'Red: Click Position', \
                                            transform=self.ax.transAxes, fontsize=12,color='red',\
                                                verticalalignment='top', horizontalalignment='left')
        
        elif self.dimension == 3:
            self.root.title("3D Visualization")
            self.fig = plt.figure(figsize=(10, 10))
            self.ax = self.fig.add_subplot(111, projection='3d')
            x_vals = list(range(0, max_val_click + 1))
            y_vals = list(range(0, max_val_click + 1))
            z_vals = list(range(0, max_val_click + 1))
            self.ax.set_xticks(range(0, max_val_click + 1, 10))  # Set x ticks from 0 to max_click
            self.ax.set_xlim(0, max_val_click)  # Set x-axis limits from 0 to max_click
            self.ax.set_yticks(range(0, max_val_click + 1, 10))  # Set y ticks from 0 to max_click
            self.ax.set_ylim(0, max_val_click)  # Set y-axis limits from 0 to max_click
            self.ax.set_zticks(range(0, max_val_click + 1, 10))  # Set z ticks from 0 to max_click
            self.ax.set_zlim(0, max_val_click)  # Set z-axis limits from 0 to max_click

            # Add trial number as a label in the upper-right corner of the plot
            self.trial_label = self.ax.text2D(0.95, 0.95, 'Trial: ', \
                                            transform=self.ax.transAxes, fontsize=12,\
                                                verticalalignment='top', horizontalalignment='right')
            
            #Add labels for the color of initial position and click position
            self.blue_label = self.ax.text2D(0.05, 0.05,'Blue: Initial Position', \
                                            transform=self.ax.transAxes, fontsize=12,color = 'blue',\
                                                verticalalignment='top', horizontalalignment='left')
            self.red_label = self.ax.text2D(0.05, 0.1,'Red: Click Position', \
                                            transform=self.ax.transAxes, fontsize=12,color = 'red',\
                                                verticalalignment='top', horizontalalignment='left')
        # Embed the matplotlib plot into the Tkinter frame
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
       

    def create_initial_point(self,coords,trial_number):
        
        self.target_x = coords[0]
        self.cursor_x = coords[1]
        self.target_y = coords[2]
        self.cursor_y = coords[3]
        self.target_z = coords[4]
        self.cursor_z = coords[5]
        #update trial label
        self.trial_label.set_text(f'Trial: {trial_number}')
        # Plot the cursor point in 1D
        # Create the initial point and store it in the points list
        if self.dimension == 1:
            point = self.ax.scatter(self.cursor_x, 0, c='blue', s=100)
        elif self.dimension == 2:
            point = self.ax.scatter(self.cursor_x, self.cursor_y, c='blue', s=100)
        elif self.dimension == 3:
            point = self.ax.scatter(self.cursor_x, self.cursor_y,self.cursor_z, c='blue', s=100)
        self.points.append(point)  # Store point in the list
        self.canvas.draw()  # Redraw the figure
        self.root.update()
        time.sleep(0.3)

  
    def move_point(self):
        """Move the point to a new position based on the given coordinates."""
       
        if self.dimension == 1:
            # Update cursor position for 1D
            # Re-plot the point at the new position
            # Create the initial point and store it in the points list
            target_point = self.ax.scatter(self.target_x, 0, c='red', s=100)
        elif self.dimension == 2:
            target_point = self.ax.scatter(self.target_x, self.target_y, c='red', s=100)
        elif self.dimension == 3:
            target_point = self.ax.scatter(self.target_x, self.target_y,self.target_z, c='red', s=100)
        
        self.points.append(target_point)  # Store point in the list
        #self.ax.set_xlim(0, max_val_click)  # Optional: adjust limits if needed
        self.canvas.draw()  # Redraw the figure
        self.root.update()
        time.sleep(0.3)
        
        
    def delete_point(self):
        for point in self.points:
            point.remove()  # Remove each point from the canvas
        self.points.clear()  # Clear the list of points
        self.canvas.draw()
        self.root.update()
        time.sleep(0.3)
