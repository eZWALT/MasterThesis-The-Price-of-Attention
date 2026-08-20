# Mean-of-epoch dB sensitivity and epoch-length rule

Date: 19 August 2026

## Keep median as primary

Path A window summaries stay **median of retained 4 s epoch dB**, not the
mean. A mean-of-epoch-dB rebuild (ICA and no-ICA) left every Holm test
null: **0 / 48** on both aggregators. Confirmatory means barely moved
(Fz theta any-ad−no-ad: median −0.085, mean −0.063). The null is not
an artifact of the median.

Median remains the better default: residual high-amplitude epochs that
pass 1,050 µV still pull a mean more than a median. The synthetic unit
test `test_window_mean_is_arithmetic_mean_of_retained_epoch_db` shows
that split.

Path B has **no aggregator**. Each ad is one 4 s pre and one 4 s post.
Mean vs median does not apply there.

Outputs (do not replace primary Gold):

- `gold/features/sensitivity/mean_of_epoch_db/condition_features.csv`
- `statistics/outputs/sensitivity/mean_of_epoch_db/`
- matching no-ICA copies under `sensitivity/no_ica_frozen_v3/mean_of_epoch_db/`

Rebuild without recleaning:

```bash
python analysis/eeg/preprocessing/gold/features/build_condition_features.py \
  --from-epochs src/project/logs/xdf/gold/features/condition_epoch_features.csv \
  --summary-output src/project/logs/xdf/gold/features/sensitivity/mean_of_epoch_db/condition_features.csv
python analysis/eeg/statistics/build_condition_contrasts.py \
  --input src/project/logs/xdf/gold/features/sensitivity/mean_of_epoch_db/condition_features.csv \
  --output-dir analysis/eeg/statistics/outputs/sensitivity/mean_of_epoch_db \
  --feature-suffix _mean --metric condition_mean
```

## What the 4 s tests currently say

Confirmatory Q1/Q2 (Fz theta, posterior alpha) are Holm-null at \(n=18\)
with and without ICA. Six ICA-only Holm hits on other Y_B bands (mostly
early explicit, more delta/theta) are exploratory and
cleaning-dependent. Do not put them in the abstract. Do not change ad
format or timing from EEG.

## Epoch-length grid (next, not a fishing licence)

Walter asked to try 2 / 4 / 8 / 16 / 32 s. Treat that as a **robustness
grid**, not a search for a p-value to publish.

- Primary stays 4 s + median until a **pre-specified** length is frozen.
- If only one width is Holm-significant, that is a sensitivity note, not
  a new confirmatory result.
- Do not pick 16 s or 32 s because it is the one that “comes out.”
- Path A: 2–32 s only changes tile size; the condition is still minutes
  long.
- Path B: the window **is** the observation; 16–32 s around an ad is a
  different question (and 32+32 s read/write pairs do not fit a typical
  52 s turn).

## Paper sentence

Primary 4 s median analyses show no Holm-significant Fz-theta or
posterior-alpha condition or ad-locked contrast (\(n=18\)). Mean-of-epoch
summaries agree. Compatible effects are small; a null is not evidence of
absence.
