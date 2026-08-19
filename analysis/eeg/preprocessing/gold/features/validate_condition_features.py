"""Validate the analysis-ready condition-level EEG feature dataset."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from build_condition_features import SUMMARY_FEATURES


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_EPOCHS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/condition_epoch_features.csv"
)
DEFAULT_SUMMARY = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/condition_features.csv"
)
DEFAULT_REPORT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/condition_feature_validation.json"
)

NUMERIC_FEATURES = SUMMARY_FEATURES


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def quantiles(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    return {
        "p50": float(np.quantile(array, 0.50)),
        "p90": float(np.quantile(array, 0.90)),
        "p95": float(np.quantile(array, 0.95)),
        "p99": float(np.quantile(array, 0.99)),
        "p99_5": float(np.quantile(array, 0.995)),
        "maximum": float(np.max(array)),
    }


def candidate_retention(
    epochs: list[dict[str, str]],
    threshold_uv: float,
) -> dict[str, Any]:
    retained_by_window: Counter[str] = Counter()
    total_by_window: Counter[str] = Counter()
    retained_count = 0
    for row in epochs:
        total_by_window[row["window_id"]] += 1
        retained = (
            float(row["max_peak_to_peak_uv"]) <= threshold_uv
            and int(row["near_flat_channel_count"]) == 0
        )
        if retained:
            retained_count += 1
            retained_by_window[row["window_id"]] += 1
    window_fractions = {
        window_id: retained_by_window[window_id] / total
        for window_id, total in total_by_window.items()
    }
    low_retention = [
        {
            "window_id": window_id,
            "retention_fraction": fraction,
            "retained_epochs": retained_by_window[window_id],
            "complete_epochs": total_by_window[window_id],
        }
        for window_id, fraction in sorted(
            window_fractions.items(),
            key=lambda item: (item[1], item[0]),
        )
        if fraction < 0.8
    ]
    return {
        "max_peak_to_peak_uv": threshold_uv,
        "retained_epoch_count": retained_count,
        "retained_epoch_fraction": retained_count / len(epochs),
        "minimum_window_retention_fraction": min(window_fractions.values()),
        "windows_below_80_percent_retention": low_retention,
    }


def high_amplitude_sources(
    epochs: list[dict[str, str]],
    threshold_uv: float,
) -> dict[str, Any]:
    affected = [
        row
        for row in epochs
        if float(row["max_peak_to_peak_uv"]) > threshold_uv
    ]
    return {
        "max_peak_to_peak_uv": threshold_uv,
        "affected_epoch_count": len(affected),
        "worst_channel_counts": dict(
            Counter(row["max_peak_to_peak_channel"] for row in affected)
            .most_common()
        ),
        "participant_counts": dict(
            Counter(row["subject_id"] for row in affected).most_common()
        ),
        "participant_channel_counts": dict(
            Counter(
                f"{row['subject_id']}:{row['max_peak_to_peak_channel']}"
                for row in affected
            ).most_common()
        ),
        "window_counts": dict(
            Counter(row["window_id"] for row in affected).most_common()
        ),
    }


def validate(
    epochs_path: Path,
    summary_path: Path,
    *,
    require_full_cohort: bool = True,
    expected_ica_applied: bool = False,
) -> dict[str, Any]:
    epochs = read_csv(epochs_path)
    summaries = read_csv(summary_path)
    if not epochs or not summaries:
        raise ValueError("Feature tables must not be empty")
    expected_ica_value = "yes" if expected_ica_applied else "no"
    observed_ica = {
        row["ica_applied"] for row in [*epochs, *summaries]
    }
    if observed_ica != {expected_ica_value}:
        raise ValueError(
            f"Expected ica_applied={expected_ica_value}, "
            f"found {sorted(observed_ica)}"
        )

    subjects = sorted({row["subject_id"] for row in summaries})
    if (
        require_full_cohort
        and (len(subjects) != 18 or "lab_subject_4" in subjects)
    ):
        raise ValueError(
            f"Expected 18 eligible lab subjects without subject 4, got {subjects}"
        )

    windows_per_subject: Counter[str] = Counter(
        row["subject_id"] for row in summaries
    )
    baseline_per_subject: Counter[str] = Counter(
        row["subject_id"]
        for row in summaries
        if row["window_type"] == "baseline"
    )
    conditions_per_subject: Counter[str] = Counter(
        row["subject_id"]
        for row in summaries
        if row["window_type"] == "condition"
    )
    if set(windows_per_subject.values()) != {6}:
        raise ValueError(f"Expected six windows per subject: {windows_per_subject}")
    if set(baseline_per_subject.values()) != {1}:
        raise ValueError(f"Expected one baseline per subject: {baseline_per_subject}")
    if set(conditions_per_subject.values()) != {5}:
        raise ValueError(
            f"Expected five conditions per subject: {conditions_per_subject}"
        )

    epoch_keys = [
        (row["subject_id"], row["window_id"], row["epoch_index"])
        for row in epochs
    ]
    if len(epoch_keys) != len(set(epoch_keys)):
        raise ValueError("Duplicate participant-window-epoch keys detected")

    non_finite: Counter[str] = Counter()
    for row in epochs:
        for feature in NUMERIC_FEATURES:
            if not math.isfinite(float(row[feature])):
                non_finite[feature] += 1
    if non_finite:
        raise ValueError(f"Non-finite spectral features detected: {non_finite}")

    epoch_counts: Counter[str] = Counter(row["window_id"] for row in epochs)
    retained_counts: Counter[str] = Counter(
        row["window_id"]
        for row in epochs
        if row["retained_by_policy"] == "yes"
    )
    for row in summaries:
        observed = epoch_counts[row["window_id"]]
        expected = int(row["complete_epoch_count"])
        if observed != expected:
            raise ValueError(
                f"{row['window_id']}: summary={expected}, epochs={observed}"
            )
        retained_observed = retained_counts[row["window_id"]]
        retained_expected = int(row["retained_epoch_count"])
        if retained_observed != retained_expected:
            raise ValueError(
                f"{row['window_id']}: retained summary={retained_expected}, "
                f"epochs={retained_observed}"
            )
    ineligible_windows = [
        row["window_id"]
        for row in summaries
        if row["primary_analysis_eligible"] != "yes"
    ]
    if require_full_cohort and ineligible_windows:
        raise ValueError(
            f"Windows fail retained-epoch policy: {ineligible_windows}"
        )

    quality_by_window_type: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in epochs:
        quality_by_window_type[row["window_type"]].append(row)

    quality_distributions: dict[str, Any] = {}
    for window_type, rows in sorted(quality_by_window_type.items()):
        quality_distributions[window_type] = {
            "epoch_count": len(rows),
            "max_peak_to_peak_uv": quantiles(
                [float(row["max_peak_to_peak_uv"]) for row in rows]
            ),
            "max_abs_amplitude_uv": quantiles(
                [float(row["max_abs_amplitude_uv"]) for row in rows]
            ),
            "epochs_with_near_flat_channel": sum(
                int(row["near_flat_channel_count"]) > 0 for row in rows
            ),
        }

    return {
        "status": "passed",
        "dataset_status": "analysis_ready_condition_v1",
        "subject_count": len(subjects),
        "subjects": subjects,
        "window_count": len(summaries),
        "baseline_window_count": sum(
            row["window_type"] == "baseline" for row in summaries
        ),
        "condition_window_count": sum(
            row["window_type"] == "condition" for row in summaries
        ),
        "epoch_count": len(epochs),
        "retained_epoch_count": sum(retained_counts.values()),
        "retained_epoch_fraction": (
            sum(retained_counts.values()) / len(epochs)
        ),
        "ineligible_window_count": len(ineligible_windows),
        "duplicate_epoch_key_count": 0,
        "non_finite_feature_count": 0,
        "ica_applied": expected_ica_applied,
        "artifact_policy_status": summaries[0]["artifact_policy_status"],
        "baseline_eye_state": "uncontrolled_mostly_open",
        "quality_distributions": quality_distributions,
        "candidate_peak_to_peak_retention": [
            candidate_retention(epochs, threshold)
            for threshold in (500.0, 750.0, 1000.0, 1050.0, 1500.0)
        ],
        "high_amplitude_sources": [
            high_amplitude_sources(epochs, threshold)
            for threshold in (500.0, 750.0, 1000.0, 1050.0, 1500.0)
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=Path, default=DEFAULT_EPOCHS)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--allow-subset",
        action="store_true",
        help="Validate selected-subject test outputs without requiring 18 subjects.",
    )
    parser.add_argument(
        "--expected-ica-applied",
        choices=("yes", "no"),
        default="yes",
    )
    args = parser.parse_args()
    report = validate(
        args.epochs,
        args.summary,
        require_full_cohort=not args.allow_subset,
        expected_ica_applied=args.expected_ica_applied == "yes",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report, indent=2))
    print(f"Wrote validation report to {args.output}")


if __name__ == "__main__":
    main()
