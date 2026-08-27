# Results ≠ Discussion, and EEG 6.3 is on Overleaf

Date: 21 August 2026

Walter asked to push so he can review on Overleaf, and to lock the
Results / Discussion split in agent context immediately.

## Standing rule

- **Results** report the estimand, the sample, the numbers, the figure,
  the tables. No design implication. No “this means ads do not affect
  EEG.” No abstract-placement advice.
- **Discussion** interprets: precise Dataset A null vs dead pipeline,
  Dataset B underpowered / not absence, do not harvest leans, mention both
  off-width cells or neither, write−read is a task-state check not an
  ad result, C1 waits on Goal 1, H1–H3 are not a liking claim.
- **Limitations** hold the EEG constraints (n=18, one Dataset B trial,
  reconstructed implicit onset, no EOG, no ERP).
- Do not invert study order: Goal 1 behaviour first, then 2, then EEG.

Cursor rule: `.cursor/rules/results-vs-discussion.mdc`.

## What was pushed (publication Overleaf)

Repo: `docs/overleaf/publication/` (its own git remote).

- §6.3 `sec:results-eeg`: confirmatory 4 s ICA, n=18, person as n.
  Dataset A Holm-null; six CIs inside ±0.3 dB. Dataset B Holm-null; wide CIs.
  Write−read Fz theta one paragraph of numbers. Both 2 s and 8 s
  sensitivity cells. 16-feature 4 s board (`fig:eeg-holm-board`): Dataset A
  0/48; six Dataset B exploratory ICA-only hits named, no extra table.
  C1 deferred. Figure `fig:eeg-forests`, tables `tab:eeg-path-a` and
  `tab:eeg-path-b` (confirmatory only — do not duplicate the board).
- Figures: `Figures/eeg_confirmatory_forests.{pdf,png}`,
  `Figures/eeg_holm_board_4s.{pdf,png}`.
- §7.1: “EEG is not in” removed; EEG spectra are in, they do not
  replace Goal 1.
- §7.3: EEG interpretation, in paper voice (no "abstract" /
  "unfreeze" shop-talk; that stays here, not in the PDF):
  - what the markers mean: Fz theta = effortful control / WM; posterior
    alpha falls with visual engagement. Both pre-specified for that.
  - Dataset A tight null = no sustained reallocation of effort or visual
    engagement. Informative on Fz theta because write−read recovers
    +0.60 dB on it; posterior alpha is the weaker instrument (it fails
    the task-state check), so a posterior-alpha null is weaker evidence.
  - **Five of the six exploratory hits are one finding, not five.**
    Relative powers share the 0.5–40 Hz denominator, so global delta
    +4.60 dB (≈3×) mechanically lifts relative delta and depresses
    relative alpha/beta. The explicit-early column = one slow-power
    rise in the first 4 s.
  - Competing readings, data favour the dull ones: visual-onset
    transient (explicit has one, implicit does not) or saccade/blink.
    Against a cognitive reading, global theta moved but **Fz theta did
    not** — frontal-midline theta is focal, not whole-head. Against
    attention capture, posterior alpha did **not** desynchronise (it
    went slightly up).
  - ICA-only cuts both ways: ICA may have unmasked a real transient
    (dispersion drops) or redistributed ocular variance. No EOG, so
    undecidable. Say so.
  - Implicit-late relative gamma: 30–40 Hz is muscular, no absolute-gamma
    counterpart, compositional. Weakest cell.
  - **The nulls carry a message**: FAA, both Pope ratios, Kislov are the
    consumer-neuroscience engagement/arousal/approach indices, and none
    moved on either path, while behavioural notice separates the formats
    sharply.
- §7.5: EEG XXXX filled (n, Dataset B trials, onset p95 0.43 s, no EOG,
  unused pre-task baseline, no ERP). Typo
  `prookey coocoooduction` → `production`.

Pushed on `docs/overleaf/publication` `main` → Overleaf
`69bc4212f5ce9e2503edc596`: `360d8c6` (6.3 drafted, split enforced),
`e4b01af` (4 s Holm board), `200e19f` (shop-talk out of 7.3),
`dc0b3b3` (real interpretation of all 16), `a52afe4` (tables to
appendix, 16 measures defined).

## Where each EEG artefact lives (anti-redundancy layout)

Three artefacts, no overlap except two deliberate reference rows.

| Artefact | Where | Unique job |
|---|---|---|
| `fig:eeg-forests` | 6.3 | \(M\) ± 95% CI; the Dataset A vs Dataset B precision contrast |
| `fig:eeg-holm-board` | 6.3 | the other 98 tests; 16 coordinates × 7 cells |
| `tab:eeg-path-a`, `tab:eeg-path-b` | Appendix `sec:app-eeg-measures` | statistics of record: SD, raw \(p\), Wilcoxon Holm |

