"""Felt-manipulation family: Model 1 (condition) + Model 2 (OCEAN moderation).

Outcome: Gold composite ``manipulation`` (mean of behaviour_pushing /
behaviour_manipulate).

Model 1
  Y_ic ~ C(condition) + (1 | experiment_id)
  Planned contrasts (same weights as Walter confirmatory):
    any_ad − no_ad, implicit − explicit, early − late
  Holm within this family (3 contrasts).

Model 2 (preferred)
  Person-level Δ scores from Gold contrast_scores.csv
    manipulation__any_ad_vs_no_ads
    manipulation__inline_vs_block
    manipulation__early_vs_late
  For each Δ: OLS on the five BFI traits (joint model).
  Secondary: one-at-a-time demographic OLS (categorical).
  Holm within each Δ across the five BFI coefficients.

Model 2b (optional check)
  Y ~ C(condition) * trait + (1 | experiment_id), one continuous BFI at a time.
  Reports interaction terms only.

Outputs under:
  analysis/behavioural/outputs/moderation_manipulation_ocean/
"""

from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
GOLD = REPO / "analysis" / "walter" / "behavioural" / "outputs" / "gold"
OUT = HERE / "outputs" / "moderation_manipulation_ocean"

OUTCOME = "manipulation"
FAMILY = "felt_manipulation"

CONDITIONS = ("no_ads", "inline_early", "inline_late", "block_early", "block_late")
CONTRASTS = {
    "any_ad_vs_no_ads": {
        "inline_early": 0.25,
        "inline_late": 0.25,
        "block_early": 0.25,
        "block_late": 0.25,
        "no_ads": -1.0,
    },
    "inline_vs_block": {
        "inline_early": 0.5,
        "inline_late": 0.5,
        "block_early": -0.5,
        "block_late": -0.5,
        "no_ads": 0.0,
    },
    "early_vs_late": {
        "inline_early": 0.5,
        "inline_late": -0.5,
        "block_early": 0.5,
        "block_late": -0.5,
        "no_ads": 0.0,
    },
}
CONTRAST_LABEL = {
    "any_ad_vs_no_ads": "any ad - no ad",
    "inline_vs_block": "implicit - explicit",
    "early_vs_late": "early - late",
}
PLANNED = ("any_ad_vs_no_ads", "inline_vs_block", "early_vs_late")

BFI = ("bfi_e", "bfi_a", "bfi_c", "bfi_n", "bfi_o")
BFI_LABEL = {
    "bfi_e": "Extraversion",
    "bfi_a": "Agreeableness",
    "bfi_c": "Conscientiousness",
    "bfi_n": "Neuroticism",
    "bfi_o": "Openness",
}
DEMO_CAT = ("demo_sex", "demo_education", "demo_familiarity", "demo_frequency")

ALPHA = 0.05


def _holm(pvals: list[float]) -> np.ndarray:
    if not pvals:
        return np.array([])
    return multipletests(pvals, alpha=ALPHA, method="holm")[1]


def load_analysis_long() -> tuple[pd.DataFrame, pd.DataFrame]:
    cond = pd.read_csv(GOLD / "condition_features.csv")
    person = pd.read_csv(GOLD / "person_features.csv")
    person_cols = [
        "experiment_id",
        "participant_id",
        *BFI,
        *DEMO_CAT,
        "demo_age",
        "arm",
    ]
    person_cols = [c for c in person_cols if c in person.columns]
    long = cond[
        [
            "experiment_id",
            "participant_id",
            "condition",
            "presentation",
            "timing",
            OUTCOME,
            "arm",
        ]
    ].merge(person[person_cols], on="experiment_id", how="left", suffixes=("", "_person"))
    if "participant_id_person" in long.columns:
        long = long.drop(columns=["participant_id_person"])
    if "arm_person" in long.columns:
        long = long.drop(columns=["arm_person"])
    long = long.dropna(subset=["experiment_id", "condition", OUTCOME]).copy()
    long["condition"] = pd.Categorical(long["condition"], categories=list(CONDITIONS))
    for t in BFI:
        long[t] = pd.to_numeric(long[t], errors="coerce")
        # sample-mean centered; trait is constant within person
        long[f"{t}_c"] = long[t] - long[t].mean()

    contrasts = pd.read_csv(GOLD / "contrast_scores.csv")
    delta_cols = [f"{OUTCOME}__{cid}" for cid in PLANNED]
    keep = ["experiment_id", "participant_id", "arm", *delta_cols]
    deltas = contrasts[keep].copy()
    deltas = deltas.merge(
        person[[c for c in person_cols if c != "arm"]],
        on="experiment_id",
        how="left",
        suffixes=("", "_person"),
    )
    if "participant_id_person" in deltas.columns:
        deltas = deltas.drop(columns=["participant_id_person"])
    for t in BFI:
        deltas[t] = pd.to_numeric(deltas[t], errors="coerce")
    return long, deltas


