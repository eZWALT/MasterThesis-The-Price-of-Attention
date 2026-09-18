# Conference review: *The Price of Attention* (jury v1, grok)

Venue stance: external PC reviewer. PDF only (`/tmp/paper_jury.pdf`, 48 pp.). No code, no thesis, no repo.

---

## 1. Consistency audit table (Job 1)

Columns: family as named in Table 3; *n*; tests; estimator; correction; headline number (Results); verbal claim (Discussion / Abstract / Conclusion). “Holm *p*” below is Holm on the family’s declared estimator unless noted.

| Family (Table 3) | *n* | Tests (declared) | Estimator | Correction | Headline number (Results) | Verbal claim |
|---|---|---|---|---|---|---|
| Behavioural battery | 54 | 16 (3×4 primary + 2×2 cued-recall) | one-sample *t* on *D<sub>i</sub>*; Wilcoxon raw; LMM check | Holm within outcome | Table 4: manip. any-ad +1.27, Holm *p*<.001; notice any-ad +2.07; implicit−explicit notice −1.15, manip. −0.62; early−late manip. +0.58, cred. −0.33, trust-reexp. −0.49; trust planned all Holm-null (early−late *t* Holm .063 / LMM .048 / Wilcoxon .026) | Abs./Conc.: pressure +1.27, banner > mention, early > late; trust planned-null, falls only post hoc. Disc. 6.1: “the one primary outcome on which format and timing both register.” |
| Format × timing | 54 | 1 per outcome, raw | same *t*, *w*=(1,−1,−1,1,0) | raw *p*, outside Holm | coded *D*: trust +0.09, cred. −0.03, manip. −0.10, notice −0.06; \|*d<sub>z</sub>*\|≤0.06; raw *p*≥.65 | Abs.: “did not seem to interact.” Conc.: “did not detectably compound.” Table 5 RQ3: “Not supported.” |
| Secondary qualities (expl.) | 54 | 3×4 | same *t* | Holm within outcome | early−late convincingness Holm *p*=.005, relevance .003; rest Holm-null | Results only; not in Abs./Conc./Table 5. |
| Logged interaction (expl.) | 54 | 36 (9×3) | same *t* | Holm within measure | “none of the nine… differs… (36 exploratory tests, none raw *p*<.05)”; “no participant clicked” | Abs./Conc.: “no one clicked” / “nobody clicked.” |
| Localisation (post hoc) | 54 | 4 cells × outcome | *t* vs *a<sup>∅</sup>* | Holm across 4 | Table 11: explicit-early trust −0.69, Holm *p*=.031; manip./notice all four cells above *a<sup>∅</sup>*, explicit-early +1.92 / +2.81 | Abs.: “fell only under the early banner in a post hoc localisation.” Conc.: “fell only under the early banner in the post hoc grid (−0.69).” Disc.: same cell. |
| Pairwise sweep (post hoc) | 54 | Friedman + 10 pairs | *t*; Wilcoxon raw | Holm within outcome | Table 12: trust no-ad − explicit-early Holm *p*=.078 (fails); Friedman trust raw *p*=.049 | Body 5.2: “add no cell that the planned contrasts do not already contain.” Conflicts with localisation headline (see disagreements). |
| Personality moderation | 54 | 60 (5×3×4) | mixed-model Wald | Holm within outcome across 15 | 0/60; nearest extraversion × cred. early−late Holm *p*=.18 (Table 13 .178) | Table 5 RQ4/RQ5 “Not supported.” Conc.: “neither personality nor demographics moderated any effect.” |
| Demographic moderation | 54 (sex 51, educ. 49) | 70 × two codings | same model | Holm within outcome | 0/70 and 0/70; nearest cued-memory early−late × familiarity Holm *p*=.44 (Table 14 .443); age 44/54, not entered | Disc. 6.1: null “not proof that personality or demography never matter.” |
| Positive control write−read | 18 | 2 confirmatory | one-sample *t* | the 2 measures | Fz *θ* +0.60 dB, Holm *p*=.007; posterior *α* +0.08, Holm *p*=.75 | Disc. 6.2: used to argue the format-null on Fz *θ* is informative. |
| Dataset A, condition aggregation | 18 | 3 contrasts × measure | *t* on *D<sup>A</sup><sub>i</sub>*; Wilcoxon raw | Holm within measure | early−late posterior *α* −0.22 dB [−0.39, −0.04], *d<sub>z</sub>*=−0.63, Holm *p*=.0496 (Table 20 prints .050); Wilcoxon raw .021; any-ad and format Holm-null | Abs.: “posterior *α* aggregated over a condition was lower for early than for late.” Table 5 RQ6 “Partly.” Conc.: “−0.22 dB, a 5% change.” |
| Dataset B, onset-locked | 18 | 4 cells × measure | *t* on *D<sup>B</sup><sub>i</sub>* | Holm within measure | all 8 confirmatory cells Holm-null; CIs 2–4 dB; nearest implicit-late Fz *θ* −1.38, Holm *p*=.22 | Abs.: confirmatory onset not claimed; “exploratory slow-power tilt” on banner. Disc.: format comparison at onset “smallest Holm *p*=.08” (number not in Results). |
| Fourteen further EEG (expl.) | 18 | same *D<sup>A</sup>*/*D<sup>B</sup>* | same *t* | within each measure | Table 19: 7 Holm cells; 5/6 Dataset-B orange cells on explicit-early (δ +4.60 dB, Holm *p*=.007, etc.) | Abs./Conc.: “exploratory slow-power tilt sat on the early banner.” Disc. 6.2: one event; ocular/transient preferred. |
| Exhaustive pairwise EEG (post hoc) | 18 | 10 (A) + 6 (B) × 16 = 256 | same *t* | Holm within measure | one Holm cell: Fz *θ* implicit-early − explicit-late −0.28 dB, Holm *p*=.014; Dataset B 6 raw *p*<.05, none Holm | Body: “not treated as a finding” (D.3). Held out of Abs./Conc. |
| Epoch width, no-ICA (sens.) | 18 | confirmatory families at 2/8/16/32 s and no-ICA | as re-estimated family | as family | Table 18: 2 s explicit-early Fz *θ* +3.30 Holm *p*=.021; 8 s explicit-late *α* −1.22 Holm *p*=.023. No-ICA explicit-early δ +3.04, Holm *p*=.29. Whole-window Dataset A early−late *α* at 4 s: −0.09 dB, raw *p*=.20 | Body 5.4: “epoch widths off 4 s do not revise the family.” D.1: *k*=37 cell “was not re-estimated at other widths.” |
| Behaviour × EEG | 18 | 6 pairs × 2 EEG scores | Spearman *ρ* | Holm within six **per score** | Dataset B trust × posterior *α* *ρ*=.80 [.48, .93], Holm *p*=.0004; Dataset A same pair *ρ*=.24; 2,560-test map 105 raw vs 128 expected, no Holm cell | Abs./Conc./Table 5 RQ7: *ρ*=.80 as “Supported.” Disc. 6.3: “candidate correlate.” |

### Disagreements (two quoted locations each)

1. **Conclusion invents a disclosure obligation that Discussion refuses.**
   - Conclusion 7.1: “What follows for a platform that wants to keep the trust of the people it serves is not a placement rule but an obligation: to disclose, and to measure what a placement costs the user before adopting it in its policy Π.”
   - Discussion 6.4: “This is not a recommendation to serve advertisements late or implicitly: … about half the participants did not report the implicit mention as sponsored, which raises a disclosure question this study did not test.”

2. **Same post-hoc trust cell survives one Holm family and fails the other; Abstract/Conclusion headline the survivor.**
   - Table 11 (localisation, 4 tests): “Explicit early −0.69 … Holm *p* .031” (bold).
   - Table 12 (pairwise, 10 tests): “Trust No ads − explicit early +0.69 … Holm *p* .078” (not bold). Body 5.2 then says the pairwise sweep “add[s] no cell that the planned contrasts do not already contain,” after having just reported the localisation trust fall.

3. **Figure 7 plots a different notice item than the percentages the body cites it for.**
   - Results 5.2: “74% and 69% … against 46% and 39% for the early and late mention, and 11% under *a<sup>∅</sup>* (Table 8, Figure 7).” Those are Table 8 *Notice outcome* (explicit 40/54 and 37/54; implicit 25/54 and 21/54).
   - Figure 7 caption + bars: “Noticed is agreement (≥ 5 of 7) on the sponsored-content detection item”; late mention bar is **37%** (Table 8 *Sponsored buttons* 20/54), not 39%. Early banner bar is **81%**, not 74%.

4. **Abstract “more than half” vs Results “about half” on implicit cued memory among non-noticers.**
   - Abstract: “About half did not identify the mention as sponsored, and more than half of those recognised it when shown again.”
   - Results 5.2: “including about half of the participants who had not noticed the implicit mention.”

5. **Discussion introduces a Holm *p* that Results never prints.**
   - Discussion 6.2: “the direct implicit-minus-explicit comparison at onset does not survive correction (smallest Holm *p* = .08).”
   - Results 5.4 lists the six exploratory orange cells and says confirmatory Dataset B is Holm-null; it does not give .08.

6. **Table 20 rounds the only confirmatory EEG *p* off the text’s boundary value.**
   - Results 5.4 / Figure 2 caption: “Holm *p* = .0496; … the early − late posterior *α* cell printed as .05 is .0496.”
   - Table 20: “Early − late post. *α* … *p*<sub>Holm</sub> .050.”

7. **Relative-power denominator contradicts itself inside Appendix D.**
   - D.2: “The same five bands divided by the 0.5–40 Hz total power within the same window.” E.2: “relative power uses an internal 0.5–40 Hz total.”
   - Table 19 caption: “Relative powers are proportions of total **1–45 Hz** power.”

8. **C.7 says arm is not a factor; Table 3 and Table 14 make it one.**
   - C.7: “The two arms are pooled throughout and arm is not a factor in any family.”
   - Table 3 Demographic row: “one of 5 factors at a time” (Methods 4.5 names “sex, education, familiarity, use frequency, arm”); Table 14 rows are “Environment (2).”

9. **RQ4 is answered with the whole 60-term family, not the format terms the question asked.**
   - Table 1 RQ4: “Do personality traits moderate the effect of advertisement presentation format on user experience?”
   - Table 5 RQ4 evidence: “0 of 60 trait × contrast terms below Holm .05” — that 60 is “5 traits × 3 contrasts × 4 outcomes” (any-ad + format + timing). RQ5 then reuses the same family (“nearest extraversion on credibility, Holm *p* = .18”).

10. **RQ7 is marked “Supported” after being narrowed from “subjective experience” to one pair.**
    - Table 1 RQ7: “the relationship between the user’s neurophysiological response at advertisement onset and the **subjective experience** subsequently reported.”
    - Table 5: “Supported … onset-locked posterior *α* × trust *ρ* = .80.” Results 5.5: of the six declared pairs, only that one survives; credibility and manipulation do not. Table 5’s own legend says “‘partly’ means only one named factor survives” — used for RQ6, not RQ7.

11. **Body hides *k*=37; appendix uses the leftover name “neighbourhood.”**
    - Methods 4.4: “the median of a **fixed number** of epochs centred on that condition’s visual onset, the count being standardised to the shortest eligible conversation” — count not named.
    - D.1: “the whole-window median rather than on the **k = 37 neighbourhood**.” Table 20 caption and E.2 name 37.

12. **Appendix leftover: “this thesis.”**
    - D.2: “which no confirmatory claim in **this thesis** makes.”
    - Title page / Abstract: this document is a paper; the thesis is a footnote companion.

13. **Body 5.4 vs D.1 on epoch-width sensitivity of the confirmatory Dataset A cell.**
    - Results 5.4: “epoch widths off 4 s do not revise the family (Appendix D).”
    - D.1: “the early-minus-late posterior *α* cell of the Results **was not re-estimated at other widths**; on the whole-window median that contrast is Holm-null at every width (4 s: −0.09 dB, raw *p* = .20).”

Checks that **pass** (stated so they are not re-litigated as findings):

- “Holm *p*” is never written as “Wilcoxon Holm.” Table 4/11/12/20 captions keep Wilcoxon raw. Personality Holm is Wald, which matches “Holm *p* of the family’s declared estimator” (p. 9).
- Dataset A is called “condition aggregation” in Methods, Results, Figure 2, Discussion, Conclusion. No Path A/B, “equal-n,” or “condition state.” Only leftover is “neighbourhood” (item 11).
- *Π* vs *π*, *a<sub>k</sub>*, *λ*, *θ*: Theory 3.2 and Methods 4.3 keep them. Insertion turn is *k* / *a<sub>2</sub>* / *a<sub>4</sub>*. Free *t* is clock time (Dataset B *t*=0; Appendix B “turn *t*” for the prompt index), not insertion timing. No *Π*/*π* swap found.
- Interaction weights are described as the coded (1,−1,−1,1,0) and reported as coded *D*, raw *p*, outside Holm. Results does not treat them as a normalised difference-of-differences.
- Planned weight order *(a<sup>imp</sup><sub>2</sub>, a<sup>imp</sup><sub>4</sub>, a<sup>exp</sup><sub>2</sub>, a<sup>exp</sup><sub>4</sub>, a<sup>∅</sup>)* matches (4.1) and the three named vectors. *t* = √*n* *D*/*s<sub>D</sub>*, *d<sub>z</sub>* = *D*/*s<sub>D</sub>* are standard. *D<sup>A</sup>*/*D<sup>B</sup>* in (4.2) match the prose.
- Abstract/Conclusion numerical claims that **do** trace to a table: +1.27 (Table 4), +1.92 (Table 11), −0.33 / −0.49 / −0.34 Holm *p*=.15 (Table 4), −0.69 (Table 11), −0.22 dB (Table 20), *ρ*=.80 (Figure 3 / §5.5), notice/memory bands (Table 8).
- No Abstract/Conclusion sentence claims “greater visual processing,” “serve late,” or “EEG depends on how and when.” Depth confound is in Disc. 6.2.
- Body inventory: Table 4, Figure 2, Figure 3, Table 2, Tables 1 and 5, Figure 1 are in the body. Localisation forest (Fig. 10), notice bars (Fig. 7), EEG forests (Fig. 13) are appendix and are pointed to. Figure 14 is only reached via “subsection D.3,” not by figure number. Figure 8 restates Table 4.

---

## 2. Findings

### CRITICAL

**C1. The Dataset A confirmatory cell is an aggregation choice; the paper’s own alternative at the same 4 s is Holm-null, and the body conceals that.**
- Location: Results 5.4 “early minus late on posterior *α* (−0.22 dB, … Holm *p* = .0496)”; Methods 4.4 “median of a fixed number of epochs centred on … visual onset”; D.1 “on the whole-window median that contrast is Holm-null at every width (4 s: −0.09 dB, raw *p* = .20)”; E.2 “*k*=37 is the shortest eligible window”; Gold “keeps the whole-window median; confirmatory tests use this aggregation.”
- Problem: Two summaries exist. The one that enters Table 20 / Abstract / Table 5 RQ6 / Conclusion is the *k*=37 nearest-onset median. The stored whole-window median at the **same** width is −0.09 dB, raw *p*=.20. Width sensitivity was run on the null aggregation, then the body says off-4 s “do not revise the family.” *k*=37 is data-dependent (shortest conversation in *this* sample: “37–251 complete 4 s epochs”). The count is unnamed in the body.
- Why it bites: This is the only confirmatory Dataset A survivor, Holm *p*=.0496 at *n*=18, already depth-confounded (Disc. 6.2). A reader of the body cannot see that the other pre-specified summary of the same recordings does not move.
- Change: Name *k*=37 in Methods. Report the whole-window 4 s contrast next to Table 20. Stop saying the width grid “does not revise” a cell the grid never re-estimated. If both aggregations were “fixed before the result was read,” say so and show both.

**C2. “Confirmatory” is a label the authors assigned after designing the analysis; nothing was pre-registered, and two processing constants were read from the data.**
- Location: Methods 4.5 “The sample size was set by recruitment and the study was not pre-registered… Confirmatory: the measure, the contrast, and its weights were fixed on theoretical grounds before the result was read.” E.2: “That amplitude bound [1,050 μV] was set after inspecting the cohort’s epoch-amplitude distribution; it is neither preregistered nor taken from the literature.” E.2 / D.1: *k*=37 from the shortest eligible window; ICA exclusions “confirmed by visual review”; “no EOG channel.”
- Problem: The confirmatory/exploratory split is an intra-author chronology, not a registered contract. Epoch count, rejection bound, and component sign-off are researcher degrees of freedom. Table 3 then prints Dataset A/B rows as confirmatory, and Table 5 / Abstract treat Holm-surviving cells as RQ answers.
- Why it bites: At *n*=18 and a boundary *p*, the word “confirmatory” is doing rhetorical work the design did not earn. A PC reader will discount every Holm-surviving EEG cell by one grade.
- Change: Drop “confirmatory” from Abstract, Table 3, and Table 5, or replace it with “planned, not registered.” Move *k* and the 1,050 μV rule into the limitations paragraph that already admits no pre-registration.

**C3. Dataset B’s pre-onset window is the retrieval wait; format cells are not like-for-like.**
- Location: Methods 4.2 “on the advertised turn retrieval … adds about 3 s, so the one silent wait … is about 6 s”; Limitations 6.5 “a pause that cancels only in the format and timing contrasts.” Methods 4.4: “one 4 s epoch before and one after visual onset, post minus pre, against the same difference at a timing-matched reply under *a<sup>∅</sup>*.” E.3: implicit onset error 0.43 s vs banner 0.23 s; “30 of the 36 [implicit] onsets are derived rather than observed”; implicit reconstruction “falling before the reply has finished streaming.”
- Problem: Limitations admit the extra TTFT cancels in format and timing *behavioural* contrasts (both advertised). It does **not** cancel in Dataset B: the 4 s pre-onset on an advertised turn is mostly the silent retrieval wait; the matched *a<sup>∅</sup>* reply has ~2.7 s TTFT and no retrieval. Implicit vs explicit onsets also differ in reconstruction error, in whether the reply is still streaming, and in what is painted. The paper never says this sentence about Dataset B.
- Why it bites: Every Dataset B cell — including the exploratory slow-power tilt that Abstract and Conclusion keep, and the *ρ*=.80 that answers RQ7 — is post-minus-pre against a control whose pre-window is a different wait. One trial per cell, CIs of 2–4 dB (Results 5.4).
- Change: State the pre-onset/TTFT confound in Methods 4.4 and Limitations. Downgrade Dataset B and the association to “confounded onset contrast” until a logged first-token-matched control exists.

### MAJOR

**M1. Conclusion’s “obligation to disclose” and Abstract’s “cost the user cannot name” outrun Discussion and the design.**
- Location: quotes under disagreement 1; Abstract “a cost the user cannot name while it is incurred”; Disc. 6.1 already notes *θ* and *λ* “were varied together.”
- Problem: *θ* is not crossed with *λ* (Methods 4.3). Discussion refuses a disclosure recommendation. Conclusion writes an obligation into *Π*. Abstract converts a notice gap into an unnamed cost.
- Why it bites: This is exactly the serving/policy language the Implications section claims not to offer. A reviewer who reads Conclusion first will file the paper as a policy note on undisclosed native ads, which the 2×2 did not test.
- Change: Rewrite 7.1 to match 6.4. Keep measurement; drop “obligation: to disclose.”

**M2. Post-hoc localisation of trust is in the Abstract and Conclusion; the stricter pairwise Holm does not agree.**
- Location: disagreement 2; Abstract “fell only under the early banner in a post hoc localisation”; Table 4 planned trust all Holm-null.
- Problem: Labelling “post hoc” is not the same as keeping it out of headlines. Two post-hoc families, two verdicts. Planned trust any-ad CI is [−0.71, 0.03] (Table 4) — a small drop is not excluded.
- Why it bites: Trust is the title commodity. The only trust *fall* a casual reader will remember is a 4-cell Holm that a 10-cell Holm takes away.
- Change: Abstract/Conclusion: planned trust is Holm-null; CI includes a small drop. Move −0.69 to a parenthetical, or report both Holm *p*s.

**M3. Holm is within each of sixteen EEG measures, not across; exploratory cells are then used as “support.”**
- Location: Table 3 “3 contrasts within each measure” / “4 cells within each measure”; D.2 “the fourteen non-confirmatory measures carry no joint error control”; Results 5.4 “Dataset A has two orange cells… confirmatory posterior *α* and relative *θ*”; Disc. 6.2 “relative *θ* moving the same way as exploratory support”; D.2 “treat the seven Holm-surviving cells of Table 19 as roughly one expected false positive among 98 uncorrected tests at *α* = .05.”
- Problem: Sixteen families × two estimands is a large uncorrected surface. Relative *θ* is compositional with the other relative bands (D.2). The “one expected false positive among 98” sentence is arithmetically wrong (98×.05≈5 uncorrected FPs, not one) and mixes Holm-survivors with an uncorrected expectation.
- Why it bites: Figure 2 is a body figure. A reader sees two asterisks on Dataset A timing and five on Dataset B explicit-early and reads a syndrome. The paper’s own appendix says there is no joint guarantee.
- Change: Fix the 98-test sentence. In 5.4/6.2, do not call relative *θ* “support” for the confirmatory *α* cell. Put a one-line family-wise caveat under Figure 2.

**M4. The “ICA did not create the tilt” argument is not sound, and there is no EOG channel.**
- Location: Disc. 6.2 “Leaving blinks in dilutes the tilt rather than removing it (subsection D.1), so the cleaning did not create it.” D.1: without ICA, explicit-early absolute *δ* “shrinks from +4.60 dB (Holm *p* = .007) to +3.04 dB (raw *p* = .073, Holm *p* = .29).” Methods 4.4 / E.2: “there is no EOG channel”; exclusions use Fp1/Fp2 proxy + visual review.
- Problem: Removing ICA **kills** the Holm cell. Direction stays positive; the finding does not. A frontal proxy plus “at most three” visually confirmed components is not a substitute for EOG. Absolute *δ* in an awake induced spectrum is the band the paper itself says “carries ocular and movement activity” (D.2).
- Why it bites: Abstract and Conclusion keep “an exploratory slow-power tilt sat on the early banner.” That tilt is the Dataset B story. It is also the band and the onset most compatible with a look/blink, on a pipeline whose ocular control is the thing that makes the cell significant.
- Change: Disc. 6.2 must say the Holm cell does not survive no-ICA. Priority for the ocular/transient reading is already in the text; make it the only reading until EOG exists.

**M5. Association *ρ*=.80 is Holm-protected inside six pairs per score, not across two scores; trust is a single item; RQ7 is over-answered.**
- Location: Table 3 “Holm within six per score”; Results 5.5 Dataset A same pair *ρ*=.24, raw *p*=.34; Disc. 6.3 “single-item trust score and eighteen people … candidate correlate”; Table 5 RQ7 “Supported.”
- Problem: Two EEG scores were evaluated per behavioural pair. Multiplicity across scores is declared by splitting families, not corrected. The significant score is the noisier one (split-half .56 vs .78 under aggregation). Single-item trust (Methods 4.4; Table 9 “has no *α*”). Table 5 marks RQ7 Supported; credibility and manipulation are silent.
- Why it bites: This is the multimodal punch. It is also *n*=18, one item, one of two estimands, Dataset B confounded (C3). “Supported” in Table 5 will be copy-pasted into reviews.
- Change: Holm within 12, or state that the second score was a second family. Table 5: “Partly — trust only.” Keep “candidate correlate” in the Conclusion, not just in 6.3.

**M6. Latin-square task is not entered in any model; realised cells run 5–17.**
- Location: C.7 “Neither the paired *t* … nor the mixed-model check enters task or position as a term”; Table 15 study-environment × implicit-late **17**/54, gardening × implicit-late **5**; *χ*²(16)=17.0, *p*=.38. Methods 4.2 claims “task identity is not confounded with condition.”
- Problem: *N*=54 is not a multiple of 25; they say so. Uniformity is not rejected, but a 17-vs-5 split on the same condition is large enough to move a Likert third-of-a-point (the credibility timing effect). Task is never a covariate.
- Why it bites: Timing and format contrasts assume the Latin square did the work. The estimator does not check.
- Change: Add task (and position) to the LMM check. If the early−late credibility cell dies, it was never a timing effect.

