# Jury v1 — Fable 5.1 (15 Sep 2026)

Thesis: v1 PDF 156 pp (`docs/overleaf/thesis/_build/dissertation.pdf`).
Prompt: `../2026-09-11-thesis-review-metaprompt.md`.
In-IDE / extra dump (not one of the five web juries). Raw examiner
dump. Do not treat its table cells as Gold. Do not apply until
Walter says so.

---

Reading complete: 156 pages, cover through Appendix F, plus rendered checks of Figures 6.1, 7.7, 7.13 and 8.1 (the text extraction could not carry their marks). Everything below is from the PDF alone.

---

# External examiner review — *The Price of Attention*

## Job 1. Cross-document consistency audit

Page numbers are the printed ones. Methods = Table 6.1 (p. 60) and §6.3 (pp. 58–62). Results = Ch 7 including Tables 7.8 and 7.9 (pp. 78–79). Discussion = Ch 8 including Table 8.1 (p. 92). A+C = Abstract (p. iii) and Ch 9 (pp. 95–98).

| Family | Methods (n · tests · estimator · family) | Results | Discussion | Abstract + Conclusion | Verdict |
|---|---|---|---|---|---|
| Behavioural battery | 54 · 3 per primary outcome + 2 per recall item = 16 · one-sample paired *t* on \(D_i\) · Holm within outcome | Table 7.2: 16 rows, 8 bold; Table 7.8: 16 / 8; notice +2.07 | "Eight of the sixteen planned contrasts survive Holm" (p. 80) | Abstract +1.27 manipulation, −0.33 credibility, −0.49 trust on re-exposure all trace to Table 7.2 | **Agrees**, except items D9, D11, D16, D26 below |
| Format × timing interaction (behavioural) | Not in Table 6.1 (3 contrasts per outcome) | "Format × timing is null on all four outcomes (\|dz\| ≤ 0.06)" (p. 65); no D, CI or *p* in any table | "null tightly: every interaction effect is at most \|dz\| = 0.06" (p. 81); Table 8.1 RQ5 | Abstract "Presentation and timing did not interact" | **Disagrees**: an Abstract claim and an RQ verdict with no table cell and no declared family |
| Personality moderation | 54 · 15 trait × contrast per outcome = 60 · LMM Wald · Holm within outcome | Fig 7.5 (40 cells shown), Table E.9 (60); Table 7.8: 60 / 0 | "sixty trait × contrast terms … none below .05" | "0 of 60 corrected tests" | **Agrees** |
| Demographic moderation | **Absent from Table 6.1** | §7.3: 70 + 70; Table 7.9 (title: "checks that are not families in Table 6.1") | §8.2 treats it as an answer to "who the user is" | Abstract: "neither personality nor demographics moderated any outcome"; Ch 9: "0 of 70, and 0 of 70 again" | **Disagrees**: undeclared check promoted to Abstract |
| Dataset A, condition aggregation | 18 · "3 contrasts, separately within each measure" (Table 6.1) **but** §6.3 p. 61 lists four weight vectors including "(1, −1, −1, 1, 0) the presentation-by-timing interaction" | Fig 7.7/7.8: 3 contrasts × 2 measures; Table 7.8: 6 / 1; early−late posterior α −0.22 dB [−0.39, −0.04], Holm .0496 | "This is the one confirmatory Dataset A cell that survives Holm" + depth caveat (p. 84) | Abstract: "posterior α power was lower for early than for late insertion" (no estimand, no caveat); Ch 9 −0.22 dB with caveat | **Methods-internal disagreement** (3 vs 4 contrasts); EEG interaction never reported; Abstract weighting |
| Dataset B, onset-locked | 18 · 4 · *t* on \(D^B_i\) · within measure | 8 confirmatory cells Holm-null; nearest implicit-late Fz θ −1.38 [−2.80, 0.04], Holm .22 | "Holm-null at 4 s with intervals spanning 2–4 dB" | Ch 9: "the eight confirmatory cells are Holm-null" | **Agrees** |
| Positive control write−read | 18 · 2 | Table 7.3: Fz θ +0.60 [0.22, 0.97], Holm .007 | agrees | Ch 9 +0.60 dB | **Agrees** |
| Exhaustive pairwise (post hoc) | 18 · 10 + 6 pairs × 16 measures = 256 | Table 7.8: 256 / 1; Table D.2 8 raw hits | agrees | not in A+C | **Agrees** |
| Fourteen exploratory EEG measures | "Exploratory covers the fourteen EEG measures" (p. 58) | 98 / 7 (Fig 7.8) | "one phenomenon rather than five" (p. 84) | Abstract "transient slow-power tilt (↑ δ, θ; ↓ α, β)" with no exploratory label | **Partly**: Appendix D.2 introduces a fifth tier "secondary" (p. 125) that §6.3's four labels do not contain |
| Trajectories \(\delta^{(a)}_2\) | 54 · 4 · "exact McNemar; paired *t* interval" | Table 7.5: "Holm-adjusted paired *t*; McNemar for the two-condition rows" — Holm *p* is the *t*; McNemar raw, absent on pooled row | "confirmatory tests on \(\delta^{(a)}_2\), late \(N_{\text{shift}}\), and \(\tilde\delta^{(a)}_2\)" (p. 85) | Ch 9 "no declared contrast separates" | **Disagrees** on which test carries the verdict (D7) |
| Late \(N_{\text{shift}}\) | 54 · 3 · paired *t*; "none of them is confirmatory" (p. 62) | Table 7.7; "the negative control declared in Table 6.1" (p. 74) — Table 6.1 does not say "control" | called "confirmatory" (p. 85) | Table 8.1 uses it as RQ4 evidence | **Disagrees** (label, control status) |
| \(\tilde\delta^{(a)}_2\) permutation | 54 · 1 · uncorrected, "none … confirmatory" | 9 vs 10.46, *p* = .80 | called "confirmatory" (p. 85) | Ch 9: 9 vs 10.46 | **Disagrees** on label |
| \(\hat g_1\) vs \(\hat g_4\) | 54 · six genres · Holm | "This is not a test but rather a check" (p. 75) then "Holm *p* < .001"; Table 7.8: 6 / 4 | used as depth evidence | — | **Self-contradiction** in one paragraph |
| Behaviour × EEG | 18 · 6 pairs × **2 scores**; "a cell that survives is also reported Holm-corrected across the twelve" (p. 59) | Table 7.8 "Tests 6"; Fig 7.13 "Holm p = 0.0004 (within six)"; across-twelve never printed | "ρ = .80 with a Holm p = .0004 within the declared six" | Abstract "candidate neural marker of a trust drop"; Ch 9 "one of the six behaviour–EEG pairs" | **Disagrees**: promised correction missing, 12 tests counted as 6 |
| Behaviour × trajectory | 54 · 6 | ρ = .22, Holm .67 | agrees | — | Agrees |
| Trajectory × EEG | 18 · 2 | Fz θ ρ = .47, Holm .095 | agrees | — | Agrees |
| Behaviour × trajectory × EEG | 18 · "3 pairwise … each pair also partialled" | Table 7.8: "3 tests, Sig. 0, key estimate … partial ρ = .80" | ".80 and .83" (p. 88) | — | **Verify**: Sig. = 0 with ρ = .80 at *n* = 18; .83 appears nowhere in Ch 7 |

