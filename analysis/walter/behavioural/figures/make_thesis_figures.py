"""Thesis-grade behavioural figures and LaTeX tables (Results 7.2, appendix).

Same palette, rcParams, and forest layout as
analysis/eeg/analysis/plot_eeg_publication_suite.py so the behavioural
figures sit next to the EEG ones. Reads only frozen outputs:

    outputs/gold/condition_features.csv, advertisement_features.csv
    outputs/confirmatory/confirmatory_planned_D.csv   (paired t, Holm)
    outputs/confirmatory/lmm_declared.csv             (Methods estimator)
    outputs/confirmatory/posthoc_vs_control.csv       (localisation, post hoc)

Writes PNG (300 dpi) + PDF + .tex under outputs/figures/thesis/.

    python analysis/walter/behavioural/figures/make_thesis_figures.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
CONF = WALTER / "behavioural" / "outputs" / "confirmatory"
OUT = WALTER / "behavioural" / "outputs" / "figures" / "thesis"

NAVY, CLAY, TEAL, SLATE, MIST, INK = "#1B3A4B", "#C45C26", "#2A6F6F", "#5C6B73", "#D5DDE3", "#12202A"

COND = {"no_ads": "No ads", "inline_early": "Implicit early", "inline_late": "Implicit late",
        "block_early": "Explicit early", "block_late": "Explicit late"}
CONTRAST = {"any_ad_vs_no_ads": "Any ad − no ads", "inline_vs_block": "Implicit − explicit", "early_vs_late": "Early − late"}
PRIMARY = ["trust", "credibility", "manipulation", "notice"]
SECONDARY = ["helpfulness", "convincingness", "relevance", "neutrality"]
RECALL = ["recall_memory", "recall_trust_shift"]
NAME = {"trust": "Trust", "credibility": "Credibility", "manipulation": "Perceived manipulation", "notice": "Notice",
        "helpfulness": "Helpfulness", "convincingness": "Convincingness", "relevance": "Relevance", "neutrality": "Neutrality",
        "recall_memory": "Cued memory", "recall_trust_shift": "Trust after re-exposure"}
ITEMS = [("trust", "Trust"), ("llm_reliable", "Reliable responses"), ("llm_false", "False information (R)"),
         ("llm_made_up", "Made-up information (R)"), ("behaviour_pushing", "Pushing or marketing content"), ("behaviour_manipulate", "Steered my choice, not neutral"),
         ("notice_brands", "Mentioned products or brands"), ("notice_sponsored", "Noticed sponsored buttons")]


def style() -> None:
    plt.rcParams.update({
        "figure.dpi": 140, "savefig.dpi": 300, "font.family": "DejaVu Sans", "font.size": 10,
        "axes.titlesize": 12, "axes.labelsize": 10, "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "text.color": INK,
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })


def save(fig: plt.Figure, stem: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for suffix in (".png", ".pdf"):
        fig.savefig(OUT / f"{stem}{suffix}", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT / stem}.pdf")


def fmt_p(p: float) -> str:
    if pd.isna(p):
        return "--"
    if p < 0.001:
        return r"$<.001$"
    return f"${p:.3f}$".replace("$0.", "$.")


def fmt_num(x: float, digits: int = 2, sign: bool = True) -> str:
    s = f"{x:+.{digits}f}" if sign else f"{x:.{digits}f}"
    return f"${s}$"


def fmt_ci(lo: float, hi: float, digits: int = 2) -> str:
    return f"$[{lo:.{digits}f},\\,{hi:.{digits}f}]$"


# --------------------------------------------------------------------------- #
# figure 1: condition profiles (descriptive)
# --------------------------------------------------------------------------- #
def condition_profiles(condition: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 4, figsize=(12.5, 3.6), sharey=True)
    labels = [COND[c].replace(" ", "\n") for c in sk.CONDITIONS]
    for ax, outcome in zip(axes, PRIMARY):
        w = sk.wide(condition, outcome)
        data = [w[c].to_numpy(dtype=float) for c in sk.CONDITIONS]
        bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.55,
                        medianprops={"color": CLAY, "lw": 1.6},
                        whiskerprops={"color": INK}, capprops={"color": INK},
                        flierprops={"marker": ".", "ms": 3, "color": SLATE, "markeredgecolor": SLATE})
        for box in bp["boxes"]:
            box.set(facecolor=MIST, edgecolor=NAVY, lw=1.0)
        ax.set_title(NAME[outcome])
        ax.set_ylim(0.8, 7.2)
        ax.set_yticks(range(1, 8))
        ax.tick_params(axis="x", labelsize=8)
        ax.grid(axis="y", color=MIST, lw=0.6)
    axes[0].set_ylabel("Rating (1–7)")
    fig.tight_layout()
    save(fig, "beh_condition_profiles")


# --------------------------------------------------------------------------- #
# figure 2: confirmatory forests (planned D, paired t)
# --------------------------------------------------------------------------- #
def _forest(ax, rows: pd.DataFrame, labels: list[str], title: str, xlabel: str, sig_col: str = "holm_sig", mark_lmm: pd.Series | None = None) -> None:
    y = np.arange(len(rows))[::-1]
    ax.axvline(0, color=INK, lw=0.9)
    ax.errorbar(rows["mean"], y, xerr=[rows["mean"] - rows["ci95_lo"], rows["ci95_hi"] - rows["mean"]], fmt="o", color=NAVY,
                ecolor=TEAL, elinewidth=1.4, capsize=3, ms=5)
    xmax = float(rows["ci95_hi"].max()); xmin = float(rows["ci95_lo"].min()); span = xmax - xmin
    for yi, hit in zip(y, rows[sig_col]):
        if hit:
            ax.text(xmax + 0.06 * span, yi, "*", color=CLAY, fontsize=16, ha="center", va="center", fontweight="bold")
    if mark_lmm is not None:
        for yi, hit in zip(y, mark_lmm):
            if hit:
                ax.text(xmax + 0.06 * span, yi, "†", color=CLAY, fontsize=11, ha="center", va="center")
    ax.set_yticks(y, labels, fontsize=9); ax.set_xlim(xmin - 0.05 * span, xmax + 0.14 * span)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.grid(axis="x", color=MIST, lw=0.6)
    # separators between outcomes
    outs = rows["outcome"].to_numpy()
    for k in range(1, len(outs)):
        if outs[k] != outs[k - 1]:
            ax.axhline(y[k] + 0.5, color=MIST, lw=0.8)


def confirmatory_forests(planned: pd.DataFrame, lmm: pd.DataFrame) -> None:
    planned = planned.merge(lmm[["outcome", "contrast", "holm_sig"]].rename(columns={"holm_sig": "holm_sig_lmm"}), on=["outcome", "contrast"])
    planned["lmm_only"] = planned.holm_sig_lmm & ~planned.holm_sig
    surveys = planned[planned.family == "surveys"].copy()
    surveys["o"] = pd.Categorical(surveys.outcome, PRIMARY); surveys["c"] = pd.Categorical(surveys.contrast, list(CONTRAST))
    surveys = surveys.sort_values(["o", "c"])
    recall = planned[planned.family == "recall"].copy()
    recall["o"] = pd.Categorical(recall.outcome, RECALL); recall["c"] = pd.Categorical(recall.contrast, ["inline_vs_block", "early_vs_late"])
    recall = recall.sort_values(["o", "c"])
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.6, 8.6), gridspec_kw={"height_ratios": [12, 4.6]})
    _forest(ax1, surveys, [f"{CONTRAST[c]}\n{NAME[o]}" for o, c in zip(surveys.outcome, surveys.contrast)],
            "Post-condition composites (N = 54)", "", mark_lmm=surveys.lmm_only)
    _forest(ax2, recall, [f"{CONTRAST[c]}\n{NAME[o]}" for o, c in zip(recall.outcome, recall.contrast)],
            "Cued recall (N = 54, four advertisement conditions)", "Mean within-person difference, Likert points (95% t CI)")
    fig.tight_layout(h_pad=1.6)
    save(fig, "beh_confirmatory_forests")


# --------------------------------------------------------------------------- #
# figure 3: localisation forest (post hoc)
# --------------------------------------------------------------------------- #
def localisation_forest(posthoc: pd.DataFrame) -> None:
    ph = posthoc[posthoc.outcome.isin(PRIMARY)].copy()
    ph["o"] = pd.Categorical(ph.outcome, PRIMARY); ph["c"] = pd.Categorical(ph.contrast, [f"{c}_vs_no_ads" for c in sk.AD_CONDITIONS])
    ph = ph.sort_values(["o", "c"])
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    _forest(ax, ph, [f"{COND[c.replace('_vs_no_ads', '')]} − no ads\n{NAME[o]}" for o, c in zip(ph.outcome, ph.contrast)],
            "Each advertisement condition against a∅ (post hoc, N = 54)", "Mean within-person difference, Likert points (95% t CI)")
    fig.tight_layout()
    save(fig, "beh_localisation_forest")


# --------------------------------------------------------------------------- #
# figure 4: Likert distributions of the eight primary items
# --------------------------------------------------------------------------- #
def likert_distributions(condition: pd.DataFrame) -> None:
    cmap = LinearSegmentedColormap.from_list("house", [CLAY, "#E8C9B5", MIST, "#9FB7C4", NAVY], N=7)
    fig, axes = plt.subplots(2, 4, figsize=(13, 5.2), sharex=True)
    for ax, (item, label) in zip(axes.ravel(), ITEMS):
        for i, c in enumerate(sk.CONDITIONS):
            s = condition.loc[condition.condition == c, item].dropna().astype(int)
            counts = np.array([(s == k).sum() for k in range(1, 8)]) / len(s) * 100
            left = 0.0
            for k in range(7):
                ax.barh(4 - i, counts[k], left=left, color=cmap(k / 6), edgecolor="white", lw=0.4)
                left += counts[k]
        ax.set_yticks(range(5), [COND[c] for c in sk.CONDITIONS[::-1]], fontsize=8)
        ax.set_title(label, fontsize=10); ax.set_xlim(0, 100); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    for ax in axes[1]:
        ax.set_xlabel("Per cent of participants")
    handles = [plt.Rectangle((0, 0), 1, 1, color=cmap(k / 6)) for k in range(7)]
    fig.legend(handles, [str(k) for k in range(1, 8)], title="Response (1 = strongly disagree, 7 = strongly agree)", ncol=7,
               loc="lower center", bbox_to_anchor=(0.5, -0.06), frameon=False, fontsize=8, title_fontsize=8)
    fig.tight_layout()
    save(fig, "beh_likert_distributions")


# --------------------------------------------------------------------------- #
# figure 5: estimator concordance (appendix)
# --------------------------------------------------------------------------- #
def estimator_concordance(planned: pd.DataFrame, lmm: pd.DataFrame) -> None:
    m = planned.merge(lmm[["outcome", "contrast", "p_holm"]].rename(columns={"p_holm": "p_holm_lmm"}), on=["outcome", "contrast"])
    m["o"] = pd.Categorical(m.outcome, PRIMARY + RECALL); m["c"] = pd.Categorical(m.contrast, list(CONTRAST))
    m = m.sort_values(["o", "c"]).reset_index(drop=True)
    y = np.arange(len(m))[::-1]
    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.axvline(-np.log10(0.05), color=CLAY, lw=1, ls="--")
    ax.text(-np.log10(0.05) + 0.03, y[0] + 0.6, "p = .05", color=CLAY, fontsize=8)
    for col, lab, mk, colr in (("p_holm", "Paired t, Holm (primary)", "o", NAVY), ("p_holm_lmm", "Random-intercept LMM, Holm (adjusted check)", "s", TEAL),
                               ("p_wilcoxon", "Wilcoxon, raw (sensitivity)", "^", SLATE)):
        ax.scatter(-np.log10(m[col].clip(lower=1e-6)), y, marker=mk, s=42, color=colr, label=lab, zorder=3, alpha=0.9)
    ax.set_yticks(y, [f"{NAME[o]} · {CONTRAST[c]}" for o, c in zip(m.outcome, m.contrast)], fontsize=8)
    ax.set_xlabel("−log10 p"); ax.set_xlim(0, 6.3); ax.grid(axis="x", color=MIST, lw=0.6)
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    ax.set_title("Planned contrasts under three estimators (N = 54)")
    fig.tight_layout()
    save(fig, "beh_estimator_concordance")


# --------------------------------------------------------------------------- #
# figure 6: Holm board over the whole battery (appendix; mirrors fig:eeg-holm-board)
# --------------------------------------------------------------------------- #
def holm_board(planned: pd.DataFrame, secondary: pd.DataFrame) -> None:
    """Rows: 4 primary + 4 secondary composites + 2 recall items. Columns: the
    three planned contrasts (recall has two). Cell text = D-bar; fill = Holm p
    (orange below .05, greys above), like the EEG board."""
    rows = PRIMARY + SECONDARY + RECALL
    cols = list(CONTRAST)
    grid_p = pd.DataFrame(np.nan, index=rows, columns=cols)
    grid_m = grid_p.copy()
    src = pd.concat([planned[["outcome", "contrast", "mean", "p_holm"]], secondary[["outcome", "contrast", "mean", "p_holm"]]])
    for _, r in src.iterrows():
        if r.outcome in rows and r.contrast in cols:
            grid_p.loc[r.outcome, r.contrast] = r.p_holm
            grid_m.loc[r.outcome, r.contrast] = r["mean"]
    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cmap = ListedColormap([CLAY, "#E8C9B5", MIST, "#F2F4F6"])
    norm = BoundaryNorm([0, 0.05, 0.10, 0.50, 1.0001], cmap.N)
    data = grid_p.to_numpy(dtype=float)
    masked = np.ma.masked_invalid(data)
    ax.imshow(masked, cmap=cmap, norm=norm, aspect="auto")
    for i, o in enumerate(rows):
        for j, c in enumerate(cols):
            if np.isnan(data[i, j]):
                ax.text(j, i, "undefined", ha="center", va="center", fontsize=7, color=SLATE)
                continue
            p = data[i, j]
            ptxt = "<.001" if p < 0.001 else f"{p:.3f}".lstrip("0")
            ax.text(j, i, f"{grid_m.iloc[i, j]:+.2f}\nHolm {ptxt}", ha="center", va="center", fontsize=8,
                    color="white" if p < 0.05 else INK, fontweight="bold" if p < 0.05 else "normal")
    ax.set_xticks(range(len(cols)), [CONTRAST[c] for c in cols], fontsize=9)
    ax.set_yticks(range(len(rows)), [NAME[o] for o in rows], fontsize=9)
    ax.axhline(len(PRIMARY) - 0.5, color=INK, lw=1.2)
    ax.axhline(len(PRIMARY) + len(SECONDARY) - 0.5, color=INK, lw=1.2)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in [CLAY, "#E8C9B5", MIST, "#F2F4F6"]]
    ax.legend(handles, ["Holm p < .05", ".05 to .10", ".10 to .50", "> .50"], loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=8)
    ax.set_title("Planned contrasts across the behavioural battery (N = 54)\nmean within-person difference in Likert points; Holm within outcome", fontsize=10)
    fig.tight_layout()
    save(fig, "beh_holm_board")


# --------------------------------------------------------------------------- #
# figure 7: rainclouds of the person-level differences D_i (appendix)
# --------------------------------------------------------------------------- #
def d_rainclouds(condition: pd.DataFrame) -> None:
    """One panel per primary composite x planned contrast: half-violin, box,
    and the 54 jittered D_i. Shows the discreteness and the zeros that the
    assumption paragraph describes; the mean and its 95% t interval are the
    navy point and bar."""
    rng = np.random.default_rng(11)
    fig, axes = plt.subplots(len(PRIMARY), len(CONTRAST), figsize=(11, 8.6), sharex="col")
    for i, outcome in enumerate(PRIMARY):
        w = sk.wide(condition, outcome)
        for j, cid in enumerate(CONTRAST):
            ax = axes[i, j]
            d = sk.contrast_scores(w, cid).dropna().to_numpy(dtype=float)
            # half violin (kde) above the axis, points below
            from scipy.stats import gaussian_kde
            xs = np.linspace(d.min() - 0.5, d.max() + 0.5, 200)
            kde = gaussian_kde(d, bw_method=0.35)(xs)
            kde = kde / kde.max() * 0.45
            ax.fill_between(xs, 0.15, 0.15 + kde, color=TEAL, alpha=0.35, lw=0)
            ax.boxplot(d, orientation="horizontal", positions=[0.15], widths=0.12, showfliers=False, patch_artist=True,
                       boxprops=dict(facecolor="white", edgecolor=INK, lw=0.9), medianprops=dict(color=CLAY, lw=1.6),
                       whiskerprops=dict(color=INK, lw=0.9), capprops=dict(color=INK, lw=0.9))
            ax.scatter(d + rng.uniform(-0.04, 0.04, len(d)), -0.25 + rng.uniform(-0.12, 0.12, len(d)), s=9, color=SLATE, alpha=0.7, zorder=2)
            m, se = d.mean(), d.std(ddof=1) / np.sqrt(len(d))
            ax.errorbar(m, -0.55, xerr=1.96 * se, fmt="o", color=NAVY, ecolor=NAVY, capsize=3, ms=5, zorder=3)
            ax.axvline(0, color=INK, lw=0.8)
            ax.set_ylim(-0.75, 0.75)
            ax.set_yticks([])
            for s in ("left", "top", "right"):
                ax.spines[s].set_visible(False)
            share_zero = (d == 0).mean()
            ax.text(0.99, 0.95, f"zeros {share_zero:.0%}", transform=ax.transAxes, ha="right", va="top", fontsize=7.5, color=SLATE)
            if i == 0:
                ax.set_title(CONTRAST[cid], fontsize=10)
            if j == 0:
                ax.set_ylabel(NAME[outcome], fontsize=9)
            if i == len(PRIMARY) - 1:
                ax.set_xlabel("$D_i$, Likert points")
    fig.suptitle("Person-level planned differences $D_i$ for the four primary composites (N = 54): density, box, points; navy = mean with 95% t interval", fontsize=10, y=0.995)
    fig.tight_layout()
    save(fig, "beh_d_rainclouds")


# --------------------------------------------------------------------------- #
# tables
# --------------------------------------------------------------------------- #
def table_planned(planned: pd.DataFrame, lmm: pd.DataFrame) -> str:
    m = planned.merge(lmm[["outcome", "contrast", "p_holm"]].rename(columns={"p_holm": "p_holm_lmm"}), on=["outcome", "contrast"])
    lines = [r"\begin{table}[!htb]", r"\centering", r"\small",
             r"\caption{Planned behavioural contrasts (\(N=54\)). Each row is a one-sample paired \(t\) on the person-level difference \(D_i\) of \eqref{eq:person-contrast}, in Likert points, with its 95\% interval and \(d_z\). Holm runs within outcome across its contrasts. Wilcoxon \(p\) is the raw signed-rank sensitivity on the same \(D_i\). The last column is the Holm \(p\) of the same contrast under the random-intercept linear mixed model of \autoref{tab:analysis-families}; point estimates coincide.}",
             r"\label{tab:beh-planned}", r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{@{}ll r c r r r r@{}}", r"\toprule",
             r"Outcome & Contrast & \(\overline{D}\) & 95\% CI & \(d_z\) & Holm \(p\) & Wilcoxon \(p\) & LMM Holm \(p\) \\", r"\midrule"]
    for fam, outs, cons in (("surveys", PRIMARY, list(CONTRAST)), ("recall", RECALL, ["inline_vs_block", "early_vs_late"])):
        for o in outs:
            first = True
            for c in cons:
                r = m[(m.outcome == o) & (m.contrast == c)].iloc[0]
                name = NAME[o] if first else ""
                first = False
                lines.append(f"{name} & {CONTRAST[c]} & {fmt_num(r['mean'])} & {fmt_ci(r.ci95_lo, r.ci95_hi)} & {fmt_num(r.dz, sign=True)} & {fmt_p(r.p_holm)} & {fmt_p(r.p_wilcoxon)} & {fmt_p(r.p_holm_lmm)} \\\\")
            lines.append(r"\addlinespace[2pt]")
        if fam == "surveys":
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def table_localisation(posthoc: pd.DataFrame) -> str:
    lines = [r"\begin{table}[!htb]", r"\centering", r"\small",
             r"\caption{Post hoc localisation: each advertisement condition against \(a^{\emptyset}\) (\(N=54\)). Paired \(t\) on the ordinary difference, Holm across the four comparisons within outcome. Added after the planned contrasts were read; it says which condition carries a marginal and is not confirmatory.}",
             r"\label{tab:beh-localisation}", r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{@{}ll r c r r r@{}}", r"\toprule",
             r"Outcome & Condition \(-\) \(a^{\emptyset}\) & \(\overline{D}\) & 95\% CI & \(d_z\) & Holm \(p\) & Wilcoxon \(p\) \\", r"\midrule"]
    for o in PRIMARY:
        first = True
        for c in sk.AD_CONDITIONS:
            r = posthoc[(posthoc.outcome == o) & (posthoc.contrast == f"{c}_vs_no_ads")].iloc[0]
            lines.append(f"{NAME[o] if first else ''} & {COND[c]} & {fmt_num(r['mean'])} & {fmt_ci(r.ci95_lo, r.ci95_hi)} & {fmt_num(r.dz)} & {fmt_p(r.p_holm)} & {fmt_p(r.p_wilcoxon)} \\\\")
            first = False
        lines.append(r"\addlinespace[2pt]")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def table_descriptives(condition: pd.DataFrame, ads: pd.DataFrame) -> str:
    lines = [r"\begin{table}[!htb]", r"\centering", r"\footnotesize",
             r"\caption{Behavioural outcomes by condition, \(M\) (SD) over the \(N=54\) participants. Composites are means of their 1--7 items after reversal; recall items exist only for the four advertisement conditions.}",
             r"\label{tab:beh-descriptives}", r"\setlength{\tabcolsep}{3.5pt}", r"\begin{tabular}{@{}l ccccc@{}}", r"\toprule",
             "Outcome & " + " & ".join(COND[c] for c in sk.CONDITIONS) + r" \\", r"\midrule"]
    for o in PRIMARY + SECONDARY:
        g = condition.groupby("condition")[o].agg(["mean", "std"]).reindex(list(sk.CONDITIONS))
        lines.append(f"{NAME[o]} & " + " & ".join(f"{r['mean']:.2f} ({r['std']:.2f})" for _, r in g.iterrows()) + r" \\")
        if o == "notice":
            lines.append(r"\midrule")
    lines.append(r"\midrule")
    for o in RECALL:
        g = ads.groupby("condition")[o].agg(["mean", "std"]).reindex(list(sk.CONDITIONS))
        lines.append(f"{NAME[o]} & " + " & ".join("--" if pd.isna(r["mean"]) else f"{r['mean']:.2f} ({r['std']:.2f})" for _, r in g.iterrows()) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def table_omnibus(friedman: pd.DataFrame, pairs: pd.DataFrame) -> str:
    """Appendix: Friedman over five conditions per composite, then every pair that
    reaches Holm-10 < .05 under the paired t or the Wilcoxon test. The full
    80-pair grid stays in outputs/confirmatory/omnibus_pairwise.csv."""
    order = PRIMARY + SECONDARY
    lines = [r"\begin{table}[H]", r"\centering", r"\small",
             r"\caption{Omnibus test per composite (\(N=54\)): Friedman \(\chi^2\) over the five conditions with Kendall's \(W\). Post hoc; \(p\) is raw. The planned contrasts of \autoref{tab:beh-planned} are the confirmatory tests.}",
             r"\label{tab:beh-friedman}", r"\begin{tabular}{@{}l r r r@{}}", r"\toprule",
             r"Outcome & Friedman \(\chi^2_4\) & Kendall's \(W\) & \(p\) \\", r"\midrule"]
    for o in order:
        r = friedman[friedman.outcome == o].iloc[0]
        lines.append(f"{NAME[o]} & ${r['stat']:.2f}$ & ${r.kendall_w:.3f}$ & {fmt_p(r.p_raw)} \\\\")
        if o == "notice":
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    hits = pairs[pairs.p_t_holm10 < 0.10].copy()
    hits["o"] = pd.Categorical(hits.outcome, list(order))
    hits = hits.sort_values(["o", "p_t_holm10"])
    lines += [r"\begin{table}[H]", r"\centering", r"\small",
              r"\caption{Pairwise sweep over the ten condition pairs within each of the eight composites (\(80\) tests, \(N=54\)), post hoc. Paired \(t\) on the ordinary within-person difference with Holm and Benjamini--Hochberg across the ten pairs of an outcome; Wilcoxon \(p\) is the raw signed-rank sensitivity on the same differences. Pairs with Holm \(p<.10\) are listed; the full grid is in the released tables. Differences read first condition minus second.}",
              r"\label{tab:beh-pairwise}", r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{@{}ll r c r r r r@{}}", r"\toprule",
              r"Outcome & Pair & \(\overline{D}\) & 95\% CI & \(d_z\) & Holm \(p\) & BH \(q\) & Wilcoxon \(p\) \\", r"\midrule"]
    last = None
    for _, r in hits.iterrows():
        name = NAME[r.outcome] if r.outcome != last else ""
        if last is not None and r.outcome != last:
            lines.append(r"\addlinespace[2pt]")
        last = r.outcome
        pair = f"{COND[r.a]} \\(-\\) {COND[r.b].lower()}"
        lines.append(f"{name} & {pair} & {fmt_num(r['mean'])} & {fmt_ci(r.ci95_lo, r.ci95_hi)} & {fmt_num(r.dz)} & {fmt_p(r.p_t_holm10)} & {fmt_p(r.q_t_bh10)} & {fmt_p(r.p_wilcoxon)} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def table_alpha(alpha: pd.DataFrame) -> str:
    a = alpha[alpha.arm == "all"].set_index("scale")
    lab = alpha[alpha.arm == "lab"].set_index("scale")
    crowd = alpha[alpha.arm == "crowd"].set_index("scale")
    lines = [r"\begin{table}[H]", r"\centering", r"\small",
             r"\caption{Internal consistency of the multi-item composites on the 270 condition rows (\(N=54\), five conditions each), items reversed once before averaging. Cronbach's \(\alpha\) with the mean inter-item Spearman \(\rho\); the arm columns repeat \(\alpha\) on the laboratory (90 rows) and crowd (180 rows) subsets. Trust is a single item and has no \(\alpha\).}",
             r"\label{tab:beh-alpha}", r"\begin{tabular}{@{}l c r r r r@{}}", r"\toprule",
             r"Composite & Items & \(\alpha\) & mean \(\rho\) & \(\alpha\) lab & \(\alpha\) crowd \\", r"\midrule"]
    for o in ["credibility", "manipulation", "notice", "helpfulness", "convincingness", "relevance", "neutrality"]:
        lines.append(f"{NAME[o]} & {int(a.loc[o, 'k_items'])} & ${a.loc[o, 'alpha']:.2f}$ & ${a.loc[o, 'mean_interitem_rho']:.2f}$ & ${lab.loc[o, 'alpha']:.2f}$ & ${crowd.loc[o, 'alpha']:.2f}$ \\\\")
        if o == "notice":
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


FIGURE_ENVIRONMENTS = r"""% Figure environments for Results 7.2 (behavioural). Paths assume the PDFs are
% copied to figures/results/ in the thesis repo. Captions follow the EEG forests.

