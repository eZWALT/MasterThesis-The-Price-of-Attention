# EEG analysis

All EEG preprocessing code, policies, manifests, validation tools, and pipeline
documentation are self-contained under `preprocessing/`. Statistical analysis
stays separate because it consumes frozen Gold feature tables rather than
creating them.

```text
analysis/eeg/
├── preprocessing/
│   ├── ingestion/        Landing and safe organization
│   ├── bronze/
│   │   └── manifests/    Inventory and recording-map evidence
│   ├── silver/
│   │   ├── markers/      Canonical event timing and validation
│   │   └── signal/       MNE conversion, cleaning, artifact QC
│   └── gold/
│       └── windows/      Condition and advertisement contracts
└── statistics/      Contrasts, models, and publication outputs
```

Raw and generated participant data deliberately remain outside the code folder
under `src/project/logs/xdf/{bronze,silver,gold}`. Bronze XDF files are immutable;
the preprocessing code only reads them and writes reproducible derivatives.

The pipeline diagram follows the project documentation convention and lives at
`src/project/docs/eeg_pipeline/`.

Start with `preprocessing/README.md`. Confirmatory Dataset A is
condition aggregation \(k=37\):

```bash
python analysis/eeg/statistics/run_equal_n_dataset_a.py
```

Do not run `statistics/build_condition_contrasts.py` onto the default
output directory — that rebuilds whole-window Dataset A over the
reported tables. Channel-set / literature-ROI averages (George
nine-site and Wang-zone) are a sensitivity
(`preprocessing/run_channel_set_sensitivity.py`); they do not replace
primary Gold. Heatmaps:
`analysis/eeg/analysis/plot_channel_set_heatmaps.py`.
