# Jury v1 — Kimi K3 Max (15 Sep 2026)

Thesis: v1 PDF 156 pp (`docs/overleaf/thesis/_build/dissertation.pdf`).
Prompt: `../2026-09-11-thesis-review-metaprompt.md`.
In-IDE / extra dump (not one of the five web juries). Raw examiner
dump. Do not treat its table cells as Gold. Do not apply until
Walter says so.

---

Review complete — I read the full 156-page PDF (cover through appendices) and verified every quoted claim against the text and, where notation mattered, the LaTeX source. Figures were read via text extraction: I could not visually inspect Figure 7.2 (distributions), the point-estimate positions in Figure 7.7, or the triangle sizes in Figure 8.1; where those carry numbers I relied on the text and tables, and I say so below. What follows is the examiner report.

---

# External examiner report — *The Price of Attention* (v1, 15 Sep compile)

## Job 1 — Cross-document consistency audit

Documents audited: Table 6.1 (analysis families), Results Ch 7 incl. Tables 7.8/7.9, Discussion Ch 8 incl. Table 8.1, Abstract, Conclusion Ch 9.

| Family | n | Tests | Estimator | Correction | Headline number | Verbal claim (surface) | Agreement |
|---|---|---|---|---|---|---|---|
| Behavioural battery | 54 | 16 | 1-sample paired \(t\) on \(D_i\); Wilcoxon raw; LMM check | Holm within outcome (3 per primary outcome, 2 per cued item) | notice any-ad \(+2.07\) [1.53, 2.62], Holm \(<.001\) | "Any advertisement raised perceived manipulation by +1.27" (Abstract) | Numbers agree across 6.1/7.2/7.8/8.1/9.1. Two exceptions: the format×timing interaction is reported but homeless (D3); the post-hoc explicit-early trust cell is promoted in Abstract/Conclusion without its post-hoc label (D16) |
| Personality moderation | 54 | 60 | random-intercept LMM, one trait at a time | Holm within outcome across 15 | nearest: extraversion on credibility early−late, Holm \(=.18\) | "neither personality nor demographics moderated any outcome" (Abstract) | Agree; well-bounded in 8.2/9.1. But Table 6.1's "demographics as covariates" describes a model never reported (D5) |
| Demographic moderation | 54 (51/49) | 70 + 70 | one-factor-at-a-time LMM, joint Wald | Holm within outcome | nearest: cued memory early−late by familiarity, Holm \(=.44\) | same null claim (Abstract/9.1) | **Missing from Table 6.1 and Table 7.8**; exists only in §7.3/Fig 7.6/Table E.10 and Table 7.9 ("checks that are not families in Table 6.1") (D5) |
| Free-text | 54 | – | collected, not analysed | none | – | – | Consistent |
| Dataset A (condition aggregation) | 18 | 6 | 1-sample \(t\) on \(D^A_i\); Wilcoxon raw | Holm within measure | early−late posterior \(\alpha\) \(-0.22\) dB [−0.39, −0.04], Holm \(=.0496\) | "posterior α power was lower for early than for late insertion" (Abstract) | Methods prose declares **four** weights incl. the interaction; Table 6.1 and Results carry three; the interaction is never reported (D3). Width-fragility disclosed only opaquely (D10); Fig 7.8 prints ".050\*" (D11); Abstract drops the depth confound (D16) |
| Dataset B (onset-locked) | 18 | 8 | 1-sample \(t\) on \(D^B_i\); Wilcoxon raw | Holm within measure | nearest: implicit-late Fz \(\theta\) \(-1.38\) [−2.80, 0.04], Holm \(=.22\) | "the eight confirmatory cells are Holm-null" (9.1) | Internally consistent — but see CRITICAL 1 (latency/pre-window confound absent from Methods/Discussion) |
| Positive control (write−read) | 18 | 2 | 1-sample \(t\) | Holm across 2 | Fz \(\theta\) \(+0.60\) [0.22, 0.97], Holm \(=.007\) | "writing a message raises Fz θ over reading one" (9.1) | Consistent. 9.1 overgeneralises the control to "the instrument"; 8.3 correctly restricts it to Fz \(\theta\) (posterior \(\alpha\) did not separate writing from reading) |
| Exhaustive pairwise, post hoc | 18 | 256 | \(t\) on every pair | Holm within measure | Fz \(\theta\) IE−EL \(-0.28\), Holm \(=.014\) | "a target for replication, and not a result of this study" (8.3) | Consistent; labelling discipline good |
| 14 exploratory EEG measures | 18 | 98 | same \(t\) | Holm within measure | explicit-early rel. \(\delta\) \(+0.19\) [0.09, 0.29], Holm \(=.004\) | "a transient slow-power tilt … was observed" (Abstract) | Consistent in Ch 7/8; Abstract drops the "exploratory" label that 9.1 carries (D16) |
| Trajectories \(\delta^{(a)}_2\) | 54 | 4 | **Table 6.1: exact McNemar + paired-\(t\) interval** | Holm across 4 | early pooled \(+0.046\) [−0.082, 0.174], Holm \(=.94\) | "No advertisement effects were detected in the intent trajectories" (Abstract) | **Estimator ambiguity**: Table 7.5 Holm-adjusts the \(t\), leaves McNemar raw (D4) |
| Trajectories late \(N_{\text{shift}}\) | 54 | 3 | paired \(t\); Wilcoxon raw | Holm across 3 | late pooled \(-0.074\) [−0.361, 0.213], Holm \(=1.00\) | "Not supported" (Table 8.1, RQ4) | Consistent |
| \(\tilde\delta^{(a)}_2\) permutation | 54 (108 conv.) | 1 | one-sided permutation of \(g^{(a)}\), 20,000 seeded draws | uncorrected | 9 vs 10.46 expected, \(p=.80\) | "occurred nine times against the 10.46 expected by chance" (9.1) | Consistent; conversation-level exception acknowledged (§6.3 Unit bullet) |
| \(\hat g_1\) vs \(\hat g_4\) instrument check | 54 | 6 | paired \(t\) on shares; Wilcoxon raw | Holm across six genres | guidance 0.478→0.211, \(d_z=-1.00\), Holm \(<.001\) | "the classifier is not silent; it is reading something else" (8.4) | Consistent; called "not a test but rather a check" (7.5) yet Holm-corrected and counted as a family in Table 7.8 (minor) |
| Kruskal–Wallis (conversation grain) | 270 rows | 12 | KW | exploratory, ICCs reported | \(N_{\text{shift}}\) by condition \(H=2.89\), \(p=.58\) | – | Consistent; declared exploratory with participant ICCs (Table F.2) |
| Behaviour × EEG | 18 | 6 pairs × 2 scores | Spearman | Holm within six per score; survivors "also reported Holm-corrected across the twelve" | onset-locked trust × posterior \(\alpha\) \(\rho=.80\) [.48, .93], Holm \(=.0004\) | "a candidate neural marker of a trust drop" (Abstract) | The across-twelve report is promised in §6.3 and never appears (D6). Table 7.8 "Tests = 6" undercounts the 12 tests run; "Sig. 0; 1" is unexplained in the caption (minor) |
| Behaviour × trajectory | 54 | 6 | Spearman | Holm within family | manipulation × late \(N_{\text{shift}}\) \(\rho=.22\), Holm \(=.67\) | "Genre trajectories join neither side of the triangle" (8.5) | Consistent |
| Trajectory × EEG | 18 | 2 | Spearman | Holm within two | Fz \(\theta\) × \(\delta^{(a)}_2\) \(\rho=.47\), Holm \(=.095\) | "The Fz θ cell does not hold" (7.6.3) | Consistent |
| Behaviour × trajectory × EEG | 18 | 3 | Spearman + partials | Holm within 3 | **Sig. 0, yet key estimate "partial \(\rho = .80\)"** | "leaves that association where it was, at .80 and .83" (8.5) | **Unreconciled** (D7); ".83" appears nowhere in Ch 7 (D8) |

