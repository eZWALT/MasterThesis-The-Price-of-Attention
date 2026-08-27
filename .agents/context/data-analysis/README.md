# Data-analysis context structure

> **CRITICAL (EEG / ICA).** Do not `--overwrite` ICA models. Read
> `eeg/CRITICAL-do-not-overwrite-ica-models.md` first.

This directory holds durable analysis decisions and audit summaries.

## Shared planning

The top level is reserved for documents that govern both analysis arms:

- `2026-07-28-data-analysis-foundation.md`
- `2026-08-03-behavioral-eeg-workstream-ownership.md`
- `2026-08-04-final-month-north-star.md`
- `2026-08-20-implicit-explicit-names.md` — paper says implicit /
  explicit; log keys stay `inline_*` / `block_*`.
- `eeg/2026-08-20-what-path-b-onset-is.md` — Dataset B onset is when the
  ad becomes visible. After-reply lock rejected; keep golden.
- `2026-08-18-analysis-priority-order.md` — behavioural first, then
  personality, EEG, trajectories, policy model last.
- `eeg/2026-08-20-paper-figures-and-narrative.md` — paper/thesis EEG
  figure cut and what the Holm-nulls allow you to say.
- Crossable leftover list (analysis + manuscripts):
  `../writing/2026-08-18-remaining-work-checklist.md`.

## Analysis arms

- `behavioral/`: behavioural ETL, scoring, outcome definitions, exclusions,
  model specifications, and audit summaries.
- `eeg/`: recording audits, marker reconstruction, preprocessing, feature
  definitions, exclusions, and EEG model specifications.

Generated datasets, manifests, figures, and executable analysis code remain under
`analysis/`. Context documents summarize what those artifacts establish and the
decisions made from them; they should not duplicate raw participant data.
