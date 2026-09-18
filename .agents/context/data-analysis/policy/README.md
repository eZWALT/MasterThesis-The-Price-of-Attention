# Side projects (not the thesis)

**Not a thesis goal.** Nothing here enters thesis, paper, or deck
before 17 September.

- **Ad-moment scorer.** Insertion-policy \(\pi\) stays dropped from the
  manuscripts (`../2026-08-24-insertion-policy-model-dropped.md`).
- **Dataset release.** Parked until the thesis PDF is in. Hub layout
  (16 Sep): `2026-09-16-hf-dataset-strategy.md` — nine public Gold
  repos (one per filled cell of the grains figure: behavioural /
  trajectories / EEG / joins), two gated (`events`, `eeg-recordings`),
  collection `price-of-attention`. Older two-bucket note:
  `2026-09-12-dataset-release-side-quest.md`.

Start here, then the newest dated note in this directory.

- **Live research line:** `2026-09-06-residual-scorer-and-next-ms-qsa.md`
  (what the 6 Sep ridge is, done vs not done, next is \(m(s)\) / \(q(s,a)\),
  not another residual). Numbers:
  `2026-09-06-evening-handoff.md`.
- Live winner: `analysis/policy/outputs/experiments/full/BEST.md`
  (Spearman 0.309, CI 0.20–0.41, same-timing 0.639)
- Original scorer design (judge → calibrator; superseded as the
  training story): `2026-09-06-ad-moment-scorer.md`
- Code: `analysis/policy/`
  - preprocess (CPU): `build_policy_dataset.ipynb` wraps
    `build_policy_silver.py` + `build_human_anchor.py`
  - locked serve: `freeze_best.py`, `score_moment.py`
  - artefacts: `outputs/silver/`, `outputs/gold/`,
    `outputs/experiments/full/`

Do not overwrite EEG ICA models. Do not put this model in Results.
