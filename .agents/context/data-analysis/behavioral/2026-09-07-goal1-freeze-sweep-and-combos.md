# 7 September (afternoon): Goal 1 freeze, exploratory sweep, Goal 5 combos

Walter's analysis space, `analysis/walter/`. Reads Walter's Gold
(`behavioural/outputs/gold/`, 7 Sep morning). Scope answers below were
Walter's; free text is **discarded for good** (codebook + LLM judge
will not be run before 17 Sep; `tab:analysis-families` should say
free text is not analysed, not "descriptive").

## Layout

Scripts produce artefacts; notebooks are thin viewers.

```
analysis/walter/
  statkit.py                        paired D, Friedman, pairwise Wilcoxon, Spearman,
                                    rmcorr, partial Spearman, raw/Holm-family/BH-global
  behavioural/
    stats/run_confirmatory.py  ->   outputs/confirmatory/   01_behavioural_confirmatory.ipynb
    stats/run_sweep.py         ->   outputs/exploratory/    02_behavioural_sweep.ipynb
  combos/
    run_combos.py              ->   outputs/{beh_eeg,beh_traj,traj_eeg,threeway}/
                                    03_beh_x_eeg / 04_beh_x_traj / 05_traj_x_eeg / 06_threeway
```

## Goal 1 confirmatory freeze (`outputs/confirmatory/confirmatory_planned_D.csv`)

Planned family, person grain, \(n=54\). Paired \(t\) primary (mean, CI,
\(d_z\)); Wilcoxon \(p\) raw; Holm within outcome. Same three \(D\)
weights as EEG Dataset A. Results 7.2 is written from this table.

Surveys (4 × 3 = 12 tests), Holm survivors:

| outcome | contrast | mean [CI] | \(d_z\) | Holm \(p\) |
|---|---|---|---|---|
| manipulation | any ad − no ad | +1.27 [0.76, 1.78] | 0.66 | \(3\times10^{-5}\) |
| manipulation | implicit − explicit | −0.62 [−1.13, −0.10] | −0.32 | .022 |
| manipulation | early − late | +0.58 [0.21, 0.95] | 0.41 | .007 |
| notice | any ad − no ad | +2.07 [1.53, 2.62] | 1.01 | \(<10^{-8}\) |
| notice | implicit − explicit | −1.15 [−1.71, −0.59] | −0.55 | \(3\times10^{-4}\) |
| credibility | early − late | −0.33 [−0.55, −0.11] | −0.39 | .016 |

Trust: Holm-null on all three (any-ad −0.34 [−0.71, 0.03], Holm .15;
early − late −0.44 [−0.81, −0.08], raw .021, Holm .063). Credibility
any-ad and implicit − explicit null. Notice early − late null.

Recall (2 × 2 = 4 tests, ad conditions only): `recall_memory`
implicit − explicit −1.45 [−1.87, −1.04], \(d_z=-0.93\), Holm
\(<10^{-7}\) (explicit ads are remembered). `recall_trust_shift`
early − late −0.49 [−0.90, −0.08], Holm .047. Other two null.

So Goal 1 is not "two Holm cells": it is 6 of 12 on surveys plus 2 of 4
on recall, with the same frozen composites Katerina was given. Trust
is the null. Do not let a formula rewrite move this.

## Exploratory sweep (`outputs/exploratory/`)

1,755 tests. Outcomes: 4 primary, 4 secondary, 4 item pairs, 17 raw
items, 11 process, 10 trajectory. Blocks: planned \(D\) + format ×
timing, Friedman (5, 4-ad), 10 pairwise Wilcoxon, BFI moderation of
each \(D\), BFI on person level. Family for Holm = outcome × block; BH
across the sweep. Raw 215 / Holm-family 106 / BH-global 53. Expected
raw false positives at .05: 88.

What BH keeps outside the primary/item-pair tiers:

