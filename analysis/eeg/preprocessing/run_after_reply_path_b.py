"""Parallel Path B after the finished reply. Does not write golden Gold.

Lock: assistant_reply + frozen explicit banner lag, for ads and matched
no-ad. Cleans each recording once with apply_saved_ica. Writes only under
sensitivity/after_reply/.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


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

from build_ad_contrasts import run as build_ad_contrasts  # noqa: E402
from build_ad_features import feature_row, response_row  # noqa: E402
from build_ad_visibility import (  # noqa: E402
    condition_blocks,
    load_log,
    unix_time,
    xdf_projection,
)
from build_ad_windows import condition_lookup, window_pair  # noqa: E402
from build_after_reply_visibility import (  # noqa: E402
    banner_lag_s,
    run as build_visibility,
)
from build_condition_features import read_csv, write_csv  # noqa: E402
from clean_eeg import clean_recording, load_policy  # noqa: E402


LENGTHS = (2.0, 4.0, 8.0)
POLICY_PATH = SIGNAL_DIR / "cleaning_policy.json"
MANIFEST = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/canonical_marker_manifest.csv"
)
CONDITIONS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/condition_windows.csv"
)
CHANNEL_QC = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/audits/eeg_channel_quality.csv"
)
GOLDEN_CALIBRATION = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/ad_visibility_calibration.csv"
)
GOLDEN_VISIBILITY = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/ad_visibility_events.csv"
)
ROOT = REPOSITORY_ROOT / "src/project/logs/xdf/gold"
WINDOW_ROOT = ROOT / "windows/sensitivity/after_reply"
FEATURE_ROOT = ROOT / "features/sensitivity/after_reply"
STATS_ROOT = (
    REPOSITORY_ROOT / "analysis/eeg/statistics/outputs/sensitivity/after_reply"
)
CONFIRMATORY = {
    "fz_theta_power_db_uv2",
    "posterior_alpha_power_db_uv2",
}
FORBIDDEN = {
    REPOSITORY_ROOT / "src/project/logs/xdf/gold/windows/ad_visibility_events.csv",
    REPOSITORY_ROOT / "src/project/logs/xdf/gold/windows/ad_analysis_windows.csv",
    REPOSITORY_ROOT / "src/project/logs/xdf/gold/windows/ad_visibility_calibration.csv",
    REPOSITORY_ROOT / "src/project/logs/xdf/gold/features/ad_response_features.csv",
    REPOSITORY_ROOT / "src/project/logs/xdf/gold/features/ad_epoch_features.csv",
    REPOSITORY_ROOT
    / "analysis/eeg/statistics/outputs/eeg_ad_response_contrasts.csv",
    REPOSITORY_ROOT
    / "analysis/eeg/statistics/outputs/sensitivity/epoch_length_grid_comparison.csv",
}


def assert_parallel(path: Path) -> None:
    resolved = path.resolve()
    if resolved in {item.resolve() for item in FORBIDDEN}:
        raise RuntimeError(f"refusing to overwrite golden file: {path}")
    if "sensitivity/after_reply" not in str(resolved):
        raise RuntimeError(f"outputs must live under after_reply/: {path}")


def visibility_path() -> Path:
    return WINDOW_ROOT / "ad_visibility_events.csv"


def windows_path(seconds: float) -> Path:
    return WINDOW_ROOT / f"epoch_{seconds:g}s" / "ad_analysis_windows.csv"


def feature_dir(seconds: float) -> Path:
    return FEATURE_ROOT / f"epoch_{seconds:g}s" / "ica"


def stats_dir(seconds: float) -> Path:
    return STATS_ROOT / f"epoch_{seconds:g}s" / "ica"


def no_ad_rows(
    manifest: list[dict[str, str]],
    *,
    conditions: dict[tuple[str, str], dict[str, str]],
    lag_s: float,
    lag_p95_s: float,
    window_seconds: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in manifest:
        if source["study_protocol_eligible"] != "yes":
            continue
        markers = read_csv(Path(source["canonical_table"]))
        blocks = condition_blocks(load_log(Path(source["source_log"])))
        no_ad_block = next(
            block
            for block in blocks
            if block[0].get("data", {}).get("condition") == "no_ads"
        )
        for turn, timing in ((2, "early"), (4, "late")):
            reply = next(
                event
                for event in no_ad_block
                if event["event"] == "assistant_reply"
                and int(event.get("turn", 0)) == turn
            )
            onset_log = unix_time(reply) + lag_s
            onset_xdf, onset_eeg, alignment = xdf_projection(
                markers,
                onset_log,
            )
            rows.extend(
                window_pair(
                    subject_id=source["subject_id"],
                    experiment_id=source["experiment_id"],
                    reference_id=f"{source['subject_id']}__no_ad_{timing}",
                    reference_kind="matched_no_ad_reply",
                    condition="no_ads",
                    ad_mode="none",
                    matched_timing=timing,
                    matched_ad_conditions=f"inline_{timing};block_{timing}",
                    onset_eeg_offset_s=onset_eeg,
                    onset_xdf_timestamp_lsl=onset_xdf,
                    onset_log_unix=onset_log,
                    onset_estimator="assistant_reply_plus_banner_lag",
                    onset_status="derived_after_reply",
                    combined_timing_uncertainty_s=alignment + lag_p95_s,
                    condition_window=conditions[(source["subject_id"], "no_ads")],
                    source_log=source["source_log"],
                    source_canonical_markers=source["canonical_table"],
                    window_seconds=window_seconds,
                )
            )
    return rows


def ad_rows_from_visibility(
    visibility: list[dict[str, str]],
    *,
    manifests: dict[str, dict[str, str]],
    conditions: dict[tuple[str, str], dict[str, str]],
    window_seconds: float,
) -> list[dict[str, Any]]:
    from build_ad_windows import ad_rows

    return ad_rows(
        visibility,
        manifests=manifests,
        conditions=conditions,
        window_seconds=window_seconds,
    )


def write_windows(seconds: float) -> Path:
    output = windows_path(seconds)
    assert_parallel(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = read_csv(MANIFEST)
    manifests = {row["subject_id"]: row for row in manifest}
    conditions = condition_lookup(read_csv(CONDITIONS))
    lag_s, lag_p95_s = banner_lag_s(GOLDEN_CALIBRATION)
    rows = ad_rows_from_visibility(
        read_csv(visibility_path()),
        manifests=manifests,
        conditions=conditions,
        window_seconds=seconds,
    )
    rows.extend(
        no_ad_rows(
            manifest,
            conditions=conditions,
            lag_s=lag_s,
            lag_p95_s=lag_p95_s,
            window_seconds=seconds,
        )
    )
    write_csv(output, rows)
    eligible = sum(row["primary_analysis_eligible"] == "yes" for row in rows)
    print(f"{seconds:g}s windows: {len(rows)} ({eligible} eligible) -> {output}")
    return output


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


def write_path_b(epoch_rows: list[dict[str, Any]], output: Path) -> Path:
    assert_parallel(output)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in epoch_rows:
        grouped[str(row["reference_id"])].append(row)
    responses = [response_row(grouped[key]) for key in sorted(grouped)]
    epochs_path = output / "ad_epoch_features.csv"
    responses_path = output / "ad_response_features.csv"
    assert_parallel(epochs_path)
    assert_parallel(responses_path)
    write_csv(epochs_path, epoch_rows)
    write_csv(responses_path, responses)
    eligible = sum(row["primary_analysis_eligible"] == "yes" for row in responses)
    print(
        f"  Path B: {len(epoch_rows)} epochs, {len(responses)} pairs "
        f"({eligible} eligible)"
    )
    return responses_path


def write_onset_shift() -> Path:
    golden = {
        (row["subject_id"], row["condition"]): row
        for row in read_csv(GOLDEN_VISIBILITY)
        if row["primary_analysis_eligible"] == "yes"
    }
    after = {
        (row["subject_id"], row["condition"]): row
        for row in read_csv(visibility_path())
        if row["primary_analysis_eligible"] == "yes"
    }
    rows: list[dict[str, Any]] = []
    for key in sorted(set(golden) & set(after)):
        old = golden[key]
        new = after[key]
        shift = float(new["visual_onset_eeg_offset_s"]) - float(
            old["visual_onset_eeg_offset_s"]
        )
        rows.append(
            {
                "subject_id": key[0],
                "condition": key[1],
                "ad_mode": new["ad_mode"],
                "golden_estimator": old["estimator"],
                "after_reply_estimator": new["estimator"],
                "golden_onset_eeg_s": old["visual_onset_eeg_offset_s"],
                "after_reply_onset_eeg_s": new["visual_onset_eeg_offset_s"],
                "shift_s": f"{shift:.6f}",
            }
        )
    output = WINDOW_ROOT / "onset_shift_vs_golden.csv"
    assert_parallel(output)
    write_csv(output, rows)
    by_mode: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_mode[row["ad_mode"]].append(float(row["shift_s"]))
    print(f"Wrote onset shifts to {output}")
    for mode, values in sorted(by_mode.items()):
        print(
            f"  {mode}: n={len(values)} mean shift {float(np.mean(values)):+.3f} s "
            f"(min {min(values):+.3f}, max {max(values):+.3f})"
        )
    return output


def holm_significant(row: dict[str, str]) -> bool:
    value = row.get("p_t_holm", "")
    if value in ("", None):
        return False
    try:
        return float(value) < 0.05
    except ValueError:
        return False


def collect_rows(seconds: float) -> list[dict[str, Any]]:
    path = stats_dir(seconds) / "eeg_ad_response_contrasts.csv"
    rows: list[dict[str, Any]] = []
    for row in read_csv(path):
        raw_p = float(row["p_t_raw"])
        holm = holm_significant(row)
        rows.append(
            {
                "epoch_seconds": seconds,
                "policy": "ica",
                "path": "B",
                "lock": "after_reply",
                "contrast_id": row["contrast_id"],
                "feature": row["feature"],
                "feature_tier": row["feature_tier"],
                "n_participants": int(float(row["n_participants"])),
                "mean_difference": float(row["mean_difference"]),
                "p_t_raw": raw_p,
                "p_t_holm": (
                    float(row["p_t_holm"])
                    if row.get("p_t_holm") not in ("", None)
                    else None
                ),
                "holm_significant": holm,
                "raw_p_lt_05": raw_p < 0.05,
                "confirmatory": (
                    row["feature"] in CONFIRMATORY
                    and row.get("contrast_tier", "") == "primary"
                ),
            }
        )
    return rows


def write_grid() -> Path:
    rows: list[dict[str, Any]] = []
    for seconds in LENGTHS:
        rows.extend(collect_rows(seconds))
    output = STATS_ROOT / "after_reply_grid_comparison.csv"
    assert_parallel(output)
    write_csv(output, rows)
    hits = [row for row in rows if row["holm_significant"]]
    confirmatory = [row for row in hits if row["confirmatory"]]
    report = {
        "lock": "after_reply",
        "grid_seconds": list(LENGTHS),
        "policy": "ica",
        "n_tests": len(rows),
        "holm_hits": len(hits),
        "confirmatory_holm_hits": confirmatory,
        "exploratory_holm_hits": [
            {
                "epoch_seconds": row["epoch_seconds"],
                "contrast_id": row["contrast_id"],
                "feature": row["feature"],
                "p_t_holm": row["p_t_holm"],
                "mean_difference": row["mean_difference"],
                "n_participants": row["n_participants"],
            }
            for row in hits
            if not row["confirmatory"]
        ],
    }
    json_path = STATS_ROOT / "after_reply_grid_comparison.json"
    assert_parallel(json_path)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Holm hits: {len(hits)} (confirmatory {len(confirmatory)})")
    return output


def run(*, skip_features: bool) -> None:
    WINDOW_ROOT.mkdir(parents=True, exist_ok=True)
    FEATURE_ROOT.mkdir(parents=True, exist_ok=True)
    STATS_ROOT.mkdir(parents=True, exist_ok=True)
    assert_parallel(visibility_path())
    build_visibility(MANIFEST, visibility_path(), GOLDEN_CALIBRATION)
    write_onset_shift()
    for seconds in LENGTHS:
        write_windows(seconds)

    if not skip_features:
        policy = load_policy(POLICY_PATH)
        epoch_rejection = policy["epoch_rejection"]
        windows_by_length = {
            seconds: [
                row
                for row in read_csv(windows_path(seconds))
                if row["primary_analysis_eligible"] == "yes"
            ]
            for seconds in LENGTHS
        }
        subjects = sorted(
            {row["subject_id"] for row in windows_by_length[4.0]}
        )
        accum: dict[float, list[dict[str, Any]]] = {
            seconds: [] for seconds in LENGTHS
        }
        for subject_id in subjects:
            subject_windows = [
                row
                for row in windows_by_length[4.0]
                if row["subject_id"] == subject_id
            ]
            first = subject_windows[0]
            print(f"{subject_id}: cleaning (ICA apply only)", flush=True)
            raw, report = clean_recording(
                subject_id=subject_id,
                xdf_path=REPOSITORY_ROOT / first["source_xdf"],
                canonical_markers_path=(
                    REPOSITORY_ROOT / first["source_canonical_markers"]
                ),
                channel_qc_path=CHANNEL_QC,
                policy_path=POLICY_PATH,
            )
            if report.ica_applied is not True:
                raise RuntimeError(f"{subject_id}: ICA was not applied")
            for seconds in LENGTHS:
                accum[seconds].extend(
                    extract_ad_epochs(
                        raw=raw,
                        windows=[
                            row
                            for row in windows_by_length[seconds]
                            if row["subject_id"] == subject_id
                        ],
                        epoch_rejection=epoch_rejection,
                        ica_applied=True,
                    )
                )
            del raw

        for seconds in LENGTHS:
            output = feature_dir(seconds)
            output.mkdir(parents=True, exist_ok=True)
            print(f"after_reply {seconds:g}s: writing features", flush=True)
            responses = write_path_b(accum[seconds], output)
            stats = stats_dir(seconds)
            stats.mkdir(parents=True, exist_ok=True)
            assert_parallel(stats / "eeg_ad_response_contrasts.csv")
            build_ad_contrasts(responses, stats, min_participants=10)

    write_grid()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-features",
        action="store_true",
        help="Rebuild windows and the grid from existing features.",
    )
    args = parser.parse_args()
    run(skip_features=args.skip_features)


if __name__ == "__main__":
    main()
