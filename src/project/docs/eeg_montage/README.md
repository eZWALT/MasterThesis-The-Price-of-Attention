# 32-channel montage (thesis figure)

Style is Sebastian's cap drawing. Channels and colours are ours.

- Generator: `make_eeg_montage.py`
- Thesis include: `figures/preprocessing/eeg_montage.pdf` (`fig:eeg-montage`)
- His original PNG is kept as `eeg_montage_sebastian.png` (not included)

Rules: 32 XDF labels, GND = Fpz (not recorded), Cz = online reference.
Red = Fz \(\theta\). Blue = posterior \(\alpha\). Yellow = other recorded.
Do not restore his FT9/TP9 labels or his green set.

The PDF is the vector original (`savefig(..., format="pdf")`). The PNG
is only a preview.
