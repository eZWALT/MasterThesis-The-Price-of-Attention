# Jury v1 — GPT 5.6 Sol (15 Sep 2026)

Thesis: v1 PDF 156 pp (`docs/overleaf/thesis/_build/dissertation.pdf`).
Prompt: `../2026-09-11-thesis-review-metaprompt.md`.
In-IDE / extra dump (not one of the five web juries). Raw examiner
dump. Do not treat its table cells as Gold. Do not apply until
Walter says so.

---

External examiner review: The Price of Attention

Evidence base: dissertation.pdf only · complete cover-to-appendix read · 156 PDF pages · no code or data inspected

Examiner position. Substantive and potentially passable only after major correction. The strongest empirical behavioural effects are credible as contrasts between two bundled implementations; the present PDF overstates what “format,” timing, EEG, moderation, and policy conclusions identify. Human-subject governance must be documented immediately.

Critical findings: 1

Major findings: 19

Overall as submitted: 4.9/10

---

# Job 1 · Cross-document consistency audit

“PASS” means the Methods contract, Results ledger, and downstream claim agree. It does not mean the method is substantively adequate; those judgements are in Job 2.

## Declared families and headline checks

| Family | Methods: n / tests / estimator / correction | Results: count / headline | Discussion + Abstract/Conclusion | Audit |
|---|---|---|---|---|
| Behavioural battery | n=54; 16 tests; one-sample t on person-level D; raw Wilcoxon sensitivity; random-intercept LMM; Holm within each outcome. | 16 tests, 8 Holm cells. Key: notice any-ad − no-ad +2.07 [1.53, 2.62], pHolm<.001. | Core counts and estimates agree. The separately claimed format×timing interaction is not in this ledger. | PARTIAL |
| Behavioural format×timing | RQ5 exists, but Table 6.1 lists only three contrasts per primary outcome and gives no interaction estimator or correction. | §7.2 says all four are null, \|dz\|≤.06; no estimate, CI, p, or row in Tables 7.8–7.9. | Abstract, §8.1, Table 8.1, and Conclusion treat the null as established. | FAIL |
| Personality moderation | n=54; LMM; 15 trait×contrast terms within each of four outcomes (60); demographics said to be covariates. | 60 tests, 0 Holm; nearest cell pHolm=.18. | Discussion is bounded; Abstract says no moderation of “any outcome.” The covariate claim conflicts with n=54 despite missing demographics. | PARTIAL |
| Demographic moderation | No row in Table 6.1. | Table 7.9 calls 70+70 tests a check “not [a family] in Table 6.1”; 0 survive. Sex n=51, education n=49, others n=54. | Abstract and Conclusion promote the result; age was not tested. | FAIL |
| Free text/open reaction | n=54; collected, not analysed; no correction. | Not analysed. | Consistently excluded from claims. | PASS |
| Dataset A: condition aggregation | n=18; 3 contrasts per measure; t(Dᴬ), raw Wilcoxon; Holm separately within each measure. | 6 confirmatory cells, 1 Holm: early−late posterior α −0.22 dB [−0.39, −0.04], pHolm=.0496. | Number agrees, but downstream text repeatedly calls the nearest-37-epoch cell a whole-condition average. | PARTIAL |
| Dataset A interaction | Eq. 6.2 declares weights (1,−1,−1,1,0) for a presentation×timing interaction. | Absent from Figure 7.7, Figure 7.8, Tables 7.8–7.9, Discussion, and Conclusion. | No scale misuse can be checked because the estimate is never reported. | FAIL |
| Dataset B: onset-lock | n=18; 4 cell-vs-matched-control contrasts per measure; t(Dᴮ), raw Wilcoxon; Holm within measure. | 8 confirmatory cells, 0 Holm. Nearest: implicit-late Fz θ −1.38 dB [−2.80, .04], pHolm=.22. | The null is usually bounded by wide CIs; onset and latency comparability remain unresolved. | PASS / METHOD LIMIT |
| Writing−reading positive control | n=18; 2 confirmatory markers; t, raw Wilcoxon; Holm across two. | 2 tests, 1 Holm: Fz θ +0.60 dB [0.22, 0.97], pHolm=.007. | Consistent, though it validates sensitivity to a writing/reading state change, not advertisement specificity. | PASS |
| Fourteen exploratory EEG measures | n=18; 14×(3 Dataset A + 4 Dataset B)=98; Holm within each measure. | 98 tests, 7 Holm cells; key relative δ explicit-early +.19 [.09,.29], pHolm=.004. | Abstract and Conclusion promote the explicit-early cluster without saying exploratory and omit that α/β changes are relative. | FAIL (CLAIM) |
| EEG exhaustive pairwise | n=18; 10 A + 6 B pairs per 16 measures=256; post hoc; Holm within measure. | 256 tests, 1 Holm: A Fz θ implicit-early−explicit-late −0.28 dB, pHolm=.014. | Consistently labelled post hoc and not used as a primary finding. | PASS |
| Trajectory δ₂⁽ᵃ⁾ | n=54; 4 contrasts; exact McNemar for binary pairs plus paired-t interval; Holm family of four. | 4 tests, 0; pooled +.046 [−.082,.174], pHolm=.94; separate raw McNemar p values. | Numbers agree, but the prose makes the exact McNemar sound primary while the Holm verdict is the paired t. | PARTIAL |
| Late Nshift | n=54; 3 paired-t contrasts, raw Wilcoxon; Holm across three. | 3 tests, 0; pooled −.074 [−.361,.213], pHolm=1.00. | Ledger agrees. It is later used to answer a timing RQ despite being entirely pre-exposure. | PASS / CLAIM FAIL |
| Genre-aligned δ̃₂⁽ᵃ⁾ | n=54; one one-sided, 20,000-draw conversation-level permutation; uncorrected. | 1 test, 0; 9 observed vs 10.46 expected, p=.80. | Consistent; global permutation does not preserve participant/task structure. | PARTIAL |
| Turn-1 vs turn-4 instrument check | n=54; 6 genre-share paired t tests, raw Wilcoxon; Holm across six. | 6 tests, 4 Holm; guidance .478→.211, dz=−1.00, pHolm<.001. | Consistently called an instrument/depth check, not an ad effect. | PASS |
| Behaviour×EEG | n=18; six pairs on each of Dᴬ and Dᴮ (12 cells); Holm within each six and promised across all 12. | Table 7.8 says “Tests 6; Sig. 0;1”; only pHolm=.0004 “within six” is reported for trust×onset posterior α. | The across-12 value is missing; Abstract/Conclusion call it a candidate marker/finding. | FAIL |
| Behaviour×trajectory | n=54; 6 Spearman pairs; Holm within six. | 6 tests, 0; largest ρ=.22 [−.05,.46], pHolm=.67. | Consistent. | PASS |
| Trajectory×EEG | n=18; 2 Spearman pairs; Holm within two. | 2 tests, 0; Fz θ×δ₂⁽ᵃ⁾ ρ=.47 [−.02,.78], pHolm=.095. | Consistent and sensitivity reversal disclosed. | PASS |
| Behaviour×trajectory×EEG | n=18; three pairwise Spearman associations; each also partialled on the third; Holm family of three. | Not reported in §7.6 body. Table 7.8 says 3 tests, 0 significant, yet gives partial trust×posterior α ρ=.80. | The p/CI are absent; with n=18, ρ=.80 is not facially compatible with “Sig. 0” unless another unreported procedure was used. | FAIL / VERIFY |

