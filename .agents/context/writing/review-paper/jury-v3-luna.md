reviewer: GPT Luna
PDF path: /home/wtroi/MasterThesis-RAG-RecSys/docs/overleaf/publication/_build/main.pdf
page count: 49
compile: succeeded
PDF mtime: 2026-09-17 14:00:06 UTC (repository copy; stamp reports scratch copy 13:59:01 UTC)
newest tex mtime: 2026-09-17 12:44:33 UTC (stamp)

# Conference review

## 1. Consistency audit

| Analysis family | n | Tests / estimator | Correction | Headline in Results | Claim in Discussion / Abstract / Conclusion | Audit |
|---|---:|---|---|---|---|---|
| Behavioural battery | 54 | 16 planned contrasts; one-sample paired t on person-level \(D_i\), Wilcoxon raw sensitivity, LMM check | Holm within each of four primary outcomes; two recall contrasts within each recall outcome | Table 4: 8/16 survive; manipulation any-ad \(+1.27\), notice \(+2.07\), early–late credibility \(-.33\), trust planned contrasts null | Felt commercial pressure is the main behavioural cost; trust is bounded/null on the declared estimator | Consistent. The Discussion correctly preserves the t/LMM/Wilcoxon disagreement for trust early–late. |
| Format × timing interaction | 54 | Four outcome-specific coded contrasts \(w=(1,-1,-1,1,0)\), one-sample t | Raw p, outside the planned Holm family | All four near zero; \(|d_z|\le .06\), raw \(p\ge .65\) | No detectable interaction; no additive-effect recommendation | Consistent. The weights and “uncorrected” status are explicit. |
| Secondary qualities | 54 | 12 planned contrasts on helpfulness, convincingness, relevance, neutrality | Holm within outcome | Early–late convincingness and relevance survive, \(p=.005,.003\) | Mentioned as supporting timing evidence, not promoted to the four-outcome headline | Consistent. |
| Logged interaction measures | 54 | 36 tests on durations, lengths, and latencies, same t | Holm within measure; exploratory | No planned or interaction cell raw \(p<.05\) | No logged behavioural effect | Consistent. |
| Localisation | 54 | Four ad condition-minus-control cells per outcome, t | Holm within outcome; post hoc | Early explicit trust \(-.69\), Holm \(p=.031\) | Trust falls only in this post hoc cell; explicitly not a planned trust result | Consistent. |
| Pairwise behavioural sweep | 54 | Ten pairs per outcome, Friedman plus paired t sweep | Holm within outcome; post hoc | Adds no primary-outcome cell beyond planned margins | Used only to localise, not to add a finding | Consistent. |
| Personality moderation | 54 | 60 trait × contrast × outcome Wald terms; OLS check | Holm within outcome across 15 terms | 0/60 survive; nearest Holm \(p=.18\) | No detectable moderation, explicitly bounded by \(N=54\) | Consistent. |
| Demographic moderation | 54 | 70 terms under each of two codings, mixed model/OLS check | Holm within outcome | 0/70 under either coding; age omitted because only 44/54 recorded | No tested demographic moderation | Consistent. |
| Positive control | 18 | Writing-minus-reading t on Fz \(\theta\), posterior \(\alpha\) | Two confirmatory measures | Fz \(\theta\) \(+0.60\) dB, Holm \(p=.007\); posterior \(\alpha\) null | Pipeline registers a within-conversation change in the predicted marker | Consistent, though “pipeline therefore registers” is validation rather than an ad effect. |
| Dataset A / condition aggregation | 18 | Three contrasts per measure; t, Wilcoxon raw | Holm within measure across three contrasts | Confirmatory posterior \(\alpha\), early–late \(-.22\) dB, Holm \(p=.0496\) | Timing leaves a trace, but the contrast shares variance with conversational depth | Consistent and appropriately caveated. |
| Dataset B / onset-lock | 18 | Four cells per measure; t, Wilcoxon raw | Holm within measure across four cells | All eight confirmatory cells null; intervals span roughly 2–4 dB | Confirmatory onset-locked cells are null | Consistent. |
| Fourteen exploratory EEG measures | 18 | Dataset A and B planned cells for each measure | Holm within each measure, no across-measure correction | 7/98 cells survive; 5 form the explicit-early slow-power pattern | A single exploratory slow-power tilt, not seven independent findings | Mostly consistent; the abstract and Discussion qualify it, but the “five of six” wording must be read as onset-locked only. |
| EEG exhaustive pairwise | 18 | 256 post hoc pairs across 16 measures | Holm within measure | One Dataset A Fz \(\theta\) pair survives; Dataset B none | Explicitly not used to revise confirmatory claims | Consistent. |
| Behaviour × EEG association | 18 | Spearman on six declared behavioural pairs per EEG score; Pearson/Kendall checks | Holm separately within six pairs for each of two EEG scores | Onset-locked posterior \(\alpha\) × trust \(\rho=.80\), Holm \(p=.0004\); condition aggregation \(\rho=.24\), raw \(p=.34\) | Candidate correlate, not mediation or mechanism | Numerically consistent, but the decision to treat the two EEG scores as separate six-test families is a substantive multiplicity vulnerability (Finding M3). |

