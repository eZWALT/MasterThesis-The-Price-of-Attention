# Jury v1 — ChatGPT (15 Sep 2026)

Thesis: v1 PDF (source-cleaned 14 Sep). Prompt:
`../2026-09-11-thesis-review-metaprompt.md`.
Raw examiner dump. Do not treat its table cells as Gold; verify
against the PDF before applying. Do not apply until Walter says so.

---

I reviewed the full 156-page PDF, including Theory, Datasets, System Design, all of Methods, Results, Discussion, Conclusion, and Appendices A–F. I also checked the rendered pages for the dense Results/EEG tables rather than relying only on extraction.

My overall assessment is that the thesis has a real experimental contribution and a much better-than-average statistical reporting discipline, but it is not yet examiner-safe. The biggest problems are not arithmetic errors. They are estimand validity and cross-document discipline: the advertising manipulation is partly confounded with latency, format is confounded with disclosure and event geometry, the EEG onset result is much weaker than the abstract/conclusion make it look, and RQ2/RQ4 are answered using a narrower construct than the questions actually asked.

# 1. Consistency audit — Job 1

### Cross-document analysis contract

| Analysis family / check                       |     n |                              Tests | Estimator                                                                 | Correction                                                                         | Headline result                                                                                                                                                                           | Verbal claim in Results/Discussion                                                                                                               |
| --------------------------------------------- | ----: | ---------------------------------: | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Behavioural battery                           |    54 |                                 16 | one-sample t on person-level \(D_i\); raw Wilcoxon sensitivity; LMM check | Holm within each outcome                                                           | 8/16 survive; any-ad → manipulation +1.27, notice +2.07; format → manipulation −0.62, notice −1.15, memory −1.45; timing → manipulation +0.58, credibility −0.33, re-exposure trust −0.49 | Ads increase felt commercial pressure and notice; explicit is more noticed/manipulative/remembered; early is more manipulative and less credible |
| Personality moderation                        |    54 |                                 60 | random-intercept LMM, trait × contrast                                    | Holm within outcome                                                                | 0/60                                                                                                                                                                                      | No detectable personality moderation                                                                                                             |
| Free text / open recall reaction              |    54 |                    not inferential | collected, not analysed                                                   | none                                                                               | none                                                                                                                                                                                      | Explicitly excluded                                                                                                                              |
| Dataset A — condition aggregation             |    18 |            6 for confirmatory pair | one-sample t on \(D_i^A\); Wilcoxon sensitivity                           | Holm within measure                                                                | posterior α early−late −0.22 dB, Holm p=.0496; one additional exploratory relative-θ cell                                                                                                 | Sustained spectral state differs by timing, but only one confirmatory cell survives                                                              |
| Dataset B — onset-locked                      |    18 |               8 confirmatory cells | one-sample t on \(D_i^B\); Wilcoxon sensitivity                           | Holm within measure                                                                | 0/8 confirmatory                                                                                                                                                                          | No confirmatory onset-locked EEG effect                                                                                                          |
| Positive control, writing vs reading          |    18 |                                  2 | one-sample t                                                              | Holm across 2                                                                      | Fz θ +0.60 dB, p=.007                                                                                                                                                                     | Recording detects a guaranteed within-conversation contrast                                                                                      |
| EEG exploratory 14 measures                   |    18 |                                 98 | same t framework                                                          | Holm separately within each measure                                                | 7/98 cells survive; five cluster at explicit-early                                                                                                                                        | Exploratory slow-power tilt after explicit-early banner; not treated as a demonstrated format difference                                         |
| EEG exhaustive post hoc sweep                 |    18 |                                256 | pairwise t; Wilcoxon sensitivity                                          | Holm within measure                                                                | 1 survives: imp-early vs exp-late Fz θ, −0.28 dB, p=.014                                                                                                                                  | Explicitly post hoc; not a finding                                                                                                               |
| Genre \(\delta_2^{(a)}\)                      |    54 |                                  4 | McNemar + paired t                                                        | Holm for paired-t family                                                           | early pooled +0.046, p=.94                                                                                                                                                                | No advertisement-associated local shift                                                                                                          |
| Late \(N_{\text{shift}}\)                     |    54 |                                  3 | paired t; Wilcoxon sensitivity                                            | Holm                                                                               | −0.074, p=1.00                                                                                                                                                                            | No whole-conversation shift under late condition                                                                                                 |
| Genre-aligned \(\tilde{\delta}_2^{(a)}\)      |    54 |                                  1 | one-sided permutation over 108 early-ad conversations                     | uncorrected                                                                        | 9 observed vs 10.46 expected, p=.80                                                                                                                                                       | No evidence of genre alignment                                                                                                                   |
| Turn-1 vs turn-4 genre share instrument check |    54 |                                  6 | paired t; Wilcoxon sensitivity                                            | Holm across genres                                                                 | guidance 0.478→0.211, dz=−1.00, p<.001; 4/6 genres move                                                                                                                                   | Conversation genre changes substantially over the four turns independent of the ad test                                                          |
| Behaviour × EEG                               |    18 | 6 declared pairs × 2 EEG estimands | Spearman                                                                  | Holm within 6 for each EEG score; Methods additionally promises cross-12 reporting | onset posterior α × trust ρ=.80, p=.0004 within six                                                                                                                                       | Association, explicitly not mediation                                                                                                            |
| Behaviour × trajectory                        |    54 |                                  6 | Spearman                                                                  | Holm                                                                               | 0; largest manipulation × late \(N_{\text{shift}}\) ρ=.22, p=.67                                                                                                                          | No declared association                                                                                                                          |
| Trajectory × EEG                              |    18 |                                  2 | Spearman                                                                  | Holm within 2                                                                      | 0; Fz θ × \(\delta_2^{(a)}\) ρ=.47, p=.095                                                                                                                                                | No declared association                                                                                                                          |
| Behaviour × trajectory × EEG                  |    18 |                                  3 | Spearman partials                                                         | Holm within 3                                                                      | 0                                                                                                                                                                                         | Exploratory conditional association only                                                                                                         |
| Demographic moderation                        |    54 |           70 + 70 alternate coding | mixed-model joint Wald; OLS/person-level check                            | Holm within outcome                                                                | 0/70 under either coding                                                                                                                                                                  | No detectable demographic moderation                                                                                                             |
| Behavioural localisation                      |    54 |                                 16 | paired t                                                                  | Holm within outcome                                                                | 9 nominal Holm cells; explicit-early trust −0.69, p=.031                                                                                                                                  | Post hoc localisation only                                                                                                                       |
| Friedman omnibus                              |    54 |                                  8 | Friedman χ²                                                               | raw p                                                                              | 6/8 raw p<.05                                                                                                                                                                             | Exploratory omnibus                                                                                                                              |
| Behavioural ten-pair sweep                    |    54 |                                 80 | paired t                                                                  | Holm across 10 pairs within outcome                                                | 13 surviving pairwise cells                                                                                                                                                               | Localisation, not primary inference                                                                                                              |
| Estimator concordance                         |    54 |                                 16 | t vs LMM                                                                  | no new family                                                                      | 15/16 same verdicts                                                                                                                                                                       | One disagreement: trust early−late                                                                                                               |
| Item leave-one-out                            |    54 |                                 45 | t                                                                         | Holm                                                                               | early−late credibility disappears without “reliable responses” item                                                                                                                       | Sensitivity only                                                                                                                                 |
| Logged interaction measures                   |    54 |                                 36 | person-level tests                                                        | none beyond raw exploratory screening                                              | none raw p<.05                                                                                                                                                                            | Exploratory only                                                                                                                                 |
| Epoch-width / cleaning sensitivity            |    18 |                                126 | EEG sensitivity branches                                                  | sensitivity                                                                        | 2 cells survive outside 4 s; both retained as sensitivity                                                                                                                                 | Not allowed to revise confirmatory 4-s result                                                                                                    |
| Exploratory 2,560 association map             | 18/54 |                              2,560 | Spearman etc.                                                             | Holm within 21 families                                                            | 105 raw hits, none Holm                                                                                                                                                                   | Explicitly not mined                                                                                                                             |
| Additional 336 association tests              | 18/54 |                                336 | mixed/turn/event/trait                                                    | Freedman–Lane family permutation                                                   | 10 raw hits, none corrected                                                                                                                                                               | Exploratory only                                                                                                                                 |
| Split-half reliability                        |    18 |                        descriptive | reliability estimates                                                     | none                                                                               | onset posterior α split-half ρ≈.56                                                                                                                                                        | Precision diagnostic                                                                                                                             |

