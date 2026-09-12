# Analysis

Thesis analyses live here. The running RAG / RecSys app stays in
`src/project/` and is not this tree.

Science decisions: `.agents/context/data-analysis/README.md`.
Operational locks and how memory works: `AGENTS.md`.
Weekend prose board: `.agents/context/writing/2026-09-12-weekend-finish-board.md`.

## Arms

| Path | Role | Gold / reported tables |
|---|---|---|
| `walter/behavioural/` | **Canonical behavioural Gold** (Goal 1) | `walter/behavioural/outputs/gold/` |
| `walter/combos/` | Goal 5 associations | `walter/combos/outputs/thesis/` |
| `eeg/` | Preprocessing + confirmatory EEG | features: `src/project/logs/xdf/gold/`; contrasts: `eeg/statistics/outputs/` |
| `trajectories/` | Genre trajectories (thesis-only) | `trajectories/outputs/*.csv` |
| `policy/` | Ad-moment scorer (**not** a thesis goal) | `policy/outputs/` |
| `behavioural/` | Katerina’s original scripts. **Not Gold.** | — |

Shared helpers: `walter/statkit.py`, `walter/viz.py`.

## Which script to run

| Need | Command |
|---|---|
| Rebuild behavioural Gold | `python analysis/walter/behavioural/build_gold.py` |
| Goal 1 freeze | `python analysis/walter/behavioural/stats/run_confirmatory.py` |
| Confirmatory Dataset A (\(k=37\)) | `python analysis/eeg/statistics/run_equal_n_dataset_a.py` |
| Thesis combo families (Ch 7.5) | `python analysis/walter/combos/run_thesis_families.py` |
| Trajectory QC | `python analysis/trajectories/validate_trajectory_dataset.py` |

Do **not** use these as the thesis entry point:

- `analysis/eeg/statistics/build_condition_contrasts.py` with default
  paths — writes whole-window Dataset A over the confirmatory \(k=37\)
  tables. Sensitivities may call it with an explicit `--output-dir`.
- `analysis/walter/combos/run_combos.py` — 2,560-test exploratory map.
- Anything under `analysis/behavioural/` for new Gold or Results numbers.

## Join rule

The key is `experiment_id`. EEG exists only on the laboratory arm
(\(n=18\)). Filter trajectories to one `genre_source` before counting
(`utterance` is primary). Participants, not epochs, are the inferential
unit.

## Output trees (EEG)

Three roots, on purpose. Do not merge them.

- `src/project/logs/xdf/gold/` — feature Gold (whole-window Dataset A
  is stored here; confirmatory tests do not use that median).
- `analysis/eeg/statistics/outputs/` — inferential tables. Dataset A
  here is condition aggregation \(k=37\).
- `analysis/eeg/analysis/outputs/` — publication figures and reports.
