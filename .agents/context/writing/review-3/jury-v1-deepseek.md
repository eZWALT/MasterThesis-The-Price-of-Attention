# Jury v1 — Deepseek (15 Sep 2026)

Thesis: v1 PDF (source-cleaned 14 Sep). Prompt:
`../2026-09-11-thesis-review-metaprompt.md`.
Raw examiner dump. Do not treat its table cells as Gold; verify
against the PDF before applying. Do not apply until Walter says so.

---

# External Examiner's Review

## Job 1: Cross-Document Consistency Audit

### Consistency Audit Table

| Analysis Family | n | Tests | Estimator | Correction | Headline Number | Verbal Claim |
|---|---|---|---|---|---|---|
| **Behavioural battery** | 54 | 16 | Paired t on D_i; Wilcoxon raw; LMM adjusted | Holm within outcome (4 primary, 2 recall) | 8/16 survive Holm | Table 7.8: "notice, any ad – no ads, +2.07 [1.53, 2.62], Holm p < .001" |
| **Personality moderation** | 54 | 60 | LMM trait × contrast | Holm within outcome across 15 | 0/60 survive | Table 7.8: "nearest extraversion on credibility, Holm p = .18" |
| **Demographic moderation** | 54 | 70 + 70 | LMM factor × contrast | Holm within outcome | 0/70 survive (both codings) | Table 7.9: "nearest cured memory early - late by familiarity, Holm p = .44" |
| **Dataset A (condition aggregation)** | 18 | 3 contrasts × 16 measures | Paired t on D_i^A; Wilcoxon raw | Holm within each measure | 1/48 survive (posterior α early−late) | Table 7.8: "early – late posterior α – 0.22 dB [−0.39, −0.04], Holm p = .0496" |
| **Dataset B (onset-locked)** | 18 | 4 contrasts × 16 measures | Paired t on D_i^B; Wilcoxon raw | Holm within each measure | 0/64 survive | Table 7.8: "nearest implicit late Fz β – 1.38 dB [−2.80, 0.04], Holm p = .22" |
| **Positive control (writing vs reading)** | 18 | 2 | Paired t on D_i | Holm across 2 | 1/2 survive (Fz θ) | Table 7.8: "Fz β + 0.60 dB [0.22, 0.97], Holm p = .007" |
| **Exhaustive pairwise EEG** | 18 | 256 | Paired t on every pair | Holm within measure | 1/256 survives (Fz θ implicit early – explicit late) | Table 7.8: "implicit early – explicit late Fz β – 0.28 dB, Holm p = .014" |
| **Fourteen exploratory EEG measures** | 18 | 98 | Paired t | Holm within measure | 7/98 survive | Table 7.8: "explicit early relative β + 0.19 [0.09, 0.29], Holm p = .004" |
| **Genre trajectories δ₂^(a)** | 54 | 4 | McNemar; paired t interval | Holm across 4 | 0/4 survive | Table 7.8: "early pooled + 0.046 [−0.082, 0.174], Holm p = .94" |
| **Genre trajectories late N_shift** | 54 | 3 | Paired t; Wilcoxon raw | Holm across 3 | 0/3 survive | Table 7.8: "late pooled – 0.074 [−0.361, 0.213], Holm p = 1.00" |
| **Genre-aligned δ̃₂^(a)** | 54 | 1 | Permutation | None (single text) | 9 aligned vs 10.46 expected, p = .80 | Table 7.8: "9 aligned shifts against 10.46 expected, permutation p = .80" |
| **Genre shares turn 1 vs turn 4** | 54 | 6 | Paired t | Holm across 6 | 4/6 survive | Table 7.8: "guidance share 0.478 → 0.211, dz = −1.00, Holm p < .001" |
| **Behaviour × EEG associations** | 18 | 12 | Spearman | Holm within 6 per score | 1/12 survives | Table 7.8: "onset-locked trust × posterior α β = .80 [.48, .93], Holm p = .0004" |
| **Behaviour × trajectory associations** | 54 | 6 | Spearman | Holm within 6 | 0/6 survive | Table 7.8: "manipulation × late Nshift β = .22 [−.05, .46], Holm p = .67" |
| **Trajectory × EEG associations** | 18 | 2 | Spearman | Holm within 2 | 0/2 survive | Table 7.8: "Fz β × g2(a) β = .47 [−.02, .78], Holm p = .095" |
| **Behaviour × trajectory × EEG** | 18 | 3 | Partial Spearman | Holm within 3 | 0/3 survive | Table 7.8: "trust × posterior α given g2(a), partial β = .80" |

