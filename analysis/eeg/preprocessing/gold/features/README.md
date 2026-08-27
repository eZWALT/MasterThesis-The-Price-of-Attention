# Condition-level EEG features

`build_condition_features.py` creates the first analysis-shaped EEG tables from
eligible baseline and sustained condition windows.

## Channel sets

Electrode lists for the 16 spectral formulas live in
`channel_set_policy.json` (`current_v1`, primary Gold). Cleaning still
uses the full montage. `channel_set_policy_literature_roi.json` is filled
(`literature_roi_v0`, George 2025 nine-site). 
`channel_set_policy_wang2022.json` is the Wang-zone sensitivity
(`wang2022_v0`). Both are hardcoded; the JSON must match.
They change the ten global band powers only.

```bash
python analysis/eeg/preprocessing/run_channel_set_sensitivity.py \
  --channel-set-policy \
  analysis/eeg/preprocessing/gold/features/channel_set_policy_literature_roi.json \
  analysis/eeg/preprocessing/gold/features/channel_set_policy_wang2022.json
```

The builders also accept `--channel-set-policy`. Non-primary policies
are rerouted under `gold/features/sensitivity/channel_sets/<version>/`
and cannot overwrite primary Gold. See
`.agents/context/data-analysis/eeg/2026-08-24-channel-set-policy.md`.

## Current contract

- Clean continuous EEG with the candidate Silver policy.
- Do not apply ICA.
- Split every eligible window into non-overlapping 4-second epochs.
- Estimate Welch power in delta, theta, alpha, beta, and gamma bands.
- Extract Fz theta and posterior alpha over `O1/Oz/O2/P3/Pz/P4`.
- Calculate log FAA as `ln(alpha F4) - ln(alpha F3)`.
- Calculate three exploratory engagement measures:
  - global Pope ratio: `beta / (alpha + theta)`;
  - frontocentral Pope ratio over `F3/F4/Fz/FC1/FC2/C3/C4/Cz`;
  - Kislov advertising ratio: central 16-24 Hz beta divided by central
    8-12 Hz alpha over `Cz/Pz/P3/P4`.
- Reject epochs above 1,050 µV peak-to-peak or containing a near-flat channel.
- Require at least 80% and five retained epochs per window.
- Aggregate retained-epoch medians and IQRs per participant and window.
- Calculate within-participant differences from the recorded baseline.

The baseline is a primary operational comparison because it was collected
before the task, but its eye state was not controlled. It is labelled
`uncontrolled_mostly_open`; every confirmatory analysis must include a
sensitivity model that excludes baseline-derived contrasts.

## Run

From the repository root:

```bash
python analysis/eeg/preprocessing/gold/features/build_condition_features.py
python analysis/eeg/preprocessing/gold/features/validate_condition_features.py
python analysis/eeg/preprocessing/gold/features/build_ad_features.py
python analysis/eeg/preprocessing/gold/features/validate_ad_features.py
python analysis/eeg/preprocessing/gold/features/validate_engagement_features.py
```

To test selected recordings:

```bash
python analysis/eeg/preprocessing/gold/features/build_condition_features.py \
  --subjects lab_subject_1 lab_subject_8
```

Outputs:

- `src/project/logs/xdf/gold/features/condition_epoch_features.csv`
- `src/project/logs/xdf/gold/features/condition_features.csv`
- `src/project/logs/xdf/gold/features/condition_feature_validation.json`
- `src/project/logs/xdf/gold/features/ad_epoch_features.csv`
- `src/project/logs/xdf/gold/features/ad_response_features.csv`
- `src/project/logs/xdf/gold/features/ad_feature_validation.json`
- `src/project/logs/xdf/gold/features/engagement_feature_validation.json`

## Dataset status

The epoch table preserves retained and rejected rows with explicit rejection
reasons. The condition table contains retained-epoch summaries and eligibility
fields. `validate_condition_features.py` must report
`dataset_status=analysis_ready_condition_v1` before analysis.

The 1,050 µV `frozen_v3` rule is a post-review, participant-retention-driven
gross-artifact boundary selected just above Subject 14's 1,042.56 µV epoch. It
is not a universal literature threshold. The 1,000 µV `frozen_v1` and 1,500 µV
`frozen_v2` policies remain mandatory stricter and permissive sensitivities.
Median aggregation and sensitivity analyses remain required. Visual validation
of filtering and interpolation is still a separate publication-readiness gate.

The implementation is native to this repository. `cognitive-mllm` informed the
high-level choice of Welch spectral estimation but is not imported, copied, or
required at runtime.