### Disagreements and checks

1. **No direct numerical contradiction between Abstract/Results/Conclusion was found.** The abstract’s \(+1.27\) manipulation effect, \(-.33\) early–late credibility effect, \(-.49\) re-exposure trust effect, \(-.22\) Dataset A posterior-\(\alpha\) effect, \(\rho=.80\), and null onset-locked confirmatory cells trace to Tables 4, 20, 21, and the Results text. The Conclusion’s rounded Holm \(p=.15\) is Table 4’s .153.
2. **The EEG wording is materially more careful in the current version.** Abstract: “the confirmatory onset-locked cells were null” and “confounded with conversational depth.” Table 21 contains eight null confirmatory cells; Results §5.4 says “Dataset B is Holm-null in all eight confirmatory cells.” These match.
3. **The exploratory EEG count is internally coherent but easy to misread.** Results §5.4 says “five of the six exploratory Holm cells on the onset-locked side”; Table 19 contains those five onset-locked explicit-early cells plus one onset-locked implicit-late cell and one Dataset A relative-\(\theta\) cell. The sentence refers to the five-of-six explicit-early onset pattern, not all seven Table 19 rows. This is not a numerical contradiction, but the wording is vulnerable.
4. **Holm terminology is consistent.** The paper repeatedly defines “Holm p” as adjusted t p and labels Wilcoxon values raw; I found no “Wilcoxon Holm” misuse.
5. **Dataset A nomenclature is consistent.** The PDF uses “condition aggregation” and “onset-locked”; I found no Path A/B or equal-\(n\) neighbourhood terminology.
6. **Notation is consistent.** \(\Pi\) is the strategic policy, \(\pi\) the online serving rule, and \(a_2/a_4\) the insertion-turn notation. The paper does not use a free \(t\) as the insertion-time symbol.
7. **The coded interaction is explicit.** Equation (4.1) and §4.5 give \((1,-1,-1,1,0)\), its difference-of-differences interpretation, and its raw p outside the three-contrast Holm family.
8. **Results and Discussion largely respect their contracts.** The Results contains some light interpretive transitions (“the protocol therefore registers...”), but no major design recommendation. Discussion adds numbers that already occur in Results rather than introducing new estimates.
9. **RQ coverage is complete.** Table 1’s RQ1–RQ7 all appear in Table 5. RQ6 is answered “Partly” because the timing/aggregation result is significant while format and onset-locked confirmatory cells are null; RQ7 is answered for trust and explicitly limits credibility/manipulation.
10. **The required body/appendix inventory is present.** The body carries the taxonomy table, UI figure, planned behavioural board, EEG Holm board, association figure, and RQ table; the body points to the appendix forests, notice percentages, localisation, and pipeline. No appendix result was found to be silently promoted as a confirmatory headline.

## 2. Findings

### CRITICAL

**C1 — The PDF is not submission-ready because ethics and funding fields remain placeholders.**  
Location: p. 18, Ethics Statement and Funding. The paper says “This work was supported by XXXXX under grant number XXXXX” and “The study was approved by XXXXX under approval number XXXXX.” These are not harmless methodological caveats: a programme committee cannot verify approval, and an ethics placeholder can block acceptance or camera-ready publication. If anonymisation is intentional, the venue’s required disclosure mechanism should be used; otherwise replace both placeholders before submission.

### MAJOR

