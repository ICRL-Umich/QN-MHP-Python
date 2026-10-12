# Look At configuration

- **Standalone Look At**: each generated stimulus has a random screen target.
- **Look At combined with See/Choice/Press_button**: each stimulus is located at the screen center by default. The stimulus color/text is preserved for Choice.
- Set `standalone_target_mode` or `combined_target_mode` in `look_at_layout.json` to `fixed` or `random`. For fixed mode, edit the corresponding millimeter coordinates.
- Screen width, height and viewing distance are defined in `visual_search_layout.json` (`screen`).
- Initial fixation is screen center by default; change `INITIAL_FIXATION_MODE` in `eye_movement_model.py` to customize it. Subsequent fixations use the previous gaze position.
- Look At targets are internally normalized to 0..100 for existing Eye Server compatibility; GUI and configuration coordinates are real millimeters.
- This change does not modify the saccade timing coefficients or Look For targets.


## Standalone Look At stimulus generation

A standalone `Look_at` task automatically generates visual entities. Without
this source, the simulation would complete with no BE or Server departures.
Configure `standalone_stimulus` in `look_at_layout.json`:

- `first_arrival_ms`: time of the first entity (default 0).
- `interval_ms`: time between entities (default 500).
- `occurrences`: number of entities (default 5).

Each entity uses the configured standalone target mode (random by default).
The first fixation starts at the configured eye position (screen center by
default); later eye movements start at the last completed fixation. The Look At
BE retains W, Y and Z Server processing before Eye Server saccade duration.
For other task combinations, the original See/Hear or compound-task entity
sources remain responsible for triggering execution.
