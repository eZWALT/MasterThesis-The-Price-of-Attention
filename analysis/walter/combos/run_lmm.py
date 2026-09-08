"""Block 3. Within-person EEG state and the behavioural outcome, as a
mixed model instead of a correlation of D's.

Laboratory arm, 18 people x 5 conditions = 90 rows (Dataset A k=37
condition medians joined to the chat's survey and process scores).

Model A, state association (90 rows):
    y ~ C(condition) + session_position + eeg_wc + (1 | person)
  eeg_wc is the EEG feature centred within person and scaled to the
  pooled within-person SD. The coefficient is Likert points (or log
  units) per 1 within-person SD of EEG, adjusted for condition and
  order. This is the rmcorr question with the design taken out.

Model B, moderation (72 advertisement rows):
    y ~ late + explicit + session_position + eeg_wc
        + late:eeg_wc + explicit:eeg_wc + (1 | person)
  Does the timing (or format) effect on y depend on the person's EEG
  state in that chat? Two interaction tests per model.

Outcomes: trust, credibility, manipulation, notice, log reply
latency, log message length. EEG: Fz theta, posterior alpha, and the
slow-fast tilt (PC1 of the 16 within-person-centred features, theta
positive). Holm within each family; plus a Freedman-Lane max-|t|
permutation (reduced-model residuals permuted within person, 2,000
draws, person fixed effects in place of the random intercept) as a
family-wise check that does not assume independent tests.

Writes outputs/lmm/.
"""

from __future__ import annotations

import json
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

import combokit as ck
from combokit import sk

OUT = ck.OUT / "lmm"
OUTCOMES = {"trust": "trust", "credibility": "credibility", "manipulation": "manipulation", "notice": "notice",
            "log_latency": "reply_latency_ms_median", "log_msglen": "user_msg_len_median"}
EEGS = ["eeg_fz_theta", "eeg_posterior_alpha", "eeg_tilt"]
N_PERM = 2000


def prepare() -> pd.DataFrame:
    L = ck.load_conditions_lab().copy()
    L["person"] = L["experiment_id"]
    L["log_latency"] = np.log(L["reply_latency_ms_median"])
    L["log_msglen"] = np.log(L["user_msg_len_median"])
    L["late"] = (L["timing"] == "late").astype(float)
    L["explicit"] = (L["presentation"] == "explicit").astype(float)
    L["pos_c"] = L["session_position"] - L["session_position"].mean()
    # slow-fast tilt: PC1 of within-person-centred EEG features, theta positive
    E = L[ck.EEG].copy()
    Ec = E - E.groupby(L["person"]).transform("mean")
    sc, load, ve = ck.pc1(Ec, orient_on="eeg_theta")
    L["eeg_tilt"] = sc
    L.attrs["tilt_loadings"] = load.round(3).to_dict(); L.attrs["tilt_var"] = ve
    for e in EEGS:
        wc = L[e] - L.groupby("person")[e].transform("mean")
        L[f"{e}_wc"] = wc / wc.std(ddof=1)
    return L


def fit(formula: str, data: pd.DataFrame):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = smf.mixedlm(formula, data, groups=data["person"])
        for method in (["lbfgs"], ["powell"], ["nm"]):
            try:
                r = m.fit(method=method, reml=True, maxiter=2000)
                if np.all(np.isfinite(r.bse.to_numpy())):
                    return r
            except Exception:  # noqa: BLE001
                continue
    return None


def coef_row(res, term: str) -> dict:
    if res is None or term not in res.params.index:
        return {"beta": np.nan, "se": np.nan, "z": np.nan, "p_raw": np.nan}
    return {"beta": float(res.params[term]), "se": float(res.bse[term]), "z": float(res.tvalues[term]), "p_raw": float(res.pvalues[term]),
            "ci_lo": float(res.conf_int().loc[term, 0]), "ci_hi": float(res.conf_int().loc[term, 1])}


def specs_for(L: pd.DataFrame, model: str) -> list[ck.FLSpec]:
    """Freedman-Lane specs (person fixed effects stand in for the random
    intercept) for every outcome x EEG cell of one model family."""
    data = L if model == "A" else L[L.condition != "no_ads"].reset_index(drop=True)
    P = pd.get_dummies(data["person"]).to_numpy(dtype=float)
    blocks = ck.person_blocks(data["person"])
    specs = []
    for e in EEGS:
        x = data[f"{e}_wc"].to_numpy(dtype=float)
        if model == "A":
            C = pd.get_dummies(data["condition"], drop_first=True).to_numpy(dtype=float)
            Z = np.column_stack([P, C, data["pos_c"]]); X = np.column_stack([Z, x]); cols = [X.shape[1] - 1]
        elif model == "B0":
            Z = np.column_stack([P, data["late"], data["explicit"], data["pos_c"]]); X = np.column_stack([Z, x]); cols = [X.shape[1] - 1]
        else:
            Z = np.column_stack([P, data["late"], data["explicit"], data["pos_c"], x])
            X = np.column_stack([Z, data["late"] * x, data["explicit"] * x]); cols = [X.shape[1] - 2, X.shape[1] - 1]
        for o in OUTCOMES:
            specs.append(ck.FLSpec(data[o].to_numpy(dtype=float), Z, X, cols, blocks))
    return specs