---

### Disagreements Found

**1. Trust early−late estimator disagreement**
- **Methods (Table 6.1):** "one-sample t on D1 of (6.1); Wilcoxon sensitivity; random-intercept linear mixed model on Y2 as an adjusted check"
- **Results (Section 7.2.1):** "The one estimator disagreement which is borderline significant after correction is trust early minus late (t Holm .063, LMM .048, raw Wilcoxon .026; Figure E.4)."
- **Problem:** The LMM and t disagree on Holm verdict. The thesis acknowledges this but does not reconcile it. The LMM is described as "the adjusted check" yet its verdict differs from the pre-specified estimator. Which is primary?

**2. Abstract/Conclusion claims not traceable to Results**
- **Abstract:** "Explicit banners were remembered far better than implicit mentions (approximately eight in ten versus six in ten)"
- **Results (Table 7.2):** Cued memory implicit early M = 4.35, explicit early M = 6.09. The "eight in ten versus six in ten" phrasing does not appear in Results; Table E.2 shows 57% and 87% for ≥5 ratings. The Abstract's numbers are approximates not directly traceable.
- **Problem:** Abstract rounds and reframes proportions without matching the Results table's exact values.

**3. "Any advertisement raised perceived manipulation by +1.27"**
- **Abstract:** "+1.27 on a seven-point scale"
- **Results (Table 7.8):** Key estimate for behavioural battery is "notice, any ad – no ads, +2.07" not manipulation. Table 7.2 does not list the pooled any-ad manipulation contrast as a separate row; it appears in Figure 7.3 localisation.
- **Problem:** The +1.27 figure requires averaging across four conditions; it is not a single table cell in the main Results.

**4. EEG "depends on how and when"**
- **Abstract:** "The EEG response 'depends on how and when'"
- **Discussion (Section 8.3):** "They do not combine into one claim that the response depends on how and when the advertisement enters."
- **Problem:** The Abstract asserts a claim the Discussion explicitly refuses. This is a direct contradiction.

**5. "Early insertions elicit 'greater visual processing'"**
- **Abstract:** Not present verbatim.
- **Discussion (Section 8.3):** "posterior α did not fall at onset but rose slightly, which is not what attentional capture would predict."
- **Problem:** If the Abstract or Conclusion implies greater visual processing, it contradicts the Discussion's caution.

**6. "Explicit-late placement is a 'compromise'"**
- **Conclusion (Section 9.1):** "an advertisement that is less visible but harder to identify is not necessarily less intrusive"
- **Discussion (Section 8.6):** "This is not a recommendation to serve advertisements late or implicitly."
- **Problem:** The Conclusion's "obligation to disclose" and "be patient" language edges toward a serving recommendation the Discussion disclaims.

**7. Dataset A naming**
- Methods consistently "condition aggregation"; no leftover "Path A/B" or "equal-n neighbourhood" found.
- **Verified:** Consistent.

**8. Notation δ_k(a_k) vs δ^{(a)}_k**
- Theory (Definition 6): "δ_k^{(a)} = I_k δ_k"
- Methods/Results: "δ^{(a)}_k" and "δ₂^(a)"
- **Disagreement:** Theory uses "δ_k^{(a)}" with subscript k and superscript (a); Results uses "δ₂^(a)" with numeral subscript. Minor but inconsistent.

**9. Interaction weights (1, −1, −1, 1, 0)**
- Methods (Section 6.3): "the presentation-by-timing interaction"
- Results: Not reported as a separate estimate; Figure 8.1 shows it as dots (unestimated).
- **Problem:** The interaction is described in Methods but never estimated in Results.

