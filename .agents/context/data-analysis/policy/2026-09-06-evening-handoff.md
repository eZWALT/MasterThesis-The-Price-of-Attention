# Evening handoff (6 September)

Superseded as the *research line* by
`2026-09-06-residual-scorer-and-next-ms-qsa.md` (done vs not done,
next is \(m(s)\) / \(q(s,a)\)). This file keeps the evening numbers.

Not a thesis goal. GPU 0 is another user (`gkoutr`). Never touch it.

Walter asked to keep iterating with transformers and every conversation
behavioural metric until the first policy model is worth publishing.

## Locked recipes (LOPO, 216 ads, human \(U\))

Always-late baseline Spearman **0.167**. Serving score is
`turn/8 + 0.15 · z(residual)` (no intercept).

| recipe | extras on 14B PCA₄ residual | Spearman | person-bootstrap CI | same-t | within |
|---|---|---:|---|---:|---:|
| **same_t (recommended π)** | log latency, Openness, `lex_q_start` | **0.309** | **0.200–0.411** | **0.639** | **0.293** |
| user_moment | log latency, Openness | 0.315 | 0.205–0.408 | 0.602 | 0.267 |
| moment-only | log latency | 0.274 | 0.156–0.375 | 0.611 | 0.270 |

`same_t` is the first recipe whose CI sits above the late rule. Openness
ranks people; `lex_q_start` (user turn opens with what/which/how/…) is
the conversation behaviour that lifts same-timing and within-person.

Do **not** dump all 54 behavioural columns into the residual. DistilBERT
/ MiniLM fine-tunes overfit (Spearman < 0).

## GPU follow-up (done, did not beat BEST)

- Qwen3-0.6B LoRA, all in-fold pairs, 5-fold: Spearman **−0.031**, same-t 0.50.
- Qwen3-Reranker-4B yes/no on the prefix: residual ρ ≈ +0.09; adding it
  is 0.312 / 0.611 — loses same-t vs 0.639.

Stop stacking features. The 216-label ceiling is the locked residual.

## Evening CPU / feature passes (none beat the joint bar)

- mix 0.28 on the *same* residual → Spearman 0.321, same-t unchanged,
  but late>early starts flipping; nested mix votes 0.35 and late>early
  0.91. Keep mix **0.15**.
- two-stage `turn + z(O)`: inverted Openness (ridge must own the sign).
- 54-column dump, HGB, kernel ridge, RankNet, 1080-prefix PCA,
  per-timing residual, Likert stack, 8B/Phi/Thrad/instruct fusion,
  MiniLM + BGE-m3 zero-shot rerankers: all lose same-t or Spearman.
- Neuroticism recipe: same-t **0.648**, within 0.307, Spearman 0.289
  (optional same-timing tilt, not primary).

## Code / artefacts

- Features: `analysis/policy/features_behaviour.py`
- Train: `train_stepwise.py`, `train_next.py`, `train_tfm_fusion.py`
- Freeze: `freeze_best.py` → `outputs/experiments/full/BEST.md`
- Do not put this in thesis / paper / deck.
