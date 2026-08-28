# EEG post-hoc pairwise sweep (28 August 2026)

Closes backlog item 2, "EEG restructure (post-hoc), Sebastian"
(`../2026-08-27-backlog-and-timeline.md`). Self-contained: read this
alone and you have the whole family.

---

## Verdict

**352 pairwise tests. 0 significant under Holm, Benjamini-Hochberg or
Benjamini-Yekutieli. 0 under every family definition from none to a
single family of 320. 0 under every one of the 65,535 feature subsets.**

Best adjusted \(p\) obtainable anywhere, by any subset, under any
method: **.0799** (Holm), **.0799** (BH), **.1958** (BY). Nothing
reaches .05, and nothing can be made to.

The confirmatory pipeline is untouched and was verified to reproduce
from the same person-level data to 1e-9.

---

## Hard locks

1. **Exploratory. No cell is promoted to confirmatory, ever, whatever
   its \(p\) or \(q\).**
2. Confirmatory EEG is unchanged and **stays on Holm** as pre-specified:
   4 s · median · ICA · \(n=18\), Fz theta and posterior alpha, Dataset
   A 3 planned contrasts, Dataset B 4 planned contrasts
   (`2026-08-20-paper-4s-primary-and-epoch-sensitivity.md`). Switching
   the confirmatory correction after seeing results would be
   indefensible.
3. No ICA refit, no Gold rebuild. New code writes only to
   `analysis/eeg/statistics/outputs/posthoc/` and
   `analysis/eeg/analysis/outputs/figures/posthoc/`.
4. **Do not re-litigate the correction or propose dropping features to
   gain power.** Both are already settled below, exhaustively.
5. **No manuscript text.** No `tab:analysis-families` row, no appendix
   LaTeX, until Walter says so (his call, 28 August).
6. Names are **Dataset A / Dataset B**, never Path A/B
   (`2026-08-27-dataset-a-b-rename.md`). Prose says implicit /
   explicit; Gold keys stay `inline_*` / `block_*`.

---

## Design facts you need

Laboratory EEG cohort \(n=18\). **Participant is the inferential unit,
never the epoch.** Five within-subject conditions:

| Key | Prose | Short |
|---|---|---|
| `no_ads` | no advertisement | N |
| `inline_early` | implicit, turn 2 | IE |
| `inline_late` | implicit, turn 4 | IL |
| `block_early` | explicit, turn 2 | EE |
| `block_late` | explicit, turn 4 | EL |

**Dataset A** = one person-level value per condition, the median over
that condition's retained 4 s epochs. 18 × 5 = 90 rows.

**Dataset B** = ad-locked change. For each ad, `post − pre` on single
4 s epochs either side of visual onset, then minus the same quantity at
a matched no-ad reply. There are only **two** control cells, both from
the participant's single no-ad conversation: \(N_e\) (turn-2 reply) and
\(N_l\) (turn-4 reply). One control serves two ad conditions.

\[
\Delta_{IE}=IE-N_e,\quad \Delta_{EE}=EE-N_e,\quad
\Delta_{IL}=IL-N_l,\quad \Delta_{EL}=EL-N_l
\]

All 18 subjects have all six cells, so \(n=18\) and \(\mathrm{df}=17\)
for every test here. Full control audit:
`2026-08-28-dataset-b-control-audit.md`.

16 spectral measures. Two are confirmatory (Fz theta, posterior alpha);
the rest are secondary or exploratory.

---

## What was computed

**Dataset A** — 10 unique condition pairs, \(D_i=y_{c_1}-y_{c_2}\).
Sign order is (IE, IL, EE, EL, N) with pairs \(i<j\), so an
ad-versus-no-ad cell reads ad − no-ad, matching the planned contrast.

**Dataset B** — 6 unique ad pairs, computed twice:

- **\(\Delta\) space** (primary): \(D_i=\Delta_{c_1}-\Delta_{c_2}\)
- **raw space** (companion): \(D_i=c_1-c_2\) on `post − pre`, no control

Same-timing pairs (IE−EE, IL−EL) are **bit-identical** across the two
spaces because the shared control cancels. The four cross-timing pairs
differ by exactly \(\pm(N_e-N_l)\), the control drift.

Every test: paired \(t\) against zero, 95% CI, \(d_z\), \(t(17)\), raw
\(p\), **Holm, BH and BY**, plus Wilcoxon as sensitivity. Columns
`p_t_{holm,bh,by}` and `p_wilcoxon_{holm,bh,by}`.

