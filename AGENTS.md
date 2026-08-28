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
  confirmatory; Discussion `sec:disc-eeg` is the EEG read. Lock:
  `.agents/context/writing/2026-08-21-results-vs-discussion-and-eeg-6-3-pushed.md`.
- Canonical ad labels: **implicit** vs **explicit**; early = turn 2; late =
  turn 4; five-condition repeated-measures (+ no-ad control). Implicit does
  not mean subliminal.
- Genre classifier: \(f_{\mathrm{genre}}\), not \(f_\theta\). Lock:
  `.agents/context/writing/2026-08-23-f-genre-notation.md`.
- **Trajectories are thesis-only** (24 August). Do not put Defs 1–6,
  Results 6.4, or trajectory Discussion/appendix back in the paper.
  Lock: `.agents/context/writing/2026-08-24-trajectories-thesis-only.md`.
- **Dataset A / Dataset B**, never Path A/B. A dataset is not the
  subject of a test ("the Dataset A **contrasts** test…"). Lock:
  `.agents/context/data-analysis/eeg/2026-08-27-dataset-a-b-rename.md`.
  27 August catch-up (figure regen, crowd age, Methods comments):
  `.agents/context/writing/2026-08-27-afternoon-save.md`.
  28 August save: channel-set retry closed; primary 32-ch stays.
  `.agents/context/data-analysis/eeg/2026-08-28-channel-set-closed.md`.

## Goals until the thesis is in

Canonical list:
`.agents/context/data-analysis/2026-08-23-goal-list.md`.

Science 1–5 (do not invert): behavioural battery → personality → EEG →
trajectories → **all combos** (behaviour × EEG, behaviour × trajectory,
trajectory × EEG, three-way). The insertion-policy model is dropped
(24 August). Delivery: thesis (17 September), paper, **presentation**.
Combos are trajectory stage 5; lab \(n=18\) wherever EEG is in;
association, not mediation. **Opened 27 August** as a joined dataset;
tests that need behavioural composites still wait on Goal 1. Sprint
board: `.agents/context/data-analysis/2026-08-27-backlog-and-timeline.md`.
Paper is optional this sprint if it fights the thesis. Start slides now.

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
  Channel-set / literature-ROI averages are a sensitivity only
  (`eeg/2026-08-24-channel-set-policy.md`,
  `eeg/2026-08-24-literature-roi-from-angela.md`,
  `eeg/2026-08-25-wang-zone-sensitivity.md`,
  `eeg/2026-08-27-angela-code-channel-set.md`). George nine-site,
  Wang-zone, AES-region, and Angela-code lists are hardcoded in
  `channel_sets`. Appendix only (`sec:app-eeg-channel-sets`). Do not
  write them into primary Gold. Do not treat them as a second
  confirmatory family. Cleaning stays on all 32 channels.
- Post-hoc pairwise sweep (Dataset A 10 pairs, Dataset B 6 pairs) is
  **exploratory only** and writes to `statistics/outputs/posthoc/`.
  352 tests, 0 significant under Holm, BH **or** BY, under every family
  definition and all 65,535 feature subsets. Do not re-litigate the
  correction or propose dropping features to gain power: families are
  within-measure, so a subset deletes families rather than shrinking
  them. Nothing there is promoted to confirmatory, whatever its \(p\).
  `eeg/2026-08-28-posthoc-pairwise.md`. How the matched controls
  actually work, and why Dataset B `early_vs_late` is raw-space only:
  `eeg/2026-08-28-dataset-b-control-audit.md`.

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
- `gold/features/sensitivity/`, `gold/windows/sensitivity/` — epoch-width,
  no-ICA, and channel-set branches
  (`sensitivity/channel_sets/<version>/`).
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

### Where the trajectory datasets live

Bronze / Silver / Gold, same contract as EEG. Bronze is the tracked JSONL
(`src/project/logs/tracked/{lab,crowd}/`, prefer `*export*`). Silver is the
rebuildable pass in `build_trajectory_dataset.py` (roster filter, parse,
genre inference \(f_{\mathrm{genre}}\)). It materializes two tables:
`classifier_inputs.csv` (1,080) and `transition_matrices.csv` (715).
Gold is the four tables the analysis reads, two grains:

- Turn: `utterances.csv` (2,160; labels live here) and `transitions.csv`
  (1,620; Family A crossing tests).
- Conversation: `conversations.csv` (540; Defs 3–5) and
  `advertisements.csv` (216; \(g^{(a)}\) for Definition 6).

Off Gold, do not query the Silver tables for tests. Heatmaps rebuild from
`transitions.csv`. Statistics live under `outputs/eda/`, `stages_2_4/`,
`exploratory/` — not Gold.

`conversation_id` is the spine. Join to the rest of the project on
`experiment_id` and `condition`, participant × condition. Both arms, so
\(N=54\). Always select one `genre_source` before counting: `utterance`
is primary (Definition 1); `contextual` is sensitivity (runtime match
1,080/1,080). Details:
`.agents/context/data-analysis/trajectories/2026-08-21-trajectory-dataset-and-first-descriptives.md`.
Medallion lock:
`.agents/context/data-analysis/trajectories/2026-08-23-trajectory-medallion.md`.
Figure: `src/project/docs/trajectory_pipeline/trajectory_pipeline.py`.

The trajectory × EEG merge is verified working. Filter a Gold table to
one `genre_source`, then inner-join `condition_features.csv` on
`["experiment_id", "condition"]`; this yields exactly 90 rows, 18 lab
subjects × 5 conditions. EEG `baseline` does not join. Run
`analysis/trajectories/validate_trajectory_dataset.py` after any rebuild;
it asserts this join among its 79 checks.

## General

- Do not commit or push unless explicitly requested.
