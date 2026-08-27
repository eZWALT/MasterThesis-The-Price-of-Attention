# Channel-set policy

Date: 24 August 2026. Wired through Dataset A, Dataset B, task-state, and
contrasts. Literature ROI lists are filled in `literature_roi_v0`.

## What this is

A JSON policy for *which electrodes enter each of the 16 Gold spectral
formulas*. Cleaning does not change. Average reference, interpolation,
and ICA stay on the full 32-channel montage. Do not subset channels
before `clean_recording()`.

Default policy `current_v1` is the confirmatory contract already in
primary Gold:

- global δ θ α β γ = mean of all recorded channels;
- Fz theta and posterior alpha as before;
- FAA / Pope / Kislov as before;
- epoch rejection still looks at every channel.

`channel_set_policy_literature_roi.json` is filled (`literature_roi_v0`,
`status=ready`). The sensors are the nine sites George and Gulia 2025
recorded, hardcoded as `channel_sets.GEORGE2025_NINE`; loading refuses
drift. Same nine for every global band. Derived measures stay on
`current_v1`. Provenance:
`2026-08-24-literature-roi-from-angela.md`.

`channel_set_policy_wang2022.json` is a second sensitivity
(`wang2022_v0`). It maps Wang & Mengoni 2022 §2.2 zone prose onto this
cap. Wang does not publish those electrode tuples. Lock:
`2026-08-25-wang-zone-sensitivity.md`. Appendix:
`sec:app-eeg-channel-sets`. Do not treat either branch as a second
confirmatory family.

## How to run

The lists are filled. Rebuild with:

```bash
python analysis/eeg/preprocessing/run_channel_set_sensitivity.py \
  --channel-set-policy \
  analysis/eeg/preprocessing/gold/features/channel_set_policy_literature_roi.json \
  analysis/eeg/preprocessing/gold/features/channel_set_policy_wang2022.json
```

Optional: `--with-task-state`, `--dry-run`.

Outputs (never primary Gold):

- `src/project/logs/xdf/gold/features/sensitivity/channel_sets/<version>/`
- `analysis/eeg/statistics/outputs/sensitivity/channel_sets/<version>/`

The feature builders also accept `--channel-set-policy` directly. If
that policy is not primary and the output paths are still the Gold
defaults, they reroute into the sensitivity folder.

`python analysis/eeg/preprocessing/run_pipeline.py` stays on
`current_v1`. It must not write a literature branch into primary Gold.

## What is frozen

- Cleaning scope: full montage.
- Primary Gold column names and 16-feature inventory.
- Confirmatory Holm family: Fz theta and posterior alpha on `current_v1`.
- ICA archive: do not refit.

## Tests

```bash
python -m unittest analysis.eeg.preprocessing.gold.features.test_channel_sets
```
