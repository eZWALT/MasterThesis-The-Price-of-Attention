"""Declared association families for thesis Results 7.5 (tab:analysis-families,
rows behaviour × EEG, behaviour × trajectory, trajectory × EEG, three-way).

Estimates exactly the pairs Methods names, Holm within each declared family,
and reports both EEG estimands that Methods defines for a person-level D:

  D^A  Dataset A, condition aggregation (median of the k=37 tiles nearest
       visual onset), planned weights of eq:person-contrast.
  D^B  Dataset B, onset-locked post − pre, minus the same quantity on the
       timing-matched no-advertisement reply.

Any ad − no ad is the D of the primer ("whether advertisements shift it at
all"); it is the contrast used for the behaviour × EEG pairs. The trajectory
D's are the ones Methods declares: δ2^(a) (early pooled − no ad) and late
N_shift (late pooled − no ad); the behavioural and EEG sides of those pairs
take the same early-pooled / late-pooled weights.

Also written: specificity of the one Holm-surviving pair across all sixteen
EEG measures, the format and timing D pairs as sensitivity, the lab-only
triangle for the three-way row, and a timing split-half reliability for the
D^B any-ad EEG scores.

    python analysis/walter/combos/run_thesis_families.py
"""

from __future__ import annotations

import json
import math

import matplotlib
import numpy as np
import pandas as pd
import scipy.stats as st
from statsmodels.stats.multitest import multipletests

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import combokit as ck  # noqa: E402
from combokit import sk  # noqa: E402
from run_eeg_beh_three_engines import dataset_b_wide  # noqa: E402

OUT = ck.OUT / "thesis"
HOLM_ORANGE = "#C45C26"
HOLM_STAR_SIZE = 16
HOLM_LEGEND = "Holm p < .05"
COMPOSITES = ["trust", "credibility", "manipulation"]
EEG2 = ["eeg_fz_theta", "eeg_posterior_alpha"]
PRETTY_EEG = {
    "eeg_fz_theta": "Fz θ", "eeg_posterior_alpha": "posterior α", "eeg_theta": "θ", "eeg_alpha": "α",
    "eeg_beta": "β", "eeg_delta": "δ", "eeg_gamma": "γ", "eeg_faa": "FAA",
    "eeg_rel_delta": "relative δ", "eeg_rel_theta": "relative θ", "eeg_rel_alpha": "relative α",
    "eeg_rel_beta": "relative β", "eeg_rel_gamma": "relative γ",
    "eeg_engagement": "β/(α+θ)", "eeg_pope": "Pope β/(α+θ)", "eeg_kislov": "Kislov β/α",
}
W_EARLY = {"inline_early": 0.5, "block_early": 0.5, "no_ads": -1.0}
W_LATE = {"inline_late": 0.5, "block_late": 0.5, "no_ads": -1.0}


# --------------------------------------------------------------------------- #
# person-level scores
# --------------------------------------------------------------------------- #
def weighted(w: pd.DataFrame, weights: dict) -> pd.Series:
    return sum(w[c] * v for c, v in weights.items()).astype(float)


def behaviour_D(cond: pd.DataFrame, outcome: str, weights: dict) -> pd.Series:
    return weighted(sk.wide(cond, outcome), weights).rename(outcome)


def eeg_A(cond_lab: pd.DataFrame, eeg: str, weights: dict) -> pd.Series:
    """Dataset A person-level D on the k=37 condition-aggregation values."""
    return weighted(sk.wide(cond_lab, eeg), weights).rename(eeg)


def eeg_B_any(ad_w: pd.DataFrame, match_w: pd.DataFrame) -> pd.Series:
    ad = ad_w.reindex(columns=list(sk.AD_CONDITIONS)).mean(axis=1)
    return (ad - match_w[["early", "late"]].mean(axis=1)).rename("D_B")


def eeg_B_early(ad_w: pd.DataFrame, match_w: pd.DataFrame) -> pd.Series:
    return (ad_w[["inline_early", "block_early"]].mean(axis=1) - match_w["early"]).rename("D_B_early")


