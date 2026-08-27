# Trajectory dataset pipeline figure

Date: 23 August 2026

## What this is

The thesis-page figure of genre-trajectory **dataset construction**, in
the same diagrams-as-code language as `catalog_pipeline.py`.

- Working figure: `src/project/docs/trajectory_pipeline/trajectory_pipeline.py`
  → `trajectory_pipeline.png` / `.pdf`
- Rebuild: `python3 src/project/docs/trajectory_pipeline/trajectory_pipeline.py`
  (needs `diagrams`, Graphviz, Nimbus Sans — same env as catalog / arch)

Canonical lock (zones, grains, joins):
`2026-08-23-trajectory-medallion.md`.

## On the figure

| Zone | What | On the figure |
|---|---|---|
| Bronze | Tracked JSONL, immutable. Prefer `*export*`. | Tracked JSONL · N = 54 |
| Silver ops | Roster filter, parse, genre inference (\(f_{\mathrm{genre}}\)). | Filter → Parse → Genre inference |
| Silver tables | `classifier_inputs.csv` (1,080), `transition_matrices.csv` (715) | two table cards |
| Gold, turn grain | `utterances.csv` (2,160), `transitions.csv` (1,620) | cylinder card |
| Gold, conversation grain | `conversations.csv` (540), `advertisements.csv` (216) | cylinder card |

Off the figure: validator, EDA, stages 2–4. `genre_source` is a row
inside Gold, not a zone. Files stay flat under
`analysis/trajectories/outputs/`.

## Keep

- Three clusters: Bronze / Silver / Gold.
- Two Gold cards, four files named. Not four Gold icons.
- Silver = table icon; Gold = database cylinder.
- Short labels. No runtime-match rates, no Def 6 prose, no join footnote.
- Orthogonal routing (`splines: ortho`), same language as the catalogue figure.
