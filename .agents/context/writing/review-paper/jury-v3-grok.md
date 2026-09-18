# Jury v3 — Grok

- reviewer: Grok
- PDF path: `/home/wtroi/MasterThesis-RAG-RecSys/docs/overleaf/publication/_build/main.pdf` (scratch `/tmp/paper_build/main.pdf`)
- page count: 49
- compile: succeeded
- PDF mtime: 2026-09-17 13:59:01 UTC (`/tmp/paper_build/main.pdf`; repo copy 2026-09-17 14:00:06 UTC)
- newest tex mtime: `sections/appendix_b_prompts.tex` 2026-09-17 12:44:33 UTC (`07_conclusion.tex` 12:44:28, `04_method.tex` 12:44:17, `06_discussion.tex` 12:44:12; `main.tex` 12:43:50)

Reviewed from `pdftotext -layout` of the stamped 49-page PDF. Title page through Appendix E. No `.tex`, no thesis, no prior juries.

---

## 1. Job 1 — Consistency audit

Headline numbers below are the ones the Abstract, Table 5, or Conclusion put in a reader’s mouth. “Agree” means those four surfaces name the same estimand, *n*, estimator, and verbal strength.

| Family (Table 3) | *n* | Tests / correction | Estimator | Headline number | Verbal claim (Abs / Res / Disc / Conc) | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| Behavioural battery — manipulation | 54 | 3 contrasts, Holm within outcome | one-sample *t* on *Dᵢ*; Wilcoxon raw; LMM check | any-ad *D* = +1.27 [0.76, 1.78], Holm *p* < .001; format −0.62; timing +0.58 (Table 4) | Abs/Conc: “+1.27 … more for the banner … more for early”; Disc: “the one primary outcome on which format and timing both register” | Yes |
| Behavioural battery — notice (Likert *Dᵢ*) | 54 | 3, Holm within outcome | same | any-ad +2.07; implicit−explicit −1.15; timing Holm-null (Table 4) | Abs quotes **shares**, not *D*; Res/Disc use both | **No — two notice operationalizations** (D1) |
| Behavioural battery — credibility | 54 | 3, Holm | same | early−late −0.33 [−0.55, −0.11], Holm *p* = .016; any-ad and format Holm-null (Table 4) | Abs/Conc “a third of a point”; Disc: ceiling ~6/7, carried by reliable-responses item | Yes on *D*; Abs omits ceiling |
| Behavioural battery — trust | 54 | 3, Holm | same | any-ad −0.34 [−0.71, 0.03], Holm *p* = .153; early−late Holm *p* = .063 / LMM .048 / Wilcoxon .026 (Table 4) | Abs/Conc: planned Holm-null; estimators “straddle”; post hoc early-banner −0.69 (Table 11) | Yes, and the estimator split is named |
| Cued memory | 54 | 2, Holm | same | implicit−explicit −1.45, Holm *p* < .001; timing null (Table 4); shares 57/59% vs 87/81% (Table 8) | Abs 57–59 / 81–87 matches Table 8 | Yes |
| Trust after re-exposure | 54 | 2, Holm | same | early−late −0.49, Holm *p* = .047 (Table 4) | Abs “half a point”; Conc −0.49 | Yes |
| Format × timing interaction | 54 | 1 raw *p* per outcome, outside Holm | *t* on claimed *w* = (1,−1,−1,1,0) | Res: trust +0.09 [−0.31, 0.49], |*d_z*| ≤ 0.06, raw *p* ≥ .65 | Abs “near zero on all four”; Table 5 RQ3 “not supported” | **No — weight vector vs reported *D*** (D2) |
| Secondary qualities (exploratory) | 54 | 3 per outcome | same | convincingness / relevance early−late Holm *p* = .005 / .003 (Fig. 8) | Body Res reports; Abs/Conc silent | Yes (correctly kept off headlines) |
| Logged interaction (exploratory) | 54 | 36 tests | same | “none of the nine … raw *p* < .05”; “no one clicked” | Abs/Conc: no one clicked | Yes |
| Localisation (post hoc) | 54 | 4 cells × outcome, Holm | *t* vs *a*∅ | trust only explicit-early −0.69, Holm *p* = .031 (Table 11); manip./notice all four cells | Abs/Conc label it post hoc | Yes |
| Pairwise sweep (post hoc) | 54 | 10 pairs, Holm | *t* | trust explicit-early vs *a*∅ Holm *p* = .078 in the ten-pair sweep (Table 12); Friedman trust raw *p* = .049 | Res: adds no primary cell the planned family lacks | Yes |
| Personality | 54 | 60 terms, Holm within outcome | mixed-model Wald | 0/60; nearest extraversion × credibility timing Holm *p* = .18 (Table 13) | Abs/Conc “neither personality nor demographics”; Table 5 RQ4–5 “not supported”; Disc does not over-read | Yes |
| Demographics (check) | 54 (sex 51, educ. 49; age 44 not entered) | 70 terms × two codings | same | 0/70; nearest cued-memory timing × familiarity Holm *p* = .44 (Table 14) | same as personality | Yes on the null; age exclusion is stated |
| Positive control, write vs read | 18 | 2 confirmatory measures | *t* | Fz *θ* +0.60 dB, Holm *p* = .007; posterior *α* Holm *p* = .75 (p. 12) | Disc uses it to underwrite the Fz *θ* format-null; Abs silent | Yes |
| Dataset A, condition aggregation | 18 | 3 contrasts × measure, Holm within measure | *t* on *Dᵢᴬ*; Wilcoxon raw | posterior *α* early−late −0.22 dB [−0.39, −0.04], *d_z* = −0.63, Holm *p* = .0496; Wilcoxon raw .021 (Table 20) | Abs/Conc lead with this cell **and** the depth confound; Table 5 RQ6 “partly” | Yes |
| Dataset B, onset-locked (confirmatory) | 18 | 4 cells × 2 measures | *t* on *Dᵢᴮ* | all eight Holm-null; nearest implicit-late Fz *θ* −1.38 dB, Holm *p* = .22; CIs 2–4 dB (Table 21) | Abs: “the confirmatory onset-locked cells were null”; Conc same | Yes |
| Fourteen further EEG (exploratory) | 18 | Holm within measure, **not** across | same *t* | Table 19: five explicit-early onset cells (global *δ* +4.60 dB Holm *p* = .007, plus rel. *δ*/*θ*/*α*/*β* pattern) + Dataset A rel. *θ* + implicit-late rel. *γ* | Abs: “exploratory slow-power tilt” at early-banner, “none after the mention at the **same turn**”; Conc adds that the direct format comparison is null | **Yes on Table 19** (see note under D8) |
| Exhaustive pairwise EEG (post hoc) | 18 | 256 tests | *t* | one Holm cell: Fz *θ* implicit-early − explicit-late −0.28 dB, Holm *p* = .014 (Table 22) | Res labels post hoc; not in Abs/Conc | Yes |
| Epoch width / no-ICA (sensitivity) | 18 | as the family | same | Table 18: two **different** Dataset B cells off 4 s; no-ICA *δ* +3.04 dB, Holm *p* = .29 (D.1) | Res: 4 s cell not re-estimated at other widths; Disc quotes +3.04 (not in §5.4) | **Mild leak of an appendix number into Discussion** (D6) |
| Behaviour × EEG | 18 | 6 pairs × 2 EEG scores, Holm within six per score | Spearman | Dataset B trust × posterior *α* *ρ* = .80 [.48, .93], Holm *p* = .0004; Dataset A same pair *ρ* = .24 (Fig. 3) | Abs/Conc *ρ* = .80, *n* = 18; Disc: candidate correlate, either direction; Table 5 RQ7 “supported for trust” | Yes on the number; RQ7 is narrowed (D3) |

Holm / Wilcoxon / Dataset A names / Π–π: no “Wilcoxon Holm” anywhere; every table that prints both *p*s says Wilcoxon is raw (Tables 4, 11, 12, 20, 21). Dataset A is “condition aggregation” in Method, Results, Figure 2, Tables 20–21, Appendix E. No Path A/B, equal-*n* neighbourhood, or “condition state”. Π vs π is not swapped. Insertion time is *k* / *a₂* / *a₄*; EEG *t* = 0 is visibility, not a turn index.

### Figure / table inventory (Job 1.8)

Body carries what the contract asked for: taxonomy Table 2; UI pair Figure 1; planned-contrast Table 4; EEG Holm board Figure 2; trust × *α* Figure 3; RQ Tables 1 and 5. Localisation forest (Fig. 10), notice percentages (Fig. 7), EEG forests (Fig. 13) sit in the appendices and **are** pointed from §5.2 / §5.4. Figure 8 (appendix) restates Table 4; Figure 13 restates Tables 20–21. Figure 14 (256-pair EEG board) is only reached via “subsection D.3”, never named in the body.

### Disagreements (two quoted locations each)

**D1. Abstract concatenates two different notice items.**
- Abstract, p. 1: “The banner was noticed by 69–74% of users and remembered by 81–87%; the mention by 39–46% and 57–59%. About half did not identify the mention as sponsored, and more than half of those recognised it when shown again.”
- Table 8, p. 28: notice-outcome ≥5 is 74/69% (banner) and 46/39% (mention); sponsored-buttons ≥5 is 81/74% and 46/37%. Results p. 12: “16 of 29 at turn 2, 20 of 34 at turn 4” = non-noticers on **sponsored buttons** (54−25, 54−20), not on the notice outcome (54−25=29 early, but late is 54−21=33, not 34).
The 39–46% band is the two-item **notice outcome**. The recognition follow-up uses the **sponsored-buttons** item. Adjacent Abstract sentences treat them as one quantity. Discussion p. 14 then says “Roughly 40% … reported the implicit mention as sponsored, against roughly 70% for the banner,” which is closer to the notice outcome than to sponsored-buttons (74–81%).

**D2. Interaction weights are written unnormalised and reported as half-weights.**
- Method §4.5, p. 9: “the fourth weight vector (1, −1, −1, 1, 0), that is (*a*₂^imp − *a*₄^imp) − (*a*₂^exp − *a*₄^exp) … reported with its raw *p*, outside the three-contrast Holm family.”
- Results §5.2, p. 11: “the coded contrast gives trust +0.09 [−0.31, 0.49], credibility −0.03 …, manipulation −0.10 …, notice −0.06 …”
Table 7 means on the Method order (*a*₂^imp, *a*₄^imp, *a*₂^exp, *a*₄^exp, *a*∅) give the unnormalised sum 4.93 − 5.28 − 4.69 + 5.22 = **+0.18** for trust, not +0.09. The three planned vectors in the same paragraph **are** averaged (*¼,¼,¼,¼,−1*, etc.) and match Table 4 / Table 7. The interaction *D* matches *(½, −½, −½, ½, 0)*. *t* / *p* / *d_z* are invariant to that scaling; the printed *D* and CI are not the vector the Method names.

**D3. RQ1 and RQ7 are answered as narrower questions than they were asked.**
- Table 1, p. 3: RQ1 “How does advertisement presentation format affect the user’s **overall experience** of the conversational assistant?” RQ7 “What is the relationship between the user’s neurophysiological response at advertisement onset and the **subjective experience** subsequently reported by the user?”
- Table 5, p. 16: RQ1 “Supported, **not on trust or credibility**”; RQ7 “**Supported for trust**” (credibility and manipulation pairs Holm-null).
“Overall experience” / “subjective experience” are quietly replaced by the subset of outcomes that moved. RQ2 is the honest version of this pattern (“Supported, not on notice or memory”). RQ6’s “Partly” is the one cell that matches how the question was asked.

**D4. Contribution 3 promises a corpus for learning *π*; Conclusion says the same corpus cannot train one.**
- Contributions, p. 2: “released so that serving rules can be learned and audited on real human responses (Data Availability).”
- Conclusion §7.2, p. 17: “each conversation here contains one served advertisement, which is enough to measure a cost and **not enough to train a model**.”

**D5. Body hides *k* = 37; the confirmatory table names it.**
- Method, p. 9: “the median of a **fixed number** of epochs whose midpoints lie nearest that condition’s visual onset, the count being standardised to the shortest eligible conversation.”
- Table 20 caption, p. 41: “median of the **37** epochs nearest visual onset”; Appendix E, p. 48: “37 is the shortest eligible window … Conversations vary in length (2.5–16.8 min; 37–251 complete 4 s epochs).”
The shortest-window justification is sound and is **not** *p*-driven on the page. Refusing the integer in the body still hides the researcher degree of freedom the appendix then prints on the confirmatory table.

**D6. Discussion introduces a number Results does not carry.**
- Results §5.4 does not give the no-ICA *δ* estimate.
- Discussion §6.2, p. 15: “Without ICA the *δ* cell keeps its sign but not its significance (+3.04 dB, Holm *p* = .29; subsection D.1).”
The number lives in Appendix D.1. It is a sensitivity, not a new confirmatory claim, but it violates the section contract as written.

**D7. Abstract closer is provider-facing; Implications refuse a serving rule.** Same direction, different heat.
- Abstract, p. 1: “Any provider deciding **how and when to advertise** should know that price first.”
- Implications §6.4, p. 15: “nothing here is advice about how to sell advertising space. … Nor is this a recommendation to serve advertisements late or implicitly.”
Not a “serve late” / “greater visual processing” / “explicit-late compromise” overclaim. The Abstract still ends on the provider’s decision, not the user’s bill.

**D8. Abstract / Conclusion EEG vs Table 19 / Results — match.**
- Abstract, p. 1: confirmatory onset-locked null; exploratory slow-power tilt at early-banner; “none after the mention at the same turn”; engagement indices silent; *ρ* = .80.
- Table 19, p. 41: five of seven exploratory Holm cells are explicit-early onset (rel. *δ* 0.189 Holm *p* = .004; global *δ* +4.60 Holm *p* = .007; rel. *β* −0.088; global *θ* +1.68; rel. *α* −0.039). No implicit-**early** cell. Extra cells are Dataset A rel. *θ* and implicit-**late** rel. *γ* — different estimand / different turn, not a contradiction of “same turn.”
- Table 21: eight confirmatory Dataset B cells Holm-null.
- Figure 2: Pope / Pope FC / Kislov Holm-null on both estimands.
- Figure 3 / §5.5: *ρ* = .80, Holm *p* = .0004, Dataset A *ρ* = .24.
Conclusion p. 17 repeats the same cells and adds the direct format comparison at onset is null (Table 22 nearest Holm *p* = .08). **EEG headlines match the tables.**

No leftover Path A/B. No “Wilcoxon Holm”. No Abstract sentence claims “greater visual processing,” an explicit-late compromise, or “serve late.”

---

## 2. Job 2 — Findings

### CRITICAL

None that falsify a confirmatory table. The disagreements above change what a reader *thinks* was tested (notice item, interaction *D*, RQ wording), not whether Table 4 / Table 20 / Table 21 were computed on the stated estimator.

### MAJOR

**M1. “Confirmatory” without a registry, with author-chosen width, epoch count, and 1,050 µV bound.**
- Location: §4.5, p. 9: “The sample size was set by recruitment and the study was not pre-registered, so four labels record the status of each test. Confirmatory: the measure, the contrast, and its weights were fixed on theoretical grounds before the result was read.” Appendix E, p. 47: “That amplitude bound was set after inspecting the cohort’s epoch-amplitude distribution; it is neither preregistered nor taken from the literature.”
- Why it bites: the same author chose Fz *θ* / posterior *α*, the 4 s width, the standardised 37-epoch neighbourhood, and the rejection bound, then reserved the word “confirmatory” for those cells. The labels are more honest than silent HARKing, and Table 18 shows they did **not** harvest the off-4 s Dataset B hits. The word still cannot bear a registered-report weight. A PC that treats “confirmatory Holm *p* = .0496” as a locked test is being sold more lock than exists.
- Change: say “planned, not registered” in the Abstract/Table 3 header; move the 37 and the 1,050 µV inspection into Method, not only E.

**M2. Format is presentation-plus-disclosure; several headlines still sound like format alone.**
- Location: Method §4.3, p. 8: “Realised disclosure *θ* co-varies with presentation (on request versus commercial nature disclosed) rather than being crossed with it.” Table 1 caption does say “bundled.” Abstract p. 1 never does: “more for the banner than for the mention.”
- Why it bites: implicit vs explicit is the paper’s main user-cost contrast (notice, manipulation, memory). Every one of those *D*s is also a disclosure contrast. Discussion §6.1 and Conclusion do carry the confound. The Abstract and the RQ1 one-liner do not. A reader who cites “explicit banners are noticed more” as a presentation result is citing a bundled manipulation.
- Change: one clause in the Abstract (“label and panel travel together”).

**M3. Five-condition within-participant battery with a shared 22-item questionnaire; randomisation is not a defence, and the paper almost says so.**
- Location: Limitations §6.5, p. 16: “Participants answered the same questionnaire five times and, after the first advertisement, could anticipate being asked whether the assistant had pushed a product; the Latin-square rotation, the warm-up, and the new-assistant warning spread that anticipation across conditions rather than removing it.”
- Why it bites: notice and manipulation — the two outcomes that carry RQ1–RQ2 — are the items that cue each other and that become obvious after block 1. Carry-over is acknowledged and then lived with. That is honest. It is also the most plausible non-ad explanation of a +1.27 manipulation any-ad effect (and of 11% “sponsored” under *a*∅, Table 8).
- Already answered: **partially**. Do not pretend the “different chatbot” warning fixes it.

**M4. Latin-square is not a multiple of 25; task is not in the model; one cell is 17/54.**
- Location: Appendix C.7, p. 37: “with *N* = 54, which is not a multiple of 25, exact balance is not possible. … The largest cell is the study-environment task under the implicit-late condition (17 of 54), the smallest the gardening task under the same condition (5). Neither the paired *t* … nor the mixed-model check enters task or position as a term.”
- Why it bites: implicit-late is the cell that makes “late is cheaper” look good on manipulation and credibility. If study-environment is an easier, more credible task, that tilt is in the timing contrast. χ² vs uniformity (*p* = .38) does not remove a 17-vs-5 alignment.
- Already answered: **partially** (limitation stated; not modelled).

**M5. Dataset B format comparison is not like-with-like; latency sits inside the pre-onset window.**
- Location: Method p. 9: leave-one-out error “0.23 s for banners, 0.43 s for mentions.” Limitations p. 16–17: “30 of the 36 [implicit] onsets are derived rather than observed” (E, p. 48); “the onset-locked pre-onset window, which sits inside the wait”; advertised-turn retrieval “adds about 3 s” (p. 7).
- Why it bites: Dataset B’s implicit cells compare a reconstructed, mid-stream mention against a timing-matched no-ad reply, after a ~3 s extra silent wait that *a*∅ does not have. The paper correctly refuses a like-with-like format claim at onset (p. 15, “smallest Holm *p* = .08”). The Abstract’s “none after the mention at the same turn” is still a format-shaped sentence about a worse-measured event.
- Already answered: **adequately** in Limitations; **partially** in the Abstract.

**M6. *n* = 18, one trial per Dataset B cell, Holm *p* = .0496 on the only confirmatory Dataset A hit.**
- Location: Table 20, p. 41: posterior *α* early−late Holm *p* = .0496, *n* = 18, *d_z* = −0.63, CI [−0.39, −0.04] dB (~5% power). Table 21 CIs span 2–4 dB.
- Why it bites: that cell is the first EEG sentence of the Abstract. The depth confound is in the same sentence — good. A boundary Holm *p* on a depth-confounded timing contrast, plus Dataset B intervals that cannot exclude several dB, cannot carry RQ6 as a neurophysiological “manifestation” of advertising. Table 5 already says “Partly.” The Abstract still leads with it.
- Already answered: **partially**. CIs are given; no MDE sermon (correct). The CIs suffice to show Dataset B is uninformative and Dataset A’s hit is a tenth-of-a-dB effect on 18 people.

**M7. Ethics and funding are `XXXXX` on p. 18.**
A programme committee cannot treat human EEG as reviewed with an approval-number placeholder. Scientific content is unaffected; accept/reject logistics are not.

### MINOR

**m1.** Likert-as-interval, single-item trust, credibility *M* ≈ 6.0–6.1 / 7 (Table 7), notice Cronbach *α* = .61 (Table 9). Discussion §6.1 already bounds the trust Holm-null by “the precision of a single integer-valued item whose any-ad interval does not exclude a small drop.” That is the right licence. Do not let “trust did not fall” travel without the CI.

**m2.** Brand-mention under no-ad is 28/54 (52%) (Table 8). Method §4.4 says brand mention is not detection. The Abstract’s “noticed by” percentages use the notice outcome (11% under *a*∅), which respects that. D1 is the remaining slip.

**m3.** Zero clicks: every mention is factual. No sentence implies behavioural effectiveness.

**m4.** Personality / demographics: 60 + 70 tests, BFI-10 two items/trait, age missing for 10/54 and “was not entered” (§5.3). Null is not over-read (p. 14: “not proof that personality or demography never matter”). Extraversion is reported as nearest Holm *p*, not picked by raw *p*.

**m5.** Exploratory EEG family-wise burden is stated (D.2, p. 40: “98 uncorrected tests … about five false positives … seven Holm-surviving cells of Table 19 are read as a pattern to replicate”). Abstract still names “a tilt” — labelled exploratory, one event, ocular/onset-transient preferred over cognition (p. 15). The no-EOG / “ICA did not invent the direction” argument is as sound as it can be without EOG: without ICA the *δ* cell keeps sign and loses Holm. They do not claim a cortical generator.

**m6.** Association: two EEG scores, “pooling them into one twelve-test family changes no verdict” (p. 10); Dataset A *ρ* = .24 vs B *ρ* = .80 is on Figure 3; “candidate correlate”; “The dependence can run either way” (p. 15); 2,560-map “105 raw hits where 128 are expected … no Holm cell” (p. 13). No mediation language. Single-item trust is carried into §6.3.

**m7.** Taxonomy (Table 2, pp. 4–6) spends a page on *ι, α, ϵ, σ, ϕ* that Results never use. Π = ⟨Γ, *μ*, *π*⟩ **is** reused in contributions, Implications, and Conclusion. It is not abandoned. It is still a notation dump relative to a 2 × 2 + control experiment that only moves *λ* (with *θ*) and *k*.

**m8.** Gap sentence, p. 4: “no study sits at the intersection of LLM-native conversational advertising and concurrent EEG.” On the citations given (Kosmyna / Baradari / Subramanian / Zhang are LLM×EEG without ads; neuromarketing surveys are ads without LLM conversations; Tang / Zelch / Salvi / Heineking are LLM ads without EEG) the triple intersection is not contradicted. The closer — “AI-generated advertisements can now outperform human-created ones” — compresses Meguellati’s personality-tailored preference result into a field-level fact. Overclaim on yield, not on the gap.

**m9.** Equation (4.1) and the three planned weight vectors match Table 4 against Table 7. Equation (4.2) for *D*ᴬ / *D*ᴮ matches the Dataset A/B prose. *t* = √*n* *D*/*s_D* and *d_z* = *D*/*s_D* are standard. The interaction vector is the broken one (D2). *k* = 37 does not appear in the body (D5).

**m10.** Reproducibility from the PDF alone: exclusion (Subject 4 crowd-protocol; incomplete instruments; team tests), ICA policy (≤3 ocular components, no EOG, thresholds in D.1), families table, and Gold cuts are enough to **rebuild the confirmatory tables** if the Gold CSVs and the 18 signed ICA models exist as cited (Troiani 2026a/b/c). Raw XDF is “upon request.” Placeholders on ethics/funding (M7). Contribution 3 vs §7.2 (D4).

**m11.** Short-form: Figure 8 reprints Table 4; Figure 13 reprints Tables 20–21. Appendix A–B (tasks, prompts) earn their pages. Appendix C.8 (estimator concordance) is the right home for Shapiro / bootstrap / Wilcoxon disagreement.

**m12.** Lab vs crowd pooling: extraversion raw *p* = .039, Holm *p* = .19 (Table 6). Arm is a demographic factor and a personality covariate; Table 17 any-ad signs match; no between-arm *D* at raw *p* < .05. Credibility any-ad is −0.32 lab vs −0.05 crowd — same sign, not the same size. Paper does not claim they are interchangeable beyond that table.

### VERIFY

**V1.** Recompute the format × timing *Dᵢ* with the printed vector (1,−1,−1,1,0) **and** with (½,−½,−½,½,0). Confirm *p* identical and that the Abstract “near zero” uses the half-weight *D*.

**V2.** Rebuild Table 8 “noticed” shares under (a) notice-outcome ≥5, (b) sponsored-buttons ≥5, (c) brand-mention ≥5. Confirm 16/29 and 20/34 are (b), and that cued-memory-among-non-noticers is not 16/29 if the denominator is (a) at turn 4 (33, not 34).

**V3.** Confirm Dataset A *k* = 37 is min eligible window length and was not chosen after looking at Holm *p*. The page says so (E, p. 48); the Gold script is not in the PDF.

**V4.** Confirm “pooling [the two EEG scores] into one twelve-test family changes no verdict” for trust × posterior *α*. The *ρ* = .80 cell would survive Holm₁₂; still verify.

**V5.** Ethics approval number, funding, and whether Troiani 2026b/c Hugging Face datasets are actually public at the printed URLs.

---

## 3. Top 5 vulnerabilities

1. **Unregistered “confirmatory” EEG at *n* = 18 whose only Holm-surviving planned cell is a depth-confounded −0.22 dB posterior-*α* contrast at *p* = .0496** — a reviewer will write: the neurophysiology does not license RQ6, and the Abstract still opens the EEG paragraph with it.
2. **Format is bundled with disclosure, and the Abstract never says so** — every notice / manipulation / memory “banner vs mention” headline is also a label-vs-on-request headline.
3. **Carry-over plus an unbalanced Latin square that is not in the model** — the two outcomes that survive (manipulation, notice) are the ones the 22-item battery teaches the participant to report, and implicit-late sits on 17 study-environment vs 5 gardening conversations.
4. **Abstract notice story splices two items** — 39–46% is the outcome mean; “those” who later recognise the mention are counted on sponsored-buttons. A fact-checker will catch it.
5. **Dataset B is one trial per cell after a 3 s extra wait, with mention onsets reconstructed (0.43 s, 30/36 derived)** — confirmatory onset-lock CIs of 2–4 dB are an absence of precision, not evidence that “the moment of insertion” is the estimand that earned its place.

---

## 4. Three strongest aspects

1. **Analysis contract on the page.** Table 3, the four status labels, “Holm *p* = Holm-adjusted paired *t*; Wilcoxon raw,” person-level *Dᵢ*, and the refusal to treat Holm-null as absence on Dataset B are unusually tight for a short-form empirical paper. The trust early−late estimator split is printed, not hedged away.
2. **Two EEG estimands kept apart, with a within-conversation positive control.** Write−read Fz *θ* +0.60 dB (Holm *p* = .007) before any ad contrast; Dataset A vs B not interchangeable; exploratory tilt reported as one compositional event; off-4 s hits left in Table 18.
3. **User-side framing that the Discussion actually keeps.** Implications refuse a serving rule; implicit mention is not sold as the cheap option; *θ*–*λ* confounding is in Table 5’s caption; RQ6 is “Partly,” not a neural confirmation of advertising.

---

## 5. Scores (1–10)

| Axis | Score | One line |
| --- | ---: | --- |
| Research question / contribution | 7 | Real gap (LLM ads × EEG, format × timing in the same people); taxonomy is scaffolding; contribution 3 overclaims the release. |
| Design | 6 | Clean 2×2+control, same product across *λ*, Latin-square intent; killed by *θ*–*λ* bundle, carry-over, task imbalance, *n*_EEG = 18, one shot per Dataset B cell. |
| Statistical validity | 7 | Right unit, right contrasts, Holm-within-family, CIs not observed power; unregistered confirmatory split and 37-epoch / 1,050 µV choices cap the score. |
| Technical correctness | 7 | Pipeline is specified well enough to rebuild; interaction *D* does not match the printed weights; *k* = 37 hidden in the body. |
| Results / interpretation discipline | 8 | Results stay on estimands; Discussion does not invent a serving rule or “greater visual processing”; Abstract EEG matches Table 19. |
| Internal consistency | 6 | D1–D5 are real cross-surface contradictions (notice item, interaction *D*, RQ narrowing, dataset-for-*π*, *k* = 37). Holm/Wilcoxon/Dataset A names are clean. |
| Reproducibility | 7 | Families, exclusions, ICA, Gold cuts, and Troiani 2026a/b/c citations are on the page; ethics/funding are not; raw EEG is gated. |
| Writing / short-form craft | 7 | Dense but navigable; Figure 2 earns its body slot; Figure 8/13 reprint tables; Abstract closer is punchier than Implications allow. |
| **Overall** | **6.5** | |

---

## 6. Reviewer verdict

I would **not** open a reject on missing trajectories, missing architecture, or unanalysed free text — those are declared omissions. I would open a **weak accept**, and I would argue **weak reject** only if the AC treated the EEG paragraph as a second contribution of equal weight to the behavioural 2×2. What would flip me to reject in the room: (i) selling Holm *p* = .0496 at *n* = 18, depth-confounded, unregistered, as “timing manifests neurally”; (ii) letting “banner vs mention” travel as a pure presentation effect; (iii) discovering that the Abstract’s 16/29–20/34 recognition story was computed on a different item than the 39–46% notice band. What would flip me to a clean accept: register the planned family after the fact as “planned,” put *θ* in the Abstract, put task in the mixed model or show the timing contrast survives it, name *k* = 37 in Method, and move the EEG lead sentence from the boundary *α* cell to the write–read control plus the *ρ* = .80 candidate. The behavioural core (manipulation +1.27, notice/memory format gap, timing on credibility and re-exposure trust, interaction ~0, personality 0/60) is a paper. The EEG is a carefully documented pilot attached to that paper.

---

## 7. Rest of the paper (short)

- **Introduction.** The Alphabet/Meta revenue lede is fine. Contributions 3 vs §7.2 (D4) should be the same sentence. RQ table is clear; do not let “overall experience” survive if Table 5 will carve it.
- **Related work.** Engineering / style / users / EEG+LLM quadrants are the right map. The gap sentence holds on the bibliography. Drop or hedge “outperform human-created ones” as a field summary (Meguellati is one *N* = 1,200 preference study).
- **Theory.** Equations (3.1)–(3.5) and Table 2 earn a short-form page only if *λ*, *θ*, *k*, Π, *π* are the symbols Results keep — they are. The unused coordinates (*ι, α, ϵ, σ, ϕ* levels) can shrink to a footnote without loss.
- **Method (outside the statistical framework).** TTFT / 3 s retrieval wait is the most important confound in the paper and is in the right place (p. 7 → §6.5). Figure 1 is the UI pair the contract wants. “No click was observed” belongs with the logged-measures family, where it is.
- **Appendices.** A–B (tasks, prompts) are protocol, not decoration. C.7 is the table a reviewer will use to attack task confounding — keep it. D.1’s Table 18 is the correct graveyard for off-4 s cells. E’s four-zone language is more than a 49-page paper needs but is what makes the confirmatory rebuild possible. Do not promote D.3.1 (George–Gulia nine-site) into the body; the paper already refuses that.

---

*End of review. Scoring function only; no edits to the paper.*
