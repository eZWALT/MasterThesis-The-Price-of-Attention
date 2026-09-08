# Combos, reduced: reliability, nine headline tests, mixed models, turn and event grains (7 Sep, night)

Code: `analysis/walter/combos/` (`combokit.py`, `run_reliability.py`,
`run_headline.py`, `run_forest.py`, `run_lmm.py`, `run_turns.py`,
`run_events.py`, `run_concordance.py`, `run_task_state.py`,
`summarise_blocks.py`). Viewer: `07_combos_reduced.ipynb`. Ledger:
`outputs/blocks_ledger.csv`, `outputs/blocks_summary.json`.

Supersedes nothing: the 2,560-cell map (`run_combos.py`, notebooks
03–06, Holm/BH-null everywhere) stays as the exhaustive record. These
blocks were planned before they were run (plan message of 7 Sep
afternoon, blocks 0–7); families were declared in the plan and are
reported in full.

## One line

336 new tests, 0 Holm, 0 BH (within table, pooled over the 336, and
pooled over the 2,896 with the map), 10 raw hits where 17 are
expected under the null. Every family-wise Freedman–Lane permutation
\(p > .23\).
The informative result is block 0: **the combos could not have found
what they looked for**, and the reasons are now numbers (with their
18-person sampling intervals; see the reliability caveat below).

## Block 0 — reliability and resolution (`outputs/reliability/`)

Rebuilt the confirmatory Dataset A \(k=37\) cells with the EEG team's
own tile selection (`build_ad_local_epochs.select_tiles`, no Gold
write), split the 37 tiles per cell in two, medianed each half.

- **EEG condition feature, within-person reliability** (Spearman–Brown):
  median 0.65 under random halves (upper bound; adjacent tiles are
  autocorrelated), 0.32 under first vs second half (lower bound; the
  148 s window is not stationary). Broadband absolute power (\(\beta\),
  \(\gamma\), Kislov) 0.9; **Fz \(\theta\) 0.26**, the least reliable
  of the 16; posterior \(\alpha\) 0.70.
- **EEG \(D_i\) reliability** (correlation of half-\(D\)'s across the 18
  people, Spearman–Brown, 0 when the halves disagree): Fz \(\theta\)
  any-ad **0.01**, format **0.00**, timing 0.50; posterior \(\alpha\)
  0.78 / 0.71 / 0.25. **The post-hoc Holm cell (implicit-early −
  explicit-late Fz \(\theta\)) has pair-\(D\) reliability 0 under every
  split** (\(r_{halves}\) −0.14 to +0.06): a mean shift with little
  detectable between-person heterogeneity. Consistent with the
  tenths-of-a-dB Dataset A reading; an individual-differences story
  for that cell has little to stand on.
- **Reliability caveat (reviewer pass 3).** A half-\(D\) correlation
  from 18 people has a wide Fisher interval: the Spearman–Brown
  **upper bound** is ≈ .64 for the Fz \(\theta\) any-ad / format
  \(D\) and .52 for the post-hoc pair. "No detectable" is the honest
  wording, not "zero". Second, **\(k=37\) costs reliability**:
  re-running the random split on every retained tile of the whole
  condition window (~95 per cell, the Gold whole-window aggregation;
  scheme `random_all_tiles`) raises the Fz \(\theta\) condition
  feature from 0.26 to 0.46, its any-ad / format \(D\) to 0.45 /
  0.35, and the post-hoc pair \(D\) to 0.47; posterior \(\alpha\)
  0.70 → 0.78, any-ad \(D\) 0.78 → 0.82. That is the ordinary
  tile-count effect on a single-channel band, not evidence for or
  against the \(k=37\) choice (which was made for onset proximity,
  not reliability). Block 1 therefore carries a whole-window EEG
  sensitivity family (21 tests, min raw \(p=.03\), 0 Holm): the
  cross-modal verdict does not depend on \(k\). Note that the
  whole-window EEG PC1 agrees with the \(k=37\) PC1 only for any-ad
  (.85) and not for format or timing (−.38 / −.55): sixteen small
  \(D\)'s from 18 people do not define a stable first axis.
- **Behavioural composite \(D_i\)**, Cronbach \(\alpha\) of the item
  \(D\)'s (\(n=54\)): helpfulness, relevance, manipulation 0.7–0.86;
  notice any-ad 0.52; credibility format 0.34; neutrality timing 0.37.
  Trust is one item: not estimable.
