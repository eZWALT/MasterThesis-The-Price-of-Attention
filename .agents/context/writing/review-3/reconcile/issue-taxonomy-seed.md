# Canonical issue taxonomy (seed, 15 Sep)

Seeded from OP / FB / GS. Map every criticism in a jury dump onto one of
these IDs. If none fits, add `NEW-<initials>-<n>` with a one-line causal
claim. One causal claim per ID; do not merge distinct causes because
they share a topic.

## Surface claims (Abstract / Ch 9 vs Ch 8)

- I1 Ch 9 serving prescription ("obligation to disclose, be patient with monetisation, not rush the earliest turns") vs §8.6 "not a recommendation"
- I2 Ch 9 "prescription is about disclosure" while θ (disclosure) is bundled with λ (presentation) by design
- I3 Ch 9 / §8.6 "the informative answer is at the event / signal is at onset" vs confirmatory record (Dataset A moved, all 8 Dataset B null)
- I4 Abstract / Ch 9 "trust fell only under the early banner" — post hoc label dropped; cell is Holm .031 in 4-way but .078 in 10-pair family
- I5 Abstract / Ch 9 "no comparable response at mention onset" vs §8.3/8.6 "formats not shown to differ" (smallest Holm .08)
- I6 Abstract band arrows ↑δ,θ ↓α,β conceal that α/β fell only in relative terms; "exploratory" label dropped
- I7 Abstract "posterior α lower for early than late" without depth caveat / estimand label / boundary p
- I8 Abstract "neither personality nor demographics moderated any outcome" — age untested, outcomes limited, demographics undeclared
- I9 Ch 9 "cost not distributed evenly across users / users who respond more strongly ... greatest loss of trust" from one ρ=.80 at n=18 with 0/130 moderation
- I10 Ch 9 "concentrates on the explicit banner arriving early" vs §8.1 "singles out no combination"
- I11 "Trust holds up" / "similarly" vs any-ad trust CI [−0.71, 0.03], raw Wilcoxon .016 (asymmetric null reading)
- I12 §1.4 claims "attention shift" metric that Ch 3 reserves; §1.2 promises "prescriptions for companies"
- I13 Ch 9 "cost is smaller than the debate suggests" — no referent
- I14 Abstract "candidate neural marker of a trust drop" — marker language from one association
- I15 Abstract "providing evidence for serving policies" framing

## Ledger (Methods ↔ Results ↔ Tables)

- L1 Behavioural format×timing interaction: no table row, no D/CI/p, not in Table 6.1; answers RQ5 and Abstract
- L2 EEG interaction weight (1,−1,−1,1,0) declared §6.3, never reported; Table 6.1 says 3 contrasts; weight not marked "coded, not halved"
- L3 Demographic moderation absent from Table 6.1 (only "covariates"); reported as 70+70; n varies 51/49/54; promoted to Abstract/Ch 9
- L4 Personality LMM "demographics as covariates" incompatible with n=54 and missing demographics
- L5 Behaviour×EEG: 12 cells counted as 6 in Table 7.8; promised across-12 Holm never printed
- L6 Table 7.8 three-way row: "Sig. 0" but key estimate partial ρ=.80; ".83" appears only in Discussion
- L7 δ₂⁽ᵃ⁾: exact McNemar declared primary, Table 7.5 Holm column is the paired t; McNemar missing for pooled row
- L8 Late N_shift: "negative control declared in Table 6.1" (not there); called "confirmatory" in §8.4 vs Methods "none confirmatory"; used as RQ4 evidence although pre-ad
- L9 ĝ₁ vs ĝ₄ "not a test but a check" yet Holm-corrected and counted as a family
- L10 §7.7 "nothing omitted from the tables" false (secondary qualities Fig E.2, interactions, three-way p)
- L11 Discussion-only numbers: 4.60 dB, |dz|≤0.37, ICC .39, .83, raw p .34; untabulated "about half / more than half / most" share; 98/156
- L12 Seven Holm-surviving exploratory EEG cells: only p printed (Fig 7.8), no M/CI/dz except relative δ
- L13 Epoch-width: Table 7.9 "4 s family does not hold at other widths" vs App D.1 "does not change the 4 s confirmatory family"; early−late posterior α never printed at 2/8/16/32 s or no-ICA
- L14 App D.2 "two hundredths to a tenth of a decibel, under 3%" vs −0.22 dB [−0.39, −0.04]
- L15 "Condition aggregation" = "sustained state over a whole condition" vs k=37 nearest-onset (148 s of 150–1008 s); orthogonality/independence claim; leftovers "equal-n cell", "on either path"
- L16 "Holm p" has three estimators (t, Spearman, Wald) under one label; Methods "Holm applied only to those t tests"
- L17 Table 7.9 "Sig." for fallback-by-turn counts raw p
- L18 Fig 8.1 caption "Asterisk: Holm p<.05" but no asterisks; undeclared contrasts drawn inside "declared associations"
- L19 Fig 7.12 / 7.13 marker captions contradict; 7.13b plots 32 scores, corrects 16
- L20 App D.2 "secondary" tier not among §6.3's labels
- L21 "borderline significant" used twice (once for Holm ≥ .44)
- L22 "δ₂⁽ᵃ⁾ score takes four values" — it takes five
- L23 Table 7.1 arm-comparison test not named
- L24 Table 8.1 RQ2/RQ4 "Not supported" while §8.4 says instrument failed → "not testable"; RQ4 structurally unanswerable; RQ2 narrowed to one cell
- L25 §7.5 "shorter form δₖ⁽ᵃ⁾ for δₖ(aₖ)" — no such form in Ch 3
- L26 Table 4.6 Kc whole-window counts in a "confirmatory" table; Fig 4.2 two Dataset A files vs one in Table 4.5; a∅ Dataset A neighbourhood undefined
- L27 Onset uncertainty stated two ways (LOO 0.23/0.43 vs p95 0.43); explicit reconstructed count not given
- L28 Sample n: "Fig 7.8 prints .050*" for a .0496 cell

