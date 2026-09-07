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
- `eeg/2026-08-20-what-dataset-b-onset-is.md` — Dataset B onset is when the
  ad becomes visible. After-reply lock rejected; keep golden.
- `2026-08-23-goal-list.md` — **canonical until thesis**: science 1–5
  (Goal 5 = all behavioural × trajectory × EEG combos) plus thesis,
  paper, presentation. Insertion-policy model dropped 24 August:
  `2026-08-24-insertion-policy-model-dropped.md`.
- `eeg/2026-08-28-channel-set-closed.md` — **28 August save.**
  Angela / channel-set retry closed. Primary 32-ch stays
  confirmatory. Do not pick electrodes by \(p\).
- `eeg/2026-08-28-posthoc-pairwise.md` — backlog item 2 bounded:
  exhaustive pairwise sweep (Dataset A 10 pairs, Dataset B 6 in
  \(\Delta\) space + raw companion). Exploratory; nothing promoted.
  Rests on `eeg/2026-08-28-dataset-b-control-audit.md`, which is the
  source of truth for the matched controls and shows Dataset B
  `early_vs_late` is raw-space only.
- `eeg/2026-08-31-equal-n-k37.md` — confirmatory Dataset A is the
  median of \(k=37\) tiles nearest visual onset (shortest chat).
  Applied and pushed to Overleaf 31 August. Gold whole-window is not
  overwritten.
- `../writing/2026-09-05-sprint-to-deadline.md` — **live sprint
  (5 Sep).** Thesis 17 Sep. Katerina back (two Holm survivors);
  do not permute items to hunt \(p\). Combos still wait on Goal 1
  freeze.
- `eeg/2026-08-29-ad-local-epochs.md` — exploratory. Median \(k\)
  tiles around ads instead of Dataset A's whole-condition average.
  \(k=5\) and \(k=10\) do not create Dataset A hits. Not confirmatory.
- EEG Holm MDE withdrawn 6 September. Do not put dB MDE ranges back
  in the manuscripts. Historical write-up:
  `../writing/2026-08-31-thesis-eeg-mde.md`.
  Do not write “approached significance”.
- `2026-08-27-backlog-and-timeline.md` — **live sprint (27 Aug)**:
  five pending analyses (item 1 closed 28 Aug; EEG post-hoc,
  behavioural EDA, free-text, joined dataset / combos still open).
  Thesis first, paper optional, presentation starts now. Goal 1
  still gates honest combo tests.
- `eeg/2026-08-27-dataset-a-b-rename.md` — Path A/B is dead; Dataset A
  = condition aggregation, Dataset B = ad-onset contrast. Figures rebuilt
  the same day so pixels match (`3fe3243`). Catch-up:
  `../writing/2026-08-27-afternoon-save.md`.
- `behavioral/2026-08-27-crowd-age-prolific-estimate.md` — Results 7.1
  crowd age is a prose-only Prolific snapshot, **not Gold**.
- `2026-08-18-analysis-priority-order.md` — older five-item list;
  superseded for open work.
- `eeg/2026-08-20-paper-figures-and-narrative.md` — paper/thesis EEG
  figure cut and what the Holm-nulls allow you to say.
- `eeg/2026-08-24-channel-set-policy.md` — which electrodes enter the
  16 spectral formulas. Default `current_v1` is primary Gold.
  Literature ROI (`literature_roi_v0`) is the nine sites George and
  Gulia 2025 recorded, same list for every band; Wang zone
  (`wang2022_v0`), AES regions, and Angela's code lists
  (`angela_code_v0`) are extra sensitivities. Do not overwrite Gold.
  `eeg/2026-08-24-literature-roi-from-angela.md`,
  `eeg/2026-08-25-wang-zone-sensitivity.md`,
  `eeg/2026-08-27-angela-code-channel-set.md`.
- Crossable leftover list (analysis + manuscripts):
  `../writing/2026-08-18-remaining-work-checklist.md`.

- `policy/` — **side project, not a thesis goal.** 6 September produced
  a human-\(U\) residual scorer, not \(m(s)\) or \(q(s,a)\). Start at
  `policy/README.md`, then
  `policy/2026-09-06-residual-scorer-and-next-ms-qsa.md`
  (done vs not done; next estimands). Winner numbers:
  `policy/2026-09-06-evening-handoff.md`. Code under `analysis/policy/`.
  Nothing enters thesis / paper / deck before 17 September.

## Analysis arms

- `behavioral/`: behavioural ETL, scoring, outcome definitions, exclusions,
  model specifications, and audit summaries.
- `eeg/`: recording audits, marker reconstruction, preprocessing, feature
  definitions, exclusions, and EEG model specifications.
- `trajectories/`: genre-trajectory dataset, the ThradBERT labelling
  decision, and the shift descriptives. Start at `trajectories/README.md`.
  Medallion (Bronze / Silver / Gold, same contract as EEG):
  `trajectories/2026-08-23-trajectory-medallion.md`. Direction:
  `trajectories/2026-08-23-analysis-direction.md` (five stages; stage 5
  blocked). First run of stages 1–4:
  `trajectories/2026-08-23-direction-pass.md`. Dataset and first-pass lock:
  `trajectories/2026-08-21-trajectory-dataset-and-first-descriptives.md`.
  Walter decided on 21 Aug that \(f_{\mathrm{genre}}\) is the **bare
  utterance**, Definition 1 read literally, with the deployed contextual
  labelling as the sensitivity analysis. That flip made the negative control
  pass on the first test and revealed that the apparent task dominance
  (Kruskal H = 43 versus 4.6) was leakage from the contextual classifier's own
  input. The note also records that advertisements do not move the trajectory
  while conversational depth clearly does, that Definition 6's `delta-tilde` is
  at chance rather than merely rare (9 of 108 against 10.5 under permutation,
  p = 0.80), and that `purchasable_products` reaches only 19 of 1,080
  utterances and 4 of 156 advertised products. Read Section 0 of
  `outputs/inference.md` before quoting the positive control: part
  of the turn drift is a message-length artefact.

Generated datasets, manifests, figures, and executable analysis code remain under
`analysis/`. Context documents summarize what those artifacts establish and the
decisions made from them; they should not duplicate raw participant data.