def eeg_B_halves(ad_w: pd.DataFrame, match_w: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    early = ad_w[["inline_early", "block_early"]].mean(axis=1) - match_w["early"]
    late = ad_w[["inline_late", "block_late"]].mean(axis=1) - match_w["late"]
    return early, late


def trajectory_D(genre_source: str = "utterance") -> pd.DataFrame:
    """δ2^(a) early pooled − no ad, and late N_shift pooled − no ad.
    `utterance` is the primary labelling (Definition 1); `contextual` is the
    deployed-window sensitivity."""
    cv = pd.read_csv(ck.REPO / "analysis/trajectories/outputs/conversations.csv")
    u = cv[cv.genre_source == genre_source].copy()
    parts = u.trajectory.str.split("|")
    u["delta2"] = parts.map(lambda s: int(s[2] != s[1]) if len(s) > 2 else np.nan)
    d2 = u.pivot_table(index="experiment_id", columns="condition", values="delta2", aggfunc="first")
    ns = u.pivot_table(index="experiment_id", columns="condition", values="n_shift", aggfunc="first")
    out = pd.DataFrame({
        "traj_delta2": weighted(d2, W_EARLY),
        "traj_nshift_late": weighted(ns, W_LATE),
    })
    out.attrs["delta2_early"] = float(u.loc[u.condition.isin(["inline_early", "block_early"]), "delta2"].mean())
    out.attrs["delta2_noad"] = float(u.loc[u.condition == "no_ads", "delta2"].mean())
    return out


# --------------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------------- #
def cell(x: pd.Series, y: pd.Series, **meta) -> dict:
    """Pair on experiment_id (Series index), then add Pearson / Kendall."""
    m = pd.concat([x, y], axis=1).dropna()
    a, b = m.iloc[:, 0], m.iloc[:, 1]
    rec = ck.spearman_ci(a, b)
    a, b = a.to_numpy(float), b.to_numpy(float)
    if len(a) >= 5:
        rec["pearson_r"], rec["pearson_p"] = map(float, st.pearsonr(a, b))
        rec["kendall_tau"], rec["kendall_p"] = map(float, st.kendalltau(a, b))
    rec.update(meta)
    return rec


def holm(df: pd.DataFrame, family_col: str = "family") -> pd.DataFrame:
    df = df.copy()
    df["p_holm"] = np.nan
    for _, idx in df.groupby(family_col).groups.items():
        df.loc[idx, "p_holm"] = multipletests(df.loc[idx, "p_raw"], method="holm")[1]
    df["k"] = df.groupby(family_col)["p_raw"].transform("count")
    df["sig_holm"] = df.p_holm < 0.05
    return df


def spearman_brown(r: float) -> float:
    return max(0.0, 2 * r / (1 + r)) if r > 0 else 0.0


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    cond = pd.read_csv(ck.GOLD / "condition_features.csv")
    cond_lab = ck.load_conditions_lab()
    Dlab = pd.read_csv(ck.GOLD / "combo_threeway_lab_D.csv").set_index("experiment_id")
    ad_w, match_w = dataset_b_wide()
    traj = trajectory_D()
    lab_ids = Dlab.index

    rows: list[dict] = []

    # ---- behaviour × EEG: six declared pairs, any ad − no ad, both estimands
    for eeg in ck.EEG:
        dA = Dlab[f"{eeg}__any_ad_vs_no_ads"]
        dB = eeg_B_any(ad_w[eeg], match_w[eeg]).reindex(lab_ids)
        for beh in ck.BEH_SURVEY:
            xb = Dlab[f"{beh}__any_ad_vs_no_ads"]
            declared = (beh in COMPOSITES) and (eeg in EEG2)
            for est, d in (("A", dA), ("B", dB)):
                fam = f"beh_eeg_declared_{est}" if declared else f"beh_eeg_sweep_{est}"
                rows.append(cell(xb, d, family=fam, block="beh_eeg", estimand=est, contrast="any_ad_vs_no_ads",
                                 beh=beh, eeg=eeg, declared=declared))
        # format and timing D pairs (sensitivity)
        for cid in ("inline_vs_block", "early_vs_late"):
            dA_c = Dlab[f"{eeg}__{cid}"]
            w = ad_w[eeg].reindex(columns=list(sk.AD_CONDITIONS)).dropna()
            dB_c = sk.contrast_scores(w, cid).reindex(lab_ids)
            for beh in COMPOSITES:
                if eeg not in EEG2:
                    continue
                xb = Dlab[f"{beh}__{cid}"]
                for est, d in (("A", dA_c), ("B", dB_c)):
                    rows.append(cell(xb, d, family=f"beh_eeg_sens_{cid}_{est}", block="beh_eeg_sens", estimand=est,
                                     contrast=cid, beh=beh, eeg=eeg, declared=False))

    # ---- behaviour × trajectory: six declared pairs, N = 54 and lab-only
    beh_early = {b: behaviour_D(cond, b, W_EARLY) for b in COMPOSITES}
    beh_late = {b: behaviour_D(cond, b, W_LATE) for b in COMPOSITES}
    for beh in COMPOSITES:
        for tname, bd in (("traj_delta2", beh_early[beh]), ("traj_nshift_late", beh_late[beh])):
            rows.append(cell(bd, traj[tname], family="beh_traj_declared", block="beh_traj", estimand="-",
                             contrast="early_pooled" if tname == "traj_delta2" else "late_pooled",
                             beh=beh, traj=tname, declared=True, arm="both"))
            # third side of the triangle on the same eighteen people; Methods names three
            # pairwise associations, so the δ2 side is the family and late N_shift is sensitivity
            rows.append(cell(bd.reindex(lab_ids), traj[tname].reindex(lab_ids),
                             family="threeway_beh_traj_lab" if tname == "traj_delta2" else "threeway_sens_nshift_lab",
                             block="threeway", estimand="-", contrast="early_pooled" if tname == "traj_delta2" else "late_pooled",
                             beh=beh, traj=tname, declared=(tname == "traj_delta2"), arm="lab"))

    # ---- contextual labelling as sensitivity for the six behaviour × trajectory pairs
    traj_ctx = trajectory_D("contextual")
    for beh in COMPOSITES:
        for tname, bd in (("traj_delta2", beh_early[beh]), ("traj_nshift_late", beh_late[beh])):
            rows.append(cell(bd, traj_ctx[tname], family="beh_traj_sens_contextual", block="beh_traj_sens", estimand="-",
                             contrast="early_pooled" if tname == "traj_delta2" else "late_pooled",
                             beh=beh, traj=tname, declared=False, arm="both"))

    # ---- trajectory × EEG: two declared pairs (early pooled D^A × δ2); D^B, whole-window
    #      EEG and the contextual labelling as sensitivity
    cf = pd.read_csv(ck.EEG_GOLD / "condition_features.csv")
    for eeg in EEG2:
        dA = eeg_A(cond_lab, eeg, W_EARLY)
        dB = eeg_B_early(ad_w[eeg], match_w[eeg])
        ww = cf.pivot_table(index="experiment_id", columns="condition", values=f"{ck.EEG_LONG[eeg]}_median", aggfunc="first")
        dWW = weighted(ww, W_EARLY)
        rows.append(cell(traj["traj_delta2"], dA, family="traj_eeg_declared_A", block="traj_eeg",
                         estimand="A", contrast="early_pooled", eeg=eeg, traj="traj_delta2", declared=True))
        rows.append(cell(traj["traj_delta2"], dB, family="traj_eeg_sens_B", block="traj_eeg_sens",
                         estimand="B", contrast="early_pooled", eeg=eeg, traj="traj_delta2", declared=False))
        rows.append(cell(traj["traj_delta2"], dWW, family="traj_eeg_sens_wholewindow", block="traj_eeg_sens",
                         estimand="A_ww", contrast="early_pooled", eeg=eeg, traj="traj_delta2", declared=False))
        rows.append(cell(traj_ctx["traj_delta2"], dA, family="traj_eeg_sens_contextual", block="traj_eeg_sens",
                         estimand="A", contrast="early_pooled", eeg=eeg, traj="traj_delta2", declared=False))

    T = holm(pd.DataFrame(rows))
    # pooled Holm over the twelve declared behaviour × EEG cells (both estimands)
    both = T.family.isin(["beh_eeg_declared_A", "beh_eeg_declared_B"])
    T["p_holm_12"] = np.nan
    T.loc[both, "p_holm_12"] = multipletests(T.loc[both, "p_raw"], method="holm")[1]
    # Holm over the sixteen EEG measures for trust, per estimand; and 3 composites × 16
    for est in ("A", "B"):
        m = (T.block == "beh_eeg") & (T.estimand == est) & (T.beh == "trust")
        T.loc[m, "p_holm_16"] = multipletests(T.loc[m, "p_raw"], method="holm")[1]
        m3 = (T.block == "beh_eeg") & (T.estimand == est) & (T.beh.isin(COMPOSITES))
        T.loc[m3, "p_holm_48"] = multipletests(T.loc[m3, "p_raw"], method="holm")[1]
        m8 = (T.block == "beh_eeg") & (T.estimand == est)
        T.loc[m8, "p_holm_128"] = multipletests(T.loc[m8, "p_raw"], method="holm")[1]
    T.to_csv(OUT / "declared_families.csv", index=False)

    # ---- three-way: partial of the surviving pair given the trajectory D's
    trust = Dlab["trust__any_ad_vs_no_ads"]
    alphaB = eeg_B_any(ad_w["eeg_posterior_alpha"], match_w["eeg_posterior_alpha"]).reindex(lab_ids)
    frame = pd.DataFrame({"trust": trust, "alphaB": alphaB,
                          "delta2": traj["traj_delta2"].reindex(lab_ids),
                          "nshift_late": traj["traj_nshift_late"].reindex(lab_ids),
                          "nshift_any": Dlab["traj_n_shift__any_ad_vs_no_ads"]})
    partials = {z: sk.partial_spearman(frame, "trust", "alphaB", z) for z in ("delta2", "nshift_late", "nshift_any")}
    # and the trajectory side of the triangle on the same 18: δ2 × trust, δ2 × alphaB
    tri = {
        "delta2_x_trust_anyad": ck.spearman_ci(frame.delta2, frame.trust),
        "delta2_x_alphaB_anyad": ck.spearman_ci(frame.delta2, frame.alphaB),
    }

    # ---- timing split-half reliability of the D^B any-ad EEG scores
    rel = {}
    for eeg in EEG2:
        e, l = eeg_B_halves(ad_w[eeg], match_w[eeg])
        r = float(st.spearmanr(*pd.concat([e, l], axis=1).dropna().to_numpy().T)[0])
        rel[eeg] = {"r_halves": r, "spearman_brown": spearman_brown(r), "n": int(pd.concat([e, l], axis=1).dropna().shape[0])}

    # ---- summary
    def pick(fam):
        sub = T[T.family == fam].sort_values("p_raw")
        cols = ["beh", "eeg", "traj", "contrast", "n", "rho", "ci_lo", "ci_hi", "p_raw", "p_holm", "k",
                "rho_loo_min", "rho_loo_max", "pearson_r", "kendall_tau", "p_holm_12", "p_holm_16", "p_holm_48", "p_holm_128"]
        cols = [c for c in cols if c in sub.columns]
        return sub[cols].round(4).to_dict(orient="records")

    hit = T[(T.family == "beh_eeg_declared_B") & (T.beh == "trust") & (T.eeg == "eeg_posterior_alpha")].iloc[0]
    same_A = T[(T.family == "beh_eeg_declared_A") & (T.beh == "trust") & (T.eeg == "eeg_posterior_alpha")].iloc[0]
    specB = T[(T.block == "beh_eeg") & (T.estimand == "B") & (T.beh == "trust")].sort_values("p_raw")
    summary = {
        "delta2_early_pooled": traj.attrs["delta2_early"], "delta2_no_ad": traj.attrs["delta2_noad"],
        "beh_eeg_declared_A": pick("beh_eeg_declared_A"),
        "beh_eeg_declared_B": pick("beh_eeg_declared_B"),
        "beh_eeg_declared_hits": {"A": int(T[T.family == "beh_eeg_declared_A"].sig_holm.sum()),
                                  "B": int(T[T.family == "beh_eeg_declared_B"].sig_holm.sum()),
                                  "pooled_12": int((T.loc[both, "p_holm_12"] < 0.05).sum())},
        "trust_posterior_alpha_B": {k: (float(hit[k]) if isinstance(hit[k], (float, int, np.floating)) else hit[k])
                                    for k in ("n", "rho", "ci_lo", "ci_hi", "p_raw", "p_holm", "p_holm_12", "p_holm_16",
                                              "p_holm_48", "p_holm_128", "rho_loo_min", "rho_loo_max", "pearson_r",
                                              "pearson_p", "kendall_tau", "kendall_p")},
        "trust_posterior_alpha_A": {k: float(same_A[k]) for k in ("rho", "ci_lo", "ci_hi", "p_raw", "p_holm")},
        "specificity_trust_B_16": specB[["eeg", "rho", "ci_lo", "ci_hi", "p_raw", "p_holm_16"]].round(4).to_dict(orient="records"),
        "specificity_trust_B_holm16_hits": specB.loc[specB.p_holm_16 < 0.05, "eeg"].tolist(),
        "beh_eeg_sens_format_timing": {f: int(T[T.family == f].sig_holm.sum()) for f in sorted(T.loc[T.block == "beh_eeg_sens", "family"].unique())},
        "beh_eeg_sens_min_raw": float(T.loc[T.block == "beh_eeg_sens", "p_raw"].min()),
        "beh_traj_declared": pick("beh_traj_declared"),
        "beh_traj_declared_hits": int(T[T.family == "beh_traj_declared"].sig_holm.sum()),
        "traj_eeg_declared_A": pick("traj_eeg_declared_A"),
        "traj_eeg_sens_B": pick("traj_eeg_sens_B"),
        "traj_eeg_sens_wholewindow": pick("traj_eeg_sens_wholewindow"),
        "traj_eeg_sens_contextual": pick("traj_eeg_sens_contextual"),
        "beh_traj_sens_contextual": pick("beh_traj_sens_contextual"),
        "traj_eeg_declared_hits": int(T[T.family == "traj_eeg_declared_A"].sig_holm.sum()),
        "delta2_D_levels_lab18": traj["traj_delta2"].reindex(lab_ids).value_counts().sort_index().to_dict(),
        "delta2_D_levels_all54": traj["traj_delta2"].value_counts().sort_index().to_dict(),
        "threeway_beh_traj_lab": pick("threeway_beh_traj_lab"),
        "threeway_sens_nshift_lab": pick("threeway_sens_nshift_lab"),
        "threeway_hits": int(T[T.family == "threeway_beh_traj_lab"].sig_holm.sum()),
        "threeway_partials_trust_alphaB": {k: {kk: float(vv) for kk, vv in v.items()} for k, v in partials.items()},
        "threeway_triangle_lab18": tri,
        "reliability_DB_anyad_timing_halves": rel,
        "n_tests_declared_total": int(T.declared.sum()),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=float) + "\n")

    make_figures(T, frame, summary)
    return summary


