# Ad-local epoch averaging (29 August 2026)

Exploratory sensitivity. Walter asked: instead of Dataset A’s
median over the whole condition (~95 four-second tiles), median only
the 5 or 10 tiles around each ad.

**Not confirmatory. No cell is promoted. Do not put this in Results
or the abstract.** Confirmatory stays 4 s · median · whole-condition
Dataset A and onset-locked Dataset B.

## What was actually computed

Same frozen Gold 4 s tiles (`condition_epoch_features.csv`), same 16
measures, same person-level Holm families as the planned analyses.
No Gold rebuild, no ICA refit.

For each visual onset (72 ads + 36 matched no-ad replies):

- `around`: the \(k\) retained tiles nearest the onset
- `pre`: the \(k\) tiles immediately before
- `post`: the \(k\) tiles immediately after

\(k \in \{1, 3, 5, 10, 20\}\). Every onset has at least 11 pre and 15
post tiles, so \(k \le 10\) is complete for all 108 onsets.

Dataset A: one person × condition median of those tiles. The no-ad
cell uses the matched turn-2 and turn-4 replies, so the control is
local in time too. Then the same four planned contrasts.

Dataset B companion: \(\Delta = \mathrm{median}(k\ \mathrm{post}) -
\mathrm{median}(k\ \mathrm{pre})\), then the same eight advertisement
contrasts. These tiles are aligned to condition start, not to visual
onset, so \(k=1\) is not confirmatory Dataset B (median \(r = 0.65\)
against the onset-locked \(\Delta\)).

`k=all` reproduces confirmatory Dataset A exactly (max \(|\Delta
\mathrm{median}| = 0\), max \(|\Delta p| = 0\)).

Scripts:

- `analysis/eeg/statistics/build_ad_local_epochs.py`
- `analysis/eeg/analysis/plot_ad_local_epochs.py`

Outputs: `analysis/eeg/statistics/outputs/sensitivity/ad_local_epochs/`
and `analysis/eeg/analysis/outputs/figures/ad_local_epochs/`.

## Verdict

**Averaging 5 or 10 tiles around ads does not turn Dataset A into a
hit.** Planned Fz theta and posterior alpha, any-ad / format / timing,
at \(k=5\) and \(k=10\) around the onset, are all Holm \(p \ge .45\).
The dilution hypothesis (a brief ad effect is washed out by ~95
tiles) is not supported for the confirmatory Dataset A estimands.

Closest Dataset A miss: Fz theta, any-ad, **post** \(k=5\)
(\(d_z = -0.51\), raw \(p = .045\), Holm \(0.135\)). Pre at the same
\(k\) is \(d_z = +0.20\). Not a result.

Twelve Holm cells appear somewhere in the \(k \times\) selection
search. That is the expected false-positive count: 240 Dataset A
primary families \(\times .05 \approx 12\), and we observed 9 Dataset A
Holm hits, several of them at \(k=1\) **before** the ad. Those are
not ad responses.

The one coherent cluster is Dataset B posterior alpha at **late**
insertions when \(\Delta\) is taken over \(k=3\) tiles
(~12 s pre vs ~12 s post):

- implicit late vs matched: \(d_z = -0.81\), Holm \(0.013\)
- explicit late vs matched: \(d_z = -0.77\), Holm \(0.014\)
- explicit late still Holm at \(k=5\) (\(d_z = -0.68\), Holm \(0.040\))

Early insertions stay null. Confirmatory 4 s Dataset B already leaned
the same way (explicit late posterior alpha \(d_z = -0.45\), Holm
\(0.28\)). The epoch-width grid already had the 8 s explicit-late
posterior-alpha cell (Holm \(0.023\)). This local-tile \(\Delta\) is
the same timescale, not a new family. \(k\) was searched, so it stays
sensitivity.

## Exhaustive \(k = 1\ldots 90\) (same day, 117 min)

`analysis/eeg/statistics/run_ad_local_k_exhaustive.py --hours 2 --k-max 90`.
Gates vs the sparse grid passed. 28,800 tests, 270 Holm cells
(highly correlated across neighbouring \(k\)). Outputs under
`statistics/outputs/sensitivity/ad_local_epochs/exhaustive/`.

**The \(k=5\) / \(k=10\) around answer does not change.** Planned
Dataset A any-ad / format / timing, Fz theta and posterior alpha,
stay Holm-null (Holm \(p \ge .45\)).