- **Extraversion tracks conversational wandering.** Person-mean
  trajectory entropy, shift rate, diversity, \(n\) shifts correlate
  with BFI-E at \(\rho \approx 0.49\)–\(0.54\) (\(n=54\), BH
  \(<.01\)); max persistence \(\rho=-0.51\). E also correlates
  negatively with perceived relevance (\(-0.54\), the strongest single
  cell in the sweep) and with `llm_addressed`, convincingness,
  helpfulness. Level effects, not treatment effects. Personality ×
  trajectory, which is a combo the goal list did not name.
- `llm_impartial` drops under any ad (−0.82, BH .029); pairwise no ad
  vs both early conditions.
- `relevance` and `llm_reliable` early − late −0.50 / −0.46 (BH
  .035 / .039): late ads cost perceived relevance and reliability,
  consistent with the credibility early − late confirmatory cell.
- `llm_not_useful` implicit − explicit \(D\) moderated by
  Agreeableness (\(\rho=-0.44\)).
- Process: **zero** Holm-family or BH hits across 349 tests. Reply
  latency, duration, message length, typing do not move with condition.
- Trajectory metrics by condition: zero hits on planned \(D\),
  Friedman, pairwise, Def 6 (matches trajectory stages 2–4). All
  trajectory hits are BFI-E level correlations.

Everything above is exploratory. If any of it goes in Results, write
"exploratory, 1,755 tests, BH" next to it.

## Combos (`analysis/walter/combos/outputs/`)

2,560 tests over four families. Grains: **D** (person \(D_i\), same
contrast both sides, Spearman) and **RM** (repeated-measures
correlation on the person × condition rows, person centred,
Bakdash–Marusich).
EEG all 16 \(k=37\) features, headline Fz \(\theta\) + posterior
\(\alpha\). Holm within combo × grain × contrast; BH across combos.

**Zero Holm-family hits, zero BH-global hits, in every family.**
Raw hits 105 vs 128 expected by chance.

- beh × EEG (\(n=18\)): 960 tests, 44 raw, headline 0/32. Lowest raw
  cells are process × engagement indices on implicit − explicit
  (\(\rho\approx-0.69\), raw .0014, Holm .35).
- beh × traj (\(n=54\)): 600 tests, 30 raw. Headline 3/80 raw
  (credibility implicit − explicit ~ entropy \(\rho=0.32\), raw .019).
- traj × EEG (\(n=18\)): 640 tests, 10 raw (fewer than chance).
- three-way partials (\(n=18\)): 360 tests, 21 raw. Cluster:
  notice any-ad ~ trajectory wandering | EEG, \(\rho_{partial}\approx
  0.6\), Holm .32. That is behaviour × trajectory with EEG held, not an
  EEG finding.

Read for the thesis: the combo layer is a null at these \(n\). Say
so in one paragraph of 7.5 with the test counts. Do not pick the
\(\rho=-0.69\) cell.

## Trust deep dive (7 Sep, midday) — `outputs/exploratory/trust/`

Script `stats/trust_deepdive.py`. Single item "I felt I could trust
the chatbot" (1–7), one answer per person per condition.

The data. Means: no ad 5.37, implicit early 4.93, implicit late 5.28,
explicit early 4.69, explicit late 5.22. Both late cells sit on the
no-ad level; both early cells sit below it. Same shape in lab
(4.89 / 4.22 / 4.89 / 4.06 / 4.89) and crowd; lab trusts less overall
(4.59 vs 5.35, Mann–Whitney .008). Heavy tails: 24 of 54 people span
\(\ge 3\) points across conditions, one lab person +5 on any-ad, one
−4. Median any-ad \(D\) −0.25; 30 down / 7 zero / 17 up.

What the tests say about the same matrix:

- Friedman over 5: \(\chi^2 = 9.55\), \(p = .049\), \(W = .04\).
  Over the 4 ad conditions: \(p = .20\).
