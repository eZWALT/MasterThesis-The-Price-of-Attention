# EEG–behavioural merge tables

Date: 19 August 2026

**7 September (evening):** do not re-join by hand. Read
`joined chat` / `joined contrasts` from
`analysis/walter/behavioural/outputs/gold/`. Catalog:
`../2026-09-07-gold-catalog-and-lineage.md`. The 19 August
builder path below is stale (Katerina's folder is not Gold).

Design only (original). Behavioural composites below for
`lab_subject_10` use the **planned** credibility / helpfulness /
manipulation formulas and are illustrative until Goal 1 scoring is
frozen.

Join rule: never merge on epoch. First combined table is person ×
condition or person × ad-response.

## What is already a column you can plug in

From Gold / stats, **one number per person × cell**. Those are the
features. Everything else is either nested (epochs) or already
collapsed across people (descriptives).

| Source | Plug-in columns | Grain | Rows now |
|---|---|---|---|
| `condition_features.csv` | 16 `*_median` | person × condition | 90 (+ 18 baseline) |
| same file | 16 `*_baseline_delta` | person × condition | 90 |
| `ad_response_features.csv` | 16 `*_post_minus_pre` | person × event | 108 (72 ad + 36 no-ad) |
| `eeg_condition_contrast_scores.csv` | `difference` after pivot | person × contrast | 18 × 4 × 16 long |
| `eeg_ad_response_contrast_scores.csv` | `difference` after pivot | person × Dataset B \(D\) | 18 × 4 primary |

**Do not plug as ML / correlation features**

- `*_iqr` — spread of epochs, not the condition state
- epoch CSVs (~9k / 216 rows) — no survey lives at that grain
- `eeg_condition_descriptives.csv` — already a cohort summary
- paths, hashes, PTP percentiles — provenance / QC, not predictors

Optional QC covariates (keep, do not treat as outcomes):
`retained_epoch_fraction`, `ica_applied`, `onset_status`,
`combined_timing_uncertainty_s`.

## Join key (must exist before any merge)

EEG `subject_id` is `lab_subject_10`. Surveys use hashed
`participant_id` (`83850ea0`). Shared key is `experiment_id`.

```
id_map: subject_id, participant_id, experiment_id, arm
```

Crowd (36) have surveys and **no EEG**. Left-join: EEG columns NA.
Lab EEG primary stay \(n=18\).

## Three analysis tables (do not squash into one)

### T1 — person × condition (correlations + most ML)

90 lab rows (18 × 5). This is C2 and the only honest “EEG predicts
trust/UX” table.

Keys: `subject_id`, `participant_id`, `experiment_id`, `condition`.

Derived: `format` (implicit / explicit / none), `timing`
(early / late / none), `task_id`.

EEG (plug from Gold medians; start with two primary):

- `eeg_fz_theta`
- `eeg_posterior_alpha`
- optional: `eeg_faa`, Pope FC, Kislov, global theta/alpha
- optional person-centering: the existing `*_baseline_delta`

Behaviour (after freeze): `trust`, `credibility`, `manipulation`,
helpfulness / convincingness, `notice_brands`, `notice_sponsored`.

Recall is **not** on this table (`no_ads` has no recall step).

### T2 — person × contrast (C1)

18 rows, wide. Same three \(D\) on EEG and on surveys.

```
D_any_ad   = mean(four ads) − no_ads
D_format   = mean(implicit) − mean(explicit)   # keys: inline_* − block_*
D_timing   = mean(early) − mean(late)
```

Build by pivoting `eeg_condition_contrast_scores.csv` and applying the
identical contrast functions to the frozen survey scores.

### T3 — person × ad event (C3 / Dataset B)

72 ad rows (+ 36 no-ad if you need the control \(\Delta\)).

EEG: `eeg_*_post_minus_pre`, plus `eeg_*_vs_control` =
ad \(\Delta\) minus matched no-ad \(\Delta\) (already in the Dataset B
score file).

Behaviour: `notice_*`, `recall_memory`, `recall_trust_shift`.
No-ad rows have recall = NA.

### T4 — person (between-subject / weak ML)

18 rows. Person-mean of the five T1 EEG medians, or the three T2 \(D\)s
as columns, plus BFI-10 and session globals. Appendix / Goal 5 only.

## ML rules if these become features

- Replication unit is still the person. 90 T1 rows are five repeats.
  Use participant-grouped splits. Do not report a random 80/20.
- T2 / T4 have \(n=18\). Correlation + CI, not a trained \(\pi\).
- Crowd-only models can use T1 without EEG. EEG models cannot use crowd.
- Predicting `condition` from EEG is a sanity/leakage check, not Goal 1.
- Goal 5 (insertion policy) is last and is not this join.

## Worked `lab_subject_10` numbers (ICA primary Gold)

Illustrative surveys: credibility =
\(\mathrm{mean}(\texttt{llm_reliable},\,8-\texttt{llm_false},\,8-\texttt{llm_made_up})\);
manipulation = mean(pushing, manipulate); helpfulness =
mean(helpful, addressed, \(8-\)not_aid).

Trust / notice / recall / BFI are raw log values.

## Related

- Ticket board: `2026-08-19-eeg-analysis-menu-and-tickets.md`
- Join gate: `2026-08-06-remaining-human-signoff-checklist.md`
- Scoring plan: `../behavioral/2026-08-18-tang-scoring-vs-ours.md`
