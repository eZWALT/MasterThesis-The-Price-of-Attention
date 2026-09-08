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
        "recall_memory": "Cued memory", "recall_trust_shift": "Trust shift on re-exposure"}
ITEMS = [("trust", "Trust"), ("llm_reliable", "Reliable information"), ("llm_false", "False information (R)"),
         ("llm_made_up", "Made-up content (R)"), ("behaviour_pushing", "Pushing / marketing"), ("behaviour_manipulate", "Steering, not assisting"),
         ("notice_brands", "Brand or product mention"), ("notice_sponsored", "Sponsored button")]


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
    x = np.arange(5)
    rng = np.random.default_rng(3)
    for ax, outcome in zip(axes, PRIMARY):
        w = sk.wide(condition, outcome)
        arm = condition.drop_duplicates("experiment_id").set_index("experiment_id")["arm"].reindex(w.index)
        for j, c in enumerate(sk.CONDITIONS):
            ax.scatter(j + rng.uniform(-0.18, 0.18, len(w)), w[c], s=7, color=MIST, zorder=1)
        for label, mask, col, ls in (("Laboratory (n = 18)", arm == "lab", TEAL, "--"), ("Crowd (n = 36)", arm == "crowd", CLAY, ":")):
            m = w.loc[mask].mean()
            ax.plot(x, [m[c] for c in sk.CONDITIONS], ls, color=col, lw=1.2, label=label, zorder=2)
        m, se = w.mean(), w.std(ddof=1) / np.sqrt(len(w))
        ax.errorbar(x, [m[c] for c in sk.CONDITIONS], yerr=[1.96 * se[c] for c in sk.CONDITIONS], fmt="o-", color=NAVY, lw=1.8,
                    ms=5, capsize=3, label="All (N = 54), 95% CI", zorder=3)
        ax.set_title(NAME[outcome]); ax.set_xticks(x, [COND[c].replace(" ", "\n") for c in sk.CONDITIONS], fontsize=8)
        ax.set_ylim(0.8, 7.2); ax.set_yticks(range(1, 8)); ax.grid(axis="y", color=MIST, lw=0.6)
    axes[0].set_ylabel("Rating (1–7)")
    axes[-1].legend(loc="lower right", fontsize=8, frameon=False)
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
    for col, lab, mk, colr in (("p_holm", "Paired t, Holm (primary)", "o", NAVY), ("p_holm_lmm", "Random-intercept LMM, Holm (declared)", "s", TEAL),
                               ("p_wilcoxon", "Wilcoxon, raw (sensitivity)", "^", SLATE)):
        ax.scatter(-np.log10(m[col].clip(lower=1e-6)), y, marker=mk, s=42, color=colr, label=lab, zorder=3, alpha=0.9)
    ax.set_yticks(y, [f"{NAME[o]} · {CONTRAST[c]}" for o, c in zip(m.outcome, m.contrast)], fontsize=8)
    ax.set_xlabel("−log10 p"); ax.set_xlim(0, 6.3); ax.grid(axis="x", color=MIST, lw=0.6)
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    ax.set_title("Planned contrasts under three estimators (N = 54)")
    fig.tight_layout()
    save(fig, "beh_estimator_concordance")


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
             r"Outcome & Condition − no ads & \(\overline{D}\) & 95\% CI & \(d_z\) & Holm \(p\) & Wilcoxon \(p\) \\", r"\midrule"]
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

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tab_beh_planned.tex").write_text(table_planned(planned, lmm) + "\n")
    (OUT / "tab_beh_localisation.tex").write_text(table_localisation(posthoc) + "\n")
    (OUT / "tab_beh_descriptives.tex").write_text(table_descriptives(condition, ads) + "\n")
    (OUT / "fig_beh_environments.tex").write_text(FIGURE_ENVIRONMENTS)
    manifest = {
        "figures": ["beh_condition_profiles", "beh_confirmatory_forests", "beh_localisation_forest", "beh_likert_distributions", "beh_estimator_concordance"],
        "tables": ["tab_beh_planned", "tab_beh_localisation", "tab_beh_descriptives"],
        "sources": ["gold/condition_features.csv", "gold/advertisement_features.csv", "confirmatory/confirmatory_planned_D.csv",
                    "confirmatory/lmm_declared.csv", "confirmatory/posthoc_vs_control.csv"],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("tables written")


if __name__ == "__main__":
    run()
