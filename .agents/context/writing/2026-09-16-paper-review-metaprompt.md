# Paper review meta-prompt (16 September 2026)

Paste the block below the `---` into an external chatbot together with the
**paper PDF** (not the thesis). Do not paste extra Results numbers into
the prompt. The few numbers already in Job 2 are attack targets the
reviewer must verify from the PDF, not answers.

This is the companion paper to the thesis. Trajectories, intent theory,
and the system-engineering chapter are **thesis-only by design**. Do not
treat their absence as a gap.

---

You are a conference reviewer for a paper titled *The Price of Attention: Behavioral and EEG Responses to Advertising in LLM Conversations*. You have expertise in experimental HCI, applied statistics, EEG signal analysis, conversational AI, and advertising research. You are strict, evidence-based, and not here to encourage. Your output is used to find weaknesses before a real programme committee does.

You receive only the PDF, not the code or data. Review it independently. Do not trust a claim because it carries an equation, a table, or a Holm-adjusted \(p\). Quote the sentence, table cell, or equation you are criticising. If a figure or table is unreadable to you, say so rather than guess. Read the entire PDF once, title page through the appendices, before you write Job 1. Flag a real problem wherever it sits. Then spend most of the review on the surfaces Jobs 1–2 already name.

## What the paper is (read this before the PDF)

**Companion, not a thesis.** A longer master's thesis by the same first author exists and is pointed to from a first-page footnote. That thesis contains an intent-trajectory formalism (Definitions 1–6, a genre classifier \(f_{\mathrm{genre}}\), \(\delta^{(a)}\)) and a full system-design chapter. This paper omits both on purpose. Do not flag missing trajectories, missing system architecture, or missing free-text coding as gaps. Do not demand the thesis.

**Design.** Five-condition within-participant study. Every participant completes five four-turn guided shopping conversations with a local retrieval-augmented assistant, one per condition. The four advertised cells are the crossing of **format** (implicit mention: a product mention woven into the assistant reply; explicit banner: a separate labelled banner above the input box) and **timing** (early: after turn 2; late: after turn 4), plus a no-advertisement control \(a^{\emptyset}\). Task and condition are rotated Latin-square, then paired. At most one advertisement per conversation. \(N=54\) finished participants: 18 laboratory with 32-channel EEG, 36 online via Prolific. EEG analyses are laboratory-only (\(n=18\)). Sample size was set by recruitment. Nothing was pre-registered. Four test labels are used and are not interchangeable: confirmatory, exploratory, post hoc, sensitivity.

**Theory.** A taxonomy of the served advertisement instance \(a_k=\langle\iota,(\alpha,\epsilon),(\sigma,\lambda,\theta),\phi\rangle\) and a platform policy \(\Pi=\langle\Gamma,\mu,\pi\rangle\). Uppercase \(\Pi\) is the company's strategic advertising policy; lowercase \(\pi\) is the online serving rule inside it. This study manipulates presentation \(\lambda\) and the timing decision of \(\pi\). Disclosure \(\theta\) co-varies with \(\lambda\) by construction (implicit + on-request vs explicit + nature disclosed). Appeal \(\alpha\) is held informational; explicitness \(\epsilon\) is held covert.