### Disagreements, each with two quoted locations

**D1. Serving recommendations the Discussion refuses.**
Discussion p. 90: "This is not a recommendation to serve advertisements late or implicitly. The design did not measure the advertiser's side at all, and about half the participants did not report the implicit mention as sponsored, which raises a disclosure question this study did not test." Discussion p. 88: "nothing below is advice about how to sell advertising space."
Conclusion p. 98: "What follows for a platform … is not a placement rule but an obligation to disclose, to be patient with monetisation rather than rush into the earliest turns simply because they command attention." Abstract p. iii: "providing evidence for serving policies that enable monetisation without unnecessarily degrading the experience."

**D2. Disclosure prescription from a design that confounds disclosure.**
Methods p. 57: "Disclosure is confounded with presentation. Realised disclosure θ co-varies with presentation λ rather than being crossed with it … The design therefore cannot apportion any memory advantage of the explicit format between the presentation itself, the disclosure label, and the mere availability of a separable object."
Conclusion p. 96: "The prescription is about disclosure rather than placement."

**D3. "The signal is at onset" vs the confirmatory record.**
Results p. 70: "Under condition aggregation the only Holm cell is early minus late on posterior α … Dataset B is Holm-null in all eight confirmatory cells."
Conclusion p. 97: "The neurophysiological record answers two different questions, and the informative answer is the one at the event"; Discussion p. 91: "An estimand locked to the onset is therefore where the signal was found here." Discussion p. 83 itself warns: "They do not combine into one claim that the response depends on how and when the advertisement enters" — Conclusion p. 97 then writes "The neural response therefore appears to be concentrated at the point of insertion, where the two formats present the user with qualitatively different events."

**D4. Trajectory test labels.**
Methods p. 62: "Three further trajectory tests are declared and none of them is confirmatory."
Discussion p. 85: "The confirmatory tests on \(\delta^{(a)}_2\), late \(N_{\text{shift}}\), and \(\tilde\delta^{(a)}_2\) are Holm-null."

**D5. "Negative control declared in Table 6.1".**
Results p. 74: "which makes them the negative control declared in Table 6.1." Table 6.1 p. 60 row: "Genre trajectories, late \(N_{\text{shift}}\) | 54 | paired *t* on \(D_i\) … | 3 contrasts" — no control designation. (Only §6.2.5 p. 57 uses the phrase.)

**D6. Instrument failure vs "Not supported".**
Discussion p. 85: "That is a failure of the instrument on this corpus, not a demonstration that such a sequence does not exist."
Table 8.1 p. 92: RQ2 "Not supported", RQ4 "Not supported", with the caption rule "'Not supported' means no Holm-surviving cell."

