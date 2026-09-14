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
2. Build survey chatbot score CSV (Helpfulness, Credibility etc) from exports (`Analysis_AdsTalkBack.ipynb`)
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

All outputs are written to `ocean_corr_outputs/`.

| Output | Description |
|--------|-------------|
| `ocean_corr_outputs/participant_ocean_scores.csv` | OCEAN scores per participant |
| `ocean_corr_outputs/participant_condition_scores_with_ocean.csv` | Survey scores joined with OCEAN |
| `ocean_corr_outputs/condition_ocean_correlations.csv` | Full correlation table |
| `ocean_corr_outputs/condition_ocean_significant_spearman.csv` | Spearman rows with uncorrected *p* < 0.05 |
| `ocean_corr_outputs/condition_ocean_significant_holm.csv` | Spearman rows with Holm-adjusted *p* < 0.05 |
| `ocean_corr_outputs/condition_ocean_significant_bh_fdr.csv` | Spearman rows with BH-FDR *q* < 0.05 |
| `ocean_corr_outputs/analysis_diagram.png` | Analysis flow diagram |
| `ocean_corr_outputs/spearman_heatmap_by_condition.png` | Combined Spearman heatmaps |
| `ocean_corr_outputs/spearman_heatmap_<condition>.png` | Per-condition heatmap |

---

### `temp_demo_moderation_model.py`

Exploratory moderation check built directly from the raw tracked logs.

- **Inputs:** `src/project/logs/tracked/lab/**` and `src/project/logs/tracked/crowd/**` JSONL exports
- **Purpose:** reconstruct participant-by-condition records from event logs and test whether condition effects vary by demographic variables
- **Moderators tested:** `demo_sex`, `demo_education`, `demo_familiarity`, `demo_frequency`
- **Model form:** `outcome ~ C(condition) * C(demographic)`
- **Status:** scratch / diagnostic analysis, not the canonical final modelling pipeline

This script reads the tracked event files, extracts the demographics submitted after the experiment and the post-condition survey outcomes, assembles a participant × condition table in memory, and prints the interaction p-values for each demographic moderator. It is useful for early signal checking before moving to the canonical Gold tables.

```bash
python temp_demo_moderation_model.py
```

---

### `moderation_model_gold.py`

Gold-data moderation analysis using the canonical behavioural tables.

- **Inputs:**
  - `analysis/walter/behavioural/outputs/gold/condition_features.csv`
  - `analysis/walter/behavioural/outputs/gold/person_features.csv`
- **Purpose:** test whether the effect of experimental condition differs across demographics using the cleaned Gold dataset
- **Outcomes tested:** `credibility`, `helpfulness`, `convincingness`, `relevance`, `neutrality`, `behaviour_pushing`, `behaviour_manipulate`
- **Moderators tested:** `demo_sex`, `demo_education`, `demo_familiarity`, `demo_frequency`
- **Model form:** `outcome ~ C(condition) + C(moderator) + C(condition):C(moderator)` using a mixed-effects specification with participant random intercepts
- **Status:** the final working script for the demographic moderation check; it prints results to the terminal rather than writing a persistent CSV

This script merges participant-level demographics onto the repeated condition rows, drops sparse moderator levels, fits one moderator-at-a-time model for each outcome, and reports the smallest interaction p-values. It is the version used for the final multiplicity-corrected inspection with Holm and BH-FDR adjustment.

```bash
python moderation_model_gold.py
```

**Note:** Prefer the one-family scripts below for Model 1 + Model 2 with OCEAN. `moderation_model_gold.py` remains the earlier demographics-only scanner.

---

### Family moderation scripts (Model 1 + Model 2)

One script per outcome family. Each fits:

1. **Model 1** — repeated-measures LMM `Y ~ C(condition) + (1 | experiment_id)` with planned contrasts (Holm within family)
2. **Model 2** — OLS of person-level contrast scores \(\Delta Y\) on BFI-10 (OCEAN); demographics secondary
3. **Model 2b** (optional) — `Y ~ C(condition) * trait` interaction check

