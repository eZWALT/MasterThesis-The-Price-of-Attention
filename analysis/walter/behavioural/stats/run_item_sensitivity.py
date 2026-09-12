"""Composite robustness: leave-one-item-out and item-level planned contrasts.

Answers Katerina's 8 September ask without changing anything confirmatory.
The pre-specified composites stay primary. This is a sensitivity analysis,
reported in the appendix regardless of what it shows.

Three things are written to outputs/sensitivity/:

1. item_diagnostics.csv  -- per composite item: Spearman with the scale
   mates before and after the single reversal, item-rest correlation,
   alpha if deleted. Shows why the three flagged items looked "low":
   they are the odd-polarity item of each three-item scale.
2. item_loo_contrasts.csv -- every three-item composite rebuilt without
   each item in turn, and the three planned contrasts re-estimated
   (paired t, Holm within outcome), next to the full composite.
3. item_level_contrasts.csv -- the three planned contrasts on each of the
   16 items behind the seven composites, Holm within item.

Plus tab_beh_item_loo.tex, tab_beh_item_diag.tex and beh_item_forest.pdf/png.

    python analysis/walter/behavioural/stats/run_item_sensitivity.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
OUT = WALTER / "behavioural" / "outputs" / "sensitivity"
FIG = WALTER / "behavioural" / "outputs" / "figures" / "thesis"

NAVY, CLAY, TEAL, SLATE, MIST, INK = "#1B3A4B", "#C45C26", "#2A6F6F", "#5C6B73", "#D5DDE3", "#12202A"
HOLM_ORANGE = CLAY
HOLM_STAR_SIZE = 16
HOLM_LEGEND = "Holm p < .05"

SCALES = {
    "credibility": (["llm_reliable", "llm_false", "llm_made_up"], {"llm_false", "llm_made_up"}),
    "helpfulness": (["llm_helpful", "llm_addressed", "llm_not_aid"], {"llm_not_aid"}),
    "convincingness": (["llm_skeptical", "llm_convincing", "llm_changed_mind"], {"llm_skeptical"}),
    "relevance": (["llm_not_useful", "llm_suggestions", "llm_relevant"], {"llm_not_useful"}),
    "neutrality": (["llm_neutral", "llm_impartial", "llm_opinionated"], {"llm_opinionated"}),
    "manipulation": (["behaviour_pushing", "behaviour_manipulate"], set()),
    "notice": (["notice_brands", "notice_sponsored"], set()),
}
FLAGGED = {"llm_reliable", "llm_opinionated", "llm_skeptical"}
PRIMARY = ["credibility", "manipulation", "notice"]
NAME = {"trust": "Trust", "credibility": "Credibility", "manipulation": "Perceived manipulation", "notice": "Notice",
        "helpfulness": "Helpfulness", "convincingness": "Convincingness", "relevance": "Relevance", "neutrality": "Neutrality"}
ITEM = {"llm_reliable": "Reliable responses", "llm_false": "False information (R)", "llm_made_up": "Made-up information (R)",
        "llm_helpful": "Helpful responses", "llm_addressed": "Adequately addressed my request", "llm_not_aid": "Response did not aid me (R)",
        "llm_skeptical": "Sceptical of its responses (R)", "llm_convincing": "Convincing responses", "llm_changed_mind": "Changed my mind",
        "llm_not_useful": "Responses not useful (R)", "llm_suggestions": "Suggestions addressed my questions", "llm_relevant": "Relevant responses",
        "llm_neutral": "Neutral (fair) responses", "llm_impartial": "Impartial and unbiased", "llm_opinionated": "Opinionated responses (R)",
        "behaviour_pushing": "Pushing or marketing content", "behaviour_manipulate": "Steered my choice, not neutral",
        "notice_brands": "Mentioned products or brands", "notice_sponsored": "Noticed sponsored buttons"}
CONTRAST = {"any_ad_vs_no_ads": "Any ad \\(-\\) no ads", "inline_vs_block": "Implicit \\(-\\) explicit", "early_vs_late": "Early \\(-\\) late"}


def alpha(df: pd.DataFrame) -> float:
    k = df.shape[1]
    return float(k / (k - 1) * (1 - df.var(ddof=1).sum() / df.sum(axis=1).var(ddof=1)))


def reversed_items(frame: pd.DataFrame, items: list[str], rev: set[str]) -> pd.DataFrame:
    d = frame[items].astype(float).copy()
    for it in rev:
        d[it] = 8.0 - d[it]
    return d


def diagnostics(condition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, (items, rev) in SCALES.items():
        if len(items) < 3:
            continue
        raw = condition[items].astype(float)
        cor = reversed_items(condition, items, rev)
        a_full = alpha(cor)
        for it in items:
            mates = [c for c in items if c != it]
            rows.append({
                "composite": name, "item": it, "reversed": it in rev, "flagged": it in FLAGGED,
                "rho_raw_min": float(min(raw[it].corr(raw[m], method="spearman") for m in mates)),
                "rho_raw_max": float(max(raw[it].corr(raw[m], method="spearman") for m in mates)),
                "rho_rev_min": float(min(cor[it].corr(cor[m], method="spearman") for m in mates)),
                "rho_rev_max": float(max(cor[it].corr(cor[m], method="spearman") for m in mates)),
                "item_rest_rho": float(cor[it].corr(cor[mates].mean(axis=1), method="spearman")),
                "alpha_full": a_full, "alpha_if_deleted": alpha(cor[mates]),
            })
    return pd.DataFrame(rows)


def planned_block(frame: pd.DataFrame, outcome_col: str) -> list[dict]:
    w = sk.wide(frame, outcome_col)
    block = []
    for cid in sk.PLANNED:
        rec = sk.paired_d(sk.contrast_scores(w, cid))
        rec.update({"contrast": cid})
        block.append(rec)
    for r, a in zip(block, multipletests([b["p_raw"] for b in block], method="holm")[1]):
        r["p_holm"] = float(a)
        r["holm_sig"] = bool(a < 0.05)
    return block


def loo_contrasts(condition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, (items, rev) in SCALES.items():
        if len(items) < 3:
            continue
        cor = reversed_items(condition, items, rev)
        variants = {"full": items} | {f"without {it}": [c for c in items if c != it] for it in items}
        for label, keep in variants.items():
            tmp = condition[["experiment_id", "condition"]].copy()
            tmp["y"] = cor[keep].mean(axis=1)
            for r in planned_block(tmp, "y"):
                r.update({"composite": name, "variant": label, "dropped": label.replace("without ", "") if label != "full" else "",
                          "flagged_drop": label.replace("without ", "") in FLAGGED, "k_items": len(keep)})
                rows.append(r)
    t = pd.DataFrame(rows)
    return t[["composite", "variant", "dropped", "flagged_drop", "k_items", "contrast", "n", "mean", "ci95_lo", "ci95_hi", "dz", "p_raw", "p_holm", "holm_sig", "p_wilcoxon"]]


def item_level(condition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, (items, rev) in SCALES.items():
        cor = reversed_items(condition, items, rev)
        for it in items:
            tmp = condition[["experiment_id", "condition"]].copy()
            tmp["y"] = cor[it]
            for r in planned_block(tmp, "y"):
                r.update({"composite": name, "item": it, "reversed": it in rev})
                rows.append(r)
    t = pd.DataFrame(rows)
    return t[["composite", "item", "reversed", "contrast", "n", "mean", "ci95_lo", "ci95_hi", "dz", "p_raw", "p_holm", "holm_sig", "p_wilcoxon"]]


# --------------------------------------------------------------------------- #
# LaTeX
# --------------------------------------------------------------------------- #
def fmt_p(p: float) -> str:
    if pd.isna(p):
        return "--"
    return r"$<.001$" if p < 0.001 else f"${p:.3f}$".replace("$0.", "$.")


def tex_diag(diag: pd.DataFrame) -> str:
    lines = [r"\begin{table}[H]", r"\centering", r"\small",
             r"\caption{Item diagnostics for the five three-item composites on the 270 condition rows, after the single reversal used to build each composite. \(\rho\) with mates is the range of the item's Spearman correlations with its two scale-mates; item--rest \(\rho\) is its correlation with the mean of those two; \(\alpha\) if deleted is Cronbach's \(\alpha\) of the remaining pair. (R) marks reversed items. The three items in bold were queried as low-correlation on the unreversed scores; each is the odd-polarity item of its scale, and before reversal it correlates with its mates at \(-.32\) to \(-.56\).}",
             r"\label{tab:beh-item-diag}", r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{@{}ll c r r@{}}", r"\toprule",
             r"Composite & Item & \(\rho\) with mates & item--rest \(\rho\) & \(\alpha\) if deleted \\", r"\midrule"]
    last = None
    for _, r in diag.iterrows():
        comp = f"{NAME[r.composite]} (\\(\\alpha={r.alpha_full:.2f}\\))" if r.composite != last else ""
        if last is not None and r.composite != last:
            lines.append(r"\addlinespace[2pt]")
        last = r.composite
        item = ITEM[r["item"]]
        if r.flagged:
            item = r"\textbf{" + item + "}"
        rev = f"${r.rho_rev_min:.2f}$ to ${r.rho_rev_max:.2f}$" if abs(r.rho_rev_min - r.rho_rev_max) > 0.005 else f"${r.rho_rev_min:.2f}$"
        lines.append(f"{comp} & {item} & {rev} & ${r.item_rest_rho:.2f}$ & ${r.alpha_if_deleted:.2f}$ \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


SHORT = {"llm_reliable": "reliable", "llm_false": "false", "llm_made_up": "made-up", "llm_helpful": "helpful", "llm_addressed": "addressed",
         "llm_not_aid": "not aid", "llm_skeptical": "sceptical", "llm_convincing": "convincing", "llm_changed_mind": "changed mind",
         "llm_not_useful": "not useful", "llm_suggestions": "suggestions", "llm_relevant": "relevant", "llm_neutral": "neutral",
         "llm_impartial": "impartial", "llm_opinionated": "opinionated"}


def tex_loo(loo: pd.DataFrame, composites=("credibility", "neutrality", "convincingness")) -> str:
    lines = [r"\begin{table}[H]", r"\centering", r"\small",
             r"\caption{Leave-one-item-out robustness of the planned contrasts (\(N=54\)) for the three composites that hold a queried item. Each cell is \(\overline{D}\) in Likert points with its Holm \(p\) in parentheses (paired \(t\), Holm within composite) when the composite is rebuilt without the named item; ``full'' is the pre-specified composite. Bold column heads are the three queried items; bold cells are Holm \(p<.05\). A verdict change is a cell crossing \(.05\) relative to the full column. The same grid for helpfulness and relevance is in the released tables; it changes one verdict (helpfulness early \(-\) late without the not-aid item, Holm \(p=.042\)).}",
             r"\label{tab:beh-item-loo}", r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{@{}l r r r r@{}}", r"\toprule"]
    for i, comp in enumerate(composites):
        items = SCALES[comp][0]
        head = " & ".join((r"\textbf{$-$ " if it in FLAGGED else "$-$ ") + SHORT[it] + ("}" if it in FLAGGED else "") for it in items)
        if i:
            lines.append(r"\midrule")
        lines.append(r"\multicolumn{5}{@{}l}{\emph{" + NAME[comp] + r"}} \\")
        lines.append(f"Contrast & full & {head} \\\\")
        lines.append(r"\addlinespace[1pt]")
        for cid in sk.PLANNED:
            cells = []
            for variant in ["full"] + [f"without {it}" for it in items]:
                r = loo[(loo.composite == comp) & (loo.variant == variant) & (loo.contrast == cid)].iloc[0]
                p = fmt_p(r.p_holm).strip("$")
                cell = f"${r['mean']:+.2f}$ ({p})"
                if r.holm_sig:
                    cell = r"\textbf{" + cell + "}"
                cells.append(cell)
            lines.append(f"{CONTRAST[cid]} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def item_forest(items_t: pd.DataFrame) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": INK, "text.color": INK, "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 6.2), sharey=True)
    rows = []
    for comp in ["credibility", "manipulation", "notice"]:
        for it in SCALES[comp][0]:
            rows.append((comp, it))
    labels = [f"{ITEM[it]}" for comp, it in rows]
    y = np.arange(len(rows))[::-1]
    for ax, cid in zip(axes, sk.PLANNED):
        ax.axvline(0, color=INK, lw=0.9)
        his, los = [], []
        for yi, (comp, it) in zip(y, rows):
            r = items_t[(items_t.item == it) & (items_t.contrast == cid)].iloc[0]
            his.append(r.ci95_hi)
            los.append(r.ci95_lo)
            ax.errorbar(r["mean"], yi, xerr=[[r["mean"] - r.ci95_lo], [r.ci95_hi - r["mean"]]], fmt="o", color=NAVY, ecolor=TEAL,
                        elinewidth=1.3, capsize=2.5, ms=4.5)
        xmax = float(max(his)); xmin = float(min(los)); span = xmax - xmin
        for yi, (comp, it) in zip(y, rows):
            r = items_t[(items_t.item == it) & (items_t.contrast == cid)].iloc[0]
            if r.holm_sig:
                ax.text(xmax + 0.06 * span, yi, "*", color=HOLM_ORANGE, fontsize=HOLM_STAR_SIZE,
                        ha="center", va="center", fontweight="bold")
        ax.set_xlim(xmin - 0.05 * span, xmax + 0.14 * span)
        comps_seq = [c for c, _ in rows]
        for k in range(1, len(rows)):
            if comps_seq[k] != comps_seq[k - 1]:
                ax.axhline(y[k] + 0.5, color=MIST, lw=0.8)
        ax.set_title(CONTRAST[cid].replace("\\(-\\)", "\u2212"), fontsize=10)
        ax.grid(axis="x", color=MIST, lw=0.6)
        ax.set_xlabel("Likert points (95% t CI)")
    axes[0].set_yticks(y, labels, fontsize=8.5)
    for yi, (comp, it) in zip(y, rows):
        if it in FLAGGED:
            axes[0].get_yticklabels()[list(y).index(yi)].set_fontweight("bold")
    handle = Line2D([0], [0], marker="*", color="none", markeredgecolor=HOLM_ORANGE,
                    markerfacecolor=HOLM_ORANGE, markersize=14, linestyle="none", label=HOLM_LEGEND)
    fig.legend(handles=[handle], loc="lower center", bbox_to_anchor=(0.5, -0.02), frameon=False, fontsize=8)
    fig.tight_layout()
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "beh_item_forest.png", format="png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(FIG / "beh_item_forest.pdf", format="pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    condition = pd.read_csv(GOLD / "condition_features.csv")
    diag = diagnostics(condition)
    diag.to_csv(OUT / "item_diagnostics.csv", index=False)
    loo = loo_contrasts(condition)
    loo.to_csv(OUT / "item_loo_contrasts.csv", index=False)
    items_t = item_level(condition)
    items_t.to_csv(OUT / "item_level_contrasts.csv", index=False)
    (FIG / "tab_beh_item_diag.tex").write_text(tex_diag(diag) + "\n")
    (FIG / "tab_beh_item_loo.tex").write_text(tex_loo(loo) + "\n")
    item_forest(items_t)

    # verdict changes
    full = loo[loo.variant == "full"].set_index(["composite", "contrast"]).holm_sig
    changes = []
    for _, r in loo[loo.variant != "full"].iterrows():
        if bool(r.holm_sig) != bool(full.loc[(r.composite, r.contrast)]):
            changes.append({"composite": r.composite, "dropped": r.dropped, "contrast": r.contrast, "mean": round(r["mean"], 3),
                            "p_holm_variant": round(r.p_holm, 4), "full_sig": bool(full.loc[(r.composite, r.contrast)])})
    summary = {
        "flagged_items": sorted(FLAGGED),
        "flagged_are_odd_polarity": all(
            (diag[(diag.item == it)].reversed.iloc[0] != diag[(diag.composite == diag[diag.item == it].composite.iloc[0]) & (diag.item != it)].reversed.all())
            for it in FLAGGED),
        "flagged_raw_rho": {it: [round(diag[diag.item == it].rho_raw_min.iloc[0], 2), round(diag[diag.item == it].rho_raw_max.iloc[0], 2)] for it in sorted(FLAGGED)},
        "flagged_reversed_rho": {it: [round(diag[diag.item == it].rho_rev_min.iloc[0], 2), round(diag[diag.item == it].rho_rev_max.iloc[0], 2)] for it in sorted(FLAGGED)},
        "flagged_item_rest_rho": {it: round(diag[diag.item == it].item_rest_rho.iloc[0], 2) for it in sorted(FLAGGED)},
        "n_loo_cells": int((loo.variant != "full").sum()),
        "verdict_changes": changes,
        "item_level_holm_hits": int(items_t.holm_sig.sum()), "item_level_cells": int(len(items_t)),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    pd.set_option("display.width", 220)
    print(diag.round(2).to_string(index=False))
    print()
    print(loo[loo.composite.isin(["credibility", "neutrality", "convincingness"])][["composite", "variant", "contrast", "mean", "p_holm", "holm_sig"]].round(3).to_string(index=False))
    print()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
