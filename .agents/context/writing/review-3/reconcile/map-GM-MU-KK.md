# Map: GM, MU, KK

Sources: `jury-v1-gemini-3-pro-full.md` (GM), `jury-v1-muse-1.3.md` (MU),
`jury-v1-kimi-k3-max.md` (KK). Taxonomy: `issue-taxonomy-seed.md`.
Mapping only; nothing checked against the PDF or the `.tex`.

Severity codes used in the matrix. GM: `J1` = Job 1 verify flag, `C/M/m/V`
= CRITICAL / MAJOR / MINOR / VERIFY (GM does not number them; numbered
here in order of appearance), `T5-n` = Top-5 question n, `R` = "rest of
the thesis" suggestion, `Vd` = examiner verdict. MU: `D#` = Job 1
disagreement, `P/NA/A` = Job 2 verdict partial / not addressed /
adequate, `C#/M#/m#/v#` = findings, `T5-n`, `R`. KK: `J1` = Job 1 table
cell, `D#`, `C#/M#/m#/V#`, `T5-n`, `R`. `?` = debatable mapping.

## Coverage matrix

| ID | GM | MU | KK | Severity given (per jury) |
|---|---|---|---|---|
| I1 Ch 9 serving prescription vs §8.6 "not a recommendation" | | x | x | MU:D6 ("strongest contradiction"), C1, T5-1. KK:D1, C2, T5-5 |
| I2 Ch 9 "prescription is about disclosure" while θ bundled with λ | | x | x | MU:D6, C1 ("θ confounded with format by design"), Job2 P ("ADEQUATE as declaration, NOT as discipline"). KK:C2 ("θ co-varies with λ by construction") |
| I3 Ch 9 / §8.6 "signal is at onset" vs confirmatory record | | ? | | MU:D7 "near-miss" only ("concentrated at the point of insertion… invites the fused reading"); no flag |
| I4 Abstract / Ch 9 "trust fell only under the early banner" without post hoc label | | x | x | MU:Job2 "MOSTLY, one slip", m3, D10 ("only" localisation). KK:J1, D16, Job2 P, m—(via D16) |
| I5 Abstract / Ch 9 "no comparable response at mention onset" vs "formats not shown to differ" | ? | x | x | GM:C2 action ("Limit claims regarding Format in Dataset B"). MU:Job2 P, M2. KK:D14, C2 |
| I6 Abstract band arrows conceal relative-only α/β; "exploratory" dropped | | x | x | MU:Job2 (arrows "bundle absolute and relative"), m7. KK:J1, D16 ("exploratory" label dropped) |
| I7 Abstract "posterior α lower for early" without depth caveat / boundary p | x | x | x | GM:M3. MU:Job2 P ("over-weighted in Abstract/Conclusion"), M5, T5-4. KK:J1, D16, M3, T5-3 |
| I8 Abstract "neither personality nor demographics moderated any outcome" | | ? | | MU:Job2 A ("near-zero power for trait×contrast… could not have found anything but huge moderation"); hedge accepted |
| I11 "Trust holds up" vs any-ad trust CI [−0.71, 0.03] | x | x | | GM:M1 ("nulls on trust are weakly informative"), T5-4, Vd. MU:Job2 "over-licence" ("does not license 'about as much'") |
| I12 §1.2 promises "prescriptions for companies" | | x | | MU:R Introduction ("promises more than the disclosure-confounded design can deliver") |
| I14 Abstract "candidate neural marker" from one association | x | x | | GM:M2 ("Demote this claim from the Abstract… generated hypothesis"). MU:Job2 P, C2 ("neural marker of trust drop"), RQ9 "Supported" overstates |
| L1 Behavioural format×timing interaction: no table row, no D/CI/p | | | x | KK:J1, D3, M1, V5, T5-4 |
| L2 EEG interaction weight declared §6.3, never reported; scale not marked | x | x | x | GM:J1 ("Unnormalized, this tests (A+D)−(B+C)"). MU:D9, m4. KK:J1 Dataset A, D3, M1 ("coded, not normalised"), T5-4 |
| L3 Demographic moderation absent from Table 6.1; n varies 51/49 | | x | x | MU:J1 "No", D5, M4 (n=51/49 exclusion rule). KK:J1 ("Missing from Table 6.1 and Table 7.8"), D5, M5 |
| L4 "demographics as covariates" describes a model never reported | | ? | x | MU:D5 ("a new family, not a covariate adjustment"). KK:J1, D5, M5 ("misdescribes") |
| L5 Behaviour×EEG 12 counted as 6; across-12 Holm never printed | | x | x | MU:J1 "undercounts", D4, m12, C2. KK:J1, D6, m6 ("Sig. 0; 1" unexplained), V2 |
| L6 Table 7.8 three-way "Sig. 0" but partial ρ=.80; ".83" Discussion-only | | | x | KK:J1 "Unreconciled", D7, D8, M7, V1 |
| L7 δ₂⁽ᵃ⁾ McNemar declared primary, Holm column is the t | | | x | KK:J1 "Estimator ambiguity", D4, M4 |
| L8 Late N_shift negative control labelling | | ? | | MU:Job2 "MOSTLY CONSISTENT" — header "Presentation format and the late-advertisement control" "implies late tests format" |
| L9 ĝ₁ vs ĝ₄ "not a test but a check" yet Holm-corrected | | | x | KK:J1 (minor), m12 |
| L10 §7.7 "nothing omitted from the tables" false | | | x | KK:D8 ("Against Ch 7.7's own completeness claim"), M6 |
| L11 Discussion-only numbers (4.60 dB, ICC .39, .83, "about half/more than half/most") | ? | x | | MU:D10 (Discussion §8.3 ".08" lives only in appendix). KK:D2, D8, M6, m1, V3 |
| L12 Seven exploratory Holm cells: only p printed | | | ? | KK:M6 ("4.60 dB… the only effect size given for the thesis's flagship exploratory event") |
| L13 Epoch-width: Table 7.9 vs App D.1; early−late α never printed at other widths | ? | | x | GM:m2 (inverted premise, see false premises). KK:J1, D10, M3, V4, T5-3 |
| L15 Condition-aggregation naming leftovers ("equal-n", "on either path") | ? | x | ? | GM:J1 verify ("equal-n neighbourhood" leak). MU:D8 ("on either path"), m6. KK:Passes ("one descriptive 'equal-n cell' in §6.3") |
| L16 "Holm p" has three estimators under one label | ? | x | | GM:J1 ("Wilcoxon vs. Holm p mixing" verify). MU:D1, M3, Maths "ONE FAIL" |
| L21 "borderline significant" used twice | | x | x | MU:Job2 "HEDGED wording", m2. KK:m5 |
| L24 Table 8.1 RQ2/RQ4 "Not supported" vs instrument failed | | | x | KK:M8, R Introduction |
| L25 §7.5 "shorter form δₖ⁽ᵃ⁾ for δₖ(aₖ)" — no such form in Ch 3 | ? | | x | GM:J1 verify ("The prompt warns… Verify no other chapters revert"). KK:D12, m3, R Theory. MU:D9 PASS (contradicts) |
| L27 Onset uncertainty stated two ways (LOO vs p95) | | | x | KK:D9, m14; Reproducibility ("LOO onset-reconstruction procedure" absent) |
| L28 Fig 7.8 prints ".050*" for .0496 | | | x | KK:J1, D11, M3, m2, T5-3 |
| S1 ~3 s retrieval wait not on confound list; inside Dataset B pre-window; behavioural co-intervention | x | x | x | GM:C1, T5-1, Vd, R System Design (?). MU:Job2 "NOT ADDRESSED for behaviour; PARTIAL for EEG", M1, T5-3, R System/Methods. KK:J1, C1, T5-1, Vd (i), R System/Methods |
| S3 Boundary cell .0496; depth/time-on-task confound | x | x | x | GM:M3 ("too fragile"), Vd ("fragile p=.0496"). MU:Job2 P, M5, T5-4. KK:Job2 P, M3, T5-3 |
| S4 ρ=.80 exceeds reliability ceiling; two scores, one selected; ρ_B vs ρ_A | x | x | | GM:M2 ("cherry-picking… ρ=.24"), T5-3. MU:Job2 P ("riskiest number"; split-half .56; 16-screen "best of ≥3 looks"), C2, v2, T5-2 |
| S5 Task×condition balance asserted, not printed; task not in LMM; N=54 not multiple of 5 | x | x | x | GM:m1 ("54 is not divisible by 25"), R Methods. MU:Job2 P, m8, R Datasets. KK:Job2 P ("balance in expectation"), R Datasets |
| S6 No pre-registration statement; "confirmatory" = self-attestation | ? | x | x | GM:m2 action ("Verify the 4 s window was strictly a priori"). MU:Job2 P ("Downgrade 'confirmatory' to 'pre-specified'"). KK:Job2 P, M2, V6, T5-2, R Introduction |
| S7 Ocular/no-ICA argument cites App D.1 with no numbers; no EOG | x | x | x | GM:R Appendices ("only ocular components… lack of an EOG channel"). MU:Job2 ("suggestive, not dispositive"). KK:Job2, M6 ("empty robustness citation"), R Appendices |
| S8 Format contrasts carried by one item each | | ? | | MU:R Appendices (item-LOO: "credibility early−late dies without `reliable-responses`, p=.159 — material caveat, correctly kept out of headlines") — noted as handled |
| S9 "Trust near ceiling" false; credibility is at ceiling | x | ? | x | GM:M1 asserts ceiling as true ("mean near ceiling (6/7)") — see false premises. MU:Job2 ("ceiling-bound single item"). KK:Job2 P ("a stretch for trust (Table E.1: 4.69–5.37)"), m7 |
| S10 Arm pooling: age gap, device, incentive; no by-arm levels | | x | x | MU:Job2 "NOT ADEQUATELY ADDRESSED", m9, T5-5, R Appendices. KK:Job2 P ("never stress-tested on a headline cell") |
| S11 Genre classifier: no target-domain validation | x | | x | GM:V2 ("32.5%… addressed before interpreting trajectory nulls"). KK:Job2 P ("no human-label validation on this corpus"), M8 |
| S12 App C.6 debrief says "ChatGPT", "selected randomly" | | | x | KK:M9, R Appendices |
| S16 "Format" is a bundle | | x | | MU:Job2 θ×λ ("cannot distinguish labelling from layout") |
| S17 Implicit onset during streaming; pre-windows unlike | x | x | x | GM:C2, T5-2. MU:Job2 P, M2. KK:Job2 P ("the unlike pre-windows are not discussed"), C1 |
| S18 Order/priming not modelled in behavioural LMM | x | x | x | GM:V1 ("different chatbot" warning). MU:Job2 P ("could partly be a learning gradient"). KK:Job2 P, m8, R Methods |
| S19 Kruskal–Wallis on 270 rows; permutation breaks pairing | x | x | | GM:C3, T5-5. MU:Job2 A (KW) / A-with-fix (permutation), m10. KK: "adequate" (no criticism) |
| S23 Catalogue 117,343 vs 117,243 | | | x | KK:D17, m11, R Datasets |
| S24 Theory: a₄ undefined; R_max ambiguous | x | x | | GM:R Theory ("δ_4^{(a)} … structural missing value"). MU:Maths ("maximal contiguous run" ambiguous), m5, R Theory |
| S25 Mechanical: broken refs, typos, Related Work exclamation marks, truncated "at most 1" | | ? | x | MU:R System ("Waiting room at most 1"… "state as constraint, not feature"). KK:D13, m4, m13, R Related Work, R System Design |
| S26 Open-release claim: no seeds / manifest | | x | x | MU:Reproducibility PARTIAL, m11, R Appendices. KK:Reproducibility "Partially adequate" |
| S30 Positive control over-generalised to "the instrument" in Ch 9 | | | x | KK:J1 positive-control row |
| S31 Notice×memory contingency not tabulated | | | ? | KK:D2 / V3 ("not derivable from Table E.2's marginals") |