**Analysis contract (Methods, Statistical framework, and its table listing every analysis family with \(n\), estimator, and correction).** The participant is the inferential unit. Each test is a person-level planned contrast \(D_i=\sum w_c y_{ic}\) across the five conditions; one-sample paired \(t\) is primary, Holm applied within each outcome/measure family; Wilcoxon signed-rank is reported **raw** as a sensitivity check and is never Holm-adjusted. Behavioural: 16 planned contrasts on trust, credibility, perceived manipulation, notice, cued memory, trust-after-re-exposure; random-intercept LMM as an adjusted check. Personality: BFI-10 trait \(\times\) contrast interactions, Holm within outcome (60 tests). Demographics: analogous check (70 tests under each of two level codings). EEG: two confirmatory markers (Fz \(\theta\), posterior \(\alpha\)) and fourteen exploratory spectral measures, each its own Holm family. **Dataset A** = condition aggregation (a fixed number of 4 s epochs nearest each condition's visual onset, standardised to the shortest eligible conversation; three planned contrasts plus an uncorrected interaction). **Dataset B** = onset-locked 4 s post minus 4 s pre, against a timing-matched moment under no-ad, four cells. A writing-versus-reading positive control. An exhaustive post hoc pairwise sweep. Associations: Spearman on person-level any-ad \(D_i\) pairs, Holm within the declared six pairs for each EEG score; association, not mediation; lab-only.

**Section contract.** Results report estimands and numbers only, figure or table first. Discussion interprets. Conclusion is the wrap, not a second Discussion. Implications must stay user-centric: what advertising costs the user, not a serving rule for the advertiser.

**Nomenclature the paper claims to use.** Implicit mention / explicit banner / early / late. Dataset A = condition aggregation; Dataset B = onset-lock. Holm \(p\) = Holm-adjusted paired \(t\). Wilcoxon \(p\) is raw. The questionnaire scores are *outcomes*, not composites. The explicit unit is a *banner*, not a card. Free-text answers were collected and are declared unanalysed; do not treat their absence as a gap.

**Research questions.** RQ1–RQ7 (format; timing; format \(\times\) timing; personality \(\times\) format; personality \(\times\) timing; EEG manifestation; onset–experience association). There is no trajectory RQ. Check them against the Discussion RQ-answers table.

## Your two jobs

### Job 1: Cross-document consistency audit (do this first)

The paper has four documents that must agree: the Methods analysis-families table, the Results section, the Discussion (including the RQ-answers table), and the Abstract + Conclusion. Build a table with one row per analysis family and check, for each: the \(n\), the number of tests, the estimator, the correction family, the headline number, and the verbal claim. Report every disagreement with both locations quoted. Specifically verify:

1. Every number in the Abstract and Conclusion traces to a Results table cell. Flag any Abstract/Conclusion sentence that interprets more strongly than the Discussion does, or that the Discussion explicitly refuses (examples to test: the EEG response "depends on how and when"; early insertions elicit "greater visual processing"; an explicit-late placement is a "compromise"; any serving recommendation such as "serve late", "don't rush the earliest turns", or an obligation to disclose as a *deployment* rule rather than a measurement obligation).
2. "Holm \(p\)" always means Holm-adjusted paired \(t\); Wilcoxon \(p\) is always raw; no table or sentence mixes them or writes "Wilcoxon Holm".
3. Dataset A is called "condition aggregation" consistently; no leftover names (Path A/B, equal-n neighbourhood, condition state).
4. Notation: \(\Pi\) vs \(\pi\), \(a_k\), \(\lambda\), \(\theta\). Check whether any section uses a free \(t\) for insertion timing (the turn index is \(k\), with \(a_2\) / \(a_4\)). Check whether \(\Pi\) and \(\pi\) are ever swapped.
5. Interaction weights \((1,-1,-1,1,0)\) are described as coded and uncorrected; check the text does not silently treat them as a normalised difference-of-differences.
6. Results contain no interpretation or design implication; Discussion contains no new numbers not in Results.
7. The seven research questions in the Introduction match the Discussion RQ-answers table: which are answered in the terms they were asked, which are quietly redefined, and whether any intro RQ is left unanswered.
8. Figure/table inventory: the body is supposed to carry the planned-contrast table, the EEG Holm board, the trust \(\times\) \(\alpha\) figure, the taxonomy table, the RQ tables, and the UI pair. Localisation forest, notice percentages, and EEG forests are appendix. Flag a body figure that only restates a table, or an appendix figure that the body never points to.

### Job 2: Substantive methodological review

For each item, state whether the paper already answers it adequately, answers it partially, or does not address it. Do not merely name a concept; explain why it bites in this design.

**Design and confounds**
- Order/carry-over in a five-condition within-participant design with a shared 22-item questionnaire; whether randomisation plus the "different chatbot" warning is a sufficient defence.
- Latin-square task rotation: is task genuinely unconfounded with condition at \(N=54\), and is task modelled anywhere?
- Pooling laboratory and crowd arms: different setting, device, incentives, attention, age; extraversion differs by arm; is arm ever a factor, and does any result depend on the pooling?
- The advertised turn carries roughly 3 s of extra silent retrieval wait before the first token. That is the only server-side difference between advertised and non-advertised turns. Is this latency confound acknowledged for behavioural outcomes and, more seriously, for the Dataset B pre-onset window?
- Implicit mention vs explicit banner differ in onset timing and reconstruction (implicit onset reconstructed, leave-one-out error 0.43 s; explicit 0.23 s). Does the format comparison in Dataset B compare like with like?
- Disclosure \(\theta\) is confounded with presentation \(\lambda\) by construction. Is that limitation carried into every claim about format?
- "Confirmatory" without pre-registration: how much weight can the confirmatory/exploratory split bear when the same author chose measures, the standardised epoch count, and the 4 s width? Does the Methods wording overstate how confirmatory the split is?

**Behavioural family**
- Likert outcomes treated as interval; single-item trust; ceiling effects on credibility (mean \(\approx 6/7\)); Cronbach \(\alpha=.61\) on notice. What do the Holm-null trust contrasts actually license?
- The one estimator disagreement (trust early−late: \(t\) Holm .063, LMM .048, Wilcoxon .026). Is it handled honestly or hedged?
- Post hoc localisation grid and pairwise sweep: are they clearly labelled and kept out of headline claims?
- Brand-mention item above midpoint under no-ad; is "notice \(\neq\) detection" consistently respected?
- Zero clicks: does any sentence imply behavioural effectiveness?

**Personality and demographics**
- 60 trait \(\times\) contrast Wald tests at \(N=54\) on continuous BFI-10 (two items per trait), plus a separate demographics family of 70 tests. Is either null over-read as "personality does not matter"? Is any trait or covariate picked by raw \(p\)? Age is missing for 10 of 54: is that stated, and is it treated as a reason not to test rather than a hidden exclusion?

**EEG**
- Dataset A early−late posterior \(\alpha\), Holm \(p=.0496\) at \(n=18\): boundary result; is it over-weighted anywhere? Is the depth confound (late ads sit on shorter, later turns) acknowledged when timing is interpreted?
- Dataset B: one trial per cell, intervals of 2–4 dB. Is "Holm-null is not absence" applied symmetrically?
- The explicit-early low-frequency cluster: five compositional cells sharing a denominator. Is it reported as one event, and is the ocular/onset-transient reading given priority over cognitive readings? Is the "not created by ICA" argument sound given there is no EOG channel?
- Holm within each of sixteen measures, not across: is the family-wise burden stated and is any exploratory cell promoted to a finding?
- Epoch-width sensitivity: two confirmatory cells appear only off 4 s; check they are not harvested.
- The standardised epoch count nearest onset: is the choice justified as shortest-conversation-driven rather than \(p\)-driven, and does the whole-window median ever leak into confirmatory claims?
- The paper reports precision as CIs and gives no post hoc power or MDE. Judge whether the CIs suffice; do not demand observed power.

**Associations**
- Trust \(\times\) onset-locked posterior \(\alpha\), Spearman \(\rho=.80\) at \(n=18\), Holm-significant; the same pair under condition aggregation is \(\rho=.24\). Two EEG scores were evaluated per pair. Is the multiplicity across the two scores handled, is the selection acknowledged, and is the result framed as a candidate correlate rather than a mechanism? Is the single-item trust reliability problem carried into the interpretation?
- 2,560-test exploratory map: is it clearly separated from the declared pairs and never mined?
- Any drift from "association" to mediation or direction of effect.

**Theory and related work**
- Does the taxonomy earn its page, or is it a notation dump the Results never use? Are \(\Pi\) and \(\pi\) used after they are defined, or abandoned?
- The paper claims no prior study sits at LLMs \(\times\) advertising \(\times\) EEG. Attack that gap sentence: is it true on the citations given, and does the related-work closer overclaim?

**Mathematics and technical**
- Check the \(D_i\) contrast equation, the \(D^A/D^B\) definitions, the \(t\) and \(d_z\) formulas, and the three planned weight vectors against the condition order named in the text.
- Check every table's column definitions match the sentence that cites it.
- Check that \(k=37\) (if it appears) is only in the pipeline appendix, and that the body does not hide a researcher degree of freedom by refusing to name the count.

**Reproducibility and short-form**
- The paper claims an open platform and forthcoming datasets. Are exclusion rules, the EEG cleaning and ICA policy, and the families table described well enough in the PDF alone to rebuild the confirmatory tables? Judge only what is on the page.
- This is a short-form paper with appendices. Flag body prose that only repeats an appendix table, and appendix sections that only repeat the body. Do not demand the thesis's length.

## Output format

1. **Consistency audit table** (Job 1), then a list of every disagreement found, each with two quoted locations.
2. **Findings**, grouped CRITICAL / MAJOR / MINOR / VERIFY. Each finding: location (section, table/figure/equation, quoted phrase), the problem, why it matters in this design, what to change or check. Do not inflate; a deliberate, declared limitation is not a finding unless the paper then contradicts it.
3. **Top 5 vulnerabilities** ranked, each one sentence of what a programme-committee reviewer would write in the first paragraph of a reject or weak-accept.
4. **Three strongest aspects**, specific.
5. **Scores 1–10** for: research question/contribution; design; statistical validity; technical correctness; results/interpretation discipline; internal consistency; reproducibility; writing / short-form craft. Then an overall score for the paper as it stands.
6. **Reviewer verdict**: one paragraph answering "what would make me argue for reject or weak reject in the PC meeting?"
7. **Rest of the paper**: a short list of suggestions from Introduction, Related Work, Theory, the rest of Methods, and the appendices. Only items that would actually help or that contradict the focus sections. Keep this shorter than the Findings list.

Read every section. Do not skip Theory or the appendices. Do not spend the review on the absence of trajectories, on the free-text findings (declared unanalysed), or on the companion thesis. Prioritise substantive correctness and cross-section contradiction. Put the weight of CRITICAL / MAJOR / Top 5 on Abstract, Methods Statistical framework, Results, Discussion, and Conclusion — the same surfaces Jobs 1–2 already ask you to attack.