Correction family = **within measure, within dataset and space**.
Dataset A families are 10 tests; Dataset B families are 6. \(\Delta\)
and raw are separate families because they are two answers to the same
six questions, not twelve questions.

### Five gates, all blocking

The builder writes nothing unless all pass, and all passed:

1. Dataset A has exactly 90 eligible rows and 18 complete subjects.
2. The four planned Dataset A contrasts, recomputed from the pairwise
   person scores, match `eeg_condition_contrasts.csv` to 1e-9.
3. The four planned Dataset B \(\Delta_c\) match
   `eeg_ad_response_contrasts.csv` to 1e-9.
4. Same-timing Dataset B pairs identical across the two spaces.
5. Every pairwise contrast reconstructs exactly in the planned basis.

Gates 2 and 3 are what make "the previous analysis is not invalidated"
a verified statement rather than a claim.

---

## Results

| Family | Tests | Holm < .05 | BH < .05 | Smallest Holm / BH |
|---|---|---|---|---|
| Dataset A pairwise | 160 | **0** | **0** | .484 / .368 — Fz theta, EE−EL, raw \(p=.048\) |
| Dataset B, \(\Delta\) | 96 | **0** | **0** | .080 / .080 — global delta, IE−EE, raw \(p=.013\) |
| Dataset B, raw | 96 | **0** | **0** | .080 / .080 — same cell (same-timing) |

Counting the 32 same-timing duplicates once, **320 distinct tests give 8
cells at uncorrected \(p<.05\)**, against a naive chance expectation of
16. The measures are strongly dependent so that comparison is
indicative, not a formal test, but the set does not behave like one
containing signal.

Every Dataset B nominal cell sits on an **explicit-early** comparison
(global delta −3.64 dB, relative delta, relative theta, relative beta,
all IE−EE). That is the already documented explicit-early slow-power
tilt from the six ICA-only exploratory hits
(`2026-08-20-paper-depth-audit.md`), re-expressed as implicit-versus-
explicit at early timing. **Localisation of a known event, not a new
one.**

### Nothing dimensionally new

Five conditions leave a **4-dimensional** contrast space and the four
planned Dataset A contrasts span it, so every pairwise difference is an
exact linear combination of contrasts already tested. Verified
numerically in `eeg_posthoc_redundancy_map.csv`:

```text
IE - N   = any_ad + 0.5 format + 0.5 timing + 0.25 interaction
IE - EL  = format + timing
EE - EL  = timing - 0.5 interaction
```

Dataset B raw: 3-dimensional, spanned by the three existing secondary
contrasts. Dataset B \(\Delta\): also 3-dimensional, but only
`inline_vs_block` and `format_x_timing` carry over. **The \(\Delta\)-space
timing direction is tested nowhere in the codebase** — the one genuinely
new direction in the sweep, and it is null too.

The sweep buys localisation and a different multiplicity structure. It
does not buy new information.

---

## Closed questions — do not reopen

### "Does this invalidate the earlier analyses?" No

The sweep writes to a separate directory; the frozen tables were never
rewritten. Gates 2 and 3 proved the planned numbers are bit-identical.
The planned families are unchanged (Dataset A 3 contrasts per measure,
Dataset B 4). All six published Dataset B hits stand. Adding 352 **null**
tests cannot weaken a prior finding; it would only matter if a hit were
being fished out, which it is not.

### "Why is the sweep null when the planned tests were not?"

Not the family. Four reasons:

1. Dataset A was 0/48 Holm before this work and the sweep is 0/160.
   Those agree; nothing to explain.
2. The six significant cells are `ad vs matched no-ad`. The pairwise
   family contains only `ad vs ad`, because the control sits inside
   every \(\Delta\). They were never candidates, not suppressed.
3. Global delta: planned raw \(p=.0017\), pairwise raw \(p=.0133\) —
   **7.8× worse before any correction**. The pairwise contrast
   differences two noisy ad cells with no control anchor, so variance
   adds and the effect shrinks.
4. Forcing the four planned tests **into** the pairwise family (joint
   family of 10, harsher than anything applied) leaves global delta at
   Holm .017, relative delta .011, relative beta .045. They survive.
   Under that same harsher family global theta, relative alpha and
   relative gamma drop out, matching the depth audit's reading that five
   of six are one compositional event. **Keep the pre-specified family
   of 4; do not retrofit a larger one.**

### "Which correction is more correct, Holm or BH?"

**Neither. They control different quantities**, and the choice follows
from what the number is for.

