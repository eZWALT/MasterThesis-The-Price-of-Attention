# Weekend finish board (12 Sep 2026)

Thesis PDF due **Thu 17 Sep**. Defence **Wed 23 Sep** morning, Padova.
Cover title switch is `\usePaperTitle` in `dissertation.tex` (now **1** =
paper title). The same checkboxes also sit at the top of `AGENTS.md`
until 17 Sep (temporary).

Percentages are “ready to submit after his weekend pass”, not “does the
file exist”. Science 1–5 is frozen. What is left is prose he still has
to own, plus one review loop.

## Section finish

| Piece | % | Frozen? | What is still his |
|---|---|---|---|
| Abstract | 90 | numbers yes | Last-touch read. Do not rewrite wholesale. |
| Thanks / dedication / companion | 92 | yes | Personal; leave unless he wants a comma. |
| Ch 1 Introduction | **50** | RQs yes | Motivation / problem / contributions still company-first, typo-heavy, AI-ish. Highest-ROI rewrite. |
| Ch 2 Related work | **45** | cites yes | Leftover “Publication Related Work” heading; informal closer; one long blob. Same rewrite zone as Ch 1. |
| Ch 3 Theory | 82 | yes | Voice/overfull leftover. Do not reopen Definitions. |
| Ch 4 Dataset | 72 | EEG/traj Gold yes | **§4.2.2 he rewrites** from the draft. Two open comments (sample said too often; “spine” vs grains). Montage is vector. |
| Ch 5 System | **60** | engineering yes | His quality pass. Informal, typos, “agentic” leftover. |
| Ch 6 Methods | 83 | families yes | One leftover: exploratory families still mention an FDR \(q\) that the thesis no longer uses. |
| Ch 7 Results | 88 | **yes** | 36 `% WALTER:` lines still on the page (he has not re-read). G1 voice-read parked. Do not change numbers. |
| Ch 8 Discussion | 87 | **yes** | 45 comments unread by him. RQ table and matrix are in. |
| Ch 9 Conclusion | 90 | jacket + future work **his** | Findings paragraphs are in. Last-touch only. |
| App A–C (prompts, questionnaires) | 88 | review-1 yes | Prompt boxes in. |
| App D EEG | 85 | review-1 yes | D.4 gone; width table lives here. |
| App E behavioural | 88 | Gold yes | Demographics + notice tables in. |
| App F trajectories | 85 | Gold yes | Exploratory estimators gone. |
| Presentation | 40 | skeleton yes | Fill Goal 1 / combos after the PDF, not instead of it. |
| Paper | 20 | no | After 25 Sep. |

**Whole thesis PDF: ~75%.** The hole is Ch 1 / 2 / 5 and §4.2.2, not Ch 7–9.

## This weekend, in order

1. **He writes.** §4.2.2. Then a voice pass on Ch 1 and Ch 2 (and Ch 5 if time).
2. **He attacks statistics** on Overleaf Ch 7–8, dropping `% WALTER:` as he goes.
3. **Compile the PDF.** Paste `2026-09-11-thesis-review-metaprompt.md` into five chatbots. Save answers under `review-3/`.
4. **Loop 3** applies his comments + the five juries. Conclusion and abstract last, one agent, no wholesale rewrite.
5. **Tell Katerina:** her design was re-run on Gold \(N=54\), 0/70 survive; her tree stays read-only.

Parked, not this weekend: G1 voice-read (72 items, mechanical ones already applied), free-text coding, ad-moment scorer, paper, deck fill.

## Missing from the repo (not from the August checklist)

Closed since that file was written: Goal 1–5, personality, demographics on Gold, combos, abstract, conclusion, gold-tables figure, montage PDF, RQ remap.

Still actually missing, or stale enough to bite a new agent:

- Local Overleaf HEAD is ahead of what he last read: paper title, vector montage, eight restored `WALTER:` lines, unglued §4.2 sentence. **Push when he says.**
- `2026-09-08-travel-and-delivery-calendar.md` “still owed” list is **wrong** (abstract/conclusion/8.2 stubs are gone). Live owed = this file.
- Ch 1 contributions still promise “advertisement t” and a company-welfare frame that the abstract no longer uses.
- `models.tex` still says exploratory families carry an FDR \(q\). BH is gone.
- `results.tex` still prints a Gold filename in the planned-contrast paragraph.
- Boxplot-vs-profile on `fig:beh-profiles` is the one restored comment that is still a real call.
- Free text stays “not analysed”. Do not open it before 17 Sep.

## Science that must not be reopened

ICA models. \(k=37\). Item drop. Katerina’s tree. Confirmatory Dataset A CSVs. Policy scorer in the manuscript. Insertion-policy \(\pi\) as a Results model.
