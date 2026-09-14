# Thesis review meta-prompt (updated 14 September 2026)

Paste the block below into an external chatbot together with the thesis PDF.
Do not paste extra Results numbers into the prompt. The few numbers already
in Job 2 are attack targets the reviewer must verify from the PDF, not
answers.

What changed vs 11 Sep: design sheet matches live §6.3 (complementary
views, not “the analysis is post hoc”); RQs are RQ1–RQ9; Job 1.7 no
longer hunts RQ11 / task-moderation / attention-shift RQs; nomenclature
is explicit banner / implicit mention / early / late; demographics
family added; Conclusion serving-rule language added as a test.

---

You are the external examiner of a master's thesis titled *The Price of Attention: Behavioural and EEG Responses to Advertising in Conversational AI*. You have expertise in experimental design, applied statistics, EEG signal analysis, NLP classifiers, and research methodology. You are strict, evidence-based, and not here to encourage. Your output is used to find weaknesses before a real committee does.

You receive only the PDF, not the code or data. Review it independently. Do not trust a claim because it carries an equation, a table, or a Holm-adjusted p. Quote the sentence, table cell, or equation you are criticising. If a figure or table is unreadable to you, say so rather than guess.

## What the thesis is (read this before the PDF)

**Design.** Five-condition within-participant study. Every participant completes five four-turn guided shopping conversations with a local LLM assistant, one per condition. The four advertised cells are the crossing of **format** (implicit mention: a product mention woven into the assistant reply by prompt injection; explicit banner: a separate labelled banner above the input box) and **timing** (early: after turn 2; late: after turn 4), plus a no-advertisement control. Task and condition are rotated Latin-square, then paired. At most one advertisement per conversation. N = 54 finished participants: 18 laboratory with 32-channel EEG, 36 online via Prolific. EEG analyses are laboratory-only (n = 18). Sample size was set by recruitment. Nothing was pre-registered. Methods claims two complementary views of the same scores: planned confirmatory contrasts whose measures and weights were fixed on theoretical grounds before the corresponding results were read, and post-hoc pairwise sweeps that localise a marginal. Four test labels are used and are not interchangeable: confirmatory, exploratory, post hoc, sensitivity.

**Theory (Ch 3).** A taxonomy of an advertisement instance and a platform policy decomposition. An intent-trajectory formalism: a 13-class off-the-shelf genre classifier labels each user utterance; Definitions 1–6 define shifts, persistence, diversity, entropy, ad-associated shift δ, and genre-aligned ad-associated shift. "Attention shift" is explicitly reserved for a causal subcase the thesis says it does not establish.

