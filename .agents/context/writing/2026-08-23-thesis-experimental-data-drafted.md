# Thesis experimental-data section drafted (not pushed)

Date: 23 August 2026. Overleaf `docs/overleaf/thesis/`, local only.

Pulled `main` first (`8fe3d50`). Walter had already sketched
`chapters/dataset.tex` § Experimental data (Ingestion / Behavioural /
Trajectories / EEG) and uploaded
`figures/preprocessing/trajectory_preprocessing.png`. Local lineage
draft from earlier in the day was stashed (`local lineage draft`) and
not restored: it used Goal language and a 3.2/3.3 split he had already
replaced.

## What was written

Filled his skeleton in `chapters/dataset.tex`:

- Ingestion: JSONL + optional XDF, \(\mathcal{D}_r=(\mathcal{E}_r,\mathcal{X}_r)\),
  \(N=54\) (\(L=18\), \(C=36\)), join on `experiment_id` + `condition`.
  Unfocused **stays** if instruments complete; unfinished / synthetic /
  crowdfail / beta are out. Corrects the Overleaf sketch that treated
  unfocused as a drop.
- Behavioural: holding paragraph. Gold scoring still pending.
- Trajectories: Bronze / Silver / Gold, two Gold grains, table
  `\label{tab:trajectory-medallion}`, \(f_{\mathrm{genre}}\),
  `genre_source` as rows, primary = bare utterance. No results numbers.
- EEG: same contract, Path A / Path B, \(n=18\), participant is the
  unit. Paper 5.6 ported into Dataset (preprocessing + two Gold
  tables) on 23 Aug local; not pushed. See
  `2026-08-23-thesis-eeg-gold-ported.md`.

Do **not** push until Walter approves.

## Agent lock this prose follows

`.agents/context/data-analysis/trajectories/2026-08-23-trajectory-medallion.md`
