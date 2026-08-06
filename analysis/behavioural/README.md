# Price_of_Attention

Lab experiment exports and analysis scripts for the AdsTalkBack / Price of Attention study.

Participants complete **5 ad conditions** (`block_early`, `block_late`, `inline_early`, `inline_late`, `no_ads`). Event logs live under `Experiment/` as `*_export.jsonl` files. Pilot sessions are under `Pilots/`.

Variable names and event fields are documented in [`variable_dictionary.md`](variable_dictionary.md).

## Requirements

- Python 3.10+ recommended
- Packages used across the scripts/notebooks:

```bash
pip install pandas numpy scipy matplotlib statsmodels jupyter
```

Run commands from this repository root:

```bash
cd RAG-RecSys-data
```

## Data layout

| Path | Description |
|------|-------------|
| `lab_subject_*/**/*_export.jsonl` | Main lab session event logs |
| `Pilots/` | Pilot session exports |
| `variable_dictionary.md` | Event / field reference |

Typical pipeline order:

1. Check whether each participants completed all 5 conditions (`check_condition_completion.py`)
2. Build survey chatpot score CSV (Helpfulness, Credibility etc) from exports (`Analysis_AdsTalkBack.ipynb`)
3. Optionally check timings, and OCEAN correlations (Python scripts below)

---

## Scripts

### `check_condition_completion.py`

Checks whether each participant completed all 5 conditions.

- **Input:** `Experiment/**/*_export.jsonl`
- **Completion rule:** a condition counts as done when `condition_end` is present
- **Also tracks:** `condition_start`, `post_condition_survey_submitted`

```bash
python check_condition_completion.py
```

| Output | Description |
|--------|-------------|
| `participant_condition_completion.csv` | One row per participant (`completed_all`, missing conditions, etc.) |

---

### `calc_condition_task_times.py`

Computes per-condition task duration, reply latency, and message length.

- **Input:** `Experiment/**/*_export.jsonl`
- **Task time:** `condition_end` → `trial_start_ts` to `trial_end_ts`
- **Reply time:** `user_message.data.time_to_reply_ms` inside active conditions (warmup / null first turns skipped)
- **Message length:** `msg_len` for user and assistant messages inside conditions

```bash
python calc_condition_task_times.py
```

| Output | Description |
|--------|-------------|
| `participant_condition_task_times.csv` | One row per participant × condition task |
| `condition_avg_task_times.csv` | Mean/median task time by condition |
| `participant_condition_reply_times.csv` | One row per numeric reply latency |
| `condition_avg_reply_times.csv` | Mean/median reply time by condition |
| `participant_condition_message_lengths.csv` | Per-message lengths |
| `condition_avg_message_lengths.csv` | Mean/median message length by condition |

---

### `calc_condition_ocean_correlations.py`

Condition-specific correlations between post-condition survey scores and OCEAN (BFI-10).

- **Inputs:**
  - `participant_condition_scores.csv` (from `Analysis_AdsTalkBack.ipynb`)
  - `Experiment/**/*_export.jsonl` (`ocean_submitted` / `session_complete`)
- **Metrics:** Spearman ρ (primary), Pearson *r* (secondary)
- **Unit of analysis:** participant **within each condition** separately

Outcomes correlated with OCEAN traits `E`, `A`, `C`, `N`, `O`:

`credibility`, `helpfulness`, `convincingness`, `relevance`, `neutrality`, `behaviour_pushing`, `behaviour_manipulate`

```bash
python calc_condition_ocean_correlations.py
```

| Output | Description |
|--------|-------------|
| `participant_ocean_scores.csv` | OCEAN scores per participant |
| `participant_condition_scores_with_ocean.csv` | Survey scores joined with OCEAN |
| `condition_ocean_correlations.csv` | Full correlation table |
| `condition_ocean_significant_spearman.csv` | Spearman rows with uncorrected *p* < 0.05 |
| `ocean_corr_outputs/analysis_diagram.png` | Analysis flow diagram |
| `ocean_corr_outputs/spearman_heatmap_by_condition.png` | Combined Spearman heatmaps |
| `ocean_corr_outputs/spearman_heatmap_<condition>.png` | Per-condition heatmap |

---

## Notebooks

### `Analysis_AdsTalkBack.ipynb`

Main lab survey analysis notebook.

1. (Optional) inspect export JSON/JSONL
2. Build composite survey scores from `post_condition_survey_submitted` events
3. Create boxplots by condition
4. Save boxplots to disk

```bash
jupyter notebook Analysis_AdsTalkBack.ipynb
# or
jupyter nbconvert --to notebook --execute Analysis_AdsTalkBack.ipynb --inplace
```

| Output | Description |
|--------|-------------|
| `participant_condition_scores.csv` | Credibility, helpfulness, convincingness, relevance, neutrality, personality, and behaviour scores |
| `boxplots_outputs/boxplot_*_by_condition.png` | Boxplots for selected score columns |

**Note:** run the “create boxplots” cell before the “save boxplots” cell (figures are stored in `boxplot_figures`).

---

### `Analysis_pilots.ipynb`

Exploratory analysis of **pilot** exports under `Pilots/` (and related `exp_*` folders). Loads JSONL into a flat table, inspects conditions, and plots Likert / survey responses. Intended for pilot exploration rather than the main lab pipeline.

---

## Suggested run order

```bash
# 1. Survey composites + boxplots
jupyter nbconvert --to notebook --execute Analysis_AdsTalkBack.ipynb --inplace

# 2. Completion check
python check_condition_completion.py

# 3. Timing / reply / message-length summaries
python calc_condition_task_times.py

# 4. OCEAN correlations (needs participant_condition_scores.csv)
python calc_condition_ocean_correlations.py
```

## Output folders

| Folder | Produced by |
|--------|-------------|
| `boxplots_outputs/` | `Analysis_AdsTalkBack.ipynb` |
| `ocean_corr_outputs/` | `calc_condition_ocean_correlations.py` |

## Conditions

| Condition ID | Meaning (short) |
|--------------|-----------------|
| `block_early` | Explicit ad block, early turn |
| `block_late` | Explicit ad block, late turn |
| `inline_early` | Inline ad, early turn |
| `inline_late` | Inline ad, late turn |
| `no_ads` | No ads |
