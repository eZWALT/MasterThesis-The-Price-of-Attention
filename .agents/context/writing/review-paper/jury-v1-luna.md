# Independent conference review

## 1. Consistency audit table (Job 1)

| Analysis family | \(n\), tests, estimator, correction as stated in Methods | Results headline | Audit |
|---|---|---|---|
| Behavioural battery | \(N=54\); 16 planned contrasts (three per primary outcome, two per recall outcome); one-sample \(t\) on \(D_i\), raw Wilcoxon sensitivity, LMM check; Holm within outcome | Table 4 reports 16 contrasts and eight Holm-surviving cells | Consistent. |
| Format × timing interaction | \(N=54\); one coded contrast per primary outcome; one-sample \(t\), raw \(p\), outside the Holm family | Four null cells, \(|d_z|\le .06\), raw \(p\ge .65\) | Consistent. |
| Secondary qualities | \(N=54\); three contrasts per outcome for four outcomes; same \(t\), Holm within outcome; exploratory | Convincingness and relevance early–late survive | Consistent, but the body’s “confirmatory family” wording around Table 4 can make the exploratory rows easy to miss. |
| Logged interaction measures | \(N=54\); nine measures × three contrasts; exploratory, Holm within measure | 36 tests, none raw \(p<.05\) | Consistent. |
| Localisation and pairwise sweep | \(N=54\); four condition-vs-control cells or ten pairs; post hoc Holm within outcome | Post hoc early-banner trust cell survives; sweep adds no headline primary cell | Consistent and labelled. |
| Personality moderation | \(N=54\); 60 trait × contrast × outcome terms; mixed model/Wald; Holm within outcome | 0/60 survive; nearest \(p_\mathrm{Holm}=.18\) | Consistent. |
| Demographic moderation | \(N=54\); 70 terms under two codings; mixed model/Wald; Holm within outcome | 0/70 under each coding | Consistent in the headline, but the implementation and missingness need clearer accounting (Finding M3). |
| Positive control | \(n=18\); two writing-minus-reading tests; one-sample \(t\) | Fz \(\theta\) rises, posterior \(\alpha\) null | Consistent. |
| Dataset A, condition aggregation | \(n=18\); three contrasts per measure; one-sample \(t\), Wilcoxon raw; Holm within each measure | Posterior \(\alpha\), early–late, \(D=-.22\), Holm \(p=.0496\) | Consistent. |
| Dataset B, onset-lock | \(n=18\); four cells per measure; one-sample \(t\), Wilcoxon raw; Holm within each measure | All eight confirmatory cells null; intervals span 2–4 dB | Consistent. |
| Fourteen exploratory EEG measures | \(n=18\); same A/B contrasts; Holm separately within each measure, not across measures | Seven cells survive within-measure Holm; five form the early-banner slow-power tilt | Consistent, but the resulting cross-measure multiplicity is underweighted in the narrative (Finding M2). |
| Behaviour × EEG associations | \(n=18\); six declared pairs for each EEG score; Spearman, Holm within six per score | Onset-locked posterior \(\alpha\) × trust \(\rho=.80\), Holm \(p=.0004\) | The declared two-score multiplicity is not controlled jointly; the later 16-measure screen is a different exploratory family (Finding M4). |

### Disagreements found

1. **Latency cancellation is claimed beyond the contrasts for which it can cancel.** Methods says: “*the one silent wait in a session is about 6 s ... identical across the four advertisement conditions, which is why it cancels in the format and timing contrasts*” (p. 7). The same paragraph also says retrieval “*adds about 3 s*” on an advertised turn. But the primary any-advertisement contrast compares advertised turns with the no-ad condition, and Dataset B compares each advertised onset window with a matched no-ad reply. The Discussion later says the pause “*cancels only in the format and timing contrasts*” (p. 16). Thus the paper itself acknowledges that it does not cancel for two prominent estimands, but does not carry that qualification into the abstract, Results, or headline interpretation.
2. **The paper’s RQ2 answer is broader than its own answer convention.** Table 5 labels RQ2 “*Supported*” and lists three surviving timing effects plus two unmoved outcomes (p. 15). The table preamble defines “*partly*” as “*only one named factor survives*,” not as “only some outcome measures survive.” This is not a numerical contradiction, but the answer label silently treats a mixed outcome pattern as a general supported timing effect; the wording should say “partly” or define the decision rule.
3. **The association correction is described at two different scopes.** Table 3 says correction is “*within the declared six pairs for each EEG score*” (p. 10), while Results says the trust screen across all 16 EEG measures uses “*Holm within sixteen*” (p. 12). These are not the same family: the former leaves the two declared EEG scores uncorrected against each other, whereas the latter is an exploratory 16-measure screen. The paper should explicitly state whether the declared six-pair families are two separate families by design or whether the two EEG scores are one 12-test family.
4. **The abstract and conclusion compress a boundary result into a cleaner finding than the Discussion permits.** Abstract: “*Early insertion lowered credibility by a third of a point*” and “*In the EEG, posterior α aggregated over a condition was lower for early than for late insertion*” (p. 1). Discussion: the credibility effect is “*carried by the reliable-responses item*” and the EEG timing cell is “*confounded with conversational depth*” (p. 14). The abstract/conclusion should carry at least the depth and item-composition caveats because these are not minor interpretive details.