**M7. Laboratory and crowd are pooled; arm is a covariate in one model, a factor in another, and “not a factor” in C.7.**
- Location: disagreement 8; Table 17 any-ad *D*s same sign; extraversion lab 3.39 vs crowd 2.78, raw *p*=.039, Holm *p*=.19 (Table 6); Limitations 6.5 “differ in age, incentive, and device”; age missing 10/54, all in the crowd export (4.1 / 5.1 / 5.3).
- Problem: Setting, device, incentive, age, and extraversion differ. The only arm-split in the PDF is the four any-ad contrasts (Table 17), uncorrected. Format and timing — the effects that survive Holm — are not shown by arm. Age is dropped rather than tested.
- Why it bites: *N*=54 is already the personality/demographics story. If the early-banner manipulation effect is a Prolific effect, the paper cannot show it.
- Change: Print format and timing *D*s by arm. Strike “arm is not a factor in any family.”

**M8. Related-work closer overclaims the gap it correctly opens.**
- Location: §2 Gap: “To the best of our knowledge no study sits at the intersection of LLMs, advertising, and EEG” — true on the citations given (Tang/Zelch/Salvi/Meguellati have users and ads, no EEG; Kosmyna/Baradari/Zhang have LLM×EEG, no ads; Kislov/Vecchiato have ads×EEG, no LLM). Next sentence: “the evidence that exists is about yield; what is missing is the user’s bill.”
- Problem: Tang et al. (*N*=179) measured notice, clicks, and stop-requests; Zelch acceptance; Salvi persuasion and notice. Those are user-side bills. The missing cell is EEG × LLM advertising × format×timing, not user measurement as such.
- Why it bites: Contribution 3 and the last sentence of the Abstract (“Any provider deciding how and when to advertise should know that price first”) rest on being first to the user’s bill. The citations already include that bill without EEG.
- Change: Narrow the gap sentence to the EEG×format×timing cell. Credit Tang/Salvi as the user-side baseline this study extends.

