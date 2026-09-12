# WP1 — Katerina reconciliation (demographics / OCEAN moderation)

Date: 11 September 2026. Owner: `inherit`. Status: **done** (analysis;
no tex edited). Comment closed: `results.tex:585` (Walter: "she did
another behavioural analysis + ocean/demographics moderation and she
found stuff specially in demographics").

Everything below is re-estimated on **Walter Gold \(N=54\)**
(`analysis/walter/behavioural/outputs/gold/`). Katerina's tree was read,
never run; none of her numbers are quoted for the thesis.

Script: `analysis/walter/behavioural/stats/run_demographic_moderation.py`
(new; standalone, does not touch `make_thesis_figures.py`). Runtime ≈ 20 s.

---

## 1. What Katerina did (commits `a93ff5b`, `67b86c5`, `c4ceea3`, `1bdc0a9`)

| Script / file | Sample | Factors and coding | Model | Correction | What it reports |
|---|---|---|---|---|---|
| `calc_condition_ocean_correlations.py` → `ocean_corr_outputs/*.csv` (9 Sep) | **\(n=19\) lab** per cell (her `Experiment/` folder = 19 lab dirs incl. `lab_subject_4_crowdfail`; Gold lab is 18) | BFI-10 E A C N O (continuous) | Spearman \(\rho\) (primary) and Pearson, **within each condition separately**; 7 outcomes (credibility, helpfulness, convincingness, relevance, neutrality, behaviour_pushing, behaviour_manipulate) × 5 traits × 5 conditions = 175 cells | Holm and BH across all 175 | 10 raw \(p<.05\), **0 Holm, 0 BH**. Strongest: implicit-late relevance × Extraversion \(\rho=-.72\), raw \(p=.0005\), Holm \(.088\). All ten raw cells are negative correlations. Heatmaps star **uncorrected** \(p<.05\). |
| `moderation_model_gold.py` (10 Sep) | **Walter Gold**, joined on `participant_id` (\(N=54\) minus missing demographics: 51 for sex, 52 for education) | `demo_sex` (ref Male), `demo_education` (ref Bachelor's; **all five levels kept**, incl. PhD \(n=3\), Other \(n=3\)), `demo_familiarity` (ref Familiar; incl. Somewhat Unfamiliar \(n=2\)), `demo_frequency` (ref 1–5/day; incl. Fewer than 5 ever \(n=2\)). No arm, no age (empty). Level filter "≥ 3 **rows**" = every level kept (each person has 5 rows). | `MixedLM(outcome ~ C(condition) * C(factor))`, random intercept per person; her 7 outcomes | **None.** Prints the five smallest raw \(p\) among the 4 × (L−1) condition-dummy × level interaction terms per factor | Console only; no CSV in the tree |
| `temp_demo_moderation_model.py` (10 Sep) | Rebuilt from `src/project/logs/tracked/{lab,crowd}` with **no roster filter** (19 + 44 directories; would include synthetic / unfinished / crowdfail sessions) | same four factors, raw levels, "≥ 3 rows" | OLS `llm_reliable ~ C(condition) * C(factor) + C(participant_id)` (participant fixed effects); **single item** `llm_reliable` as the only outcome | None. Prints top-10 raw \(p\) | Console only |
| `README.md`, `variable_dictionary.md` | — | — | documents the OCEAN script and JSONL fields; the two moderation scripts are undocumented | — | — |
| `outputs/ad_notice/*.csv` | 45 participants per condition (roster differs from Gold) | — | descriptive notice shares | — | for WP3 cross-check only; not quoted |
| `Cronbach_alpha.py` (`67b86c5`) | — | — | one-reverse fix | — | already reconciled 8 Sep (`2026-09-08-item-correlations-held.md`) |
| `c4ceea3` | — | — | condition-score CSVs **without** `llm_reliable` / `llm_opinionated` / `llm_skeptical` | — | **item drop; do not use** (AGENTS.md hard stop) |

So "she found stuff in demographics" = the raw-\(p\) interaction terms
printed by `moderation_model_gold.py` / `temp_demo_moderation_model.py`.
There is no saved table of them. To name those cells I refitted **her
exact model on Gold** (block `katerina_design_on_gold` in the new script).

### Her design on Gold, named

440 condition-dummy × level terms (10 outcomes: her 7 + trust,
manipulation, notice; 4 factors). **18 raw \(p<.05\)**; 14 of the 18 sit
on levels with **two or three people** (education "Other" \(n=3\): 6
cells; PhD \(n=3\): 4; "Somewhat Unfamiliar" \(n=2\): 2; "Fewer than 5
times ever" \(n=2\): 2). By factor: education 10, frequency 4, sex 2,
familiarity 2.

After Holm within outcome, **2 of 440 survive**, and both are the same two
people: relevance × explicit-early × "Somewhat Unfamiliar" (\(n=2\),
\(\hat\beta=-3.94\), raw \(.0003\), Holm \(.013\)) and relevance ×
explicit-early × "Fewer than 5 times ever" (\(n=2\), \(\hat\beta=-3.85\),
raw \(.0005\), Holm \(.022\)). Those two participants
(`exp_20260729T142615Z_78e41297`, `exp_20260731T134108Z_a4a5b76b`) rated
relevance 1.7 and 1.0 in explicit-early against 5–7 in every other
condition. A two-person level is not a moderation finding; it is two
outliers with a coefficient.

The only raw hit on a level with \(\geq 5\) people that survives Holm
**within its own factor model** (her per-model view, 8 terms) is
neutrality × explicit-early × Female (\(n=21\), \(\hat\beta=-1.25\), raw
\(.0046\), Holm-within-factor \(.019\)); across the outcome (32 terms) it
is Holm \(.20\). Neutrality is a secondary outcome. The other three
non-sparse raw cells (helpfulness × explicit-late × >5/day; convincingness
× explicit-late × 1–5/week; neutrality × implicit-late × Female) are Holm
\(\geq .12\) even within factor.

File: `outputs/exploratory/demographic_moderation_katerina_design.csv`.

---

## 2. Re-estimation on Walter Gold \(N=54\): the declared design

Estimand kept: random-intercept LMM on \(Y_{ic}\), the three planned
contrast codes × one demographic factor at a time; cell \(=\) joint Wald
\(\chi^2\) on the \((L-1)\) contrast × level terms; **Holm within outcome**
across factor × contrast cells (4 primary × 3 × 5 factors = 15 per
outcome; cued memory × 2 contrasts × 5 = 10). Person-level OLS of
\(D_i\) on the factor (F test) beside it as concordance. Age not
estimable (`demo_age` empty for all 54).

Two codings, side by side (`coding` column):

| Factor | `katerina` (levels kept; sparse merged at < 5 people) | `collapsed` (two-level screen) |
|---|---|---|
| Sex | Male 30 / Female 21 (3 missing excluded) | same |
| Education | High school 10 / Bachelor's 20 / **Master's or PhD 19** (PhD \(n=3\) merged up; "Other" \(n=3\) excluded, no place on the scale; 2 missing) | Bachelor's or less 30 / Graduate degree 19 |
| Familiarity | Familiar 42 / **Less than familiar 12** (Somewhat Unfamiliar \(n=2\) merged) | Familiar 42 / Other 12 (identical) |
| Use frequency | >5/day 16 / 1–5/day 19 / 1–5/week 12 / **Monthly or less 7** (Fewer than 5 ever \(n=2\) merged) | Daily 35 / Less 19 |
| Environment (arm) | Crowd 36 / Laboratory 18 | same |

### Result

| Coding | Cells | Raw \(p<.05\) | **Holm \(p<.05\)** | OLS Holm | LMM vs OLS verdicts |
|---|---|---|---|---|---|
| `katerina` | 70 | 1 | **0** | 0 | 70 / 70 agree ("neither") |
| `collapsed` | 70 | 2 | **0** | 0 | 70 / 70 agree |
| secondary sensitivity (helpfulness, convincingness, relevance, neutrality; her coding) | 60 | 2 | **0** | — | — |

All models converged. Nearest cells (never below Holm \(.43\)):

- Cued memory, early − late × familiarity: less-than-familiar users remember
  early ads better than late (\(\overline D=+1.13\)); familiar users do not
  (\(-0.07\)); \(\chi^2(1)=4.05\), raw \(.044\), **Holm \(.44\)** (both codings).
- Trust, implicit − explicit × daily use (collapsed): daily users trust the
  implicit format slightly more (\(+0.44\)), less-than-daily users slightly
  less (\(-0.40\)); raw \(.029\), **Holm \(.44\)**. With the four frequency
  levels kept the same cell is raw \(.14\), Holm \(1.0\) — the two-level
  split is what makes it look like a signal. This is the same cell already
  in `personality_demo_screen.csv` (raw \(.022\), Holm \(.26\)).
- Cued memory, early − late × use frequency (4 levels): \(\chi^2(3)=7.66\),
  raw \(.054\), Holm \(.48\).
- Credibility, early − late × environment: laboratory \(-0.65\) vs crowd
  \(-0.17\); raw \(.061\), Holm \(.92\).

### Why her cells do not replicate

1. **Sparse levels.** 14 of her 18 raw cells are two- or three-person
   levels; merging them at \(<5\) people removes the cells, and the two
   Holm survivors are literally two participants.
2. **Coding by condition dummy, not by planned contrast.** Her model has
   \(4\times(L-1)\) free interaction terms per factor against a treatment
   reference; the thesis estimand is three planned codes, so one joint test
   per contrast. Under the planned codes nothing is below raw \(.03\).
3. **No correction.** She printed raw \(p\). Holm within outcome, or even
   within her own factor model, empties the list except the two-person
   cells.
4. **Sample.** The OCEAN heatmaps are \(n=19\) lab (incl. the crowdfail
   session) and already 0/175 under her own Holm and BH; her Gold
   moderation script did use \(N=54\), so sample is not the reason there —
   coding and correction are.

### What does replicate (direction, honestly)

Nothing at Holm \(<.05\). The **direction** of her non-sparse cells is
consistent with the nearest cells here (women rate neutrality lower after
any ad than men: raw \(.035\) under the planned any-ad code, Holm \(.49\);
laboratory rates neutrality lower for explicit than crowd: raw \(.024\),
Holm \(.36\)). Both are secondary outcomes and both stay in the sensitivity
CSV, not in Results.

---

## 3. Proposed text (for WP5a to integrate; **not applied**)

### Results 7.3 (`sec:results-personality`), after the personality paragraph

> No demographic factor moderates the planned contrasts either
> (\autoref{fig:beh-demographics}). Sex, education, chatbot familiarity,
> use frequency, and environment were each entered one at a time as a
> factor interacting with the three planned contrast codes in the same
> random-intercept model, on the four primary outcomes and cued memory
> (\(N=54\); age was not recorded). With levels kept, 0 of 70 factor
> \(\times\) contrast cells survive Holm within outcome; with two-level
> coding, again 0 of 70; a person-level OLS on \(D_i\) agrees on every cell
> (\autoref{tab:beh-demographics}). The nearest cell is cued memory, early
> minus late, by familiarity: less-familiar users remember early
> advertisements better than late ones (\(+1.13\) points) and familiar users
> do not (\(-0.07\)), Holm \(p=.44\). Education levels with fewer than five
> people (PhD, Other) were merged or excluded before testing.

Caption for `fig:beh-demographics` (≤ 2 lines):

> Demographic moderation of the planned contrasts (\(N=54\)). Cell: spread of
> the mean within-person contrast across factor levels (Likert points) and
> Holm \(p\) of the joint contrast \(\times\) factor test, within outcome.
> Top: levels kept. Bottom: two-level coding. No cell below \(.05\).

### Discussion 8.2 (`sec:disc-personality`), one short paragraph after the personality one

> **Demographic moderation.** Who the user is does not change what the
> advertisement costs them. Sex, education, familiarity with chatbots, use
> frequency, and laboratory versus crowd setting leave the format and
> timing effects the same size on trust, credibility, perceived
> manipulation, notice, and cued memory (\autoref{sec:results-personality}).
> An earlier pass over these factors on the same data read raw
> \(p\)-values on single condition dummies and found cells that rested on
> two or three participants in one education or frequency level; under the
> planned contrasts, with sparse levels merged and Holm within outcome,
> none remains. The practical reading is positive for the user: the
> trust-neutral implicit format and the well-noticed explicit banner behave
> the same way across the demographic range this sample covers, so the
> findings of \autoref{sec:disc-behaviour} are not a property of one
> subgroup.

(Keep the existing "Fifty-four people are a modest sample…" caveat
paragraph as the closing sentence, or fold its first sentence in.)

### Appendix E (`sec:app-beh-personality` neighbour)

Insert `tab_beh_demographics.tex` directly after `tab:beh-personality`
under a new `\section{Demographic moderation}` `\label{sec:app-beh-demographics}`
with two sentences:

> \autoref{tab:beh-demographics} is the full demographic family:
> factor levels kept where at least five people fill them (PhD merged into
> Master's; "Other" education excluded; the two least-familiar and the two
> rarest-use participants merged into their neighbouring levels), joint
> Wald on the contrast \(\times\) factor terms, Holm within outcome. The
> two-level coding and the person-level OLS columns agree on every verdict.
> Under a condition-dummy parameterisation without correction, the same
> data yield 18 raw \(p<.05\) terms out of 440, 14 of them on levels of two
> or three people; two survive Holm and are the same two participants.

Update the existing sentence "A collapsed demographic screen is empty
(48 tests)" in App E and Results 7.3 to point at the new table (the
48-test screen is superseded by the 70 + 70 family).

`tab:results-checks` row "Demographic factor screen on \(D_i\)" → replace
with: "Demographic moderation (LMM) & 54 & 70 + 70 & 0 & sex, education,
familiarity, use frequency, environment × three planned contrasts, two
codings; nearest cued memory early − late by familiarity, Holm \(p=.44\)
& §\ref{sec:app-beh-demographics}".

---

## 4. Files produced

Analysis (`analysis/walter/behavioural/`):

- `stats/run_demographic_moderation.py` — new, standalone.
- `outputs/exploratory/demographic_moderation_lmm.csv` — 140 cells (70 per coding) with joint Wald, Holm, level means of \(D_i\), OLS check, verdict.
- `outputs/exploratory/demographic_moderation_levels.csv` — per-level interaction coefficients (treatment reference) behind each cell.
- `outputs/exploratory/demographic_moderation_katerina_design.csv` — her model refitted on Gold, 440 terms, raw and Holm.
- `outputs/exploratory/demographic_moderation_secondary.csv` — secondary outcomes, her coding, sensitivity only.
- `outputs/exploratory/demographic_moderation_summary.json` — counts, coding notes (raw → coded counts, merged / excluded levels), nearest cells.
- `outputs/figures/thesis/beh_demographics_board.pdf` (+ `.png`) — vector (cells drawn as patches; **0 embedded images**), same palette / bands as `beh_personality_board`, orange `*` reserved for Holm \(<.05\).
- `outputs/figures/thesis/tab_beh_demographics.tex` — booktabs, family divider rules per outcome, bold rows for Holm \(<.05\) (none), one-line caption.

Copied to `docs/overleaf/thesis/figures/results/`:
`beh_demographics_board.pdf`, `tab_beh_demographics.tex`.

Not edited: any `.tex`, `make_thesis_figures.py`, anything under
`analysis/behavioural/`. Nothing committed or pushed.

---

## 5. Open questions for Walter

1. **Where do the demographics go?** Proposal: one sentence + figure in
   7.3, one paragraph in 8.2, the full table in App E. Katerina's Friedman
   omnibus / ten pairs are already in App F (`tab:beh-friedman`,
   `tab:beh-pairwise`) from `run_omnibus_pairwise.py`; nothing new needed
   there.
2. **Do you want the two-person cells named in the thesis?** The appendix
   sentence above says "two participants" without IDs. The IDs are in the
   CSV if a footnote is wanted.
3. **Katerina's OCEAN heatmaps** are \(n=19\), uncorrected stars, and
   0/175 under her own Holm. I propose they stay out of the thesis entirely
   (the declared personality family already covers RQ8/RQ9 on \(N=54\)).
4. **Age.** Not recorded in the JSONL for anyone; the crowd Prolific
   estimate (26 of 36) cannot be joined at person level. Say "age was not
   recorded" once in 7.3, or leave to Limitations (WP5b).
5. **Commit `c4ceea3`** (scores without `llm_reliable` / `llm_opinionated`
   / `llm_skeptical`) is an item-drop variant. AGENTS.md says items stay in;
   confirm we ignore it (a word to Katerina may be needed).

## 6. Side note for WP2 (figures)

The checklist says every `figures/results/*.pdf` has 0 embedded rasters.
That is not true for the `imshow` boards: `beh_personality_board.pdf` (2
images), `beh_holm_board.pdf` (2), `eeg_holm_board_4s.pdf` (3),
`posthoc_pairwise_thesis.pdf` (1), `traj_heatmap_both.pdf` (3). They
need the same fix used here (cells as `Rectangle` patches instead of
`imshow`) to be vector.