The board's top two rows repeat the confirmatory Holm \(p\). That is
intentional (reference frame for the fourteen below) and the caption
says so. Do not delete them, and do not re-add the tables to 6.3.

Appendix `sec:app-eeg-measures` now defines all 16 coordinates
(absolute ×5, relative ×5, Fz theta, posterior alpha, FAA, Pope ×2,
Kislov), states the tiers, and carries the dB-reading note
(\(10^{\Delta/10}\); 0.5 dB ≈ 12%, 3 dB ≈ ×2). 6.3 references it.
Relative powers are flagged compositional there — that is what makes
the five explicit-early cells one finding.

## Section 5 + 6 readability pass (21 Aug, commit `ebd0a2b`)

Walter: Sections 5/6 were cryptic — things "you and I understand" that a
reader cannot. He chose: fix GOLDEN subsections too (prose only, never
change a claim), EEG-only statistical analysis with the behavioural half
left an explicit stub, introduce Dataset A/B in 5.6 **and** formally in
5.8, keep Bronze/Silver/Gold but explain it, and write for an
HCI / consumer-neuroscience audience (explain Holm, \(d_z\), dB inline).

**5.8 Statistical Analysis is now written.** It was still the raw
template ("Describe the statistical model used, such as:"). It now has:
unit of analysis = participant and why the epoch is not; how \(D_i\) is
formed per path (Dataset B is a difference of differences); the 3 Dataset A
and 4 Dataset B planned comparisons; confirmatory (2) vs exploratory (14);
paired \(t\) + Wilcoxon and why **not** RM-ANOVA or cluster permutation;
Cohen's \(d_z\) defined; Holm within a measure and the compositional
reason for not correcting across the sixteen; the writing−reading
positive control; three sensitivity branches (no-ICA, width grid,
threshold); software (MNE-Python 1.12, SciPy 1.17, NumPy 2.2, Py 3.13).

**New fact surfaced from code, now in the paper:** `format_x_timing` in
`build_condition_contrasts.py` is `contrast_tier="secondary"` and
`correction_family="secondary_uncorrected"`. The presentation×timing
interaction is therefore secondary and uncorrected, and 5.8 says so.
It is **not** one of the three Dataset A confirmatory contrasts (those are
`any_ad_vs_no_ads`, `inline_vs_block`, `early_vs_late`; note inline =
implicit, block = explicit in the code).

Also verified from code for 5.8: CI is a two-sided 95% \(t\) interval
(`stats.t.ppf(0.975, n-1)`), the test is `ttest_1samp` on the person
differences against 0, `d_z = mean/SD` with `ddof=1`, Wilcoxon is
two-sided. Turn pairs for the positive control: reading = first complete
4 s after `assistant_reply`, writing = last complete 4 s before the next
`user_message`, within condition bounds, non-overlapping, 268 pairs,
13–15 per person.

