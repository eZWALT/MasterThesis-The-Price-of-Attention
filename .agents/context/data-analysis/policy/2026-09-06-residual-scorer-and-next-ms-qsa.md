# Residual scorer lock, then \(m(s)\) / \(q(s,a)\) (6 September evening)

Side project. **Not a thesis goal.** Insertion-policy \(\pi\) stays
dropped from the manuscripts
(`../../2026-08-24-insertion-policy-model-dropped.md`).
Nothing here enters thesis, paper, or deck before 17 September.
Future Work may say: one ad per chat cannot train \(m(s)\) / \(q(s,a)\).

This note is the **live research-line lock**. Evening numbers live in
`2026-09-06-evening-handoff.md`. Winner file:
`analysis/policy/outputs/experiments/full/BEST.md`.
Do not restack features on the 216-row residual. The next object is
not a bigger ridge.

## Why this is still interesting

The thesis dropped Goal 6 (24 August) because \(N=54\), one ad per
chat, is not a training corpus for a serving \(\pi\). That is still
true. What happened on 6 September is a **side line** that diverged
from both the original scorer design and the original thesis plan,
and still produced a real object.

Original scorer (`2026-09-06-ad-moment-scorer.md`): a judge rubric
(need / ready / safe / no_degrade) → DistilBERT heads → LOPO
calibrator onto human \(U\). That judge **does not track humans**
(smoke \(\rho(\bar r, U)=-0.035\); 4B v2 labels saturate at 1.0 on
every `swt_*` turn). Training on it teaches “always insert.”

What we actually fit is different: a **human-only residual scorer**
on the RCT. Prefix → Qwen3-14B last-token → PCA₄, plus two
serve-time scalars, on \(U\) after \(\lambda\) and task are
residualised out of the label. Presentation \(\lambda\) is still
neither an input nor an output. The late rule (Spearman 0.167) is
the bar; same-timing pairwise is the only place turn cannot help.

That is interesting because it is the first number in this repo that
is a **policy-shaped estimand** rather than a condition contrast:
“how good is *this* moment for *some* ad?”, evaluated LOPO on
people, against a human UX composite. It is also a warning. The
sample ceiling is two extras on a 14B residual. Fine-tunes and fat
feature dumps die. So the interesting continuation is **not**
another encoder on the same 216 rows. It is to stop pretending the
ridge *is* \(m(s)\) or \(q(s,a)\), write those objects down, and
change the data or the estimand.

Theory stays \(\Pi=\langle\Gamma,\mu,\pi\rangle\). \(\lambda\) is a
coordinate of \(a_k\) realised by \(\mu\). \(\Gamma\) (veto genres)
is not learned. What we lack is a value function for \(\pi\).

## What the locked ridge actually is

\[
\widehat{m}_{\mathrm{ridge}}(s_k)
=\frac{k}{8}
+0.15\cdot z\bigl(\mathrm{Ridge}(\mathrm{PCA}_4(h_{\mathrm{14B}}(x_k)),
\log(1+\mathrm{lat}_k),\,O,\,\texttt{lex\_q\_start})\bigr)
\]

\(s_k\) here is a prefix plus latency (and optional BFI Openness).
It is **not** \(m(s)\). It is a ranking score whose turn term is
locked and whose residual is LOPO-ridge on \(U^{\mathrm{resid}}\).
Person-bootstrap 95% CI on Spearman is 0.200–0.411 (above 0.167).
Same-timing pairwise 0.639 (\(z=2.89\), \(n=108\)). Within-person
Spearman 0.293. Openness ranks people; `lex_q_start` ranks moments
inside a timing. Mix stays 0.15 (higher mix inflates Spearman by
weakening “insert late”).

Serving artefacts:
`analysis/policy/outputs/experiments/full/scorer_BEST_fixedturn_14b_lat.npz`,
`score_moment.py`, `freeze_best.py`.

---

## Done vs not done

Use this table. Do not re-audit Bronze. Do not rebuild Silver unless
Goal 1 composites freeze (then rebuild the anchor and re-pin the sha).
Do not train on `outputs/rescued/labels_real_v2_logprob_0to9.csv`.

### Done

