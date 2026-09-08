"""Block 5. Does the onset-locked EEG response to *this* advertisement
predict what the person then does or says about *this* advertisement?

Event grain, laboratory arm: 72 primary-eligible advertisements
(18 people x 4 ad chats), Dataset B post - pre deltas (14 features)
joined on experiment_id x condition to

  behavioural ad table  recall_memory, recall_trust_shift (per ad),
                        notice, manipulation, trust (that chat)
  trajectory            ad_associated_shift, ad_associated_divergence
                        (Definition 6; early ads only, 36)
  utterances            next user turn (turn 3) log characters and
                        log latency (early ads only, 36)

Model, person random intercept:
    y ~ eeg_wc + late + explicit + pos_c + (1 | person)
eeg_wc = the delta centred within person and scaled to the pooled
within-person SD, so the coefficient reads "outcome units per 1
within-person SD of the ad-locked EEG response". Binary targets use
GEE binomial with an exchangeable person structure.

Headline family: Fz theta, posterior alpha, and the slow-fast tilt
(PC1 of the 14 within-person-centred deltas, theta positive) x 9
targets = 27 tests, Holm within, plus a Freedman-Lane max-|t|
permutation (reduced-model residuals permuted within person).
Exploratory: the other 12 features x 9 = 108 tests, BH over all 135.

The binary target (ad_associated_shift) is 33 shifts / 3 non-shifts
among the EEG-eligible early ads, so only three people are
informative. GEE asymptotics are not trustworthy there; the reported
p is the Freedman-Lane permutation p of a person fixed-effects linear
probability model, and the GEE numbers are kept only as a record.

Writes outputs/events/.
"""

from __future__ import annotations

import json
import warnings
import zlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

import combokit as ck

OUT = ck.OUT / "events"
UTT = ck.REPO / "analysis/trajectories/outputs/utterances.csv"
CONV = ck.REPO / "analysis/trajectories/outputs/conversations.csv"
FEATS = [f for f in ck.EEG if f not in ("eeg_pope", "eeg_kislov")]  # Dataset B carries 14 features
TARGETS = {"recall_memory": "lmm", "recall_trust_shift": "lmm", "notice": "lmm", "manipulation": "lmm", "trust": "lmm",
           "ad_associated_shift": "gee", "ad_associated_divergence": "lmm", "next_turn_log_chars": "lmm", "next_turn_log_latency": "lmm"}
N_PERM = 2000


def prepare() -> pd.DataFrame:
    b = pd.read_csv(ck.EEG_GOLD / "ad_response_features.csv")
    b = b[(b.reference_kind == "advertisement") & (b.primary_analysis_eligible == "yes")].copy()
    for short, long in ck.EEG_LONG.items():
        if short in FEATS:
            b[short] = b[f"{long}_post_minus_pre"]
    b = b[["subject_id", "experiment_id", "condition", "combined_timing_uncertainty_s", "onset_estimator"] + FEATS]
    adb = pd.read_csv(ck.GOLD / "advertisement_features.csv")
    adb = adb[adb.arm == "lab"][["experiment_id", "condition", "presentation", "timing", "session_position", "recall_memory", "recall_trust_shift", "notice", "manipulation", "trust"]]
    d = b.merge(adb, on=["experiment_id", "condition"], how="inner", validate="one_to_one")
    c = pd.read_csv(CONV); c = c[c.genre_source == "utterance"][["experiment_id", "condition", "ad_associated_shift", "ad_associated_divergence"]]
    d = d.merge(c, on=["experiment_id", "condition"], how="left", validate="one_to_one")
    u = pd.read_csv(UTT); u = u[(u.genre_source == "utterance") & (u.turn == 3)][["experiment_id", "condition", "characters", "latency_seconds"]]
    u["next_turn_log_chars"] = np.log(u["characters"].clip(lower=1)); u["next_turn_log_latency"] = np.log(u["latency_seconds"].clip(lower=0.5))
    d = d.merge(u[["experiment_id", "condition", "next_turn_log_chars", "next_turn_log_latency"]], on=["experiment_id", "condition"], how="left", validate="one_to_one")
    d.loc[d.timing == "late", ["next_turn_log_chars", "next_turn_log_latency"]] = np.nan  # no post-ad user turn after a reply-4 ad
    d["person"] = d["experiment_id"]
    d["late"] = (d.timing == "late").astype(float); d["explicit"] = (d.presentation == "explicit").astype(float)
    d["pos_c"] = d.session_position - d.session_position.mean()
    E = d[FEATS]; Ec = E - E.groupby(d.person).transform("mean")
    sc, load, ve = ck.pc1(Ec, orient_on="eeg_theta")
    d["eeg_tilt"] = sc; d.attrs["tilt_loadings"] = load.round(3).to_dict(); d.attrs["tilt_var"] = ve
    for e in FEATS + ["eeg_tilt"]:
        wc = d[e] - d.groupby("person")[e].transform("mean")
        d[f"{e}_wc"] = wc / wc.std(ddof=1)
    return d


