# Agent resources

> **CRITICAL (EEG / ICA).** Do not overwrite
> `src/project/logs/xdf/silver/ica/candidate_v1/`.
> Read `.agents/context/data-analysis/eeg/CRITICAL-do-not-overwrite-ica-models.md`
> before any ICA fit, `--overwrite`, or Gold rebuild.

Project-specific material for AI agents and collaborators:

- `context/` contains dated handover documents, settled decisions, and operational
  knowledge that should survive across sessions.
- `context/writing/` covers thesis and publication prose, Overleaf workflow, and
  theoretical framing decisions. Prefer the newest dated entry there for writing
  work.
- `context/data-analysis/` covers behavioural and EEG analysis decisions.
- `skills/` is reserved for reusable project-specific agent procedures.

**Manuscript source of truth:** only the Overleaf Git repositories under
`docs/overleaf/`. Writing context documents do not override LaTeX.

Read the newest relevant document under `context/` before changing study analysis,
experiment data, or Overleaf sources.
