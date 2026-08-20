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

## General

- Do not commit or push unless explicitly requested.
