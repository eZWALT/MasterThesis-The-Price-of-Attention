"""Effects matrix: every estimated effect of the thesis in one visual grid.

WP6 of review loop 2 (11 Sep 2026). Reads only frozen outputs; never rebuilds.

Rows are outcomes grouped by family; columns are the three planned contrasts
(thesis coding: any ad - no ad, implicit - explicit, early - late) and the four
condition marginals against a^0 (implicit early, implicit late, explicit early,
explicit late). A cell is 1-3 triangles: direction = sign of the estimate in the
row's own units; count = |d_z| band (<.2, .2-.5, >.5) or |rho| band for
correlations (<.3, .3-.6, >.6); filled orange = Holm p < .05, hollow grey
otherwise; "." = not estimated in the thesis; "0" = estimate exactly zero.

Outputs
- analysis/walter/combos/outputs/thesis/effects_matrix.pdf (vector)
- docs/overleaf/thesis/figures/results/effects_matrix.pdf (copy)
- analysis/walter/combos/outputs/thesis/effects_matrix_cells.csv (provenance)

Run:  python analysis/walter/combos/make_effects_matrix.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
BEH = ROOT / "analysis/walter/behavioural/outputs/confirmatory"
EEG = ROOT / "analysis/eeg/statistics/outputs"
TRAJ = ROOT / "analysis/trajectories/outputs/stages_2_4/tables"
COMBOS = ROOT / "analysis/walter/combos/outputs/thesis"
OUT_DIR = COMBOS
FIG_COPY = ROOT / "docs/overleaf/thesis/figures/results/effects_matrix.pdf"

# Shared thesis palette (same CLAY orange as the unified Holm asterisk).
NAVY, CLAY, TEAL, SLATE, MIST, INK = "#1B3A4B", "#C45C26", "#2A6F6F", "#5C6B73", "#D5DDE3", "#12202A"

# ----------------------------------------------------------------------------
# Column and row definitions
# ----------------------------------------------------------------------------
COLUMNS = [
    ("any_ad", "Any ad $-$\nno ad"),
    ("imp_exp", "Implicit $-$\nexplicit"),
    ("early_late", "Early $-$\nlate"),
    ("IE", "Implicit\nearly"),
    ("IL", "Implicit\nlate"),
    ("EE", "Explicit\nearly"),
    ("EL", "Explicit\nlate"),
]
PLANNED = ("any_ad", "imp_exp", "early_late")
MARGINAL = ("IE", "IL", "EE", "EL")

# (group id, group label, [(row id, row label, effect type, exploratory flag)])
GROUPS = [
    ("beh", "Behavioural\n($N=54$)", [
        ("notice", "Notice", "dz", False),
        ("manipulation", "Perceived manipulation", "dz", False),
        ("credibility", "Credibility", "dz", False),
        ("trust", "Trust", "dz", False),
        ("recall_memory", "Cued memory", "dz", False),
        ("recall_trust_shift", "Trust on re-exposure", "dz", False),
    ]),
    ("eegA", "EEG, condition\naggregation\n($n=18$)", [
        ("A_fz_theta", r"Fz $\theta$", "dz", False),
        ("A_post_alpha", r"Posterior $\alpha$", "dz", False),
    ]),
    ("eegB", "EEG,\nonset-locked\n($n=18$)", [
        ("B_fz_theta", r"Fz $\theta$", "dz", False),
        ("B_post_alpha", r"Posterior $\alpha$", "dz", False),
        ("B_slow_tilt", r"Slow-power tilt (abs. $\delta$)$^{\dagger}$", "dz", True),
    ]),
    ("traj", "Trajectories\n($N=54$)", [
        ("delta2", r"$\delta^{(a)}_2$", "dz", False),
        ("nshift_late", r"Late $N_{\mathrm{shift}}$", "dz", False),
    ]),
    ("assoc", "Association\n($n=18$)", [
        ("rho_A", r"Trust $\times$ post. $\alpha$, cond. aggr.", "rho", False),
        ("rho_B", r"Trust $\times$ post. $\alpha$, onset-locked", "rho", False),
    ]),
]

# ----------------------------------------------------------------------------
# Thesis tables used as tie-breakers (rounded as printed). Only cells that the
# thesis prints as a number are listed; the script reports disagreements.
# ----------------------------------------------------------------------------
THESIS = {
    # (row, column): (estimate, effect size, Holm p or "<.001", "table")
    ("trust", "any_ad"): (-0.34, -0.25, 0.153, "tab:beh-planned"),
    ("trust", "imp_exp"): (0.15, 0.11, 0.405, "tab:beh-planned"),
    ("trust", "early_late"): (-0.44, -0.32, 0.063, "tab:beh-planned"),
    ("credibility", "any_ad"): (-0.14, -0.13, 0.673, "tab:beh-planned"),
    ("credibility", "imp_exp"): (-0.06, -0.10, 0.673, "tab:beh-planned"),
    ("credibility", "early_late"): (-0.33, -0.39, 0.017, "tab:beh-planned"),
    ("manipulation", "any_ad"): (1.27, 0.66, "<.001", "tab:beh-planned"),
    ("manipulation", "imp_exp"): (-0.62, -0.32, 0.022, "tab:beh-planned"),
    ("manipulation", "early_late"): (0.58, 0.41, 0.007, "tab:beh-planned"),
    ("notice", "any_ad"): (2.07, 1.01, "<.001", "tab:beh-planned"),
    ("notice", "imp_exp"): (-1.15, -0.55, "<.001", "tab:beh-planned"),
    ("notice", "early_late"): (0.26, 0.16, 0.234, "tab:beh-planned"),
    ("recall_memory", "imp_exp"): (-1.45, -0.93, "<.001", "tab:beh-planned"),
    ("recall_memory", "early_late"): (0.19, 0.10, 0.473, "tab:beh-planned"),
    ("recall_trust_shift", "imp_exp"): (0.12, 0.09, 0.525, "tab:beh-planned"),
    ("recall_trust_shift", "early_late"): (-0.49, -0.32, 0.047, "tab:beh-planned"),
    ("trust", "IE"): (-0.44, -0.24, 0.250, "tab:beh-localisation"),
    ("trust", "IL"): (-0.09, -0.05, 1.000, "tab:beh-localisation"),
    ("trust", "EE"): (-0.69, -0.38, 0.031, "tab:beh-localisation"),
    ("trust", "EL"): (-0.15, -0.08, 1.000, "tab:beh-localisation"),
    ("credibility", "IE"): (-0.35, -0.23, 0.411, "tab:beh-localisation"),
    ("credibility", "IL"): (0.01, 0.01, 1.000, "tab:beh-localisation"),
    ("credibility", "EE"): (-0.26, -0.21, 0.411, "tab:beh-localisation"),
    ("credibility", "EL"): (0.04, 0.04, 1.000, "tab:beh-localisation"),
    ("manipulation", "IE"): (1.20, 0.42, 0.006, "tab:beh-localisation"),
    ("manipulation", "IL"): (0.72, 0.29, 0.040, "tab:beh-localisation"),
    ("manipulation", "EE"): (1.92, 0.97, "<.001", "tab:beh-localisation"),
    ("manipulation", "EL"): (1.24, 0.53, "<.001", "tab:beh-localisation"),
    ("notice", "IE"): (1.60, 0.59, "<.001", "tab:beh-localisation"),
    ("notice", "IL"): (1.40, 0.52, "<.001", "tab:beh-localisation"),
    ("notice", "EE"): (2.81, 1.18, "<.001", "tab:beh-localisation"),
    ("notice", "EL"): (2.49, 0.99, "<.001", "tab:beh-localisation"),
    ("A_post_alpha", "early_late"): (-0.22, None, 0.0496, "sec:results-eeg text / tab:results-summary"),
    ("B_slow_tilt", "EE"): (None, None, None, "fig:eeg-holm-board text (five of six explicit early)"),
    ("delta2", "any_ad"): (0.046, 0.10, 0.94, "tab:traj-crossing"),
    ("delta2", "IE"): (0.093, 0.17, 0.91, "tab:traj-crossing"),
    ("delta2", "EE"): (0.000, 0.00, 1.00, "tab:traj-crossing"),
    ("delta2", "imp_exp"): (0.093, 0.16, 0.91, "tab:traj-crossing"),
    ("nshift_late", "any_ad"): (-0.074, -0.07, 1.00, "tab:traj-late"),
    ("nshift_late", "IL"): (-0.019, -0.02, 1.00, "tab:traj-late"),
    ("nshift_late", "EL"): (-0.130, -0.11, 1.00, "tab:traj-late"),
    ("rho_A", "any_ad"): (0.24, 0.24, 1.00, "sec:results-combos / tab:results-summary"),
    ("rho_B", "any_ad"): (0.80, 0.80, 0.0004, "sec:results-combos / tab:results-summary"),
}


# ----------------------------------------------------------------------------
# Cell construction
# ----------------------------------------------------------------------------
def band(value: float, kind: str) -> int:
    v = abs(value)
    if kind == "rho":
        return 1 if v < 0.3 else (2 if v <= 0.6 else 3)
    return 1 if v < 0.2 else (2 if v <= 0.5 else 3)


def cell(row, col, est, eff, p_holm, kind, src, key, cols, note="", exploratory=False, in_figure=True):
    if est is None:
        status = "not_estimated"
        sign, arrows, filled = "", 0, False
    elif est == 0:
        status = "zero"
        sign, arrows, filled = "0", 0, bool(p_holm is not None and p_holm < 0.05)
    else:
        status = "estimated"
        sign = "up" if est > 0 else "down"
        arrows = band(eff, kind)
        filled = bool(p_holm is not None and p_holm < 0.05)
    return dict(
        row=row, column=col, status=status, estimate=est, effect_size=eff, effect_type=kind,
        p_holm=p_holm, sign=sign, arrows=arrows, filled=filled, exploratory=exploratory,
        in_figure=in_figure, source_file=src, source_row=key, source_columns=cols, note=note,
    )


def not_estimated(row, col, why):
    return cell(row, col, None, None, None, "", "", "", "", note=why)


def build_cells() -> list[dict]:
    cells: list[dict] = []

    # --- Behavioural planned contrasts -------------------------------------
    planned = pd.read_csv(BEH / "confirmatory_planned_D.csv")
    src_p = "analysis/walter/behavioural/outputs/confirmatory/confirmatory_planned_D.csv"
    cmap = {"any_ad_vs_no_ads": "any_ad", "inline_vs_block": "imp_exp", "early_vs_late": "early_late"}
    for outcome in ("notice", "manipulation", "credibility", "trust", "recall_memory", "recall_trust_shift"):
        sub = planned[planned.outcome == outcome]
        for contrast, col in cmap.items():
            r = sub[sub.contrast == contrast]
            if r.empty:
                cells.append(not_estimated(outcome, col, "no a^0 cell for recall outcomes (tab:beh-planned)"))
                continue
            r = r.iloc[0]
            cells.append(cell(outcome, col, float(r["mean"]), float(r.dz), float(r.p_holm), "dz",
                              src_p, f"outcome={outcome},contrast={contrast}", "mean,dz,p_holm"))

    # --- Behavioural localisation (each condition - a^0) --------------------
    post = pd.read_csv(BEH / "posthoc_vs_control.csv")
    src_l = "analysis/walter/behavioural/outputs/confirmatory/posthoc_vs_control.csv"
    lmap = {"inline_early_vs_no_ads": "IE", "inline_late_vs_no_ads": "IL",
            "block_early_vs_no_ads": "EE", "block_late_vs_no_ads": "EL"}
    for outcome in ("notice", "manipulation", "credibility", "trust"):
        sub = post[post.outcome == outcome]
        for contrast, col in lmap.items():
            r = sub[sub.contrast == contrast].iloc[0]
            cells.append(cell(outcome, col, float(r["mean"]), float(r.dz), float(r.p_holm), "dz",
                              src_l, f"outcome={outcome},contrast={contrast}", "mean,dz,p_holm",
                              note="post hoc, Holm within outcome across four"))
    for outcome in ("recall_memory", "recall_trust_shift"):
        for col in MARGINAL:
            cells.append(not_estimated(outcome, col, "recall outcomes have no a^0 condition"))

    # --- EEG Dataset A (condition aggregation) ------------------------------
    eegA = pd.read_csv(EEG / "eeg_condition_contrasts.csv")
    src_a = "analysis/eeg/statistics/outputs/eeg_condition_contrasts.csv"
    feats = {"A_fz_theta": "fz_theta_power_db_uv2", "A_post_alpha": "posterior_alpha_power_db_uv2"}
    for row, feat in feats.items():
        sub = eegA[(eegA.feature == feat) & (eegA.contrast_tier == "primary")]
        for contrast, col in cmap.items():
            r = sub[sub.contrast_id == contrast].iloc[0]
            cells.append(cell(row, col, float(r.mean_difference), float(r.cohen_dz), float(r.p_t_holm), "dz",
                              src_a, f"feature={feat},contrast_id={contrast}",
                              "mean_difference,cohen_dz,p_t_holm"))
    # Marginals: post hoc pairwise sweep, Holm within measure (ten pairs).
    pairA = pd.read_csv(EEG / "posthoc/eeg_posthoc_pairwise_dataset_a.csv")
    src_pa = "analysis/eeg/statistics/outputs/posthoc/eeg_posthoc_pairwise_dataset_a.csv"
    pmap = {"inline_early__minus__no_ads": "IE", "inline_late__minus__no_ads": "IL",
            "block_early__minus__no_ads": "EE", "block_late__minus__no_ads": "EL"}
    for row, feat in feats.items():
        sub = pairA[(pairA.feature == feat) & (pairA.comparison_type == "ad_vs_no_ad")]
        for pair, col in pmap.items():
            r = sub[sub.pair_id == pair].iloc[0]
            cells.append(cell(row, col, float(r.mean_difference), float(r.cohen_dz), float(r.p_t_holm), "dz",
                              src_pa, f"feature={feat},pair_id={pair}", "mean_difference,cohen_dz,p_t_holm",
                              note="post hoc pairwise sweep (sec:app-eeg-posthoc), Holm within measure",
                              exploratory=True))

    # --- EEG Dataset B (onset-locked) ----------------------------------------
    eegB = pd.read_csv(EEG / "eeg_ad_response_contrasts.csv")
    src_b = "analysis/eeg/statistics/outputs/eeg_ad_response_contrasts.csv"
    bmap = {"inline_early_vs_no_ad_early": "IE", "inline_late_vs_no_ad_late": "IL",
            "block_early_vs_no_ad_early": "EE", "block_late_vs_no_ad_late": "EL"}
    featsB = {"B_fz_theta": "fz_theta_power_db_uv2", "B_post_alpha": "posterior_alpha_power_db_uv2",
              "B_slow_tilt": "delta_power_db_uv2"}
    for row, feat in featsB.items():
        sub = eegB[(eegB.feature == feat) & (eegB.contrast_tier == "primary")]
        for contrast, col in bmap.items():
            r = sub[sub.contrast_id == contrast].iloc[0]
            cells.append(cell(row, col, float(r.mean_difference), float(r.cohen_dz), float(r.p_t_holm), "dz",
                              src_b, f"feature={feat},contrast_id={contrast}",
                              "mean_difference,cohen_dz,p_t_holm",
                              note="exploratory measure; Holm within measure across four cells" if row == "B_slow_tilt" else "",
                              exploratory=(row == "B_slow_tilt")))
        for col in PLANNED:
            cells.append(not_estimated(row, col,
                                       "onset-locked planned contrasts are secondary_uncorrected in the CSV and not reported in the thesis"))
    # Companion measures of the tilt (not drawn; provenance only).
    for feat, label in (("delta_relative_power", "relative delta"), ("alpha_relative_power", "relative alpha"),
                        ("beta_relative_power", "relative beta"), ("theta_power_db_uv2", "global theta")):
        sub = eegB[(eegB.feature == feat) & (eegB.contrast_tier == "primary")]
        for contrast, col in bmap.items():
            r = sub[sub.contrast_id == contrast].iloc[0]
            cells.append(cell(f"B_tilt_companion:{label}", col, float(r.mean_difference), float(r.cohen_dz),
                              float(r.p_t_holm), "dz", src_b, f"feature={feat},contrast_id={contrast}",
                              "mean_difference,cohen_dz,p_t_holm", note="companion of the slow-power tilt row; not drawn",
                              exploratory=True, in_figure=False))

    # --- Trajectories ---------------------------------------------------------
    t1 = pd.read_csv(TRAJ / "t1_crossing_hard.csv").set_index("contrast")
    src_t1 = "analysis/trajectories/outputs/stages_2_4/tables/t1_crossing_hard.csv"
    t4 = pd.read_csv(TRAJ / "t4_negative_control.csv").set_index("contrast")
    src_t4 = "analysis/trajectories/outputs/stages_2_4/tables/t4_negative_control.csv"

    def traj(row, col, tab, src, key, note=""):
        r = tab.loc[key]
        return cell(row, col, float(r["mean"]), float(r.dz), float(r.p_holm), "dz", src, f"contrast={key}",
                    "mean,dz,p_holm", note=note)

    cells.append(traj("delta2", "any_ad", t1, src_t1, "early ads pooled - no ad", "early pooled - a^0"))
    cells.append(traj("delta2", "imp_exp", t1, src_t1, "implicit early - explicit early", "implicit early - explicit early"))
    cells.append(not_estimated("delta2", "early_late", "delta_2^(a) exists only for turn-2 advertisements"))
    cells.append(traj("delta2", "IE", t1, src_t1, "implicit early - no ad"))
    cells.append(traj("delta2", "EE", t1, src_t1, "explicit early - no ad"))
    for col in ("IL", "EL"):
        cells.append(not_estimated("delta2", col, "a late advertisement has no following utterance"))

    cells.append(traj("nshift_late", "any_ad", t4, src_t4, "late ads pooled - no ad", "late pooled - a^0"))
    cells.append(not_estimated("nshift_late", "imp_exp", "not in the declared late family (tab:traj-late)"))
    cells.append(not_estimated("nshift_late", "early_late", "not in the declared late family (tab:traj-late)"))
    cells.append(traj("nshift_late", "IL", t4, src_t4, "implicit late - no ad"))
    cells.append(traj("nshift_late", "EL", t4, src_t4, "explicit late - no ad"))
    for col in ("IE", "EE"):
        cells.append(not_estimated("nshift_late", col, "late N_shift family compares late conditions only"))

    # --- Associations ----------------------------------------------------------
    fam = pd.read_csv(COMBOS / "declared_families.csv")
    src_f = "analysis/walter/combos/outputs/thesis/declared_families.csv"
    for row, est in (("rho_A", "A"), ("rho_B", "B")):
        sel = fam[(fam.block == "beh_eeg") & (fam.estimand == est) & (fam.contrast == "any_ad_vs_no_ads")
                  & (fam.beh == "trust") & (fam.eeg == "eeg_posterior_alpha") & (fam.declared == True)]  # noqa: E712
        r = sel.iloc[0]
        cells.append(cell(row, "any_ad", float(r.rho), float(r.rho), float(r.p_holm), "rho", src_f,
                          f"family={r.family},contrast=any_ad_vs_no_ads,beh=trust,eeg=eeg_posterior_alpha",
                          "rho,p_holm", note="declared family, Holm within six"))
        for contrast, col in (("inline_vs_block", "imp_exp"), ("early_vs_late", "early_late")):
            sel = fam[(fam.block == "beh_eeg_sens") & (fam.estimand == est) & (fam.contrast == contrast)
                      & (fam.beh == "trust") & (fam.eeg == "eeg_posterior_alpha")]
            r = sel.iloc[0]
            cells.append(cell(row, col, float(r.rho), float(r.rho), float(r.p_holm), "rho", src_f,
                              f"family={r.family},contrast={contrast},beh=trust,eeg=eeg_posterior_alpha",
                              "rho,p_holm", note="sensitivity pairs (tab:results-checks: 24 tests, 0 Holm)",
                              exploratory=True))
        for col in MARGINAL:
            cells.append(not_estimated(row, col, "associations are on the any ad - no ad person score only"))
    return cells


# ----------------------------------------------------------------------------
# Thesis cross-check
# ----------------------------------------------------------------------------
def check_against_thesis(cells: list[dict]) -> list[str]:
    idx = {(c["row"], c["column"]): c for c in cells if c["in_figure"]}
    issues: list[str] = []
    for key, (est, eff, p, table) in THESIS.items():
        c = idx[key]
        if est is not None and abs(round(c["estimate"], 2) - est) > 0.0051 and abs(round(c["estimate"], 3) - est) > 0.0011:
            issues.append(f"{key}: estimate CSV {c['estimate']:.3f} vs {table} {est}")
        if eff is not None and abs(round(c["effect_size"], 2) - eff) > 0.0051:
            issues.append(f"{key}: effect size CSV {c['effect_size']:.3f} vs {table} {eff}")
        if p == "<.001":
            if not c["p_holm"] < 0.001:
                issues.append(f"{key}: Holm p CSV {c['p_holm']:.4f} vs {table} <.001")
        elif p is not None and abs(c["p_holm"] - p) > 0.0015 and abs(round(c["p_holm"], 2) - p) > 0.0051:
            issues.append(f"{key}: Holm p CSV {c['p_holm']:.4f} vs {table} {p}")
    return issues


# ----------------------------------------------------------------------------
# Drawing
# ----------------------------------------------------------------------------
def draw(cells: list[dict], out_pdf: Path) -> None:
    idx = {(c["row"], c["column"]): c for c in cells if c["in_figure"]}
    rows: list[tuple[str, str, str, float]] = []  # row id, label, group id, y
    group_span: dict[str, tuple[float, float, str]] = {}
    y = 0.0
    gap = 0.55
    for gi, (gid, glabel, members) in enumerate(GROUPS):
        if gi:
            y += gap
        y0 = y
        for rid, rlabel, _kind, _expl in members:
            rows.append((rid, rlabel, gid, y))
            y += 1.0
        group_span[gid] = (y0 - 0.5, y - 0.5, glabel)
    n_rows_y = y - 0.5

    fig_w_in = 6.3
    fig_h_in = 0.33 * len(rows) + gap * (len(GROUPS) - 1) * 0.33 + 2.0
    fig, ax = plt.subplots(figsize=(fig_w_in, fig_h_in))
    fig.subplots_adjust(left=0.34, right=0.985, top=0.885, bottom=0.185)
    ax.set_xlim(-0.5, len(COLUMNS) - 0.5)
    ax.set_ylim(n_rows_y, -0.5)
    ax.axis("off")

    fs_cell = 8.0
    fs_lab = 8.0
    fs_small = 6.6
    ms = 4.6  # triangle marker size (points)
    dx = 0.19

    # Column headers (two tiers).
    for j, (_cid, clabel) in enumerate(COLUMNS):
        ax.text(j, -0.62, clabel, ha="center", va="bottom", fontsize=fs_lab, color=INK, linespacing=1.05)
    trans = ax.get_xaxis_transform()
    ax.plot([-0.45, 2.45], [1.075, 1.075], transform=trans, color=SLATE, lw=0.8, clip_on=False)
    ax.plot([2.55, 6.45], [1.075, 1.075], transform=trans, color=SLATE, lw=0.8, clip_on=False)
    ax.text(1.0, 1.09, "Planned contrasts", transform=trans, ha="center", va="bottom", fontsize=fs_lab,
            color=INK, style="italic")
    ax.text(4.5, 1.09, r"Condition $-$ $a^{\emptyset}$", transform=trans, ha="center", va="bottom", fontsize=fs_lab,
            color=INK, style="italic")

    # Vertical divider between planned and marginal columns.
    ax.plot([2.5, 2.5], [-0.5, n_rows_y], color=MIST, lw=1.0, zorder=0)

    # Row labels, group labels, separators, light row banding.
    for i, (rid, rlabel, gid, yy) in enumerate(rows):
        if i % 2 == 0:
            ax.axhspan(yy - 0.5, yy + 0.5, xmin=0, xmax=1, color="#F4F6F8", zorder=-1)
        ax.text(-0.62, yy, rlabel, ha="right", va="center", fontsize=fs_lab, color=INK)
    # Group labels sit in a gutter at the far left: x in figure fraction, y in data units.
    gutter = blended_transform_factory(fig.transFigure, ax.transData)
    for gi, (gid, glabel, _m) in enumerate(GROUPS):
        y0, y1, _ = group_span[gid]
        if gi:
            ysep = y0 - gap / 2
            ax.plot([-0.5, len(COLUMNS) - 0.5], [ysep, ysep], color=SLATE, lw=0.6, zorder=0)
        ax.text(0.012, (y0 + y1) / 2, glabel, transform=gutter, ha="left", va="center", fontsize=fs_small,
                color=NAVY, style="italic", linespacing=1.05, clip_on=False)

    # Cells.
    for rid, _rlabel, _gid, yy in rows:
        for j, (cid, _cl) in enumerate(COLUMNS):
            c = idx[(rid, cid)]
            if c["status"] == "not_estimated":
                ax.text(j, yy, "\u00b7", ha="center", va="center", fontsize=fs_cell + 3, color=SLATE)
                continue
            if c["status"] == "zero":
                ax.text(j, yy, "0", ha="center", va="center", fontsize=fs_cell, color=SLATE)
                continue
            marker = "^" if c["sign"] == "up" else "v"
            n = c["arrows"]
            xs = [j + (k - (n - 1) / 2) * dx for k in range(n)]
            if c["filled"]:
                mfc, mec = CLAY, CLAY
            else:
                mfc, mec = "white", SLATE
            ax.plot(xs, [yy] * n, linestyle="none", marker=marker, ms=ms, mfc=mfc, mec=mec, mew=1.0, zorder=3)

    # Legend.
    def tri(marker, filled):
        return Line2D([], [], linestyle="none", marker=marker, ms=ms, mfc=CLAY if filled else "white",
                      mec=CLAY if filled else SLATE, mew=1.0)

    handles = [tri("^", True), tri("^", False), tri("v", False),
               Line2D([], [], linestyle="none", marker=".", ms=4, color=SLATE)]
    labels = ["Holm $p<.05$", "Holm $p\\geq.05$", "estimate below zero", "not estimated"]
    leg = fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.012, 0.165), ncol=4, fontsize=fs_small,
                     frameon=False, handletextpad=0.4, columnspacing=1.4, borderaxespad=0.0)
    leg.set_zorder(5)
    notes = (
        r"Triangle direction is the sign of the estimate in the row's own units (higher trust $\blacktriangle$, higher manipulation $\blacktriangle$)."
        "\n"
        r"Triangle count 1 / 2 / 3: $|d_z|<.2$ / $.2$–$.5$ / $>.5$; association rows $|\rho|<.3$ / $.3$–$.6$ / $>.6$ ($\blacktriangle$ = positive $\rho$). 0: estimate exactly zero."
        "\n"
        r"Trajectory any-ad cells are early pooled ($\delta^{(a)}_2$) or late pooled ($N_{\mathrm{shift}}$) minus $a^{\emptyset}$; "
        r"condition-aggregation marginals are the post hoc pairwise sweep."
        "\n"
        r"$^{\dagger}$Exploratory measure. Absolute $\delta$ is shown; relative $\alpha$ and $\beta$ fall in the same explicit-early cell (Holm $.026$, $.018$)."
    )
    fig.text(0.012, 0.125, notes, ha="left", va="top", fontsize=fs_small - 0.4, color=INK, linespacing=1.4)

    fig.savefig(out_pdf, format="pdf")
    plt.close(fig)


# ----------------------------------------------------------------------------
def main() -> None:
    cells = build_cells()
    issues = check_against_thesis(cells)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(cells)
    order = {r: i for i, r in enumerate([m[0] for g in GROUPS for m in g[2]])}
    col_order = {c[0]: i for i, c in enumerate(COLUMNS)}
    df["_r"] = df.row.map(lambda r: order.get(r, 99))
    df["_c"] = df.column.map(col_order)
    df = df.sort_values(["_r", "row", "_c"]).drop(columns=["_r", "_c"])
    df.to_csv(OUT_DIR / "effects_matrix_cells.csv", index=False)

    out_pdf = OUT_DIR / "effects_matrix.pdf"
    draw(cells, out_pdf)
    FIG_COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out_pdf, FIG_COPY)

    print(f"wrote {out_pdf}")
    print(f"copied to {FIG_COPY}")
    print(f"wrote {OUT_DIR / 'effects_matrix_cells.csv'} ({len(df)} rows, {int(df.in_figure.sum())} drawn)")
    if issues:
        print("THESIS DISAGREEMENTS:")
        for s in issues:
            print("  -", s)
    else:
        print("thesis cross-check: all listed cells agree at printed precision")


if __name__ == "__main__":
    main()