## Sensitivity, post-hoc, and exploratory checks

| Check | Contract | Results | Downstream use | Audit |
|---|---|---|---|---|
| Behavioural localisation | n=54; 16 post-hoc condition-vs-control t tests; Holm within outcome. | 9 Holm; trust explicit-early −.69 [−1.17,−.20], pHolm=.031. | Labelled post hoc in Results; promoted without that label in Abstract/Conclusion. The same trust pair is pHolm=.078 in the full ten-pair family. | PARTIAL |
| Behavioural Friedman | Post hoc; 8 rank omnibus tests; raw p. | 6/8 raw p<.05; no Holm count claimed. | Consistent. | PASS |
| Behavioural ten-pair sweep | 80 post-hoc paired t tests; Holm within outcome; raw Wilcoxon. | 13 Holm, 12 on manipulation/notice. | Clearly separated. | PASS |
| Estimator concordance | 16 planned contrasts under t, LMM, and raw Wilcoxon. | One t/LMM verdict disagreement: trust early−late (.063 vs .048); Wilcoxon .026. | Reported honestly in Results and Discussion. | PASS |
| Item leave-one-out | 45 sensitivity cells. | Credibility timing loses significance without reliable-response item (pHolm=.159). | Disclosed; primary score retained. | PASS |
| Logged interaction measures | 9 measures×3 contrasts+interaction=36 exploratory. | 0 raw p<.05. | Does not test the 4-s EEG pre-window latency confound. | PASS / IRRELEVANT TO CONFOUND |
| Epoch width and cleaning | 126 sensitivity cells (summary only). | Two off-4-s confirmatory cells; 4-s family does not hold at other widths. | Not harvested; no complete no-ICA estimates are printed. | PARTIAL |
| Deployed-context δ₂⁽ᵃ⁾ | n=54; 4 sensitivity contrasts. | 0; pooled −.019 [−.137,.100], pHolm=1.00. | Consistent. | PASS |
| Clustered logistic/bootstrap | GEE/task/position adjustment and bootstrap check of δ₂⁽ᵃ⁾. | One headline: OR 1.31, p=.51; bootstrap interval [−.074,.176]. | Consistent, but model specification is incomplete. | PARTIAL |
| Whole-conversation Nshift/H/R | Exploratory Kruskal–Wallis on 270 conversations. | 12 tests, 0; ICC .043–.111. | Declared, but contradicts the participant-as-unit rule; low ICC does not restore independence. | FAIL (METHOD) |
| Fallback-by-turn | Participant-clustered logistic checks. | 2 tests, 2; turn β=.34, p=.0003; log(words) β=−.29, p=.0007. | Consistent and used as an instrument diagnosis. | PASS |
| Trust against all 16 EEG measures | Exploratory screen; n=18; Holm within 16. | 2 cells: onset posterior α ρ=.80, pHolm=.001; absolute α ρ=.69, pHolm=.025. | Clearly separated from declared pairs. | PASS |
| Other behaviour×EEG contrasts | 24 cells over format/timing and two EEG scores. | 0; smallest raw p=.12. | Consistent. | PASS |
| Deployed-context trajectory pairs | 8 sensitivity associations. | 0; Fz θ×δ reverses to −.46. | Consistent and appropriately weakens the nominal lean. | PASS |
| Exploratory association map | 2,560 tests in 21 families; Holm within family. | 105 raw hits vs 128 expected; 0 Holm. | Clearly separated and not mined into a finding. | PASS |
| Joined models | 336 tests; family permutation. | 10 raw hits vs 17 expected; 0 Holm; permutation p≥.23. | Consistent. | PASS |
| Split-half reliability | Descriptive reliability check; no test count. | Posterior α A=.78; onset α=.56; Fz θ difference not detectable. | Used to bound interpretation, though trust reliability remains weak. | PASS |

## Every cross-document disagreement found

**1. The RQ5 interaction has no auditable result**

Location A. Methods, Table 6.1 (p.60): “3 planned contrasts within each of the four primary outcomes.”

Location B. Results §7.2.1 (p.65): “Format × timing is null on all four outcomes (|dz| ≤ 0.06).” Abstract (p.iii): “Presentation and timing did not interact.”

Finding. Four interaction tests appear in no family, table, CI, or p-value ledger. Add four estimates with coding, CIs, estimator, and correction status, or withdraw the null claim.

**2. A declared EEG interaction disappears**

Location A. Methods Eq. 6.2 (p.61): “(1, −1, −1, 1, 0) [is] the presentation-by-timing interaction.”

Location B. Results Table 7.8 (p.78): Dataset A reports “Tests 6,” exactly 2 measures×3 contrasts; Figures 7.7–7.8 show only any-ad, format, and timing.

Finding. The coded interaction is neither corrected nor reported. Its raw scale is therefore never misread, but only because it is absent.

**3. The declared trajectory estimator changes at reporting**

Location A. Methods Table 6.1 and §6.3 (pp.60–62): “exact McNemar; paired t interval” and “the test is an exact McNemar test.”

Location B. Results Table 7.5 (p.74): “Holm-adjusted paired t; McNemar for the two-condition rows”; Table 8.1 uses the paired-t Holm value .91 rather than McNemar p=.36.

Finding. Both verdicts are null, but the primary estimator changed. Name and multiplicity-adjust one primary test per contrast.

**4. Demographics is promoted from an undeclared check**

Location A. Results Table 7.9 caption (p.79): “Sensitivity and exploratory checks that are not families in Table 6.1”; row: “Demographic moderation … 70 + 70.”

Location B. Abstract (p.iii): “neither personality nor demographics moderated any outcome.” Conclusion (p.96): “none of the five recorded background factors … moderated them.”

Finding. The analysis-families table has no demographic row; age was not tested. Call this exploratory and scope the claim to the five tested factors.

**5. The demographic summary n is not the analysis n for every cell**

Location A. Results §7.3 (p.68): “the sex model holds n=51 and the education model n=49 … the other three all 54.”

Location B. Results Table 7.9 (p.79): “Demographic moderation … n 54 … 70 + 70.”

Finding. If n means inferential units, the row must show the varying n or split the factors.

**6. The personality model cannot both adjust for missing demographics and use all 54**

Location A. Methods Table 6.1 (p.60): personality LMM has “demographics as covariates.”

Location B. Appendix Table E.9 (p.134): “N = 54”; Results §7.3 (p.68): sex models have n=51 and education n=49 because of missing values.

Finding. State the actual covariates and missing-data handling. If demographics were not covariates, correct Table 6.1.

**7. Behaviour×EEG is 12 evaluated cells but the summary says six**

Location A. Methods §6.3 (p.59): “each behaviour × EEG pair is evaluated on both, Holm within the six for each score, and a cell that survives is also reported Holm-corrected across the twelve.”

