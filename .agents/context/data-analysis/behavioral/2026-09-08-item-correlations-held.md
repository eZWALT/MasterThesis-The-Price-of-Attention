# Item correlations — held, do not rerun (8 September)

**HIGH IMPORTANT.** Katerina looked at item–item correlations and
asked Walter to retry the behavioural analysis after dropping three
items that sat low:

- `llm_reliable` (credibility)
- `llm_opinionated` (neutrality)
- `llm_skeptical` (convincingness)

**Do not rerun.** Do not drop those items from Gold, from the
confirmatory family, from Cronbach, or from the thesis tables.
Do not pick a questionnaire item by correlation or by \(p\). That
is the same class of error as picking EEG \(k\) or a montage by
\(p\). Confirmatory composites stay the planned sets (Tang scoring,
`8-x` once).

If this is ever opened, it is a **sensitivity / appendix** only,
after 17 September, and only if asked. Note the three names; do
not invent a fourth.

## 8 September evening: Walter asked; answered as sensitivity only

Walter asked (17:37) whether the drop is sensible, and whether it should
be done after seeing better results. Answer, now in thesis Appendix F
`sec:app-beh-items` (`stats/run_item_sensitivity.py`,
`outputs/sensitivity/`):

- **Why they looked low.** The three are exactly the odd-polarity item
  of their scale (`llm_reliable` the only positive credibility item;
  `llm_opinionated`, `llm_skeptical` the only reversed items of
  neutrality / convincingness). Unreversed they correlate \(-.32\) to
  \(-.56\) with their mates; reversed once, \(+.32\) to \(+.56\),
  item–rest \(.37\)–\(.52\). No reliability ground to drop. Dropping
  `llm_reliable` "raises" α .78→.85 only because false / made-up are
  near-paraphrases (\(\rho=.76\)).
- **Would verdicts change.** Leave-one-item-out over the five 3-item
  composites (45 cells): 4 verdicts cross .05, in both directions.
  Credibility early − late (a confirmatory survivor) is **carried by
  `llm_reliable`** (item alone −0.46, Holm-sig; composite without it
  −0.26, Holm .159). Neutrality any-ad would *gain* a hit without
  `llm_opinionated` (.028); neutrality early − late without
  `llm_neutral` (.014); helpfulness early − late without `llm_not_aid`
  (.042). Convincingness unchanged under any drop.
- **Verdict.** Deciding after seeing that grid trades one finding for
  another = outcome-dependent analysis. Pre-specified composites stay
  primary. Nothing in Gold, the confirmatory family, or Ch 7 tables
  changed. Reported as sensitivity: `tab:beh-item-diag`,
  `tab:beh-item-loo`, `fig:beh-item-forest`, one row in
  `tab:results-checks`, one sentence in 7.2, one clause in 8.1.

The hold above stands: still no drop, still no rerun of the family.

8 September also: one-time fix of her `analysis/behavioural/Cronbach_alpha.py`
double reverse (parse + α). Gold and thesis α are unchanged
(.78 / .86 / .61 / .90 / .74 / .87 / .63 on 270 rows). Canonical
code remains `analysis/walter/behavioural/`. Do not edit her tree
again unless Walter says so.