def contrast_wald(res, weights: dict[str, float], levels: tuple[str, ...]) -> dict:
    names = list(res.fe_params.index)
    vec = np.zeros(len(names))
    for lvl, w in weights.items():
        if w == 0.0 or lvl == levels[0]:
            continue
        vec[names.index(f"C(condition)[T.{lvl}]")] = w
    est = float(vec @ res.fe_params.to_numpy())
    cov = res.cov_params().loc[names, names].to_numpy()
    se = float(np.sqrt(vec @ cov @ vec))
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


def run_model1(long: pd.DataFrame) -> pd.DataFrame:
    d = long[["experiment_id", "condition", OUTCOME]].dropna().copy()
    d["condition"] = pd.Categorical(d["condition"], categories=list(CONDITIONS))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = smf.mixedlm(f"{OUTCOME} ~ C(condition)", d, groups=d["experiment_id"])
        res = model.fit(reml=True, method=["powell"])
    icc = float(res.cov_re.iloc[0, 0] / (res.cov_re.iloc[0, 0] + res.scale))
    rows = []
    for cid in PLANNED:
        r = contrast_wald(res, CONTRASTS[cid], CONDITIONS)
        r.update(
            {
                "model": "model1_lmm",
                "family": FAMILY,
                "outcome": OUTCOME,
                "contrast": cid,
                "contrast_label": CONTRAST_LABEL[cid],
                "n_people": int(d["experiment_id"].nunique()),
                "n_rows": int(len(d)),
                "icc": icc,
            }
        )
        rows.append(r)
    adj = _holm([r["p_raw"] for r in rows])
    for r, p_h in zip(rows, adj):
        r["p_holm"] = float(p_h)
        r["holm_sig"] = bool(p_h < ALPHA)
    return pd.DataFrame(rows)


