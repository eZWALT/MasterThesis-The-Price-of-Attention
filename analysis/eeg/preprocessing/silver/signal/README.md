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

The ICA implementation is the approved primary cleaning branch as of
2026-08-19. The fitted models remain under `ica/candidate_v1/` so they can be
reused without refitting:

- `cleaning_policy.json` (`frozen_v5_ica_primary`) enables ICA for Gold;
- `cleaning_policy_ica_candidate_v1.json` is the model-fit recipe;
- `cleaning_policy_no_ica_sensitivity.json` rebuilds the mandatory no-ICA
  archive;
- `fit_ica_cohort.py` fits one 99%-variance model per eligible participant;
- `ica_cleaning.py` saves the model, component-level evidence, topographies,
  and source/proxy time courses;
- `build_ica_review_report.py` combines all participant evidence into
  `src/project/logs/xdf/silver/ica/candidate_v1/ica_review.html`.

Automated exclusion requires both strong `Fp1/Fp2` source correlation and a
frontally dominant topography, with at most three excluded components. Human
review on 2026-08-19 approved all automatic exclusions.
