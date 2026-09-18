# Jury review v1 — kimi (independent conference reviewer)

Paper reviewed: *The Price of Attention: Behavioral and EEG Responses to Advertising in LLM
Conversations* (`/tmp/paper_jury.pdf`, 48 pp., body pp. 1–17, references pp. 18–21, appendices
A–E pp. 22–48). Reviewed from the PDF alone, title page through Appendix E, before writing.

---

## 1. Consistency audit (Job 1)

One row per analysis family of Table 3 (p. 10). "Agreement" checks Methods (§4.4–4.5, Table 3)
against Results (§5), Discussion (§6, Table 5), and Abstract/Conclusion (§7.1).

| Family | n | Tests | Estimator | Correction | Headline | Verbal claim | Agreement |
|---|---|---|---|---|---|---|---|
| Behavioural battery | 54 | 16 (4 outcomes × 3 + 2 recall × 2) | one-sample t on \(D_i\); Wilcoxon raw; LMM check | Holm within outcome | 8/16 survive; manipulation any-ad +1.27 | "Eight of sixteen planned contrasts survive Holm" (§5.2) | OK. Cell arithmetic reproduces from Table 7 means (e.g. 5.03−5.37=−0.34 trust any-ad; 4.0025−2.73=+1.27 manipulation) |
| Format × timing interaction | 54 | 4 (1/outcome) | same t on \(w=(1,-1,-1,1,0)\) | raw p, outside Holm | null, \(\|d_z\|\le0.06\) | "Format λ × timing is null on all four outcomes" (§5.2) | OK; weights correctly described as coded, not normalised |
| Secondary qualities (exploratory) | 54 | 12 | same | Holm within outcome | convincingness −0.49 (Holm .005), relevance −0.50 (Holm .003) | §5.2 matches Figure 8 | OK |
| Logged interaction measures (exploratory) | 54 | **"36"** | same t | "3 contrasts within each measure; 36 tests" | none | "nine interaction measures … (36 exploratory tests…)" (§5.2) | **DISAGREEMENT D1: 9 measures × 3 contrasts = 27 ≠ 36** |
| Localisation (post hoc) | 54 | 4 cells/outcome | paired t | Holm across 4 | trust falls only explicit-early (−0.69, Holm .031) | "Trust falls only there" (§5.2); carried to Abstract/Conclusion with post hoc label | OK |
| Pairwise sweep (post hoc) | 54 | 10 pairs/outcome | Friedman + paired t | Holm within outcome | adds one secondary cell (convincingness IE−EL, Holm .034) | "adds no cell that the planned contrasts do not already contain" (§5.2) vs C.5 "adds one secondary cell" | Minor tension, acceptable (planned family vs sweep) |
| Personality moderation | 54 | 60 | mixed-model Wald | Holm within outcome across 15 | 0/60; nearest Holm .18 | "Neither personality nor background detectably changes…" (§6.1) | OK; null properly bounded in §6.1 |
| Demographic moderation | 54 | 70 × 2 codings | same | Holm within outcome | 0/70, 0/70 | §5.3 | Factor named "arm" in §4.5 but **"Environment (2)" in Table 14, never defined** (D2) |
| Positive control | 18 | 2 | one-sample t | the 2 confirmatory measures | Fz θ +0.60 dB, Holm .007; posterior α null | §5.4 | OK |
| Dataset A (condition aggregation) | 18 | 3 contrasts × 2 measures | t on \(D^A_i\); Wilcoxon raw | Holm within measure | early−late posterior α −0.22 dB, Holm .0496 | Abstract: "posterior α aggregated over a condition was lower for early than for late" | **DISAGREEMENT D6: estimand is onset-centred (37 epochs nearest onset), not "averaged over the whole conversation" (§6.2); whole-window median null (D.1)** |
| Dataset B (onset-locked) | 18 | 4 cells × 2 measures | t on \(D^B_i\); Wilcoxon raw | Holm within measure | all 8 confirmatory cells null, CIs 2–4 dB | "Dataset B is Holm-null in all eight confirmatory cells" (§5.4) | OK on the page; pre-window latency asymmetry unaddressed (Finding M1) |
| Fourteen further EEG measures | 18 | 98 | same | Holm within measure; no across-measure control | 7 cells, 6 on explicit-early onset | "a single slow-power tilt" (§6.2) | OK; family-wise price honestly stated in D.2 |
| Exhaustive EEG pairwise (post hoc) | 18 | 256 | same | Holm within measure | 1 cell (Fz θ IE−EL, Holm .014); B: "about the five chance predicts" | kept out of headlines | OK |
| Epoch width / no-ICA (sensitivity) | 18 | grid | re-estimation | as re-estimated family | 2 off-4 s cells quarantined in Table 18 | "epoch widths off 4 s do not revise the family" (§5.4) | **Partially false for Dataset A: the grid scored the whole-window median, never the reported k=37 cell (D.1)** (D6) |
| Behaviour × EEG | 18 | 6 pairs × 2 scores | Spearman | Holm within six per score | onset-locked trust × posterior α ρ=.80, Holm .0004; aggregated ρ=.24 | "candidate correlate" (§6.3) | OK; two per-score families not jointly corrected, mitigated by 16-measure screen (Holm .001) |