def run_model2_delta_bfi(deltas: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cid in PLANNED:
        col = f"{OUTCOME}__{cid}"
        use = deltas[["experiment_id", col, *BFI]].dropna().copy()
        use = use.rename(columns={col: "delta"})
        formula = "delta ~ " + " + ".join(BFI)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = smf.ols(formula, data=use).fit()
        block = []
        for term in BFI:
            block.append(
                {
                    "model": "model2_delta_bfi",
                    "family": FAMILY,
                    "outcome": OUTCOME,
                    "contrast": cid,
                    "contrast_label": CONTRAST_LABEL[cid],
                    "moderator": term,
                    "moderator_label": BFI_LABEL[term],
                    "coef": float(res.params[term]),
                    "se": float(res.bse[term]),
                    "ci95_lo": float(res.conf_int().loc[term, 0]),
                    "ci95_hi": float(res.conf_int().loc[term, 1]),
                    "t": float(res.tvalues[term]),
                    "p_raw": float(res.pvalues[term]),
                    "n": int(res.nobs),
                    "r2": float(res.rsquared),
                }
            )
        adj = _holm([b["p_raw"] for b in block])
        for b, p_h in zip(block, adj):
            b["p_holm"] = float(p_h)
            b["holm_sig"] = bool(p_h < ALPHA)
        rows.extend(block)
    return pd.DataFrame(rows)


def run_model2_delta_demo(deltas: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cid in PLANNED:
        col = f"{OUTCOME}__{cid}"
        for demo in DEMO_CAT:
            use = deltas[["experiment_id", col, demo]].dropna().copy()
            use = use.rename(columns={col: "delta"})
            vc = use[demo].astype(str).value_counts()
            keep = vc[vc >= 3].index.tolist()
            if len(keep) < 2:
                rows.append(
                    {
                        "model": "model2_delta_demo",
                        "family": FAMILY,
                        "outcome": OUTCOME,
                        "contrast": cid,
                        "contrast_label": CONTRAST_LABEL[cid],
                        "moderator": demo,
                        "term": None,
                        "coef": np.nan,
                        "se": np.nan,
                        "p_raw": np.nan,
                        "p_holm": np.nan,
                        "holm_sig": False,
                        "n": int(len(use)),
                        "note": "skipped_sparse",
                    }
                )
                continue
            use = use[use[demo].astype(str).isin(keep)].copy()
            use[demo] = use[demo].astype(str)
            formula = f"delta ~ C({demo})"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                res = smf.ols(formula, data=use).fit()
            # overall factor test via F for the categorical block
            try:
                f_test = res.f_test([name for name in res.params.index if name != "Intercept"])
                p_overall = float(np.asarray(f_test.pvalue).reshape(-1)[0])
            except Exception:
                p_overall = np.nan
            rows.append(
                {
                    "model": "model2_delta_demo",
                    "family": FAMILY,
                    "outcome": OUTCOME,
                    "contrast": cid,
                    "contrast_label": CONTRAST_LABEL[cid],
                    "moderator": demo,
                    "term": "factor_overall",
                    "coef": np.nan,
                    "se": np.nan,
                    "p_raw": p_overall,
                    "n": int(res.nobs),
                    "r2": float(res.rsquared),
                    "note": "",
                }
            )
            for name in res.params.index:
                if name == "Intercept":
                    continue
                rows.append(
                    {
                        "model": "model2_delta_demo",
                        "family": FAMILY,
                        "outcome": OUTCOME,
                        "contrast": cid,
                        "contrast_label": CONTRAST_LABEL[cid],
                        "moderator": demo,
                        "term": name,
                        "coef": float(res.params[name]),
                        "se": float(res.bse[name]),
                        "p_raw": float(res.pvalues[name]),
                        "n": int(res.nobs),
                        "r2": float(res.rsquared),
                        "note": "",
                    }
                )
    out = pd.DataFrame(rows)
    # Holm within each contrast × moderator for level terms only; overall F separate
    out["p_holm"] = np.nan
    out["holm_sig"] = False
    for (cid, demo), g in out.groupby(["contrast", "moderator"]):
        mask = (out["contrast"] == cid) & (out["moderator"] == demo) & (out["term"] != "factor_overall")
        idxs = out.index[mask & out["p_raw"].notna()]
        if len(idxs) == 0:
            continue
        adj = _holm(out.loc[idxs, "p_raw"].tolist())
        out.loc[idxs, "p_holm"] = adj
        out.loc[idxs, "holm_sig"] = adj < ALPHA
        # also mark overall
        omask = (out["contrast"] == cid) & (out["moderator"] == demo) & (out["term"] == "factor_overall")
        if omask.any() and out.loc[omask, "p_raw"].notna().any():
            p = float(out.loc[omask, "p_raw"].iloc[0])
            out.loc[omask, "p_holm"] = p  # single test; same as raw
            out.loc[omask, "holm_sig"] = p < ALPHA
    return out


def run_model2b_interactions(long: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for trait in BFI:
        d = long[["experiment_id", "condition", OUTCOME, f"{trait}_c"]].dropna().copy()
        d = d.rename(columns={f"{trait}_c": "trait_c"})
        d["condition"] = pd.Categorical(d["condition"], categories=list(CONDITIONS))
        formula = f"{OUTCOME} ~ C(condition) * trait_c"
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = smf.mixedlm(formula, d, groups=d["experiment_id"])
                res = model.fit(reml=True, method=["powell"])
        except Exception as e:
            rows.append(
                {
                    "model": "model2b_interaction",
                    "family": FAMILY,
                    "outcome": OUTCOME,
                    "moderator": trait,
                    "moderator_label": BFI_LABEL[trait],
                    "term": None,
                    "coef": np.nan,
                    "p_raw": np.nan,
                    "note": f"failed:{type(e).__name__}",
                }
            )
            continue
        for name, coef in res.fe_params.items():
            if ":" not in str(name):
                continue
            rows.append(
                {
                    "model": "model2b_interaction",
                    "family": FAMILY,
                    "outcome": OUTCOME,
                    "moderator": trait,
                    "moderator_label": BFI_LABEL[trait],
                    "term": str(name),
                    "coef": float(coef),
                    "se": float(res.bse[name]),
                    "p_raw": float(res.pvalues[name]),
                    "n_people": int(d["experiment_id"].nunique()),
                    "note": "",
                }
            )
    out = pd.DataFrame(rows)
    if out.empty or out["p_raw"].isna().all():
        out["p_holm"] = np.nan
        out["holm_sig"] = False
        return out
    out["p_holm"] = np.nan
    out["holm_sig"] = False
    for trait, g in out.groupby("moderator"):
        idxs = g.index[g["p_raw"].notna()]
        if len(idxs) == 0:
            continue
        adj = _holm(out.loc[idxs, "p_raw"].tolist())
        out.loc[idxs, "p_holm"] = adj
        out.loc[idxs, "holm_sig"] = adj < ALPHA
    return out


def significant_summary(
    m1: pd.DataFrame, m2_bfi: pd.DataFrame, m2_demo: pd.DataFrame, m2b: pd.DataFrame
) -> pd.DataFrame:
    parts = []
    if not m1.empty:
        hit = m1[m1["holm_sig"]].copy()
        hit["source"] = "model1"
        parts.append(
            hit[
                [
                    "source",
                    "outcome",
                    "contrast",
                    "contrast_label",
                    "estimate",
                    "p_raw",
                    "p_holm",
                ]
            ].rename(columns={"estimate": "effect"})
        )
    if not m2_bfi.empty:
        hit = m2_bfi[m2_bfi["holm_sig"]].copy()
        hit["source"] = "model2_delta_bfi"
        parts.append(
            hit[
                [
                    "source",
                    "outcome",
                    "contrast",
                    "contrast_label",
                    "moderator",
                    "coef",
                    "p_raw",
                    "p_holm",
                ]
            ].rename(columns={"coef": "effect"})
        )
    if not m2_demo.empty:
        hit = m2_demo[(m2_demo["holm_sig"]) & (m2_demo["term"] == "factor_overall")].copy()
        if not hit.empty:
            hit["source"] = "model2_delta_demo"
            parts.append(
                hit[
                    [
                        "source",
                        "outcome",
                        "contrast",
                        "contrast_label",
                        "moderator",
                        "p_raw",
                        "p_holm",
                    ]
                ]
            )
    if not m2b.empty:
        hit = m2b[m2b["holm_sig"]].copy()
        if not hit.empty:
            hit["source"] = "model2b_interaction"
            parts.append(
                hit[
                    [
                        "source",
                        "outcome",
                        "moderator",
                        "term",
                        "coef",
                        "p_raw",
                        "p_holm",
                    ]
                ].rename(columns={"coef": "effect"})
            )
    if not parts:
        return pd.DataFrame(
            columns=[
                "source",
                "outcome",
                "contrast",
                "contrast_label",
                "moderator",
                "term",
                "effect",
                "p_raw",
                "p_holm",
            ]
        )
    return pd.concat(parts, ignore_index=True, sort=False)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    long, deltas = load_analysis_long()

    m1 = run_model1(long)
    m2_bfi = run_model2_delta_bfi(deltas)
    m2_demo = run_model2_delta_demo(deltas)
    m2b = run_model2b_interactions(long)
    sig = significant_summary(m1, m2_bfi, m2_demo, m2b)

    # Persist
    long.to_csv(OUT / "analysis_long.csv", index=False)
    m1.to_csv(OUT / "model1_condition_effects.csv", index=False)
    m2_bfi.to_csv(OUT / "model2_delta_moderation.csv", index=False)
    m2_demo.to_csv(OUT / "model2_delta_demographics.csv", index=False)
    m2b.to_csv(OUT / "model2_interaction_terms.csv", index=False)
    sig.to_csv(OUT / "significant_summary.csv", index=False)

    manifest = {
        "family": FAMILY,
        "outcome": OUTCOME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "gold_dir": str(GOLD),
        "n_rows_long": int(len(long)),
        "n_people_long": int(long["experiment_id"].nunique()),
        "n_people_deltas": int(deltas["experiment_id"].nunique()),
        "conditions": list(CONDITIONS),
        "planned_contrasts": list(PLANNED),
        "bfi": list(BFI),
        "demographics": list(DEMO_CAT),
        "demo_age_non_null": int(long["demo_age"].notna().sum()) if "demo_age" in long else 0,
        "alpha": ALPHA,
        "correction": "Holm within family block (Model 1: 3 contrasts; Model 2 BFI: 5 traits per contrast)",
        "outputs": [
            "analysis_long.csv",
            "model1_condition_effects.csv",
            "model2_delta_moderation.csv",
            "model2_delta_demographics.csv",
            "model2_interaction_terms.csv",
            "significant_summary.csv",
            "run_manifest.json",
        ],
    }
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote outputs to {OUT}")
    print("\nModel 1 (planned contrasts, Holm within family):")
    print(
        m1[
            ["contrast_label", "estimate", "ci95_lo", "ci95_hi", "p_raw", "p_holm", "holm_sig"]
        ].to_string(index=False)
    )
    print("\nModel 2 BFI Holm hits:")
    hits = m2_bfi[m2_bfi["holm_sig"]]
    if hits.empty:
        print("  none")
    else:
        print(
            hits[
                ["contrast_label", "moderator_label", "coef", "p_raw", "p_holm"]
            ].to_string(index=False)
        )
    print(f"\nSignificant summary rows: {len(sig)}")


if __name__ == "__main__":
    main()