The core Methods table explicitly defines the participant as the inferential unit and states that sample size was set by recruitment, not an a priori power calculation. It also explicitly distinguishes confirmatory, exploratory, post hoc, and sensitivity analyses.

The Results closing tables then reproduce the main families and their headline estimates. Table 7.8 reports, for example, Dataset A \(n=18\), 6 tests, 1 surviving cell; Dataset B 8 confirmatory cells and none surviving; the positive control 1/2; the 256-test EEG pairwise sweep 1; and the 98-test exploratory EEG block 7. Table 7.9 explicitly labels the additional demographic, post hoc, sensitivity, trajectory, and exploratory checks as items “that are not families in Table 6.1.”

### Where the four documents do **not** agree cleanly

## A. “Holm p” is not used consistently enough

This is the clearest nomenclature problem.

Methods says:

> “Holm is applied only to those t tests”
> “A Wilcoxon p is reported raw, is never pooled with the t tests into one family, and is therefore not a Holm p.”

But the association Results explicitly say:

> “a Holm p here is a Holm-adjusted Spearman p.”

And Table 7.8 gives the behavioural×EEG association as:

> “ρ = .80 [.48, .93], Holm p = .0004”

Likewise, demographic moderation uses Holm-adjusted joint Wald tests, not paired t tests.

So the document cannot simultaneously maintain “Holm p” as a synonym for “Holm-adjusted paired t” and use the same unqualified label for Spearman and Wald tests.

**Required fix:** rename these throughout, e.g. \(p_{\mathrm{Holm,t}}\), \(p_{\mathrm{Holm,\rho}}\), and \(p_{\mathrm{Holm,Wald}}\), or define “Holm-adjusted p” generically and always state the estimator alongside it.

There is **no evidence of a “Wilcoxon Holm” error**. The tables consistently say Wilcoxon p is raw.

---

## B. RQ2/RQ4 are quietly narrower in Table 8.1 than in the Introduction

Introduction:

> “Does advertisement presentation format alter the trajectory of the conversation following the advertisement?”