### Disagreements found (both locations quoted)

- **D1 — Test-count arithmetic does not close.** Table 3 (p. 10): "same t on nine duration,
  length, and latency scores | 3 contrasts within each measure; **36 tests**". §5.2 (p. 11):
  "none of the **nine interaction measures** … differs on any planned contrast (**36 exploratory
  tests**, none raw p < .05)". Nine measures × three contrasts is 27. Either 12 measures or 4
  contrasts were run; the PDF never reconciles it.
- **D2 — "Arm is not a factor in any family" is false as written.** C.7 (p. 36): "The two arms
  are pooled throughout and **arm is not a factor in any family**." §4.5 (p. 10): the personality
  model runs "**with arm, sex, familiarity, and use frequency as covariates**"; Table 14 (p. 35)
  tests "**Environment (2)**" on every outcome × contrast — the arm under a new, undefined name.
- **D3 — Discussion flattens the estimator straddle.** §6.1 (p. 14): "**Trust did not fall on any
  corrected contrast**". Table 4 (p. 11): "Trust Early − late −0.44 [−0.81, −0.08] −0.32 **.063
  .026 .048**" — the LMM Holm p of .048 is a corrected contrast below .05. §5.2 says it correctly:
  "the single cell on which the three estimators straddle the threshold (t Holm .063, LMM .048,
  raw Wilcoxon .026)". Conclusion (p. 16) repeats the flattening: "Trust counter-intuitively did
  not fall on any planned contrast".
- **D4 — Notice percentages do not reconcile with the cited figure.** §5.2 (p. 11): "**74% and
  69%** of participants reported the early and late banner as sponsored, against **46% and 39%**
  for the early and late mention, and 11% under \(a^\emptyset\) (**Table 8, Figure 7**)." Figure 7
  (p. 28) plots 11/46/37/81/74 — Table 8's *sponsored-buttons* column — and its caption redefines
  the measure: "Noticed is agreement (≥ 5 of 7) on **the sponsored-content detection item**",
  against §4.4 (p. 8): "Notice is **the mean of the brand-mention and sponsored-button items**".
  The quoted 69% and 39% appear nowhere in the cited figure.
- **D5 — Abstract/Conclusion assert a format difference the Discussion refuses.** Abstract (p. 1):
  "at banner onset an exploratory slow-power tilt appeared and **none after the mention**".
  Conclusion (p. 16): the tilt "sat on the early banner **and not on the mention**". §6.2
  (pp. 14–15): "the direct implicit-minus-explicit comparison at onset **does not survive
  correction** (smallest Holm p = .08), so what stands is the explicit-early response against its
  own control, **not a demonstrated difference between the formats**."
