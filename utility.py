# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 08:36:28 2024
@author: wyuanc
"""

"""Utility functions and shared configuration for the QN-MHP project.

This module centralizes:
- file persistence helpers used by the GUI
- random processing-time generators
- shared task and attribute dictionaries
- lightweight logging helpers
- formatted simulation summary tables

The goal is to keep the rest of the codebase focused on model behavior rather
than repeated housekeeping logic.
"""


import os
import pickle
import shutil
import stat
import math
import random
import numpy as np 

PROJECT_MARKER_FILE = 'qn_mhp_project.marker'
active_project_dir = None

def set_active_project_dir(project_dir):
    """Set the currently opened/saved project folder for automatic mirroring."""
    global active_project_dir
    active_project_dir = project_dir

def get_active_project_dir():
    return active_project_dir


#Section 1 Save and Retrieve
#save and retrieve user input from GUI
class save_user_input:
    
    def __init__(self,saved):
        
        if saved==0:
            global path
            path='backup/'    
            self.mkdir(path)
            
        else:
            pass
           
    def mkdir(self,path):
        
        path=path.rstrip('/')
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs (path)
        else:
            return False
            
    
    #save variable in a user created folder
    def save_var(self,v,filename):
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
        f=open(filename,'wb')
        pickle.dump(v,f)
        f.close()

        # When a project folder is active, keep it synchronized with the
        # current backup/ working folder so Save As can be used first and
        # later edits still persist automatically.
        try:
            normalized = os.path.normpath(filename)
            backup_root = os.path.normpath('backup')
            if active_project_dir and (normalized == backup_root or normalized.startswith(backup_root + os.sep)):
                rel_path = os.path.relpath(normalized, backup_root)
                mirror_path = os.path.join(active_project_dir, rel_path)
                os.makedirs(os.path.dirname(mirror_path) or active_project_dir, exist_ok=True)
                with open(mirror_path, 'wb') as mirror_file:
                    pickle.dump(v, mirror_file)
                self._write_project_marker(active_project_dir)
        except Exception:
            pass
        return filename
    
    def load_var(self,filename):
        f=open(filename,'rb')
        r=pickle.load(f)
        f.close()
        return r
    
    def _write_project_marker(self, folder):
        os.makedirs(folder, exist_ok=True)
        marker_path = os.path.join(folder, PROJECT_MARKER_FILE)
        with open(marker_path, 'w', encoding='utf-8') as f:
            f.write('QN-MHP project folder')

    def folder_has_project_data(self, folder):
        if not folder or not os.path.isdir(folder):
            return False
        marker_path = os.path.join(folder, PROJECT_MARKER_FILE)
        if os.path.exists(marker_path):
            return True
        for entry in os.scandir(folder):
            if entry.is_file() and entry.name.endswith('.txt'):
                return True
        return False

    def copy_search_file(self,srcDir,desDir):
        """Copy all files from srcDir into desDir without deleting the working folder."""
        os.makedirs(desDir, exist_ok=True)
        if not os.path.exists(srcDir):
            return
        ls=os.listdir(srcDir)
        for line in ls:
            filePath=os.path.join(srcDir,line)
            destPath=os.path.join(desDir,line)
            if os.path.isfile(filePath):
                shutil.copy2(filePath,destPath)
            elif os.path.isdir(filePath):
                if os.path.exists(destPath):
                    shutil.rmtree(destPath, onerror=_remove_readonly)
                shutil.copytree(filePath,destPath)
        self._write_project_marker(desDir)

    def load_search_file(self,srcDir,desDir):
        """Load a saved configuration folder into the session working folder."""
        os.makedirs(desDir, exist_ok=True)
        reset_session_folder(desDir)
        if not srcDir or not os.path.exists(srcDir):
            return
        ls=os.listdir(srcDir)
        for line in ls:
            if line == PROJECT_MARKER_FILE:
                continue
            filePath=os.path.join(srcDir,line)
            destPath=os.path.join(desDir,line)
            if os.path.isfile(filePath):
                shutil.copy2(filePath,destPath)
            elif os.path.isdir(filePath):
                shutil.copytree(filePath,destPath)

def has_saved_input(filename):
    """Return True when a saved GUI parameter file already exists."""
    return os.path.exists(filename)
def has_any_saved_inputs(*filenames):
    """Return True when at least one saved GUI parameter file exists."""
    return any(os.path.exists(name) for name in filenames)
def _remove_readonly(func, path, _):
    """Allow cleanup of read-only files on Windows."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def reset_session_folder(folder_path):
    """Clear saved GUI parameters for the current run without deleting the folder itself."""
    os.makedirs(folder_path, exist_ok=True)
    for entry in os.scandir(folder_path):
        try:
            if entry.is_file() or entry.is_symlink():
                os.unlink(entry.path)
            elif entry.is_dir():
                shutil.rmtree(entry.path, onerror=_remove_readonly)
        except PermissionError:
            # Skip locked files so the GUI can still open; new values from this run will overwrite them.
            continue
