"""Ordinal and mixed models for Goal 1.

Why: the planned test is a paired t on D_i, and the Likert items are
heavy-tailed 1-7 answers. This is the model-based check that says
whether the t or the Wilcoxon is the better read, with arm, session
position, and task genre adjusted for and the person as the cluster.

Single items (1-7)      OrdinalGEE, proportional-odds logit,
                        cluster = person, sandwich SE. Coefficients
                        are log-odds of a *higher* answer. OR > 1 means
                        higher trust / notice / etc.
Composites (means)      MixedLM, random intercept per person.
Recall (ad grain, 216)  same two engines with format + timing factors.

Every model: y ~ condition (ref no_ads) + arm + position_c + task_genre.
Planned contrasts are Wald tests on the same three D weights as the
confirmatory table; Holm within outcome.
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
OUT = WALTER / "behavioural" / "outputs" / "ordinal"

ITEMS = (
    "trust", "personality_influence", "personality_changed_mind",
    "behaviour_pushing", "behaviour_manipulate",
    "notice_brands", "notice_sponsored",
    "llm_reliable", "llm_false", "llm_made_up",
    "llm_neutral", "llm_impartial", "llm_opinionated",
    "llm_relevant", "llm_helpful", "llm_convincing",
)
COMPOSITES = ("credibility", "manipulation", "notice", "helpfulness", "convincingness", "relevance", "neutrality")
PRIMARY = ("trust", "credibility", "manipulation", "notice")
RECALL = ("recall_memory", "recall_trust_shift")

COND_TERM = "C(condition, Treatment('no_ads'))"
FORMULA = f"y ~ {COND_TERM} + C(arm, Treatment('crowd')) + pos_c + C(task_genre, Treatment('Social'))"
RECALL_FORMULA = "y ~ implicit + early + C(arm, Treatment('crowd')) + pos_c + C(task_genre, Treatment('Social'))"


def _prep(table: pd.DataFrame, outcome: str) -> pd.DataFrame:
    d = table[["experiment_id", "arm", "condition", "session_position", "task_genre", outcome]].dropna().copy()
    d = d.rename(columns={outcome: "y"})
    d["pos_c"] = d["session_position"] - 2.0
    d = d.sort_values(["experiment_id", "session_position"]).reset_index(drop=True)
    return d


def _contrast_vectors(param_names: list[str]) -> dict[str, np.ndarray]:
    """Planned D weights on the four condition dummies (no_ads is the reference => weight lands on dummies only)."""
    def idx(cond: str) -> int:
        matches = [i for i, n in enumerate(param_names) if n.startswith(COND_TERM) and n.endswith(f"[T.{cond}]")]
        if len(matches) != 1:
            raise KeyError(f"{cond}: {matches} in {param_names}")
        return matches[0]
    vecs = {}
    for cid, weights in sk.CONTRASTS.items():
        v = np.zeros(len(param_names))
        for cond, wgt in weights.items():
            if cond == "no_ads" or wgt == 0.0:
                continue  # reference level: its weight is absorbed (dummies are already 'minus no_ads')
            v[idx(cond)] = wgt
        vecs[cid] = v
    return vecs


def _wald_rows(res, vecs: dict[str, np.ndarray], outcome: str, engine: str, scale: str) -> list[dict]:
    rows = []
    for cid, v in vecs.items():
        t = res.t_test(v)
        est = float(np.asarray(t.effect).reshape(-1)[0])
        se = float(np.asarray(t.sd).reshape(-1)[0])
        p = float(np.asarray(t.pvalue).reshape(-1)[0])
        row = {"engine": engine, "outcome": outcome, "contrast": cid, "contrast_label": sk.CONTRAST_LABEL[cid],
               "estimate": est, "se": se, "ci95_lo": est - 1.96 * se, "ci95_hi": est + 1.96 * se,
               "z": est / se if se > 0 else np.nan, "p_raw": p, "scale": scale}
        if scale == "log-odds":
            row.update({"OR": np.exp(est), "OR_lo": np.exp(est - 1.96 * se), "OR_hi": np.exp(est + 1.96 * se)})
        rows.append(row)
    return rows


def _condition_rows(res, param_names: list[str], outcome: str, engine: str, scale: str) -> list[dict]:
    rows = []
    for cond in sk.AD_CONDITIONS:
        name = [n for n in param_names if n.startswith(COND_TERM) and n.endswith(f"[T.{cond}]")][0]
        est = float(res.params[name]); se = float(res.bse[name]); p = float(res.pvalues[name])
        row = {"engine": engine, "outcome": outcome, "condition": cond, "condition_label": sk.LABEL[cond],
               "estimate_vs_no_ad": est, "se": se, "ci95_lo": est - 1.96 * se, "ci95_hi": est + 1.96 * se, "p_raw": p, "scale": scale}
        if scale == "log-odds":
            row.update({"OR": np.exp(est), "OR_lo": np.exp(est - 1.96 * se), "OR_hi": np.exp(est + 1.96 * se)})
        rows.append(row)
    for name in param_names:
        if name.startswith("C(arm") or name == "pos_c":
            rows.append({"engine": engine, "outcome": outcome, "condition": name, "condition_label": name,
                         "estimate_vs_no_ad": float(res.params[name]), "se": float(res.bse[name]),
                         "ci95_lo": float(res.params[name] - 1.96 * res.bse[name]), "ci95_hi": float(res.params[name] + 1.96 * res.bse[name]),
                         "p_raw": float(res.pvalues[name]), "scale": scale})
    return rows


def fit_ordinal_gee(d: pd.DataFrame):
    d = d.copy()
    d["y"] = d["y"].round().astype(int)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = sm.OrdinalGEE.from_formula(FORMULA, groups="experiment_id", data=d, cov_struct=sm.cov_struct.Independence())
        res = model.fit(maxiter=200)
    return res


def fit_lmm(d: pd.DataFrame):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = smf.mixedlm(FORMULA, d, groups=d["experiment_id"])
        res = model.fit(reml=True, method=["powell"])
    return res


def covariate_names(res) -> list[str]:
    names = list(res.params.index)
    # OrdinalGEE prepends threshold intercepts named like 'I(y>1.0)'; MixedLM appends 'Group Var'.
    return [n for n in names if not n.startswith("I(y>") and n not in ("Group Var", "Intercept")]


def full_vector(res, partial: dict[str, np.ndarray], cov_names: list[str]) -> dict[str, np.ndarray]:
    # MixedLM.t_test takes a (1, k_fe) matrix over fixed effects only; GEE takes the full parameter vector.
    names = list(res.fe_params.index) if hasattr(res, "fe_params") else list(res.params.index)
    out = {}
    for cid, v in partial.items():
        full = np.zeros((1, len(names)))
        for val, n in zip(v, cov_names):
            full[0, names.index(n)] = val
        out[cid] = full
    return out


def run_condition_models(table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    contrast_rows, cond_rows = [], []
    for outcome in ITEMS:
        if outcome not in table.columns:
            continue
        d = _prep(table, outcome)
        try:
            res = fit_ordinal_gee(d)
        except Exception as exc:  # noqa: BLE001
            print(f"  ordinal GEE failed for {outcome}: {exc}")
            continue
        cov = covariate_names(res)
        vecs = full_vector(res, _contrast_vectors(cov), cov)
        contrast_rows += _wald_rows(res, vecs, outcome, "ordinal_gee", "log-odds")
        cond_rows += _condition_rows(res, list(res.params.index), outcome, "ordinal_gee", "log-odds")
    for outcome in COMPOSITES + ("trust",):
        d = _prep(table, outcome)
        res = fit_lmm(d)
        cov = covariate_names(res)
        vecs = full_vector(res, _contrast_vectors(cov), cov)
        contrast_rows += _wald_rows(res, vecs, outcome, "lmm", "points")
        cond_rows += _condition_rows(res, list(res.params.index), outcome, "lmm", "points")
    contrasts = pd.DataFrame(contrast_rows)
    # Holm within engine × outcome over the three planned contrasts (interaction reported raw)
    contrasts["p_holm"] = np.nan
    planned = contrasts["contrast"].isin(sk.PLANNED)
    for _, idx in contrasts.loc[planned].groupby(["engine", "outcome"]).groups.items():
        contrasts.loc[idx, "p_holm"] = multipletests(contrasts.loc[idx, "p_raw"], method="holm")[1]
    contrasts["holm_sig"] = contrasts["p_holm"] < 0.05
    return contrasts, pd.DataFrame(cond_rows)


def run_recall_models(ads: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in RECALL:
        d = ads[["experiment_id", "arm", "condition", "session_position", "task_genre", outcome]].dropna().copy()
        d = d.rename(columns={outcome: "y"})
        d["pos_c"] = d["session_position"] - 2.0
        d["implicit"] = d["condition"].str.startswith("inline").astype(int)
        d["early"] = d["condition"].str.endswith("early").astype(int)
        for engine in ("ordinal_gee", "lmm"):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if engine == "ordinal_gee":
                    dd = d.copy(); dd["y"] = dd["y"].round().astype(int)
                    res = sm.OrdinalGEE.from_formula(RECALL_FORMULA, groups="experiment_id", data=dd, cov_struct=sm.cov_struct.Independence()).fit(maxiter=200)
                else:
                    res = smf.mixedlm(RECALL_FORMULA, d, groups=d["experiment_id"]).fit(reml=True, method=["powell"])
            for term, cid in (("implicit", "inline_vs_block"), ("early", "early_vs_late")):
                est = float(res.params[term]); se = float(res.bse[term]); p = float(res.pvalues[term])
                row = {"engine": engine, "outcome": outcome, "contrast": cid, "contrast_label": sk.CONTRAST_LABEL[cid],
                       "estimate": est, "se": se, "ci95_lo": est - 1.96 * se, "ci95_hi": est + 1.96 * se, "z": est / se, "p_raw": p,
                       "scale": "log-odds" if engine == "ordinal_gee" else "points"}
                if engine == "ordinal_gee":
                    row.update({"OR": np.exp(est), "OR_lo": np.exp(est - 1.96 * se), "OR_hi": np.exp(est + 1.96 * se)})
                rows.append(row)
    out = pd.DataFrame(rows)
    out["p_holm"] = np.nan
    for _, idx in out.groupby(["engine", "outcome"]).groups.items():
        out.loc[idx, "p_holm"] = multipletests(out.loc[idx, "p_raw"], method="holm")[1]
    out["holm_sig"] = out["p_holm"] < 0.05
    return out


def forest_or(contrasts: pd.DataFrame, outcomes: tuple, path: Path, title: str) -> None:
    sub = contrasts.loc[(contrasts["engine"] == "ordinal_gee") & contrasts["outcome"].isin(outcomes) & contrasts["contrast"].isin(sk.PLANNED)]
    outcomes = [o for o in outcomes if o in set(sub["outcome"])]
    fig, axes = plt.subplots(1, len(outcomes), figsize=(3.3 * len(outcomes), 3.4), sharex=True)
    axes = np.atleast_1d(axes)
    for ax, outcome in zip(axes, outcomes):
        b = sub.loc[sub["outcome"] == outcome].set_index("contrast").reindex(list(sk.PLANNED)).reset_index()
        y = np.arange(len(b))
        ax.axvline(1, color="0.6", lw=1)
        ax.errorbar(b["OR"], y, xerr=[b["OR"] - b["OR_lo"], b["OR_hi"] - b["OR"]], fmt="o", color="black", capsize=3)
        for yi, hit in zip(y, b["holm_sig"]):
            if hit:
                ax.plot(b.loc[yi, "OR"], yi, "o", color="crimson", ms=8, zorder=3)
        ax.set_xscale("log")
        ax.set_yticks(y, [sk.CONTRAST_LABEL[c] for c in b["contrast"]])
        ax.set_title(outcome.replace("_", " "))
        ax.invert_yaxis()
    axes[0].set_xlabel("odds ratio for a higher answer (log scale)")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def forest_conditions(conds: pd.DataFrame, outcomes: tuple, engine: str, path: Path, title: str) -> None:
    sub = conds.loc[(conds["engine"] == engine) & conds["outcome"].isin(outcomes) & conds["condition"].isin(sk.AD_CONDITIONS)]
    outcomes = [o for o in outcomes if o in set(sub["outcome"])]
    fig, axes = plt.subplots(1, len(outcomes), figsize=(3.3 * len(outcomes), 3.4), sharex=(engine == "ordinal_gee"))
    axes = np.atleast_1d(axes)
    for ax, outcome in zip(axes, outcomes):
        b = sub.loc[sub["outcome"] == outcome].set_index("condition").reindex(list(sk.AD_CONDITIONS)).reset_index()
        y = np.arange(len(b))
        if engine == "ordinal_gee":
            ax.axvline(1, color="0.6", lw=1)
            ax.errorbar(b["OR"], y, xerr=[b["OR"] - b["OR_lo"], b["OR_hi"] - b["OR"]], fmt="o", color="black", capsize=3)
            ax.set_xscale("log")
        else:
            ax.axvline(0, color="0.6", lw=1)
            ax.errorbar(b["estimate_vs_no_ad"], y, xerr=[b["estimate_vs_no_ad"] - b["ci95_lo"], b["ci95_hi"] - b["estimate_vs_no_ad"]], fmt="o", color="black", capsize=3)
        for yi, p in zip(y, b["p_raw"]):
            if p < 0.05:
                ax.plot(b.loc[yi, "OR" if engine == "ordinal_gee" else "estimate_vs_no_ad"], yi, "o", color="crimson", ms=8, zorder=3)
        ax.set_yticks(y, [sk.LABEL[c] for c in b["condition"]])
        ax.set_title(outcome.replace("_", " "))
        ax.invert_yaxis()
    axes[0].set_xlabel("odds ratio vs no ad" if engine == "ordinal_gee" else "points vs no ad")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    table = pd.read_csv(GOLD / "condition_features.csv")
    ads = pd.read_csv(GOLD / "advertisement_features.csv")

    contrasts, conds = run_condition_models(table)
    recall = run_recall_models(ads)
    contrasts.to_csv(OUT / "model_contrasts.csv", index=False)
    conds.to_csv(OUT / "model_conditions_vs_no_ad.csv", index=False)
    recall.to_csv(OUT / "model_recall_contrasts.csv", index=False)

    forest_or(contrasts, ("trust", "behaviour_pushing", "behaviour_manipulate", "notice_brands", "notice_sponsored"),
              OUT / "forest_or_items.png", "Ordinal GEE, planned contrasts as odds ratios. Red = Holm < .05 within item. n = 54, 270 answers.")
    forest_or(contrasts, ("llm_reliable", "llm_false", "llm_made_up", "llm_impartial", "llm_relevant"),
              OUT / "forest_or_items_credibility.png", "Ordinal GEE: credibility items and two neutrality / relevance items.")
    forest_conditions(conds, ("trust", "behaviour_pushing", "behaviour_manipulate", "notice_brands", "notice_sponsored"), "ordinal_gee",
                      OUT / "forest_or_conditions.png", "Ordinal GEE, each ad condition vs no ad (adjusted for arm, position, task). Red = raw p < .05.")
    forest_conditions(conds, PRIMARY, "lmm", OUT / "forest_lmm_conditions.png",
                      "Random-intercept LMM, each ad condition vs no ad, points on the 1-7 scale. Red = raw p < .05.")

    # side-by-side: paired t (confirmatory) vs Wilcoxon vs ordinal GEE vs LMM, primary outcomes
    conf = pd.read_csv(WALTER / "behavioural" / "outputs" / "confirmatory" / "confirmatory_planned_D.csv")
    side = conf.loc[conf["family"] == "surveys", ["outcome", "contrast", "contrast_label", "mean", "p_raw", "p_holm", "p_wilcoxon"]].rename(
        columns={"mean": "D_mean", "p_raw": "p_paired_t", "p_holm": "p_holm_t"})
    gee = contrasts.loc[(contrasts["engine"] == "ordinal_gee") & contrasts["outcome"].isin(PRIMARY), ["outcome", "contrast", "OR", "p_raw", "p_holm"]].rename(
        columns={"p_raw": "p_ordinal_gee", "p_holm": "p_holm_gee"})
    lmm = contrasts.loc[(contrasts["engine"] == "lmm") & contrasts["outcome"].isin(PRIMARY), ["outcome", "contrast", "estimate", "p_raw", "p_holm"]].rename(
        columns={"estimate": "lmm_points", "p_raw": "p_lmm", "p_holm": "p_holm_lmm"})
    side = side.merge(gee, on=["outcome", "contrast"], how="left").merge(lmm, on=["outcome", "contrast"], how="left")
    side.to_csv(OUT / "primary_four_engines.csv", index=False)

    summary = {
        "n_items_ordinal": int(contrasts.loc[contrasts["engine"] == "ordinal_gee", "outcome"].nunique()),
        "n_composites_lmm": int(contrasts.loc[contrasts["engine"] == "lmm", "outcome"].nunique()),
        "primary_four_engines": side.round(4).to_dict(orient="records"),
        "ordinal_holm_hits": contrasts.loc[(contrasts["engine"] == "ordinal_gee") & contrasts["holm_sig"], ["outcome", "contrast_label", "OR", "OR_lo", "OR_hi", "p_holm"]].round(3).to_dict(orient="records"),
        "recall": recall[["engine", "outcome", "contrast_label", "estimate", "p_raw", "p_holm"]].round(4).to_dict(orient="records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    s = run()
    pd.set_option("display.width", 220); pd.set_option("display.max_columns", 30)
    print(pd.DataFrame(s["primary_four_engines"]).to_string(index=False))
    print("\nordinal Holm hits:")
    print(pd.DataFrame(s["ordinal_holm_hits"]).to_string(index=False))
    print("\nrecall:")
    print(pd.DataFrame(s["recall"]).to_string(index=False))
    print(f"\nWrote {OUT}")
