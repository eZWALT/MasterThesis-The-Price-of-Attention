# Modelling restart (6 September, late)

Not a thesis goal. GPU 0 is another user. Do not touch ICA.
Do **not** train on rescued 4B judge labels.

Walter rejected the first GPU pass (probes worse than the late
rule). The first pass was scored wrong. This note is the live state.

## What was wrong

1. LOPO ridge **with intercept** anti-correlates the fold intercept
   with the held-out person's mean \(U\). Raw turn Spearman +0.17;
   LOPO-ridge(turn) −0.26. Learned probes were compared to the raw
   turn baseline. Serving score is now `X @ w` (no intercept).
2. 4096-d last-token + ridge, turn not in \(X\).
3. Broadcasting conversation \(Y\) onto all 1,080 turns **hurt**.
4. Dedicated sentence embedders (bge, Qwen3-Embedding 0.6/4/8B)
   do not beat the late rule on this \(n\).
5. Qwen3-8B LoRA 5-fold hinge finished at Spearman 0.001.

## Winner (locked)

`analysis/policy/outputs/experiments/full/BEST.md`

\[
\mathrm{score} = \frac{k}{8} + 0.15\cdot
z\bigl(\mathrm{Ridge}(\mathrm{PCA}_4(h_{\mathrm{Qwen3-14B}}),\ \log(1+\mathrm{lat}))\bigr)
\]

on residual \(U\) (turn locked, text+latency only explain the leftover).

| metric | late rule | this model |
|---|---:|---:|
| Spearman U LOPO | 0.167 | **0.274** |
| person-bootstrap 95% CI | — | 0.156–0.375 (overlaps 0.167) |
| same-timing pairwise n=108 | 0 (ties) | **0.611** (z=2.31) |
| AUROC good_moment | 0.534 | **0.581** |

Inference \(X\): prefix text → Qwen3-14B last-token, turn, user-message
latency. No λ, person, task id, EEG. OCEAN helps ~0.01 more if you
already have BFI; not in the locked recipe.

Artefacts: `scorer_BEST_fixedturn_14b_lat.npz`,
`pred_BEST_fixedturn_14b_lat.npy`, `freeze_best.py`.

## Still running

14B last-token + mean-pool on all 1,080 prefixes (GPU 1), then
`train_14b_1080.py`. Campaign / confirm / WildChat-bge PCA on CPU.
If 1080-row training beats 0.274, replace BEST.md.