**M1 — The five-condition repeated-measures design leaves order, questionnaire carry-over, and task-position effects unmodelled.**  
Location: Methods §4.2 p. 7: “Tasks rotate in Latin-square order and the five conditions are shuffled independently”; Results Appendix C.7 p. 37: “Task identity and session position are balanced by that rotation rather than modelled”; Limitations p. 16: “a task effect that happened to align with a condition would stay in the contrast.” The realised task × condition table is notably uneven (e.g., study environment × implicit late = 17, gardening × implicit late = 5), despite a non-significant omnibus uniformity test. Randomisation is a design protection, not a test that removes realised imbalance, and the repeated 22-item battery plus awareness of later recall can create position-dependent ratings. The paper acknowledges this but still presents pooled condition contrasts as if the randomisation fully protects them. At minimum, the primary claims need a sensitivity model including task and session position (with the estimand and degrees of freedom stated), or the scope of the claims should be reduced to the randomised sample rather than treated as task-general.

**M2 — Any-advertisement behavioural effects and Dataset B pre-onset windows are inseparable from the approximately three-second retrieval delay.**  
Location: Methods p. 7: “retrieval runs before generation and adds about 3 s”; Limitations p. 16: “the any-advertisement cells therefore measure the advertisement together with its delay” and “the onset-locked pre-onset window... sits inside the wait.” This is a direct treatment-control confound for the largest behavioural headline, \(+1.27\) manipulation and \(+2.07\) notice, and it changes the physiological baseline immediately before the nominal display onset. The statement that delay “cancels in the format and timing contrasts” is only partly reassuring: it cancels as a nominal server feature across ad cells, but early and late ads occur at different conversational moments, and the onset-locked pre-window is not a neutral pre-stimulus baseline because it includes waiting for the response. The paper correctly discloses the problem, but the abstract and conclusion should not let “any advertisement” read as a pure ad effect, and the Dataset B interpretation should foreground “ad-plus-wait versus matched reply” rather than a clean onset response.

**M3 — The association’s multiplicity policy is defensible numerically but under-justified scientifically.**  
Location: Methods §4.5 p. 10: “the two EEG scores are two families by design”; Results p. 12: \(\rho=.80\), raw \(p=6\times10^{-5}\), Holm \(p=.0004\); Discussion p. 15: “Trust is related to the posterior \(\alpha\) response.” The analysis evaluates six behavioural pairs for each of two EEG estimands, and the estimand producing the headline result is the onset-locked score. Treating the two scores as independent families is not implied by the fact that they are different estimands; they are two operationalisations of the same RQ7 and were both inspected. A single 12-test family would still leave the reported association significant, so this does not overturn the result, but it changes the error-control claim. The paper should state the result under the joint 12-test correction and make explicit that the association is a candidate correlate selected among two estimands and six behavioural outcomes, not a confirmatory mechanism.

**M4 — “Confirmatory” carries more authority than the design can support without preregistration.**  
Location: Methods p. 9: “The sample size was set by recruitment and the study was not pre-registered”; p. 9: “Confirmatory: the measure, the contrast, and its weights were fixed on theoretical grounds before the result was read”; Appendix D p. 39: the 1,050 µV threshold was “set after inspecting the cohort’s epoch-amplitude distribution.” The paper is unusually transparent about this, and the 4 s width and 37-epoch count are justified. However, a reader cannot independently know that the measure, threshold, width, epoch selection, and exclusion choices were fixed before results. The confirmatory label should be framed as “planned/unregistered” throughout, especially for the boundary \(p=.0496\) posterior-\(\alpha\) cell, rather than relying on “confirmatory” as if it conveyed preregistered protection.

**M5 — The Dataset A timing EEG result is still vulnerable to a depth/turn confound despite the new caveat.**  
Location: Abstract p. 1: “confounded with conversational depth”; Results p. 12: “posterior α was lower for early than for late insertion”; Discussion p. 14: “how much of the cell belongs to the insertion is not separable.” Early versus late changes the amount and content of conversation surrounding the 37 selected epochs, not only the ad’s time. The paper’s conclusion calls this a timing result and says “the moment of insertion... registers,” although the same sentence acknowledges depth. A PC reviewer can reasonably say this is an early-versus-late session-position/depth contrast, not evidence that ad timing itself changes sustained posterior alpha. The effect should be labelled as the early–late condition-aggregation contrast in every headline sentence, with the causal timing interpretation explicitly withheld.

