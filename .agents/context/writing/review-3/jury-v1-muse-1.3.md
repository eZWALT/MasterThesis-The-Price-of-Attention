# Jury v1 — Muse 1.3 (15 Sep 2026)

Thesis: v1 PDF 156 pp (`docs/overleaf/thesis/_build/dissertation.pdf`).
Prompt: `../2026-09-11-thesis-review-metaprompt.md`.
In-IDE / extra dump (not one of the five web juries). Raw examiner
dump. Do not treat its table cells as Gold. Do not apply until
Walter says so.

---

# External examiner report — *The Price of Attention: Behavioural and EEG Responses to Advertising in Conversational AI*

I read the 156-page PDF cover-to-appendices (checked against `docs/overleaf/thesis` source where the PDF text was ambiguous). I quote the sentence, cell, or equation criticised. Where I could not verify a figure's readability from text extraction I say so. The thesis is substantially stronger than most MSc theses on this topic — and it still has five vulnerabilities a real committee would press.

---

## JOB 1 — Cross-document consistency audit

### 1A. One row per analysis family

Methods reference: `Tab. analysis-families` (Methods § Statistical Framework). Results reference: `Tab. results-summary` + `Tab. results-checks` (Results §7.7). Discussion reference: Ch.8. Abstract/Conclusion: frontmatter + Ch.9.

| Family (Methods name) | n | Tests declared | Estimator | Correction family declared | Results summary reports | Headline number | Verbal claim | Agreement? |
|---|---|---|---|---|---|---|---|---|
| Behavioural battery | 54 | 3 planned contrasts × 4 primary + 2 × 2 cued-recall = **16** | one-sample t on \(D_i\); Wilcoxon raw; random-intercept LMM | 3 within each primary; 2 within each cued-recall item | 16, **8 sig**, key `notice, any ad − no ads, +2.07 [1.53,2.62], Holm p<.001`, `Tab. beh-planned` | matches cell | "Manipulation and notice rise with any ad and more under explicit" | **Yes** |
| Personality moderation | 54 | 15 trait×contrast **within each primary** = 60 total | LMM trait×contrast, demographics as covariates | 15 within each outcome | 60, 0 sig, nearest `extraversion on credibility, Holm p=.18` | matches Appx `Tab. beh-personality` (extraversion early−late on credibility raw p=.012, Holm .178) | "No BFI-10 trait moderates" | **Yes, but see D1** |
| Free-text / open recall | 54 | — | collected, not analysed | none | —, not analysed | — | no claim rests on them | **Yes** |
| Dataset A, condition aggregation | 18 | 3 contrasts, **separately within each measure** | t on \(D^A_i\); Wilcoxon | within-measure | **6, 1 sig**, key `early−late posterior α −0.22 dB [−0.39,−0.04], Holm p=.0496` | matches `Fig. eeg-forests` + text §7.4 | "only Holm cell" | **Partial — see D2**: 6 = 3×2 confirmatory only; remaining 14×3 folded into "98" row. Methods implies 16×3. Defensible split but not stated in Methods table. |
| Dataset B, onset-locked | 18 | 4 contrasts, separately within each measure | t on \(D^B_i\); Wilcoxon | within-measure | **8, 0 sig**, nearest `implicit late Fz θ −1.38 dB [−2.80,0.04], Holm p=.22` | matches §7.4 "Holm-null in all eight" | null | **Same partial** |
| Positive control writing−reading | 18 | 2 | t on \(y_{\mathrm{write}} - y_{\mathrm{read}}\) | 2 confirmatory | 2, 1 sig, `Fz θ +0.60 dB [0.22,0.97], Holm p=.007` | matches `Tab. eeg-task-state` | "recordings register change" | **Yes** |
| Exhaustive pairwise post hoc | 18 | 10 (A) + 6 (B) **per measure** = 256 | same t; Wilcoxon | within-measure | **256, 1 sig**, `implicit early − explicit late Fz θ −0.28 dB, Holm p=.014` | matches §7.4 + Appx `Tab. app-posthoc-near` | post hoc, not a finding | **Yes** |
| Fourteen exploratory measures A+B | 18 | (3+4)×14 = **98** | same | within-measure | **98, 7 sig**, key `explicit early relative δ +0.19 [0.09,0.29], Holm p=.004` | matches `Fig. eeg-holm-board` | "slow-power tilt, one event" | **Yes, but count VERIFY — see D3** |
| Genre \(\delta^{(a)}_2\) | 54 | **4** | exact McNemar + paired-t interval on \(D_i=\delta^{(a)}_{2,i} - \delta^{\emptyset}_{2,i}\) | across 4 | 4, 0, `early pooled +0.046 [−0.082,0.174], Holm p=.94` | matches `Tab. traj-crossing` | null | **Yes** |
| Late \(N_{\mathrm{shift}}\) | 54 | **3** | paired t; Wilcoxon | across 3 | 3, 0, `late pooled −0.074 [−0.361,0.213], Holm p=1.00` | matches `Tab. traj-late` | negative control | **Yes** |
| \(\tilde{\delta}^{(a)}_2\) | 54 (108 convos) | **1 uncorrected** | one-sided permutation 20,000 draws | none | 1, 0, `9 vs 10.46 expected, p=.80` | matches `Tab. traj-aligned-counts` | chance | **Yes** |
| \(\hat g_1\) vs \(\hat g_4\) instrument check | 54 | **6** genres ≥5% | paired t; Wilcoxon | across 6 | 6, **4 sig**, `guidance 0.478→0.211, d_z=−1.00, Holm p<.001` | matches `Fig. traj-depth` | classifier reads depth | **Yes** |
| Behaviour×EEG | 18 | **6 pairs × 2 EEG scores = 12** (Fzθ/post-α × trust/cred/manip) | Spearman on any-ad−no-ad \(D\) pairs | Holm within 6 **for each score**; survivor also across 12 | reports "**6**, 0;1", key `onset-locked trust×post-α ρ=.80 [.48,.93], Holm p=.0004` | **undercounts**; text §7.6.1 also reports `ρ=.80, raw p=6×10⁻⁵, Holm p=.0004` and Appx screen `post-α Holm p=.001; absolute α ρ=.69 Holm p=.025` within 16 | "Supported" (RQ9) | **No — see D4** |
| Behaviour×trajectory | 54 | **6** | Spearman, same pooled weights | 6 | 6, 0, `manip×late N_shift ρ=.22 [−.05,.46], Holm p=.67` | matches §7.6.2 | null | **Yes** |
| Trajectory×EEG | 18 | **2** | Spearman, early-pooled−∅ both sides | 2 | 2, 0, `Fzθ×δ(a)_2 ρ=.47 [−.02,.78], Holm p=.095` | matches §7.6.3 | null | **Yes** |
| Behaviour×traj×EEG | 18 | **3** pairwise among the three \(D\)s + partialled | Spearman + partial | 3 | 3, 0, `trust×post-α given δ(a)_2 partial ρ=.80` | matches §7.6 | association not mediation | **Yes** |
| Demographics moderation | 54 (51/49 subsets) | **70 + 70** (5 factors×3 contrasts; two codings) | same LMM, joint Wald, Holm within outcome + OLS check | within-outcome | 70+70, 0, nearest `cued memory early−late by familiarity Holm p=.44` | matches `Fig. beh-demographics` | "no demographic moderates" | **No — not in Methods families table; see D5** |

