# Five-LLM jury (two iterations)

Prompt (PDF only): `../2026-09-11-thesis-review-metaprompt.md`.
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

Empty until v2 is compiled.

## Reconcile (later, not now)

When Walter says rank the v1 dumps: paste
`ensemble-jury-reconciliation.md` (everything after the `---`)
with the five web dumps plus the five extra in-IDE dumps
(MU, KK, OP, FB, GS). Shared-brief correction is in that prompt;
do not majority-vote. Do not apply from the ranking until
he says start v2.

## Apply

Iteration 1 is full. Use Gemini
`jury-v1-gemini-3-pro-full.md` (156-pp PDF). Keep
`jury-v1-gemini-3-pro.md` only as the truncated first pass.
Muse 1.3, Kimi K3 Max, Opus 5, Fable 5.1, and GPT 5.6 Sol
are extra in-IDE dumps, not replacements for the five web
juries.
Do not apply until Walter says start.