**D7. Which test carries the \(\delta^{(a)}_2\) verdict.**
Methods p. 62: "the test is an exact McNemar test … computed on the conversations that disagree between the two conditions and reported with a paired t interval on \(D_i\)."
Table 7.5 p. 74 header: "Holm-adjusted paired t; McNemar for the two-condition rows" — the Holm column is the *t*, the McNemar *p* is raw and absent for "Early pooled − a∅"; Table 7.8 quotes "Holm p = .94" (the *t*).

**D8. Dataset A: three or four contrasts.**
Table 6.1 p. 60: "3 contrasts, separately within each measure."
§6.3 p. 61: "( ¼, ¼, ¼, ¼, −1 ) pools advertisements against a∅, ( ½, ½, −½, −½, 0 ) is implicit against explicit, ( ½, −½, ½, −½, 0 ) early against late, and (1, −1, −1, 1, 0) the presentation-by-timing interaction." No EEG interaction result appears in Fig 7.7, Fig 7.8, Table 7.8 or Appendix D.

**D9. Behavioural interaction has no home.**
Results p. 65: "Format × timing is null on all four outcomes (\|dz\| ≤ 0.06)."
Table 6.1 p. 60 behavioural row: "3 planned contrasts within each of the four primary outcomes" (16 total, all listed in Table 7.2; no interaction). The claim feeds Table 8.1 RQ5 and the Abstract.

**D10. Behaviour × EEG multiplicity.**
Methods p. 59: "each behaviour × EEG pair is evaluated on both, Holm within the six for each score, and a cell that survives is also reported Holm-corrected across the twelve."
Fig 7.13a p. 77 inset: "Holm p = 0.0004 (within six)"; Table 7.8 p. 78: "Behaviour × EEG | 18 | 6 | 0; 1". The across-twelve value is never printed.

**D11. Four quantifications of one untabulated share.**
Results p. 66: "including about half of those who had not noticed the implicit mention." Abstract: "more than half of those who initially failed to notice the mention recognised it." Discussion p. 82: "more than half of the participants who had not reported the mention." Conclusion p. 96: "most of those participants recognised it when shown again." No table gives the count.

**D12. Demographics: undeclared, then in the Abstract.**
Table 7.9 title p. 79: "Sensitivity and exploratory checks that are not families in Table 6.1" — contains "Demographic moderation (mixed model) | 54 | 70 + 70 | 0."
Abstract: "neither personality nor demographics moderated any outcome." Also "any outcome" overreaches: §7.3 tests four primary outcomes plus cued memory; secondary qualities and trust-on-re-exposure are never tested for moderation.

**D13. "Not a test" that is Holm-corrected.**
Results p. 75: "This is not a test but rather a check whether \(f_{\text{genre}}\) registers any change." Same page: "general guidance and information, 0.478 to 0.211 (dz = −1.00, Holm p < .001)"; Table 7.8 row "\(\hat g_1\) vs \(\hat g_4\) (instrument check) | 54 | 6 | 4."

**D14. Leftover names.** Discussion p. 85: "None of them differed by presentation, by timing, or against a∅, on either path." Methods p. 61: "k = 37 makes that an equal-n cell." Otherwise "condition aggregation" is used consistently; no "Path A/B" or "condition state" found; "Wilcoxon Holm" does not occur.

**D15. Numbers first appearing in the Discussion.**
"participant ICC .39" (p. 81); "absolute δ rises by 4.60 dB" (p. 84) — Table 7.8 gives only "relative δ +0.19 [0.09, 0.29]" and Fig 7.8 gives only *p*; "staying inside \|dz\| ≤ 0.37" (p. 84); "at .80 and .83" (p. 88); "six nominal cells out of 96" (p. 85) is derivable, the others are not.

**D16. Post hoc trust cell without label in Abstract/Conclusion, and unstable across post hoc families.**
Abstract: "trust fell only under the early banner." Conclusion p. 96: "the one place trust falls below the advertisement-free condition is the early explicit banner (−0.69)."
Table E.6 p. 132 (four-way Holm): "Explicit early −0.69 … Holm p .031"; Table E.8 p. 133 (ten-pair Holm): "No ads − explicit early +0.69 … Holm p .078". Same pair, two verdicts; the Abstract picks the favourable one and drops "post hoc".

**D17. Notation claim about Theory that Theory does not support.**
Results p. 71: "Definition 6 is written here in a shorter form: \(\delta^{(a)}_k\) for the ad-associated shift \(\delta^{(a)}_k(a_k)\) (3.8)." Eq. 3.8 p. 15 already reads "\(\delta^{(a)}_k = I_k\,\delta_k\)"; no "\((a_k)\)" form exists in Ch 3. Table 4.4 and Table F.2 write "\(\delta^{(a)}\)" without index.

**D18. Theory cannot represent the late advertisement.**
Theory p. 13: "A = (a₁, a₂, …, a_{T−1}), a_k ∈ A ∪ {∅} where u_k → a_k → u_{k+1}." With T = 4 the sequence has slots 1–3; Methods p. 50 defines "a₄" throughout. The symbol A is also used for both the sequence and the set of advertisements in the same line.

