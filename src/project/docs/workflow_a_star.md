# Workflow A* — Experimental Protocol

## Overview

5-condition within-subject design evaluating advertisement format and timing
in an LLM-powered shopping assistant.  Each participant completes the full
protocol in ~45–60 minutes.

## 5 Conditions

| # | Condition | Ad Format | Timing Window | Injector |
|---|-----------|-----------|---------------|----------|
| 1 | `no_ads` | None | Never | — |
| 2 | `inline_early` | Inline (woven into LLM reply) | Turn 1–2 | `inline_persuasive` |
| 3 | `inline_late` | Inline (woven into LLM reply) | Turn 3–5 | `inline_persuasive` |
| 4 | `block_early` | Block (banner above input) | Turn 1–2 | `explicit_ad_block` |
| 5 | `block_late` | Block (banner above input) | Turn 3–5 | `explicit_ad_block` |

Each ad condition injects **exactly 1 ad** at a randomly chosen turn within its
window.  The `no_ads` condition never injects.

## Participant Flow

```
consent → demographics → instructions → warmup_chat → first_impression
→ [condition_intro → condition_chat → post_condition_survey] × 5
→ ocean (BFI-10) → vals → global_evaluation → done
```

### Screen Details

| Step | Screen | Duration | Data Collected |
|------|--------|----------|----------------|
| 0 | `consent` | 1 min | Agreement |
| 1 | `demographics` | 1 min | Age, gender, AI experience |
| 2 | `instructions` | 30 s | — |
| 3 | `warmup_chat` | 2–5 min | 5-turn chat, no ads |
| 4 | `first_impression` | 1 min | Free-text, reuse intent, sentiment |
| 5–9 | `condition_intro` | 30 s each | — |
| 5–9 | `condition_chat` | 3–5 min each | 5-turn chat, ad injected per timing |
| 5–9 | `post_condition_survey` | 1 min each | Trust, usefulness, satisfaction (Likert 1–7) |
| 10 | `ocean` | 2 min | BFI-10 personality (5 traits) |
| 11 | `vals` | 2 min | Lifestyle segmentation (8 items) |
| 12 | `global_evaluation` | 2 min | Overall trust, usefulness, awareness, disruption, reuse intent, open-ended |

## Counterbalancing

- **Condition order**: Latin-square rotation keyed by `?cb=N` or
  `hash(participant_id)` to ensure each condition appears equally often
  in each ordinal position.
- **Task–condition pairing**: Tasks 1–5 from `TASK_CATALOG` are shuffled
  together with conditions if `?seed=N` is set, otherwise conditions rotate
  while tasks stay in catalog order.

## Configuration

All constants live in `core/config.py` (Section 5):

- `CONDITIONS` — list of 5 condition keys
- `CONDITION_LABELS` — human-readable names
- `CONDITION_AD_MODE` — maps condition → injector key
- `CONDITION_TIMING` — maps condition → `(min_turn, max_turn)` or `None`

## Data Model

Per-participant JSONL log contains:

- `session_started` — participant_id, study_type, full condition_plan
- Per-condition events (identical to existing trial logging)
- `condition_complete` — condition_id, ad_mode, ad_turn, turns, metrics
- `post_condition_survey_submitted` — trust, usefulness, satisfaction
- `session_complete` — demographics, first_impression, ocean_scores,
  vals_responses, condition_summaries, condition_surveys, global_evaluation

## Dev Mode

- `?dev=true` — free-form chat with condition selector, ad controls, task picker
- `?dev=flow` — participant flow with skip buttons, condition override,
  ad override, debug panels