### 1B. Every disagreement found (two quoted locations each)

**D1 — "Holm only on t" vs LMM-Holm and Spearman-Holm.**
Methods: *"Holm is applied only to those `t` tests, within the family named in Tab. analysis-families."* and *"Holm is the only correction used… the `p` values of the nonparametric sensitivity tests are reported raw."*
Results `Tab. beh-planned` column header: *"`LMM Holm p`"*, with cells e.g. *Trust early−late `LMM .048`*, and §7.6: *"so a Holm `p` here is a Holm-adjusted Spearman `p`"*. Either Holm was applied beyond `t` (contradicting Methods) or the labels are wrong. This is not cosmetic: the single most-cited estimator disagreement (trust early−late `t Holm .063` vs `LMM .048` vs `Wilcoxon .026`) turns on what "Holm" means in each column.

**D2 — EEG confirmatory/exploratory split not in Methods table.**
Methods table: *"Dataset A… 3 contrasts, separately within each measure"* (implies 16×3) and *"Dataset B… 4 contrasts, separately within each measure"* (implies 16×4). Results splits into *"Dataset A 6 tests"* + *"Dataset B 8 tests"* + *"Fourteen exploratory measures, A and B 98 tests"*. The split is sensible but never declared in Methods; a reader checking family-wise burden from Methods alone undercounts by 98 tests.

**D3 — Exploratory count VERIFY (possible double-count).**
Results summary: *"Fourteen exploratory measures, A and B… 98… 7"*. Discussion §8.3: *"Five of the six exploratory orange cells on the onset-locked side… sit in one column, explicit early… the sixth is implicit-late relative γ"* plus Dataset A *"confirmatory posterior α and relative θ"* = 2 + 6 = 8 orange cells at 4 s, of which 1 (post-α) is already counted in the confirmatory row. 8−1 = 7 matches the "7", but only if relative-θ (Dataset A exploratory) + 5 explicit-early + 1 implicit-late γ = 7. The board figure is not machine-readable in text extraction; I could not independently verify 7 vs 8. Flag as VERIFY, not as error.

**D4 — Behaviour×EEG test count.**
Methods: *"each behaviour×EEG pair is evaluated on both [EEG scores]… Holm within the six for each score, and a cell that survives is also reported Holm-corrected across the twelve."* Results summary: *"Behaviour×EEG… 6… 0;1"*. It should read 12 (6×2 scores). The headline `ρ=.80, Holm p=.0004` is reported as "within the declared six" (Discussion RQ9 row) in one place and alongside a separate 16-measure screen (`post-α Holm p=.001; absolute α Holm p=.025`, Results §7.6.1, `Fig. combos-trust-alpha b`) in another. Whether `.0004` is within-6, across-12, or within-16 is never pinned to one sentence. See CRITICAL C2.

**D5 — Demographics family absent from Methods.**
Methods families table has *"Personality moderation… the 15 trait×contrast interactions, within each primary outcome"* and text *"The personality family is the same mixed model with each centred BFI-10 trait… and collapsed demographic covariates."* Results §7.3 + `Tab. results-checks` introduce *"Demographic moderation (mixed model)… 70 + 70… 0"* as a full family (sex, education, familiarity, frequency, environment × 3 contrasts × outcomes, two codings). That family was never declared in Methods. The thesis is honest that it is exploratory, but Job 1 requires Methods↔Results agreement: this is a new family, not a covariate adjustment.

**D6 — Abstract/Conclusion vs Discussion on serving advice (strongest contradiction).**
Discussion §8.5: *"**This is not a recommendation to serve advertisements late or implicitly.** The design did not measure the advertiser's side at all…"*
Conclusion §9.1: *"What follows… is not a placement rule but an **obligation to disclose**, **to be patient** with monetisation rather than rush into the earliest turns simply because they command attention, and **to measure**…"* plus *"an advertisement they can recognise… is worth more to them than a recommendation offered as 'fake friend' advice"*.
"Not a placement rule" + "to be patient rather than rush into the earliest turns" + "obligation to disclose" **is** a placement/timing rule and a disclosure deployment rule, drawn without advertiser-side data and while disclosure \(\theta\) was confounded with format by design (§6.5.2: *"Disclosure is confounded with presentation"*). The Abstract is careful (*"providing evidence for serving policies"*); the Conclusion oversteps what Ch.8 explicitly refuses. The brief asked to test exactly `"be patient"`, `"don't rush the earliest turns"`, and `obligation to disclose as a deployment rule` — all three appear in the Conclusion paragraph quoted above.

**D7 — "Depends on how and when" — PASS with a near-miss.**
Discussion §8.3: *"They do not combine into one claim that the response depends on how and when the advertisement enters."* Neither Abstract nor Conclusion uses that sentence. Near-miss: Conclusion *"The neural response therefore appears to be concentrated at the point of insertion, where the two formats present the user with qualitatively different events"* invites the fused reading without stating it. No flag beyond noting the temptation is handled correctly in Discussion and loosely in Conclusion.