- **Trajectory \(D_i\)**: the only parallel form is the contextual
  classifier. Agreement of \(D_i\) between the utterance and contextual
  readings of the same chats is **−0.07 to +0.32** (person level
  0.2–0.34). The instrument barely agrees with itself at the
  person-difference grain.
- **Resolution**: raw .05 needs \(|\rho| \ge .47\) at \(n=18\), .27 at
  54; 80 % power at raw .05 needs .62 / .37; Holm within 16 needs
  .66 / .40; the first BH hit of 2,560 needs .83 / .55.
- **Attenuation ceiling** (`attenuation_ceiling_headline.csv`): max
  observable \(\rho\) = \(\sqrt{rel_X rel_Y}\), now tabulated for all
  three EEG-\(D\) reliability readings (\(k=37\) random, \(k=37\)
  first/second, whole-window random) with the "true \(\rho\) needed"
  taken from the **most favourable** one, so the claim below is the
  conservative one. Fz \(\theta\) any-ad or format × any behavioural
  composite: ceiling 0.00–0.27 at \(k=37\), **0.34–0.61** whole-window;
  even at the favourable ceiling a raw-.05 hit at \(n=18\) needed a
  true \(\rho \ge .77\) and a Holm-16 hit needed a true \(\rho > 1\)
  (unreachable). Posterior \(\alpha\) any-ad × manipulation is the
  best-placed pair: ceiling 0.81–0.83, raw hit needs true \(\rho \ge
  .57\), Holm-16 \(\ge .80\).

## Block 1 — one score per modality (`outputs/headline/`)

PC1 of the z-scored \(D_i\) block, per contrast. Behaviour PC1 =
negative evaluation (manipulation up; trust, credibility,
helpfulness, convincingness, relevance, neutrality down; 48–52 %
variance). Trajectory PC1 = movement (n_shift, diversity, entropy up,
max_persistence down; 65 %). **EEG PC1 = the slow-vs-fast spectral
tilt** (\(\delta\), \(\theta\), rel-\(\delta\) up; \(\beta\),
\(\gamma\), rel-\(\beta\), rel-\(\gamma\), engagement indices down;
31–43 %). Fz \(\theta\) loads 0.03–0.51 and posterior \(\alpha\)
−0.24–0.34 on it: the a-priori primaries are not the main EEG axis.

Nine tests, Holm within nine: 0 hits. Closest: behaviour × trajectory
any-ad \(\rho=.25\) (\(n=54\), \(p=.06\)); trajectory × EEG early−late
\(\rho=-.45\) (\(n=18\), \(p=.06\)). Planned-primaries family (PC1 ×
Fz \(\theta\) / posterior \(\alpha\), 12 tests) min raw \(p=.26\).
Process PC1 family (duration, reply latency, message length; 9
tests): process × EEG tilt at format \(\rho=.40\), \(p=.10\); same
direction as the raw process × engagement cluster below. z-mean
composites, lab-only, and partial-given-arm sensitivities agree, and
so does the whole-window EEG family (21 tests, min raw .03, 0 Holm).

**PC1 stability** (`pc1_variance.csv`, `pc1_loo_*`): leave one person
out and refit. Behaviour, trajectory and process PC1 reproduce the
full fit at \(\ge .99\). EEG PC1 does not: minimum score agreement
.82 / .99 / .83 and minimum loading cosine .84 / .95 / .67 for any-ad
/ format / timing at \(k=37\); the whole-window format axis is .61 /
.68, and whole-window PC1 agrees with the \(k=37\) PC1 only at any-ad
(.85; format −.38, timing −.55). Sixteen small \(D\)'s from 18 people
do not define a stable first axis; the a-priori primaries family is
the interpretable EEG test, the tilt PC1 is a summary.

## Block 2 — forests (`outputs/forest/`)

Every a-priori cell's interval crosses zero. Twelve smallest raw
\(p\) of the 2,560: Holm \(\ge .32\), BH .90. The only coherent raw
cluster: all 21 process × fast-band cells at the format contrast are
negative (\(\rho\) −0.15 to −0.69; reply latency × Pope −0.69, raw
.0014, Holm .35). Variables inside the cluster are correlated, so it
is not 21 replications. Exploratory.

## Block 3 — mixed models (`outputs/lmm/`)

