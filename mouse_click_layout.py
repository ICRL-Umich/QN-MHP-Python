"""Choice-dependent mouse-click geometry and cursor starting-position policy.

Developer guide
---------------
Change ``button_geometry`` to customize button centers and widths. The GUI
and movement-time model both use this function, so targets stay aligned.

Available cursor start policies (CURSOR_START_MODE):
  "previous_target" (DEFAULT): Start at the last completed click target.
  "fixed": Start every trial at FIXED_START_POSITION.
  "random": Start each trial at a random location within the canvas.

For "previous_target", the FIRST click begins at the center of the canvas.
State is tracked independently for each task. It is updated after the mouse
movement completes, not when an entity is generated.

Coordinates and widths are measured in canvas pixels. Fitts' law coefficients
remain those of the original Mouse_click model; they are not calibrated to
pixels, so predicted movement times should not be interpreted as validated
physical movement times without fitting a suitable scale and coefficients.

Standalone Mouse_click intentionally keeps its original independent 1D/2D/3D
random-coordinate behavior; these settings apply only to Choice + Mouse_click.
"""
import random

CURSOR_START_MODE = "previous_target"  # "previous_target", "fixed", "random"
FIXED_START_POSITION = None  # None = canvas center, or (x, y) in pixels
BUTTON_WIDTH = 120.0
BUTTON_HEIGHT = 36.0

# Task-specific cursor locations for Choice + Mouse_click.
_last_completed_target = {}


def reset_cursor_positions():
    """Reset all Choice + Mouse_click cursor positions for a new simulation."""
    _last_completed_target.clear()


def button_geometry(index, count, canvas_width, canvas_height, dimension=1):
    """Return the visible target's (x, y, width, height), in canvas pixels.

    Choice + Mouse_click layouts:
      1D: horizontal targets; movement distance uses only x.
      2D: a centered two-column grid; distance uses x and y.
      3D: the same projected grid with a visible z label; all targets
          currently have z=0 because the Tk canvas is two-dimensional.

    Choice + Press_button always uses the legacy horizontal layout (1D).
    To change target positions, edit this function; both the canvas and
    the Fitts' law distance calculation call it.
    """
    if count < 1 or not 0 <= index < count:
        raise ValueError("Invalid button index or count")
    if dimension not in (1, 2, 3):
        raise ValueError("Mouse-click dimension must be 1, 2, or 3")
    if dimension == 1:
        # Fit every button within the available canvas width.
        spacing = canvas_width / (count + 1)
        width = min(BUTTON_WIDTH, spacing * 0.78)
        return (spacing * (index + 1), canvas_height / 2, width, BUTTON_HEIGHT)
    columns = min(2, count)
    rows = (count + columns - 1) // columns
    column = index % columns
    row = index // columns
    spacing_x = canvas_width / (columns + 1)
    # Leave room for the title and optional 3D coordinate labels.
    top, bottom = 65.0, max(100.0, canvas_height - 35.0)
    spacing_y = (bottom - top) / max(rows - 1, 1)
    cy = (top + bottom) / 2 if rows == 1 else top + row * spacing_y
    return (spacing_x * (column + 1), cy,
            min(BUTTON_WIDTH, spacing_x * 0.78), BUTTON_HEIGHT)


def button_depth(index, count):
    """Projected 3D button depth, in pixels; default is a flat screen.

    Developers can assign individual z coordinates here for a true 3D
    target layout. The mouse movement model must use the same depth.
    """
    return 0.0


def get_start(task, canvas_width, canvas_height):
    """Get the cursor position at the start of a click."""
    center = (canvas_width / 2.0, canvas_height / 2.0)
    if CURSOR_START_MODE == "previous_target":
        return _last_completed_target.get(task, center)
    if CURSOR_START_MODE == "fixed":
        return FIXED_START_POSITION if FIXED_START_POSITION is not None else center
    if CURSOR_START_MODE == "random":
        return (random.uniform(0, canvas_width), random.uniform(0, canvas_height))
    raise ValueError(f"Unsupported CURSOR_START_MODE: {CURSOR_START_MODE}")


def complete_click(task, target):
    """Record the completed click location for the next trial."""
    _last_completed_target[task] = tuple(target)