**D8 — "Greater visual processing" / "compromise" / RQ10-11 — PASS.**
Zero occurrences of *"greater visual processing"*, *"compromise"*, *"Wilcoxon Holm"*, *"Path A/B"*, *"equal-n neighbourhood"*, *"condition state"*, *"RQ10"/"RQ11"* in chapters + frontmatter. Dataset A is consistently *"condition aggregation"*; Dataset B *"onset-locked"*. One leftover: Discussion §8.3 *"on either path"* — the only use of "path" for A/B. Trivial, fix in copy-edit.

**D9 — Notation — PASS (declared alias).**
Theory Eq. ad-associated-shift defines \(\delta^{(a)}_k = I_k \delta_k\); Results §7.5: *"Definition 6 is written here in a shorter form: \(\delta^{(a)}_k\) for the ad-associated shift \(\delta_k(a_k)\)…, \(\tilde{\delta}^{(a)}_k\) for its genre-aligned subcase"*. \(f_{\mathrm{genre}}\) is consistent throughout. Interaction weights \((1,-1,-1,1,0)\) are listed as *"fixed in advance"* (Methods). They are **not** described as a normalised difference-of-differences, and Results reports only \(|d_z|\le 0.06\) for the interaction (scale-free, so the ×2 scaling cancels). No silent normalisation error, but the thesis should state the scale once (the mean \(D\) with these weights is twice the textbook interaction).

**D10 — Results contains interpretation; Discussion contains one new number.**
Contract says Results = numbers only. Results §7.5: *"A whole-conversation count is close to its ceiling, 2.45 shifts of a possible 3… so it has little room left in which to register an insertion"*; §7.6.1: *"The sign is positive: participants whose trust fell further… are those whose posterior α fell further…"*; §7.2.1: *"Trust falls only there (−0.69, Holm p=.031)"* (the "only" is a localisation claim, strictly post hoc). These are interpretations, though all are hedged and later repeated in Discussion. Conversely Discussion §8.3 introduces *"its smallest Holm p being .08 (Tab. app-posthoc-near)"* — a number that lives only in the appendix table, not in Ch.7 text. Minor contract breaches, not headline-changing.

**D11 — RQs vs RQ-answers table — PASS.**
Intro RQ1–RQ9 map 1:1 onto `Tab. rq-answers`. RQ2/RQ4 ask *"trajectory of the conversation"*, answered as *"implicit−explicit early \(\delta^{(a)}_2\) +0.093, Holm p=.91"* and *"early pooled \(\delta^{(a)}_2\) +0.046, Holm p=.94; late \(N_{\mathrm{shift}}\) −0.074"* — not redefined as "attention shift"; Discussion §8.4 explicitly: *"calling it an attention shift would require a causal argument this study reserved and did not make."* No RQ10/11. Task moderation correctly noted as *"not modelled as a moderator"* (Discussion §8.2), not smuggled in as an RQ.

---

## JOB 2 — Substantive review (adequate / partial / not addressed + why it bites)

### Design and confounds

**Order/carry-over (5×22-item battery + "different chatbot" warning) — PARTIAL.** The flow chapter is unusually honest (gating, deferred cued recall, BFI at end). But answering the same manipulation/notice items five times teaches participants to hunt ads by condition 3–5. Latin-square + random order spreads this across conditions on average; it does not remove a *condition×position* interaction (e.g. early-banner detection improving with practice). With \(N=54\) and no position factor in the confirmatory model, the defence is asserted, not estimated. The GEE check adjusts for session position only for trajectories, not behaviour. Bites because the headline timing effect (early>late manipulation +0.58) could partly be a learning gradient.

**Latin-square task rotation; task unmodelled — PARTIAL.** Methods: *"tasks rotated in Latin-square order… then paired so that, across participants, task identity is not confounded with condition."* At \(N=54\) with 5 tasks × 5 conditions, perfect balance needs multiples of 25 pairings; 54 is not divisible, and exclusions/beta-testers break it further. Realised balance is claimed to be *"written into the session log"* but no balance table appears in Results. Task appears only in trajectory Kruskal-Wallis (`p=.33`) and the GEE covariate, never in the behavioural LMM. Bites because tasks differ wildly in commercial intent (laptop vs pet) and product-match quality is admitted unknown (*"mostly unknown (but recorded)"*, Discussion §8.6).

**Pooling lab (\(n=18\), EEG, voucher, experimenter present) + crowd (\(n=36\), own device, Prolific pay, validation check) — NOT ADEQUATELY ADDRESSED.** Arms differ in setting, device, incentives, attention, age (lab 21–42 \(M=29.5\); crowd subset 23–56 \(M=35.7\)), power-use (8/18 vs 8/36 >5×/day), and extraversion (raw \(p=.039\), Holm .19). Arm is *"not a factor in the family"* (Discussion §§8.1/8.6) by declaration, not by test. No arm×contrast interaction, no leave-one-arm-out, no heterogeneity statistic. Bites because every behavioural headline pools across arms; if the timing effect lives in one arm, the pooled \(D\) is misleading. The extraversion arm gap makes the personality null harder to read.

**~3 s extra silent retrieval wait on advertised turns (System Ch.5: *"median 3.03 s… silent wait is about 6 s… the only ads-versus-no-ads difference in server wait"*) — NOT ADDRESSED for behaviour; PARTIAL for EEG.** This is the only server-side difference between ad and no-ad turns, yet Ch.7–8 never name latency as a confound for manipulation/trust/credibility. A 6-s silent stall before the first token is itself manipulative-feeling. For Dataset B it is worse: the pre-onset 4-s window on advertised turns contains a retrieval stall that the timing-matched \(a^{\emptyset}\) window does not. The thesis discusses onset-reconstruction jitter (0.23 s explicit / 0.43 s implicit) but not the stall. Bites fatally for any "ad vs no-ad" onset claim; the explicit-early tilt could partly be a waiting-vs-reading contrast.