Lab 90 rows. Model A `y ~ C(condition) + pos + eeg_wc + (1|person)`;
B0 `y ~ late + explicit + pos + eeg_wc` on 72 ad rows; B adds
`late:eeg_wc + explicit:eeg_wc`. Outcomes trust, credibility,
manipulation, notice, log latency, log length; EEG Fz \(\theta\),
posterior \(\alpha\), tilt. 72 tests: 0 Holm. Freedman–Lane
max-\(|t|\) family \(p\) = .69 (A), .74 (B0), .89 (B).

## Block 4 — turn grain (`outputs/turns/`)

1,080 user turns, LMM with person + conversation effects,
`C(task_genre)` covariate. **Task assignment is randomised, not
counterbalanced**: implicit-late drew 30/54 Transactional tasks,
no-ad 27/54 Social; turn-2 shift probability, before any ad is on
screen, is .71 Transactional vs .87 Informational (by condition
\(\chi^2\) \(p=.17\)). A shifting turn is not shorter, longer or
slower (4 tests, min \(p=.16\)). **Post-ad turn** (turns 3–4 in
early conditions vs the same turns with nothing on screen): length
−16 % to +18 %, latency −5 % to +21 % (95 % CI), shift log-odds
+0.31 [−0.32, 0.94], purchasable-products mass unchanged. Late ads
(reply 4) have no post-ad user turn.

## Block 5 — event grain, Dataset B (`outputs/events/`)

72 primary-eligible ads, post − pre deltas within-person centred,
person random intercept, `late + explicit + pos`. Targets: cued
recall memory and trust shift, the chat's notice / manipulation /
trust, Definition 6 shift and divergence (36 early ads), next-turn
length and latency (36). 135 tests: 0 Holm, 0 BH; Freedman–Lane
family \(p\) .23 (headline 27) / .36 (all). Best a-priori cell:
ad-locked Fz \(\theta\) → notice, 0.68 Likert per within-person SD,
raw .005, cell permutation .02, Holm .14, sign stable under
leave-one-person-out.

**Methods warning.** `ad_associated_shift` is 33/36 among the
EEG-eligible early ads; three people are discordant. A GEE binomial
gave \(\gamma\) \(p=.0003\) (Holm-108 .028, BH .035) and \(\beta\)
\(p=.002\). The person-fixed-effects Freedman–Lane permutation gives
.80 and .93; the fixed-effects \(t\) is −0.21; sign test 1/3;
Mann–Whitney on raw deltas .55. The GEE numbers stay in
`event_tests.csv` as `gee_*` columns to document why they were not
used. Do not report them as a hit.

Also found and fixed on the way: permuting the EEG column within
person while keeping within-person covariates fixed is not a valid
null (EEG differs by format within person). All permutations are
Freedman–Lane on reduced-model residuals with persons as blocks
(`combokit.FLSpec`). Per-cell permutation seeds are CRC32 of the cell
name (Python `hash()` is process-randomised).

## Block 6 — concordance (`outputs/concordance/`)

Within-person-centred condition profiles in pooled within-person SD
units. Behaviour: notice and manipulation separate no-ad from
explicit by ~1.5 SD. Trajectory: every condition within ±0.2 SD.
EEG: intervals cross zero; Fz \(\theta\) implicit-early −0.5 vs
explicit-late +0.5 is the post-hoc pair. Kendall \(\tau\) between
orderings is descriptive only (5 conditions).

## Block 7 — write−read trait (`outputs/task_state/`)

`task_state_person_features.csv` (median write − read per person) ×
behavioural \(D\), levels, trajectory \(D\); 44 tests, 0 Holm.
Closest: write−read Fz \(\theta\) × notice early−late \(D\),
\(\rho=.65\), raw .003, Holm .11.

## What may go in the thesis (user decides; nothing pushed)

**Superseded 7 Sep evening for the declared families**: the four
Methods rows are estimated exactly as declared in
`analysis/walter/combos/run_thesis_families.py` (`outputs/thesis/`) and
drafted for Results 7.5 / Discussion 8.5 in
`../../writing/2026-09-07-combos-ch7-ch8.md`. Blocks 1–7 still stay out
of the Results body (one exploratory paragraph + `tab:results-checks`
rows). The list below is the earlier position.