Location B. Results Table 7.8 (p.78): “Behaviour × EEG … Tests 6 … 0; 1”; Figure 7.13 says p=.0004 “within six.”

Finding. Report 12 cells and the promised across-12 adjusted p. The strong cell likely remains small, but the contract is not met.

**8. The three-way association row is internally unresolved**

Location A. Methods Table 6.1 (p.60): “each pair also partialled on the third,” with three pairwise associations.

Location B. Results Table 7.8 (p.78): “Sig. 0” but “trust × posterior α given δ₂⁽ᵃ⁾, partial ρ=.80.”

Finding. No p or CI is reported and §7.6 does not present this family. Discussion p.88 additionally says partialling leaves values “at .80 and .83,” while Table 7.8 labels .80 as the partial value. Recompute/report the three partial tests and explain the zero count.

**9. “Holm p” does not have one estimator**

Location A. Methods §6.3 (p.59): “Holm is applied only to those t tests.”

Location B. Results §7.6 (p.75): “a Holm p here is a Holm-adjusted Spearman p.” Appendix E.5 (p.133): “Holm is Wald on the trait × contrast term.”

Finding. Wilcoxon is consistently raw and “Wilcoxon Holm” never appears. The remaining label is still ambiguous: write pHolm(t), pHolm(Spearman), and pHolm(Wald).

**10. Condition aggregation is not a whole-condition average**

Location A. Datasets Eq. 4.10 (p.36): Yᴬ is the median over “the 37 retained epochs whose midpoints lie nearest that condition’s visual onset.”

Location B. Methods §6.3 (p.61): “a participant’s sustained state over a whole condition”; Discussion §8.3 (p.83): “Averaged over the whole conversation.”

Finding. Thirty-seven 4-s epochs are a 148-s onset-neighbourhood subset, not the whole 2.5–16.8 min conversation. Rename the estimand everywhere.

**11. Exploratory EEG is promoted and the bands are misstated**

Location A. Methods §6.2.2 (p.52): “The other fourteen are exploratory … and no claim rests on them.” Results Figure 7.8 shows absolute α and β Holm-null; relative α and β are the cells that fall.

Location B. Abstract (p.iii): “a transient slow-power tilt (↑ δ, θ; ↓ α, β) was observed, with no comparable response at mention onset.” Conclusion (p.97) repeats the shorthand.

Finding. Say exploratory; specify absolute δ/θ and relative δ/α/β; and retain the direct format comparison, whose smallest adjusted p is .08.

**12. The Conclusion reverses the stated no-policy boundary**

Location A. Discussion §8.6 (p.90): “This is not a recommendation to serve advertisements late or implicitly.”

Location B. Conclusion §9.1 (p.98): “an obligation to disclose, to be patient with monetisation rather than rush into the earliest turns simply because they command attention.”

Finding. Delete the deployment rule. The study measures no advertiser objective and does not manipulate disclosure independently.

**13. The Conclusion singles out a combination after declaring no interaction**

Location A. Discussion §8.1 (p.81): “the design singles out no combination of the two.”

Location B. Conclusion §9.1 (p.98): “It concentrates on the explicit banner arriving early.”

Finding. An explicit-early post-hoc cell is not evidence of interaction or concentration. State additive format/timing patterns and label localisation post hoc.

**14. Disclosure is prescribed despite being unidentifiable**

Location A. Methods §6.2.5 (p.57): “The design therefore cannot apportion any memory advantage … between the presentation itself, the disclosure label, and the mere availability of a separable object.”

Location B. Conclusion §9.1 (p.96): “The prescription is about disclosure rather than placement.”

Finding. This is the opposite of what the design supports. Recast as an ethical consideration or test disclosure factorially.

**15. RQ2 is narrowed to one early local genre contrast**

Location A. Introduction RQ2 (p.3): “Does advertisement presentation format alter the trajectory of the conversation following the advertisement?”

Location B. Table 8.1 (p.92): “Does format shift the conversation’s genre?” Evidence is only “implicit − explicit early δ₂⁽ᵃ⁾ +0.093, Holm p=.91.”

Finding. This does not answer format effects after late ads or the broader trajectory. Mark RQ2 partially operationalised, not simply unsupported.

**16. RQ4 compares different outcomes rather than timing**

Location A. Introduction RQ4 (p.3): “Does the moment of advertisement insertion alter the trajectory of the conversation following the advertisement?”

Location B. Table 8.1 (p.92): early uses local δ₂⁽ᵃ⁾; late uses whole-conversation Nshift.

Finding. The late Nshift is measured before the terminal ad and cannot be compared with a post-ad early shift. RQ4 is not answered in the terms asked.

**17. New numbers first appear in Discussion**

Location A. Results Figure 7.8 (p.71) prints adjusted p values; Table 7.8 gives relative δ +.19 as the representative explicit-early estimate.

Location B. Discussion §8.3 (p.84) first gives “absolute δ rises by 4.60 dB”; §8.1 first gives trust “participant ICC .39”; §8.5 first gives Dataset-A raw p=.34 and partial ρ=.83.

Finding. Move each number into Results/a results table or remove it from Discussion.

**18. Some Abstract/Conclusion numbers do not trace to a Results cell**

Location A. Abstract (p.iii): “more than half of those who initially failed to notice the mention recognised it when shown again.” Conclusion (p.96) repeats “most.”

Location B. Results §7.2.2 states this in prose but supplies no notice×memory contingency table. Conclusion’s “98 of the 156 served products” is likewise Results prose, not a table cell.

Finding. Add the underlying contingency counts and advertised-genre count to Results tables, including the operational thresholds.

**19. The summary’s completeness claim is false**

Location A. Results §7.7 (p.78): “nothing in this chapter is omitted from the tables.”

Location B. The behavioural interactions, the Dataset-A interaction, and the body results/p values for the three-way partial family are absent.

Finding. Close the ledger before using Tables 7.8–7.9 as the thesis-wide contract.

**20. The unqualified EEG headline drops the depth limitation**

Location A. Discussion §8.3 (p.84): “timing under condition aggregation is confounded with conversational depth.”

Location B. Abstract (p.iii): “posterior α power was lower for early than for late insertion.”

Finding. The abstract must add the depth qualification, especially because the timing-matched onset analysis is null.

**21. The moderation headline exceeds its tested scope**

Location A. Results §7.3 (p.68): “Age was incomplete … and was therefore not tested”; personality tests cover four primary outcomes and demographics add cued memory.

Location B. Abstract (p.iii): “neither personality nor demographics moderated any outcome.”

Finding. Use “No moderation was detected for the tested traits, factors, contrasts, and outcomes.”

## Consistency checks that passed

Wilcoxon p is consistently raw; “Wilcoxon Holm” does not appear. Dataset A is consistently called condition aggregation; no Path A/B, equal-n neighbourhood, or condition-state label was found. The fgenre symbol itself is consistent, although its formal input domain is not. There is no RQ10/RQ11, and task moderation is not presented as an RQ. The coded interaction is not silently interpreted as a normalised magnitude; it is simply not reported.

---

# Job 2 · Requested methodological surfaces