**10. Results chapter interpretation**
- **Section 7.2.1:** "Trust is Holm-null on the three planned contrasts."
- **Section 7.4:** "That is the reassuring half of the result"
- **Problem:** "Reassuring" is interpretation, not a number. The Results chapter contains evaluative language.

**11. RQ answers**
- **Introduction:** RQ1–RQ9 as specified.
- **Discussion Table 8.1:** Answers nine questions.
- **RQ2:** "Does format shift the conversation's genre?" — answered "Not supported" on δ₂^(a), but the question asked about trajectory, not just the crossing shift.
- **RQ4:** "Does timing shift the conversation's genre?" — answered "Not supported" on N_shift, but late ads have no following utterance, so the question is structurally unanswerable for late conditions.
- **Problem:** RQ2/RQ4 are quietly redefined from "trajectory" to "ad-associated shift" or "N_shift."

**12. No RQ10/RQ11**
- **Verified:** No RQ10 or RQ11 exists.

**13. Task moderation not an RQ**
- **Verified:** Task is not modelled as a moderator; it appears only in sensitivity checks.

---

## Findings

### CRITICAL

**C1. Abstract–Discussion contradiction on EEG interpretation**
- **Location:** Abstract: "The EEG response 'depends on how and when'"; Discussion Section 8.3: "They do not combine into one claim that the response depends on how and when the advertisement enters."
- **Problem:** The Abstract asserts a claim the Discussion explicitly refuses. This is a direct logical contradiction on the thesis's most novel contribution.
- **Why it matters:** The EEG is the thesis's differentiator. If the Abstract overclaims, examiners will challenge the entire neurophysiological contribution.
- **Change:** Delete the "depends on how and when" phrasing from the Abstract or align it with the Discussion's more cautious language.

**C2. Confirmatory status without pre-registration**
- **Location:** Methods Section 6.3: "Two complementary views... planned confirmatory contrasts, whose measures and weights were fixed on theoretical grounds before the corresponding results were read"
- **Problem:** No pre-registration exists. The same author chose the measures (k = 37 epochs, 4 s width), the contrasts, and the correction families. The confirmatory/exploratory split is post hoc.
- **Why it matters:** The entire statistical framework's credibility rests on the claim that confirmatory tests were fixed before data. Without pre-registration, this is unverifiable.
- **Change:** Acknowledge explicitly that the split is logical, not temporal, and temper claims accordingly.

**C3. EEG multiplicity: Holm within measure, not across**
- **Location:** Methods Section 6.3: "on EEG it never runs across the sixteen measures, because the five relative powers share a denominator and cannot move independently"
- **Problem:** The sixteen measures are correlated, but correcting within each measure ignores the family-wise burden across all sixteen. The confirmatory pair (Fz θ, posterior α) is tested separately, but the exploratory fourteen are also Holm-corrected within measure, not across the fourteen.
- **Why it matters:** With 16 measures × 3 contrasts = 48 tests on Dataset A, the probability of at least one Holm-surviving cell by chance is not controlled at α = .05 across the board.
- **Change:** Report the family-wise error rate across all EEG tests or justify why the correlation structure licenses within-measure correction.

**C4. Dataset B: single trial per cell, no reliability**
- **Location:** Section 4.2.4: "All 216 Dataset B epochs were retained (108 pairs). There is no median over many epochs: a single 4 s window is the observation."
- **Problem:** Dataset B has one trial per cell. The onset-locked score is a single 4 s response. Split-half reliability is reported only for Dataset A (posterior α any-ad − no-ad .78, Fz θ not detectable). No reliability is reported for Dataset B.
- **Why it matters:** A single-trial measure with unknown reliability cannot support strong claims. The trust × posterior α association (ρ = .80) rests on this single-trial score.
- **Change:** Report split-half or test-retest reliability for Dataset B scores, or acknowledge the limitation explicitly in the association interpretation.

