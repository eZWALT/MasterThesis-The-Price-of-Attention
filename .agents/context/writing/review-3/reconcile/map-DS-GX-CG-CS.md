# Map: DS, GX, CG, CS

Source dumps: `jury-v1-deepseek.md` (DS), `jury-v1-grok-4.6.md` (GX),
`jury-v1-chatgpt.md` (CG), `jury-v1-claude-sonnet-5.md` (CS). Taxonomy:
`issue-taxonomy-seed.md`. Nothing here was checked against the PDF or
the `.tex`; every number and location is the jury's own.

Reference legend used in the severity column:
`D<n>` = Job-1 "disagreement" item; `C/M/m/V<n>` = the jury's own
CRITICAL / MAJOR / MINOR / VERIFY numbering; `T` = remark in the
consistency-audit table; `J2` = CS's un-numbered Job-2 checklist item;
`R` = "rest of the thesis"; `X` = examiner verdict; `Top<n>` = position
in the jury's Top 5. `(adequate)` = the jury raised the item and judged
it handled. `?` = debatable mapping.

## Coverage matrix

| ID | DS | GX | CG | CS | Severity given (per jury) |
|---|---|---|---|---|---|
| I1 | x | | x | x | DS:D6 · CG:D-E (Job 1) · CS:D2/C2 (Top1). GX:D10 asserts the sentence is *not* in the Conclusion (see false premises) |
| I2 | ? | | x | x | DS:M3? (θ/λ confound "not carried into every format claim", §8.1) · CG:D-E/M6 · CS:D2/C2, J2 "Disclosure θ confounded" |
| I3 | | | ? | | CG:M8? ("confirmatory onset-locked results are not mentioned as null" in Abstract) |
| I4 | | x | ? | | GX:T-Behavioural ("Partial"), D1, C1 (Top1) · CG:M5? ("'timing affects trust' impression from … the post hoc explicit-early trust cell"), D-F (−0.69 traces to App E.6) |
| I5 | | | x | ? | CG:M9 ("smallest Holm p being .08… not a demonstrated difference") · CS:M4? ("no comparable response… at mention onset" explained only one way) |
| I6 | | x | x | | GX:T-Dataset B ("Abstract elevates exploratory"), D2, D9 · CG:D-C, M9 (Top3) |
| I7 | ? | x | x | | DS:X? ("sits exactly at the boundary") · GX:T-Dataset A ("over-weighted relative to boundary"), Major-1 (Top2), X-(d) · CG:D-C, M7 |
| I9 | | | x | ? | CG:D-D ("some users carry more of it than others" vs null moderation) · CS:J2 association→mediation? (Conclusion p. 98 "those whose posterior α fell more… withdrew more trust", judged caveated) |
| I11 | | ? | x | | GX:minor-1? ("Holm-null trust planned contrasts license little") · CG:M4, m1 ("trusting the assistant similarly"; CI [−0.71, 0.03]) |
| I12 | | | ? | x | CS:D1/C1 (Top5) · CG:R-Introduction? ("deployment rhetoric"). CG:m2 judges "attention shift" a *pass* (contradiction, see false premises) |
| I14 | | x | x | ? | GX:T-Behaviour×EEG ("Partial"), D3, Major-4 · CG:D-C, M10 (Top5) · CS:J2 associations (adequate: "individual sensitivity… not a uniform effect") |
| I15 | | ? | | | GX:D10? (Abstract closes "the price of attention … should be measured and minimised" — "borderline elevation only") |
| L1 | ? | | | | DS:D9? ("The interaction is described in Methods but never estimated in Results" — not split by family) |
| L2 | x | | | ? | DS:D9 · CS:J2 D_i/dz? (checks that unscaled (1,−1,−1,1,0) does not bias dz — adequate). GX:D7 and CG:D-H declare "Match" on scaling only |
| L3 | | | | x | CS:T-Demographic ("not itemised in Tbl 6.1 (only named in prose, §6.3)"), M1? |
| L5 | | x | x | | GX:Major-4 ("Report both scores with the cross-12 Holm") · CG:T-Behaviour×EEG, M11, v4 |
| L8 | | x | x | ? | GX:minor-4 ("late conditions analysed on N_shift and sometimes called 'control'… comparison is not symmetric") · CG:M15 ("pre-treatment trajectory balance check", not "negative control") · CS:J2 δ₄?/m-d? (adequate, terminology only) |
| L11 | | | x | x | CG:D-I ("minor traceability problem": "an earlier pass… 14 of 18… two survive Holm… same two participants" in Discussion, documented App E.10) · CS:D3/C3 (Top2; "4.60 dB" first appears §8.3 p. 84). GX:D8 declares "Discussion interprets without new numbers. Match" |
| L12 | | | | x | CS:D3/C3 ("reported only as a Holm p-value (.007)"; fix: "magnitude + CI for every cell asterisked in Fig. 7.8") |
| L15 | | ? | ? | | GX:VERIFY-2? ("Whether whole-conversation-window EEG features… ever enter confirmatory claims") · CG:D-G? (finds "equal-n cell" as k=37 description, judges harmless). DS:D7 and GX:D5 declare naming clean |
| L16 | | | x | | CG:D-A ("a Holm p here is a Holm-adjusted Spearman p"; demographic Holm on joint Wald). DS:m1 and GX:D6 declare "Match" having checked only Wilcoxon |
| L18 | ? | | | | DS:D9? ("Figure 8.1 shows it as dots (unestimated)") |
| L21 | ? | | | | DS:D1? quotes §7.2.1 "borderline significant after correction" without objecting to the phrase |
| L24 | x | | x | | DS:D11 ("quietly redefined from 'trajectory' to 'ad-associated shift' or 'N_shift'"; RQ4 "structurally unanswerable") · CG:D-B, C5 (Top4), R-Theory. GX:D9 declares "no quiet redefinition" |
| L25 | ? | | | | DS:D8/m2? (notation drift δ_k^{(a)} vs δ₂^(a); DS claims Theory Def. 6 already writes δ_k^{(a)} — see false premises) |
| L26 | | ? | | x | GX:VERIFY-2? · CS:M6 (VERIFY), J2 k=37, R-Appendix D (Table 4.6 Kc 54–238 vs Eq. 4.10 k=37) |
| L27 | ? | ? | ? | ? | DS:M2, GX:minor-3, CG:C2, CS:M4 all quote "0.23 s" and "0.43 s" (LOO vs p95) side by side as if the same kind of quantity; none flags the two statements |
| L28 | | | | x | CS:m-a, J2 Dataset A ("Figure 7.8's own displayed cell reads '.050'") |
| S1 | x | x | x | x | DS:M1 · GX:C3 (Top4), R-System Design · CG:C1 (Top1), v2, R-System Design, R-Methods ("table of what exactly differs between ad and no-ad turns") · CS:M3 (Top4) |
| S3 | ? | x | x | ? | DS:X? · GX:Major-1 (Top2; "unmodelled turn depth") · CG:M7 ("early vs late is … ad timing + stage of conversation") · CS:J2 Dataset A (partial; depth confound "acknowledged… adjacent") |
| S4 | x | x | x | ? | DS:C4 (Top4; "no reliability for Dataset B"), M6 ("selection between scores is post hoc") · GX:D3, Major-4 ("two EEG scores evaluated per pair; single-item trust") · CG:M10 (Top5; "single-item trust outcome, one EEG score per cell") · CS:J2 associations (adequate; quotes §8.5 split-half .56 and ρ=.80 vs ρ=.24) |
| S5 | x | x | x | x | DS:D13 · GX:minor-7 · CG:M2 · CS:J2 Latin-square, M2 (Top3) |
| S6 | x | x | | ? | DS:C2 (Top2) · GX:C2 (Top5) · CS:J2 (adequate; only "two complementary views" caveat) |
| S7 | | | x | ? | CG:C4, v3, R-Appendices ("ocular-artifact sensitivity appendix") · CS:J2 explicit-early cluster (adequate; "indirect argument by construction") |
| S9 | | x | ? | x | GX:minor-1 asserts the ceiling ("Ceiling effects on trust/credibility (means ≈6/7)") · CG:M4? ("credibility is near 6/7") · CS:J2 Likert, v-2 (checked: trust M=4.69–5.37, credibility 5.69–6.08) |
| S10 | | x | x | ? | GX:minor-8 ("extraversion differs by arm (uncorrected); arm never entered as a factor") · CG:M1 ("lab 3.39 vs crowd 2.78, p=.039, Holm=.19"), v1 · CS:J2 pooling (adequate) |
| S11 | x | x | x | | DS:C5 (Top5; "32.5%") · GX:Major-2 (Top3; "83.8 %… 32.5 %") · CG:M12 (Top4). CS:J2 judges instrument validity "Adequate" |
| S12 | | | | x | CS:m-c, R-Appendix C.6 ("here is what we instructed ChatGPT to do") |
| S14 | x | | x | | DS:C3 (Top3) · CG:C3, m3 ("correction rationale is overbroad"). CS:J2 Holm-within-measure "Adequate" |
| S15 | | | ? | | CG:C1?/M7? ("Early and late ad turns may encounter different conversational response lengths and states") |
| S16 | x | x | x | ? | DS:M3 · GX:Major-3 · CG:C2 (Top2), M6 · CS:J2 θ/λ ("not… 'carried into every claim about format'") |
| S17 | | | x | ? | CG:C2 ("implicit onset ≈ injection + 1.57 s, during streaming… textual position is not fixed") · CS:M4? ("fixed +1.57 s offset assumption") |
| S18 | | | ? | ? | CG:M3? · CS:J2 order/carry-over? — both filed as NEW-CG-2 below |
| S19 | x | x | x | ? | DS:M8 (permutation) · GX:minor-5 (KW 270 rows) · CG:M13 (permutation, adequate), M14 (KW) · CS:J2 permutation/KW (adequate) |
| S24 | | ? | | | GX:VERIFY-4?, R-Theory ("inequality chain and index usage should be re-checked line-by-line"). DS:V2 and CS:J2 declare Definitions 1–6 consistent |
| S25 | | | | ? | CS:R-Related Work? ("became viral due to the scary concerns…" editorialising) |
| S26 | | | x | | CG:v5 ("exclusion table, randomisation seeds, and data dictionary") |

