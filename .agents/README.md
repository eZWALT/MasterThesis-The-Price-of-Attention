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
  EEG channel-set / literature-ROI averages:
  `context/data-analysis/eeg/2026-08-24-channel-set-policy.md`
  and `eeg/2026-08-24-literature-roi-from-angela.md`. Hardcoded lists;
  appendix `sec:app-eeg-channel-sets` only.
- `skills/` is reserved for reusable project-specific agent procedures.

**Manuscript source of truth:** only the Overleaf Git repositories under
`docs/overleaf/`. Writing context documents do not override LaTeX.

Read the newest relevant document under `context/` before changing study analysis,
experiment data, or Overleaf sources.

Live sprint (27 August): five pending analyses, thesis first, paper
optional, presentation starts now.
`.agents/context/data-analysis/2026-08-27-backlog-and-timeline.md`.
Newest analysis save (28 August): channel-set closed, primary stays.
`.agents/context/data-analysis/eeg/2026-08-28-channel-set-closed.md`.
Newest writing catch-up (Dataset A/B figures, 7.1 crowd age, Methods
comments): `.agents/context/writing/2026-08-27-afternoon-save.md`.
29 August defence-deck flow (rollback `d5d42ab`):
`.agents/context/writing/2026-08-29-presentation-flow-pass.md`.
31 August defence save (waves slide + EEG power / MDE numbers):
`.agents/context/writing/2026-08-31-presentation-eeg-waves-and-power.md`.
31 August slow-power / High-level discussion lock:
`.agents/context/writing/2026-08-31-slow-power-and-high-level-discussion.md`.