- Ten pairwise Wilcoxon, Holm within 10: **no ad − explicit early
  +0.69, Holm .029** is the only survivor. Implicit late − explicit
  early raw .025, Holm .23.
- Planned \(D\), paired \(t\): any-ad −0.34 [−0.71, 0.03], \(p = .076\)
  (Holm .15); early − late −0.44 [−0.81, −0.08], \(p = .021\)
  (Holm .063). **Wilcoxon on the same \(D\): any-ad \(p = .016\),
  early − late \(p = .026\).** The \(t\) is dragged by the two
  \(|D| \ge 4\) people; the rank test is not.
- Lab early − late −0.75, \(d_z = -0.61\), \(p = .019\) at \(n = 18\).
  Crowd −0.29 ns.

So "trust is null" is a statement about the paired \(t\) under Holm
on a heavy-tailed 7-point item. Under Friedman + pairwise Wilcoxon
(the sweep engine) trust shows an omnibus at .049 and one Holm pair:
explicit-early ads cost trust relative to no ad. The honest thesis
sentence is: trust is Holm-null on the planned paired \(t\); the
rank-based sweep finds the early-explicit cell; effect \(\approx\)
two thirds of a point. Do not switch the confirmatory statistic
because the rank test is friendlier.

Confounds checked: session position has no effect on trust
(Friedman over position .94; last − first −0.20, \(p = .61\)); task
genre means 4.98–5.16; design is not perfectly balanced (no-ad
over-represented at positions 1–2), but with no position effect that
does not move trust. Trust \(D\) tracks credibility \(D\) (+.40) and
manipulation \(D\) (−.40), not notice \(D\) (−.09): people who trusted
less under ads are the ones who felt manipulated and found the bot
less credible, not simply the ones who noticed. No BFI trait moderates
trust \(D\). Cued-recall "after seeing this content I could trust the
chatbot" has the same shape: explicit early 3.85, explicit late 4.56.

**Ordinal / mixed models (7 Sep, 12:30).** `stats/run_ordinal.py` →
`outputs/ordinal/`. Ordinal GEE (proportional-odds logit, person as
cluster, sandwich SE; no R / PyMC on this machine, so no CLMM) for
the 16 single items; random-intercept LMM for composites and trust.
All adjust for arm, session position (centred), task genre.
Contrasts are Wald tests on the same three \(D\) weights; Holm
within outcome. `primary_four_engines.csv` puts paired \(t\),
Wilcoxon, GEE and LMM side by side on the 12 primary cells.

- Manipulation, notice, credibility: all four estimators agree with
  the freeze (same cells survive, same cells do not).
- **Trust any-ad**: \(t\) .076, GEE .075 (OR 0.68), LMM .13. The
  Wilcoxon .016 is the odd one out. Not there.
- **Trust early − late**: \(t\) .021 (Holm .063), GEE .044 (OR 0.67,
  Holm .13), LMM .014 (**Holm .041**). Borderline; the adjusted LMM
  crosses, the others do not. Per-condition: only explicit early
  separates from no ad, in both engines.
- Item-level Holm survivors (GEE): sponsored-notice OR 11.3 under any
  ad and 0.24 implicit vs explicit; pushing 3.6 / manipulate 2.6
  under any ad; reliable 0.53, impartial 0.59, relevant 0.50,
  convincing 0.52 early vs late; impartial 0.46 under any ad.
- Recall: memory implicit − explicit −1.46 log-odds (Holm < 1e-4);
  trust-shift early − late GEE Holm .053, LMM Holm .048.