**Implicit vs explicit onset asymmetry in Dataset B — PARTIAL.** Dataset Ch.4: explicit onset = *"assistant reply plus 0.49 s"*; implicit = *"injection event plus 1.57 s… lands before the reply has finished streaming; 30 of 36 implicit onsets are reconstructed"*, p95 uncertainty 0.43 s vs ~0.23 s. So Dataset B compares a banner painted onto a static page against a mention injected mid-stream with 2× the timing error, inside a 4-s window. Discussion §8.3 admits *"the direct implicit-minus-explicit comparison at onset does not survive correction, smallest Holm p=.08, so what stands is the explicit-early response against its own control and not a demonstrated difference between formats"* — correct, but the Abstract (*"transient slow-power tilt… with no comparable response at mention onset"*) and Conclusion invite the format comparison the design cannot support. Bites because the "where to look" message becomes a format message in any citation.

**Disclosure \(\theta\) × presentation \(\lambda\) confound — ADEQUATE as declaration, NOT as discipline.** Methods §6.5.2 and Discussion §8.6 state it plainly (*"cannot apportion any memory advantage… between presentation, disclosure label, and mere availability of a separable object"*). But behavioural Discussion (*"Format separates notice, manipulation, cued memory… in the same direction"*) and the Conclusion disclosure prescription repeatedly attribute effects to "format"/"banner vs mention" without re-attaching the caveat. Bites because the most citable memory result (explicit 8/10 vs implicit 6/10) cannot distinguish labelling from layout.

**"Confirmatory" without pre-registration — PARTIAL, wording overstates.** Methods: *"measures and weights were fixed on theoretical grounds before the corresponding results were read"* + *"Two complementary views of the same scores."* In a single-author thesis where \(k=37\) (*"shortest eligible window"*), 4-s width (*"fixed on these grounds before any contrast was estimated"*), the 16-measure set, and the \((\tfrac14,\tfrac14,\tfrac14,\tfrac14,-1)\) weights were all chosen by the same person who then read the results, "confirmatory" means "pre-read", not "pre-registered". The thesis never claims pre-registration (honest), but "two complementary views" implies independence the design does not have. Bites because the boundary \(p=.0496\) (see EEG) inherits confirmatory authority it has not earned. Downgrade "confirmatory" to "pre-specified" throughout.

### Behavioural family

**Likert-as-interval, single-item trust, ceilings, \(\alpha=.61\) — ADEQUATE with one over-licence.** The \(D_i\)-averaging justification + Wilcoxon + LMM + bootstrap + item-LOO appendix is exemplary. Limits are stated (*"Trust is a single item… least reliable"*, *"Credibility… mean 6 of 7… bounds what any contrast can show"*, *"notice \(\alpha=.61\)… index different things by design"*). Over-licence: Discussion *"Trust holds up… participants ended the session trusting the assistant about as much"* — a Holm-null on a ceiling-bound single item with ICC .39 and CI reaching −0.71 (`Any ad−no ads −0.34 [−0.71,0.03]`) does not license "about as much". The CI admits a 0.7-point drop. Should read "no detected difference under this constraint".

**Trust early−late estimator split (t Holm .063 / LMM .048 / Wilcoxon .026) — ADEQUATE reporting, HEDGED wording.** All three numbers appear in text, table, and `Fig. beh-estimators`; appendix notes Shapiro rejects 7/16 and bootstrap agrees 15/16. Honest. Hedged: *"The one estimator disagreement which is borderline significant after correction"* — "borderline significant" after Holm is still null under the declared rule. The thesis does not upgrade it to a finding (correct), but the phrase invites citation as "trend". Replace with "Holm-null on the pre-specified estimator; nominal on two sensitivities".

**Post hoc grids kept out of headlines? — MOSTLY, one slip.** Localisation (`Fig. beh-localisation`: *"Trust falls only there (−0.69, Holm p=.031)"*) is labelled post hoc in caption and Discussion (*"Where trust does fall is a single cell of the post hoc grid"*). Slip: Conclusion summary elevates it — *"the one place trust falls below the ad-free condition is the early explicit banner (−0.69)"* — without "post hoc" in that sentence. A casual reader takes it as confirmatory.

**"Notice ≠ detection" — ADEQUATE.** *"Brand mention is already high in the no-ad control… so it is not treated as detection"* (Results §7.2.2) is respected throughout; detection item defined, Wilson intervals shown. No finding confuses the two.

**Zero clicks — ADEQUATE.** *"No participant clicked"* (Results §7.2.2, Discussion §8.1/8.6). No sentence implies behavioural effectiveness; Discussion explicitly *"It is not a measure of whether the pressure worked, and nothing in the family says it did."* Exemplary.

### Personality & demographics (60 + 70+70 tests, \(N=54\), BFI-10 two items/trait)

**Null over-read? — ADEQUATE, borderline exemplary.** Discussion: *"Fifty-four people are a modest sample for interaction terms… The null is a null under that constraint… It is not proof that personality or demography never matter."* No trait picked by raw \(p\) (nearest Holm .18/.44 reported as non-findings). The 70-test demographics family should have been in Methods (D5), but its interpretation is disciplined. Bites only in that BFI-10 two-item traits + \(N=54\) have near-zero power for `trait×contrast` — the family could not have found anything but huge moderation; stating the range (*"across the traits… this sample covers"*) is the right hedge.

### EEG

**Dataset A early−late post-α Holm \(p=.0496\), \(n=18\) — PARTIAL, over-weighted in Abstract/Conclusion.** The number is reported exactly once with CI \([-0.39,-0.04]\) and Wilcoxon .021 — good. Depth confound is admitted in Discussion (*"late ads sit on shorter, more fallback-labelled turns… not separable"*). But Abstract (*"posterior α power was lower for early than for late insertion"*) and RQ8 (*"Partly… −0.22 dB, Holm p=.0496"*) give it confirmatory headline status without the depth caveat in the same sentence. At \(p=.0496\) with 16 within-measure families (no across-measure control) and an unmodelled depth confound, this is the weakest cell to carry RQ8's "Partly". Bites because it is the only confirmatory EEG cell; the whole "timing registers neurally" claim rests on it.