def permutation_family(L: pd.DataFrame, model: str, rng: np.random.Generator) -> tuple[float, np.ndarray]:
    obs, null, _ = ck.fl_maxt(specs_for(L, model), N_PERM, rng)
    return obs, null


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    L = prepare()
    rows = []
    ad = L[L.condition != "no_ads"].reset_index(drop=True)
    for e in EEGS:
        for o, raw in OUTCOMES.items():
            rA = fit(f"{o} ~ C(condition, Treatment('no_ads')) + pos_c + {e}_wc", L)
            rows.append({"family": "A_state_association", "model": "A", "outcome": o, "eeg": e, "term": f"{e}_wc", "n_obs": len(L), "n_persons": L.person.nunique(),
                         "converged": rA is not None and bool(rA.converged), "sd_y": float(L[o].std(ddof=1)), **coef_row(rA, f"{e}_wc")})
            rB = fit(f"{o} ~ late + explicit + pos_c + {e}_wc + late:{e}_wc + explicit:{e}_wc", ad)
            for term in (f"late:{e}_wc", f"explicit:{e}_wc"):
                rows.append({"family": "B_moderation", "model": "B", "outcome": o, "eeg": e, "term": term, "n_obs": len(ad), "n_persons": ad.person.nunique(),
                             "converged": rB is not None and bool(rB.converged), "sd_y": float(ad[o].std(ddof=1)), **coef_row(rB, term)})
            # main effect within the four advertisement chats: model without interactions
            rB0 = fit(f"{o} ~ late + explicit + pos_c + {e}_wc", ad)
            rows.append({"family": "B0_main_within_ads", "model": "B0", "outcome": o, "eeg": e, "term": f"{e}_wc", "n_obs": len(ad), "n_persons": ad.person.nunique(),
                         "converged": rB0 is not None and bool(rB0.converged), "sd_y": float(ad[o].std(ddof=1)), **coef_row(rB0, f"{e}_wc")})
    T = ck.holm_bh(pd.DataFrame(rows))
    T.to_csv(OUT / "lmm_tests.csv", index=False)
    rng = np.random.default_rng(7)
    perm = {}
    for model in ("A", "B0", "B"):
        obs, null = permutation_family(L, model, rng)
        perm[model] = {"observed_max_abs_t": float(obs), "p_perm_family": float((np.sum(null >= obs) + 1) / (N_PERM + 1)),
                       "null_95pct_max_abs_t": float(np.quantile(null, 0.95)), "n_perm": N_PERM, "method": "Freedman-Lane, residuals permuted within person"}
    figure(T)
    summary = {"tilt_loadings": L.attrs["tilt_loadings"], "tilt_var_explained": L.attrs["tilt_var"],
               "hits_holm": {f: int(T[T.family == f].sig_holm_family.sum()) for f in T.family.unique()},
               "min_p_raw": {f: float(T[T.family == f].p_raw.min()) for f in T.family.unique()},
               "n_tests": {f: int(T[T.family == f].p_raw.notna().sum()) for f in T.family.unique()},
               "n_not_converged": int((~T.converged).sum()),
               "permutation_maxT": perm,
               "top": T.sort_values("p_raw").head(8)[["family", "outcome", "eeg", "term", "beta", "se", "p_raw", "p_holm_family"]].round(4).to_dict(orient="records")}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def figure(T: pd.DataFrame) -> None:
    fams = [("A_state_association", "Model A: EEG state → outcome,\nadjusted for condition and order (90 rows)"),
            ("B0_main_within_ads", "Model B0: EEG state → outcome\nwithin the four ad chats (72 rows)"),
            ("B_moderation", "Model B: EEG state × timing / × format\ninteractions (72 ad rows)")]
    fig, axes = plt.subplots(1, 3, figsize=(18, 7), gridspec_kw={"width_ratios": [1, 1, 2]})
    for ax, (fam, title) in zip(axes, fams):
        sub = T[T.family == fam].copy()
        sub["label"] = sub.apply(lambda r: f"{r.outcome} | {r.eeg.replace('eeg_', '')}" + ("" if ":" not in r.term else f" × {r.term.split(':')[0]}"), axis=1)
        y = np.arange(len(sub))
        for i, (_, r) in enumerate(sub.iterrows()):
            c = "tab:red" if r.p_raw < 0.05 else "0.3"
            ax.plot([r.ci_lo / r.sd_y, r.ci_hi / r.sd_y], [i, i], color=c, lw=1)
            ax.plot(r.beta / r.sd_y, i, "o", color=c, ms=4)
        ax.set_yticks(y, sub.label, fontsize=6.5); ax.invert_yaxis(); ax.axvline(0, color="k", lw=0.8); ax.set_xlim(-1.2, 1.2)
        ax.set_title(title, fontsize=9); ax.set_xlabel("outcome SDs per 1 within-person SD of EEG (95% CI)", fontsize=8)
    fig.suptitle("Block 3: mixed models with a person random intercept; red = raw p < .05; no cell survives Holm or the within-person max-|t| permutation", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "lmm_forest.png", dpi=150); plt.close(fig)


if __name__ == "__main__":
    s = run()
    pd.set_option("display.width", 220)
    print(json.dumps({k: v for k, v in s.items() if k != "top"}, indent=2))
    print(pd.DataFrame(s["top"]).to_string(index=False))
    print(f"Wrote {OUT}")