- **D6 — The Dataset A estimand is misdescribed, and its verdict is aggregation-dependent.**
  §6.2 (p. 14): "**Averaged over the whole conversation**, format leaves no trace in the two
  declared markers". §4.4 (p. 8) and E.2 (p. 46): the score is "the median of a fixed number of
  epochs **centred on that condition's visual onset**" / "the **37 retained epochs whose midpoints
  lie nearest** that condition's visual onset" — an onset-centred window, not a whole-conversation
  average. D.1 (p. 38): "on the whole-window median that contrast is **Holm-null at every width**
  (4 s: −0.09 dB, raw p = .20)".
- **D7 — Same conditional share, two wordings.** §5.2 (p. 11): cued memory ≥ 5 "including **about
  half** of the participants who had not noticed the implicit mention". §6.1 (p. 14): "**more than
  half** of those who had not reported the mention as sponsored still recognised it afterwards".
  Abstract (p. 1): "**more than half** of those recognised it when shown again". No table gives
  the underlying count.
- **D8 — RQ7 answer is generous under the table's own legend.** Table 5 (p. 16) legend: "'partly'
  means only one named factor survives". RQ7 is answered "**Supported**" on one surviving pair of
  the six declared (trust × posterior α; the other five null).
- **D9 — Estimand wording drift.** §4.4 (p. 8): "centred on that condition's visual onset" vs
  E.2 (p. 46): "whose midpoints lie nearest that condition's visual onset" vs Table 20 caption
  (p. 40): "median of the 37 epochs nearest visual onset".
- **D10 — Appendix A note contradicts the printed briefing.** p. 23: briefings are "copied from
  TASK_CATALOG … **including mistakes that reached the live study (the laptop briefing used a euro
  sign before 1,200)**", but A.2 (p. 22) prints "your budget is capped at **EUR 1,200**" — no euro
  sign, no mistake.
- **D11 — Spelling convention split.** Title (p. 1): "**Behavioral** and EEG Responses". Body:
  "**Behavioural** measures." (§4.4, p. 8), "Behaviour × EEG" (Table 3), "Behaviour–EEG
  associations" (§5.5).
- **D12 — The paper calls itself a thesis.** D.2 (p. 39): "such a family would test whether any of
  sixteen measures moves, which no confirmatory claim in **this thesis** makes."
- **D13 — Free \(t\) for turn index.** Appendix B (p. 24): "**On turn t** the system message is
  \(p_t = p_{base} \oplus p_{task} \oplus [p_{inject}]_{imp} \oplus [p_{aware}]_{after}\)"; the
  body fixes the turn index as \(k\) (\(a_2\), \(a_4\), utterance \(u_k\)).
- **D14 — Placeholders in the back matter.** p. 17: "supported by **XXXXX** under grant number
  **XXXXX**"; "approved by **XXXXX** under approval number **XXXXX**".
- **D15 — Incomplete references.** No venue for [Qiu and Mei, 2026], [Yun et al., 2026],
  [Tang et al., 2025], [Subramanian et al., 2026], [Zhang et al., 2026b]; several titles
  lowercased ("Eeg-based consumer behavior prediction", "llm chatbots").
- **D16 — Leftover internal naming.** D.1 (p. 38): "the **k = 37 neighbourhood**" — the retired
  internal name for the Dataset A aggregation, surfacing once in an appendix.

Checks that came back clean: "Holm p" is always the Holm-adjusted paired \(t\) and Wilcoxon is
always raw (Tables 4, 11, 12, 20, 21 state it identically); no "Wilcoxon Holm" anywhere; Dataset A
is "condition aggregation" throughout (no Path A/B, no "condition state"); \(\Pi\) vs \(\pi\)
never swapped (verified in §1, §2, §3.2, §4.3, §7); the interaction weights are described as
coded and uncorrected, never silently normalised; Results carries no design implications;
Discussion introduces no wholly new results (borderline exception: the "smallest Holm p = .08"
of §6.2 lives only in appendix Table 22); the figure/table inventory matches the contract —
body carries Tables 1–5 and Figures 1–3, localisation forest, notice percentages, and EEG forests
are appendix, and every appendix figure is pointed to from the body or its own appendix text.