What the grid lights up is almost entirely **early vs late**, not
any-ad:

- Around, posterior alpha, early vs late: \(k=37\) and \(k=39\)–\(74\)
  (gap at 38). Best Holm \(\approx .0038\) at \(k=55\), \(d_z \approx -0.91\).
  Sign-flip search \(p\) on min Holm \(\approx .021\).
- Post, Fz theta, early vs late: mostly \(k=18\)–\(90\) with small gaps.
  min Holm \(\approx .012\). Search \(p \approx .044\).
- Post, posterior alpha, early vs late: \(k=29\)–\(90\). min Holm
  \(\approx .013\). Search \(p \approx .045\).
- Pre: two singleton \(k\)s. Treat as noise.

Dataset B: 9 Holm cells. The planned late posterior-alpha cluster is
still \(k=3\) (implicit) and \(k=3\)–\(5\) (explicit). Search \(p\) on
min Holm \(\approx .030\) / \(.031\). Random-tile ranking
\(p(\ge 9\ \mathrm{hits}) \approx .46\): nearest-to-onset ranking is
not special among pre/post tiles.

**Do not quote** `p_at_least_this_many_hits` for Dataset B
(reported 1.50). `n_hit_perm` is summed over leftover feature axis,
so the count can exceed \(n_{\mathrm{perm}}\). Dataset A around / pre /
post hit-count \(p\)s (.18 / .15 / .007) have the same leftover axis;
use `p_search_min_holm` instead. Around random-tile \(p \approx .015\)
is a different null (shuffle tile order, same \(k\)-prefix) and does
not have that bug.

\(k \gtrsim 37\) starts saturating short conversations (min condition
tiles = 37). The around-onset early-vs-late run is **not** “a few
epochs around the ad”; it is minutes of tiles, and whole-condition
confirmatory early vs late posterior alpha is still Holm-null
(\(d_z = -0.09\), Holm \(0.59\)). Do not pick \(k=55\).

## Balanced \(k = 30\ldots 70\) (31 August)

Walter asked to standardise tile count (e.g. 50 around the ad) so
short chats (37 tiles) and long chats (251) are not mixed.

`analysis/eeg/statistics/run_ad_local_balanced_k.py` reuses
`exhaustive/arrays.npz`. Around-onset only. Two rules:

- **saturate** (the exhaustive grid): keep \(n=18\); people with
  fewer than \(k\) tiles use all of them. Gates against exhaustive
  \(d_z\) (max \(|\Delta|=0\)).
- **complete**: drop anyone with any of the five conditions \(< k\).
  Ad conditions then have exactly \(k\) tiles. The no-ad cell still
  has more (two matched replies).

**\(k=50\) does not equalise without dropping people.** Shortest
condition is 37 tiles. Complete-case \(n\):

| \(k\) | \(n\) | who goes |
|---|---|---|
| 30–37 | 18 | nobody |
| 50 | 17 | `lab_subject_17` |
| 55 | 13 | five people |
| 70 | 8 | ten people |

The only \(k\) that equalises all 18 people is **37** (2.5 min of
tiles nearest the onset). Any-ad and format stay Holm-null there.
Early vs late posterior alpha is Holm \(0.0496\), \(d_z=-0.63\) —
the edge of the already-known timing run, not a new any-ad result.

At complete-case \(k=50\) (\(n=17\)) the same timing cell is still
Holm (\(d_z=-0.76\), Holm \(0.020\)); any-ad is still null. At
complete-case \(k=55\) that Holm **dies** (\(n=13\), Holm \(0.088\)).
The pretty saturate-mode peak at \(k=55\) needed the short chats
kept in with fewer than 55 tiles.

Still exploratory. \(k\) was scanned. Do not promote. Do not put
\(k=37\) or \(k=50\) in confirmatory Results. Outputs:
`statistics/outputs/sensitivity/ad_local_epochs/balanced_k/`.

Nothing is promoted. No manuscript text unless Walter asks.

## Locks

1. Exploratory. Nothing is promoted, whatever its \(p\).
2. Holm is still within feature within dataset, as confirmatory. It is
   **not** applied across the \(k\)-grid. Do not pick a \(k\) by Holm.
3. Do not treat \(k=1\) as an ERP. Tiles are 4 s and condition-aligned.
4. Do not rebuild Gold or change confirmatory 4 s.
5. No manuscript text until Walter says so.
