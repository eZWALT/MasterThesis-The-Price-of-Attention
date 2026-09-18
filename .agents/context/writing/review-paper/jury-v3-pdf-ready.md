# Paper PDF ready for jury v3

Stamp: 17 Sep 2026, ~16:00 CEST. Compile only; no `.tex` edits, no
commit, no push, no review.

## Build

| | |
| --- | --- |
| Status | **success** |
| Compiler | pdfLaTeX via `docker run --rm texlive/texlive:latest` + `latexmk -f -pdf -interaction=nonstopmode` (TeX Live 2026) |
| Source tree | `/tmp/paper_src` (copy of `docs/overleaf/publication/`: `main.tex`, `sections/`, `Figures/`, `bibliography.bib`, `nips_2018_wider_nonotice.sty`) |
| Aux | written only under `/tmp/paper_build/` — not copied into git |

## PDF

| | |
| --- | --- |
| Pages | **49** (`pdfinfo`) |
| Size | 2 481 310 bytes |
| Page size | 612 × 792 pts (letter) |
| Jury copy | `/home/wtroi/MasterThesis-RAG-RecSys/docs/overleaf/publication/_build/main.pdf` |
| Scratch copy | `/tmp/paper_build/main.pdf` |
| PDF mtime | 2026-09-17 13:59:01 UTC (`/tmp/paper_build/main.pdf`; repo copy 14:00:06 UTC) |
| Newest source `.tex` | `sections/appendix_b_prompts.tex`, 2026-09-17 12:44:33 UTC (also `07_conclusion.tex` 12:44:28, `04_method.tex` 12:44:17, `06_discussion.tex` 12:44:12) |
| Newest `main.tex` | 2026-09-17 12:43:50 UTC |

PDF is newer than every `.tex` in the publication tree. Previous `_build/main.pdf` was 16 Sep 18:17 (48 pp).

## Log (`/tmp/paper_build/main.log`)

| Check | Count |
| --- | --- |
| Fatal / `!` errors | **0** |
| Undefined references | **0** |
| Undefined citations | **0** |
| `LaTeX Warning: … undefined` | **0** |
| Package warnings | 2 (hyperref: `pdfusetitle` already used; empty anchor on `main.tex` line 110, the unnumbered thesis-URL footnote) |

BibTeX ran. Final pass: `Output written on /out/main.pdf (49 pages, 2481310 bytes).`

## Abstract wording (post-jury-edit check)

`pdftotext` pages 1–2. Both phrases are in the Abstract, so this is
the 17 Sep source, not the stale 16 Sep Overleaf PDF:

- **"confirmatory onset-locked"** — yes (`the confirmatory onset-locked cells were null`)
- **"conversational depth"** — yes (`confounded with conversational depth because a late advertisement sits on a shorter, later turn`)

Opening sentence also matches current `main.tex`: *When advertising
enters a conversational assistant…*