### Disagreements found (each with two quoted locations)

**D1 — Conclusion prescribes what the Discussion explicitly refuses.**
- Ch 9.1: *"What follows for a platform that wants to keep the trust of the people it serves is not a placement rule but an **obligation to disclose**, **to be patient** with monetisation rather than rush into the earliest turns simply because they command attention, and **to measure**."*
- Ch 8.6: *"**This is not a recommendation to serve advertisements late or implicitly**. The design did not measure the advertiser's side at all, and about half the participants did not report the implicit mention as sponsored, which raises a disclosure question this study did not test."*

**D2 — The same recognition share escalates across documents.**
- Ch 7.2.2: *"including about half of those who had not noticed the implicit mention."*
- Ch 8.1: *"more than half of the participants who had not reported the mention as sponsored during the conversation still recognised it afterwards"*; Abstract: *"more than half of those who initially failed to notice the mention recognised it when shown again"*; Ch 9.1: *"most of those participants recognised it when shown again."* Four surfaces, three quantifiers ("about half" → "more than half" → "most") for one count that is not printed anywhere.

**D3 — The format × timing interaction has no family, no table cell, and no \(p\)-value.**
- Ch 6.3: *"the Dataset A weights are fixed in advance: … and \((1, -1, -1, 1, 0)\) the presentation-by-timing interaction."* vs Table 6.1, Dataset A row: *"3 contrasts, separately within each measure."*
- Ch 7.2.1: *"Format × timing is null on all four outcomes (\(|d_z| \le 0.06\))"* — no row in Table 7.2, no \(p\), no correction label — while Table 8.1 answers RQ5 with *"interaction estimated on the four post-condition outcomes and null on all four, \(|d_z| \le 0.06."* The EEG interaction declared in Methods is reported nowhere.

**D4 — \(\delta^{(a)}_2\) family: McNemar named as the test, the \(t\) is what gets Holm.**
- Table 6.1: *"exact McNemar; paired \(t\) interval on \(D_i\)"*; §6.3: *"the test is an exact McNemar test … reported with a paired \(t\) interval."*
- Table 7.5 caption: *"Holm-adjusted paired \(t\); McNemar for the two-condition rows"* — the "Holm \(p\)" column is the \(t\); McNemar \(p\) is raw. Table 7.8's headline (*"Holm \(p=.94\)"*) is the \(t\), not the estimator Methods names.