Not raised by any of the three: I9, I10, I13, I15 (MU calls the
Abstract phrase "careful"; see false premises), L14, L17, L18 (MU v3 is
a generic render check only), L19, L20, L22, L23, L26, S2, S13, S14 (MU
calls the rationale "correct"; see false premises), S15, S20, S21, S22,
S27, S28, S29.

## New issues

| ID | Causal claim (one line) | Raised by | Severity given | Quoted thesis location (as the jury gives it) |
|---|---|---|---|---|
| NEW-GM-1 | Related Work neuromarketing literature does not feed the EEG methodology actually used, so it should be compressed | GM | R (Introduction / Related Work) | "Compress the neuromarketing literature if it does not directly feed into the EEG methodology used." |
| NEW-MU-1 | Methods Table 6.1 does not declare the EEG confirmatory (2 measures) vs exploratory (14 measures) split; family-wise burden read from Methods alone undercounts by 98 tests | MU | D2 ("Partial") | Methods table "Dataset A… 3 contrasts, separately within each measure" (implies 16×3) vs Results "Dataset A 6 tests" + "Dataset B 8 tests" + "Fourteen exploratory measures, A and B 98 tests" |
| NEW-MU-2 | Exploratory EEG survivor count "7" may double-count the confirmatory posterior-α cell among the 8 orange cells at 4 s | MU | D3, v1 (VERIFY) | Results summary "Fourteen exploratory measures, A and B… 98… 7"; Discussion §8.3 "Five of the six exploratory orange cells… the sixth is implicit-late relative γ" |
| NEW-MU-3 | Results chapter contains interpretive sentences that belong in Discussion | MU | D10, m1 | Results §7.5 "A whole-conversation count is close to its ceiling, 2.45 shifts of a possible 3… little room left"; §7.6.1 "participants whose trust fell further… are those whose posterior α fell further"; §7.2.1 "Trust falls only there (−0.69, Holm p=.031)" |
| NEW-MU-4 | Holm-within-16-measures leaves the cross-measure false-positive rate far above 5%; the board caption carries no family-wise warning (rationale accepted, burden understated) | MU | Job2 "ADEQUATE disclosure, UNDERSTATED burden" | Appendix: "Restricting Holm to within a measure is deliberate: the five relative powers share a denominator…"; "the board should carry that warning in its caption" |
| NEW-MU-5 | KV-cache "10/40 full-attention layers" count needs confirming against the cited model config (arithmetic itself verified) | MU | v4 (VERIFY) | "KV-cache '10/40 full-attention layers' — confirm against Qwen3.6-35B-A3B config cited" |
| NEW-MU-6 | Same letter k names two different objects (retrieval shortlist k=30, EEG epoch count k=37) | MU | R Datasets | "Rename retrieval shortlist k=30 vs EEG k=37 distinctly (same letter, different objects)" |
| NEW-KK-1 | g⁽ᵃ⁾ₖ loses its subscript outside Ch 3 | KK | D12 (part), m3 | "g^{(a)}_k in Ch 3 loses its subscript in Table 6.1/§7.5, 'permutation of g^{(a)}'" |
| NEW-KK-2 | Ch 9 "overall picture" paragraph states the trajectory null as a fact about the world while §8.4 calls it instrument failure (Conclusion surface; cf. L24 for the Table 8.1 surface) | KK | D15, C2 | Ch 9.1: cost is "not a collapse of trust and not a conversation steered towards the product" vs Ch 8.4: "That is a failure of the instrument on this corpus, not a demonstration that such a sequence does not exist" |
| NEW-KK-3 | The nine logged interaction measures behind the 36 exploratory tests are never enumerated | KK | m10, Reproducibility, R Appendices | "the nine logged interaction measures (never enumerated)" |
| NEW-KK-4 | Table 7.9 "126 tests" for epoch width/cleaning cannot be reconstructed from the text | KK | m9 | "Table 7.9's '126 tests' for epoch width/cleaning cannot be reconstructed from the text (presumably 9 branches × 14 confirmatory cells — say so)" |
| NEW-KK-5 | T=4 realisable ceilings (log 4, 4, 3) are not noted at Definitions 4–5, so Table F.1's headers surprise | KK | R Theory | "consider noting the T=4 realisable ceilings (log 4, 4, 3) at Definitions 4–5 so Table F.1's headers don't surprise" |