Table 8.1 answers:

> “Does format shift the conversation’s genre?”
> “Does timing shift the conversation’s genre?”

That is not equivalent wording. The original questions are about the **conversation trajectory following the ad**. The answer table substitutes **genre shift**, which is the operationalised classifier construct.

This matters particularly because late insertion has no post-ad user utterance, and the classifier itself is demonstrably unstable across contexts. The thesis knows this: the Discussion says the trajectory result is partly an instrument failure and that calling it an “attention shift” would require a causal argument it does not have.

**Verdict:** the result is not “wrong”; the RQ mapping is too loose. RQ2/RQ4 should be rewritten explicitly as operational questions or answered with a clear statement that the study tests only the genre-based operationalisation of trajectory.

---

## C. The Abstract/Conclusion promote EEG evidence more strongly than Discussion does

Abstract:

> “In the EEG, posterior α power was lower for early than for late insertion.”
> “At early-banner onset, a transient slow-power tilt … was observed…”
> “The onset-locked posterior α response covaried with the change in reported trust (ρ = .80), making it a candidate neural marker of a trust drop.”

Discussion is materially more cautious:

> “What produced the tilt is not settled by this design.”
> “the tilt is a response to be replicated with an instrument that can separate these accounts”
> “failure to reject on the confirmatory pair is not evidence of absence.”

And the Discussion explicitly says:

> “That is a statement about where to look, not a claim that the banner captured attention…”

So the abstract turns a deliberately qualified exploratory EEG observation into a headline “response,” while Ch8 expressly refuses the cognitive interpretation.

The same problem exists for the \(n=18\) posterior-alpha timing result. Results reports:

> “−0.22 dB, Holm p = .0496; raw Wilcoxon p = .021.”

Discussion correctly says the timing result is confounded with conversational depth:

> “A late advertisement sits on a shorter, more fallback-labelled turn… timing under condition aggregation is confounded with conversational depth.”

But the Abstract/Conclusion do not carry that qualification.

---

## D. Conclusion overstates heterogeneity after reporting null moderation

Conclusion:

> “some users carry more of it than others.”

Discussion:

> “No moderation was detected…”
> “nothing here makes those costs a property of one subgroup…”
> “It is not proof that personality or demography never matter…”

Those are talking about different statistical concepts — moderation versus individual variation — but the Conclusion does not make that distinction. In context it reads like a statement of user heterogeneity despite the preceding null moderation analysis.

**Fix:** say “individual variation is visible in the EEG–trust association” rather than “some users carry more of it,” unless the thesis explicitly defines that as an association rather than treatment-effect heterogeneity.

---

## E. Conclusion contains a deployment prescription that Discussion explicitly disclaims

Discussion says:

> “This is not a recommendation to serve advertisements late or implicitly.”

But Conclusion says:

> “what follows for a platform… [is] an obligation to disclose, to be patient with monetisation rather than rush into the earliest turns…”

That is a deployment recommendation. More seriously, “obligation to disclose” cannot be experimentally attributed to the study because disclosure \(\theta\) is confounded with presentation \(\lambda\): the methods themselves state that the design cannot apportion the explicit-format advantage between presentation, disclosure, and the separable banner object.

The Conclusion therefore crosses a line that Discussion explicitly avoids.

---

## F. “Every abstract/conclusion number traces to Results” is mostly true, but not all through the main Results tables

The principal quantitative claims are traceable.

For example:

* +1.27 is Table 7.2.
* −0.33 is Table 7.2.
* −0.22, p=.0496 is Figure 7.7 / Results.
* ρ=.80 is Figure 7.13 / Results.
* −0.69 is traceable to Appendix Table E.6, not Table 7.2.

So the number is not fabricated; the trace is just sometimes to the appendix rather than the principal Results summary.

---

## G. No real nomenclature problem with Dataset A/B was found

This part is clean.

The thesis consistently describes:

> “Dataset A (condition aggregation)” and “Dataset B (onset-locked)”

and Results says:

> “dataset A is condition aggregation … dataset B is onset-locked”

“equal-n cell” appears as a description of why \(k=37\) was selected, not as an alternate Dataset A name.

No substantive Path-A/Path-B naming contamination survived the audit.

---

## H. Notation and interaction weights are consistent

Theory defines \(f_{\mathrm{genre}}\) and distinguishes temporal index \(k\) from genre index \(i\).

Results shortens \(\delta_k(a_k)\) to \(\delta_k^{(a)}\), and explicitly defines both in the Results notation paragraph.

The interaction vector is explicitly:

> “(1, −1, −1, 1, 0) the presentation-by-timing interaction.”

I found no chapter silently treating it as an unnormalised or normalised difference-of-differences under another scaling. This is a pass.

---

## I. Results/Discussion separation is good overall, but not perfect

Results largely restricts itself to estimates and labels; it explicitly says Table 7.8 and 7.9 exist so all reported analyses are accounted for.

Discussion begins:

> “This chapter interprets the analysis families estimated in Chapter 7…”

The main exception is the demographic retrospective:

> “an earlier pass… 14 of 18… two survive Holm… same two participants.”

Those numbers are indeed documented in Appendix E.10, but they are not part of the main Chapter 7 narrative. So I would call this a **minor traceability problem**, not a substantive contradiction.

---

# 2. Findings — Job 2

