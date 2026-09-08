# Gold tables

```bash
python src/project/docs/behavioural_pipeline/behavioural_grains.py
```

`behavioural_grains.png` / `.pdf`. Same image also written as
`behavioural_lineage.*`.

| Grain | One row | Roll-up |
|---|---|---|
| Message | one utterance | 8 → 1 chat |
| Chat | one conversation | 5 → 1 person |
| Person | one person | — |

## Catalog

A table is `stream.grain.view`. The figure shows only **view**: stream
is the row, grain is the column. Dataset A / Dataset B keep those
names. Files are provenance, not titles. Do not rename EEG or
trajectory Gold on disk.

| ID | View on figure | File |
|---|---|---|
| `beh.msg.turns` | turns | `messages.csv` |
| `beh.chat.ratings` | ratings | `condition_features.csv` (+ `conclusions.csv`) |
| `beh.chat.recall` | recall | `advertisement_features.csv` |
| `beh.person.BFI` | BFI + demo | `person_features.csv` (+ `id_map.csv`) |
| `beh.person.contrasts` | contrasts | `contrast_scores.csv` |
| `traj.msg.labels` | labels | `utterances.csv` |
| `traj.msg.pairs` | turn pairs | `transitions.csv` |
| `traj.chat.shifts` | shifts | `conversations.csv` |
| `traj.chat.adgenre` | ad genre | `advertisements.csv` |
| `eeg.chat.A` | Dataset A | `k37/condition_features.csv` |
| `eeg.chat.A.window` | Dataset A window | `gold/features/condition_features.csv` |
| `eeg.chat.B` | Dataset B | `ad_response_features.csv` |
| `eeg.person.contrasts` | contrasts | `eeg_condition_contrast_scores.csv` |
| `eeg.person.writeread` | write − read | `task_state_person_features.csv` |
| `join.chat` | joined chat | `combo_threeway.csv` |
| `join.chat.lab` | joined chat, lab | `combo_threeway_lab.csv` |
| `join.person.contrasts` | joined contrasts | `combo_threeway_D.csv` |
| `join.person.contrasts.lab` | joined contrasts, lab | `combo_threeway_lab_D.csv` |

Joins are a view, not a fourth grain. Empty cells are real:
trajectories have no person table; EEG has no message table; joins
start at chat.

`utterances.csv` / `conversations.csv` are long on `genre_source`
(2,160 = 1,080 × 2; 540 = 270 × 2). Select one source before counting.

Join keys: message / chat = `experiment_id` + `condition` (+ `turn`);
person = `experiment_id`. EEG is lab only.
