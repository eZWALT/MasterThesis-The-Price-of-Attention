# Ad-moment training plan (show this before any launch)

Nothing below has been launched. GPU 1 is free. The leftover full-run kernel was killed after we rescued its artefacts.

## 0. Math and why a single “good moment ∈ [0,1]” on this study is not industrial

The production object we still want:

\[
m(x_k,z_k)\in[0,1],\qquad
\text{insert iff } m>\tau \text{ and no }\Gamma\text{ veto}.
\]

\(x_k\) is the role-tagged last-4-turn prefix. \(z_k=(\min(k,8)/8,\ \mathrm{fit}_k)\). \(\lambda\), person, task, EEG are not in \(X\).

The study does **not** give a dense \(Y\) for that \(m\). Two facts, now measured:

1. **The conversations are commercial by design.** Five `swt_*` tasks (laptop, gift, pet, fitness, study). A judge asked “is there a product need / is this a natural mention?” on Qwen3-4B with the v2 log-prob rubric. Result on 1,479 study turns: median \(\bar r=1.00\), mean \(0.95\), \(86\%\) of rows \(>0.9\). Same ceiling as v1. This is a *dataset* property, not a judge bug. Training DistilBERT on those labels teaches “always insert.”
2. **The human signal is sparse and mostly timing.** 216 ads, \(U_i=\frac13(\Delta\mathrm{cred}+\Delta\mathrm{trust}-\Delta\mathrm{manip})\) vs that person’s own no-ad chat, residualised on \(\lambda\) and task. Mean \(U=-0.58\). Early \(-0.81\), late \(-0.36\). Good-moment rate \(0.29\). Smoke calibrator: turn-only AUROC \(0.53\), text \(\hat r\) AUROC \(0.38\) and a **negative** coefficient.

So one encoder trained on a study-turn judge is not a ChatGPT-shaped policy. Industry needs three pieces, and we can only *learn* two of them from this RCT:

| Piece | What it answers | Where the \(Y\) lives | Industrial job |
|---|---|---|---|
| \(M_{\mathrm{intent}}\) | Is this conversation commercial at all? | WildChat / OASST1 (8k prefixes already rescued), **not** `swt_*` | Gate retrieval (the 3 s HyDE+FAISS cost) |
| \(M_{\mathrm{harm}}\) | If we insert *here*, does UX drop? | 216 human \(U^{\mathrm{resid}}\) | Brand-safety / \(\Gamma\) |
| \(\pi\) | Insert or wait | OPE on 216 INSERT + 54 WAIT, propensity \(0.2\) | The serving rule. **Evaluate**, do not PPO. |

Optional: a ranker / DPO on 324 within-person pairs (chosen = higher \(U\)). Every pair is **cross-task** (`same_task=0`, Latin square). Task-grouped CV is mandatory or we just learn “laptop vs fitness.”

RL that is honest here = **offline contextual bandit + IPS/SNIPS/DR**. PPO/GRPO on 216 rows is not a paradigm we will run.

## 1. Preprocessing — done, shape is clean

QC: `python analysis/policy/validate_policy_dataset.py` → **17/17**.

Gold: `python analysis/policy/build_policy_gold.py`

| Table | Rows | Role |
|---|---|---|
| `outputs/gold/turns_clean.csv` | 1,479 (1,080 study) | \(X\) + fold ids |
| `outputs/gold/human_anchor.csv` | 216 | \(Y=U^{\mathrm{resid}}\), ad-turn prefix joined |
| `outputs/gold/preference_pairs.csv` | 324 | pairwise rank / DPO |
| `outputs/gold/bandit_rows.csv` | 270 | 216 INSERT + 54 WAIT |
| `outputs/rescued/external_prefixes.csv` | 8,000 WildChat | \(M_{\mathrm{intent}}\) later |
| `outputs/rescued/labels_real_v2_logprob_0to9.csv` | 1,479 | **failed** weak label; do not train on it |

Primary study rectangle: 54 people × 5 conditions × 4 turns, no empty text, no duplicate keys, every primary conversation has a survey, every ad has `fit_score` and recall.

Preprocess notebook (CPU, Bronze): `build_policy_dataset.ipynb`. Do not rebuild Silver unless Goal 1 composites freeze.

## 2. Environments and grids

Profiles stay `atlas` / `laptop16` / `colab` / `kaggle` / `smoke`. Atlas = GPU **1** only (GPU 0 is `gkoutr`, leave it).

Grids live in [`configs/paradigms.yaml`](configs/paradigms.yaml). Summary:

| ID | Paradigm | \(n\) | Models | Grid (small) | Env |
|---|---|---|---|---|---|
| **P0** | Supervised MSE on \(U^{\mathrm{resid}}\) | 216 | ThradBERT, bge-small, DeBERTa-small; freeze encoder on/off | lr 1e-5–1e-4, wd 0.01/0.1, ep 5–20 | all |
| **P1** | Pairwise BCE / ListNet | 324 pairs | ThradBERT, bge-small | lr, margin, freeze | all |
| **P2** | Offline bandit OPE | 270 | thresholds on P0; always-late / wait | \(\tau\in\{-1,-0.5,0,0.25\}\) | CPU |
| **P3** | LoRA-DPO tiny LLM | 324 pairs | SmolLM3-3B, Phi-4-mini, Qwen3-4B | r=8/16, \(\beta=0.1/0.3\), 1–2 ep | atlas only |
| **P4** | Intent gate, external only | 8k | ThradBERT or Qwen3-1.7B | 2–3 ep | atlas / colab |

First launch, if you approve: **P0 + P2 only**. That is the industrially honest pair (harm model + how a threshold policy would have scored). P1 after. P3 only if P0 is null and we still want a readable YES/NO. P4 is a separate data job (new binary rubric on WildChat).

## 3. Models identified (Raschka gallery + current HF)

Gallery: [sebastianraschka.com/llm-architecture-gallery](https://sebastianraschka.com/llm-architecture-gallery/) (93 models, last gallery update Jul 2026; site map 2 Sep 2026). Most of that board is 30B–2.8T. For a **50 ms retrieval gate** we want encoders, not Kimi K3.

**Train / serve (recommended order)**

1. `Thrad/thrad-bert-conversation-classifier` (67M) — already in the product
2. `BAAI/bge-small-en-v1.5` (33M)
3. `microsoft/deberta-v3-small` (44M)
4. `HuggingFaceTB/SmolLM3-3B` — open recipe, LoRA on Atlas
5. `microsoft/Phi-4-mini-instruct` (3.8B)
6. `Qwen/Qwen3-4B-Instruct-2507` — judge / DPO; we already know it saturates the old rubric
7. `Qwen/Qwen3-1.7B` — laptop16 judge / P4
8. `meta-llama/Llama-3.2-1B-Instruct` — gated, Raschka’s local-experiment size

Rejected for v1: 35B chat model, gallery MoEs (Inkling, GLM-5.x, Qwen3.6 3B-active until P0 exists).

Full cards: [`configs/models.yaml`](configs/models.yaml).

## What I will not do until you say go

- No training job on GPU 1
- No new 4B judge pass
- No thesis / paper / deck edits
- No PPO

When you say go, the first command is P0 on ThradBERT, freeze-encoder, LOPO, then P2 OPE against always-late and always-wait.
