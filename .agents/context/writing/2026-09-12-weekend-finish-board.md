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
| Ch 1 Introduction | **85** | structure + RQs yes | User-centric pass only. Not a rewrite. |
| Ch 2 Related work | **85** | cites yes | Stays compact **on purpose**. Do not add context. User-centric closer; drop the leftover paper heading. |
| Ch 3 Theory | 82 | yes | Voice/overfull leftover. Do not reopen Definitions. |
| Ch 4 Dataset | 85 | EEG/traj/beh Gold yes | §4.2.2 text is in (8 Sep Gold). Open comments only: “spine”→grains; \(N=54\) once; optional pipeline figure; keep `tab:beh-gold`. Not a rewrite. |
| Ch 5 System | **85** | engineering yes | User-centric pass only. Not a rewrite. |
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

**Whole thesis PDF: ~85%.** What is left is his review of Ch 7–8, a user-centric pass on Ch 1/5, and a few §4.2.2 comments. Not a rewrite of Ch 1 / 2 / 4.2.2 / 5.

## This weekend, in order

1. **He writes.** Done enough for v1: user-centric pass on Ch 1–2, Ch 4
   notation aligned to Ch 5. Residual comment-only asks are archived in
   `2026-09-14-thesis-v1-source-clean.md`.
2. **He attacks statistics** on Overleaf Ch 7–8. **Closed for v1.** All
   `% WALTER:` / `% WALTER+:` lines were stripped from the source on
   14 Sep evening so a committee cannot read the review chat.
3. **Five-LLM jury, two iterations.** Prompt:
   `2026-09-11-thesis-review-metaprompt.md`. Index:
   `review-3/jury-README.md`. v1 five-pack is in (use Gemini
   full-PDF dump). Extra in-IDE dumps listed there. Wait
   before apply.
   Then: apply → v2 → second five-judge pass → apply → v3 → final.
4. **Each apply** uses the juries from that pass only. Conclusion and
   abstract last, one agent, no wholesale rewrite. Do not put
   `% WALTER:` back. Do not treat jury table cells as Gold.
5. **Tell Katerina:** her design was re-run on Gold \(N=54\), 0/70 survive; her tree stays read-only.

Parked, not this weekend: G1 voice-read (72 items, mechanical ones already applied), free-text coding, ad-moment scorer, dataset release, paper, deck fill.

## Missing from the repo (not from the August checklist)

Closed since that file was written: Goal 1–5, personality, demographics on Gold, combos, abstract, conclusion, gold-tables figure, montage PDF, RQ remap.

Still actually missing, or stale enough to bite a new agent:

- Montage: Sebastian's cap style, our 32-ch rules (GND=Fpz, Cz=ref; red Fz \(\theta\), blue posterior \(\alpha\), yellow other). Generator `src/project/docs/eeg_montage/make_eeg_montage.py`. PDF is vector. His original PNG is `eeg_montage_sebastian.png`.
- `2026-09-08-travel-and-delivery-calendar.md` “still owed” list is **wrong** (abstract/conclusion/8.2 stubs are gone). Live owed = this file.
- Ch 1 still has one leftover company-welfare sentence (“advertisement t”). Catch it on the user-centric pass; do not expand the chapter.
- `models.tex` still says exploratory families carry an FDR \(q\). BH is gone.
- `results.tex` still prints a Gold filename in the planned-contrast paragraph.
- Boxplot-vs-profile on `fig:beh-profiles` is the one restored comment that is still a real call.
- Free text stays “not analysed”. Do not open it before 17 Sep.

## Science that must not be reopened

ICA models. \(k=37\). Item drop. Katerina’s tree. Confirmatory Dataset A CSVs. Policy scorer in the manuscript. Insertion-policy \(\pi\) as a Results model.