**Dataset B Holm-null symmetry — ADEQUATE.** *"failure to reject on the confirmatory pair is not evidence of absence"* + *"intervals spanning 2–4 dB"* + *"one trial per cell… single 4-s response rather than average"*. The thesis does not use nulls to kill unfavoured leans while keeping favoured ones — except the tilt (below).

**Explicit-early slow tilt (abs δ, abs θ, rel δ, rel α, rel β sharing a denominator) — ADEQUATE as single-event framing, PARTIAL on mechanism.** Discussion correctly: *"five… cells… are one phenomenon rather than five separate findings"* + compositional warning + *"global θ moved while Fz θ did not… posterior α did not fall at onset… not what attentional capture would predict."* "Not created by ICA" argument: *"Leaving blinks in dilutes it and widens its spread, which is the opposite of an ocular-only account"* — without EOG this is suggestive, not dispositive; a blink-evoked transient survives ICA residuals and leaks into δ/θ in induced spectra. The thesis admits *"no dedicated EOG… cannot be measured directly"* and *"What produced the tilt is not settled"* — adequate. Bites because the Abstract's *"(↑δ,θ;↓α,β)"* bundles absolute and relative changes sharing a denominator as four independent arrows.

**Holm within each of 16, not across — ADEQUATE disclosure, UNDERSTATED burden.** Appendix: *"Restricting Holm to within a measure is deliberate: the five relative powers share a denominator…"*. Correct rationale, stated. But the family-wise chance of ≥1 false orange cell across 16 measures × 7 contrasts at \(\alpha=.05\) is far above 5%; the board should carry that warning in its caption, not only in the appendix tier paragraph. No exploratory cell is promoted to "finding" in Discussion (tilt stays "exploratory… to be replicated") — good discipline.

**Off-4-s cells (2-s explicit-early Fzθ +3.30 Holm .021; 8-s explicit-late post-α −1.22 Holm .023, `Tab. eeg-width`) — ADEQUATE (kept sensitivity).** *"They stay sensitivity"* / *"do not revise the 4-s family"* / *"Taking either as the primary… would replace the pre-specified estimand with a window chosen after inspection."* Exemplary. Do not harvest.

**Median \(k=37\) nearest-onset; whole-window medians — ADEQUATE.** *"\(k=37\) is the shortest eligible window, so every condition contributes exactly 37 epochs… fixed in §Dataset-A"* + *"stored Gold keeps whole-window median; confirmatory tests use this aggregation"*. Justified as shortest-conversation-driven, not \(p\)-driven. No evidence whole-window features leak into confirmatory claims. The "nearest onset" choice (vs random 37) is a degree of freedom, but disclosed.

**No post hoc power/MDE, CIs only — ADEQUATE, agree.** CIs (`[−0.39,−0.04]`, `2–4 dB spans`, `[.48,.93]`) suffice; observed power would add nothing. Do not demand it.

### Trajectories

**Instrument validity (ThradBERT 83.8% on own data; 32.5% agreement with runtime; bare 2.45/3 shifts vs deployed 0.40) — ADEQUATE, the best chapter.** The thesis does not interpret nulls before establishing the instrument fails: ceiling/floor table, 6-window sweep (all Holm-null, smallest unadjusted .096 → Holm .58), fallback-by-turn logistic (`turn β=0.34 p=.0003`), depth drift (`guidance 0.478→0.211`), advertised-genre overlap (98/156 `guid`). *"failure of the instrument on this corpus, not a demonstration that such a sequence does not exist."* Correct.

**Context choice as researcher DF; six-window sweep as answer — ADEQUATE.** Primary (bare) declared before deployed-sensitivity; sweep recipes *"fixed before the tests were run"*, Holm across six. The sweep is itself multiplicity, handled. No window fished.

**\(\delta^{(a)}_4\) undefined; late as "control" — MOSTLY CONSISTENT.** Methods: *"Late advertisements have no following utterance, so \(\delta^{(a)}_k\) does not exist after turn 4… late conditions therefore serve as a negative control."* Results: *"no late condition can enter it"* / *"late conditions… carried by \(N_{\mathrm{shift}}\) instead… negative control"*. One loose sentence (Results §7.5 header *"Presentation format and the late-advertisement control"*) implies late tests format; it tests \(N_{\mathrm{shift}}\), a different estimand — fair comparison as control, not as format contrast. Minor wording fix.

**Permutation across 108 conversations breaks pairing — ADEQUATE (acknowledged as conversation-level).** Methods: *"permutation of \(g^{(a)}\) is the one conversation-level exception"* to participant-as-unit. Results reports conversation counts (9/108 vs 10.46). Acknowledged; two early ads per person induce dependence the permutation ignores — could cluster-permute by participant as sensitivity. Minor.

**Kruskal-Wallis on 270 rows vs participant-as-unit — ADEQUATE (flagged + ICC).** *"These are the exploratory conversation-grain tests… participant ICC 0.043–0.111"* + appendix full table. Flagged as exploratory with ICC is sufficient for a thesis, though a clustered test would be better. Not a finding-driver.

**Advertised genre mostly `guid` (98/156) — ADEQUATE, admitted before null.** *"asks whether the next message moves into the genre of the product… close to unanswerable… hard to tell apart from a shift that would have happened anyway."* Correct order: weakness first, null second.

**Holm-null as verdict on theory vs defence beyond instrument — ADEQUATE.** *"That is a failure of the instrument… not a demonstration that such a sequence does not exist"* + *"cannot serve as a cheap proxy… until shown to detect insertion."* Neither kills Definitions 1–6 nor saves them. The inequality \(\tilde{\delta} \le \delta^{(a)} \le \delta\) and \(T-1\) range check out (see Maths).

### Associations