| Surface | Status | Examiner assessment |
|---|---|---|
| Order/carry-over | PARTIAL | Random order and the different-chatbot warning are described; §8.7 admits five repeated ad-focused questionnaires create anticipation. No period, predecessor, or carry-over sensitivity is reported. |
| Behavioural early-vs-late estimand | NOT ADDRESSED | Early ads remain available for two later turns and longer exposure; late ads are terminal and immediately precede the findings/rating phase. Timing therefore bundles depth, exposure duration, intervening interaction, and rating delay. |
| Latin-square task rotation | PARTIAL | Independent random pairing is unbiased in expectation, not exact balance at N=54. The realised 5×5 task×condition table is absent; task is adjusted only in a trajectory GEE, not behavioural or EEG analyses. |
| Pooling lab and crowd | PARTIAL | Within-person contrasts remove arm level shifts, but arm may modify effects. “Environment” is an underpowered exploratory moderator; the primary pooled family has no arm factor or arm-stratified sensitivity. |
| ~3-s retrieval wait | NOT ADDRESSED | The system chapter identifies the only server-side ad/no-ad difference. It is not carried into behavioural limitations or the Dataset-B pre-window interpretation. |
| Dataset-B format comparability | PARTIAL | Onset reconstruction error and qualitative event differences are disclosed. Implicit begins during streaming; explicit is painted after the reply, so pre/post windows do not isolate a common perceptual event. |
| Dataset-B filter-boundary leakage | NOT ADDRESSED | The PDF gives only a 0.5–40 Hz band-pass, not filter type, phase, order/length, or transition bands. With adjacent pre/post windows, zero-phase low-frequency filtering could smear post-onset energy into the pre-window. |
| Disclosure θ vs presentation λ | PARTIAL | The confound is stated clearly in Methods and Limitations, then contradicted by the disclosure prescription in Conclusion. |
| “Confirmatory” without preregistration | PARTIAL | Recruitment-set n and internal before-reading choices are disclosed. There is no external timestamp/hash, and the same analyst chose measures, k=37, and width; “planned, not preregistered” is the defensible label. |
| Likert/t/single trust/ceilings/notice α | PARTIAL | Person-level contrasts, bootstrap, Wilcoxon, LMM, ceiling, and reliability are discussed. Trust-null prose slips into similarity/equivalence; α over 270 repeated rows mixes covariance levels; BFI-10 two-item reliability is absent; and notice is not a common detector across formats. |
| Trust estimator disagreement | ADEQUATE | The .063/.048/.026 disagreement is stated in Results, Discussion, Appendix E, and not silently resolved in favour of one estimator. |
| Post-hoc localisation/sweep | PARTIAL | Results labels both layers correctly; the early-banner trust cell is nevertheless promoted in Abstract/Conclusion without the post-hoc qualifier. |
| Brand mention under no-ad | ADEQUATE | The thesis repeatedly says brand mention is not detection. The remaining problem is that the sponsored-button item is structurally format-specific. |
| Zero clicks | ADEQUATE | Zero clicks is stated and no click/conversion effectiveness is claimed. |
| Personality/demographic multiplicity | PARTIAL | Raw cells are not cherry-picked and limitations acknowledge interaction power. Abstract overgeneralises, age is untested, BFI-10 trait reliability is absent, and demographics is undeclared in Table 6.1. |
| A posterior α p=.0496/depth | PARTIAL | Depth is explicitly acknowledged. The abstract omits it; the result is boundary-level, width-fragile, and depends on separate-by-measure family construction. |
| Dataset-B wide nulls | ADEQUATE | The Discussion says failure to reject is not absence and prints 2–4 dB precision. No observed power/MDE is needed. |
| Explicit-early slow-power cluster | PARTIAL | It is correctly treated as one event and onset/ocular accounts precede cognitive claims in §8.3. The no-ICA argument is not decisive without EOG, and headline sections promote it. |
| Holm within 16 measures | INADEQUATE | The family choice is stated, but dependence is incorrectly used as a reason not to correct across measures even though the thesis correctly says Holm permits arbitrary dependence. |
| Epoch-width sensitivity | ADEQUATE | Off-4-s cells remain sensitivity and are not substituted for primary estimates. The 4-s A result’s lack of width robustness should still enter the abstract-level caveat. |
| k=37/whole-window leakage | PARTIAL | k=37 is tied to the shortest eligible conversation and said to precede testing; whole-window medians are said not to be tested. Later prose wrongly calls the k=37 subset a whole-condition state. |
| Precision rather than post-hoc power | ADEQUATE | CIs expose the wide n=18 uncertainty. There is no reason to demand observed power. |
| Classifier validity | PARTIAL | Own-domain 83.8% accuracy is not target-domain validation; no human labels exist for these shopping utterances/product titles. The thesis ultimately diagnoses instrument failure rather than treating the classifier as ground truth. |
| Bare/context windows | PARTIAL | Saturation and floor are clearly shown, and a six-window Holm sweep is useful. It demonstrates robustness of the null to these recipes, not validity of any recipe. |
| Undefined δ₄⁽ᵃ⁾/late “control” | INADEQUATE | Undefinedness is consistent, but late Nshift is entirely pre-ad and hence a leakage/randomisation check, not evidence about a late advertisement or a fair timing comparison. |
| Genre permutation | PARTIAL | The conversation-level exception is declared. Global reassignment breaks two-conversation participant pairing and task-conditioned product genres. |
| Kruskal–Wallis on 270 rows | INADEQUATE | Exploratory labelling and low ICC reduce consequence, not pseudoreplication. A clustered permutation or participant-level model is required. |
| Weak advertised-genre target | ADEQUATE | The 98/156 guidance concentration and 25/108 already-in-genre cases are admitted before interpretation. |
| Trajectory null vs theory | PARTIAL | Discussion correctly calls it instrument failure, not falsification. Table 8.1 and Conclusion still answer RQ2/RQ4 too categorically. |
| Trust×onset posterior α | PARTIAL | n=18, CI, leave-one-out, null means, single-item trust, and split-half .56 are disclosed. Across-12 Holm is absent, A-vs-B correlations are not directly compared, and both change scores reuse the same no-ad state, which is not decomposed. |
| 2,560-test map | ADEQUATE | It is visibly separated, chance-calibrated, and no cell is mined into a main finding. |
| Association vs mediation/direction | PARTIAL | Methods and Discussion are disciplined and give bidirectional/common-cause examples. Abstract/Conclusion drift to “marker,” “withdrew trust,” and individual sensitivity. |
| Definitions 1–6 | PARTIAL | The inequality δ̃≤δ⁽ᵃ⁾≤δ and k/i indexing are sound. A=(a₁,…,aT−1) cannot contain the study’s terminal a₄ when T=4; persistence is ambiguous when a genre has several runs. |
| D, Dᴬ/Dᴮ, t, dz | PARTIAL | The person-level contrast, t, and dz formulas are correct. Dᴬ is later misdescribed; Dᴮ suppresses the timing index; declared interaction weights are not reported. |
| KV-cache arithmetic | ADEQUATE | 16,384×10×2 heads×2(K,V)×256×2 bytes=335,544,320 bytes=320 MiB. |
| Table/figure column contracts | PARTIAL | Most captions define estimators and raw/adjusted p correctly. Table 7.8’s “0;1” and six-test behaviour×EEG row, n=54 demographic row, and three-way zero count do not. |
| PDF-only reproducibility | INADEQUATE | Many thresholds, instruments, file grains, exclusions, and package versions are strong. Exact random/ICA/permutation seeds, component exclusions, realised allocations, full model formulae, release DOI/manifest, and consent basis for open data are missing. |