## CRITICAL

### C1. The advertising manipulation is confounded with an approximately 3-second retrieval delay

**Status: does not address adequately.**

Location: System Design §5.1.2.

> “On the one advertised turn, retrieval runs before the first token (median 3.03 s), so that silent wait is about 6 s… and the only ads-versus-no-ads difference in server wait.”

This is not a cosmetic implementation detail. It changes the treatment.

The behavioural estimand is presented as an advertising effect, but the participant receives a longer silent wait specifically when an ad is present. Since the thesis itself says latency can affect “trust or helpfulness,” this is part of the causal contrast unless controlled.

For behavioural outcomes, that means “ad vs no-ad” is more accurately:

**advertisement + retrieval-induced delay + different streaming dynamics vs no-ad response.**

For timing comparisons, the problem is not eliminated. Early and late ad turns may encounter different conversational response lengths and states.

For Dataset B it is worse. The onset-locked pre-window is defined as:

> \([t_i-4,t_i)\)

relative to visual onset.

Yet the ad turn has a multi-second silent retrieval interval before the first token. Therefore the “pre” window may contain a mixture of waiting-for-retrieval, post-submission waiting, and streaming context that is systematically different from the matched no-ad moment.

That threatens the interpretation of a post-minus-pre EEG change as an advertisement-onset response.

**What to change/check:** report the exact timing from user submission → retrieval start → injection → first token → visual onset for every cell; quantify how much of each 4-s pre-window is waiting time; either match the no-ad control on latency or statistically/experimentally control it. At minimum, the thesis must redefine the estimand as the effect of the deployed ad procedure rather than pure advertising presentation.

---

### C2. Format is not a pure presentation manipulation in Dataset B

**Status: partially addressed, but insufficiently incorporated into the headline claims.**

The thesis correctly states:

> “Disclosure is confounded with presentation.”

And the physical onset definitions differ:

> explicit onset ≈ reply + 0.49 s
> implicit onset ≈ injection + 1.57 s, during streaming;
> reconstruction uncertainty ≈ 0.23 s explicit and ≈ 0.43 s implicit.

These are not simply two ways of displaying the same event.

The explicit banner is a discrete UI object whose appearance is externally salient. The implicit mention is embedded in a stream whose textual position is not fixed. So Dataset B compares two different event geometries: discrete visual object versus modified ongoing language generation.

The Discussion correctly says:

> “a banner [is] an abrupt, structurally separate object and a mention [arrives] inside a reply that is already streaming”

but then the abstract still frames the results as straightforward format/timing EEG effects.

**Fix:** frame Dataset B as an effect of the *implemented event* rather than a clean causal estimate of \(\lambda\).

---

### C3. The 14-measure EEG exploratory result is under-corrected for the claim actually made

**Status: partially addressed statistically; interpretation remains too ambitious.**

The thesis explicitly says:

> “Holm adjustment is applied within a measure across the planned contrasts, never across measures.”

That is internally consistent with the stated protocol, but the justification is not sufficient for the inference actually made.

There are 98 exploratory cells across 14 measures and two estimands. Seven survive within-measure Holm, five concentrate in explicit-early.

The thesis then compresses those five cells into:

> “a single slow-power tilt.”

That is a sensible descriptive synthesis, but not a jointly corrected inferential event. “Five related cells” are being used as converging evidence even though multiplicity was controlled separately for each measure.

The denominator issue does justify caution for the five relative-power measures, but it does **not** establish that Fz θ, posterior α, global bands, FAA, and the engagement ratios can all be treated as one statistical family.

**Fix:** either control the 14-measure exploratory family jointly, or explicitly label the slow-power cluster as a descriptive pattern observed in an exploratory board, not a statistically established event.

---

### C4. The ocular/ICA defence does not establish a cognitive interpretation

**Status: partially addressed, but the argument is not sufficient.**

The thesis has a reasonable preprocessing description: ICA uses Fp1/Fp2 proxy correlations plus frontal topography criteria, with at most three components removed.

But:

> “Leaving blinks in dilutes it and widens its spread, which is the opposite of an ocular-only account.”

This is not a sufficient exclusion argument.

Without a dedicated EOG channel or eye-tracking, the study cannot directly establish that the explicit-early spectral pattern is not caused or materially altered by condition-specific eye movements, blinking, or onset-related visual behaviour. The thesis itself admits:

> “There is no dedicated electro-oculogram channel, so ocular activity is removed by component rejection and cannot be measured directly.”

The statement about “leaving blinks in” is a sensitivity intuition, not a diagnostic test.

**Fix:** provide no-ICA / alternative-ICA sensitivity, blink/ocular proxy measures, component-level diagnostics, or independent eye-movement evidence. Do not describe the slow-power tilt as attentional processing.

---

### C5. RQ2 and RQ4 are answered with a construct that is narrower than the stated question

**Status: does not adequately address the original wording.**

This is a methodological issue, not merely wording.

The original questions concern conversational trajectory **following the advertisement**.

The analysis actually operates on:

* a 13-class genre classifier,
* a bare-message or deployed-context string,
* a local genre transition \(\delta_k\),
* \(N_{\text{shift}}\),
* a genre-aligned indicator.

The resulting instrument has striking context instability:

> bare utterance: mean 2.45 shifts / 3;
> deployed window: mean 0.40;
> 70% of conversations never shift under the latter.

