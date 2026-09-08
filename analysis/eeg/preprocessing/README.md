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

Fit the 99%-variance ICA models (already approved as primary). Regenerating
this runner writes a duplicate under `sensitivity/ica_candidate_v1/` and does
**not** replace primary Gold. Compare ICA primary against the archived no-ICA
sensitivity with:

```bash
python analysis/eeg/preprocessing/run_ica_sensitivity.py --skip-model-fit
python analysis/eeg/statistics/compare_ica_sensitivity.py
```

Primary cleaning is `cleaning_policy.json` (`frozen_v5_ica_primary`).
The no-ICA archive lives at
`src/project/logs/xdf/gold/features/sensitivity/no_ica_frozen_v3/`.

Rebuild Dataset A tiles and Dataset B pre/post windows at 2 / 8 / 16 / 32 s
without replacing 4 s primary Gold (one clean per person per policy):

```bash
python analysis/eeg/preprocessing/run_epoch_length_sensitivity.py
```

Read-versus-write positive control (does not replace Dataset A/B Gold):

```bash
python analysis/eeg/preprocessing/run_task_state_positive_control.py
```

Rebuild Dataset A/B on the George nine-site and/or Wang-zone channel
sets (ten global band powers only). Never writes primary Gold:

```bash
python analysis/eeg/preprocessing/run_channel_set_sensitivity.py \
  --channel-set-policy \
  analysis/eeg/preprocessing/gold/features/channel_set_policy_literature_roi.json \
  analysis/eeg/preprocessing/gold/features/channel_set_policy_wang2022.json
```

Default electrode lists stay `channel_set_policy.json` (`current_v1`).
Cleaning remains the full 32-channel montage. See
`.agents/context/data-analysis/eeg/2026-08-24-channel-set-policy.md`.

After generating the separate Silver visual pack and the threshold sensitivity
branch, aggregate all machine-checkable evidence with:

```bash
python analysis/eeg/preprocessing/run_pipeline.py --stage validation
```

Preview without executing:

```bash
python analysis/eeg/preprocessing/run_pipeline.py --dry-run
```

Run the single-file metric and generated-dataset sanity suite:

```bash
python -m unittest analysis/eeg/preprocessing/test_eeg_metrics.py -v
```

The suite uses known synthetic sinusoids to verify band power, regional
features, FAA, Pope and Kislov engagement formulas, artifact rejection, and ad
response arithmetic. When local generated outputs exist, it also checks the
primary and ICA Gold validators plus all ICA models and visual evidence.

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
reports. Filtering figures and ICA exclusions were approved on 2026-08-19;
ICA is the primary Gold branch.

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

### 6. Statistical tables

Dataset B contrasts, then confirmatory Dataset A (\(k=37\)). Do not
run bare `build_condition_contrasts.py` onto `statistics/outputs/` —
that is the whole-window estimand and is refused once \(k=37\) is
marked confirmatory.

```bash
python analysis/eeg/statistics/build_ad_contrasts.py
python analysis/eeg/statistics/run_equal_n_dataset_a.py
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
python src/project/docs/eeg_pipeline/eeg_pipeline.py      # original, kept
python src/project/docs/eeg_pipeline/eeg_pipeline_v2.py   # publication candidate
```

The original five-band figure is unchanged. v2 keeps the lake colours and
adds $X \to Y_A,Y_B \to D$ with shape evolution. The diagram follows the
repository-wide documentation convention rather than living inside the
executable preprocessing package.

## Current gate

Condition and ad response datasets are executable for all 18 laboratory
recordings. Objective cleaning checks pass. Filtering/interpolation figures and
all automatic ICA exclusions were approved on 2026-08-19; ICA is the primary
Gold branch and no-ICA is the mandatory sensitivity. Remaining publication
gates are the read-versus-write positive control, uncontrolled-baseline
interpretation, and behavioral join. Laboratory feedback identifies `Cz` as
online reference and `Fpz` as ground; average rereferencing remains the offline
policy.