Precision judgement. The thesis is right not to report observed power or post-hoc MDE. The CIs are the appropriate evidence. The problem is interpretive: several nulls are written as stability or no moderation even when the intervals and measurement reliability do not support equivalence.

---

# Findings by severity

## CRITICAL (1)

**C1. Human-subject governance and the delivered debrief are not defensible from the PDF**

Location: Methods §6.2.3–6.2.4; Abstract; Appendix C.1 and C.6

Quote: “The laboratory recording is not named in this text either”; “These products and brands were selected randomly”; “here is what we instructed ChatGPT to do”; “the … multimodal datasets are released openly.”

Problem. No ethics committee/IRB authority or protocol identifier is reported. The reproduced consent does not name EEG or open release. The debrief says products were random although §5.3 serves the top semantic retrieval result, and says ChatGPT although §5.2 used Qwen and Appendix B prints a different prompt.

Why it matters here. This is an EEG study using deception and potentially identifying chat text. An inaccurate debrief and undocumented consent/approval basis are governance failures, not prose defects.

Change/check. Before submission, add the approving body, protocol/decision number, approval date and scope; identify/reproduce the separate EEG and data-sharing consent if it exists; correct the actual participant debrief; state what data can legally and ethically be released. If these records do not exist, stop the open-data claim and escalate to the supervisors.

## MAJOR (19)

**M1. The “format” treatment is a bundle, not presentation λ**

Location: Theory §3.2; Methods §6.2.1; Appendix B.3

Quote: “σ is text … The two advertisements differ only in the surface pair (λ, θ)” versus the explicit banner’s “product image … call to action,” while the implicit condition rewrites the assistant reply through a product-injection prompt.

Problem. Format co-varies with disclosure, image/modal content, UI separability, CTA, and whether the assistant’s answer itself is commercially altered.

Why it matters here. The notice, manipulation, memory, trust, and EEG differences cannot be attributed specifically to presentation λ.

Change/check. Rename the estimand as the contrast between two bundled implementations. To identify presentation, cross disclosure and modality and hold product/text/reply content constant.

**M2. Behavioural timing is exposure regime, not insertion time alone**

Location: Methods §6.2.1 and §6.2.4; Results/Discussion timing claims

Quote: Late insertion is “the final turn … immediately before the written conclusion”; an early advertisement remains available “for the rest of the session.”

Problem. Early conditions include two post-ad turns, longer exposure, and a different delay to rating; late conditions include no post-ad interaction.

Why it matters here. The −0.33 credibility, +0.58 manipulation, and re-exposure trust differences cannot be attributed solely to the insertion moment.

Change/check. Call the contrast early sustained exposure versus terminal exposure. A clean timing study needs equal post-ad turns and outcomes collected at a fixed delay.

**M3. The retrieval wait contaminates treatment and the Dataset-B baseline**

Location: System §5.1.2; EEG Eq. 4.11; Discussion/Limitations

Quote: “retrieval runs before the first token (median 3.03 s) … the only ads-versus-no-ads difference in server wait”; Epre=[t−4,t).

Problem. Advertised pre-onset windows contain roughly three extra seconds of silent waiting. The matched no-ad pre-window does not. Behavioural any-ad effects also include this co-intervention, but the limitation is not carried forward.

Why it matters here. A post−pre difference can change because the pre state differs, even if the visual event has no effect. This directly threatens every Dataset-B cell.

Change/check. Show pre and post levels separately, align matched controls to submission/TTFT states, adjust or stratify by TTFT, and state that current contrasts estimate ad implementation plus latency.

**M4. Implicit and explicit onset windows do not compare like with like**

Location: EEG §4.2.4; Methods §6.2.1; Discussion §8.3

Quote: Implicit onset is “injected during streaming” and 30/36 are reconstructed (p95 error .43 s); the explicit banner is painted “0.49 s after the reply is on screen.”

Problem. One post-window includes a still-streaming answer and uncertain product-token onset; the other begins after a new, separate object is painted over an already displayed reply.

Why it matters here. A format contrast mixes visual transient, reading phase, streaming, onset error, and content integration.

Change/check. Log client-side first-pixel/first-product-token events, use the same reply phase for both formats, add eye tracking/EOG, and treat current format comparisons as implementation-specific.

**M5. The correction strategy fragments co-primary and exploratory EEG outcomes**

Location: Methods §6.3; Appendix D.2; Abstract

Quote: “Each measure is its own Holm family”; Holm “assumes nothing about how the tests … depend”; later, correcting across measures is rejected because relative powers “share a denominator.”

Problem. Dependence does not invalidate Holm. Sixteen separate .05 families provide no family-wise guarantee across the EEG board; the boundary p=.0496 and seven exploratory cells depend on that choice.

Why it matters here. The abstract turns within-measure exploratory hits into a neural finding despite a large analysis surface and no preregistration.

Change/check. Define co-primary markers as one six/eight-cell family or report both corrections; use a predeclared multivariate/compositional exploratory test; label all surviving non-primary cells exploratory in headline sections.

**M6. “Confirmatory” has no external time stamp**

Location: Methods opening and §6.3

Quote: “pre-specified analysis plan”; measures and weights were fixed “before the corresponding result was read”; sample size “set by recruitment.”

Problem. No preregistration, dated analysis plan, repository hash, or independent freeze is supplied. The analyst also chose markers, k=37, window width, families, and exclusions.

Why it matters here. The distinction remains useful for disclosure but cannot carry the evidential weight of prospective confirmation.

Change/check. Use “planned, not preregistered”; give a dated immutable record if one exists; reserve confirmatory claims for a replication.

**M7. The slow-power headline is stronger and less precise than the actual result**

Location: Figure 7.8; Abstract; Discussion §8.3; Conclusion

Quote: Abstract: “↑ δ, θ; ↓ α, β … no comparable response at mention onset.” Discussion: “the direct implicit-minus-explicit comparison at onset does not survive correction.”

Problem. Only absolute δ/θ and relative δ/α/β move; absolute α/β do not. The cluster is exploratory, one 4-s post/pre observation per cell, and no direct format difference survives.

Why it matters here. Significance versus non-significance is not a significant difference, and one broad 4-s contrast cannot establish a transient time course.

Change/check. Use the exact five measures, call it one exploratory explicit-early-vs-control pattern, delete “no comparable response,” and prioritise onset/ocular explanations.

**M8. The sole confirmatory EEG finding is a depth-confounded, width-fragile boundary result**

Location: Results §7.4; Discussion §8.3; Appendix D.1; Abstract