def fit(formula: str, d: pd.DataFrame, kind: str):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if kind == "gee":
            return smf.gee(formula, groups=d["person"], data=d, family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit()
        m = smf.mixedlm(formula, d, groups=d["person"])
        for method in (["lbfgs"], ["powell"], ["nm"]):
            try:
                r = m.fit(method=method, reml=True, maxiter=2000)
                if np.all(np.isfinite(r.bse.to_numpy())):
                    return r
            except Exception:  # noqa: BLE001
                continue
    return None


def row(res, term: str, **meta) -> dict:
    if res is None or term not in res.params.index:
        return {**meta, "term": term, "beta": np.nan, "se": np.nan, "p_raw": np.nan}
    ci = res.conf_int().loc[term]
    return {**meta, "term": term, "beta": float(res.params[term]), "se": float(res.bse[term]), "z": float(res.tvalues[term]),
            "p_raw": float(res.pvalues[term]), "ci_lo": float(ci.iloc[0]), "ci_hi": float(ci.iloc[1])}


def cell_spec(sub: pd.DataFrame, t: str, e: str) -> ck.FLSpec:
    """Person fixed-effects design for one target x EEG cell."""
    P = pd.get_dummies(sub.person).to_numpy(dtype=float)
    covs = [sub.late, sub.explicit, sub.pos_c] if sub.late.nunique() > 1 else [sub.explicit, sub.pos_c]
    Z = np.column_stack([P] + covs)
    X = np.column_stack([Z, sub[f"{e}_wc"].to_numpy(dtype=float)])
    return ck.FLSpec(sub[t].to_numpy(dtype=float), Z, X, [X.shape[1] - 1], ck.person_blocks(sub.person))


def fe_ols_perm(sub: pd.DataFrame, t: str, e: str, rng: np.random.Generator, n_perm: int = 4000) -> dict:
    """Person fixed-effects linear model for one cell with a
    Freedman-Lane within-person permutation p."""
    return ck.fl_cell(cell_spec(sub, t, e), n_perm, rng)


def permutation(d: pd.DataFrame, eegs: list[str], rng: np.random.Generator) -> dict:
    """Freedman-Lane max-|t| over target x EEG cells; person fixed
    effects stand in for the random intercept."""
    specs = []
    for t in TARGETS:
        sub = d.dropna(subset=[t]).reset_index(drop=True)
        for e in eegs:
            specs.append(cell_spec(sub, t, e))
    obs, null, _ = ck.fl_maxt(specs, N_PERM, rng)
    return {"observed_max_abs_t": float(obs), "p_perm_family": float((np.sum(null >= obs) + 1) / (N_PERM + 1)),
            "null_95pct_max_abs_t": float(np.quantile(null, 0.95)), "n_perm": N_PERM, "method": "Freedman-Lane, residuals permuted within person"}


def hit_audit(d: pd.DataFrame, T: pd.DataFrame) -> list[dict]:
    """For every cell with BH < .05 or Holm < .05: how many people are
    informative (discordant on a binary target), the exact within-
    person permutation p of that single cell, leave-one-person-out
    range, and the same cell on the raw (not within-person-centred)
    delta with a plain Fisher / Mann-Whitney check."""
    out = []
    hits = T[(T.sig_bh_global) | (T.sig_holm_family) | (T.p_raw < 0.01)]
    for _, h in hits.iterrows():
        t, e = h.target, h.eeg
        sub = d.dropna(subset=[t]).reset_index(drop=True)
        y = sub[t].to_numpy(dtype=float)
        cell = ck.fl_cell(cell_spec(sub, t, e), 20000, np.random.default_rng(5))
        loo = []
        for pid in sub.person.unique():
            s2 = sub[sub.person != pid].reset_index(drop=True)
            loo.append(float(cell_spec(s2, t, e).t(s2[t].to_numpy(dtype=float))[0]))
        rec = {"target": t, "eeg": e, "n_obs": int(len(sub)), "n_persons": int(sub.person.nunique()), "fe_ols_t": cell["z"],
               "p_perm_cell_within_person": cell["p_raw"], "n_distinct_null_t": cell["n_distinct_null_t"],
               "loo_t_min": float(np.min(loo)), "loo_t_max": float(np.max(loo))}
        if set(np.unique(y)) <= {0.0, 1.0}:
            per = sub.groupby("person")[t].agg(["min", "max"])
            n_disc = int((per["min"] != per["max"]).sum())
            rec.update({"n_events": int(y.sum()), "n_nonevents": int(len(y) - y.sum()), "n_discordant_persons": n_disc})
            # raw-delta check: Mann-Whitney of the uncentred delta between shifted and not-shifted ads
            a, b_ = sub.loc[sub[t] == 1, e], sub.loc[sub[t] == 0, e]
            from scipy.stats import mannwhitneyu
            rec["mannwhitney_raw_delta_p"] = float(mannwhitneyu(a, b_, alternative="two-sided").pvalue)
            rec["raw_delta_median_shift"] = float(a.median()); rec["raw_delta_median_noshift"] = float(b_.median())
            # sign test on discordant persons: is the shifted ad the one with the larger delta?
            wins = 0
            for pid, g in sub.groupby("person"):
                if g[t].nunique() == 2:
                    wins += int(g.loc[g[t] == 1, e].mean() > g.loc[g[t] == 0, e].mean())
            from scipy.stats import binomtest
            rec["discordant_wins"] = wins
            rec["sign_test_p"] = float(binomtest(wins, n_disc, 0.5).pvalue) if n_disc else np.nan
        out.append(rec)
    return out


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    d = prepare()
    d.to_csv(OUT / "events_joined.csv", index=False)
    headline = ["eeg_fz_theta", "eeg_posterior_alpha", "eeg_tilt"]
    rows = []
    for e in FEATS + ["eeg_tilt"]:
        for t, kind in TARGETS.items():
            sub = d.dropna(subset=[t]).copy()
            covs = "late + explicit + pos_c" if sub.late.nunique() > 1 else "explicit + pos_c"
            fam = "events_headline" if e in headline else "events_all_exploratory"
            if kind == "gee":
                # Binary target with very few non-events (ad_associated_shift is 33/36 here): GEE asymptotics
                # are not trustworthy, so inference is the exact within-person permutation of a person
                # fixed-effects linear probability model; the GEE fit is kept only as a record.
                g = fit(f"{t} ~ {e}_wc + {covs}", sub, "gee")
                fe = fe_ols_perm(sub, t, e, np.random.default_rng(zlib.crc32(f"{t}|{e}".encode())))
                rows.append({"family": fam, "target": t, "eeg": e, "estimator": "FE-LPM + within-person permutation", "n_obs": len(sub), "n_persons": sub.person.nunique(),
                             "sd_y": float(sub[t].std(ddof=1)), "term": f"{e}_wc", **fe,
                             "gee_beta_logodds": float(g.params[f"{e}_wc"]) if g is not None else np.nan, "gee_p_asymptotic": float(g.pvalues[f"{e}_wc"]) if g is not None else np.nan,
                             "n_events": int(sub[t].sum()), "n_nonevents": int(len(sub) - sub[t].sum())})
                continue
            r = fit(f"{t} ~ {e}_wc + {covs}", sub, kind)
            rec = row(r, f"{e}_wc", family=fam, target=t, eeg=e, estimator=kind, n_obs=len(sub), n_persons=sub.person.nunique(), sd_y=float(sub[t].std(ddof=1)))
            # Freedman-Lane cell p (person fixed effects) next to the Wald p: 18 clusters is thin for asymptotics
            fl = ck.fl_cell(cell_spec(sub.reset_index(drop=True), t, e), 2000, np.random.default_rng(zlib.crc32(f"{t}|{e}|fl".encode())))
            rec["p_perm_cell"] = fl["p_raw"]; rec["fe_t"] = fl["z"]
            rows.append(rec)
    T = pd.DataFrame(rows)
    T["p_perm_cell"] = T["p_perm_cell"].fillna(T["p_raw"])  # binary target rows already carry the permutation p
    # the exploratory family includes the headline cells too (all 14 + tilt x 9), BH over everything
    T = ck.holm_bh(T)
    T.to_csv(OUT / "event_tests.csv", index=False)
    perm = permutation(d, headline, np.random.default_rng(3))
    perm_all = permutation(d, FEATS + ["eeg_tilt"], np.random.default_rng(4))
    audit = hit_audit(d, T)
    figure(T)
    summary = {"n_ads": int(len(d)), "n_persons": int(d.person.nunique()), "n_early_ads": int((d.late == 0).sum()),
               "tilt_loadings": d.attrs["tilt_loadings"], "tilt_var_explained": d.attrs["tilt_var"],
               "hits_holm": {f: int(T[T.family == f].sig_holm_family.sum()) for f in T.family.unique()},
               "hits_bh_global": int(T.sig_bh_global.sum()),
               "min_p_raw": {f: float(T[T.family == f].p_raw.min()) for f in T.family.unique()},
               "n_tests": {f: int(T[T.family == f].p_raw.notna().sum()) for f in T.family.unique()},
               "permutation_headline": perm, "permutation_all_exploratory": perm_all, "hit_audit": audit,
               "wald_vs_permutation": {"n_cells": int(T.p_raw.notna().sum()), "n_raw_wald_lt_05": int((T.p_raw < 0.05).sum()), "n_perm_cell_lt_05": int((T.p_perm_cell < 0.05).sum()),
                                       "spearman_wald_perm": float(T[["p_raw", "p_perm_cell"]].corr(method="spearman").iloc[0, 1])},
               "top": T.sort_values("p_raw").head(8)[["family", "target", "eeg", "n_obs", "beta", "se", "p_raw", "p_perm_cell", "p_holm_family", "p_bh_global"]].round(4).to_dict(orient="records")}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def figure(T: pd.DataFrame) -> None:
    H = T[T.family == "events_headline"].copy()
    fig, ax = plt.subplots(figsize=(10, 7))
    H["label"] = H.target + " | " + H.eeg.str.replace("eeg_", "") + "  (n=" + H.n_obs.astype(str) + ")"
    for i, (_, r) in enumerate(H.iterrows()):
        c = "tab:red" if r.p_raw < 0.05 else "0.3"
        lo, hi, b = r.ci_lo / r.sd_y, r.ci_hi / r.sd_y, r.beta / r.sd_y
        ax.plot([lo, hi], [i, i], color=c, lw=1); ax.plot(b, i, "o", color=c, ms=4)
        ax.text(1.02, i, f"raw {r.p_raw:.3f}  Holm {r.p_holm_family:.2f}", va="center", fontsize=7, transform=ax.get_yaxis_transform())
    ax.set_yticks(range(len(H)), H.label, fontsize=7); ax.invert_yaxis(); ax.axvline(0, color="k", lw=0.8); ax.set_xlim(-1.5, 1.5)
    ax.set_xlabel("outcome SDs per 1 within-person SD of the ad-locked EEG delta; 95% CI (binary shift: linear probability, permutation p)")
    ax.set_title("Block 5: onset-locked EEG response to the ad → what happened next (72 lab ads; 36 for early-only targets)", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "event_forest.png", dpi=150, bbox_inches="tight"); plt.close(fig)

    A = T.copy(); A["b_std"] = A.beta / A.sd_y
    piv = A.pivot(index="eeg", columns="target", values="b_std").loc[FEATS + ["eeg_tilt"], list(TARGETS)]
    pp = A.pivot(index="eeg", columns="target", values="p_raw").loc[piv.index, piv.columns]
    fig, ax = plt.subplots(figsize=(11, 6.5))
    im = ax.imshow(piv.to_numpy(), cmap="RdBu_r", vmin=-0.8, vmax=0.8, aspect="auto")
    for r_ in range(piv.shape[0]):
        for c_ in range(piv.shape[1]):
            ax.text(c_, r_, f"{piv.iat[r_, c_]:+.2f}" + ("*" if pp.iat[r_, c_] < 0.05 else ""), ha="center", va="center", fontsize=7)
    ax.set_xticks(range(piv.shape[1]), piv.columns, rotation=30, ha="right", fontsize=8); ax.set_yticks(range(piv.shape[0]), [i.replace("eeg_", "") for i in piv.index], fontsize=8)
    ax.set_title("All 15 EEG deltas × 9 targets (standardised coefficient; * raw p < .05; no cell survives BH)", fontsize=10)
    fig.colorbar(im, ax=ax, shrink=0.7); fig.tight_layout(); fig.savefig(OUT / "event_heat.png", dpi=150); plt.close(fig)


if __name__ == "__main__":
    s = run()
    pd.set_option("display.width", 220)
    print(json.dumps({k: v for k, v in s.items() if k not in ("top", "tilt_loadings")}, indent=2))
    print(pd.DataFrame(s["top"]).to_string(index=False))
    print(f"Wrote {OUT}")
