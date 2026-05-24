# Experiment Logs

This directory stores versioned experiment run data as JSONL files.

## Structure

```
logs/
  {experiment_id}/
    {run_id}.jsonl
```

- **experiment_id**: `exp_{ISO_UTC}_{config_hash8}` — stable per config
- **run_id**: `run_{uuid12}` — unique per app launch

## Schema (one JSON object per line)

| Field | Type | Description |
|---|---|---|
| `experiment_id` | str | Experiment configuration identifier |
| `run_id` | str | Unique run identifier |
| `participant_id` | str | Human subject ID |
| `conversation_id` | str | Conversation UUID |
| `timestamp` | str | ISO-8601 UTC |
| `event` | str | Event type key |
| `source` | str | `user` / `model` / `system` / `retrieval` |
| `step_index` | int | Global monotonic counter within run |
| `ad_mode` | str | Experimental condition |
| `trial_index` | int | Trial number (0-based) |
| `turn` | int | Turn within trial |
| `data` | object | Free-form event-specific payload |

## Event Types

- `user_message` — participant utterance
- `assistant_reply` — LLM response (with timing)
- `retrieval` — RAG pipeline result (query, scores, timing)
- `ad_injected` — ad insertion details (mode, title, position)
- `attention_shift` — KL/JSD divergence measurement
- `eye_tracking_ad_exposure` — gaze fixation on ad AOI

## Versioning

These files are git-tracked. Commit after each experiment session:

```bash
git add logs/ && git commit -m "data: experiment logs $(date +%F)"
```
