# v2 jury: typo pass done, substantive items triaged (15 Sep, 16:50)

## Typo-only pass — pushed to Overleaf as `4f48b30` (on top of Walter's `a6ef0c8`)

Method: `codespell` + pyspellchecker dictionary sweep (LaTeX stripped, BrE
suffixes allowed) over `chapters/*.tex` + `frontmatter/*.tex`, then a read of
the three Walter-authored chapters (Intro, Related Work, System Design).
No labels, refs, numbers, or `\rev{}` wrappers touched. 12 files, 70 lines.
Scratch compile: 162 pp, zero undefined references.

Fixed classes:
- Misspellings (~45): strenght, break fre, datasetm, succed, appropiately,
  aggreation, elegible, recieve/d/ing, wellfare, environmnets/enviromnents,
  hided→hid, whre, akward, simultaenously, standarized, Artifical,
  usefullness, aggresive, prioritzed, straightfoward, propietary, crutial,
  possibily, atleast (×2), peripherics, unnatentive, succeptible, ous→us,
  "told to got"→"go", lexic→lexical, ortiented, inidivdual, industrialzed,
  identificating, softwares, TFTT→TTFT, "Advertisement t in".
- `its`→`it is` (×9); `a`/`an` (a advertisement, a unstructured, a extensive,
  an URL, an 32 channel, an hybrid); doubled word (full-attention attention).
- `i.e`/`e.g` without stops → `e.g.\ ` / `i.e.\ ` (×6).
- Lowercase brands: qwen, ollama, qdrant, pinecone, youchat, chatgpt, llm.
- Acknowledgments: "everything i got" → "everything I've got".
- BrE harmonisation in prose only: catalog→catalogue, colors→colours,
  rigor→rigour, behavioral→behavioural, optimization→optimisation (Intro §1.2).
  `-ize` forms elsewhere left alone (title has "Monetization").
- Deepseek m3: "Qwen 3.6 35B A3B" → "35B-A3B".

Left alone on purpose: `covert` (correct), `retuned` (correct), `Studi`
(Italian), `confirmatorily`, mixed `-ize` outside the fixes above.

## v2 substantive items — triage for the next (last) round

### Deepseek reader artefacts — NOT thesis errors (verified in .tex)
- M1/D2 "↑β,β;↓α,β" in Conclusion: source is `\uparrow\delta,\theta;\downarrow\alpha,\beta`.
- M2/D4 `\hat g_k` collision: source Def. 2 uses `\delta_k`.
- M3/D3 "β^(a)" in Results 7.5 / Fig 7.10: source is `\delta^{(a)}`.
- m1/D6 Table 6.1 "y*min − y*med": source is `y^{write}−y^{read}`.
- m2 Fig 4.5 "Fz \hat θ_i": source is `Fz \(\theta\)`.
Same δ/θ→β artefact as DS v1. Record in `map-DS-GX-CG-CS.md` false-premise list.

### Grok false premise
- "Latency confound still unaddressed / not named in Limitations": it is —
  §5.1.2 non-functional latency bullet (median 3.03 s), Methods §6.2.5
  "The advertised turn waits longer" bullet, Discussion limitations.
  ChatGPT v2 quotes exactly this text. Grok likely read a stale PDF or missed it.

### Real, small (candidates for the final round; not typos)
- DS D5/M5: Discussion §8.3 "six nominal cells out of 96" — check whether the
  96-cell Dataset B pairwise count is in Results/App. D.3; if not, add one
  clause there or drop the number in Discussion.
- DS M4/D1: Abstract +1.27 manipulation — traceable to Table 7.2 (behavioural
  key estimates), not Table 7.8's single key row. Fine; optionally cite
  "Table 7.2" nowhere needed in an abstract. No change.
- DS V2: Table 7.8 caption — say the Dataset A row is the 2 confirmatory
  measures × 3 contrasts (6), exploratory 14 measures are their own row.
- CG "abstract vs body": Abstract says "candidate neural correlate of a trust
  drop"; Discussion says onset response is not evidence of captured
  attention. Not contradictory (correlate ≠ capture) — Walter's call; abstract
  is edited last.
- GM Flash: LaTeX-wrapped numbers in prose ("32 channels, 500 Hz") — cosmetic.
- GX/CG design confounds (retrieval wait, θ–λ confound, classifier 32.5 %,
  depth confound): all already stated in Limitations; nothing to write, only
  to own in the viva.

### Scores
GX 5.5→6.5 · CG 6.5→7.2 · DS 6.8 · GM Flash "near-submission shape".