**Trust × onset post-α \(\rho=.80\), \(n=18\), two EEG scores per pair — PARTIAL, the thesis's riskiest number.** Reported: Dataset A same pair \(\rho=.24\) raw \(p=.34\); Dataset B \(\rho=.80\) raw \(p=6\times10^{-5}\) Holm \(p=.0004\) (within six); 16-measure screen `post-α Holm p=.001; abs-α ρ=.69 Holm p=.025`. Selection across two scores (A vs B) + 16-measure screen means the cited `.0004` is the best of ≥3 looks; the "also across twelve" correction does not cover the 16-screen. LOO stability (.77–.86) and Pearson/Kendall agreement are good but do not fix selection. Single-item trust reliability unmeasured; onset-α split-half .56; lower bound .48 correctly flagged as *"the number to carry"* — but RQ9 *"Supported"* + Abstract *"candidate neural marker of a trust drop"* frame it as a finding, not a bounded hypothesis. With \(n=18\), one influential participant can move \(\rho\) by ~.05; the scatterplot (`Fig. combos-trust-alpha a`) needs inspection for leverage (cannot verify from text). Bites because this is the thesis's most citable result and its CI, while excluding zero, spans "moderate" to "near-perfect".

**2,560-test map — ADEQUATE.** *"105 raw hits where 128 expected, none survives Holm"* + 336-test joined set + Freedman-Lane \(p\ge.23\). Clearly separated; the coherent process×Pope block (\(\rho=-.69\) raw \(p=.001\) etc.) is named as *"interesting… not a sixth independent finding"* with the pre-specified follow-up prescribed. Exemplary exploratory discipline.

**Mediation/direction drift — ADEQUATE.** *"association and not mediation… None fixes direction"* (Methods, Results, Discussion ×3) + *"dependence can run either way, or through a third variable: a participant who distrusts may look…"*. No drift found.

### Mathematics & technical

- **Defs 1–6: PASS with one wording fix.** \(\delta_k=1[\hat g_{k+1}\neq\hat g_k]\), \(N_{\mathrm{shift}}=\sum_{k=1}^{T-1}\delta_k\), \(p_i=(1/T)\sum 1[\hat g_k=g^{(i)}]\) (sums to 1), \(N_{ij}\), \(D=|\{\hat g_k\}|\), \(H=-\sum p_i\log p_i\), \(\delta^{(a)}_k=I_k\delta_k\), \(\tilde{\delta}^{(a)}_k=\delta^{(a)}_k 1[\hat g_{k+1}=g^{(a)}_k]\), \(\tilde{\delta}\le\delta^{(a)}\le\delta\) (holds since indicators \(\in\{0,1\}\)). Indices: Theory uses \(k\) for time, \(i\) for genre (\(g^{(i)}\)) — consistent except \(R(g^{(i)})\) defined as *"length of the maximal contiguous run"* (singular; if a genre recurs in two runs, which run? Should read "maximum over runs" or per-run). \(k\) vs \(i\) otherwise clean.
- **\(D_i=\sum w_c y_{ic},\ \sum w_c=0;\ t=\sqrt{n}\,\overline{D}/s_D,\ d_z=\overline{D}/s_D\): PASS.** Standard paired-t on contrasts; df \(n-1\) implied. \(D^A_i=\sum w_c\operatorname{med}_{\ell\in N_{ic}(37)} y_{i\ell}\), \(D^B_i=(y_{\mathrm{post}}-y_{\mathrm{pre}})_a-(y_{\mathrm{post}}-y_{\mathrm{pre}})_{\emptyset}\): PASS, matches Gold shapes \(18\times5\times16\) / \(18\times6\times16\).
- **KV-cache arithmetic: PASS.** \(16384\cdot1\cdot10\cdot2\cdot2\cdot256\cdot2\,\mathrm{B}=16384\cdot20\,\mathrm{KiB}=320\,\mathrm{MiB}\) — verified: 10 layers × 2 KV × 2 heads × 256 dim × 2 B = 20,480 B/token = 20 KiB/token; ×16384 = 320 MiB. Correct. (Gated-DeltaNet layers excluded — stated.)
- **Table columns vs citing sentences: ONE FAIL (D1).** `Tab. beh-planned` "LMM Holm p" contradicts *"Holm applied only to t"*. All other columns (\(\overline{D}\), 95% CI, \(d_z\), Holm \(p\), Wilcoxon \(p\)) match citing sentences.

### Reproducibility (PDF alone)

**PARTIAL.** Strengths: full questionnaires reprinted, task briefings + LLM prompts (base/inject/aware/HyDE) reprinted, EEG chain thresholds (notch 50, bandpass 0.5–40, avg ref, spline interp, FastICA 1–40 Hz fit, \(|r|\ge0.35\) + frontal \(\ge1.5\times\) mean, \(\le3\) comps, reject 1050 µV pp / 0.5 µV SD, Welch 2-s 50% overlap, \(\Delta f=0.5\)), Gold shapes/grains/join keys, freeze dates (behavioural Gold 8 Sep 2026), package versions (Python 3.13, MNE 1.12, SciPy 1.17, NumPy 2.2, statsmodels). Gaps: no random seeds (20k-draw permutation "seeded" but seed value absent), no randomisation/allocation log, HyDE `num_docs/tokens/llm_max_tokens` placeholders unfilled, FAISS/BM25 fusion weights given (80/20, RRF \(k=60\), \(k=30\to10\to1\)) but reranker threshold absent, ICA component maps not shown, exclusion folder-tags listed but counts per tag absent, crowd age partial (26/36). Cannot rebuild tables from PDF alone; with the claimed open repo+data it is likely reproducible — judge the PDF, not the promise.

---

## Findings (do not inflate; declared limitations restated are not findings unless contradicted)

### CRITICAL (challenge in defence)

**C1. Conclusion prescribes what Discussion refuses — disclosure + timing rule without advertiser-side or \(\theta\) evidence.**
Location: Conclusion §9.1 *"not a placement rule but an **obligation to disclose**, **to be patient**… rather than rush into the earliest turns"* vs Discussion §8.5 *"**This is not a recommendation to serve late or implicitly**"* + Methods §6.5.2 *"Disclosure \(\theta\) co-varies with presentation… cannot apportion."* Problem: a deployment obligation + a "don't monetise early turns" rule from a design that measured only user-side cost, held \(\epsilon\) covert, and confounded \(\theta\) with \(\lambda\). Why it matters: the thesis's most-quoted paragraph will be cited as policy evidence; it exceeds the estimands. Change: delete "obligation", restore Discussion's refusal in Conclusion, or reframe as "design hypothesis for a disclosure-crossed follow-up".

