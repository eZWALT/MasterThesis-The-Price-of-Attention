# WP3 — Notice / recall descriptive percentages (11 Sep 2026)

Closes results.tex:588 ("simple percentages of how many people noticed
ads per condition … e.g. 90% of people didn't notice implicit").
Descriptive only: shares of participants with Wilson 95 % intervals. No
test, no Holm. Walter Gold \(N=54\) (18 lab + 36 crowd), one rating per
participant × condition, no missing ratings.

Script: `analysis/walter/behavioural/stats/run_notice_percentages.py`
(reads only `outputs/gold/condition_features.csv` and
`advertisement_features.csv`; `build_gold.py` and
`make_thesis_figures.py` untouched). Thresholds were declared in the
docstring before any number was read and all are in the CSV:
≥ 5 "noticed / remembered", ≥ 4 at-or-above midpoint, ≤ 3 "did not
notice". Item names: Gold `notice_sponsored` = questionnaire
`personality_sponsored` ("I felt I noticed or clicked on sponsored
buttons"), `notice_brands` = `personality_brands`, `notice` = their
mean, `recall_memory` = cued memory.

## 1. Headline numbers

### Sponsored-button item (the detection item), per condition

| Condition | noticed ≥ 5 | midpoint 4 | did not notice ≤ 3 |
|---|---|---|---|
| No ad | 6/54 = 11 % [5, 22] | 1 | 47/54 = 87 % [76, 94] |
| Implicit early | 25/54 = 46 % [34, 59] | 1 | 28/54 = 52 % [39, 65] |
| Implicit late | 20/54 = 37 % [25, 50] | 4 | 30/54 = 56 % [42, 68] |
| Explicit early | 44/54 = 81 % [69, 90] | 0 | 10/54 = 19 % [10, 31] |
| Explicit late | 40/54 = 74 % [61, 84] | 0 | 14/54 = 26 % [16, 39] |

≥ 4 differs from ≥ 5 only where the midpoint was used (implicit early 48 %,
implicit late 44 %, no ad 13 %; explicit unchanged).

### Per format (pooled over timing) and any ad, sponsored ≥ 5

| Group | in at least one timing | in both timings | pooled ratings (n = 108 / 216) |
|---|---|---|---|
| Implicit | 33/54 = 61 % [48, 73] | 12/54 = 22 % [13, 35] | 45/108 = 42 % [33, 51] |
| Explicit | 49/54 = 91 % [80, 96] | 35/54 = 65 % [51, 76] | 84/108 = 78 % [69, 85] |
| Any ad (4 cond.) | 50/54 = 93 % [82, 97] | 9/54 = 17 % [9, 29] | 129/216 = 60 % [53, 66] |

"Did not notice" (≤ 3) in **both** implicit conditions: 19/54 = 35 %
[24, 49]; in **at least one** implicit condition: 39/54 = 72 % [59, 82].
So Walter's "90 % didn't notice implicit" is not what Gold says: it is
about half per implicit condition (52 % / 56 %), not nine in ten.

### Brand-mention item ≥ 5 (reported, **not** detection)

No ad 28/54 = 52 % [39, 65] · implicit early 42/54 = 78 % [65, 87] ·
implicit late 40/54 = 74 % [61, 84] · explicit early 44/54 = 81 % [69, 90]
· explicit late 43/54 = 80 % [67, 88]. Half the participants already
agree the assistant "mentioned products or brands" when nothing was
inserted (a shopping assistant names products anyway), so this item
separates ad from no ad by only ~25 points and barely separates the
formats. Do not read it as detection; the thesis already says so
(results.tex:166).

### Notice outcome (mean of the two items) ≥ 5

No ad 6/54 = 11 % · implicit early 25/54 = 46 % · implicit late 21/54 =
39 % · explicit early 40/54 = 74 % · explicit late 37/54 = 69 %.
Tracks the sponsored item almost exactly, because the brand item is
high everywhere.

### Cued memory (four ad conditions)

| Condition | remembered ≥ 5 | not remembered ≤ 3 | noticed ∧ remembered (both ≥ 5) | remembered given noticed |
|---|---|---|---|---|
| Implicit early | 31/54 = 57 % [44, 70] | 21/54 = 39 % [27, 52] | 15/54 = 28 % [18, 41] | 15/25 = 60 % |
| Implicit late | 32/54 = 59 % [46, 71] | 19/54 = 35 % [24, 49] | 12/54 = 22 % [13, 35] | 12/20 = 60 % |
| Explicit early | 47/54 = 87 % [76, 94] | 3/54 = 6 % [2, 15] | 38/54 = 70 % [57, 81] | 38/44 = 86 % |
| Explicit late | 44/54 = 81 % [69, 90] | 8/54 = 15 % [8, 27] | 33/54 = 61 % [48, 73] | 33/40 = 82 % |

Every participant remembered at least one explicit banner (54/54 ≥ 5 in
at least one explicit condition); 43/54 = 80 % remembered at least one
implicit mention when cued. Memory is not conditional on having flagged
the sponsored button: among participants who did **not** rate the
sponsored item ≥ 5 under implicit early, 16/29 = 55 % still rated cued
memory ≥ 5 (implicit late 20/34 = 59 %). Cued memory and in-session
notice are different things; the recall cue shows the ad again.

### Within-person: noticed the explicit banner but not the implicit mention

Sponsored ≥ 5 under explicit **and** ≤ 3 under implicit, same timing:

| Reading | share |
|---|---|
| Early pair (explicit early ≥ 5 ∧ implicit early ≤ 3) | 21/54 = 39 % [27, 52] |
| Late pair | 22/54 = 41 % [29, 54] |
| Both pairs | 11/54 = 20 % [12, 33] |
| At least one pair | 32/54 = 59 % [46, 71] |
| Reverse (implicit ≥ 5 ∧ explicit ≤ 3), early / late / either | 3/54 = 6 % · 5/54 = 9 % · 8/54 = 15 % [8, 27] |
| Noticed both formats, early / late | 22/54 = 41 % · 15/54 = 28 % |
| Noticed neither, early / late | 7/54 = 13 % · 8/54 = 15 % |

Four in ten participants, in each timing pair, reported the explicit
banner as sponsored and did not report the implicit mention as
sponsored; the reverse pattern is under one in ten.

## 2. Proposed text (numbers only; orchestrator / WP5a integrates)

### Results 7.2, `sec:results-behaviour-notice` (after the existing first paragraph)

\autoref{fig:beh-notice-percentages} and \autoref{tab:beh-notice-percentages}
give the shares of participants who agreed (rating \(\geq 5\) of 7) with
each notice item; Wilson 95\% intervals, \(N=54\) per condition. Under
\(a^{\emptyset}\), 6 of 54 participants (11\%, [5, 22]) reported noticing
sponsored buttons and 47 (87\%) disagreed (\(\leq 3\)). Under the implicit
conditions, 25 of 54 (46\%, [34, 59]; early) and 20 of 54 (37\%, [25, 50];
late) reported the mention as sponsored, while 28 (52\%) and 30 (56\%)
disagreed. Under the explicit conditions, 44 of 54 (81\%, [69, 90]; early)
and 40 of 54 (74\%, [61, 84]; late) reported the banner and 10 (19\%) and
14 (26\%) did not. Within participants and at the same timing, 21 of 54
(39\%) at turn 2 and 22 of 54 (41\%) at turn 4 reported the explicit banner
but not the implicit mention; the reverse pattern occurred in 3 and 5
participants. Cued memory was rated \(\geq 5\) by 31 and 32 of 54 for the
implicit mentions (57\%, 59\%) and by 47 and 44 of 54 for the explicit
banners (87\%, 81\%); among participants who had not reported the implicit
mention as sponsored, 55\% (early) and 59\% (late) still rated cued memory
\(\geq 5\). The brand-mention item is \(\geq 5\) for 28 of 54 participants
(52\%) under \(a^{\emptyset}\) and 74--81\% in every advertisement
condition, and is not read as detection.

(Trim to 3–5 sentences as needed; the Wilson intervals can be dropped
from prose and left to the figure. Keep the "not read as detection"
sentence merged with the existing one at results.tex:166.)

### Discussion 8.1 (descriptive, no test, user-centric)

Roughly half of the participants did not report the implicit mention as
sponsored (28 and 30 of 54 in the two implicit conditions), against one in
five to one in four for the labelled banner (10 and 14 of 54); four in ten
participants, at the same turn, reported the banner and not the mention.
An implicit mention therefore reaches a large share of users without
being recognised as advertising, and this is the group the perceived
manipulation and trust outcomes cannot speak for, since they rated a reply
they did not read as sponsored. Cued recall does not close that gap: more
than half of those who had not flagged the implicit mention still
remembered its content once it was shown again, so the mention was read
and retained, not overlooked.

(Third sentence is the interpretive one; keep it if WP5a wants the
memory-without-notice point, drop it otherwise.)

### Caption for the figure (≤ 2 lines)

Share of participants rating "I noticed sponsored buttons" \(\geq 5\)
(noticed), 4, or \(\leq 3\) (did not notice), by condition (\(N=54\)).
Orange whiskers: Wilson 95\% interval on the noticed share.

Figure environment to insert (thesis `figures/results/`):

```latex
\begin{figure}[!htb]
\centering
\includegraphics[width=0.9\linewidth]{figures/results/beh_notice_percentages.pdf}
\caption{Share of participants rating ``I noticed sponsored buttons'' \(\geq 5\) (noticed), 4, or \(\leq 3\) (did not notice), by condition (\(N=54\)). Orange whiskers: Wilson 95\% interval on the noticed share.}
\label{fig:beh-notice-percentages}
\end{figure}
\input{figures/results/tab_beh_notice_percentages.tex}
```

## 3. Files produced

- `analysis/walter/behavioural/stats/run_notice_percentages.py` (new,
  standalone; rerun in ~2 s).
- `analysis/walter/behavioural/outputs/exploratory/notice_recall_percentages.csv`
  — 195 rows, long: `measure, threshold, group, unit, k, n, share,
  wilson_lo, wilson_hi`. `unit` is `participants` except the `*_trials`
  rows (`ratings`, denominators 108 / 216, kept only for comparison with
  trial-pooled readings; never quote them as people).
- `analysis/walter/behavioural/outputs/figures/thesis/beh_notice_percentages.pdf`
  (vector, 0 embedded images, fonttype 42; `.png` sibling is a preview
  only) and `tab_beh_notice_percentages.tex` (booktabs, one row per
  condition, cells `k/54 (pct)`, one-line caption).
- Copied to `docs/overleaf/thesis/figures/results/beh_notice_percentages.pdf`
  and `tab_beh_notice_percentages.tex`. **No `.tex` chapter edited, nothing
  committed.**

## 4. Cross-check against Katerina's `outputs/ad_notice/`

Read only. Her definition: a trial is "noticed" when **either** item
(brands or sponsored) is ≥ 5; midpoint counts as not noticed; roster
\(n=45\) participants (her 45 are a strict subset of the Gold 54; the 9
missing are all Gold participants she excluded). Her table is trial =
participant per condition, so denominators match in kind.

- **Direction and magnitude agree.** Her sponsored-only ≥ 5 shares by
  condition are within 1–4 points of the Gold \(N=54\) shares above
  (implicit ≈ 40 %, explicit ≈ 70–80 %, no ad well under 10 % vs 11 %
  here). Her brands-only shares are within 4 points as well. The Gold
  equivalent of her composite "either item ≥ 5" (row `sponsored_or_brands`
  in the CSV: no ad 54 %, implicit 80 % / 80 %, explicit 89 % / 87 %) sits
  within 0–3 points of hers.
- **Where we disagree is the definition, not the data.** Her headline
  "noticed" is driven by the brand item, which is ≥ 5 for half the
  participants under \(a^{\emptyset}\); by her rule 54 % of Gold
  participants "noticed" an ad in the condition that had none. The thesis
  should therefore keep the sponsored-button item as the detection
  measure (as results.tex:166 already does) and report brands separately.
  Her `pct_noticed` numbers must not be quoted; the Gold rows above
  replace them.

## Open questions for Walter

- Walter's "90 % didn't notice implicit" is not supported: it is ~52–56 %
  per implicit condition (35 % in both). The user-centric claim that holds
  is "about half did not report the implicit mention as sponsored, against
  one in five for the banner; four in ten reported the banner but not the
  mention at the same turn".
- Whether the figure goes in 7.2 proper or the appendix (7.2 already has
  profiles + forests + localisation; this one is small and descriptive).
