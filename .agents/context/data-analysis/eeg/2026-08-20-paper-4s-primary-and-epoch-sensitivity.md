# Paper EEG: 4 s primary + epoch-length sensitivity

Date: 20 August 2026
Walter: keep **4 s + median + ICA** as confirmatory. Mention the 2 s
and 8 s Dataset B cells as **sensitivity**, not as a new result and not as
a reason to change epoch width.

Inferential unit is always the **participant**. Holm is per feature
across the 3 Dataset A or 4 Dataset B primary contrasts, **not** across five
widths × two cleanings. CIs are 95% paired *t* intervals on the
person-level differences. Scores are (ad post−pre) − (matched no-ad
post−pre), in dB.

Sources (do not rebuild Gold):

- primary 4 s ICA: `analysis/eeg/statistics/outputs/eeg_ad_response_contrasts.csv`
  and `eeg_condition_contrasts.csv`
- grid: `analysis/eeg/statistics/outputs/sensitivity/epoch_{2,4,8,16,32}s/{ica,no_ica}/`
- comparison: `statistics/outputs/sensitivity/epoch_length_grid_comparison.csv`
- after-reply (rejected lock): `statistics/outputs/sensitivity/after_reply/`
- read vs write: `statistics/outputs/task_state/eeg_task_state_contrasts.csv`

Log keys stay `block_*`. Paper names: **explicit** = `block`,
**implicit** = `inline`.

## Decision

| Role | What |
|---|---|
| Confirmatory | 4 s · median · ICA · \(n=18\) · Fz theta + posterior alpha |
| Sensitivity (mention both or neither) | 2 s explicit-early Fz theta (ICA only); 8 s explicit-late posterior alpha (ICA and no-ICA) |
| One-sentence sanity check | writing − reading Fz theta |
| Not primary | after-reply lock, hybrid lock, mean-of-epoch, 16/32 s, exploratory bands |

Dataset A is Holm-null at every width (2–32 s), ICA and no-ICA. The two
Dataset B hits are **different cells**: different width, different timing,
different feature. That is why they are a sensitivity note, not a
re-freeze.

## Paper sentences

Primary confirmatory EEG used 4 s epochs, person-level medians, and ICA
(\(n=18\)). Condition-level and ad-locked contrasts on Fz theta and
posterior alpha were Holm-null. The same chain distinguished writing
from reading on Fz theta (\(M=+0.60\) dB, 95% CI \([0.22, 0.97]\),
\(d_z=0.80\), Holm \(p=0.007\)); that is a pipeline check, not an ad
finding.

A pre-specified epoch-length sensitivity (2 / 8 / 16 / 32 s; 4 s
reused) left Dataset A Holm-null at every width. Two Dataset B confirmatory
cells crossed Holm only off the frozen 4 s width: (i) a 2 s window
after explicit-early ads showed higher Fz theta than matched no-ad
under ICA only (\(M=+3.30\) dB, 95% CI \([1.12, 5.49]\), \(d_z=0.75\),
Holm \(p=0.021\)); the cell was gone without ICA (Holm \(p=0.44\)) and
at every longer width; (ii) an 8 s window after explicit-late ads
showed lower posterior alpha than matched no-ad under both ICA
(\(M=-1.22\) dB, 95% CI \([-2.04, -0.41]\), \(d_z=-0.74\), Holm
\(p=0.023\)) and no-ICA (\(M=-1.30\) dB, 95% CI \([-2.09, -0.50]\),
\(d_z=-0.81\), Holm \(p=0.012\)). Neither contrast was Holm-significant
at the pre-specified 4 s width. If one cell is mentioned, mention both.

Do **not** put either cell in the abstract as an ad effect. Appendix
figure: epoch-grid heatmap / traces (`figure_10` / `figure_11`).

## Confirmatory 4 s ICA (what the paper reports)

Dataset A, person-median of retained 4 s tiles, \(n=18\), df = 17.