## 2. Findings

### CRITICAL

**C1. The core any-ad and onset-locked EEG comparisons are confounded by the advertised-turn retrieval delay.**  
Location: §4.2, p. 7: “*retrieval runs before generation and adds about 3 s*”; §6.5, p. 16: “*a pause that cancels only in the format and timing contrasts*.” The paper explicitly identifies a server-side difference between advertised and no-ad turns, yet the any-ad contrast and every Dataset B advertised-versus-no-ad contrast retain it. For behaviour, the extra waiting experience can itself raise pressure or alter trust; for Dataset B, it can occupy or contaminate the pre-onset 4-second window and changes the temporal context immediately before the “event.” The statement that the confound cancels is therefore false for headline estimands. Reanalyse with matched latency, model wait duration, or downgrade every advertised-vs-no-ad behavioural and Dataset B interpretation; report the exact retrieval and visual-onset timeline.

**C2. Task is demonstrably imbalanced across conditions and is not modelled, so “condition” can retain task content.**  
Location: Appendix C.7, p. 36: “*with \(N=54\), which is not a multiple of 25, exact balance is not possible*”; “*the largest cell ... 17 ... the smallest ... 5*”; and “*Neither ... mixed-model check enters task or position as a term*.” A Latin-square intention plus a chi-square test of marginal counts does not establish that the realised task-by-condition imbalance is harmless, especially with five semantically different shopping tasks and cell counts ranging from 5 to 17. A task effect aligned with an ad format or timing can bias person-level contrasts and is not removed by the stated estimator. Include task and session position in the inferential model, or provide a randomisation-based sensitivity analysis and limit causal language.

**C3. Pooling laboratory and crowd participants is not supported by the analyses reported.**  
Location: §4.1, p. 6: “*the arms differ only where recruitment or the EEG recording makes a change necessary*”; Appendix C.7, p. 36: “*The two arms are pooled throughout and arm is not a factor in any family*.” The arms differ in device, setting, incentive, age availability, and procedure, and the paper itself reports different use-frequency distributions and an arm difference in extraversion before correction. Table 17 checks only the any-advertisement contrast and only descriptively; it does not test arm × format, arm × timing, or arm × interaction effects. “Same sign and order” is not evidence of exchangeability. Add arm interactions or present arm-stratified estimates for every headline contrast; otherwise restrict pooled claims to the target population justified by the design.

**C4. The EEG “confirmatory” timing result is a boundary, depth-confounded estimate, while the paper’s conclusion presents it as a clean temporal neurophysiological effect.**  
Location: Table 20, p. 40: posterior \(\alpha\), “*Early − late ... Holm \(p=.050\)*” (the text gives .0496); §6.2, p. 14: “*A late advertisement sits on a shorter, later turn ... timing ... is confounded with conversational depth*”; Conclusion, p. 16: “*posterior α was lower for early than late under condition aggregation*.” The 37-epoch condition-aggregation windows summarize substantially different conversation positions and durations; the contrast cannot isolate insertion timing from accumulated dialogue and the late-turn context. At \(n=18\), a corrected \(p\) at .0496 is also highly sensitive to analytic choices. Report the result as a fragile, depth-confounded association in the condition-aggregation estimand, not as evidence that early insertion itself changes visual attention.

### MAJOR

**M1. Repeated exposure and questionnaire demand are acknowledged but not addressed in the primary analysis.**  
Location: §4.2, p. 6: “*Five condition blocks follow*”; Appendix C.7, p. 36: “*after the first advertisement, could anticipate being asked whether the assistant had pushed a product*”; §6.5, p. 16: “*the notice and manipulation items, asked in the same battery, may cue one another*.” The warning that each chat is a different assistant does not remove carry-over, learning, fatigue, or demand effects from four ad exposures and five repetitions of the same 22-item battery. Random condition order only spreads these effects; it does not estimate them. Include session position and prior-ad exposure in a sensitivity model, report order/position interactions, or narrow claims to this repeated laboratory-like protocol.

