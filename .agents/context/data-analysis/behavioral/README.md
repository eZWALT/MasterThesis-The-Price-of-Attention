# Behavioural analysis context

Use this directory for behavioural-arm documents that expand the shared analysis
plan, including:

- canonical JSONL ETL and derived-table contracts;
- questionnaire scoring keys and reliability decisions;
- behavioural exclusions and sensitivity populations;
- primary and secondary model specifications;
- recall, open-text, latency, effort, and semantic-shift audits.

Cross-arm ownership, shared identifiers, planned contrasts, and multimodal
integration decisions remain in the parent `data-analysis/` directory.

Analysis order (whole study): behavioural battery → personality /
demographics → EEG → genre trajectories → all combos. The
insertion-policy model is dropped (24 August).
See `../2026-08-18-analysis-priority-order.md`.

**27 August:** Katerina is missing. Walter owns Goal 1 (battery EDA)
and free-text this window. Combos opened as a joined person ×
condition dataset once scoring exists.
`../2026-08-27-backlog-and-timeline.md`.

Free-text plan (codebook from *Ads that Talk Back*, LLM-as-judge
assignment, prevalence / co-occurrence / length / quotes / word cloud):
`2026-08-27-free-text-codebook-and-llm-judge.md`. Two corpora, 270
findings (has \(a^{\emptyset}\)) and 216 cued-recall reactions (no
control). Person is the unit, so prevalence is paired or Cochran's Q,
not a plain chi-square over texts. Open decision recorded there:
`tab:analysis-families` currently declares free text **descriptive**,
which conflicts with testing prevalence.

Newest roster / log-scheme audit:

- `2026-08-18-behavioural-roster-and-log-schemes.md` — finished *N*,
  early `export.jsonl` + numeric conditions, production-only 42–44.

Instrument order / why-this-order (for Methods Flow Design):
`../../writing/2026-08-25-experiment-flow-design.md`.
