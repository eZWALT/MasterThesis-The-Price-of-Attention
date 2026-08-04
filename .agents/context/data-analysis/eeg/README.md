# EEG analysis context

This directory contains durable EEG-arm decisions and summaries. Executable
pipelines, generated manifests, and participant-level outputs remain under
`analysis/eeg/` and `src/project/logs/xdf/`.

## Current entries

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
  required 99%-variance ICA branch, engagement decision, and candidate
  amplitude, entropy, PSD, asymmetry, and PLV features.
- `2026-08-04-eeg-preprocessing-how-it-works.md`
  is the durable Markdown companion to the interactive pipeline canvas. It
  records the exact executable trace, input/output array shapes, condition-blind
  signal QC, deterministic cleaning transformations, validation evidence,
  lazy-cleaning architecture, policy-version distinctions, and remaining human
  gates.

## Governing distinction

Recording and marker eligibility is not the same as final signal eligibility.
Subject 4 is the only known protocol exclusion. The remaining 18 recordings
have usable acquisition, event timing, and condition-level signal. Individual
four-second epochs or pre/post pairs may still be rejected by the frozen
artifact policy without excluding the participant globally.
