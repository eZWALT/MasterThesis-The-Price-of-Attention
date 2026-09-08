# 8 September: behavioural Ch 7.2 / 8.1 applied and pushed (thesis `15cf438`)

Supersedes the "not applied" status of `2026-09-07-ch7-ch8-behavioural-ready.md`.
Sits on top of the combos push `d206df3` (same morning, other session);
the two working trees did not collide.

## Decisions Walter took (8 Sep, 10:40)

1. **Paired \(t\) on \(D_i\) is primary.** `tab:analysis-families` behavioural
   row amended: "one-sample \(t\) on \(D_i\); Wilcoxon sensitivity;
   random-intercept LMM on \(Y_{ic}\) as an adjusted check". Dagger removed.
   The LMM Holm \(p\) stays as the last column of `tab:beh-planned`; the
   forest carries a dagger on the one LMM-only cell (trust early − late:
   \(t\) Holm .063, LMM .048, raw Wilcoxon .026).
2. **16 confirmatory tests**, not 11: 4 composites (trust, credibility,
   perceived manipulation, notice) × 3 planned contrasts + 2 cued-recall
   items (memory, trust after re-exposure) × 2. Holm is within outcome, so
   no \(p\) changed; 8/16 survive. Walter allowed option A (11) if it read
   better; 16 was kept because the Discussion already names notice as a
   primary outcome and the recall item is in the Methods DV paragraph.
3. **Katerina's design runs on Gold, \(N=54\)**, not on her \(n=19\)
   lab-only table. Friedman over five conditions + ten pairs, Holm-10 and
   BH-10 within outcome, eight composites: `stats/run_omnibus_pairwise.py`
   → `outputs/confirmatory/omnibus_{friedman,pairwise}.csv`. Post hoc,
   appendix only (`tab:beh-friedman`, `tab:beh-pairwise`).
4. **Push directly once it compiles.** No local TeX; static checks
   (braces, `\(`/`\)`, environments, `$` parity, every `\ref` resolves,
   every `\includegraphics` file present) passed. Walter checks the
   Overleaf compile.

## Katerina's `fb7e426` (7 Sep 14:38), reviewed

- Five conditions now; Friedman + Wilcoxon-Holm and a BH twin. Two
  survivors on her table: credibility explicit late vs implicit early
  (Holm .037) and pushing explicit early vs no ads (Holm .019).
- Still lab-only and **19 participants** (95 rows): includes
  `lab_subject_4_crowdfail`, which Methods excludes. No trust, notice,
  manipulation composite, or recall.
- `Cronbach_alpha.py` reverse-codes twice (once while parsing, once in
  the α function) → α on un-reversed items, negative for every
  multi-item scale. Correct α on Gold (270 rows): credibility .78,
  manipulation .86, notice .61, helpfulness .90, convincingness .74,
  relevance .87, neutrality .63 (`outputs/confirmatory/cronbach_alpha.csv`,
  `tab:beh-alpha`; one sentence in Methods §Behavioral Measures).
- Both her survivors replicate on Gold \(N=54\): credibility implicit
  early − explicit late is \(t\) Holm-10 .054 with raw Wilcoxon .004
  (never write "Wilcoxon Holm" in the thesis; her engine is described
  as raw Wilcoxon beside the Holm \(t\));
  manipulation explicit early − no ads Holm \(<.001\). Her folder is
  untouched; nothing in the thesis reads from it.

## What is now live in the thesis

- **Methods** `models.tex`: α sentence after the composites paragraph;
  family row (above); personality row no longer says "the same mixed
  model"; free-text row renamed "Free-text findings and open recall
  reaction"; behavioural post hoc layers declared in the same paragraph
  as the EEG pairwise sweep, pointing to `sec:app-behaviour`.
- **Results** `results.tex` §7.2: chapter opener no longer lists the
  battery as unestimated. 7.2.1 profiles fig → planned forests +
  `tab:beh-planned` (16 rows, \(\overline D\), CI, \(d_z\), Holm,
  Wilcoxon, LMM Holm) → localisation forest (post hoc) → one paragraph
  on omnibus/pairwise. Interaction sentence (null, \(|d_z|\le .06\)).
  7.2.2 "Advertisement notice and cued recall": notice items (sponsored
  button 1.85 → 3.4–3.7 → 5.3–5.7; brand mention 4.07 under \(a^\emptyset\)),
  cued recall, logged interaction measures (36 tests, 0 raw; largest
  \(d_z=-0.24\)), free text not analysed. `tab:results-summary`
  behavioural rows filled (16 / 8); four rows added to
  `tab:results-checks` (localisation 16/9, omnibus 80/13, estimator
  concordance, process 36/0).
- **Discussion** `discussion.tex` §8.1: six claim paragraphs — notice is a
  passed manipulation check; perceived manipulation is the detected cost;
  credibility and trust barely move (engine sensitivity named, no
  "approached"); format separates notice and memory, timing separates
  credibility, manipulation answers to both, interaction null; memory
  without a format difference in trust on re-exposure; what the battery
  cannot say. Opener drops the "battery not estimated" clause.
  Implications: new first paragraph (felt pressure, largest for an early
  labelled card; explicitly not a serving rule; RQ1/4/5/7 named); closing
  line now "Task moderation (RQ3) and personality moderation (RQ8, RQ9)
  remain unestimated." Limitations: credibility ceiling, notice α .61,
  arms pooled.
- **Appendix F** `appendix_f.tex` (`sec:app-behaviour`, included after E):
  descriptives, Likert distributions, α, localisation, Friedman,
  pairwise, estimator concordance figure + assumption paragraph
  (Shapiro 7/16 on \(D_i\), 20/20 on raw cells; bootstrap/\(t\) width
  ratio .97–1.01; engines agree 14/16, both exceptions trust; ICCs).
- **Abstract / Conclusion**: `% [TODO behavioural]` comment drafts only,
  next to the combos ones. Nothing live. Walter owns those sections.
- Figures copied to `figures/results/beh_*.pdf` (five).

## Names

`recall_trust_shift` is the item "After seeing this content, I felt I
could trust the chatbot overall." Display name **trust after
re-exposure**, not "trust shift". Fixed in `make_thesis_figures.py`.

## Do not

- Do not switch the primary statistic by a normality pre-test.
- Do not report Katerina's \(n=19\) numbers in the thesis.
- Do not promote the omnibus / pairwise stream or the secondary composites
  to confirmatory.
- Do not write "approached significance" for trust early − late; name
  the three \(p\).