**D19. Contribution claims a metric the Theory withholds.**
Intro p. 4: "expand the concept of intent and some novel metrics like attention shift." Theory p. 16: "we reserve the term attention shift for an ad-associated genre shift sub-case that can be causally attributed … outside the scope of the present thesis."

**D20. Trust "holds up" vs its interval.**
Discussion p. 81: "Trust holds up … participants ended the session trusting the assistant about as much as they trusted it without advertisements." Conclusion p. 96: "trusting the assistant similarly as they trusted it without advertisements."
Table 7.2 p. 66: "Trust | Any ad − no ads | −0.34 | [−0.71, 0.03] | −0.25 | .153 | .016 | .193" — a CI reaching −0.7 points and a raw Wilcoxon of .016.

**D21. Table 7.9 "Sig." column.** Caption of Table 7.8 (inherited by 7.9): "'Sig.' counts Holm-surviving tests." Table 7.9 row "Fallback label by turn | 54 | 2 | 2 | clustered logistic: turn β = 0.34 (p = .0003)" — raw *p*, not Holm.

**D22. Catalogue counts.** Table 4.1 p. 20: "Products 117,343 … Normalized categories 39." Table 4.2 p. 21: "Total 117,243"; Fig 4.1: "117,243 products"; Table 4.2 has 30 category rows.

**D23. Figure 8.1 caption vs figure.** Caption p. 89: "Asterisk: Holm p < .05." The rendered figure carries no asterisks; the text (p. 88) says "a filled orange triangle survived Holm correction." The figure also draws trust × posterior α under "Implicit − explicit" and "Early − late", which Table 6.1 does not declare (they are the 24-test check in Table 7.9), inside a figure titled "declared associations."

**D24. Abstract vs Discussion on format at onset.** Abstract: "with no comparable response at mention onset." Discussion p. 90: "a direct test of the two formats at onset did not survive correction, so the formats are not shown here to differ."

**D25. Conclusion claim with no referent.** Conclusion p. 98: "over a short session that cost is smaller than the debate around it suggests." No Results cell, no cited debate.

### RQ audit (Intro §1.3 vs Table 8.1)

| RQ | Asked (p. 3–4) | Answered as (p. 92) | Status |
|---|---|---|---|
| RQ1 | "How does … format affect the user's overall experience" | "Does format change the reported experience? Supported" | Answered; "how" → "does", "overall" → "reported" (acceptable narrowing) |
| RQ2 | "alter the trajectory of the conversation following the advertisement" | "Does format shift the conversation's genre? Not supported" on one cell (implicit − explicit early \(\delta^{(a)}_2\)) | **Redefined** (trajectory → one transition) and **mis-verdicted** (instrument admitted invalid, D6) |
| RQ3 | "How does the moment of insertion affect …" | Supported | Answered |
| RQ4 | "alter the trajectory …" | Not supported on \(\delta^{(a)}_2\) + late \(N_{\text{shift}}\) | Redefined; late \(N_{\text{shift}}\) is null by design (see C4); mis-verdicted |
| RQ5 | interaction on experience | Not supported, \|dz\| ≤ 0.06 | Answered from an untabulated, undeclared test (D9) |
| RQ6/7 | personality × format / timing | Not supported | Answered as asked |
| RQ8 | "How do format and timing manifest …" | "Partly" | Answered; rests on the .0496 boundary cell |
| RQ9 | response "at advertisement onset" vs subsequent report | Supported | Answered as asked; RQ text pre-commits to onset-lock, which weakens the "two scores evaluated, one selected" defence rather than strengthening it |

No RQ is left unanswered; there is no RQ10/11; task moderation is correctly not an RQ. Intro p. 3 says "so that chapter 7 can answer every one of them" — the answers are in Ch 8.

---

## Job 2. Findings

### CRITICAL

**C1. The Conclusion prescribes what the Discussion says was not tested, and what the design cannot separate.** (D1, D2.) Location: Ch 9 p. 96 "The prescription is about disclosure rather than placement"; p. 98 "an obligation to disclose, to be patient with monetisation rather than rush into the earliest turns." Problem: disclosure θ was never manipulated (θ moves with λ by construction, p. 57) and timing was a two-slot within-subject factor on user-side outcomes with zero clicks and no advertiser-side measure. "Be patient / don't rush the earliest turns" is a placement rule stated one sentence after "not a placement rule." Why it bites: a committee will read the Abstract and Conclusion first; the thesis's own §8.6 disowns both sentences. Change: delete the two prescriptive sentences and "providing evidence for serving policies" from the Abstract; keep "what it costs the user" as the frame the Discussion already sets.

**C2. The "signal is at onset" narrative inverts the confirmatory record and rests on one selected association.** (D3, D10.) Location: Conclusion p. 97, Discussion p. 91 "Onset-locked designs"; Abstract "candidate neural marker of a trust drop." Problem: the only Holm-surviving confirmatory EEG cell is Dataset A; all eight Dataset B confirmatory cells are null with 2–4 dB intervals. The onset story is carried by (i) an exploratory compositional cluster and (ii) trust × posterior α ρ = .80, which was one of twelve declared correlations (two scores × six pairs), for which the promised across-twelve Holm is never printed, and which is then re-found in a 16-test screen (Fig 7.13b) and sits inside the 2,560-test map. Selecting the score that worked and calling the other "ρ = .24" a contrast is post hoc estimand selection by result. Why it bites: RQ9 "Supported" and the Abstract's marker claim rest on this. Change: print the across-twelve Holm; state in Results that two scores were evaluated and one survived; move "candidate neural marker" to Future Work; rewrite the Conclusion paragraph so that the confirmatory verdict (condition aggregation moved, onset did not) is stated before the exploratory lean.

