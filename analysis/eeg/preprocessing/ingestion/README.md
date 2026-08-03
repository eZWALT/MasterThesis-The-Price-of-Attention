# Ingestion and landing

Source discovery, transfer checks, and safe organization of incoming EEG files.
This layer may place byte-preserved files into Bronze but never alters XDF
contents.

Preview with:

```bash
python analysis/eeg/preprocessing/ingestion/organize_xdf_lake.py
```

Add `--apply` only when landing new recordings.
