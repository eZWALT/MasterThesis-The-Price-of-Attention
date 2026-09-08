"""Omnibus + pairwise stream on Gold: Katerina's design, N = 54, correct roster.

Per composite: Friedman over the five conditions (Kendall's W), then the ten
condition pairs as paired t (Holm-10 and BH-10 within outcome) with the
Wilcoxon signed-rank test beside it (also Holm-10 and BH-10 within outcome,
reported as sensitivity). Post hoc by construction: the four planned weights
already span the five-condition space, so every pair is a linear combination
of the planned estimates. This stream localises; it does not replace the
planned family.

Also writes the Cronbach alpha table for the seven multi-item composites, on
the 270 condition rows (items reversed once, before the composite).

Reads only Gold. Writes outputs/confirmatory/omnibus_friedman.csv,
outputs/confirmatory/omnibus_pairwise.csv, outputs/confirmatory/cronbach_alpha.csv.

    python analysis/walter/behavioural/stats/run_omnibus_pairwise.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

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
SECONDARY = ("helpfulness", "convincingness", "relevance", "neutrality")

# items behind each composite; reversal is what build_gold.py applies once
SCALES = {
    "credibility": (["llm_reliable", "llm_false", "llm_made_up"], {"llm_false", "llm_made_up"}),
    "helpfulness": (["llm_helpful", "llm_addressed", "llm_not_aid"], {"llm_not_aid"}),
    "convincingness": (["llm_skeptical", "llm_convincing", "llm_changed_mind"], {"llm_skeptical"}),
    "relevance": (["llm_not_useful", "llm_suggestions", "llm_relevant"], {"llm_not_useful"}),
    "neutrality": (["llm_neutral", "llm_impartial", "llm_opinionated"], {"llm_opinionated"}),
    "manipulation": (["behaviour_pushing", "behaviour_manipulate"], set()),
    "notice": (["notice_brands", "notice_sponsored"], set()),
}


def omnibus(condition: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    fried, pairs = [], []
    for outcome in PRIMARY + SECONDARY:
        w = sk.wide(condition, outcome)
        f = sk.friedman(w, sk.CONDITIONS)
        f.update({"outcome": outcome, "family": "surveys" if outcome in PRIMARY else "secondary"})
        fried.append(f)
        block = []
        for a, b in sk.PAIRS:
            rec = sk.paired_d((w[a] - w[b]).astype(float))
            rec.update({"outcome": outcome, "family": "surveys" if outcome in PRIMARY else "secondary",
                        "pair": f"{a}_vs_{b}", "pair_label": f"{sk.LABEL[a]} \u2212 {sk.LABEL[b]}", "a": a, "b": b})
            block.append(rec)
        for pcol, holm, bh in (("p_raw", "p_t_holm10", "q_t_bh10"), ("p_wilcoxon", "p_wilcoxon_holm10", "q_wilcoxon_bh10")):
            ps = [r[pcol] for r in block]
            for r, h, q in zip(block, multipletests(ps, method="holm")[1], multipletests(ps, method="fdr_bh")[1]):
                r[holm] = float(h)
                r[bh] = float(q)
        pairs.extend(block)
    f = pd.DataFrame(fried)
    f["p_holm8"] = multipletests(f.p_raw, method="holm")[1]  # across the eight omnibus tests, for the record
    p = pd.DataFrame(pairs).rename(columns={"p_raw": "p_t", "stat": "t"})
    p["sig_t_holm10"] = p.p_t_holm10 < 0.05
    p["sig_wilcoxon_holm10"] = p.p_wilcoxon_holm10 < 0.05
    p["verdict"] = np.select([p.sig_t_holm10 & p.sig_wilcoxon_holm10, p.sig_t_holm10 & ~p.sig_wilcoxon_holm10,
                              ~p.sig_t_holm10 & p.sig_wilcoxon_holm10], ["both", "t only", "Wilcoxon only"], default="neither")
    cols = ["family", "outcome", "pair", "pair_label", "a", "b", "n", "mean", "sd", "ci95_lo", "ci95_hi", "dz", "t", "p_t",
            "p_t_holm10", "q_t_bh10", "wilcoxon_w", "p_wilcoxon", "p_wilcoxon_holm10", "q_wilcoxon_bh10",
            "sig_t_holm10", "sig_wilcoxon_holm10", "verdict"]
    return f[["family", "outcome", "n", "k", "stat", "kendall_w", "p_raw", "p_holm8"]], p[cols]


def cronbach(condition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, (items, rev) in SCALES.items():
        for arm_label, frame in (("all", condition), ("lab", condition[condition.arm == "lab"]), ("crowd", condition[condition.arm == "crowd"])):
            d = frame[items].dropna().astype(float).copy()
            for it in rev:
                d[it] = 8.0 - d[it]
            k = d.shape[1]
            alpha = k / (k - 1) * (1 - d.var(ddof=1).sum() / d.sum(axis=1).var(ddof=1))
            # mean inter-item Spearman for the record
            r = d.corr(method="spearman").to_numpy()
            mean_r = float(r[np.triu_indices(k, 1)].mean())
            rows.append({"scale": name, "arm": arm_label, "k_items": k, "rows": len(d), "alpha": float(alpha), "mean_interitem_rho": mean_r})
    return pd.DataFrame(rows)


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    condition = pd.read_csv(GOLD / "condition_features.csv")
    f, p = omnibus(condition)
    f.to_csv(OUT / "omnibus_friedman.csv", index=False)
    p.to_csv(OUT / "omnibus_pairwise.csv", index=False)
    a = cronbach(condition)
    a.to_csv(OUT / "cronbach_alpha.csv", index=False)

    pd.set_option("display.width", 250)
    print(f.round(4).to_string(index=False))
    print()
    print(p.loc[p.verdict != "neither", ["outcome", "pair_label", "mean", "ci95_lo", "ci95_hi", "dz", "p_t_holm10", "q_t_bh10", "p_wilcoxon_holm10", "verdict"]].round(3).to_string(index=False))
    print()
    print(a[a.arm == "all"].round(3).to_string(index=False))
    summary = {
        "friedman_raw_lt_05": f.loc[f.p_raw < 0.05, "outcome"].tolist(),
        "n_pairwise_tests": int(len(p)),
        "pairwise_t_holm10_hits": int(p.sig_t_holm10.sum()),
        "pairwise_wilcoxon_holm10_hits": int(p.sig_wilcoxon_holm10.sum()),
        "pairwise_t_bh10_hits": int((p.q_t_bh10 < 0.05).sum()),
        "verdicts": p.verdict.value_counts().to_dict(),
        "alpha_all": {r.scale: round(r.alpha, 3) for r in a[a.arm == "all"].itertuples()},
    }
    (OUT / "omnibus_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
