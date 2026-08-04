"""Fit the candidate 99%-variance ICA model for every eligible recording."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from clean_eeg import DEFAULT_POLICY, clean_recording, load_policy
from ica_cleaning import fit_candidate_ica, ica_paths


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[4]
DEFAULT_ICA_POLICY = HERE / "cleaning_policy_ica_candidate_v1.json"
DEFAULT_WINDOWS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/condition_windows.csv"
)
DEFAULT_CHANNEL_QC = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/audits/eeg_channel_quality.csv"
)
DEFAULT_SUMMARY = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/ica/candidate_v1/"
    "ica_cohort_summary.csv"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("Refusing to write an empty ICA cohort summary")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def recording_sources(
    *,
    windows_path: Path,
    subjects: set[str] | None,
) -> list[dict[str, str]]:
    selected: dict[str, dict[str, str]] = {}
    for row in read_csv(windows_path):
        subject_id = row["subject_id"]
        if row["primary_analysis_eligible"] != "yes":
            continue
        if subjects is not None and subject_id not in subjects:
            continue
        selected.setdefault(subject_id, row)
    if not selected:
        raise ValueError("No eligible recordings selected for ICA")
    return [selected[key] for key in sorted(selected)]


def fit_cohort(
    *,
    windows_path: Path,
    channel_qc_path: Path,
    base_policy_path: Path,
    ica_policy_path: Path,
    summary_output: Path,
    subjects: set[str] | None,
    overwrite: bool,
) -> None:
    ica_policy = load_policy(ica_policy_path)
    rows: list[dict[str, Any]] = []
    for source in recording_sources(
        windows_path=windows_path,
        subjects=subjects,
    ):
        subject_id = source["subject_id"]
        paths = ica_paths(
            repository_root=REPOSITORY_ROOT,
            subject_id=subject_id,
            policy=ica_policy,
        )
        if paths["report"].exists() and not overwrite:
            print(f"{subject_id}: reusing fitted ICA", flush=True)
            report = json.loads(
                paths["report"].read_text(encoding="utf-8")
            )
        else:
            print(f"{subject_id}: deterministic cleaning", flush=True)
            raw, _ = clean_recording(
                subject_id=subject_id,
                xdf_path=REPOSITORY_ROOT / source["source_xdf"],
                canonical_markers_path=(
                    REPOSITORY_ROOT
                    / source["source_canonical_markers"]
                ),
                channel_qc_path=channel_qc_path,
                policy_path=base_policy_path,
            )
            print(f"{subject_id}: fitting candidate ICA", flush=True)
            report = fit_candidate_ica(
                raw=raw,
                subject_id=subject_id,
                policy=ica_policy,
                repository_root=REPOSITORY_ROOT,
            )
        rows.append(
            {
                "subject_id": subject_id,
                "policy_version": report["policy_version"],
                "fitted_component_count": report[
                    "fitted_component_count"
                ],
                "excluded_component_count": report[
                    "excluded_component_count"
                ],
                "excluded_components": ",".join(
                    str(value)
                    for value in report["excluded_components"]
                ),
                "human_visual_signoff": report[
                    "human_visual_signoff"
                ],
                "model_path": report["model_path"],
            }
        )
        write_csv(summary_output, rows)
    print(f"Wrote {len(rows)} ICA summaries to {summary_output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--windows", type=Path, default=DEFAULT_WINDOWS)
    parser.add_argument(
        "--channel-qc",
        type=Path,
        default=DEFAULT_CHANNEL_QC,
    )
    parser.add_argument(
        "--base-policy",
        type=Path,
        default=DEFAULT_POLICY,
    )
    parser.add_argument(
        "--ica-policy",
        type=Path,
        default=DEFAULT_ICA_POLICY,
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=DEFAULT_SUMMARY,
    )
    parser.add_argument("--subjects", nargs="+")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    fit_cohort(
        windows_path=args.windows,
        channel_qc_path=args.channel_qc,
        base_policy_path=args.base_policy,
        ica_policy_path=args.ica_policy,
        summary_output=args.summary_output,
        subjects=set(args.subjects) if args.subjects else None,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
