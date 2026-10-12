# Look At and Look For: amplitude-based eye movement timing

- The first Look At starts at the screen center (50, 50). Later movements start at the previous completed fixation, including movements initiated by Look For.
- To change the initial mode to `fixed` or `random`, edit `INITIAL_FIXATION_MODE` in `eye_movement_model.py`. To set a custom first fixation, choose `fixed` and edit `INITIAL_FIXED_POSITION`.
- The Look At GUI still specifies a target position in normalized 0–100 coordinates. The window dimensions and viewing distance in `eye_movement_model.py` convert two positions to the angle between the sight lines.
- Eye Server movement duration (ms) = max(0, 20 + 2 × amplitude_in_degrees + Gaussian noise with SD 5 ms). If the amplitude is less than 0.1°, duration is 0. These are illustrative coefficients **not validated experimental parameters**. W/Y/Z processing is unchanged.
- Look For creates random screen positions for its configured targets at the start of every simulation, retaining their labels and colors. Positions stay fixed during that run; the existing Look For search and judgment logic is unchanged. The target list is still configured in `visual_search_layout.json`.
- The Eye Server resource serializes movements across tasks; the shared fixation position is read and updated while that resource is held.
- The model predicts **saccade duration**, not stimulus-to-saccade latency or full visual search reaction time. Other BE times remain in the simulation. Use calibrated parameters before drawing empirical conclusions.
- Check terminal output for each movement's start, target, angular amplitude, and duration.
