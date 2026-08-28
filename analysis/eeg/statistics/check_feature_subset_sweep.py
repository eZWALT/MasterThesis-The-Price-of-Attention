"""Can any choice of spectral measures make the pairwise sweep significant?

Sebastian suggested dropping features to reduce the multiplicity burden.
That advice assumes the correction runs across features. It does not:
the sweep corrects within measure, so a subset removes whole families
and leaves the surviving ones untouched.

This script settles the question exhaustively rather than by argument.
It evaluates named subsets a reader might propose, and then searches
**every one of the 65,535 non-empty subsets** of the 16 measures under
the harsher across-feature family, for Holm and for Benjamini-Hochberg.

    python analysis/eeg/statistics/check_feature_subset_sweep.py

Two closed-form facts make the search cheap and the result exact.
With p sorted ascending inside a family of m tests:

    min Holm adjusted = m * p_(1)              (Holm is monotone in rank)
    min BH adjusted   = min_j (m / j) * p_(j)

Reported in .agents/context/data-analysis/eeg/2026-08-28-posthoc-pairwise.md
"""

from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_condition_contrasts import read_csv, write_csv  # noqa: E402


ROOT = Path(__file__).resolve().parents[3]
POSTHOC = ROOT / "analysis/eeg/statistics/outputs/posthoc"
ALPHA = 0.05

ABSOLUTE = (
    "delta_power_db_uv2",
    "theta_power_db_uv2",
    "alpha_power_db_uv2",
    "beta_power_db_uv2",
    "gamma_power_db_uv2",
)
RELATIVE = (
    "delta_relative_power",
    "theta_relative_power",
    "alpha_relative_power",
    "beta_relative_power",
    "gamma_relative_power",
)
CONFIRMATORY = ("fz_theta_power_db_uv2", "posterior_alpha_power_db_uv2")
FAA = ("faa_log_f4_minus_f3",)
ENGAGEMENT = (
    "engagement_beta_over_alpha_theta",
    "engagement_pope_frontocentral_beta_over_alpha_theta",
    "engagement_kislov_central_beta16_24_over_alpha8_12",
)
ALL_FEATURES = CONFIRMATORY + ABSOLUTE + RELATIVE + FAA + ENGAGEMENT


def min_holm(p_values: np.ndarray) -> float:
    """Smallest Holm-adjusted value in a family of these raw p."""
    if p_values.size == 0:
        return 1.0
    return float(min(1.0, p_values.size * p_values.min()))


def min_bh(p_sorted: np.ndarray) -> float:
    """Smallest BH-adjusted value in a family of these raw p (sorted)."""
    if p_sorted.size == 0:
        return 1.0
    ranks = np.arange(1, p_sorted.size + 1)
    return float(min(1.0, (p_sorted.size / ranks * p_sorted).min()))


def min_by(p_sorted: np.ndarray) -> float:
    """Smallest BY-adjusted value: BH inflated by the harmonic number."""
    if p_sorted.size == 0:
        return 1.0
    factor = float(np.sum(1.0 / np.arange(1, p_sorted.size + 1)))
    return float(min(1.0, min_bh(p_sorted) * factor))


def load() -> dict[str, dict[str, np.ndarray]]:
    """Raw p per feature, per view."""
    rows: list[dict[str, str]] = []
    rows.extend(read_csv(POSTHOC / "eeg_posthoc_pairwise_dataset_a.csv"))
    rows.extend(read_csv(POSTHOC / "eeg_posthoc_pairwise_dataset_b.csv"))
    views: dict[str, dict[str, list[float]]] = {
        "dataset_a": {},
        "dataset_b_delta": {},
        "dataset_b_raw": {},
    }
    for row in rows:
        if row["dataset"] == "dataset_a":
            view = "dataset_a"
        elif row["contrast_space"] == "delta_matched_control":
            view = "dataset_b_delta"
        else:
            view = "dataset_b_raw"
        views[view].setdefault(row["feature"], []).append(
            float(row["p_t_raw"])
        )
    return {
        view: {
            feature: np.sort(np.asarray(values, dtype=float))
            for feature, values in features.items()
        }
        for view, features in views.items()
    }


def best_engagement(view_data: dict[str, dict[str, np.ndarray]]) -> str:
    """The engagement index with the smallest raw p anywhere."""
    return min(
        ENGAGEMENT,
        key=lambda feature: min(
            float(view[feature].min()) for view in view_data.values()
        ),
    )


def evaluate(
    view_data: dict[str, dict[str, np.ndarray]],
    subset: tuple[str, ...],
) -> dict[str, float]:
    """Best achievable adjusted p under both family schemes."""
    out: dict[str, float] = {}
    for view, features in view_data.items():
        pooled = np.sort(
            np.concatenate([features[name] for name in subset])
        )
        # Within-feature families: each measure corrected on its own.
        for method, function in (
            ("holm", min_holm),
            ("bh", min_bh),
            ("by", min_by),
        ):
            out[f"{view}__within_{method}"] = min(
                function(features[name]) for name in subset
            )
            # Across-feature family: one family per view per subset.
            out[f"{view}__across_{method}"] = function(pooled)
    return out


