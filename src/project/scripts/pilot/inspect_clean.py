import sys
import pyxdf
import numpy as np

file_path = sys.argv[1] if len(sys.argv) > 1 else "sub-P007_ses-S001_task-Default_run-001_eeg.xdf"

streams, header = pyxdf.load_xdf(file_path)

print(f"Number of streams: {len(streams)}")

for i, stream in enumerate(streams):
    info = stream['info']
    label = info['name'][0] if 'name' in info else 'Unnamed'
    stype = info['type'][0] if 'type' in info else 'Unknown'
    ts = stream['time_series']
    shape = ts.shape if hasattr(ts, 'shape') else f"list of length {len(ts)}"
    stamps = stream['time_stamps']
    tshape = stamps.shape if hasattr(stamps, 'shape') else f"list of length {len(stamps)}"
    print(f"\nStream {i}: {label}")
    print(f"  Type: {stype}")
    print(f"  time_series shape: {shape}")
    print(f"  time_stamps shape: {tshape}")

eeg = None
pilot = None
for i, stream in enumerate(streams):
    info = stream['info']
    label = info['name'][0] if 'name' in info else 'Unnamed'
    stype = info['type'][0] if 'type' in info else 'Unknown'
    if stype == 'EEG' or 'actiCHamp' in label:
        eeg = stream
        print(f"\nFound EEG stream at index {i}: {label}")
    if 'experiment_lab_pilot' in label.lower():
        data_count = len(stream['time_series']) if 'time_series' in stream else 0
        if pilot is None or data_count > len(pilot['time_series']):
            pilot = stream
        print(f"\nFound experiment_lab_pilot at index {i}: {label} - {data_count} markers")

if eeg:
    ch = eeg['info']['desc'][0]['channels'][0]['channel']
    print(f"\nEEG Channels ({len(ch)}):")
    for idx, c in enumerate(ch):
        print(f"  {idx}: {c['label'][0]}")
    times = eeg['time_stamps']
    print(f"\nEEG: {len(times)} samples @ ~{1/np.mean(np.diff(times)):.0f} Hz, {times[-1]-times[0]:.1f}s")

if pilot:
    events = [str(e[0]) if isinstance(e, (list, np.ndarray)) else str(e) for e in pilot['time_series']]
    unique = sorted(set(events))
    print(f"\nexperiment_lab_pilot markers ({len(events)} total, {len(unique)} unique):")
    print(f"  Unique: {unique}")
    print(f"  First 10: {events[:10]}")
    stamps = pilot['time_stamps']
    print(f"  Duration: {stamps[-1] - stamps[0]:.3f}s")
else:
    print("\nNo experiment_lab_pilot stream found")
