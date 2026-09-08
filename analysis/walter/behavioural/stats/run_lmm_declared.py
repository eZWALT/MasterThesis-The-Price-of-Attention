"""The estimator Methods `tab:analysis-families` declares for the behavioural battery.

    linear mixed model on Y_ic, participant random intercept;
    3 planned contrasts within each composite; 2 for cued memory.

No covariates (that is `run_ordinal.py`, the adjusted check). Condition is a
five-level factor, the planned contrasts are Wald tests on the fixed effects
with the Dataset-A weights, Holm within composite. With complete balanced
data the point estimate equals the paired mean D̄ exactly; only the standard
error differs (pooled residual variance vs the empirical SD of D_i), so any
disagreement with `confirmatory_planned_D.csv` is a sphericity story, not an
estimand story.

Writes outputs/confirmatory/lmm_declared.csv and a side-by-side with the
paired t.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
OUT = WALTER / "behavioural" / "outputs" / "confirmatory"
PRIMARY = ("trust", "credibility", "manipulation", "notice")
SECONDARY = ("helpfulness", "convincingness", "relevance", "neutrality")
RECALL = ("recall_memory", "recall_trust_shift")


def fit(frame: pd.DataFrame, outcome: str, levels: tuple[str, ...]):
    d = frame[["experiment_id", "condition", outcome]].dropna().copy()
    d["condition"] = pd.Categorical(d["condition"], categories=list(levels))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = smf.mixedlm(f"{outcome} ~ C(condition)", d, groups=d["experiment_id"])
        res = model.fit(reml=True, method=["powell"])
    return res, d


def contrast_row(res, weights: dict[str, float], levels: tuple[str, ...]) -> dict:
    # fixed-effect names: Intercept, C(condition)[T.<level>] for levels[1:]
    names = list(res.fe_params.index)
    vec = np.zeros(len(names))
    for lvl, w in weights.items():
        if w == 0.0:
            continue
        if lvl == levels[0]:
            continue  # reference level: contributes only via the intercept, which cancels (weights sum to 0)
        vec[names.index(f"C(condition)[T.{lvl}]")] = w
    est = float(vec @ res.fe_params.to_numpy())
    cov = res.cov_params().loc[names, names].to_numpy()
    se = float(np.sqrt(vec @ cov @ vec))
    z = est / se
    from scipy import stats
    p = float(2 * stats.norm.sf(abs(z)))
    return {"estimate": est, "se": se, "ci95_lo": est - 1.96 * se, "ci95_hi": est + 1.96 * se, "z": z, "p_raw": p}


def run() -> None:
    condition = pd.read_csv(GOLD / "condition_features.csv")
    ads = pd.read_csv(GOLD / "advertisement_features.csv")
    rows = []
    for outcome in PRIMARY + SECONDARY:
        res, d = fit(condition, outcome, sk.CONDITIONS)
        icc = float(res.cov_re.iloc[0, 0] / (res.cov_re.iloc[0, 0] + res.scale))
        block = []
        for cid in sk.PLANNED:
            r = contrast_row(res, sk.CONTRASTS[cid], sk.CONDITIONS)
            r.update({"family": "surveys" if outcome in PRIMARY else "secondary", "outcome": outcome, "contrast": cid,
                      "contrast_label": sk.CONTRAST_LABEL[cid], "n": d.experiment_id.nunique(), "icc": icc,
                      "sigma_person": float(np.sqrt(res.cov_re.iloc[0, 0])), "sigma_resid": float(np.sqrt(res.scale))})
            block.append(r)
        for r, a in zip(block, multipletests([b["p_raw"] for b in block], method="holm")[1]):
            r["p_holm"] = float(a); r["holm_sig"] = bool(a < 0.05)
        rows.extend(block)
    for outcome in RECALL:
        res, d = fit(ads, outcome, sk.AD_CONDITIONS)
        icc = float(res.cov_re.iloc[0, 0] / (res.cov_re.iloc[0, 0] + res.scale))
        block = []
        for cid in ("inline_vs_block", "early_vs_late"):
            r = contrast_row(res, sk.CONTRASTS[cid], sk.AD_CONDITIONS)
            r.update({"family": "recall", "outcome": outcome, "contrast": cid, "contrast_label": sk.CONTRAST_LABEL[cid],
                      "n": d.experiment_id.nunique(), "icc": icc,
                      "sigma_person": float(np.sqrt(res.cov_re.iloc[0, 0])), "sigma_resid": float(np.sqrt(res.scale))})
            block.append(r)
        for r, a in zip(block, multipletests([b["p_raw"] for b in block], method="holm")[1]):
            r["p_holm"] = float(a); r["holm_sig"] = bool(a < 0.05)
        rows.extend(block)
    lmm = pd.DataFrame(rows)
    lmm.to_csv(OUT / "lmm_declared.csv", index=False)

    t = pd.read_csv(OUT / "confirmatory_planned_D.csv")
    side = t.merge(lmm[["outcome", "contrast", "estimate", "se", "ci95_lo", "ci95_hi", "p_raw", "p_holm", "holm_sig", "icc"]],
                   on=["outcome", "contrast"], suffixes=("_t", "_lmm"))
    side["verdict"] = np.select([side.holm_sig_t & side.holm_sig_lmm, side.holm_sig_t & ~side.holm_sig_lmm, ~side.holm_sig_t & side.holm_sig_lmm],
                                ["both", "t only", "LMM only"], default="neither")
    side.to_csv(OUT / "planned_t_vs_lmm.csv", index=False)
    pd.set_option("display.width", 250)
    print(side[["outcome", "contrast_label", "mean", "estimate", "ci95_lo_t", "ci95_hi_t", "ci95_lo_lmm", "ci95_hi_lmm", "p_holm_t", "p_holm_lmm", "icc", "verdict"]].round(3).to_string(index=False))
    print(side.verdict.value_counts().to_dict())


if __name__ == "__main__":
    run()
