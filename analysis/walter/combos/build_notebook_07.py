"""Write 07_combos_reduced.ipynb, the thin viewer for blocks 0-7.
Run once after the block scripts; the notebook only reads outputs.

    python analysis/walter/combos/build_notebook_07.py
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

SETUP = r'''from pathlib import Path
import json, sys, warnings
warnings.filterwarnings("ignore")
import pandas as pd
from IPython.display import Image, display, Markdown

HERE = Path.cwd().resolve()
while not (HERE / "analysis" / "walter" / "statkit.py").exists():
    HERE = HERE.parent
OUT = HERE / "analysis" / "walter" / "combos" / "outputs"
pd.set_option("display.max_columns", 60); pd.set_option("display.width", 200); pd.set_option("display.max_rows", 200)
def show(p, w=1100):
    display(Image(filename=str(OUT / p), width=w))
def js(p):
    return json.loads((OUT / p).read_text())
'''

CELLS: list[tuple[str, str]] = [
    ("markdown", r"""# 07 — Combos, reduced: reliability, nine headline tests, mixed models, turn and event grains

The 2,560-cell map (notebooks 03–06) is Holm/BH-null everywhere. This notebook asks the questions that map cannot: **how reliable are the person-level scores being correlated** (block 0), **what does one score per modality say** (block 1), **what do the a-priori cells look like with intervals** (block 2), **does EEG state moderate the behavioural effect within person** (block 3), **does genre movement relate to process at the turn grain** (block 4), **does the onset-locked EEG response to an ad predict recall, genre shift or the next turn** (block 5), **do the modalities order the five conditions alike** (block 6), and **does the one EEG quantity that works here (write − read Fz \(\theta\)) predict the behavioural ad effect as a trait** (block 7).

Person is the inferential unit throughout. Every family is Holm-corrected within itself, BH across its table, and the model families carry a Freedman–Lane max-\(|t|\) permutation with persons as exchangeability blocks. Scripts: `run_reliability.py`, `run_headline.py`, `run_forest.py`, `run_lmm.py`, `run_turns.py`, `run_events.py`, `run_concordance.py`, `run_task_state.py`, `summarise_blocks.py`.

