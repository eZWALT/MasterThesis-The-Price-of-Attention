# Remaining work checklist (18 August 2026)

High-level items only. Cross them when the artefact exists (script +
numbers, or Overleaf prose), not when they have been discussed.

Hard deadline: **thesis 17 September 2026**. Paper after that.
Analysis feeds the paper. The paper feeds the thesis.

Order of analysis (do not invert):

1. behavioural battery
2. personality / demographics
3. EEG
4. genre / intent
5. insertion-policy model (drop first if time is short)

---

## Analysis

### Behavioural

- [x] Finished roster: \(N=54\) (\(L=18\), \(C=36\)); unfocused kept if complete
- [x] Descriptive notice + cued recall (first pass; refresh on frozen ETL)
- [ ] Freeze one behavioural ETL (old `export.jsonl`, numeric conditions, no doubles)
- [ ] Goal 1: trust, credibility, manipulation, notice by condition / format / \(a^{\emptyset}\)
- [ ] Goal 2: same outcomes × BFI-10 and demographics (no personality clusters)

### EEG

- [x] Goal 3: primary spectral contrasts written (condition + ad-locked vs \(a^{\emptyset}\)) — tables exist; manuscript Results still unwritten
- [x] Human signoff: ICA vs no-ICA as primary (ICA primary as of 2026-08-19)
- [x] Human signoff: filter / interpolation figures (2026-08-19)
- [x] Mean-of-epoch dB vs median (Y_A still 0/48 Holm; keep median)
- [ ] Epoch-length robustness grid 2/4/8/16/32 s (do not pick by p-value)
- [ ] Read vs write positive control (contract decided; not coded)
- [ ] EEG × trust/credibility/manipulation: same three \(D\) as Goal 3
  (exploratory; lab \(n=18\); after Goal 1 freeze). See
  `../data-analysis/eeg/2026-08-19-eeg-analysis-menu-and-tickets.md`

### Later, if 1–3 are stable

- [ ] Goal 4: freeze genre classifier; \(\delta^{(a)}_k\) for early ads only
- [ ] Goal 5: multi-output insertion model + feature importance (optional)

---

## Paper (Overleaf `publication/`)

Already standing: Theory, most of Method, flow figure, Results / Discussion /
Future Work skeleton, notice/recall slice in prose.

- [ ] Fill Results for goal 1 (then 2, then 3). No invented tables
- [ ] Rewrite Statistical Analysis (still a visibility / `XXXXX` template)
- [ ] Delete leftover Method red (ERP / ICA list that fights the spectral paragraph)
- [ ] When rewriting EEG Method: use the 2026-08-19 comments in
  `publication/main.tex` (shapes \(Y_A,Y_B,D\); Smulders median;
  Kislov estimand hedge; ICA now primary). Do not dump extra EEG cites.
- [ ] Cut or rewrite the 14 RQs and H1–H3 so they match the five-goal order
- [ ] Related Work / Research Gap polish (Heineking ≠ implicit/explicit)
- [ ] Admin: author roles, funding, ethics number, broken cites
- [ ] Appendices, or drop them

---

## Thesis (Overleaf `thesis/`)

Port the paper. Do not invent a second analysis.

- [ ] Method / procedure (from the paper)
- [ ] Results / discussion (from the paper, once numbers exist)
- [ ] Theory / RQs aligned with the paper
- [ ] Extra dissertation chapters: system, RAG, catalog, deployment
- [ ] Conclusion + future work
- [ ] Presentation skeleton

---

## Do not treat as leftover science

These are done enough to stop re-litigating them:

- implicit vs explicit; early = turn 2; late = turn 4; five conditions + \(a^{\emptyset}\)
- implicit ≠ subliminal ≠ covert
- participant is the inferential unit
- \(\theta\) co-varies with \(\lambda\); \(\epsilon\) is held
- local \(\delta^{(a)}_k\) undefined after turn 4; not a causal attention shift