| | Controls | Guarantee | Dependence assumption |
|---|---|---|---|
| **Holm** | family-wise error rate | \(P(\ge 1\) false positive\() \le \alpha\) | **none — valid under arbitrary dependence** |
| **BH** | false discovery rate | \(E[\text{false}/\text{flagged}] \le \alpha\) | independence or positive regression dependency |
| **BY** | false discovery rate | same as BH | **none — valid under arbitrary dependence** |

FWER suits confirmatory tests, where one false positive is a wrong
scientific claim. FDR suits screening, where hits get followed up.

**The catch: BH's assumption is violated on this feature set.** The five
relative powers **sum to one by construction**, so they are *negatively*
dependent; the engagement ratios reuse the same bands. BY restores the
FDR guarantee under any dependence by inflating BH by the harmonic
number of the family size (×2.45 at \(m=6\), ×2.93 at \(m=10\)), which
here makes it **stricter than Holm**:

| View, best cell | Holm | BH | BY |
|---|---|---|---|
| Dataset A | .484 | .367 | **1.000** |
| Dataset B \(\Delta\) | .080 | .080 | **.196** |

So "Holm was too conservative, use something laxer" has no valid
destination on this data: the laxer procedure is the one whose
assumption fails, and the assumption-free FDR is harsher than what we
started with.

**Practical upshot, decided 28 August.** Confirmatory stays Holm: it is
pre-specified, assumption-free, and **BH gives numerically identical
values on the confirmatory family** (all six Dataset B hits, e.g. global
delta .0069 under both), so switching would change nothing while
creating the appearance of changing the rule after seeing results. Under
BY, four of those six still clear .05 (global delta .0143, relative
delta .0089, relative beta .0375, global theta .0478; relative alpha
.0549 and relative gamma .0778 do not) — a useful robustness line.

The exploratory sweep reports all three. All three give zero.

`check_posthoc_family_sensitivity.py`, on the 320 distinct tests:

| Family definition | Families | Size | Holm | BH | BY |
|---|---|---|---|---|---|
| none (uncorrected) | 320 | 1 | **8** | **8** | **8** |
| within measure, within dataset and space (as run) | 48 | 4–10 | **0** | **0** | **0** |
| within measure, spaces pooled | 32 | 10 | **0** | **0** | **0** |
| within measure, both datasets pooled | 16 | 20 | **0** | **0** | **0** |
| within dataset, 16 measures pooled | 3 | 64–160 | **0** | **0** | **0** |
| one family over the entire sweep | 1 | 320 | **0** | **0** | **0** |

The defence is structural: **an under-correction critique can only
create hits, never destroy them.** Every complaint available about the
family choice argues for *less* correction, and even with none the sweep
gives 8 nominal cells where chance predicts 16.

(That table deduplicates the 32 raw-space same-timing copies, so the raw
Dataset B family reads 4 rather than the 6 actually used. Marginally
less conservative; still zero.)

### "Drop features to reduce multiplicity" — cannot help, proven

This rests on a misreading: **the correction never ran across 160.** It
runs within measure, so Dataset A families are 10 and Dataset B 6.

> Dropping features removes whole families and leaves the survivors
> untouched. It can **delete** the best cell; it can never **improve**
> a surviving one.

`check_feature_subset_sweep.py` settles it by exhaustion rather than
argument: **all 65,535 non-empty subsets** of the 16 measures, under the
harsher across-feature family, **all three corrections tracked
separately** (589,815 subset × view × method evaluations).

| Method | Best adjusted \(p\) anywhere | Achieved by |
|---|---|---|
| Holm | **.0799** | Dataset B \(\Delta\), global delta alone |
| BH | **.0799** | Dataset B \(\Delta\), global delta alone |
| BY | **.1958** | Dataset B \(\Delta\), global delta alone |

**None reach .05 under any method.**

Named subsets, within-measure families (what the sweep uses):

