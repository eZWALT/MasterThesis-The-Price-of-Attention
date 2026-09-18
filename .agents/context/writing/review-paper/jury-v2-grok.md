# Jury v2 — independent conference review

Paper: *The Price of Attention: Behavioural and EEG Responses to Advertising in LLM Conversations* (PDF `/tmp/paper_jury_v2.pdf`, 48 pp.). Reviewed from the PDF alone. Figures 1, 4–6, 15–17 are image-heavy; I could read captions and extracted labels, not the pixels.

---

## 1. Consistency audit table

| Family (Table 3) | *n* | Tests | Estimator / correction | Headline number (Results) | Verbal claim (Abstract / Discussion / Conclusion / Table 5) | Agree? |
|---|---|---|---|---|---|---|
| Behavioural battery | 54 | 16 planned (3×4 outcomes + 2×2 cued) | one-sample *t* on *Dᵢ*; Holm within outcome; Wilcoxon raw; LMM check | Table 4: 8/16 Holm; manipulation any-ad +1.27; format −0.62; timing +0.58; notice any-ad +2.07; format −1.15; credibility timing −0.33; memory format −1.45; re-exposure timing −0.49; trust all Holm-null (timing Holm .063 / LMM .048 / Wilcoxon .026) | Abs: “+1.27… more for the banner… more for early”; “credibility by a third of a point”; “trust… did not separate… on any planned contrast”. Disc 6.1 / Conc / Table 5 RQ1–2 match the cells. Abs *opening* still says the user pays “trust”. | Numbers yes; jacket no |
| Format × timing | 54 | 1 per outcome, raw *p* | *t* on *w*=(1,−1,−1,1,0), uncorrected | 5.2: \|*d_z*\|≤0.06; coded *D* trust +0.09 [−0.31, 0.49] … notice −0.06; raw *p*≥.65 | Abs: “did not seem to interact”. Table 5 RQ3 “Not supported”. Conc: “did not detectably compound”. | Yes |
| Secondary qualities (exploratory) | 54 | 3×4 | same *t*, Holm within outcome | 5.2: convincingness / relevance early−late Holm *p*=.005 / .003 | Not in Abstract. Figure 8 reprints them. | Yes (kept off jacket) |
| Logged interaction (exploratory) | 54 | 36 | *t*; 3 contrasts + interaction per measure | 5.2: “none raw *p*<.05”; “no participant clicked” | Abs / Conc: “no one clicked” / “nobody clicked”. | Yes |
| Localisation (post hoc) | 54 | 4 cells / outcome | Holm across 4 | Table 11: trust explicit-early −0.69, Holm *p*=.031; manipulation +1.92; notice +2.81 | Abs: “fell only under the early banner in a post hoc localisation”. Conc tags −0.69 as post hoc but leads the bill with untagged “+1.92 under the early banner”. | Partial |
| Pairwise sweep (post hoc) | 54 | 10 pairs / outcome | Friedman; Holm on pairs | 5.2: trust same pair Holm *p*=.078 in the ten-pair sweep; Table 12 convincingness IE−EL Holm *p*=.034 | 5.2: “add no cell that the planned contrasts do not already contain” — false for convincingness IE−EL. | No |
| Personality | 54 | 60 | mixed model; Holm within outcome ×15 | 5.3: 0/60; nearest extraversion × credibility timing Holm *p*=.18 | Abs: “neither personality nor demographics moderated any effect”. Table 5 RQ4–5 “Not supported”. Disc 6.1 caveats *N*=54. | Yes (Abs omits the caveat) |
| Demographics (check) | Table 3: 54; Table 14: sex 51, education 49 | 70×2 codings | same model; Holm within outcome | 5.3: 0/70 and 0/70; age 44/54 “was not entered”; nearest cued-memory timing × familiarity Holm *p*=.44 | Same Abs sentence. Table 3 *n*=54 does not match Table 14. | *n* disagrees |
| Positive control write−read | 18 | 2 measures | *t*; Holm on the 2 | Fz *θ* +0.60 dB, Holm *p*=.007; posterior *α* +0.08, Holm *p*=.75 | Not in Abstract. Disc 6.2 uses it to underwrite the Fz *θ* format null. | Yes |
| Dataset A, condition aggregation | 18 | 3 / measure | *t* on *Dᵢᴬ*; Holm within measure | 5.4 / Table 20: early−late posterior *α* −0.22 dB, Holm *p*=.0496; any-ad and format Holm-null | Abs: “posterior *α* aggregated over a condition was lower for early than for late”. Table 5 RQ6 “Partly” on that cell, no depth confound. Disc 6.2 / Conc name the depth confound. | Partial |
| Dataset B, onset-lock | 18 | 4 / measure | *t* on *Dᵢᴮ*; Holm within measure | Table 21: all 8 confirmatory Holm-null; CIs 2–4 dB; nearest implicit-late Fz *θ* −1.38, Holm *p*=.22 | Abs does not claim a confirmatory onset effect. Conc “The EEG registered the moment of insertion, not the format” sounds like Dataset B. | Wording slip |
| 14 further EEG (exploratory) | 18 | 3 (A) + 4 (B) / measure | same; Holm within measure, not across | Table 19: 7 cells; 5 of 6 Dataset B orange cells on explicit-early | Abs: “at banner onset an exploratory slow-power tilt appeared and none after the mention”. Disc 6.2: one event; direct format Holm *p*=.08 is the post hoc pair (Table 22). | Partial |
| Exhaustive EEG pairwise (post hoc) | 18 | 256 | *t*; Holm within measure | Table 22: Fz *θ* IE−EL −0.28 dB, Holm *p*=.014; Dataset B nearest Holm *p*=.08 | 5.4 reports it as post hoc. Disc 6.2 recasts *p*=.08 as “the direct implicit-minus-explicit comparison at onset”. | Recast |
| Epoch width / no-ICA (sensitivity) | 18 | as parent family | same | Table 18: 2 s explicit-early Fz *θ* +3.30 Holm *p*=.021; 8 s explicit-late posterior *α* −1.22 Holm *p*=.023; no-ICA *δ* +3.04, Holm *p*=.29 | Not harvested into Abstract/Results. Disc 6.2 quotes +3.04 / .29 from D.1 — not in §5. | Disc new number |
| Behaviour × EEG | 18 | 6 pairs / EEG score | Spearman; Holm within six per score | 5.5: Dataset B trust × posterior *α* *ρ*=.80, Holm *p*=.0004; Dataset A same pair *ρ*=.24; split-half *α* .56 | Abs: “*ρ*=.80, *n*=18” only. Table 5 RQ7 “Supported for trust”. Disc 6.3: candidate correlate; single-item trust. | Abs omits the twin score and reliability |

