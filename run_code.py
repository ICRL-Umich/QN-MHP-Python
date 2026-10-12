"""
Created on Tue Aug  6 13:23:02 2024

@author: wyuanc
"""

"""Main entry point for running the QN-MHP simulation.

Usage:
    python run_code.py

The script launches the GUI, builds the SimPy model, runs the selected tasks
"""




import simpy
import gui_general
import utility
from utility import save_user_input as save
from utility import attribute_dic,tracktrace_name
import numpy as np



import sys
import os
from datetime import datetime
import atexit

# ----------------------------------------------------------------------
# Tee class:
# Redirects all standard output (print statements) to both:
# 1) Console (terminal)
# 2) Log file
# ----------------------------------------------------------------------
class Tee:
    def __init__(self, filename):
        # Open log file with UTF-8 encoding
        self.file = open(filename, "w", encoding="utf-8")
        self.stdout = sys.stdout  # Original console output

    def write(self, message):
        # Write to both file and console
        if not self.file.closed:
            self.file.write(message)
            self.file.flush()
        self.stdout.write(message)  # Ensure real-time logging (important for simulation)

    def flush(self):
        # Required for compatibility with sys.stdout
        if not self.file.closed:
            self.file.flush()
        self.stdout.flush()


# ----------------------------------------------------------------------
# Create log directory if it does not exist
# ----------------------------------------------------------------------
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)

# ----------------------------------------------------------------------
# Generate a timestamped log filename
# Example: log_20260328_154233.txt
# ----------------------------------------------------------------------
log_file = os.path.join(
    log_dir,
    f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
)

# ----------------------------------------------------------------------
# Redirect all print() output to both console and file
# ----------------------------------------------------------------------
sys.stdout = Tee(log_file)


# ----------------------------------------------------------------------
# Ensure log file is properly closed when the program exits
# ----------------------------------------------------------------------
def close_log():
    if isinstance(sys.stdout, Tee):
        tee = sys.stdout
        sys.stdout = tee.stdout
        if not tee.file.closed:
            tee.file.close()

atexit.register(close_log)


# ----------------------------------------------------------------------
# Optional: Mark the start of simulation (useful for experiment tracking)
# ----------------------------------------------------------------------
print("===== Simulation Started =====")




env = simpy.Environment()
if not gui_general.run():
    print("Simulation cancelled.")
    sys.exit(0)

#Run GUI


from gui_general import task_info_dic,Tasklist_dic,SIMTIME,anim,entity_dic,entity_dic_hear,entity_dic_see


from entity_basic_BE import entity_generation as gen_basic
from entity_compound_BE import entity_generation as gen_comp

from model import QN_MHP
qnmhp = QN_MHP(env)


#run model
#ignition of entity generation accorcing to user input data

