# Paper jury v1 (16 Sep evening) — three no-context reviewers on the PDF

PDF judged: paper Overleaf `74db73e` build (48 pp). Prompt:
`../2026-09-16-paper-review-metaprompt.md`. Reviewers read only the PDF.

| Jury | Model | Overall | File |
| --- | --- | --- | --- |
| Luna | gpt-5.6-luna-medium | 5/10 | `jury-v1-luna.md` |
| Grok | cursor-grok-4.6-xhigh-fast | 6/10 | `jury-v1-grok.md` |
| Kimi | kimi-k3-max | — | `jury-v1-kimi.md` |

## Applied the same evening (paper `74db73e` → `3f9b0c5`)

Consistency and wording only; no Gold number changed.

- Table 20 Holm `.050` → `.0496`; Table 19 relative-power denominator
  `1–45 Hz` → `0.5–40 Hz` (Gold code integrates 0.5–40).
- App. D: "this thesis" → "this paper"; `k=37 neighbourhood` →
  "37-epoch onset-centred aggregation"; "one expected false positive
  among 98" → "about five by chance".
- Results 5.4: width grid statement now says the Dataset A onset-centred
  cell was not re-estimated off 4 s (was "do not revise the family");
  smallest onset format Holm p = .08 named (was Discussion-only).
- Results 5.2: post hoc trust cell carries both Holm p (.031 in four,
  .078 in the ten-pair sweep); notice numbers tied to the notice outcome,
  Fig. 7 declared as the sponsored-item alone; non-noticer recall is
  "more than half" with the Gold count (16/29, 20/34); 36 tests =
  9 measures × (3 contrasts + interaction).
- Method 4.5: interaction spelled out and tested (raw p), exploratory
  redefined, two association families stated, Dataset B shared controls
  stated; 4.4 "centred on" → "nearest"; markers "reported to" rise/fall.
- Discussion: "did not fall on any corrected contrast" → declared
  estimator + straddle; "averaged over the whole conversation" →
  "aggregated over the condition"; no-ICA loses the δ Holm cell, said;
  relative θ no longer "support"; limitations in four paragraphs with
  latency scope (any-ad and Dataset B pre-window not cancelled).
- Conclusion: "obligation: to disclose" → measurement obligation +
  disclosure as next experiment; onset tilt "not on the mention" →
  "no Holm-surviving counterpart; direct format comparison null";
  numbers on every "fell".
- RQ table: legend rule for Supported/partly; RQ4/5 counts per factor;
  RQ7 "Supported for trust".
- App. B turn index `t` → `k`; prompt separator prints `---`; App. A
  euro-sign note fixed; bib acronyms braced; arXiv venues added.

## Not applied — Walter's call

1. **k = 37 and the whole-window aggregation.** All three juries called
   the hidden count the top vulnerability (Grok C1, Kimi C1) because
   App. D.1 printed the deprecated whole-window median at 4 s (−0.09 dB,
   raw p = .20). Walter 16 Sep 20:00: whole-window is deprecated, not a
   sensitivity; removed from D.1, E.2, and Results 5.4 (`a66e803`). Body
   still says only "standardised to the shortest eligible conversation".
2. **"Confirmatory" without pre-registration** (Luna M5, Grok C2). Rename
   to "planned" or add a clause that the 1,050 µV bound and the epoch
   count were fixed on this cohort.
3. **Dataset B pre-onset window = the 3 s retrieval wait** (Luna C1,
   Grok C3, Kimi M1). Now stated in Limitations; a delay-matched control
   analysis would be Gold work.
4. **Task and arm not in any model; arm-split only for any-ad** (Luna C2,
   C3; Grok M6, M7). A format/timing-by-arm table and a task covariate
   LMM are re-estimation on Gold.
5. **Abstract** (his): "none after the mention", post hoc trust cell,
   "did not seem to interact", no depth caveat on the EEG timing cell.
6. Title "Behavioral" (US) vs British body; XXXXX funding/ethics; HF/GitHub
   releases cited as live; acknowledgement register ("even if it's just a
   bit").
7. Related-work gap: Tang/Salvi/Zelch already measure user-side notice
   and acceptance; closer now says the missing piece is the bill measured
   while incurred with format × timing crossed — check he likes it.