The thesis itself concludes:

> “That is a failure of the instrument on this corpus, not a demonstration that such a sequence does not exist.”

That sentence is appropriately cautious. The problem is that Table 8.1 still presents RQ2/RQ4 as simply “Not supported.”

The correct scientific conclusion is closer to:

**“The specified genre-based operationalisation did not detect an advertisement-associated trajectory change in this corpus.”**

That is not the same proposition.

---

## MAJOR

### M1. No arm factor is included despite a demonstrable lab/crowd difference

**Status: partially addressed.**

The thesis is explicit:

> “The two arms run in parallel and are pooled, with arm not a factor in the family.”

It also reports a significant uncorrected extraversion difference:

> lab 3.39 vs crowd 2.78, p=.039, Holm=.19.

The demographic analysis actually includes environment/lab-vs-crowd as a moderator and finds no corrected interaction.

That is helpful, but it does not answer the more basic question: **are the core treatment contrasts stable across arm?**

A null interaction in a 54-person moderation analysis is not strong evidence of transportability between an experimenter-controlled EEG lab and unsupervised Prolific participants on their own devices.

The two arms differ in setting, hardware, experimenter presence, attention-check burden, incentive structure, and age composition.

**Fix:** report arm-stratified descriptive and primary contrast estimates, or at least a sensitivity model with condition × arm for the main outcomes. It should remain explicitly secondary given n=18 in the lab arm.

---

### M2. Task is balanced by construction, but task is not actually modelled

**Status: partially addressed.**

The assignment procedure is solid:

> “task identity is not confounded with condition.”

So the design does protect the main contrasts against deterministic task-condition confounding.

But “balanced” is not the same as “irrelevant.” Different tasks can differ in product relevance, response length, difficulty, and baseline trust/credibility. The thesis later says task type is not modelled as a moderator.

Because task is deliberately rotated, it need not be a bias for the *average treatment contrast* if randomisation worked. But for a complex conversational system, task can still contribute variance and interact with timing or ad relevance.

**Fix:** make the distinction explicit: task is balanced as a design factor, but not included in the primary model; report a task sensitivity model rather than merely a task-moderation statement.

---

### M3. The within-subject questionnaire has known carry-over and anticipatory effects

**Status: adequately acknowledged, not experimentally solved.**

The thesis itself says:

> “in the later conditions they could anticipate being asked whether the assistant had pushed a product” and Latin-square order “spread[s] that anticipation across conditions rather than removing it.”

The “different chatbot” warning does not neutralise this. It could reduce interpersonal carry-over while leaving **measurement-specific anticipation** fully intact: after one or two rounds of repeated 22-item questionnaires, participants know what constructs matter.

This matters especially for notice, manipulation, and trust.

I would not call this a fatal flaw because the design does take reasonable mitigation steps, and every participant receives the same repeated battery.

**Verdict:** adequate as a declared limitation, but not a defence against carry-over.

---

### M4. Likert-as-interval is defensible at the contrast level, but “trust holds up” is too strong

**Status: mostly adequate statistically; interpretation needs tightening.**

The thesis provides a reasonable justification: participant-level \(D_i\) values average several bounded ratings, and the t test operates on the cross-participant distribution of those differences. It also uses Wilcoxon and an LMM sensitivity.

The problem is the outcome itself:

> trust is a single item,
> credibility is near 6/7 in every condition,
> notice α=.61.

For any-ad trust the CI is \([-0.71,0.03]\), not an equivalence interval.

Thus:

> “participants ended the session trusting the assistant similarly”

is stronger than “no evidence of an average difference.”

A null does not show equivalence.

---

### M5. The estimator disagreement is handled honestly, but the conclusion should stop reminding the reader that the t result is “the” answer

**Status: adequately addressed; borderline result should remain visibly secondary.**

The thesis transparently reports:

> t Holm .063, LMM .048, raw Wilcoxon .026.

and Discussion explicitly calls it:

> “the one cell of sixteen on which the paired t and the adjusted mixed model return different Holm verdicts.”

That is good practice.

The problem is not the estimator choice. It is that a reader could come away with a “timing affects trust” impression from the re-exposure trust result and the post hoc explicit-early trust cell.

The examiner-safe wording is “primary paired-t result is Holm-significant at .047 for re-exposure trust, with estimator sensitivity elsewhere; the direct post-condition trust family is Holm-null.”

---

### M6. Disclosure \(\theta\) and format \(\lambda\) are explicitly confounded, but the thesis still builds normative disclosure claims

**Status: methodologically acknowledged, downstream claim not adequately constrained.**

Methods says:

> “Realised disclosure θ co-varies with presentation λ rather than being crossed with it.”

This is a genuine structural limitation.

Yet Conclusion:

> “what follows for a platform… [is] an obligation to disclose.”

There is no experimental contrast in which disclosure changes while presentation is held fixed. The banner is simultaneously separable **and** explicitly labelled. The mention is simultaneously embedded **and** effectively undisclosed.

The memory, notice, and manipulation differences therefore cannot be attributed to “disclosure” alone.

**Fix:** convert “obligation to disclose” into a normative implication grounded in transparency literature, not a demonstrated experimental effect.

---

### M7. The EEG timing effect is a boundary result with a serious depth confound

**Status: partially addressed.**

The primary result is:

