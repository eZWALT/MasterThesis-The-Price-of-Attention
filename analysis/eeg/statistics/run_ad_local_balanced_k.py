"""Fixed-k Dataset A around-onset medians, k = 30..70.

Exploratory only. Does not touch Gold or ICA. Reuses the frozen
exhaustive arrays (k nearest retained tiles to each visual onset).

Two rules:

- saturate: keep all 18 people; short conversations use every tile they
  have (the exhaustive k-grid). This does **not** equalize n_tiles.
- complete: drop anyone with fewer than k tiles in any of the five
  conditions. Survivors all have exactly k tiles on every ad condition.
  n falls below 18 as soon as k exceeds the shortest chat (37).

The equal-n rule without dropping anyone is k = 37, not 50.

    python analysis/eeg/statistics/run_ad_local_balanced_k.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_condition_contrasts import FEATURE_TIERS, holm_adjust, write_csv  # noqa: E402
from build_posthoc_pairwise import bh_adjust, by_adjust  # noqa: E402
from run_ad_local_k_exhaustive import (  # noqa: E402
    A_CONTRASTS,
    A_PRIMARY,
    A_WEIGHTS,
    FEATURES,
    scores_from_values,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ARRAYS = (
    REPOSITORY_ROOT
    / "analysis/eeg/statistics/outputs/sensitivity/ad_local_epochs/exhaustive/arrays.npz"
)
OUTPUT = (
    REPOSITORY_ROOT
    / "analysis/eeg/statistics/outputs/sensitivity/ad_local_epochs/balanced_k"
)
FIGURES = (
    REPOSITORY_ROOT
    / "analysis/eeg/analysis/outputs/figures/ad_local_epochs/balanced_k"
)
K_MIN = 30
K_MAX = 70
AROUND = 0
INK = "#12202A"
SLATE = "#5C6B73"
CLAY = "#C45C26"
NAVY = "#1B3A4B"


def test_scores(scores: np.ndarray) -> dict[str, np.ndarray]:
    """scores: (n_contrast, n_feat, n_subj)."""
    n = scores.shape[-1]
    mean = scores.mean(axis=-1)
    sd = scores.std(axis=-1, ddof=1)
    se = sd / math.sqrt(n)
    critical = float(stats.t.ppf(0.975, n - 1)) if n > 1 else math.nan
    with np.errstate(invalid="ignore", divide="ignore"):
        dz = mean / sd
        t_stat = dz * math.sqrt(n)
    p_raw = 2.0 * stats.t.sf(np.abs(t_stat), n - 1)
    return {
        "n": np.full(mean.shape, n),
        "mean": mean,
        "sd": sd,
        "se": se,
        "critical": np.full(mean.shape, critical),
        "dz": dz,
        "t": t_stat,
        "p_raw": p_raw,
    }


def rows_for_k(
    *,
    k: int,
    rule: str,
    scores: np.ndarray,
    keep: np.ndarray,
    subjects: np.ndarray,
    n_saturated_cells: int,
) -> list[dict[str, Any]]:
    kept_scores = scores[:, :, keep]
    stats_k = test_scores(kept_scores)
    n = int(keep.sum())
    dropped = [str(name) for name, ok in zip(subjects, keep) if not ok]
    holm = np.full((len(A_CONTRASTS), len(FEATURES)), np.nan)
    bh = np.full_like(holm, np.nan)
    by = np.full_like(holm, np.nan)
    for f_i in range(len(FEATURES)):
        family = stats_k["p_raw"][:A_PRIMARY, f_i].tolist()
        holm[:A_PRIMARY, f_i] = holm_adjust(family)
        bh[:A_PRIMARY, f_i] = bh_adjust(family)
        by[:A_PRIMARY, f_i] = by_adjust(family)
    rows: list[dict[str, Any]] = []
    for c_i, contrast in enumerate(A_CONTRASTS):
        primary = c_i < A_PRIMARY
        for f_i, feature in enumerate(FEATURES):
            p_h = holm[c_i, f_i]
            rows.append(
                {
                    "dataset": "A",
                    "selection": "around",
                    "rule": rule,
                    "k_epochs": k,
                    "n_participants": n,
                    "n_saturated_cells": n_saturated_cells,
                    "dropped_subjects": ";".join(dropped),
                    "contrast_id": contrast,
                    "contrast_tier": "primary" if primary else "secondary",
                    "feature": feature,
                    "feature_tier": FEATURE_TIERS[feature],
                    "mean_difference": float(stats_k["mean"][c_i, f_i]),
                    "sd_difference": float(stats_k["sd"][c_i, f_i]),
                    "se_difference": float(stats_k["se"][c_i, f_i]),
                    "ci_lower": float(
                        stats_k["mean"][c_i, f_i]
                        - stats_k["critical"][c_i, f_i] * stats_k["se"][c_i, f_i]
                    ),
                    "ci_upper": float(
                        stats_k["mean"][c_i, f_i]
                        + stats_k["critical"][c_i, f_i] * stats_k["se"][c_i, f_i]
                    ),
                    "cohen_dz": float(stats_k["dz"][c_i, f_i]),
                    "t_statistic": float(stats_k["t"][c_i, f_i]),
                    "degrees_of_freedom": n - 1,
                    "p_t_raw": float(stats_k["p_raw"][c_i, f_i]),
                    "p_t_holm": "" if not primary else float(p_h),
                    "p_t_bh": "" if not primary else float(bh[c_i, f_i]),
                    "p_t_by": "" if not primary else float(by[c_i, f_i]),
                    "holm_significant": (
                        "yes" if primary and p_h < 0.05 else "no"
                    ),
                }
            )
    return rows


def plot_balance(coverage: list[dict[str, Any]], comparison: list[dict[str, Any]]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    ks = [row["k_epochs"] for row in coverage if row["rule"] == "complete"]
    n_keep = [row["n_participants"] for row in coverage if row["rule"] == "complete"]
    n_sat = [row["n_saturated_cells"] for row in coverage if row["rule"] == "complete"]

    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.4), constrained_layout=True)
    axes[0].plot(ks, n_keep, color=NAVY, lw=2)
    axes[0].axvline(37, color=CLAY, ls="--", lw=1, label="k = 37 (min chat)")
    axes[0].axvline(50, color=SLATE, ls=":", lw=1, label="k = 50")
    axes[0].set_xlabel("k tiles nearest the onset")
    axes[0].set_ylabel("People with all five cells ≥ k")
    axes[0].set_ylim(0, 19)
    axes[0].set_title("Complete-case n")
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].plot(ks, n_sat, color=CLAY, lw=2)
    axes[1].axvline(37, color=CLAY, ls="--", lw=1)
    axes[1].axvline(50, color=SLATE, ls=":", lw=1)
    axes[1].set_xlabel("k tiles nearest the onset")
    axes[1].set_ylabel("Cells using fewer than k tiles")
    axes[1].set_title("Saturation if you keep n = 18")
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(colors=INK)
    fig.savefig(FIGURES / "coverage.png", dpi=160, bbox_inches="tight", facecolor="white")
    fig.savefig(FIGURES / "coverage.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    planned = [
        row
        for row in comparison
        if row["contrast_id"] == "early_vs_late"
        and row["feature"] == "posterior_alpha_power_db_uv2"
    ]
    fig, ax = plt.subplots(figsize=(6.4, 3.6), constrained_layout=True)
    for rule, color, label in (
        ("saturate", SLATE, "Keep n = 18 (short chats saturate)"),
        ("complete", NAVY, "Drop short chats (equal n_tiles)"),
    ):
        chunk = [row for row in planned if row["rule"] == rule]
        ax.plot(
            [row["k_epochs"] for row in chunk],
            [row["cohen_dz"] for row in chunk],
            color=color,
            lw=2,
            label=label,
        )
        hits = [row for row in chunk if row["holm_significant"] == "yes"]
        if hits:
            ax.scatter(
                [row["k_epochs"] for row in hits],
                [row["cohen_dz"] for row in hits],
                color=CLAY if rule == "saturate" else NAVY,
                s=18,
                zorder=3,
            )
    ax.axvline(37, color=CLAY, ls="--", lw=1)
    ax.axhline(0, color=SLATE, lw=0.6)
    ax.set_xlabel("k tiles nearest the onset")
    ax.set_ylabel("Early − late posterior alpha  $d_z$")
    ax.set_title("Timing contrast, around-onset median")
    ax.legend(frameon=False, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(
        FIGURES / "early_vs_late_posterior_alpha.png",
        dpi=160,
        bbox_inches="tight",
        facecolor="white",
    )
    fig.savefig(
        FIGURES / "early_vs_late_posterior_alpha.pdf",
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)


def run() -> None:
    packed = np.load(ARRAYS)
    a_values = packed["a_values"]
    a_count = packed["a_count"]
    subjects = packed["subjects"]
    around_values = a_values[AROUND]
    around_count = a_count[AROUND]
    comparison: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []

    for k in range(K_MIN, K_MAX + 1):
        k_i = k - 1
        counts = around_count[k_i]
        complete_keep = (counts >= k).all(axis=1)
        n_sat = int((counts < k).sum())
        # values[k]: (n_subj, n_cell, n_feat) → (n_subj, n_contrast, n_feat)
        # test_scores wants (n_contrast, n_feat, n_subj).
        scores = np.transpose(
            scores_from_values(around_values[k_i], A_WEIGHTS), (1, 2, 0)
        )
        saturate_keep = np.ones(len(subjects), dtype=bool)
        comparison.extend(
            rows_for_k(
                k=k,
                rule="saturate",
                scores=scores,
                keep=saturate_keep,
                subjects=subjects,
                n_saturated_cells=n_sat,
            )
        )
        comparison.extend(
            rows_for_k(
                k=k,
                rule="complete",
                scores=scores,
                keep=complete_keep,
                subjects=subjects,
                n_saturated_cells=n_sat,
            )
        )
        for rule, keep in (("saturate", saturate_keep), ("complete", complete_keep)):
            dropped = [str(name) for name, ok in zip(subjects, keep) if not ok]
            coverage.append(
                {
                    "k_epochs": k,
                    "rule": rule,
                    "n_participants": int(keep.sum()),
                    "n_saturated_cells": n_sat,
                    "dropped_subjects": ";".join(dropped),
                }
            )

    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT / "comparison.csv", comparison)
    write_csv(OUTPUT / "coverage.csv", coverage)

    def planned(rule: str, k: int) -> list[dict[str, Any]]:
        return [
            row
            for row in comparison
            if row["rule"] == rule
            and row["k_epochs"] == k
            and row["contrast_tier"] == "primary"
            and row["feature"]
            in ("fz_theta_power_db_uv2", "posterior_alpha_power_db_uv2")
        ]

    snapshot_ks = (30, 37, 50, 55, 70)
    snapshots = {
        f"{rule}_k{k}": [
            {
                "contrast": row["contrast_id"],
                "feature": row["feature"],
                "n": row["n_participants"],
                "dz": round(row["cohen_dz"], 3),
                "holm": None
                if row["p_t_holm"] == ""
                else round(float(row["p_t_holm"]), 4),
                "holm_hit": row["holm_significant"],
            }
            for row in planned(rule, k)
        ]
        for rule in ("saturate", "complete")
        for k in snapshot_ks
    }
    holm_complete = [
        row
        for row in comparison
        if row["rule"] == "complete" and row["holm_significant"] == "yes"
        and row["feature"]
        in ("fz_theta_power_db_uv2", "posterior_alpha_power_db_uv2")
    ]
    manifest = {
        "exploratory": True,
        "confirmatory_untouched": True,
        "k_min": K_MIN,
        "k_max": K_MAX,
        "max_equal_n_without_dropping": 37,
        "n_at_k50_complete": next(
            row["n_participants"]
            for row in coverage
            if row["k_epochs"] == 50 and row["rule"] == "complete"
        ),
        "n_at_k70_complete": next(
            row["n_participants"]
            for row in coverage
            if row["k_epochs"] == 70 and row["rule"] == "complete"
        ),
        "snapshots": snapshots,
        "planned_complete_holm_hits": [
            {
                "k": row["k_epochs"],
                "n": row["n_participants"],
                "contrast": row["contrast_id"],
                "feature": row["feature"],
                "dz": round(row["cohen_dz"], 3),
                "holm": round(float(row["p_t_holm"]), 4),
            }
            for row in holm_complete
        ],
    }
    (OUTPUT / "findings.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    plot_balance(coverage, comparison)
    print(json.dumps({key: manifest[key] for key in (
        "max_equal_n_without_dropping",
        "n_at_k50_complete",
        "n_at_k70_complete",
        "planned_complete_holm_hits",
    )}, indent=2))


if __name__ == "__main__":
    run()
