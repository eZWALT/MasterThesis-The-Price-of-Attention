# Experiments launched (6 September evening)

Walter: stop planning, train on our labels, go bigger than 3B,
evaluate on our Gold, do not consult.

## What is being trained on (the only Y)

Not the saturated 4B judge. Not SmolLM3 as the cap.

- **X**: ad-turn conversation prefix (`outputs/gold/human_anchor.csv` `prefix_text`)
- **Y**: `ux_retention_resid` and `good_moment_human` from the RCT
  (person vs own no-ad; λ residualised). 216 rows.
- **Pairs**: 324 within-person preferences (higher U wins).
- **Eval**: LOPO by participant, task-grouped Spearman, pairwise acc,
  IPS vs always-late. Always against the same Gold file.

## Job

`CUDA_VISIBLE_DEVICES=1` `analysis/policy/train_eval.py`

1. Baselines: turn, fit, always-late
2. Frozen probes + LOPO ridge: ThradBERT, bge-small, **Qwen3-8B**,
   **Qwen3-14B 4-bit**, **Phi-4 14B 4-bit**
3. LoRA pairwise hinge on Qwen3-8B, 5-fold by person

First pass **finished** (~12 min, exit 0). Frozen 8B/14B/Phi-4 last-token
probes all lose to `baseline_turn` (Spearman 0.17). 14B 0.08, Phi-4 −0.05.
ThradBERT crashed (`token_type_ids`); LoRA crashed (`step` unbound).
Both fixed; rerun `--only thradbert` + LoRA on GPU 1.

GPU 0 is another user. Do not touch.
