# XDF to MNE boundary

This package converts immutable Bronze XDF recordings into in-memory MNE objects
with Silver canonical markers.

The adapter performs only representation changes:

- selects the longest EEG stream;
- validates channel metadata and monotonic timestamps;
- converts source microvolts to the volts required by MNE;
- applies an explicit montage;
- attaches only timing-eligible canonical markers.

It does not filter, rereference, interpolate, run ICA, or overwrite an XDF.
Those decisions belong to the separately frozen cleaning policy.

Run the cohort conversion audit from the repository root:

```bash
python analysis/eeg/preprocessing/silver/signal/audit_xdf_mne.py
python analysis/eeg/preprocessing/silver/signal/audit_signal_quality.py
```

The current acquisition facts, laboratory-reported `Cz` reference/`Fpz` ground,
and XDF export caveat are recorded in `acquisition_contract.md`. Signal-quality
findings, recording-specific channel repairs, ICA plan, and the frozen
condition-epoch artifact policy are documented in
`signal_quality_and_cleaning.md`.
