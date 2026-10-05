# 2026-09-18 — Defence deck: narrative, 20-minute cut, second plane

Deck commit: see `docs/overleaf/presentation` log for 18 Sep. Defence
Wed 23 Sep, Padova, 20 minutes + Q&A. Walter rehearses today and only
adds back slides if he comes in early.

## Where it stood

42 main-path slides (6 red cards included) for 20 minutes, ~28 s per
slide. Bloat in three places: five "why ads" slides before the question
is posed, four slides on the trajectory null, and two Discussion slides
that repeat Takeaways.

## The story in one sentence

Advertising inside a conversational assistant has a measurable cost that
the user pays: felt commercial pressure (+1.27 / 7), a credibility dent
when the ad arrives early, and a notice gap where about half do not
recognise the implicit mention as advertising. The sharpest signal sits
at the moment of insertion (onset EEG after the early banner; onset-locked
posterior α × trust ρ = .80), not in a redirected conversation. Title:
*The Price of Attention*. Every main-path slide serves that sentence.

Sources: thesis abstract, `tab:rq-answers`, Conclusion "The overall
picture"; paper abstract, §Implications, §Conclusion.

## Arc and time budget (20:00, 28 slides)

| Block | Slides | Time | Beat |
| --- | --- | --- | --- |
| Hook | Era, Free, Big Tech, OpenAI, Triad, Literature | 5:00 | mass medium → inference is not free → ads already fund Alphabet/Meta → OpenAI switched them on → triad tension → literature: nobody notices, labels barely help → so, user-centric. AI Race parked 22 Sep. |
| Question | Theoretical Work (1), RQ summary | 1:30 | instance vs policy (why λ and timing); four RQ blocks |
| Method | Formats, 2×2 + control, Flow (N = 54 / 18), Variables, Retrieval pipeline, Platform | 4:00 | what a subject lived through; what I built. Name the stack, do not walk the boxes. |
| Results | Experience forest, Who notices, User, Unconscious, Trust meets the scalp | 5:30 | Trajectory block, including "no steering seen", parked 22 Sep for time. One sentence stays on Takeaways. |
| Discussion | Effects matrix (wide), Limits | 1:30 | four beats spoken over the matrix |
| Close | Takeaways, Future work, Thanks | 1:30 | the price of attention; measure it, disclose it |

Red section cards are **on** (`\sectioncardsfalse` hides them). Six cards,
about 2--5 s each; Walter put them back 18 Sep.

## Mechanism

Header of `main.tex`: `\newif\ifsecondplane` (default false) and
`\newif\ifsectioncards` (default false). Every parked frame is wrapped

```
% OFF (18 Sep): reason
\ifsecondplane
\begin{frame}{…} … \end{frame}
\fi
```

Nothing deleted; source order preserved. Recover one frame by deleting
its two wrapper lines; recover all with `\secondplanetrue`. Full deck
with both flags on builds to 73 pages (verified), main path to 58
(28 talk + appendix).

The old `\iffasttalk\else … \fi` wrappers were converted to
`\ifsecondplane … \fi`; the flag no longer exists.

## Parked, in the order to bring back

1. Discussion: *What moved, what did not*
2. Results: trajectory transitions heatmap
3. Results: trajectory descriptives table
4. Results: trajectory genre example (definition slide)
5. Results: original δ̃ single-result slide (merged into the new one)
6. Close: *Artifacts* (one spoken line on Takeaways)
7. Question: *High-Level Goals*

Items 2–5 are one `\ifsecondplane` block; move the `\fi` up to recover
a subset.

## New / changed frames

- **4 - Trajectory: no steering seen** (new, replaces four): claim line,
  the three definitions in one row, a six-row table (270 / 1,080;
  81.7 % of steps change genre; N_shift 2.45 of 3; KW p = .58; early −
  a∅ on δ₂ Holm p = 1.00; 9 vs 10.46, p = .80), the permutation figure,
  closer "the classifier sees conversational depth, not the
  advertisement". Table is in a `\resizebox` because the scriptsize
  tabular overflowed its column.
- **Takeaways** rewritten to the thesis "overall picture": cost is
  specific (pressure + credibility, trust does not collapse, early
  banner bites); implicit is not the cheap option; nobody is spared +
  trajectories bound the instrument; price of attention paid at
  insertion; measure it before a serving rule, disclose it. His
  commented-out bullet kept.
- Big Tech slide got a spoken `%` line carrying the AI Race point.

## Do not

- Delete a parked frame. Park with the wrapper.
- Re-add trajectory slides before the rehearsal time is known.
- Say the slow tilt is "processing before the text" or "active
  processing"; say "a slow-power tilt in the first seconds after the
  early banner; none after the mention".
- Say Dataset A is all-null: early − late posterior α is Holm p = .0496.
