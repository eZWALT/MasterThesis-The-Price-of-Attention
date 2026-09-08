# Gold catalog and lineage (7 September, evening)

One experimental run writes a JSONL event stream. Laboratory runs also
write an XDF. Everything we analyse is a view of that pair, rolled up
to one of **three grains**, split by **two arms**, in **three data
types**. Joins are not a fourth type.

Figure (source of the names):
`src/project/docs/behavioural_pipeline/behavioural_grains.png`.
On Overleaf, not yet included: `figures/gold_tables.png` (thesis),
`Figures/gold_tables.png` (paper), `figures/gold_tables.png` (deck).
Rebuild: `python src/project/docs/behavioural_pipeline/behavioural_grains.py`.

Paper names are the **view**. Filenames stay as provenance. Do not
rename EEG or trajectory Gold on disk. Dataset A / Dataset B keep
those names.

## How to read a row

A person finishes five chats. Each chat is eight utterances (user +
assistant, four turns). Lab has EEG; crowd does not.

| Grain | One row is | Roll-up | Key |
|---|---|---|---|
| Message | one utterance | 8 → 1 chat | `experiment_id` + `condition` + `turn` |
| Chat | one conversation | 5 → 1 person | `experiment_id` + `condition` |
| Person | one finished participant | — | `experiment_id` |

Lab 18 + Crowd 36 = 54 people. That split is an **arm**, not a grain.
Five conditions vs four advertisements, and the wide contrast table,
are **views** of chat or person, not extra grains.

Empty cells are real: trajectories stop at chat (no person table);
EEG starts at chat (no message table); joins start at chat.

## The catalog

`stream.grain.view`. On the figure, stream is the row and grain is the
column, so only the view is printed.

### Behavioural (both arms)

Bronze is the tracked JSONL
(`src/project/logs/tracked/{lab,crowd}/`, prefer `*export*`).
Gold: `analysis/walter/behavioural/outputs/gold/`.
Builder: `analysis/walter/behavioural/build_gold.py`.
Katerina's folder is not Gold.

| View | What it is | File | n (lab · crowd) |
|---|---|---|---|
| **turns** | process: length, latency, both speakers | `messages.csv` | 720 · 1,440 = 2,160 |
| **ratings** | Likert composites + process, five conditions | `condition_features.csv` | 90 · 180 = 270 |
| **recall** | cued recall, four ads (no control) | `advertisement_features.csv` | 72 · 144 = 216 |
| **BFI + demo** | BFI-10 + demographics | `person_features.csv` | 18 · 36 = 54 |
| **contrasts** | three planned \(D\) (same weights as EEG) | `contrast_scores.csv` | 18 · 36 = 54 |

Sibling files, same grain and view, not drawn as their own cards:
`conclusions.csv` sits with ratings; `id_map.csv` sits with BFI + demo.

`demo_age` is empty in the JSONL (crowd age is a Prolific prose
estimate, not Gold). `n_ad_clicked` is measured and is 0. Composites
are the planned formulas; the two manipulation items and the two
notice items stay beside their means; raw `llm_*` stay. Do not drop
items to hunt \(p\).

### Trajectories (both arms, long on `genre_source`)

Gold under `analysis/trajectories/outputs/`. Select **utterance**
before counting (Definition 1). `contextual` is sensitivity.
File totals below include both sources.

| View | What it is | File | n (lab · crowd) |
|---|---|---|---|
| **labels** | genre of each utterance | `utterances.csv` | 720 · 1,440 = 2,160 |
| **turn pairs** | \(\tau_k=(\hat g_k,\hat g_{k+1})\), Family A | `transitions.csv` | 540 · 1,080 = 1,620 |
| **shifts** | chat-level \(N_{\mathrm{shift}}\), entropy, \(\delta^{(a)}\) (Defs 3–5) | `conversations.csv` | 180 · 360 = 540 |
| **ad genre** | \(g^{(a)}\) of the retrieved product (Def 6) | `advertisements.csv` | 72 · 144 = 216 |

**shifts** is not “ad shifts”. Shift *counts* live on `conversations.csv`.
**ad genre** is the product’s label; that file has no shift columns.
There is no trajectory person table.

Silver (`classifier_inputs.csv`, `transition_matrices.csv`) is not
inferential.

### EEG (lab only)

No message table: onset is locked at chat.

| View | What it is | File | n |
|---|---|---|---|
| **Dataset A** | confirmatory condition aggregation, \(k=37\) | `k37/condition_features.csv` | 90 |
| **Dataset A window** | stored whole-window median, includes baseline | `gold/features/condition_features.csv` | 108 |
| **Dataset B** | onset-lock, after − before | `ad_response_features.csv` | 108 |
| **contrasts** | 4 planned \(D\) × 16 features | `eeg_condition_contrast_scores.csv` | 18 people (long 18×4×16) |
| **write − read** | task-state positive control | `task_state_person_features.csv` | 18 |

Do not test epoch rows. Do not treat the whole-window Gold as the
confirmatory Dataset A cell.

### Joins (views, not a grain)

Kitchen-sink tables in Walter Gold. EEG columns are empty on crowd
rows. Association, not mediation. Lab \(n=18\) wherever EEG is filled.

| View | What it is | File | n |
|---|---|---|---|
| **joined chat** | ratings + shifts + Dataset A | `combo_threeway.csv` | 90 · 180 = 270 |
| **joined chat, lab** | same, Dataset A filled | `combo_threeway_lab.csv` | 90 |
| **joined contrasts** | the three contrast tables | `combo_threeway_D.csv` | 18 · 36 = 54 |
| **joined contrasts, lab** | same, Dataset A filled | `combo_threeway_lab_D.csv` | 18 |

Older `combo_condition_*.csv` names are copies. Do not re-join by
hand; the join key is `experiment_id` (+ `condition`, + `turn` at
message). `lab_subject_4_crowdfail` is already out.

## What this is not

- Lab / crowd is not a grain.
- Condition vs advertisement is not a grain.
- Contrast \(D\) is not a grain.
- Joins are not a fourth data type.
- Free text is discarded for analysis.
- The insertion-policy model is dropped. The catalog (Amazon 2023)
  is a different dataset (thesis §4.1), not a fourth experimental type.