\begin{figure}[!htb]
\centering
\includegraphics[width=\linewidth]{figures/results/beh_condition_profiles.pdf}
\caption{Post-condition composites by condition (\(N=54\)). Navy is the pooled mean with its 95\% \(t\) interval; the dashed teal and dotted orange lines are the laboratory (\(n=18\)) and crowd (\(n=36\)) means. Grey points are the individual ratings, jittered.}
\label{fig:beh-profiles}
\end{figure}

\begin{figure}[!htb]
\centering
\includegraphics[width=0.92\linewidth]{figures/results/beh_confirmatory_forests.pdf}
\caption{Planned behavioural contrasts (\(N=54\)). Top: the four post-condition composites under the three planned contrasts. Bottom: cued recall under the two contrasts defined on the four advertisement conditions. Each point is the mean within-person difference \(\overline{D}\) in Likert points with its 95\% paired-\(t\) interval. The orange asterisk marks Holm \(p<.05\) within outcome; the dagger marks the one cell that reaches Holm \(p<.05\) under the declared random-intercept mixed model but not under the paired \(t\) (\autoref{tab:beh-planned}).}
\label{fig:beh-forests}
\end{figure}

\begin{figure}[!htb]
\centering
\includegraphics[width=0.85\linewidth]{figures/results/beh_localisation_forest.pdf}
\caption{Post hoc localisation: each advertisement condition against \(a^{\emptyset}\) (\(N=54\)). Paired \(t\) on the ordinary difference; the asterisk marks Holm \(p<.05\) across the four comparisons within outcome. This grid was read after the planned contrasts and is not confirmatory.}
\label{fig:beh-localisation}
\end{figure}