### Disagreements (two quoted locations each)

1. **Abstract opening vs planned trust family.** Abstract: “the user pays: attention, trust, and the experience of the conversation itself.” Table 4 / §5.2: “Trust is Holm-null on the three planned contrasts”. Conclusion 7.1: “Trust counter-intuitively did not fall on any planned contrast on the declared estimator (any advertisement −0.34, Holm *p* = .15)”.

2. **Abstract EEG vs depth confound.** Abstract: “posterior *α* aggregated over a condition was lower for early than for late insertion” — no caveat. Discussion 6.2: “A late advertisement sits on a shorter, later turn, however, so timing under condition aggregation is confounded with conversational depth, and how much of the cell belongs to the insertion is not separable in this design.” Table 5 RQ6 evidence column repeats −0.22 dB, Holm *p*=.0496, and drops the confound.

3. **Conclusion “moment of insertion” vs which estimand.** Conclusion: “The EEG registered the moment of insertion, not the format: posterior *α* was lower for early than late under condition aggregation (−0.22 dB…)”. Methods 4.5: “A result on one estimand is not evidence about the other”. Dataset A is a sustained-state contrast, not an onset lock; Dataset B confirmatory is “Holm-null in all eight confirmatory cells” (§5.4).

4. **Conclusion +1.92 untagged vs post hoc contract.** Conclusion: “felt commercial pressure (+1.27 … +1.92 under the early banner)”. Table 3 / §4.5: localisation is “Post hoc: comparisons added after the planned contrasts had been read”. The same paragraph tags trust −0.69 as “post hoc grid” and leaves +1.92 unmarked.