| Contrast (paper) | Feature | \(M\) (dB) | SD | SE | 95% CI | \(d_z\) | \(t\) | raw \(p\) | Holm \(p\) |
|---|---|---|---|---|---|---|---|---|---|
| any-ad − no-ads | Fz theta | −0.08 | 0.30 | 0.07 | [−0.23, 0.06] | −0.28 | −1.21 | 0.244 | 0.488 |
| implicit − explicit | Fz theta | −0.02 | 0.24 | 0.06 | [−0.14, 0.10] | −0.06 | −0.27 | 0.788 | 0.788 |
| early − late | Fz theta | −0.11 | 0.29 | 0.07 | [−0.26, 0.03] | −0.39 | −1.64 | 0.119 | 0.358 |
| any-ad − no-ads | posterior alpha | +0.07 | 0.43 | 0.10 | [−0.14, 0.28] | 0.17 | 0.71 | 0.489 | 0.961 |
| implicit − explicit | posterior alpha | +0.05 | 0.29 | 0.07 | [−0.10, 0.19] | 0.17 | 0.72 | 0.481 | 0.961 |
| early − late | posterior alpha | −0.09 | 0.28 | 0.07 | [−0.23, 0.05] | −0.32 | −1.35 | 0.196 | 0.587 |

Dataset B, the two cells that later light up off-width, at the **frozen**
4 s lock:

| Contrast | Feature | Cleaning | \(n\) | \(M\) (dB) | SD | SE | 95% CI | \(d_z\) | \(t\) | raw \(p\) | Holm \(p\) | Wilcoxon \(W\) | Wilcoxon Holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| explicit early − no-ad | Fz theta | ICA | 18 | +0.74 | 2.02 | 0.48 | [−0.27, 1.74] | 0.36 | 1.55 | 0.140 | 0.421 | 60 | 0.851 |
| explicit early − no-ad | Fz theta | no-ICA | 18 | +0.72 | 4.08 | 0.96 | [−1.31, 2.75] | 0.18 | 0.75 | 0.462 | 1.000 | 56 | 0.636 |
| explicit late − no-ad | posterior alpha | ICA | 18 | −1.29 | 2.83 | 0.67 | [−2.70, 0.12] | −0.45 | −1.93 | 0.071 | 0.284 | 50 | 0.475 |
| explicit late − no-ad | posterior alpha | no-ICA | 18 | −1.10 | 2.60 | 0.61 | [−2.40, 0.19] | −0.42 | −1.80 | 0.090 | 0.359 | 49 | 0.475 |

At 4 s the late-alpha CI already leans negative and includes zero.
Holm does not reject. That is the confirmatory result.

## Sensitivity cell 1 — 2 s · explicit early · Fz theta

“Banner just appeared.” Post = `[onset, onset+2)`. ICA-only Holm hit.
Gone at 4 / 8 / 16 / 32 s. Dies under the after-reply lock.

| Width | Cleaning | \(n\) | \(M\) (dB) | SD | SE | 95% CI | \(d_z\) | \(t\) (df) | raw \(p\) | Holm \(p\) | \(W\) | Wilcoxon Holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **2 s** | **ICA** | **18** | **+3.30** | **4.39** | **1.04** | **[1.12, 5.49]** | **0.75** | **3.19 (17)** | **0.005** | **0.021** | **23** | **0.019** |
| 2 s | no-ICA | 18 | +2.26 | 5.66 | 1.33 | [−0.56, 5.07] | 0.40 | 1.69 (17) | 0.109 | 0.437 | 53 | 0.669 |
| 4 s | ICA | 18 | +0.74 | 2.02 | 0.48 | [−0.27, 1.74] | 0.36 | 1.55 (17) | 0.140 | 0.421 | 60 | 0.851 |
| 8 s | ICA | 17 | +0.26 | 2.19 | 0.53 | [−0.87, 1.38] | 0.12 | 0.48 (16) | 0.637 | 1.000 | 58 | 1.000 |
| 16 s | ICA | 17 | +0.18 | 1.51 | 0.37 | [−0.60, 0.96] | 0.12 | 0.49 (16) | 0.628 | 1.000 | 51 | 0.760 |
| 32 s | ICA | 16 | +0.27 | 0.79 | 0.20 | [−0.15, 0.69] | 0.34 | 1.37 (15) | 0.190 | 0.759 | 42 | 0.771 |
| 2 s after-reply | ICA | 18 | +2.55 | 4.30 | 1.01 | [0.41, 4.69] | 0.59 | 2.51 (17) | 0.022 | 0.090 | 32 | 0.073 |