**C3. The 3 s retrieval wait on the advertised turn is unaddressed as a confound, and it sits inside the Dataset B pre-window.** Location: Ch 5 p. 39: "On the one advertised turn, retrieval runs before the first token (median 3.03 s), so that silent wait is about 6 s … the only ads-versus-no-ads difference in server wait." Nowhere in §6.2.5 "Structural confounds", §8.3, or §8.7. Problem: for the explicit banner, onset = reply + 0.49 s, so \(E^{\text{pre}} = [t−4, t)\) is almost entirely silent waiting at a static screen; the matched a∅ reply arrives ~2.7 s after send, so its pre-window includes the end of typing/sending. Your own positive control shows writing raises Fz θ by 0.60 dB and Discussion p. 84 admits a visual onset produces a low-frequency transient — so \(D^B = (\text{post}−\text{pre})_a − (\text{post}−\text{pre})_{a^\emptyset}\) differs in pre-state as well as post-event. For behaviour, a 6 s stall on exactly one turn is a plausible contributor to "pushing/steering" and "reliable responses" ratings. Also, §7.2.2 reports "Nine logged interaction measures … none with raw p < .05" — if reply latency is one of them, a designed +3 s on one of four turns should register; either the measure is not TTFT or the statement needs checking. Change: add the wait to §6.2.5 and §8.7; report TTFT by condition; for Dataset B, at minimum report the pre-window means by cell and discuss.

**C4. The trajectory family uses labels it disowns and returns verdicts on an instrument it declares invalid.** (D4–D7.) Location: Table 8.1 RQ2/RQ4 "Not supported"; p. 85 "confirmatory tests on … late \(N_{\text{shift}}\), and \(\tilde\delta^{(a)}_2\)"; p. 74 "negative control declared in Table 6.1." Problem: (i) 32.5% agreement with the runtime label (F.2), depth-tracking (Fig 7.11), 98/156 product titles labelled "general guidance" — the thesis itself calls this "a failure of the instrument." A failed instrument yields "not testable", not "not supported." (ii) Late \(N_{\text{shift}}\) vs a∅ compares whole-conversation shift counts of conversations that differ only after the last utterance; no effect can exist by construction. That is a fine negative control, but it is then used as RQ4 evidence, which is circular. (iii) The McNemar declared as the test is displaced by the paired *t* Holm in Table 7.5. Change: Table 8.1 RQ2/RQ4 → "Not testable with this instrument"; strike "confirmatory" from p. 85; drop late \(N_{\text{shift}}\) from RQ4 evidence; make Table 7.5's Holm column the McNemar or say explicitly why the *t* is the verdict.

### MAJOR

**M1. The interaction contrast exists in three states.** (D8, D9.) Declared with weights for EEG, never reported; undeclared for behaviour, reported as "\|dz\| ≤ 0.06" with no D, CI or *p*; then answers RQ5 and the Abstract. Add a row per outcome to Table 7.2 (D, CI, Holm *p*) and to Table 6.1; report or drop the EEG interaction. Note also that (1, −1, −1, 1, 0) is the full difference-of-differences, on twice the scale of the ½-weighted main effects; Methods never says so, and Table 8.1's "\|dz\| ≤ 0.06" hides the fact that no reader can compare its D to the −0.44 timing effect.

**M2. Nulls are read asymmetrically.** Dataset B: "failure to reject on the confirmatory pair is not evidence of absence" (p. 84) and "A late implicit mention lowering … is therefore a target for replication" (p. 85, from Holm-null leans). Behaviour: "Trust holds up" (p. 81), "Who the user is does not seem to change what the advertisement costs them" (p. 82), "null tightly" (p. 81); Abstract "neither personality nor demographics moderated any outcome." The trust any-ad CI is [−0.71, 0.03] with raw Wilcoxon .016; the extraversion × timing slope on trust is −0.46 [−0.83, −0.10] per BFI point — an interaction as large as the timing main effect, Holm .20. Neither licenses "holds up" or "does not matter." Apply one rule: a Holm-null with a wide CI is "not detected" in every chapter, including the Abstract.

**M3. Implicit onset validity is not established, yet the Abstract compares formats at onset.** (D24.) Ch 4 p. 35: onset for the mention is "the injection event plus 1.57 s, which lands before the reply has finished streaming; 30 of the 36 implicit onsets are reconstructed this way"; Methods p. 51: the mention "may appear at the beginning, in the middle, or at the end." So the 4 s post-window is locked to when the model *was told* to advertise, not when the product sentence was rendered or read. For a mention at the end of a long reply the window may contain no advertisement. Explicit onset is an observed marker on a painted object. The Abstract's "no comparable response at mention onset" compares an event with a non-event. Change: state this in §8.7 (currently only the 0.43 s p95 is given) and in Results 7.4; remove the format comparison at onset from the Abstract.

