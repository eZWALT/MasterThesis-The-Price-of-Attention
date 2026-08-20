# EEG analysis context

> **CRITICAL — read first:** `CRITICAL-do-not-overwrite-ica-models.md`
> Do not run `fit_ica_cohort.py --overwrite` or
> `run_ica_sensitivity.py --overwrite-models`. The signed-off models in
> `src/project/logs/xdf/silver/ica/candidate_v1/` must be reused.

This directory contains durable EEG-arm decisions and summaries. Executable
pipelines, generated manifests, and participant-level outputs remain under
`analysis/eeg/` and `src/project/logs/xdf/`.

## Current entries

- `../2026-08-20-implicit-explicit-names.md`
  paper names: implicit / explicit. Log keys stay `inline_*` / `block_*`.
- `CRITICAL-do-not-overwrite-ica-models.md`
  is the hard stop on refitting or replacing the 2026-08-19 ICA archive.
- `2026-08-20-pipeline-sanity-audit.md`
  Gold IDs, Path A/B arithmetic, and why the 4 s Holm-null is not a
  scrambled pipeline.
- `2026-08-20-eeg-pipeline-figure-v2.md`
  thesis preprocessing figure; do not edit the 6 Aug original.
- `2026-08-19-eeg-behavioural-merge-tables.md`
  person × condition / ad-response join only. No epoch merge.

- `2026-08-03-independent-xdf-recording-audit.md`
  records recording identity, marker anomalies, reconstruction, exclusions, and
  the evidence supporting the 18-participant laboratory EEG cohort.
- `2026-08-03-eeg-pipeline-state-and-stage-gates.md`
  records the current Ingestion, Bronze, Silver, and Gold implementation state,
  what is frozen, and the remaining publication gates.
- `2026-08-03-eeg-analysis-ready-datasets-and-open-decisions.md`
  records the completed condition/ad datasets, feature and statistical
  contracts, versioned Subject 14 threshold decision, literature-grounded
  preprocessing audit, prior motor-imagery-paper reuse boundaries, engagement
  definitions, proof chain, exact commands, and remaining human inputs.
- `2026-08-03-eeg-publication-analysis-workspace.md`
  records the analysis sibling folder, notebook, publication tables and
  figures, twenty executable quality gates, initial results, and multimodal
  integration boundary.
- `2026-08-04-human-feedback-reference-ica-and-feature-candidates.md`
  records the Cz online reference, Fpz ground, average offline reference,
  implemented 99%-variance ICA candidate branch and review boundary,
  engagement decision, and candidate amplitude, entropy, PSD, asymmetry, and
  PLV features.
- `2026-08-04-eeg-preprocessing-how-it-works.md`
  is the durable Markdown companion to the interactive pipeline canvas. It
  records the exact executable trace, input/output array shapes, condition-blind
  signal QC, deterministic cleaning transformations, validation evidence,
  lazy-cleaning architecture, policy-version distinctions, and remaining human
  gates.
- `2026-08-06-remaining-human-signoff-checklist.md`
  separates resolved acquisition and preprocessing inputs from the remaining
  positive-control and behavioral handoff decisions. Filtering, ICA
  exclusions, and the ICA-as-primary choice closed on 2026-08-19.
- `2026-08-19-gold-paths-shapes-and-ica.md`
  is the Gold-layer pedagogy note: what each of the two Gold paths writes
  after lazy cleaning, the evolving `(32, N) → epoch → summary` shape for
  one participant, and what ICA changes (values and provenance, not matrix
  axes or row geometry).
- `2026-08-19-ica-primary-and-visual-signoff.md`
  records the 2026-08-19 approvals (filter figures, all automatic ICA
  exclusions, ICA as primary) and the read-versus-write window contract.
  What that control proved is in
  `2026-08-19-read-vs-write-what-it-proved.md`.
- `2026-08-19-mean-vs-median-and-epoch-length.md`
  records that mean-of-epoch dB does not change the Holm-null Y_A
  result, so median stays primary, and that a 2/4/8/16/32 s grid is a
  robustness check rather than a search for a publishable p-value.
- `2026-08-19-epoch-length-grid.md`
  records the 2/8/16/32 s rebuild (4 s reused): Path A remains Holm-null
  at every width; three confirmatory Path B Holm cells appeared (2 s Fz
  theta ICA-only; 8 s posterior alpha under both ICA and no-ICA). Primary
  stays 4 s + median + ICA.
- `2026-08-20-pipeline-sanity-audit.md`
  records the 20 August check that Gold IDs, clocks, window geometry,
  ICA flags, and contrast arithmetic are consistent, so the 4 s null is
  treated as a small estimated effect rather than a broken pipeline.
- `2026-08-19-read-vs-write-what-it-proved.md`
  is the short interpretation note: B1 proved the 4 s ICA chain can
  recover a chat-state difference (Fz theta writing > reading, Holm
  0.007). It did not prove ads work. Not for the abstract as an ad
  finding.
- `2026-08-19-eeg-only-analyses-complete.md`
  is the EEG-only stop line: Path A/B nulls, epoch grid, ICA, read-versus-
  write positive control, session-order null, and the figure suite. Next
  EEG work is manuscript prose and C1 after Goal 1.
  Figure hub: `analysis/eeg/analysis/outputs/figures/eeg_only/`
  (Holm heatmaps Path A/B at 2 / 4 / 8 s).
- `2026-08-19-literature-justifications-in-overleaf.md`
  records the literature sanity-check on the median collapse and
  person-level Holm tests, the short cite set parked as Overleaf
  comments, and what must not be added as citation soup.
- `2026-08-19-eeg-analysis-menu-and-tickets.md`
  is the high-level EEG analysis menu: within-person \(D\),
  EEG–trust/UX correlations, between-person global scores, and
  APPROVED / PENDING / OUT tickets.
- `2026-08-19-eeg-behavioural-merge-tables.md`
  designs the three join tables (person × condition, person ×
  contrast, person × ad) and which Gold/stat columns are plug-in
  features. No builder yet.

- `2026-08-20-eeg-pipeline-figure-v2.md`
  records the publication preprocessing figure v2: title
  **Laboratory EEG Preprocessing Pipeline**; Silver follows
  `clean_recording()` (notch → 0.5–40 Hz → average ref → spline → ICA);
  Gold says **4 s epochs** (not tiles); shape rail is
  \(X\to\tilde{X}\to E\to Y_A,Y_B\) with
  \(X,\tilde{X}\in\mathbb{R}^{18\times 32\times T_i}\) and
  \(E\in\mathbb{R}^{18\times K_i\times 32\times 2000}\) (Path A
  \(K_i\) varies; Path B \(K_i=12\)) and no `y(16)`.

Publication figure: original
`src/project/docs/eeg_pipeline/eeg_pipeline.png` is frozen (6 Aug). v2 is
`eeg_pipeline_v2.png` / `.pdf` / `.svg`.

## Names

Paper language is **implicit** / **explicit**. Log keys stay
`inline_*` / `block_*`. See
`../2026-08-20-implicit-explicit-names.md`.

## Governing distinction

Recording and marker eligibility is not the same as final signal eligibility.
Subject 4 is the only known protocol exclusion. The remaining 18 recordings
have usable acquisition, event timing, and condition-level signal. Individual
four-second epochs or pre/post pairs may still be rejected by the frozen
artifact policy without excluding the participant globally.
