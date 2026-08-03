# XDF data lake

This directory uses an immutable bronze, derived silver, and analysis-ready gold
layout.

```text
xdf/
├── bronze/                  Original XDF recordings; never modified
│   └── lab_subject_N/
├── silver/                  Reproducible derivatives
│   ├── audits/
│   ├── canonical_markers/
│   └── validation/
└── gold/                    Future analysis-ready EEG feature tables
```

## Layer contract

- **Bronze** contains byte-preserved acquisition files. No processing script may
  write into an XDF or replace a bronze file.
- **Silver** contains marker audits, reconstructed canonical timelines, alignment
  diagnostics, and validation reports. Every row retains its raw source.
- **Gold** is reserved for cleaned EEG measurements and model-ready tables after
  preprocessing decisions are frozen.

The data files remain ignored by Git. Pipeline code and documentation live under
`analysis/eeg/preprocessing/`.