**C2. \(\rho=.80\) trust×onset-α survives by selection across scores/screens at \(n=18\).**
Location: Results §7.6.1 *"\(\rho=.80\), raw \(p=6\times10^{-5}\), Holm \(p=.0004\)"* + *"Fig. combos-trust-alpha b screens trust against each of 16 onset-locked measures, Holm within sixteen. Two survive: posterior α (Holm \(p=.001\)) and absolute α (\(\rho=.69\), Holm \(p=.025\))"* vs Methods *"Holm within six for each score… also across twelve"*. Problem: the headline `.0004` is within-6; the 16-screen is a third look at the same pair; absolute-α is the same signal under another name (whole-scalp vs posterior). With single-item trust + split-half .56 + \(n=18\), "Supported" (RQ9) overstates. Why it matters: a \(\rho=.80\) at \(n=18\) with CI \([.48,.93]\) will be cited as "neural marker of trust drop"; the lower bound (.48) is the honest number and even that assumes no selection. Change: report one pre-declared multiplicity (across 12, or across 16 if the screen is confirmatory), demote RQ9 to "preliminary, requires pre-registered replication at \(n\ge50\) with per-ad trust", show leverage/LOO scatterplot in main text.

### MAJOR

**M1. Latency confound unacknowledged (behaviour + Dataset B pre-window).**
System Ch.5: *"retrieval runs before the first token (median 3.03 s)… silent wait is about 6 s… the only ads-versus-no-ads difference in server wait"* vs zero mentions of latency in Ch.7–8. A 6-s stall can itself raise pushing/steering scores and depress credibility; the Dataset B pre-window on ad turns contains stall, the \(a^{\emptyset}\) control does not. Check: add TTFT/latency as covariate or report ad−no-ad latency \(D\) × outcome correlations; for EEG, compare pre-window spectra ad vs \(a^{\emptyset}\) directly.

**M2. Format onset comparison in Dataset B is not like-with-like, but Abstract invites it.**
Dataset Ch.4: explicit *"reply plus 0.49 s"*, implicit *"injection plus 1.57 s… before reply finished streaming; 30/36 reconstructed"*, p95 0.43 s vs 0.23 s. Discussion handles it (*"not a demonstrated difference"*); Abstract *"tilt… with no comparable response at mention onset"* does not carry the caveat. Fix Abstract/Conclusion to attach "against own timing-matched control; formats not directly compared".

**M3. Holm-label contradiction (t-only vs LMM/Spearman Holm).**
Methods *"Holm applied only to t"* vs `Tab. beh-planned "LMM Holm p"` and §7.6 *"Holm-adjusted Spearman p"*. Decide: either Holm covers LMM+Spearman (rewrite Methods, justify) or relabel columns "LMM p (Holm within outcome)" vs "raw". Currently the trust early−late `.063/.048/.026` row is uninterpretable as a family.

**M4. Demographics 70+70 family appears without Methods declaration.**
Results §7.3/`Tab. results-checks` vs absent Methods row. Add it to the families table as exploratory with correction family, or move to appendix-only. Also: sex model \(n=51\), education \(n=49\) — state exclusion rule once (merging <5s is stated; missingness handling is not).

**M5. Boundary \(p=.0496\) carries RQ8 with unmodelled depth confound.**
Results §7.4 *"early minus late posterior α (−0.22 dB, Holm p=.0496)"*; Discussion admits depth confound but RQ8 *"Partly"* + Abstract headline do not. At \(n=18\) with 16 families, a single `.0496` should be "marginal, confounded, requires replication", not "registers in the EEG". Tone down or model turn-length/fallback share as covariates.

### MINOR

- m1. Results interpretive sentences (§7.5 ceiling *"little room"*, §7.6.1 *"participants whose trust fell…"*) belong in Discussion; move or flag as descriptive.
- m2. *"borderline significant after correction"* (§7.2.1) — replace with "Holm-null; nominal on sensitivities".
- m3. Conclusion elevates post hoc trust −0.69 without "post hoc" in-sentence; add it.
- m4. Interaction weights \((1,-1,-1,1,0)\) scale — note "twice the textbook interaction mean; \(d_z\) unaffected".
- m5. \(R(g^{(i)})\) "maximal run" ambiguous for recurring genres; define max-over-runs.
- m6. *"on either path"* (Discussion §8.3) leftover; replace with "on either estimand".
- m7. Abstract *"(↑δ,θ;↓α,β)"* mixes absolute/relative sharing a denominator; write "broadband slow-power tilt (see §8.3 for compositional reading)".
- m8. Task balance table (realised task×condition counts) missing; add one appendix table.
- m9. Arm heterogeneity: add arm×contrast sensitivity (or state why not); report lab-only vs crowd-only behavioural headlines in appendix.
- m10. Permutation dependence (2 early ads/person): cluster-by-participant sensitivity.
- m11. HyDE placeholders (`num_docs`, `tokens_per_doc`) unfilled; seed values absent — fill for reproducibility.
- m12. `Tab. results-summary` Behaviour×EEG "Tests 6" → "12 (6×2 scores)"; clarify which Holm (within-6 / across-12 / within-16) the cited `.0004` uses.

### VERIFY (need data/code, not PDF flaws)

- v1. Exploratory-EEG "7" count vs 8 orange cells (see D3) — confirm board tallies; check no double-count of confirmatory post-α.
- v2. `Fig. combos-trust-alpha a` leverage — confirm \(\rho=.80\) not driven by 1–2 participants (LOO .77–.86 suggests not, but inspect).
- v3. Figure readability — forest/board captions ≤2 lines claimed; PDF-extracted captions look compliant; confirm orange-asterisk Holm marking renders in print.
- v4. KV-cache "10/40 full-attention layers" — confirm against Qwen3.6-35B-A3B config cited; arithmetic itself verified.

---

## Top 5 vulnerabilities (what I would ask aloud)