**Shared inputs (Walter Gold, lab + crowd, \(N=54\)):**

- `analysis/walter/behavioural/outputs/gold/condition_features.csv` (survey families)
- `analysis/walter/behavioural/outputs/gold/advertisement_features.csv` (recall families)
- `analysis/walter/behavioural/outputs/gold/person_features.csv` (BFI + demographics)
- `analysis/walter/behavioural/outputs/gold/contrast_scores.csv` (survey \(\Delta\) scores; recall scripts build \(\Delta\) from the wide ad matrix)

**Planned contrasts**

| Family type | Contrasts |
|-------------|-----------|
| Survey (`manipulation`, `credibility`, `notice`) | any ad − no ad; implicit − explicit; early − late |
| Recall (`recall_memory`, `recall_trust_shift`) | implicit − explicit; early − late only (ad-only; no no-ad cell) |

| Script | Outcome \(Y\) | Output folder |
|--------|---------------|---------------|
| `moderation_manipulation_ocean.py` | `manipulation` (felt manipulation) | `outputs/moderation_manipulation_ocean/` |
| `moderation_credibility_ocean.py` | `credibility` | `outputs/moderation_credibility_ocean/` |
| `moderation_notice_ocean.py` | `notice` (ad noticing) | `outputs/moderation_notice_ocean/` |
| `moderation_recall_memory_ocean.py` | `recall_memory` | `outputs/moderation_recall_memory_ocean/` |
| `moderation_recall_trust_ocean.py` | `recall_trust_shift` (trust after re-exposure) | `outputs/moderation_recall_trust_ocean/` |

```bash
python moderation_manipulation_ocean.py
python moderation_credibility_ocean.py
python moderation_notice_ocean.py
python moderation_recall_memory_ocean.py
python moderation_recall_trust_ocean.py
```

Each run writes the same file set under its output folder:

| Output | Description |
|--------|-------------|
| `analysis_long.csv` | Person × condition rows used in the models |
| `model1_condition_effects.csv` | Model 1 planned-contrast estimates (LMM) |
| `model2_delta_moderation.csv` | Model 2: \(\Delta Y\) ~ BFI traits |
| `model2_delta_demographics.csv` | Secondary: \(\Delta Y\) ~ demographics |
| `model2_interaction_terms.csv` | Optional condition × BFI interaction terms |
| `significant_summary.csv` | Holm hits only (Model 1 + Model 2) |
| `run_manifest.json` | \(n\), paths, correction rule, timestamp |

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

# 5. Family-wise Model 1 + Model 2 moderation (uses Walter Gold)
python moderation_manipulation_ocean.py
python moderation_credibility_ocean.py
python moderation_notice_ocean.py
python moderation_recall_memory_ocean.py
python moderation_recall_trust_ocean.py
```

## Output folders

| Folder | Produced by |
|--------|-------------|
| `boxplots_outputs/` | `Analysis_AdsTalkBack.ipynb` |
| `ocean_corr_outputs/` | `calc_condition_ocean_correlations.py` |
| `outputs/moderation_manipulation_ocean/` | `moderation_manipulation_ocean.py` |
| `outputs/moderation_credibility_ocean/` | `moderation_credibility_ocean.py` |
| `outputs/moderation_notice_ocean/` | `moderation_notice_ocean.py` |
| `outputs/moderation_recall_memory_ocean/` | `moderation_recall_memory_ocean.py` |
| `outputs/moderation_recall_trust_ocean/` | `moderation_recall_trust_ocean.py` |

## Conditions

| Condition ID | Meaning (short) |
|--------------|-----------------|
| `block_early` | Explicit ad block, early turn |
| `block_late` | Explicit ad block, late turn |
| `inline_early` | Inline ad, early turn |
| `inline_late` | Inline ad, late turn |
| `no_ads` | No ads |