# --------------------------------------------------------------------------- #
# figures
# --------------------------------------------------------------------------- #
def _forest(ax, sub: pd.DataFrame, labels: list[str], y: np.ndarray, marker: str, color: str, fill: bool, label: str):
    ax.errorbar(sub.rho, y, xerr=[sub.rho - sub.ci_lo, sub.ci_hi - sub.rho], fmt=marker, color=color,
                mfc=color if fill else "white", mec=color, ms=5.5, capsize=2.5, lw=1.1, label=label)


def _holm_handle() -> Line2D:
    return Line2D(
        [0], [0], marker="*", color="none", markeredgecolor=HOLM_ORANGE,
        markerfacecolor=HOLM_ORANGE, markersize=14, linestyle="none", label=HOLM_LEGEND,
    )


def _is_holm(hit) -> bool:
    if pd.isna(hit):
        return False
    if isinstance(hit, str):
        return hit.strip().lower() in {"true", "1", "yes"}
    return bool(hit)


def _mark_holm(ax, y, hits, xmax: float, span: float) -> None:
    for yi, hit in zip(y, hits):
        if _is_holm(hit):
            ax.text(xmax + 0.06 * span, yi, "*", color=HOLM_ORANGE, fontsize=HOLM_STAR_SIZE,
                    ha="center", va="center", fontweight="bold")


