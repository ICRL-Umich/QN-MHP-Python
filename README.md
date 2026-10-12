# QN-MHP Python

A graphical simulation environment for the **Queueing Network Model Human Processor (QN-MHP)**. The model represents human information processing through interacting servers and supports studies of reaction time, task performance, and resource competition. Built with **Python, Tkinter, SimPy, NumPy, and Matplotlib**.

For step-by-step operation, see **QN_MHP Python Work Instruction.pdf**.

## Getting started

Install the project dependencies (including `simpy`, `numpy`, `matplotlib`, and `pyautogui`), then run:

```bash
python run_code.py
```

In the GUI:

1. **Define Task:** choose tasks, behavior elements (BEs), and their execution order.
2. **Define Entity and BE Parameters:** configure stimuli and task-specific settings.
3. **Define Simulation Parameters:** set simulation duration (milliseconds) and animation.
4. **Start:** run the simulation and review logs and plots.

The task editor provides up to **five task slots**. Simultaneous execution depends on the task combination; in particular, tracking/tracing modes have additional restrictions. GUI capacity should not be interpreted as guaranteed support for five concurrent tasks.

## Behavior elements

**Basic BEs:** `See`, `Hear`, `Store_to_WM`, `Choice`, `Judge_identity`, `Judge_relative_location`, `Count`, `Cal_single_digit_num`, `Press_button`, `Mouse_click`, and `Look_at`.

**Compound BEs:** `Look_for`; tracking variants (`Tracking_1D`, `Tracking_1D_1W`, `Tracking_1D_Random`, `Tracking_2D`, `Tracking_2D_Random`, `Tracking_2D_1W`); and tracing variants (`Tracing_1D_Bounded`, `Tracing_1D_1W`, `Tracing_2D_Bounded`, `Tracing_2D_1W`). Compound BEs coordinate basic processing and response behaviors.

A standalone **Look At** task generates visual targets and processes each through **Server W → Server Y → Server Z → Eye Server**. Its reaction window distinguishes the current fixation from the next target. **Look For** performs visual search across a configurable set of targets; it has a separate reaction-window layout.

## Coordinates and eye movement

**Look At and Look For targets are specified in physical screen coordinates (millimeters)**, with origin at the **top-left**, x increasing rightward and y increasing downward. For example, on a 500 × 300 mm screen, the center is **(250 mm, 150 mm)**. The physical screen width, height, and viewing distance are configured in `visual_search_layout.json`.

- **Look At:** `look_at_layout.json` specifies standalone random/fixed targets, combined-task target behavior, and standalone stimulus timing. Standalone Look At generates a new random target by default; combined Look At uses a fixed center target by default.
- **Look For:** `visual_search_layout.json` specifies the search-target positions, labels, and colors in millimeters.
- **Internal eye coordinates:** physical positions are converted to a **0–100 normalized screen range** before eye-movement calculations. The eye model uses physical display geometry and viewing distance to calculate **visual-angle displacement in degrees**, then estimates saccade duration in **milliseconds**. The default timing coefficients are illustrative, not experimentally calibrated.
- **Tracking and tracing:** plot/task coordinates are distinct from physical screen millimeters. Visible plot positions are mapped into normalized screen coordinates for eye movement; plotted coordinates should not be interpreted as measured physical positions without display calibration.
- **Mouse Click:** supports 1D, 2D, and 3D task representations; mouse movement timing is separate from eye movement timing.

## Simulation and outputs

Simulation time and server service times are in **milliseconds**. Entities are scheduled through SimPy and dispatched to the selected BE sequences. Outputs can include console departure summaries, BE/server sojourn-time statistics, optional QN-MHP animations and reaction windows, and RMSE plots for tracking/tracing tasks. Results depend on task setup and whether events complete before the simulation ends.

The software stores GUI configurations and experiment parameters in its active save directory (commonly `backup/`). Use the GUI's save/open controls to preserve experiment settings.

## Project structure

| File | Purpose |
| --- | --- |
| `run_code.py`, `main_process.py` | GUI entry point, simulation setup, entity dispatch |
| `gui_general.py`, `gui_basic_BE.py`, `gui_compound_BE.py` | Task and parameter configuration |
| `entity_basic_BE.py`, `entity_compound_BE.py` | Entity generation |
| `basic_BE.py`, `compound_BE.py`, `model.py` | BE logic and SimPy server resources |
| `eye_movement_model.py`, `look_at_target.py`, `mouse_movement_model.py` | Movement geometry and timing |
| `visual_search_layout.json`, `look_at_layout.json` | Physical display and target configuration |
| `display_basic_BE.py`, `display_compound_BE.py`, `animation_general.py`, `qn_mhp_layout.py` | Reaction windows and animation |
| `plot.py`, `utility.py` | Results, shared utilities, and persistence |

## Extending the model

The software serves as both a QN-MHP demonstration environment and a foundation for custom task simulations. Developers can reuse and combine individual BE implementations, adjust their parameters, and construct workflows beyond those exposed by the GUI.

**Example research application:** Wang, Y., Liu, Y., & Yang, X. J. (2025). *Experimental Investigation and Queuing Network (QN) Modeling of Speed-Accuracy Tradeoff (SAT) and Speed-Confidence Tradeoff (SCT) in Multi-Task Human-Robot Collaboration (HRC).* Proceedings of the Human Factors and Ergonomics Society Annual Meeting, 69(1), 541–547.