**C5. Genre classifier validity not established**
- **Location:** Section 4.2.3: "The two disagree on most turns" (bare vs contextual); Section 7.5: "Agreement with the runtime log 351/1,080 (32.5%)"
- **Problem:** The 13-class DistilBERT classifier (ThradBERT, 83.8% held-out accuracy on its own data) agrees with the runtime label only 32.5% of the time on this corpus. The classifier's validity on short shopping utterances is not established before its nulls are interpreted.
- **Why it matters:** The entire trajectory family rests on this instrument. If the classifier is invalid for this domain, the nulls are uninterpretable.
- **Change:** Validate the classifier on a sample of this corpus before interpreting the nulls, or state explicitly that the nulls are about the instrument, not the theory.

---

### MAJOR

**M1. Latency confound in Dataset B pre-onset window**
- **Location:** Section 5.1.2: "On the one advertised turn, retrieval runs before the first token (median 3.03 s), so that silent wait is about 6 s"
- **Problem:** The advertised turn carries ~3 s of extra silent retrieval wait. Dataset B's pre-onset window is [-4 s, 0). If the pre-window includes the retrieval wait, the contrast is confounded with latency.
- **Why it matters:** The onset-locked difference (post − pre) may reflect the release from waiting, not the advertisement.
- **Change:** Verify whether the pre-window includes retrieval wait; if so, acknowledge the confound.

**M2. Format comparison in Dataset B: onset timing mismatch**
- **Location:** Section 4.2.4: "the moment it becomes visible is uncertain to about 0.23 s for explicit banners and 0.43 s approximately for implicit mentions"
- **Problem:** Implicit onset is reconstructed (p95 uncertainty 0.43 s), explicit banner onset is observed (0.49 s after reply is on screen). The two formats are not measured with equal precision.
- **Why it matters:** The implicit–explicit comparison at onset may reflect onset timing uncertainty, not format.
- **Change:** Acknowledge this limitation in every format comparison in Dataset B.

**M3. Disclosure θ confounded with presentation λ**
- **Location:** Section 6.2.5: "Realised disclosure θ co-varies with presentation λ rather than being crossed with it"
- **Problem:** The limitation is declared but not carried into every format claim. The Discussion Section 8.1 interprets format effects (notice, manipulation, memory) without consistently noting that disclosure is confounded.
- **Why it matters:** Any format effect could be a disclosure effect.
- **Change:** Add a sentence to each format interpretation noting the confound.

**M4. Personality null over-read**
- **Location:** Section 8.2: "Who the user is does not seem to change what the advertisement costs them"
- **Problem:** 60 tests at N = 54 with two-item BFI-10 traits is low power. The null is not evidence of absence.
- **Why it matters:** The conclusion "personality does not matter" is too strong for the design.
- **Change:** Temper to "no moderation detected in this sample."

**M5. Demographics family: 70 tests with sparse levels**
- **Location:** Section 8.2: "An earlier pass over these factors on the same data read uncorrected p-values on single condition dummies; most of the cells it flagged (14 of 18) sit on levels filled by two or three people"
- **Problem:** The family was run with 70 tests, some on levels with n = 2 or 3. This is underpowered and unstable.
- **Why it matters:** The null is uninformative; the "nearest cell" at Holm p = .44 is meaningless.
- **Change:** Acknowledge that the demographic family is underpowered and the null is not informative.

**M6. Trust × posterior α association: multiplicity across two scores**
- **Location:** Section 6.3: "each behaviour × EEG pair is evaluated on both, Holm within the six for each score"
- **Problem:** Two EEG scores (Dataset A, Dataset B) were evaluated per pair. The Holm-significant result is on Dataset B; the same pair on Dataset A is ρ = .24. The selection between scores is post hoc.
- **Why it matters:** The association is a bounded hypothesis, not a finding.
- **Change:** Frame explicitly as a hypothesis for replication, not a result.

