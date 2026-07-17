import pyxdf
import numpy as np

streams, _ = pyxdf.load_xdf("sub-P007_ses-S001_task-Default_run-001_eeg.xdf")

for i, s in enumerate(streams):
    label = s["info"]["name"][0]
    if "experiment_lab_pilot" in label.lower() and len(s["time_series"]) > 0:
        ts = s["time_series"]
        stamps = s["time_stamps"]
        t0 = stamps[0]
        print(f"Stream {i}: {label} ({len(ts)} markers)")
        for j in range(len(ts)):
            val = ts[j][0] if isinstance(ts[j], (list, np.ndarray)) else ts[j]
            offset = stamps[j] - t0
            print(f"  [{j:2d}] +{offset:7.3f}s  {val}")