Quote: “early − late posterior α −0.22 dB … Holm p=.0496”; “timing … is confounded with conversational depth”; “the 4 s family does not hold at other widths.”

Problem. The result does not separate ad timing from turn depth, message shortening, and generic genre drift. The timing-matched onset analysis is null. Appendix D.2 also says Dataset-A confirmatory differences run only “to about a tenth of a decibel,” inconsistent with −0.22 dB.

Why it matters here. The abstract presents it as an advertisement timing response when the thesis itself says attribution is inseparable.

Change/check. Qualify the abstract; report a depth-matched/no-ad difference-in-differences if possible; frame this as a fragile timing-position association needing replication.

**M9. The onset-specific trust claim is not tested as onset-specific**

Location: Results §7.6.1; Discussion §8.5; Abstract/Conclusion

Quote: Dataset B ρ=.80, Dataset A ρ=.24; Discussion: the relationship is “concentrated at the moment” and Abstract calls a “candidate neural marker.”

Problem. The two dependent correlations are never directly compared. The promised across-12 Holm value is absent. Both any-ad difference scores reuse a common no-ad component, which can induce change-score covariance; their ad and no-ad components are never examined separately. Trust is a single item and onset α split-half reliability is .56.

Why it matters here. One significant and one non-significant correlation do not prove that the correlations differ; same-sample marker language also implies validation that did not occur.

Change/check. Bootstrap/permute the paired difference ρB−ρA, report across-12 adjustment, inspect ad/no-ad components or a repeated condition-level model, and call the result a bounded prereplication association.

**M10. The analysis ledger is not closed**

Location: Table 6.1; Eq. 6.2; Tables 7.8–7.9; Table 8.1

Quote: Results claims “nothing … is omitted,” yet behavioural interactions, the EEG interaction, demographic family status, 12-vs-6 behaviour×EEG cells, and three-way partial p values are unresolved.

Problem. n, test counts, estimators, and correction families do not map one-to-one across the four required documents.

Why it matters here. A reader cannot reconstruct the inferential universe or verify headline nulls.

Change/check. Create one authoritative ledger with every family/check, exact n per test, estimator, sidedness, correction set, estimate/CI/p, and downstream claim.

**M11. The Conclusion contradicts the Discussion’s inferential limits**

Location: Discussion §8.1 and §8.6; Conclusion §9.1

Quote: “not a recommendation to serve advertisements late or implicitly” and “the design singles out no combination” versus “be patient … rather than rush into the earliest turns” and “concentrates on the explicit banner arriving early.”

Problem. A post-hoc cell is converted into an interaction/concentration claim and then into a serving rule.

Why it matters here. The study has no advertiser objective, no significant behavioural interaction, and no independently manipulated disclosure.

Change/check. Delete the serving prescription and combination claim. Keep the user-side measurements and ethical disclosure concern.

**M12. Failure to reject trust differences is repeatedly treated as stability**

Location: Table 7.2; Discussion §8.1; Conclusion §9.1

Quote: Any-ad−no-ad trust −.34 [−.71,.03], pHolm=.153; “Trust holds up”; participants trusted “similarly.”

Problem. The CI remains compatible with a meaningful trust decrease; there is no equivalence margin or test. The only significant condition-vs-control trust cell is post hoc.

Why it matters here. Ceiling/single-item measurement further reduces the ability to detect a change.

Change/check. Say “no planned contrast rejected zero; effects as large as −.71 remain compatible.” Label the explicit-early localisation post hoc everywhere.

**M13. RQ2 and RQ4 are not answered in the terms asked**

Location: Introduction §1.3; Table 8.1

Quote: RQ2/RQ4 ask whether format/timing alter “the trajectory … following the advertisement”; Table 8.1 substitutes an early local genre shift and a late whole-conversation count.

Problem. RQ2 covers only early format. RQ4 compares unlike estimands, and late Nshift occurs before the terminal ad.

Why it matters here. A structural absence of u5 makes the intended timing question unidentifiable.

Change/check. Mark both questions partially/unanswerably operationalised, or redefine them prospectively and add a post-late turn in a future design.

**M14. The terminal advertisement is outside the theory’s own sequence**

Location: Theory §3.1 Eq. 3.1–3.8; Methods §6.2.1

Quote: A=(a1,…,aT−1), where uk→ak→uk+1; the experiment uses a4 with T=4.

Problem. The formal advertisement sequence contains only a1–a3, so the late treatment a4 is undefined as an advertisement instance before Definition 6 is even reached.

Why it matters here. The central theory cannot represent one half of the timing manipulation.

Change/check. Define served artifacts A=(a1,…,aT), with transition-linked δk⁽ᵃ⁾ only for k<T.

**M15. The trajectory instrument is not validated for the target domain**

Location: System §5.2.3; Results §7.5; Appendix F.2

Quote: 83.8% held-out accuracy on the model’s own 2,224 samples; bare/deployed readings yield Nshift=2.45 vs .40 and agree on only 351/1,080 runtime labels.

Problem. There is no human-labelled shopping-utterance or product-title validation. Formally, fgenre is defined on utterances, then applied to 510-token context windows and product titles without a context-construction function or expanded domain. Both contexts have severe ceiling/floor failure modes.

Why it matters here. Null trajectory contrasts cannot cleanly answer whether conversation changed; the classifier may simply not measure the construct.

Change/check. Keep the instrument-failure conclusion, weaken RQ nulls, and validate on a blinded target-domain sample before using δ measures substantively.

**M16. The trajectory inferential exceptions do not preserve the design**

Location: Methods §6.3; Results §7.5; Appendix F.1

Quote: “The participant” is the unit and the genre permutation is “the one conversation-level exception”; Kruskal–Wallis nevertheless uses 270 conversation rows.

Problem. The global advertised-genre permutation breaks participant/task structure; Kruskal–Wallis treats five rows per person as independent. Low ICC is not a correction.

Why it matters here. The nominal reference distributions do not match the repeated-measures assignment.

Change/check. Permute within participant/task-compatible strata and use participant-level contrasts, clustered permutation, or mixed models for whole-conversation outcomes.

**M17. The notice outcome partly measures which UI was shown**

Location: Appendix C.3; Results §7.2.2; Appendix E.2

Quote: Item 20: “I felt I noticed or clicked on sponsored buttons”; implicit treatment has no sponsored button, while brand mention is 52% even under no-ad.

Problem. The two-item α=.61 score combines a ubiquitous brand-mention item with an item structurally tailored to the explicit banner.

Why it matters here. The large format effect on “notice” is partly built into item applicability and cannot be read as a common detection construct.

Change/check. Report items separately; use format-neutral forced-choice detection/source-attribution items and objective recognition in replication.

**M18. Arm, task, and period robustness is incomplete**

Location: Methods §6.2.4–6.3; Results §7.3; Limitations §8.7

Quote: Tasks and conditions were “shuffled independently; … paired so that … task identity is not confounded”; “The two arms run in parallel and are pooled; arm is not a factor in the family.”

Problem. At N=54 exact task×condition balance is not shown, behavioural/EEG models omit task and period, and lab/crowd differ in recruitment, device, incentives, age, and supervision.