## Substantive method

- S1 ~3 s retrieval wait on advertised turn not on §6.2.5 / §8.7 confound list; sits in Dataset B pre-window; behavioural any-ad co-intervention; 36 logged-measure tests silent
- S2 Notice item "noticed or clicked on sponsored buttons" is format-specific (no button in implicit) and double-barrelled
- S3 Boundary cell Holm .0496: width sensitivity run, not printed; 37-epoch window asymmetric between early (straddles onset) and late (before onset); depth/time-on-task
- S4 ρ=.80 exceeds reliability ceiling (split-half .56 × single-item trust); two scores evaluated, one selected; ρ_B vs ρ_A never compared; shared no-ad component
- S5 Task×condition: "not confounded" asserted, realised table not printed; task not in behavioural LMM; N=54 not multiple of 5
- S6 No pre-registration statement; "confirmatory" rests on self-attestation → "planned, not preregistered"
- S7 Ocular/no-ICA argument cites App D.1 which has no tilt numbers; no EOG; dilution argument non-discriminating
- S8 Format contrasts on notice / manipulation carried by one item each (Fig E.3), not stated as for credibility
- S9 "Trust near ceiling" false (trust means 4.7–5.4, SD ~1.7); credibility is at ceiling
- S10 Arm pooling: age gap, device, incentive; no by-arm outcome levels; crowd-only contrasts not shown
- S11 Genre classifier: mean max posterior .43 unused; no target-domain validation
- S12 App C.6 debrief says "ChatGPT", "selected randomly", personalisation; no ethics body / protocol id; consent does not name EEG or open release
- S13 Fig 6.1 illegible at print size; banner disclosure label string never quoted; mention position distribution not reported
- S14 Holm-within-measure rationale ("dependence would distort") statistically wrong
- S15 Behavioural timing = exposure regime (early has two post-ad turns; late is terminal)
- S16 "Format" is a bundle (image, CTA, separability, reply altered), not λ alone
- S17 Implicit onset = injection +1.57 s during streaming; mention position free; window may hold no ad
- S18 Order/priming (a∅ position) not modelled in behavioural LMM
- S19 Kruskal–Wallis on 270 rows pseudoreplication; global permutation breaks participant pairing
- S20 Filter type/phase unspecified; zero-phase leakage across pre/post boundary
- S21 Wilcoxon "assumes no distributional form" misstated; 4-s rationale errors; 50 Hz "inside gamma" (30–40)
- S22 Embedding dim 1536 vs 459 MB index implies 1024
- S23 Catalogue 117,343 vs 117,243; 39 vs 30 categories; "200k" requirement vs 117k
- S24 Theory: A has T−1 slots so a₄ undefined; A both set and sequence; R_max ambiguous; "It has been proven"; D overloaded
- S25 Mechanical: broken refs ("Equation 4.2.4", "Figure 4.2.4", "Figure Figure 5.3", empty §5.2.1), truncated "at most 1", typos, Related Work exclamation marks / "barely nobody", DistilBERT 0.5 GB, Eq 4.5 argmax, rectangular tensors, ref years, "Behavioral" title vs "Behavioural", "Promotional Card"
- S26 Open-release claim: no DOI / manifest / seeds / model formulae
- S27 Session position 4 levels in Table F.2
- S28 Fig 7.7 panels differ ~8× in x scale under one caption
- S29 Related Work reads as annotated list; [22] antecedent unclear; [25] summary does not match paper
- S30 Positive control (write−read Fz θ) non-specific; Ch 9 over-generalises it to "the instrument"
- S31 Free-text / recognition share: notice×memory contingency not tabulated
