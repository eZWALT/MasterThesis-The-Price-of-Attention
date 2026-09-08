"""Figures for Walter's behavioural / combo notebooks.

Every function takes Gold tables (or the long test tables) and returns a
matplotlib Figure. Notebooks call them inline; scripts can save them.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

import statkit as sk

COND = list(sk.CONDITIONS)
LAB = [sk.LABEL[c] for c in COND]
ARM_COLOR = {"lab": "tab:blue", "crowd": "tab:orange"}
LIKERT_CMAP = plt.get_cmap("RdYlGn")


def _wide(c: pd.DataFrame, outcome: str) -> pd.DataFrame:
    w = c.pivot_table(index="experiment_id", columns="condition", values=outcome, aggfunc="first")[COND]
    arm = c.drop_duplicates("experiment_id").set_index("experiment_id")["arm"]
    w["arm"] = arm.reindex(w.index)
    return w


# ----------------------------------------------------------------------------- #
# per-outcome overviews
# ----------------------------------------------------------------------------- #
def overview(c: pd.DataFrame, outcome: str, title: str | None = None) -> plt.Figure:
    """Heatmap of the 54 × 5 matrix, jittered dots with mean/median, arm profile."""
    w = _wide(c, outcome)
    vals = w[COND].to_numpy(dtype=float)
    d_any = vals[:, 1:].mean(axis=1) - vals[:, 0]
    order = np.argsort(d_any)
    vmin, vmax = np.nanmin(vals), np.nanmax(vals)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), gridspec_kw={"width_ratios": [1.1, 1.3, 1.1]})
    ax = axes[0]
    im = ax.imshow(vals[order], aspect="auto", cmap="RdYlGn", vmin=vmin, vmax=vmax)
    ax.set_xticks(range(5), LAB, rotation=30, ha="right")
    ax.set_ylabel("person, sorted by any-ad − no-ad")
    ax.set_title(f"{outcome}: 54 × 5")
    for i, idx in enumerate(order):
        if w["arm"].iloc[idx] == "lab":
            ax.plot(-0.6, i, "s", color="tab:blue", ms=3, clip_on=False)
    fig.colorbar(im, ax=ax, fraction=0.045)

    ax = axes[1]
    rng = np.random.default_rng(0)
    for i, cond in enumerate(COND):
        v = c.loc[c.condition == cond, outcome].dropna()
        ax.plot(np.full(len(v), i) + rng.uniform(-0.2, 0.2, len(v)), v, "o", ms=3.5, alpha=0.35, color="0.3")
        ax.plot([i - 0.32, i + 0.32], [v.mean()] * 2, color="crimson", lw=2.5)
        ax.plot([i - 0.22, i + 0.22], [v.median()] * 2, color="navy", lw=2.5)
    ax.set_xticks(range(5), LAB, rotation=30, ha="right")
    ax.set_title("by condition (red mean, blue median)")

    ax = axes[2]
    for arm, col in ARM_COLOR.items():
        sub = c[c.arm == arm].groupby("condition")[outcome].agg(["mean", "sem"]).reindex(COND)
        ax.errorbar(range(5), sub["mean"], yerr=1.96 * sub["sem"], marker="o", capsize=3,
                    label=f"{arm} (n={c[c.arm == arm].experiment_id.nunique()})", color=col)
    pooled = c.groupby("condition")[outcome].mean().reindex(COND)
    ax.plot(range(5), pooled, color="k", lw=1, ls="--", label="pooled")
    ax.set_xticks(range(5), LAB, rotation=30, ha="right")
    ax.set_title("mean ± 95% CI by arm"); ax.legend(fontsize=8)
    if title:
        fig.suptitle(title)
    fig.tight_layout()
    return fig


def likert_stack(c: pd.DataFrame, outcome: str, levels=range(1, 8)) -> plt.Figure:
    """Stacked share of each Likert answer per condition."""
    tab = c.pivot_table(index="condition", columns=outcome, values="experiment_id", aggfunc="count").reindex(COND)
    tab = tab.reindex(columns=list(levels)).fillna(0)
    share = tab.div(tab.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(9, 3.2))
    left = np.zeros(len(COND))
    for k in levels:
        ax.barh(LAB, share[k], left=left, color=LIKERT_CMAP((k - 1) / 6), edgecolor="white", label=str(k))
        left += share[k].to_numpy()
    ax.set_xlim(0, 1); ax.invert_yaxis()
    ax.set_title(f"{outcome}: share of each answer 1 (red) … 7 (green)")
    ax.legend(ncol=7, fontsize=8, loc="lower center", bbox_to_anchor=(0.5, -0.45), title="answer")
    fig.tight_layout()
    return fig


def arm_profiles(c: pd.DataFrame, outcomes, ncols: int = 4) -> plt.Figure:
    n = len(outcomes); nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.6 * ncols, 3.0 * nrows), squeeze=False)
    for ax, outcome in zip(axes.ravel(), outcomes):
        for arm, col in ARM_COLOR.items():
            sub = c[c.arm == arm].groupby("condition")[outcome].agg(["mean", "sem"]).reindex(COND)
            ax.errorbar(range(5), sub["mean"], yerr=1.96 * sub["sem"], marker="o", capsize=2, color=col, label=arm, lw=1.2)
        pooled = c.groupby("condition")[outcome].mean().reindex(COND)
        ax.plot(range(5), pooled, color="k", lw=1, ls="--")
        ax.set_xticks(range(5), ["no ad", "impl E", "impl L", "expl E", "expl L"], fontsize=8)
        ax.set_title(outcome, fontsize=10)
    for ax in axes.ravel()[n:]:
        ax.axis("off")
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Mean ± 95% CI by arm (dashed = pooled)")
    fig.tight_layout()
    return fig


def spaghetti(c: pd.DataFrame, outcome: str) -> plt.Figure:
    w = _wide(c, outcome)
    fig, ax = plt.subplots(figsize=(8, 4.4))
    rng = np.random.default_rng(1)
    for _, r in w.iterrows():
        ax.plot(range(5), r[COND].to_numpy(dtype=float) + rng.uniform(-0.08, 0.08), color=ARM_COLOR[r["arm"]], alpha=0.25, lw=1)
    m = c.groupby("condition")[outcome].mean().reindex(COND)
    ax.plot(range(5), m, color="k", lw=3, marker="o", label="mean")
    ax.set_xticks(range(5), LAB, rotation=15)
    ax.set_title(f"{outcome}: every person's profile (blue lab, orange crowd)"); ax.legend()
    fig.tight_layout()
    return fig


def d_histograms(c: pd.DataFrame, outcome: str) -> plt.Figure:
    w = _wide(c, outcome)
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.4))
    for ax, cid in zip(axes, sk.PLANNED):
        d = sk.contrast_scores(w[COND], cid)
        span = max(1.0, float(np.nanmax(np.abs(d))))
        ax.hist(d, bins=np.arange(-span - 0.125, span + 0.25, 0.25), color="0.45")
        ax.axvline(0, color="k")
        ax.axvline(d.mean(), color="crimson", label=f"mean {d.mean():+.2f}")
        ax.axvline(d.median(), color="navy", ls="--", label=f"median {d.median():+.2f}")
        neg, zero, pos = int((d < 0).sum()), int((d == 0).sum()), int((d > 0).sum())
        ax.set_title(f"{sk.CONTRAST_LABEL[cid]}   ↓{neg} ={zero} ↑{pos}")
        ax.legend(fontsize=8)
    fig.suptitle(f"{outcome}: within-person planned differences, n = {len(w)}")
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------------- #
# test tables → figures
# ----------------------------------------------------------------------------- #
def forest_D(table: pd.DataFrame, outcomes, title: str, holm_col: str = "holm_sig") -> plt.Figure:
    outcomes = [o for o in outcomes if o in set(table["outcome"])]
    fig, axes = plt.subplots(1, len(outcomes), figsize=(3.2 * len(outcomes), 3.4))
    axes = np.atleast_1d(axes)
    for ax, outcome in zip(axes, outcomes):
        b = table.loc[table["outcome"] == outcome].reset_index(drop=True)
        y = np.arange(len(b))
        ax.axvline(0, color="0.6", lw=1)
        ax.errorbar(b["mean"], y, xerr=[b["mean"] - b["ci95_lo"], b["ci95_hi"] - b["mean"]], fmt="o", color="black", capsize=3)
        for yi, hit in zip(y, b[holm_col]):
            if hit:
                ax.plot(b.loc[yi, "mean"], yi, "o", color="crimson", ms=8, zorder=3)
        ax.set_yticks(y, b["contrast_label"]); ax.set_title(outcome.replace("_", " ")); ax.invert_yaxis()
    fig.suptitle(title); fig.tight_layout()
    return fig


def forest_dz(table: pd.DataFrame, title: str, sig_col: str | None = None, label_col: str = "test_label") -> plt.Figure:
    """One-panel forest of standardised paired effects d_z with approximate 95% CI.

    For outcomes on different scales (process variables). CI uses
    SE(d_z) ≈ sqrt(1/n + d_z² / 2n).
    """
    b = table.reset_index(drop=True)
    se = np.sqrt(1.0 / b["n"] + b["dz"] ** 2 / (2 * b["n"]))
    y = np.arange(len(b))
    fig, ax = plt.subplots(figsize=(7, 0.28 * len(b) + 1.5))
    ax.axvline(0, color="0.6", lw=1)
    for lim in (-0.2, 0.2):
        ax.axvline(lim, color="0.85", lw=1, ls="--")
    ax.errorbar(b["dz"], y, xerr=1.96 * se, fmt="o", color="black", capsize=2, ms=4)
    if sig_col and sig_col in b:
        for yi, hit in zip(y, b[sig_col]):
            if hit:
                ax.plot(b.loc[yi, "dz"], yi, "o", color="crimson", ms=8, zorder=3)
    ax.set_yticks(y, [f"{o.replace('_', ' ')} · {l}" for o, l in zip(b["outcome"], b[label_col])], fontsize=8)
    ax.invert_yaxis(); ax.set_xlabel("d_z (paired), 95% CI; dashed = ±0.2")
    ax.set_title(title, fontsize=10); fig.tight_layout()
    return fig


def pairwise_heat(sweep: pd.DataFrame, outcomes, value: str = "mean") -> plt.Figure:
    """10 pairs × outcomes: mean difference, • raw < .05, ★ Holm-within-outcome < .05."""
    sub = sweep.loc[(sweep["block"] == "pairwise") & sweep["outcome"].isin(outcomes)].copy()
    pairs = [f"{a} - {b}" for a, b in sk.PAIRS]
    labels = [f"{sk.LABEL[a]} − {sk.LABEL[b]}" for a, b in sk.PAIRS]
    piv = sub.pivot_table(index="test", columns="outcome", values=value).reindex(index=pairs, columns=list(outcomes))
    praw = sub.pivot_table(index="test", columns="outcome", values="p_raw").reindex(index=pairs, columns=list(outcomes))
    pholm = sub.pivot_table(index="test", columns="outcome", values="p_holm_family").reindex(index=pairs, columns=list(outcomes))
    lim = float(np.nanmax(np.abs(piv.to_numpy()))) or 1.0
    fig, ax = plt.subplots(figsize=(1.6 * len(outcomes) + 3, 5.2))
    im = ax.imshow(piv.to_numpy(dtype=float), cmap="coolwarm", norm=TwoSlopeNorm(0, -lim, lim), aspect="auto")
    ax.set_xticks(range(len(outcomes)), outcomes, rotation=30, ha="right")
    ax.set_yticks(range(len(pairs)), labels, fontsize=8)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.iat[i, j]
            if pd.isna(v):
                continue
            mark = "★" if pholm.iat[i, j] < 0.05 else ("•" if praw.iat[i, j] < 0.05 else "")
            ax.text(j, i, f"{v:+.2f}{mark}", ha="center", va="center", fontsize=8, color="black")
    fig.colorbar(im, ax=ax, fraction=0.03, label="mean paired difference (first − second)")
    ax.set_title("Pairwise Wilcoxon, 10 pairs per outcome.  • raw p < .05   ★ Holm within the 10 < .05")
    fig.tight_layout()
    return fig


def friedman_bars(sweep: pd.DataFrame, outcomes) -> plt.Figure:
    sub = sweep.loc[(sweep["block"] == "friedman") & sweep["outcome"].isin(outcomes)]
    piv = sub.pivot_table(index="outcome", columns="test", values="p_raw").reindex(list(outcomes))
    w = sub.pivot_table(index="outcome", columns="test", values="kendall_w").reindex(list(outcomes))
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4))
    x = np.arange(len(piv))
    for k, (test, col) in enumerate((("friedman_5", "0.3"), ("friedman_4ad", "0.7"))):
        axes[0].bar(x + (k - 0.5) * 0.38, -np.log10(piv[test]), width=0.38, color=col, label=test.replace("_", " "))
        axes[1].bar(x + (k - 0.5) * 0.38, w[test], width=0.38, color=col, label=test.replace("_", " "))
    axes[0].axhline(-np.log10(0.05), color="crimson", ls="--", lw=1, label="p = .05")
    axes[0].set_xticks(x, piv.index, rotation=20); axes[0].set_ylabel("−log10 p"); axes[0].set_title("Friedman omnibus"); axes[0].legend(fontsize=8)
    axes[1].set_xticks(x, piv.index, rotation=20); axes[1].set_ylabel("Kendall W"); axes[1].set_title("effect size (0 = no agreement across people)")
    fig.tight_layout()
    return fig


def four_engines(side: pd.DataFrame) -> plt.Figure:
    """Primary outcomes × planned contrasts: −log10 p from paired t, Wilcoxon, ordinal GEE, LMM."""
    engines = [("p_paired_t", "paired t"), ("p_wilcoxon", "Wilcoxon"), ("p_ordinal_gee", "ordinal GEE"), ("p_lmm", "LMM")]
    side = side.copy()
    side["row"] = side["outcome"] + "  " + side["contrast_label"]
    fig, ax = plt.subplots(figsize=(9, 0.42 * len(side) + 1.5))
    y = np.arange(len(side))
    markers = ["o", "s", "^", "D"]
    for (col, name), m in zip(engines, markers):
        v = -np.log10(side[col].astype(float).clip(lower=1e-10))
        ax.plot(v, y, m, label=name, ms=6, alpha=0.85)
    ax.axvline(-np.log10(0.05), color="crimson", ls="--", lw=1, label="p = .05")
    ax.set_yticks(y, side["row"], fontsize=8); ax.invert_yaxis()
    ax.set_xlabel("−log10 p (raw)"); ax.set_xlim(0, min(10, ax.get_xlim()[1]))
    ax.set_title("Same contrast, four estimators. Ordinal GEE is missing for composites (they are means).")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------------- #
# sweep-level
# ----------------------------------------------------------------------------- #
def hits_by_block(sweep: pd.DataFrame) -> plt.Figure:
    g = sweep.groupby(["tier", "block"]).agg(n=("p_raw", "count"), raw=("sig_raw", "sum"),
                                              holm=("sig_holm_family", "sum"), bh=("sig_bh_global", "sum")).reset_index()
    g["label"] = g["tier"] + " / " + g["block"]
    g["expected"] = 0.05 * g["n"]
    fig, ax = plt.subplots(figsize=(11, 0.32 * len(g) + 1.5))
    y = np.arange(len(g))
    ax.barh(y - 0.25, g["raw"], height=0.25, color="0.7", label="raw < .05")
    ax.barh(y, g["holm"], height=0.25, color="tab:orange", label="Holm within family")
    ax.barh(y + 0.25, g["bh"], height=0.25, color="tab:red", label="BH across sweep")
    ax.plot(g["expected"], y - 0.25, "k|", ms=8, label="expected raw by chance")
    ax.set_yticks(y, g["label"], fontsize=8); ax.invert_yaxis()
    ax.set_xlabel("number of significant tests"); ax.legend(fontsize=8, loc="lower right")
    ax.set_title("Hits per block. Read the black tick before the grey bar.")
    fig.tight_layout()
    return fig


def volcano(sweep: pd.DataFrame) -> plt.Figure:
    """Standardised effect vs −log10 p; colour by tier; BH survivors outlined."""
    s = sweep.copy()
    eff = np.where(s["block"].isin(["planned_D", "pairwise"]), s["dz"],
                   np.where(s["block"].isin(["bfi_moderation", "bfi_level"]), s["rho"],
                            np.where(s["block"] == "friedman", np.sqrt(s["kendall_w"].astype(float)), np.nan)))
    s["eff"] = eff
    s = s.dropna(subset=["eff"])
    tiers = list(dict.fromkeys(s["tier"]))
    cmap = plt.get_cmap("tab10")
    fig, ax = plt.subplots(figsize=(10, 5.2))
    for k, tier in enumerate(tiers):
        sub = s[s.tier == tier]
        ax.scatter(sub["eff"], -np.log10(sub["p_raw"].clip(lower=1e-12)), s=14, alpha=0.55, color=cmap(k), label=f"{tier} ({len(sub)})")
    hit = s[s.sig_bh_global]
    ax.scatter(hit["eff"], -np.log10(hit["p_raw"].clip(lower=1e-12)), s=40, facecolors="none", edgecolors="k", lw=0.8, label=f"BH-global < .05 ({len(hit)})")
    ax.axhline(-np.log10(0.05), color="crimson", ls="--", lw=1)
    ax.set_xlabel("standardised effect (d_z for D and pairs, ρ for BFI, √W for Friedman)")
    ax.set_ylabel("−log10 p (raw)"); ax.set_title(f"Exploratory sweep, {len(s)} tests with an effect size")
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    return fig


def bfi_scatter_grid(person_means: pd.DataFrame, trait: str, outcomes, ncols: int = 3) -> plt.Figure:
    n = len(outcomes); nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.0 * ncols, 3.3 * nrows), squeeze=False)
    for ax, outcome in zip(axes.ravel(), outcomes):
        d = person_means[[trait, outcome, "arm"]].dropna()
        for arm, col in ARM_COLOR.items():
            sub = d[d.arm == arm]
            ax.scatter(sub[trait], sub[outcome], s=22, color=col, alpha=0.75, label=arm)
        r = sk.spearman(d[trait], d[outcome])
        if len(d) > 2:
            coef = np.polyfit(d[trait], d[outcome], 1)
            xs = np.linspace(d[trait].min(), d[trait].max(), 20)
            ax.plot(xs, np.polyval(coef, xs), color="k", lw=1)
        ax.set_title(f"{outcome}\nρ = {r.get('rho', np.nan):+.2f}, p = {r.get('p_raw', np.nan):.4f}, n = {r.get('n', 0)}", fontsize=9)
        ax.set_xlabel(trait)
    for ax in axes.ravel()[n:]:
        ax.axis("off")
    axes[0, 0].legend(fontsize=8)
    fig.tight_layout()
    return fig


def giant_corr(frame: pd.DataFrame, cols, title: str, cluster: bool = True, mark_p: float = 0.05,
               groups: dict | None = None, figsize=None) -> plt.Figure:
    """Spearman matrix over many columns, optionally ordered by hierarchical clustering.

    Cells with raw p < mark_p carry a dot. n per cell is pairwise-complete.
    ``groups`` maps column -> block name; block boundaries are drawn when given
    and clustering is off.
    """
    from scipy.cluster.hierarchy import linkage, leaves_list
    from scipy.spatial.distance import squareform

    d = frame[list(cols)].apply(pd.to_numeric, errors="coerce")
    d = d.loc[:, d.notna().sum() >= 8]
    d = d.loc[:, d.std(skipna=True) > 0]
    rho = d.corr(method="spearman")
    # p-values pairwise
    p = pd.DataFrame(np.nan, index=rho.index, columns=rho.columns)
    for i, a in enumerate(rho.index):
        for b in rho.columns[i + 1:]:
            r = sk.spearman(d[a], d[b])
            p.loc[a, b] = p.loc[b, a] = r.get("p_raw", np.nan)
    order = list(rho.index)
    if cluster and len(order) > 2:
        dist = squareform(1 - rho.fillna(0).to_numpy(), checks=False)
        order = [rho.index[i] for i in leaves_list(linkage(dist, method="average"))]
    rho, p = rho.loc[order, order], p.loc[order, order]
    n = len(order)
    if figsize is None:
        figsize = (0.32 * n + 3, 0.32 * n + 2)
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(rho.to_numpy(dtype=float), cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(n), order, rotation=90, fontsize=7)
    ax.set_yticks(range(n), order, fontsize=7)
    pv = p.to_numpy(dtype=float)
    ys, xs = np.where(pv < mark_p)
    ax.scatter(xs, ys, s=4, color="black")
    if groups and not cluster:
        bounds = [i for i in range(1, n) if groups.get(order[i]) != groups.get(order[i - 1])]
        for b in bounds:
            ax.axhline(b - 0.5, color="black", lw=0.8); ax.axvline(b - 0.5, color="black", lw=0.8)
    fig.colorbar(im, ax=ax, fraction=0.025, label="Spearman ρ")
    ax.set_title(f"{title}   (dot = raw p < {mark_p}; {n} variables, {n * (n - 1) // 2} pairs)")
    fig.tight_layout()
    fig.rho_, fig.p_ = rho, p
    return fig


# ----------------------------------------------------------------------------- #
# combos
# ----------------------------------------------------------------------------- #
def scatter_D(dtab: pd.DataFrame, left: str, right: str, contrast: str) -> plt.Figure:
    a, b = f"{left}__{contrast}", f"{right}__{contrast}"
    d = dtab[[a, b] + (["arm"] if "arm" in dtab.columns else [])].dropna()
    r = sk.spearman(d[a], d[b])
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    if "arm" in d.columns:
        for arm, col in ARM_COLOR.items():
            sub = d[d.arm == arm]
            ax.scatter(sub[a], sub[b], s=28, color=col, alpha=0.8, label=arm)
        ax.legend(fontsize=8)
    else:
        ax.scatter(d[a], d[b], s=28, color="0.3")
    ax.axhline(0, color="0.7", lw=1); ax.axvline(0, color="0.7", lw=1)
    ax.set_xlabel(f"D {left}\n{sk.CONTRAST_LABEL[contrast]}"); ax.set_ylabel(f"D {right}")
    ax.set_title(f"Spearman ρ = {r.get('rho', np.nan):+.2f}, raw p = {r.get('p_raw', np.nan):.3f}, n = {r.get('n', 0)}", fontsize=9)
    fig.tight_layout()
    return fig


def rm_plot(state: pd.DataFrame, x: str, y: str) -> plt.Figure:
    """Repeated-measures correlation picture: one line per person through their five points."""
    d = state[["experiment_id", x, y]].dropna()
    r = sk.rmcorr(d, "experiment_id", x, y)
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    cmap = plt.get_cmap("viridis")
    people = list(d.experiment_id.unique())
    for i, pid in enumerate(people):
        sub = d[d.experiment_id == pid].sort_values(x)
        ax.plot(sub[x], sub[y], "-o", ms=3, lw=0.8, alpha=0.6, color=cmap(i / max(1, len(people) - 1)))
    ax.set_xlabel(x); ax.set_ylabel(y)
    ax.set_title(f"r_rm = {r.get('rrm', np.nan):+.2f}, p = {r.get('p_raw', np.nan):.3f}, {r.get('n_persons', 0)} people × {r.get('n_obs', 0) // max(1, r.get('n_persons', 1))} conditions", fontsize=9)
    fig.tight_layout()
    return fig


def combo_heat(table: pd.DataFrame, combo: str, contrast: str, right_order=None) -> plt.Figure:
    sub = table.loc[(table["combo"] == combo) & (table["grain"] == "D") & (table["contrast"] == contrast)]
    piv = sub.pivot_table(index="left", columns="right", values="effect")
    pp = sub.pivot_table(index="left", columns="right", values="p_raw").reindex(index=piv.index, columns=piv.columns)
    if right_order is not None:
        cols = [c for c in right_order if c in piv.columns]
        piv, pp = piv[cols], pp[cols]
    fig, ax = plt.subplots(figsize=(0.55 * piv.shape[1] + 3, 0.36 * piv.shape[0] + 1.8))
    im = ax.imshow(piv.to_numpy(dtype=float), cmap="coolwarm", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(piv.shape[1]), [c.replace("eeg_", "").replace("traj_", "") for c in piv.columns], rotation=60, ha="right", fontsize=8)
    ax.set_yticks(range(piv.shape[0]), piv.index, fontsize=8)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            if pd.notna(pp.iat[i, j]) and pp.iat[i, j] < 0.05:
                ax.text(j, i, "•", ha="center", va="center", fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.03, label="Spearman ρ on D_i")
    ax.set_title(f"{combo}: {sk.CONTRAST_LABEL[contrast]}   (• raw p < .05; zero Holm / BH hits)")
    fig.tight_layout()
    return fig
