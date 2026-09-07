# Ad-moment scorer handoff (6 September afternoon)

Walter asked to keep this context current so the next agent does not
re-audit the repo. Read this note, then
`2026-09-06-ad-moment-scorer.md`, then the files under
`analysis/policy/`. Do not re-walk Bronze JSONL unless the Silver
hashes change.

## Status at this write

| Piece | State |
|---|---|
| Silver | Built. 1,479 turns (1,080 primary / 256 beta / 143 unlabeled), 361 conversations. `outputs/silver/build_report.json`. |
| Human anchor | Built. 216 rows, sha256_16 `949605816c501b72`. Composites **provisional** until Goal 1 freeze. |
| Preprocess notebook | `analysis/policy/build_policy_dataset.ipynb` (CPU). Thin wrapper around the two scripts. |
| Trainer notebook | `analysis/policy/ad_moment_scorer.ipynb` updated this afternoon: `atlas` / `laptop16` / `colab` / `kaggle` / `smoke` profiles, rubric version stored on the label CSV, optional UX ridge head (8b). |
| Smoke run | Succeeded on Atlas GPU 1 (~3 min, Qwen3-0.6B, 60 OASST1). Artefacts in `outputs/notebook_runs/smoke/`. |
| Full run | **Aborted.** No finished 4B-judge labels. `outputs/notebook_runs/full/` has partial `labels_real.csv` / `external_prefixes.csv` only. Do not treat those as v2 rubric. |
| Serving hook | Not written. Class `MomentScorer` lives in the trainer notebook only. |
| Thesis / paper / deck | Untouched. Keep it that way until 17 September. |

## What the smoke run actually showed

Do not invent a better story.

- Encoder learns the judge: OOF Spearman \(\hat{\bar r}\) vs \(\bar r\) = 0.539. Tabular ridge on turn + runtime genre = 0.572. **Text did not beat metadata in smoke.** Smoke judge is 0.6B and degenerate; this is plumbing, not a finding.
- Judge vs human anchor: Spearman \(\bar r\) vs \(U^{\mathrm{resid}}\) = −0.035; AUROC vs `good_moment_human` = 0.475 (chance). Recall memory −0.043. Purchasable posterior −0.024.
- Calibrated LOPO AUROC = 0.356. Turn-only AUROC = 0.534 (late ads cost less UX; the turn feature recovers that). \(\hat r\) coefficient is **negative** (−0.21).
- Non-inferiority of high- vs low-\(\hat r\) moments: mean diff −0.088, CI [−0.384, 0.208], margin −0.5, `non_inferior=true`. Wilcoxon raw \(p=0.766\).
- Honest claim after smoke: **receptivity plumbing works; the 0.6B judge does not track humans.** A full 4B-judge run is still required before any rubric talk.

The older context note mentioned a v1→v2 rubric freeze. That revision is
**in the notebook code** (`RUBRIC_VERSION = v2_logprob_0to9`) but has
**not** been run at full scale. Smoke used 0.6B. Do not write “v2 is
validated.”

## Environments (locked this afternoon)

The trainer auto-detects, or set `AD_MOMENT_ENV`.

| Profile | Machine | Judge | \(n_{\mathrm{ext}}\) | enc bs / max_len | Peak VRAM | Wall time (approx) |
|---|---|---|---|---|---|---|
| `atlas` | 2× A100 40 GB (this box; GPU 1 is the free one) | Qwen3-4B-Instruct-2507 | 8000 | 32 / 512 | ~10 GB judge, ~6 GB encoder | ~1 h |
| `laptop16` | 16 GB consumer GPU tomorrow | same 4B, judge batch 4 | 2000 | 16 / 384 | ~10 GB | ~3–5 h |
| `colab` | T4 16 GB, ~12 h cap | 4B, judge batch 8 | 4000 | 16 / 512 | ~10 GB | ~3–4 h |
| `kaggle` | P100 / T4, ~12 h, no internet after start | 4B, judge batch 8; prefer OASST1 (open) | 4000 | 16 / 512 | ~10 GB | ~3–4 h |
| `cpu` / `smoke` | any | Qwen3-0.6B | 60 | 16 / 256 | ~2 GB | minutes |

Overrides: `AD_MOMENT_RUN_MODE=smoke|full`, `AD_MOMENT_JUDGE=...`,
`AD_MOMENT_N_EXTERNAL=...`, `CUDA_VISIBLE_DEVICES=1` on Atlas.

Colab / Kaggle need a zip of `analysis/policy/outputs/{silver,anchor}`
(not `notebook_runs`). Preprocess **on a machine that has Bronze**
(Atlas or the laptop with the repo). The trainer does not walk JSONL.

## X and Y (do not reinvent)

Inference \(X\): serialised last-4-turn prefix \(x_k\) (encoder) plus
\(z_k=(\min(k,8)/8,\ \mathrm{fit}_k)\) (calibrator). No \(\lambda\),
no person, no task, no EEG.

Training \(Y\), two layers:

1. Dense judge \(\mathbf r_k\in[0,1]^4\) (need, ready, safe, no_degrade),
   soft BCE on DistilBERT `Linear(768,4)`.
2. Sparse human \(y_i=\mathbb 1[U_i^{\mathrm{resid}}\ge 0]\) on 216 rows,
   LOPO logistic calibrator → scalar \(m_k\).

Optional diagnostic (not the gate): frozen-encoder head
\(\hat{\mathbf y}\in\mathbb R^6\) =
\((\Delta\mathrm{cred},\Delta\mathrm{trust},\Delta\mathrm{manip},\Delta\mathrm{help},\mathrm{notice}_{\mathrm{sponsored}},\mathrm{recall}_{\mathrm{memory}})\),
LOPO on the 216 ad turns.

Production output: `{moment_score, receptivity, items, veto, insert, abstain}`
plus optional `ux_hat` if that head was trained.

Base model: `Thrad/thrad-bert-conversation-classifier` (67M). Baseline
`BAAI/bge-small-en-v1.5`. Tokenizer fallback `bert-base-uncased`
(ThradBERT repo ships without tokenizer files).

## What the next agent should do

1. Do **not** rebuild Silver/anchor unless Walter asks or Goal 1
   composites freeze (then re-run `build_human_anchor.py` and re-pin
   the sha).
2. Run the **full** trainer on one of the four profiles. On Atlas:
   `CUDA_VISIBLE_DEVICES=1 AD_MOMENT_ENV=atlas AD_MOMENT_RUN_MODE=full`.
3. Read `judge_validation.json`, `ablations.csv`, `calibration.json`,
   and `ux_head.json` if present. Append the numbers to this directory
   as a new dated note. Do not hunt a better rubric unless the 4B
   labels saturate the same way v1 did (descriptive ceiling, not
   anchor AUROC).
4. Keep thesis / paper / deck clean.

## What not to do

- Do not treat format \(\lambda\) as an input or output.
- Do not add EEG features.
- Do not train the encoder on the human anchor.
- Do not launch a 35B judge.
- Do not `--overwrite` ICA models.
- Do not commit `outputs/notebook_runs/` (gitignored).
- Do not release participant text without a consent check.