5. **§5.2 pairwise claim vs Table 12.** Results: “The Friedman omnibus and the ten-pair sweep (Table 12) add no cell that the planned contrasts do not already contain.” Table 12: “Convincingness Implicit early − explicit late … Holm *p* .034”.

6. **Notice shares labeled as “sponsored”.** §5.2: “74% and 69% of participants reported the early and late banner as sponsored, against 46% and 39%”. Table 8 those figures are the “Notice outcome” column; “Sponsored buttons” is 81%, 74%, 46%, 37%. Figure 7 caption: “Noticed is agreement (≥ 5 of 7) on the sponsored-content detection item.”

7. **Discussion *d_z* bound not in Results.** Discussion 6.2: “nothing comparable after the implicit-early mention (\|*d_z*\| ≤ 0.37 on the same measures)”. Section 5.4 lists the explicit-early cluster and does not give implicit-early *d_z*. Table 19 contains only Holm-surviving cells.

8. **Discussion 6.2 “direct format comparison” is a post hoc pair.** Discussion: “the direct implicit-minus-explicit comparison at onset does not survive correction (smallest Holm *p* = .08)”. Table 22 / §5.4: that .08 is “implicit early minus explicit early on global *δ* (Holm *p* = .08)” in the 256-test sweep, not a planned Dataset B contrast (planned cells are each format-timing vs matched *a*∅).

9. **Discussion 6.2 no-ICA numbers not in §5.** Discussion: “Without ICA the *δ* cell keeps its sign but not its significance (+3.04 dB, Holm *p* = .29; subsection D.1)”. Section 5.4 does not report +3.04.

10. **Table 3 *n* vs Table 14 *n*.** Table 3: “Demographic moderation (check) … 54”. Table 14 caption: “Cohort *N* = 54; sex *n* = 51, education *n* = 49”.

11. **Notice as manipulation check vs RQ1 “Supported”.** Discussion 6.1: “Notice certifies that the manipulation was delivered … it does not say what the advertisement did to attention or to trust.” Table 5 RQ1 evidence: “explicit above implicit on notice +1.15, perceived manipulation +0.62, cued memory +1.45”.

12. **RQ wording quietly rewritten.** Table 1 RQ1: “How does advertisement presentation format affect the user’s **overall experience** of the conversational assistant?” Table 5 RQ1: “Does format change the **reported** experience?” Table 1 RQ7: “What is the relationship between … onset and the **subjective experience** subsequently reported”. Table 5 RQ7: “Does the response at onset **track** reported experience? … **Supported for trust**”.

13. **Contribution 3 vs Future work.** Contribution 3: “released so that serving rules can be learned and audited on real human responses”. §7.2: “each conversation here contains one served advertisement, which is enough to measure a cost and **not enough to train a model**.”

14. **Discussion refuses a serving rule; Conclusion gives users one.** Discussion 6.4: “Nor is this a recommendation to serve advertisements late or implicitly, because the design did not measure the advertiser’s side.” Conclusion: “What follows for users is that an advertisement they can recognise, and argue with, is worth more to them than a recommendation offered as ‘fake friend’ advice with no receipt”.

15. **Holm *p* / Wilcoxon.** No “Wilcoxon Holm” found. Table 4 caption: “Holm-adjusted paired *t*; Wilcoxon *p* is raw”. Table 20: “*p_W* is the uncorrected Wilcoxon … not Holm-adjusted”. This check passes.