**D5 — The demographics family is absent from the Methods contract and misdescribed where mentioned.**
- Table 6.1, personality row: *"random-intercept linear mixed model with BFI-10 trait × contrast interactions, demographics as covariates."*
- Ch 7.3: *"Sex, education, chatbot familiarity, use frequency, and environment each entered the same random-intercept model one at a time … 0 of 70 factor × contrast cells survive Holm"* — a separate one-at-a-time joint-Wald family, not covariates; it appears in Table 7.9 under *"checks that are not families in Table 6.1"* and is missing from Table 7.8's declared families.

**D6 — A promised correction is never reported.**
- Ch 6.3: *"each behaviour × EEG pair is evaluated on both, Holm within the six for each score, and a cell that survives is also reported Holm-corrected across the twelve."*
- Ch 7.6.1 / Fig 7.13a: *"\(\rho=.80\), raw \(p=6\times10^{-5}\), Holm \(p=.0004\)"* / *"Holm \(p=0.0004\) (within six)"* — no across-twelve value appears anywhere. (It would still survive; the promise is simply unkept on the page.)

**D7 — Table 7.8 reports Sig. = 0 for a family whose key estimate is partial \(\rho = .80\).**
- Table 7.8: *"Behaviour × trajectory × EEG | 18 | 3 | **0** | trust × posterior \(\alpha\) given \(\delta^{(a)}_2\), partial \(\rho=.80\)."*
- Ch 8.5: *"Partialling the trajectory score out of trust × posterior α leaves that association where it was, at .80 and .83."* A partial \(\rho\) of .80 at \(n=18\) would ordinarily survive Holm-within-3 by a wide margin; either the count, the estimate, or the (undocumented) partial-correction test is wrong. Meanwhile the Discussion uses the partialled value defensively without disclosing the family's Sig. = 0.

