# Jury v2 — Deepseek (web, PDF only, black v2). Stored 15 Sep 2026, 16:34.

Verbatim dump. Not Gold. **Known extraction artefact:** Deepseek's PDF reader
renders δ and θ as β (as in v1). Every "β" below that stands where the source
has \(\delta\) or \(\theta\) (Fz β, β^(a), "↑β,β;↓α,β", \hat{g}_k for
\(\delta_k\)) is a reader error, not a thesis error. Verify against the .tex.

---

# External Examiner's Review — Version 2

## Job 1: Cross-Document Consistency Audit

### Consistency Audit Table

| Analysis Family / Check | n | Tests | Estimator | Correction Family | Headline Number | Verbal Claim | Disagreement? |
|---|---|---|---|---|---|---|---|
| Behavioural battery | 54 | 16 | Paired *t* on D_i; Wilcoxon raw; LMM adjusted | Holm within each of 4 primary outcomes (3 contrasts) and 2 cued-recall items (2 contrasts) | 8/16 survive Holm | Table 7.8: "notice, any ad – no ads, +2.07 [1.53, 2.62], Holm p < .001" | Abstract gives +1.27 for manipulation, not traceable to Table 7.8 |
| Personality moderation | 54 | 60 | LMM trait × contrast | Holm within outcome across 15 | 0/60 survive | Table 7.8: "nearest extraversion on credibility, Holm p = .18" | None |
| Demographic moderation | 54 | 70 + 70 | LMM factor × contrast | Holm within outcome | 0/70 survive (both codings) | Table 7.9: "nearest cued memory early–late by familiarity, Holm p = .44" | None |
| Dataset A — condition aggregation (confirmatory) | 18 | 6 (2 measures × 3 contrasts) | Paired *t* on D_i^A; Wilcoxon raw | Holm within each measure | 1/6 survive | Table 7.8: "early – late posterior α –0.22 dB [−0.39, −0.04], Holm p = .0496" | None |
| Dataset B — onset-locked (confirmatory) | 18 | 8 (2 measures × 4 contrasts) | Paired *t* on D_i^B; Wilcoxon raw | Holm within each measure | 0/8 survive | Table 7.8: "nearest implicit late Fz β –1.38 dB [−2.80, 0.04], Holm p = .22" | None |
| Positive control (writing vs reading) | 18 | 2 | Paired *t* on D_i | Holm across 2 | 1/2 survive | Table 7.8: "Fz β +0.60 dB [0.22, 0.97], Holm p = .007" | Table 6.1 typo: "D1 = y1*min − y1*med" |
| Exhaustive pairwise EEG | 18 | 256 | Paired *t* on every pair | Holm within measure | 1/256 survives | Table 7.8: "implicit early – explicit late Fz β –0.28 dB, Holm p = .014" | None |
| Fourteen exploratory EEG measures | 18 | 98 | Paired *t* | Holm within measure | 7/98 survive | Table 7.8: "explicit early relative β +0.19 [0.09, 0.29], Holm p = .004" | None |
| Genre trajectories δ₂^(a) | 54 | 4 | McNemar; paired *t* interval | Holm across 4 | 0/4 survive | Table 7.8: "early pooled +0.046 [−0.082, 0.174], Holm p = .94" | Results uses β^(a) instead of δ^(a) |
| Genre trajectories late N_shift | 54 | 3 | Paired *t*; Wilcoxon raw | Holm across 3 | 0/3 survive | Table 7.8: "late pooled –0.074 [−0.361, 0.213], Holm p = 1.00" | None |
| Genre-aligned δ̃₂^(a) | 54 | 1 | Permutation | None (single test) | 9 aligned vs 10.46 expected, p = .80 | Table 7.8: "9 aligned shifts against 10.46 expected, permutation p = .80" | None |
| Genre shares turn 1 vs turn 4 | 54 | 6 | Paired *t* | Holm across 6 | 4/6 survive | Table 7.8: "guidance share 0.478 → 0.211, dz = −1.00, Holm p < .001" | None |
| Behaviour × EEG associations | 18 | 6 + 6 | Spearman | Holm within 6 per score | 1/12 survives | Table 7.8: "onset-locked trust × posterior α ρ = .80 [.48, .93], Holm p = .0004" | None |
| Behaviour × trajectory associations | 54 | 6 | Spearman | Holm within 6 | 0/6 survive | Table 7.8: "manipulation × late N_shift ρ = .22 [−.05, .46], Holm p = .67" | None |
| Trajectory × EEG associations | 18 | 2 | Spearman | Holm within 2 | 0/2 survive | Table 7.8: "Fz β × δ₂^(a) ρ = .47 [−.02, .78], Holm p = .095" | None |
| Behaviour × trajectory × EEG | 18 | 3 | Partial Spearman | Holm within 3 | 0/3 survive | Table 7.8: "trust × posterior α given δ₂^(a), partial ρ = .80" | None |