**M4. The ocular argument cites evidence that is not on the page.** Discussion p. 84: "Removing ocular components is the preprocessing choice that could have created the tilt. Leaving blinks in dilutes it and widens its spread, which is the opposite of an ocular-only account (Appendix D.1)." Appendix D.1 says only "Rerunning without ICA … does not change the 4 s confirmatory family" — the tilt is exploratory and no no-ICA numbers for it appear. Further: no EOG; ICA proxy is Fp1/Fp2 mean (blink-oriented, weak for the lateral saccade a new banner invites); ≤3 components; a 1,050 µV peak-to-peak bound passes every blink. "Dilution" when blinks are left in is compatible with blink variance widening both cells, not with a non-ocular origin. Conclusion p. 97 upgrades this to "a measurable neural signature." Add the no-ICA tilt estimates to Appendix D or drop the sentence; keep "neural" out of the Conclusion for this cell.

**M5. The Holm-within-measure rationale is statistically wrong, and it lowers the bar the exploratory tilt then clears.** §6.3 p. 61 and D.2 p. 125: "the five relative powers share a denominator and cannot move independently, so correcting across all sixteen would distort the family as much as ignoring multiplicity would." Holm controls FWER under arbitrary dependence; dependence makes it conservative, it does not "distort" it. The real effect of the choice is 16 families of 3–4 tests instead of one family of 56, so exploratory Holm *p* of .004–.026 are reported on a board where the burden is stated but never quantified (Table 7.8: 98 tests, 7 survivors, five compositional). The tilt then reaches the Abstract without the word "exploratory." Fix the rationale; state in Results what fraction of 98 would survive a single family; label the tilt exploratory wherever it appears.

**M6. Order/priming is admitted but never modelled for behaviour.** §8.7 p. 93: "in the later conditions they could anticipate being asked whether the assistant had pushed a product." The a∅ conversation is in a random position, so in ~80% of participants at least one advertised condition (and its "pushing/marketing", "sponsored buttons" items) precedes it. Session position is a covariate in the trajectory GEE and Kruskal–Wallis but appears nowhere in the behavioural LMM. The "different chatbot" warning addresses anchoring on the assistant, not learning what the questionnaire asks. Report the a∅ outcome means by session position, or add position to the LMM.

**M7. Latin square asserted, never shown; task never modelled for behaviour.** Methods p. 55: "the two sequences were then paired so that, across participants, task identity is not confounded with condition." With N = 54, five tasks, five conditions and independent shuffling, the 5 × 5 task × condition table is balanced only in expectation; it is never printed. §8.2: "Task type is not modelled as a moderator either." Product category is fixed per task (p. 22) and product quality is "mostly unknown" (p. 93), so task carries the advertisement's relevance. Print the realised table; add task to the LMM as a check.

**M8. Pooling of arms is defended only by an interaction test.** "The two arms run parallel and are pooled; arm is not a factor in the family" (p. 82, p. 93). Evidence against homogeneity on the page: notice α .70 lab vs .56 crowd (Table E.3); extraversion 3.39 vs 2.78 (raw .039); crowd age unknown for 10/36; crowd device, screen, and setting unknown. The "Environment" moderation row tests only whether contrasts differ by arm, not whether the a∅ baseline does. Add arm as a main effect in the LMM check and report whether any Holm verdict changes.

**M9. Discussion and Abstract carry numbers that Results does not.** (D11, D15.) ICC .39, 4.60 dB, \|dz\| ≤ 0.37, partial .83, and the "about half / more than half / most" share. Either add to Ch 7 tables or delete from Ch 8/9/Abstract.

**M10. The boundary cell is over-weighted in the Abstract.** "posterior α power was lower for early than for late insertion" is stated as a fact with no estimand label, no *p*, no depth caveat; Fig 7.8 prints ".050". The Discussion's own caveat ("how much of it belongs to the insertion and how much to how far the conversation had travelled is not separable") must travel with the number. Also note from Fig 7.7 that early−late Fz θ under condition aggregation is negative with a CI ending near zero; a late window that reaches into the written conclusion (write−read: +0.60 dB) makes depth a live explanation for both markers.

**M11. Reproducibility claims exceed the page.** Abstract/Conclusion: "the multimodal datasets are released openly" / "the linked behavioural and EEG dataset." The PDF gives one GitHub URL for the platform [61]; no dataset DOI, licence, or location. Not given: permutation/bootstrap seeds (only "seeded"), LMM fixed-effect list and estimation, GEE working correlation, which demographics are the "collapsed covariates" in the personality model, the Kislov "central-site" channel set, which Latin square. Ambiguity in the confirmatory Dataset A cell: "for a∅, the matched turn-2 and turn-4 replies" (p. 36) — two onsets, one \(Y_{A,i,a^\emptyset}\) cell of 37 epochs; which neighbourhood, or the union, is not stated.