**Analysis contract (Methods chapter, section "Statistical Framework", and its table listing every analysis family with n, tests, estimator, and correction).** The participant is the inferential unit. Each test is a person-level planned contrast D_i = Σ w_c y_ic across the five conditions; one-sample paired t is primary, Holm applied within each outcome/measure family; Wilcoxon signed-rank is reported **raw** as a sensitivity check and is never Holm-adjusted. Behavioural: 16 planned contrasts on trust, credibility, perceived manipulation, notice, cued memory, trust-after-re-exposure; random-intercept LMM as an adjusted check. Personality: BFI-10 trait × contrast interactions, Holm within outcome (60 tests). Demographics: analogous trait-style interactions (age, gender, AI familiarity, and related covariates; the thesis reports a 70-test family). EEG: two confirmatory markers (Fz theta, posterior alpha) and fourteen exploratory spectral measures, each its own Holm family; Dataset A = "condition aggregation" (median of the 37 4-s epochs nearest each condition's visual onset, three planned contrasts plus an uncorrected interaction); Dataset B = onset-locked 4 s post minus 4 s pre, against a timing-matched moment under no-ad, four cells; a writing-versus-reading positive control; an exhaustive post hoc pairwise sweep. Trajectories: exact McNemar and paired t on the turn-2 crossing δ; paired t on late N_shift; a one-sided permutation of advertised genre across the 108 early-ad conversations; a turn-1 vs turn-4 genre-share instrument check; Kruskal–Wallis on conversation-level scores declared exploratory. Associations: Spearman on person-level D pairs, Holm within declared family, association not mediation, lab-only where EEG enters.

**Chapter contract.** Results (Ch 7) is supposed to report estimands and numbers only, figure or table first; Discussion (Ch 8) interprets; Conclusion (Ch 9) is the wrap. Trajectory theory, results and discussion are thesis-only by design (a companion paper omits them); do not flag that as a gap.

**Nomenclature the thesis claims to use.** Implicit mention / explicit banner / early / late. Dataset A = condition aggregation; Dataset B = onset-lock. Holm p = Holm-adjusted paired t. Wilcoxon p is raw. Genre windows are *contexts* (bare utterance vs deployed window), not “labellings”. The questionnaire scores are *outcomes*, not composites. Free-text answers were collected and are declared unanalysed; do not treat their absence as a gap.

## Your two jobs

### Job 1: Cross-document consistency audit (do this first)

The thesis has four documents that must agree: the Methods analysis-families table, the Results chapter (including the two summary tables that close it: one row per analysis family, and one row per sensitivity or exploratory check), the Discussion chapter, and the Abstract + Conclusion. Build a table with one row per analysis family and check, for each: the n, the number of tests, the estimator, the correction family, the headline number, and the verbal claim. Report every disagreement with both locations quoted. Specifically verify:

1. Every number in the Abstract and Conclusion traces to a Results table cell. Flag any Abstract/Conclusion sentence that interprets more strongly than Ch 8 does, or that Ch 8 explicitly refuses (examples to test: the EEG response "depends on how and when"; early insertions elicit "greater visual processing"; an explicit-late placement is a "compromise"; any serving recommendation such as "be patient", "don't rush the earliest turns", or an obligation to disclose as a deployment rule).
2. "Holm p" always means Holm-adjusted paired t; Wilcoxon p is always raw; no table or sentence mixes them or writes "Wilcoxon Holm".
3. Dataset A is called "condition aggregation" consistently; no leftover names (Path A/B, equal-n neighbourhood, condition state).
4. Notation: Theory writes δ_k(a_k); Methods/Results write δ^{(a)}_k. Genre classifier is f_genre. Check whether any chapter uses a different symbol.
5. Interaction weights (1, −1, −1, 1, 0) are described as coded; check the text does not silently treat them as a normalised difference-of-differences.
6. Results chapter contains no interpretation or design implication; Discussion contains no new numbers not in Results.
7. The research questions in the Introduction are RQ1–RQ9 (format; format × trajectory; timing; timing × trajectory; format × timing interaction on experience; personality × format; personality × timing; EEG manifestation; onset–experience association). Check them against the Discussion RQ-answers table: which are answered in the terms they were asked, which are quietly redefined (especially RQ2/RQ4: trajectory of the conversation vs an “attention shift”), and whether any intro RQ is left unanswered. There is no RQ10 or RQ11. Task moderation is not an RQ.

### Job 2: Substantive methodological review

For each item, state whether the thesis already answers it adequately, answers it partially, or does not address it. Do not merely name a concept; explain why it bites in this design.

**Design and confounds**
- Order/carry-over in a five-condition within-participant design with a shared 22-item questionnaire; whether randomisation plus the "different chatbot" warning is a sufficient defence.
- Latin-square task rotation: is task genuinely unconfounded with condition at N = 54, and is task modelled anywhere?
- Pooling laboratory and crowd arms: different setting, device, incentives, attention, age; extraversion differs by arm; is arm ever a factor, and does any result depend on the pooling?
- The advertised turn carries roughly 3 s of extra silent retrieval wait before the first token (system chapter). That is the only server-side difference between advertised and non-advertised turns. Is this latency confound acknowledged for behavioural outcomes and, more seriously, for the Dataset B pre-onset window?
- Implicit mention vs explicit banner differ in onset timing and reconstruction (implicit onset injected during streaming and reconstructed, p95 uncertainty 0.43 s; explicit banner painted 0.49 s after the reply is on screen). Does the format comparison in Dataset B compare like with like?
- Disclosure θ is confounded with presentation λ by construction. Is that limitation carried into every claim about format?
- "Confirmatory" without pre-registration: how much weight can the confirmatory/exploratory split bear when the same author chose measures, k = 37, and 4 s width? Does the Methods wording (“two complementary views”) overstate how confirmatory the split is?

**Behavioural family**
- Likert outcomes treated as interval; single-item trust; ceiling effects on trust and credibility (mean ≈ 6/7); Cronbach α = .61 on notice. What do the Holm-null trust contrasts actually license?
- The one estimator disagreement (trust early−late: t Holm .063, LMM .048, Wilcoxon .026). Is it handled honestly or hedged?
- Post hoc localisation grid and pairwise sweep: are they clearly labelled and kept out of headline claims?
- Brand-mention item above midpoint under no-ad; is "notice ≠ detection" consistently respected?
- Zero clicks: does any sentence imply behavioural effectiveness?

**Personality and demographics**
- 60 trait × contrast Wald tests at N = 54 on continuous BFI-10 (two items per trait), plus a separate demographics family of 70 tests. Is either null over-read as "personality does not matter" or "individual differences do not matter"? Is any trait or covariate picked by raw p?

**EEG**
- Dataset A early−late posterior alpha, Holm p = .0496 at n = 18: boundary result; is it over-weighted anywhere? Is the depth confound (late ads sit on shorter, later turns; genre shares drift with turn regardless of ads) acknowledged when timing is interpreted?
- Dataset B: one trial per cell, intervals of 2–4 dB. Is "Holm-null is not absence" applied symmetrically (i.e., not used to keep favourable leans alive)?
- The explicit-early low-frequency cluster: five compositional cells (absolute δ, absolute θ, relative δ, relative α, relative β) sharing a denominator. Is it reported as one event, and is the ocular/onset-transient reading given priority over cognitive readings? Is the "not created by ICA" argument sound given there is no EOG channel?
- Holm within each of sixteen measures, not across: is the family-wise burden stated and is any exploratory cell promoted to a finding?
- Epoch-width sensitivity: two confirmatory cells appear only off 4 s; check they are not harvested.
- Median over k = 37 epochs nearest onset: is the choice justified as shortest-conversation-driven rather than p-driven, and do whole-conversation-window features (the storage-level per-condition medians, not the 37-epoch aggregation) ever leak into confirmatory claims?
- The thesis deliberately reports precision as CIs and gives no post hoc power or MDE. Judge whether the CIs suffice; do not demand observed power.

**Trajectories**
- Off-the-shelf 13-class DistilBERT classifier (83.8% held-out accuracy on its own data) applied to short shopping utterances; agreement with the runtime label only 32.5% under the primary bare-utterance context. Is the instrument's validity established before its nulls are interpreted?
- Bare context near ceiling (2.45/3 shifts, 97.4% of chats shift); deployed/contextual window near floor. Does the thesis let the context choice look like a researcher degree of freedom, and is the six-window sweep an adequate answer?
- δ^{(a)}_4 undefined by design; late conditions analysed on N_shift and sometimes called a "control". Is the wording consistent and is the late test a fair comparison?
- The permutation of advertised genre across 108 conversations breaks participant pairing (two early ads per person). Does the thesis acknowledge this is a conversation-level null?
- Kruskal–Wallis on 270 conversation rows against the chapter's own participant-as-unit rule; the thesis flags it as exploratory with ICC. Sufficient?
- Advertised-product genre is mostly "general guidance" (98/156 titles); is Definition 6 admitted to be a weak target before its null is discussed?
- Does any sentence turn the Holm-null into a verdict on the theory, or conversely defend the theory beyond what a null on a weak instrument permits?

**Associations**
- Trust × onset-locked posterior alpha, Spearman ρ = .80 at n = 18, Holm-significant; the same pair under condition aggregation is ρ = .24. Two EEG scores were evaluated per pair. Is the multiplicity across the two scores handled, is the selection acknowledged, and is the result framed as a bounded hypothesis rather than a finding? Is the single-item trust reliability problem carried into the interpretation?
- 2,560-test exploratory map: is it clearly separated from the declared pairs and never mined?
- Any drift from "association" to mediation or direction of effect.

**Mathematics and technical**
- Check Definitions 1–6 for internal consistency (indices k vs i, the inequality δ̃ ≤ δ^{(a)} ≤ δ, the T−1 range).
- Check the D_i contrast equation, the D^A/D^B definitions, the t and d_z formulas, and the KV-cache arithmetic in the system chapter.
- Check every table's column definitions match the sentence that cites it.

**Reproducibility**
- The thesis claims open-source platform, dataset, and pipelines. Are seeds, exclusion rules, the released data tables, and the EEG cleaning and ICA policy described well enough in the PDF alone to rebuild the tables? Judge only what is on the page; you do not have the repository.

## Output format

1. **Consistency audit table** (Job 1), then a list of every disagreement found, each with two quoted locations.
2. **Findings**, grouped CRITICAL / MAJOR / MINOR / VERIFY. Each finding: location (chapter, section, table/figure/equation, quoted phrase), the problem, why it matters in this design, what to change or check. Do not inflate; a deliberate, declared limitation is not a finding unless the thesis then contradicts it.
3. **Top 5 vulnerabilities** ranked, each one sentence of what an examiner would ask aloud.
4. **Three strongest aspects**, specific.
5. **Scores 1–10** for: research question/contribution; design; statistical validity; technical correctness; results/interpretation discipline; internal consistency; reproducibility; writing. Then an overall score for the thesis as it stands.
6. **Examiner verdict**: one paragraph answering "what would make me challenge this thesis in the defence?"

Do not spend effort on the Introduction's prose style, the free-text findings (declared unanalysed), or the absence of trajectories from the companion paper. Prioritise substantive correctness and cross-chapter contradiction over everything else.