**M6 — The onset-locked format comparison is not like-for-like and the abstract’s juxtaposition risks implying one.**  
Location: Methods p. 8: mention onset reconstruction error 0.43 s versus banner 0.23 s; Limitations p. 16: “the onset-locked comparison is strongest as the banner against its matched control rather than as a like-with-like comparison”; Abstract p. 1: “at early-banner onset an exploratory slow-power tilt appeared and none after the mention at the same turn.” The direct implicit-versus-explicit onset comparison is null (smallest Holm \(p=.08\)), while the banner-versus-control exploratory cells survive within-measure correction. “Banner has a tilt, mention does not” is a descriptive asymmetry, not evidence of a format effect when the formats differ in physical onset, reconstruction error, streaming state, and disclosure. The paper states this in Discussion, but the abstract/conclusion should put the null direct comparison before the juxtaposed cell pattern.

### MINOR

**m1 — The exploratory EEG family description risks false reassurance from within-measure Holm.**  
Location: Table 3 p. 10 and Appendix D p. 40: “Holm within measure across its planned contrasts, never across measures”; “seven Holm-surviving cells.” The paper does state that 98 tests yield roughly five chance hits and calls the cells a pattern to replicate. Still, a reader scanning Figure 2/Table 19 sees seven asterisks and may read them as seven controlled findings. The table caption or first Results sentence should say “seven cells across 14 uncorrected-across-measure exploratory families; not joint-FWER controlled” in one place.

**m2 — The boundary posterior-\(\alpha\) result is numerically precise but rhetorically close to a positive finding.**  
Location: Table 20 p. 41: \(-.22\) dB, Holm \(p=.0496\); Discussion p. 14: “the one confirmatory Dataset A cell that survives Holm.” The paper gives the depth caveat and does not hide the boundary. Given \(n=18\), an unregistered pipeline, and the fact that the significant result is one of six confirmatory marker/contrast cells, the language should consistently say “one boundary surviving planned cell” rather than “timing leaves a trace” without the estimand qualifier.

**m3 — The no-click result is correctly reported but the contribution language can still be read as effectiveness-adjacent.**  
Location: Abstract p. 1: “no one clicked”; Introduction p. 2: “user-side cost”; Data Availability p. 18. The paper generally avoids claiming behavioural effectiveness, and Discussion explicitly says it does not measure advertiser-side outcomes. Still, “served rules can be learned and audited on real human responses” and “no one clicked” sit near advertising-performance framing. The contribution should keep clicks clearly as a null logged interaction outcome, not evidence that the formats were ineffective commercially.

**m4 — The notice measure’s low reliability and its interpretation as a single “notice” outcome deserve one stronger limitation sentence.**  
Location: Methods p. 8: notice is the mean of brand mention and sponsored-button items; Appendix C p. 29: \(\alpha=.61\); Discussion p. 14: “Notice as a manipulation check.” The paper correctly says brand mention is not detection, but the composite combines a generic product/brand recognition item with a sponsored-button item. The strong format effect may partly reflect the banner’s visible button affordance rather than a general detection construct. The item-level appendix shows this, but the headline “notice” should remain explicitly operational (“agreement on the two-item notice outcome”).

### VERIFY

**V1 — The literature-gap sentence is stronger than the evidence visible in the PDF.**  
Location: Related Work p. 4: “no study sits at the intersection of LLM-native conversational advertising and concurrent EEG.” The cited literature plausibly separates the three areas, but the PDF gives no search protocol and an absolute “no study” claim cannot be verified from a short reference list. This is a reasonable motivation claim, not a demonstrated result; qualify it as “we found no...” or define the search boundary.

**V2 — Reproducibility is strong in outline but not fully rebuildable from the PDF alone.**  
Location: Methods p. 6–10 and Appendix E p. 45–48. The paper provides hardware, markers, filtering, ICA thresholds, epoch rejection, spectral definitions, family table, and released-data links. However, the confirmatory tables still depend on implementation details not fully specified here: exact handling of incomplete windows and marker fallbacks, the complete condition/session pairing algorithm, and the precise mixed-model formula/covariance structure. This is not a fatal short-paper omission because code/data are linked, but the PDF-only rebuild criterion is not fully met.

**V3 — The taxonomy earns a useful framing role, but its empirical reuse is limited.**  
Location: Table 2 and §3 p. 5; Methods p. 7. \(\Pi\), \(\pi\), \(\lambda\), and \(\theta\) are used later, while most dimensions are held fixed. The taxonomy is not merely abandoned notation, but the paper should be clear that it is a measurement vocabulary and design scaffold, not a validated taxonomy of deployed advertising systems.