16. **Dataset A name.** “Condition aggregation” is consistent (Table 3, Figure 2, §4.4, §6.2, Appendix E). No “Path A/B”, “equal-*n* neighbourhood”, or “condition state”.

17. **Π vs *π*; *t* vs *k*.** §3.2: “Uppercase Π is the company’s advertising policy … Lowercase *π* is the online serving policy inside it.” Insertion is *a*₂ / *a*₄ / turn *k* (§1, §4.3). Appendix E “Here *t* = 0 is visibility” is clock time, not the turn index. No Π/*π* swap found. §3.2 then calls *λ* one of “that rule’s two visible outputs” after Contribution 1 called *λ* “one dimension of the instance” — a small role slip, not a symbol swap.

18. **Interaction coding.** §4.5: “*w* = (1, −1, −1, 1, 0), that is (*a*^imp₂ − *a*^imp₄) − (*a*^exp₂ − *a*^exp₄) … raw *p*, outside the three-contrast Holm family”. §5.2 reports the coded *D*, not a ÷4 difference-of-differences. Pass, with a scale mismatch: planned early−late uses ±½ weights (*D*=−0.44 on trust) while the interaction uses ±1 (*D*=+0.09).

---

## 2. Findings

### CRITICAL

**C1. The jacket bills trust (and attention) as paid; the planned families do not.**
- Location: Abstract, first sentence: “the user pays: attention, trust, and the experience of the conversation itself.” Title: “The Price of Attention.”
- Problem: Table 4 trust any-ad *D*=−0.34, Holm *p*=.153, CI [−0.71, 0.03]. Dataset B confirmatory posterior *α* is Holm-null in all four cells (Table 21). The only confirmatory “attention” movement is Dataset A early−late posterior *α*, Holm *p*=.0496 at *n*=18, which Discussion 6.2 says is inseparable from conversational depth.
- Why it bites: a PC reader who stops at the title and abstract takes home a trust-and-attention cost the Results refuse on the declared estimator.
- Change: rewrite the opening to the quantities that move (perceived manipulation, notice/memory gap). Do not lead with trust or with “attention” as a paid resource.

**C2. “Confirmatory” is an author label, not a registered contract, and the headline EEG cell sits on the Holm line.**
- Location: §4.5: “the study was not pre-registered, so four labels record the status of each test. Confirmatory: the measure, the contrast, and its weights were fixed on theoretical grounds before the result was read.” Table 20: early−late posterior *α* *t*=−2.66, *p_raw*=.017, *p_Holm*=.0496. Appendix E: “That amplitude bound [1,050 μV] was set after inspecting the cohort’s epoch-amplitude distribution; it is neither preregistered nor taken from the literature.” Gold Dataset A: “37 is the shortest eligible window”.
- Problem: the same author chose the two markers, the 4 s width, the shortest-window epoch count, the rejection bound, and the per-measure Holm families, then printed *p*=.0496 as Figure 2’s only confirmatory asterisk and as Table 5’s RQ6 support.
- Why it bites: without a time-stamped protocol, “confirmatory” vs “exploratory” cannot carry the weight Abstract/Results give it. At *n*=18, Holm *p*=.0496 is a boundary that a different family (across two markers, or across 16 measures) would kill.
- Change: state in the body that the EEG timing cell is a single, unregistered, depth-confounded, *n*=18 boundary result. Do not let Table 5 say “Partly” as if the question were answered on the same footing as manipulation +1.27.

### MAJOR

**M1. Format is *λ* bundled with *θ*; Conclusion then licenses a disclosure preference.**
- Location: §4.3: “Realised disclosure *θ* co-varies with presentation (on request versus commercial nature disclosed) rather than being crossed with it.” Table 5 caption: “Format is the bundled presentation-plus-disclosure contrast (*λ* with *θ*).” Discussion 6.4: “which raises a disclosure question this study did not test.” Conclusion: “an advertisement they can recognise, and argue with, is worth more to them…”
- Problem: every format contrast (notice −1.15, manipulation −0.62, memory −1.45) is *λ*+*θ*. The limitation is declared, then the last page converts it into a user-side deployment preference.
- Why it bites: a reviewer who accepts 6.4 will call 7.1 a contradiction; a reviewer who skims 7.1 will think the design isolated disclosure.
- Change: delete the “worth more” sentence. Keep “Whether disclosure repairs that cost is the next experiment”.

**M2. Dataset B cannot support a format-at-onset story, and the Abstract still opens the EEG paragraph with a banner-onset tilt.**
- Location: Abstract: “at banner onset an exploratory slow-power tilt appeared and none after the mention”. §4.4: leave-one-out onset error “0.23 s for banners, 0.43 s for mentions”; Appendix E: “30 of the 36 [implicit] onsets are derived rather than observed”. Table 21: eight confirmatory cells Holm-null, CIs several dB. Table 19: five compositional relatives/absolutes on one explicit-early column. Discussion 6.2: “a visual onset produces a broadband low-frequency transient… Without ICA the *δ* cell keeps its sign but not its significance”.
- Problem: one trial per cell; implicit and explicit onsets are not like-with-like; the five “cells” share a denominator; the confirmatory format contrast at onset does not exist as a planned test (four cells vs *a*∅); the *p*=.08 “direct comparison” is post hoc (Table 22).
- Why it bites: Abstract’s “how” in the EEG is an exploratory, ocular-plausible, ICA-sensitive cluster. Consumer-neuroscience indices “did not move” is an exploratory null promoted to the jacket.
- Change: Abstract EEG = Dataset A timing cell (with depth) + *ρ*=.80 (as candidate) + confirmatory Dataset B null. Move the tilt to one Discussion sentence.

**M3. *ρ*=.80 is sold as the multimodal finding; the twin score, reliability, and item are in the basement.**
- Location: Abstract: “the onset-locked posterior *α* response covaried with the change in reported trust (*ρ* = .80, *n* = 18)”. §5.5: “same pair, Dataset A: *ρ* = .24”; “Split-half reliability of the onset-locked posterior *α* score across early and late halves is .56”; trust is “a single item” (§4.4). §4.5: “pooling them into one twelve-test family changes no verdict.”
- Problem: two EEG scores were evaluated per pair; the authors assert multiplicity would not change the verdict rather than showing the twelve-test Holm table. Abstract drops *ρ*=.24, *r_xx*=.56, and the single-item limit. Neither mean differs from zero (trust −0.38, *p*=.38; *α* −0.33 dB, *p*=.61), so the headline is a rank correlation of residuals around two nulls.
- Why it bites: RQ7 becomes “Supported for trust” (Table 5) on eighteen people, one Likert box, and the less reliable of the two *α* scores.
- Change: Abstract must carry *n*=18, single-item trust, Dataset A *ρ*=.24, and “candidate correlate”. Show the 12-pair Holm line, not only the claim.

**M4. Within-participant order, extra TTFT, incomplete Latin square, and pooled arms are acknowledged and then ignored by the primary estimator.**
- Location: §4.2: advertised-turn retrieval “adds about 3 s”; “it does not cancel against *a*∅ (subsection 6.5)”. §6.5: “the onset-locked pre-onset window, which sits inside the wait”. Appendix C.7: task × condition cells 5 and 17; “Neither the paired *t* … nor the mixed-model check enters task or position as a term.” Table 17: arms pooled; extraversion lab 3.39 vs crowd 2.78, raw *p*=.039 (Table 6). §6.5: “Participants answered the same questionnaire five times and, after the first advertisement, could anticipate…”
- Problem: any-ad behavioural effects and every Dataset B pre-window are advertisement-plus-delay. Task is unbalanced and unmodelled. Arm is a covariate only in the personality model. The “different chatbot” warning is, in the paper’s own words, not a removal of carry-over.
- Why it bites: the cleanest effects (manipulation +1.27, notice +2.07) are exactly the contrasts that do not cancel the 3 s wait and that the repeated battery can inflate after the first ad.
- Change: put arm and task in the LMM that is already the “adjusted check”; report any-ad as a joint ad+latency estimand in Table 4’s caption, not only in 6.5.

**M5. Likert / single-item / *α*=.61 / ceiling: Holm-null trust does not license “trust was intact”.**
- Location: Table 7 credibility means 5.69–6.08 on a 1–7 scale. Table 9 notice Cronbach *α*=.61 on 270 condition rows. §6.1: “the precision of a single integer-valued item whose any-ad interval does not exclude a small drop.”
- Problem: the paper is careful in 6.1 and then Abstract/Conclusion treat the trust Holm-null as the “reassuring half” (6.1) and “counter-intuitively did not fall” (7.1). Notice percentages in the Abstract (69–74% / 39–46%) are the *α*=.61 outcome, not the detection item.
- Why it bites: a one-item trust null at *N*=54 with CI touching −0.71 cannot underwrite a trust-preserving design story; a two-item notice outcome cannot underwrite precise detection rates.
- Change: quote the sponsored-item row of Table 8 in the Abstract; write trust as “interval includes 0 and −0.7 points”, not “did not fall”.

**M6. Taxonomy Contribution 1 is mostly unused by Results.**
- Location: Table 2 / (3.1)–(3.5); Contribution 1. Results §5 never uses *ι*, *α*, *ε*, *σ*, *ϕ*.
- Problem: a page of morphological layers to say the study crossed *λ* with turn and bundled *θ*. Π and *π* do return in 4.3, 6.4, 7.1, 7.2, so they are not abandoned; the four-layer instance is a notation dump.
- Why it bites: short-form space is spent on symbols the analysis never estimates; Contribution 1 looks larger than the experiment.
- Change: one paragraph + the *λ*/*θ* bundle. Move Table 2 to an appendix.

