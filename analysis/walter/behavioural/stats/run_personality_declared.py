"""Goal 2 as Methods `tab:analysis-families` declares it.

    random-intercept LMM on Y_ic
    BFI-10 trait × the three planned contrast codes
    demographics as covariates
    Holm on the 5 trait × 3 contrast interactions, within each composite

RQ8 is the format column (implicit − explicit). RQ9 is the timing
column (early − late). Any-ad is estimated because the family names
the same three planned contrasts as the battery; it is not an RQ.

One trait at a time, so a trait is not partialled on the other four.
Traits are centred at the sample mean. The interaction coefficient on
a contrast code equals the slope of that person-level D_i on the trait
(balanced five-condition design; see run_lmm_declared.py).

A person-level OLS of D_i on the same centred trait and covariates is
written beside the LMM as a check, not a second decision rule.

Demographics enter the confirmatory model as covariates only. A
separate screen of demo-factor × D_i is written under exploratory/
and is not the family.

Writes
  outputs/confirmatory/personality_lmm.csv
  outputs/confirmatory/personality_d_ols.csv
  outputs/exploratory/personality_demo_screen.csv
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
CONF = WALTER / "behavioural" / "outputs" / "confirmatory"
EXPL = WALTER / "behavioural" / "outputs" / "exploratory"

PRIMARY = ("trust", "credibility", "manipulation", "notice")
BFI = ("bfi_e", "bfi_a", "bfi_c", "bfi_n", "bfi_o")
TRAIT_LABEL = {
    "bfi_e": "Extraversion",
    "bfi_a": "Agreeableness",
    "bfi_c": "Conscientiousness",
    "bfi_n": "Neuroticism",
    "bfi_o": "Openness",
}
CONTRAST_CODES = ("any_ad_vs_no_ads", "inline_vs_block", "early_vs_late")


def _person_covars(person: pd.DataFrame) -> pd.DataFrame:
    p = person.copy()
    p["sex"] = p["demo_sex"].fillna("Unknown").astype(str)
    fam = p["demo_familiarity"].fillna("Unknown").astype(str)
    p["familiar"] = np.where(fam.eq("Familiar"), "Familiar", "Other")
    freq = p["demo_frequency"].fillna("Unknown").astype(str)
    daily = freq.isin(["1–5 times per day", "Greater than 5 times per day"])
    p["daily"] = np.where(daily, "Daily", "Less")
    return p


def _add_codes(frame: pd.DataFrame) -> pd.DataFrame:
    d = frame.copy()
    for cid in CONTRAST_CODES:
        d[cid] = d["condition"].map(sk.CONTRASTS[cid]).astype(float)
    return d


def _wald(res, name: str) -> dict:
    if name not in res.fe_params.index:
        return {"estimate": np.nan, "se": np.nan, "ci95_lo": np.nan, "ci95_hi": np.nan, "z": np.nan, "p_raw": np.nan}
    est = float(res.fe_params[name])
    cov = res.cov_params()
    se = float(np.sqrt(cov.loc[name, name]))
    z = est / se if se > 0 else np.nan
    p = float(2 * stats.norm.sf(abs(z))) if np.isfinite(z) else np.nan
    return {
        "estimate": est,
        "se": se,
        "ci95_lo": est - 1.96 * se,
        "ci95_hi": est + 1.96 * se,
        "z": z,
        "p_raw": p,
    }


def _holm_within(table: pd.DataFrame, keys: list[str], p_col: str, out_col: str) -> pd.DataFrame:
    out = table.copy()
    out[out_col] = np.nan
    out[f"{out_col}_sig"] = False
    for _, idx in out.groupby(keys, dropna=False).groups.items():
        p = out.loc[idx, p_col]
        ok = p.notna()
        if ok.sum() == 0:
            continue
        adj = multipletests(p.loc[ok].to_numpy(dtype=float), method="holm")[1]
        out.loc[p.index[ok], out_col] = adj
        out.loc[p.index[ok], f"{out_col}_sig"] = adj < 0.05
    return out


def fit_lmm(condition: pd.DataFrame, person: pd.DataFrame) -> pd.DataFrame:
    cov = _person_covars(person)
    traits = {t: float(person[t].mean()) for t in BFI}
    rows = []
    for outcome in PRIMARY:
        base = condition[["experiment_id", "arm", "condition", outcome]].merge(
            cov[["experiment_id", "sex", "familiar", "daily", *BFI]],
            on="experiment_id",
            how="inner",
        ).dropna(subset=[outcome, *BFI])
        base = _add_codes(base)
        n_people = int(base["experiment_id"].nunique())
        for trait in BFI:
            d = base.copy()
            d["y"] = d[outcome]
            d["trait_c"] = d[trait] - traits[trait]
            formula = (
                "y ~ any_ad_vs_no_ads * trait_c + inline_vs_block * trait_c "
                "+ early_vs_late * trait_c + C(arm) + C(sex) + C(familiar) + C(daily)"
            )
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = smf.mixedlm(formula, d, groups=d["experiment_id"])
                res = model.fit(reml=True, method=["powell"])
            for cid in CONTRAST_CODES:
                rec = _wald(res, f"{cid}:trait_c")
                rec.update({
                    "family": "personality",
                    "outcome": outcome,
                    "trait": trait,
                    "trait_label": TRAIT_LABEL[trait],
                    "contrast": cid,
                    "contrast_label": sk.CONTRAST_LABEL[cid],
                    "n": n_people,
                    "converged": bool(res.converged),
                })
                rows.append(rec)
    return pd.DataFrame(rows)


def fit_d_ols(condition: pd.DataFrame, person: pd.DataFrame) -> pd.DataFrame:
    cov = _person_covars(person).set_index("experiment_id")
    traits = {t: float(person[t].mean()) for t in BFI}
    rows = []
    for outcome in PRIMARY:
        w = sk.wide(condition, outcome)
        ids = w.index.intersection(cov.index)
        w = w.loc[ids]
        for cid in CONTRAST_CODES:
            d_i = sk.contrast_scores(w, cid)
            for trait in BFI:
                frame = pd.DataFrame({
                    "D": d_i,
                    "trait_c": cov.loc[ids, trait] - traits[trait],
                    "arm": cov.loc[ids, "arm"],
                    "sex": cov.loc[ids, "sex"],
                    "familiar": cov.loc[ids, "familiar"],
                    "daily": cov.loc[ids, "daily"],
                }).dropna()
                res = smf.ols("D ~ trait_c + C(arm) + C(sex) + C(familiar) + C(daily)", frame).fit()
                est = float(res.params["trait_c"])
                se = float(res.bse["trait_c"])
                ci = res.conf_int().loc["trait_c"]
                rows.append({
                    "family": "personality_ols",
                    "outcome": outcome,
                    "trait": trait,
                    "trait_label": TRAIT_LABEL[trait],
                    "contrast": cid,
                    "contrast_label": sk.CONTRAST_LABEL[cid],
                    "n": int(len(frame)),
                    "estimate": est,
                    "se": se,
                    "ci95_lo": float(ci.iloc[0]),
                    "ci95_hi": float(ci.iloc[1]),
                    "t": float(res.tvalues["trait_c"]),
                    "p_raw": float(res.pvalues["trait_c"]),
                })
    return pd.DataFrame(rows)


def demo_screen(condition: pd.DataFrame, person: pd.DataFrame) -> pd.DataFrame:
    """Exploratory: does a collapsed demo factor predict D_i? Not the family."""
    cov = _person_covars(person).set_index("experiment_id")
    factors = ("arm", "sex", "familiar", "daily")
    rows = []
    for outcome in PRIMARY:
        w = sk.wide(condition, outcome)
        ids = w.index.intersection(cov.index)
        w = w.loc[ids]
        for cid in CONTRAST_CODES:
            d_i = sk.contrast_scores(w, cid)
            for factor in factors:
                frame = pd.DataFrame({"D": d_i, factor: cov.loc[ids, factor]}).dropna()
                if frame[factor].nunique() < 2:
                    continue
                full = smf.ols(f"D ~ C({factor})", frame).fit()
                reduced = smf.ols("D ~ 1", frame).fit()
                fstat, p_f, _ = full.compare_f_test(reduced)
                rows.append({
                    "family": "demo_screen",
                    "outcome": outcome,
                    "contrast": cid,
                    "contrast_label": sk.CONTRAST_LABEL[cid],
                    "factor": factor,
                    "n": int(len(frame)),
                    "k_levels": int(frame[factor].nunique()),
                    "f": float(fstat),
                    "p_raw": float(p_f),
                })
    return pd.DataFrame(rows)


def run() -> dict:
    CONF.mkdir(parents=True, exist_ok=True)
    EXPL.mkdir(parents=True, exist_ok=True)
    condition = pd.read_csv(GOLD / "condition_features.csv")
    person = pd.read_csv(GOLD / "person_features.csv")

    lmm = fit_lmm(condition, person)
    lmm = _holm_within(lmm, ["outcome"], "p_raw", "p_holm")
    lmm.to_csv(CONF / "personality_lmm.csv", index=False)

    ols = fit_d_ols(condition, person)
    ols = _holm_within(ols, ["outcome"], "p_raw", "p_holm")
    ols.to_csv(CONF / "personality_d_ols.csv", index=False)

    demo = demo_screen(condition, person)
    demo = _holm_within(demo, ["outcome"], "p_raw", "p_holm")
    demo.to_csv(EXPL / "personality_demo_screen.csv", index=False)

    side = lmm.merge(
        ols[["outcome", "trait", "contrast", "estimate", "ci95_lo", "ci95_hi", "p_raw", "p_holm", "p_holm_sig"]],
        on=["outcome", "trait", "contrast"],
        suffixes=("_lmm", "_ols"),
    )
    side["verdict"] = np.select(
        [
            side.p_holm_sig_lmm & side.p_holm_sig_ols,
            side.p_holm_sig_lmm & ~side.p_holm_sig_ols,
            ~side.p_holm_sig_lmm & side.p_holm_sig_ols,
        ],
        ["both", "LMM only", "OLS only"],
        default="neither",
    )
    side.to_csv(CONF / "personality_lmm_vs_ols.csv", index=False)

    summary = {
        "n_lmm": int(len(lmm)),
        "lmm_holm_hits": int(lmm["p_holm_sig"].sum()),
        "lmm_raw_hits": int((lmm["p_raw"] < 0.05).sum()),
        "ols_holm_hits": int(ols["p_holm_sig"].sum()),
        "ols_raw_hits": int((ols["p_raw"] < 0.05).sum()),
        "demo_holm_hits": int(demo["p_holm_sig"].sum()),
        "demo_raw_hits": int((demo["p_raw"] < 0.05).sum()),
        "lmm_vs_ols": side["verdict"].value_counts().to_dict(),
        "nearest_lmm": (
            lmm.sort_values("p_raw")
            .head(8)[["outcome", "trait_label", "contrast_label", "estimate", "ci95_lo", "ci95_hi", "p_raw", "p_holm"]]
            .round(4)
            .to_dict(orient="records")
        ),
        "converged": bool(lmm["converged"].all()),
    }
    (CONF / "personality_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    s = run()
    print(json.dumps(s, indent=2))
    print(f"Wrote {CONF / 'personality_lmm.csv'}")
