# Dataset release (side quest)

**Superseded for hub layout** by
`2026-09-16-hf-dataset-strategy.md` (streams × grains × lineage;
`gold` / `events` / `eeg-recordings`; no RAW/PROCESSED). This file
keeps the inventory of what exists on disk.

**Not this weekend. Not a thesis goal.** Same shelf as the ad-moment
scorer: do not put a release plan in the abstract, Ch 9, or the deck
before 17 September. Open this only after the PDF is in.

The study produced several grains, not one file. Do not upload “the
repo”. Ship layers, in this order.

## What exists

| Layer | Where | Public? |
|---|---|---|
| Bronze events | `src/project/logs/tracked/{lab,crowd}/` (~24 MB) | Yes, after de-id check |
| Bronze EEG | `src/project/logs/xdf/` Bronze (~4.1 GB) | No, unless a later gated drop |
| Silver EEG / ICA | `…/xdf/silver/ica/candidate_v1/` (18 signed models) | Separate gated dataset, or not at all |
| Gold behavioural | `analysis/walter/behavioural/outputs/gold/` \(N=54\) | Yes. Not `analysis/behavioural/` |
| Gold trajectories | `analysis/trajectories/outputs/*.csv` (utterance primary) | Yes |
| Gold EEG tests | `analysis/eeg/statistics/outputs/eeg_condition_*.csv` (\(k=37\)) | Yes |
| Combo joins | `analysis/walter/combos/outputs/` | Yes |
| Catalog / Amazon JSONL | `src/project/data/catalogs/` (gitignored) | License first; probably no |
| Policy silver/gold | `analysis/policy/outputs/` (591 MB) | No. Other side quest |

## Strategy (when we come back)

1. **RAW, gated** — `scripts/upload_raw_dataset.py` →
   `eZWALT/Price-of-Attention-RAW`. Tracked JSONL + lab XDF only.
   Dry-run. Ethics / consent / timestamps / Prolific IDs first.
2. **GOLD, public** — one dataset card, four folders: `behavioural/`,
   `trajectories/`, `eeg/`, `combos/`. The tables the thesis quotes.
   One `README` that says utterance context is primary and Dataset A
   is condition aggregation \(k=37\).
3. **ICA / features, gated or skip** — do not mix into GOLD.
4. **Never in the first drop** — Bronze XDF dump, Amazon catalog,
   Katerina’s tree, policy outputs, `resources/papers/`.

Two Hugging Face repos is enough. A third only if ICA ships.

Script already written for step 1. Step 2 needs a new uploader that
reads Gold paths from `analysis/README.md`, not a folder walk.