| Subset | k | A Holm | A BH | A BY | B\(\Delta\) Holm | B\(\Delta\) BH | B\(\Delta\) BY |
|---|---|---|---|---|---|---|---|
| all 16 | 16 | .484 | .368 | 1.000 | .080 | .080 | .196 |
| drop 5 relative | 11 | .484 | .368 | 1.000 | .080 | .080 | .196 |
| drop 5 absolute globals | 11 | .484 | .368 | 1.000 | .127 | .094 | .231 |
| drop 3 engagement | 13 | .484 | .368 | 1.000 | .080 | .080 | .196 |
| keep best engagement only | 14 | .484 | .368 | 1.000 | .080 | .080 | .196 |
| drop relative + engagement | 8 | .484 | .368 | 1.000 | .080 | .080 | .196 |
| drop absolute + engagement | 8 | .484 | .368 | 1.000 | .127 | .094 | .231 |
| confirmatory + FAA | 3 | .484 | .368 | 1.000 | .166 | .094 | .231 |
| confirmatory only | 2 | .484 | .368 | 1.000 | .166 | .094 | .231 |
| global delta alone | 1 | .813 | .813 | 1.000 | .080 | .080 | .196 |

Read the constancy down the columns: **Dataset A never moves** for any
subset that keeps Fz theta, and Dataset B only *worsens* when the cull
deletes global delta, the family that held the minimum. BH is uniformly
at or below Holm; BY is uniformly above it. Across-feature families are
worse still.

An absolute-versus-relative cull is still defensible **for parsimony**
(the five relative powers sum to one, so they are compositionally
redundant with the absolutes), but never as a multiplicity gain. Best
engagement index by raw \(p\) is Pope frontocentral.

---

## Open item, owed to Methods

Dataset B **secondary** contrast weights were never pre-specified, so
the `early_vs_late` in `build_ad_contrasts.py` is an implementation
choice: it lives in raw space, while every other Dataset B contrast is
space-invariant.

| Measure | raw (in code) | \(\Delta\) (in no code) | drift \(N_e-N_l\) |
|---|---|---|---|
| Fz theta | \(+0.670\), \(p=.144\) | \(+1.427\), \(p=.052\) | \(-0.757\), SD 2.31, \(p=.182\) |
| Posterior alpha | \(+1.228\), \(p=.023\) | \(+1.740\), \(p=.079\) | \(-0.511\), SD 3.20, \(p=.507\) |

Identity `raw = Δ + drift` verified to 1e-9 on all 16 measures. Drift is
not significant on its own for any measure.

The two confirmatory measures **disagree about which version looks
better**: raw wins for posterior alpha, \(\Delta\) wins for Fz theta.
Both are uncorrected secondary numbers. **Fix the estimand on principle
and write it into Methods; do not choose it from \(p\).** Neither is
promoted. This is a documentation gap on an uncorrected row, not an
analysis defect, and it predates this work.

---

## Artefacts

Scripts, `analysis/eeg/statistics/`:

| Script | Job |
|---|---|
| `build_posthoc_pairwise.py` | The 352 tests, Holm + BH + BY, 5 blocking gates |
| `check_posthoc_family_sensitivity.py` | Verdict under 6 family definitions × 3 methods |
| `check_feature_subset_sweep.py` | All 65,535 feature subsets × 3 methods × 2 family schemes |

Plot: `analysis/eeg/analysis/plot_posthoc_pairwise.py`.

Tables, `analysis/eeg/statistics/outputs/posthoc/`:

- `eeg_posthoc_pairwise_dataset_a.csv` (160 rows)
- `eeg_posthoc_pairwise_dataset_b.csv` (192, both spaces)
- `eeg_posthoc_pairwise_scores_dataset_{a,b}.csv` (person-level \(D_i\))
- `eeg_posthoc_timing_discrepancy.csv`
- `eeg_posthoc_redundancy_map.csv`
- `eeg_posthoc_family_sensitivity.csv`
- `eeg_posthoc_feature_subset_sweep.csv`

Figures, `analysis/eeg/analysis/outputs/figures/posthoc/`. The artefact
to read is the **32-page** `posthoc_pairwise_report.pdf`: cover,
Findings page (bullet summary), overview of the two confirmatory
measures against all three corrections, twelve 16-panel boards (effect /
Holm / BH / BY × Dataset A, Dataset B \(\Delta\), Dataset B raw), the
control-drift board, then one page per measure with all three views
against all four panels. Each board also stands alone as pdf/png.

---

## Related

- Control audit (what \(N_e\) / \(N_l\) are, every existing Dataset B
  formula, raw vs \(\Delta\)): `2026-08-28-dataset-b-control-audit.md`
- Confirmatory lock: `2026-08-20-paper-4s-primary-and-epoch-sensitivity.md`
- The six ICA-only exploratory hits: `2026-08-20-paper-depth-audit.md`
- Requested by: `../2026-08-27-backlog-and-timeline.md` item 2
- Precedent for "sensitivity, not a second family":
  `2026-08-28-channel-set-closed.md`
