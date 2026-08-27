# What Dataset B “onset” is

Date: 20 August 2026

Onset is a **clock time**, not a brain event. It is the \(t=0\) we
cut the ad-locked EEG around. Nobody “has an onset.” The ad does.

```text
pre:  [onset − 4 s, onset)     what the EEG was doing just before
post: [onset, onset + 4 s)     the next 4 s of EEG
test: post − pre, then minus the same contrast on a matched no-ad reply
```

The 4 s is the **length of that slice**. It is not a waiting room after
the message finishes.

## The three times people mix up

On one ad turn the log has (at least) three different clocks:

| Name | What it is | Typical place |
|---|---|---|
| **inject** | Server stuffed the product into the prompt | before anything new is on screen |
| **reply** | `assistant_reply` — stream ended, full text is in the log | message finished sending |
| **onset** | Best estimate of **when the ad became visible** | the Dataset B lock |

Those are not the same instant.

## How we get onset (golden / confirmatory)

Prefer the UI event `ad_displayed` when it actually fired.

If it is missing — it often is, especially for implicit ads — reconstruct:

- **Explicit:** reply finished, then +0.49 s. That is when the labelled
  banner is painted on the Streamlit rerun, after the reply is already
  on screen.
- **Implicit:** injection, then +1.57 s. That is when an old
  `ad_displayed` used to fire, **during** streaming, before the reply
  marker. The clickable URL is only applied after the stream ends.
- **Matched no-ad:** the no-ad `assistant_reply` at the same turn.
  There is no ad to display, so the control is “reply just finished.”

Worst-case reconstruction error is about 0.4 s. Fine for a 4 s
spectrum. Useless for an ERP.

`turn_N_read` is not onset. Session baseline is not onset.

## One explicit turn, in order

1. Inject (~3 s before onset).
2. Reply appears (~0.5 s **before** onset). The assistant text is
   already up.
3. **Onset:** banner appears above the reply.
4. Dataset B post is the next 4 s: labelled ad + the reply that was
   already there.

## One implicit turn, in order

1. Inject (~1.6 s before onset).
2. **Onset:** our estimate of “ad chrome is on screen” while the
   sentence is still streaming. Product name may be visible as
   plain text; the URL is not clickable yet.
3. Reply marker (~1.6 s **after** onset). Stream done. Next rerun
   linkifies the URL.
4. Dataset B post is 4 s from that mid-stream estimate, so it usually
   contains the reply start. A 2 s post often misses the reply.

## What we tried and rejected

Branch `eeg-path-b-after-reply` locked every cell to
`assistant_reply + 0.49 s` (finished message, then the same rerun
lag). Implicit onsets jumped +2.6 s on average. 4 s confirmatory
stayed Holm-null. The 2 s explicit-early Fz theta hit died.

**Keep the golden visual-onset lock.** After-reply is a sensitivity
only. See `2026-08-20-path-b-after-reply-lock.md`.

Dataset A does not use this clock. Dataset A tiles the whole condition.
