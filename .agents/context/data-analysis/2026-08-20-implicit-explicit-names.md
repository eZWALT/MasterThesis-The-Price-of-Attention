# Implicit / explicit, not inline / block

Date: 20 August 2026

Paper and agent language is **implicit** vs **explicit**. That is
presentation \(\lambda\).

Log / Gold keys are unchanged. Do not rename these fields:

| Paper name | Condition key | Injector |
|---|---|---|
| Implicit early | `inline_early` | `inline_persuasive` |
| Implicit late | `inline_late` | `inline_persuasive` |
| Explicit early | `block_early` | `explicit_ad_block` |
| Explicit late | `block_late` | `explicit_ad_block` |
| No ads | `no_ads` | — |

Path A format contrast: implicit − explicit (`inline_vs_block` in
tables). Path B cells: implicit/explicit × early/late minus matched
no-ad.

Display labels live in `analysis/eeg/analysis/condition_labels.py`.
Figures must import those names. Implicit ≠ subliminal ≠ Heineking
covert.
