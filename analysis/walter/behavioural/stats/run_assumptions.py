"""Assumption check for the frozen planned family, and the t-vs-Wilcoxon concordance.

Three questions a reader (or Katerina) can ask:

1. Are the D_i normal enough for a paired t?  Shapiro-Wilk, skew, excess
   kurtosis, share of exact zeros, on every planned D_i (12 survey + 4
   recall) and every localisation D (16), plus QQ grids.  Raw per-condition
   Likert distributions are checked too, and are expected to fail: they are
   integer-valued on 1-7.
2. Does the verdict depend on the engine?  Paired t (Holm) vs Wilcoxon
   (Holm) vs sign test (Holm) vs bootstrap percentile CI of the mean on the
   same D_i.  A cell that flips between engines is flagged.
3. Katerina's design run on Gold: all 10 condition pairs x 4 primaries,
   paired t Holm-10 and Wilcoxon Holm-10 within outcome, agreement table.

Pre-testing normality and then choosing the statistic is not the decision
rule (Rochon, Gatignol & Kimmel 2012; Zimmerman 2004): the paired t is the
pre-specified primary (Methods), the rest is sensitivity.  This script
documents the assumption; it does not switch the statistic.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
OUT = WALTER / "behavioural" / "outputs" / "assumptions"

PRIMARY = ("trust", "credibility", "manipulation", "notice")
RECALL = ("recall_memory", "recall_trust_shift")
B = 10_000
SEED = 7


# --------------------------------------------------------------------------- #
# the D_i series, exactly as the confirmatory script builds them
# --------------------------------------------------------------------------- #
def planned_series(condition: pd.DataFrame, ads: pd.DataFrame) -> list[tuple[str, str, str, str, pd.Series]]:
    out = []
    for outcome in PRIMARY:
        w = sk.wide(condition, outcome)
        for cid in sk.PLANNED:
            out.append(("surveys", outcome, cid, sk.CONTRAST_LABEL[cid], sk.contrast_scores(w, cid)))
        for cond in sk.AD_CONDITIONS:
            out.append(("posthoc_vs_control", outcome, f"{cond}_vs_no_ads", f"{sk.LABEL[cond]} \u2212 no ad", (w[cond] - w["no_ads"]).astype(float)))
    for outcome in RECALL:
        piv = ads.pivot_table(index="experiment_id", columns="condition", values=outcome, aggfunc="first")
        piv = piv.reindex(columns=list(sk.AD_CONDITIONS)).dropna()
        out.append(("recall", outcome, "inline_vs_block", sk.CONTRAST_LABEL["inline_vs_block"],
                    0.5 * (piv["inline_early"] + piv["inline_late"]) - 0.5 * (piv["block_early"] + piv["block_late"])))
        out.append(("recall", outcome, "early_vs_late", sk.CONTRAST_LABEL["early_vs_late"],
                    0.5 * (piv["inline_early"] + piv["block_early"]) - 0.5 * (piv["inline_late"] + piv["block_late"])))
    return out


def describe(series: pd.Series, rng: np.random.Generator) -> dict:
    s = pd.Series(series).dropna().astype(float).to_numpy()
    n = len(s)
    nz = s[s != 0]
    W, p_sw = stats.shapiro(s)
    t, p_t = stats.ttest_1samp(s, 0.0)
    p_w = 1.0 if len(nz) == 0 else float(stats.wilcoxon(s, zero_method="wilcox").pvalue)
    p_sign = 1.0 if len(nz) == 0 else float(stats.binomtest(int((nz > 0).sum()), len(nz), 0.5).pvalue)
    boot = rng.choice(s, size=(B, n), replace=True).mean(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    se = s.std(ddof=1) / np.sqrt(n)
    return {
        "n": n, "mean": s.mean(), "median": float(np.median(s)), "sd": s.std(ddof=1),
        "skew": float(stats.skew(s, bias=False)), "excess_kurtosis": float(stats.kurtosis(s, bias=False)),
        "n_unique": int(len(np.unique(s))), "share_zero": float((s == 0).mean()),
        "shapiro_W": float(W), "shapiro_p": float(p_sw),
        "t_ci_lo": s.mean() - 1.96 * se, "t_ci_hi": s.mean() + 1.96 * se,
        "boot_ci_lo": float(lo), "boot_ci_hi": float(hi),
        "p_t": float(p_t), "p_wilcoxon": p_w, "p_sign": p_sign,
    }


def holm_within(table: pd.DataFrame, pcol: str, out: str) -> pd.DataFrame:
    table[out] = np.nan
    for (_, _), idx in table.groupby(["family", "outcome"]).groups.items():
        table.loc[idx, out] = multipletests(table.loc[idx, pcol], method="holm")[1]
    return table


def assumption_table(condition: pd.DataFrame, ads: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    rows = []
    for family, outcome, cid, label, s in planned_series(condition, ads):
        rec = describe(s, rng)
        rec.update({"family": family, "outcome": outcome, "contrast": cid, "contrast_label": label})
        rows.append(rec)
    t = pd.DataFrame(rows)
    for pcol, out in (("p_t", "p_t_holm"), ("p_wilcoxon", "p_wilcoxon_holm"), ("p_sign", "p_sign_holm")):
        t = holm_within(t, pcol, out)
    t["sig_t"] = t.p_t_holm < 0.05
    t["sig_wilcoxon"] = t.p_wilcoxon_holm < 0.05
    t["sig_sign"] = t.p_sign_holm < 0.05
    t["sig_boot"] = (t.boot_ci_lo > 0) | (t.boot_ci_hi < 0)
    t["engines_agree"] = (t.sig_t == t.sig_wilcoxon) & (t.sig_t == t.sig_boot)
    t["boot_vs_t_ci_width_ratio"] = (t.boot_ci_hi - t.boot_ci_lo) / (t.t_ci_hi - t.t_ci_lo)
    front = ["family", "outcome", "contrast", "contrast_label", "n", "mean", "median", "sd", "skew", "excess_kurtosis",
             "n_unique", "share_zero", "shapiro_W", "shapiro_p", "t_ci_lo", "t_ci_hi", "boot_ci_lo", "boot_ci_hi",
             "boot_vs_t_ci_width_ratio", "p_t", "p_t_holm", "p_wilcoxon", "p_wilcoxon_holm", "p_sign", "p_sign_holm",
             "sig_t", "sig_wilcoxon", "sig_sign", "sig_boot", "engines_agree"]
    return t[front]


def raw_normality(condition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in PRIMARY:
        for cond in sk.CONDITIONS:
            s = condition.loc[condition.condition == cond, outcome].dropna().astype(float).to_numpy()
            W, p = stats.shapiro(s)
            rows.append({"outcome": outcome, "condition": sk.LABEL[cond], "n": len(s), "n_unique": int(len(np.unique(s))),
                         "mean": s.mean(), "sd": s.std(ddof=1), "skew": float(stats.skew(s, bias=False)),
                         "shapiro_W": float(W), "shapiro_p": float(p), "rejected_05": bool(p < 0.05)})
    return pd.DataFrame(rows)


def qq_grid(table: pd.DataFrame, series: list, family: str, path: Path, ncols: int) -> None:
    items = [(o, c, l, s) for f, o, c, l, s in series if f == family]
    outcomes = list(dict.fromkeys(o for o, *_ in items))
    fig, axes = plt.subplots(len(outcomes), ncols, figsize=(3.0 * ncols, 2.8 * len(outcomes)), squeeze=False)
    for i, outcome in enumerate(outcomes):
        for j, (o, c, l, s) in enumerate([x for x in items if x[0] == outcome]):
            ax = axes[i, j]
            x = pd.Series(s).dropna().astype(float).to_numpy()
            (osm, osr), (slope, intercept, _) = stats.probplot(x, dist="norm")
            ax.plot(osm, osr, "o", ms=3, color="black"); ax.plot(osm, slope * osm + intercept, color="crimson", lw=1)
            row = table[(table.family == family) & (table.outcome == outcome) & (table.contrast == c)].iloc[0]
            ax.set_title(f"{outcome} · {l}\nShapiro p = {row['shapiro_p']:.3f} · skew {row['skew']:+.2f} · {row['n_unique']} values", fontsize=8)
            ax.set_xlabel(""); ax.set_ylabel("")
    fig.suptitle(f"{family}: QQ of the person-level D_i against a normal (n = 54)", y=1.0)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


# --------------------------------------------------------------------------- #
# Katerina's design on Gold: 10 pairs, t and Wilcoxon, Holm-10 within outcome
# --------------------------------------------------------------------------- #
def pairwise_concordance(condition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in PRIMARY:
        w = sk.wide(condition, outcome)
        block = []
        for a, b in sk.PAIRS:
            d = (w[a] - w[b]).astype(float)
            rec = sk.paired_d(d)
            rec.update({"outcome": outcome, "pair": f"{a} - {b}", "pair_label": f"{sk.LABEL[a]} \u2212 {sk.LABEL[b]}"})
            block.append(rec)
        for pcol, out in (("p_raw", "p_t_holm10"), ("p_wilcoxon", "p_wilcoxon_holm10")):
            adj = multipletests([r[pcol] for r in block], method="holm")[1]
            for r, a in zip(block, adj):
                r[out] = float(a)
        rows.extend(block)
    t = pd.DataFrame(rows).rename(columns={"p_raw": "p_t", "stat": "t"})
    t["sig_t"] = t.p_t_holm10 < 0.05
    t["sig_wilcoxon"] = t.p_wilcoxon_holm10 < 0.05
    t["verdict"] = np.select([t.sig_t & t.sig_wilcoxon, t.sig_t & ~t.sig_wilcoxon, ~t.sig_t & t.sig_wilcoxon],
                             ["both", "t only", "Wilcoxon only"], default="neither")
    return t[["outcome", "pair", "pair_label", "n", "mean", "sd", "dz", "ci95_lo", "ci95_hi", "t", "p_t", "p_t_holm10",
              "wilcoxon_w", "p_wilcoxon", "p_wilcoxon_holm10", "sig_t", "sig_wilcoxon", "verdict"]]


def concordance_figure(pw: pd.DataFrame, path: Path) -> None:
    code = {"neither": 0, "both": 1, "t only": 2, "Wilcoxon only": 3}
    colors = ["#f0f0f0", "#c0392b", "#f39c12", "#2980b9"]
    pairs = [f"{sk.LABEL[a]} \u2212 {sk.LABEL[b]}" for a, b in sk.PAIRS]
    m = pw.pivot(index="outcome", columns="pair_label", values="verdict").reindex(index=list(PRIMARY), columns=pairs)
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.imshow(m.map(code.get).to_numpy(dtype=float), cmap=plt.matplotlib.colors.ListedColormap(colors), vmin=-0.5, vmax=3.5, aspect="auto")
    for i, o in enumerate(m.index):
        for j, p in enumerate(m.columns):
            r = pw[(pw.outcome == o) & (pw.pair_label == p)].iloc[0]
            ax.text(j, i, f"{r['mean']:+.2f}\nt {r.p_t_holm10:.2f} W {r.p_wilcoxon_holm10:.2f}", ha="center", va="center", fontsize=6.5)
    ax.set_xticks(range(len(pairs)), pairs, rotation=40, ha="right", fontsize=7); ax.set_yticks(range(len(m.index)), m.index)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors]
    ax.legend(handles, list(code), loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=7, frameon=False)
    ax.set_title("Katerina's design on Gold: 10 pairs × 4 primaries, Holm-10 within outcome. Paired t vs Wilcoxon.", fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    condition = pd.read_csv(GOLD / "condition_features.csv")
    ads = pd.read_csv(GOLD / "advertisement_features.csv")
    series = planned_series(condition, ads)

    table = assumption_table(condition, ads)
    table.to_csv(OUT / "assumptions_planned_D.csv", index=False)
    raw = raw_normality(condition)
    raw.to_csv(OUT / "raw_condition_normality.csv", index=False)
    qq_grid(table, series, "surveys", OUT / "qq_planned_D.png", ncols=3)
    qq_grid(table, series, "recall", OUT / "qq_recall_D.png", ncols=2)
    qq_grid(table, series, "posthoc_vs_control", OUT / "qq_posthoc_D.png", ncols=4)

    pw = pairwise_concordance(condition)
    pw.to_csv(OUT / "pairwise_t_vs_wilcoxon.csv", index=False)
    concordance_figure(pw, OUT / "pairwise_concordance.png")

    planned = table[table.family.isin(["surveys", "recall"])]
    summary = {
        "n_planned_cells": int(len(planned)),
        "planned_shapiro_rejected_05": int((planned.shapiro_p < 0.05).sum()),
        "planned_abs_skew_max": float(planned["skew"].abs().max()),
        "planned_excess_kurtosis_range": [float(planned.excess_kurtosis.min()), float(planned.excess_kurtosis.max())],
        "planned_engines_agree": int(planned.engines_agree.sum()),
        "planned_disagreements": planned.loc[~planned.engines_agree, ["outcome", "contrast_label", "mean", "p_t_holm", "p_wilcoxon_holm", "p_sign_holm", "boot_ci_lo", "boot_ci_hi"]].round(4).to_dict(orient="records"),
        "boot_vs_t_ci_width_ratio_range": [float(planned.boot_vs_t_ci_width_ratio.min()), float(planned.boot_vs_t_ci_width_ratio.max())],
        "raw_condition_cells_shapiro_rejected": f"{int(raw.rejected_05.sum())}/{len(raw)}",
        "pairwise_verdicts": pw.verdict.value_counts().to_dict(),
        "pairwise_disagreements": pw.loc[pw.verdict.isin(["t only", "Wilcoxon only"]), ["outcome", "pair_label", "mean", "p_t_holm10", "p_wilcoxon_holm10", "verdict"]].round(4).to_dict(orient="records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
