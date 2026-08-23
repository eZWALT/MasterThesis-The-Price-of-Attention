# Trajectory Bronze / Silver / Gold

Date: 23 August 2026. Same contract as EEG. Gold is the tables the
**analysis reads**, not every CSV the builder writes.

Files stay **flat** under `analysis/trajectories/outputs/`. Do not move
them into `outputs/{bronze,silver,gold}/` unless Walter asks.
`genre_source` is a **row inside Gold**, not a zone.

Figure (diagrams-as-code): `src/project/docs/trajectory_pipeline/trajectory_pipeline.py`.
Thesis copy: `docs/overleaf/thesis/figures/preprocessing/trajectory_preprocessing.png`.

## Zones

| Zone | What |
|---|---|
| **Bronze** | Tracked JSONL, immutable. `src/project/logs/tracked/{lab,crowd}/`. Prefer `*export*`. \(N=54\) (\(L=18\), \(C=36\)). Out: unfinished, synthetic, crowdfail, beta. In: finished `unfocused` if instruments complete. |
| **Silver ops** | In memory in `build_trajectory_dataset.py`: roster filter, parse four turns, genre inference \(f_{\mathrm{genre}}\). Do not test here. |
| **Silver tables** | `classifier_inputs.csv` (1,080, provenance) and `transition_matrices.csv` (715, faceted kernel). Heatmaps rebuild from Gold `transitions.csv`. |
| **Gold, turn grain** | `utterances.csv` (2,160; labels live here) and `transitions.csv` (1,620; Family A crossing / McNemar / GEE). |
| **Gold, conversation grain** | `conversations.csv` (540; Defs 3–5) and `advertisements.csv` (216; \(g^{(a)}\) for Def 6). One row per advertised conversation; not long on `genre_source`. |

Statistics (`outputs/eda/`, `stages_2_4/`, `exploratory/`) are **outside** Gold.

`build_report.json` is a build manifest, not a zone.

## Joins

`conversation_id` is the spine. To the rest of the project: `experiment_id`
+ `condition`, participant × condition. Both arms, so \(N=54\).

Trajectory × EEG: filter a Gold table to one `genre_source`, inner-join
`condition_features.csv` on `["experiment_id", "condition"]` → 90 rows
(18 lab × 5). EEG `baseline` does not join.

Always select one `genre_source` before counting. Primary is `utterance`
(Definition 1, bare message). `contextual` is sensitivity (runtime
1,080/1,080).

Run `analysis/trajectories/validate_trajectory_dataset.py` after any
rebuild; 79 checks, 0 failed.

Code identifiers (`GenreClassifier`, `PRIMARY_SOURCE`) stay. Notation in
prose is \(f_{\mathrm{genre}}\), not \(f_\theta\).