**M2. The exploratory EEG board has substantial uncorrected cross-measure multiplicity, yet the slow-power cluster is given a coherent event interpretation.**  
Location: §5.4, p. 12: “*five of its six exploratory orange cells sit on explicit early*”; Appendix D.2, p. 39: “*seven Holm-surviving cells among 98 uncorrected tests*” and “*roughly one expected false positive*”; §6.2, p. 14: “*a single slow-power tilt on the exploratory battery*.” The per-measure Holm procedure does not control the chance of at least one finding across 14 measures, two estimands, and many cells. Relative bands are also compositional, so several orange cells are mechanically coupled. The cautious language helps, but “one tilt” still risks converting a cluster of selected cells into an event-level finding. Show a joint multiplicity treatment or explicitly label this as a descriptive pattern requiring replication, with no cognitive interpretation.

**M3. Missingness and factor construction in the demographic analysis are insufficiently transparent for a 70-test null claim.**  
Location: Results §5.3, p. 11: “*Age was recorded for only 44 of 54 participants and was not entered*”; Appendix C.7, p. 36: education \(n=49\); Appendix C.6, p. 34: “*doctoral merged into master’s ... ‘Other’ education excluded*.” The headline says “neither personality nor demographics” moderates effects, but age is a demographic omitted because of missingness, and several other factors are recoded or excluded. This is not a null result for demographics as a whole. State the per-factor analytic \(n\), missingness mechanism, and estimand, and replace the global wording with “the tested factors did not moderate.”

**M4. The \(\rho=.80\) association is not jointly multiplicity-controlled across the two declared EEG scores and is vulnerable to low reliability and common-difference structure.**  
Location: Table 3, p. 10: “*Holm within six per score*”; §5.5, p. 12: “*trust covaries with posterior α (\(\rho=.80\) ... Holm \(p=.0004\))*”; same section: “*split-half reliability ... is .56*.” Two EEG scores are each tested against six behavioural pairs, but the declared correction is separate per score, so the probability statement is not for the 12 tests considered together. Both variables are participant-level difference scores against the same no-ad baseline, which can induce association through shared baseline or arm/individual response characteristics; \(n=18\) and reliability .56 further weaken precision. Correct the joint family, provide a partial/robustness analysis for arm and baseline, and keep the result strictly as a candidate association rather than a neurophysiological correlate of trust.

**M5. The “confirmatory” label is carrying more authority than the design warrants.**  
Location: §4.5, p. 9: “*The sample size was set by recruitment and the study was not pre-registered*,” followed by “*Confirmatory: the measure, the contrast, and its weights were fixed ... before the result was read*.” Fixing choices before reading the result is useful, but it does not establish prospective hypotheses, a locked analysis plan, or protection against researcher degrees of freedom in measure selection, epoch width, epoch count, cleaning, and family definition. The paper should call these prespecified or primary analyses, disclose when each choice was fixed, and reserve “confirmatory” for a genuinely preregistered protocol or explicitly qualify the term throughout the abstract and conclusion.

**M6. The format manipulation cannot identify presentation effects separately from disclosure effects, but some text still attributes the result to format.**  
Location: §4.3, p. 8: “*Realised disclosure θ co-varies with presentation*”; §6.1, p. 14: “*Whether the difference is due to the disclosure label or to the banner’s presentation cannot be told apart here*”; Table 5, p. 15: “*RQ1 ... Does format change ...? Supported*.” The design identifies a bundled banner-plus-disclosure versus mention-plus-on-request contrast, not \(\lambda\) alone. The limitation is stated, but the RQ answer and repeated “format” claims are broader than the manipulation. Rename the estimand as the bundled presentation/disclosure contrast or change the RQ wording, and reserve causal format claims for a crossed follow-up.

**M7. The trust and credibility evidence is internally cautious in Discussion but over-compressed in the abstract and conclusion.**  
Location: Abstract, p. 1: “*Early insertion lowered credibility by a third of a point*”; §6.1, p. 14: “*it is carried by the reliable-responses item ... not a suspicion that the assistant invented anything*”; Table 9, p. 29: trust is single-item and notice has \(\alpha=.61\). A ceiling-near credibility mean (about 6/7), a component-specific effect, and a single-item trust outcome do not support broad claims about trust or credibility costs. Revise the short form to identify the early–late credibility contrast and the reliable-responses component, and keep the corrected trust null central.

