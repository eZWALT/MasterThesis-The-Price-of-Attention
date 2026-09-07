# Best serving policy so far

**Recommended serving π (moments, not just people):**
`score = turn/8 + 0.15·z(Ridge(PCA₄(Qwen3-14B last-token), log latency, Openness, starts-with-question))`

Person-bootstrap CI sits above the late rule (0.167).

- Spearman U LOPO: **0.3088** (person-bootstrap 95% CI 0.1999–0.4113)
- same-timing pairwise: **0.6389** (z=2.887, n=108)
- within-person Spearman: **0.2926**
- AUROC: **0.5973**
- all-pair pairwise: 0.6265

`lex_q_start` is a conversation behaviour (user turn opens with what/which/how/…). Openness is BFI-10 if the product has it.

**Highest Spearman (people + moments):** drop the question feature → 0.3145 (CI 0.2049–0.4079), same-t 0.6019, within 0.2667. Mostly ranks who tolerates ads.

**Moment-only (no BFI):** turn + latency + 14B → Spearman 0.2737, same-t 0.6111, CI [0.1564, 0.3749].

Failed (do not promote): fat 54-column residual; DistilBERT / MiniLM / Qwen3-0.6B LoRA / RankNet fine-tunes (Spearman ≤ 0); two-stage turn+z(Openness); 8B/Phi/Thrad/instruct fusion; HGB; 1080-prefix PCA; MiniLM / BGE-m3 / Qwen3-Reranker-4B zero-shot; mix>0.15 (Spearman rises, late-prior flips). Keep mix **0.15**. Stepwise addition is what moved the number.
