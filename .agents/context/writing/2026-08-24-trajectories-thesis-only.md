# Trajectories live in the thesis only (24 August 2026)

Walter + supervisor: the paper is not the place for genre-trajectory
theory, results, or discussion. That analysis is a tangent there.
Port it to the thesis. Do **not** put 6.4, `sec:disc-trajectories`,
Defs 1–6, or a trajectory appendix back into
`docs/overleaf/publication/`.

## Paper (keep out)

Remove and keep out:

- Theory: Intent and Attention Shifts, Definitions 1–6, \(f_{\mathrm{genre}}\),
  \(\delta_k\), \(\delta^{(a)}_k\), \(\tilde{\delta}^{(a)}\), \(N_{\mathrm{shift}}\),
  \(D\), \(H\), \(R\)
- Results 6.4 and its figures
- Discussion `sec:disc-trajectories`
- Trajectory appendix
- Method 5.8 rows / test paragraph that exist only for those tests
- RQ2 / RQ6 (conversational dynamics / attention shift)

Stay in the paper: taxonomy \(\lambda\), serving policy \(\pi\),
early = turn 2, late = turn 4, EEG, behavioural battery.

## Thesis chapter order (locked)

```text
1  Introduction
2  Related Work
3  Theory            ← Defs 1–6 stay here
4  Dataset
5  System design     ← after Dataset, before Methods
6  Methods
7  Results           ← numbers only (sample, EEG, trajectories)
8  Discussion        ← new chapter; paper-style split
9  Conclusion        ← summary + Future Work (not its own chapter)
```

Results ≠ Discussion still holds. Trajectory Holm-null \(\neq\) theory
is wrong lives in thesis Discussion, not Results.

When porting the appendix, strip AI em-dashes / prose `---` separators.
Keep booktabs rules and math minus signs.

Thesis front matter has a one-paragraph note
(`frontmatter/companion.tex`, not in the TOC) stating that the paper is
the condensed cut and that genre-intent trajectories stay thesis-only.
