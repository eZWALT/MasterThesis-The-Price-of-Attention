# EEG preprocessing pipeline

This folder is the single entry point for transforming laboratory XDF
recordings into validated, analysis-ready EEG windows and features.

Data remains under `src/project/logs/xdf/`:

- Bronze: immutable source XDF files and hash inventory;
- Silver: canonical markers, conversion evidence, cleaning and quality control;
- Gold: eligible windows and analysis-shaped feature tables.

## Run the current pipeline

From the repository root:

```bash
python analysis/eeg/preprocessing/run_pipeline.py
```

Run the archived 1,000 µV `frozen_v1` and 1,500 µV `frozen_v2` sensitivity
analyses without replacing the 1,050 µV `frozen_v3` primary outputs:

```bash
python analysis/eeg/preprocessing/run_threshold_sensitivity.py
```

Sensitivity features and statistics are written under versioned
`sensitivity/frozen_v1/` and `sensitivity/frozen_v2/` directories.

Fit the candidate 99%-variance ICA models, regenerate all current features, and
compare participant-level conclusions against the no-ICA primary branch with:

```bash
python analysis/eeg/preprocessing/run_ica_sensitivity.py
```

The command writes only to versioned `ica/candidate_v1/` and
`sensitivity/ica_candidate_v1/` directories. Reuse already fitted models with
`--skip-model-fit`. ICA remains a sensitivity branch until its topographies and
source/proxy traces receive human signoff.

After generating the separate Silver visual pack and the threshold sensitivity
branch, aggregate all machine-checkable evidence with:

```bash
python analysis/eeg/preprocessing/run_pipeline.py --stage validation
```

Preview without executing:

```bash
python analysis/eeg/preprocessing/run_pipeline.py --dry-run
```

Run one stage:

```bash
python analysis/eeg/preprocessing/run_pipeline.py --stage silver-markers
```

The runner is fail-fast and never moves raw XDF files. New recordings must be
landed separately with the ingestion command and an explicit `--apply`.

## Pipeline order

Run commands from the repository root.

### 1. Ingestion and recording inventory

```bash
python analysis/eeg/preprocessing/ingestion/organize_xdf_lake.py
python analysis/eeg/preprocessing/bronze/manifests/build_recording_manifest.py
```

Use `--apply` on the organizer only when landing new files.

### 2. Marker audit and canonical timeline

```bash
python analysis/eeg/preprocessing/silver/markers/audit_marker_anomalies.py
python analysis/eeg/preprocessing/silver/markers/build_canonical_markers.py
python analysis/eeg/preprocessing/silver/markers/validate_marker_reconstruction.py
python analysis/eeg/preprocessing/silver/markers/verify_recovery_invariants.py
```

### 3. Signal conversion and quality control

```bash
python analysis/eeg/preprocessing/silver/signal/audit_xdf_mne.py
python analysis/eeg/preprocessing/silver/signal/audit_signal_quality.py
python analysis/eeg/preprocessing/silver/signal/validate_cleaning_visual.py
python analysis/eeg/preprocessing/silver/signal/fit_ica_cohort.py
```

`silver/signal/cleaning_policy.json` freezes the artifact and retention policy.
The visual command generates filtering and interpolation figures plus
machine-checkable evidence. ICA fitting generates per-participant component
selection plots, topographies, source/proxy traces, and machine-readable
reports. Human visual signoff remains required before publication.

### 4. Window contracts

```bash
python analysis/eeg/preprocessing/gold/windows/build_condition_windows.py
python analysis/eeg/preprocessing/gold/windows/build_ad_visibility.py
python analysis/eeg/preprocessing/gold/windows/build_ad_windows.py
```

### 5. Spectral feature datasets

```bash
python analysis/eeg/preprocessing/gold/features/build_condition_features.py
python analysis/eeg/preprocessing/gold/features/validate_condition_features.py
python analysis/eeg/preprocessing/gold/features/build_ad_features.py
python analysis/eeg/preprocessing/gold/features/validate_ad_features.py
```

This creates condition and ad response features, including Fz theta, posterior
alpha, FAA, band power, engagement, provenance, and retained-signal evidence.

### 6. Initial statistical tables

```bash
python analysis/eeg/statistics/build_condition_contrasts.py
python analysis/eeg/statistics/build_ad_contrasts.py
```

### 7. Publication analysis workspace

```bash
python analysis/eeg/analysis/run_publication_analysis.py
python analysis/eeg/analysis/execute_notebook.py
```

This generates the analysis-facing tables, publication figures, twenty-gate
report, and executable notebook without mutating preprocessing outputs.

### 8. Pipeline diagram

```bash
python src/project/docs/eeg_pipeline/eeg_pipeline.py
```

The diagram follows the repository-wide documentation convention rather than
living inside the executable preprocessing package.

## Current gate

Condition and ad response datasets are executable for all 18 laboratory
recordings. Objective cleaning checks pass. The 99%-variance ICA branch is
implemented and reproducible; automated component choices still require human
visual signoff before it can replace the no-ICA primary branch. Other remaining
publication gates are interpretation decisions for the uncontrolled baseline
and estimated inline onset. Laboratory feedback identifies `Cz` as online
reference and `Fpz` as ground; average rereferencing remains the offline policy.
