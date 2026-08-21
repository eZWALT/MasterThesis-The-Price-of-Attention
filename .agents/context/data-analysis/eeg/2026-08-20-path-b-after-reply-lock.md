# Path B lock after the finished reply — rejected as primary

Date: 20 August 2026
Branch: `eeg-path-b-after-reply`

**Decision (Walter, 20 August):** keep the golden visual-onset Path B
lock. After-reply is a dead sensitivity. It did not improve the 4 s
confirmatory tests. Do not promote it. Do not touch golden Gold.

A later hybrid (implicit @ `assistant_reply`, explicit golden) lives
only in untracked `analysis/eeg/scratch/hybrid_implicit_reply/`.
Same verdict: 4 s confirmatory still null. Do not commit that folder.

What “onset” means: `2026-08-20-what-path-b-onset-is.md`.

The confirmatory Path B lock stays what it is on `main`:

```text
t = 0  visual ad onset
pre  = [onset − 4 s, onset)
post = [onset, onset + 4 s)
```

Onset today:

| Format | Clock used now | Typical place |
|---|---|---|
| Explicit | observed `ad_displayed`, else `assistant_reply` + 0.49 s | banner after the reply |
| Implicit | observed `ad_displayed` if it fired before the reply, else `ad_injected` + 1.57 s | **before** the reply finishes |
| Matched no-ad | clock-projected `assistant_reply` | reply just finished |

That implicit cell is not “wait until the message is done.”

## What the UI actually does

The lab chat **streams** the assistant text (`st.write_stream`).
`assistant_reply` is logged when the stream ends. Then Streamlit reruns.

- **Implicit:** during the stream the product name is plain text. The
  clickable URL is applied only when history is re-rendered after the
  rerun (`linkify_inline_ad_titles`). So the inspectable implicit ad
  exists **after the whole reply is sent**.
- **Explicit:** `_render_turn_ads` paints the banner on that same rerun
  and logs `ad_displayed`. The banner is **after** the reply. Current
  Path B is already about this moment (reply + ~0.5 s).

So Walter’s read is right for implicit, and already roughly true for
explicit. The mismatch is the implicit lock vs the no-ad lock.

## Proposed alternative (this branch only)

Same 4 s pre/post, same ICA models, same 18 people, **different \(t=0\)**:

```text
t = 0  first moment the finished turn is inspectable
```

Practical rule, both ad formats and the matched no-ad cells:

1. take `assistant_reply`;
2. add the explicit banner lag (0.49 s) so implicit / explicit / no-ad
   share one post-rerun clock;
3. cut `[t − 4, t)` and `[t, t + 4)`.

Do **not** add a second 4 s dead time after that. The 4 s is still the
epoch length, not a waiting room.

This is a different estimand: “first seconds after the finished
ad-bearing reply,” not “first seconds after reconstructed ad chrome.”

## How to build it without killing Gold

If this is approved, write **parallel** files only. Never overwrite:

- `src/project/logs/xdf/gold/windows/ad_visibility_events.csv`
- `src/project/logs/xdf/gold/windows/ad_analysis_windows.csv`
- `src/project/logs/xdf/gold/features/ad_response_features.csv`
- `analysis/eeg/statistics/outputs/eeg_ad_response_contrasts.csv`

Suggested names:

```text
gold/windows/sensitivity/after_reply/ad_visibility_events.csv
gold/windows/sensitivity/after_reply/ad_analysis_windows.csv
gold/features/sensitivity/after_reply/ad_response_features.csv
statistics/outputs/sensitivity/after_reply/eeg_ad_response_contrasts.csv
```

Reuse `candidate_v1` ICA. No `--overwrite`. Path A is unchanged.

## What this will and will not answer

It can test whether the current implicit Holm-null is partly “we locked
before the URL existed.” It cannot become the paper primary by peeking
at *p*. Primary stays the frozen visual-onset 4 s + median + ICA unless
Sebastian agrees to change the estimand **before** looking.

Path A is irrelevant here. Those tiles cover the whole condition.

## Built 20 August 2026 (this branch)

Runner: `analysis/eeg/preprocessing/run_after_reply_path_b.py`
Heatmaps: `analysis/eeg/analysis/outputs/figures/eeg_only/heatmaps/after_reply/`

Onset moved relative to golden visual onset:

- implicit (`inline_persuasive`): mean +2.57 s (min +0.89, max +10.54)
- explicit (`explicit_ad_block`): mean +0.42 s (min −0.24, max +5.34)

All 216 windows eligible at 2 / 4 s; 8 s dropped one pair (107/108).

Confirmatory Path B (Fz theta, posterior alpha), ICA, Holm within feature:

| Width | What changed |
|---|---|
| 4 s | Still Holm-null. Implicit did not appear. Several *p* values moved toward 1. |
| 2 s | Golden explicit-early Fz theta (Holm 0.021; \(M=+3.30\) dB, CI \([1.12, 5.49]\)) is gone (now Holm 0.090; \(M=+2.55\) dB, CI \([0.41, 4.69]\)). |
| 8 s | Explicit-late posterior alpha stays Holm 0.023 (\(M=-1.08\) dB, CI \([-1.80, -0.36]\); same cell as golden). |

Exploratory 4 s hits that remain are explicit-early delta / relative delta / relative alpha. That is a thinner version of the golden 4 s exploratory cluster, not a new implicit story.

The assumption did **not** create a 4 s confirmatory effect. It removed the 2 s “first glance” theta cell, which is what you would expect if that cell was banner chrome rather than the finished reply. Primary stays golden visual-onset 4 s.