**Result in one line: 336 new tests, 0 Holm, 0 BH (within table and pooled over the 336, and pooled with the 2,560-cell map), 10 raw hits where 17 are expected under the null; every family-wise permutation \(p > .23\).** The informative output is block 0: the Fz \(\theta\) \(D_i\) at \(k=37\) have no *detectable* between-person reliability (point estimates 0.00–0.01, 18-person upper bounds ≈ .64; .35–.61 with all ~95 tiles), the trajectory \(D_i\) barely agree across the two genre classifiers, and at \(n=18\) a Spearman needs \(|\rho| > .47\) to reach raw .05."""),
    ("code", SETUP),
    ("markdown", r"""## Ledger"""),
    ("code", r'''L = pd.read_csv(OUT / "blocks_ledger.csv")
display(L.drop(columns="source").round(4))
S = js("blocks_summary.json")
display(Markdown(f"**Map:** {S['map_tests']} tests. **Blocks 1–7:** {S['new_tests_blocks_1_7']} tests, {S['new_hits_raw']} raw hits (expected {S['expected_raw_hits_under_null']:.1f}), {S['new_hits_holm']} Holm, {S['new_hits_bh_within_table']} BH within table, {S['new_hits_bh_pooled']} BH pooled over {S['n_pooled_new']}, {S['all_hits_bh_pooled_blocks_plus_map']} BH pooled over {S['n_pooled_all']} (blocks + map)."))
display(pd.Series(S["familywise_permutation_p"], name="Freedman-Lane family-wise p").round(3))'''),
    ("markdown", r"""## Block 0 — what is being correlated, and how reliable it is

Split-half over the 37 tiles of each Dataset A \(k=37\) cell (random halves, 200 draws, Spearman–Brown = upper bound; first vs second half = lower bound, confounded with drift). Reliability of a \(D_i\) is the corrected correlation of the two half-\(D\)'s across the 18 people. Behavioural composite \(D_i\): Cronbach \(\alpha\) of the item-level \(D\)'s. Trajectory: agreement of \(D_i\) between the utterance and contextual genre classifiers (no Spearman–Brown; parallel forms, not halves)."""),
    ("code", r'''show("reliability/reliability.png", 1200)
R = js("reliability/summary.json")
display(Markdown(f"Median within-person reliability of an EEG condition feature: random halves **{R['eeg_feature_rel_within_SB_median']['random']:.2f}**, first/second **{R['eeg_feature_rel_within_SB_median']['first_second']:.2f}**. Median \(D_i\) reliability: **{R['eeg_D_rel_median']['random']:.2f}** / **{R['eeg_D_rel_median']['first_second']:.2f}**."))
d = pd.read_csv(OUT / "reliability/eeg_D_reliability.csv")
display(d[d.scheme == "random"].pivot(index="feature", columns="contrast", values="rel_D_SB").round(2))
display(d[d.feature.isin(["eeg_fz_theta", "eeg_posterior_alpha"]) & d.scheme.isin(["random", "random_all_tiles"])][["scheme", "feature", "contrast", "r_halves", "r_halves_ci_lo", "r_halves_ci_hi", "rel_D_SB", "rel_D_SB_ci_hi"]].round(2))'''),
    ("markdown", r"""Fz \(\theta\) — the primary feature — is the least reliable condition feature at \(k=37\) (0.26; 0.46 with all tiles) and its any-ad and format \(D_i\) have no *detectable* true variance (point estimates 0.01, 0.00; the 18-person sampling interval puts the Spearman–Brown upper bound at ≈ .64). With every retained tile (~95, the whole-window Gold aggregation) those rise to .45 and .35: \(k=37\) costs reliability on the single-channel feature. Posterior \(\alpha\) any-ad \(D\) is 0.78 (0.82 whole-window). The post-hoc Dataset A cell (implicit-early − explicit-late Fz \(\theta\)) has pair-\(D\) reliability 0 at \(k=37\) under every split (upper bound .52) and .47 whole-window: a mean shift with little detectable between-person heterogeneity."""),
    ("code", r'''display(pd.read_csv(OUT / "reliability/trajectory_D_source_agreement.csv").round(2))
display(pd.read_csv(OUT / "reliability/behavioural_D_alpha.csv").pivot(index="composite", columns="contrast", values="alpha").round(2))
show("reliability/resolution.png", 700)
display(pd.read_csv(OUT / "reliability/attenuation_ceiling_headline.csv").round(2))'''),
    ("markdown", r"""The attenuation table is the punchline, read at its most favourable column (`max_observable_rho_best`, which is the whole-window reliability for every Fz \(\theta\) cell): for Fz \(\theta\) any-ad or format the largest *observable* Spearman with a behavioural composite is 0.34–0.61 (0.00–0.27 with the \(k=37\) reliabilities), so a raw-.05 hit at \(n=18\) needed a **true** \(\rho \ge 0.77\) and a Holm-within-16 hit needed a true \(\rho > 1\), i.e. was unreachable. Posterior \(\alpha\) any-ad is the best-placed pair: raw .05 needs a true \(\rho \ge 0.57\)–0.72, Holm-16 \(\ge 0.80\).

## Block 1 — one score per modality per contrast (9 tests)

PC1 of the z-scored \(D_i\) block per modality (behaviour: 8 survey composites → a negative-evaluation factor; trajectory: 10 metrics → a movement factor; EEG: 16 features → the slow-vs-fast spectral tilt). Behaviour × trajectory \(n=54\); anything with EEG \(n=18\)."""),
    ("code", r'''show("headline/pc1_loadings.png", 1200)
show("headline/headline_scatter.png", 1000)
H = pd.read_csv(OUT / "headline/headline_tests.csv")
cols = ["family", "contrast", "left", "right", "arm", "n", "rho", "ci_lo", "ci_hi", "p_raw", "p_holm_family", "rho_loo_min", "rho_loo_max"]
display(H[H.family == "headline_PC1"][cols].round(3))
display(H[H.family == "process_PC1"][cols].round(3))
display(H[H.family == "planned_primaries"][cols].round(3))
display(H[H.family.str.startswith("sensitivity")][cols].round(3))
display(Markdown(r"Whole-window EEG (all ~95 tiles) in place of \(k=37\): 21 tests, min raw \(p=.03\), 0 Holm. Its PC1 agrees with the \(k=37\) PC1 only for any-ad (.85), not for format or timing (−.38, −.55): PC1 of sixteen \(D\)'s from 18 people is not a stable axis when the \(D\)'s are small."))
display(pd.read_csv(OUT / "headline/pc1_variance.csv").round(3))
display(Markdown(r"Leave-one-person-out refits (`pc1_loo_*`): behaviour, trajectory and process PC1 reproduce the full fit at \(\ge .99\) whichever person is dropped. The EEG PC1 does not: minimum score agreement .82 / .99 / .83 and minimum loading cosine .84 / .95 / .67 for any-ad / format / timing at \(k=37\), and .61 / .68 for the whole-window format axis. The EEG 'tilt' score at the timing contrast hinges on single people."))'''),
    ("markdown", r"""Nothing survives. The two closest cells are behaviour × trajectory any-ad (\(\rho=.25\), \(n=54\), \(p=.06\); people whose evaluation worsened with ads moved genre a little more) and trajectory × EEG early−late (\(\rho=-.45\), \(n=18\), \(p=.06\)). Process PC1 × EEG PC1 at the format contrast is \(\rho=.40\) (\(p=.10\)), the same direction as the raw process × engagement cluster in the old map.

## Block 2 — the a-priori cells with their intervals"""),
    ("code", r'''show("forest/forest_headline.png", 1300)
show("forest/forest_top12.png", 1100)
display(pd.read_csv(OUT / "forest/cluster_process_x_engagement_format.csv")[["left", "right", "n", "effect", "p_raw", "p_holm_family", "p_bh_global"]].round(3))'''),
    ("markdown", r"""Every a-priori interval crosses zero. The twelve smallest raw \(p\) of the 2,560 have Holm \(\ge .32\) and BH \(.90\). The one coherent raw cluster — all 21 process × fast-band cells at the format contrast are negative (\(\rho\) −0.15 to −0.69) — is not 21 independent replications (the variables within it are correlated) and is exploratory.

## Block 3 — mixed models: EEG state → outcome, and EEG × timing/format

Laboratory 90 rows (Model A, adjusted for condition and order), 72 ad rows (B0 main effect; B two interactions). EEG within-person centred; person random intercept. Freedman–Lane max-\(|t|\) permutation per family."""),
    ("code", r'''show("lmm/lmm_forest.png", 1300)
M = js("lmm/summary.json")
display(pd.DataFrame(M["permutation_maxT"]).T.round(3))
display(pd.DataFrame(M["top"]).round(4))'''),
    ("markdown", r"""## Block 4 — turn grain: genre movement × process, and the post-ad turn

1,080 user turns, person + conversation effects, `task_genre` covariate (task assignment is randomised, not counterbalanced). Early ads appear in reply 2, so turns 3–4 are the only post-ad user turns; late ads have none."""),
    ("code", r'''show("turns/turn_profiles.png", 1200)
show("turns/turn_forest.png", 1000)
display(pd.read_csv(OUT / "turns/turn_descriptives.csv").round(3))'''),
    ("markdown", r"""A turn that changes genre is not measurably shorter, longer or slower. The post-ad turn is between −16 % and +18 % in length and between −5 % and +21 % in latency of a turn at the same position with no ad on screen (95 % CI); its shift log-odds are +0.31 [−0.32, 0.94], and its probability mass on purchasable products does not move.

## Block 5 — event grain: the onset-locked EEG response to *this* ad → what happened next

72 primary-eligible ads (Dataset B post − pre), person random intercept, EEG within-person centred. Targets: cued recall (memory, trust shift), the chat's notice / manipulation / trust, Definition 6 shift and divergence (36 early ads), the next user turn's length and latency (36)."""),
    ("code", r'''show("events/event_forest.png", 1000)
show("events/event_heat.png", 1000)
E = js("events/summary.json")
display(pd.DataFrame({"headline": E["permutation_headline"], "all": E["permutation_all_exploratory"]}).round(3))
display(pd.DataFrame(E["top"]).round(4))
display(pd.Series(E["wald_vs_permutation"]))
T = pd.read_csv(OUT / "events/event_tests.csv")
display(T[T.target == "ad_associated_shift"][["eeg", "beta", "se", "p_raw", "gee_beta_logodds", "gee_p_asymptotic", "n_events", "n_nonevents"]].round(3))'''),
    ("markdown", r"""The best a-priori cell is ad-locked Fz \(\theta\) → notice (0.68 Likert per within-person SD, raw .005, Holm .14, sign stable under leave-one-person-out); the family-wise permutation \(p\) is .23. **Methods warning kept on purpose:** the binary target is 33 shifts / 3 non-shifts, so only three people are informative. A GEE binomial fit returned \(\gamma\) \(p=.0003\) and \(\beta\) \(p=.002\) there; the person-fixed-effects Freedman–Lane permutation gives .80 and .93. The GEE numbers are in the table as a record of why they were not used.

## Block 6 — do the modalities order the conditions alike? (descriptive)"""),
    ("code", r'''show("concordance/condition_profiles.png", 1300)
show("concordance/kendall_tau_profiles.png", 700)'''),
    ("markdown", r"""## Block 7 — write − read EEG trait × behavioural / trajectory ad effects (\(n=18\))"""),
    ("code", r'''show("task_state/task_state_forest.png", 900)
K = js("task_state/summary.json")
display(pd.DataFrame(K["top"]).round(3))'''),
    ("markdown", r"""Nothing after Holm (44 tests). The closest is write−read Fz \(\theta\) × notice early−late \(D\) (\(\rho=.65\), raw .003, Holm .11).

## What this adds to the thesis

1. **A precise, documented cross-modal null with the reasons.** Not "no relation", but: the person-level EEG contrast scores for the primary feature carry no reliable between-person variance; trajectory scores barely agree across classifiers; and \(n=18\) cannot resolve \(|\rho| < .47\). The combos were not powered to find what they looked for, and block 0 says so with numbers rather than an MDE sermon.
2. **The one surviving Dataset A cell is mostly a mean shift** (pair-\(D\) reliability 0 at \(k=37\), upper bound .52; .47 whole-window), consistent with the "tenths of a dB" Dataset A reading; an individual-differences story for it has little to stand on.
3. **Turn- and event-grain nulls** on process and genre movement after an ad, with tight intervals at the turn grain.
4. **A methods note**: GEE with 3 non-events produced two "significant" cells that a within-person permutation dismisses; none of it enters Results."""),
]


def main() -> None:
    cells = []
    for kind, src in CELLS:
        cell = {"cell_type": kind, "metadata": {}, "source": src.splitlines(keepends=True)}
        if kind == "code":
            cell.update({"execution_count": None, "outputs": []})
        cells.append(cell)
    nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                       "language_info": {"name": "python", "version": "3.13.12"}}, "nbformat": 4, "nbformat_minor": 5}
    (HERE / "07_combos_reduced.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote 07_combos_reduced.ipynb")


if __name__ == "__main__":
    main()
