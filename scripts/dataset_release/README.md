# Price of Attention, public tables

`build_price_of_attention.py` writes the Hugging Face dataset
`eZWALT/price-of-attention` from the Gold tables.

It drops chat text, Prolific identifiers, session folders, recording
paths, and calendar timestamps, and remaps `experiment_id`. The salt
stays in `~/.config/price-of-attention/` and must not be committed or
uploaded.

```bash
python scripts/dataset_release/build_price_of_attention.py --out /tmp/poa-hf
python scripts/dataset_release/build_price_of_attention.py --out /tmp/poa-hf --upload
```

The build refuses to finish if a headline drifts (manipulation mean,
re-exposure trust, the two trust × posterior-alpha correlations) or if
a private identifier survives.

Not included, on purpose: raw EEG, ICA models, the Amazon catalogue,
and `analysis/behavioural/`.
