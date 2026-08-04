"""Validate literature-grounded EEG engagement feature implementations."""

from __future__ import annotations

import argparse
import json
import math
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import spearmanr

from build_condition_features import read_csv


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
FEATURE_ROOT = REPOSITORY_ROOT / "src/project/logs/xdf/gold/features"
DEFAULT_CONDITION_EPOCHS = FEATURE_ROOT / "condition_epoch_features.csv"
DEFAULT_AD_EPOCHS = FEATURE_ROOT / "ad_epoch_features.csv"
DEFAULT_POLICY = REPOSITORY_ROOT / (
    "analysis/eeg/preprocessing/silver/signal/cleaning_policy.json"
)
DEFAULT_OUTPUT = FEATURE_ROOT / "engagement_feature_validation.json"

ENGAGEMENT_FEATURES = (
    "engagement_beta_over_alpha_theta",
    "engagement_pope_frontocentral_beta_over_alpha_theta",
    "engagement_kislov_central_beta16_24_over_alpha8_12",
)


def summarize(values: np.ndarray) -> dict[str, float | int]:
    return {
        "count": int(values.size),
        "minimum": float(np.min(values)),
        "q25": float(np.quantile(values, 0.25)),
        "median": float(np.median(values)),
        "q75": float(np.quantile(values, 0.75)),
        "maximum": float(np.max(values)),
    }


def retained_values(
    rows: list[dict[str, str]], feature: str
) -> np.ndarray:
    return np.asarray(
        [
            float(row[feature])
            for row in rows
            if row["retained_by_policy"] == "yes"
        ],
        dtype=float,
    )


def validate_dataset(rows: list[dict[str, str]]) -> dict[str, Any]:
    missing = [
        feature for feature in ENGAGEMENT_FEATURES if feature not in rows[0]
    ]
    if missing:
        raise ValueError(f"Missing engagement features: {missing}")

    summaries: dict[str, dict[str, float | int]] = {}
    finite = True
    positive = True
    for feature in ENGAGEMENT_FEATURES:
        values = retained_values(rows, feature)
        finite = finite and bool(np.all(np.isfinite(values)))
        positive = positive and bool(np.all(values > 0))
        summaries[feature] = summarize(values)

    correlations: dict[str, dict[str, float | int]] = {}
    for left, right in combinations(ENGAGEMENT_FEATURES, 2):
        left_values = retained_values(rows, left)
        right_values = retained_values(rows, right)
        result = spearmanr(left_values, right_values)
        correlations[f"{left}__vs__{right}"] = {
            "n": int(left_values.size),
            "spearman_rho": float(result.statistic),
            "p_value": float(result.pvalue),
        }

    return {
        "row_count": len(rows),
        "retained_row_count": sum(
            row["retained_by_policy"] == "yes" for row in rows
        ),
        "all_retained_values_finite": finite,
        "all_retained_values_positive": positive,
        "summaries": summaries,
        "pairwise_correlations": correlations,
    }


def validate(
    condition_epochs_path: Path,
    ad_epochs_path: Path,
    policy_path: Path,
    expected_policy_status: str,
    expected_threshold_uv: float,
) -> dict[str, Any]:
    condition_rows = read_csv(condition_epochs_path)
    ad_rows = read_csv(ad_epochs_path)
    with policy_path.open(encoding="utf-8") as handle:
        policy = json.load(handle)
    condition_report = validate_dataset(condition_rows)
    ad_report = validate_dataset(ad_rows)
    checks = {
        "policy_status_matches_expected": (
            policy["epoch_rejection"]["status"] == expected_policy_status
        ),
        "threshold_matches_expected": math.isclose(
            float(policy["epoch_rejection"]["max_peak_to_peak_uv"]),
            expected_threshold_uv,
        ),
        "condition_values_are_valid": (
            condition_report["all_retained_values_finite"]
            and condition_report["all_retained_values_positive"]
        ),
        "ad_values_are_valid": (
            ad_report["all_retained_values_finite"]
            and ad_report["all_retained_values_positive"]
        ),
    }
    return {
        "validation_status": "pass" if all(checks.values()) else "fail",
        "definitions": {
            "engagement_beta_over_alpha_theta": (
                "Global beta 13-30 Hz / (alpha 8-13 Hz + theta 4-8 Hz); "
                "Pope-family index."
            ),
            "engagement_pope_frontocentral_beta_over_alpha_theta": (
                "Pope-family ratio over F3/F4/Fz/FC1/FC2/C3/C4/Cz."
            ),
            "engagement_kislov_central_beta16_24_over_alpha8_12": (
                "Advertising-specific beta/alpha replication over "
                "Cz/Pz/P3/P4."
            ),
        },
        "checks": checks,
        "condition_epochs": condition_report,
        "ad_epochs": ad_report,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--condition-epochs",
        type=Path,
        default=DEFAULT_CONDITION_EPOCHS,
    )
    parser.add_argument(
        "--ad-epochs",
        type=Path,
        default=DEFAULT_AD_EPOCHS,
    )
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument(
        "--expected-policy-status",
        default="frozen_v3",
    )
    parser.add_argument(
        "--expected-threshold-uv",
        type=float,
        default=1050.0,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    report = validate(
        args.condition_epochs,
        args.ad_epochs,
        args.policy,
        args.expected_policy_status,
        args.expected_threshold_uv,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    if report["validation_status"] != "pass":
        raise ValueError(f"Engagement validation failed: {report['checks']}")
    print(
        "Validated three engagement indices in condition and ad epochs; "
        f"wrote {args.output}"
    )


if __name__ == "__main__":
    main()
