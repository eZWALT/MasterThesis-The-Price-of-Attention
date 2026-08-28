# Dataset B matched-control audit (28 August 2026)

Audit of how the Dataset B control cells are built and which existing
contrasts live in which space. Done from `build_ad_windows.py`,
`build_ad_contrasts.py`, and the Gold rows, not from prose. Nothing was
modified. Confirmatory EEG is untouched.

Ordered against the audit questions asked before the post-hoc sweep.

## 1. What `no_ads_early` and `no_ads_late` are

Both come from **the same single `no_ads` conversation** of that
participant (`build_ad_windows.py:no_ad_rows`). They are the
`assistant_reply` markers at **turn 2** and **turn 4** of that one
conversation, projected onto the EEG clock.

- Estimator `log_projected_assistant_reply`, status
  `derived_clock_aligned`.
- Pre `[onset-4s, onset)`, post `[onset, onset+4s)`. Single epochs, no
  median (that is Dataset A's collapse, not this one).
- `matched_ad_conditions` names who each control serves:
  `inline_early;block_early` and `inline_late;block_late`. **One control
  cell is deliberately shared by two ad conditions.**

Known asymmetry: ad onsets use visual-onset estimators (explicit =
reply + 0.49 s; implicit = inject + 1.57 s, i.e. *before* its own
reply), while the control is the reply instant itself. The control is
therefore not the identical phase of the turn as an implicit ad onset.
Lock: `2026-08-20-what-dataset-b-onset-is.md`.

## 2. Exact formulas in the code

`build_ad_contrasts.py:contrast_functions()`. Each symbol is that cell's
`post_minus_pre`; \(N_e\) / \(N_l\) are the two controls above.

| Contrast | Tier | Formula |
|---|---|---|
| `inline_early_vs_no_ad_early` | primary | IE − \(N_e\) |
| `block_early_vs_no_ad_early` | primary | EE − \(N_e\) |
| `inline_late_vs_no_ad_late` | primary | IL − \(N_l\) |
| `block_late_vs_no_ad_late` | primary | EL − \(N_l\) |
| `any_ad_vs_matched_no_ad` | secondary | mean(IE,EE,IL,EL) − mean(\(N_e\),\(N_l\)) |
| `inline_vs_block` | secondary | mean(IE,IL) − mean(EE,EL) |
| `early_vs_late` | secondary | mean(IE,EE) − mean(IL,EL) |
| `format_x_timing` | secondary | (IE−IL) − (EE−EL) |

Holm runs within measure over the four primary rows only. The four
secondary rows are stamped `secondary_uncorrected`.

## 3. Raw space versus \(\Delta\) space

Everything is computed in **raw post−pre space**. There is no
\(\Delta\) column in Gold or in the statistics; \(\Delta\) exists only
implicitly.

- The four primary contrasts **are** the four \(\Delta_c\) exactly.
- `any_ad_vs_matched_no_ad` equals mean(\(\Delta\)) exactly.
- `inline_vs_block` and `format_x_timing` are **identical in both
  spaces**; the controls cancel algebraically.
- **`early_vs_late` is raw-space only.** Its \(\Delta\)-space
  counterpart differs by \(-(N_e-N_l)\).

Verified on Fz theta, \(n=18\): code `early_vs_late` \(=+0.670\) dB,
\(\Delta\)-space timing \(=+1.427\) dB, difference exactly
\((N_e-N_l)\), mean \(-0.757\) dB, SD \(2.31\).

Exactly one existing contrast is space-dependent, and it is the timing
one.

## 4. What the plan declares

Thesis Methods `sec:methods:statistical-framework` writes out the
Dataset **A** weights explicitly, timing included
\((\tfrac12,-\tfrac12,\tfrac12,-\tfrac12,0)\). For Dataset **B** it
declares only the \(D^{B}\) equation and "4 contrasts, separately within
each measure".

**The Dataset B secondary weights are not written down anywhere.** The
raw-space `early_vs_late` is an implementation choice, not a
pre-specification. Nothing published rests on it (those rows are
uncorrected secondary), but the plan cannot be cited to justify either
space. **Open Methods item**, not an analysis defect.

## 5. Separate or pooled controls

Separate, deliberately, and the rationale holds: turn 2 and turn 4 are
different points in a conversation, so a late ad is matched to a late
reply. `any_ad_vs_matched_no_ad` is the only pooling and it averages
symmetrically, so it is clean.

Correct matching is exactly *why* cross-timing comparisons inherit
\(\pm(N_e-N_l)\). That is a consequence, not a bug.

## Cohort fact

All 18 subjects have all six cells (108 eligible rows, 18 × 6). So
\(n=18\) and \(\mathrm{df}=17\) for every Dataset B pair, including
cross-timing ones. Earlier worry that the \(n\ge 15\) tolerance in
`build_ad_contrasts.py` would bite is not realised on this cohort.

## Related

- Post-hoc sweep built on this audit: `2026-08-28-posthoc-pairwise.md`
- Confirmatory lock: `2026-08-20-paper-4s-primary-and-epoch-sensitivity.md`
- Onset lock: `2026-08-20-what-dataset-b-onset-is.md`
