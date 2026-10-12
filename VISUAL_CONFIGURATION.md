# Visual attention configuration (physical millimeters)

## Look For — fixed physical positions

Edit `visual_search_layout.json` before starting the simulator.

- `screen.width_mm`, `screen.height_mm`: **physical usable display area** in millimeters.
- `screen.viewing_distance_mm`: perpendicular distance from participant's eyes to the screen plane, in millimeters.
- `targets`: add, remove, or change `label`, `color`, `x_mm`, and `y_mm`.
- Coordinates are measured from the **top-left** of the usable screen area: X increases rightward, Y downward. Every target must be within screen bounds.
- `position_mode`: `fixed` (default); `random` is optional.

Example for a 500 x 300 mm screen and 600 mm viewing distance:

```json
{
  "coordinate_system": "millimeters",
  "position_mode": "fixed",
  "screen": {"width_mm": 500, "height_mm": 300, "viewing_distance_mm": 600},
  "targets": [
    {"label": "a", "color": "red", "x_mm": 100, "y_mm": 45},
    {"label": "b", "color": "green", "x_mm": 375, "y_mm": 105}
  ]
}
```

The legacy Look For renderer and Eye Server use normalized coordinates internally;
the configuration loader converts the physical millimeter positions to that
coordinate system. The **same physical screen dimensions and viewing distance**
are applied to the Eye Server's visual-angle calculation. Consequently,
changing screen size while holding a target's physical position fixed changes
its normalized display position but not the intended physical location.

The first Look At / Look For fixation defaults to the physical screen center.
The Eye Server uses the previous fixation for subsequent eye movements. Change
`INITIAL_FIXATION_MODE` and `INITIAL_FIXED_POSITION` in `eye_movement_model.py`
if required. `INITIAL_FIXED_POSITION` remains normalized (0..100).

## Look At — physical target coordinates

The Look At dialog now accepts **X and Y in millimeters** from the top-left
of the same physical screen configured in `visual_search_layout.json`.
X must be within `0..screen.width_mm`; Y within `0..screen.height_mm`.

The dialog shows the current screen dimensions and viewing distance.
The same geometry applies to both Look At and Look For. To change it,
edit the `screen` object in `visual_search_layout.json` and restart the app.

Existing simulation code and drawing routines still use normalized positions
internally. The dialog converts millimeters to normalized coordinates when
saving, and converts back to millimeters when reopening. Older saved projects
remain readable, but if the physical screen geometry changes, their saved
normalized targets will map to different physical millimeter positions.

The first fixation defaults to screen center; subsequent saccades begin at
previous fixation. Developers may change `INITIAL_FIXATION_MODE` in
`eye_movement_model.py` (`center`, `fixed`, or `random`).

## Important

Configure the usable screen area and viewing distance for the actual experiment.
The sample dimensions and saccade timing coefficients are placeholders, not
validated participant-specific measurements. Restart the application after
editing target labels or counts to refresh GUI choices.
