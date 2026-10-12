"""Eye movement timing and position configuration for Look_at / Look_for.

Coordinates are normalized visual-field positions (0..100), NOT degrees.
Physical display dimensions and viewing distance convert them to visual angles.
All durations are milliseconds. Example coefficients are NOT calibrated values.

Developers can select the initial fixation mode:
    center: start at the center of the display (default)
    fixed: start at INITIAL_FIXED_POSITION
    random: choose a random position for the first fixation
Subsequent saccades always begin at the most recent completed fixation.

The fixation is shared by all tasks because the model has one Eye Server.
The position is read/updated while the Eye Server resource is held.
"""
import math
import random
import json
from pathlib import Path

INITIAL_FIXATION_MODE = 'center'  # 'center', 'fixed', or 'random'
INITIAL_FIXED_POSITION = (50.0, 50.0)
# Display and observer geometry in millimeters. Set to the actual setup.
SCREEN_WIDTH_MM = 500.0
SCREEN_HEIGHT_MM = 300.0
VIEWING_DISTANCE_MM = 600.0

# Example saccadic main-sequence approximation; calibrate before research use.
SACCADE_INTERCEPT_MS = 20.0
SACCADE_SLOPE_MS_PER_DEG = 2.0
SACCADE_NOISE_SD_MS = 5.0
MIN_SACCADE_AMPLITUDE_DEG = 0.1

def load_screen_geometry():
    """Read shared physical screen geometry for Look At and Look For."""
    global SCREEN_WIDTH_MM, SCREEN_HEIGHT_MM, VIEWING_DISTANCE_MM
    config = Path(__file__).with_name('visual_search_layout.json')
    if config.exists():
        screen = json.loads(config.read_text(encoding='utf-8'))['screen']
        width, height, distance = (float(screen[key]) for key in
                                   ('width_mm', 'height_mm', 'viewing_distance_mm'))
        if not all(math.isfinite(v) and v > 0 for v in (width, height, distance)):
            raise ValueError('Screen geometry must contain positive finite millimeters')
        SCREEN_WIDTH_MM, SCREEN_HEIGHT_MM, VIEWING_DISTANCE_MM = width, height, distance


load_screen_geometry()

_current_fixation = None

def reset_eye_position():
    global _current_fixation
    if INITIAL_FIXATION_MODE == 'center':
        _current_fixation = (50.0, 50.0)
    elif INITIAL_FIXATION_MODE == 'fixed':
        _current_fixation = tuple(map(float, INITIAL_FIXED_POSITION))
    elif INITIAL_FIXATION_MODE == 'random':
        _current_fixation = (random.uniform(0, 100), random.uniform(0, 100))
    else:
        raise ValueError('Invalid INITIAL_FIXATION_MODE: ' + str(INITIAL_FIXATION_MODE))
    return _current_fixation

def get_eye_position():
    return _current_fixation if _current_fixation is not None else reset_eye_position()

def _direction(position):
    # The eye is located in front of the center of a planar display.
    x, y = map(float, position)
    if not (0 <= x <= 100 and 0 <= y <= 100):
        raise ValueError('Eye target must be within the normalized 0..100 visual field')
    if min(SCREEN_WIDTH_MM, SCREEN_HEIGHT_MM, VIEWING_DISTANCE_MM) <= 0:
        raise ValueError('Display dimensions and viewing distance must be positive')
    return ((x / 100 - .5) * SCREEN_WIDTH_MM,
            (y / 100 - .5) * SCREEN_HEIGHT_MM,
            VIEWING_DISTANCE_MM)

def angular_distance_deg(start, target):
    """Angle between two sight lines, including off-center positions."""
    a, b = _direction(start), _direction(target)
    dot = sum(x*y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x*x for x in a))
    norm_b = math.sqrt(sum(x*x for x in b))
    cosine = max(-1.0, min(1.0, dot / (norm_a * norm_b)))
    return math.degrees(math.acos(cosine))

def calculate_saccade_duration(amplitude_deg):
    """Movement duration (ms) only; no initiation latency.

    Developers may replace this empirical model or tune the coefficients above.
    The default coefficients are illustrative, not calibrated.
    """
    amplitude_deg = float(amplitude_deg)
    if not math.isfinite(amplitude_deg) or amplitude_deg < 0:
        raise ValueError('Saccade amplitude must be a finite nonnegative angle')
    if amplitude_deg < MIN_SACCADE_AMPLITUDE_DEG:
        return 0.0
    return max(0.0, SACCADE_INTERCEPT_MS +
               SACCADE_SLOPE_MS_PER_DEG * amplitude_deg +
               random.gauss(0, SACCADE_NOISE_SD_MS))


def prepare_saccade(target):
    """Calculate the duration without updating fixation (call under Eye lock)."""
    start = get_eye_position()
    target = tuple(map(float, target))
    amplitude = angular_distance_deg(start, target)
    duration = calculate_saccade_duration(amplitude)
    return start, target, amplitude, duration

def complete_saccade(target):
    global _current_fixation
    _current_fixation = tuple(map(float, target))


def set_visual_gaze_target(attribute, display, x, y=None):
    """Map the currently visible plot position to normalized screen coordinates.

    Plot coordinates are task units, NOT physical mm. The plot axes represent
    the configured physical display; its visible x/y limits are mapped onto
    SCREEN_WIDTH_MM / SCREEN_HEIGHT_MM. For scrolling tasks, use the current
    viewport rather than global task coordinates. Developers should calibrate
    plot-area dimensions if the graph does not occupy the entire screen.
    """
    import math
    ax = display.ax
    xmin, xmax = map(float, ax.get_xlim())
    ymin, ymax = map(float, ax.get_ylim())
    if y is None:
        # One-dimensional tasks place their gaze on the horizontal midline.
        y = (ymin + ymax) / 2
    x, y = float(x), float(y)
    if not all(map(math.isfinite, (x, y, xmin, xmax, ymin, ymax))):
        raise ValueError('Tracking/Tracing gaze coordinate must be finite')
    if xmax <= xmin or ymax <= ymin:
        raise ValueError('Tracking/Tracing viewport has invalid axis limits')
    # Targets outside the visible plot cannot be fixated on the screen.
    nx = max(0.0, min(100.0, 100.0 * (x - xmin) / (xmax - xmin)))
    ny = max(0.0, min(100.0, 100.0 * (y - ymin) / (ymax - ymin)))
    attribute['_visual_gaze_target'] = (nx, ny)
    return attribute['_visual_gaze_target']


def prepare_eye_motion(attribute):
    """All eye movements use the same visual-angle-based duration model."""
    target = attribute.get('_visual_gaze_target', attribute.get('eye_loc'))
    if target is None:
        raise ValueError('Look At has no eye target')
    if len(target) != 2:
        raise ValueError('Look At requires a 2D gaze target; received %d coordinates. '
                         'Check entity generation and task-specific eye_loc.' % len(target))
    return prepare_saccade(target)
