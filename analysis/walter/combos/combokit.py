"""Helpers shared by the combo blocks (run_headline, run_forest, run_lmm,
run_turns, run_events, run_concordance, run_task_state).

Column catalogues for the three modalities, a Spearman with
Bonett-Wright CI and leave-one-out range, a sign-oriented PC1, and
the loaders for the Gold views. Person is the inferential unit.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as st

HERE = Path(__file__).resolve().parent
WALTER = HERE.parent
REPO = WALTER.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402,F401

GOLD = WALTER / "behavioural" / "outputs" / "gold"
EEG_GOLD = REPO / "src/project/logs/xdf/gold/features"
EEG_STATS = REPO / "analysis/eeg/statistics/outputs"
TRAJ_GOLD = REPO / "analysis/trajectories/outputs/gold"
OUT = HERE / "outputs"

BEH_SURVEY = ["trust", "credibility", "manipulation", "notice", "helpfulness", "convincingness", "relevance", "neutrality"]
BEH_PRIMARY = ["trust", "credibility", "manipulation", "notice"]
BEH_PROCESS = ["duration_sec", "reply_latency_ms_median", "user_msg_len_median"]
TRAJ = ["traj_n_shift", "traj_shift_rate", "traj_diversity", "traj_entropy_nats", "traj_entropy_normalised",
        "traj_max_persistence", "traj_mean_js_divergence", "traj_max_js_divergence", "traj_mean_total_variation",
        "traj_shifted_into_purchasable"]
EEG = ["eeg_fz_theta", "eeg_posterior_alpha", "eeg_theta", "eeg_alpha", "eeg_beta", "eeg_faa", "eeg_delta", "eeg_gamma",
       "eeg_rel_delta", "eeg_rel_theta", "eeg_rel_alpha", "eeg_rel_beta", "eeg_rel_gamma", "eeg_engagement", "eeg_pope",
       "eeg_kislov"]
EEG_PRIMARY = ["eeg_fz_theta", "eeg_posterior_alpha"]
# Gold EEG feature name -> short name used in the combo tables
EEG_LONG = {
    "eeg_fz_theta": "fz_theta_power_db_uv2", "eeg_posterior_alpha": "posterior_alpha_power_db_uv2",
    "eeg_theta": "theta_power_db_uv2", "eeg_alpha": "alpha_power_db_uv2", "eeg_beta": "beta_power_db_uv2",
    "eeg_faa": "faa_log_f4_minus_f3", "eeg_delta": "delta_power_db_uv2", "eeg_gamma": "gamma_power_db_uv2",
    "eeg_rel_delta": "delta_relative_power", "eeg_rel_theta": "theta_relative_power", "eeg_rel_alpha": "alpha_relative_power",
    "eeg_rel_beta": "beta_relative_power", "eeg_rel_gamma": "gamma_relative_power",
    "eeg_engagement": "engagement_beta_over_alpha_theta",
    "eeg_pope": "engagement_pope_frontocentral_beta_over_alpha_theta",
    "eeg_kislov": "engagement_kislov_central_beta16_24_over_alpha8_12",
}
PRETTY = {
    "any_ad_vs_no_ads": "any ad − no ad", "inline_vs_block": "implicit − explicit", "early_vs_late": "early − late",
    "beh": "behaviour", "traj": "trajectory", "eeg": "EEG", "proc": "process", "eeg_wholewindow": "EEG (whole window)",
}


# --------------------------------------------------------------------------- #
# loaders
# --------------------------------------------------------------------------- #
def load_D() -> pd.DataFrame:
    return pd.read_csv(GOLD / "combo_threeway_D.csv")


def load_conditions() -> pd.DataFrame:
    return pd.read_csv(GOLD / "combo_threeway.csv")


def load_conditions_lab() -> pd.DataFrame:
    return pd.read_csv(GOLD / "combo_threeway_lab.csv")


def dcols(block: list[str], contrast: str) -> list[str]:
    return [f"{v}__{contrast}" for v in block]


# --------------------------------------------------------------------------- #
# statistics
# --------------------------------------------------------------------------- #
def spearman_ci(x, y, alpha: float = 0.05) -> dict:
    """Spearman rho with Bonett-Wright (2000) Fisher-z interval and
    leave-one-out range. Returns {} when n < 5."""
    pair = pd.concat([pd.Series(np.asarray(x, dtype=float)), pd.Series(np.asarray(y, dtype=float))], axis=1).dropna()
    n = len(pair)
    if n < 5:
        return {"n": int(n)}
    a, b = pair.iloc[:, 0].to_numpy(), pair.iloc[:, 1].to_numpy()
    rho, p = st.spearmanr(a, b)
    rho = float(rho)
    se = math.sqrt((1 + rho * rho / 2) / (n - 3))
    z = np.arctanh(np.clip(rho, -0.9999, 0.9999))
    zc = st.norm.ppf(1 - alpha / 2)
    lo, hi = np.tanh(z - zc * se), np.tanh(z + zc * se)
    loo = [st.spearmanr(np.delete(a, i), np.delete(b, i))[0] for i in range(n)] if n > 5 else [rho]
    return {"n": int(n), "rho": rho, "ci_lo": float(lo), "ci_hi": float(hi), "p_raw": float(p),
            "rho_loo_min": float(np.min(loo)), "rho_loo_max": float(np.max(loo)),
            "loo_sign_stable": bool(np.min(loo) * np.max(loo) > 0)}


def pc1(frame: pd.DataFrame, orient_on: str | None = None) -> tuple[pd.Series, pd.Series, float]:
    """PC1 of the z-scored columns (complete rows). Returns scores,
    loadings (correlation of each column with the score) and the
    proportion of variance explained. Sign: the ``orient_on`` column
    loads positively (or the sum of loadings is positive)."""
    d = frame.dropna()
    z = (d - d.mean()) / d.std(ddof=1)
    z = z.loc[:, z.std().notna() & (z.std() > 0)]
    u, s, vt = np.linalg.svd(z.to_numpy(), full_matrices=False)
    comp = vt[0]
    scores = z.to_numpy() @ comp
    var_expl = float(s[0] ** 2 / np.sum(s ** 2))
    load = pd.Series([np.corrcoef(scores, z[c])[0, 1] for c in z.columns], index=z.columns)
    sign = 1.0
    if orient_on is not None and orient_on in load.index:
        sign = 1.0 if load[orient_on] >= 0 else -1.0
    elif load.sum() < 0:
        sign = -1.0
    return pd.Series(sign * scores, index=d.index), sign * load, var_expl


def pc1_loo_stability(frame: pd.DataFrame, orient_on: str | None = None) -> dict:
    """How much PC1 depends on any one row. Refit PC1 leaving each row
    out; report the smallest |Spearman| between the leave-one-out scores
    and the full-sample scores on the same rows, and the smallest
    |cosine| between the leave-one-out and full loading vectors. Values
    near 1 mean the axis does not hinge on one person; with 16 columns
    and 18 rows this is the check that matters."""
    d = frame.dropna()
    full_sc, full_load, _ = pc1(d, orient_on=orient_on)
    sc_agree, load_cos = [], []
    for i in d.index:
        sub = d.drop(index=i)
        sc, load, _ = pc1(sub, orient_on=orient_on)
        common = sc.index
        sc_agree.append(abs(pd.concat([sc, full_sc.loc[common]], axis=1).corr(method="spearman").iloc[0, 1]))
        a, b = load.reindex(full_load.index).fillna(0).to_numpy(), full_load.to_numpy()
        load_cos.append(abs(float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))))
    return {"pc1_loo_min_score_spearman": float(np.min(sc_agree)), "pc1_loo_min_loading_cosine": float(np.min(load_cos)),
            "pc1_loo_n_fits": int(len(sc_agree))}


def zmean(frame: pd.DataFrame, signs: pd.Series | None = None) -> pd.Series:
    """Unit-weighted composite: mean of z-scores, optionally sign-flipped."""
    d = frame.dropna()
    z = (d - d.mean()) / d.std(ddof=1)
    if signs is not None:
        z = z * np.sign(signs.reindex(z.columns).fillna(1.0))
    return z.mean(axis=1)


def holm_bh(table: pd.DataFrame, family_col: str = "family") -> pd.DataFrame:
    return sk.add_corrections(table, family_col=family_col)


# --------------------------------------------------------------------------- #
# Freedman-Lane permutation with persons as exchangeability blocks
# --------------------------------------------------------------------------- #
class FLSpec:
    """One regression cell for the permutation: outcome y, reduced
    design Z (person dummies + nuisance covariates), full design X
    (= Z plus the tested columns), the indices of the tested columns in
    X, and the within-person index blocks.

    Freedman & Lane (1983): fit the reduced model, permute its
    residuals within person, add them back to the reduced fit, refit
    the full model and take the t of the tested column(s). The
    outcome's association with the nuisance covariates and the EEG
    column's association with them are both preserved, which a plain
    within-person shuffle of the EEG column is not."""

    def __init__(self, y: np.ndarray, Z: np.ndarray, X: np.ndarray, test_cols: list[int], groups: list[np.ndarray]):
        self.y = np.asarray(y, dtype=float)
        self.groups = groups
        Zp = np.linalg.pinv(Z)
        self.yhat_r = Z @ (Zp @ self.y)
        self.e_r = self.y - self.yhat_r
        self.Xp = np.linalg.pinv(X)
        self.H = X @ self.Xp
        self.dof = X.shape[0] - np.linalg.matrix_rank(X)
        XtX_inv = np.linalg.pinv(X.T @ X)
        self.test_cols = test_cols
        self.v = np.array([XtX_inv[j, j] for j in test_cols])
        self.w = self.Xp[test_cols, :]

    def t(self, y: np.ndarray) -> np.ndarray:
        b = self.w @ y
        r = y - self.H @ y
        s2 = (r @ r) / self.dof
        return b / np.sqrt(s2 * self.v)

    def permuted_y(self, rng: np.random.Generator) -> np.ndarray:
        e = self.e_r.copy()
        for idx in self.groups:
            e[idx] = self.e_r[rng.permutation(idx)]
        return self.yhat_r + e


def fl_maxt(specs: list[FLSpec], n_perm: int, rng: np.random.Generator) -> tuple[float, np.ndarray, list[np.ndarray]]:
    """Family-wise max-|t| over all tested columns of all specs.
    Returns observed max |t|, its null draws, and the observed t per spec."""
    obs_t = [s.t(s.y) for s in specs]
    obs = max(float(np.max(np.abs(t))) for t in obs_t)
    null = np.empty(n_perm)
    for b in range(n_perm):
        best = 0.0
        for s in specs:
            tt = s.t(s.permuted_y(rng))
            best = max(best, float(np.max(np.abs(tt))))
        null[b] = best
    return obs, null, obs_t


def fl_cell(spec: FLSpec, n_perm: int, rng: np.random.Generator) -> dict:
    """Single-cell Freedman-Lane p for the first tested column."""
    obs = float(spec.t(spec.y)[0])
    null = np.array([spec.t(spec.permuted_y(rng))[0] for _ in range(n_perm)])
    beta = float((spec.Xp @ spec.y)[spec.test_cols[0]])
    r = spec.y - spec.H @ spec.y
    se = float(np.sqrt((r @ r) / spec.dof * spec.v[0]))
    return {"beta": beta, "se": se, "z": obs, "p_raw": float((np.sum(np.abs(null) >= abs(obs)) + 1) / (n_perm + 1)),
            "ci_lo": beta - 1.96 * se, "ci_hi": beta + 1.96 * se, "n_distinct_null_t": int(len(np.unique(null.round(8))))}


def person_blocks(person: pd.Series) -> list[np.ndarray]:
    codes = pd.factorize(person)[0]
    return [np.flatnonzero(codes == g) for g in np.unique(codes)]