**M7. 2,560-test exploratory map**
- **Location:** Section 7.6.3: "2,560 tests in 21 families, Holm within family; 105 reach raw .05 where 128 are expected"
- **Problem:** The map is clearly separated from declared pairs, but the "105 raw hits where 128 expected" is a null result presented as a finding ("no cell survives Holm").
- **Why it matters:** The null is expected by chance; it does not validate the absence of effects.
- **Change:** State that the map is underpowered and the null is uninformative.

**M8. Permutation of advertised genre breaks participant pairing**
- **Location:** Section 6.3: "the advertised genre g^(a) is reassigned at random across the 108 early-advertisement conversations"
- **Problem:** Each participant has two early ads. The permutation is at the conversation level, not the participant level, breaking the within-participant pairing.
- **Why it matters:** The null is a conversation-level null, not a participant-level test.
- **Change:** Acknowledge that the permutation is conversation-level and the inference is limited.

---

### MINOR

**m1. "Holm p" vs "Wilcoxon p"**
- **Location:** Table 7.2: "Holm-adjusted paired t; Wilcoxon p is raw"
- **Verified:** Consistent throughout. No "Wilcoxon Holm" appears.

**m2. Notation inconsistency**
- **Location:** Theory: "δ_k^{(a)}"; Results: "δ₂^(a)"
- **Problem:** Minor notation drift.
- **Change:** Standardise.

**m3. Figure 7.8 readability**
- **Location:** Figure 7.8: "Holm p within each EEG measure at 4s (n = 18)"
- **Problem:** The figure is dense and hard to read. The colour coding is not explained in the caption.
- **Change:** Add a colour legend and simplify.

**m4. Results chapter interpretation**
- **Location:** Section 7.2.1: "Trust is Holm-null"
- **Problem:** "Holm-null" is a label, not a number. The Results chapter should report estimands, not verdicts.
- **Change:** Report the estimate and interval, not just the Holm verdict.

**m5. Abstract numbers not traceable**
- **Location:** Abstract: "+1.27 on a seven-point scale"
- **Problem:** The number is not in a table cell; it requires averaging.
- **Change:** Report the exact table cell or add a footnote.

---

### VERIFY

**V1. KV-cache arithmetic**
- **Location:** Section 5.2.2: "Total KV-cache size = 16384 · 1 · 10 · 2 · 2 · 256 · 2 B = 320 MiB"
- **Check:** Verify the calculation. 16384 × 10 × 2 × 2 × 256 × 2 = 16384 × 20480 = 335,544,320 B ≈ 320 MiB. Correct.

**V2. Definitions 1–6 internal consistency**
- **Check:** δ̃ ≤ δ^(a) ≤ δ holds by construction. T−1 range: τ_k for k ∈ [1, T−1] is correct. Indices k vs i: k is temporal, i is genre index. Consistent.

**V3. D_i contrast equation**
- **Check:** D_i = Σ w_c y_ic, Σ w_c = 0. Correct.

**V4. D^A/D^B definitions**
- **Check:** D_i^A = Σ w_c median_{ℓ ∈ N_i(37)} y_iℓ; D_i^B = (y_post − y_pre)_a − (y_post − y_pre)_{a^0}. Correct.

**V5. t and d_z formulas**
- **Check:** t = √n D̄ / s_D; d_z = D̄ / s_D. Correct.

**V6. Table column definitions**
- **Check:** Table 6.1 columns match the sentence citing it. Mostly consistent.

---

## Top 5 Vulnerabilities

1. **Abstract–Discussion contradiction on EEG:** How do you reconcile the Abstract's "depends on how and when" with the Discussion's explicit refusal of that claim?

2. **Confirmatory status without pre-registration:** You claim confirmatory contrasts were fixed before results were read, but there is no pre-registration. How can an examiner trust the confirmatory/exploratory split?

3. **EEG multiplicity:** You correct within each of sixteen measures, not across them. What is the family-wise error rate across all EEG tests, and why is within-measure correction adequate?

4. **Dataset B reliability:** The onset-locked score is a single trial with no reported reliability. How can the trust × posterior α association (ρ = .80) be interpreted when the neural score's reliability is unknown?

