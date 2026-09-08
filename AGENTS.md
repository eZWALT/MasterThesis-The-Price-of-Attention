# Agent entrypoint

Operational router. Dated history lives under `.agents/context/`. Do
not treat this file as a changelog or a Results number sheet.

| File | Role |
|---|---|
| Root `README.md` | Human landing page: what the study is, how to launch the app. **Not** analysis status. |
| `src/project/README.md` | How to run the Streamlit platform. Leave that tree alone unless the task is the app. |
| `AGENTS.md` | This file. Hard stops + which Live now box to open next. |

> **CRITICAL (EEG / ICA).** Do not run `fit_ica_cohort.py --overwrite` or
> `run_ica_sensitivity.py --overwrite-models`. Do not replace files under
> `src/project/logs/xdf/silver/ica/candidate_v1/`. Those 18 models are
> human-signed (2026-08-19). Full stop:
> `.agents/context/data-analysis/eeg/CRITICAL-do-not-overwrite-ica-models.md`

## Read next, then stop

| Track | Open this, then **stop at Live now** |
|---|---|
| Code map | `analysis/README.md` |
| Science | `.agents/context/data-analysis/README.md` → Live now box, then the arm README |
| Manuscripts | `.agents/context/writing/README.md` → Live now box |
| Side project | `.agents/context/data-analysis/policy/README.md` |

Dated notes below those boxes are history. Do **not** follow “newest
dated filename” past Live now.

**Do not use as live status:** root `README.md`, `.agents/README.md`,
the 5 September “Combos wait on that freeze” paragraph, or
`analysis/eeg/preprocessing/README.md` as a runbook.

## Hard stops

- Do not commit or push unless asked.
- Manuscript source of truth is only the Overleaf mirrors under
  `docs/overleaf/` (`publication/`, `thesis/`, `presentation/`). Context
  notes never override LaTeX. Pull before drafting; show text before
  applying; push only after explicit approval.
- Do not overwrite live `conclusion.tex`.
- Do not put the ad-moment scorer in thesis / paper / deck before
  17 September. Do not rebuild its Silver unless asked.
- Do not pick a \(k\), montage, or questionnaire item by \(p\) or
 by item–item correlation. Katerina's 8 Sep ask to drop
 `llm_reliable` / `llm_opinionated` / `llm_skeptical` is **held**;
 answered as a sensitivity-only appendix (thesis `sec:app-beh-items`),
 composites unchanged:
 `.agents/context/data-analysis/behavioral/2026-09-08-item-correlations-held.md`.
- Leave `src/project/` application code alone unless the task is the
  platform itself.
- **`analysis/behavioural/` is Katerina’s tree. Do not open, edit, run,
  quote, or rebuild anything in it.** Exception, 8 Sep only:
  `Cronbach_alpha.py` no longer reverse-codes at parse (α still
  does `8-x` once). Canonical behavioural Gold and Results numbers
  come only from `analysis/walter/behavioural/`.
- **Never run** `python analysis/eeg/preprocessing/run_pipeline.py`.
  Default order rebuilds whole-window feature Gold. Dataset A tables:
  only `run_equal_n_dataset_a.py`, and only if asked.
- **Never quote** `analysis/eeg/analysis/outputs/figures/suite/`
  rainclouds as confirmatory \(k=37\). Those plots read whole-window
  Gold (`condition_features.csv`). Confirmatory Dataset A is
  `analysis/eeg/statistics/outputs/eeg_condition_*.csv`. Three output
  trees: `analysis/README.md`.
- `build_condition_contrasts.py` with default paths **refuses** to
  overwrite confirmatory \(k=37\) once the estimand marker is set.
  Do not pass `--force-overwrite-confirmatory`.
- Start-here commands below **rebuild frozen artefacts**. Do not run
  them unless asked.

## Writing locks

- **Results ≠ Discussion.** Results report estimands and numbers.
  Discussion interprets. EEG interpretation is `sec:disc-eeg`, not
  Results. Trajectories (Defs 1–6, Results, Discussion) are
  **thesis-only**.
- **Figure first.** One claim, then the artefact, then only what the
  visual cannot say. Holm \(p\) is the Holm-adjusted paired \(t\).
  Wilcoxon \(p\) is raw. Never write “Wilcoxon Holm”. Rule:
  `.cursor/rules/results-figure-first.mdc`.
- **Discussion.** Interpret estimated families only. Do not restore
  “depends on how and when”, “greater visual processing”,
  explicit-late-as-compromise, a serving-rule *price of attention*,
  MDE / Holm-80% / “approached significance”, or `sec:disc-summary`.
  Rule: `.cursor/rules/discussion-interpret-not-serve.mdc`.
  Lock: `.agents/context/writing/2026-09-06-conclusion-critique-and-ch8.md`.