### MINOR

**m1.** Figure 8 (Appendix C) reprints Table 4. Figure 10 reprints Table 11. Body already has the planned-contrast table; the appendix board is a second copy. Figure 14 is only reached via “subsection D.3”, never named in §5. Table 23 / D.3.1 (nine-site montage) is never pointed to from the body.

**m2.** *k*=37 is correctly kept out of the body prose and then printed in Table 20’s caption (“median of the 37 epochs nearest visual onset”) and E.2. The body rule (“standardised to the shortest eligible conversation”) is the right justification; hiding the integer still looks like an RDF until the reader hits p. 40.

**m3.** Cronbach *α* in Table 9 is computed on “270 condition rows” — five repeated measures per person treated as independent.

**m4.** Band edges cited to Cochran et al. 1967 (an FFT tutorial) and a 0.5–40 Hz passband cited to Lopez-Cardona et al. 2026 (a VLM–EEG workshop paper). Wrong authorities.

**m5.** Table 5 “Supported” is defined as “at least one planned contrast … survives Holm”, then applied to RQ7 (a Spearman family) and RQ4–5 (Wald terms).

**m6.** §3.2: “*π* is a deterministic rule … the experiment manipulates that rule’s two visible outputs, *λ* and the turn.” Contribution 1: *λ* is “one dimension of the instance”. Pick one.