def make_figures(T: pd.DataFrame, frame: pd.DataFrame, summary: dict) -> None:
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    cA, cB, cT, cE = "#D32F2F", "#1565C0", "#F9A825", "#6A1B9A"

    # ---- Figure 1: declared families
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 4.3), gridspec_kw={"width_ratios": [1.05, 1]})
    pairs = [(b, e) for e in EEG2 for b in COMPOSITES]
    lab = [f"{b} × {PRETTY_EEG[e]}" for b, e in pairs]
    yy = np.arange(len(pairs))[::-1].astype(float)
    subs = []
    # Same marker convention as panel (b) of combos_trust_alpha: B filled squares, A hollow circles.
    for est, col, mk, fill, off, name in (("A", cA, "o", False, 0.16, "Dataset A, condition aggregation"),
                                          ("B", cB, "s", True, -0.16, "Dataset B, onset-locked")):
        sub = pd.concat([T[(T.family == f"beh_eeg_declared_{est}") & (T.beh == b) & (T.eeg == e)] for b, e in pairs])
        _forest(ax1, sub, lab, yy + off, mk, col, fill, name)
        subs.append((sub, yy + off))
    hi = pd.concat([s["ci_hi"] for s, _ in subs]); lo = pd.concat([s["ci_lo"] for s, _ in subs])
    xmax = float(hi.max()); xmin = float(lo.min()); span = xmax - xmin
    for sub, yoff in subs:
        _mark_holm(ax1, yoff, sub.sig_holm.tolist(), xmax, span)
    ax1.axvline(0, color="k", lw=0.8)
    ax1.set_yticks(yy); ax1.set_yticklabels(lab)
    ax1.set_xlim(min(-1.0, xmin - 0.05 * span), xmax + 0.14 * span)
    ax1.set_xlabel("Spearman ρ, any ad − no ad, n = 18")
    ax1.set_title("(a) Behaviour × EEG: six declared pairs, two estimands", fontsize=9, loc="left")

    bt = T[T.family == "beh_traj_declared"]
    te = T[T.family == "traj_eeg_declared_A"]
    rows2, lab2 = [], []
    for tname, tl in (("traj_delta2", "δ₂⁽ᵃ⁾"), ("traj_nshift_late", "late N_shift")):
        for b in COMPOSITES:
            rows2.append(bt[(bt.beh == b) & (bt.traj == tname)].iloc[0]); lab2.append(f"{b} × {tl}")
    for e in EEG2:
        rows2.append(te[te.eeg == e].iloc[0]); lab2.append(f"{PRETTY_EEG[e]} × δ₂⁽ᵃ⁾")
    sub2 = pd.DataFrame(rows2)
    y2 = np.arange(len(sub2))[::-1].astype(float)
    _forest(ax2, sub2.iloc[:6], lab2[:6], y2[:6], "o", cT, True, "behaviour × trajectory, N = 54")
    _forest(ax2, sub2.iloc[6:], lab2[6:], y2[6:], "D", cE, True, "trajectory × EEG (Dataset A), n = 18")
    xmax2 = float(sub2.ci_hi.max()); xmin2 = float(sub2.ci_lo.min()); span2 = xmax2 - xmin2
    _mark_holm(ax2, y2, sub2.sig_holm.tolist(), xmax2, span2)
    ax2.axhline(1.5, color="0.8", lw=0.8, ls=":")
    ax2.axvline(0, color="k", lw=0.8)
    ax2.set_yticks(y2); ax2.set_yticklabels(lab2)
    ax2.set_xlim(min(-1.0, xmin2 - 0.05 * span2), xmax2 + 0.14 * span2)
    ax2.set_xlabel("Spearman ρ, same pooled contrast on both sides")
    ax2.set_title("(b) Trajectory pairs: six and two declared", fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(OUT / "combos_declared_forests.png", format="png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT / "combos_declared_forests.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)

    # ---- Figure 2: the surviving pair and its specificity
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 4.4), gridspec_kw={"width_ratios": [0.9, 1.1]})
    h = summary["trust_posterior_alpha_B"]
    ax1.axhline(0, color="0.75", lw=0.8); ax1.axvline(0, color="0.75", lw=0.8)
    ax1.scatter(frame.trust, frame.alphaB, s=34, color=cB, edgecolor="white", lw=0.6, zorder=3)
    ax1.set_xlabel("trust, any ad − no ad (Likert points)")
    ax1.set_ylabel("posterior α, onset-locked D (dB)")
    ax1.set_title("(a) Trust × posterior α, Dataset B, n = 18", fontsize=9, loc="left")
    ax1.text(0.02, 0.97, f"ρ = {h['rho']:.2f}  [{h['ci_lo']:.2f}, {h['ci_hi']:.2f}]\nHolm p = {h['p_holm']:.4f} (within six)\n"
             f"leave-one-out ρ {h['rho_loo_min']:.2f}–{h['rho_loo_max']:.2f}\nsame pair, Dataset A: ρ = {summary['trust_posterior_alpha_A']['rho']:.2f}",
             transform=ax1.transAxes, va="top", fontsize=8)

    sB = T[(T.block == "beh_eeg") & (T.estimand == "B") & (T.beh == "trust")].set_index("eeg")
    sA = T[(T.block == "beh_eeg") & (T.estimand == "A") & (T.beh == "trust")].set_index("eeg")
    order = sB.sort_values("rho").index.tolist()
    y3 = np.arange(len(order)).astype(float)
    sB, sA = sB.loc[order], sA.loc[order]
    _forest(ax2, sB, order, y3 + 0.15, "s", cB, True, "Dataset B, onset-locked")
    _forest(ax2, sA, order, y3 - 0.15, "o", cA, False, "Dataset A, condition aggregation")
    xmax3 = float(max(sB.ci_hi.max(), sA.ci_hi.max()))
    xmin3 = float(min(sB.ci_lo.min(), sA.ci_lo.min()))
    span3 = xmax3 - xmin3
    _mark_holm(ax2, y3 + 0.15, (sB.p_holm_16 < 0.05).tolist(), xmax3, span3)
    ax2.axvline(0, color="k", lw=0.8)
    ax2.set_yticks(y3); ax2.set_yticklabels([PRETTY_EEG[e] for e in order])
    ax2.set_xlim(min(-1.0, xmin3 - 0.05 * span3), xmax3 + 0.14 * span3)
    ax2.set_xlabel("Spearman ρ with trust, any ad − no ad, n = 18")
    ax2.set_title("(b) Trust against all sixteen EEG measures", fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(OUT / "combos_trust_alpha.png", format="png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT / "combos_trust_alpha.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)


def plot_from_frozen() -> None:
    """Re-plot the two thesis combo figures from declared_families.csv + Gold joins."""
    T = pd.read_csv(OUT / "declared_families.csv")
    summary = json.loads((OUT / "summary.json").read_text())
    Dlab = pd.read_csv(ck.GOLD / "combo_threeway_lab_D.csv").set_index("experiment_id")
    ad_w, match_w = dataset_b_wide()
    trust = Dlab["trust__any_ad_vs_no_ads"]
    alphaB = eeg_B_any(ad_w["eeg_posterior_alpha"], match_w["eeg_posterior_alpha"]).reindex(Dlab.index)
    frame = pd.DataFrame({"trust": trust, "alphaB": alphaB})
    make_figures(T, frame, summary)


if __name__ == "__main__":
    s = run()
    print(f"δ2 early pooled {s['delta2_early_pooled']:.3f}, no ad {s['delta2_no_ad']:.3f}")
    print("\n=== behaviour × EEG, six declared pairs ===")
    for est in ("A", "B"):
        print(f"-- Dataset {est}: Holm hits {s['beh_eeg_declared_hits'][est]}")
        for r in s[f"beh_eeg_declared_{est}"]:
            print(f"   {r['beh']:13s} {r['eeg']:20s} ρ={r['rho']:+.3f} [{r['ci_lo']:+.2f},{r['ci_hi']:+.2f}] raw={r['p_raw']:.4f} Holm-6={r['p_holm']:.4f} Holm-12={r['p_holm_12']:.4f}")
    h = s["trust_posterior_alpha_B"]
    print(f"\nHIT trust × posterior α (B): ρ={h['rho']:.3f} raw={h['p_raw']:.2e} Holm-6={h['p_holm']:.4f} Holm-12={h['p_holm_12']:.4f} "
          f"Holm-16={h['p_holm_16']:.4f} Holm-48={h['p_holm_48']:.4f} Holm-128={h['p_holm_128']:.4f} LOO {h['rho_loo_min']:.2f}–{h['rho_loo_max']:.2f} "
          f"Pearson {h['pearson_r']:.2f} Kendall {h['kendall_tau']:.2f}")
    print(f"same pair Dataset A: ρ={s['trust_posterior_alpha_A']['rho']:.3f} raw={s['trust_posterior_alpha_A']['p_raw']:.3f}")
    print("specificity Holm-16 hits (B, trust):", s["specificity_trust_B_holm16_hits"])
    for r in s["specificity_trust_B_16"]:
        print(f"   {r['eeg']:20s} ρ={r['rho']:+.3f} raw={r['p_raw']:.4f} Holm-16={r['p_holm_16']:.4f}")
    print("format/timing sensitivity Holm hits:", s["beh_eeg_sens_format_timing"], " min raw", round(s["beh_eeg_sens_min_raw"], 3))
    print("\n=== behaviour × trajectory, six declared (N=54) === hits", s["beh_traj_declared_hits"])
    for r in s["beh_traj_declared"]:
        print(f"   {r['beh']:13s} {r['traj']:17s} ρ={r['rho']:+.3f} [{r['ci_lo']:+.2f},{r['ci_hi']:+.2f}] raw={r['p_raw']:.3f} Holm-6={r['p_holm']:.3f}")
    print("\n=== trajectory × EEG, two declared (A) === hits", s["traj_eeg_declared_hits"])
    for r in s["traj_eeg_declared_A"]:
        print(f"   {r['eeg']:20s} ρ={r['rho']:+.3f} [{r['ci_lo']:+.2f},{r['ci_hi']:+.2f}] raw={r['p_raw']:.3f} Holm-2={r['p_holm']:.3f}")
    for key, lab in (("traj_eeg_sens_B", "Dataset B early"), ("traj_eeg_sens_wholewindow", "whole-window EEG"),
                     ("traj_eeg_sens_contextual", "contextual labelling")):
        print(f"   sensitivity, {lab}:")
        for r in s[key]:
            print(f"      {r['eeg']:20s} ρ={r['rho']:+.3f} [{r['ci_lo']:+.2f},{r['ci_hi']:+.2f}] raw={r['p_raw']:.3f}")
    print("   δ2 D levels, lab 18:", s["delta2_D_levels_lab18"], " all 54:", s["delta2_D_levels_all54"])
    print("   behaviour × trajectory, contextual labelling:")
    for r in s["beh_traj_sens_contextual"]:
        print(f"      {r['beh']:13s} {r['traj']:17s} ρ={r['rho']:+.3f} raw={r['p_raw']:.3f}")
    print("\n=== three-way === hits", s["threeway_hits"])
    for r in s["threeway_beh_traj_lab"]:
        print(f"   lab {r['beh']:13s} {r['traj']:17s} ρ={r['rho']:+.3f} [{r['ci_lo']:+.2f},{r['ci_hi']:+.2f}] raw={r['p_raw']:.3f} Holm-3={r['p_holm']:.3f}")
    for r in s["threeway_sens_nshift_lab"]:
        print(f"   lab sens {r['beh']:13s} {r['traj']:17s} ρ={r['rho']:+.3f} raw={r['p_raw']:.3f}")
    for z, v in s["threeway_partials_trust_alphaB"].items():
        print(f"   trust × posterior α (B) | {z:12s} partial ρ={v['rho_partial']:+.3f} p={v['p_raw']:.2e}")
    for k, v in s["threeway_triangle_lab18"].items():
        print(f"   {k}: ρ={v['rho']:+.3f} p={v['p_raw']:.3f}")
    print("\n=== timing split-half reliability, D^B any-ad ===")
    for e, v in s["reliability_DB_anyad_timing_halves"].items():
        print(f"   {e:20s} r_halves={v['r_halves']:+.3f} Spearman–Brown={v['spearman_brown']:.2f} n={v['n']}")
    print(f"\nWrote {OUT}")
