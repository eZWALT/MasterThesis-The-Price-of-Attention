"""Goal 1 confirmatory freeze.

Two planned families, both at the person grain:

  surveys   trust, credibility, manipulation, notice  ×  three planned D
  recall    recall_memory, recall_trust_shift          ×  implicit−explicit, early−late

Paired t is primary (mean, CI, d_z). Wilcoxon p is raw. Holm is within
outcome across its contrasts. This table is what Results 7.2 is written
from. Nothing here is chosen by p.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
OUT = WALTER / "behavioural" / "outputs" / "confirmatory"

PRIMARY = ("trust", "credibility", "manipulation", "notice")
RECALL = ("recall_memory", "recall_trust_shift")


def survey_family(condition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in PRIMARY:
        w = sk.wide(condition, outcome)
        block = []
        for cid in sk.PLANNED:
            rec = sk.paired_d(sk.contrast_scores(w, cid))
            rec.update({"family": "surveys", "outcome": outcome, "contrast": cid,
                        "contrast_label": sk.CONTRAST_LABEL[cid]})
            block.append(rec)
        p = [r["p_raw"] for r in block]
        adj = multipletests(p, method="holm")[1]
        for r, a in zip(block, adj):
            r["p_holm"] = float(a)
            r["holm_sig"] = bool(a < 0.05)
        rows.extend(block)
    return pd.DataFrame(rows)


def recall_family(ads: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in RECALL:
        piv = ads.pivot_table(index="experiment_id", columns="condition", values=outcome, aggfunc="first")
        piv = piv.reindex(columns=list(sk.AD_CONDITIONS)).dropna()
        d = {
            "inline_vs_block": 0.5 * (piv["inline_early"] + piv["inline_late"]) - 0.5 * (piv["block_early"] + piv["block_late"]),
            "early_vs_late": 0.5 * (piv["inline_early"] + piv["block_early"]) - 0.5 * (piv["inline_late"] + piv["block_late"]),
        }
        block = []
        for cid, series in d.items():
            rec = sk.paired_d(series)
            rec.update({"family": "recall", "outcome": outcome, "contrast": cid,
                        "contrast_label": sk.CONTRAST_LABEL[cid]})
            block.append(rec)
        adj = multipletests([r["p_raw"] for r in block], method="holm")[1]
        for r, a in zip(block, adj):
            r["p_holm"] = float(a)
            r["holm_sig"] = bool(a < 0.05)
        rows.extend(block)
    return pd.DataFrame(rows)


def posthoc_vs_control(condition: pd.DataFrame, outcomes=PRIMARY) -> pd.DataFrame:
    """Localisation stream: each ad condition minus no ad, Holm across the four.

    Secondary / post-hoc by construction. It answers "which ad condition
    moved the outcome", not "did ads move it". Same paired t + Wilcoxon
    machinery as the planned family so the two tables read alike.
    """
    rows = []
    for outcome in outcomes:
        w = sk.wide(condition, outcome)
        block = []
        for cond in sk.AD_CONDITIONS:
            rec = sk.paired_d(w[cond] - w["no_ads"])
            rec.update({"family": "posthoc_vs_control", "outcome": outcome, "contrast": f"{cond}_vs_no_ads",
                        "contrast_label": f"{sk.LABEL[cond]} \u2212 no ad"})
            block.append(rec)
        adj = multipletests([r["p_raw"] for r in block], method="holm")[1]
        for r, a in zip(block, adj):
            r["p_holm"] = float(a)
            r["holm_sig"] = bool(a < 0.05)
        rows.extend(block)
    return pd.DataFrame(rows)


def forest(table: pd.DataFrame, path: Path) -> None:
    outcomes = list(dict.fromkeys(table["outcome"]))
    fig, axes = plt.subplots(1, len(outcomes), figsize=(3.1 * len(outcomes), 3.6), sharex=False)
    if len(outcomes) == 1:
        axes = [axes]
    for ax, outcome in zip(axes, outcomes):
        b = table.loc[table["outcome"] == outcome].reset_index(drop=True)
        y = np.arange(len(b))
        ax.axvline(0, color="0.6", lw=1)
        ax.errorbar(b["mean"], y, xerr=[b["mean"] - b["ci95_lo"], b["ci95_hi"] - b["mean"]],
                    fmt="o", color="black", capsize=3)
        for yi, hit in zip(y, b["holm_sig"]):
            if hit:
                ax.plot(b.loc[yi, "mean"], yi, marker="o", color="crimson", ms=8, zorder=3)
        ax.set_yticks(y, b["contrast_label"])
        ax.set_title(outcome.replace("_", " "))
        ax.invert_yaxis()
    fig.suptitle("Planned D_i, mean and 95% CI. Red = Holm < .05 within outcome. n = 54.")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    condition = pd.read_csv(GOLD / "condition_features.csv")
    ads = pd.read_csv(GOLD / "advertisement_features.csv")

    surveys = survey_family(condition)
    recall = recall_family(ads)
    both = pd.concat([surveys, recall], ignore_index=True)
    cols = ["family", "outcome", "contrast", "contrast_label", "n", "mean", "sd", "ci95_lo", "ci95_hi",
            "dz", "stat", "p_raw", "p_holm", "holm_sig", "wilcoxon_w", "p_wilcoxon"]
    both = both[cols].rename(columns={"stat": "t"})
    both.to_csv(OUT / "confirmatory_planned_D.csv", index=False)
    forest(surveys, OUT / "forest_surveys.png")
    forest(recall, OUT / "forest_recall.png")

    posthoc = posthoc_vs_control(condition, PRIMARY + ("helpfulness", "convincingness", "relevance", "neutrality"))
    posthoc = posthoc[cols].rename(columns={"stat": "t"})
    posthoc.to_csv(OUT / "posthoc_vs_control.csv", index=False)
    forest(posthoc.loc[posthoc["outcome"].isin(PRIMARY)], OUT / "forest_posthoc_vs_control.png")

    hits = both.loc[both["holm_sig"], ["family", "outcome", "contrast_label", "mean", "ci95_lo", "ci95_hi", "dz", "p_holm"]]
    summary = {
        "n_people": int(both["n"].max()),
        "n_tests_surveys": int(len(surveys)),
        "n_tests_recall": int(len(recall)),
        "holm_hits": hits.round(4).to_dict(orient="records"),
        "posthoc_vs_control_holm_hits": posthoc.loc[posthoc["holm_sig"], ["outcome", "contrast_label", "mean", "ci95_lo", "ci95_hi", "dz", "p_holm"]].round(4).to_dict(orient="records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
    print(f"Wrote {OUT}")
