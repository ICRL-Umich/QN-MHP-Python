"""Developer-configurable Look At target selection (physical millimeters).

The first saccade starts at the screen center by default, configured separately
in eye_movement_model.py. Later saccades start at the last completed fixation.

Standalone Look At: generate a new random target for each entity by default.
Combined Look At + See/Choice/etc.: target the screen center by default.
Change look_at_layout.json to override either behavior. Positions are stored
internally as normalized 0..100 coordinates for compatibility with the Eye Server.
"""
import json
import random
from pathlib import Path
from eye_movement_model import SCREEN_WIDTH_MM, SCREEN_HEIGHT_MM


def target_for_task(is_standalone):
    config = json.loads(Path(__file__).with_name('look_at_layout.json').read_text(encoding='utf-8'))
    prefix = 'standalone' if is_standalone else 'combined'
    mode = config[prefix + '_target_mode']
    if mode == 'random':
        x_mm = random.uniform(0, SCREEN_WIDTH_MM)
        y_mm = random.uniform(0, SCREEN_HEIGHT_MM)
    elif mode == 'fixed':
        position = config[prefix + '_fixed_target_mm'] if is_standalone else config[prefix + '_target_mm']
        x_mm, y_mm = float(position['x_mm']), float(position['y_mm'])
    else:
        raise ValueError('Unsupported Look At target mode: ' + str(mode))
    if not (0 <= x_mm <= SCREEN_WIDTH_MM and 0 <= y_mm <= SCREEN_HEIGHT_MM):
        raise ValueError('Look At target is outside configured physical screen')
    return (x_mm / SCREEN_WIDTH_MM * 100, y_mm / SCREEN_HEIGHT_MM * 100)