5. **Genre classifier validity:** The classifier agrees with the runtime label only 32.5% of the time. How can the null trajectory results be interpreted when the instrument's validity on this corpus is not established?

---

## Three Strongest Aspects

1. **Theoretical contribution:** The taxonomy of conversational advertising (Table 3.1) and the intent-trajectory formalism (Definitions 1–6) provide a reusable vocabulary for a nascent field. The distinction between platform policy Π and serving policy π is analytically useful.

2. **Open-source commitment:** The platform, datasets, and analysis pipelines are released openly. The data lake architecture (Bronze/Silver/Gold) is well-documented and reproducible in principle.

3. **Methodological transparency:** The thesis declares its limitations extensively. The distinction between confirmatory, exploratory, post hoc, and sensitivity is maintained. The limitations section (8.7) is unusually thorough.

---

## Scores

| Dimension | Score (1–10) |
|---|---|
| Research question/contribution | 8 |
| Design | 7 |
| Statistical validity | 5 |
| Technical correctness | 7 |
| Results/interpretation discipline | 6 |
| Internal consistency | 6 |
| Reproducibility | 8 |
| Writing | 7 |
| **Overall** | **6.5** |

---

## Examiner Verdict

What would make me challenge this thesis in the defence?

I would challenge the confirmatory status of the EEG findings. The thesis claims that measures and weights were fixed on theoretical grounds before results were read, but without pre-registration, this is unverifiable. The same author chose k = 37 epochs, the 4 s width, the sixteen measures, and the Holm families. The one confirmatory Dataset A cell (posterior α early−late, Holm p = .0496) sits exactly at the boundary, and the LMM/t/Wilcoxon disagreement on trust early−late shows the estimator choice matters. I would ask: if the analysis choices were fixed in advance, why does the trust early−late cell produce three different Holm verdicts? And if the EEG family is corrected within measure, not across, what is the true family-wise error rate? The trust × posterior α association (ρ = .80) is presented as a finding but rests on a single-trial Dataset B score with no reported reliability and a multiplicity across two EEG scores. I would challenge the Abstract's claim that the EEG response "depends on how and when" when the Discussion explicitly refuses that claim. Finally, I would challenge the genre trajectory nulls: the classifier agrees with the runtime label only 32.5% of the time, and the advertised products share the modal genre with the conversations. The null is about the instrument, not the theory, and the thesis should say so more clearly.

---

## Rest of the Thesis

**Introduction:** The motivation is well-argued but long. The research questions are clear and well-specified. The contributions are overstated; "Small Survey on LLM based Advertisement" is not a contribution.

**Related Work:** Comprehensive and well-organised. The six-theme structure is effective. The gap statement ("no research to date sits at the intersection of LLMs, advertising, and EEG") is well-supported.

**Theory:** The taxonomy (Table 3.1) and the policy decomposition (Π = ⟨Γ, μ, π⟩) are useful. The intent-trajectory formalism is dense but internally consistent. The attention shift definition is carefully reserved for a causal subcase.

**Datasets:** The data lake architecture is well-documented. The Gold tables are clearly described. The EEG preprocessing is detailed and reproducible in principle.

**System Design:** The retrieval pipeline (HyDE + BM25 + cross-encoder) is well-motivated. The KV-cache arithmetic is correct. The limitations section is honest.

**Methods:** The statistical framework is detailed but overclaims confirmatory status. The analysis families table (6.1) is a useful summary. The D_i contrast equation is correct.

**Appendices:** The EEG preprocessing detail (Appendix D) is thorough. The behavioural battery (Appendix E) is comprehensive. The genre trajectory tables (Appendix F) are clear.

**Suggestions:**
- Add a pre-registration statement or temper the confirmatory claims.
- Report the family-wise error rate across all EEG tests.
- Add reliability estimates for Dataset B.
- Validate the genre classifier on this corpus before interpreting nulls.
- Reconcile the Abstract and Discussion on EEG interpretation.
- Standardise the δ notation.
- Simplify Figure 7.8.
