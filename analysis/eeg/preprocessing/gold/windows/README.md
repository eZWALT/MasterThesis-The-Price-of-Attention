# Gold processing

Construction of eligible EEG windows, prespecified measurements, and
analysis-ready feature tables from validated Silver data.

## Current window builders

```bash
python analysis/eeg/preprocessing/gold/windows/build_condition_windows.py
python analysis/eeg/preprocessing/gold/windows/build_ad_visibility.py
python analysis/eeg/preprocessing/gold/windows/build_ad_windows.py
```

The sustained condition window starts at `condition_start` and ends at
`condition_conclusion_submitted`. Questionnaire time is excluded. The
`turn_N_read` marker is not treated as visual onset because it is emitted near
the corresponding submission marker.

Advertisement timing has a separate provenance-aware contract:

- use `ad_displayed` when it was observed;
- for missing explicit-block events, use assistant reply completion plus the
  calibrated median lag;
- for missing inline events, use injection plus the calibrated median legacy
  display lag.

Current leave-one-out p95 calibration errors are 0.226 seconds for the block
estimator and 0.433 seconds for the inline estimator. These estimates support
multi-second spectral windows, not ERP claims.

`build_ad_windows.py` freezes one 4-second epoch immediately before and after
each visual onset. It also creates matched no-ad controls around the
clock-projected `assistant_reply` at turns 2 and 4 of the no-ad condition.
These are reply-display proxies; `turn_N_read` is never substituted. The
current laboratory contract contains 144 advertisement windows and 72 matched
no-ad windows.

Generated tables are written under
`src/project/logs/xdf/gold/windows/`.
