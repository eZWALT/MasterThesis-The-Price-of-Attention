# ICA primary branch and visual signoff

Date: 19 August 2026

## Human decisions recorded today

Walter approved all three remaining cleaning gates:

1. filtering and interpolation figures (`filtering_validation.png`,
   `interpolation_validation.png`);
2. all automatic ICA exclusions, including Subject 14's three of 22
   components (IC0, IC2, IC5; cap is three);
3. ICA as the primary Gold branch; no-ICA remains a mandatory sensitivity.

Do not reverse the primary branch because some ad-response tests are
significant only under ICA. Those six tests stay labelled ICA-dependent.

## What 99% PCA is not

`n_components=0.99` is fit dimensionality only. It is not the variance held
after `ica.apply`. Measured 2026-08-19 (MNE/EEGLAB percent variance
accounted for, filtered pre-ICA Raw vs applied ICA):

- held after apply: min 25%, median 65%, max 100%;
- Subject 14: 3 ICs, 34% removed / 66% held;
- harshest: Subjects 11 and 15 (~75% removed);
- Subject 12 loses 66% with one IC;
- Subject 19: 0 removed, 100% held.

## What changed on disk

- Primary policy: `cleaning_policy.json` → `frozen_v5_ica_primary`, ICA
  enabled, signoff `approved_as_primary_2026-08-19`.
- No-ICA archive: `gold/features/sensitivity/no_ica_frozen_v3/` and
  `analysis/eeg/statistics/outputs/sensitivity/no_ica_frozen_v3/`.
- Primary Gold and primary statistics now carry `ica_applied=yes`.
- Threshold 1,000 / 1,500 µV sensitivities remain no-ICA. Do not compare them
  to ICA primary.
- ICA report JSON and `ica_cohort_summary.csv` signoff: `approved`.
- Visual validation JSON signoff: `approved`.

## Read versus write positive control — explained, not implemented

This is **not** Q1 (sustained condition) and **not** Q2 (ad-locked
post−pre). It is a pipeline sanity check.

Q1/Q2 ask whether advertising format or timing changes EEG. A null there
could mean “ads do not move these spectra” or “the chain cannot recover any
known state difference.” The positive control tries to recover a difference
we already believe exists: reading the assistant versus composing a reply,
inside the same conversation, with the same 4 s epochs and the same 16
features.

### Why not `turn_N_read` / `turn_N_write`

The analysis plan originally named those markers. The protocol text says
`turn_N_read` is reading onset and `turn_N_write` is composing onset. The
deployed lab app does not keep that contract.

Without `?start_typing=1`, `_render_write_trigger` fires both
`user_starts_typing` and `turn_N_write` when the chat message is **submitted**,
not when typing starts. `ConversationManager` then logs `turn_N_read`
immediately after `user_message`, still at submission, before the next
assistant reply exists. Those three names can share one timestamp. They do
not mark “started reading the reply” or “started typing.”

### Static contract (decided 2026-08-06; still uncoded)

Use events that do have trustworthy order:

| State | Window |
|---|---|
| baseline | existing retained non-overlapping 4 s baseline epochs |
| reading | first complete 4 s after `assistant_reply` |
| writing | last complete 4 s before the next `user_message` |

Constraints:

- only inside `condition_start` → `condition_conclusion_submitted`;
- drop warmup, questionnaires, and post-task;
- drop pairs that overlap or are incomplete.

If coded, this would be a third Gold cutter on the same cleaned Raw. It would
not change Path A or Path B shapes. Dynamic-duration windows (reply length,
message length, `time_to_reply_ms`) would be a later sensitivity.

Do not implement until Walter confirms this contract.
