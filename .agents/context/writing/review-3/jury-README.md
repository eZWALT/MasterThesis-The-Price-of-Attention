# Five-LLM jury (two iterations)

Prompt (PDF only, **black v2**): `../2026-09-15-thesis-review-metaprompt-v2.md`.
Manuscript: Overleaf thesis v1 (source-cleaned 14 Sep). Full local
PDF for in-IDE agents:
`docs/overleaf/thesis/_build/dissertation.pdf` (156 pp, 15 Sep
compile). Do not put review chat back in the `.tex`.

Plan Walter named 15 Sep: **1st LLM judge → apply (v2) → 2nd LLM
judge → apply (v3) → final thesis.** Five models each judge pass.
Abstract and Conclusion last in each apply, one agent, no wholesale
rewrite.

Raw dumps are not Gold. Fact-check every number against the PDF
before changing prose.

## Iteration 1 (on v1 → apply produces v2)

| Model | File | In |
|---|---|---|
| Deepseek | `jury-v1-deepseek.md` | 15 Sep |
| Grok 4.6 web (think low) | `jury-v1-grok-4.6.md` | 15 Sep |
| ChatGPT | `jury-v1-chatgpt.md` | 15 Sep |
| Claude Sonnet 5 | `jury-v1-claude-sonnet-5.md` | 15 Sep |
| Gemini 3 Pro (truncated PDF) | `jury-v1-gemini-3-pro.md` | 15 Sep; superseded |
| Gemini 3 Pro (full 156-pp PDF) | `jury-v1-gemini-3-pro-full.md` | 15 Sep |

Extra in-IDE dump (not one of the five web juries; do not
substitute it for them on apply unless Walter says so):

| Muse 1.3 in-IDE (full local PDF) | `jury-v1-muse-1.3.md` | 15 Sep |
| Kimi K3 Max (full local PDF) | `jury-v1-kimi-k3-max.md` | 15 Sep |
| Opus 5 (full local PDF) | `jury-v1-opus-5.md` | 15 Sep |
| Fable 5.1 (full local PDF) | `jury-v1-fable-5.1.md` | 15 Sep |
| GPT 5.6 Sol (full local PDF) | `jury-v1-gpt-5.6-sol.md` | 15 Sep |

## Iteration 2 (on v2 → apply produces v3)

Black v2 PDF (green off, `e68be52`), prompt `../2026-09-15-thesis-review-metaprompt-v2.md`.

| Model | File | In |
|---|---|---|
| Grok 4.6 web | `jury-v2-grok-4.6.md` | 15 Sep 16:34 |
| ChatGPT | `jury-v2-chatgpt.md` | 15 Sep 16:34 |
| Gemini Flash | `jury-v2-gemini-flash.md` | 15 Sep 16:34 |
| Deepseek | `jury-v2-deepseek.md` | 15 Sep 16:34 (δ/θ→β reader artefact, as in v1) |

Scores moved 5.5→6.5 (GX), 6.5→7.2 (CG), 6.8 (DS). Walter's call 15 Sep: store, then a **typo-only pass** first; substantive v2 items reconciled after.

**Reconciliation of the four v2 judges: `reconcile/v2-ranked-issues.md`.**
Three real fixes pushed as `e0bf6cc` (Dataset B 96-cell split in Results,
Table 7.8 EEG header, wait cancels in format/timing contrasts).
Typo pass pushed (`4f48b30`); log: `reconcile/v2-typo-pass-and-triage.md`.
Deepseek's M1–M3/m1–m2 are δ/θ→β reader artefacts (source verified). Grok's
"latency not in Limitations" is false (it is; ChatGPT quotes it).

## Reconcile (done 15 Sep midday)

Ranking lives in `reconcile/ranked-issues.md`; the mapping
tables are `reconcile/map-GM-MU-KK.md` and
`reconcile/map-DS-GX-CG-CS.md` over
`reconcile/issue-taxonomy-seed.md`. The truncated Gemini pass
was deleted; `jury-v1-gemini-3-pro-full.md` is the Gemini dump.
Critique of `ensemble-jury-reconciliation.md` is at the end of
`ranked-issues.md` (brief leakage, per-item weights, verify
before rank).

## Apply

Walter authorised green edits on 15 Sep, Abstract and Ch 9
included, sentence-level. Tier 1 of `ranked-issues.md` is in
the `.tex` under `\rev{}`. Tier 0 (science) and Tier 2 (cheap
wording) wait for his word. v2 = the source after he accepts or
rejects the green.

**15 Sep, midday.** Tier 2 wording applied in green and pushed (`f2132a7`). Two "false premises" in `ranked-issues.md` were themselves wrong and are corrected there: CG's Holm .047 re-exposure trust is real (never removed from the thesis); MU's \(\delta^{(a)}_k\)-in-Theory is real (Results notation sentence fixed). Left for a re-plot, not prose: Fig 7.12a and Fig 7.13b use opposite fill conventions (captions are each correct). Remaining open: Tier 3 parked items; Walter's read of the green.

**15 Sep, afternoon.** Tier 3 applied and pushed (`b7823dd`). Round-2 jury prompt: `../2026-09-15-thesis-review-metaprompt-v2.md` (no leaked checklist, quote-or-drop, fixed schema, Job 0 regression on green). Send with the v2 PDF compiled **with green on**. Store dumps as `jury-v2-<model>.md` here.