| Item | Where / what it is |
|---|---|
| Silver | `analysis/policy/outputs/silver/{turns,conversations}.csv`. 1,479 turns (1,080 primary). |
| Human anchor \(Y\) | `outputs/gold/human_anchor.csv`, 216 ads. \(U=\frac13(\Delta\mathrm{cred}+\Delta\mathrm{trust}-\Delta\mathrm{manip})\) vs own no-ad, residualised on \(\lambda\) and task. `good_moment_human` rate ≈ 0.29. Mean \(U\) negative; late better than early. sha16 `949605816c501b72`. Composites provisional until Goal 1. |
| Gold extras | `preference_pairs.csv` (324, **all cross-task**), `bandit_rows.csv` (216 INSERT + 54 WAIT), `turns_clean.csv` (1,479). `gold_report.json`. QC `validate_policy_dataset.py` 17/17 when last run. |
| Behavioural \(X\) | `features_behaviour.py`: lexical, running latency/length, last-assistant, prefix-user agg, MNLI 7 hyps, ThradBERT prefix posteriors, OCEAN (51/54, 3 imputed). 65 serve-time columns. |
| Cached embeddings (216 and/or 1,080) | Qwen3-14B last-token (the one that matters), 8B, Phi-4, bge, ThradBERT, Qwen3-Embedding 0.6/4/8B, instruct 0.6/4/8B. Mean-pool 14B is **anti-correlated**; last-token only. |
| Locked residual recipes | moment-only 0.274 / 0.611; user+moment (Openness) 0.315 / 0.602; **same_t** (Openness + question) **0.309 / 0.639**. |
| Negative results we already paid for | LOPO ridge **with intercept** anti-correlates person means (do not repeat). Broadcast \(Y\) onto 1,080 turns hurts. Dedicated embedders do not beat late. Fat 54-col residual drowns the model. DistilBERT-MNLI / MiniLM / Qwen3-0.6B LoRA / RankNet fine-tunes Spearman ≤ 0. Two-stage `turn+z(O)` inverts Openness unless the ridge owns the sign. 1080-prefix PCA, per-timing residual, Likert stack, 8B/Phi/Thrad/instruct fusion, MiniLM / BGE-m3 / Qwen3-Reranker-4B zero-shot: lose same-t or Spearman. mix > 0.15 is not a better model. |
| External prefixes rescued | `outputs/rescued/external_prefixes.csv` (8k WildChat). Unused for a real \(M_{\mathrm{intent}}\). |
| Compute rule | GPU **1** only on Atlas. GPU 0 is another user. Do not overwrite ICA models. |

### Not done (do not pretend otherwise)

| Item | Why it is still open |
|---|---|
| The original judge scorer | Full-scale v2 4B labels were never produced as a *valid* \(Y\). Smoke 0.6B does not track \(U\). Saturated 4B rescue is forbidden as training \(Y\). |
| \(m(s)\) as a value | No estimate of \(\mathbb{E}[U\mid s,\mathrm{INSERT}]-\mathbb{E}[U\mid s,\mathrm{WAIT}]\). The ridge is a ranking score, not a counterfactual moment value. The 54 WAIT rows exist in `bandit_rows.csv` and were not used as such. |
| \(q(s,a)\) | No action-value. \(a\) was never a first-class object (timing only, or `{WAIT, INSERT}`, or creative / \(\lambda\)). \(\lambda\) must not enter \(\pi\) as an input; it *can* be a coordinate of \(a\) inside \(q\). |
| Offline policy evaluation (P2) | IPS / SNIPS / DR on the 270 bandit rows was specified in `TRAINING_PLAN.md` and not run. No threshold \(\tau\) on \(\widehat{m}\) was evaluated as a policy against always-late / always-wait. |
| Pairwise / DPO as the *objective* (P1, P3) | Pairs exist (324). RankNet on them lost to MSE. LoRA-DPO (SmolLM / Phi / Qwen) was never launched. Every pair is cross-task: task-grouped CV is mandatory or you learn laptop vs fitness. |
| Intent gate \(M_{\mathrm{intent}}\) (P4) | WildChat 8k prefixes sit unused. Study turns cannot teach “is this commercial?” — they all are. |
| Harm / \(\Gamma\) as a learned head | Veto genres stay rules. No calibrated \(P(\text{UX drop}\mid s)\). |
| Serving hook in the product | `MomentScorer` / `{moment_score, receptivity, veto, insert, abstain}` was sketched in the notebook and never wired. `score_moment.py` is a file, not a runtime. |
| Training-plan P0 encoder on \(U\) | ThradBERT / DeBERTa-small supervised MSE (the *planned* P0) was not the winner. ThradBERT tokenizer needs `use_fast=True` (slow path crashes: `vocab_file is None`). |
| New data | No extra RCT, no dense per-turn human labels, no logged bandit from a live \(\pi\), no second timing beyond {2, 4}. |
| Thesis / paper / deck copy | Untouched. Keep it that way through 17 September. |

`analysis/policy/README.md` still said “no training launched.” That
line is stale. Training launched, the residual is locked, P0–P4 as
written in `TRAINING_PLAN.md` are mostly **not** what won.

---

## Next line: write \(m(s)\) and \(q(s,a)\) down, then change the problem

Do not add column 66 to the ridge. Pick one of these and treat the
locked scorer as a **baseline feature**, not the estimand.

### \(m(s)\) — moment value of the state