**M12. Theory formalism does not contain the experiment.** (D17–D19.) A has T−1 slots so a₄ is outside it; A is both sequence and set; "attention shift" is listed as a delivered metric in the Contributions. Definition 3 "length of the maximal contiguous run of g(i)" is ambiguous when a genre has several runs (Table 4.4 silently uses \(R_{\max}\)). Definitions 1–6 are otherwise internally consistent: indices *k* (time) and *i* (genre) are kept apart, \(\tilde\delta^{(a)}_k \le \delta^{(a)}_k \le \delta_k\) holds, and the \(k \in [1, T−1]\) range is consistent with \(u_5\) not existing.

### MINOR

- Broken cross-references: "Equation 4.2.4" (pp. 61, 70, ×4), "Figure 4.2.4" (p. 122, ×3), "Figure 4.2.3" (p. 27), "Figure 4.1.2" (p. 43), "Figure Figure 5.3" (p. 46), "subsection 5.2.1" for the cross-encoder (p. 45) — §5.2.1 "Model choices" is empty and Embedding/Reranker sit under §5.2.2 "Conversational LLM".
- Truncated sentence p. 40: "The waiting room is therefore at most 1".
- "borderline significant after correction" (p. 65), "borderline significant also with credibility and manipulation" (p. 76) — language the thesis's own framework forbids.
- Fig 7.12 caption "Filled circles: condition aggregation; hollow squares: onset-lock"; Fig 7.13 caption "squares: onset-lock; hollow circles: condition aggregation" — rendered 7.13b shows filled squares and hollow circles; one caption is wrong.
- "\(\delta^{(a)}_2\) score takes four values" (p. 77): \(D_i = \tfrac12(\delta^{\text{imp}}+\delta^{\text{exp}}) − \delta^{\emptyset}\) takes five (−1, −½, 0, ½, 1).
- Table 7.1: the test behind "*p*" and "*p*Holm" for arm comparisons is not named.
- "one in five to one in four for the labelled banner" (p. 80): from Fig 7.4, 19% and 26% — fine; from Table E.2 "Notice outcome", 26% and 31%. Say which item.
- 5.1.1 "200k Item Vector Database" vs 117k; 4.1 "(+20)" categories vs "39" vs 30 rows.
- Appendix C.6 deception text tells participants "here is what we instructed ChatGPT to do … and to personalize its response to the user" — the system was Qwen and φ = session (no personalisation). Copied from Tang et al.; a committee member on ethics will notice.
- D.1 Table D.1 caption "Bold rows survive Holm" — both rows have Holm < .05; the extraction cannot show bold, so state it in text.
- "It has been proven that the usage of intent and genres allow for response-decoupled and bidding-decoupled ad allocations" (p. 13) — [8] proposes, it does not prove.
- Related Work register: "barely nobody would click", "92%!", "9.5%!", "Opus 4.5 did it 98% of the time!" — remove exclamation marks and colloquialisms.

### VERIFY

