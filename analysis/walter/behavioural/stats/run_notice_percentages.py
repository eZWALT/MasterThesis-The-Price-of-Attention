"""Descriptive notice / recall percentages on Walter Gold (N = 54).

Walter (results.tex, review loop 2): "simple percentages of how many people
noticed ads per condition and which didn't". No test, no Holm; shares of
participants with a Wilson 95 % interval.

Thresholds are declared here, before any number was read, and every one is
reported:

    ge5  rating >= 5  "agree side"           (noticed / remembered)
    ge4  rating >= 4  at or above midpoint
    le3  rating <= 3  "disagree side"        (did not notice / not remembered)

Measures (all 1-7 Likert, one rating per participant x condition):

    sponsored  personality_sponsored  "I felt I noticed or clicked on
               sponsored buttons"  -> Gold column notice_sponsored.
               This is the detection item.
    brands     personality_brands    "I felt the chatbot mentioned products
               or brands"          -> Gold column notice_brands.
               High under no ad as well (a shopping assistant names
               products anyway); reported, NOT treated as detection.
    notice     planned outcome, mean of the two items.
    memory     recall_memory (cued recall, four ad conditions only).

Groupings:

    condition  five conditions, denominator = 54 participants each.
    format     implicit / explicit pooled over timing, three declared
               readings: `either` (>= threshold in at least one of the two
               timings), `both` (in both), `trials` (108 ratings pooled;
               denominator is ratings, not people, kept for comparison).
    any ad     same three readings over the four ad conditions.

Also reported: joint noticed (sponsored ge5) AND remembered (memory ge5),
remembered given noticed, and the within-person pattern "noticed the
explicit banner but not the implicit mention" (sponsored ge5 under explicit
and le3 under implicit), timing-matched and pooled, plus its reverse.

Reads only frozen Gold:

    outputs/gold/condition_features.csv
    outputs/gold/advertisement_features.csv

Writes:

    outputs/exploratory/notice_recall_percentages.csv
    outputs/figures/thesis/beh_notice_percentages.pdf (+ .png preview)
    outputs/figures/thesis/tab_beh_notice_percentages.tex

    python analysis/walter/behavioural/stats/run_notice_percentages.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

BEH = WALTER / "behavioural"
GOLD = BEH / "outputs" / "gold"
OUT_CSV = BEH / "outputs" / "exploratory" / "notice_recall_percentages.csv"
OUT_FIG = BEH / "outputs" / "figures" / "thesis"

# Palette of figures/make_thesis_figures.py (EEG suite house colours).
NAVY, CLAY, TEAL, SLATE, MIST, INK = "#1B3A4B", "#C45C26", "#2A6F6F", "#5C6B73", "#D5DDE3", "#12202A"
LIGHT_CLAY = "#E8C9B5"

COND_NAME = {"no_ads": "No ad", "inline_early": "Implicit early", "inline_late": "Implicit late",
             "block_early": "Explicit early", "block_late": "Explicit late"}
FORMAT = {"implicit": ("inline_early", "inline_late"), "explicit": ("block_early", "block_late")}

MEASURES = {
    "sponsored": "notice_sponsored",
    "brands": "notice_brands",
    "notice": "notice",
    "memory": "recall_memory",
}
THRESHOLDS = {"ge5": lambda x: x >= 5, "ge4": lambda x: x >= 4, "le3": lambda x: x <= 3}
Z = 1.959963984540054


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def wilson(k: int, n: int) -> tuple[float, float, float]:
    """Wilson score interval; returns (share, lo, hi)."""
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = k / n
    denom = 1 + Z**2 / n
    centre = (p + Z**2 / (2 * n)) / denom
    half = Z * np.sqrt(p * (1 - p) / n + Z**2 / (4 * n**2)) / denom
    return p, max(0.0, centre - half), min(1.0, centre + half)


def wide(table: pd.DataFrame, col: str, conditions: tuple[str, ...]) -> pd.DataFrame:
    piv = table.pivot_table(index="experiment_id", columns="condition", values=col, aggfunc="first")
    return piv.reindex(columns=list(conditions))


def row(measure: str, threshold: str, group: str, unit: str, flags: pd.Series | np.ndarray) -> dict:
    flags = np.asarray(flags, dtype=bool)
    n = int(flags.size)
    k = int(flags.sum())
    share, lo, hi = wilson(k, n)
    return {"measure": measure, "threshold": threshold, "group": group, "unit": unit,
            "k": k, "n": n, "share": share, "wilson_lo": lo, "wilson_hi": hi}


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> None:
    condition = pd.read_csv(GOLD / "condition_features.csv")
    ads = pd.read_csv(GOLD / "advertisement_features.csv")
    assert condition.experiment_id.nunique() == 54, condition.experiment_id.nunique()
    assert len(condition) == 270 and len(ads) == 216, (len(condition), len(ads))

    W: dict[str, pd.DataFrame] = {}
    for m, col in MEASURES.items():
        src = ads if m == "memory" else condition
        conds = sk.AD_CONDITIONS if m == "memory" else sk.CONDITIONS
        W[m] = wide(src, col, conds)
        assert W[m].notna().all().all(), f"missing ratings in {m}"

    rows: list[dict] = []
    for m, w in W.items():
        for t, fn in THRESHOLDS.items():
            flags = fn(w)
            # per condition
            for c in w.columns:
                rows.append(row(m, t, c, "participants", flags[c]))
            # per format
            for f, (c1, c2) in FORMAT.items():
                rows.append(row(m, t, f"{f}_either", "participants", flags[c1] | flags[c2]))
                rows.append(row(m, t, f"{f}_both", "participants", flags[c1] & flags[c2]))
                rows.append(row(m, t, f"{f}_trials", "ratings", np.concatenate([flags[c1], flags[c2]])))
            # any ad
            ad_cols = [c for c in sk.AD_CONDITIONS if c in w.columns]
            rows.append(row(m, t, "any_ad_either", "participants", flags[ad_cols].any(axis=1)))
            rows.append(row(m, t, "any_ad_all", "participants", flags[ad_cols].all(axis=1)))
            rows.append(row(m, t, "any_ad_trials", "ratings", flags[ad_cols].to_numpy().ravel()))

    # joint noticed (sponsored ge5) and remembered (memory ge5), four ad conditions
    sp = W["sponsored"] >= 5
    mem = W["memory"] >= 5
    for c in sk.AD_CONDITIONS:
        both = sp[c] & mem[c]
        rows.append(row("sponsored_and_memory", "ge5", c, "participants", both))
        rows.append(row("memory_given_sponsored", "ge5", c, "participants noticing", mem[c][sp[c]]))
        rows.append(row("memory_given_not_sponsored", "ge5", c, "participants not noticing", mem[c][~sp[c]]))
    for f, (c1, c2) in FORMAT.items():
        rows.append(row("sponsored_and_memory", "ge5", f"{f}_trials", "ratings",
                        np.concatenate([(sp[c1] & mem[c1]), (sp[c2] & mem[c2])])))

    # within-person: noticed explicit banner but not the implicit mention
    lo3 = W["sponsored"] <= 3
    rows.append(row("explicit_ge5_implicit_le3", "ge5/le3", "early", "participants",
                    sp["block_early"] & lo3["inline_early"]))
    rows.append(row("explicit_ge5_implicit_le3", "ge5/le3", "late", "participants",
                    sp["block_late"] & lo3["inline_late"]))
    rows.append(row("explicit_ge5_implicit_le3", "ge5/le3", "both_timings", "participants",
                    sp["block_early"] & sp["block_late"] & lo3["inline_early"] & lo3["inline_late"]))
    rows.append(row("explicit_ge5_implicit_le3", "ge5/le3", "either_timing", "participants",
                    (sp["block_early"] & lo3["inline_early"]) | (sp["block_late"] & lo3["inline_late"])))
    rows.append(row("implicit_ge5_explicit_le3", "ge5/le3", "early", "participants",
                    sp["inline_early"] & lo3["block_early"]))
    rows.append(row("implicit_ge5_explicit_le3", "ge5/le3", "late", "participants",
                    sp["inline_late"] & lo3["block_late"]))
    rows.append(row("implicit_ge5_explicit_le3", "ge5/le3", "either_timing", "participants",
                    (sp["inline_late"] & lo3["block_late"]) | (sp["inline_early"] & lo3["block_early"])))
    # noticed both formats / neither, timing-matched
    rows.append(row("explicit_ge5_implicit_ge5", "ge5", "early", "participants", sp["block_early"] & sp["inline_early"]))
    rows.append(row("explicit_ge5_implicit_ge5", "ge5", "late", "participants", sp["block_late"] & sp["inline_late"]))
    rows.append(row("explicit_le3_implicit_le3", "le3", "early", "participants", lo3["block_early"] & lo3["inline_early"]))
    rows.append(row("explicit_le3_implicit_le3", "le3", "late", "participants", lo3["block_late"] & lo3["inline_late"]))
    # Katerina-style cross-check reading (either item >= 5), computed on Gold only
    either = (W["sponsored"] >= 5) | (W["brands"] >= 5)
    for c in sk.CONDITIONS:
        rows.append(row("sponsored_or_brands", "ge5", c, "participants", either[c]))

    out = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False, float_format="%.4f")
    print(f"wrote {OUT_CSV} ({len(out)} rows)")

    make_figure(W["sponsored"])
    make_table(out)


# --------------------------------------------------------------------------- #
# figure: stacked shares of the sponsored-button item per condition
# --------------------------------------------------------------------------- #
def make_figure(sp: pd.DataFrame) -> None:
    plt.rcParams.update({
        "figure.dpi": 140, "savefig.dpi": 300, "font.family": "DejaVu Sans", "font.size": 10,
        "axes.titlesize": 12, "axes.labelsize": 10, "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "text.color": INK,
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })
    n = len(sp)
    conds = list(sk.CONDITIONS)
    noticed = (sp >= 5).sum()
    mid = (sp == 4).sum()
    notn = (sp <= 3).sum()
    x = np.arange(len(conds))
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    p_not = notn[conds].to_numpy() / n
    p_mid = mid[conds].to_numpy() / n
    p_yes = noticed[conds].to_numpy() / n
    ax.bar(x, p_yes, color=NAVY, edgecolor="white", lw=0.6, width=0.62, label="Noticed")
    ax.bar(x, p_mid, bottom=p_yes, color=MIST, edgecolor="white", lw=0.6, width=0.62, label="Midpoint")
    ax.bar(x, p_not, bottom=p_yes + p_mid, color=LIGHT_CLAY, edgecolor="white", lw=0.6, width=0.62,
           label="Did not notice")
    for i, c in enumerate(conds):
        share, lo, hi = wilson(int(noticed[c]), n)
        ax.errorbar(x[i], share, yerr=[[share - lo], [hi - share]], fmt="none", ecolor=CLAY, elinewidth=1.4,
                    capsize=4, zorder=4)
        # short bars: move the label off the whisker
        dx = -0.17 if share < 0.15 else 0.0
        ax.text(x[i] + dx, share / 2, f"{share:.0%}", ha="center", va="center", color="white", fontsize=9,
                fontweight="bold")
        if p_not[i] > 0.08:
            ax.text(x[i], p_yes[i] + p_mid[i] + p_not[i] / 2, f"{p_not[i]:.0%}", ha="center", va="center",
                    color=INK, fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels([COND_NAME[c].replace(" ", "\n") for c in conds], fontsize=9)
    ax.set_ylim(0, 1.0)
    ax.set_yticks(np.linspace(0, 1, 6))
    ax.set_yticklabels([f"{v:.0%}" for v in np.linspace(0, 1, 6)])
    ax.set_ylabel("Percentage of participants")
    ax.grid(axis="y", color=MIST, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    handles, labels = ax.get_legend_handles_labels()
    handles.append(plt.Line2D([0], [0], color=CLAY, lw=1.4))
    labels.append("Wilson 95% on noticed")
    ax.legend(handles, labels, loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False, fontsize=8.5)
    fig.tight_layout()
    OUT_FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG / "beh_notice_percentages.pdf", format="pdf", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT_FIG / "beh_notice_percentages.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT_FIG / 'beh_notice_percentages.pdf'}")


# --------------------------------------------------------------------------- #
# table: one row per condition, share >= 5 on four measures
# --------------------------------------------------------------------------- #
def make_table(out: pd.DataFrame) -> None:
    ge5 = out[(out.threshold == "ge5") & (out.unit == "participants")].set_index(["measure", "group"])

    def cell(measure: str, cond: str) -> str:
        if (measure, cond) not in ge5.index:
            return "--"
        r = ge5.loc[(measure, cond)]
        return f"{int(r.k)}/{int(r.n)} ({100 * r.share:.0f}\\%)"

    lines = [r"\begin{table}[H]", r"\centering", r"\small",
             r"\caption{Participants rating each item \(\geq 5\) of 7, by condition (\(N=54\); Wilson intervals in \autoref{fig:beh-notice-percentages} and the exploratory CSV).}",
             r"\label{tab:beh-notice-percentages}",
             r"\begin{tabular}{@{}l r r r r@{}}", r"\toprule",
             r"Condition & Sponsored buttons & Brands mentioned & Notice outcome & Cued memory \\", r"\midrule"]
    for c in sk.CONDITIONS:
        lines.append(f"{COND_NAME[c]} & {cell('sponsored', c)} & {cell('brands', c)} & {cell('notice', c)} & {cell('memory', c)} \\\\")
        if c == "no_ads":
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    path = OUT_FIG / "tab_beh_notice_percentages.tex"
    path.write_text("\n".join(lines) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
