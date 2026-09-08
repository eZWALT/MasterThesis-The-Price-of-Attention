# Behavioural Gold and combo-ready joins (7 September)

Walter asked for combo tables and for process variables that the
Likert-only scoring never used.

Builder: `analysis/behavioural/build_behavioural_gold.py`.
Contract: `analysis/behavioural/outputs/gold/README.md`.

## What exists now

| File | Rows | Grain |
|---|---|---|
| `id_map.csv` | 54 | person |
| `person_features.csv` | 54 | BFI + demographics |
| `condition_features.csv` | 270 | surveys + process |
| `advertisement_features.csv` | 216 | + cued recall |
| `conclusions.csv` | 270 | findings text |
| `combo_condition_all.csv` | 270 | + utterance trajectories |
| `combo_condition_lab.csv` | 90 | + Dataset A \(k=37\) EEG |
| `combo_contrast_lab.csv` | 18 | same \(D\) on surveys / process / EEG |

Joins assert: 18 lab + 36 crowd; no `crowdfail`; no duplicate
`experiment_id` × `condition`; trajectory `n_shift` complete on 270;
EEG `eeg_fz_theta` complete on 90; EEG \(D_i\) complete on 18.

Lab Likert on the 18 finished subjects matches Katerina's
`participant_condition_scores.csv` exactly (max abs 0). The extra
hashed id in her file is `1384a95c` = `lab_subject_4_crowdfail`.
She never scored the 36 crowd sessions.

Credibility Cronbach \(\alpha = 0.78\) on all 270 rows (items already
reversed). Report statistic, not a hunt.

## She used self-report. The logs have more

Every finished condition has four user messages. The JSONL already
stores duration (`trial_start_ts` / `trial_end_ts`),
`time_to_reply_ms`, `msg_len`, typing, `ad_injected` / `ad_displayed`,
findings text, and cued recall. Those are now columns.

`ad_clicked` exists as an event type and is **0 / 216 ads** in this
cohort. Keep the column. Do not write “clicks were not logged”.

`demo_age` is empty in every `demographics_post_submitted`. Crowd age
stays the Prolific prose estimate.

## What this does not do

No Goal 1 confirmatory tests. No item permutation. No combo \(p\)
values. The three combo views are joins so Goal 5 can start the
moment the composites freeze. Association, not mediation. Lab
\(n=18\) wherever EEG enters.

EEG on T1 is the confirmatory \(k=37\) neighbourhood medians, not
whole-window Gold. T2 uses `eeg_condition_contrast_scores.csv`.
Trajectory side is `genre_source == utterance` only.