**D8 — Discussion introduces numbers that exist nowhere in Results.**
- Ch 8.3: *"absolute \(\delta\) rises by \(4.60\) dB"* — no such cell in Ch 7 or in Appendix D (Table D.2's nearest entry is \(-3.64\) dB for a different pair); Fig 7.7's onset panel spans only ±3 dB and shows only the confirmatory pair.
- Ch 8.1: *"(participant ICC .39)"* — not in Ch 7. Ch 8.3: *"staying inside \(|d_z| \le 0.37\)"* — not in Ch 7. Ch 8.5: *".80 and .83"* — the .83 is not in Ch 7.
- Against Ch 7.7's own completeness claim: *"Table 7.9 does the same for every reported sensitivity or exploratory check, so that nothing in this chapter is omitted from the tables."*

**D9 — The same 0.43 s is two different statistics.**
- Ch 4.2.4: *"uncertain to about 0.23 s for explicit banners and 0.43 s approximately for implicit mentions. Those figures are leave-one-out estimates of the reconstruction error."*
- Ch 8.7: *"with a 95th-percentile uncertainty of 0.43 s."*

**D10 — The width-fragility of the one confirmatory EEG survivor is never stated in text.**
- Ch 7.4: *"Epoch-width branches that leave 4 s are in Appendix D; they do not revise the 4 s family."*
- Table 7.9: *"Epoch width and cleaning | … | the 4 s family does not hold at other widths."* The fate of the posterior \(\alpha\) early−late cell at 2/8/16/32 s is printed nowhere; only the two off-width Dataset B cells are tabulated (Table D.1).

**D11 — Figure 7.8 prints ".050" with a "Holm \(p<.05\)" asterisk.**
- Fig 7.8 (`eeg_holm_board_4s.pdf`): *"Posterior α \(*\) .97 .97 .050 …"*
- Ch 7.4 / Table 7.8: *"Holm \(p=.0496\)."* A reader sees an asterisk on ".050", which as printed is not \(<.05\).

**D12 — Results misquotes Theory's notation.**
- Ch 7.5: *"Definition 6 is written here in a shorter form: \(\delta^{(a)}_k\) for the ad-associated shift \(\delta_k(a_k)\) (3.8)."*
- Theory (3.8): \(\delta^{(a)}_k = I_k\,\delta_k = I_k\,\mathbb{I}[\hat g_{k+1} \neq \hat g_k]\) — Theory already writes \(\delta^{(a)}_k\); the symbol \(\delta_k(a_k)\) appears nowhere in Ch 3. (Similarly \(g^{(a)}_k\) in Ch 3 loses its subscript in Table 6.1/§7.5, *"permutation of \(g^{(a)}\)"*.)

**D13 — Broken cross-references in the compiled PDF.**
- Appendix D: *"Figure 4.2.4 states the recording hardware and Figure 4.2.4 the cleaning chain."* (section labels rendered as figures; again in D.2).
- Ch 6.3: *"the number itself is fixed in Equation 4.2.4"*; Ch 7.4: *"dataset A is condition aggregation Equation 4.2.4) and dataset B is onset-locked Equation 4.2.4)"* (dangling parenthesis; lowercase "dataset").
- Ch 9.1: *"the insertion event itself 8.7, where the temporal relationship … can be preserved"* (bare ref; the sentence also lacks its final period); Ch 8.6: *"taken into account 8.7."*

**D14 — Conclusion asserts an absence the Discussion refuses.**
- Ch 9.1: *"a transient slow-power tilt \((\uparrow\delta,\theta;\downarrow\alpha,\beta)\) that the implicit mention **does not produce**."*
- Ch 8.3: *"the implicit-early cell shows nothing comparable … so what stands is the explicit-early response against its own control and **not a demonstrated difference between the two formats**"* and *"failure to reject on the confirmatory pair is not evidence of absence."*

**D15 — Conclusion states the trajectory null as a fact about the world.**
- Ch 9.1: the cost is *"not a collapse of trust and not a conversation steered towards the product."*
- Ch 8.4: *"That is a failure of the instrument on this corpus, not a demonstration that such a sequence does not exist."* (9.1's own steering paragraph complies; the closing "overall picture" paragraph does not.)

**D16 — The Abstract drops labels and confounds that Ch 7/8 attach to the same cells.**
- Abstract: *"trust fell only under the early banner"* — that cell is post hoc (Fig 7.3 caption: *"Post hoc"*; Ch 8.1: *"a single cell of the post hoc grid"*).
- Abstract: *"a transient slow-power tilt … was observed"* — exploratory battery (9.1 says *"on the exploratory battery"*; the Abstract does not).
- Abstract: *"posterior α power was lower for early than for late insertion"* — Ch 8.3 attaches the confound: *"timing under condition aggregation is confounded with conversational depth"* (9.1 carries it; the Abstract does not).

**D17 — Catalogue size disagrees with itself.** Table 4.1: *"Products 117,343"* vs Table 4.2: *"Total 117,243"* vs Fig 4.1: *"117,243 products."*

**Passes recorded:** "Holm \(p\)" is never mixed with Wilcoxon (raw everywhere); no "Wilcoxon Holm"; "condition aggregation" is the only Dataset A name (one descriptive "equal-\(n\) cell" in §6.3, no "Path A/B" or "condition state"); contexts, not "labellings"; outcomes, not "composites"; "\(u_5\) does not exist" once (§7.5); nine RQs, no RQ10/11; task moderation is not an RQ; every Abstract/Conclusion number I tested traces to a Results cell except the items in D2/D8. The "depends on how and when" fusion is explicitly refused (8.3), as is "captured attention" (8.6) and "greater visual processing" (never written).

---

## Job 2 — adequacy sweep (compact verdicts)

**Design/confounds.** Order/carry-over: *partially* — mitigation by design is well argued (§6.2.5) and honestly bounded in §8.7 ("spread … rather than removing it"), but no session-position check on the behavioural outcomes is reported (position is tested only for \(N_{\text{shift}}\), \(p=.52\)). Latin square: *partially* — tasks Latin-squared, conditions shuffled independently, then paired; that is balance in expectation at \(N=54\), not guaranteed balance; the realised plan is "written into the session log" but no balance table is shown; task is modelled only in the trajectory GEE. Arm pooling: *partially* — "environment" enters the demographic family (null), but the primary contrasts pool without an arm term, and the arms differ in age (29.5 vs 35.7) and extraversion (raw \(p=.039\)); declared as a limitation, never stress-tested on a headline cell. Latency: **not addressed** outside the system chapter (CRITICAL 1). Onset reconstruction asymmetry (0.23 s explicit vs 0.43 s implicit, 30/36 implicit onsets reconstructed): *partially* — it justifies the induced-spectrum choice and the refusal of ERP, but the unlike pre-windows are not discussed. \(\theta\)–\(\lambda\) confound: *adequately* declared (§6.2.5, §8.7) and mostly carried. "Confirmatory" without registration: *partially* (MAJOR 2).

**Behavioural.** Likert-as-interval: *adequately* defended via the \(D_i\) argument plus bootstrap/Wilcoxon/LMM concordance (E.6). Ceiling: *partially* — "Trust and credibility sit near the ceiling" is fair for credibility (6.0/7) but a stretch for trust (Table E.1: 4.69–5.37). Notice \(\alpha=.61\): *adequately* disclosed and justified. Estimator disagreement (trust early−late .063/.048/.026): *adequately* handled — disclosed in 7.2.1 and 8.1, pre-specified \(t\) verdict kept, not hedged into a claim. Post-hoc labelling: *partially* — clean in Ch 7/8, dropped at the summary surfaces (D16). Notice ≠ detection: *adequate* and consistent. Zero clicks: *adequate* — "nothing in the family says it did" (8.1).

**Personality/demographics.** *Adequate*: 0/60 and 0/70 are bounded ("not proof that personality or demography never matter", 8.2; "not a demonstration of equivalence", 9.1); no trait picked by raw \(p\) (extraversion nearest cell explicitly refused). The "earlier pass" disclosure (8.2) is commendably honest — and relevant to MAJOR 2.

**EEG.** Boundary cell \(p=.0496\): *partially* (MAJOR 3). "Null ≠ absence" symmetry: *adequate* (implicit-late Fz \(\theta\) leans explicitly denied result status). Explicit-early cluster as one event with ocular/transient reading prioritised: *adequate* in interpretation, but the "not created by ICA" robustness claim cites an appendix that shows no such numbers (MAJOR 6). Within-measure Holm burden: *adequately* stated (D.2 tiers). Width sensitivity: *partially* — off-4 s cells correctly quarantined (8.3), but the survivor's own fragility is unstated (D10). \(k=37\): *adequate* — shortest-window-driven, fixed in 4.2.4, and I found no leak of whole-window medians into confirmatory claims. CIs instead of post-hoc power: *adequate* by the review's own standard.

**Trajectories.** Instrument validity: *partially* — 83.8% held-out accuracy (§5.2.3) is on its own distribution; the decisive number, 32.5% agreement with the runtime label under the bare context, is appendix-only (F.2), and no human-label validation on this corpus exists; the "instrument failure" framing is itself an interpretation, though the turn-1/turn-4 check supports "reads depth, not the ad". Context choice as researcher df: *adequately* answered by the six-window sweep with pre-fixed recipes (F.3). \(\delta^{(a)}_4\) undefined / late as control: *adequate*, wording consistent. Permutation pairing break: *adequately* acknowledged ("the one conversation-level exception"). KW on 270 rows: *adequate* (exploratory + ICC). Genre overlap (98/156): *adequately* admitted before the null is discussed. Null → theory verdict: *adequate* in 8.4, one slip in 9.1 (D15).

**Associations.** Multiplicity across the two EEG scores: *partially* — declared and both reported, but the across-twelve report is missing (D6) and the partial-\(\rho\) defence is undermined by Table 7.8's Sig. 0 (D7). Single-item trust reliability carried into interpretation: *adequate* ("the lower bound is the number to carry", 8.5). 2,560-test map: *adequate* — separated, chance-calibrated (105 vs 128 expected), the process-side cluster explicitly denied finding status. Mediation drift: *adequate* ("None of these correlations is mediation", 8.5).

**Mathematics/technical.** Definitions 1–6: internally consistent (indices \(k\) vs \(i\) explicitly distinguished; \(\tilde\delta^{(a)}_k \le \delta^{(a)}_k \le \delta_k\) holds as binary indicators; \(T-1\) ranges correct; the Table F.1 ceilings \(1.386=\log 4\), /4, /3 are the realisable \(T=4\) ceilings, consistent). \(D_i\), \(D^A/D^B\), \(t=\sqrt{n}\,\bar D/s_D\), \(d_z\): correct. KV-cache arithmetic: correct (\(16384 \cdot 1 \cdot 10 \cdot 2 \cdot 2 \cdot 256 \cdot 2\) B \(= 320\) MiB, with the 10/40 full-attention layers correctly used). Table column definitions vs citing sentences: spot-checked ~10, all match.

**Reproducibility (PDF only).** *Partially adequate*: software versions, exclusion tags, ICA thresholds (0.35 proxy correlation, 1.5× frontal topography, ≤3 components, 1,050 µV, 0.5 µV), epoch rules, and Gold schemas are all on the page — unusually complete. Not on the page: any seed value ("20,000 seeded draws" without the seed), the realised Latin-square/condition assignments, the nine logged interaction measures (never enumerated), the LOO onset-reconstruction procedure in reconstructable detail, and the data tables themselves. The tables cannot be rebuilt from the PDF alone; the claim rests on the linked repository.

---

## Findings

### CRITICAL

**C1 — The only server-side difference between advertised and control turns — ~3 s of silent retrieval wait — never reaches the Methods confounds or the Discussion, and it sits inside the Dataset B pre-onset window.**
- Location: §5.1.2: *"On the one advertised turn, retrieval runs before the first token (median 3.03 s), so that silent wait is about 6 s: noticeable, still below 10 s, and **the only ads-versus-no-ads difference in server wait**."* §4.2.4: implicit onset is *"the injection event plus 1.57 s … which lands before the reply has finished streaming"*; explicit onset is *"the assistant reply plus 0.49 s."*
- Problem: for implicit mentions the 4 s pre-onset window is largely the silent retrieval wait plus the first ~1.5 s of streaming; for explicit banners it is the final 4 s of reply reading; for the timing-matched \(a^\emptyset\) moments there is no wait at all. The pre-states are not like with like, so the implicit onset-locked cells contrast "streaming resumes after a stall" against "an ordinary reply moment", not "mention visible" against a matched baseline. The same wait is also inside every behavioural ad-vs-\(a^\emptyset\) contrast (a ~6 s silent stall is itself a UX event that can move manipulation and trust ratings).
- Why it matters here: Dataset B is one trial per cell with 2–4 dB intervals; a systematic pre-window asymmetry is exactly the kind of artefact a single-trial difference cannot absorb. The thesis's own confound list (§6.2.5 "Structural confounds the design cannot remove"; §8.7) omits it entirely.
- Change: declare it in §6.2.5 and §8.7; discuss its direction for both the behavioural family and Dataset B; ideally re-cut implicit pre-windows to exclude the wait or show the wait is spectrally inert in the relevant bands.

**C2 — The Conclusion claims prescriptions and absences that the Discussion explicitly refuses.**
- Locations and quotes: D1 (obligation to disclose / "be patient … rather than rush into the earliest turns" vs *"This is not a recommendation to serve advertisements late or implicitly … a disclosure question this study did not test"*), D14 ("does not produce" vs "not a demonstrated difference between the two formats"), D15 ("not a conversation steered towards the product" vs "a failure of the instrument … not a demonstration that such a sequence does not exist").
- Problem: the most-read page of the thesis overclaims in three distinct directions — a serving recommendation, a format absence, and a trajectory fact.
- Why it matters: a committee reads the Conclusion as the thesis's claim set; here it contradicts the candidate's own analysis chapter. Disclosure was never crossed with presentation (\(\theta\) co-varies with \(\lambda\) by construction, §6.2.5), so an "obligation to disclose" is a policy prescription resting on a manipulation the design cannot apportion.
- Change: rewrite the "overall picture" paragraph to the evidentiary level of §8.3–8.6; convert the prescriptions into the questions the study actually raises.

### MAJOR

**M1 — The format × timing interaction is declared in Methods and answered in Table 8.1, but lives in no family and no results table.** (D3.) RQ5's answer rests on four estimates reported only as "\(|d_z| \le 0.06\)" — no \(D\), no CI, no \(p\), no correction label; the EEG interaction weights \((1,-1,-1,1,0)\) are "fixed in advance" in §6.3 and never reported. Also note the weights are coded, not normalised: alongside \((\tfrac14,\tfrac14,\tfrac14,\tfrac14,-1)\) the text never flags that the interaction is on a doubled scale (harmless for \(d_z\), misleading if a \(D\) is ever quoted). Change: give the interaction a row in Table 6.1 and Table 7.2 (and report or explicitly drop the EEG interaction), stating its correction status.

**M2 — "Confirmatory" without registration, and no statement that nothing was registered.** §6.3: *"the planned confirmatory contrasts, whose measures and weights were fixed on theoretical grounds before the corresponding results were read"* — an unverifiable self-report; the word "pre-registered" appears nowhere in 156 pages. The disclosure in §8.2 that *"an earlier pass over these factors on the same data read uncorrected p-values on single condition dummies"* (14 of 18 flagged cells on 2–3-person levels) demonstrates that results were read and families re-parameterised — for demographics, which is not labelled confirmatory, but the committee cannot verify the boundary. The \(k=37\) and 4 s choices are genuinely argued on design grounds (shortest eligible window; Welch settings), which is the strong part. Change: one sentence in §6.3 stating the study was not pre-registered and defining what "fixed before reading" operationally means here (frozen Gold tables, dated); soften "two complementary views" accordingly.

**M3 — The single confirmatory EEG survivor is width-fragile, boundary, and presented cleanest where it is weakest.** (D10, D11, D16.) The posterior \(\alpha\) early−late cell (\(-0.22\) dB, Holm \(p=.0496\), \(n=18\)) appears in the Abstract without the depth confound that §8.3 attaches to it; Table 7.9's own key estimate says *"the 4 s family does not hold at other widths"* while §7.4 says the branches *"do not revise the 4 s family"* — only the favourable direction of the asymmetry is in prose; and Fig 7.8 prints ".050\*". Change: state in §7.4/§8.3 which confirmatory cells survive at which widths; print ".0496" or ".049" in the figure; carry the confound into the Abstract sentence.

**M4 — The confirmatory \(\delta^{(a)}_2\) family's estimator is ambiguous between Table 6.1 and Table 7.5.** (D4.) Methods names the exact McNemar as "the test" with the \(t\) as interval; Results Holm-adjusts the \(t\) and leaves McNemar raw. All verdicts are null either way, so nothing changes substantively — but the confirmatory pipeline's primary test should not be ambiguous on paper. Change: pick one, say which column is Holm-adjusted, and align Table 6.1.

**M5 — The 70-test demographics family is missing from Table 6.1 and from Table 7.8, and the one mention misdescribes it.** (D5.) "Demographics as covariates" (in the personality row) is not the reported analysis (one-factor-at-a-time joint Wald, Table E.10). The Methods table that "lists every analysis family" should list it. Change: add the row; delete or correct "demographics as covariates".

**M6 — Discussion-only numbers, including the quantitative basis of the tilt paragraph, and an empty robustness citation.** (D8.) The "4.60 dB" absolute-\(\delta\) rise is the only effect size given for the thesis's flagship exploratory event and appears in no Results table or figure; ICC .39 (trust) and ".83" (partial) likewise. Separately, §8.3's *"Leaving blinks in dilutes it and widens its spread (Appendix D.1)"* cites an appendix section that contains no such numbers — the no-ICA dilution claim is unverifiable from the PDF. Change: move all four numbers into Ch 7/Appendix tables, or delete them from Ch 8; print the no-ICA tilt estimates in D.1.

**M7 — Table 7.8's three-way family: Sig. = 0 with key estimate partial \(\rho = .80\), used defensively in §8.5.** (D7.) If the partial correlation is really .80 at \(n=18\), its surviving Holm-within-3 would be expected; if the partial test is computed differently (ties-heavy \(\delta^{(a)}_2\): 12 of 18 at zero), the method is undocumented. Either way the table and the Discussion's use of it ("leaves that association where it was, at .80 and .83") cannot both be right. Change: report the partial's \(p\) and its Holm status, or drop the defence.

**M8 — The genre instrument's decisive validity number is appendix-only, and Table 8.1 overstates closure on RQ2/RQ4.** §5.2.3: *"Held-out accuracy is 83.8% on 2,224 samples"* (the model's own distribution); F.2: *"The bare reading agrees with the logged runtime label on 351 of 1,080 utterances (32.5%)"* — the number that actually bears on this corpus. §8.4 argues the nulls are *"a failure of the instrument on this corpus"*, yet Table 8.1 answers RQ2/RQ4 flatly "Not supported"; only the §8.6.1 prose carries the caveat (*"bounded by the instrument of section 8.4 as much as by the advertisements"*). Note also that "instrument failure" is itself an interpretation: an insensitive-but-valid instrument and a true absence are not separable here — the turn-1/turn-4 check shows the classifier reads depth, not that it could have seen an ad effect. Change: bring the 32.5% into §7.5; add the instrument bound to Table 8.1's RQ2/RQ4 rows.

**M9 — The participant-facing debrief misdescribes the study in three ways.** Appendix C.6: *"here is what we instructed ChatGPT to do during your interactions with it: To mention the product/brand in a positive light … and to personalize its response"* and *"These products and brands were selected randomly."* The model was a local Qwen 3.6 35B-A3B (§5.2.2); the actual injection prompt (B.3) instructs *"Keep the mention brief and factual; do not sound salesy or promotional"* — the opposite of "in a positive light"; and products were selected by deterministic semantic retrieval (§5.3), not randomly. The thesis itself flags one inconsistency (*"The live consent screen does not mention personalities for AI; that clause appears only here"*) but not these. Change: correct the debrief text or annotate it as inherited boilerplate that does not describe the live manipulation.

### MINOR

1. Quantifier drift on the recognition share: "about half" → "more than half" → "most" (D2); print the count once and reuse it.
2. Fig 7.8 ".050\*" for \(p=.0496\) (D11) — display rounding contradicts the threshold rule on the page.
3. Notation: §7.5's "shorter form" sentence misquotes Theory's (3.8) (D12); \(g^{(a)}_k\) loses its subscript outside Ch 3.
4. Broken cross-references: "Figure 4.2.4" ×3 (App. D), "Equation 4.2.4" (§6.3), "Equation 4.2.4)" with dangling paren and lowercase "dataset A/B" (§7.4), "itself 8.7" (§9.1, also missing the sentence's final period), "account 8.7" (§8.6) (D13).
5. "borderline significant" appears twice (§7.2.1, §7.6.1 — the latter for pairs with Holm \(p \ge .44\)), a register the thesis otherwise avoids.
6. Table 7.8: "Sig. 0; 1" is unexplained in the caption; "Tests = 6" for behaviour × EEG undercounts the 12 tests actually run.
7. "Trust … near its ceiling" (§7.2.1, §8.1) is a stretch at 4.69–5.37 on 1–7 (Table E.1); the claim is fair for credibility only.
8. No session-position (order) check on behavioural outcomes despite five repetitions of the 22-item battery; position is tested only for \(N_{\text{shift}}\).
9. Table 7.9's "126 tests" for epoch width/cleaning cannot be reconstructed from the text (presumably 9 branches × 14 confirmatory cells — say so).
10. The nine logged interaction measures behind the 36 exploratory tests are never enumerated.
11. Catalogue size: 117,343 (Table 4.1) vs 117,243 (Table 4.2, Fig 4.1) (D17).
12. The instrument check is called *"not a test but rather a check"* (§7.5) while being Holm-corrected and counted as a 6-test family in Table 7.8.
13. Spelling/register cluster: "datasetm" (companion note), "aggreation" (§4.2.4), and in Ch 5 "percieved", "inidivdual", "unnatentive", "crutial", "simultaenously", "degradated", "artifical", "usefullness", "succed", "appropiately", "anonimization"; exclamation-mark register in Related Work ("Opus 4.5 did it 98% of the time!", "scary concerns"); "Individual differences" paragraph title lacks its period (§9.1); acknowledgments "strenght", "fre".
14. Onset uncertainty is a LOO reconstruction error in §4.2.4 and a "95th-percentile uncertainty" in §8.7 (D9).

### VERIFY (cannot be settled from the PDF)

1. The partial-\(\rho\) testing method behind Table 7.8's Sig. 0 (see M7).
2. The across-twelve Holm value for trust × posterior \(\alpha\) (promised, absent; verdict would stand).
3. The exact count behind "about half" (not derivable from Table E.2's marginals).
4. Which cells fail at which widths inside Table 7.9's "the 4 s family does not hold at other widths" — the substantive robustness fact for the \(p=.0496\) cell.
5. Whether the behavioural interaction used \((1,-1,-1,1,0)\) and under what correction.
6. Whether the demographics "earlier pass" touched only non-confirmatory families (as the text implies).

---

## Top 5 vulnerabilities — what an examiner asks aloud

1. *"Your advertised turn carries about three seconds of extra silent retrieval wait — your own system chapter calls it the only server-side difference between ad and no-ad turns — so for the implicit mention, your Dataset B pre-onset window is that wait: what is the onset-locked contrast actually contrasting, and why is this not in your confound list?"*
2. *"Nothing was pre-registered, and §8.2 discloses an earlier uncorrected pass over the demographic factors — why should the word 'confirmatory' carry more weight than 'disciplined after the fact'?"*
3. *"Your only confirmatory EEG survivor is \(p=.0496\) at \(n=18\), your Table 7.9 says the 4 s family 'does not hold at other widths', and your figure prints '.050' with an asterisk — why is this cell a flat finding in the Abstract?"*
4. *"RQ5 is answered with an interaction that appears in no analysis-family table and no results table — where exactly is it estimated and under what correction; and where did the EEG interaction weights declared in Methods go?"*
5. *"Your Conclusion tells platforms they have 'an obligation to disclose' and to 'be patient … rather than rush into the earliest turns', while your Discussion says in bold that this is not a recommendation and that disclosure was not tested — which page should I believe?"*

## Three strongest aspects

1. **The multiplicity architecture is real and auditable.** Participant-as-unit throughout, named families with named corrections, a four-label test taxonomy that is actually enforced, sensitivity estimators reported beside the primary (16/16 cells in Fig E.4), and two closing summary tables (7.8/7.9) that let a reader reconstruct the entire testing surface — including the chance calibration of the 2,560-test map (105 raw hits vs 128 expected). Very few theses at this level expose their own machinery like this.
2. **EEG discipline.** Two explicitly separated estimands, a genuine positive control (write−read, \(+0.60\) dB on Fz \(\theta\)), off-width cells quarantined to the appendix and explicitly refused as primary (*"would replace the pre-specified estimand with a window chosen after inspection"*), the 256-pair sweep demoted to localisation, "failure to reject … is not evidence of absence" applied symmetrically (the implicit-late Fz \(\theta\) leans are *"a target for replication, and not a result"*), and the direct implicit−explicit onset claim refused.
3. **The trajectory null is analysed as measurement, not waved away.** Ceiling/floor diagnosis of the two contexts (2.45/3 vs 0.40/3), the advertised-genre overlap inventory (98 of 156 "general guidance"; 25 of 108 already aligned), a six-window sweep with pre-fixed recipes, and the turn-1/turn-4 depth check — a model failure report. Paired with the notice ≠ detection handling (brand mention at 52% under no-ad correctly never treated as detection).

## Scores

| Dimension | Score /10 |
|---|---|
| Research question / contribution | 8 |
| Design | 6 |
| Statistical validity | 7 |
| Technical correctness | 7 |
| Results / interpretation discipline | 7 |
| Internal consistency | 6 |
| Reproducibility (from the PDF alone) | 6 |
| Writing | 6 |
| **Overall, as it stands** | **6.5** |

## Examiner verdict

What would make me challenge this thesis in the defence is not the science — the frozen analysis, the participant-unit discipline, and the refusal to harvest nulls are above the standard I expect at this level — it is the gap between the analysis and the surfaces that summarise it. I would press four points: (i) the ~3 s retrieval wait on the advertised turn, which sits inside the implicit pre-onset window and inside every behavioural ad-vs-control contrast, and which the Methods and Discussion never mention; (ii) the word "confirmatory" without registration, in a thesis that discloses an earlier uncorrected analytic pass; (iii) a boundary confirmatory cell (\(p=.0496\), \(n=18\)) whose width-fragility is admitted only in a summary table's key-estimate column while the Abstract states it flatly; and (iv) a Conclusion that issues serving prescriptions and asserts two absences its own Discussion explicitly refuses. All four are cheap to fix — the numbers are frozen and the honest versions already exist inside Chapters 7–8 — but as submitted, the Abstract and Conclusion claim more than the analysis chapter allows, and that is exactly where a committee starts.

## Rest of the thesis — shorter suggestions

- **Introduction:** add the one sentence stating the study was not pre-registered; decide whether RQ2/RQ4 should carry the instrument bound into Table 8.1 rather than only in §8.6.1 prose.
- **Related Work:** content is well chosen; drop the exclamation marks and the informal register ("scary concerns", "This paper alone shows").
- **Theory:** Definitions 1–6 are internally consistent; fix the §7.5 "shorter form" sentence that misquotes (3.8); consider noting the \(T=4\) realisable ceilings (\(\log 4\), 4, 3) at Definitions 4–5 so Table F.1's headers don't surprise.
- **Datasets:** reconcile 117,343 vs 117,243; show the realised task × condition balance table (the Latin-square claim is currently balance-in-expectation only).
- **System Design:** the chapter needs a language pass (typo cluster above); cross-reference the advertised-turn latency paragraph from §6.2.5 — that single link defuses C1's behavioural half.
- **Methods (rest of 6.2):** the flow/bias section is strong; add the latency confound and an order-effect check plan to the structural list.
- **Appendices:** D.1 should print the no-ICA tilt numbers that §8.3 cites; C.6's debrief text needs the M9 corrections (model, tone instruction, selection mechanism); enumerate the nine logged interaction measures; Appendix A/C are otherwise careful and honest (the TASK_CATALOG mistakes note is good practice).