def main() -> None:
    view_data = load()
    winner = best_engagement(view_data)
    print(f"Best engagement index by raw p: {winner}\n")

    named: dict[str, tuple[str, ...]] = {
        "all 16": ALL_FEATURES,
        "drop 5 relative (11)": CONFIRMATORY + ABSOLUTE + FAA + ENGAGEMENT,
        "drop 5 absolute globals (11)": (
            CONFIRMATORY + RELATIVE + FAA + ENGAGEMENT
        ),
        "drop 3 engagement (13)": CONFIRMATORY + ABSOLUTE + RELATIVE + FAA,
        "keep best engagement only (14)": (
            CONFIRMATORY + ABSOLUTE + RELATIVE + FAA + (winner,)
        ),
        "drop relative and engagement (8)": CONFIRMATORY + ABSOLUTE + FAA,
        "drop absolute and engagement (8)": CONFIRMATORY + RELATIVE + FAA,
        "confirmatory + FAA (3)": CONFIRMATORY + FAA,
        "confirmatory only (2)": CONFIRMATORY,
        # Global delta carries the smallest raw p in the whole sweep, so a
        # one-measure family around it is the most favourable case there is.
        "global delta alone (1)": ("delta_power_db_uv2",),
    }

    methods = ("holm", "bh", "by")
    views = ("dataset_a", "dataset_b_delta", "dataset_b_raw")
    summary: list[dict[str, Any]] = []
    print("Holm, BH and BY reported separately. 'within' = one family per")
    print("measure (what the sweep does). 'across' = one family per view "
          "for the whole subset.\n")
    header = (
        f"{'subset':<32}{'k':>3}  "
        f"{'Dataset A within':>26}  {'Dataset B delta within':>26}"
    )
    print(header)
    print(
        f"{'':<32}{'':>3}  "
        + "  ".join([f"{'Holm':>8}{'BH':>9}{'BY':>9}"] * 2)
    )
    print("-" * len(header))
    for label, subset in named.items():
        scores = evaluate(view_data, subset)
        bests = {
            method: min(
                value
                for key, value in scores.items()
                if key.endswith(f"_{method}")
            )
            for method in methods
        }
        summary.append(
            {
                "subset": label,
                "n_features": len(subset),
                **{
                    f"{view}_{scheme}_{method}": round(
                        scores[f"{view}__{scheme}_{method}"], 4
                    )
                    for view in views
                    for scheme in ("within", "across")
                    for method in methods
                },
                **{
                    f"best_{method}_anywhere": round(value, 4)
                    for method, value in bests.items()
                },
                "any_significant_at_0.05": (
                    "yes" if min(bests.values()) < ALPHA else "no"
                ),
            }
        )
        cells = "  ".join(
            f"{scores[f'{view}__within_holm']:>8.3f}"
            f"{scores[f'{view}__within_bh']:>9.3f}"
            f"{scores[f'{view}__within_by']:>9.3f}"
            for view in ("dataset_a", "dataset_b_delta")
        )
        print(f"{label:<32}{len(subset):>3}  {cells}")

    print("\nExhaustive search over every non-empty subset of the 16 "
          "measures, across-feature family, each method tracked "
          "separately:")
    best = {method: 1.0 for method in methods}
    winner = {method: "" for method in methods}
    checked = 0
    for size in range(1, len(ALL_FEATURES) + 1):
        for subset in combinations(ALL_FEATURES, size):
            checked += 1
            for view, features in view_data.items():
                pooled = np.sort(
                    np.concatenate([features[name] for name in subset])
                )
                for method, value in (
                    ("holm", min_holm(pooled)),
                    ("bh", min_bh(pooled)),
                    ("by", min_by(pooled)),
                ):
                    if value < best[method]:
                        best[method] = value
                        winner[method] = (
                            f"{view} / {size} measure(s): "
                            + ", ".join(subset)
                        )
    print(f"  subsets evaluated: {checked:,}  ({checked * 3 * 3:,} "
          "subset x view x method evaluations)")
    for method in methods:
        print(
            f"  best {method.upper():<4} adjusted p anywhere: "
            f"{best[method]:.4f}   <- {winner[method]}"
        )
    overall_best = min(best.values())
    print(
        f"  subsets reaching p < {ALPHA} under any method: "
        f"{'NONE' if overall_best >= ALPHA else 'SOME - investigate'}"
    )

    summary.append(
        {
            "subset": f"EXHAUSTIVE BEST over {checked} subsets",
            "n_features": "1-16",
            **{
                f"best_{method}_anywhere": round(value, 4)
                for method, value in best.items()
            },
            "any_significant_at_0.05": "yes" if overall_best < ALPHA else "no",
        }
    )
    write_csv(POSTHOC / "eeg_posthoc_feature_subset_sweep.csv", summary)
    print("\nWrote eeg_posthoc_feature_subset_sweep.csv")


if __name__ == "__main__":
    main()
