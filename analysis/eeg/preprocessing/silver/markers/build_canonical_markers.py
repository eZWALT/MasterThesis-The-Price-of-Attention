"""Build one canonical marker table per recording as silver-layer sidecars."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

from marker_pipeline import (
    Alignment,
    best_session_alignment,
    canonical_rows,
    discover_logs,
    discover_xdfs,
    load_xdf_markers,
    write_csv,
)


DEFAULT_BRONZE = Path("src/project/logs/xdf/bronze")
DEFAULT_LOGS = Path("src/project/logs/production")
DEFAULT_SILVER = Path("src/project/logs/xdf/silver")


def load_bronze_hashes(silver_root: Path) -> dict[str, str]:
    inventory_path = silver_root / "audits" / "bronze_inventory.csv"
    if not inventory_path.exists():
        raise FileNotFoundError(
            f"Missing {inventory_path}; run organize_xdf_lake.py --apply first"
        )
    with inventory_path.open(newline="", encoding="utf-8") as handle:
        hashes = {
            row["relative_path"]: row.get("sha256", "")
            for row in csv.DictReader(handle)
        }
    if not hashes or any(not value for value in hashes.values()):
        raise ValueError(
            "Bronze inventory has missing SHA-256 values; rerun "
            "organize_xdf_lake.py --apply"
        )
    return hashes


def run(
    bronze_root: Path,
    log_root: Path,
    silver_root: Path,
    *,
    minimum_anchors: int,
    maximum_p95_residual_s: float,
    maximum_slope_deviation: float,
) -> None:
    logs = discover_logs(log_root)
    xdfs = discover_xdfs(bronze_root)
    bronze_hashes = load_bronze_hashes(silver_root)
    manifest_rows: list[dict[str, object]] = []

    mapped_sessions: set[str] = set()
    for number in sorted(xdfs):
        xdf = load_xdf_markers(xdfs[number])
        session, initial = best_session_alignment(xdf, logs.values())
        if session.experiment_id in mapped_sessions:
            raise ValueError(
                f"Multiple XDF recordings map to {session.experiment_id}"
            )
        mapped_sessions.add(session.experiment_id)
        fit = initial.fit
        fit_valid = bool(
            fit is not None
            and fit.anchor_count >= minimum_anchors
            and fit.p95_abs_residual_s <= maximum_p95_residual_s
            and abs(fit.slope - 1.0) <= maximum_slope_deviation
        )
        governed_alignment = (
            initial
            if fit_valid
            else Alignment(fit=None, matches={})
        )
        rows = canonical_rows(session, xdf, governed_alignment)
        relative_xdf = str(xdf.path.relative_to(silver_root.parent))
        source_hash = bronze_hashes.get(relative_xdf, "")
        if not source_hash:
            raise ValueError(
                f"No bronze SHA-256 inventory entry for {relative_xdf}"
            )
        for row in rows:
            row["source_xdf_sha256"] = source_hash
        output_path = (
            silver_root
            / "canonical_markers"
            / f"{session.subject_id}.csv"
        )
        write_csv(output_path, rows)

        observed = sum(row["provenance"] == "observed" for row in rows)
        derived = sum(
            row["provenance"] == "derived"
            and row["reconstruction_method"] != "unavailable"
            for row in rows
        )
        unavailable = sum(
            row["reconstruction_method"] == "unavailable" for row in rows
        )
        metadata_only = sum(
            row["reconstruction_scope"] == "metadata_only" for row in rows
        )
        duplicate_raw = sum(int(row["duplicate_raw_count"]) for row in rows)
        outside_eeg = sum(row["inside_eeg_span"] != "yes" for row in rows)
        manifest_rows.append(
            {
                "subject_id": session.subject_id,
                "experiment_id": session.experiment_id,
                "study_type": session.study_type,
                "study_protocol_eligible": (
                    "yes" if session.study_type == "lab" else "no"
                ),
                "xdf_folder_subject_number": number,
                "mapping_matches_folder_number": (
                    "yes" if session.subject_number == number else "no"
                ),
                "source_xdf": str(xdf.path),
                "source_xdf_sha256": source_hash,
                "source_log": str(session.path),
                "canonical_table": str(output_path),
                "expected_event_count": len(session.events),
                "observed_event_count": observed,
                "derived_event_count": derived,
                "unavailable_event_count": unavailable,
                "metadata_only_derived_event_count": metadata_only,
                "duplicate_raw_marker_count": duplicate_raw,
                "outside_eeg_span_count": outside_eeg,
                "fit_valid": "yes" if fit_valid else "no",
                "anchor_count": fit.anchor_count if fit is not None else 0,
                "fit_slope": (
                    f"{fit.slope:.9f}" if fit is not None else ""
                ),
                "fit_rmse_s": (
                    f"{fit.rmse_s:.6f}" if fit is not None else ""
                ),
                "fit_p95_abs_residual_s": (
                    f"{fit.p95_abs_residual_s:.6f}"
                    if fit is not None
                    else ""
                ),
                "fit_max_abs_residual_s": (
                    f"{fit.max_abs_residual_s:.6f}"
                    if fit is not None
                    else ""
                ),
                "complete_canonical_timeline": (
                    "yes"
                    if unavailable == 0 and outside_eeg == 0
                    else "no"
                ),
            }
        )
        fit_text = (
            f"p95={fit.p95_abs_residual_s:.6f}s"
            if fit is not None and math.isfinite(fit.p95_abs_residual_s)
            else "no fit"
        )
        print(
            f"{session.subject_id}: {observed} observed, {derived} derived, "
            f"{unavailable} unavailable, {duplicate_raw} duplicates; {fit_text}"
        )

    manifest_path = silver_root / "canonical_marker_manifest.csv"
    write_csv(manifest_path, manifest_rows)
    print(f"Wrote canonical marker manifest to {manifest_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bronze-root", type=Path, default=DEFAULT_BRONZE)
    parser.add_argument("--log-root", type=Path, default=DEFAULT_LOGS)
    parser.add_argument("--silver-root", type=Path, default=DEFAULT_SILVER)
    parser.add_argument("--minimum-anchors", type=int, default=10)
    parser.add_argument(
        "--maximum-p95-residual-s",
        type=float,
        default=0.1,
    )
    parser.add_argument(
        "--maximum-slope-deviation",
        type=float,
        default=0.001,
    )
    args = parser.parse_args()
    run(
        args.bronze_root,
        args.log_root,
        args.silver_root,
        minimum_anchors=args.minimum_anchors,
        maximum_p95_residual_s=args.maximum_p95_residual_s,
        maximum_slope_deviation=args.maximum_slope_deviation,
    )


if __name__ == "__main__":
    main()