**Bayesian random-intercept ordered logit (PyMC 6.3.1 installed 7 Sep
12:35; `stats/run_bayes_ordinal.py` →
`outputs/ordinal/bayes_ordinal_random_intercept.csv`).** The
subject-specific model the GEE is not. Trust: any-ad OR 0.79
[0.47, 1.30], \(P(<0)=.83\); early − late OR 0.59 [0.35, 0.96],
\(P(<0)=.98\); explicit early vs no ad OR 0.51 [0.26, 0.98]; implicit
early 0.72 [0.38, 1.36]; both late cells ≈ 1. Person SD 1.39
log-odds (≈ 4× odds per SD): who the person is dwarfs condition.
Positive control `behaviour_pushing`: any-ad OR 3.0 [1.8, 5.2],
explicit early 5.9. \(\hat R \le 1.002\), ESS > 1,700, 0 divergences,
6 s per model. Same verdict as GEE / \(t\).

Thesis wording for trust stays: Holm-null on the planned paired
\(t\); one exploratory pair (no ad − explicit early) and a borderline
adjusted early − late. Do not swap the primary statistic. ELI5 of
the four estimators and why they disagreed on one cell is in the
7 Sep chat; the short form: \(t\) averages distances, Wilcoxon ranks
directions, ordinal models count box-shifts with the person as
cluster; the ordinal models sided with the \(t\).

**Gold bug fixed.** `ad_turn` on `condition_features.csv` /
`advertisement_features.csv` read 4 for 26 of 54 `block_early` cells
(all sessions from 27 July, production logger). Cause: block ads stay
on screen and re-fire `ad_displayed` on turns 2, 3, 4 (twice per
turn); the builder let the last one overwrite `ad_turn`. Raw
`ad_injected` was at turn 2 for every one of them; delivery was
right. `build_gold.py` now takes `ad_turn` from injection only.
`n_ad_displayed` is a render count (6 for block cells), not a delivery
count. Rebuilt; confirmatory table byte-identical.

## Two streams and the split with Katerina (7 Sep, 14:00)

Katerina's stream is omnibus + post-hoc (Friedman over conditions,
pairwise Wilcoxon, Holm). She is extending it to the fifth condition
(no ad) and both arms. Walter's stream is the planned contrasts
above. Division:

- **Planned (Walter, confirmatory, Results 7.2).** 4 outcomes × 3
  \(D\) + recall 2 × 2; paired \(t\), Holm within outcome. Frozen.
- **Localisation (post-hoc).** Each ad condition − no ad, Holm across
  4 within outcome: `outputs/confirmatory/posthoc_vs_control.csv`,
  `forest_posthoc_vs_control.png`, notebook 01 §2b. Survivors:
  notice all 4, manipulation all 4 (explicit early largest,
  \(d_z=0.97\)), trust explicit early − no ad −0.69 [−1.17, −0.20],
  Holm .031. Credibility none. This is where "which condition" is
  answered; it is post-hoc and reported with the family size.
