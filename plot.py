# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 09:00:45 2024

@author: wyuanc
"""

"""Plotting utilities for timeline, tick, and RMSE output produced by the simulation."""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from gui_general import Tasklist_dic,task_info_dic
from main_process import rt_mean_dic,rt_var_dic

class Plot:
        
   
    def __init__(self):    
        self.root = tk.Tk()
        self.root.title('Plot')
        self.root.geometry('1400x400')
        self.root.config(bg='#fff')
        
        length = len(Tasklist_dic)

         
        
        f = plt.Figure(figsize=(2,1), dpi=72)
        f
        self.ave_plot = f.add_subplot(211)
        self.ave_plot.plot()
        self.sd_plot=f.add_subplot(212)
        self.sd_plot.plot()

        
        self.data_plot = FigureCanvasTkAgg(f, master=self.root)
        self.data_plot.get_tk_widget().config(height=400)
        self.data_plot.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.root, width=1300, height=350, bg="white")
        self.canvas.update()

     
    def tick(self):
        
        
        
        self.ave_plot.cla()
        self.ave_plot.set_xlabel("Number of Stimuli")
        self.ave_plot.set_ylabel("Mean of Sojourn Time")
        
        
        for (key, value) in rt_mean_dic.items():
            if value!=[]:
                self.ave_plot.step(
                    [index for (index, waits) in enumerate(value,start=1)],
                    [waits for (index, waits) in enumerate(value,start=1)],
                     label=f'Task {key}',marker='.'
                )
    
        if self.ave_plot.get_legend_handles_labels()[0]:
            self.ave_plot.legend()
        
        
        self.sd_plot.cla()
        self.sd_plot.set_xlabel("Number of Stimuli")
        self.sd_plot.set_ylabel("Standard Deviation of Sojourn Time")
        
        
        for (key, value) in rt_var_dic.items():      
            if value!=[]:
                self.sd_plot.step(
                    [index for (index, waits) in enumerate(value,start=1)],
                    [waits for (index, waits) in enumerate(value,start=1)],
                     label = f'Task {key}',marker='.'
                )
        
        if self.sd_plot.get_legend_handles_labels()[0]:
            self.sd_plot.legend()
     
        self.data_plot.draw()
        self.canvas.update()
        
    def RMSE (self):
        
        from compound_BE import rmse_dic,rmse_var_dic

        self.ave_plot.cla()
        self.ave_plot.set_xlabel("Response Number")
        self.ave_plot.set_ylabel("RMSE")
        
        self.ave_plot.step(
            [t for (t, waits) in rmse_dic.items()],
            [waits for (t, waits) in rmse_dic.items()],
            'b.-'
        )
        
        self.sd_plot.cla()
        self.sd_plot.set_xlabel("Response Number")
        self.sd_plot.set_ylabel("Standard Deviation of Squre Error")
        self.sd_plot.step(
            [t for (t, waits) in rmse_var_dic.items()],
            [waits for (t, waits) in rmse_var_dic.items()],
            'b.-'
        )
        
     
        self.data_plot.draw()
        self.canvas.update()


