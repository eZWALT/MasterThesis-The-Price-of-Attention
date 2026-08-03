# EEG preprocessing pipeline

This folder is the single entry point for transforming laboratory XDF
recordings into validated, analysis-ready EEG windows and features.

Data remains under `src/project/logs/xdf/`:

- Bronze: immutable source XDF files and hash inventory;
- Silver: canonical markers, conversion evidence, cleaning and quality control;
- Gold: eligible windows and future feature tables.

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
```

`silver/signal/cleaning_policy.json` remains a candidate policy until visual
artifact validation and epoch-retention thresholds are frozen.

### 4. Window contracts

```bash
python analysis/eeg/preprocessing/gold/windows/build_condition_windows.py
python analysis/eeg/preprocessing/gold/windows/build_ad_visibility.py
```

### 5. Pipeline diagram

```bash
python src/project/docs/eeg_pipeline/eeg_pipeline.py
```

The diagram follows the repository-wide documentation convention rather than
living inside the executable preprocessing package.

## Current gate

Recording identity, marker recovery, XDF-to-MNE conversion, and timing-window
construction are validated for the 18 laboratory recordings. Final Gold EEG
features remain blocked on Silver visual cleaning validation and artifact/epoch
retention rules.
