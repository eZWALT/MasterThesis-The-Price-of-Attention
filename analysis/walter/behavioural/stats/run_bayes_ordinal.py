"""Bayesian ordered-logit with a random intercept per person (the CLMM the
GEE could not give us). Trust is the target; behaviour_pushing is a
positive control so the reader can see what a real effect looks like
in the same model.

  y_ij ~ OrderedLogistic(eta_ij, cutpoints)
  eta_ij = a_i + beta_cond[condition] + beta_lab * lab_i + beta_pos * pos_c
  a_i ~ Normal(0, sigma_a),  sigma_a ~ HalfNormal(1.5)
  beta ~ Normal(0, 1.5)   (weakly informative on the log-odds scale)

Reports posterior mean, 95% equal-tailed interval and P(effect < 0) for each ad
condition vs no ad and for the three planned contrasts.
Usage: python run_bayes_ordinal.py [outcome ...]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import arviz as az
import numpy as np
import pandas as pd
import pymc as pm

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
OUT = WALTER / "behavioural" / "outputs" / "ordinal"
COND = list(sk.CONDITIONS)


def fit(outcome: str, draws: int = 1500, tune: int = 1500, seed: int = 7) -> pd.DataFrame:
    c = pd.read_csv(GOLD / "condition_features.csv")
    d = c[["experiment_id", "arm", "condition", "session_position", outcome]].dropna().copy()
    d["y"] = d[outcome].round().astype(int) - 1          # 0..6
    d["pid"] = pd.Categorical(d["experiment_id"]).codes
    d["cond"] = pd.Categorical(d["condition"], categories=COND).codes  # 0 = no_ads
    d["lab"] = (d["arm"] == "lab").astype(float)
    d["pos_c"] = d["session_position"] - 2.0
    n_people = d["pid"].nunique()
    K = 7

    with pm.Model():
        cut = pm.Normal("cutpoints", mu=np.linspace(-2.5, 2.5, K - 1), sigma=2.0, shape=K - 1,
                        transform=pm.distributions.transforms.ordered, initval=np.linspace(-2.5, 2.5, K - 1))
        sigma_a = pm.HalfNormal("sigma_a", 1.5)
        a_raw = pm.Normal("a_raw", 0.0, 1.0, shape=n_people)
        a = pm.Deterministic("a", a_raw * sigma_a)
        b_cond_ad = pm.Normal("b_cond_ad", 0.0, 1.5, shape=4)       # four ad conditions vs no_ads
        b_cond = pm.math.concatenate([np.zeros(1), b_cond_ad])
        b_lab = pm.Normal("b_lab", 0.0, 1.5)
        b_pos = pm.Normal("b_pos", 0.0, 1.0)
        eta = a[d["pid"].to_numpy()] + b_cond[d["cond"].to_numpy()] + b_lab * d["lab"].to_numpy() + b_pos * d["pos_c"].to_numpy()
        pm.OrderedLogistic("y", eta=eta, cutpoints=cut, observed=d["y"].to_numpy())

        # planned contrasts on the log-odds scale (no_ads coefficient is 0)
        pm.Deterministic("any_ad_vs_no_ads", pm.math.mean(b_cond_ad))
        # order of AD_CONDITIONS in COND[1:]: inline_early, inline_late, block_early, block_late
        pm.Deterministic("inline_vs_block", 0.5 * (b_cond_ad[0] + b_cond_ad[1]) - 0.5 * (b_cond_ad[2] + b_cond_ad[3]))
        pm.Deterministic("early_vs_late", 0.5 * (b_cond_ad[0] + b_cond_ad[2]) - 0.5 * (b_cond_ad[1] + b_cond_ad[3]))

        idata = pm.sample(draws=draws, tune=tune, chains=4, cores=4, target_accept=0.9,
                          random_seed=seed, progressbar=False)

    rows = []
    def add(name, samples, label):
        s = np.asarray(samples).reshape(-1)
        hdi = np.percentile(s, [2.5, 97.5])  # equal-tailed 95% interval
        rows.append({"outcome": outcome, "term": name, "label": label, "mean_logodds": float(s.mean()),
                     "ci95_lo": float(hdi[0]), "ci95_hi": float(hdi[1]),
                     "OR": float(np.exp(s.mean())), "OR_lo": float(np.exp(hdi[0])), "OR_hi": float(np.exp(hdi[1])),
                     "P_lt_0": float((s < 0).mean()), "P_gt_0": float((s > 0).mean())})
    post = idata.posterior
    for k, cond in enumerate(COND[1:]):
        add(cond, post["b_cond_ad"].values[..., k], f"{sk.LABEL[cond]} vs no ad")
    for cid in sk.PLANNED:
        add(cid, post[cid].values, sk.CONTRAST_LABEL[cid])
    add("b_lab", post["b_lab"].values, "lab vs crowd")
    add("b_pos", post["b_pos"].values, "per session position")
    add("sigma_a", post["sigma_a"].values, "person SD (log-odds)")
    out = pd.DataFrame(rows)
    rhat = az.rhat(idata, var_names=["b_cond_ad", "b_lab", "b_pos", "sigma_a", "cutpoints"])
    ess = az.ess(idata, var_names=["b_cond_ad", "b_lab", "b_pos", "sigma_a", "cutpoints"])
    out.attrs["max_rhat"] = float(max(float(v.max()) for v in rhat.data_vars.values()))
    out.attrs["min_ess_bulk"] = float(min(float(v.min()) for v in ess.data_vars.values()))
    out.attrs["divergences"] = int(idata.sample_stats["diverging"].sum())
    return out


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    outcomes = sys.argv[1:] or ["trust", "behaviour_pushing"]
    frames, diag = [], {}
    for o in outcomes:
        res = fit(o)
        diag[o] = {"max_rhat": res.attrs["max_rhat"], "min_ess_bulk": res.attrs["min_ess_bulk"], "divergences": res.attrs["divergences"]}
        frames.append(res)
        pd.set_option("display.width", 200)
        print(f"\n=== {o}   (rhat max {diag[o]['max_rhat']:.3f}, ess min {diag[o]['min_ess_bulk']:.0f}, divergences {diag[o]['divergences']})")
        print(res[["label", "mean_logodds", "ci95_lo", "ci95_hi", "OR", "OR_lo", "OR_hi", "P_lt_0"]].round(3).to_string(index=False))
    table = pd.concat(frames, ignore_index=True)
    table.to_csv(OUT / "bayes_ordinal_random_intercept.csv", index=False)
    (OUT / "bayes_ordinal_diagnostics.json").write_text(json.dumps(diag, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT / 'bayes_ordinal_random_intercept.csv'}")