**V4 — The “same product” control needs a little more evidence.**  
Location: Methods p. 7: “The same product then feeds either the mention or the banner, so presentation and product content are not confounded”; Limitations p. 16: “The relevance of the particular product served is recorded but unknown.” If product assignment is deterministic from the conversation and shared within the format pair, this is adequate for the format contrast; if retrieval is rerun separately, it is not. The paper should state how product identity was paired across conditions and whether any products/tasks were missing.

## 3. Top five vulnerabilities

1. A committee would say the largest behavioural effect is advertisement-plus-retrieval-delay versus no advertisement, while the onset-locked EEG baseline is literally inside that delay, so the central “cost of advertising” is not isolated from system latency.
2. A committee would say the only confirmatory EEG timing effect is a boundary \(p=.0496\) early–late condition contrast in which early and late are confounded with conversational depth, so it cannot support a causal timing claim.
3. A committee would say the repeated within-subject battery, uneven realised task-by-condition counts, and unmodelled session position leave carry-over and task alignment as plausible alternatives to the pooled behavioural contrasts.
4. A committee would say the headline \(\rho=.80\) association is selected from two EEG estimands and multiple behavioural outcomes, while the paper treats the estimands as separate correction families; the result survives a joint correction but the reported inferential contract is not the strongest one.
5. A committee would say the exploratory EEG “slow-power tilt” is assembled from five cells among 98 tests with no across-measure error control and a no-EOG ICA pipeline, so it is a replication hypothesis rather than evidence for a format-specific neurophysiological effect.

## 4. Three strongest aspects

1. The paper is unusually explicit about estimands and analytical status. It distinguishes condition aggregation from onset-lock, gives the full planned-weight vectors, labels post hoc and sensitivity analyses, and repeatedly states that Wilcoxon p values are raw.
2. The behavioural interpretation is disciplined. It does not convert the trust null into proof of no harm, preserves the t/LMM/Wilcoxon disagreement, distinguishes notice from detection, and keeps the post hoc early-banner trust drop out of the planned headline.
3. The EEG limitations are visible rather than buried: the paper reports one trial per onset-locked cell, reconstruction error, no EOG channel, no-ICA sensitivity, epoch-width sensitivity, the depth confound, and the lack of joint correction across exploratory measures.

## 5. Scores

- Research question / contribution: **7/10**
- Design: **5/10**
- Statistical validity: **6/10**
- Technical correctness: **7/10**
- Results / interpretation discipline: **7/10**
- Internal consistency: **8/10**
- Reproducibility: **6/10**
- Writing / short-form craft: **8/10**
- Overall score as it stands: **6/10**

## 6. Reviewer verdict

I would argue for weak reject unless the venue permits a substantial limitations/reframing pass. The study has a clear user-side question, a valuable crossed behavioural design, and unusually good disclosure of its EEG and multiplicity limitations, but its strongest claims remain exposed at exactly the points a programme committee will test: the main ad-versus-control effects include a large server-delay difference; the only confirmatory EEG timing effect is a boundary, depth-confounded early–late contrast; the onset-locked format evidence is not a direct format effect; and the association correction treats two estimands as separate families. These are not fatal because the association survives a joint correction and the authors mostly acknowledge the confounds, but the paper currently asks the reader to accept “cost of advertising,” “timing registers,” and a banner-specific slow-power pattern more strongly than the design can identify. The ethics/funding placeholders are an immediate submission blocker.

## 7. Rest-of-paper notes

- **Introduction:** The user-centric motivation is clear, but the opening macroeconomic material is longer than needed for a short paper; the strongest contribution begins when the paper defines the measured user-side cost.
- **Related Work:** Qualify the absolute intersection-gap sentence and separate “no concurrent EEG study found” from the broader claim that prior work does not measure user-side cost.
- **Theory:** Keep the \(\Pi/\pi\) distinction and Table 2, but explicitly state that most taxonomy coordinates are held fixed and are not empirically identified here.
- **Methods:** State the exact pairing/randomisation and mixed-model formula; explain whether product identity is held fixed across matched format cells; make the joint association correction visible as a sensitivity result.
- **Appendices:** The pipeline appendix is valuable. Add a compact table mapping each abstract/conclusion EEG phrase to Table 19, 20, or 21, and make the seven exploratory cells’ lack of across-measure control visually unavoidable.