Wilcoxon agrees with the *t* test on the 2 s ICA cell (Holm 0.019).
no-ICA 2 s CI includes zero. After-reply keeps a raw *p* = 0.022 but
Holm 0.090 — the “first glance” story does not survive a lock after
the finished reply.

## Sensitivity cell 2 — 8 s · explicit late · posterior alpha

Last reply of the condition, not a mid-chat turn. Survives ICA and
no-ICA. Not Holm-significant at 2 / 4 / 16 / 32 s. Survives the
after-reply lock at 8 s (Holm still 0.023). Still not 4 s.

| Width | Cleaning | \(n\) | \(M\) (dB) | SD | SE | 95% CI | \(d_z\) | \(t\) (df) | raw \(p\) | Holm \(p\) | \(W\) | Wilcoxon Holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 s | ICA | 18 | −1.91 | 3.95 | 0.93 | [−3.88, 0.05] | −0.48 | −2.05 (17) | 0.056 | 0.223 | 43 | 0.266 |
| 2 s | no-ICA | 18 | −1.92 | 3.76 | 0.89 | [−3.79, −0.05] | −0.51 | −2.17 (17) | 0.044 | 0.178 | 44 | 0.295 |
| 4 s | ICA | 18 | −1.29 | 2.83 | 0.67 | [−2.70, 0.12] | −0.45 | −1.93 (17) | 0.071 | 0.284 | 50 | 0.475 |
| **8 s** | **ICA** | **18** | **−1.22** | **1.64** | **0.39** | **[−2.04, −0.41]** | **−0.74** | **−3.16 (17)** | **0.006** | **0.023** | **28** | **0.042** |
| **8 s** | **no-ICA** | **18** | **−1.30** | **1.60** | **0.38** | **[−2.09, −0.50]** | **−0.81** | **−3.44 (17)** | **0.003** | **0.012** | **23** | **0.019** |
| 16 s | ICA | 17 | −0.90 | 1.76 | 0.43 | [−1.81, 0.00] | −0.51 | −2.11 (16) | 0.051 | 0.203 | 36 | 0.228 |
| 32 s | ICA | 16 | −0.93 | 1.46 | 0.36 | [−1.71, −0.16] | −0.64 | −2.56 (15) | 0.022 | 0.087 | 26 | 0.116 |
| 8 s after-reply | ICA | 18 | −1.08 | 1.45 | 0.34 | [−1.80, −0.36] | −0.75 | −3.16 (17) | 0.006 | 0.023 | 26 | 0.031 |

32 s ICA excludes zero in the uncorrected CI (\(n=16\)) but Holm is
0.087. Do not promote that near-miss. *n* drops at 16–32 s because
some onsets sit too close to the condition edge, or the long slice
fails amplitude QC.

## Why mention both

The whole confirmatory Dataset B × Fz-theta/posterior-alpha × ICA/no-ICA
× {2,4,8,16,32} s grid has **exactly three** Holm hits, and they are
these two stories (8 s alpha appears twice, once per cleaning).
Mentioning only the 2 s theta cell looks like fishing. Mentioning only
the 8 s alpha cell hides that a different width lights a different
moment. Mention both, label them sensitivity, keep 4 s.

## Sanity check (one sentence only)

Writing − reading, 4 s ICA, person-median of 268 turn pairs, \(n=18\):

| Feature | \(M\) (dB) | SD | 95% CI | \(d_z\) | \(t\) | raw \(p\) | Holm \(p\) |
|---|---|---|---|---|---|---|---|
| Fz theta | +0.60 | 0.75 | [0.22, 0.97] | 0.80 | 3.38 | 0.004 | 0.007 |
| posterior alpha | +0.08 | 1.03 | [−0.43, 0.59] | 0.08 | 0.32 | 0.751 | 0.751 |

Not Q1, not Q2, not the abstract.

## Related

- Grid contract: `2026-08-19-epoch-length-grid.md`
- Median stays primary: `2026-08-19-mean-vs-median-and-epoch-length.md`
- After-reply rejected: `2026-08-20-dataset-b-after-reply-lock.md`
- Pipeline alive: `2026-08-19-read-vs-write-what-it-proved.md`
- Stop line: `2026-08-19-eeg-only-analyses-complete.md`
