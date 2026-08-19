"""Rebuild Path A/B features at 2/8/16/32 s without replacing primary Gold.

Cleans each recording once per policy (ICA primary, no-ICA), then tiles
condition windows from condition start and cuts ad-locked pre/post windows
at each duration. Existing 4 s ICA primary and no-ICA archives are reused.

This is a robustness grid, not a licence to freeze a new confirmatory
epoch length because one cell is Holm-significant.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PREPROCESSING = REPOSITORY_ROOT / "analysis/eeg/preprocessing"
SIGNAL_DIR = PREPROCESSING / "silver/signal"
FEATURE_DIR = PREPROCESSING / "gold/features"
WINDOW_DIR = PREPROCESSING / "gold/windows"
STATISTICS_DIR = REPOSITORY_ROOT / "analysis/eeg/statistics"
sys.path.insert(0, str(SIGNAL_DIR))
sys.path.insert(0, str(FEATURE_DIR))
sys.path.insert(0, str(WINDOW_DIR))
sys.path.insert(0, str(STATISTICS_DIR))

from build_ad_features import feature_row, response_row  # noqa: E402
from build_ad_windows import run as build_ad_windows  # noqa: E402
from build_ad_contrasts import run as build_ad_contrasts  # noqa: E402
from build_condition_contrasts import (  # noqa: E402
    FEATURE_TIERS,
    run as build_condition_contrasts,
)
from build_condition_features import (  # noqa: E402
    add_baseline_deltas,
    complete_epoch_bounds,
    epoch_row,
    read_csv,
    summarize_window,
    write_csv,
)
from clean_eeg import clean_recording, load_policy  # noqa: E402


DEFAULT_LENGTHS = (2.0, 8.0, 16.0, 32.0)
REUSED_SECONDS = 4.0
POLICIES = {
    "ica": SIGNAL_DIR / "cleaning_policy.json",
    "no_ica": SIGNAL_DIR / "cleaning_policy_no_ica_sensitivity.json",
}
CONDITION_WINDOWS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/condition_windows.csv"
)
CHANNEL_QC = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/audits/eeg_channel_quality.csv"
)
AD_MANIFEST = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/canonical_marker_manifest.csv"
)
AD_VISIBILITY = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/ad_visibility_events.csv"
)
FEATURE_ROOT = REPOSITORY_ROOT / "src/project/logs/xdf/gold/features"
STATS_ROOT = REPOSITORY_ROOT / "analysis/eeg/statistics/outputs"
FOUR_SECOND_SOURCES = {
    "ica": {
        "condition_summary": FEATURE_ROOT / "condition_features.csv",
        "ad_responses": FEATURE_ROOT / "ad_response_features.csv",
        "stats": STATS_ROOT,
    },
    "no_ica": {
        "condition_summary": (
            FEATURE_ROOT / "sensitivity/no_ica_frozen_v3/condition_features.csv"
        ),
        "ad_responses": (
            FEATURE_ROOT / "sensitivity/no_ica_frozen_v3/ad_response_features.csv"
        ),
        "stats": STATS_ROOT / "sensitivity/no_ica_frozen_v3",
    },
}
CONFIRMATORY_FEATURES = {
    "fz_theta_power_db_uv2",
    "posterior_alpha_power_db_uv2",
}


def feature_dir(seconds: float, policy_name: str) -> Path:
    return FEATURE_ROOT / "sensitivity" / f"epoch_{seconds:g}s" / policy_name


def stats_dir(seconds: float, policy_name: str) -> Path:
    return STATS_ROOT / "sensitivity" / f"epoch_{seconds:g}s" / policy_name


def ad_window_path(seconds: float) -> Path:
    return (
        REPOSITORY_ROOT
        / "src/project/logs/xdf/gold/windows/sensitivity"
        / f"epoch_{seconds:g}s"
        / "ad_analysis_windows.csv"
    )


def summarize_grouped(
    grouped: dict[str, list[dict[str, Any]]],
    epoch_rejection: dict[str, Any],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for window_id in sorted(grouped):
        try:
            summaries.append(summarize_window(grouped[window_id], epoch_rejection))
        except ValueError as error:
            print(f"  skip {window_id}: {error}", flush=True)
    return summaries


def extract_condition_epochs(
    *,
    raw: Any,
    windows: list[dict[str, str]],
    epoch_seconds: float,
    epoch_rejection: dict[str, Any],
    ica_applied: bool,
) -> list[dict[str, Any]]:
    sfreq = float(raw.info["sfreq"])
    rows: list[dict[str, Any]] = []
    for window in windows:
        for epoch_index, start_sample, stop_sample in complete_epoch_bounds(
            start_s=float(window["start_eeg_offset_s"]),
            end_s=float(window["end_eeg_offset_s"]),
            sfreq=sfreq,
            epoch_seconds=epoch_seconds,
            raw_sample_count=int(raw.n_times),
        ):
            data_v = raw.get_data(
                start=start_sample,
                stop=stop_sample,
                picks="eeg",
            )
            rows.append(
                epoch_row(
                    window,
                    epoch_index=epoch_index,
                    start_sample=start_sample,
                    stop_sample=stop_sample,
                    sfreq=sfreq,
                    data_v=data_v,
                    channel_names=raw.ch_names,
                    epoch_rejection=epoch_rejection,
                    ica_applied=ica_applied,
                )
            )
    return rows


def extract_ad_epochs(
    *,
    raw: Any,
    windows: list[dict[str, str]],
    epoch_rejection: dict[str, Any],
    ica_applied: bool,
) -> list[dict[str, Any]]:
    sfreq = float(raw.info["sfreq"])
    rows: list[dict[str, Any]] = []
    for window in windows:
        start = int(round(float(window["start_eeg_offset_s"]) * sfreq))
        stop = int(round(float(window["end_eeg_offset_s"]) * sfreq))
        data_v = raw.get_data(start=start, stop=stop, picks="eeg")
        expected = int(round(float(window["duration_s"]) * sfreq))
        if data_v.shape[1] != expected:
            raise ValueError(
                f"{window['window_id']}: expected {expected} samples, "
                f"found {data_v.shape[1]}"
            )
        rows.append(
            feature_row(
                window,
                data_v=data_v,
                sfreq=sfreq,
                channel_names=raw.ch_names,
                epoch_rejection=epoch_rejection,
                ica_applied=ica_applied,
            )
        )
    return rows


def write_path_a(
    epoch_rows: list[dict[str, Any]],
    epoch_rejection: dict[str, Any],
    output: Path,
) -> Path:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in epoch_rows:
        grouped[str(row["window_id"])].append(row)
    summaries = summarize_grouped(grouped, epoch_rejection)
    add_baseline_deltas(summaries)
    epochs_path = output / "condition_epoch_features.csv"
    summary_path = output / "condition_features.csv"
    write_csv(epochs_path, epoch_rows)
    write_csv(summary_path, summaries)
    print(
        f"  Path A: {len(epoch_rows)} epochs, {len(summaries)} summaries",
        flush=True,
    )
    return summary_path


def write_path_b(
    epoch_rows: list[dict[str, Any]],
    output: Path,
) -> Path:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in epoch_rows:
        grouped[str(row["reference_id"])].append(row)
    responses = [
        response_row(grouped[key]) for key in sorted(grouped)
    ]
    epochs_path = output / "ad_epoch_features.csv"
    responses_path = output / "ad_response_features.csv"
    write_csv(epochs_path, epoch_rows)
    write_csv(responses_path, responses)
    eligible = sum(
        row["primary_analysis_eligible"] == "yes" for row in responses
    )
    print(
        f"  Path B: {len(epoch_rows)} epochs, {len(responses)} pairs "
        f"({eligible} eligible)",
        flush=True,
    )
    return responses_path


def copy_four_second_stats(policy_name: str) -> None:
    source = FOUR_SECOND_SOURCES[policy_name]
    destination = stats_dir(REUSED_SECONDS, policy_name)
    destination.mkdir(parents=True, exist_ok=True)
    for name in (
        "eeg_condition_descriptives.csv",
        "eeg_condition_contrasts.csv",
        "eeg_condition_contrast_scores.csv",
        "eeg_ad_response_contrasts.csv",
        "eeg_ad_response_contrast_scores.csv",
    ):
        origin = source["stats"] / name
        if origin.exists():
            shutil.copy2(origin, destination / name)


def run_stats(seconds: float, policy_name: str, *, skip_stats: bool) -> None:
    if skip_stats:
        return
    output = stats_dir(seconds, policy_name)
    features = feature_dir(seconds, policy_name)
    if seconds == REUSED_SECONDS:
        copy_four_second_stats(policy_name)
        return
    build_condition_contrasts(
        features / "condition_features.csv",
        output,
        expected_condition_rows=None,
        drop_incomplete_subjects=True,
    )
    build_ad_contrasts(
        features / "ad_response_features.csv",
        output,
        min_participants=10,
    )


def holm_significant(row: dict[str, str]) -> bool:
    value = row.get("p_t_holm", "")
    if value in ("", None):
        return False
    try:
        return float(value) < 0.05
    except ValueError:
        return False


def collect_contrast_rows(
    seconds: float,
    policy_name: str,
    path_name: str,
    filename: str,
) -> list[dict[str, Any]]:
    path = stats_dir(seconds, policy_name) / filename
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for row in read_csv(path):
        holm = holm_significant(row)
        raw_p = float(row["p_t_raw"])
        rows.append(
            {
                "epoch_seconds": seconds,
                "policy": policy_name,
                "path": path_name,
                "contrast_id": row["contrast_id"],
                "feature": row["feature"],
                "feature_tier": row["feature_tier"],
                "n_participants": int(float(row["n_participants"])),
                "mean_difference": float(row["mean_difference"]),
                "p_t_raw": raw_p,
                "p_t_holm": (
                    float(row["p_t_holm"]) if row.get("p_t_holm") not in ("", None)
                    else None
                ),
                "holm_significant": holm,
                "raw_p_lt_05": raw_p < 0.05,
                "confirmatory": (
                    row["feature"] in CONFIRMATORY_FEATURES
                    and row.get("contrast_tier", "") == "primary"
                ),
            }
        )
    return rows


def write_grid_summary(lengths: list[float], policies: list[str]) -> Path:
    rows: list[dict[str, Any]] = []
    for seconds in [REUSED_SECONDS, *lengths]:
        for policy_name in policies:
            rows.extend(
                collect_contrast_rows(
                    seconds,
                    policy_name,
                    "A",
                    "eeg_condition_contrasts.csv",
                )
            )
            rows.extend(
                collect_contrast_rows(
                    seconds,
                    policy_name,
                    "B",
                    "eeg_ad_response_contrasts.csv",
                )
            )
    output = STATS_ROOT / "sensitivity" / "epoch_length_grid_comparison.csv"
    write_csv(output, rows)
    confirmatory_hits = [
        row
        for row in rows
        if row["confirmatory"] and row["holm_significant"]
    ]
    any_holm = [row for row in rows if row["holm_significant"]]
    report = {
        "grid_seconds": [REUSED_SECONDS, *lengths],
        "policies": policies,
        "n_tests": len(rows),
        "holm_hits": len(any_holm),
        "confirmatory_holm_hits": confirmatory_hits,
        "exploratory_holm_hits": [
            {
                "epoch_seconds": row["epoch_seconds"],
                "policy": row["policy"],
                "path": row["path"],
                "contrast_id": row["contrast_id"],
                "feature": row["feature"],
                "p_t_holm": row["p_t_holm"],
                "mean_difference": row["mean_difference"],
                "n_participants": row["n_participants"],
            }
            for row in any_holm
            if not row["confirmatory"]
        ],
    }
    json_path = STATS_ROOT / "sensitivity" / "epoch_length_grid_comparison.json"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Wrote {json_path}")
    print(
        f"Holm hits: {len(any_holm)} "
        f"(confirmatory {len(confirmatory_hits)})"
    )
    return output


def run_grid(
    *,
    lengths: list[float],
    policies: list[str],
    subjects: set[str] | None,
    skip_stats: bool,
) -> None:
    condition_windows = [
        row
        for row in read_csv(CONDITION_WINDOWS)
        if row["primary_analysis_eligible"] == "yes"
        and row["window_type"] in {"baseline", "condition"}
        and (subjects is None or row["subject_id"] in subjects)
    ]
    if not condition_windows:
        raise ValueError("No eligible condition windows selected")

    for seconds in lengths:
        output = ad_window_path(seconds)
        output.parent.mkdir(parents=True, exist_ok=True)
        build_ad_windows(
            AD_MANIFEST,
            AD_VISIBILITY,
            CONDITION_WINDOWS,
            output,
            window_seconds=seconds,
        )

    windows_by_subject: dict[str, list[dict[str, str]]] = defaultdict(list)
    for window in condition_windows:
        windows_by_subject[window["subject_id"]].append(window)
    ad_windows_by_length = {
        seconds: [
            row
            for row in read_csv(ad_window_path(seconds))
            if row["primary_analysis_eligible"] == "yes"
            and (subjects is None or row["subject_id"] in subjects)
        ]
        for seconds in lengths
    }

    for policy_name in policies:
        policy_path = POLICIES[policy_name]
        policy = load_policy(policy_path)
        epoch_rejection = policy["epoch_rejection"]
        condition_accum: dict[float, list[dict[str, Any]]] = {
            seconds: [] for seconds in lengths
        }
        ad_accum: dict[float, list[dict[str, Any]]] = {
            seconds: [] for seconds in lengths
        }
        print(f"\n=== policy {policy_name} ===", flush=True)
        feature_ready = all(
            (feature_dir(seconds, policy_name) / "condition_features.csv").exists()
            and (feature_dir(seconds, policy_name) / "ad_response_features.csv").exists()
            for seconds in lengths
        )
        if feature_ready:
            print(
                f"resume: {policy_name} features already exist; running stats only",
                flush=True,
            )
            for seconds in lengths:
                run_stats(seconds, policy_name, skip_stats=skip_stats)
            run_stats(REUSED_SECONDS, policy_name, skip_stats=skip_stats)
            continue
        for subject_id in sorted(windows_by_subject):
            subject_windows = windows_by_subject[subject_id]
            first = subject_windows[0]
            print(f"{subject_id}: cleaning ({policy_name})", flush=True)
            raw, report = clean_recording(
                subject_id=subject_id,
                xdf_path=REPOSITORY_ROOT / first["source_xdf"],
                canonical_markers_path=(
                    REPOSITORY_ROOT / first["source_canonical_markers"]
                ),
                channel_qc_path=CHANNEL_QC,
                policy_path=policy_path,
            )
            for seconds in lengths:
                condition_accum[seconds].extend(
                    extract_condition_epochs(
                        raw=raw,
                        windows=subject_windows,
                        epoch_seconds=seconds,
                        epoch_rejection=epoch_rejection,
                        ica_applied=report.ica_applied,
                    )
                )
                ad_accum[seconds].extend(
                    extract_ad_epochs(
                        raw=raw,
                        windows=[
                            row
                            for row in ad_windows_by_length[seconds]
                            if row["subject_id"] == subject_id
                        ],
                        epoch_rejection=epoch_rejection,
                        ica_applied=report.ica_applied,
                    )
                )
            del raw

        for seconds in lengths:
            output = feature_dir(seconds, policy_name)
            output.mkdir(parents=True, exist_ok=True)
            print(f"{policy_name} {seconds:g}s: writing features", flush=True)
            write_path_a(condition_accum[seconds], epoch_rejection, output)
            write_path_b(ad_accum[seconds], output)
            run_stats(seconds, policy_name, skip_stats=skip_stats)

        run_stats(REUSED_SECONDS, policy_name, skip_stats=skip_stats)

    if not skip_stats:
        write_grid_summary(lengths, policies)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lengths",
        type=float,
        nargs="+",
        default=list(DEFAULT_LENGTHS),
        help="Epoch/window durations to rebuild. 4 s is reused, not rebuilt.",
    )
    parser.add_argument(
        "--policies",
        nargs="+",
        default=["ica", "no_ica"],
        choices=sorted(POLICIES),
    )
    parser.add_argument("--subjects", nargs="+")
    parser.add_argument(
        "--skip-stats",
        action="store_true",
        help="Write features only (smoke tests).",
    )
    args = parser.parse_args()
    lengths = [float(value) for value in args.lengths]
    if REUSED_SECONDS in lengths:
        lengths = [value for value in lengths if value != REUSED_SECONDS]
        print("Skipping rebuild of 4 s; reusing existing primary / no-ICA archives")
    run_grid(
        lengths=lengths,
        policies=list(args.policies),
        subjects=set(args.subjects) if args.subjects else None,
        skip_stats=args.skip_stats,
    )


if __name__ == "__main__":
    main()