### MINOR

**m1. Notice outcome vs sponsored-button item (disagreement 3).** Align Figure 7 with Table 8’s Notice column or stop citing Figure 7 for the 39–46% / 69–74% numbers.

**m2. Interaction *D* and main-effect *D* are on different weight scales.** Methods is explicit that *w*=(1,−1,−1,1,0) is unnormalised. Results reports those *D*s next to \|*d<sub>z</sub>*\|≤0.06. Fine if a sentence says the coded *D* is not a mean-of-cells DoD.

**m3. Figure 8 restates Table 4; Figure 10 restates Table 11; Figure 13 restates Tables 20–21.** Short-form waste. Figure 14 is never cited by number in the body.

**m4. Taxonomy *Γ*, *μ*, *ι*, *α*, *ϵ*, *σ*, *ϕ* are defined and then almost unused.** *λ*, *θ*, *π* earn their keep. Two pages of Theory for a checklist the Results never refer to. Cut *Γ*/*μ* or use them in Limitations (“*μ* was prompt injection vs UI paint”).

**m5. Cronbach *α*=.61 on notice (Table 9); credibility means 5.69–6.08 / 7 (Table 7); trust is one item.** Discussion 6.1 and 6.5 say this. Holm-null trust then only licenses “this item, this session, this *N*, did not separate,” which 6.1 mostly does. Conclusion “Trust counter-intuitively did not fall” still overplays a single integer.

**m6. Estimator disagreement on trust early−late is handled honestly in Results 5.2 and C.8** (Shapiro–Wilk rejects 7/16 *D<sub>i</sub>* series; bootstrap and LMM both break on that cell). Not a finding against the paper — listed so it is not re-opened. Do not silently prefer LMM *p*=.048.

**m7. Brand-mention under no-ad is 28/54 (52%) (Table 8).** Methods 4.4 and Figure 7 respect notice ≠ detection. Held.

**m8. Zero clicks: no sentence claims effectiveness.** Held.

**m9. Personality/demographics: no raw-*p* fishing in headlines; age 10/54 stated and excluded, not silently dropped from a tested model.** Held, except Conclusion’s “neither … moderated any effect” is one notch stronger than 6.1.

**m10. Depth confound on Dataset A timing is acknowledged (Disc. 6.2).** The Abstract still reports early < late posterior *α* without it. One clause in the Abstract.

**m11. Dataset B “Holm-null is not absence” is applied to confirmatory markers (CIs 2–4 dB) but not symmetrically to the engagement-index silence** (“were silent by presentation, by timing, and against *a<sup>∅</sup>*” — Disc. 6.2). Those CIs are also wide.

**m12. 2,560-test map is separated and not mined.** Held.

**m13. Association language stays at association in Results; Disc. 6.3 allows either direction.** Held. Conclusion “covaried with the change in reported trust (*ρ* = .80)” is still a bit causal-adjacent (“the change”).

**m14. *k*=37 appears only in the appendix, as the brief requires — but that is how the RDF stays hidden (C1).** Not a pass.

**m15. Placeholders: “supported by XXXXX,” “approved by XXXXX” (p. 17).** Unfit for a camera-ready conference PDF.

**m16. Carry-over / repeated 22-item battery.** Limitations 6.5 is adequate as a declared limit (“spread that anticipation … rather than removing it”). Not contradicted. Sufficient defence? No, and they do not claim it is.

### VERIFY

**V1. Whether *k*=37 is truly the shortest *eligible* window** (E.2: conversations “37–251 complete 4 s epochs”; eligibility ≥5 epochs and ≥80%). Cannot recompute from the PDF.

**V2. Whether 9,449/9,468 and “all 108 pairs” are exact.** Stated twice (4.4 and E.2); no listing.

**V3. HF / GitHub releases cited as already out** (Troiani 2026a,b,c; Data Availability). Links not fetched.

**V4. Model name “quantised Qwen 3.6 35B-A3B”** (Methods 4.2). Looks like a version typo; cannot check from the PDF.

**V5. Figure 2 heatmap.** Values used above are from the text layer. If a print reader cannot resolve .0496 vs .050, the caption already warns; the table still prints .050.

---

## 3. Top 5 vulnerabilities

1. The only confirmatory Dataset A EEG cell is Holm *p*=.0496 at *n*=18 on a *k*=37 nearest-onset median the body never names, while the paper’s own whole-window median at the same 4 s is Holm-null (−0.09 dB, raw *p*=.20), and late ads sit on shorter later turns.
2. Nothing is pre-registered, yet Table 3/Abstract/Table 5 sell a confirmatory split whose epoch count and 1,050 μV bound were read from these recordings, with ICA visually signed and no EOG.
3. Dataset B (and therefore *ρ*=.80) contrasts a 4 s pre-onset window that is mostly the extra ~3 s retrieval wait against a no-ad reply that does not have that wait, with implicit onsets reconstructed in 30/36 cases (0.43 s vs 0.23 s).
4. Conclusion writes an “obligation to disclose” into *Π* after Discussion says that question “this study did not test,” and Abstract/Conclusion keep a post-hoc trust drop (Holm .031 in a 4-cell family, .078 in the 10-pair sweep) that the planned trust family does not contain.
5. Sixteen EEG measures × two estimands are Holm-corrected only within measure; the exploratory slow-power tilt loses Holm significance without ICA, and RQ7 is marked “Supported” on one of six pairs with single-item trust.

---

## 4. Three strongest aspects

1. **Two named EEG estimands, written down before the contrasts, with a within-conversation write−read control.** *D<sup>A</sup>* vs *D<sup>B</sup>* in (4.2), Figure 2 side by side, and Fz *θ* +0.60 dB on writing are the methodological contribution that Related Work actually lacked — not the taxonomy.
2. **The behavioural planned family is complete, three-estimator, and mostly honestly narrated.** Table 4 plus the trust early−late straddle (*.063 / .048 / .026*) is how a non-registered Likert study should look; notice ≠ detection is enforced (Table 8 brand-mention 52% under no-ad vs notice 11%).
3. **User-side framing is held in Implications 6.4** (“nothing here is advice about how to sell advertising space”) and in the refusal to turn implicit/late into a serving rule — until Conclusion 7.1 breaks it.

---

## 5. Scores (1–10)

| Axis | Score | One reason |
|---|---|---|
| Research question / contribution | 7 | Real LLM×ads×EEG cell; taxonomy over-sold; user-bill gap overclaimed vs Tang/Salvi. |
| Design | 6 | Clean 2×2+control within; *θ* locked to *λ*; TTFT; Dataset B one trial; pool of two arms; task unmodelled. |
| Statistical validity | 5 | No prereg; *k*=37 / 1,050 μV; two post-hoc Holm families; Holm-within-16; *n*=18 boundary *p*. |
| Technical correctness | 6 | Contrast algebra holds; 0.5–40 vs 1–45 Hz; “one FP among 98”; ICA argument; “this thesis.” |
| Results / interpretation discipline | 6 | Results mostly stay numerical; Conclusion/Abstract do not; *p*=.08 appears in Discussion; relative *θ* as “support.” |
| Internal consistency | 5 | Disclose obligation; Fig. 7 vs Table 8; arm-as-factor; *k*=37 neighbourhood; Table 20 .050 vs .0496. |
| Reproducibility | 6 | Appendices E/D are unusually complete; visual ICA and XXXXX ethics/funding are not; *k* unnamed in the body. |
| Writing / short-form craft | 7 | Tight Methods→Results contract; figure-first; Theory long; appendix restatement; placeholders; informal ack. |
| **Overall** | **6** | |

---

## 6. Reviewer verdict

I would argue **weak reject** in a selective HCI / NeurIPS-adjacent venue, **weak accept only if** the authors strip “confirmatory” from the EEG claims, put *k*=37 and the whole-window null in the body, move the post-hoc trust cell and the disclosure obligation out of Abstract/Conclusion, and write the Dataset B TTFT confound as a limitation on *ρ*=.80. What I would stand on in the meeting: an unregistered *n*=18 spectral study whose single Holm-surviving planned EEG cell is a data-dependent neighbourhood at *p*=.0496, whose own alternate aggregation is null, and whose multimodal headline is a one-trial onset contrast confounded with a 3 s wait, attached to a single Likert item. The behavioural *N*=54 family is the publishable core; it is not enough to carry the EEG-and-policy jacket as written.

---

## 7. Rest of the paper

**Introduction.** Alphabet/Meta revenue open is fine; “attention is the currency of this economy” is a slogan the Results never operationalise (no one clicked; notice is a Likert mean). Contribution 3 (“released so that serving rules can be learned”) already points at *π*-learning the Limitations say this corpus cannot support (one ad per conversation, §7.2).

**Related Work.** Engineering triad (Xu, Feizi, Duetting) is the right setup. Style paragraph correctly holds appeal fixed. Gap closer: see M8. Do not demand more citations.

**Theory.** Equations (3.1)–(3.5) and Table 2 are a notation dump unless Results mention them. Keep *a<sup>imp</sup>*, *a<sup>exp</sup>*, *λ*, *θ*, *π*. Fold *Γ*/*μ* into one paragraph or drop.

