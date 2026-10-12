"""Configurable mouse movement time models. All durations are milliseconds."""
import math

FITTS_MODEL = 'shannon'  # 'shannon' (default) or 'legacy_clamped'
FITTS_INTERCEPT_MS = 1.0
FITTS_SLOPE_MS = 2.0

def calculate_mouse_movement_time(distance, target_width, model=None):
    """Return nonnegative mouse movement time; distance and width share units.

    The default Shannon formulation avoids negative times near a target.
    The legacy model is available for comparisons but is clamped at zero.
    Developers should calibrate the intercept, slope and target width.
    """
    distance = float(distance)
    target_width = float(target_width)
    if not math.isfinite(distance) or distance < 0:
        raise ValueError('Mouse distance must be finite and nonnegative')
    if not math.isfinite(target_width) or target_width <= 0:
        raise ValueError('Mouse target width must be finite and positive')
    a, b = FITTS_INTERCEPT_MS, FITTS_SLOPE_MS
    if not all(math.isfinite(v) and v >= 0 for v in (a, b)):
        raise ValueError('Fitts parameters must be finite and nonnegative')
    if distance == 0:
        return 0.0
    mode = model or FITTS_MODEL
    if mode == 'shannon':
        difficulty = math.log2(1.0 + distance / target_width)
    elif mode == 'legacy_clamped':
        difficulty = math.log2(2.0 * distance / target_width)
    else:
        raise ValueError('Unknown Fitts model: ' + str(mode))
    return max(0.0, a + b * difficulty)
