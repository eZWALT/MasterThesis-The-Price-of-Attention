"""Build the ICA-cleaned sensitivity branch without replacing primary outputs."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ICA_VERSION = "ica_candidate_v1"
ICA_POLICY = REPOSITORY_ROOT / (
    "analysis/eeg/preprocessing/silver/signal/"
    "cleaning_policy_ica_candidate_v1.json"
)
FEATURE_OUTPUT = REPOSITORY_ROOT / (
    f"src/project/logs/xdf/gold/features/sensitivity/{ICA_VERSION}"
)
STATISTICS_OUTPUT = REPOSITORY_ROOT / (
    f"analysis/eeg/statistics/outputs/sensitivity/{ICA_VERSION}"
)


def run(*arguments: str | Path) -> None:
    command = [sys.executable, *(str(argument) for argument in arguments)]
    print("$ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=REPOSITORY_ROOT, check=True)


def run_ica_branch(*, fit_models: bool, overwrite_models: bool) -> None:
    if fit_models:
        arguments: list[str | Path] = [
            "analysis/eeg/preprocessing/silver/signal/fit_ica_cohort.py"
        ]
        if overwrite_models:
            arguments.append("--overwrite")
        run(*arguments)
    run(
        "analysis/eeg/preprocessing/silver/signal/"
        "build_ica_review_report.py"
    )

    condition_epochs = FEATURE_OUTPUT / "condition_epoch_features.csv"
    condition_summary = FEATURE_OUTPUT / "condition_features.csv"
    condition_validation = (
        FEATURE_OUTPUT / "condition_feature_validation.json"
    )
    ad_epochs = FEATURE_OUTPUT / "ad_epoch_features.csv"
    ad_responses = FEATURE_OUTPUT / "ad_response_features.csv"
    ad_validation = FEATURE_OUTPUT / "ad_feature_validation.json"
    engagement_validation = (
        FEATURE_OUTPUT / "engagement_feature_validation.json"
    )

    run(
        "analysis/eeg/preprocessing/gold/features/"
        "build_condition_features.py",
        "--policy",
        ICA_POLICY,
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
        "--expected-ica-applied",
        "yes",
        "--output",
        condition_validation,
    )
    run(
        "analysis/eeg/preprocessing/gold/features/build_ad_features.py",
        "--policy",
        ICA_POLICY,
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
        "--expected-ica-applied",
        "yes",
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
        ICA_POLICY,
        "--expected-policy-status",
        "frozen_v3",
        "--expected-threshold-uv",
        "1050",
        "--output",
        engagement_validation,
    )
    run(
        "analysis/eeg/statistics/build_condition_contrasts.py",
        "--input",
        condition_summary,
        "--output-dir",
        STATISTICS_OUTPUT,
    )
    run(
        "analysis/eeg/statistics/build_ad_contrasts.py",
        "--input",
        ad_responses,
        "--output-dir",
        STATISTICS_OUTPUT,
    )
    run("analysis/eeg/statistics/compare_ica_sensitivity.py")
    print(
        "Completed ICA sensitivity branch; primary frozen_v3 no-ICA "
        "outputs were not changed."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-model-fit",
        action="store_true",
        help="Use existing cohort ICA models and reports.",
    )
    parser.add_argument(
        "--overwrite-models",
        action="store_true",
        help="Refit existing ICA models rather than reuse them.",
    )
    args = parser.parse_args()
    run_ica_branch(
        fit_models=not args.skip_model_fit,
        overwrite_models=args.overwrite_models,
    )


if __name__ == "__main__":
    main()