Why it matters here. Randomisation protects expectation, not exact finite-sample balance or effect homogeneity; repeated questionnaires can create predecessor/period effects.

Change/check. Print allocation counts and add prespecified task, period/predecessor, and arm-interaction sensitivity estimates.

**M19. EEG artefact control is too weakly demonstrated for the strongest onset claim**

Location: EEG §4.2.4; Appendix D.1; Discussion §8.3

Quote: Epoch rejection requires >1,050 μV; 99.8% of Dataset-A epochs survive; there is no EOG; “leaving blinks in dilutes [the tilt] … opposite of an ocular-only account.”

Problem. The threshold rejects only catastrophic movement, typing/muscle activity remains plausible, and a noisier no-ICA branch cannot rule out ocular origin or ICA-induced structure.

Why it matters here. The explicit banner is exactly the event most likely to trigger gaze/blink transients in δ/θ.

Change/check. Print no-ICA estimates/CIs, ICA component IDs and seeds, pre/post EOG-proxy diagnostics, and subject/epoch influence; prioritise replication with EOG and eye tracking.

## MINOR (10)

**m1. The Wilcoxon assumption is misstated**

Location: Methods §6.3

Quote: Wilcoxon “assumes no distributional form.”

Problem. Signed-rank inference about a location shift assumes a symmetric difference distribution; it is not assumption-free and does not test exactly the mean null.

Why it matters here. The three trust/credibility estimator disagreements are therefore not simple robustness votes on one identical hypothesis.

Change/check. State its symmetry/location assumptions or add a sign/permutation test aligned to the desired estimand.

**m2. The four-second spectral rationale contains two technical errors**

Location: EEG §4.2.4, “Why four seconds”

Quote: Four seconds is “the shortest window” supporting 2-s Welch segments; “A 2 s window is as long as the onset uncertainty itself.”

Problem. A 2-s window supports one 2-s segment and still has 0.5-Hz resolution; 4 s provides three segments and lower variance. The reported uncertainty is .23/.43 s, not 2 s.

Why it matters here. The 4-s choice is outcome-sensitive and lacks robustness, so its rationale must be exact.

Change/check. Correct resolution versus variance language and the uncertainty comparison.

**m3. Several EEG signal definitions are technically incomplete**

Location: EEG §4.2.4 and Appendix D.2

Quote: The 50-Hz notch is said to remove mains noise that “would otherwise sit inside the gamma band,” while gamma is defined as 30–40 Hz.

Problem. Fifty hertz is outside the stated gamma band. Welch window/detrending/FFT/scaling and non-overlapping band-bin conventions are omitted; exact summation of relative bands therefore cannot be checked.

Why it matters here. These details affect a compositional multi-band headline and PDF-only reproducibility.

Change/check. Correct the 50-Hz statement and specify Welch, dB reference, channel aggregation, and half-open frequency-bin rules.

**m4. Genre persistence is not uniquely defined**

Location: Definition 3

Quote: “For a maximal contiguous run of genre g(i), its persistence is R(g(i)).”

Problem. A genre can have several maximal runs; later analyses use Rmax without formally defining the max over runs.

Why it matters here. Two trajectories can map ambiguously under the written definition.

Change/check. Index runs R(i,r), then define Rmax=maxi,r R(i,r).

**m5. The product catalogue total disagrees by 100**

Location: Tables 4.1–4.2 and Figure 4.1

Quote: Table 4.1: “Products 117,343”; Table 4.2/Figure 4.1: “117,243.”

Problem. The PDF gives two source population sizes.

Why it matters here. It weakens release provenance and downstream retrieval reproducibility.

Change/check. Correct the total and explain any 100-row filtering step.

**m6. The writing−reading control is non-specific**

Location: Results §7.4; Discussion §8.3

Quote: Writing minus reading is used to show the Fz θ pipeline “register[s] a within-conversation change.”

Problem. Writing differs in motor, muscle, gaze, and cognitive state; Fz θ alone does not validate posterior α or advertisement sensitivity.

Why it matters here. It supports signal responsiveness, not construct validity.

Change/check. Call it a state/manipulation positive control and avoid using it to vindicate all null EEG markers.

**m7. Results contains interpretation despite its own chapter contract**

Location: Results §7.4–7.6

Quote: The ceiling “has little room … to register an insertion”; the control asks whether recordings “register … change”; the context cell “does not hold.”

Problem. These are interpretations and design judgements, not estimands/numbers.

Why it matters here. They blur the clean Results/Discussion split asserted at the chapter opening.

Change/check. Move these sentences to §§8.3–8.5.

**m8. Several references and labels need a final factual pass**

Location: References; Appendix C.4.1; title page

Quote: Reference [20] labels arXiv:2604… as 2025; [22] does likewise; the title uses “Behavioral” while the thesis uses “Behavioural”; recall calls the banner “Promotional Card.”

Problem. Dates and nomenclature are internally inconsistent.

Why it matters here. These are easy examiner confidence losses.

Change/check. Verify years/identifiers and normalise the title and banner terminology, preserving literal UI text only when explicitly marked.

**m9. Dense summary graphics are not self-sufficient at page scale**

Location: Figures 7.6, D.1, and F.1

Quote: Large heatmaps place many tiny p values or transition shares in a single page-width panel.

Problem. Exact cells are difficult to audit without Tables E.10/D.2/F.3.

Why it matters here. A summary figure should communicate the pattern without magnification.

Change/check. Keep only the inferentially relevant cells in the main figure and point to machine-readable/full appendix tables.

**m10. Variable-length EEG objects are written as rectangular tensors**

Location: Equation 4.8 and Table 4.5

Quote: X∈R18×32×Ti and E∈R18×Ki×32×2000 while Ti and Ki are said to vary by participant.

Problem. A single rectangular tensor cannot have participant-specific dimensions; Dataset B’s “participant × advertisement” grain also includes two no-ad locks.

Why it matters here. The notation obscures the actual data structure.

Change/check. Write collections {Xi} and {Ei}, and call Dataset B participant × onset-cell.

## VERIFY (8)

**V1. Ethics approval and separate EEG/open-data consent**

Location: Methods/Appendix C

Quote: The PDF says participants consented but gives no approving authority or protocol identifier.

Problem. Absence from the PDF may be documentation failure or absence of approval.

Why it matters here. The distinction determines whether the issue is correctable prose or a governance stop.

Change/check. Produce the approval decision and exact forms used, not a retrospective paraphrase.

**V2. Realised task×condition×period allocation**

Location: Methods §6.2.4

Quote: “The realised plan is written into the session log,” but no allocation table is printed.

Problem. Exact balance and predecessor patterns cannot be checked from the PDF.

Why it matters here. N=54 is not a multiple of five and product/task quality is heterogeneous.

Change/check. Add counts and adjusted sensitivity estimates.

**V3. Across-12 and partial-correlation p values**

Location: Methods §6.3; Table 7.8

Quote: Across-12 correction is promised; partial ρ=.80 is paired with “Sig. 0.”

Problem. The reported ledger is incomplete or wrong.

Why it matters here. These are headline association claims.

Change/check. Recompute from the frozen person-level table and print all cells.

