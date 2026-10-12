# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 15:21:26 2024

@author: wyuanc
"""
"""Display primitives and animation support for compound behavior-element tasks."""

import time
import tkinter as tk
from tkinter import messagebox
from gui_general import task_info_dic
from qn_mhp_layout import myCanvas
from qn_mhp_layout import myCanvas_scroll
from utility import color_changer, look_for_ls,n_look_for_ls,color_list,ppi
from utility import track1D_amp_dic,track1D_freq_dic,track2D_amp_dic,track2D_freq_dic,static2D_amp_dic,direction_static2D,dynamic1D_amp_dic,dynamic2D_amp_dic
from utility import tracing2D_curve, tracking2D_curve
from utility import pixels_to_mm
import pyautogui as ag
import random
import math
import numpy as np
from numpy import arange as npar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


if 'Tracking_1D' in task_info_dic.values():
    from gui_compound_BE import track1D_b_x_target, track1D_b_x_cursor,track1D_b_amp,track1D_b_freq
    class Reaction_tracking1d_b:
        def __init__(self,**kwargs):
            self.target_x = track1D_b_x_target  # Initial position of the red target point
            self.target_y = 0  # Y-coordinate of the target point
            self.cursor_x = track1D_b_x_cursor  # Initial position of the black cursor point
            self.current_x = self.cursor_x
            self.cursor_y = 0  # Y-coordinate of the cursor point
            self.moving_forward = True  # Initialize direction to forward for the cursor
            self.animation_running = False  # To control animation start/stop
            self.point = None
            self.target_point = None  # The red target point
            self.canvas = None
            self.ax = None
            self.mm_label = None
            self.end_x = 100
            self.reach = 1
            self.marker_size = 6 
            self.env = kwargs['environment']
    
        def plot_curve(self):
    
            # Ensure animation starts
            self.animation_running = True
    
            user_x = self.cursor_x
    
            # Create the main window
            self.root = tk.Tk()
    
            # Create a new window for the plot
            plot_window = self.root
            plot_window.title('Line Plot')
    
            # Create a wider matplotlib figure for plotting in the new window
            fig, self.ax = plt.subplots(figsize=(30, 4))  # Increase the width for a wider window
            self.canvas = FigureCanvasTkAgg(fig, master=plot_window)
            self.canvas.get_tk_widget().pack()
            dpi = fig.get_dpi()
            
            
            # Add a label to display pixel coordinates
            self.mm_label = tk.Label(plot_window, text="Coordinates in mm: (x, y)")
            self.mm_label.pack(pady=5)
    
            # Generate x values for plotting (from 0 to 100)
            x_vals = np.linspace(0.01, 100, 1000)
    
            # Adjust the curve for larger distance between waves
            y_vals = 0 * x_vals
            user_y = 0
            self.start_y = self.end_y = 0
    
            # Plot the curve
            self.ax.plot(x_vals, y_vals, label='line')
    
            # Plot the initial cursor point
            self.point, = self.ax.plot(user_x, user_y, 'bo',markersize = self.marker_size, label="Blue Cursor Point")  # blue point for cursor
            # Plot the initial target point
            self.target_point, = self.ax.plot(self.target_x, self.target_y, 'ro', markersize = self.marker_size,label="Red Target Point")  # red point for target
    
            # Set labels and title
            self.ax.set_title("Line")
            self.ax.set_xlabel("X Axis (0 to 100)")
            self.ax.set_ylabel("Y Axis")
    
            # Set intermediate ticks for the x-axis, with the range from 0 to 100
            self.ax.set_xticks(np.arange(0, 101, 5))  # Adding ticks every 50 units for a wider x-axis
            self.ax.set_xlim(0, 100)  # Set the x-axis limit from 0 to 100
    
            self.ax.grid(True)  # Optional: adds a grid for better visibility of the scale
    
            # Update the plot
            self.ax.legend()
            
            #diameter of the point in pixel
            self.diameter_pixel= (self.marker_size * dpi) / 72 
            #diameter of the point in mm
            self.diameter_mm = pixels_to_mm(self.diameter_pixel)
    
            # Update current y value
            self.current_y = user_y
            
            # Convert the cursor's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_cursor = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords_cursor[0]),pixels_to_mm(self.pixel_coords_cursor[1]))
                
            # Convert the target's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_target = self.ax.transData.transform((self.target_x, self.target_y))
            self.mm_coords_target = (pixels_to_mm(self.pixel_coords_target[0]),pixels_to_mm(self.pixel_coords_target[1]))
            
            # Start the SimPy process for target movement
            self.env.process(self.move_target())
    
        def move_point_to(self, location_x, location_y):
            self.current_x = location_x 
            self.current_y = location_y 
    
            # Update the cursor's position on the plot
            self.point.set_data([self.current_x], [self.current_y])
            self.canvas.draw()
            
            self.cursor_x = self.current_x
            self.cursor_y = self.current_y
            
            # Convert the cursor's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_cursor = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords_cursor[0]),pixels_to_mm(self.pixel_coords_cursor[1]))
            #print(f"Actual coordinates of the cursor in mm: {self.mm_coords_cursor}")
            
            # Update the label with the actual pixel coordinates
            self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_cursor}")
    
            # Refresh the GUI
            self.root.update()
    
        def move_target(self):
            """SimPy process to move the red target point in a random direction with a certain frequency."""
            while True:
                step_size = track1D_amp_dic[track1D_b_amp]
    
                # Move the target left or right        
                if self.moving_forward:
                    new_x = self.target_x + step_size
                else:
                    new_x = self.target_x - step_size
                # Keep the target within bounds (0 to 100)
                # move to other direction if <0 of >100
                if new_x < 0:
                    self.moving_forward = True
                    self.target_x = 0
                elif new_x > 100:
                    self.moving_forward = False
                    self.target_x = 100
                else:
                    self.target_x = new_x
                
                # Update the target point's position on the plot
                self.target_point.set_data([self.target_x], [self.target_y])
                self.canvas.draw()
                
                # Convert the target's (x, y) in data coordinates to pixel coordinates
                self.pixel_coords_target = self.ax.transData.transform((self.target_x, self.target_y))
                self.mm_coords_target = (pixels_to_mm(self.pixel_coords_target[0]),pixels_to_mm(self.pixel_coords_target[1]))
                #print(f"Actual coordinates of the target in mm: {self.mm_coords_target}")
        
                # Update the label with the actual pixel coordinates
                self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_target}")
                               
                # Simulate a delay for the next movement (frequency)
                yield self.env.timeout(track1D_freq_dic[track1D_b_freq])  # Wait for some time (depend on frequency) before moving again

            
if 'Tracking_1D_1W' in task_info_dic.values():
    # Import from gui_compound_BE
    from gui_compound_BE import track1D_1w_x_cursor,track1D_1w_x_target,track1D_1w_amp,track1D_1w_freq
    
    class Reaction_tracking1d_1w:     
        def __init__(self,**kwargs):
            self.cursor_x = track1D_1w_x_cursor # Initialize starting x location of cursor
            self.target_x = track1D_1w_x_target
            self.current_x = self.cursor_x
            self.cursor_y = 0
            self.target_y = 0
            self.moving_forward = True  # Direction control
            self.animation_running = False  # Controls the animation state
            self.point = None
            self.canvas = None
            self.ax = None
            self.pixel_label = None
            self.curve_type = "line"
            
            # Initialize x and y limits
            self.max_x = 10**5  # Full range for x values
            self.x_range = 100  # Visible range for x-axis
            self.x_min = 0  # Start of the visible window
            self.x_max = self.x_min + self.x_range  # End of the visible window
            
            # Initialize the first y-value and limits
            self.current_y = 0  # Initial y-value based on curve
            
            self.new_screen = 1
            self.marker_size = 6 
            self.env = kwargs['environment']
    
        def plot_curve(self):
            """Plot the curve and initialize moving point."""
            # Ensure animation starts
            self.animation_running = True  
            user_x = self.current_x
            
            # Create the main window
            self.root = tk.Tk()
            plot_window = self.root
            plot_window.title("Line Plot")
        
            # Create a wider matplotlib figure for plotting
            fig, self.ax = plt.subplots(figsize=(10, 4))  # A wider window with aspect ratio suited to scrolling
            self.canvas = FigureCanvasTkAgg(fig, master=plot_window)
            self.canvas.get_tk_widget().pack()
            dpi = fig.get_dpi()
            # Add a label to display pixel coordinates
            self.mm_label = tk.Label(plot_window, text="Coordinates in mm: (x, y)")
            self.mm_label.pack(pady=5)
        
            # Generate x values for the entire curve (from 0 to 10^5)
            self.x_vals = np.linspace(0.01, self.max_x, 100000)  # Avoid x=0 for ln(x)
        
            # Get y-values using the external utility function
            self.y_vals = 0*self.x_vals
            user_y = 0
            self.y_end = 0
    
            # Plot the initial portion of the curve from 0 to 100 (visible window)
            self.line, = self.ax.plot(self.x_vals, self.y_vals, label=self.curve_type)
        
            # Plot the initial cursor point
            self.point, = self.ax.plot(user_x, user_y, 'bo',markersize = self.marker_size, label="Blue Cursor Point")  # blue point for cursor
            # Plot the initial target point
            self.target_point, = self.ax.plot(self.target_x, self.target_y, 'ro', markersize = self.marker_size,label="Red Target Point")  # red point for target
        
            # Set labels and title
            self.ax.set_title(f"Curve: {self.curve_type}")
            self.ax.set_xlabel(f"X Axis ({self.x_min} to {self.x_max})")
            self.ax.set_ylabel("Y Axis")
        
            # Set the initial limits for the x-axis and y-axis
            self.ax.set_xlim(self.x_min, self.x_max)
           
            # Add grid for better visibility
            self.ax.grid(True)
        
            # Update the plot with the legend
            self.ax.legend()
            
            #diameter of the point in pixel
            self.diameter_pixel= (self.marker_size * dpi) / 72 
            #diameter of the point in mm
            self.diameter_mm = pixels_to_mm(self.diameter_pixel)
                        
            # Convert the cursor's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_cursor = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords_cursor[0]),pixels_to_mm(self.pixel_coords_cursor[1]))
                
            # Convert the target's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_target = self.ax.transData.transform((self.target_x, self.target_y))
            self.mm_coords_target = (pixels_to_mm(self.pixel_coords_target[0]),pixels_to_mm(self.pixel_coords_target[1]))
            
            # Start the SimPy process for target movement
            self.env.process(self.move_target())
            
        def adjust_x_range(self):
            """Adjust the x-axis range to ensure both cursor and target are visible."""
            min_x = min(self.current_x, self.target_x)
            max_x = max(self.current_x, self.target_x)
    
            # Add some padding to the x-axis for better visibility
            padding = 5
    
            # Check if either point goes beyond the current x-axis limits
            if min_x - padding < self.x_min or max_x + padding > self.x_max:
                # Adjust the x-axis limits to fit both points
                self.x_min = min_x - padding
                self.x_max = max_x + padding
                self.ax.set_xlim(self.x_min, self.x_max)
                self.ax.set_xlabel(f"X Axis ({self.x_min} to {self.x_max})")
                self.canvas.draw()    
        
        
        def move_point_to(self, location_x, location_y):
                self.new_screen = 0
                """Move the point along the curve and ensure smooth movement."""
                # Move the x value forward
                self.current_x = location_x
            
                # Check if the x value has reached or exceeded the visible window's end
                if self.current_x >= self.x_max:
                    # Scroll the visible window by moving the x-axis range forward
                    self.x_min += self.x_range
                    self.x_max += self.x_range                   
                    self.new_screen = 1
          
                # Ensure we don't go beyond the maximum x-value limit
                if self.current_x >= self.max_x:
                    self.current_x = self.max_x
            
                # Adjust the x-axis range to ensure both the cursor and target are visible
                self.adjust_x_range()
               
                # Update the point's position on the plot
                self.point.set_data([self.current_x], [self.current_y])
                self.canvas.draw()  # Refresh the plot
            
                self.cursor_x = self.current_x
                
                # Convert the point's (x, y) in data coordinates to pixel coordinates
                self.pixel_coords = self.ax.transData.transform((self.current_x, self.current_y))
                self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords[0]),pixels_to_mm(self.pixel_coords[1]))
                #print(f"Actual pixel coordinates of the point: {pixel_coords}")
            
                # Update the label with the pixel coordinates
                self.mm_label.config(text=f"Pixel Coordinates: {self.mm_coords_cursor}")
                
                # Refresh the GUI to show changes
                self.root.update()

        def move_target(self):
            """SimPy process to move the red target point in a random direction with a certain frequency."""
            while True:
                step_size = track1D_amp_dic[track1D_1w_amp]
    
                # Move the target left or right
                self.target_x += step_size
                
                # Adjust the x-axis range to ensure both the cursor and target are visible
                self.adjust_x_range()
                
                # Update the target point's position on the plot
                self.target_point.set_data([self.target_x], [self.target_y])
                self.canvas.draw()
                
                # Convert the target's (x, y) in data coordinates to pixel coordinates
                self.pixel_coords_target = self.ax.transData.transform((self.target_x, self.target_y))
                self.mm_coords_target = (pixels_to_mm(self.pixel_coords_target[0]),pixels_to_mm(self.pixel_coords_target[1]))
                #print(f"Actual coordinates of the target in mm: {self.mm_coords_target}")
        
                # Update the label with the actual pixel coordinates
                self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_target}")
                               
                # Simulate a delay for the next movement (frequency)
                yield self.env.timeout(track1D_freq_dic[track1D_1w_freq])  # Wait for some time (depend on frequency) before moving again


if 'Tracking_1D_Random' in task_info_dic.values():
    from gui_compound_BE import track1D_r_x_target, track1D_r_x_cursor,track1D_r_amp,track1D_r_freq
    class Reaction_tracking1d_r:
        def __init__(self,**kwargs):
            self.target_x = track1D_r_x_target  # Initial position of the red target point
            self.target_y = 0  # Y-coordinate of the target point
            self.cursor_x = track1D_r_x_cursor  # Initial position of the black cursor point
            self.current_x = self.cursor_x
            self.cursor_y = 0  # Y-coordinate of the cursor point
            self.moving_forward = True  # Initialize direction to forward for the cursor
            self.animation_running = False  # To control animation start/stop
            self.point = None
            self.target_point = None  # The red target point
            self.canvas = None
            self.ax = None
            self.mm_label = None
            self.end_x = 100
            self.reach = 1
            self.marker_size = 6 
            self.env = kwargs['environment']
    
        def plot_curve(self):
    
            # Ensure animation starts
            self.animation_running = True
    
            user_x = self.cursor_x
    
            # Create the main window
            self.root = tk.Tk()
    
            # Create a new window for the plot
            plot_window = self.root
            plot_window.title('Line Plot')
    
            # Create a wider matplotlib figure for plotting in the new window
            fig, self.ax = plt.subplots(figsize=(30, 4))  # Increase the width for a wider window
            self.canvas = FigureCanvasTkAgg(fig, master=plot_window)
            self.canvas.get_tk_widget().pack()
            dpi = fig.get_dpi()
            
            # Add a label to display pixel coordinates
            self.mm_label = tk.Label(plot_window, text="Coordinates in mm: (x, y)")
            self.mm_label.pack(pady=5)
    
            # Generate x values for plotting (from 0 to 100)
            x_vals = np.linspace(0.01, 100, 1000)
    
            # Adjust the curve for larger distance between waves
            y_vals = 0 * x_vals
            user_y = 0
            self.start_y = self.end_y = 0
    
            # Plot the curve
            self.ax.plot(x_vals, y_vals, label='line')
    
            # Plot the initial cursor point
            self.point, = self.ax.plot(user_x, user_y, 'bo',markersize = self.marker_size, label="Blue Cursor Point")  # blue point for cursor
            # Plot the initial target point
            self.target_point, = self.ax.plot(self.target_x, self.target_y, 'ro', markersize = self.marker_size,label="Red Target Point")  # red point for target
    
            # Set labels and title
            self.ax.set_title("Line")
            self.ax.set_xlabel("X Axis (0 to 100)")
            self.ax.set_ylabel("Y Axis")
    
            # Set intermediate ticks for the x-axis, with the range from 0 to 100
            self.ax.set_xticks(np.arange(0, 101, 5))  # Adding ticks every 50 units for a wider x-axis
            self.ax.set_xlim(0, 100)  # Set the x-axis limit from 0 to 100
    
            self.ax.grid(True)  # Optional: adds a grid for better visibility of the scale
    
            # Update the plot
            self.ax.legend()
            
            #diameter of the point in pixel
            self.diameter_pixel= (self.marker_size * dpi) / 72 
            #diameter of the point in mm
            self.diameter_mm = pixels_to_mm(self.diameter_pixel)
    
            # Update current y value
            self.current_y = user_y
            
            # Convert the cursor's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_cursor = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords_cursor[0]),pixels_to_mm(self.pixel_coords_cursor[1]))
                
            # Convert the target's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_target = self.ax.transData.transform((self.target_x, self.target_y))
            self.mm_coords_target = (pixels_to_mm(self.pixel_coords_target[0]),pixels_to_mm(self.pixel_coords_target[1]))
            
            # Start the SimPy process for target movement
            self.env.process(self.move_target())
    
        def move_point_to(self, location_x, location_y):
            self.current_x = location_x 
            self.current_y = location_y 
    
            # Update the cursor's position on the plot
            self.point.set_data([self.current_x], [self.current_y])
            self.canvas.draw()
            
            self.cursor_x = self.current_x
            self.cursor_y = self.current_y
            
            # Convert the cursor's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_cursor = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords_cursor[0]),pixels_to_mm(self.pixel_coords_cursor[1]))
            #print(f"Actual coordinates of the cursor in mm: {self.mm_coords_cursor}")
            
            # Update the label with the actual pixel coordinates
            self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_cursor}")
    
            # Refresh the GUI
            self.root.update()
    
        def move_target(self):
            """SimPy process to move the red target point in a random direction with a certain frequency."""
            while True:
                # 50% chance to move left or right
                direction = random.choice([-1, 1])
                step_size = track1D_amp_dic[track1D_r_amp]
    
                # Move the target left or right
                new_x = self.target_x + direction*step_size
 
                # Keep the target within bounds (0 to 100)
                # move to other direction if <0 of >100
                if new_x < 0:
                    self.target_x +=  step_size
                elif new_x > 100:
                    self.target_x -= step_size
                else:
                    self.target_x = new_x
                # Update the target point's position on the plot
                self.target_point.set_data([self.target_x], [self.target_y])
                self.canvas.draw()
                
                # Convert the target's (x, y) in data coordinates to pixel coordinates
                self.pixel_coords_target = self.ax.transData.transform((self.target_x, self.target_y))
                self.mm_coords_target = (pixels_to_mm(self.pixel_coords_target[0]),pixels_to_mm(self.pixel_coords_target[1]))
                #print(f"Actual coordinates of the target in mm: {self.mm_coords_target}")
        
                # Update the label with the actual pixel coordinates
                self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_target}")
                               
                # Simulate a delay for the next movement (frequency)
                yield self.env.timeout(track1D_freq_dic[track1D_r_freq])  # Wait for some time (depend on frequency) before moving again


if 'Tracking_2D' in task_info_dic.values():
    from gui_compound_BE import track2D_b_x_cursor,track2D_b_x_target,track2D_b_shape,track2D_b_amp,track2D_b_freq
    class Reaction_tracking2d_b:        
        def __init__(self,**kwargs):         
            self.cursor_x = track2D_b_x_cursor
            self.current_x = self.cursor_x
            self.target_x = track2D_b_x_target
            self.moving_forward = True  # Initialize direction to forward
            self.animation_running = False  # To control animation start/stop
            self.point = None
            self.canvas = None
            self.ax = None
            self.pixel_label = None
            self.curve_type = track2D_b_shape
            self.end_x = 100
            self.reach = 1
            self.marker_size = 6 
            self.env = kwargs['environment']

        def plot_curve(self):

            # Ensure animation starts
            self.animation_running = True  
            
            user_x = self.current_x
            
            # Create the main window
            self.root = tk.Tk()
            
            # Create a new window for the plot
            plot_window = self.root
            plot_window.title(f"Curve Plot: {self.curve_type}")
        
            # Create a wider matplotlib figure for plotting in the new window
            fig, self.ax = plt.subplots(figsize=(30, 4))  # Increase the width for a wider window
            self.canvas = FigureCanvasTkAgg(fig, master=plot_window)
            self.canvas.get_tk_widget().pack()
            dpi = fig.get_dpi()
        
            # Add a label to display pixel coordinates
            self.mm_label = tk.Label(plot_window, text="Pixel Coordinates: (x, y)")
            self.mm_label.pack(pady=5)
        
            # Generate x values for plotting (from 0 to 100)
            x_vals = np.linspace(0.01, 100, 1000)
        
            # Adjust the curve for larger distance between waves
            y_vals = tracking2D_curve(self.curve_type, x_vals)
            user_y = tracking2D_curve(self.curve_type, user_x)
            self.start_y = tracking2D_curve(self.curve_type, 0)
            self.end_y = tracking2D_curve(self.curve_type, self.end_x)
            self.target_y = tracking2D_curve(self.curve_type, self.target_x)

            #get the max and min values of y
            self.max_y = np.max(y_vals)
            self.min_y = np.min(y_vals)
            # Plot the curve
            self.ax.plot(x_vals, y_vals, label=self.curve_type)
        
            # Plot the initial cursor point
            self.point, = self.ax.plot(user_x, user_y, 'bo',markersize = self.marker_size, label="Blue Cursor Point")  # blue point for cursor
            # Plot the initial target point
            self.target_point, = self.ax.plot(self.target_x, self.target_y, 'ro', markersize = self.marker_size,label="Red Target Point")  # red point for target
        
            # Set labels and title
            self.ax.set_title(f"Curve: {self.curve_type}")
            self.ax.set_xlabel("X Axis (0 to 100)")
            self.ax.set_ylabel("Y Axis")
        
            # Set intermediate ticks for the x-axis, with the range from 0 to 100
            self.ax.set_xticks(np.arange(0, 101, 5))  # Adding ticks every 50 units for a wider x-axis
            self.ax.set_xlim(0, 100)  # Set the x-axis limit from 0 to 100
        
            self.ax.grid(True)  # Optional: adds a grid for better visibility of the scale
        
            # Update the plot
            self.ax.legend()
            
            #diameter of the point in pixel
            self.diameter_pixel= (self.marker_size * dpi) / 72 
            #diameter of the point in mm
            self.diameter_mm = pixels_to_mm(self.diameter_pixel)
     
            #Update current y value
            self.current_y = user_y
            self.cursor_y = self.current_y
            
            # Convert the cursor's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_cursor = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords_cursor[0]),pixels_to_mm(self.pixel_coords_cursor[1]))
                
            # Convert the target's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_target = self.ax.transData.transform((self.target_x, self.target_y))
            self.mm_coords_target = (pixels_to_mm(self.pixel_coords_target[0]),pixels_to_mm(self.pixel_coords_target[1]))
            
            # Start the SimPy process for target movement
            self.env.process(self.move_target())

        # Function to move the point along the curve once
        def move_point_to(self, location_x, location_y):
            self.current_x = location_x
            self.current_y = location_y 
            
    
            # Update the cursor's position on the plot
            self.point.set_data([self.current_x], [self.current_y])
            self.canvas.draw()
            
            self.cursor_x = self.current_x
            self.cursor_y = self.current_y
            
            # Convert the cursor's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_cursor = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords_cursor[0]),pixels_to_mm(self.pixel_coords_cursor[1]))
            #print(f"Actual coordinates of the cursor in mm: {self.mm_coords_cursor}")
    
            # Update the label with the actual pixel coordinates
            self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_cursor}")
    
            # Refresh the GUI
            self.root.update()
            
        def move_target(self):
            """SimPy process to move the red target point in a random direction with a certain frequency."""
            while True:
                
                step_size = track2D_amp_dic[track2D_b_amp]  # Use 2D amplitude for both x and y
        
                # Move the target in both x and y directions
                if self.moving_forward:
                    new_x = self.target_x + step_size
                else:
                    new_x = self.target_x - step_size
                # Move right if it attempts to go below 0
                if new_x < 0:
                    self.moving_forward = True
                    self.target_x = 0
                elif new_x > 100:
                    self.moving_forward = False
                    self.target_x = 100 
                else:
                    self.target_x = new_x
                
                self.target_y = tracking2D_curve(self.curve_type, self.target_x)
        
                # Update the target point's position on the plot
                self.target_point.set_data([self.target_x], [self.target_y])
                self.canvas.draw()
        
                # Convert the target's (x, y) in data coordinates to pixel coordinates
                self.pixel_coords_target = self.ax.transData.transform((self.target_x, self.target_y))
                self.mm_coords_target = (pixels_to_mm(self.pixel_coords_target[0]), pixels_to_mm(self.pixel_coords_target[1]))
                
                # Update the label with the actual pixel coordinates
                self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_target}")
        
                # Simulate a delay for the next movement (frequency)
                yield self.env.timeout(track2D_freq_dic[track2D_b_freq])  # Use 2D frequency


if 'Tracking_2D_Random' in task_info_dic.values():
    

    from gui_compound_BE import track2D_r_x_target, track2D_r_y_target,track2D_r_x_cursor, track2D_r_y_cursor, track2D_r_amp,track2D_r_freq
    class Reaction_tracking2d_r:
        def __init__(self,**kwargs):
            self.target_x = track2D_r_x_target  # Initial position of the red target point
            self.target_y = track2D_r_y_target  # Y-coordinate of the target point
            self.cursor_x = track2D_r_x_cursor  # Initial position of the black cursor point
            self.current_x = self.cursor_x
            self.cursor_y = track2D_r_y_cursor  # Y-coordinate of the cursor point
            self.moving_forward = True  # Initialize direction to forward for the cursor
            self.animation_running = False  # To control animation start/stop
            self.point = None
            self.target_point = None  # The red target point
            self.canvas = None
            self.ax = None
            self.mm_label = None
            self.end_x = 100
            self.reach = 1
            self.marker_size = 6 
            self.env = kwargs['environment']
    
        def plot_curve(self):
    
            # Ensure animation starts
            self.animation_running = True
    
            user_x = self.cursor_x
    
            # Create the main window
            self.root = tk.Tk()
    
            # Create a new window for the plot
            plot_window = self.root
            plot_window.title('Plot')
    
            # Create a wider matplotlib figure for plotting in the new window
            fig, self.ax = plt.subplots(figsize=(10, 10))  # Increase the width for a wider window
            self.canvas = FigureCanvasTkAgg(fig, master=plot_window)
            self.canvas.get_tk_widget().pack()
            dpi = fig.get_dpi()
            
            
            # Add a label to display pixel coordinates
            self.mm_label = tk.Label(plot_window, text="Coordinates in mm: (x, y)")
            self.mm_label.pack(pady=5)
    
            # Generate x values for plotting (from 0 to 100)
            x_vals = np.linspace(0.01, 100, 1000)
    

            user_y = self.cursor_y
            self.start_y = 0
            self.end_y = 100
    
            # Plot the initial cursor point
            self.point, = self.ax.plot(user_x, user_y, 'bo',markersize = self.marker_size, label="Blue Cursor Point")  # blue point for cursor
            # Plot the initial target point
            self.target_point, = self.ax.plot(self.target_x, self.target_y, 'ro', markersize = self.marker_size,label="Red Target Point")  # red point for target
    
            # Set labels and title
            self.ax.set_title("")
            self.ax.set_xlabel("X Axis (0 to 100)")
            self.ax.set_ylabel("Y Axis")
    
            self.ax.set_xlim(0, 100)  # Set the x-axis limit from 0 to 100
            self.ax.set_ylim(0, 100)  # Set the x-axis limit from 0 to 100
    
            self.ax.grid(True)  # Optional: adds a grid for better visibility of the scale
    
            # Update the plot
            self.ax.legend()
            
            #diameter of the point in pixel
            self.diameter_pixel= (self.marker_size * dpi) / 72 
            #diameter of the point in mm
            self.diameter_mm = pixels_to_mm(self.diameter_pixel)
    
            # Update current y value
            self.current_y = user_y
            
            # Convert the cursor's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_cursor = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords_cursor[0]),pixels_to_mm(self.pixel_coords_cursor[1]))
            
            # Convert the target's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_target = self.ax.transData.transform((self.target_x, self.target_y))
            self.mm_coords_target = (pixels_to_mm(self.pixel_coords_target[0]),pixels_to_mm(self.pixel_coords_target[1]))
    
            # Start the SimPy process for target movement
            self.env.process(self.move_target())

    
        def move_point_to(self, location_x, location_y):
            self.current_x = location_x
            self.current_y = location_y 
            
    
            # Update the cursor's position on the plot
            self.point.set_data([self.current_x], [self.current_y])
            self.canvas.draw()
            
            self.cursor_x = self.current_x
            self.cursor_y = self.current_y
            
            # Convert the cursor's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords_cursor = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords_cursor[0]),pixels_to_mm(self.pixel_coords_cursor[1]))
            #print(f"Actual coordinates of the cursor in mm: {self.mm_coords_cursor}")
    
            # Update the label with the actual pixel coordinates
            self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_cursor}")
    
            # Refresh the GUI
            self.root.update()

        def move_target(self):
            """SimPy process to move the red target point in a random direction with a certain frequency."""
            while True:
                # Randomly choose one of the four directions (up, down, left, right)
                direction = random.choice([-2, -1, 1,2])  # Randomly move down (-2) left (-1), right (1), or up (+2)
                
                step_size = track2D_amp_dic[track2D_r_amp]  # Use 2D amplitude for both x and y
        
                # Move the target in both x and y directions
                if direction in [-1, 1]:  # Horizontal movement (left/right)
                    new_x = self.target_x + direction * step_size
                    
                    # Move right if it attempts to go below 0
                    if new_x < 0:
                        self.target_x += step_size  # Move right by step_size
                    elif new_x > 100:
                        self.target_x -= step_size  # Move left by step_size to stay in bounds
                    else:
                        self.target_x = new_x
                else:
                    if direction == 2:  # Vertical movement (up/down)
                        new_y = self.target_y +  step_size
                    else:
                        new_y = self.target_y -  step_size
                    # Move up if it attempts to go below 0
                    if new_y < 0:
                        self.target_y += step_size  # Move up by step_size
                    elif new_y > 100:
                        self.target_y -= step_size  # Move down by step_size to stay in bounds
                    else:
                        self.target_y = new_y
        
                # Update the target point's position on the plot
                self.target_point.set_data([self.target_x], [self.target_y])
                self.canvas.draw()
        
                # Convert the target's (x, y) in data coordinates to pixel coordinates
                self.pixel_coords_target = self.ax.transData.transform((self.target_x, self.target_y))
                self.mm_coords_target = (pixels_to_mm(self.pixel_coords_target[0]), pixels_to_mm(self.pixel_coords_target[1]))
                
                # Update the label with the actual pixel coordinates
                self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_target}")
        
                # Simulate a delay for the next movement (frequency)
                yield self.env.timeout(track2D_freq_dic[track2D_r_freq])  # Use 2D frequency


if 'Tracking_2D_1W' in task_info_dic.values():
    from gui_compound_BE import track2D_1w_x_cursor,track2D_1w_x_target,track2D_1w_shape,track2D_1w_amp,track2D_1w_freq
    class Reaction_tracking2d_1w:        
        def __init__(self,**kwargs):         
            self.cursor_x = track2D_1w_x_cursor
            self.current_x = self.cursor_x
            self.target_x = track2D_1w_x_target
            self.cursor_y = tracking2D_curve(track2D_1w_shape, self.cursor_x)
            self.current_y = self.cursor_y
            self.target_y = tracking2D_curve(track2D_1w_shape, self.target_x)
            self.animation_running = False
            self.point = None
            self.canvas = None
            self.ax = None
            self.pixel_label = None
            self.curve_type = track2D_1w_shape
            self.marker_size = 6 
            self.env = kwargs['environment']

            self.max_x = 10**5
            self.x_range = 100
            self.x_min = 0
            self.x_max = self.x_min + self.x_range

        def plot_curve(self):
            self.animation_running = True  
            user_x = self.current_x

            self.root = tk.Tk()
            plot_window = self.root
            plot_window.title(f"Curve Plot: {self.curve_type}")

            fig, self.ax = plt.subplots(figsize=(10, 4))
            self.canvas = FigureCanvasTkAgg(fig, master=plot_window)
            self.canvas.get_tk_widget().pack()
            dpi = fig.get_dpi()

            self.mm_label = tk.Label(plot_window, text="Coordinates in mm: (x, y)")
            self.mm_label.pack(pady=5)

            self.x_vals = np.linspace(0.01, self.max_x, 100000)
            self.y_vals = tracking2D_curve(self.curve_type, self.x_vals)
            user_y = tracking2D_curve(self.curve_type, user_x)
            self.target_y = tracking2D_curve(self.curve_type, self.target_x)

            self.line, = self.ax.plot(self.x_vals, self.y_vals, label=self.curve_type)
            self.point, = self.ax.plot(user_x, user_y, 'bo',markersize = self.marker_size, label="Blue Cursor Point")
            self.target_point, = self.ax.plot(self.target_x, self.target_y, 'ro', markersize = self.marker_size,label="Red Target Point")

            self.ax.set_title(f"Curve: {self.curve_type}")
            self.ax.set_xlabel(f"X Axis ({self.x_min} to {self.x_max})")
            self.ax.set_ylabel("Y Axis")
            self.ax.set_xlim(self.x_min, self.x_max)
            self.ax.grid(True)
            self.ax.legend()

            self.diameter_pixel= (self.marker_size * dpi) / 72 
            self.diameter_mm = pixels_to_mm(self.diameter_pixel)

            self.current_y = user_y
            self.cursor_y = self.current_y

            self.pixel_coords_cursor = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords_cursor[0]),pixels_to_mm(self.pixel_coords_cursor[1]))

            self.pixel_coords_target = self.ax.transData.transform((self.target_x, self.target_y))
            self.mm_coords_target = (pixels_to_mm(self.pixel_coords_target[0]),pixels_to_mm(self.pixel_coords_target[1]))

            self.env.process(self.move_target())

        def adjust_x_range(self):
            min_x = min(self.current_x, self.target_x)
            max_x = max(self.current_x, self.target_x)
            padding = 5

            if min_x - padding < self.x_min or max_x + padding > self.x_max:
                self.x_min = min_x - padding
                self.x_max = max_x + padding
                self.ax.set_xlim(self.x_min, self.x_max)
                self.ax.set_xlabel(f"X Axis ({self.x_min} to {self.x_max})")
                self.canvas.draw()    

        def move_point_to(self, location_x, location_y):
            self.current_x = location_x
            self.current_y = location_y

            if self.current_x >= self.x_max:
                self.x_min += self.x_range
                self.x_max += self.x_range

            if self.current_x >= self.max_x:
                self.current_x = self.max_x

            self.adjust_x_range()

            self.point.set_data([self.current_x], [self.current_y])
            self.canvas.draw()

            self.cursor_x = self.current_x
            self.cursor_y = self.current_y

            self.pixel_coords_cursor = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords_cursor[0]),pixels_to_mm(self.pixel_coords_cursor[1]))

            self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_cursor}")
            self.root.update()

        def move_target(self):
            while True:
                step_size = track2D_amp_dic[track2D_1w_amp]
                self.target_x += step_size

                if self.target_x >= self.max_x:
                    self.target_x = self.max_x

                self.target_y = tracking2D_curve(self.curve_type, self.target_x)
                self.adjust_x_range()

                self.target_point.set_data([self.target_x], [self.target_y])
                self.canvas.draw()

                self.pixel_coords_target = self.ax.transData.transform((self.target_x, self.target_y))
                self.mm_coords_target = (pixels_to_mm(self.pixel_coords_target[0]), pixels_to_mm(self.pixel_coords_target[1]))

                self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_target}")

                yield self.env.timeout(track2D_freq_dic[track2D_1w_freq])



if 'Tracing_1D_Bounded' in task_info_dic.values():
    
    class Reaction_tracing1d_b:
        def __init__(self):
            
            from gui_compound_BE import tracing1D_b_loc_x
            
            self.current_x = tracing1D_b_loc_x
            self.moving_forward = True  # Initialize direction to forward
            self.animation_running = False  # To control animation start/stop
            self.point = None
            self.canvas = None
            self.ax = None
            self.mm_label = None
            self.end_x = 100
            self.start_x = 0
            self.reach = 1
            self.marker_size = 6

        def plot_curve(self):

            # Ensure animation starts
            self.animation_running = True  
            
            user_x = self.current_x
            
            # Create the main window
            self.root = tk.Tk()
            
            # Create a new window for the plot
            plot_window = self.root
            plot_window.title('Line Plot')
        
            # Create a wider matplotlib figure for plotting in the new window
            fig, self.ax = plt.subplots(figsize=(30, 4))  # Increase the width for a wider window
            self.canvas = FigureCanvasTkAgg(fig, master=plot_window)
            self.canvas.get_tk_widget().pack()
            dpi = fig.get_dpi()
            
            # Add a label to display pixel coordinates
            self.mm_label = tk.Label(plot_window, text="Coordinates in mm: (x, y)")
            self.mm_label.pack(pady=5)
        
            # Generate x values for plotting (from 0 to 100)
            x_vals = np.linspace(0.01, 100, 1000)
        
            # Adjust the curve for larger distance between waves
            y_vals = 0*x_vals
            user_y = 0
            self.start_y = self.end_y = 0

            #get the max and min values of y
            self.max_y = self.min_y = 0
            # Plot the curve
            self.ax.plot(x_vals, y_vals, label='line')
        
            # Plot the initial point
            self.point, = self.ax.plot(user_x, user_y, 'ro', markersize=self.marker_size,label="Moving Point")  # red point
        
            # Set labels and title
            self.ax.set_title("Line")
            self.ax.set_xlabel("X Axis (0 to 100)")
            self.ax.set_ylabel("Y Axis")
        
            # Set intermediate ticks for the x-axis, with the range from 0 to 100
            self.ax.set_xticks(np.arange(0, 101, 5))  # Adding ticks every 50 units for a wider x-axis
            self.ax.set_xlim(0, 100)  # Set the x-axis limit from 0 to 100
        
            self.ax.grid(True)  # Optional: adds a grid for better visibility of the scale
        
            # Update the plot
            self.ax.legend()
            
            #diameter of the point in pixel
            self.diameter_pixel= (self.marker_size * dpi) / 72 
            #diameter of the point in mm
            self.diameter_mm = pixels_to_mm(self.diameter_pixel)
            
            #Update current y value
            self.current_y = user_y
            
            # Convert the point's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords[0]),pixels_to_mm(self.pixel_coords[1]))
            #convert the end point in data coordinate to pixel and mm coordinates
            self.pixel_end = self.ax.transData.transform((self.start_x, self.end_x))
            self.mm_x_start = pixels_to_mm(self.pixel_end[0])
            self.mm_x_end = pixels_to_mm(self.pixel_end[1])
                      
        def click_location_mm(self,old_x,old_y,magnitude_x,magnitude_y):
            #check if the point changes moving direction
           
            # Check the current direction and adjust the x value
            if self.moving_forward:
                new_x = old_x + magnitude_x
            else:
                new_x = old_x - magnitude_x
        
            # Reverse direction if the point reaches 0 or 1000
            if new_x > 100:
                new_x = 100
            elif new_x < 0:
                new_x = 0
            
            # Convert the point's (x, y) in data coordinates to pixel coordinates
            self.pixel_new_click = self.ax.transData.transform((new_x, self.current_y))
            self.mm_coords_new_click = (pixels_to_mm(self.pixel_new_click[0]),pixels_to_mm(self.pixel_new_click[1]))
            return self.mm_coords_new_click
        # Function to move the point along the curve once
        def move_point(self, magnitude_x,magnitude_y):
            #check if the point changes moving direction
            self.reach = 0
            # Check the current direction and adjust the x value
            if self.moving_forward:
                self.current_x += magnitude_x
            else:
                self.current_x -= magnitude_x
        
            # Reverse direction if the point reaches 0 or 1000
            if self.current_x >= 100:
                self.current_x = 100
                self.moving_forward = False
                self.reach = 1
            elif self.current_x <= 0:
                self.current_x = 0
                self.moving_forward = True
                self.reach = 1
        
            self.current_y = 0
            
            # Update the point's position on the plot
            self.point.set_data([self.current_x], [self.current_y])
            self.canvas.draw()
        
            # Convert the point's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords[0]),pixels_to_mm(self.pixel_coords[1]))
            #print(f"Actual pixel coordinates of the point: {pixel_coords}")
        
            # Update the label with the actual pixel coordinates
            self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_cursor}")
            # This allows the GUI to refresh
            self.root.update()
            # This allows the GUI to refresh


if 'Tracing_1D_1W' in task_info_dic.values():
    class Reaction_tracing1d_1w:
        
        def __init__(self):
            # Import from gui_compound_BE
            from gui_compound_BE import tracing1D_1w_loc_x
            
            self.current_x = tracing1D_1w_loc_x  # Initialize starting x location
            self.moving_forward = True  # Direction control
            self.animation_running = False  # Controls the animation state
            self.point = None
            self.canvas = None
            self.ax = None
            self.mm_label = None
            self.curve_type = "line"
            
            # Initialize x and y limits
            self.max_x = 10**5  # Full range for x values
            self.x_range = 100  # Visible range for x-axis
            self.x_min = 0  # Start of the visible window
            self.x_max = self.x_min + self.x_range  # End of the visible window
            
            # Initialize the first y-value and limits
            self.current_y = 0  # Initial y-value based on curve
            self.y_padding_factor = 0.2 # Padding factor for y scrolling to ensure some space around the point
            
            self.marker_size = 6
            
            self.new_screen = 1
    
        def plot_curve(self):
            """Plot the curve and initialize moving point."""
            # Ensure animation starts
            self.animation_running = True  
            user_x = self.current_x
            
            # Create the main window
            self.root = tk.Tk()
            plot_window = self.root
            plot_window.title("Line Plot")
        
            # Create a wider matplotlib figure for plotting
            fig, self.ax = plt.subplots(figsize=(10, 4))  # A wider window with aspect ratio suited to scrolling
            self.canvas = FigureCanvasTkAgg(fig, master=plot_window)
            self.canvas.get_tk_widget().pack()
            dpi = fig.get_dpi()
            
            # Add a label to display pixel coordinates
            self.mm_label = tk.Label(plot_window, text="Coordinates in mm: (x, y)")
            self.mm_label.pack(pady=5)
        
            # Generate x values for the entire curve (from 0 to 10^5)
            self.x_vals = np.linspace(0.01, self.max_x, 100000)  # Avoid x=0 for ln(x)
        
            # Get y-values using the external utility function
            self.y_vals = 0*self.x_vals
            user_y = 0
            self.y_end = 0
    
            # Plot the initial portion of the curve from 0 to 100 (visible window)
            self.line, = self.ax.plot(self.x_vals, self.y_vals, label=self.curve_type)
        
            # Plot the initial point at user_x, user_y
            self.point, = self.ax.plot(user_x, user_y, 'ro', markersize = self.marker_size,label="Moving Point")
        
            # Set labels and title
            self.ax.set_title(f"Curve: {self.curve_type}")
            self.ax.set_xlabel(f"X Axis ({self.x_min} to {self.x_max})")
            self.ax.set_ylabel("Y Axis")
        
            # Set the initial limits for the x-axis and y-axis
            self.ax.set_xlim(self.x_min, self.x_max)
           
            # Add grid for better visibility
            self.ax.grid(True)
        
            # Update the plot with the legend
            self.ax.legend()
        
            # Set current y value for the moving point
            self.current_y = user_y
            
            #diameter of the point in pixel
            self.diameter_pixel= (self.marker_size * dpi) / 72 
            #diameter of the point in mm
            self.diameter_mm = pixels_to_mm(self.diameter_pixel)
            
            # Convert the point's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords[0]),pixels_to_mm(self.pixel_coords[1]))
            #convert the end point in data coordinate to pixel and mm coordinates
            self.pixel_end = self.ax.transData.transform((self.x_min, self.x_max))
            self.mm_x_start = pixels_to_mm(self.pixel_end[0])
            self.mm_x_end = pixels_to_mm(self.pixel_end[1])
    
        def click_location_mm(self,old_x,old_y,magnitude_x,magnitude_y):
           
            # Check the current direction and adjust the x value
            if self.moving_forward:
                new_x = old_x + magnitude_x
            else:
                new_x = old_x - magnitude_x
        
            # Convert the point's (x, y) in data coordinates to pixel coordinates
            self.pixel_new_click = self.ax.transData.transform((new_x, self.current_y))
            self.mm_coords_new_click = (pixels_to_mm(self.pixel_new_click[0]),pixels_to_mm(self.pixel_new_click[1]))
            return self.mm_coords_new_click    
        
        
        def move_point(self, magnitude_x, magnitude_y):
                self.new_screen = 0
                """Move the point along the curve and ensure smooth movement."""
                # Move the x value forward
                if self.moving_forward:
                    self.current_x += magnitude_x
            
                # Check if the x value has reached or exceeded the visible window's end
                if self.current_x >= self.x_max:
                    # Scroll the visible window by moving the x-axis range forward
                    self.x_min += self.x_range
                    self.x_max += self.x_range
                   
                    # Update x-axis limits
                    self.ax.set_xlim(self.x_min, self.x_max)
                    self.ax.set_xlabel(f"X Axis ({self.x_min} to {self.x_max})")
                    
                    self.new_screen = 1
    
                    
                # Ensure we don't go beyond the maximum x-value limit
                if self.current_x >= self.max_x:
                    self.current_x = self.max_x
            
            
                # Update the point's position on the plot
                self.point.set_data([self.current_x], [self.current_y])
                self.canvas.draw()  # Refresh the plot
            
                # Convert the point's (x, y) in data coordinates to pixel coordinates
                # Convert the point's (x, y) in data coordinates to pixel coordinates
                self.pixel_coords = self.ax.transData.transform((self.current_x, self.current_y))
                self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords[0]),pixels_to_mm(self.pixel_coords[1]))
                #convert the end point in data coordinate to pixel and mm coordinates
                self.pixel_end = self.ax.transData.transform((self.x_min, self.x_max))
                self.mm_x_start = pixels_to_mm(self.pixel_end[0])
                self.mm_x_end = pixels_to_mm(self.pixel_end[1])
               
                #print(f"Actual pixel coordinates of the point: {pixel_coords}")
            
                # Update the label with the pixel coordinates
                self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_cursor}")
                
                # Refresh the GUI to show changes
                self.root.update()



if 'Tracing_2D_Bounded' in task_info_dic.values():
    

   class Reaction_tracing2d_b:
       
       def __init__(self):
           
           from gui_compound_BE import tracing2D_b_loc_x,tracing2D_b_shape
           
           self.current_x = tracing2D_b_loc_x
           self.moving_forward = True  # Initialize direction to forward
           self.animation_running = False  # To control animation start/stop
           self.point = None
           self.canvas = None
           self.ax = None
           self.mm_label = None
           self.curve_type = tracing2D_b_shape
           self.start_x = 0
           self.end_x = 100
           self.marker_size = 6
           self.reach = 1
           self.press_y = None

       def plot_curve(self):

           # Ensure animation starts
           self.animation_running = True  
           
           user_x = self.current_x
           
           # Create the main window
           self.root = tk.Tk()
           
           # Create a new window for the plot
           plot_window = self.root
           plot_window.title(f"Curve Plot: {self.curve_type}")
       
           # Create a wider matplotlib figure for plotting in the new window
           fig, self.ax = plt.subplots(figsize=(30, 4))  # Increase the width for a wider window
           self.canvas = FigureCanvasTkAgg(fig, master=plot_window)
           self.canvas.get_tk_widget().pack()
           dpi = fig.get_dpi()
       
           # Add a label to display pixel coordinates
           self.mm_label = tk.Label(plot_window, text="Coordinates in mm: (x, y)")
           self.mm_label.pack(pady=5)
       
           # Generate x values for plotting (from 0 to 100)
           x_vals = np.linspace(0.01, 100, 1000)  # Avoid x=0 for ln(x)
       
           # Adjust the curve for larger distance between waves
           y_vals = tracing2D_curve(self.curve_type, x_vals)
           user_y = tracing2D_curve(self.curve_type, user_x)
           self.start_y = tracing2D_curve(self.curve_type, 0)
           self.end_y = tracing2D_curve(self.curve_type, self.end_x)

           #get the max and min values of y
           self.max_y = np.max(y_vals)
           self.min_y = np.min(y_vals)
           # Plot the curve
           self.ax.plot(x_vals, y_vals, label=self.curve_type)
       
           # Plot the initial point
           self.point, = self.ax.plot(user_x, user_y, 'ro', markersize=self.marker_size,label="Moving Point")  # red point
       
           # Set labels and title
           self.ax.set_title(f"Curve: {self.curve_type}")
           self.ax.set_xlabel("X Axis (0 to 100)")
           self.ax.set_ylabel("Y Axis")
       
           # Set intermediate ticks for the x-axis, with the range from 0 to 100
           self.ax.set_xticks(np.arange(0, 101, 5))  # Adding ticks every 50 units for a wider x-axis
           self.ax.set_xlim(0, 100)  # Set the x-axis limit from 0 to 100
       
           self.ax.grid(True)  # Optional: adds a grid for better visibility of the scale
       
           # Update the plot
           self.ax.legend()
           
           #Update current y value
           self.current_y = user_y
           
           #diameter of the point in pixel
           self.diameter_pixel= (self.marker_size * dpi) / 72 
           #diameter of the point in mm
           self.diameter_mm = pixels_to_mm(self.diameter_pixel)
           
           # Convert the point's (x, y) in data coordinates to pixel coordinates
           self.pixel_coords = self.ax.transData.transform((self.current_x, self.current_y))
           self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords[0]),pixels_to_mm(self.pixel_coords[1]))
           #convert the end point in data coordinate to pixel and mm coordinates
           self.pixel_end_x = self.ax.transData.transform((self.start_x, self.end_x))
           self.mm_x_start = pixels_to_mm(self.pixel_end_x[0])
           self.mm_x_end = pixels_to_mm(self.pixel_end_x[1])
           
           self.pixel_end_y = self.ax.transData.transform((self.start_y, self.end_y))
           self.mm_y_start = pixels_to_mm(self.pixel_end_y[0])
           self.mm_y_end = pixels_to_mm(self.pixel_end_y[1])
           
       def click_location_mm(self,old_x,old_y,magnitude_x,magnitude_y):
          
           # Check the current direction and adjust the x value
           if self.moving_forward:
               new_x = old_x + magnitude_x
           else:
               new_x = old_x - magnitude_x
        
           y_val = tracing2D_curve(self.curve_type,new_x)
           
           #adjust the moving direction along y axis according to the relative location of the old y location and the y location on the curve
           if abs(y_val-old_y) > 0.05:
               
               if old_y < y_val:
                   new_y = old_y + magnitude_y
               elif old_y < y_val:
                    new_y = old_y - magnitude_y
               else:
                    new_y = old_y
           else:
               new_y = old_y
                
             
           # Convert the point's (x, y) in data coordinates to pixel coordinates
           self.pixel_new_click = self.ax.transData.transform((new_x, new_y))
           self.mm_coords_new_click = (pixels_to_mm(self.pixel_new_click[0]),pixels_to_mm(self.pixel_new_click[1]))
           return self.mm_coords_new_click    
        
        
       # Function to move the point along the curve once
       def move_point(self, magnitude_x,magnitude_y):
           self.reach = 0    
           self.press_y = None
           # Check the current direction and adjust the x value
           if self.moving_forward:
               self.current_x += magnitude_x
           else:
               self.current_x -= magnitude_x
       
           # Reverse direction if the point reaches 0 or 1000
           if self.current_x >= 100:
               self.current_x = 100
               self.moving_forward = False
               self.reach = 1
           elif self.current_x <= 0:
               self.current_x = 0
               self.moving_forward = True
               self.reach = 1
       
           # calculte the y-value based on the curve type and the new x position
           new_y = tracing2D_curve(self.curve_type, self.current_x)
           
           if abs(self.current_y - new_y)>0.05: #move along y if difference is larger than a threshold
               self.press_y = True    
               if self.current_y<new_y:
                   self.current_y += magnitude_y
               elif self.current_y>new_y:
                   self.current_y -= magnitude_y
           if self.current_y >= self.max_y:
               self.current_y = self.max_y
           elif self.current_y <= self.min_y:
               self.current_y = self.min_y
    
           
           # Update the point's position on the plot
           self.point.set_data([self.current_x], [self.current_y])
           self.canvas.draw()
       
           # Convert the point's (x, y) in data coordinates to pixel coordinates
           # Convert the point's (x, y) in data coordinates to pixel coordinates
           self.pixel_coords = self.ax.transData.transform((self.current_x, self.current_y))
           self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords[0]),pixels_to_mm(self.pixel_coords[1]))
           #print(f"Actual pixel coordinates of the point: {pixel_coords}")
       
           # Update the label with the actual pixel coordinates
           self.mm_label.config(text=f"Coordinates in mm: {self.mm_coords_cursor}")
           # This allows the GUI to refresh
           self.root.update()
           # This allows the GUI to refresh

if 'Tracing_2D_1W' in task_info_dic.values():
    class Reaction_tracing2d_1w:
        
        def __init__(self):
            # Import from gui_compound_BE
            from gui_compound_BE import tracing2D_1w_loc_x, tracing2D_1w_shape
            
            self.current_x = tracing2D_1w_loc_x  # Initialize starting x location
            self.moving_forward = True  # Direction control
            self.animation_running = False  # Controls the animation state
            self.point = None
            self.canvas = None
            self.ax = None
            self.mm_label = None
            self.curve_type = tracing2D_1w_shape  # Initialize curve type from external GUI setup
            
            # Initialize x and y limits
            self.max_x = 10**5  # Full range for x values
            self.x_range = 100  # Visible range for x-axis
            self.x_min = 0  # Start of the visible window
            self.x_max = self.x_min + self.x_range  # End of the visible window
            
            # Initialize the first y-value and limits
            self.current_y = tracing2D_curve(self.curve_type, self.current_x)  # Initial y-value based on curve
            self.y_padding_factor = 0.2 # Padding factor for y scrolling to ensure some space around the point
            
            self.new_screen = 1
            self.press_y = None
            
            self.marker_size = 6
    
        def plot_curve(self):
            """Plot the curve and initialize moving point."""
            # Ensure animation starts
            self.animation_running = True  
            user_x = self.current_x
            
            # Create the main window
            self.root = tk.Tk()
            plot_window = self.root
            plot_window.title(f"Curve Plot: {self.curve_type}")
        
            # Create a wider matplotlib figure for plotting
            fig, self.ax = plt.subplots(figsize=(30, 4))  # A wider window with aspect ratio suited to scrolling
            self.canvas = FigureCanvasTkAgg(fig, master=plot_window)
            self.canvas.get_tk_widget().pack()
            dpi = fig.get_dpi()
        
            # Add a label to display pixel coordinates
            self.mm_label = tk.Label(plot_window, text="Pixel Coordinates: (x, y)")
            self.mm_label.pack(pady=5)
        
            # Generate x values for the entire curve (from 0 to 10^5)
            self.x_vals = np.linspace(0.01, self.max_x, 100000)  # Avoid x=0 for ln(x)
        
            # Get y-values using the external utility function
            self.y_vals = tracing2D_curve(self.curve_type, self.x_vals)
            user_y = tracing2D_curve(self.curve_type, user_x)
            self.y_end = tracing2D_curve(self.curve_type, self.x_max)
    
            # Plot the initial portion of the curve from 0 to 100 (visible window)
            self.line, = self.ax.plot(self.x_vals, self.y_vals, label=self.curve_type)
        
            # Plot the initial point at user_x, user_y
            self.point, = self.ax.plot(user_x, user_y, 'ro', markersize=self.marker_size,label="Moving Point")
        
            # Set labels and title
            self.ax.set_title(f"Curve: {self.curve_type}")
            self.ax.set_xlabel(f"X Axis ({self.x_min} to {self.x_max})")
            self.ax.set_ylabel("Y Axis")
        
            # Set the initial limits for the x-axis and y-axis
            self.ax.set_xlim(self.x_min, self.x_max)
            self.adjust_y_limits()  # Adjust the y-axis based on the current point's y value
        
            # Add grid for better visibility
            self.ax.grid(True)
        
            # Update the plot with the legend
            self.ax.legend()
        
            # Set current y value for the moving point
            self.current_y = user_y
            
            #diameter of the point in pixel
            self.diameter_pixel= (self.marker_size * dpi) / 72 
            #diameter of the point in mm
            self.diameter_mm = pixels_to_mm(self.diameter_pixel)
            
            # Convert the point's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords[0]),pixels_to_mm(self.pixel_coords[1]))
            #convert the end point in data coordinate to pixel and mm coordinates
            self.pixel_end_x = self.ax.transData.transform((self.x_min, self.x_max))
            self.mm_x_start = pixels_to_mm(self.pixel_end_x[0])
            self.mm_x_end = pixels_to_mm(self.pixel_end_x[1])
            
            self.pixel_end_y = self.ax.transData.transform((user_y,self.y_end))
            self.mm_y_end = pixels_to_mm(self.pixel_end_y[1])
    
    
        def click_location_mm(self,old_x,old_y,magnitude_x,magnitude_y):
           
            # Check the current direction and adjust the x value
            if self.moving_forward:
                new_x = old_x + magnitude_x
            else:
                new_x = old_x - magnitude_x
         
            y_val = tracing2D_curve(self.curve_type,new_x)
            #if click, y of the point can be on the curve
            
            if abs(y_val-old_y) > 0.05:
                if old_y < y_val:
                    new_y = old_y + magnitude_y
                elif old_y < y_val:
                    new_y = old_y - magnitude_y
                else:
                    new_y = old_y
            else:
                new_y = old_y
            # Convert the point's (x, y) in data coordinates to pixel coordinates
            self.pixel_new_click = self.ax.transData.transform((new_x, new_y))
            self.mm_coords_new_click = (pixels_to_mm(self.pixel_new_click[0]),pixels_to_mm(self.pixel_new_click[1]))
            return self.mm_coords_new_click    
    
    
        def adjust_y_limits(self):
            """Adjust the y-axis dynamically to fit the current y-values."""
            # Calculate dynamic y limits based on the current position
            self.y_vals_onescreen  = tracing2D_curve(self.curve_type, np.linspace(self.x_min+0.01, self.x_max, self.x_range*10))
            self.y_min_visible = np.min(self.y_vals_onescreen)
            self.y_max_visible = np.max(self.y_vals_onescreen)

            # Ensure we do not set invalid limits for logarithmic curves
            if self.curve_type == "ln" and self.current_x <= 1:
                self.y_min_visible = min(self.y_vals[self.x_vals > 1])
            
            # Update the y-axis limits
            self.ax.set_ylim(self.y_min_visible, self.y_max_visible)
    
        def move_point(self, magnitude_x, magnitude_y):
            self.press_y = None
            self.new_screen = 0
            """Move the point along the curve and ensure smooth movement."""
            # Move the x value forward
            if self.moving_forward:
                self.current_x += magnitude_x
        
            # Check if the x value has reached or exceeded the visible window's end
            if self.current_x >= self.x_max:
                # Scroll the visible window by moving the x-axis range forward
                self.x_min += self.x_range
                self.x_max += self.x_range
               
                # Update x-axis limits
                self.ax.set_xlim(self.x_min, self.x_max)
                self.ax.set_xlabel(f"X Axis ({self.x_min} to {self.x_max})")
                
                self.new_screen = 1
            if self.current_x == self.x_min:
                self.new_screen = 1
                
            # Ensure we don't go beyond the maximum x-value limit
            if self.current_x >= self.max_x:
                self.current_x = self.max_x
        
            # Calculate the new y-value based on the current x
            new_y = tracing2D_curve(self.curve_type, self.current_x)
            
            '''
            # Adjust the y-value with smooth transitions
            if self.current_y < new_y:
                self.current_y = min(self.current_y + magnitude_y, new_y)  # Ensure y doesn't overshoot
            elif self.current_y > new_y:
                self.current_y = max(self.current_y - magnitude_y, new_y)  # Ensure y doesn't overshoot
            '''
            if abs(self.current_y - new_y)>0.05: #move along y if difference is larger than a threshold
                self.press_y = True    
                if self.current_y < new_y:
                    self.current_y =self.current_y + magnitude_y  
                elif self.current_y > new_y:
                    self.current_y = self.current_y - magnitude_y
            # Update y-axis to ensure dynamic scrolling based on current y
            self.adjust_y_limits()
        
            # Update the point's position on the plot
            self.point.set_data([self.current_x], [self.current_y])
            self.canvas.draw()  # Refresh the plot
        
            # Convert the point's (x, y) in data coordinates to pixel coordinates
            self.pixel_coords = self.ax.transData.transform((self.current_x, self.current_y))
            self.mm_coords_cursor = (pixels_to_mm(self.pixel_coords[0]),pixels_to_mm(self.pixel_coords[1]))
            #convert the end point in data coordinate to pixel and mm coordinates
            self.pixel_end_x = self.ax.transData.transform((self.x_min, self.x_max))
            self.mm_x_start = pixels_to_mm(self.pixel_end_x[0])
            self.mm_x_end = pixels_to_mm(self.pixel_end_x[1])
        
            # Update the label with the pixel coordinates
            self.mm_label.config(text=f"Coordinatesin mm: {self.mm_coords_cursor}")
            
            # Refresh the GUI to show changes
            self.root.update()




        
        
