# Completion snapshot (19 August 2026)

> 21 August: EEG 6.3 Results + 7.3 Discussion split are on Overleaf.
> See `2026-08-21-results-vs-discussion-and-eeg-6-3-pushed.md`.
> EEG Epoching was already pushed earlier; ignore the stale
> “DRAFTED (local, unpushed)” line below.

Rough. Weighted by what still has to exist, not by pages typed.
Analysis feeds the paper. The paper feeds the thesis.
Hard deadline: **thesis 17 September 2026**.

Crossable leftover items:
`2026-08-18-remaining-work-checklist.md`.

Overleaf paper STATUS banners (Airflow-simple) live in
`docs/overleaf/publication/main.tex` above each heading. They do not
override this note if they disagree; pull and check.

| Tag | Meaning |
|---|---|
| DONE (GOLDEN) | keep; do not rewrite |
| IN-PROGRESS (ADVANCED) | real prose, later polish |
| IN-PROGRESS (MID) | usable, still holes |
| IN-PROGRESS (LOW) | started, not in the right shape |
| SKELETON | headings / holding text; write on top |
| TO-START | empty, leftover template, or XXXXX |

---

## Estimates

| Stream | ~% | Why |
|---|---|---|
| **Paper** | **40** | Theory, Future Work, and most of Method are real. Intro / Related Work advanced. Results, Discussion, Conclusion, Statistical Analysis, and the RQ cut are not. No goal-1 numbers → not halfway to submission. |
| **Analysis** | **20** | Roster \(N=54\), EEG pipeline, notice/recall slice. Goal 1 (trust / credibility / manipulation) is not done. Goals 2–5 have not started as results. |
| **Thesis** | **15** | Intro + some related work / catalog. No Method chapter. Results stub + flow figure. Models, system, conclusion, appendices are headings. Cannot outrun the paper. |

What moves the numbers:

- paper → ~55–60% when goal-1 Results are in; ~70% after EEG or personality
- analysis → ~45% after frozen ETL + goal 1; ~60% after goal 2; ~75% after goal 3
- thesis → ~35% after porting Theory + Method; ~60% after the same Results as the paper

---

## Paper STATUS map (19 August)

Do not treat SKELETON Discussion / Conclusion as a blank board: some
holding prose already interprets the notice slice. Rewrite when models
exist. Future Work is golden again (restored list; do not skeletonize).

- **DONE (GOLDEN):** Theory (all three subsections); Method design,
  instruments, lab demographics, sample; Future Work; Acknowledgements;
  Disclosure; EEG Acquisition
- **IN-PROGRESS (ADVANCED):** Introduction, Problem Statement, Related
  Work, Method shell
- **IN-PROGRESS (MID):** Research Gap, EEG Preprocessing, Limitations
- **IN-PROGRESS (LOW):** Research Questions + H1–H3; Data availability
- **SKELETON:** Results (except sample), Discussion, Conclusion
- **TO-START:** EEG Measures / Statistical Analysis templates;
  funding; ethics; appendices
- **DRAFTED (local, unpushed):** EEG Epoching (20 August) --- Dataset A/B
  geometry, 4~s freeze, 2~s/8~s sensitivity. In
  `docs/overleaf/publication/main.tex`. Do not push until Walter asks.

EEG Acquisition is done. EEG Epoching is drafted locally. EEG
Preprocessing is mid because of the leftover red list and the outdated
``ICA was not applied'' sentence.
