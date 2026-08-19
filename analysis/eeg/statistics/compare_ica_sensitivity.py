"""Compare the ICA primary branch with the archived no-ICA sensitivity."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[2]
PRIMARY_STATISTICS = HERE / "outputs"
NO_ICA_STATISTICS = HERE / "outputs/sensitivity/no_ica_frozen_v3"
PRIMARY_FEATURES = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features"
)
NO_ICA_FEATURES = PRIMARY_FEATURES / "sensitivity/no_ica_frozen_v3"
ICA_COHORT_SUMMARY = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/ica/candidate_v1/"
    "ica_cohort_summary.csv"
)
DEFAULT_OUTPUT = HERE / "outputs/ica_sensitivity_comparison.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def paired_rows(
    primary: list[dict[str, str]],
    candidate: list[dict[str, str]],
    key_fields: tuple[str, ...],
) -> list[tuple[dict[str, str], dict[str, str]]]:
    primary_index = {
        tuple(row[field] for field in key_fields): row for row in primary
    }
    candidate_index = {
        tuple(row[field] for field in key_fields): row for row in candidate
    }
    if set(primary_index) != set(candidate_index):
        missing_candidate = sorted(set(primary_index) - set(candidate_index))
        missing_primary = sorted(set(candidate_index) - set(primary_index))
        raise ValueError(
            "ICA comparison keys differ: "
            f"missing candidate={missing_candidate[:5]}, "
            f"missing primary={missing_primary[:5]}"
        )
    return [
        (primary_index[key], candidate_index[key])
        for key in sorted(primary_index)
    ]


def correlation(first: np.ndarray, second: np.ndarray) -> float | None:
    if len(first) < 2 or np.std(first) == 0 or np.std(second) == 0:
        return None
    return float(np.corrcoef(first, second)[0, 1])


def compare_contrasts(
    primary_path: Path,
    candidate_path: Path,
) -> dict[str, Any]:
    pairs = paired_rows(
        read_csv(primary_path),
        read_csv(candidate_path),
        ("contrast_id", "feature"),
    )
    primary_values = np.asarray(
        [float(primary["mean_difference"]) for primary, _ in pairs]
    )
    candidate_values = np.asarray(
        [float(candidate["mean_difference"]) for _, candidate in pairs]
    )
    nonzero = (np.abs(primary_values) > 1e-12) | (
        np.abs(candidate_values) > 1e-12
    )
    corrected_pairs = [
        (primary, candidate)
        for primary, candidate in pairs
        if primary["p_t_holm"] and candidate["p_t_holm"]
    ]
    significance_agreement = sum(
        (float(primary["p_t_holm"]) < 0.05)
        == (float(candidate["p_t_holm"]) < 0.05)
        for primary, candidate in corrected_pairs
    )
    significance_changes = [
        {
            "contrast_id": primary["contrast_id"],
            "feature": primary["feature"],
            "no_ica_p_t_holm": float(primary["p_t_holm"]),
            "ica_p_t_holm": float(candidate["p_t_holm"]),
            "no_ica_significant": float(primary["p_t_holm"]) < 0.05,
            "ica_significant": float(candidate["p_t_holm"]) < 0.05,
        }
        for primary, candidate in corrected_pairs
        if (float(primary["p_t_holm"]) < 0.05)
        != (float(candidate["p_t_holm"]) < 0.05)
    ]
    direction_changes = [
        {
            "contrast_id": primary["contrast_id"],
            "feature": primary["feature"],
            "no_ica_mean_difference": float(primary["mean_difference"]),
            "ica_mean_difference": float(candidate["mean_difference"]),
        }
        for primary, candidate in pairs
        if np.sign(float(primary["mean_difference"]))
        != np.sign(float(candidate["mean_difference"]))
    ]
    effect_shifts = sorted(
        (
            {
                "contrast_id": primary["contrast_id"],
                "feature": primary["feature"],
                "no_ica_mean_difference": float(
                    primary["mean_difference"]
                ),
                "ica_mean_difference": float(
                    candidate["mean_difference"]
                ),
                "absolute_shift": abs(
                    float(candidate["mean_difference"])
                    - float(primary["mean_difference"])
                ),
            }
            for primary, candidate in pairs
        ),
        key=lambda row: row["absolute_shift"],
        reverse=True,
    )
    return {
        "paired_contrast_count": len(pairs),
        "mean_difference_correlation": correlation(
            primary_values,
            candidate_values,
        ),
        "effect_direction_agreement_fraction": float(
            np.mean(
                np.sign(primary_values[nonzero])
                == np.sign(candidate_values[nonzero])
            )
        ),
        "mean_absolute_effect_shift": float(
            np.mean(np.abs(candidate_values - primary_values))
        ),
        "maximum_absolute_effect_shift": float(
            np.max(np.abs(candidate_values - primary_values))
        ),
        "corrected_test_count": len(corrected_pairs),
        "corrected_significance_agreement_fraction": (
            significance_agreement / len(corrected_pairs)
            if corrected_pairs
            else None
        ),
        "corrected_significance_changes": significance_changes,
        "effect_direction_changes": direction_changes,
        "ten_largest_absolute_effect_shifts": effect_shifts[:10],
    }


def compare_scores(
    primary_path: Path,
    candidate_path: Path,
) -> dict[str, Any]:
    pairs = paired_rows(
        read_csv(primary_path),
        read_csv(candidate_path),
        ("subject_id", "contrast_id", "feature"),
    )
    primary_values = np.asarray(
        [float(primary["difference"]) for primary, _ in pairs]
    )
    candidate_values = np.asarray(
        [float(candidate["difference"]) for _, candidate in pairs]
    )
    absolute_shift = np.abs(candidate_values - primary_values)
    return {
        "paired_participant_score_count": len(pairs),
        "participant_score_correlation": correlation(
            primary_values,
            candidate_values,
        ),
        "median_absolute_participant_score_shift": float(
            np.median(absolute_shift)
        ),
        "p95_absolute_participant_score_shift": float(
            np.quantile(absolute_shift, 0.95)
        ),
    }


def build_report() -> dict[str, Any]:
    condition_primary_validation = read_json(
        PRIMARY_FEATURES / "condition_feature_validation.json"
    )
    condition_no_ica_validation = read_json(
        NO_ICA_FEATURES / "condition_feature_validation.json"
    )
    ad_primary_validation = read_json(
        PRIMARY_FEATURES / "ad_feature_validation.json"
    )
    ad_no_ica_validation = read_json(
        NO_ICA_FEATURES / "ad_feature_validation.json"
    )
    cohort = read_csv(ICA_COHORT_SUMMARY)
    excluded_counts = np.asarray(
        [int(row["excluded_component_count"]) for row in cohort],
        dtype=int,
    )
    component_counts = np.asarray(
        [int(row["fitted_component_count"]) for row in cohort],
        dtype=int,
    )

    return {
        "comparison": "frozen_v5_ica_primary_vs_no_ica_sensitivity",
        "interpretation_status": "ica_approved_as_primary_2026-08-19",
        "primary_branch": "ica",
        "primary_branch_changed": True,
        "ica_cohort": {
            "subject_count": len(cohort),
            "pca_explained_variance": 0.99,
            "minimum_component_count": int(np.min(component_counts)),
            "median_component_count": float(np.median(component_counts)),
            "maximum_component_count": int(np.max(component_counts)),
            "recordings_with_component_exclusion": int(
                np.sum(excluded_counts > 0)
            ),
            "total_excluded_components": int(np.sum(excluded_counts)),
            "minimum_excluded_components": int(np.min(excluded_counts)),
            "median_excluded_components": float(
                np.median(excluded_counts)
            ),
            "maximum_excluded_components": int(np.max(excluded_counts)),
            "human_visual_signoff": "approved",
        },
        "retention": {
            "condition_epoch_fraction_no_ica": (
                condition_no_ica_validation["retained_epoch_fraction"]
            ),
            "condition_epoch_fraction_ica": (
                condition_primary_validation["retained_epoch_fraction"]
            ),
            "ad_epoch_fraction_no_ica": (
                ad_no_ica_validation["retained_epoch_fraction"]
            ),
            "ad_epoch_fraction_ica": (
                ad_primary_validation["retained_epoch_fraction"]
            ),
            "ad_eligible_pair_fraction_no_ica": (
                ad_no_ica_validation[
                    "eligible_response_pair_fraction"
                ]
            ),
            "ad_eligible_pair_fraction_ica": (
                ad_primary_validation[
                    "eligible_response_pair_fraction"
                ]
            ),
        },
        "condition_contrasts": compare_contrasts(
            NO_ICA_STATISTICS / "eeg_condition_contrasts.csv",
            PRIMARY_STATISTICS / "eeg_condition_contrasts.csv",
        ),
        "condition_participant_scores": compare_scores(
            NO_ICA_STATISTICS / "eeg_condition_contrast_scores.csv",
            PRIMARY_STATISTICS / "eeg_condition_contrast_scores.csv",
        ),
        "ad_contrasts": compare_contrasts(
            NO_ICA_STATISTICS / "eeg_ad_response_contrasts.csv",
            PRIMARY_STATISTICS / "eeg_ad_response_contrasts.csv",
        ),
        "ad_participant_scores": compare_scores(
            NO_ICA_STATISTICS / "eeg_ad_response_contrast_scores.csv",
            PRIMARY_STATISTICS / "eeg_ad_response_contrast_scores.csv",
        ),
        "interpretation": (
            "Human signoff on 2026-08-19 approved filtering/interpolation "
            "figures and all automatic ICA exclusions. ICA frozen_v5 is the "
            "primary branch. No-ICA frozen_v3 remains the mandatory "
            "sensitivity. Do not reverse this choice because some ad tests "
            "are significant only under ICA."
        ),
    }


def main() -> None:
    report = build_report()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    print(f"Wrote ICA sensitivity comparison to {DEFAULT_OUTPUT}")


if __name__ == "__main__":
    main()