**m7.** Exploratory engagement-index nulls in the Abstract (“consumer-neuroscience engagement indices did not move”) are not confirmatory families.

**m8.** Funding and Ethics are “XXXXX” (p. 17). A conference PDF that claims an approved study cannot ship placeholders.

### VERIFY

**V1.** Alphabet $402.8B / $294.7B and Meta $201B / $196.2B (p. 2) — cited to 2026 filings; not checkable from the PDF.

**V2.** “Qwen 3.6 35B-A3B” (§4.2) — unusual identifier; confirm against the platform tag in Troiani, 2026a.

**V3.** Gap sentence: “no study sits at the intersection of LLMs, advertising, and EEG” (§2). On the bibliography given (Zhang 2026a, Kosmyna 2025, Baradari 2025, Subramanian 2026, Tang 2025, Salvi 2026, neuromarketing reviews) the three-way intersection is empty. That is not a proof of the literature.

**V4.** Figure 1 UI pair: present, captioned “as the participant saw them”. Pixels not inspected here.

**V5.** *t*=−2.66, df=17 → two-sided *p*≈.0165, Holm×3≈.0496. Table 20’s *p_raw*=.017 / *p_Holm*=.0496 is internally consistent (rounding).

---

## 3. Top 5 vulnerabilities

1. The title and first abstract sentence collect a trust-and-attention bill that Table 4 (trust Holm-null) and Table 21 (onset-lock confirmatory Holm-null) do not pay.
2. The only confirmatory EEG hit is Dataset A early−late posterior *α* at Holm *p*=.0496, *n*=18, unregistered, and — by the paper’s own Discussion — confounded with conversational depth.
3. Dataset B is one 4 s trial per cell with 2–4 dB intervals; the Abstract’s banner-onset “tilt” is an exploratory, compositional, ICA-sensitive cluster, and implicit onsets are mostly reconstructed (30/36, 0.43 s error).
4. Presentation *λ* is bundled with disclosure *θ*, which the Methods and Table 5 admit, and the Conclusion still tells users that a recognisable advertisement is “worth more”.
5. Any-ad behaviour and every Dataset B pre-window include a ~3 s extra retrieval wait; five repetitions of the same 22-item battery, an unmodelled Latin square (cells 5 vs 17), and a pooled lab/crowd sample sit under every *N*=54 headline.

