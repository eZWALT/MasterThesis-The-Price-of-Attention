"""Shared statistics for Walter's behavioural and combo passes.

Person is the inferential unit everywhere. Condition rows are only
ever tested through person-level D_i, a Friedman block, or a
repeated-measures correlation with the person centred out.

Corrections are reported three ways on every long table:
  p_raw          the test's own p
  p_holm_family  Holm within the declared ``family`` column
  p_bh_global    Benjamini-Hochberg across the whole table
"""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd
import scipy.stats as stats
from statsmodels.stats.multitest import multipletests

CONDITIONS = ("no_ads", "inline_early", "inline_late", "block_early", "block_late")
AD_CONDITIONS = ("inline_early", "inline_late", "block_early", "block_late")
LABEL = {
    "no_ads": "no ad",
    "inline_early": "implicit early",
    "inline_late": "implicit late",
    "block_early": "explicit early",
    "block_late": "explicit late",
}

# Same weights as EEG Dataset A (models.tex).
CONTRASTS = {
    "any_ad_vs_no_ads": {
        "inline_early": 0.25, "inline_late": 0.25,
        "block_early": 0.25, "block_late": 0.25, "no_ads": -1.0,
    },
    "inline_vs_block": {
        "inline_early": 0.5, "inline_late": 0.5,
        "block_early": -0.5, "block_late": -0.5, "no_ads": 0.0,
    },
    "early_vs_late": {
        "inline_early": 0.5, "inline_late": -0.5,
        "block_early": 0.5, "block_late": -0.5, "no_ads": 0.0,
    },
    "format_x_timing": {
        "inline_early": 0.5, "inline_late": -0.5,
        "block_early": -0.5, "block_late": 0.5, "no_ads": 0.0,
    },
}
CONTRAST_LABEL = {
    "any_ad_vs_no_ads": "any ad \u2212 no ad",
    "inline_vs_block": "implicit \u2212 explicit",
    "early_vs_late": "early \u2212 late",
    "format_x_timing": "format \u00d7 timing",
}
PLANNED = ("any_ad_vs_no_ads", "inline_vs_block", "early_vs_late")

PAIRS = [
    (a, b) for i, a in enumerate(CONDITIONS) for b in CONDITIONS[i + 1:]
]


# --------------------------------------------------------------------------- #
# reshaping
# --------------------------------------------------------------------------- #
def wide(condition_table: pd.DataFrame, outcome: str) -> pd.DataFrame:
    """person × condition matrix for one outcome; rows with any NA dropped."""
    piv = condition_table.pivot_table(
        index="experiment_id", columns="condition", values=outcome, aggfunc="first"
    )
    return piv.reindex(columns=list(CONDITIONS)).dropna()


def contrast_scores(w: pd.DataFrame, contrast_id: str) -> pd.Series:
    weights = CONTRASTS[contrast_id]
    out = sum(w[c] * wgt for c, wgt in weights.items() if wgt != 0.0)
    return out.astype(float)


# --------------------------------------------------------------------------- #
# single tests
# --------------------------------------------------------------------------- #
def paired_d(series: pd.Series) -> dict:
    s = pd.Series(series).dropna().astype(float)
    n = int(len(s))
    if n < 3:
        return {"n": n}
    mean = float(s.mean())
    sd = float(s.std(ddof=1))
    se = sd / math.sqrt(n) if sd > 0 else 0.0
    t, p_t = stats.ttest_1samp(s, 0.0)
    if np.allclose(s, 0.0):
        w, p_w = np.nan, 1.0
    else:
        w, p_w = stats.wilcoxon(s, zero_method="wilcox", alternative="two-sided")
    return {
        "n": n,
        "mean": mean,
        "sd": sd,
        "ci95_lo": mean - 1.96 * se,
        "ci95_hi": mean + 1.96 * se,
        "dz": mean / sd if sd > 0 else np.nan,
        "stat": float(t),
        "p_raw": float(p_t),
        "wilcoxon_w": float(w) if w is not None else np.nan,
        "p_wilcoxon": float(p_w),
    }


def friedman(w: pd.DataFrame, columns: Iterable[str]) -> dict:
    cols = list(columns)
    block = w[cols].dropna()
    n, k = block.shape
    if n < 3:
        return {"n": n}
    chi2, p = stats.friedmanchisquare(*[block[c].to_numpy() for c in cols])
    kendall_w = chi2 / (n * (k - 1)) if n * (k - 1) > 0 else np.nan
    return {"n": int(n), "k": int(k), "stat": float(chi2), "p_raw": float(p), "kendall_w": float(kendall_w)}


