# Ad-moment scorer

Side project. Not a thesis Results artefact.
Context: `.agents/context/data-analysis/policy/` (newest dated note).
Live research line:
`.agents/context/data-analysis/policy/2026-09-06-residual-scorer-and-next-ms-qsa.md`.

**Stop line (6 Sep night):** the human-\(U\) residual ridge is locked
(`outputs/experiments/full/BEST.md`). Do not restack features on the
216 ads. Next estimands are \(m(s)\) and \(q(s,a)\) (OPE on
`outputs/gold/bandit_rows.csv`, intent gate on WildChat, factored
creative term on same-timing pairs). See the context note.

| Step | File | State |
|---|---|---|
| Bronze → Silver | `build_policy_dataset.ipynb` / the two `.py` | done |
| QC | `validate_policy_dataset.py` | 17/17 when last run |
| Gold | `build_policy_gold.py` → `outputs/gold/` | done |
| Residual \(\widehat{m}_{\mathrm{ridge}}\) | `freeze_best.py`, `score_moment.py` | **locked** |
| Plan (old grid) | `TRAINING_PLAN.md`, `configs/` | P0–P4 mostly not what won |
| \(m(s)\) / \(q(s,a)\) | not started | next line |

Do not train on `outputs/rescued/labels_real_v2_logprob_0to9.csv`
(4B judge, saturated). GPU 0 is another user.