---

### Disagreements Found

**D1. Abstract manipulation number not traceable to Table 7.8**
- **Abstract (p. 3):** "Any advertisement raised perceived manipulation by +1.27 on a seven-point scale"
- **Results (Table 7.8):** "Key estimate: notice, any ad – no ads, +2.07 [1.53, 2.62], Holm p < .001"
- **Problem:** The +1.27 manipulation effect is not the key estimate in Table 7.8 and is not quoted in the Results text. It may appear in Table 7.2, but the Abstract's headline number must be directly traceable to a Results table cell.

**D2. Conclusion misstates the EEG slow-power tilt**
- **Conclusion (Section 9.1):** "the first four seconds after an early banner carry a transient slow-power tilt (↑β,β;↓α,β)"
- **Discussion (Section 8.3):** "absolute β rises by 4.60 dB, absolute θ and relative δ rise with it, and relative α and β fall"
- **Abstract (p. 3):** "absolute β and θ up, relative α and β down"
- **Problem:** "↑β,β" is internally contradictory and does not match the Discussion or Abstract. It should be "↑δ,θ;↓α,β" or similar.

**D3. Results uses β for the ad-associated genre shift**
- **Results (Section 7.5):** "AD-ASSOCIATED SHIFTS (β^(a))" and Figure 7.10: "Share of transitions with \hat{\beta}_k = 1"
- **Theory (Definition 2/6):** "\hat{g}_k = \mathbb{I}[\hat{g}_{k+1} \neq \hat{g}_k]" and "\hat{g}_k^{(a)} = I_k \hat{g}_k"
- **Problem:** β is not the symbol defined for genre shifts. The central trajectory measure is inconsistently named across chapters.

**D4. Theory uses the same symbol for genre label and shift indicator**
- **Definition 1:** "\hat{g}_k = f_{\mathrm{genre}}(u_k)"
- **Definition 2:** "\hat{g}_k = \mathbb{I}[\hat{g}_{k+1} \neq \hat{g}_k]"
- **Problem:** \hat{g}_k denotes both the predicted genre and the binary shift indicator. This is a notation collision that makes the formal definitions ambiguous.

**D5. Discussion introduces a new test count not in Results**
- **Discussion (Section 8.3):** "On Dataset B, six nominal cells out of 96 is about what chance predicts"
- **Results (Table 7.8 / Appendix D.3):** Reports 256 exhaustive pairwise tests and 8 of 256 raw p < .05.
- **Problem:** The 96-test subset for Dataset B is not reported in Results. The chapter contract says Discussion should not introduce new numbers not in Results.

**D6. Table 6.1 typo in positive control formula**
- **Methods (Table 6.1):** "one-sample t on D1 = y1*min − y1*med"
- **Intended:** Writing minus reading.
- **Problem:** Typo in a formal table.

---

## Findings

### MAJOR

