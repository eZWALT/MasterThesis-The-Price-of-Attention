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
  what is frozen, and what remains before feature extraction.

## Governing distinction

Recording and marker eligibility is not the same as final signal eligibility.
Subject 4 is the only known protocol exclusion. The remaining 18 recordings
have usable acquisition and event timing, but final participant retention must
still be determined from cleaned epoch quality using prespecified rules.