**Rest of Methods.** Assistant/retrieval (HyDE, FAISS, BM25, cross-encoder, ~117k products) is more platform than needed for the contrasts; it does establish that product is not confounded with *λ*. TTFT vs Nielsen 10 s is a red herring — the issue is the 3 s *difference*, not the 10 s cap. BFI-10 after the session is correctly not an input to *ϕ*.

**Appendices.** A (tasks) and B (prompts) are the right place for injection wording (“Do NOT sound salesy”) — that wording *is* the implicit treatment and belongs in a limitation (implicitness is prompt-enforced covertness, *ϵ* held covert by construction). C.8 assumption checks are the paper’s best statistical honesty; they should be one sentence in 4.5, not only appendix. D.3.1 nine-site montage is unused in the body and should stay that way (it already says it does not enter Holm). E’s four-zone/Bronze-Silver-Gold jargon is engineering theatre; the cuts in E.2 are the science. Strike “this thesis” (D.2). Fix Table 19 “1–45 Hz.”

---

## Typos and wording

Page numbers from the PDF footer (“— *n* of 48 —”).

1. **p. 16, Acknowledgements:** “even if it’s just a bit” — register break in a conference closing.
2. **p. 17, Funding / Ethics:** “XXXXX under grant number XXXXX”; “approved by XXXXX under approval number XXXXX” — leftover placeholders.
3. **p. 39, D.2:** “which no confirmatory claim in **this thesis** makes” — wrong document.
4. **p. 37, D.1:** “**k = 37 neighbourhood**” — leftover internal name.
5. **p. 7, A.2 briefing (quoted):** “3d-editing” — should be “3D-editing”; the appendix says mistakes that reached the study were kept, so this may be intentional, but it reads as a typo.
6. **p. 24, B.5.1:** “separated by a line that is only three hyphens” vs the prompt line “only: –-” — en-dash / hyphen mismatch.
7. **p. 1, Abstract:** “Format and timing **did not seem to** interact” — hedge that Results (“null tightly, \|*d<sub>z</sub>*\|≤0.06”) does not need.
8. **p. 16, Conclusion:** “Trust **counter-intuitively** did not fall” — “counter-intuitively” is interpretation in the wrap.
9. **p. 13, Disc. 6.1:** “the **reassuring** half of the result for the user” — cheerleading.
10. **p. 4, Related Work:** “the same advertisement lands differently on an extravert than on a **sceptic**” — extraversion vs scepticism are not a pair; openness/neuroticism would be.
11. **p. 8, Methods 4.4:** “FastICA with at most three visually confirmed ocular components removed per recording” — “confirmed” vs D.1’s automatic-then-reviewed rule; wording drifts.
12. **p. 39, Table 19 caption:** “total **1–45 Hz** power” vs D.2/E.2 “0.5–40 Hz” — error, not style.
13. **p. 40, Table 20:** “*p*<sub>Holm</sub> **.050**” vs body **.0496** — rounding that matters at the threshold.
14. **p. 6, 4.2:** “**Qwen 3.6** 35B-A3B” — likely “Qwen3” / “3.5”; unverified.
15. **p. 22, A.1:** “select a single suitable gift **at least**” — dangling.
16. **p. 23, A.4:** “and which sport you would like to initiate” — not parallel with the rest of the briefing.
17. **p. 9, after (4.1):** “*t* = √*n* *D*/*s<sub>D</sub>*” written with *D* as if a single observation; prose says it is the mean of *D<sub>i</sub>*. Works, but the symbol collision with *D<sub>i</sub>* is ugly.
18. **p. 2, contribution 4:** “**four-zone** preprocessing pipeline” — Bronze/Silver/Gold jargon in a contribution bullet.
19. **p. 11, Figure 2 caption:** “the early − late posterior *α* cell printed as .05 is .0496” — admits the figure is already rounding the only asterisk that matters.
20. **p. 27, Figure 7 vs p. 11 Results:** “39%” / “37%” late-mention notice — see disagreement 3; if not a figure error, the sentence that cites both is the wording fault.
