"""Run the reproducible EEG preprocessing stages in dependency order.

The runner never lands or moves raw XDF files. Use the ingestion organizer
explicitly with ``--apply`` only when adding new recordings.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

STAGES: dict[str, tuple[str, ...]] = {
    "bronze": (
        "analysis/eeg/preprocessing/bronze/manifests/"
        "build_recording_manifest.py",
    ),
    "silver-markers": (
        "analysis/eeg/preprocessing/silver/markers/"
        "audit_marker_anomalies.py",
        "analysis/eeg/preprocessing/silver/markers/"
        "build_canonical_markers.py",
        "analysis/eeg/preprocessing/silver/markers/"
        "validate_marker_reconstruction.py",
        "analysis/eeg/preprocessing/silver/markers/"
        "verify_recovery_invariants.py",
    ),
    "silver-signal": (
        "analysis/eeg/preprocessing/silver/signal/audit_xdf_mne.py",
        "analysis/eeg/preprocessing/silver/signal/audit_signal_quality.py",
    ),
    "silver-visual": (
        "analysis/eeg/preprocessing/silver/signal/"
        "validate_cleaning_visual.py",
    ),
    "gold-windows": (
        "analysis/eeg/preprocessing/gold/windows/"
        "build_condition_windows.py",
        "analysis/eeg/preprocessing/gold/windows/build_ad_visibility.py",
        "analysis/eeg/preprocessing/gold/windows/build_ad_windows.py",
    ),
    "gold-features": (
        "analysis/eeg/preprocessing/gold/features/"
        "build_condition_features.py",
        "analysis/eeg/preprocessing/gold/features/"
        "validate_condition_features.py",
        "analysis/eeg/preprocessing/gold/features/build_ad_features.py",
        "analysis/eeg/preprocessing/gold/features/validate_ad_features.py",
        "analysis/eeg/preprocessing/gold/features/"
        "validate_engagement_features.py",
    ),
    "analysis": (
        "analysis/eeg/statistics/build_ad_contrasts.py",
        "analysis/eeg/statistics/run_equal_n_dataset_a.py",
    ),
    "publication-analysis": (
        "analysis/eeg/analysis/run_publication_analysis.py",
    ),
    "validation": (
        "analysis/eeg/preprocessing/validate_preprocessing_soundness.py",
    ),
    "diagram": (
        "src/project/docs/eeg_pipeline/eeg_pipeline.py",
    ),
}

DEFAULT_ORDER = (
    "bronze",
    "silver-markers",
    "silver-signal",
    "gold-windows",
    "gold-features",
    "analysis",
    "publication-analysis",
)


def selected_stages(requested: list[str]) -> tuple[str, ...]:
    if not requested or "all" in requested:
        return DEFAULT_ORDER
    return tuple(requested)


def run(stages: tuple[str, ...], *, dry_run: bool) -> None:
    for stage in stages:
        print(f"\n=== {stage} ===", flush=True)
        for relative_script in STAGES[stage]:
            command = [sys.executable, relative_script]
            print("$ " + " ".join(command), flush=True)
            if dry_run:
                continue
            subprocess.run(
                command,
                cwd=REPOSITORY_ROOT,
                check=True,
            )
    print("\nEEG preprocessing stages completed.", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run EEG preprocessing stages without modifying Bronze XDF files."
        )
    )
    parser.add_argument(
        "--stage",
        action="append",
        choices=("all", *STAGES),
        default=[],
        help=(
            "Stage to run; repeat for multiple stages. Defaults to data and "
            "analysis stages; excludes the visual pack and diagram."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them.",
    )
    args = parser.parse_args()
    run(selected_stages(args.stage), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