> early−late posterior α = −0.22 dB, Holm p=.0496.

The Discussion candidly states:

> “timing under condition aggregation is confounded with conversational depth.”

This is exactly the problem: the early ad is inserted into a conversation that still has later turns; the late ad is placed at the terminal turn. Their 37-epoch windows therefore come from structurally different conversational states.

In other words:

**early vs late is not just ad timing; it is ad timing + stage of conversation.**

At n=18 and p=.0496, that result should not be elevated to “EEG demonstrates a timing effect” without qualification.

---

### M8. Dataset B “null is not absence” is used responsibly in Discussion, but the evidential asymmetry must remain visible

**Status: adequately handled in Ch8, partly undermined by the Abstract.**

Discussion says:

> “failure to reject on the confirmatory pair is not evidence of absence.”

That is correct.

But the Abstract foregrounds the positive exploratory slow-power result and the onset trust association while the confirmatory onset-locked results are not mentioned as null.

This creates an asymmetric evidential framing: exploratory positive signals survive into the headline; confirmatory nulls disappear.

That is exactly the kind of presentation a committee will attack.

---

### M9. The explicit-early “slow-power tilt” is properly grouped as one phenomenon, but still receives too much narrative weight

**Status: partially adequate.**

The Discussion says five exploratory cells are:

> “one phenomenon rather than five separate findings.”

That is sensible.

It also correctly points out that the direct explicit-vs-implicit comparison does not survive correction:

> “smallest Holm p being .08… not a demonstrated difference between the two formats.”

The problem is the Abstract:

> “At early-banner onset, a transient slow-power tilt … was observed…”

The wording makes the exploratory cluster sound like a main result, even though the thesis itself says it is not a demonstrated format difference and that its physiological origin is unresolved.

---

### M10. The ρ=.80 trust–posterior-alpha association is not a finding about “a trust drop” in the causal sense

**Status: partially addressed.**

Results are actually quite careful:

> “The sign is positive… Neither mean differs from zero”

and Methods says associations are “not mediation.”

The association also has decent within-sample sensitivity:

> Pearson \(r=.78\), Kendall \(\tau=.65\), leave-one-out ρ=.77–.86.

So this is not a fragile statistical accident.

But it remains a correlation at \(n=18\), with a single-item trust outcome, one EEG score per cell, no repeated onset trials, and no ability to establish direction.

Thus:

> “candidate neural marker of a trust drop”

is acceptable only with “candidate correlational marker” and only if “drop” is understood as an individual difference in change score.

I would not allow “predicts,” “mediates,” “causes,” or “neural mechanism.”

---

### M11. The cross-score multiplicity in Behaviour × EEG is specified in Methods more strongly than it is reported

**Status: partially addressed.**

Methods says:

> each behaviour×EEG pair is evaluated on both EEG scores, Holm within six for each score, and “a cell that survives is also reported Holm-corrected across the twelve.”

Results displays:

> ρ=.80, Holm p=.0004 “within six.”

I did not find the promised cross-12 value presented as the headline result.

That does not invalidate the result — .0004 is so small that a second Holm step would obviously remain significant — but it is a contract/reporting mismatch.

**Fix:** report both \(p_{\text{Holm,within-6}}\) and \(p_{\text{Holm,across-12}}\), or delete the promise of the second correction from Methods.

---

### M12. The classifier validity is far weaker than the 83.8% headline suggests

**Status: partially addressed; theory nulls remain instrument-bounded.**

System Design reports:

> “Held-out accuracy is 83.8% on 2,224 samples.”

But the thesis reports the much more relevant deployment/corpus mismatch: bare-message and contextual inputs produce radically different trajectories, with the discussion describing the two contexts as effectively opposite failure modes.

The primary deployed label source has low agreement with the runtime interpretation according to the study's own validation analysis.

An external held-out benchmark accuracy does not establish **construct validity on four-turn, short shopping-assistant utterances**.

The thesis does acknowledge this, which is why I would not call the trajectory analysis dishonest. But the phrase “no advertisement effects were detected in intent trajectories” remains scientifically weaker than “the tested classifier-based trajectory measures showed no advertisement effect.”

---

### M13. The permutation test genuinely breaks participant pairing, but the thesis correctly declares it

**Status: adequately addressed.**

Methods explicitly identifies it as the single conversation-level exception to the participant unit.

Results frames it over:

> “108 early-advertisement conversations”

That is acceptable for a permutation null about advertised genre, provided it is not treated as equivalent to the person-level confirmatory tests.

No major finding here.

---

### M14. Kruskal–Wallis on 270 conversation rows remains formally inconsistent with the participant-as-unit rule

**Status: partially addressed.**

Results openly labels this exploratory and reports participant ICCs 0.043–0.111.

That is better than silently pseudoreplicating.

It is still pseudoreplication: the test is a 270-row KW test while the stated inferential unit is the 54 participant.

Low ICC does not prove independence.

I would accept this as a **clearly labelled exploratory descriptive diagnostic**, not as inferential evidence.

---

### M15. The “late advertisement as negative control” wording is acceptable only for the pre-ad trajectory balance logic

Late ads occur after the final user utterance, so they cannot alter a trajectory measure computed only from user turns 1–4. The thesis explicitly notes:

> “Late advertisements have no following user utterance…”

