# Epoch-length grid 2/4/8/16/32 s

Date: 19 August 2026

## Contract

Fixed-length epochs only. Path A tiles from condition start (remainder
dropped). Path B is `[onset−W, onset)` / `[onset, onset+W)`. Welch
`nperseg` stays 2 s, so the grid changes how much time is averaged into
one row, not the FFT resolution. Median remains the Path A aggregator.
ICA remains primary. 4 s is not rebuilt; existing ICA primary and no-ICA
archives are reused.

Do **not** freeze 2 s or 8 s because a Holm cell appeared. Holm is per
feature across the 3 (Path A) or 4 (Path B) primary contrasts, not across
five lengths × two cleaning branches.

## What ran

`analysis/eeg/preprocessing/run_epoch_length_sensitivity.py`

- lengths 2, 8, 16, 32 s × ICA + no-ICA
- one `clean_recording` per person per policy, then all cuts
- outputs under `gold/features/sensitivity/epoch_{N}s/{ica,no_ica}/`
  (gitignored) and `statistics/outputs/sensitivity/epoch_{N}s/`
- comparison: `statistics/outputs/sensitivity/epoch_length_grid_comparison.csv`

32 s Path A drops Subjects 10, 14, 17 (too few complete tiles / 80%
rule) → n=15. Baseline ~30 s cannot make a 32 s epoch. Path B pair
counts fall at 16–32 s (some onsets too close to the condition edge, or
a 32 s slice fails amplitude QC).

## Holm hunt (1,920 tests)

Path A: **0 Holm hits** at every length, ICA and no-ICA.

Confirmatory Path B Holm hits (Fz theta or posterior alpha, primary
ad−matched-control contrasts):

| W | Cleaning | Contrast | Feature | n | mean dB | Holm p |
|---|---|---|---|---|---|---|
| 2 s | ICA | block early − no-ad | Fz theta | 18 | +3.30 | 0.021 |
| 8 s | ICA | block late − no-ad | posterior alpha | 18 | −1.22 | 0.023 |
| 8 s | no-ICA | block late − no-ad | posterior alpha | 18 | −1.30 | 0.012 |

The 8 s posterior-alpha labelled-block-late cell is the only confirmatory
hit that appears under **both** ICA and no-ICA. It is not Holm-significant
at 2, 4, 16, or 32 s (32 s is a near miss, Holm ~0.09, n=16).

The 2 s Fz-theta block-early cell is ICA-only (no-ICA Holm 0.44) and is
gone at every longer width.

Exploratory Holm hits (16 of 19) are mostly the same labelled-block-early
spectral tilt already seen at 4 s ICA (more delta/theta, less relative
alpha/beta). They thin out at 16–32 s.

## Decision

Primary remains **4 s + median + ICA**. Path A null is robust to tile
size. The 8 s alpha cell may be mentioned as a sensitivity note, not as
a new confirmatory result and not as a reason to change ad format.

## Paper sentence

Primary 4 s analyses are Holm-null for Fz theta and posterior alpha.
An 8 s ad-locked window showed lower posterior alpha after labelled-block
late ads than after matched no-ad replies under both ICA and no-ICA; that
contrast was not Holm-significant at the pre-specified 4 s width or at
2 / 16 / 32 s.
