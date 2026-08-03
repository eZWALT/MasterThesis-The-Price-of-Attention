# Context — behavioural and EEG analysis workstreams

Written 3 August 2026 after reviewing the study repository, the Tang et al.
analysis release, the production log schema, the EEG/LSL marker implementation,
and Angela's `scripts/cognitive-mllm` repository.

This document records team ownership and execution order. It complements
`.agents/context/data-analysis/2026-07-28-data-analysis-foundation.md` and
`docs/generated/eeg-analysis-plan.md`; it does not replace their statistical
detail.

## Team ownership

- **Person A — colleague:** behavioural and shared-data lead.
- **Person B — Walter:** EEG and reproducibility lead.
- Walter and the analysis agent will later help Person A with the larger
  behavioural stream after the EEG foundation is stable.

The approximate initial split is 60% behavioural/shared data work and 40% EEG.
Ownership is end to end: avoid dividing work by isolated figures or individual
questionnaire variables.

## Shared analysis contract

Both streams must use the same stable identifiers and frozen derivative tables.

Behavioural/shared artifacts:

1. participant table;
2. condition table;
3. turn table;
4. recall table;
5. normalized event table;
6. exclusions ledger.

EEG artifacts:

1. recording map (`lab_subject` to `experiment_id` to XDF);
2. marker manifest;
3. EEG epoch manifest;
4. long-form EEG feature table;
5. preprocessing and signal-quality report.

Every derived row must retain its source file, derivation version, quality flags,
and stable participant/experiment/condition/turn keys. Hand-edited CSVs are not
analysis inputs.

## Person A work units — behavioural and shared data

### A1. Production JSONL ETL

- Load all three historical JSONL naming schemes and prefer validated exports.
- Normalize legacy event names and logging eras.
- Reconstruct transcripts from `user_message` and `assistant_reply`.
- Derive the five canonical conditions from the logged assignment plan:
  `no_ads`, `inline_early`, `inline_late`, `block_early`, and `block_late`.
- Build and validate the six shared behavioural artifacts.

### A2. Scoring, reliability, and exclusions

- Freeze item directions before inspecting condition means.
- Keep item-level ratings alongside every composite.
- Treat perceived manipulation and credibility as the initial primary outcome
  families; report direct `personality_trust` separately.
- Score BFI-10 traits continuously. Do not create personality clusters at the
  present sample size.
- Produce a complete exclusions ledger and sensitivity populations.

### A3. Primary behavioural inference

- Fit repeated-measures mixed models using the planned contrasts:
  any advertising versus no advertising, inline versus labelled block, and
  early versus late. Treat format-by-timing as secondary.
- Include task, condition position, and study arm.
- Report raw 1–7 scale effects, intervals, within-person effect sizes, and
  multiplicity-adjusted confirmatory tests.

### A4. Secondary behavioural analyses

- Model response latency and effort at turn level.
- Analyse cued memory and recall text without calling them objective recognition.
- Define an embedding-derived measure as **semantic trajectory shift**, not
  attention.
- Because turn-4 advertisements have no subsequent user message, estimate
  post-ad semantic/behavioural shift only for early advertisements against a
  matched no-ad turn-2 pseudo-event.
- Use blinded qualitative coding and a double-coded subset before any
  LLM-assisted coding.

## Person B work units — Walter's EEG stream

### B1. XDF inventory and recording map

- Mount the full external recordings.
- Explicitly map each `lab_subject` to its `experiment_id` and XDF file.
- Audit streams, duration, overlap, channel labels, units, sampling rate,
  reference, and marker coverage.
- Never infer participant identity from XDF filename numbering alone.

### B2. XDF/MNE adapter

Angela's `scripts/cognitive-mllm` is useful but is not directly compatible:

- it reads BrainVision `.vhdr` files rather than XDF;
- it segments numeric annotation pairs (`5` to `6`);
- this study uses named JSONL/LSL events and has marker drift.

Reuse its MNE organization, segment-manifest pattern, spectral-feature functions,
participant-grouped validation ideas, and diagnostic outputs. Add a study-specific
`pyxdf` to MNE adapter and named-event layer.

Do not inherit methodological defaults blindly. In particular:

- verify whether 50 Hz notch filtering is needed rather than applying both 50
  and 60 Hz;
