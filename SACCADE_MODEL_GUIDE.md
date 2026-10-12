# Unified eye-movement model

All Look At, Look For, Tracking, and Tracing calls to `Look_at` use `eye_movement_model.calculate_saccade_duration(amplitude_deg)`.

- The configurable coefficients are in `eye_movement_model.py`. They are **illustrative**, not empirically calibrated.
- Eye movement is measured in visual degrees computed using screen dimensions and viewing distance from `visual_search_layout.json`.
- Tracking/Tracing retain their original `eye_loc` data for motor/control logic. Immediately before each `Look_at`, `set_visual_gaze_target` converts the visible plot position to normalized screen coordinates in a separate `_visual_gaze_target` field.
- The plot viewport is assumed to occupy the configured physical display. If a plot occupies only part of a screen, calibrate the plot-to-display mapping for accurate visual angles. Scrolling plots use the current axis limits.
- The first fixation defaults to screen center. Subsequent movements use the last completed fixation, shared across tasks.
- The duration models movement time only; do not interpret it as full stimulus-to-response latency.