**M1. Conclusion misstates the EEG slow-power tilt**
- **Location:** Conclusion Section 9.1: "transient slow-power tilt (↑β,β;↓α,β)"
- **Problem:** The bands are contradictory and inconsistent with the Abstract and Discussion. "↑β,β" is impossible.
- **Why it matters:** This is a headline EEG result. An examiner will ask which bands moved.
- **Change:** Correct to "↑δ,θ;↓α,β" or align exactly with Discussion.

**M2. Notation collision in Theory Definitions 1–2**
- **Location:** Definition 1: "\hat{g}_k = f_{\mathrm{genre}}(u_k)"; Definition 2: "\hat{g}_k = \mathbb{I}[\hat{g}_{k+1} \neq \hat{g}_k]"
- **Problem:** The same symbol denotes genre label and shift indicator.
- **Why it matters:** The trajectory formalism is the thesis's theoretical contribution. Ambiguity here undermines all downstream uses.
- **Change:** Use distinct symbols, e.g., \delta_k for the shift indicator.

**M3. Results uses β for the ad-associated shift**
- **Location:** Results Section 7.5: "AD-ASSOCIATED SHIFTS (β^(a))"; Figure 7.10: "\hat{\beta}_k = 1"
- **Problem:** β is not defined for genre shifts. Theory uses \hat{g}_k^{(a)} or δ.
- **Why it matters:** The central trajectory measure is inconsistently named, confusing readers and reviewers.
- **Change:** Replace β with δ or \hat{g}^{(a)} throughout Results and Figures.

**M4. Abstract's +1.27 manipulation effect not traceable to Table 7.8**
- **Location:** Abstract p. 3: "+1.27 on a seven-point scale"
- **Problem:** Table 7.8's key estimate is notice +2.07, not manipulation +1.27. The Abstract's headline number needs a direct table cell.
- **Why it matters:** The consistency audit requires Abstract numbers to trace to Results.
- **Change:** Ensure Table 7.2 contains +1.27 and cite it explicitly, or revise Abstract.

**M5. Discussion introduces 96-test subset not in Results**
- **Location:** Discussion Section 8.3: "six nominal cells out of 96"
- **Problem:** Results reports 256 exhaustive pairwise tests and 8/256 raw hits; the 96 subset for Dataset B is not in Results.
- **Why it matters:** Violates the chapter contract that Discussion contains no new numbers not in Results.
- **Change:** Move the 96-test count to Results or Appendix D.3 and cite it.

### MINOR

**m1. Table 6.1 positive control formula typo**
- **Location:** Table 6.1: "D1 = y1*min − y1*med"
- **Change:** Correct to writing minus reading.

**m2. Figure 4.5 caption notation**
- **Location:** Figure 4.5: "Red: Fz \hat{\theta}_{i}"
- **Change:** Correct to Fz θ.

**m3. Inconsistent model naming**
- **Location:** Section 5.2.2: "Qwen 3.6 35B-A3B" vs "35 BA3B"
- **Change:** Standardise.

**m4. Abstract approximate proportions**
- **Location:** Abstract: "approximately eight in ten versus six in ten"
- **Problem:** Results gives 57%, 59% vs 87%, 81%. Approximations are acceptable but could be exact.
- **Change:** Optionally use exact percentages.

### VERIFY

**V1. Trust early–late LMM Holm .048 vs Abstract "trust did not differ"**
- **Abstract:** "trust did not differ on any planned contrast"
- **Results:** "LMM .048" for trust early–late.
- **Check:** The planned estimator is paired *t*; LMM is adjusted check. If the Abstract refers to planned contrasts, it is correct. Clarify.

**V2. Table 7.8 Dataset A tests = 6**
- **Methods:** "3 contrasts, separately within each measure" for 16 measures = 48.
- **Results Table 7.8:** "Dataset A, condition aggregation 18 6 1"
- **Check:** Table 7.8 likely counts only the 2 confirmatory measures × 3 contrasts = 6. The 14 exploratory measures are in a separate row (98 tests). This is consistent if read as confirmatory family only. Clarify in table caption.