### MINOR

**m1. The interaction test is described as “null tightly” without a precision statement for all four cells.**  
Location: §6.1, p. 14: “*the interaction is null on all four outcomes, and null tightly (\(|d_z|\le .06\))*.” The small standardized point estimates do not by themselves establish a practically negligible interaction; the paper should give the interaction confidence intervals or predefine a smallest effect of interest. Replace “null tightly” with “estimated near zero in this sample” unless equivalence is tested.

**m2. “Cued memory” is called recognition although the reported measure is a self-rated memory item.**  
Location: §4.4, p. 8: “*cued memory is therefore a recognition measure*”; Table 7, p. 27: “Cued memory” is a 1–7 rating. Re-exposure plus “I feel I remember this content well” measures subjective cued recognition, not objective recognition or recall. Use “subjective cued-memory rating” consistently.

**m3. The no-ad brand-mention baseline is potentially misleading despite the paper’s good warning.**  
Location: §4.4, p. 8: “*brand mention alone is not treated as advertisement detection*”; Table 8, p. 27: no-ad brands mentioned \(28/54\) (52%), but the notice outcome is \(6/54\) (11%). The distinction is correct, but the abstract’s “noticed” phrasing can still be read as objective detection. Define “noticed” as agreement with the sponsored-content item at first use in the abstract and conclusion.

**m4. The EEG positive control validates a writing-versus-reading contrast, not the interpretation of posterior alpha as visual attention.**  
Location: §5.4, p. 12: “*the protocol [registers] a within-conversation change in the predicted marker and direction*”; §6.2, p. 14: “*its format null is a null on a marker this cohort can move*.” The control supports signal responsiveness for Fz theta, but it does not validate the posterior-alpha visual-attention interpretation or the advertisement onset timing. Narrow the control claim.

**m5. The paper uses “attention” in the title and conclusion while its primary behavioural outcome is perceived commercial pressure.**  
Location: title, p. 1; conclusion, p. 16: “*The bill ... is felt commercial pressure*.” EEG is an induced spectral proxy with no eye tracking and no EOG, and the authors explicitly say the measures are “not ... attention in themselves” (p. 8). Keep “attention” as a motivated framing term, but avoid implying that the study directly measured attention.

### VERIFY

**V1. Verify the novelty sentence against a systematic, current search.**  
Location: Related Work, p. 4: “*To the best of our knowledge no study sits at the intersection of LLMs, advertising, and EEG*.” The sentence may be accurate, but the cited review-like material is not a systematic search and several 2025–2026 adjacent works are listed. State search boundaries and date, or soften to “we found no prior study in the reviewed literature.”

**V2. Verify the platform/data-release claims before publication.**  
Location: Introduction, p. 2: “*An open multimodal dataset*”; Data Availability, p. 17: “*released as a raw ... and a processed dataset*.” A conference reviewer cannot reconstruct the confirmatory tables from the PDF alone: the exact exclusion ledger, participant-condition assignment, prompts at runtime, and released file versions are not supplied in the paper. Confirm that the cited repository and datasets are public, version-pinned, and contain the files needed to reproduce Tables 4, 20, and 21.

**V3. Verify ethics and funding metadata before submission.**  
Location: p. 17: “*approved by XXXXX under approval number XXXXX*” and “*supported by XXXXX under grant number XXXXX*.” These are publication-blocking placeholders, not harmless omissions in a camera-ready paper. Replace them or explain the anonymisation policy to the venue.

## 3. Top 5 vulnerabilities

1. The headline advertised-versus-no-ad comparisons retain a roughly three-second retrieval delay, and the paper admits that this delay cancels only for format and timing contrasts, not for the main any-ad or Dataset B estimands.
2. The only confirmatory EEG effect is a boundary \(p=.0496\) early–late condition-aggregation contrast that is explicitly confounded with conversational depth and is presented too cleanly in the short form.
3. Task-by-condition counts range from 5 to 17 and task is not in any model, so the Latin-square intention does not establish that condition effects are not task effects.
4. Laboratory and Prolific arms are pooled without arm interactions; the only arm check covers one any-ad contrast and cannot establish general exchangeability for format, timing, or EEG-linked claims.
5. The \(\rho=.80\) trust–onset-alpha result uses \(n=18\), reliability .56, shared person-level difference scores, and separate rather than joint correction across the two declared EEG scores.

