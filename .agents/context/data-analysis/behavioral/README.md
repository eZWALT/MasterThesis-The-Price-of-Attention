# Behavioural analysis context

## Live now (8 September)

- **Item correlations held.** Katerina flagged `llm_reliable`,
  `llm_opinionated`, `llm_skeptical` as low-correlation and asked
  for a rerun without them. **Do not rerun. Do not drop items.**
  `2026-09-08-item-correlations-held.md`.
- Canonical Gold and confirmatory α stay on Walter's tree
  (`analysis/walter/behavioural/`). Her `Cronbach_alpha.py` was
  one-reverse-fixed this evening (parse no longer `8-x`); do not
  edit `analysis/behavioural/` again unless asked.

**7 September (night):** combos, reduced (blocks 0–7 in
`analysis/walter/combos/`, viewer `07_combos_reduced.ipynb`). 336
tests, 0 Holm / BH, Freedman–Lane family \(p > .23\). Block 0 is the
finding: Fz \(\theta\) \(D_i\) split-half reliability at \(k=37\) not
detectable (upper bound ≈ .6; .35–.61 whole-window), trajectory
\(D_i\) inter-classifier agreement < .33, \(n=18\) resolves only
\(|\rho| > .47\); the post-hoc Fz \(\theta\) pair is mostly a mean
shift. GEE cells in `outputs/events/` are not hits.
`2026-09-07-combos-reduced-blocks.md`.

**7 September (evening):** shared Gold catalog and lineage
(`../2026-09-07-gold-catalog-and-lineage.md`). Three grains
(message / chat / person). Paper names on the figure; files stay.
Thesis Ch 4.2 is the prose home; 4.2.2 is still a stub.

**7 September (afternoon, later):** Goal 1 freeze run on Walter's
Gold: 6 of 12 survey cells + 2 of 4 recall cells Holm-significant;
trust is the null. Exploratory sweep (1,755 tests) and Goal 5 combos
(2,560 tests, zero corrected hits) are in.
**Free text is discarded for good.**
`2026-09-07-goal1-freeze-sweep-and-combos.md`.

**7 September (afternoon):** canonical Gold is Walter's
`analysis/walter/behavioural/outputs/gold/`.
`2026-09-07-walter-behavioural-gold.md`.
Morning join contract:
`2026-09-07-behavioural-gold-and-combos.md`.
Do not write new Gold into Katerina's folder.


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

**5 September (superseded 7 Sep):** freeze-before-combos is done.
Do not permute items to hunt \(p\).
`../writing/2026-09-05-sprint-to-deadline.md`.

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

Crowd age for thesis Results 7.1 is a **prose-only** Prolific-export
estimate (26 of 36 with numeric age; not in Gold):
`2026-08-27-crowd-age-prolific-estimate.md`.

Instrument order / why-this-order (for Methods Flow Design):
`../../writing/2026-08-25-experiment-flow-design.md`.