---

## 4. Three strongest aspects

1. **Analysis contract.** Table 3 plus §4.5 (four status labels; Holm = adjusted *t*; Wilcoxon raw; participant as unit; two EEG estimands; interaction outside Holm; 2,560-map expected-hit check) is more disciplined than most HCI+EEG short papers.
2. **Declared, carried *λ*–*θ* and latency limits.** Equations (3.2)–(3.3), §4.3, §6.5 (TTFT “does not cancel against *a*∅, nor in the onset-locked pre-onset window”), and the write−read Fz *θ* +0.60 dB positive control before any ad contrast.
3. **Post hoc hygiene on the big maps.** 105/2560 raw hits vs 128 expected; Table 18 width-grid cells kept off the 4 s board; estimator disagreement on trust early−late written as “straddle” with three numbers, not a picked winner.

---

## 5. Scores

| Surface | Score |
|---|---|
| Research question / contribution | 7 |
| Design | 6 |
| Statistical validity | 7 |
| Technical correctness | 8 |
| Results / interpretation discipline | 5 |
| Internal consistency | 6 |
| Reproducibility | 6 |
| Writing / short-form craft | 7 |
| **Overall** | **6** |

---

## 6. Reviewer verdict

I would argue **weak reject** in the PC meeting unless the jacket is rewritten before camera-ready: a paper that is this careful in Table 3 and §6.5 cannot open by saying the user pays trust and attention, cannot let Holm *p*=.0496 at *n*=18 answer RQ6 in Table 5 without the depth sentence, and cannot end by telling users that disclosed ads are “worth more” after §6.4 forbade a serving rule. The experiment is real (five-condition within-subjects, crossed format×timing, lab EEG, honest nulls on personality and Dataset B confirmatory). The contribution is a user-side measurement, not a theory of Π. Fix the Abstract, Table 5 evidence column, and §7.1, and I would argue weak accept as a solid empirical note with a heavy appendix. As the PDF stands, the first paragraph of a reject writes itself from the title, the trust Holm-null, and the boundary EEG cell.