def format_departure_be_table(departure_be_dict):
    """Return a formatted table for behavior element departures."""
    rows = []
    for be_name, task_map in departure_be_dict.items():
        if isinstance(task_map, dict):
            for task_no, departure_no in task_map.items():
                if departure_no not in ('', None):
                    rows.append((str(be_name), str(task_no), str(departure_no)))
    if not rows:
        return "No behavior element departure records."
    rows.sort(key=lambda item: (item[0], int(item[1]) if item[1].isdigit() else item[1]))
    headers = ("Behavior element", "Task no.", "Departure no.")
    widths = [
        max(len(headers[0]), max(len(row[0]) for row in rows)),
        max(len(headers[1]), max(len(row[1]) for row in rows)),
        max(len(headers[2]), max(len(row[2]) for row in rows)),
    ]
    line = "-" * (sum(widths) + 10)
    output = [line, f"{headers[0]:<{widths[0]}} | {headers[1]:<{widths[1]}} | {headers[2]:<{widths[2]}}", line]
    for row in rows:
        output.append(f"{row[0]:<{widths[0]}} | {row[1]:<{widths[1]}} | {row[2]:<{widths[2]}}")
    output.append(line)
    return "\n".join(output)
def format_departure_server_table(departure_server_dict):
    """Return a formatted table for server departures by task and simulation time."""
    rows = []
    for server_name, task_map in departure_server_dict.items():
        for task_no, record in task_map.items():
            times = record.get("time", [])
            numbers = record.get("number", [])
            for sim_time, departure_no in zip(times, numbers):
                rows.append((str(server_name), str(task_no), f"{sim_time:.3f}", str(departure_no)))
    if not rows:
        return "No server departure records."
    rows.sort(key=lambda item: (
        item[0],
        int(item[1]) if item[1].isdigit() else item[1],
        float(item[2])
    ))
    headers = ("Server", "Task no.", "Sim time", "Departure no.")
    widths = [
        max(len(headers[0]), max(len(row[0]) for row in rows)),
        max(len(headers[1]), max(len(row[1]) for row in rows)),
        max(len(headers[2]), max(len(row[2]) for row in rows)),
        max(len(headers[3]), max(len(row[3]) for row in rows)),
    ]
    line = "-" * (sum(widths) + 13)
    output = [line, f"{headers[0]:<{widths[0]}} | {headers[1]:<{widths[1]}} | {headers[2]:<{widths[2]}} | {headers[3]:<{widths[3]}}", line]
    for row in rows:
        output.append(f"{row[0]:<{widths[0]}} | {row[1]:<{widths[1]}} | {row[2]:<{widths[2]}} | {row[3]:<{widths[3]}}")
    output.append(line)
    return "\n".join(output)
#Section2 color changer
#change the (r,g,b) value to hexadecimal color code 
def color_changer(a,b,c):
    return "#"+"".join([i[2:] if len(i[2:])>1 else '0'+i[2:] for i in [hex(a),hex(b),hex(c)]])
        
#Section3 define ppt, cpt, mpt
#ppt, cpt, mpt are model parameters that are also shown in model.py
#but need to be defined here       
# Define functions that return new random values each time they are called
def random_ppt():
    return (-1) * 16 * math.log(1 - random.uniform(0, 1)) + 17
def random_cpt():
    return (-1) * 22 * math.log(1 - random.uniform(0, 1)) + 13
def random_mpt():
    return (-1) * 14 * math.log(1 - random.uniform(0, 1)) + 10
