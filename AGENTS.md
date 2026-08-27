# Agent entrypoint

> **CRITICAL (EEG / ICA) — read before any cleaning or Gold command.**
> Do **not** run `fit_ica_cohort.py --overwrite` or
> `run_ica_sensitivity.py --overwrite-models`. Do **not** replace files
> under `src/project/logs/xdf/silver/ica/candidate_v1/`.
> Full stop: `.agents/context/data-analysis/eeg/CRITICAL-do-not-overwrite-ica-models.md`

## Writing / Overleaf

- Start with `.agents/context/writing/README.md`, then the newest dated entry
  in that directory.
- **Source of truth for manuscript content is only the Overleaf Git repos under
  `docs/overleaf/`** (especially `publication/` and `thesis/`). Context notes
  summarize decisions; they never override the LaTeX.
- Pull the relevant Overleaf mirror before drafting or editing. Show proposed
  text before applying; push only after explicit approval.
- **Results ≠ Discussion.** Results report estimands and numbers.
  Discussion interprets (precise null vs dead pipeline, Dataset B not
  absence, abstract placement, design implications, H1–H3). EEG 6.3 is
  confirmatory; 7.3 is the EEG read. Lock:
  `.agents/context/writing/2026-08-21-results-vs-discussion-and-eeg-6-3-pushed.md`.
- Canonical ad labels: **implicit** vs **explicit**; early = turn 2; late =
  turn 4; five-condition repeated-measures (+ no-ad control). Implicit does
  not mean subliminal.

## Data analysis

- Start with `.agents/context/data-analysis/README.md`, then the relevant arm's
  `README.md`; prefer the newest dated entry.
- Verify durable summaries against executable code and generated manifests.
- Keep raw Bronze/XDF immutable; add versioned Silver, Gold, statistics, or
  analysis outputs instead.
- EEG code lives in `analysis/eeg/`; generated EEG data lives under
  `src/project/logs/xdf/`.
- Treat participants—not epochs—as inferential units.
- Record scientific decisions in `.agents/context/data-analysis/`.
- EEG paper figure cut and Results sentences:
  `.agents/context/data-analysis/eeg/2026-08-20-paper-figures-and-narrative.md`.
  Depth audit (MDE, compatibility, exploratory lock):
  `.agents/context/data-analysis/eeg/2026-08-20-paper-depth-audit.md`.
  Confirmatory is 4 s + median + ICA. C1 is blocked on Goal 1.

### Where the EEG datasets live

Medallion zones under `src/project/logs/xdf/` (Bronze is immutable):

- `bronze/lab_subject_*/` — raw XDF, 19 enrolled subjects, ~4 GB.
- `silver/canonical_markers/<subject>.csv` — reconstructed event
  timelines; `silver/audits/` — channel and recording QC;
  `silver/ica/candidate_v1/` — fitted ICA models, see the banner above.
- `gold/windows/condition_windows.csv` — window definitions.
- `gold/features/condition_features.csv` — **Dataset A**, one row per
  participant × condition, 18 subjects, all `primary_analysis_eligible`.
- `gold/features/ad_response_features.csv` — **Dataset B**, one row per
  participant × advertisement, with onset estimator and uncertainty.
- `gold/features/task_state/task_state_person_features.csv` — the
  writing-versus-reading positive control.
- `gold/features/sensitivity/`, `gold/windows/sensitivity/` — epoch-width
  and no-ICA branches.
- `*_epoch_features.csv` are epoch-grain. Participants are the
  inferential unit, so never test on those rows directly.

Statistics: `analysis/eeg/statistics/outputs/`. `*_contrasts.csv` are
group results; `*_contrast_scores.csv` are the person-level difference
scores \(D_i\); branches under
`sensitivity/epoch_{2,4,8,16,32}s/{ica,no_ica}/` and `task_state/`.

### Merging EEG with behavioural

Behavioural sessions are JSONL, not a database:
`src/project/logs/tracked/{lab,crowd}/<subject>/<experiment_id>_export.jsonl`.
Prefer `*export*.jsonl` over `*events*.jsonl` when both exist, or rows
double. `tracked/beta/` is sensitivity only. Roster, exclusion tags, and
the ETL contract (finished \(L=18\), \(C=36\), \(N=54\)):
`.agents/context/data-analysis/behavioral/2026-08-18-behavioural-roster-and-log-schemes.md`.

**The join key is `experiment_id`.** It is a column in the EEG Gold
tables and is both a field and the filename stem on the behavioural
side. Verified example: `lab_subject_10` carries
`exp_20260728T091433Z_242026ac` in `condition_features.csv` and in
`tracked/lab/lab_subject_10/exp_20260728T091433Z_242026ac_export.jsonl`.
`condition`, `ad_mode`, and `trial_index` exist on both sides, so the
merge grain is participant × condition — the same grain the EEG
difference scores already use.

Only the laboratory arm has EEG, so a merged table has 18 people, not
54; the 36 crowd participants remain behavioural-only. That is why the
behaviour × EEG family is laboratory-only and an association rather
than a mediation claim. `lab_subject_4_crowdfail` is already excluded
from both sides.

## General

- Do not commit or push unless explicitly requested.