---

## 7. Rest of the paper

- **Introduction.** The Alphabet/Meta revenue lead is fine as motivation; “the bill is now being presented to conversational AI” oversells what this *N*=54 session measured. RQ1–RQ7 match Table 5’s *topics*; they do not match Table 5’s *wording* (how→does; overall experience→reported; RQ7→trust only). Align the two tables.
- **Related Work.** The closer (“AI-generated advertisements can now outperform human-created ones… models readily act against the user’s interest”) is a three-citation collage (Meguellati, Tang/Salvi, Wu), not “the state of the field” in one sentence. Keep the narrower gap: no LLM×ad×EEG crossing with format×timing in the same people.
- **Theory.** Keep Π vs *π* and the *λ*/*θ* bundle. Table 2’s unused levels (*ι*, *ϕ* rungs, *σ* modalities) do not earn a body table.
- **Methods (outside 4.5).** §4.2’s retrieval paragraph is longer than the dependent-variable definitions. The 22 items are never listed in the body — only section themes. For a short paper that is acceptable if Appendix C.2/Figure 6 is treated as the item list; say so. Name 37 in one Methods clause (“the shortest eligible window, 37 epochs”) so Table 20 is not the first reveal.
- **Appendices.** A and B are useful (tasks, `pinject`). C.5–C.6 duplicate body claims at table scale; keep the tables, drop Figure 8. D.2’s family-wise paragraph (“98 uncorrected tests… about five false positives… pattern to replicate, not as seven findings”) is the sentence Figure 2 needs in the body. D.3.1 (nine-site) is a dangling sensitivity with no body pointer — cut or point once. E is rebuildable at the level of cuts and measures; it is not rebuildable as a confirmatory reproduction without the tagged repo (visual ICA sign-off, “every automatic exclusion was confirmed by visual review”, no EOG).

---

## Typos and wording

- p. 2: “within everybody’s reach” — prefer “everyone’s”.
- p. 5, (3.2)–(3.3): `aimp` / `aexp` line-breaks as *a*imp₂ across a slash look like two tokens in the text layer.
- p. 11: “74% and 69% … reported the early and late banner **as sponsored**” — those percentages are Table 8’s notice *outcome*, not the sponsored-buttons item.
- p. 16: “did not seem to interact” (Abstract) vs “did not detectably compound” (Conclusion) — hedge then harden.
- p. 17, Acknowledgements: “even if it’s just a bit” — too informal; contraction.
- p. 17: “This work was supported by XXXXX under grant number XXXXX.” / “approved by XXXXX under approval number XXXXX.” — placeholders in the PDF.
- p. 20, Virtanen et al.: “Polat, ˙I.” — broken initial.
- p. 22, A.2: “3d-editing” → “3D editing”.
- p. 22, A.1: “select a single suitable gift at least” — hanging “at least”.
- p. 23, A.4: “and which sport you would like to initiate” — awkward; “which sport to start”.
- p. 25, B.5.1: “matched against that index, write like a catalogue entry” — comma splice; needs “so write” or a period.
- p. 16, Conclusion: “Trust counter-intuitively did not fall” — “counter-intuitively” is a wink, not a result.
- p. 39, D.3.1: “primary-Gold electrodes” — internal pipeline name in a conference appendix.
- p. 46: “˜X ∈ R18×32×Tᵢ” and “*E* ∈ R^{18×*Kᵢ*×32×2000}” — *Kᵢ* as a tensor dimension is not a well-formed shape.
- Figure 3b labels both “Pope *β*/(*α*+*θ*)” and “*β*/(*α*+*θ*)” — the second is presumably Pope FC; say so.
- Figure 2 cell “.05 *” with caption “printed as .05 is .0496” — print .0496 in the cell.
- Keywords line is one jammed clause; fine but hard to scan.
- p. 7: “a yellow panel roughly two message-lines tall” — hyphenate “message-lines” or write “two message lines”.