#ppt=33
#cpt=35
#mpt=24
#Section 4 BE and attribute reference
#BE and the attribute information to refer
#define BE index
BE_dic = {}
BE_dic[11] = 'See'
BE_dic[31] = 'Hear'
BE_dic[101] = 'Store_to_WM'
BE_dic[111] = 'Choice'
BE_dic[211] ='Press_button'
BE_dic[212] ='Mouse_click'
BE_dic[201] = 'Look_at'
BE_dic[121] = 'Judge_relative_location'
BE_dic[123] = 'Judge_identity'
BE_dic[130] = 'Count'
BE_dic[135] = 'Cal_single_digit_num'
BE_dic[321] = 'Look_for'
#compound_BE
compound_BE=['Look_for','Tracking_1D','Tracking_1D_Random','Tracking_1D_1W',\
                   'Tracking_2D','Tracking_2D_Random','Tracking_2D_1W',\
                       'Tracing_1D_Bounded','Tracing_1D_1W',\
                       'Tracing_2D_Bounded','Tracing_2D_1W']
basic_BE = [item for item in BE_dic.values()]
#global data to save departure number of each BE
departure_BE_N = {key: {} for key in set(compound_BE) | set(basic_BE)}
server = ['server1','server2','server3','server4','server5','server6','server7','server8',\
          'serverA','serverB','serverC','serverD','serverE','serverF','serverG','serverW','serverY','serverZ',\
              'righthand','lefthand','eyes']
