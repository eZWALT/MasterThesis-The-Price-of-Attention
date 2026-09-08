# Combos (Goal 5)

```bash
python analysis/walter/combos/run_combos.py
```

Reads only `analysis/walter/behavioural/outputs/gold/combo_threeway*.csv`.
Nothing is re-joined here.

| Notebook | Family | \(n\) |
|---|---|---|
| `03_beh_x_eeg.ipynb` | behaviour × EEG | 18 lab |
| `04_beh_x_traj.ipynb` | behaviour × trajectory | 54 |
| `05_traj_x_eeg.ipynb` | trajectory × EEG | 18 lab |
| `06_threeway.ipynb` | partial Spearman, three-way | 18 lab |

Grains: **D** (person-level planned \(D_i\), Spearman, same contrast
both sides) and **RM** (repeated-measures correlation on condition
state, person centred out). EEG: all 16 Dataset A \(k=37\) features
swept; Fz \(\theta\) + posterior \(\alpha\) headline. Trajectories:
`utterance` source only.

Outputs: `outputs/<family>/{tests,tests_headline,hits_raw,hits_holm_family,hits_bh_global}.csv`,
`outputs/combos_all_tests.csv`, `outputs/summary.json`.

Association, not mediation. Holm is within `combo × grain × contrast`;
BH runs across all combo tests. Quote the test count with any hit.

## Reduced blocks (7 Sep, night)

```bash
cd analysis/walter/combos
python run_reliability.py   # block 0: split-half reliability of k=37 features and D_i, resolution, attenuation ceiling
python run_headline.py      # block 1: PC1 per modality per contrast, 9 headline tests (+ process, primaries, sensitivities)
python run_forest.py        # block 2: CI forests of the a-priori cells and the top-12 raw cells of the map
python run_lmm.py           # block 3: LMM state association and EEG x timing/format moderation (lab 90 / 72 rows)
python run_turns.py         # block 4: turn grain, shift x process and the post-ad turn (1,080 user turns)
python run_events.py        # block 5: Dataset B ad-locked delta -> recall, Def. 6 shift, next turn (72 ads)
python run_concordance.py   # block 6: condition profiles per modality (descriptive)
python run_task_state.py    # block 7: write-read EEG trait x behavioural / trajectory D (18)
python summarise_blocks.py  # ledger -> outputs/blocks_ledger.csv, outputs/blocks_summary.json
python build_notebook_07.py && jupyter nbconvert --to notebook --execute --inplace 07_combos_reduced.ipynb
```

Shared helpers: `combokit.py` (column catalogues, Spearman with
Bonett–Wright CI and leave-one-out range, sign-oriented PC1,
Freedman–Lane permutation with persons as blocks). Viewer:
`07_combos_reduced.ipynb`.

Result: 336 tests, 0 Holm, 0 BH, family-wise permutation \(p > .23\)
everywhere; the same with whole-window EEG in place of \(k=37\).
Block 0 is the part worth reading: Fz \(\theta\) \(D_i\) at \(k=37\)
have no *detectable* between-person reliability (point 0, 18-person
upper bound ≈ .6; .35–.61 with all ~95 tiles, so \(k=37\) costs
reliability on that feature); trajectory \(D_i\) agree at < .33
across the two genre classifiers; \(n=18\) resolves only
\(|\rho| > .47\). Binary targets with a handful of non-events use a
person-fixed-effects permutation, not GEE (see `run_events.py`).
Note: `.agents/context/data-analysis/behavioral/2026-09-07-combos-reduced-blocks.md`.

## Declared families for the thesis (7 Sep, evening)

```bash
python run_thesis_families.py   # -> outputs/thesis/{declared_families.csv, summary.json, combos_*.pdf/png}
```

Exactly the four rows of thesis `tab:analysis-families`: behaviour ×
EEG (6 pairs, any ad − no ad, **both** EEG scores \(D^A\) condition
aggregation and \(D^B\) onset-locked, Holm within six each and across
the twelve), behaviour × trajectory (3 composites × \(\delta^{(a)}_2\),
late \(N_{\mathrm{shift}}\); \(N=54\)), trajectory × EEG (Fz \(\theta\),
posterior \(\alpha\) × \(\delta^{(a)}_2\), early pooled both sides),
three-way (lab-arm third side + partials). Plus specificity of the one
surviving cell across all sixteen EEG measures, format / timing pairs,
contextual labelling and whole-window EEG sensitivities, and a timing
split-half reliability of \(D^B\). Result: Dataset A 0/6; Dataset B
trust × posterior \(\alpha\) \(\rho=.80\) \([.48,.93]\), Holm .0004;
everything else null. `\delta^{(a)}_2` is rebuilt from
`analysis/trajectories/outputs/conversations.csv` (\(u_3\ne u_2\)) and
reproduces `tab:traj-crossing` (0.824 / 0.778).

**Alignment warning.** `combokit.spearman_ci` pairs by *position*. Pass
two Series in the same row order or align on `experiment_id` first
(`run_thesis_families.cell` does). A misaligned pair once produced a
spurious \(\rho=.71\) here.
Note: `.agents/context/writing/2026-09-07-combos-ch7-ch8.md`.
