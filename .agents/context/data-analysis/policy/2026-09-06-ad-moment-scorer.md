# Ad-moment scorer (6 September 2026)

Side project, **not a thesis goal**. The insertion-policy model stays
dropped for the manuscripts (`../2026-08-24-insertion-policy-model-dropped.md`).
Nothing here enters thesis, paper, or deck before 17 September. Future
Work may name it in one sentence and must say the sample alone is too
small for a serving \(\pi\).

**Live status:** `2026-09-06-residual-scorer-and-next-ms-qsa.md`
(research line). Numbers: `2026-09-06-evening-handoff.md`.
This file is the *original* judge-calibrator design. We did not ship
it; the 4B judge saturates and does not track \(U\).

## What it is

A serving-policy component \(\pi\): given the conversation up to user
utterance \(u_k\), output **one scalar** \(m\in[0,1]\), how good this
moment is for *some* advertisement. Presentation \(\lambda\) is a
coordinate of \(a_k\) realised by \(\mu\) (`theory.tex`), so it is
**neither an input nor an output**. No EEG, no person covariates, no
task ids at inference. Those exist in Silver only as fold ids and to
denoise labels.

\[
x_k=\mathrm{serialise}\big([\texttt{TURN}\ \min(k,8)],\,u_{k-3},a_{k-3},\ldots,u_k\big),
\quad
z_k=\big(\min(k,8)/8,\,\mathrm{fit}_k\big)
\]

\[
\hat{\mathbf r}_k=\sigma(W h_\theta(x_k)_{[\mathrm{CLS}]}+b)\in[0,1]^4,
\quad
m_k=\sigma(\alpha^\top[\bar{\hat r}_k,z_k]+\beta)
\]

Human label (216 rows, encoder never trains on it):

\[
U_i=\tfrac13(\Delta_{\mathrm{cred}}+\Delta_{\mathrm{trust}}-\Delta_{\mathrm{manip}}),\quad
\Delta^y_i=y_{i,\mathrm{ad}}-y_{i,a^\emptyset},\quad
y_i=\mathbb 1[U_i^{\mathrm{resid}}\ge 0]
\]

\(U\) is residualised on \(\lambda\) and task so format is marginalised
at label construction, not at inference.

Optional diagnostic head (not the gate): frozen encoder → 6 UX deltas
on the same 216 rows.

## Files

- Preprocess (CPU, needs Bronze logs):
  `analysis/policy/build_policy_dataset.ipynb`
  → `build_policy_silver.py` → `outputs/silver/{turns,conversations}.csv`
  → `build_human_anchor.py` → `outputs/anchor/human_anchor.csv`
  (sha256_16 `949605816c501b72`).
- Train (GPU): `analysis/policy/ad_moment_scorer.ipynb`
  Env profiles: `atlas` / `laptop16` / `colab` / `kaggle` / `smoke`.
- Run artefacts: `outputs/notebook_runs/<mode>/` (gitignored).

## Rubric

`RUBRIC_VERSION = v2_logprob_0to9`. Four items (need, ready, safe,
no_degrade), 0–9 anchors, expected value over digit-token
probabilities. v1 (0/1/2 JSON) is documented as saturating; that
revision is in the notebook. **Full-scale v2 labels have not been
produced.** Smoke used Qwen3-0.6B.

Veto genres (`other_obscene_or_illegal`,
`relationships_and_personal_reflection`) are \(\Gamma\), not learned.

## Honesty rules

- The judge defines the weak label. Revise the rubric only on a
  descriptive failure (ceiling / no variance), not by hunting anchor
  AUROC.
- Do not pick windows, \(\tau\), or the judge by the human AUROC.
  The ablation ladder is fixed in the notebook config.
- Shuffled-label control must sit near 0.5; report it next to the real
  AUROC.
- If the anchor cannot separate moments, the deliverable is a
  receptivity scorer with a non-inferiority guarantee, stated as such.
- Participant text is not released without a consent check.
- Composites provisional until Goal 1 freeze; rebuild the anchor and
  re-pin the sha.

## Compute (four places)

See the afternoon handoff table. 67M encoder fits anywhere. The judge
is the GPU hog (~8–10 GB for 4B fp16). Sequential: delete the judge
before fine-tuning. No 35B. No A100 required.

Colab / Kaggle: zip `outputs/{silver,anchor}` only. Preprocess where
Bronze lives.