departure_server_N = {key: {i: {"time": [], "number": []} for i in range(1, 6)} for key in server}
attribute_dic={}
attribute_dic['stimuli']=[1,0]#stimuli,noise
attribute_dic['type']=[2,3]#visual,auditory
attribute_dic['info']=[4,5,6,7]#spatial,verbal,both spatial and verbal,unknown
attribute_dic[0]='noise'
attribute_dic[1]='stimuli'
attribute_dic[2]= 'visual'
attribute_dic[3]='auditory'
attribute_dic[4]='spatial'
attribute_dic[5]='verbal'
attribute_dic[6]='both spatial and verbal'
attribute_dic[7]='unknown'
#Section 5 variables for specific BE
#can be modified according to your specific task requirements
#5.1 for Choice
color_list=[(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(255,128,0)]       
color_dic={'red':(255,0,0), 'green':(0,255,0), 'blue':(0,0,255),\
          'yellow':(255,255,0), 'cyan':(0,255,255),'megenta':(255,0,255)
          }
text_list = ['A','B','C','D','E','F','G','H']
    
#5.2 for Look_for
#items for look_for task    
# Edit visual_search_layout.json to set any number of targets at arbitrary
# positions in the normalized visual field (x/y between 0 and 100).
# The legacy tuple is (row=y, column=x), followed by label and color.
import json as _visual_json
from pathlib import Path as _VisualPath

import math

def _load_visual_search_config():
    """Validate screen geometry and target coordinates in physical millimeters."""
    config_path = _VisualPath(__file__).with_name('visual_search_layout.json')
    if not config_path.exists():
        raise FileNotFoundError('Missing Look For configuration: ' + str(config_path))
    data = _visual_json.loads(config_path.read_text(encoding='utf-8'))
    if data.get('coordinate_system') != 'millimeters':
        raise ValueError('Look For coordinate_system must be millimeters')
    if data.get('position_mode', 'fixed') not in ('fixed', 'random'):
        raise ValueError('Look For position_mode must be fixed or random')
    screen = data['screen']
    width = float(screen['width_mm'])
    height = float(screen['height_mm'])
    distance = float(screen['viewing_distance_mm'])
    if not all(math.isfinite(value) and value > 0 for value in (width, height, distance)):
        raise ValueError('Screen dimensions and viewing distance must be positive finite millimeters')
    # One geometry for the Look For layout and the Eye Server's angle calculation.
    import eye_movement_model as eye_model
    eye_model.SCREEN_WIDTH_MM = width
    eye_model.SCREEN_HEIGHT_MM = height
    eye_model.VIEWING_DISTANCE_MM = distance
    return data, width, height


def _load_visual_search_targets():
    """Read physical target coordinates, preserving the legacy (y, x) layout API.

    Internally the existing renderer and Eye Server still accept normalized
    0..100 coordinates. Convert physical millimeters at this boundary so that
    target rendering and movement timing use identical positions.
    """
    data, width, height = _load_visual_search_config()
    targets = []
    for index, item in enumerate(data['targets'], start=1):
        x_mm, y_mm = float(item['x_mm']), float(item['y_mm'])
        if not (math.isfinite(x_mm) and math.isfinite(y_mm) and
                0 <= x_mm <= width and 0 <= y_mm <= height):
            raise ValueError('Look For target %d must be within screen dimensions in mm' % index)
        label, color = str(item['label']), str(item['color']).lower()
        if not label:
            raise ValueError('Look For target %d has an empty label' % index)
        if color not in color_dic:
            raise ValueError('Look For target %d has unsupported color %r; use %s' %
                             (index, color, ', '.join(sorted(color_dic))))
        targets.append(((100 * y_mm / height, 100 * x_mm / width), label, color))
    if not targets:
        raise ValueError('At least one Look For target is required')
    return targets


def reset_visual_search_positions():
    """Reload developer configuration at the start of each simulation run."""
    from random import uniform
    data, _width, _height = _load_visual_search_config()
    templates = _load_visual_search_targets()
    if data.get('position_mode', 'fixed') == 'random':
        templates = [((uniform(5, 95), uniform(5, 95)), label, color)
                     for _position, label, color in templates]
    look_for_ls[:] = templates
    return look_for_ls


look_for_ls = _load_visual_search_targets()

# Backward-compatible name for integrations using the earlier randomizer.
def randomize_visual_search_positions():
    return reset_visual_search_positions()

look_for_dic = {'2D': look_for_ls}
n_look_for_ls=len(look_for_ls)
look_at_list = [str(item[0]) for item in look_for_ls]
#5.3 for Mouse click
max_val_click = 100
#5.4 for tracking and tracing
#amplitude(pixel) and frequency
#1W: 1 Way 
tracktrace_name = ['Tracking_1D','Tracking_1D_Random','Tracking_1D_1W',\
                   'Tracking_2D','Tracking_2D_Random','Tracking_2D_1W',\
                       'Tracing_1D_Bounded','Tracing_1D_1W',\
                       'Tracing_2D_Bounded','Tracing_2D_1W']
track1D_freq_dic={'Slow':100,'Medium':50,'Quick':10}  #how long (ms) between each movement 
track1D_amp_dic={'Small':1,'Medium':5,'Large':10}
track2D_freq_dic={'Slow':200,'Medium':100,'Quick':50}
track2D_amp_dic={'Small':1,'Medium':5,'Large':10}
static2D_freq_dic={'Slow':10,'Medium':50,'Quick':100}
static2D_amp_dic={'Small':1,'Medium':10,'Large':20}
dynamic1D_freq_dic={'Slow':10,'Medium':50,'Quick':100}
dynamic1D_amp_dic={'Small':1,'Medium':10,'Large':20}
dynamic2D_freq_dic={'Slow':10,'Medium':50,'Quick':100}
dynamic2D_amp_dic={'Small':1,'Medium':10,'Large':20}
tracing1D_amp_dic = {'Small':1,'Medium':5,'Large':10}
tracing2D_amp_x_dic = {'Small':0.1,'Medium':1,'Large':2.5}
tracing2D_amp_y_dic = {'Small':0.1,'Medium':0.25,'Large':0.5}
direction_track1D=1
direction_static2D=[1]
direction_dynamic2D=[1]
ppi=157 #determined by display 
def pixels_to_mm(pixels):
    # Conversion factor from inches to millimeters
    inches_to_mm = 25.4
    
    # Convert pixels to millimeters
    mm = (pixels / ppi) * inches_to_mm
    return mm
def tracking2D_curve(curve_type,x_vals):
    """Calculate y-values based on the specified curve type."""
    if curve_type == "sin":
        return np.sin(x_vals / 5)  # Adjusting the scaling as needed
    elif curve_type == "ln":
        return np.log(x_vals)  # Logarithmic function
    elif curve_type == "e^x":
        return np.exp(x_vals / 50)  # Scaling for e^x
    #define more curve types here
def tracing2D_curve(curve_type,x_vals):
    """Calculate y-values based on the specified curve type."""
    if curve_type == "sin":
        return np.sin(x_vals / 5)  # Adjusting the scaling as needed
    elif curve_type == "ln":
        return np.log(x_vals+0.01)  # Logarithmic function  # Avoid x=0 for ln(x)
    elif curve_type == "e^x":
        return np.exp(x_vals / 50)  # Scaling for e^x
    #define more curve types here
    
#convert the real position in the tkinter canvas to coordinate range 0-100
def real_to_coor_x(real_x,real_y,origin,length,scale):
    coor_x = (real_x-origin)/length*scale
    return (coor_x)
    