- freeze and enable a documented artifact/ICA policy;
- use an explicitly declared log-power FAA convention rather than the inherited
  raw `F3 - F4` alpha-power difference;
- do not reuse its uncorrected collection of paired tests as the inferential
  analysis.

### B3. Marker reconstruction

Classify recordings into three tiers:

1. **Healthy marker stream:** use for direct analysis and validation.
2. **Partial marker stream:** match common XDF and JSONL markers by name and
   ordinal, robustly fit a participant-specific affine clock mapping, and
   project missing logged events with recorded uncertainty.
3. **No synchronization anchor:** do not transfer a clock offset from another
   participant. Healthy recordings provide the expected event sequence and
   delay distributions, not the missing participant's clock mapping. Use
   recording metadata/start anchors only if independently validated; otherwise
   event-locked analysis is unavailable for that recording.

The marker manifest must record whether every event is observed or derived, the
reconstruction method, anchors, residual error, confidence tier, and exclusion
reason.

Important semantics:

- `ad_displayed` is validation-only: it is missing for inline ads and duplicated
  for blocks.
- `ad_injected` is generation onset, not visual exposure.
- block visibility can be estimated from reply completion plus a validated UI
  delay.
- inline visibility requires a streaming/text-position estimator whose error is
  measured on available validation sessions.
- deployed `turn_N_read` and `turn_N_write` markers do not identify clean reading
  and writing states.

### B4. EEG preprocessing and features

- Freeze preprocessing blind to condition: filters, bad channels, rereferencing,
  interpolation, ICA/artifact criteria, and participant/epoch exclusions.
- Verify the actual montage before selecting regions.
- Primary spectral features: frontal-midline theta and posterior alpha log power.
- Beta is secondary. FAA and engagement ratios are exploratory.
- The safest primary EEG outcome is sustained condition-level spectral activity.
- Exposure-locked pre/post analysis proceeds only if reconstructed visual-onset
  error passes a frozen tolerance.
- Classical ERP analysis, single-trial decoding, and claims that EEG directly
  measures trust or persuasion remain out of scope.

### B5. EEG inference and multimodal integration

- Fit small participant-level mixed models mirroring the behavioural contrasts,
  adjusted for task and order.
- Limit confirmatory EEG inference to two or three prespecified feature families.
- Separate within-person EEG changes from between-person average differences.
- Test EEG's incremental value only by comparing behaviour-only and
  behaviour-plus-EEG models on the identical lab subset with participant-grouped
  validation.

## Coordination and execution order

Person A and Person B start in parallel:

1. jointly freeze the dataset manifest, schemas, scoring key, contrasts, and
   exclusions;
2. Person A builds behavioural ETL while Person B builds the XDF inventory and
   adapter;
3. Person A fits primary behavioural models while Person B reconstructs markers;
4. Person A runs secondary behavioural analyses while Person B preprocesses EEG
   and extracts spectral features;
5. Person B fits EEG contrasts;
6. both streams meet in the lab-only multimodal ablation;
7. Walter and the agent then help Person A package and extend the larger
   behavioural analysis.

At each work-unit boundary, cross-review one participant end to end from raw
files to model input. Merge complete reproducible vertical slices with tests and
manifests.

## Stop/go gates

- No behavioural inference before scoring, exclusions, task balance, and
  condition coding are frozen.
- No event-locked EEG without a validated participant-specific time mapping.
- No exposure-locked EEG claims before reconstructed onset error is quantified.
- No predictive result without participant-grouped leakage checks.
- No claim that EEG measures trust, persuasion, or positive/negative attention
  directly.

## Related durable documents

- `.agents/context/data-analysis/2026-07-28-data-analysis-foundation.md`
- `.agents/context/data-analysis/eeg/2026-08-03-independent-xdf-recording-audit.md`
- `docs/generated/eeg-analysis-plan.md`
- `docs/generated/model-feasibility.md`
- `docs/generated/related-code-chatbot-ads.md`
- `.agents/context/2026-07-30-analysis-planning-and-data-state.md`
- `.agents/context/2026-07-31-overleaf-literature-merge-and-writing-preferences.md`

The interactive `docs/data-analysis-foundation.canvas.tsx` is an earlier view of
the overall analysis design. Where it conflicts with the newer Markdown marker
audits, the newer Markdown is authoritative.
