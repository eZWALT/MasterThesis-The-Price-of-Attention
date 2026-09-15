# Jury v1 — Gemini 3 Pro, full PDF (15 Sep 2026)

Thesis: v1 PDF 156 pp (`docs/overleaf/thesis/_build/dissertation.pdf`,
compiled 15 Sep from `41536e8`). Prompt:
`../2026-09-11-thesis-review-metaprompt.md`.
Supersedes `jury-v1-gemini-3-pro.md` (that dump used a truncated
PDF that stopped mid-Ch 5). Raw examiner dump. Do not treat its
table cells as Gold. Do not apply until Walter says so.

---

Job 1: Cross-Document Consistency Audit

| Analysis Family | n | Tests | Estimator | Correction | Headline Number | Verbal Claim in Abstract/TOC |
|---|---|---|---|---|---|---|
| Behavioural | 54 | 16 | Paired t, LMM, Wilcoxon | Holm (within outcome) | +1.27 perceived manipulation | "Any advertisement raised perceived manipulation by +1.27... with stronger effects for the banner" |
| Personality | 54 | 60 | Wald tests (trait × contrast) | Holm (within outcome) | None | "neither personality nor demographics moderated any outcome." |
| Demographics | 54 | 70 | Wald tests (covariate × contrast) | Holm (within outcome) | None | "neither personality nor demographics moderated any outcome." |
| EEG Dataset A | 18 | 2 conf., 14 exp. | Median of 37 4-s epochs, paired t | Holm (within measure) | p=.0496 | "posterior α power was lower for early than for late insertion." |
| EEG Dataset B | 18 | 4 cells vs no-ad | 4s post minus 4s pre onset, paired t | Holm | ↑δ,θ;↓α,β | "transient slow-power tilt... was observed, with no comparable response at mention onset." |
| Trajectories | 54 | Multiple | McNemar, paired t, Permutation | None stated for some | None | "No advertisement effects were detected in the intent trajectories" |
| Associations | 18/54 | 2,560 exp. | Spearman ρ | Holm (within family) | ρ=.80 | "onset-locked posterior α response covaried with the change in reported trust (ρ=.80)" |

Disagreements & Verification Flags:

Wilcoxon vs. Holm p mixing: The abstract asserts "trust after re-exposure was lower for early than for late insertions". Verify that this claim does not secretly rely on the raw Wilcoxon p=.026 when the Holm-adjusted paired t is non-significant (p=.063).

Interaction weights as differences-of-differences: Verify that contrast weights (1,−1,−1,1,0) are properly scaled. Unnormalized, this tests (A+D)−(B+C), which changes the magnitude of the estimand compared to a standard interaction effect.

Notation discrepancy: The prompt warns that Theory writes δ_k(a_k). However, the text shows Equation 3.8 as δ_k^{(a)}=I_k δ_k. Verify no other chapters revert to the δ_k(a_k) notation.

Dataset A Nomenclature: Verify that "condition aggregation" is strictly used. Page 30 explicitly sets "Dataset A (condition aggregation)", but check that old terms like "equal-n neighbourhood" do not leak into the unprovided results text.

Job 2: Substantive Methodological Review

CRITICAL

Location: Chapter 4, Section 4.2.4, "Dataset B (onset-locked contrast)".

Problem: Server latency confound. The advertised turn carries ≈3 seconds of extra retrieval wait. The Dataset B pre-onset window (−4s to 0s) for implicit mentions will capture this silent wait, while the no-ad control will capture active reading/streaming.

Impact: You are not comparing like with like. The pre-stimulus baseline for the treatment condition is contaminated by waiting, invalidating the "post minus pre" subtraction.

Action: Acknowledge that Dataset B's baseline is fundamentally confounded by system architecture.

Location: Chapter 4, Section 4.2.4, "Epoching".

Problem: Visual onset timing asymmetry. Implicit mentions are injected during streaming (onset uncertainty 0.43 s); explicit banners are painted after the reply (uncertainty 0.23 s).

Impact: Dataset B directly compares the ERP/spectral response of these two formats. Comparing a mid-stream text injection to a post-stream UI pop-up confounds format with task-state (reading vs. finishing reading).

Action: Limit claims regarding Format in Dataset B; prioritize the ocular/transient explanation for the explicit banner.

Location: Appendix F, Table F.2, "Kruskal–Wallis on 270 conversations".

Problem: Pooling non-independent rows. The participant is the inferential unit, yet 270 conversation rows (5 per person) are pooled for a Kruskal-Wallis test.

Impact: Violates the independence assumption. N=54 is artificially inflated to N=270, driving down p-values.

Action: Remove or heavily caveat; report only participant-aggregated tests.

MAJOR

Location: Chapter 7, Table 7.2 / Abstract "early insertion reduced credibility".

Problem: Single-item trust reliability and ceiling effects. Trust is a single item with a mean near ceiling (6/7).

Impact: Holm-null contrasts on a single, saturated item do not prove "trust was unaffected"; they merely show a lack of statistical power to detect changes at the ceiling.

