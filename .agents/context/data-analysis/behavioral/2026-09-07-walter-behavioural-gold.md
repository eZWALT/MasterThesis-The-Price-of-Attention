# Walter behavioural Gold (7 September, afternoon)

Canonical behavioural Gold moved to
`analysis/walter/behavioural/outputs/gold/`.
Builder: `analysis/walter/behavioural/build_gold.py`.
Notebook: `analysis/walter/behavioural/Behavioural_EDA.ipynb`.

Katerina's folder (`analysis/behavioural/`) is left alone. Her lab
Likert CSV is still only a scoring check.

Composites are the planned formulas. The two manipulation items and
the two notice items stay as columns beside `manipulation` and
`notice`. Raw `llm_*` items are on the condition table. Do not drop
items to hunt \(p\).

`contrast_scores.csv` is 54 rows (same three \(D\) as EEG). The
kitchen-sink joins are `combo_threeway.csv` (270) and
`combo_threeway_D.csv` (54): all behavioural columns, all utterance
trajectory metrics, all 16 Dataset A \(k=37\) EEG medians / \(D\).
EEG is NA on crowd rows. Lab slices are `_lab` / `_lab_D`.
EDA tables and figures: `analysis/walter/behavioural/outputs/eda/`.

## Three grains

Message (2,160) → chat (270) → participant (54). Lab / crowd is an
arm split. The 4-ad table and the wide \(D\) table are **views**, not
grains. `messages.csv` is the process view of the message grain;
trajectory `utterances.csv` is the labelled view of the same grain.

Map: `src/project/docs/behavioural_pipeline/behavioural_grains.png`.
Human catalog (paper names, what each view is, empty cells):
`../2026-09-07-gold-catalog-and-lineage.md`.

Paper names: **turns**, **ratings**, **recall**, **BFI + demo**,
**contrasts**. `conclusions.csv` sits with ratings; `id_map.csv`
sits with BFI + demo. Demographics are on `person_features.csv`,
not a separate table (`demo_age` empty).
