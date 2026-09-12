# WP-A report — titles, case, 6.2 order, Results↔Discussion match, composites

12 Sep 2026, orchestrator. Items 1–6 of the HIGH LEVEL COMMENTS in `dissertation.tex`.

## Chapter titles

| Before | After |
|---|---|
| `Related Work \& Context` | `Related Work` (and the lone `\section{Publication Related Work}` heading is dropped; the chapter body follows the intro directly; "in the first section" removed from the intro sentence) |
| `Dataset` | `Datasets` |
| `AI System Design \& Engineering` | `System Design and Engineering` — alternatives left in a `% [AI:]` line: `Platform Design and Engineering`, `The Assistant Platform` |
| `Additional information on …` (App E, F) | Title Case |

## Case rule

Chapters **Title Case**; `\section`, `\subsection`, `\subsubsection` **sentence case**. This was already the pattern in Introduction, Results, Discussion, Appendices A–C, E, F; it is now applied to Theory (3), Datasets (4), System Design (5), Methods (6), Appendix D, Conclusion (`Future work` heading only). 46 headings changed. Renames with content: `Behavioral Measures` → `Behavioural measures` (British), `Laboratory Specific` / `Crowd Specific` → `Laboratory arm` / `Crowd arm`, `AI System Architecture Design` → `System architecture`, `Ad Insertion …` → `Advertisement insertion …`, `Product Catalog` → `Product catalogue` (catalogue is the majority spelling in prose), `Trajectories Data` → `Trajectory data`, `Post-hoc` → `Post hoc`. No label changed; all `\autoref`s still resolve (`\autoref` prints numbers, not names).

## Methods 6.2 order

Before: IVs → Laboratory conditions → Experimental design → Flow design → **Dependent variables** → Statistical framework.
After: IVs → **Dependent variables** → Laboratory conditions → Experimental design → Flow design → Statistical framework. Text moved verbatim (3 051 characters); nothing rewritten. The two `% To-Do` lines stay where they were (above Laboratory conditions).

## Results ↔ Discussion section titles

Results 7.5 `Genre trajectories and intent theory` → `Genre trajectories`. All other pairs already matched: Behavioural outcomes · Personality and demographic moderation · Neurophysiological outcomes · Genre trajectories · Associations across the three families. Results-only: Sample, exclusions, and descriptives; Summary of outcomes. Discussion-only: Implications; Limitations.

## composites → outcomes

`rg -i composite chapters/*.tex frontmatter/*.tex figures/results/*.tex` (prose lines, not `%` comments): **0 hits**. Already propagated in loop 2.

## Comment tags

Items 1–6 flipped to `% WALTER+:`; 7–11 tagged `% WALTER:` (open, running in WP-B/C/E; 8 blocked until after the juries).
