# Change request: respect tie-switch capacity during FLISR restoration

Restoration plans produced by `backend/app/flisr.py::locate_fault` / the restoration planner must
not transfer more load onto a tie switch than its rated capacity. When the tie capacity is not
known the plan must say so instead of restoring. Telemetry for tie capacity arrives from the SCADA
scan every 10 s.
