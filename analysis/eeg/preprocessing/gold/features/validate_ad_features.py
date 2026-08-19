"""Validate the pre/post ad and matched no-ad EEG feature dataset."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from build_condition_features import SUMMARY_FEATURES, read_csv


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_WINDOWS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/ad_analysis_windows.csv"
)
DEFAULT_EPOCHS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/ad_epoch_features.csv"
)
DEFAULT_RESPONSES = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/ad_response_features.csv"
)
DEFAULT_OUTPUT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/ad_feature_validation.json"
)


def validate(
    windows_path: Path,
    epochs_path: Path,
    responses_path: Path,
    *,
    expected_ica_applied: bool = False,
) -> dict[str, Any]:
    windows = read_csv(windows_path)
    epochs = read_csv(epochs_path)
    responses = read_csv(responses_path)
    expected_ica_value = "yes" if expected_ica_applied else "no"
    observed_ica = {
        row["ica_applied"] for row in [*epochs, *responses]
    }
    if observed_ica != {expected_ica_value}:
        raise ValueError(
            f"Expected ica_applied={expected_ica_value}, "
            f"found {sorted(observed_ica)}"
        )
    if len(windows) != 216 or len(epochs) != 216 or len(responses) != 108:
        raise ValueError(
            "Expected 216 windows/epochs and 108 response pairs, got "
            f"{len(windows)}/{len(epochs)}/{len(responses)}"
        )
    subjects = sorted({row["subject_id"] for row in responses})
    if len(subjects) != 18 or "lab_subject_4" in subjects:
        raise ValueError(f"Unexpected ad-feature cohort: {subjects}")

    epoch_keys = [(row["window_id"], row["phase"]) for row in epochs]
    if len(epoch_keys) != len(set(epoch_keys)):
        raise ValueError("Duplicate ad epoch keys")
    if len({row["reference_id"] for row in responses}) != len(responses):
        raise ValueError("Duplicate ad response keys")

    non_finite: Counter[str] = Counter()
    for row in epochs:
        for feature in SUMMARY_FEATURES:
            if not math.isfinite(float(row[feature])):
                non_finite[feature] += 1
    if non_finite:
        raise ValueError(f"Non-finite ad features: {non_finite}")

    reference_counts = Counter(row["reference_kind"] for row in responses)
    if reference_counts != {
        "advertisement": 72,
        "matched_no_ad_reply": 36,
    }:
        raise ValueError(f"Unexpected reference counts: {reference_counts}")
    condition_counts = Counter(row["condition"] for row in responses)
    expected_conditions = {
        "block_early": 18,
        "block_late": 18,
        "inline_early": 18,
        "inline_late": 18,
        "no_ads": 36,
    }
    if condition_counts != expected_conditions:
        raise ValueError(f"Unexpected condition counts: {condition_counts}")

    retained_epochs = sum(
        row["retained_by_policy"] == "yes" for row in epochs
    )
    eligible_responses = [
        row for row in responses if row["primary_analysis_eligible"] == "yes"
    ]
    eligible_by_condition = Counter(
        row["condition"] for row in eligible_responses
    )
    insufficient = {
        condition: count
        for condition, count in eligible_by_condition.items()
        if count < 15
    }
    if insufficient:
        raise ValueError(
            f"Fewer than 15 retained pairs in condition cells: {insufficient}"
        )

    uncertainty = [
        float(row["combined_timing_uncertainty_s"])
        for row in responses
    ]
    return {
        "status": "passed",
        "dataset_status": "analysis_ready_ad_v1",
        "subject_count": len(subjects),
        "window_count": len(windows),
        "epoch_count": len(epochs),
        "retained_epoch_count": retained_epochs,
        "retained_epoch_fraction": retained_epochs / len(epochs),
        "response_pair_count": len(responses),
        "eligible_response_pair_count": len(eligible_responses),
        "eligible_response_pair_fraction": (
            len(eligible_responses) / len(responses)
        ),
        "reference_counts": dict(reference_counts),
        "condition_counts": dict(condition_counts),
        "eligible_by_condition": dict(eligible_by_condition),
        "maximum_combined_timing_uncertainty_s": max(uncertainty),
        "duplicate_key_count": 0,
        "non_finite_feature_count": 0,
        "ica_applied": expected_ica_applied,
        "artifact_policy_status": responses[0]["artifact_policy_status"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--windows", type=Path, default=DEFAULT_WINDOWS)
    parser.add_argument("--epochs", type=Path, default=DEFAULT_EPOCHS)
    parser.add_argument("--responses", type=Path, default=DEFAULT_RESPONSES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--expected-ica-applied",
        choices=("yes", "no"),
        default="yes",
    )
    args = parser.parse_args()
    report = validate(
        args.windows,
        args.epochs,
        args.responses,
        expected_ica_applied=args.expected_ica_applied == "yes",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report, indent=2))
    print(f"Wrote ad feature validation to {args.output}")


if __name__ == "__main__":
    main()