- Discussion `sec:disc-trajectories` / combos paragraph: the
  cross-modal families are null **and** block 0 explains why in
  numbers (no detectable between-person reliability of the Fz
  \(\theta\) \(D_i\) at \(k=37\), upper bound ≈ .6; trajectory
  \(D_i\) inter-classifier agreement < .33; \(n=18\) resolves only
  \(|\rho| > .47\)). This is not an MDE sermon (withdrawn 6 Sep); it is
  a measurement statement about the scores that were correlated.
  Write "no detectable", never "zero".
- Discussion `sec:disc-eeg`, post-hoc pair: pair-\(D\) reliability
  not detectable at \(k=37\) (upper bound .52; .47 whole-window) →
  mostly a mean shift, little room for an individual-differences
  reading. One sentence at most, and only if the post-hoc cell is
  mentioned at all.
- Nothing from blocks 1–7 belongs in Results. The GEE episode is a
  methods footnote at most.

## Reviewer passes (what changed because of them)

1. Task-balance check → `task_genre` covariate at the turn grain;
   Wald-only inference in block 5 → per-cell Freedman–Lane \(p\);
   arm confound in behaviour × trajectory → partial Spearman; no
   ledger → `summarise_blocks.py`.
2. `explicit` as covariate for chats with no ad yet → `late_chat`;
   process variables missing from the headline → `process_PC1`
   family; post-hoc pair \(D\) reliability added; negative
   Spearman–Brown values → 0; block 6 title de-claimed.
3. Prose numbers re-derived from the CSVs (post-ad CIs corrected);
   `hash()` seeds → CRC32; notebook executed end to end; Fisher
   intervals on every half-\(D\) correlation ("reliability ≈ 0" →
   "no detectable", upper bound ≈ .64); `random_all_tiles` scheme
   shows \(k=37\) costs Fz \(\theta\) reliability; whole-window EEG
   sensitivity family added to block 1 (336 tests in total, 10 raw
   hits, 0 Holm / BH). Attenuation ceiling re-tabulated for all three
   reliability readings (the old "upper/lower" columns were
   mislabelled where first/second exceeded random) and the "true
   \(\rho\) needed" now uses the most favourable ceiling. Pooled BH
   over 336 and 2,896 added to the ledger. PC1 leave-one-out
   stability added. Found that `run_headline.py` had been crashing in
   the loadings figure since the process family was added
   (`PRETTY['proc']` missing), leaving `pc1_loadings.png` and
   `headline/summary.json` stale while the CSVs were current; fixed
   and regenerated. Notebook re-executed (10/11 code cells produce
   output; check that, not just the absence of error cells).
4. From-scratch reproducibility, both pipelines. Combos: all ten
   scripts exit 0 (`run_combos` 7 s, `run_reliability` 99 s,
   `run_events` 40 s, rest < 10 s), notebook 07 executes, and every
   headline number (336 / 10 / 0 / 0; family \(p\) .69 / .74 / .89 /
   .36 / .23) is identical to the documented run (seeded). Behavioural:
   `build_gold` → `run_eda` → `run_giant_corr` → `run_confirmatory` →
   `run_sweep` → `run_ordinal` → `trust_deepdive` → `run_bayes_ordinal`
   all exit 0; the 14 Gold CSVs are **byte-identical** after the
   rebuild; notebooks EDA / 01 / 02 execute. The `random_all_tiles`
   medians reproduce the Gold whole-window `*_median` columns to
   \(10^{-15}\) on all 90 cells, so the whole-window scheme is on the
   Gold tile set. Warnings audited: the 35 constant-input Spearman
   warnings in the sweep come from cells that are dropped before
   recording (1,755 rows, 0 NaN \(p\)); the 9 GEE `sqrt` warnings
   leave no NaN SE or \(p\) in any ordinal table (NaN `OR` is by
   design on covariate rows and LMM rows); `traj_shifted_into_purchasable`
   agreement is undefined because the contextual classifier never
   fires it (now a `note` column, no warning). Bayesian ordinal:
   \(\hat R\) 1.002, ESS 1,782, 0 divergences. Wording: the RM grain
   label "condition state" (a banned Dataset A display name) renamed
   to "person × condition rows, person centred" in `run_combos.py`
   and the 7 Sep freeze note; notebook 01 §5 now separates the
   confirmatory verdict (trust null at the paired \(t\)) from the
   sensitivity split on early − late.