Thus the late \(N_{\text{shift}}\) comparison is really a **pre-treatment balance check**, not evidence that late advertisements “do not affect trajectories.”

I would change the label from “negative control” to “pre-treatment trajectory balance check” wherever the wording implies a treatment effect.

---

### M16. The no-click result is handled correctly

**Status: adequately addressed.**

The thesis says:

> “No participant clicked an advertisement.”

and does not use that to claim low/high behavioural effectiveness. It explicitly says the manipulation result is not a measure of whether the advertising “worked.”

Pass.

---

### M17. Personality and demographic nulls are not seriously over-read

**Status: adequate.**

The thesis is explicit that \(N=54\) is modest for interactions and says:

> “It is not proof that personality or demography never matter…”

It also refuses to promote the nearest raw cell and reports the 0/60 personality and 0/70 demographic corrected results.

The earlier raw-p demographic pass is disclosed rather than mined.

This is one of the better parts of the statistical discipline.

---

### M18. The post hoc sweeps are correctly labelled and excluded from headline inference

**Status: adequate.**

Methods says the pairwise sweep was added after the planned contrasts were read.

Appendix D explicitly says:

> “Nothing in it revises a confirmatory test, and no cell in it is treated as a finding.”

This is exactly how a post-hoc localisation should be handled.

---

## MINOR

### m1. “Holm-null trust” should be phrased as “no evidence of a difference,” not “trust holds up”

The CIs do not establish equivalence; the language should match the estimand.

### m2. “Attention shift” is generally used responsibly

Theory explicitly says a genre shift does not itself imply causality.

Discussion also says calling it an attention shift requires a causal argument the study does not make.

This is a **pass**, with the caveat that Abstract language should remain equally strict.

### m3. Relative-power dependence is understood, but the correction rationale is overbroad

The thesis correctly notes that a change in absolute power necessarily changes relative shares.

But that only partially justifies refusing any across-measure correction. The explanatory burden is stronger for unrelated absolute/regional features.

### m4. Epoch-width sensitivity is handled correctly

The two non-4-s cells are explicitly kept as sensitivity and not harvested into the primary result.

Pass.

### m5. \(k=37\) is adequately justified

The thesis explicitly ties the 37-epoch median to equal weighting of short and long conditions and fixes it in the analysis contract before results.

Pass.

### m6. The positive EEG control is a strong methodological feature

Writing vs reading produces:

> Fz θ +0.60 dB, Holm p=.007; posterior α p=.75.

That establishes that the recording pipeline can register at least one within-conversation difference before interpreting advertising contrasts.

### m7. Free-text non-analysis is not a gap

The thesis explicitly declares it unanalysed in both Methods and Results. This should remain exactly as is.

---

## VERIFY

These are things I would ask the author to verify against the released code/data before defence, rather than declaring them errors from the PDF alone.

### v1. Exact arm-stability of the main behavioural effects

The moderator analysis includes arm as a factor, but the thesis should produce the raw arm-specific contrast estimates for the four primary outcomes.

### v2. Exact overlap of Dataset-B pre-windows with ad-retrieval latency

This should be reconstructed event-by-event. It is potentially the most important unreported implementation confound.

### v3. EEG ICA sensitivity

The PDF gives the ICA rule and says the rule was fixed, but the committee should see whether the explicit-early cluster persists under the no-ICA / alternative-ICA branches already mentioned.

### v4. Cross-12 Behaviour×EEG correction

Methods promises it; Results foregrounds the within-six value. Verify whether the cross-12-adjusted p is also available.

### v5. Released exclusion table and randomisation ledger

The PDF says the session log preserves the realised plan and exclusion rules, but reproducibility cannot be fully judged without seeing the actual exclusion table, randomisation seeds, and data dictionary.

### v6. Product relevance

The thesis admits that relevance/quality of the served product is mostly unknown and recorded. A badly matched product is a direct mechanism for trust/credibility noise.

---

# 3. Top 5 vulnerabilities

**1.** “Your advertised turns take roughly twice as long to begin; why should I interpret the behavioural and EEG differences as advertising effects rather than advertising-plus-latency effects?”

**2.** “Your explicit banner changes disclosure, separability, onset geometry, and visual salience simultaneously; what experimental contrast identifies a pure format effect?”

**3.** “Why should an exploratory explicit-early slow-power cluster be in your abstract when your two confirmatory Dataset-B markers are null and your own Discussion says the physiological source is unresolved?”

**4.** “RQ2 and RQ4 ask about post-ad conversation trajectory, so why does Table 8.1 answer a narrower question about genre shifts from a classifier whose context-dependent validity is demonstrably unstable?”

**5.** “With \(n=18\), one onset trial per cell, reconstructed onset times, no EOG, and a single trust item, why should ρ=.80 be treated as more than a replication candidate?”

---

# 4. Three strongest aspects

### 1. The participant-level contrast contract is unusually disciplined

The thesis makes the inferential unit explicit, defines \(D_i\), gives the weights, distinguishes one-sample t from the paired interpretation, and keeps raw Wilcoxon and LMM in their proper roles. The mathematical formulation is coherent: \(D_i=\sum_c w_c y_{ic}\), \(\sum w_c=0\), \(t=\sqrt{n}\bar D/s_D\), \(d_z=\bar D/s_D\).

### 2. EEG preprocessing and sensitivity documentation is strong