def pairwise_wilcoxon(w: pd.DataFrame) -> list[dict]:
    rows = []
    for a, b in PAIRS:
        diff = (w[a] - w[b]).dropna().astype(float)
        n = int(len(diff))
        if n < 3:
            continue
        if np.allclose(diff, 0.0):
            stat, p = np.nan, 1.0
        else:
            stat, p = stats.wilcoxon(diff, zero_method="wilcox", alternative="two-sided")
        mean = float(diff.mean())
        sd = float(diff.std(ddof=1))
        # matched-pairs rank-biserial r from W: r = 1 - 2W / (n(n+1)/2)
        nz = diff[diff != 0]
        rb = (1.0 - 2.0 * stat / (len(nz) * (len(nz) + 1) / 2.0)) if len(nz) and not np.isnan(stat) else np.nan
        rows.append(
            {
                "pair": f"{a} - {b}",
                "pair_label": f"{LABEL[a]} \u2212 {LABEL[b]}",
                "n": n,
                "mean": mean,
                "sd": sd,
                "dz": mean / sd if sd > 0 else np.nan,
                "stat": float(stat) if not np.isnan(stat) else np.nan,
                "p_raw": float(p),
                "rank_biserial": float(rb) if not np.isnan(rb) else np.nan,
            }
        )
    return rows


def spearman(x: pd.Series, y: pd.Series) -> dict:
    pair = pd.concat([x, y], axis=1).dropna()
    n = int(len(pair))
    if n < 5:
        return {"n": n}
    r, p = stats.spearmanr(pair.iloc[:, 0].to_numpy(), pair.iloc[:, 1].to_numpy())
    r = float(np.asarray(r).reshape(-1)[0])
    p = float(np.asarray(p).reshape(-1)[0])
    return {"n": n, "rho": r, "stat": r, "p_raw": p}


def rmcorr(frame: pd.DataFrame, subject: str, x: str, y: str) -> dict:
    """Repeated-measures correlation (Bakdash & Marusich 2017), ANCOVA form.

    Centres x and y within person, Pearson on the residuals,
    df = N_obs - k_persons - 1.
    """
    d = frame[[subject, x, y]].dropna()
    k = d[subject].nunique()
    n = len(d)
    dof = n - k - 1
    if dof < 3:
        return {"n_obs": int(n), "n_persons": int(k)}
    xc = d[x] - d.groupby(subject)[x].transform("mean")
    yc = d[y] - d.groupby(subject)[y].transform("mean")
    if xc.std() == 0 or yc.std() == 0:
        return {"n_obs": int(n), "n_persons": int(k)}
    r = float(np.corrcoef(xc, yc)[0, 1])
    t = r * math.sqrt(dof / max(1e-12, 1 - r * r))
    p = 2 * stats.t.sf(abs(t), dof)
    return {"n_obs": int(n), "n_persons": int(k), "dof": int(dof), "rrm": r, "stat": r, "p_raw": float(p)}


def partial_spearman(frame: pd.DataFrame, x: str, y: str, z: str) -> dict:
    d = frame[[x, y, z]].dropna()
    n = len(d)
    if n < 8:
        return {"n": int(n)}
    rx, ry, rz = (stats.rankdata(d[c]) for c in (x, y, z))
    Z = np.column_stack([np.ones(n), rz])
    def resid(v):
        beta, *_ = np.linalg.lstsq(Z, v, rcond=None)
        return v - Z @ beta
    ex, ey = resid(rx), resid(ry)
    if ex.std() == 0 or ey.std() == 0:
        return {"n": int(n)}
    r = float(np.corrcoef(ex, ey)[0, 1])
    dof = n - 3
    t = r * math.sqrt(dof / max(1e-12, 1 - r * r))
    p = 2 * stats.t.sf(abs(t), dof)
    return {"n": int(n), "rho_partial": r, "stat": r, "p_raw": float(p)}


# --------------------------------------------------------------------------- #
# corrections
# --------------------------------------------------------------------------- #
def add_corrections(table: pd.DataFrame, family_col: str = "family", p_col: str = "p_raw") -> pd.DataFrame:
    out = table.copy()
    out["p_holm_family"] = np.nan
    out["p_bh_global"] = np.nan
    ok = out[p_col].notna()
    for _, idx in out.loc[ok].groupby(family_col).groups.items():
        p = out.loc[idx, p_col].to_numpy(dtype=float)
        if len(p) == 0:
            continue
        out.loc[idx, "p_holm_family"] = multipletests(p, method="holm")[1]
    p_all = out.loc[ok, p_col].to_numpy(dtype=float)
    if len(p_all):
        out.loc[ok, "p_bh_global"] = multipletests(p_all, method="fdr_bh")[1]
    out["sig_raw"] = out[p_col] < 0.05
    out["sig_holm_family"] = out["p_holm_family"] < 0.05
    out["sig_bh_global"] = out["p_bh_global"] < 0.05
    out["n_tests_in_family"] = out.groupby(family_col)[p_col].transform("count")
    out["n_tests_global"] = int(ok.sum())
    return out


def summarise(table: pd.DataFrame) -> dict:
    return {
        "n_tests": int(table["p_raw"].notna().sum()),
        "n_families": int(table["family"].nunique()),
        "hits_raw": int(table["sig_raw"].sum()),
        "hits_holm_family": int(table["sig_holm_family"].sum()),
        "hits_bh_global": int(table["sig_bh_global"].sum()),
        "expected_false_raw_at_005": float(0.05 * table["p_raw"].notna().sum()),
    }
