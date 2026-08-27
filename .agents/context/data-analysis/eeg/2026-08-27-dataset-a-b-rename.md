# Path A/B renamed to Dataset A/B (27 August)

Naming lock. **Do not reintroduce "Path A" or "Path B" anywhere.**

- **Dataset A** — condition state. One median spectrum per participant
  × condition, `gold/features/condition_features.csv`. Sustained effect.
- **Dataset B** — advertisement onset contrast, 4 s either side of
  visibility against a timing-matched moment under \(a^{\emptyset}\),
  `gold/features/ad_response_features.csv`. Transient effect.

The letters stay, so \(D^{A}\) and \(D^{B}\) are unchanged and no
equation, contrast weight, or stored result moved.

## Why the letters were kept

Walter chose "Dataset A / Dataset B" over the descriptive alternative
(`sustained` / `onset-locked`) on 27 August. Recorded because the
alternative has a real argument behind it and may resurface: 42 of the
50 thesis occurrences are *analytical* rather than about a table
("Path A **tests** whether…", "the Path A **weights**"), and the
Discussion says outright that Dataset B "is a weaker estimand **on the
same recordings**" — there is one recording set and two reductions of
it, not two data collections.

The compromise actually shipped: six sentences were reworded so that a
dataset is never the subject of a test. They read "the Dataset~A
**contrasts** test whether…" and "the Dataset~B **contrast** is a weaker
estimand". Keep that convention when writing new text.

## Scope of the sweep

- Thesis: 50 occurrences over five chapters; labels `tab:eeg-path-a/b`
  and `subsubsec:dataset:eeg-path-a/b` renamed with all their refs.
  Pushed as thesis `7afc524`.
- Repo: 31 renamed paths, 45 files with content changes, plus the two
  context notes whose filenames carried `path-b`. Committed as
  `333f903`.
- `rg` skips dot-directories by default, so `.agents/` and `.cursor/`
  were missed on the first pass. If you ever sweep again, pass
  `--hidden`.
- Code: the plotting modules used `path` for both the A/B selector and a
  filesystem path. The selector is now `dataset`; genuine filesystem
  arguments in `src/project/core/retrieval/` were left as `path`.
- Output filenames were renamed to match the stems the plotting scripts
  emit, verified stem by stem. **Nothing was re-executed and no ICA
  model was touched.**
- `analysis/eeg/analysis/outputs/paper_depth/summary.json` is generated;
  its keys were edited in place to match the script. Re-run
  `run_paper_depth_audit.py` if you want it authentic.

## Commit hygiene

Nineteen of the touched files carried unrelated uncommitted work. The
rename commit was built by staging "HEAD plus the substitution" rather
than the working tree, so that work stayed unstaged. It is still
uncommitted; it was never part of `333f903`.