class ModelRun:
    
    def entity(self):
        """
        Process entities based on the Tasklist_dic and run the appropriate simulation.
        """
        for no in Tasklist_dic:
            self.process_task(no)
        # A standalone Look At has no See/Hear stimulus source. Generate
        # visual entities explicitly so it can reach W, Y, Z and Eye Server.
        # All other task types retain their original entity generation paths.
        self.generate_standalone_look_at_entities()
        if entity_dic_see!={} or entity_dic_hear!={}:
            self.process_entity_data(entity_dic_see)
            self.process_entity_data(entity_dic_hear)

    def generate_standalone_look_at_entities(self):
        """Schedule developer-configurable stimuli for standalone Look At tasks."""
        import json
        from pathlib import Path

        config_path = Path(__file__).with_name('look_at_layout.json')
        config = json.loads(config_path.read_text(encoding='utf-8'))
        stimulus = config.get('standalone_stimulus', {})
        first_arrival_ms = float(stimulus.get('first_arrival_ms', 0))
        interval_ms = float(stimulus.get('interval_ms', 500))
        occurrences = int(stimulus.get('occurrences', 5))
        if first_arrival_ms < 0 or interval_ms <= 0 or occurrences < 1:
            raise ValueError('Invalid standalone Look At stimulus configuration')

        for task_no, steps in Tasklist_dic.items():
            if steps != [['Look_at']]:
                continue
            print('Scheduling standalone Look At: task=%s, first=%.2f ms, '
                  'interval=%.2f ms, occurrences=%d' %
                  (task_no, first_arrival_ms, interval_ms, occurrences))
            env.process(gen_basic().color_en(
                env, qnmhp, str(task_no), fa=first_arrival_ms,
                iat=interval_ms, occur=occurrences, seeorhear='see'
            ))

    def process_task(self, no):
        """
        Process a compound BE based on its identifier.

        """
        task_types = {
            'Look_for': lambda: env.process(gen_comp().Look_for_en(env, qnmhp, no)),
            'Tracking_1D': lambda: self.track_1d(no),
            'Tracking_1D_1W': lambda: self.track_1d(no),
            'Tracking_1D_Random': lambda: self.track_1d(no),
            'Tracking_2D': lambda: self.track_2d(no),
            'Tracking_2D_Random': lambda: self.track_2d(no),
            'Tracking_2D_1W': lambda: self.track_2d(no),
            'Tracing_1D_Bounded': lambda: self.tracing_1d_bounded(no),
            'Tracing_1D_1W': lambda: self.tracing_1d_1w(no),
            'Tracing_2D_Bounded': lambda: self.tracing_2d_bounded(no),
            'Tracing_2D_1W': lambda: self.tracing_2d_1w(no)
        }

        for task_type, action in task_types.items():
            if [task_type] in Tasklist_dic[no]:
                action()
                break

    def track_1d(self, no):
        """
        Process 1D tracking.

        Args:
        - no: Identifier for the task to process.
        """
        start_time = env.now
        env.process(gen_comp().track1D_en(env, qnmhp, no))
        
    def track_2d(self, no):
        """
        Process 2D tracking.

        Args:
        - no: Identifier for the task to process.
        """
        start_time = env.now
        env.process(gen_comp().track2D_en(env, qnmhp, no))

    def tracing_1d_bounded(self, no):
        """
        Process 1D bounded tracing.

        Args:
        - no: Identifier for the task to process.
        """
        start_time = env.now
        env.process(gen_comp().tracing1D_b_en(env, qnmhp, no))

    def tracing_1d_1w(self, no):
        """
        Process 1D tracing with one way.

        Args:
        - no: Identifier for the task to process.
        """
        start_time = env.now
        env.process(gen_comp().tracing1D_1w_en(env, qnmhp, no))

    def tracing_2d_bounded(self, no):
        """
        Process 2D bounded tracing.

        Args:
        - no: Identifier for the task to process.
        """
        start_time = env.now
        env.process(gen_comp().tracing2D_b_en(env, qnmhp, no))

    def tracing_2d_1w(self, no):
        """
        Process 2D tracing with one way.

        Args:
        - no: Identifier for the task to process.
        """
        start_time = env.now
        env.process(gen_comp().tracing2D_1w_en(env, qnmhp, no))

    def process_entity_data(self, entity_dict):
        """
        Process entities (see or hear) based on their characteristics.

        Args:
        - entity_dict: Dictionary of entities to process.
        """
        if entity_dict==entity_dic_see:
            entity_source='see'
        else:
            entity_source='hear'
        if entity_dict:
            for (r, c, no) in entity_dict:
                if entity_dict[(r, c, no)]!='':
                    entity_value = entity_dict[(r, c, no)] 
                    fa = eval(entity_dict[(r, 2, no)])
                    iat = eval(entity_dict[(r, 3, no)])
                    occur = eval(entity_dict[(r, 4, no)])
                    k_ = no
                    if entity_value == 'Color':
                        env.process(gen_basic().color_en(env, qnmhp, k_, fa=fa, iat=iat, occur=occur,seeorhear=entity_source))
                    elif entity_value == 'Text':
                        env.process(gen_basic().text_en(env, qnmhp, k_, fa=fa, iat=iat, occur=occur,seeorhear=entity_source))

    def print_departure_summary(self):
        """Print departure logs before any final GUI window is closed."""
        print("\nBehavior element departure summary")
        print(utility.format_departure_be_table(utility.departure_BE_N))
        print("\nServer departure summary")
        print(utility.format_departure_server_table(utility.departure_server_N))

    def run(self):
        # Start each new simulation with no previous Choice + Mouse_click target.
        from mouse_click_layout import reset_cursor_positions
        reset_cursor_positions()
        from eye_movement_model import reset_eye_position
        reset_eye_position()
        # Restore the developer-configured Look For layout for every run.
        # Fixed mode keeps positions; optional random mode reshuffles them.
        if any('Look_for' in str(be) for tasks in gui_general.Tasklist_dic.values() for be in tasks):
            utility.reset_visual_search_positions()
        """
        Run the simulation and handle animations and plotting.
        """
        self.entity()
        print('Simulation setup: SIMTIME=%s ms, tasks=%s, visual sources=%d, auditory sources=%d' %
              (SIMTIME, Tasklist_dic, len(entity_dic_see), len(entity_dic_hear)))
        if not Tasklist_dic:
            print('WARNING: No tasks were loaded from the saved configuration.')
        env.run(until=SIMTIME)  # Running time

        if anim == 1:
            import qn_mhp_layout
            layout = qn_mhp_layout.Structure()
            layout.background()
        
        from plot import Plot
        
        """
        Check for tracking or tracing tasks and plot the corresponding graphs.
        """
        track_trace_task = any(any(task in Tasklist_dic[task_no] for task in [[item]]) for task_no in Tasklist_dic for item in tracktrace_name)

        if track_trace_task:
            a = Plot()
            a.RMSE()
            if len(Tasklist_dic) != 1:
                b = Plot()
                b.tick()
        else:
            Plot().tick()

        self.print_departure_summary()

        if anim == 1:
            layout.root.mainloop()



# Initialize reaction if certain tasks are present
if 'Look_at' in task_info_dic.values() or 'Look_for' in task_info_dic.values():
    from display_basic_BE import Reaction_general
    # A standalone Look At must not inherit Look For search targets.
    standalone_look_at = False
    try:
        from gui_general import Tasklist_dic
        standalone_look_at = (len(Tasklist_dic) == 1 and
                              list(Tasklist_dic.values())[0] == [['Look_at']])
    except (ImportError, AttributeError, TypeError):
        pass
    Reaction_general().look_at(standalone=standalone_look_at)
    


# Run the model
ModelRun().run()