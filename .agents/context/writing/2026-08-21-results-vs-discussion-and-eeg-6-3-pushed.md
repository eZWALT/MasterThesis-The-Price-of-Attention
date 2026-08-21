# Results ≠ Discussion, and EEG 6.3 is on Overleaf

Date: 21 August 2026

Walter asked to push so he can review on Overleaf, and to lock the
Results / Discussion split in agent context immediately.

## Standing rule

- **Results** report the estimand, the sample, the numbers, the figure,
  the tables. No design implication. No “this means ads do not affect
  EEG.” No abstract-placement advice.
- **Discussion** interprets: precise Path A null vs dead pipeline,
  Path B underpowered / not absence, do not harvest leans, mention both
  off-width cells or neither, write−read is a task-state check not an
  ad result, C1 waits on Goal 1, H1–H3 are not a liking claim.
- **Limitations** hold the EEG constraints (n=18, one Path B trial,
  reconstructed implicit onset, no EOG, no ERP).
- Do not invert study order: Goal 1 behaviour first, then 2, then EEG.

Cursor rule: `.cursor/rules/results-vs-discussion.mdc`.

## What was pushed (publication Overleaf)

Repo: `docs/overleaf/publication/` (its own git remote).

- §6.3 `sec:results-eeg`: confirmatory 4 s ICA, n=18, person as n.
  Path A Holm-null; six CIs inside ±0.3 dB. Path B Holm-null; wide CIs.
  Write−read Fz theta one paragraph of numbers. Both 2 s and 8 s
  sensitivity cells. 16-feature 4 s board (`fig:eeg-holm-board`): Path A
  0/48; six Path B exploratory ICA-only hits named, no extra table.
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
  - Path A tight null = no sustained reallocation of effort or visual
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
- §7.5: EEG XXXX filled (n, Path B trials, onset p95 0.43 s, no EOG,
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
| `fig:eeg-forests` | 6.3 | \(M\) ± 95% CI; the Path A vs Path B precision contrast |
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

## Still TO-START / not this push

- 5.8 Statistical Analysis still `XXXXX`.
- 6.2 Goal 1 behavioural models still skeleton. Do not invent tables.
- Extra Analysis appendix empty.
- Appendix `Device` subsection is a TO-START stub whose only sentence
  describes the *measures*, not a device. Leftover; delete or fill.
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
Welch 2 s × 50% = 3 periodograms at \(\Delta f=0.5\) Hz, 216 Path B
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
4. Path B onset provenance: 5.6 now says **30 of 36 implicit onsets
   are derived**, not merely "a reconstruction".

5.7 also gained a pre-specification clause. This matters because 5.7
argues 2 s is "too stimulus-locked" and 8 s "too aggregated", while 6.3
reports the only two Path B Holm cells at exactly 2 s and 8 s. Without
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
