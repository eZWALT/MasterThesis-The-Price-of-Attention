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

## Candidate deterministic cleaning

`cleaning_policy.json` currently specifies:

1. 50 Hz notch filter;
2. 0.5–40 Hz band-pass filter;
3. mark reviewed bad channels;
4. average rereference excluding marked bad channels;
5. spherical-spline interpolation of marked channels.

The implementation was executed successfully on subject 8, including
interpolation of `F10`.

## Not yet frozen

- Online acquisition reference remains unconfirmed.
- ICA is disabled until component selection using `Fp1/Fp2` is visually
  validated; there are no dedicated EOG channels.
- Epoch-level amplitude and retention thresholds require distributions from the
  actual condition/ad windows.
- The current channel audit samples the complete recording evenly but does not
  replace full-window QC after epoch construction.
