# Evening iterate (6 September)

Not a thesis goal. GPU 0 is another user.

Walter: use transformers and every behavioural metric in the
conversation; keep looping until the model is actually worth
publishing. Previous BEST was turn + 0.15 × residual(14B PCA₄, latency)
at Spearman 0.274 / same-timing 0.611.

## What is being added

Serve-time only (still no λ, no EEG, no post-treatment Likert as X):

- lexical readiness / hedge / product / question stats on the user turn
- running latency/length slope inside the chat
- 13 ThradBERT posteriors + prefix trajectory
- DistilBERT-MNLI entailment on 7 conversation-state hypotheses
- OCEAN optional
- all 8 UX deltas as *multi-task Y*, not as X
- ThradBERT + DistilBERT-MNLI fine-tune with fused tabular head
  (MSE + pairwise, 5-fold person)
- Qwen3-0.6B LoRA done properly (all in-fold pairs, not 80)

Code: `features_behaviour.py`, `train_iterate.py`, `train_tfm_fusion.py`.
Job: `run_hours.sh`. Logs: `outputs/experiments/full/{iterate,tfm,loop}.log`.

Replace `BEST.md` only if Spearman > 0.274 **and** same-timing ≥ 0.60.