## 4. Three strongest aspects

1. The paper clearly separates condition aggregation from onset-lock and writes the estimands explicitly: “*A result on one estimand is not evidence about the other*” (p. 9). That is unusually good discipline for a conversational EEG study.
2. The behavioural reporting is generally transparent about estimator disagreement: Table 4 shows the trust early–late \(t\), LMM, and raw Wilcoxon values side by side, and the Discussion calls it “*the single cell on which the three estimators straddle the threshold*” (p. 11).
3. The paper does not convert clicks or self-report pressure into persuasion: “*it is not a measure of whether the pressure worked*” (p. 13), and the association is explicitly labelled “*association, not mediation*” (p. 10).

## 5. Scores (1–10)

- Research question / contribution: **7**
- Design: **5**
- Statistical validity: **5**
- Technical correctness: **6**
- Results / interpretation discipline: **6**
- Internal consistency: **7**
- Reproducibility: **5**
- Writing / short-form craft: **8**
- Overall score: **5/10**

## 6. Reviewer verdict

I would argue for reject or weak reject in the PC meeting if the paper continues to present the pooled behavioural effects, the early–late EEG result, and the trust–alpha association as evidence about advertising format/timing without resolving the retrieval-latency confound, task imbalance, and arm pooling. The work is unusually candid and well written, and the two-estimand EEG framing is valuable, but the most interesting claims depend on small samples and analysis choices whose uncertainty is acknowledged in limitations rather than propagated into the headline estimands. A revision that models task/position/arm, isolates or bounds latency, jointly controls the association family, and downgrades the EEG and exploratory claims could become a strong methodological pilot rather than an overinterpreted causal study.

## 7. Rest of the paper

- **Introduction:** Replace “the user pays” and “attention has a price” with a more operational statement of the measured outcomes; the rhetorical framing currently exceeds what the EEG and click measures identify.
- **Related Work:** Give a reproducible search boundary for the intersection claim and distinguish conversational advertising from adjacent sponsored conversational search and neuroadaptive-chatbot work.
- **Theory:** The \(\Pi/\pi\) distinction is coherent and used later, but the taxonomy would be more useful if the paper stated explicitly which coordinates are estimands, which are held fixed, and which are bundled by the manipulation in the opening paragraph of §3.
- **Methods:** Report the randomisation algorithm, realised condition/task/position assignment at participant level, retrieval-delay distribution, visual-onset distribution, and exact missingness \(n\) for every moderator.
- **Methods:** Clarify whether the two declared EEG-score association families are jointly corrected; give an explicit decision rule for calling a question “supported” when only some named outcomes survive.
- **Appendices:** Put the exact participant exclusion flow and the runtime UI/event timeline beside the EEG pipeline. Replace placeholder ethics/funding text and provide version-pinned links and a minimal reproduction map for the headline tables.

## Typos and wording

- “*advertisement paid for the technologies in which frontier AI emerged*” (p. 2): awkward causal wording; “helped fund” would be more precise.
- “*the user’s side of the optimisation is quantified before a policy is chosen*” (p. 2): “optimisation” is not defined as a formal objective here and reads as an overclaim.
- “*the user’s bill*” (p. 4): memorable but metaphorical; define it as the measured user-side outcomes on first use.
- “*the one silent wait in a session is about 6 s*” (p. 7): “one” is ambiguous because there are four ad conditions across a participant’s five sessions; write “each advertised turn.”
- “*cued memory is therefore a recognition measure*” (p. 8): technically inaccurate for a subjective rating; see Finding m2.
- “*null tightly*” (p. 14): awkward and stronger than the reported evidence; see Finding m1.
- “*the records ... agree on who paid the most*” (p. 15): vivid but anthropomorphic and stronger than a small-sample association supports.
- “*even if it’s just a bit*” (p. 17): informal acknowledgement wording for a conference paper.
- Appendix A: “*3d-editing*” (p. 22) should be “3D editing.”
- Appendix A: “*which sport you would like to initiate*” (p. 23) is unidiomatic; use “which sport you would like to take up.”
- Appendix B: “*a line that is only three hyphens*” (p. 25) conflicts with the shown separator “–-” and should be standardised.
- Appendix D.2: “*Primary Gold averages*” (p. 39) is unexplained internal pipeline jargon in a paper; use “primary analysis.”
- Appendix E.2: “*the naming follows the Bronze/Silver/Gold convention common in data engineering*” (p. 44) is unnecessary implementation terminology unless the public pipeline is itself the object of the paper.
