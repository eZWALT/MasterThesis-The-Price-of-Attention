"""Compare 1,050 µV primary against archived threshold sensitivities."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PRIMARY_ROOT = REPOSITORY_ROOT / "analysis/eeg/statistics/outputs"
SENSITIVITY_ROOT = PRIMARY_ROOT / "sensitivity"
OUTPUT = PRIMARY_ROOT / "threshold_sensitivity_comparison.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def optional_float(value: str) -> float | None:
    return float(value) if value else None


def row_key(row: dict[str, str], analysis: str) -> tuple[str, ...]:
    metric_key = "metric" if analysis == "condition" else "response_metric"
    return (
        row["contrast_id"],
        row["feature"],
        row[metric_key],
    )


def corrected_significance(row: dict[str, str]) -> bool:
    corrected = [
        optional_float(row["p_t_holm"]),
        optional_float(row["p_wilcoxon_holm"]),
    ]
    return any(value is not None and value < 0.05 for value in corrected)


def compare_file(
    primary_path: Path,
    sensitivity_path: Path,
    *,
    analysis: str,
) -> dict[str, Any]:
    primary_rows = read_csv(primary_path)
    sensitivity_rows = read_csv(sensitivity_path)
    primary = {row_key(row, analysis): row for row in primary_rows}
    sensitivity = {
        row_key(row, analysis): row for row in sensitivity_rows
    }
    if primary.keys() != sensitivity.keys():
        raise ValueError(f"{analysis}: primary and sensitivity keys differ")

    comparisons: list[dict[str, Any]] = []
    for key in sorted(primary):
        primary_row = primary[key]
        sensitivity_row = sensitivity[key]
        primary_mean = float(primary_row["mean_difference"])
        sensitivity_mean = float(sensitivity_row["mean_difference"])
        comparisons.append(
            {
                "contrast_id": primary_row["contrast_id"],
                "feature": primary_row["feature"],
                "feature_tier": primary_row["feature_tier"],
                "contrast_tier": primary_row["contrast_tier"],
                "primary_n": int(primary_row["n_participants"]),
                "sensitivity_n": int(
                    sensitivity_row["n_participants"]
                ),
                "primary_mean_difference": primary_mean,
                "sensitivity_mean_difference": sensitivity_mean,
                "absolute_mean_difference_change": abs(
                    primary_mean - sensitivity_mean
                ),
                "direction_changed": (
                    math.copysign(1.0, primary_mean)
                    != math.copysign(1.0, sensitivity_mean)
                ),
                "primary_corrected_significant": corrected_significance(
                    primary_row
                ),
                "sensitivity_corrected_significant": (
                    corrected_significance(sensitivity_row)
                ),
            }
        )

    confirmatory = [
        row
        for row in comparisons
        if row["feature_tier"] == "primary"
        and row["contrast_tier"] == "primary"
    ]
    maximum_change = max(
        comparisons,
        key=lambda row: row["absolute_mean_difference_change"],
    )
    direction_changes = [
        {
            "contrast_id": row["contrast_id"],
            "feature": row["feature"],
            "feature_tier": row["feature_tier"],
            "contrast_tier": row["contrast_tier"],
            "primary_mean_difference": row["primary_mean_difference"],
            "sensitivity_mean_difference": row[
                "sensitivity_mean_difference"
            ],
        }
        for row in comparisons
        if row["direction_changed"]
    ]
    return {
        "comparison_count": len(comparisons),
        "participant_count_change_count": sum(
            row["primary_n"] != row["sensitivity_n"]
            for row in comparisons
        ),
        "direction_change_count_all_features": sum(
            row["direction_changed"] for row in comparisons
        ),
        "direction_change_count_confirmatory": sum(
            row["direction_changed"] for row in confirmatory
        ),
        "corrected_conclusion_change_count_confirmatory": sum(
            row["primary_corrected_significant"]
            != row["sensitivity_corrected_significant"]
            for row in confirmatory
        ),
        "primary_corrected_significant_confirmatory_count": sum(
            row["primary_corrected_significant"] for row in confirmatory
        ),
        "sensitivity_corrected_significant_confirmatory_count": sum(
            row["sensitivity_corrected_significant"]
            for row in confirmatory
        ),
        "maximum_absolute_mean_difference_change": maximum_change[
            "absolute_mean_difference_change"
        ],
        "maximum_change_contrast": {
            "contrast_id": maximum_change["contrast_id"],
            "feature": maximum_change["feature"],
            "feature_tier": maximum_change["feature_tier"],
            "contrast_tier": maximum_change["contrast_tier"],
            "primary_mean_difference": maximum_change[
                "primary_mean_difference"
            ],
            "sensitivity_mean_difference": maximum_change[
                "sensitivity_mean_difference"
            ],
        },
        "participant_count_change_contrasts": sorted(
            {
                row["contrast_id"]
                for row in comparisons
                if row["primary_n"] != row["sensitivity_n"]
            }
        ),
        "direction_changes_all_features": direction_changes,
        "confirmatory_direction_changes": [
            row
            for row in confirmatory
            if row["direction_changed"]
        ],
    }


def main() -> None:
    sensitivity_policies = {
        "frozen_v1_1000_uv": SENSITIVITY_ROOT / "frozen_v1",
        "frozen_v2_1500_uv": SENSITIVITY_ROOT / "frozen_v2",
    }
    comparisons: dict[str, dict[str, Any]] = {}
    for policy_name, sensitivity_root in sensitivity_policies.items():
        condition = compare_file(
            PRIMARY_ROOT / "eeg_condition_contrasts.csv",
            sensitivity_root / "eeg_condition_contrasts.csv",
            analysis="condition",
        )
        ad = compare_file(
            PRIMARY_ROOT / "eeg_ad_response_contrasts.csv",
            sensitivity_root / "eeg_ad_response_contrasts.csv",
            analysis="ad",
        )
        comparisons[policy_name] = {
            "checks": {
                "no_confirmatory_corrected_conclusion_changes": (
                    condition[
                        "corrected_conclusion_change_count_confirmatory"
                    ]
                    == 0
                    and ad[
                        "corrected_conclusion_change_count_confirmatory"
                    ]
                    == 0
                ),
                "no_confirmatory_direction_changes": (
                    condition["direction_change_count_confirmatory"] == 0
                    and ad["direction_change_count_confirmatory"] == 0
                ),
            },
            "condition": condition,
            "ad_response": ad,
        }
    checks = {
        "all_sensitivities_preserve_corrected_conclusions": all(
            comparison["checks"][
                "no_confirmatory_corrected_conclusion_changes"
            ]
            for comparison in comparisons.values()
        ),
        "all_sensitivities_preserve_confirmatory_directions": all(
            comparison["checks"]["no_confirmatory_direction_changes"]
            for comparison in comparisons.values()
        ),
    }
    report = {
        "status": "pass" if all(checks.values()) else "review_required",
        "primary_policy": "frozen_v3_1050_uv",
        "checks": checks,
        "sensitivities": comparisons,
    }
    with OUTPUT.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report, indent=2))
    print(f"Wrote threshold sensitivity comparison to {OUTPUT}")


if __name__ == "__main__":
    main()