- Table 7.8 "Behaviour × trajectory × EEG | 3 | 0 | partial ρ = .80": a partial ρ of .80 at *n* = 18 has *p* ≈ 10⁻⁴; either it was not tested or "Sig." is wrong.
- Whether "reply latency" among the nine logged measures is TTFT or completion time, and why no raw *p* < .05 given the designed +3 s (C3).
- Whether the late-ad 37-epoch neighbourhood overlaps the written conclusion, and the share of writing epochs by condition (M10).
- Where "participant ICC .39" for trust comes from (not in Table 7.9's reliability row).
- The a∅ Dataset A neighbourhood definition (M11).
- The realised task × condition and condition × position tables (M6, M7).
- Whether the no-ICA branch changes the explicit-early tilt (M4).

---

## Top 5 vulnerabilities (what an examiner will ask aloud)

1. "Your §8.6 says 'This is not a recommendation to serve advertisements late or implicitly' and that disclosure 'was not tested'; your Conclusion tells platforms to disclose and not to rush the earliest turns. Which chapter should we grade?"
2. "Your only Holm-surviving confirmatory EEG cell is under condition aggregation and all eight onset-locked confirmatory cells are null — on what confirmatory basis does the Conclusion say the informative answer is 'at the event'?"
3. "The advertised turn stalls about three seconds longer before the first token, and your onset-locked pre-window sits inside that stall while the matched no-ad pre-window includes typing. Why is the slow-power tilt not a wait-versus-typing artefact?"
4. "ρ = .80 was one of twelve declared correlations; Methods promised a Holm across the twelve that never appears, and the same pair is re-tested against sixteen measures and inside a 2,560-test map. Why is this a finding rather than a selection?"
5. "Your genre classifier agrees with the runtime label on 32.5% of utterances and, by your own account, tracks turn depth rather than the advertisement. Why does Table 8.1 say RQ2 and RQ4 are 'Not supported' rather than 'not testable'?"

## Three strongest aspects

1. **Test accounting.** Table 6.1 → Tables 7.8/7.9 → Table 8.1 is a complete ledger: every declared family with *n*, tests, survivors and location, plus every sensitivity and exploratory check down to the 2,560-test map and its expected false-positive count (105 vs 128). Three estimators on all sixteen behavioural contrasts, leave-one-item-out, and raw-Wilcoxon discipline are above the master's norm.
2. **EEG pipeline transparency.** Condition-blind channel QC on twelve windows placed without the event log, named ICA thresholds (0.35 correlation, 1.5× frontal weight, ≤ 3 components, 99% variance), a no-ICA mandatory branch, the "induced spectrum, not ERP" argument tied to the measured onset jitter, decibel semantics spelled out, and off-4 s cells quarantined in an appendix rather than harvested.
3. **The trajectory chapter as an honest failure report.** The fallback-by-turn clustered logistic model, the six-window context sweep with recipes stated, the 98/156 "general guidance" admission, and F.2's saturation-vs-floor diagnosis are exactly the diagnostics an instrument failure requires — the problem is only that Table 8.1 does not carry the verdict the chapter earns.

## Scores (1–10)

| Dimension | Score | One-line reason |
|---|---|---|
| Research question / contribution | 7 | Real gap (LLM ads × EEG × user cost); user-centric frame is right; theory contribution over-claimed in the Intro |
| Design | 5 | Within-subject 2×2+control is sound; θ/λ, depth, latency and order confounds are only partly declared and never modelled for behaviour; one trial per Dataset B cell |
| Statistical validity | 6 | Participant-as-unit and Holm discipline are correct; two-score selection, Holm-within-measure rationale, McNemar/t displacement, and asymmetric null reading cost points |
| Technical correctness | 6 | Definitions, \(D_i\), *t*, \(d_z\), KV-cache arithmetic check out; A has T−1 slots, notation drift, catalogue counts, broken refs |
| Results / interpretation discipline | 5 | Results mostly clean; Discussion introduces new numbers; Abstract and Conclusion interpret beyond Ch 8 and contradict it |
| Internal consistency | 4 | 25 documented disagreements, four of them between Conclusion/Abstract and Discussion on the central claims |
| Reproducibility | 5 | Pipeline thresholds excellent; no dataset location, no seeds, model specifications missing |
| Writing | 6 | Methods/Results/Discussion prose is disciplined; Related Work and System chapters are informal and error-prone; cross-referencing broken |
| **Overall, as it stands** | **5.5** | Publishable core buried under a Conclusion that overrides its own Discussion |

## Examiner verdict

I would challenge this thesis on the gap between what Chapter 8 permits and what the Abstract and Chapter 9 assert. Chapter 8 is careful: it separates the two EEG estimands, refuses to combine them, refuses a serving recommendation, admits the trajectory instrument failed, and tells the reader to carry the lower bound of the ρ = .80 interval. Chapter 9 then prescribes disclosure and patience, declares the neural signal to be "at the event" against a confirmatory record that says the opposite, calls a trust CI reaching −0.7 points "similar", and labels the trajectory nulls as verdicts. Beneath that, three design issues are undeclared or under-declared and would be my substantive line of questioning: the 3 s retrieval stall that sits inside the onset-locked pre-window, the reconstructed implicit onset that may not contain the mention, and the untabulated interaction that answers RQ5. The statistical framework, the EEG pipeline description and the trajectory diagnostics are strong enough that the fix is editorial rather than analytical: make the Abstract and Conclusion say only what Table 7.8, Table 8.1 and §8.6 already say, add the four missing numbers and the two missing covariate checks, and the thesis holds.

## Rest of the thesis — suggestions

- **Introduction.** Contribution list (p. 4) claims "novel metrics like attention shift" and §1.2 promises "prescriptions for how companies could steer their advertisement policies"; both contradict Ch 3 and §8.6. Align with the user-cost frame the Abstract's first paragraph already uses.
- **Related Work.** Remove exclamation marks and colloquialisms; "This work will serve as the statistical foundation of our analysis" for Tang et al. is fine, but say which items were dropped and why (the Methods do).
- **Theory.** Extend A to T slots or state that a late ad is \(a_T\) outside the trajectory formalism; rename the set of advertisements; define \(R_{\max}\) explicitly; soften "It has been proven."
- **Datasets.** Reconcile 117,343 / 117,243 and 39 / 30 categories; Table 4.6's \(K_c\) column shows whole-window counts (238, 162 …) in a table said to hold the confirmatory 37-epoch cells — label which; state the a∅ neighbourhood.
- **System.** Fill or delete §5.2.1; fix the truncated waiting-room sentence; move the latency paragraph's confound consequence into Methods §6.2.5; Figure 5.1 is a third-party model diagram and adds nothing to a reproducibility argument.
- **Methods (rest).** Add the interaction row to Table 6.1 or remove the weight vector; add "demographic moderation" as a declared family or keep it out of the Abstract; name the LMM covariates.
- **Appendices.** C.6: the deception text names ChatGPT and personalisation — either what participants saw needs a footnote that it was inherited wording, or it is an ethics-form discrepancy the committee should hear from you first. D: add Kislov channel set and the no-ICA tilt numbers. F: fine as is.