1. You prescribe "obligation to disclose" and "be patient, don't rush early turns" while your Discussion says "not a recommendation" and your design confounds disclosure with layout — which sentence should a policymaker cite?
2. Your \(\rho=.80\) trust–alpha at \(n=18\) was selected across two EEG scores and a 16-measure screen with single-item trust — what is the selection-adjusted \(p\), and why is RQ9 "Supported" rather than "preliminary"?
3. The only server-side ad-vs-no-ad difference is a ~3 s silent retrieval stall — why is latency absent from every behavioural and Dataset-B model?
4. Your sole confirmatory EEG cell is \(p=.0496\) with 16 families and a depth confound you admit — why does it carry RQ8's "Partly" instead of "marginal, confounded"?
5. You pool lab and crowd with no arm factor despite different devices, incentives, ages, and an extraversion gap — show me the arm-split headlines; do any depend on pooling?

---

## Three strongest aspects (specific)

1. **Multiplicity honesty where it hurts.** 2,560-test map with *"105 where 128 expected, none survives"*, 336-test joined set, six-window trajectory sweep, off-width EEG cells quarantined as sensitivity, compositional warning on relative powers — a thesis that reports the looks it took.
2. **Trajectory failure report done right.** Ceiling (2.45/3, 97.4% shift) vs floor (0.40, 70% sticky), 32.5% runtime agreement, fallback-by-turn model, depth drift, 98/156 genre overlap — the null is attributed to the instrument before the advertisement, with the exact experiment that would redeem it named.
3. **Estimand separation for EEG.** Condition-aggregation vs onset-lock as *"different questions… do not combine"*, with the writing−reading positive control (`Fzθ +0.60 dB, Holm p=.007`) proving the pipeline can move — the right design lesson even though the confirmatory cells are null.

---

## Scores (1–10, thesis as it stands)

| Dimension | Score | One-line justification |
|---|---|---|
| Research question / contribution | 7 | RQ1–9 well-posed, user-side framing novel; trajectory theory unvalidated by its own test |
| Design | 6 | Clever 5-condition within-subject + EEG; latency, arm-pooling, task-balance, \(\theta\)-confound unhandled |
| Statistical validity | 6 | Pre-specified contrasts + sensitivities exemplary; Holm-scope contradiction, 16-family burden, \(\rho=.80\) selection, \(p=.0496\) weight |
| Technical correctness | 7 | \(D_i\)/t/\(d_z\)/\(D^A\)/\(D^B\)/KV-cache verified; \(R(g)\) wording, interaction scale need notes |
| Results / interpretation discipline | 7 | Results≈numbers, Discussion≈interpretation, exploratory quarantine; Abstract/Conclusion overstep twice |
| Internal consistency | 6 | Four-document audit mostly clean; D1, D4–D6 are real contradictions |
| Reproducibility (PDF alone) | 5 | Instruments/prompts/thresholds reprinted; seeds, allocation log, HyDE params missing |
| Writing | 7 | Short paragraphs, defined terms, honest limits; "borderline significant", post hoc elevation in Conclusion |
| **Overall** | **6.2** | A good thesis with two defence-grade overclaims; fix C1–C2 + M1–M5 and it is a 7.5. |

---

## Examiner verdict: what would make me challenge this in the defence?

I would challenge it, but I would expect it to pass after corrections. The experiment is real, the data are hard-won (54 behaviour + 18 EEG with a documented pipeline), and the most tempting over-readings are already refused in Discussion — which makes the two places the thesis does over-read (a disclosure/timing prescription in Conclusion that Discussion forbids, and a \(\rho=.80\) "neural marker" at \(n=18\) selected across scores/screens with single-item trust) stand out as choices, not accidents. Add the unacknowledged 3-s latency confound that shadows every ad-vs-no-ad contrast, the \(p=.0496\) confirmatory cell carrying an EEG claim with an admitted depth confound, and a pooled lab+crowd analysis with no arm check, and the defence has a full hour of fair, evidence-bound questions. None requires new data: relabel Holm scope, demote RQ9 and RQ8 to preliminary/marginal, restore Discussion's refusal in Conclusion, and add the four sensitivity checks (latency covariate, arm split, task balance, cluster-permutation) as an appendix. Do that, and the core contribution — felt manipulation +1.27 with format/timing main effects, a disciplined trajectory failure report, and an onset-locked design lesson — survives intact and deserves the degree.

---

## Rest of the thesis (short; only what helps or contradicts focus chapters)

- **Introduction:** RQ block naming measures that answer each RQ is excellent — keep. Problem statement's *"prescriptions for how companies could steer policies toward user welfare"* promises more than the disclosure-confounded design can deliver; soften to "cost estimates".
- **Related Work:** Tang (N=179, 49% miss + halo) and Salvi (CTR 22→61%, notice 18%) correctly motivate the notice≠detection split; neuromarketing survey + Afshar/GNN caveat (79% accuracy "rendered useless") is the right caution for any future classifier claim.
- **Theory:** \(\Pi=\langle\Gamma,\mu,\pi\rangle\) + \(a_k=\langle\iota,(\alpha,\epsilon),(\sigma,\lambda,\theta),\phi\rangle\) cleanly separates artefact from policy; the served instances (\(a^{\mathrm{imp}}\) on-request vs \(a^{\mathrm{exp}}\) nature, \(\epsilon\) covert, \(\phi\) session) pin what was actually manipulated. Fix \(R(g)\) max-over-runs.
- **Datasets:** Bronze/Silver/Gold lineage + Gold shapes (270 ratings, 216 recall, \(18\times5\times16\) / \(18\times6\times16\)) + join keys is audit-grade. Rename retrieval shortlist \(k=30\) vs EEG \(k=37\) distinctly (same letter, different objects) to avoid misreading.
- **System Design:** TTFT/latency paragraph is the thesis's most important confound admission — cross-reference it from Methods/Results instead of stranding it in Ch.5. KV-cache math verified. "Waiting room at most 1" follows from the 6-s hold — state as constraint, not feature.
- **Appendices:** Questionnaires, prompts, EEG thresholds, item-LOO (credibility early−late dies without `reliable-responses`, \(p=.159\) — material caveat, correctly kept out of headlines), personality/demographics full tables, trajectory sweep — exactly what a sceptic needs. Add seeds + allocation balance + arm-split headlines and reproducibility is complete.
