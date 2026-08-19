# Signal-quality audit and cleaning policy

Date: 3 August 2026

## Cohort audit

The condition-blind audit sampled twelve evenly spaced 30-second windows from
each of the 19 current recordings (six minutes per recording).

- 19 of 19 recordings converted from XDF to MNE.
- All recordings have the same 32-channel layout and complete standard 10-20
  coordinates.
- No near-flat or flatline channels were detected.
- No recording is automatically excluded by signal QC.
- Subject 8 channel `F10` is the only current non-ocular channel flagged for
  both extreme filtered amplitude and low inter-channel correlation.
- Low correlation in `Fp1` or `Fp2` is treated as ocular activity, not automatic
  channel failure; these channels are retained as ICA proxies.
- Strong 50 Hz power is common to all recordings and establishes the need for a
  50 Hz notch filter. It is not used as a channel-rejection rule.

Generated evidence:

- `src/project/logs/xdf/silver/audits/eeg_channel_quality.csv`
- `src/project/logs/xdf/silver/audits/eeg_recording_quality.csv`

## Deterministic cleaning

`cleaning_policy.json` currently specifies:

1. 50 Hz notch filter;
2. 0.5–40 Hz band-pass filter;
3. mark reviewed bad channels;
4. average rereference excluding marked bad channels;
5. spherical-spline interpolation of marked channels.

Generated epochs retain the observed 500 Hz sampling rate. Their Nyquist
frequency is therefore 250 Hz, safely above the 40 Hz low-pass cutoff
(6.25-fold margin). The aggregate soundness validator checks this from the
generated epoch rows rather than relying only on nominal metadata.

Full-window epoch evidence added three recording-specific interpolations:
subject 1 `P4`, subject 9 `P4`, and subject 10 `C4`. Subject 8 `F10` remains
interpolated from the condition-blind channel audit. These decisions are stored
in the generated policy rather than human annotation columns.

The primary gross-artifact rule is 1,050 µV peak-to-peak (`frozen_v3`), with no
near-flat channels, a minimum retained fraction of 80%, and at least five
retained epochs per condition window. It was selected after observing Subject
14's 1,042.56 µV no-ad epoch and is therefore explicitly post-review. The
1,000 µV `frozen_v1` and 1,500 µV `frozen_v2` rules remain mandatory
sensitivities. Current Gold outputs apply the approved ICA primary branch
(`frozen_v5_ica_primary`). No-ICA tables are archived under
`gold/features/sensitivity/no_ica_frozen_v3/`.

`validate_cleaning_visual.py` generates the validation pack under
`src/project/logs/xdf/silver/validation/cleaning_visual/`. Representative notch
and average-reference checks pass. All four interpolated channels fall below
1,000 µV in their worst inspected segment and correlate with neighboring
signals after repair (`r=0.688` to `0.991`). Human visual signoff was approved
on 2026-08-19.

## Frozen cleaning branch

- Laboratory feedback reports `Cz` online reference and `Fpz` ground; average
  rereferencing remains the offline policy.
- ICA uses 99% PCA explained variance, FastICA, seed 97, at most three
  components with both `|r| ≥ 0.35` vs Fp1/Fp2 and frontal dominance `≥ 1.5`.
- Human review on 2026-08-19 approved all automatic exclusions and made ICA
  the primary branch. No-ICA remains a mandatory sensitivity.