% Appendix candidates
\begin{figure}[!htb]
\centering
\includegraphics[width=\linewidth]{figures/results/beh_likert_distributions.pdf}
\caption{Response distributions of the eight items behind the primary composites, by condition (\(N=54\)). (R) marks items reversed before averaging.}
\label{fig:beh-likert}
\end{figure}

\begin{figure}[!htb]
\centering
\includegraphics[width=0.85\linewidth]{figures/results/beh_estimator_concordance.pdf}
\caption{The sixteen planned contrasts under three estimators on the same person-level differences: the paired \(t\) with Holm within outcome, the random-intercept linear mixed model of \autoref{tab:analysis-families} with Holm within outcome, and the raw Wilcoxon signed-rank test. Values below \(10^{-6}\) are drawn at 6.}
\label{fig:beh-estimators}
\end{figure}
"""


TRAIT_NAME = {
    "bfi_e": "E", "bfi_a": "A", "bfi_c": "C", "bfi_n": "N", "bfi_o": "O",
}
TRAIT_ORDER = ["bfi_e", "bfi_a", "bfi_c", "bfi_n", "bfi_o"]


def personality_board(lmm: pd.DataFrame) -> None:
    """RQ8 (format) and RQ9 (timing): 4 composites × 5 traits. Cell = slope of
    D_i per BFI point; fill = Holm p within composite across the 15
    trait × contrast interactions."""
    from matplotlib.colors import ListedColormap, BoundaryNorm

    panels = [
        ("inline_vs_block", "Format (implicit − explicit)"),
        ("early_vs_late", "Timing (early − late)"),
    ]
    cmap = ListedColormap([CLAY, "#E8C9B5", MIST, "#F2F4F6"])
    norm = BoundaryNorm([0, 0.05, 0.10, 0.50, 1.0001], cmap.N)
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.0), sharey=True)
    for ax, (cid, title) in zip(axes, panels):
        block = lmm[lmm.contrast == cid]
        grid_p = pd.DataFrame(np.nan, index=PRIMARY, columns=TRAIT_ORDER)
        grid_m = grid_p.copy()
        for _, r in block.iterrows():
            grid_p.loc[r.outcome, r.trait] = r.p_holm
            grid_m.loc[r.outcome, r.trait] = r.estimate
        data = grid_p.to_numpy(dtype=float)
        ax.imshow(data, cmap=cmap, norm=norm, aspect="auto")
        for i, o in enumerate(PRIMARY):
            for j, t in enumerate(TRAIT_ORDER):
                p = data[i, j]
                ptxt = "<.001" if p < 0.001 else (f"{p:.2f}" if p >= 1 else f"{p:.2f}".lstrip("0"))
                ax.text(j, i, f"{grid_m.iloc[i, j]:+.2f}\n{ptxt}", ha="center", va="center", fontsize=8,
                        color="white" if p < 0.05 else INK, fontweight="bold" if p < 0.05 else "normal")
        ax.set_xticks(range(5), [TRAIT_NAME[t] for t in TRAIT_ORDER])
        ax.set_yticks(range(4), [NAME[o] for o in PRIMARY])
        ax.set_title(title, fontsize=10)
        ax.tick_params(length=0)
        for s in ("top", "right", "left", "bottom"):
            ax.spines[s].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in [CLAY, "#E8C9B5", MIST, "#F2F4F6"]]
    axes[-1].legend(handles, ["Holm p < .05", ".05–.10", ".10–.50", "> .50"], loc="upper left",
                    bbox_to_anchor=(1.02, 1), frameon=False, fontsize=8)
    fig.tight_layout()
    save(fig, "beh_personality_board")


def table_personality(lmm: pd.DataFrame) -> str:
    lines = [
        r"\begin{table}[H]", r"\centering", r"\footnotesize",
        r"\caption{Declared personality family (\(N=54\)): random-intercept mixed model of each primary composite on the three planned contrast codes, their interactions with one centred BFI-10 trait, and collapsed demographic covariates (arm, sex, familiar vs other, daily vs less). Each cell is the trait \(\times\) contrast slope in Likert points on \(D_i\) per one point on the 1--5 trait. Holm runs within composite across the fifteen interactions. No cell survives.}",
        r"\label{tab:beh-personality}",
        r"\setlength{\tabcolsep}{3.5pt}",
        r"\begin{tabular}{@{}ll l r c r r@{}}", r"\toprule",
        r"Outcome & Contrast & Trait & Slope & 95\% CI & Raw \(p\) & Holm \(p\) \\", r"\midrule",
    ]
    shown = lmm.copy()
    shown["outcome"] = pd.Categorical(shown["outcome"], PRIMARY)
    shown["contrast"] = pd.Categorical(shown["contrast"], list(CONTRAST))
    shown["trait"] = pd.Categorical(shown["trait"], TRAIT_ORDER)
    shown = shown.sort_values(["outcome", "contrast", "trait"])
    last_oc = None
    for _, r in shown.iterrows():
        oc = (r.outcome, r.contrast)
        o_lab = NAME[r.outcome] if last_oc is None or last_oc[0] != r.outcome else ""
        c_lab = CONTRAST[r.contrast] if last_oc != oc else ""
        if last_oc is not None and last_oc[0] != r.outcome:
            lines.append(r"\midrule")
        lines.append(
            f"{o_lab} & {c_lab} & {r.trait_label} & {fmt_num(r.estimate)} & "
            f"$[{r.ci95_lo:.2f},\\,{r.ci95_hi:.2f}]$ & {fmt_p(r.p_raw)} & {fmt_p(r.p_holm)} \\\\"
        )
        last_oc = oc
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def run() -> None:
    style()
    condition = pd.read_csv(GOLD / "condition_features.csv")
    ads = pd.read_csv(GOLD / "advertisement_features.csv")
    planned = pd.read_csv(CONF / "confirmatory_planned_D.csv")
    lmm = pd.read_csv(CONF / "lmm_declared.csv")
    posthoc = pd.read_csv(CONF / "posthoc_vs_control.csv")

    condition_profiles(condition)
    confirmatory_forests(planned, lmm)
    localisation_forest(posthoc)
    likert_distributions(condition)
    estimator_concordance(planned, lmm)
    # secondary composites, Holm within outcome over the three planned contrasts,
    # from the leave-one-item-out run ("full" variant = pre-specified composite)
    loo_path = WALTER / "behavioural" / "outputs" / "sensitivity" / "item_loo_contrasts.csv"
    if loo_path.exists():
        loo = pd.read_csv(loo_path)
        secondary = loo[(loo.variant == "full") & (loo.composite.isin(SECONDARY))].rename(columns={"composite": "outcome"})
        holm_board(planned, secondary)
    d_rainclouds(condition)

    pers_path = CONF / "personality_lmm.csv"
    pers = pd.read_csv(pers_path) if pers_path.exists() else None
    if pers is not None:
        personality_board(pers)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tab_beh_planned.tex").write_text(table_planned(planned, lmm) + "\n")
    (OUT / "tab_beh_localisation.tex").write_text(table_localisation(posthoc) + "\n")
    (OUT / "tab_beh_descriptives.tex").write_text(table_descriptives(condition, ads) + "\n")
    friedman = pd.read_csv(CONF / "omnibus_friedman.csv")
    pairs = pd.read_csv(CONF / "omnibus_pairwise.csv")
    alpha = pd.read_csv(CONF / "cronbach_alpha.csv")
    (OUT / "tab_beh_omnibus.tex").write_text(table_omnibus(friedman, pairs) + "\n")
    (OUT / "tab_beh_alpha.tex").write_text(table_alpha(alpha) + "\n")
    if pers is not None:
        (OUT / "tab_beh_personality.tex").write_text(table_personality(pers) + "\n")
    (OUT / "fig_beh_environments.tex").write_text(FIGURE_ENVIRONMENTS)
    manifest = {
        "figures": ["beh_condition_profiles", "beh_confirmatory_forests", "beh_localisation_forest", "beh_likert_distributions", "beh_estimator_concordance", "beh_personality_board"],
        "tables": ["tab_beh_planned", "tab_beh_localisation", "tab_beh_descriptives", "tab_beh_omnibus", "tab_beh_alpha", "tab_beh_personality"],
        "sources": ["gold/condition_features.csv", "gold/advertisement_features.csv", "confirmatory/confirmatory_planned_D.csv",
                    "confirmatory/lmm_declared.csv", "confirmatory/posthoc_vs_control.csv", "confirmatory/personality_lmm.csv"],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("tables written")


if __name__ == "__main__":
    run()
