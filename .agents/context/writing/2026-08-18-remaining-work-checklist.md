# Remaining work checklist (18 August 2026)

High-level items only. Cross them when the artefact exists (script +
numbers, or Overleaf prose), not when they have been discussed.

Hard deadline: **thesis 17 September 2026**. Paper after that if it
fights the thesis (27 August: paper optional this sprint).

Canonical goals (23 August):
`../data-analysis/2026-08-23-goal-list.md`.
Live sprint (27 August):
`../data-analysis/2026-08-27-backlog-and-timeline.md`.

Order of analysis (do not invert):

1. behavioural battery
2. personality / demographics
3. EEG
4. genre / trajectories
5. **all combos**: behavioural × EEG, behavioural × trajectory,
   trajectory × EEG, and the three-way (lab \(n=18\) wherever EEG
   is in; association, not mediation; blocked until 1 and 4 are frozen)

Insertion-policy model: **dropped 24 August**. Do not write it.

Delivery (also goals): thesis (17 September), paper, **presentation**.

---

## Analysis

### Behavioural

- [x] Finished roster: \(N=54\) (\(L=18\), \(C=36\)); unfocused kept if complete
- [x] Descriptive notice + cued recall (first pass; refresh on frozen ETL)
- [ ] Freeze one behavioural ETL (old `export.jsonl`, numeric conditions, no doubles). **Katerina missing (27 Aug); Walter owns this.**
- [ ] Goal 1: trust, credibility, manipulation, notice by condition / format / \(a^{\emptyset}\)
- [ ] Goal 2: same outcomes × BFI-10 and demographics (no personality clusters)
- [ ] Free-form text: findings + `recall_reaction` (descriptive / coding)

### EEG

- [x] Goal 3: primary spectral contrasts (4 s + median + ICA). Results 6.3 / thesis EEG Results are on Overleaf. Interpretation is Discussion, not Results.
- [ ] Angela / literature-ROI sensor retry (sensitivity; appendix only; boards exist)
- [x] EEG post-hoc restructure (Sebastian; **not** confirmatory 6.3).
  Bounded and run 28 August as a pairwise sweep:
  `../data-analysis/eeg/2026-08-28-posthoc-pairwise.md`. Analysis only;
  no manuscript text yet.
- [ ] **Methods gap:** Dataset B *secondary* contrast weights are not
  written down, so raw-space `early_vs_late` is an implementation
  choice. Decide the estimand and state it.
  `../data-analysis/eeg/2026-08-28-dataset-b-control-audit.md`
- [x] Human signoff: ICA vs no-ICA as primary (ICA primary as of 2026-08-19)
- [x] Human signoff: filter / interpolation figures (2026-08-19)
- [x] Mean-of-epoch dB vs median (Y_A still 0/48 Holm; keep median)
- [x] Epoch-length robustness grid 2/4/8/16/32 s (do not pick by p-value; 8 s alpha is sensitivity only)
- [x] Read vs write positive control (Fz theta Holm 0.007; alpha null).
  Proved the chain is alive, not that ads work. See
  `../data-analysis/eeg/2026-08-19-read-vs-write-what-it-proved.md`
- [ ] EEG × trust/credibility/manipulation: same three \(D\) as Goal 3
  (exploratory; lab \(n=18\); after Goal 1 freeze). See
  `../data-analysis/eeg/2026-08-19-eeg-analysis-menu-and-tickets.md`

### Trajectories (Goal 4)

- [x] Dataset + first pass of stages 1–4 (bare utterance primary)
- [x] Paper-shaped write-up of stages 1–4 (thesis only, 24 August)

### Cross-arm combos (Goal 5) — opened 27 August (joined dataset)

Honest tests that use behavioural composites still wait on Goal 1.

- [ ] Person × condition Gold join (behaviour + trajectory + EEG columns)
- [ ] Behavioural × EEG (\(n=18\))
- [ ] Behavioural × trajectory (\(N=54\))
- [ ] Trajectory × EEG (\(n=18\))
- [ ] Behavioural × trajectory × EEG (\(n=18\))

### Last science

- ~~Goal 6: multi-output insertion model~~ **Dropped 24 August.**

---

## Paper (Overleaf `publication/`)

Already standing: Theory, most of Method, flow figure, Results / Discussion /
Future Work skeleton, notice/recall slice in prose.

- [ ] Fill Results for goal 1 (then 2). Goal 3 EEG Results 6.3 are on
  Overleaf (pushed 21 August). Interpretation is Discussion 7.3, not 6.3.
  No invented Goal 1 tables.
- [ ] Rewrite Statistical Analysis (still a visibility / `XXXXX` template)
- [ ] Delete leftover Method red (ERP / ICA list that fights the spectral paragraph)
- [ ] When rewriting EEG Method: use the 2026-08-19 comments in
  `publication/main.tex` (shapes \(Y_A,Y_B,D\); Smulders median;
  Kislov estimand hedge; ICA now primary). Do not dump extra EEG cites.
- [ ] Cut or rewrite the remaining RQs (1–11) and H1–H3 so they match
  science 1–5. Predictive Analysis / RQ12–RQ14 dropped 24 August.
- [ ] Related Work / Research Gap polish (Heineking ≠ implicit/explicit)
- [ ] Admin: author roles, funding, ethics number, broken cites
- [ ] Appendices, or drop them

---

## Thesis (Overleaf `thesis/`)

Port the paper. Do not invent a second analysis.

- [x] Dataset § Experimental data: ingestion + trajectory Bronze/Silver/Gold
  + EEG preprocessing and Dataset A/B Gold (paper 5.6; pushed 23 Aug).
  Behavioural Gold still pending.
- [x] Method / procedure from the paper (design, IVs/DVs, EEG stats;
  pushed 23 Aug). Behavioural family still specified-not-estimated.
- [x] EEG Results 6.3 + sample descriptives into thesis Results (numbers
  only; Discussion 7.3 not ported).
- [x] Theory chapter (`chapters/theory.tex`, after Related Work).
- [x] EEG appendix D + Conclusion Future Work.
- [ ] Results / discussion for behavioural.
- [x] Trajectory results + discussion ported to thesis (24 August). Paper
  no longer carries Defs 1–6 / 6.4 / trajectory appendix.
- [ ] Theory / RQs: thesis keeps trajectory RQs; paper no longer does.
- [ ] Extra dissertation chapters: system, RAG, catalog, deployment.
  **27 Aug:** Walter is hand-polishing Ch 5–6 (quality pass; more owed).
- [ ] Conclusion summary (write last).

---

## Presentation (Overleaf `presentation/`) — Goal 8

**Start now (27 August).** Skeleton from thesis Methods; fill numbers when they exist.

- [x] Slide skeleton (28 August). Six sections, five conditions,
      \(N=54\) / EEG \(n=18\). `2026-08-28-presentation-skeleton.md`.
- [x] Appendix EEG bands slide + `waves.jpg` (31 August).
      Power/MDE write-up:
      `2026-08-31-presentation-eeg-waves-and-power.md`.
- [ ] Goal 1 takeaways into the grey Results block
- [ ] Goal 3 / 4 spoken polish (EEG and trajectories are already in)
- [ ] Combo slide only if Goal 5 ran

---

## Do not treat as leftover science

These are done enough to stop re-litigating them:

- implicit vs explicit; early = turn 2; late = turn 4; five conditions + \(a^{\emptyset}\)
- implicit ≠ subliminal ≠ covert
- participant is the inferential unit
- \(\theta\) co-varies with \(\lambda\); \(\epsilon\) is held
- local \(\delta^{(a)}_k\) undefined after turn 4; not a causal attention shift