Taxonomy IDs raised by none of the four: I8, I10, I13, L4, L6, L7, L9,
L10, L13, L14, L17, L19, L20, L22, L23, S2, S8, S13, S20–S23, S27–S31.
(L13 is actively contradicted: GX R-Appendices, CG m4, CS J2
epoch-width all say off-4 s cells are "correctly" kept as sensitivity.)

Not mapped: DS:D5 ("Early insertions elicit 'greater visual
processing'") — DS itself writes "Abstract: Not present verbatim" and
phrases the item conditionally ("If the Abstract or Conclusion
implies…"). Recorded under false premises only. Pure verify-clean items
(KV-cache, D_i formulas, no RQ10/11, zero clicks, free text) are not
criticisms and are not mapped.

## New issues

| ID | Causal claim (one line) | Raised by | Severity given | Quoted thesis location (as the jury gives it) |
|---|---|---|---|---|
| NEW-DS-1 | Trust early−late estimator disagreement (t Holm .063 / LMM .048 / raw Wilcoxon .026) is reported but never reconciled; the thesis does not say which estimator is primary when they split | DS, GX, CG?, CS(adequate) | DS:D1, X · GX:minor-2 · CG:M5 ("adequately addressed") · CS:J2 (adequate; listed as a strength) | DS: "Methods (Table 6.1)… 'one-sample t on D1 of (6.1); Wilcoxon sensitivity; random-intercept linear mixed model on Y2 as an adjusted check'" vs "Results (Section 7.2.1)… (t Holm .063, LMM .048, raw Wilcoxon .026; Figure E.4)" |
| NEW-DS-2 | Abstract headline numbers (+1.27, "approximately eight in ten versus six in ten", −0.69) do not sit in a main Results table cell; they require an appendix table or averaging | DS, GX, CG? | DS:D2, D3, m5 · GX:VERIFY-1 · CG:D-F ("−0.69 is traceable to Appendix Table E.6, not Table 7.2"; but "+1.27 is Table 7.2") | DS: "Results (Table 7.2): Cued memory implicit early M = 4.35, explicit early M = 6.09… Table E.2 shows 57% and 87% for ≥5 ratings"; "The +1.27 figure requires averaging across four conditions" |
| NEW-DS-3 | Abstract asserts the EEG response "depends on how and when" while §8.3 refuses that claim | DS | DS:D4, C1 (Top1), R-Suggestions | DS: "Abstract: 'The EEG response "depends on how and when"'; Discussion (Section 8.3): 'They do not combine into one claim that the response depends on how and when the advertisement enters.'" — **suspected false premise, see below** |
| NEW-DS-4 | Results prose carries verdict/evaluative language ("reassuring half", "Holm-null") rather than estimands | DS | DS:D10, m4 | DS: "Section 7.2.1: 'Trust is Holm-null on the three planned contrasts.' Section 7.4: 'That is the reassuring half of the result'" |
| NEW-DS-5 | Onset-timing precision is asymmetric between formats (implicit mostly reconstructed, p95 0.43 s; explicit mostly observed, ~0.23 s); jitter alone could smear an implicit transient, and this alternative to "different kind of event" is never discussed | DS, GX, CG, CS | DS:M2 · GX:minor-3 · CG:C2 (Top2, folded into "event geometry") · CS:J2 onset precision (partial), M4 | DS: "Section 4.2.4: 'the moment it becomes visible is uncertain to about 0.23 s for explicit banners and 0.43 s approximately for implicit mentions'"; CS: "§4.2.4, p. 35; restated in Limitations §8.7, p. 93" vs "§8.3, p. 84"; CS: "implicit mentions are mostly reconstructed (30 of 36)" |
| NEW-DS-6 | Personality/demographic null read as evidence of absence ("Who the user is does not seem to change what the advertisement costs them") at N=54 with two-item BFI-10 traits | DS, GX | DS:M4 · GX:Major-5. CG:M17 and CS:J2 say the nulls are *not* over-read | DS: "Section 8.2: 'Who the user is does not seem to change what the advertisement costs them'"; GX: "Abstract/Conclusion phrasing 'neither personality nor demographics moderated any outcome'" |
| NEW-DS-7 | Demographic family (70 tests) run on factor levels filled by two or three people; the null and its "nearest cell" (Holm .44) are uninformative | DS | DS:M5 | DS: "Section 8.2: 'An earlier pass over these factors on the same data read uncorrected p-values on single condition dummies; most of the cells it flagged (14 of 18) sit on levels filled by two or three people'" |
| NEW-DS-8 | 2,560-test exploratory map null ("105 reach raw .05 where 128 are expected") is presented as a finding although it is the chance expectation and underpowered | DS | DS:M7. CS:J2 judges it "Adequate" | DS: "Section 7.6.3: '2,560 tests in 21 families, Holm within family; 105 reach raw .05 where 128 are expected'" |
| NEW-DS-9 | Fig 7.8 is dense and its colour coding is not explained in the caption | DS | DS:m3, R-Suggestions | DS: "Figure 7.8: 'Holm p within each EEG measure at 4s (n = 18)'" |
| NEW-DS-10 | Introduction contributions list is overstated ("Small Survey on LLM based Advertisement" listed as a contribution); motivation section is long | DS | DS:R-Introduction | DS: "The contributions are overstated; 'Small Survey on LLM based Advertisement' is not a contribution" |
| NEW-GX-1 | Likert ratings treated as interval after averaging | GX, CG(defensible) | GX:minor-1 · CG:M4 ("defensible at the contrast level") | GX: "Likert treated as interval after averaging" (no location) |
| NEW-GX-2 | Notice scale Cronbach α = .61 limits the notice contrasts | GX, CG, CS(adequate) | GX:minor-1 · CG:M4 · CS:J2 Likert (adequate) | GX: "Cronbach α=.61 on notice"; CG: "notice α=.61"; CS: "Cronbach's α=.61 on notice" (no location given by any) |
| NEW-GX-3 | Advertised-product genre is mostly "general guidance" (98/156), so the genre-aligned target of Definition 6 is weak by construction | GX, DS?, CS(adequate) | GX:minor-6 · DS:X? ("the advertised products share the modal genre with the conversations") · CS:J2 (adequate; "§8.4, p. 85–86, and again in Conclusion §9.1, p. 96") | GX: "Advertised-product genre is mostly 'general guidance' (98/156); Definition 6 is a weak target" |
| NEW-GX-4 | Related Work gap statement ("no research sits at the three-way intersection") is not verified against concurrent neuromarketing + LLM work | GX | GX:R-Related Work. DS:R says the gap statement "is well-supported" | GX: "'to the best of our knowledge no research sits at the three-way intersection'" |
| NEW-CG-1 | Five explicit-early exploratory cells (absolute δ, absolute θ, relative δ/α/β) are compressed into one "slow-power tilt" event and used as converging evidence although multiplicity was controlled per measure, not jointly | CG | CG:C3 (Top3) | CG: "'Holm adjustment is applied within a measure across the planned contrasts, never across measures.'… 'a single slow-power tilt.'" |
| NEW-CG-2 | Repeated 22-item battery answered five times creates measurement-specific anticipation; Latin square spreads it, the "different chatbot" warning does not neutralise it | CG, CS | CG:M3 ("adequately acknowledged, not experimentally solved") · CS:J2 order/carry-over (partial) | CG: "'in the later conditions they could anticipate being asked whether the assistant had pushed a product'… 'spread[s] that anticipation across conditions rather than removing it.'"; CS: "§6.2.5" |
| NEW-CG-3 | Abstract omits the eight confirmatory Dataset B nulls while headlining exploratory onset positives (asymmetric evidential framing) | CG | CG:M8 | CG: "Discussion says: 'failure to reject on the confirmatory pair is not evidence of absence.'… the Abstract foregrounds the positive exploratory slow-power result… while the confirmatory onset-locked results are not mentioned as null" |
| NEW-CG-4 | Relevance/quality of the served product is unmeasured, a direct mechanism for trust/credibility noise | CG | CG:v6, R-Datasets | CG: "The thesis admits that relevance/quality of the served product is mostly unknown and recorded" (no section given) |
| NEW-CG-5 | Related Work treats adjacent work (recommender systems, synthetic users, ad generation, neuromarketing) as methodologically comparable to direct human experimental evidence | CG | CG:R-Related Work | CG: "The argument occasionally treats proximity as methodological comparability" |
| NEW-CS-1 | "Environment" (§7.3 / Fig 7.6) and "the laboratory against the crowd setting" (§8.2) are the same variable but never defined as "= arm" (not in Table C.6), and its use as a moderator contradicts "arm is not a factor in the family" (§8.1, §8.7) | CS | CS:D4, M1 | CS: "Results §7.3, p. 68, and Fig. 7.6 axis labels"; "Discussion §8.2, p. 82–83"; "Discussion §8.1, p. 82, and Limitations §8.7, p. 93"; "Table C.6, p. 119" |
| NEW-CS-2 | §8.3 reads a Holm-null EEG format contrast as absence ("format leaves no trace… does not differ"), against the standard the thesis sets in the Fig 8.1 caption | CS | CS:J2 Dataset B ("slips exactly once"), m-b | CS: "§8.3 (p. 83), 'Averaged over the whole conversation, format leaves no trace in the two declared markers. A conversation with an advertisement does not differ from one without…'" vs "Fig. 8.1 caption, p. 90" |
| NEW-CS-3 | Abstract "Early insertion reduced credibility by about one third of a point" drops the referent "against a late one" that the Conclusion keeps; credibility was Holm-null against a∅ in every ad condition | CS | CS:M5 | CS: "Abstract, p. iii" vs "Conclusion §9.1, p. 96: 'Credibility fell by a third of a point for an early insertion against a late one.'"; "Fig. 7.3, Table E.6" |
| NEW-CS-4 | BFI-10 reversal (6−x, 1–5) and battery reversal (8−x, 1–7) are both described as "inverted once" without restating the scale at the point of use | CS | CS:v-1 ("clarity note only") | CS: "§4.2.2 p. 26 vs. Appendix C.4.2 p. 118" |
| NEW-CS-5 | System Design names fast-moving model releases (Qwen 3.6 35B-A3B; "Qwen 3.8 27B" as comparator in Limitations) without an access/verification date | CS | CS:R-System Design | CS: "Ch. 5… Limitations" |
| NEW-CS-6 | Two different design elements are both called "control" in §6.2.5 (late-condition "negative control" vs a∅ "no-ad control") without cross-reference | CS | CS:m-d, J2 δ₄ (adequate, "minor terminology overlap only") | CS: "§6.2.5, p. 57" |

## Suspected false premises

1. **DS — "depends on how and when" in the Abstract (D4, C1, Top1).**
   Quote: "Abstract: 'The EEG response "depends on how and when"'". No
   other jury quotes this string from the Abstract; GX and CG quote the
   Abstract's EEG sentences verbatim as "posterior α power was lower for
   early than for late insertion", "At early-banner onset, a transient
   slow-power tilt…", "candidate neural marker of a trust drop" — none
   contains "depends on how and when". The phrase is the brief's example
   and the `.cursor/rules` forbidden-phrase list. DS's own Discussion
   quote ("They do not combine into one claim that the response depends
   on how and when…") is the *refusal* sentence, which suggests DS found
   the phrase only there. DS builds its #1 CRITICAL and Top-1
   vulnerability on it.

2. **DS — "greater visual processing" (D5).** DS writes "Abstract: Not
   present verbatim" and then argues conditionally ("If the Abstract or
   Conclusion implies greater visual processing…"). A non-finding
   dressed as a disagreement; the phrase is from the brief.

3. **DS — "No reliability is reported for Dataset B" (C4, Top4).** CS
   quotes "§8.5, p. 87: 'with a single-item trust score and an
   onset-locked α split-half of .56… the lower bound is the number to
   carry'" and CG's table lists "onset posterior α split-half ρ≈.56".
   DS's counter-number "posterior α any-ad − no-ad .78, Fz θ not
   detectable" for Dataset A appears in no other dump.

4. **DS — Fz β for Fz θ, and β for ρ, throughout the audit table.**
   Positive control: "Fz β + 0.60 dB [0.22, 0.97], Holm p = .007" (CG:
   "Fz θ +0.60 dB, p=.007"; CS: "Fz θ +0.60 dB, Holm p=.007"). Pairwise
   sweep: "1/256 survives (Fz θ implicit early – explicit late)" in one
   column and "Fz β – 0.28 dB, Holm p = .014" in the next (CG: "imp-early
   vs exp-late Fz θ, −0.28 dB, p=.014"). Dataset B nearest: "implicit
   late Fz β – 1.38 dB" (CS: "implicit late Fz θ, Holm p=.22").
   Trajectory × EEG: "Fz β × g2(a) β = .47" (CG: "Fz θ × δ₂ ρ=.47"). All
   Spearman coefficients written "β = .80", "β = .22". The "−1.38 dB
   [−2.80, 0.04]" interval is unique to DS.

5. **DS — Dataset A/B family sizes (C3, audit table).** "1/48 survive"
   and "0/64 survive" treat 3×16 and 4×16 as the confirmatory families
   ("With 16 measures × 3 contrasts = 48 tests on Dataset A"). GX, CG and
   CS all report the confirmatory families as 6 and 8 cells plus a
   separate 98-cell exploratory block, and DS's own table also lists a
   98-test exploratory row. The FWER argument in C3 double-counts.

6. **DS — Theory already writes δ_k^{(a)} (D8, m2).** "Theory
   (Definition 6): 'δ_k^{(a)} = I_k δ_k'". GX: "Theory (Ch 3):
   δ_k(a_k). Methods/Results: δ^{(a)}_k". CG: "Results shortens
   δ_k(a_k) to δ_k^{(a)}, and explicitly defines both in the Results
   notation paragraph". Taxonomy L25 says Ch 3 has no such form. DS's
   "inconsistency" (subscript k vs numeral 2) is an instantiation, not a
   drift.

7. **DS — interaction "never estimated"; Fig 8.1 "dots (unestimated)"
   (D9).** "Results: Not reported as a separate estimate; Figure 8.1
   shows it as dots (unestimated)". No check shown; Fig 8.1 is the
   associations figure (taxonomy L18), not a contrast table. The
   defensible form is L1/L2 ("not reported"). GX:D7 and CG:D-H declare
   the weights "Match" but only on scaling, so neither confirms nor
   refutes DS.

8. **DS vs CG — is +1.27 a table cell?** DS: "Table 7.2 does not list
   the pooled any-ad manipulation contrast as a separate row… requires
   averaging across four conditions". CG:D-F: "+1.27 is Table 7.2". GX's
   audit table: "manip any-ad D=+1.27" under Results. Two of three place
   it in Table 7.2.

9. **GX — "Ceiling effects on trust/credibility (means ≈6/7)" (minor-1).**
   CS:v-2 checked "Table E.1": "credibility genuinely sits near ceiling
   (5.69–6.08/7)… but trust does not (M=4.69–5.37/7)". CG:M4 says only
   "credibility is near 6/7 in every condition". Taxonomy S9. GX's
   sentence reproduces the brief's premise.

10. **GX — serving prescription "does not appear" (D10).** "no 'be
    patient / don't rush earliest turns / obligation to disclose' as
    deployment rules appear in the audited Abstract/Conclusion text".
    CS quotes "Conclusion §9.1, 'The overall picture,' p. 98: '…an
    obligation to disclose, to be patient with monetisation rather than
    rush into the earliest turns…'"; CG:D-E quotes the same; DS:D6 quotes
    "obligation to disclose". GX's VERIFY section admits "pages partially
    truncated". GX therefore misses I1/I2 entirely.

11. **GX — "Discussion interprets without new numbers. Match" (D8)** vs
    CS:C3 ("absolute δ rises by 4.60 dB… No table or in-text sentence in
    Chapter 7 states the 4.60 dB figure") and CG:D-I (demographic
    retrospective numbers). Taxonomy L11.

12. **GX — "no quiet redefinition" of the trajectory RQs (D9)** vs
    DS:D11 and CG:D-B/C5 (both quote the Introduction wording "alter the
    trajectory of the conversation following the advertisement" vs Table
    8.1 "shift the conversation's genre"). Taxonomy L24.

13. **DS m1 / GX D6 — "Holm p" consistent, "No 'Wilcoxon Holm'".** Both
    checked only the brief's example. CG:D-A finds the actual problem:
    "'a Holm p here is a Holm-adjusted Spearman p'" and Holm on
    demographic joint Wald tests under the same label (taxonomy L16).
    The "Wilcoxon Holm" check is brief-induced; all three juries report
    it as clean.

14. **DS D7 / GX D5 / CG D-G — Dataset A naming "clean".** CG
    nonetheless reports "'equal-n cell' appears as a description of why
    k=37 was selected" and waves it through; taxonomy L15 lists
    "equal-n cell" and "on either path" as leftovers. Three juries
    checked only for "Path A/B" and "equal-n neighbourhood" — the
    brief's strings.

15. **CS vs DS/GX/CG — does the latency confound reach the Dataset B
    pre-window?** CS:M3: "the onset-locked ±4 s window is anchored to
    visual onset… which on the timeline sits well after the ~3 s
    pre-token wait for both formats — so the window itself is likely
    insulated from this particular confound". DS:M1 ("If the pre-window
    includes the retrieval wait, the contrast is confounded"), GX:C3
    ("contaminates D_i^B"), CG:C1 ("the 'pre' window may contain a
    mixture of waiting-for-retrieval…") all assume contamination. CS
    alone reasons from the timeline; none reconstructed it. CS also
    limits the behavioural reach to "any ad − no ads" ("it does not
    touch the implicit-vs-explicit or early-vs-late contrasts"), which
    CG:C1 contradicts ("For timing comparisons, the problem is not
    eliminated").

16. **CG:m2 vs CS:C1 — "attention shift".** CG: "'Attention shift' is
    generally used responsibly… This is a **pass**". CS: "Introduction
    §1.4, Contributions, p. 4: '…some novel metrics like attention
    shift'" listed as a delivered metric (taxonomy I12). CG did not
    check the Contributions list.

17. **S6 split.** DS:C2 and GX:C2 make "confirmatory without
    pre-registration" a CRITICAL; CS:J2: "the word 'confirmatory' is
    never used as a substitute for 'pre-registered' anywhere I found…
    honest framing, not overclaiming". CG does not raise it. Both DS and
    GX write "The same author chose… k = 37… 4 s width" without quoting
    where the thesis claims temporal precedence beyond "before the
    corresponding results were read".

18. **S11 split.** DS:C5, GX:Major-2, CG:M12 treat the 32.5 % agreement
    as unestablished validity; CS:J2: "Adequate — this is one of the
    thesis's more careful sections". Not a false premise, but the same
    number carries opposite verdicts.

19. **CG:M5 — ".047".** "primary paired-t result is Holm-significant at
    .047 for re-exposure trust" — no other jury gives .047; CG's own
    table gives only "re-exposure trust −0.49". Unverified, unique.

20. **DS:D2 — "Table E.2 shows 57% and 87% for ≥5 ratings".** Unique to
    DS; no other jury cites Table E.2 or these percentages.

21. **CS — brief leakage into the review text.** "exactly the five
    'explicit early' hits your brief named", "better than your brief's
    premise", "per your instruction", "I have not treated the absence of
    a post hoc power calculation as a defect, per your instruction". CS
    discloses that its checklist (Job 2 headings) and its ceiling check
    came from the brief; the other three do not disclose, but their
    item lists have the same order (see near-duplicates).

22. **S24 split.** DS:V2 ("Definitions 1–6 internal consistency…
    Consistent") and CS:J2 ("Genuinely clean formal work") declare the
    formalism clean against taxonomy S24 (T−1 slots so a₄ undefined; A
    both set and sequence; R_max ambiguous). GX hedges ("full equations
    need line-by-line check"). All three checked the brief's triple
    (k vs i, δ̃≤δ⁽ᵃ⁾≤δ, T−1 range), not S24's items.

23. **L13 unanimously contradicted.** GX:R-Appendices ("they correctly
    keep off-4 s cells as sensitivity. No major contradictions found
    there"), CG:m4 ("handled correctly"), CS:J2 ("Adequate… This is a
    strength"). None quotes Table 7.9 against App D.1.

## Per-jury top 5 and overall score

**DS (Deepseek)** — Overall **6.5** (RQ 8, Design 7, Stats 5, Technical
7, Results discipline 6, Consistency 6, Reproducibility 8, Writing 7).
1. Abstract–Discussion contradiction on EEG ("depends on how and when").
2. Confirmatory status without pre-registration.
3. EEG multiplicity: Holm within each of sixteen measures, not across.
4. Dataset B reliability: single trial, no reported reliability; ρ=.80.
5. Genre classifier validity: 32.5 % agreement with runtime label.

**GX (Grok 4.6)** — Overall **5.5** (RQ 7, Design 5, Stats 5, Technical
6, Results discipline 6, Consistency 5, Reproducibility 4, Writing 7).
1. Post-hoc trust cell in the Abstract vs the analysis contract.
2. Sole confirmatory EEG timing effect Holm .0496 at n=18 with turn-depth confound.
3. Classifier agrees with runtime label 32.5 % — nulls about instrument, not theory.
4. Extra ~3 s silent wait on advertised turns contaminating the Dataset B pre-onset window.
5. Nothing pre-registered; author chose markers, k=37 and 4 s width.

**CG (ChatGPT)** — Overall **6.5** (RQ 8, Design 6, Stats 6, Technical 8,
Results discipline 6.5, Consistency 5.5, Reproducibility 7.5, Writing 7).
"could pass after a substantive revision pass".
1. Advertised turns take ~twice as long to begin — advertising vs advertising-plus-latency.
2. Banner changes disclosure, separability, onset geometry and salience at once — no pure format contrast.
3. Exploratory explicit-early slow-power cluster in the Abstract while both confirmatory Dataset B markers are null.
4. RQ2/RQ4 answered with a narrower genre-shift construct from an unstable classifier.
5. n=18, one onset trial per cell, reconstructed onsets, no EOG, single trust item — ρ=.80 a replication candidate only.

**CS (Claude Sonnet 5)** — Overall **6.5** (RQ 7, Design 6, Stats 8,
Technical 7, Results discipline 6, Consistency 6, Reproducibility 7,
Writing 7).
1. C2 — Conclusion's disclosure/timing prescription vs §8.6 disclaimer.
2. C3 — the 4.60 dB explicit-early δ figure not in Chapter 7.
3. M2 — task never modelled for primary outcomes.
4. M3 — the dropped ~3 s latency confound.
5. C1 — "attention shift" as a claimed contribution in §1.4.

## Near-duplicate phrasing

- **"no moderation detected in this sample"** — DS:M4 Change: "Temper
  to 'no moderation detected in this sample.'"; GX:Major-5 Change:
  "Soften to 'no moderation detected in this sample'." Identical target
  sentence.
- **"The same author chose … k = 37 … 4 s width"** — DS:C2: "The same
  author chose the measures (k = 37 epochs, 4 s width), the contrasts,
  and the correction families"; DS:X: "The same author chose k = 37
  epochs, the 4 s width, the sixteen measures, and the Holm families";
  GX:C2: "author chose measures, k=37, 4 s width, and the two EEG
  markers"; GX:Top5: "you chose the markers, k=37 and the 4 s width".
- **"two-item BFI-10"** — DS:M4 "two-item BFI-10 traits is low power";
  GX:Major-5 "two-item BFI-10 scales; absence of evidence is not
  evidence of absence".
- **"Cronbach α=.61 on notice"** — GX:minor-1, CG:M4 ("notice α=.61"),
  CS:J2 ("Cronbach's α=.61 on notice"); none gives a location. CS
  attributes the item list to "your brief".
- **"~3 s" latency rounding** — DS:M1 "~3 s of extra silent retrieval
  wait"; GX:C3 "extra ~3 s wait before first token"; CS:M3 "The ~3 s
  retrieval-latency confound"; taxonomy S1 "~3 s". DS, CG and CS all
  quote the same thesis sentence "retrieval runs before the first token
  (median 3.03 s), so that silent wait is about 6 s".
- **Kruskal–Wallis "270 … rows" + "participant-as-unit rule"** —
  GX:minor-5 "Kruskal–Wallis on 270 conversation rows is flagged
  exploratory with ICC; still violates the participant-as-unit rule";
  CG:M14 "Kruskal–Wallis on 270 conversation rows remains formally
  inconsistent with the participant-as-unit rule"; CS:J2
  "Kruskal–Wallis on 270 rows vs. the participant-as-unit rule".
- **"general guidance (98/156)"** — GX:minor-6 "Advertised-product genre
  is mostly 'general guidance' (98/156)"; CS:J2 "Advertised genre mostly
  'general guidance' (98/156)". Taxonomy L11 lists 98/156 as a
  Discussion-only number.
- **"bare-ceiling / deployed-floor"** — GX:Major-2 "Ceiling under bare
  context (2.45/3 shifts) and floor under deployed context"; CS:J2
  heading "Bare-ceiling vs. deployed-floor as a researcher degree of
  freedom"; CG:C5 "bare utterance: mean 2.45 shifts / 3; deployed
  window: mean 0.40; 70% of conversations never shift".
- **"Multiplicity across the two scores"** — DS:M6 title "multiplicity
  across two scores"; GX:D3 "multiplicity across the two scores
  under-stated"; CS:J2 "Multiplicity across the two EEG scores (DAi,
  DBi)".
- **"one trial per cell" / "single trial per cell"** — DS:C4 "Dataset
  B: single trial per cell, no reliability"; CS:J2 heading "Dataset B,
  one trial per cell"; CG:Top5 "one onset trial per cell".
- **"Definitions 1–6 (k vs i, δ̃≤δ⁽ᵃ⁾≤δ, T−1 range)"** — DS:V2, GX:VERIFY-4
  ("indices (k vs i), inequality δ̃≤δ^{(a)}≤δ, T−1 range"), CS:J2
  ("k vs i, the δ̃≤δ⁽ᵃ⁾≤δ inequality, T−1 range"). Same three check
  items in the same order.
- **KV-cache "320 MiB"** — DS:V1, GX:VERIFY-3, CG:R-System Design, CS:J2
  all verify the same product; CG and CS both reduce it to "20 KiB ×
  16,384".
- **Verdict opener** — DS: "What would make me challenge this thesis in
  the defence?"; CG: "What would make me challenge this thesis in the
  defence is not the existence of the experiment"; CS: "What would make
  me challenge this thesis in the defence is not the statistics". The
  prompt's question echoed verbatim.
- **Job-2 checklist order** — GX's MINOR list and CS's Job-2 headings
  run in the same order: order/carry-over → Latin-square/task → pooling
  lab/crowd → latency → onset precision → θ/λ → confirmatory without
  pre-registration → Likert/ceiling/single-item/α=.61 → estimator
  disagreement → post hoc → … → permutation → Kruskal–Wallis → 98/156 →
  two scores → 2,560 map → mediation drift → Definitions → KV-cache.
  CG's M-list follows the same spine (M1 arm, M2 task, M3 carry-over,
  M4 Likert, M5 estimator, M6 θ/λ, M7 boundary, …, M13 permutation, M14
  KW, M15 negative control, M16 clicks, M17 personality, M18 post hoc).
- **"exploratory orange cells"** — GX:D2 "the five compositional cells
  are exploratory orange cells on the onset-locked board"; CS:T "Five
  of the six exploratory orange cells… sit… explicit early (§8.3)".
- **"105 … where 128 are expected"** — DS:M7, CG:T, CS:J2 all quote the
  pair; DS alone calls the null "presented as a finding".
- **Estimator triple ".063 / .048 / .026"** — DS:D1, GX:minor-2, CG:M5,
  CS:J2 all cite exactly "t Holm .063, LMM .048, raw Wilcoxon .026".
