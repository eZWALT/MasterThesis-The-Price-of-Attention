# Literature ROI: George 2025 nine-site montage

Date: 24 August 2026; corrected 25 August 2026. Sensitivity only.

The first fill mixed George & Gulia 2025 Table 1 with Wang & Mengoni
2022 §2.2 and invented per-band electrode tuples. Neither paper
publishes those tuples. That mix is dropped.

## What the papers actually say

George & Gulia, *Ann Neurosci* 2025, doi:10.1177/09727531251341665:

- Methods: they record **nine** unipolar 10–20 sites:
  `O1, Oz, O2, C3, Cz, C4, F3, Fz, F4`.
- They extract theta and alpha power from those nine sites.
- Table 1 is location *prose* (frontal δ, medial-temporal θ, posterior
  α, fronto-motor β, somatosensory γ). It does not name electrodes.
- They have no temporal electrodes, so Table 1 “medial temporal” θ
  cannot be turned into T7/T8 from that paper.

Wang & Mengoni, *Brain Inform* 2022, doi:10.1186/s40708-022-00159-3:

- §2.2 is the same kind of regional prose.
- Their method maps clinical-report keywords onto 10–20 *zones*
  (Fp, F, C, P, T, O) per patient. Not one fixed five-band list.

Angela's *manuscript* treats band power as a channel-wise feature and
cites Zheng / Cochran only for band names (Newson for Hz). Her *code*
has a separate `BAND_CHANNELS` ROI dict; that is now
`angela_code_v0` (`2026-08-27-angela-code-channel-set.md`). Do not
mix that dict into this George nine-site branch.

## What we fill (`literature_roi_v0`)

One paper, one list, all five global bands:

`F3, Fz, F4, C3, Cz, C4, O1, Oz, O2`

Hardcoded as `channel_sets.GEORGE2025_NINE`. JSON must match.
Derived measures stay on `current_v1`. Cleaning stays 32-channel.
Appendix: `sec:app-eeg-channel-sets`.

A separate Wang-zone branch (`wang2022_v0`) maps §2.2 geography onto
this cap. That is not George, and Wang still does not publish those
electrodes. See `2026-08-25-wang-zone-sensitivity.md`.
