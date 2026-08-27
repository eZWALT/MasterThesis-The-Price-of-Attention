# Epoch-length grid 2/4/8/16/32 s

Date: 19 August 2026

## Contract

Fixed-length epochs only. Dataset A tiles from condition start (remainder
dropped). Dataset B is `[onset−W, onset)` / `[onset, onset+W)`. Welch
`nperseg` stays 2 s, so the grid changes how much time is averaged into
one row, not the FFT resolution. Median remains the Dataset A aggregator.
ICA remains primary. 4 s is not rebuilt; existing ICA primary and no-ICA
archives are reused.

Do **not** freeze 2 s or 8 s because a Holm cell appeared. Holm is per
feature across the 3 (Dataset A) or 4 (Dataset B) primary contrasts, not across
five lengths × two cleaning branches.

## What ran

`analysis/eeg/preprocessing/run_epoch_length_sensitivity.py`

- lengths 2, 8, 16, 32 s × ICA + no-ICA
- one `clean_recording` per person per policy, then all cuts
- outputs under `gold/features/sensitivity/epoch_{N}s/{ica,no_ica}/`
  (gitignored) and `statistics/outputs/sensitivity/epoch_{N}s/`
- comparison: `statistics/outputs/sensitivity/epoch_length_grid_comparison.csv`

32 s Dataset A drops Subjects 10, 14, 17 (too few complete tiles / 80%
rule) → n=15. Baseline ~30 s cannot make a 32 s epoch. Dataset B pair
counts fall at 16–32 s (some onsets too close to the condition edge, or
a 32 s slice fails amplitude QC).

## Holm hunt (1,920 tests)

Dataset A: **0 Holm hits** at every length, ICA and no-ICA.

Confirmatory Dataset B Holm hits (Fz theta or posterior alpha, primary
ad−matched-control contrasts):

| W | Cleaning | Contrast | Feature | n | mean dB | 95% CI | \(d_z\) | Holm p |
|---|---|---|---|---|---|---|---|---|
| 2 s | ICA | explicit early − no-ad | Fz theta | 18 | +3.30 | [1.12, 5.49] | 0.75 | 0.021 |
| 8 s | ICA | explicit late − no-ad | posterior alpha | 18 | −1.22 | [−2.04, −0.41] | −0.74 | 0.023 |
| 8 s | no-ICA | explicit late − no-ad | posterior alpha | 18 | −1.30 | [−2.09, −0.50] | −0.81 | 0.012 |

The 8 s posterior-alpha explicit-late cell is the only confirmatory
hit that appears under **both** ICA and no-ICA. It is not Holm-significant
at 2, 4, 16, or 32 s (32 s is a near miss, Holm ~0.09, n=16).

The 2 s Fz-theta explicit-early cell is ICA-only (no-ICA Holm 0.44) and is
gone at every longer width.

Exploratory Holm hits (16 of 19) are mostly the same explicit-early
spectral tilt already seen at 4 s ICA (more delta/theta, less relative
alpha/beta). They thin out at 16–32 s.

## Decision

Primary remains **4 s + median + ICA**. Dataset A null is robust to tile
size. Mention **both** off-width cells as sensitivity, not as a new
confirmatory result and not as a reason to change ad format or epoch
width. Numbers: `2026-08-20-paper-4s-primary-and-epoch-sensitivity.md`.

4 s is not an arbitrary middle. Dataset B locks to visual ad onset
(see `2026-08-20-what-dataset-b-onset-is.md`). A 20 August after-reply
lock (finished message + 0.49 s) stayed 4 s Holm-null and killed the
2 s explicit-early theta cell. Keep the golden lock.
On explicit ads the reply is already up (~0.5 s); on implicit it follows
(~1.6 s). A 2 s post window is still “ad chrome / first glance” and
misses the reply entirely for about one in five ads. A 4 s window
almost always contains the reply and never reaches the next act
(early: next `user_message` ~53 s; late: conclusion ~79 s). An 8 s
window is just more of that same reply — and the only Holm hit is
**late explicit alpha**, i.e. the last reply of the condition, not a
mid-chat turn. The 2 s hit is a **different** cell (early explicit theta,
ICA-only). Two widths, two moments, two features is not one story.
Timeline: `figure_17_epoch_timeline` and canvas `eeg-epoch-timeline`.

## Paper sentence (frozen 20 August)

Primary stays **4 s + median + ICA**. Mention **both** off-width Dataset B
cells as sensitivity, or mention neither. Full CIs, \(d_z\), Wilcoxon,
and the 4 s comparison:

`2026-08-20-paper-4s-primary-and-epoch-sensitivity.md`

Short form: 2 s explicit-early Fz theta, ICA only,
\(M=+3.30\) dB, 95% CI \([1.12, 5.49]\), \(d_z=0.75\), Holm \(p=0.021\);
8 s explicit-late posterior alpha, ICA
\(M=-1.22\) dB, 95% CI \([-2.04, -0.41]\), \(d_z=-0.74\), Holm \(p=0.023\),
and no-ICA \(M=-1.30\) dB, 95% CI \([-2.09, -0.50]\), Holm \(p=0.012\).
Neither cell is Holm-significant at 4 s.