Action: State that the nulls on trust are weakly informative due to measurement limits.

Location: Abstract, "onset-locked posterior α response covaried... (ρ=.80)".

Problem: Multiplicity and selection in Associations. ρ=.80 is reported for onset-locked, while the same pair under condition aggregation is ρ=.24.

Impact: Selecting the higher of two exploratory datasets to feature in the Abstract constitutes cherry-picking. With n=18, a Spearman of .80 is easily driven by a few outliers.

Action: Demote this claim from the Abstract. It is a generated hypothesis, not a confirmatory finding.

Location: Abstract, "posterior α power was lower for early than for late insertion".

Problem: Boundary p-value and depth confound. Dataset A early-late posterior α has a Holm p=.0496 at n=18. Early ads sit on turn 2; late ads on turn 4.

Impact: Turn 4 utterances differ systematically from Turn 2 (fatigue, task completion). The p=.0496 is too fragile to support an unqualified structural claim.

Action: Frame as a marginal, confounded observation rather than a strict temporal effect.

MINOR

Location: Chapter 6, Section 6.2.4 "Experimental design".

Problem: Latin-square task rotation at N=54. 54 is not divisible by 25 (5 conditions × 5 tasks).

Impact: The rotation is unbalanced. Task variance will leak into condition estimates.

Action: Model task as a random intercept in the LMM sensitivity check.

Location: Chapter 4, Section 4.2.4, "Why four seconds".

Problem: "Epoch-width sensitivity". The confirmatory cells appear only off the 4 s window.

Impact: Smells of researcher degrees of freedom if 3 s or 5 s windows were tested and discarded.

Action: Verify the 4 s window was strictly a priori.

VERIFY

Verify that the "different chatbot" warning adequately washes out carry-over effects in trust across the 5 within-participant conditions.

Verify that the 13-class DistilBERT classifier's poor agreement (32.5%) under the bare-utterance context is addressed before interpreting trajectory nulls.

Top 5 Vulnerabilities (Examiner Questions)

"How do you justify interpreting the Dataset B baseline when the implicit-ad condition suffers from a server-side latency confound that the no-ad condition lacks?"

"Given that your explicit banners appear after the text finishes streaming, while implicit mentions are injected mid-stream, how can you untangle the 'format' effect from the 'task state' (reading vs. waiting) in your EEG data?"

"Your headline association of ρ=.80 between trust and EEG relies on selecting Dataset B over Dataset A (ρ=.24) at n=18; isn't this classic multiplicity and capitalization on chance?"

"You treat the lack of a significant trust drop as evidence that certain ad formats are 'safe', but trust was measured with a single item exhibiting severe ceiling effects—doesn't this just mean you couldn't measure a drop even if one existed?"

"Why did you violate your own participant-as-unit inferential rule by running a Kruskal-Wallis test on 270 pooled, non-independent conversation rows?"

Three Strongest Aspects

Ecological Validity & Systems Engineering: Building a functional retrieval-augmented LLM pipeline with live intent classification and vector database retrieval (FAISS) to serve real Amazon products.

Multimodal Integration: Combining high-level conversational taxonomy/theory with both behavioral self-reports and dense 32-channel EEG data in a unified analytical framework.

Strict Analytical Discipline (mostly): The commitment to tracking multiple dataset grains (Bronze/Silver/Gold) and isolating confirmatory tests from exhaustive post-hoc sweeps shows strong data governance.

Scores

Research question/contribution: 8/10

Design: 6/10

Statistical validity: 5/10

Technical correctness: 7/10

Results/interpretation discipline: 5/10

Internal consistency: 7/10

Reproducibility: 8/10

Writing: 8/10

Overall Score: 6.5/10

Examiner Verdict

I would challenge this thesis primarily on the causal claims stemming from the EEG data and the over-interpretation of null behavioral results. The systemic confounding in the experimental setup—specifically the server latency injected before implicit ads and the timing discrepancy between mid-stream mentions and post-stream banners—renders the onset-locked (Dataset B) comparisons highly suspect. Furthermore, the reliance on a single-item trust metric plagued by ceiling effects to claim "no effect", coupled with the cherry-picking of a fragile p=.0496 and a ρ=.80 correlation at n=18, demonstrates a lack of statistical restraint. The engineering and theoretical taxonomy are impressive, but the quantitative interpretations stretch far beyond what the flawed design can bear.

Suggestions for the Rest of the Thesis

Introduction / Related Work: Compress the neuromarketing literature if it does not directly feed into the EEG methodology used.

Theory (Definitions 1-6): Clarify whether δ_4^{(a)} is explicitly handled as a structural missing value in the equations, preventing denominator mismatches.

System Design: Explicitly quantify the exact KV-cache latency penalty for the RAG injection and discuss it as a limitation.

Methods: Add a brief justification for why task variance is not explicitly partialled out of the primary paired t-tests given the N=54 imbalance.

Appendices: Ensure the ICA rejection criteria strictly states that only ocular components were removed, given the lack of an EOG channel.

What specific aspect of the EEG analysis would you like to clarify first before finalizing the defense slides?