- **Omnibus + 10 pairs (Katerina's stream).** Until her version runs
  on Gold (N = 54, five conditions, frozen composites), the sweep's
  Friedman + pairwise block (notebook 02 §5) is the stand-in. She
  must use Gold and the composites in `build_gold.py`; changing the
  formula or dropping items is not allowed.

Process variables: `outputs/eda/process_by_condition.csv` (mean, SD
by condition for duration, first-message latency, reply latency,
message length, words, assistant length, typing, conclusion). 0
corrected hits in the sweep; reported as a descriptive manipulation
check only. `n_typing_events` is constant 2.7 in every cell and
`conclusion_n_words` is 0 — both are logger artefacts, do not
report them as findings.

Giant Spearman matrices (`outputs/eda/giant_corr_*.png` + `_rho.csv`,
`viz.giant_corr`, `stats/run_giant_corr.py`): person means N = 54
(37 variables, blocked and clustered), lab n = 18 with 16 EEG,
any-ad \(D_i\). Dots are raw \(p<.05\); ~5 % noise by construction.
What they show: survey block coheres (trust · credibility ·
helpfulness · convincingness · relevance · influence), manipulation
· notice · pushing form a second block anticorrelated with
neutrality; process variables are one block that does not touch
surveys except assistant length; BFI-E is negatively related to
trajectory shifting (already a sweep hit, BH-null); EEG blocks
are absolute vs relative power, and do not touch surveys at
n = 18. Curiosity artefact, not a result.

Notebook repair: `Behavioural_EDA.ipynb` (7 Sep morning) had raw
`\(` escapes in its JSON and no `outputs` fields; nbformat could not
read it. Fixed and executed; giant correlations and the process
table appended.

## Assumption check and engine concordance (7 Sep, 17:00) — `outputs/assumptions/`

`stats/run_assumptions.py`; shown in notebook 01 §2c. Answers "do we
need a normality test to choose between \(t\) and Wilcoxon".

- The paired \(t\) assumption is on the person-level **differences**
  \(D_i\), not the raw Likert. Raw per-condition Likert fails Shapiro
  in 20/20 cells by construction (6–14 distinct values).
- Planned \(D_i\) (16 cells): Shapiro rejects 7/16, all trust /
  credibility (heavy tails, excess kurtosis up to 5.6 from a few
  people). Manipulation, notice, recall \(D_i\) are close to normal.
- Bootstrap percentile CI (10,000, seed 7) is within 3 % of the
  \(t\) CI in every cell (width ratio 0.97–1.01): the \(t\) interval
  is not misled at \(n = 54\).
- Engines (\(t\) Holm, Wilcoxon Holm, sign Holm, bootstrap CI) agree in
  14/16 planned cells. The two disagreements are both **trust**:
  any ad − no ad (\(t\) .15 / Wilcoxon .048 / sign .24; bootstrap CI
  [−0.70, 0.03]) and early − late (.063 / .052 / .24; bootstrap
  [−0.81, −0.09]). The nonparametric result is itself at the boundary.
- Katerina's design on Gold (10 pairs × 4 primaries, Holm-10 within
  outcome): \(t\) and Wilcoxon agree 38/40. Wilcoxon-only: trust no ad
  − explicit early (.029 vs .078), credibility implicit early −
  explicit late (.041 vs .054). No \(t\)-only cell.
  `pairwise_t_vs_wilcoxon.csv`, `pairwise_concordance.png`.

**Decision.** Pre-test-then-switch is not the rule (Rochon, Gatignol &
Kimmel 2012; Zimmerman 2004). Paired \(t\) stays primary as Methods
states; Wilcoxon stays raw beside it; this table is the sensitivity
report (appendix). The trust paragraph names the two engine-sensitive
cells. Friedman / ANOVA are omnibus and not the alternative to a
planned contrast; the nonparametric planned contrast is Wilcoxon on
\(D_i\), which every row already carries.

**Katerina vs Walter, stated precisely.** Same Gold, same composites.
Her post-hoc is Wilcoxon on the 10 condition pairs after Friedman;
Walter's localisation is \(t\) + Wilcoxon on the 4 control pairs. On
the pairs the statistic almost never matters (38/40). The real
difference is the planned contrasts (any-ad pools four conditions vs
one; implicit − explicit and early − late pool two vs two), the family
size (3–4 vs 10), \(N = 54\) vs her 19 lab, and the fifth condition.

**Process variables closed.** Planned \(D\) (+ format × timing) on the
nine process variables: 36 tests, 0 below raw .05, max \(|d_z| = 0.24\)
(assistant reply length, early − late). Figure
`outputs/eda/process_planned_D_forest.png` (from
`viz.forest_dz` on the sweep rows), table
`outputs/eda/process_by_condition.csv`. One sentence in the thesis:
ads did not change how people chatted. Nothing further to run here.

## Judgment calls made without asking

- Confirmatory freeze keeps paired \(t\) + raw Wilcoxon on \(D_i\)
  (Methods already says so; matches EEG). Friedman + pairwise
  Wilcoxon is the sweep engine, not the confirmatory statistic.
- Free text dropped for good.
- Katerina's folder is not read by any of these scripts.
