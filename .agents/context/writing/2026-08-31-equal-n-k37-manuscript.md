# Equal-n \(k=37\) Dataset A — applied (31 August 2026)

Walter consented. **On Overleaf locally** (thesis, paper, presentation).
**Do not push** until he asks.

## Estimand

Confirmatory Dataset A is the median of the 37 retained 4 s tiles
whose midpoints are nearest visual onset (`around`). \(k=37\) is
\(\min\lfloor D/4\rfloor\) on the 90 eligible lab conditions
(shortest chat: `lab_subject_17` implicit-early). Every advertisement
condition has exactly 37 tiles; \(n=18\). No-ad uses matched turn-2
and turn-4 replies. Tiles stay condition-start aligned (not recut at
onset; that is Dataset B). Dataset B is unchanged. Gold
`condition_features.csv` still stores the whole-window median.

Rationale in the manuscripts: conversations vary in length, so a
fixed epoch count equalizes short vs long chats. Do not write search
/ HARKing / exhaustive \(k\) into Overleaf.

## Discussion read (Walter)

Early advertisements were associated with lower posterior alpha
power than late advertisements, suggesting a difference in
visual-attentional / cortical engagement depending on ad timing.

Theta: if early insertions had recruited more effortful control, Fz
\(\theta\) would be *higher* for early than late. The matching
contrast goes the other way (\(M=-0.20\) dB) and is Holm-null, so
we do not claim a control-related timing effect. Exploratory relative
\(\theta\) is also lower for early than late (Holm \(p=.038\)): a
lower theta *share*, not a rise in frontal-midline control theta.

Any-ad remains the advertisement-versus-none bound.

## Numbers of record (\(n=18\), Holm within 3)

| Contrast | Fz \(\theta\) \(M\) / CI / \(d_z\) / Holm \(t\) / Holm \(W\) | Post. \(\alpha\) \(M\) / CI / \(d_z\) / Holm \(t\) / Holm \(W\) |
|---|---|---|
| Any-ad | −0.04 / [−0.18, 0.11] / −0.13 / .60 / .47 | +0.09 / [−0.17, 0.35] / +0.17 / .97 / .83 |
| Format | −0.08 / [−0.21, 0.05] / −0.30 / .43 / .26 | +0.06 / [−0.20, 0.32] / +0.11 / .97 / .83 |
| Early vs late | −0.20 / [−0.38, −0.01] / −0.52 / **.12** / .10 | **−0.22 / [−0.39, −0.04] / −0.63 / .050 / .062** |

Wilcoxon does **not** agree on the Holm decision for timing
posterior alpha. Do not write “Wilcoxon agrees in every cell.”
Do not write “approached significance.”

Exploratory remaining 14: early vs late relative theta Holm \(p=.038\).
Dataset A is 2/48, not 0/48.

Holm-80% MDE (first-step \(\alpha=0.05/3\)): \(d_z\) bound still
0.83. dB: **0.22–0.44** (any-ad Fz \(\theta\) 0.24 dB). Observed
Holm power on the six cells 3–52% (timing post. \(\alpha\) 52%).
Dataset B MDE unchanged 1.7–3.7 dB.

Post-hoc (exploratory): one Holm/BH/BY cell on Dataset A —
implicit-early minus explicit-late Fz \(\theta\), \(M=-0.28\) dB,
Holm \(p=.014\). Do not promote.

## What changed where

- Stats: `run_equal_n_dataset_a.py` writes k=37 into
  `statistics/outputs/eeg_condition_contrasts.csv` (whole-window
  archived under `sensitivity/whole_window_dataset_a/`).
- Figures: forests, 4 s Holm board, post-hoc board — thesis, paper,
  presentation copies.
- Presentation: \(D^A_i\) uses \(N_{ic}(37)\); limits slide MDE
  \(0.22\)–\(0.44\) dB. Do not rewrite Walter’s `%` spoken comments
  or the high-level discussion enumerate. His forest comment still
  says all CIs contain 0; a second `%` line flags the stale bit.
- High-level discussion “cannot state overall difference” stays:
  any-ad is still Holm-null.

Analysis lock: `../data-analysis/eeg/2026-08-31-equal-n-k37.md`.
