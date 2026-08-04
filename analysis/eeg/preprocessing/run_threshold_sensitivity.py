"""Run archived artifact-threshold sensitivity analyses."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
POLICY_CONFIG = {
    "frozen_v1": {
        "threshold_uv": 1000.0,
        "path": REPOSITORY_ROOT
        / (
            "analysis/eeg/preprocessing/silver/signal/"
            "cleaning_policy_frozen_v1.json"
        ),
    },
    "frozen_v2": {
        "threshold_uv": 1500.0,
        "path": REPOSITORY_ROOT
        / (
            "analysis/eeg/preprocessing/silver/signal/"
            "cleaning_policy_frozen_v2.json"
        ),
    },
}


def run(*arguments: str | Path) -> None:
    command = [sys.executable, *(str(argument) for argument in arguments)]
    print("$ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=REPOSITORY_ROOT, check=True)


def run_policy(policy_version: str) -> None:
    config = POLICY_CONFIG[policy_version]
    policy = Path(config["path"])
    feature_output = REPOSITORY_ROOT / (
        "src/project/logs/xdf/gold/features/sensitivity/"
        f"{policy_version}"
    )
    statistics_output = REPOSITORY_ROOT / (
        "analysis/eeg/statistics/outputs/sensitivity/"
        f"{policy_version}"
    )
    condition_epochs = feature_output / "condition_epoch_features.csv"
    condition_summary = feature_output / "condition_features.csv"
    condition_validation = (
        feature_output / "condition_feature_validation.json"
    )
    ad_epochs = feature_output / "ad_epoch_features.csv"
    ad_responses = feature_output / "ad_response_features.csv"
    ad_validation = feature_output / "ad_feature_validation.json"
    engagement_validation = (
        feature_output / "engagement_feature_validation.json"
    )

    run(
        "analysis/eeg/preprocessing/gold/features/"
        "build_condition_features.py",
        "--policy",
        policy,
        "--epochs-output",
        condition_epochs,
        "--summary-output",
        condition_summary,
    )
    run(
        "analysis/eeg/preprocessing/gold/features/"
        "validate_condition_features.py",
        "--epochs",
        condition_epochs,
        "--summary",
        condition_summary,
        "--output",
        condition_validation,
    )
    run(
        "analysis/eeg/preprocessing/gold/features/build_ad_features.py",
        "--policy",
        policy,
        "--epochs-output",
        ad_epochs,
        "--responses-output",
        ad_responses,
    )
    run(
        "analysis/eeg/preprocessing/gold/features/validate_ad_features.py",
        "--epochs",
        ad_epochs,
        "--responses",
        ad_responses,
        "--output",
        ad_validation,
    )
    run(
        "analysis/eeg/preprocessing/gold/features/"
        "validate_engagement_features.py",
        "--condition-epochs",
        condition_epochs,
        "--ad-epochs",
        ad_epochs,
        "--policy",
        policy,
        "--expected-policy-status",
        policy_version,
        "--expected-threshold-uv",
        str(config["threshold_uv"]),
        "--output",
        engagement_validation,
    )
    run(
        "analysis/eeg/statistics/build_condition_contrasts.py",
        "--input",
        condition_summary,
        "--output-dir",
        statistics_output,
    )
    run(
        "analysis/eeg/statistics/build_ad_contrasts.py",
        "--input",
        ad_responses,
        "--output-dir",
        statistics_output,
    )
    print(
        f"Completed {policy_version} sensitivity analysis without changing "
        "primary frozen_v3 outputs."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--policy-version",
        action="append",
        choices=tuple(POLICY_CONFIG),
        help="Archived policy to run; repeat as needed. Defaults to both.",
    )
    args = parser.parse_args()
    selected = args.policy_version or list(POLICY_CONFIG)
    for policy_version in selected:
        run_policy(policy_version)
    run("analysis/eeg/statistics/compare_threshold_sensitivity.py")


if __name__ == "__main__":
    main()
