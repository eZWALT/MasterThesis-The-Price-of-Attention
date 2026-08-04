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
python analysis/eeg/preprocessing/silver/signal/fit_ica_cohort.py
```

The current acquisition facts, laboratory-reported `Cz` reference/`Fpz` ground,
and XDF export caveat are recorded in `acquisition_contract.md`. Signal-quality
findings, recording-specific channel repairs, ICA plan, and the frozen
condition-epoch artifact policy are documented in
`signal_quality_and_cleaning.md`.

The ICA implementation is deliberately separate from the frozen no-ICA
primary branch:

- `cleaning_policy_ica_candidate_v1.json` fixes the reproducible candidate
  parameters;
- `fit_ica_cohort.py` fits one 99%-variance model per eligible participant;
- `ica_cleaning.py` saves the model, component-level evidence, topographies,
  and source/proxy time courses;
- `build_ica_review_report.py` combines all participant evidence into
  `src/project/logs/xdf/silver/ica/candidate_v1/ica_review.html`;
- `run_ica_sensitivity.py` regenerates Gold features and statistics under ICA
  without replacing primary outputs.

Automated exclusion requires both strong `Fp1/Fp2` source correlation and a
frontally dominant topography, with at most three excluded components. This is
candidate automation, not final human approval. Every generated component pack
still requires visual signoff.