**Rendering bugs fixed** (all were printing in the PDF): an unclosed
`\color{red}` at old line 1262 rendered *all of 5.4 Dependent
Variables* in red; `\ref{architecture}`, `\ref{pipeline}`,
`\ref{fig:eeg}`, `\ref{fig:flow-crowd}` and the two ad-example refs had
no "Figure~" so they printed as bare numbers; the montage caption
printed "(placeholder) ... Replace this file with the signed-off
drawing" (moved to a LaTeX comment — the figure **is** still a
placeholder); typos `recieved`, `alongisde`, `An crucial`, `5-tasks`;
and a garbled clause in 5.3.2 ("we believe sincerely in the research
questions can have the most impact").

**Vocabulary:** the sixteen spectral "coordinates" are now "measures"
throughout (paper-wide, including 7.3 and the appendix). Added a
four-symbol notation recap (\(a\), \(\lambda\), \(\pi\), \(a^{\emptyset}\),
\(\phi\)) to the Method intro so readers need not flip back to Section 4.
Added `\label{sec:behavioral-measures}` and a `gramfort2013mne` bib entry.

Pre-existing broken citations, **not** introduced here and still open:
`cite-of-arxiv-thesis` (template leftover) and `subramanian2026riding`.

## Section 5 + 6 second pass, 21 Aug (`2a88611`…`d9d476c`)

Walter: "5.8 is HUGE". It has to hold the behavioural, trajectory, and
behaviour×EEG analyses later, so it must be **concise and scalable**,
and may use maths to shorten prose.

**5.8 is now 603 words and extensible.** Structure to preserve:
three shared conventions → `tab:analysis-families` → within-participant
spectral contrasts (with \(D^{A}_{i}\), \(D^{B}_{i}\) as an `aligned`
equation pair) → tiers and Holm scope → positive control and
sensitivity → software. **To add an analysis later, add a table row and
a sentence — do not add another paragraph block per topic.** Families
not estimated are flagged \(^{\dagger}\) in the table.

### Third pass on 5.8, 21 Aug

Walter again: "too long and redundant, too many details, the first
paragraphs are fine but the last are horrible." The tail went 515 → 350
words. What was cut and why:

- **"Families not yet estimated" paragraph deleted entirely.** Every
  claim in it was already a column of `tab:analysis-families`: mixed
  effects with a participant random effect, pending genre estimator,
  association and laboratory-arm-only for behaviour×EEG. The table *is*
  the scalable mechanism — do not re-prose it.
- **Relative-power denominator argument** and **RM-ANOVA / cluster
  permutation rejection** moved to App. EEG Measures (the latter as a
  new `Estimators not used.` paragraph). The tier discussion there
  already covered the same ground, so 5.8 now points at it.
- **Positive-control window definitions** stay out of 5.8: 6.3 defines
  reading and writing windows precisely, so the Method only needs the
  contrast and its directional prediction.

Fixed an inconsistency while cutting: 5.8 said "the other fourteen are
exploratory" but App. Tiers says four are *secondary* and ten
exploratory. 5.8 now reads "secondary or exploratory".

**Second cut, same day** (Walter repeated the complaint): tail 350 →
293 words, section 660 → 603. The remaining engineering numbers left
5.8 as well — epoch widths 2/8/16/32~s and bounds 1,000/1,500~µV around
1,050~µV now live only in `sec:app-eeg-device`, and 5.8 names the three
branches abstractly as artefact removal, epoch width, and rejection
bound. This also removed a circular pointer: the appendix used to say
"Section 5.8 lists the sensitivity branches" while 5.8 listed the
numbers, so neither section was self-contained. The appendix now lists
them and 5.8 points to the appendix, one direction only.

### Results intro, same complaint

Walter: "the first results paragraph also started good but the end is
trash... again stating too much stuff we don't need to state as
subliminal." Cut the closing sentence "Two interpretive conventions
hold throughout: we do not treat implicit presentation as subliminal,
and we do not treat a participant noticing a brand mention as evidence
that they detected an advertisement." Intro 155 → 108 words.

Both conventions were already stated where they are *defined*:
implicit-is-not-subliminal in 5.3.2 (`main.tex` line ~821), and
brand-mention-is-not-detection in 5.4.1 with the notice composite. The
Results copy was the fourth occurrence of the first and the second of
the second. **Do not restate interpretive conventions at the head of
Results.** Define them once in the Method; the Discussion may draw on
them, but Results reports numbers. `subliminal` should stay at three
occurrences: Method (definition), Discussion limits, Conclusion (design
implication).

### Ultra-critical audit of 5/6/7, 21 Aug

Walter asked for a hostile read of Sections 5, 6, 7 and for Section 9
to be gutted. Fixed in this pass:

- **Section 9 (Conclusion) reduced to a commented outline.** Its one
  paragraph duplicated the design implication already in 7.4
  (Implications), so nothing unique was lost. Banner now `TO-START`.
- **`Goal~1` leaked into 7.1** ("the missing Goal 1 composites"). The
  vocabulary sweep missed it. Now "the behavioural composites".
- **7.1 was project-status prose, not discussion**: "the study has not
  answered its first question", "trajectory algebra", "are not in"
  three times, "on the page". Rewritten as scope.
- **"chrome"** in 7.2 read as the browser to anyone outside HCI. Now
  "a visually separate unit carrying a disclosure header".
- **"covert in Heineking's sense"** had no `\cite`; added.
- **`confirmatory features`** in the heatmap caption — last survivor of
  the feature→measure sweep.
- **"it awaits"** for a plural subject in 6.3; now "they await".
- **Comma splice** in Limitations: "Cued memory is a self-report after
  the instance is shown again, it could be improved." The trailing
  "could be improved" was a note to self, not a limitation.
- **Informal comments in the TeX source** (two leftover draft notes)
  removed. Commented source ships with an arXiv source
  upload. The two commented-out draft paragraphs beside them were
  already covered by the live text, so they went too.

**Still open, needs Walter's call:**

1. ~~6.2~~ **DONE (cut to one sentence, 21 Aug).** Was: It makes six
   directional claims with zero numbers ("stay low", "sit at the top of
   the scale", "appears weak beside format", "only modestly
   associated"), and it says results "will be recomputed on the final
   data extract" while 6.1 says the sample is *finished* at N=54. Those
   two statements contradict each other. Either give the descriptives
   numbers and a table, or cut the paragraph to one sentence saying the
   battery is not yet estimated.
2. **Future Work uses `\\` after paragraphs** (three times), which
   produces bad vertical spacing; and "paired up with", "we completely
   acknowledge" are informal for a GOLDEN section.
3. Section 4 (RQs/hypotheses) is still `IN-PROGRESS (LOW)` — Walter
   already said 4 needs revision at the end.
4. Personal TODOs sit after `\end{document}` (revise Sebastian's
   citation, ping for review). Harmless, not rendered, left alone.

Rule of thumb for this section: 5.8 states **methods and goals only**.
Thresholds, component rules, and QC provenance belong in
`sec:app-eeg-device`; measure definitions and tiers in
`sec:app-eeg-measures`; window mechanics in the Results subsection that
uses them.

\(D^{A}_{i}=\sum_{c}w_{c}\operatorname{med}_{\ell\in c}y_{i\ell}\) with
\(\sum_c w_c=0\) is exactly what the code computes (weighted condition
means), so the maths is not decoration.

### Word counts after the pass (use to judge "too long")

| Subsection | words |
|---|---|
| 5.6 EEG Preprocessing | ~1,490 (the real outlier) |
| 5.8 Statistical Analysis | 660 (was 820) |
| 6.3 Neurophysiological | ~880 |
| 5.7 EEG Epoching | ~515 |
| App. EEG Measures | ~1,110 |

5.6 stays largest because it carries the whole measurement chain plus
five equations. Implementation detail was already moved out to
`sec:app-eeg-device`; **further cuts would remove facts, so ask Walter
first.**

### Vocabulary now standardised (do not regress)

- sixteen spectral **measures**, never "coordinates", never "features".
- a **contrast**, never a "cell". A **grid**, never a "board".
- **pre-specified** or **fixed**, not "frozen", in the manuscript.
  "Frozen" stays fine in these notes.
- Holm applied **within each measure**, never "within feature".
- Internal terms removed from the PDF: "Goal 1 extract", "frozen
  against executable code", "already on the table", "levers",
  "advertisement chrome", "the next act".

### Also done

- Rewrote 5.1, 5.2.1, 5.2.2, 5.3.2, 5.4.1, 5.5, 5.6, 5.7, 6.1, 6.2,
  6.4, 6.5 prose. Removed `\\` used as paragraph breaks.
- `\label{EEG_adquisition}` → `\label{sec:eeg-acquisition}`.
- Both broken citations resolved. `subramanian2026riding` is
  **Subramanian, Bettadapura, Sathish, "Riding Brainwaves in LLM
  Space", arXiv:2603.21847 (2026)** — verified against the abstract,
  the \(\rho=0.183\) vs \(0.020\) high-gamma figures in §2 are correct.
  `cite-of-arxiv-thesis` was a placeholder for Walter's own
  dissertation; the sentence no longer carries a dangling key and has a
  TODO for when it gets an identifier.
- Fixed "Age ommited" caption and five plain grammar errors in the §3
  intent passage (`an true`, `recieved`, `its untractable`, and two
  broken clauses). §3 was otherwise left alone — Walter says 1–3 are
  good and §4 needs revision at the end.

## Still TO-START / not this push

- 5.8 behavioural half is a deliberate stub: it names a likely
  mixed-effects specification and states that nothing is estimated.
  Do not turn that into a results claim before Goal 1 lands.
- 6.2 Goal 1 behavioural models still skeleton. Do not invent tables.
- Extra Analysis appendix empty.
- ~~Appendix `Device` stub~~ — done. It is now
  `sec:app-eeg-device`, "Acquisition and signal quality": recording
  descriptives, the condition-blind quality profile, the per-channel
  evidence for the three interpolations, the exact ICA thresholds, and
  the status of the two engineering thresholds.
- **Trajectory analysis: dataset and first-pass inference now exist**
  (21 Aug). 5.8's table row and sentence can be filled from
  `.agents/context/data-analysis/trajectories/2026-08-21-trajectory-dataset-and-first-descriptives.md`;
  fill those rather than restructuring. What the Method needs to state:
  participant as the unit at \(N=54\) (both arms, unlike EEG), the genre
  space is the 13 ThradBERT classes, exact paired tests for shift
  outcomes because shifts are rare, Jensen-Shannon divergence as the
  continuous companion, Holm within family, and task as a covariate.
  Two things the Theory section will need to absorb: Definition 1 says
  \(f_\theta(u_k)\) but the deployed classifier was given the task prompt
  and recent history as well, and Definition 6's \(\tilde\delta\) is
  empirically empty. Results are a bounded null with a passing positive
  control, so this family is reportable rather than a placeholder.
- §4 Research Questions and Hypotheses needs a revision pass "at the
  end" (Walter's call, not started).
- Methods figure is still `eeg_preprocessing.png` and the montage is
  still a placeholder file; both carry TODO comments in `main.tex`.
- Method never states *why* Fz theta and posterior alpha were chosen
  (functional rationale). That currently lives only in 7.3 and
  `sec:app-eeg-measures`. A sentence belongs in the Method too.
- Do not overwrite ICA models or golden Gold.
- Parent thesis repo is not part of this Overleaf push.

## Method 5.6 / 5.7 audit (21 Aug, commit `bfa6723`)

Audited **5.6 EEG Preprocessing** and **5.7 EEG Epoching** line by line
against `cleaning_policy_ica_candidate_v1.json` and
`gold/features/build_condition_features.py`.

**Every number in 5.6 is correct** — 1,050 µV ptp, near-flat std
< 0.5 µV, ≥5 epochs / ≥80%, ICA 99% PCA / \(|r|\ge0.35\) / dominance
≥1.5 / ≤3 components, interpolations P4·s1, P4·s9, C4·s10, notch 50,
0.5–40 Hz, average ref excluding bads, spline, twelve 30 s QC windows,
Welch 2 s × 50% = 3 periodograms at \(\Delta f=0.5\) Hz, 216 Dataset B
epochs / 108 pairs / \(K_i=12\). The stale “ICA not applied” prose is
gone; ICA is stated as primary.

**Watch the retention number.** 6.3-adjacent text must say **9,449 /
9,468 (99.8%)** — that is the *ICA* branch. **9,438 (99.68%)** is the
*no-ICA* branch and appears in several pre-19-Aug notes
(`2026-08-03-*`, `2026-08-19-gold-paths-shapes-and-ica.md`,
`2026-08-20-eeg-pipeline-figure-v2.md`). Those notes are stale on this
point. The paper has the right one. Do not "correct" it to 9,438.

Four gaps were fixed in `bfa6723`:

1. Typo `mandatoryok` → `mandatory` (same family as `prookey
   coocoooduction`).
2. ICA was under-specified: now names FastICA, the 1–40 Hz decimated
   **fit** copy, and that the unmixing is applied to the 0.5–40 Hz
   data. Also flags the thresholds as engineering choices, per
   `2026-08-04-human-feedback-reference-ica-and-feature-candidates.md`.
3. **1,050 µV provenance disclosed.** It was set after seeing Subject
   14's 1,042.56 µV epoch;
   `2026-08-03-eeg-analysis-ready-datasets-and-open-decisions.md` says
   in bold it "must never be described as preregistered or
   literature-derived". 5.6 now says so and cites the 1,000/1,500 µV
   reruns. **Never let this sentence be edited back out.**
4. Dataset B onset provenance: 5.6 now says **30 of 36 implicit onsets
   are derived**, not merely "a reconstruction".

5.7 also gained a pre-specification clause. This matters because 5.7
argues 2 s is "too stimulus-locked" and 8 s "too aggregated", while 6.3
reports the only two Dataset B Holm cells at exactly 2 s and 8 s. Without
the clause a reviewer reads the Method as retrofitted. The claim is
true: 4 s epochs are already in the 3 Aug datasets note, the grid ran
19 Aug. The stale appendix cross-ref ("names are listed") now says the
measures are defined there.

### Left open in 5.6 / 5.7 (judgement calls, not done)

- Methods figure is `Figures/eeg_preprocessing.png`, not
  `eeg_pipeline_v2.png`. Different files, both 20 Aug. Decide which is
  canonical before submission. Caption is bare ("Laboratory EEG
  preprocessing") and does not name the four zones.
- Online reference Cz / ground Fpz are asserted as fact; the policy
  marks them `reported_by_lab_2026-08-04` with a note to verify the
  actiCHamp export handling.
- \(E\in\mathbb{R}^{18\times K_i\times 32\times 2000}\) is ragged
  notation. Disclosed in the text; left as is.

## Related

- Numbers: `../data-analysis/eeg/2026-08-20-paper-4s-primary-and-epoch-sensitivity.md`
- Depth: `../data-analysis/eeg/2026-08-20-paper-depth-audit.md`
- Figure cut: `../data-analysis/eeg/2026-08-20-paper-figures-and-narrative.md`
- Earlier local draft note: `2026-08-20-eeg-results-section-drafted.md`
