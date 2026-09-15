# Thesis v1: source cleaned for jury (14 Sep 2026, evening)

Walter declared the Overleaf thesis **v1** after the loop-3 prose
pass. Green review marks were already off (`466d248`). This note is
the memory of the **source** clean that followed: unwrap `\rev{}`,
delete every `% WALTER:` / `% WALTER+:` / `% [AI:]` line, and strip
comments a committee would use against the manuscript if they ever
opened the Overleaf source.

Live manuscript: `docs/overleaf/thesis/` (Overleaf git). Do **not**
put Walter-review chat, agent instructions, or `\rev` back into the
`.tex`. New asks go here or in a new dated note.

## What was removed from the `.tex`

- All `\rev{…}` wrappers and the `\useReviewMarks` / `ReviewGreen` /
  `\rev` machinery in `dissertation.tex`.
- Every `% WALTER:` / `% WALTER+:` / `% Walter:` line, including the
  HIGH LEVEL COMMENTS block after `\end{document}`.
- Every `% [AI: …]` reply (and wrapped continuations).
- The **REVIEWER ATTACK SURFACE** block at the top of
  `introduction.tex` (archived below).
- Informal / process comments: “improve this with AI lol”, “To-Do
  (Mostly Katerina)”, “chatbot arena (for vibes)” design note,
  Katerina-tree “never quote” notes, review-1 leftovers, the
  REMINDER WALTER orchestration paragraph at the end of
  `results.tex`, leftover commented algorithm template in
  `dataset.tex`.

Prose itself was not rewritten in this pass. Content from the
accepted green pass (Ch 1–2, Ch 4 notation aligned to Ch 5, 8.3
rewrite, credibility pointer, ρ=.80 caveat, Limitations lines)
stayed.

## What was kept (on purpose)

Gold-provenance comments only:

- `% NUMBERS: analysis/walter/behavioural/…`
- `% Source: analysis/walter/behavioural/stats/…`
- `% Sensitivity only. Pre-specified outcomes stay primary.`

Plus compile / layout comments (`%!TEX`, appendix `\include` trap,
advisor stubs in `personalize.tex`). Those look like a thesis, not
like a chat log.

## Open asks that lived only in comments (not forgotten)

These were `% WALTER:` lines, not applied, and are now only here:

1. **The word “confirmatory”** (`models.tex`). He dislikes the weight
   it carries. Kept: it is the jury’s vocabulary for
   pre-specification. Do not rename it in a drive-by.
2. **More Kahneman** beyond peak–end (`discussion.tex` trust × α).
   Peak–end is the one that fits. Duration neglect is the same 1993
   paper already cited. Do not stack *Thinking, Fast and Slow*.
3. **Behavioural pipeline figure** (`dataset.tex`). He flagged the
   EEG/traj vs behavioural depth mismatch. Overkill for this weekend;
   leave it.
4. **Age as moderator.** Incomplete crowd ages; would be a new post
   hoc family. Limitation already in Results.
5. **Boxplot vs profile** on `fig:beh-profiles`. His call; not
   reopened.
6. **`models.tex` FDR \(q\)** leftover in exploratory-family prose
   (mechanical, still open if it is still in the body).
7. **Captions / page breaks / float placement.** After the jury, not
   before.

## Archived attack-surface item (was in `introduction.tex`)

Trajectory whole-conversation Kruskal–Wallis on \(N_{\mathrm{shift}}\),
\(H\), \(R\) runs on 270 conversation rows, not on the 54 participants
the chapter declares as its inferential unit. It is labelled
exploratory; participant ICC is 0.04–0.11; confirmatory tests use
person-level \(D_i\). A reviewer can still ask why this one does not.
Do not put this list back in the `.tex`. If the jury raises it,
answer in prose or in an appendix sentence, not in a comment.

## Jury next

1. Compile the Overleaf PDF (black, no green).
2. Paste `.agents/context/writing/2026-09-11-thesis-review-metaprompt.md`
   into the five chatbots with that PDF only.
3. Save answers under `.agents/context/writing/review-3/`.
4. Loop 3b applies the juries. Abstract and Ch 9 last, one agent, no
   wholesale rewrite.

Cover remains `\usePaperTitle=1` (paper title) until he flips it for
the long thesis title.