State \(s\) = serve-time prefix (text + turn + latency; optional BFI).
The object we actually want:

\[
m(s)
=\mathbb{E}\bigl[U\mid s, A=\mathrm{INSERT}\bigr]
-\mathbb{E}\bigl[U\mid s, A=\mathrm{WAIT}\bigr].
\]

That is a **treatment effect in conversation state**, not a
correlation of a score with \(U\) among inserted ads only. The 216
rows identify the first term only if you ignore confounding of
*when* we inserted. The 54 WAIT rows identify the second term only
as a person-level no-ad chat, not as “wait at this \(s_k\) and
insert later.” Honest moves:

1. **Define WAIT at the turn.** Use `bandit_rows.csv`. Propensity
   is the RCT (early / late / no-ad), not a learned \(\pi\). OPE a
   threshold on \(\widehat{m}_{\mathrm{ridge}}\) (P2). Report
   IPS/SNIPS against always-late. If the CI covers always-late, say
   so. That is the first *policy* number.
2. **Binary \(m\) as \(P(\text{good moment}\mid s)\).** Logistic
   LOPO on `good_moment_human`. We already have AUROC 0.597 for the
   ridge; a calibrated probability is a different artefact.
3. **Do not** broadcast conversation \(U\) onto non-ad turns and
   call it \(m(s_k)\). That was tried. It hurts.

New data that would change \(m(s)\): more than one insert-or-wait
decision per chat, or a logged policy that sometimes waits at turn 2
and inserts at 4 *in the same conversation*.

### \(q(s,a)\) — action value

Action \(a\) has to be declared. Three useful restrictions, in
increasing hunger for data:

| \(a\) | What \(q\) answers | Data we have | Trap |
|---|---|---|---|
| \(\{\mathrm{WAIT},\mathrm{INSERT}\}\) | Insert now vs hold | 270 bandit rows | WAIT is a whole no-ad chat, not a pause at \(k\) |
| \(\{\mathrm{early},\mathrm{late}\}\) | Turn 2 vs 4, given we will insert | 216 ads, within-person | This is almost the late rule; \(q\) must beat it on same-task or same-timing leftovers |
| \((\mathrm{timing},\,\mathrm{creative})\) or \((\mathrm{timing},\,\lambda)\) | Which ad / format at this \(s\) | `fit_score`, 216 rows | \(\lambda\) is \(\mu\), not \(\pi\). Factor \(q(s,a)=m(s)+f(\mathrm{fit})\) rather than concatenating \(\lambda\) into \(X\) |

A factored form is the one that respects the thesis:

\[
q(s,a)=m(s)+b^\top\phi(s,a_{\mathrm{creative}}),\qquad
a_{\mathrm{timing}}\in\pi,\;
a_\lambda\in\mu.
\]

We have `fit_score` and never used it well (it drowned same-t).
A new line is: **keep \(m(s)\) as the locked residual (or the OPE
threshold), learn only the creative term on pairs that share
timing.** Same-timing pairwise is exactly that grain (\(n=108\)).

What would make \(q(s,a)\) real: a logged bandit with more than two
timings, or an off-policy dataset where \(\pi_b\) is known and
\(a\) includes wait. PPO/GRPO on 216 rows is still not a paradigm.

### New formulations / models / data worth exploring

In this order, if someone continues the side project after the
thesis:

1. **OPE (P2) on `bandit_rows.csv`.** Threshold the locked score.
   Always-late / always-wait / \(\tau\) sweep. This is the missing
   *policy* evaluation of the thing we already have.
2. **\(M_{\mathrm{intent}}\) on WildChat** (P4). Binary “is this
   commercial at all?” Separate model, separate data. The study
   cannot teach it.
3. **Factored \(q\)** on same-timing pairs only: ridge or a tiny
   ranker on \((\mathrm{fit}, \texttt{lex\_q\_start}, \log\mathrm{lat})\)
   *without* stuffing Openness into the same vector if the product
   question is “which moment,” not “which user.”
4. **New labels**, not new encoders. Per-turn human “would an ad
   hurt *here*?” on a larger logged chat corpus. Or a second RCT
   with wait-at-\(k\) as a real action.
5. **New models only after 1–2.** DeBERTa / ThradBERT P0, DPO P3,
   Qwen3-Reranker-8B — all are repeats of a 216-row fine-tune unless
   the estimand changed.

## Standing rules (unchanged)

- Eval vs `human_anchor.csv`, LOPO by participant, 216 ads.
- Serving score is `X @ w` (no intercept).
- No \(\lambda\), no EEG, no person id, no task id in \(X\) unless
  the product already has BFI and you say so.
- Do not pick mix / \(k\) / features by the same 216 after the fact
  and call it a new BEST. Nested LOPO or a new estimand.
- GPU 1 only. Do not overwrite ICA.
- Do not put this in Results.
