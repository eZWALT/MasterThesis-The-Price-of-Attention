# Chapter 7 summary tables and conclusion handoff (6 September)

## State saved before the conclusion review

The Chapter 7 readability pass is on thesis Overleaf. Relevant commits:

- `d251c31`: correctness, figure-first layout, recut figures, trajectory
  context, late-control table, and Results/Discussion separation.
- `d1c577d`: first expandable summary-table redesign.
- `bc0ff17`: audited redesign now on Overleaf. This supersedes
  `d1c577d`.

Parent repository has the corresponding figure/script pass in `db61e60`,
but its GitHub push remains blocked by SSH authentication. Do not confuse
that with the Overleaf mirrors, which were pushed successfully.

## Canonical Chapter 7 summary design

Section 7.6 now has two tables:

1. `tab:results-summary` mirrors every family in
   `tab:analysis-families`, in the same order.
2. `tab:results-checks` contains every sensitivity or exploratory check
   reported in Chapter 7 but not declared as a Methods family.

Columns are `Family/Check`, \(n\), `Tests`, `Sig.`, `Headline`, and
`Where`. Pending behavioural and association rows keep their planned
test counts and blank `Sig.` cells so they can be filled without
redesigning the table.

The headline rule is explicit and non-selective:

- use the primary contrast where Methods names one (for example, pooled
  advertisement contrasts);
- otherwise use the cell with the smallest Holm \(p\);
- include the 95% interval;
- use only one compact headline per row.

The exploratory EEG row was corrected during the audit: the headline is
explicit-early relative \(\delta\), \(+0.19\), 95% CI
\([0.09,0.29]\), Holm \(p=.004\), not the visually larger absolute
\(\delta\) cell (\(+4.60\) dB, \(p=.007\)).

The sensitivity table records:

- Dataset A width/cleaning: 0/54;
- Dataset B width/cleaning: 3/72;
- contextual trajectory labelling: 0/4;
- GEE/bootstrap re-estimate of \(\delta^{(a)}_2\);
- whole-conversation Kruskal--Wallis block: 0/12, explicitly at the
  conversation rather than participant grain;
- fallback-label logistic checks: 2/2.

The two tables compile on separate pages with zero Chapter 7 overfull
boxes and zero undefined references.

## Scientific locks for the conclusion

- Results report numbers; Discussion and Conclusion interpret.
- Do not write “Wilcoxon Holm.” Holm \(p\) is the Holm-adjusted paired
  \(t\); Wilcoxon \(p\) is raw.
- Dataset A is **condition aggregation**. Never Path A/B, condition
  state, or equal-\(n\) neighbourhood.
- Dataset A planned any-ad and implicit-vs-explicit EEG contrasts are
  Holm-null. Early-vs-late posterior \(\alpha\) is the one
  confirmatory Dataset A cell below .05:
  \(M=-0.22\) dB, 95% CI \([-0.39,-0.04]\), Holm \(p=.0496\).
- Dataset B is Holm-null on both confirmatory measures at the
  pre-specified 4 s width and has intervals spanning roughly 2--4 dB.
- Do not restore EEG MDE, observed-power, “approached significance,” or
  causal processing language. The withdrawn power paragraph still
  exists in `discussion.tex` and needs a later cleanup.
- The one post-hoc Dataset A Fz \(\theta\) pair is exploratory and must
  not be promoted.
- The explicit-early low-frequency EEG pattern below the confirmatory
  rows is exploratory. It is not evidence that the advertisement was
  processed before the reply or proof of active processing.
- Trajectories are thesis-only. Planned advertisement-associated
  trajectory contrasts are Holm-null, but the classifier does register
  turn-depth changes. Two of four moving genre shares are fallback
  classes, so this is an instrument qualification rather than an
  advertisement effect.
- Behavioural Results 7.2 and cross-family associations 7.5 remain WIP.
  Conclusion language must not imply that those results exist.
- Wherever EEG enters, \(n=18\), laboratory only. Behavioural and
  trajectory-only families use \(N=54\).

## Open writing request

The user next wants candidate conclusion bullet points after a
whole-thesis read. Before proposing them:

1. pull the thesis Overleaf mirror;
2. read the full source architecture, especially the abstract,
   Introduction research questions, Theory, Methods family table,
   Results, Discussion, current Conclusion, and limitations;
3. distinguish conclusions supported by finished results from
   placeholders that depend on WIP Sections 7.2 and 7.5;
4. propose bullets only; do not edit Overleaf until the user approves
   wording.

The bullets should be self-contained for a reader who has only the
thesis. Avoid sprint vocabulary, generic claims, “AI” cadence, excessive
hyphenation, and conclusions that merely restate every table row.
