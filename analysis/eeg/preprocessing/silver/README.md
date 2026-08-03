# Silver stage

Silver creates validated, reproducible derivatives from immutable Bronze data.
It is split into two human-readable work areas:

- `markers/`: raw-marker anomaly audit, event matching, canonicalization,
  governed reconstruction, and leakage-resistant validation;
- `signal/`: XDF-to-MNE conversion, montage/scaling checks, filtering,
  rereferencing, artifact policy, interpolation, and signal QC.

Every output must retain Bronze source paths and hashes. A derived event may
enter EEG analysis only when its provenance, uncertainty, EEG-span status, and
protocol eligibility permit it.
