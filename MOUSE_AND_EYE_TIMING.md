# Mouse and Eye Timing

Mouse Click uses `mouse_movement_model.calculate_mouse_movement_time()` for all branches, including 1D/2D tracking/tracing and independent/Choice mouse click. Default: Shannon Fitts law `MT = a + b*log2(1 + A/W)` for A>0; A=0 returns 0. Distances and widths must share units. Parameters and optional clamped legacy model are in `mouse_movement_model.py`.

Look At retains the existing W -> Y -> Z server processing (each with its own `mpt` delay), then requests the Eye Server and waits for the saccade movement duration from `eye_movement_model.prepare_eye_motion()`. Hence Look At time includes the original server delays, resource waiting, and the new movement time. Eye movement duration does not replace W/Y/Z time. The same order applies to animation and non-animation paths.

All timing coefficients are provisional assumptions, not calibrated empirical values.