The PDF documents the 32-channel/500 Hz pipeline, condition-blind QC, ICA thresholds, epoch rejection, Welch spectra, the two estimands, the positive control, and off-width sensitivity branches. This is considerably stronger than the usual “EEG was cleaned in MNE” level of reporting.

### 3. The thesis is unusually candid about the trajectory instrument’s failure

The author does not simply report nulls and declare the theory false. It identifies the bare/deployed-context instability, the overlap between advertised-product genre and background genre, the weakness of the target, and the distinction between observable genre shift and causal attention shift. That is methodologically mature.

---

# 5. Scores

| Dimension                           |   Score / 10 | Examiner view                                                                                                                             |
| ----------------------------------- | -----------: | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Research question / contribution    |        **8** | Strong, original intersection; contribution is real                                                                                       |
| Experimental design                 |        **6** | Clever within-subject structure, but latency, disclosure/format, onset geometry and arm issues materially constrain causal interpretation |
| Statistical validity                |        **6** | Generally disciplined, but multiplicity semantics and some family-level reasoning need tightening                                         |
| Technical correctness               |        **8** | Equations/pipeline are mostly coherent; no major arithmetic or basic formula error found                                                  |
| Results / interpretation discipline |      **6.5** | Results are mostly disciplined; Abstract/Conclusion and some Discussion wording overclaim EEG/normative implications                      |
| Internal consistency                |      **5.5** | Main weakness: Holm terminology, RQ2/RQ4 reframing, and Conclusion vs Discussion                                                          |
| Reproducibility                     |      **7.5** | Strong PDF-level documentation; still missing enough operational detail that code/data remain necessary to reproduce exactly              |
| Writing                             |        **7** | Clear and unusually explicit, but some claims are more rhetorical than the evidence permits                                               |
| **Overall thesis as it stands**     | **6.5 / 10** | Defensible master's work, but not examiner-proof without revisions                                                                        |

I would regard this as a thesis that could pass after a **substantive revision pass**, but I would not let the present Abstract, Conclusion, or EEG interpretation stand unchanged.

---

# 6. Examiner verdict

What would make me challenge this thesis in the defence is not the existence of the experiment; it is whether the candidate can distinguish the **implemented intervention** from the theoretical intervention they claim to estimate. The behavioural experiment does not isolate advertising from its additional retrieval latency; the format manipulation does not isolate presentation from disclosure and event geometry; the headline EEG evidence is partly exploratory and partly a boundary result under a conversational-depth confound; and RQ2/RQ4 are answered through a fragile classifier-based genre operationalisation rather than the broader trajectory question originally posed. The candidate must therefore defend the thesis as an **initial measurement framework with bounded empirical evidence**, not as identification of pure advertising mechanisms or deployment-optimal serving rules. The moment the defence drifts from “this is what this particular implementation did” to “this is what conversational advertising does,” the evidential basis becomes inadequate.

---

# 7. Rest of the thesis

### Introduction

The contribution and nine-RQ structure are good, but the introductory framing occasionally moves from “study of a controlled implementation” toward “inevitable future of advertising in LLMs.” Narrow the causal and deployment rhetoric to what this experiment can actually support.

### Related Work

The coverage is broad, but the thesis would benefit from a cleaner separation between directly comparable human experimental evidence and adjacent work on recommender systems, synthetic users, ad generation, and neuromarketing. The argument occasionally treats proximity as methodological comparability.

### Theory

Keep the taxonomy. Tighten the bridge from “trajectory” to “genre trajectory,” and make the causal/non-causal distinction around \(\delta_k(a_k)\) impossible to miss. The mathematical definitions themselves are broadly coherent.

### Datasets

The product-catalogue and Gold-table lineage is strong. The main thing missing is a stronger treatment of **ad relevance/quality as an empirical nuisance variable**, because the thesis itself admits this may affect trust and credibility.

### System Design

This chapter contains one of the most important threats to inference — the advertising-turn retrieval wait — but it is presented as a performance characteristic rather than a treatment confound. Move that issue explicitly into the causal limitations of the experiment.

The KV-cache arithmetic itself checks out from the PDF: the stated \(16{,}384\times20\) KiB = 320 MiB calculation is internally consistent.

### Remaining Methods

The core contrast framework is a strength. Add an explicit table of **what exactly differs between ad and no-ad turns**, including latency, retrieval, prompt injection, UI rendering, and downstream system state. That would make the estimand transparent.

### Appendices

Appendix D is valuable and unusually detailed. The most useful addition before defence would be an explicit ocular-artifact sensitivity appendix and a complete event-timing trace showing how reconstructed onset relates to retrieval and streaming timestamps.

Appendix E is also strong on item robustness and estimator sensitivity. Appendix F is appropriately sceptical about the trajectory instrument and should be treated as a limitation of measurement, not evidence against the broader theory.

---

## Bottom line

The strongest version of this thesis is:

> **A carefully instrumented first study showing that this particular implementation of conversational advertising changes perceived manipulation, notice, memory, and some timing-sensitive subjective outcomes, while providing preliminary EEG and trajectory machinery whose strongest claims still require replication and cleaner causal separation.**

The weakest version — and the one I would challenge — is:

> **A study that has identified the neural and behavioural cost of conversational advertising and derived deployment rules about disclosure and timing.**

The PDF supports the first statement. It does **not** yet support the second.
