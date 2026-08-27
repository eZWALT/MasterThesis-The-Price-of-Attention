# Wang 2022 zone channel set

Date: 25 August 2026. Sensitivity only.

Wang and Mengoni 2022 do **not** publish a per-band electrode list.
`wang2022_v0` applies §2.2 geography to that paper's own 10–20 zone
letters on this 32-channel cap. It is not a second confirmatory family.
Do not put it in EEG 6.3 or the abstract.

## Mapping (`channel_sets.WANG2022_BAND_CHANNELS`)

| Band | Wang §2.2 words | Sensors on this cap |
|---|---|---|
| δ 0.5–4 | adults frontally | Fp1 Fp2 F3 Fz F4 F7 F8 F9 F10 |
| θ 4–8 | left central, parietal, temporal | C3 P3 T7 P7 |
| α 8–13 | occipital | O1 Oz O2 |
| β 13–30 | frontal and central | F3 Fz F4 F7 F8 F9 F10 C3 Cz C4 |
| γ 30–40 | cortex; intro groups with frontal/central alertness | same as β |

P7 is in θ because Wang §2.1 says P7/P8 are posterior temporal, not
parietal. F7/F8 stay in the frontal lists. No FC/CP sites were added.
Hz edges stay Angela/Zheng/Cochran. Derived measures stay `current_v1`.
Cleaning stays 32-channel.

George 2025 remains `literature_roi_v0`: the same nine Methods sites
for every band. Do not mix the two papers.

## Run

```bash
python analysis/eeg/preprocessing/run_channel_set_sensitivity.py \
  --channel-set-policy \
  analysis/eeg/preprocessing/gold/features/channel_set_policy_literature_roi.json \
  analysis/eeg/preprocessing/gold/features/channel_set_policy_wang2022.json
python analysis/eeg/analysis/plot_channel_set_heatmaps.py
```
