# Gold stage

Gold applies study-level analysis contracts to validated Silver data.

- `windows/` defines baseline, sustained condition, advertisement, and matched
  no-ad timing contracts.
- `features/` creates validated 4-second epoch and condition-level band-power,
  regional theta/alpha, FAA, engagement, ad-response, retention, and
  signal-quality tables.

Gold does not decide how raw EEG is cleaned. It consumes the frozen Silver
cleaning and artifact policy.