---

## 2. Findings

### CRITICAL

**C1. The paper's only confirmatory EEG survival is estimand-fragile, and the fragility is
disclosed only in an appendix QC log.**
Location: §5.4 (p. 12) "the only Holm cell is early minus late on posterior α (−0.22 dB,
[−0.39, −0.04], \(d_z\) = −0.63, Holm p = .0496)"; Abstract (p. 1) "posterior α aggregated over
a condition was lower for early than for late insertion"; Table 5 RQ6 "Partly"; Conclusion
(p. 16) "−0.22 dB, a 5% change in band power". Against: D.1 (p. 38) "The width grid scores
Dataset A on the whole-window median rather than on the k = 37 neighbourhood, so the
early-minus-late posterior α cell of the Results was not re-estimated at other widths; on the
whole-window median that contrast is **Holm-null at every width (4 s: −0.09 dB, raw p = .20)**."
Problem: the confirmatory estimand is the median of the 37 epochs nearest onset — a choice the
authors made, without pre-registration, because 37 is the shortest eligible window. The natural
alternative aggregation, which the authors themselves compute and store, halves the estimate and
kills the verdict. The width-sensitivity grid that §5.4 cites as reassurance ("epoch widths off
4 s do not revise the family") never re-estimated the reported cell at all. Meanwhile §6.2
describes the estimand as "Averaged over the whole conversation", which is the null variant, not
the reported one.
Why it matters: the confirmatory/exploratory split is this paper's statistical spine, and RQ6's
"Partly", the abstract's EEG sentence, and the Conclusion all rest on one boundary cell
(p = .0496 at n = 18) that flips sign of significance under the study's own descriptive
estimand. A reviewer who finds D.1 will read the body's silence as concealment, even though the
appendix is honest.
Change: state in §5.4 and §6.2 that the cell is specific to the onset-centred 37-epoch
aggregation and null under the whole-window median; fix the "averaged over the whole
conversation" sentence; consider downgrading the abstract clause to match.

### MAJOR

**M1. The Dataset B pre-onset window absorbs the advertised turn's ~3 s retrieval silence, and
this is never acknowledged for EEG.**
§4.2 (p. 7): "on the advertised turn retrieval runs before generation and adds about 3 s …
identical across the four advertisement conditions, which is why it cancels in the format and
timing contrasts." §6.5 (p. 15): "a pause that cancels only in the format and timing contrasts."
But the confirmatory Dataset B cells are each advertisement **against a matched no-ad reply**
(E.4, p. 46), where the pause does not cancel: the 4 s pre-window of an advertised turn is
dominated by an abnormally long silent wait (≈6 s TTFT vs 2.7 s), while the matched control's
pre-window follows normal pacing. Post−pre therefore partly contrasts "relief from an unusually
long wait" against an ordinary reply onset. For implicit mentions the pre-window additionally
contains partial reply streaming ("the latter falling before the reply has finished streaming",
E.3, p. 47), which the control pre-window does not.
Why it matters: the paper is careful about this confound for behaviour and silent about it for
the one EEG estimand whose entire logic is a clean pre/post comparison. The null Dataset B board
is easy to live with; the exploratory explicit-early tilt is not — a 4.6 dB δ rise after an
abrupt paint following an abnormal silence is exactly where a waiting/orienting confound bites.
Change: one paragraph in §6.5 or E.3 stating the asymmetry and why it does or does not threaten
the onset-locked cells; ideally a control analysis locking no-ad windows to equally delayed
replies.

**M2. "Trust did not fall on any corrected contrast" is contradicted by the paper's own adjusted
estimator.** (D3 above.) The Results section handles the straddling cell with exemplary honesty;
the Discussion and Conclusion then erase it. Either the LMM is an "adjusted check" whose Holm
p = .048 counts as corrected — in which case the sentence is false — or the primary-estimator
reading is intended, in which case say "on the declared estimator" and keep the straddle visible.
A PC reviewer will quote Table 4 against §6.1.

**M3. Two different "noticed" operationalisations are cited interchangeably.** (D4 above.) The
abstract's headline notice numbers (69–74% / 39–46%) are the two-item outcome; the figure the
text cites for those numbers (Figure 7) plots the single sponsored-buttons item (81/74/46/37)
and redefines "noticed" in its caption. One of the paper's most quotable findings — the notice
gap — currently cannot be traced from sentence to figure without opening Table 8 and guessing
which column is meant. Fix the citation or the figure; state one definition.

**M4. The pooling defence is quarter-answered and one defence sentence is false.** (D2 above.)
Table 17 checks the any-ad contrast by arm; the format and timing contrasts — the actual RQ1/RQ2
effects — are never reported by arm, in a sample where the arms differ in age (M 29.5 vs 35.7),
device, incentive, and raw extraversion (p = .039). C.7's "arm is not a factor in any family" is
contradicted by §4.5 and Table 14. The claim "the four primary any-advertisement contrasts have
the same sign and order in each arm" (§6.5) is the right kind of evidence; extend it to the
format and timing contrasts or soften the pooling claim, and delete or repair the false sentence.

**M5. The abstract and Conclusion promote an exploratory onset effect into a format difference
the Discussion explicitly refuses to claim.** (D5 above.) "None after the mention" is an absence
claim on cells with asymmetric onset precision (reconstruction error 0.43 s for mentions vs
0.23 s for banners, §4.4) and 2–4 dB intervals at one trial per cell. The Discussion's own
verdict — "not a demonstrated difference between the formats" — is the correct one; the short
forms must match it.

### MINOR

- **m1.** "36 exploratory tests" for nine measures × three contrasts (D1). Fix the count or name
  the twelfth measure / fourth contrast.
- **m2.** "which no confirmatory claim in this thesis makes" (D.2, p. 39) — this is the paper.
- **m3.** The body never names the epoch count behind Dataset A; "the count being standardised to
  the shortest eligible conversation" (§4.8/4.4) cannot be turned into 37 epochs ≈ 148 s without
  the appendices. Given C1, the count belongs in the body. Also the "k = 37 neighbourhood"
  leftover (D16).
- **m4.** "On turn t" in Appendix B (D13) against \(k\) everywhere else.
- **m5.** Title "Behavioral" vs body "behavioural" (D11).
- **m6.** RQ7 "Supported" against the legend's own "partly" definition (D8): one of six declared
  pairs survives. At minimum the legend needs a third clause.
- **m7.** Conclusion (p. 16): "not a placement rule but **an obligation: to disclose**" — a
  deployment prescription from a design that never crossed disclosure with presentation
  ("Realised disclosure θ co-varies with presentation … rather than being crossed with it",
  §4.3). The study measured that half the users missed the sponsorship of a mention; it did not
  measure that disclosure changes any outcome. Related slip, Future Work (p. 17): "vary appeal α,
  explicitness ϵ, modality σ, **initiative, frequency**, and repeated exposure, so that the
  taxonomy's other coordinates receive the same measurement" — initiative and frequency are
  decisions of \(\pi\) ("persistence, and exposure pattern", §3.2), not coordinates of \(a_k\).
- **m8.** Related-work closer (p. 4): "The evidence that exists is **about yield**; what is
  missing is the user's bill" — overclaims on the page's own citations: Tang et al. measured
  notice and stop-requests, Salvi et al. persuasion and notice, Zelch et al. acceptance. The
  defensible gap is the EEG × format × timing within-participant combination, which the first
  gap sentence already states.
- **m9.** Appendix A euro-sign note vs the printed "EUR 1,200" (D10); "3d-editing" (A.2, p. 22).
- **m10.** Venue-less references and lowercased titles (D15).
- **m11.** "XXXXX" placeholders in Funding and Ethics (D14) — acceptable only if the venue
  requires anonymised back matter; verify.
- **m12.** §6.2's "smallest Holm p = .08" is a number that exists only in appendix Table 22;
  borderline new-number-in-Discussion.
- **m13.** "About half" (§5.2) vs "more than half" (§6.1, Abstract) for the
  recognised-afterwards share (D7); table the count.

### VERIFY

- **v1.** §5.1 "35 use a chatbot at least daily" against Figure 5d's stacked percentages — the
  figure dump does not let me reconstruct the counts exactly; likely rounding, but check.
- **v2.** Dataset B's four cells share two matched control windows ("Four labelled
  advertisements and two matched \(a^\emptyset\) replies per participant", E.5): early cells
  share one control, late cells share another. Holm is valid under that dependence, but the
  sharing is never stated where the cells are reported.
- **v3.** The explicit-early tilt's Holm survival is ICA-dependent: "+4.60 dB (Holm p = .007)"
  with ICA vs "+3.04 dB (raw p = .073, Holm p = .29)" without (D.1). The Discussion's "the
  cleaning did not create it" is fair as far as it goes; with no EOG channel and a proxy-based
  component rule, the residual ocular contribution to a broadband δ rise after an abrupt paint
  is not excluded. The Discussion's "What produced the tilt is not settled" mostly covers this —
  keep it that way in any revision.
- **v4.** ρ = .80 at n = 18 on a single-item trust outcome and an EEG score whose split-half
  reliability is .56 (§5.5): an observed correlation that high against that reliability ceiling
  invites the capitalisation-on-chance reading. The paper reports LOO ρ .77–.86, Pearson/Kendall
  agreement, and frames it as "a candidate correlate" — the right frame; expect the PC to push.
- **v5.** The two association families (six pairs per EEG score) are not jointly corrected
  across the two scores; the sixteen-measure screen (posterior α survives at Holm p = .001)
  mops this up for trust, but the two-family structure deserves one clause.
- **v6.** The realised-design uniformity checks (χ²(16) = 17.0, p = .38; χ²(16) = 17.4, p = .36,
  C.7) have almost no power at N = 54 over 25 cells with realised imbalance 5 vs 17; the paper's
  own admission that "a task effect that happened to align with a condition would not be removed"
  is the honest sentence — keep it prominent.

---

## 3. Top 5 vulnerabilities

1. The single confirmatory EEG effect (early−late posterior α, −0.22 dB, Holm p = .0496, n = 18)
   is null under the authors' own whole-window median (−0.09 dB, p = .20) at every epoch width,
   and the abstract, RQ6, and Conclusion all carry the cell without that caveat.
2. The onset-locked EEG estimand compares post−pre windows whose pre-window contains the
   advertised turn's extra ~3 s of silent retrieval wait — a confound the paper acknowledges for
   behaviour ("cancels only in the format and timing contrasts") and never mentions for Dataset B.
3. The headline trust sentence "Trust did not fall on any corrected contrast" is contradicted by
   the paper's own Table 4 (LMM Holm p = .048 on early−late), so the one estimator-straddling
   cell is handled honestly in Results and flattened in Discussion and Conclusion.
4. The notice-gap numbers cannot be traced from text to figure: abstract and §5.2 quote the
   two-item outcome (69/39%) while citing Figure 7, which plots the single sponsored-buttons
   item (74/37%) under a caption that redefines "noticed".
5. The paper's bridge finding — trust × onset-locked posterior α, ρ = .80 — rests on n = 18, a
   single-item trust score, and an EEG score with split-half reliability .56, with two per-pair
   correction families; it is framed as a candidate correlate but is already in the abstract.

## 4. Three strongest aspects

1. **The analysis contract.** Table 3 plus §4.5 enumerate every family with its n, estimator,
   and correction family, and the four-status label system (confirmatory / exploratory /
   post hoc / sensitivity) is actually enforced in the prose: post hoc grids are labelled in
   their headings, the 256-test sweep is reported as "about the five chance predicts", and the
   2,560-test map as "105 raw hits where 128 are expected under the global null". The contrast
   algebra (weights, \(t=\sqrt{n}\bar D/s_D\), \(d_z\), the decibel reading in D.2) checks out
   against the condition means of Table 7.
2. **The positive control before the nulls.** Testing writing-vs-reading on the two confirmatory
   markers before any advertisement contrast (Fz θ +0.60 dB, Holm p = .007, in the predicted
   direction) is exactly the discipline consumer-EEG work usually skips, and it converts the
   Dataset A/B nulls from "dead pipeline" into informative precision statements with intervals
   "tenths of a decibel wide".
3. **Self-undermining robustness reporting.** Leave-one-item-out moves are reported in both
   directions (Table 10), the condition-dummy parameterisation's 18 raw hits "rest on the same
   two participants" (C.6), the ICA-dependence of the tilt is quantified (D.1), and the
   estimator concordance figure puts the one straddling cell on display. This is a paper that
   shows its seams, which is rarer than any of its results.

## 5. Scores

| Dimension | Score (1–10) |
|---|---|
| Research question / contribution | 8 |
| Design | 6 |
| Statistical validity | 7 |
| Technical correctness | 7 |
| Results / interpretation discipline | 7 |
| Internal consistency | 6 |
| Reproducibility | 7 |
| Writing / short-form craft | 8 |
| **Overall, as it stands** | **6** |

## 6. Reviewer verdict

What would make me argue weak reject in the PC meeting: not the sample size, which the paper is
honest about, but the pattern that the short forms keep outrunning the analysis. The one
confirmatory EEG cell is aggregation-fragile and the fragility lives in Appendix D.1 while the
abstract spends it; the trust sentence in the Discussion is falsified by the paper's own Table 4;
the notice percentages in the abstract cannot be found in the figure cited for them; and the
onset-locked estimand has an unacknowledged latency asymmetry in its pre-window. Each item is
individually repairable in a day of editing, and the underlying discipline (families, labels,
sensitivity quarantine, positive control) is genuinely better than most submissions in this
space — but a paper whose main contribution is measurement rigour is judged by whether its
sentences survive contact with its own tables, and right now four of its most quotable sentences
do not. If the revision carries the caveats into the abstract/Discussion and fixes the
traceability slips, this moves to a clear accept; as submitted, I would argue weak accept at
best, trending weak reject if the PC weights the EEG headline.

## 7. Rest of the paper

- **Introduction.** The Alphabet/Meta revenue framing earns its paragraph; the jump from "the
  bill is now being presented to conversational AI" to the welfare triad is fast but works.
  Consider stating earlier that nothing here is pre-registered — it is currently first disclosed
  in §4.5, and reviewers will want it on page 1–2.
- **Related work.** Fix the "evidence … is about yield" closer (m8). The gap sentence itself
  ("no study sits at the intersection of LLMs, advertising, and EEG") is defensible on the
  citations given.
- **Theory.** The taxonomy mostly earns its page: \(\lambda\), \(\theta\), and the fixed
  coordinates do real work in §4.3, and \(\pi\) is used afterwards (Related Work, §4.3,
  Future Work). \(\iota\) and \(\sigma\) are never used again after Table 2; one sentence saying
  so would pre-empt the "notation dump" reading. The \(\mu\)/\(\pi\) boundary hedge ("may depend
  on the system architecture") is appropriately modest.
- **Methods.** Name the Dataset A epoch count in the body (m3). State the shared-control
  structure of Dataset B where the cells are introduced (v2). The "different assistant" warning
  is itself a small deception on top of the advertising deception; one clause acknowledging the
  layering would strengthen the ethics paragraph.
- **Appendices.** A and B are genuinely useful (verbatim prompts and briefings, declared
  mistakes). C is well organised. D.1 is where the paper's most important caveat hides — promote
  its Dataset A paragraph. E is the strongest appendix; the four-zone pipeline and the
  never-written-to-disk cleaning rule are reproducibility practice worth keeping. The 22-item
  questionnaire itself is nowhere reprinted (only item short labels in figures); for a paper
  claiming an open instrument, add the battery to an appendix or cite a public deposit for it.
- **Data availability.** "Raw EEG recordings … upon reasonable request" is standard; the
  de-identified tables release is the real asset and should be cited in §5.1, not only in the
  back matter.

---

## Typos and wording

- p. 1 (title): "**Behavioral** and EEG Responses" — US spelling against UK "behavioural"
  throughout the body (e.g. §4.4 "Behavioural measures", p. 8; "Behaviour–EEG associations",
  p. 12).
- p. 7 (§4.2): "so **the one silent wait in a session** is about 6 s" — there are four advertised
  conversations per session, hence four such waits; should read "in a conversation".
- p. 39 (D.2): "which no confirmatory claim in **this thesis** makes" — should be "this paper".
- p. 38 (D.1): "the **k = 37 neighbourhood**" — leftover internal naming; also the only place
  the body-adjacent reader meets the count.
- p. 24 (Appendix B): "**On turn t** the system message is \(p_t\)" — free \(t\); the turn index
  is \(k\) everywhere else (\(a_k\), \(u_k\), \(a_2\)/\(a_4\)).
- p. 12 (§5.4): "on Dataset B six cells reach raw p < .05, **about the five chance predicts**" —
  garbled; presumably "about the five that chance predicts".
- p. 4 (§3.1): "although the two **share some overlap**" — redundant; "although the two overlap".
- p. 22 (A.2): "**3d-editing**" — should be "3D editing" (declared verbatim copy, but then see
  next item).
- p. 23 (Appendix A intro): "(the laptop briefing **used a euro sign before 1,200**)" — the
  printed A.2 reads "capped at **EUR 1,200**"; the note describes a mistake the printed text
  does not contain.
- p. 10 (Table 3): "3 contrasts within each measure; **36 tests**" — arithmetic (9 × 3 = 27);
  repeated at p. 11 ("36 exploratory tests").
- p. 35 (Table 14): "**Environment (2)**" — undefined factor name for the laboratory/crowd arm;
  §4.5 calls the same factor "arm".
- p. 36 (C.7): "arm is **not a factor in any family**" — false as written (see D2).
- p. 14 (§6.1): "Trust did not fall on **any corrected contrast**" — contradicted by Table 4's
  LMM Holm p = .048.
- p. 28 (Figure 7 caption): "Noticed is agreement (≥ 5 of 7) on **the sponsored-content
  detection item**" — redefines the two-item outcome of §4.4 as a single item.
- p. 17 (Funding/Ethics): "supported by **XXXXX** under grant number **XXXXX**"; "approved by
  **XXXXX** under approval number **XXXXX**" — placeholders.
- p. 17 (Acknowledgements): "even if **it's** just a bit" — contraction and hedge are fine in
  an acknowledgement but sit oddly against the paper's register.
- pp. 18–21 (References): missing venues for [Qiu and Mei, 2026], [Yun et al., 2026],
  [Tang et al., 2025], [Subramanian et al., 2026], [Zhang et al., 2026b]; lowercased titles
  ("**Eeg**-based consumer behavior prediction", "injecting personalized advertising into **llm**
  chatbots", "**Naiad**: Initiate data-driven research for **llm** advertising").
- p. 8 (§4.4) vs p. 46 (E.2): "epochs **centred on** that condition's visual onset" vs "epochs
  whose midpoints lie **nearest** that condition's visual onset" — pick one description.
- p. 11 (§5.2) vs p. 14 (§6.1): "**about half** of the participants who had not noticed the
  implicit mention" vs "**more than half** of those who had not reported the mention as
  sponsored" — same share, two wordings, no tabled count.
