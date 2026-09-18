# Deepseek 4.1 flash jury on the paper, after the refinement (17 Sep)

PDF judged: paper after `7698241` (round 2 + jury v1/v2 applied). Every claim
below was checked against the current `.tex` and, where numbers were at stake,
against frozen Gold. Nothing was re-estimated. Not committed, not pushed.

**Verdict in one line: four of the six "must fix" claims are wrong about the
current source. Two were real and are fixed.**

## The six claims

### 1. "16 vs 15 planned behavioural contrasts" — false in source

Table 4 (`tab:beh-planned`) has **16 rows**, and the row Deepseek says is
missing, *trust after re-exposure, implicit − explicit*
(\(+0.12\), Holm \(.525\)), is present. Bold rows count to **8**: credibility
early − late, all three manipulation contrasts, notice any-ad and
implicit − explicit, cued memory implicit − explicit, trust after
re-exposure early − late. Table 3 declares the same family size
("3 planned contrasts within each of the four primary outcomes; 2 within each
of the two cued-recall items" = 12 + 4 = 16). The Holm family is rebuildable
from the PDF as printed. **No edit.**

### 2. "None after the mention" vs the implicit-late relative \(\gamma\) cell — true, fixed

Table 19 does carry onset-locked *implicit late − \(a^{\emptyset}\)* on relative
\(\gamma\) at Holm \(p=.037\), so both headline sentences were too broad. The
precise statement, already in Discussion 6.2, is that nothing comparable
follows the **implicit-early** mention. Both were qualified to the same turn,
one clause each.

- Abstract: "at **early-banner** onset an exploratory slow-power tilt appeared
  and none after the mention **at the same turn**".
- Conclusion 7.1: "…with no Holm-surviving counterpart after the mention **at
  the same turn**, though the direct format comparison at onset is null".

The relative \(\gamma\) cell is not named in the Abstract or Conclusion on
purpose: Results 5.4 already names it ("the sixth is implicit-late relative
\(\gamma\)") and Table 19 prints it, and calling it "exploratory" as a
distinguishing feature would mislead, since the explicit-early tilt is
exploratory too.

### 3. Personality "nearest" term — false in source

The named cell is right. Gold (`personality_lmm.csv`, 60 rows) has the smallest
raw \(p\) on credibility × extraversion × early − late (\(p_{\mathrm{raw}}=.0119\),
Holm within outcome across fifteen = \(.178\) → \(.18\)); next is trust ×
extraversion × early − late (\(.201\)). Table 13 prints \(.178\) in that cell.
Deepseek's alternative, *extraversion on perceived manipulation, any ad*, is
\(1.000\) in Table 13. Results 5.3 and the RQ5 row of Table 5 both already say
\(.18\). **No edit.**

### 4. \(D_i\) ordering typo — false in source

Method 4.5 prints five conditions,
\((a^{\mathrm{imp}}_{2},a^{\mathrm{imp}}_{4},a^{\mathrm{exp}}_{2},a^{\mathrm{exp}}_{4},a^{\emptyset})\),
with \((\tfrac14,\tfrac14,\tfrac14,\tfrac14,-1)\). No duplicated
\(a^{\mathrm{exp}}\). **No edit.**

### 5. Abstract "platform policy II" — false in source

The source is `\(\Pi\)` in both the abstract and contribution 1. This is a
PDF text-extraction artefact on the reviewer's side, not a typo. **No edit.**

### 6. Positive-control interpretation in Results — true, fixed

The interpretive tail is gone; the numbers and Walter's pipeline-validation ask
(`% WALTER+:` above the paragraph) both stay.

> Writing minus reading … raises Fz \(\theta\) by \(+0.60\)~dB … and does not
> move posterior \(\alpha\) … The recordings and the pipeline therefore register
> a within-conversation change in the predicted marker and direction before any
> advertisement contrast is read.

Cut: ", which is the check the advertisement nulls below are read against."
Not moved to Discussion — 6.2 already says the Fz \(\theta\) format null is
"a null on a marker this cohort can move".

## Cheap "may fix" items, applied

**Related Work closer.** "stops at self-report after the fact" undersold Tang
(logged clicks and requests to stop) and Salvi (persuasion). One clause:

> The evidence that exists is mostly about yield, and the user-side evidence,
> non-recognition and persuasion included, is read off after the exchange
> rather than while it happens; what is missing is the user's bill measured
> while it is incurred…

**Limitations, task and position.** Appendix C.7 was the only place saying the
models do not enter task or position. One sentence added to *Protocol and
self-report* (no new analysis):

> Task identity and session position are balanced by that rotation rather than
> modelled: with \(N=54\) the rotation does not divide evenly, and neither the
> paired \(t\) nor the mixed-model check enters task or position as a term, so
> a task effect that happened to align with a condition would stay in the
> contrast (\autoref{sec:app-beh-design}).

Pooled arms were already in *Sample and setting*; not expanded.

**Familywise burden.** The main Statistical framework named the family choice
but never its price. One clause on the existing sentence:

> Each EEG measure is its own Holm family, so the fourteen exploratory measures
> carry no joint error control across measures (\autoref{sec:app-eeg-measures}).

The Appendix D.2 "98 uncorrected tests … about five false positives" sentence
stays where it is.

## Refused (locked or frozen)

- **No new models.** No task or position random effect, no arm × contrast
  primary LMM, no re-estimation of the Dataset A onset-centred cell at other
  widths. The paper already states that last one as a stated limit.
- **"Confirmatory" stays.** Method 4.5 already says the study was not
  pre-registered and defines four status labels. The confirmatory/exploratory
  split is not demoted and no caveat was rewritten.
- **No design implications, H1–H3, or "what this means" into Results.** The
  positive-control fix removes an interpretation rather than relocating one.
- **Nothing reopened** on ICA, \(k=37\), montage, or questionnaire items.
  `analysis/behavioural/` untouched; no Gold rebuild; no ICA model touched.
- **No `% WALTER:` / `% [AI:]` / `\rev` added.** Every existing `% WALTER+:`
  and `% NUMBERS:` line is intact.

## Greps after the edits

Clean for: "eight of sixteen" (only the correct "Eight of sixteen" in 5.2),
"sixteen planned", "none after the mention" (now qualified),
"no Holm-surviving counterpart after the mention" (now qualified),
"platform policy II", duplicated \(a^{\mathrm{exp}}\), "this thesis",
"Wilcoxon Holm", Path A/B, "equal-n", "condition state", Vargas, `\rev{`,
open `% WALTER:` in any file this pass edited.

## Compile

**Not compiled.** No `latexmk`, `pdflatex`, or `tectonic` on this machine; the
last local PDF in `_build/` was produced root-side in a container. Net change
is about +60 words (−11 in Results 5.4, +6 across abstract and conclusion,
+7 in Related Work, +14 in Method 4.5, +42 in Discussion 6.5), so expect at
most a float nudge on pp. 4, 12, 15, and 16 and no change to the page count.
Verify in Overleaf.

## Files touched

`main.tex` (abstract), `sections/02_related_work.tex`,
`sections/04_method.tex`, `sections/05_results.tex`,
`sections/06_discussion.tex`, `sections/07_conclusion.tex`.