- **Names.** implicit vs explicit (not subliminal); early = turn 2,
  late = turn 4; five-condition RM + no-ad. Log keys stay `inline_*` /
  `block_*`. Dataset A / Dataset B, never Path A/B. Dataset A display
  name is **condition aggregation** (\(k=37\)), not “equal-n
  neighbourhood” or “condition state”. Genre classifier is
  \(f_{\mathrm{genre}}\), not \(f_\theta\).
- **MDE withdrawn.** Do not put `eq:mde`, Holm-80% dB ranges, or
  observed-power paragraphs back in thesis, paper, or deck.
- **Gold catalog.** Paper names on the figure; filenames are
  provenance. `advertisements.csv` is **ad genre**, not ad shifts.
  Demographics sit on **BFI + demo**.
  `.agents/context/data-analysis/2026-09-07-gold-catalog-and-lineage.md`.

Deck notes stay under `.agents/context/writing/`. Do not rewrite
Walter’s spoken slides.

## Current science state (8 September)

Science 1→5 is done as *analyses*. Thesis write-up is in progress
(deadline **17 September**). Defence is **23 September** morning
in Padova, not 18–20. Calendar:
`.agents/context/writing/2026-09-08-travel-and-delivery-calendar.md`.
Live now boxes override this table.

| Goal | Status | Where |
|---|---|---|
| 1 Behavioural battery | Frozen. Ch 7.2 / 8.1 **applied** (thesis `15cf438`). Paired \(t\) primary. | `analysis/walter/behavioural/` |
| 2 Personality | On person Gold with BFI | same |
| 3 EEG | Confirmatory frozen (4 s, median, ICA, \(k=37\)) | `analysis/eeg/` |
| 4 Trajectories | Stages 1–4 frozen; utterance primary | `analysis/trajectories/` |
| 5 Combos | Declared families **applied** (thesis `d206df3`). Dataset A 0/6; Dataset B trust × posterior \(\alpha\) \(\rho=.80\). | `analysis/walter/combos/run_thesis_families.py` |

Insertion-policy \(\pi\) as a Results model is dropped. The residual
scorer under `analysis/policy/` is a **side project**.

## Data analysis — where things live

Participants, not epochs, are the inferential unit. Join on
`experiment_id`. Verify numbers against code and manifests. Bronze /
XDF stay immutable.

### EEG

Code: `analysis/eeg/`. Data: `src/project/logs/xdf/`.

- Gold whole-window (storage): `gold/features/condition_features.csv`,
  `ad_response_features.csv`,
  `gold/features/task_state/task_state_person_features.csv`.
- **Confirmatory Dataset A** is condition aggregation \(k=37\) in
  `analysis/eeg/statistics/outputs/eeg_condition_*.csv`.
- Epoch-grain `*_epoch_features.csv` must not be tested as people.
- Channel-set / post-hoc pairwise / ad-local \(k\) are sensitivity or
  exploratory. Appendix only. Cleaning stays 32-ch.

### Behavioural

Bronze: `src/project/logs/tracked/{lab,crowd}/` (prefer `*export*`).
Roster: drop `synthetic` / `unfinished` / `crowdfail`; keep
`unfocused`. \(L=18\), \(C=36\), \(N=54\).

Gold: `analysis/walter/behavioural/outputs/gold/`
Rebuild (only if asked): `python analysis/walter/behavioural/build_gold.py`.

### Combos

Read the joined views; do not re-join by hand. Lab-only wherever EEG
is in (\(n=18\)); association, not mediation.

Thesis entry: `python analysis/walter/combos/run_thesis_families.py`.
`combokit.spearman_ci` aligns pandas Series on their index
(`experiment_id`). Align before passing numpy arrays.
`run_combos.py` (2,560 tests) is the exploratory map, not Results.

### Trajectories

Gold (flat under `analysis/trajectories/outputs/`): `utterances.csv`
(labels), `transitions.csv` (turn pairs), `conversations.csv`
(shifts), `advertisements.csv` (ad genre). Always select one
`genre_source` (`utterance` primary). QC (only if asked):
`python analysis/trajectories/validate_trajectory_dataset.py`.

### Policy (not a thesis goal)

`analysis/policy/`. Residual ridge locked; next is \(m(s)\) / \(q(s,a)\).

## Rebuild commands (only if asked)

```bash
python analysis/walter/behavioural/build_gold.py
python analysis/walter/behavioural/stats/run_confirmatory.py
python analysis/eeg/statistics/run_equal_n_dataset_a.py
python analysis/walter/combos/run_thesis_families.py
python analysis/trajectories/validate_trajectory_dataset.py
```
