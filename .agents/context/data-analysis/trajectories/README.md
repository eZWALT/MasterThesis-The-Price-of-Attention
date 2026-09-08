# Genre-trajectory analysis context

This directory holds durable decisions for the trajectory arm. Executable
code, generated tables, and figures stay under `analysis/trajectories/`.

## Current entries

- Shared catalog (7 Sep): trajectory Gold is **labels**, **turn pairs**,
  **shifts**, **ad genre** on the three-grain figure. No person table.
  `advertisements.csv` is ad genre, not ad shifts.
  `../2026-09-07-gold-catalog-and-lineage.md`.
- `2026-08-23-trajectory-medallion.md`
  **Canonical Bronze / Silver / Gold lock.** Gold is the four tables
  analysis reads, two grains (message + chat in the shared figure).
  Silver tables are provenance / kernels, not inferential. Files stay
  flat under `analysis/trajectories/outputs/`.
- `2026-08-23-trajectory-pipeline-figure.md`
  Diagrams-as-code figure of that lock. Rebuild:
  `src/project/docs/trajectory_pipeline/trajectory_pipeline.py`.
  Thesis copy: `figures/preprocessing/trajectory_preprocessing.png`.
- `2026-08-23-contextual-sweep.md`
  six context windows for ThradBERT. No recipe clears .05. The live
  window is sticky because of the task prompt; dropping the task does
  not produce an ad effect. Closest p is 0.096 and the wrong sign.
- `2026-08-23-exploratory-pass.md`
  exploratory only, never confirmatory. Continuous redirection on
  posterior mass (with a working late-ad placebo), the no-hidden-responders
  variance test, the transition-matrix omnibus, and the 162-cell slice grid
  priced against a max-|t| randomisation null. Also records the
  `gee_crossing()` import bug that had been printing `model failed` into
  the stages 2–4 report.
- `2026-08-23-stages-2-4.md`
  confirmatory family A on the crossing estimand, δ-tilde permutation,
  type moderation, late as negative control. Figure cut decided.
  Canvas: `analysis/trajectories/trajectory-stages-2-4.canvas.tsx`.
- `2026-08-23-eda-stage-1.md`
  stage 1 proper: deep EDA, seven tables, eight figures, the variance
  checks, the label-validity subsection, and the diversity-ceiling
  correction. Figure cut decided 23 Aug (three paper figures). Canvas copy:
  `analysis/trajectories/trajectory-eda-stage1.canvas.tsx`.
- `2026-08-23-direction-pass.md`
  first run of stages 1–4. Heatmaps and report live under
  `analysis/trajectories/outputs/`.
- Stage 5 (EEG × behavioural × all combos) **ran 7 September**.
  Thesis entry: `analysis/walter/combos/run_thesis_families.py`.
  This August note still says “blocked”; ignore that sentence.
  Goal list: `../2026-08-23-goal-list.md`.
- `2026-08-21-trajectory-dataset-and-first-descriptives.md`
  dataset build, schema lock (`conversation_id` spine, long on
  `genre_source`), Walter's call that \(f_{\mathrm{genre}}\) is the bare utterance,
  first descriptives, and first-pass inference. Open questions left at
  the end are write-up only (lead sentence, §5.8, one §3 disclosure).

## Standing decisions

- Primary labelling is the bare utterance. Contextual (deployed) is
  sensitivity. Flip `PRIMARY_SOURCE` in all three analysis scripts
  together, never one alone.
- `delta`-tilde stays in the paper, reported as specified but at chance.
- Participant is the inferential unit, \(N=54\). Binary tests sit on the
  advertisement-crossing transition, not on conversation-level "did it
  shift."
- Run `validate_trajectory_dataset.py` after any rebuild; it must report
  79 passed, 0 failed.
- Diversity and entropy are bounded by \(T=4\), not by the 13 classes.
  Ceilings are 3 shifts, 4 genres, \(\ln 4\) nats, 4 turns of persistence.
  Always report the ceiling next to the mean.

Generated numbers live in `analysis/trajectories/outputs/inference.md`,
`descriptives.md`, and `advertisements.md`. Quote those, not this
directory, when a figure or p-value is needed.