**V4. Onset reconstruction calibration**

Location: EEG §4.2.4

Quote: 30/36 implicit onsets are reconstructed; p95 uncertainty is .43 s from leave-one-out prediction.

Problem. The number and distribution of observed calibration events are not stated clearly enough to assess a p95 estimate.

Why it matters here. Six or similarly few observed events would make tail-error estimation unstable.

Change/check. Print observed/reconstructed counts by format, calibration residuals, and subject-level sensitivity.

**V5. ICA reproducibility and no-ICA branch**

Location: Appendix D.1; Table 7.9

Quote: Visual confirmation is described, while Table 7.9 compresses width and cleaning into 126 checks.

Problem. FastICA seed, excluded components per participant, and no-ICA estimates are not on the page.

Why it matters here. The onset cluster’s artefact interpretation depends on them.

Change/check. Add a subject×component QC table and complete sensitivity estimates.

**V6. Open release and deterministic rebuild**

Location: Abstract; Datasets; Methods

Quote: Artifacts are said to be “released openly,” but only a general repository citation is supplied.

Problem. No DOI/versioned dataset manifest, checksums, exact seeds, decoding parameters, or model formulas are provided.

Why it matters here. The PDF alone cannot establish that the published tables can be rebuilt.

Change/check. Add a frozen release DOI/tag, file manifest/checksums, seeds, exclusions, model specifications, and one rebuild command.

**V7. Filter impulse response at the onset boundary**

Location: EEG preprocessing and Eq. 4.11

Quote: Only “0.5–40 Hz band-pass” is specified before immediately adjacent [t−4,t) and [t,t+4) windows.

Problem. The PDF does not reveal whether zero-phase filtering smears post-onset low-frequency power backward into pre-onset data.

Why it matters here. The main exploratory event is a large δ/θ change at exactly that boundary.

Change/check. Report filter type, phase, length/order and transition bands; add a guard-interval or causal/filter sensitivity.

**V8. Session-position coding**

Location: Appendix Table F.2

Quote: “Session position 4” levels despite each participant completing five conditions.

Problem. The encoded range or a dropped/merged level is unexplained.

Why it matters here. Session position is invoked as an order check.

Change/check. Verify the factor construction and correct the level count or explain exclusion.

---

# Scores and verdict

## Top five defence vulnerabilities

1. Show me the ethics approval and the exact consent/debrief used: why does the PDF omit EEG/open release and tell participants that products were random and ChatGPT-generated when neither was true?
2. What causal quantity do you call “format” when the two cells also change disclosure, image/modal content, CTA, UI separability, and whether the assistant reply itself is altered?
3. How do you rule out the extra three-second retrieval wait and unlike pre-onset/streaming states as the cause of the Dataset-B contrasts?
4. Why should I treat pHolm=.0496 and seven exploratory EEG cells as evidence after sixteen separate measure families, no preregistration, and no width robustness?
5. Why does the Conclusion recommend disclosure and patience and claim an explicit-early concentration when the Discussion says disclosure is confounded, there is no interaction, and this is not a serving recommendation?

## Three strongest aspects

1. The participant-level contrast framework is explicit: n counts people, t estimates have CIs and dz, Wilcoxon is printed raw, and the one t/LMM disagreement is not hidden.
2. The EEG pipeline distinguishes condition aggregation from onset-lock, reports one-trial precision, onset reconstruction, no-EOG limitations, width sensitivity, and a writing−reading control instead of pretending nulls are precise.
3. The trajectory chapter performs a genuinely useful failure analysis: saturation versus floor, six context windows, depth drift, product-genre collapse, and the distinction between ad-associated and causal “attention” shift are all made visible.

## Scores

| Dimension | Score | Basis |
|---|---|---|
| Research question / contribution | 7/10 | Timely, user-centred, and unusually multimodal; several RQs outrun their operationalisation. |
| Design | 5/10 | Strong within-person skeleton, but bundled treatment, latency, depth, period, arm, and terminal-turn confounds remain. |
| Statistical validity | 5/10 | Person-level contrasts and CIs are good; family fragmentation, ledger gaps, pseudoreplication, and null/equivalence drift are material. |
| Technical correctness | 5/10 | Core arithmetic and many formulas are sound; theory cannot represent a4, EEG timing/QC claims and Welch rationale need correction. |
| Results / interpretation discipline | 4/10 | Results are mostly transparent, but Abstract/Conclusion promote exploratory/post-hoc findings and issue policies Discussion refuses. |
| Internal consistency | 4/10 | Several family counts, model covariates, interactions, measure labels, RQ answers, and conclusion claims conflict. |
| Reproducibility | 5/10 | Good lineage and thresholds; insufficient PDF-only seeds, allocations, ICA decisions, model formulas, and release/ethics manifest. |
| Writing | 4/10 | The structure is navigable, but grammar, stale labels, broken references, and oversized figures remain submission-visible. |

**Overall score: 4.9/10.** This score is for the PDF as it stands, not for the latent quality of the project or repository. A corrected ledger, bounded claims, fixed ethics documentation, and a disciplined Abstract/Conclusion could move the thesis materially without collecting new data.

## Examiner verdict

I would challenge this thesis in the defence where it converts transparent but limited estimates into identified constructs and policy advice: whether “format” is separable from disclosure/modality/reply alteration; whether Dataset B is an ad-onset response rather than a latency and event-phase contrast; whether p=.0496 and an exploratory compositional cluster survive a defensible EEG family; whether RQ2/RQ4 are answerable without a post-turn-4 utterance; and whether the onset α–trust correlation is genuinely stronger than the condition-aggregation correlation. Before any of that, I would require the ethics approval and exact consent/debrief record. Failure to produce those documents would be more serious than any p value.

## Rest of the thesis · short corrective list

| Part | High-value correction |
|---|---|
| Introduction | Replace promises to “derive prescriptions” and the contribution claim around “attention shift” with the actually identified user-side contrasts and ad-associated genre measures. |
| Related Work | Convert the promotional catalogue of recent arXiv claims into a critical synthesis; verify years/identifiers and distinguish external validity, disclosure, persuasion, detection, and EEG evidence. |
| Theory | Allow terminal aT, repair persistence notation, and make the taxonomy match the image-bearing explicit banner and the bundled intervention mechanism. |
| Datasets | Resolve 117,343 vs 117,243; add a versioned release/consent manifest, checksums, and exact Gold-table provenance. |
| System Design | Carry the 3.03-s wait into the causal estimand; correct the “ANN” label for IndexFlatIP; report decoding/retrieval determinism and queue-latency arithmetic. |
| Remaining Methods | Add ethics approval, realised randomisation counts, period/predecessor/task/arm checks, exact LMM/GEE/CI specifications, and externally dated analysis status. |
| Appendices | Correct the participant debrief, add ICA component/seed/no-ICA tables and onset calibration residuals, repair broken figure/equation references, and simplify dense heatmaps. |

Tables and figures were audited from the PDF. Figures 7.6, D.1, and F.1 are too dense to serve as standalone audit surfaces at normal page scale; where exact values mattered, this review used their adjacent PDF tables and did not infer unreadable cells.