**V3. Definition 6 indices**
- **Definition 6:** "\hat{g}_k^{(a)} = I_k \hat{g}_k"
- **Check:** The inequality \tilde{g} ≤ \hat{g}^{(a)} ≤ \hat{g} holds if \hat{g} is the shift indicator. Ensure notation is unambiguous.

---

## Top 5 Vulnerabilities

1. **Conclusion EEG tilt typo:** How can the slow-power tilt be "↑β,β;↓α,β" when the Discussion says "absolute β rises... relative α and β fall"?
2. **Notation collision in Theory:** You use \hat{g}_k for both genre label and shift indicator. How is a reader supposed to parse Definitions 1–6?
3. **Results uses β for genre shifts:** Why does Results call the ad-associated shift β^(a) when Theory defines it as \hat{g}^{(a)} or δ?
4. **Abstract manipulation number:** Where is +1.27 in the Results tables? Table 7.8 shows notice +2.07, not manipulation +1.27.
5. **Discussion's 96-test subset:** You report "six nominal cells out of 96" in Discussion, but Results only reports 256 pairwise tests and 8/256 raw hits. Where does 96 come from?

---

## Three Strongest Aspects

1. **Declared limitations are now explicit:** Non-pre-registration, EEG within-measure correction, classifier validity, and Dataset B single-trial nature are all acknowledged.
2. **Abstract–Discussion alignment on EEG:** The Abstract no longer claims "depends on how and when"; it correctly frames the trust association as a candidate for replication.
3. **Open-source and reproducibility:** The platform, data card, fixed seeds, and versioned identifier are described well enough in the PDF to support rebuild in principle.

---

## Scores

| Dimension | Score (1–10) |
|---|---|
| Research question/contribution | 8 |
| Design | 7 |
| Statistical validity | 5.5 |
| Technical correctness | 7.5 |
| Results/interpretation discipline | 7 |
| Internal consistency | 6.5 |
| Reproducibility | 8 |
| Writing | 7 |
| **Overall** | **6.8** |

---

## Examiner Verdict

What would make me challenge this thesis in the defence? I would challenge the notation and internal consistency of the trajectory formalism. The Theory chapter uses \hat{g}_k for both the predicted genre and the binary shift indicator, and the Results chapter then uses β for the ad-associated shift. This is not a cosmetic issue: the genre-trajectory measure is one of the thesis's theoretical contributions, and an examiner cannot verify the definitions if the symbols are overloaded. I would also challenge the Conclusion's misstatement of the EEG slow-power tilt as "↑β,β;↓α,β" when the Discussion says absolute β rises and relative α and β fall. And I would ask where +1.27 comes from in the behavioural results, since Table 7.8's key estimate is notice +2.07. The thesis has improved substantially in its declared limitations and Abstract–Discussion alignment, but these remaining inconsistencies will be the first things a committee picks up.

---

## Rest of the Thesis — Suggestions

**Introduction:** The RQ list is clear. RQ2 and RQ4 now correctly say "not testable here" in Table 8.1. Good.

**Related Work:** Strong coverage. The gap statement is well-supported.

**Theory:** Fix the notation collision in Definitions 1–2. Use \delta_k for the shift indicator and \hat{g}_k only for the genre label.

**Datasets:** Table 4.6 is garbled in the PDF conversion; ensure the final PDF is readable.

**System Design:** The KV-cache arithmetic is correct. The limitations section is honest.

**Methods:** Table 6.1 has a typo in the positive control formula. Clarify that Table 7.8's Dataset A row counts only the confirmatory measures.

**Results:** Replace β with δ or \hat{g}^{(a)} in Section 7.5 and Figure 7.10. Move the 96-test subset to Results or Appendix D.3.

**Discussion:** Avoid new numbers not in Results; cite the 96-test subset if kept.

**Appendices:** Appendix D is thorough. Appendix E provides useful robustness checks. Appendix F clearly documents the context-window sweep.

**Conclusion:** Correct the EEG tilt notation. Ensure the "obligation to disclose" is framed as a policy implication, not a serving recommendation, consistent with Discussion Section 8.6.