## Suspected false premises

1. **GM, J1 flag:** "The abstract asserts 'trust after re-exposure was lower for early than for late insertions'. Verify that this claim does not secretly rely on the raw Wilcoxon p=.026." — No other jury finds such an Abstract sentence; "trust after re-exposure" is not a measure any jury lists. MU: "The thesis does not upgrade it to a finding (correct)". KK Passes: "'Holm p' is never mixed with Wilcoxon (raw everywhere); no 'Wilcoxon Holm'". Reads as the brief's "Wilcoxon Holm" check item echoed as a finding.
2. **GM, MAJOR:** "Trust is a single item with a mean near ceiling (6/7)." and T5-4 "trust was measured with a single item exhibiting severe ceiling effects". — KK: "'Trust and credibility sit near the ceiling' is fair for credibility (6.0/7) but a stretch for trust (Table E.1: 4.69–5.37)". Taxonomy S9. The 6/7 figure is credibility's. Note KK locates the ceiling sentence in the thesis itself (§7.2.1, §8.1), so GM may be repeating the thesis, but the number is wrong for trust.
3. **GM, MAJOR location:** "Chapter 7, Table 7.2 / Abstract 'early insertion reduced credibility'". — No other jury quotes this Abstract sentence; MU's Appendix note is that credibility early−late "dies without `reliable-responses`" and is "correctly kept out of headlines". Quote unverified by the other two.
4. **GM, T5-4:** "You treat the lack of a significant trust drop as evidence that certain ad formats are 'safe'". — The quoted word "safe" appears in no other jury; MU's nearest quote is "Trust holds up… about as much".
5. **GM, MINOR:** "'Epoch-width sensitivity'. The confirmatory cells appear only off the 4 s window." — Inverted. MU: "Off-4-s cells (2-s explicit-early Fzθ +3.30 Holm .021; 8-s explicit-late post-α −1.22 Holm .023) — ADEQUATE (kept sensitivity)… Do not harvest." KK: "off-4 s cells correctly quarantined (8.3)". The confirmatory survivor is the 4 s cell; the off-width cells are sensitivity. Off-4 s cells treated as confirmatory.
6. **GM, J1 flag:** "check that old terms like 'equal-n neighbourhood' do not leak into the unprovided results text." — "unprovided results text" contradicts the dump header ("full PDF 156 pp"). MU: "Zero occurrences of… 'equal-n neighbourhood'"; KK: "one descriptive 'equal-n cell' in §6.3".
7. **GM, J1 flag:** "The prompt warns that Theory writes δ_k(a_k)." — Explicitly brief-derived. GM itself finds Eq 3.8 is δ^{(a)}; KK D12 confirms "the symbol δ_k(a_k) appears nowhere in Ch 3" (it is §7.5's). MU D9 goes the other way and calls it a "PASS (declared alias)" — MU contradicts KK and taxonomy L25.
8. **GM, J1 table, Trajectories row:** Correction "None stated for some". — MU and KK both list every trajectory family with its declared correction (Holm across 4, across 3, "uncorrected"/"none" declared for the permutation, across 6).
9. **GM, R System Design:** "quantify the exact KV-cache latency penalty for the RAG injection". — MU and KK both verify the KV-cache arithmetic as a separate item and locate the latency as retrieval before the first token ("median 3.03 s", §5.1.2). GM conflates KV-cache with the retrieval wait.
10. **GM, CRITICAL location:** "Chapter 4, Section 4.2.4… The advertised turn carries ≈3 seconds of extra retrieval wait." — MU and KK both quote the wait from "System Ch.5" / "§5.1.2"; §4.2.4 is where the onset reconstruction is. Location likely misattributed.
11. **GM, R Appendices:** "Ensure the ICA rejection criteria strictly states that only ocular components were removed." — MU and KK both report the ICA criteria as on the page (MU: "|r|≥0.35 + frontal ≥1.5× mean, ≤3 comps"; KK: "0.35 proxy correlation, 1.5× frontal topography, ≤3 components"). The ask may already be met; GM gives no quote.
12. **GM, V2:** "13-class DistilBERT classifier". — MU and KK call it "ThradBERT" / "the classifier"; neither gives "13-class". Unverified detail.
13. **MU, D9:** "Interaction weights (1,−1,−1,1,0) are listed as 'fixed in advance' (Methods)… Results reports only |d_z|≤0.06 for the interaction (scale-free, so the ×2 scaling cancels). No silent normalisation error". — KK D3 attributes the (1,−1,−1,1,0) weights to the Dataset A (EEG) declaration and says "The EEG interaction declared in Methods is reported nowhere"; the |d_z|≤0.06 is the behavioural interaction (Ch 7.2.1). MU fuses the EEG weight declaration with the behavioural result and so misses L1/L2.
14. **MU, Job2 Behavioural:** "a Holm-null on a ceiling-bound single item with ICC .39". — Trust called ceiling-bound; KK: trust 4.69–5.37 is "a stretch". MU's own quoted thesis line is "Credibility… mean 6 of 7". Also uses ICC .39 uncritically, which KK D8 flags as Discussion-only.
15. **MU, D6:** "The Abstract is careful ('providing evidence for serving policies'); the Conclusion oversteps". — Taxonomy I15 flags exactly that Abstract framing as an issue. Jury vs taxonomy contradiction.
16. **MU, Job2 EEG:** "Holm within each of 16, not across — ADEQUATE disclosure… Correct rationale, stated." — Taxonomy S14 says the within-measure rationale ("dependence would distort") is statistically wrong. Jury vs taxonomy contradiction.
17. **MU vs GM, KW on 270 rows:** MU "ADEQUATE (flagged + ICC)… Not a finding-driver"; KK "adequate (exploratory + ICC)"; GM "CRITICAL… driving down p-values" and T5-5. Two juries treat as declared-exploratory; GM treats as inferential violation.
18. **MU vs KK, section number of the refusal sentence:** MU "Discussion §8.5: 'This is not a recommendation…'"; KK "Ch 8.6: 'This is not a recommendation…'"; taxonomy I1 says §8.6. One of the two section numbers is wrong.
19. **MU, D2:** Methods "implies 16×3" for Dataset A vs KK J1: "Methods prose declares four weights incl. the interaction; Table 6.1 and Results carry three". Different reading of how many Dataset A contrasts Methods declares (3 vs 4).
20. **MU, Job2 Order:** "the headline timing effect (early>late manipulation +0.58)". — The +0.58 appears in no other jury; KK's timing quotes are the trust −0.69 cell and the notice/manipulation any-ad numbers. Unverified number.
21. **MU, C2 / v2:** "LOO stability (.77–.86)" and "split-half .56" — KK does not cite these; taxonomy S4 lists "split-half .56" so it is at least in the seed. LOO range unverified by the other two.
22. **KK, D8:** "Table D.2's nearest entry is −3.64 dB for a different pair" — no other jury; cannot be cross-checked here, listed for completeness (taxonomy L11 confirms 4.60 dB is Discussion-only).
23. **GM, MAJOR:** "Early ads sit on turn 2; late ads on turn 4." — MU and KK phrase depth as "shorter, more fallback-labelled turns" / "conversational depth"; turn numbers unconfirmed by them (KK's T=4 is consistent with late = turn 4).

Brief items from the metaprompt not asserted as findings by any of the
three (correct passes): "depends on how and when" in Abstract (MU D7,
KK Passes both PASS); "greater visual processing" (MU D8, KK Passes);
Fz β vs Fz θ mix-up (none); EEG interaction "never estimated" — KK says
"never reported"/"reported nowhere", MU says nothing, GM asks only
about scaling.

## Per-jury top 5 and overall score

**GM — Overall 6.5/10** (RQ 8, Design 6, Stat validity 5, Technical 7, Results/interp 5, Consistency 7, Repro 8, Writing 8)
1. Dataset B baseline: implicit-ad server-side latency confound the no-ad condition lacks.
2. Banners after streaming vs mentions mid-stream: format vs task state (reading vs waiting) in EEG.
3. ρ=.80 relies on selecting Dataset B over Dataset A (ρ=.24) at n=18 — multiplicity / capitalization on chance.
4. Lack of trust drop read as formats "safe", but single item with severe ceiling effects.
5. Kruskal–Wallis on 270 pooled non-independent rows violates participant-as-unit.

**MU — Overall 6.2/10** (RQ 7, Design 6, Stat validity 6, Technical 7, Results/interp 7, Consistency 6, Repro 5, Writing 7; "fix C1–C2 + M1–M5 and it is a 7.5")
1. "Obligation to disclose" / "be patient" vs Discussion "not a recommendation" and θ–layout confound — which sentence should a policymaker cite?
2. ρ=.80 at n=18 selected across two EEG scores and a 16-measure screen with single-item trust — selection-adjusted p; why RQ9 "Supported"?
3. ~3 s silent retrieval stall is the only server-side ad-vs-no-ad difference — why absent from every behavioural and Dataset-B model?
4. Sole confirmatory EEG cell p=.0496 with 16 families and admitted depth confound — why "Partly" not "marginal, confounded"?
5. Lab and crowd pooled with no arm factor (devices, incentives, ages, extraversion gap) — show arm-split headlines.

**KK — Overall 6.5/10** (RQ 8, Design 6, Stat validity 7, Technical 7, Results/interp 7, Consistency 6, Repro 6, Writing 6)
1. ~3 s extra silent retrieval wait sits in the implicit Dataset B pre-onset window — what is the onset-locked contrast contrasting; why not on the confound list?
2. Nothing pre-registered, §8.2 discloses an earlier uncorrected demographic pass — why should "confirmatory" outweigh "disciplined after the fact"?
3. Only confirmatory EEG survivor is p=.0496 at n=18, Table 7.9 says "does not hold at other widths", figure prints ".050" with asterisk — why a flat Abstract finding?
4. RQ5 answered with an interaction in no family table and no results table; where did the EEG interaction weights go?
5. Conclusion "obligation to disclose" / "be patient" vs Discussion bold "not a recommendation" and disclosure not tested — which page to believe?

Overlap across the three Top-5 lists: latency (GM-1, MU-3, KK-1);
p=.0496 cell (MU-4, KK-3; GM as MAJOR); ρ=.80 selection (GM-3, MU-2);
Ch 9 prescription (MU-1, KK-5; absent from GM entirely).

## Near-duplicate phrasing

- **Ch 9 prescription quote.** MU and KK quote the identical Conclusion sentence, with identical bolding of the same three phrases: "not a placement rule but an **obligation to disclose**, **to be patient** with monetisation rather than rush into the earliest turns simply because they command attention, and **to measure**". MU states outright: "The brief asked to test exactly 'be patient', 'don't rush the earliest turns', and 'obligation to disclose as a deployment rule'". Same for the paired refusal sentence "**This is not a recommendation to serve advertisements late or implicitly**" (MU §8.5 / KK §8.6). Likely real thesis text, but the selection and emphasis are brief-driven.
- **Latency quote.** MU and KK both quote "the only ads-versus-no-ads difference in server wait" and "median 3.03 s" / "silent wait is about 6 s". GM paraphrases "≈3 seconds of extra retrieval wait" and "silent wait" with the same pre-window argument ("the no-ad control will capture active reading/streaming" ≈ MU "a waiting-vs-reading contrast"). All three end with the same Dataset B pre-window reading.
- **Onset uncertainty numbers.** All three use "0.23 s" explicit / "0.43 s" implicit. MU and KK both add "30 of 36 implicit onsets are reconstructed" and "injection event plus 1.57 s" / "reply plus 0.49 s".
- **Interaction weight scale.** GM "Unnormalized, this tests (A+D)−(B+C)"; MU "the mean D with these weights is twice the textbook interaction… d_z unaffected"; KK "the interaction is on a doubled scale (harmless for d_z, misleading if a D is ever quoted)". Three juries, one argument, same "d_z unaffected" clause — brief-induced.
- **Latin square arithmetic.** GM "54 is not divisible by 25 (5 conditions × 5 tasks)"; MU "perfect balance needs multiples of 25 pairings; 54 is not divisible"; KK "balance in expectation at N=54, not guaranteed balance". MU and KK both quote "written into the session log" and both say no balance table appears.
- **Arm gap numbers.** MU "lab 21–42 (M=29.5); crowd subset 23–56 (M=35.7)… extraversion (raw p=.039, Holm .19)"; KK "age (29.5 vs 35.7) and extraversion (raw p=.039)". Same two numbers, same pairing.
- **ρ=.80 vs ρ=.24.** GM "the same pair under condition aggregation is ρ=.24"; MU "Dataset A same pair ρ=.24 raw p=.34". GM and MU both use "n=18… few outliers" / "one influential participant".
- **Quarantine vocabulary.** MU "off-width EEG cells quarantined as sensitivity… Do not harvest"; KK "off-width cells quarantined to the appendix"; "refusal to harvest nulls". Shared metaphor not in ordinary reviewing prose.
- **Trajectory diagnostics.** MU and KK both cite "2.45/3 vs 0.40", "32.5%", "83.8%", "98/156", "guidance 0.478→0.211, d_z=−1.00", "105 raw hits where 128 expected", "9 vs 10.46". Consistent numbers, plausibly from the page; noted for dependence tracking.
- **Estimator triple.** GM ".026 … .063"; MU "t Holm .063 / LMM .048 / Wilcoxon .026"; KK ".063/.048/.026". Same three-number row in all three.
- **Scores.** Design = 6 in all three juries; GM and KK both Overall 6.5; MU 6.2.
