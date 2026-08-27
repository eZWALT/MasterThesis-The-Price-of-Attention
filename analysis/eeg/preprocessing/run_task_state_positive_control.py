"""Read-versus-write EEG positive control (ICA primary, 4 s).

Sanity check, not Q1/Q2. Person-level median of (writing − reading) on the
same 16 spectral features. Holm is across the two confirmatory features.
Does not replace Dataset A or Dataset B Gold.
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats


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

from build_condition_contrasts import (  # noqa: E402
    FEATURE_TIERS,
    confidence_interval,
    holm_adjust,
    mean,
    write_csv,
)
from channel_sets import (  # noqa: E402
    assert_output_allowed,
    rejection_channel_spec,
    require_ready,
    resolve_channel_set,
    suggested_sensitivity_dir,
    suggested_stats_dir,
)
from build_condition_features import (  # noqa: E402
    SUMMARY_FEATURES,
    quality_features,
    spectral_features,
)
from build_task_state_windows import run as build_windows  # noqa: E402
from clean_eeg import clean_recording, load_policy  # noqa: E402


WINDOW_SECONDS = 4.0
CHANNEL_QC = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/audits/eeg_channel_quality.csv"
)
POLICY = SIGNAL_DIR / "cleaning_policy.json"
FEATURE_OUTPUT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/task_state"
)
STATS_OUTPUT = REPOSITORY_ROOT / (
    "analysis/eeg/statistics/outputs/task_state"
)
WINDOWS_OUTPUT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/task_state_windows.csv"
)
MANIFEST = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/canonical_marker_manifest.csv"
)
CONDITIONS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/condition_windows.csv"
)


def feature_row(
    window: dict[str, str],
    *,
    data_v: np.ndarray,
    sfreq: float,
    channel_names: list[str],
    epoch_rejection: dict[str, Any],
    ica_applied: bool,
    channel_set=None,
) -> dict[str, Any]:
    policy = resolve_channel_set(channel_set)
    quality = quality_features(
        data_v,
        channel_names,
        rejection_channels=rejection_channel_spec(policy),
    )
    rejection: list[str] = []
    if float(quality["max_peak_to_peak_uv"]) > float(
        epoch_rejection["max_peak_to_peak_uv"]
    ):
        rejection.append("gross_peak_to_peak")
    if (
        epoch_rejection["reject_near_flat_channels"]
        and int(quality["near_flat_channel_count"]) > 0
    ):
        rejection.append("near_flat_channel")
    row: dict[str, Any] = {
        "subject_id": window["subject_id"],
        "experiment_id": window["experiment_id"],
        "window_id": window["window_id"],
        "pair_id": window["pair_id"],
        "state": window["state"],
        "condition": window["condition"],
        "ad_mode": window["ad_mode"],
        "turn_index": window["turn_index"],
        "start_eeg_offset_s": window["start_eeg_offset_s"],
        "end_eeg_offset_s": window["end_eeg_offset_s"],
        "duration_s": window["duration_s"],
        "gap_s": window["gap_s"],
        "sampling_rate_hz": f"{sfreq:.6f}",
        "channel_count": len(channel_names),
        "ica_applied": "yes" if ica_applied else "no",
        "artifact_policy_status": epoch_rejection["status"],
        **quality,
        "retained_by_policy": "no" if rejection else "yes",
        "artifact_rejection_reason": ";".join(rejection),
        **spectral_features(
            data_v,
            sfreq=sfreq,
            channel_names=channel_names,
            channel_set=policy,
        ),
        **(
            {"channel_set_policy_version": policy.policy_version}
            if not policy.is_primary
            else {}
        ),
        "source_log": window["source_log"],
        "source_xdf": window["source_xdf"],
        "source_xdf_sha256": window["source_xdf_sha256"],
    }
    return row


def pair_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_state = {row["state"]: row for row in rows}
    if set(by_state) != {"reading", "writing"}:
        raise ValueError(f"{rows[0]['pair_id']} lacks reading and writing")
    reading = by_state["reading"]
    writing = by_state["writing"]
    eligible = (
        reading["retained_by_policy"] == "yes"
        and writing["retained_by_policy"] == "yes"
    )
    output: dict[str, Any] = {
        "subject_id": reading["subject_id"],
        "experiment_id": reading["experiment_id"],
        "pair_id": reading["pair_id"],
        "condition": reading["condition"],
        "ad_mode": reading["ad_mode"],
        "turn_index": reading["turn_index"],
        "gap_s": reading["gap_s"],
        "reading_retained": reading["retained_by_policy"],
        "writing_retained": writing["retained_by_policy"],
        "primary_analysis_eligible": "yes" if eligible else "no",
        "exclusion_reason": "" if eligible else "gross_artifact_in_pair",
        "ica_applied": reading["ica_applied"],
    }
    for feature in SUMMARY_FEATURES:
        read_value = float(reading[feature])
        write_value = float(writing[feature])
        output[f"{feature}_reading"] = read_value
        output[f"{feature}_writing"] = write_value
        output[f"{feature}_writing_minus_reading"] = write_value - read_value
    return output


def person_medians(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pairs:
        if row["primary_analysis_eligible"] == "yes":
            by_subject[row["subject_id"]].append(row)
    summaries: list[dict[str, Any]] = []
    for subject_id in sorted(by_subject):
        rows = by_subject[subject_id]
        summary: dict[str, Any] = {
            "subject_id": subject_id,
            "eligible_pair_count": len(rows),
            "ica_applied": rows[0]["ica_applied"],
            "primary_analysis_eligible": "yes" if len(rows) >= 5 else "no",
        }
        for feature in SUMMARY_FEATURES:
            values = [float(row[f"{feature}_writing_minus_reading"]) for row in rows]
            summary[f"{feature}_median"] = float(np.median(values))
            summary[f"{feature}_mean"] = float(np.mean(values))
        summaries.append(summary)
    return summaries


def test_row(
    *,
    feature: str,
    tier: str,
    values: list[float],
) -> dict[str, Any]:
    array = np.asarray(values, dtype=float)
    lower, upper = confidence_interval(values)
    t_result = stats.ttest_1samp(array, 0.0)
    try:
        wilcoxon = stats.wilcoxon(array)
        w_stat = float(wilcoxon.statistic)
        w_p = float(wilcoxon.pvalue)
    except ValueError:
        w_stat, w_p = 0.0, 1.0
    sd = float(np.std(array, ddof=1))
    return {
        "contrast_id": "writing_minus_reading",
        "contrast_tier": "primary" if tier == "primary" else "secondary",
        "feature": feature,
        "feature_tier": tier,
        "metric": "person_median_of_turn_differences",
        "n_participants": len(values),
        "mean_difference": mean(values),
        "sd_difference": sd,
        "ci_lower": lower,
        "ci_upper": upper,
        "cohen_dz": mean(values) / sd if sd > 0 else math.nan,
        "t_statistic": float(t_result.statistic),
        "p_t_raw": float(t_result.pvalue),
        "p_t_holm": "",
        "wilcoxon_statistic": w_stat,
        "p_wilcoxon_raw": w_p,
        "p_wilcoxon_holm": "",
        "correction_family": (
            "primary_task_state__writing_minus_reading"
            if tier == "primary"
            else "secondary_uncorrected"
        ),
        "dataset_status": "task_state_positive_control_v1",
    }


def contrast_tables(summaries: list[dict[str, Any]]) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    eligible = [
        row for row in summaries if row["primary_analysis_eligible"] == "yes"
    ]
    if len(eligible) < 15:
        raise ValueError(
            f"Only {len(eligible)} participants have ≥5 eligible read/write pairs"
        )
    tests: list[dict[str, Any]] = []
    scores: list[dict[str, Any]] = []
    for feature, tier in FEATURE_TIERS.items():
        values = [float(row[f"{feature}_median"]) for row in eligible]
        for row, value in zip(eligible, values):
            scores.append(
                {
                    "subject_id": row["subject_id"],
                    "contrast_id": "writing_minus_reading",
                    "feature": feature,
                    "feature_tier": tier,
                    "eligible_pair_count": row["eligible_pair_count"],
                    "difference": value,
                }
            )
        tests.append(test_row(feature=feature, tier=tier, values=values))
    family = [row for row in tests if row["feature_tier"] == "primary"]
    adjusted_t = holm_adjust([float(row["p_t_raw"]) for row in family])
    adjusted_w = holm_adjust([float(row["p_wilcoxon_raw"]) for row in family])
    for row, p_t, p_w in zip(family, adjusted_t, adjusted_w):
        row["p_t_holm"] = p_t
        row["p_wilcoxon_holm"] = p_w
    return tests, scores


def extract_features(
    windows: list[dict[str, str]],
    channel_set=None,
) -> list[dict[str, Any]]:
    policy = load_policy(POLICY)
    epoch_rejection = policy["epoch_rejection"]
    by_subject: dict[str, list[dict[str, str]]] = defaultdict(list)
    for window in windows:
        if window["primary_analysis_eligible"] != "yes":
            continue
        by_subject[window["subject_id"]].append(window)
    rows: list[dict[str, Any]] = []
    for subject_id in sorted(by_subject):
        subject_windows = by_subject[subject_id]
        source = subject_windows[0]
        print(f"{subject_id}: cleaning task-state windows", flush=True)
        raw, report = clean_recording(
            subject_id=subject_id,
            xdf_path=REPOSITORY_ROOT / source["source_xdf"],
            canonical_markers_path=REPOSITORY_ROOT
            / source["source_canonical_markers"],
            channel_qc_path=CHANNEL_QC,
            policy_path=POLICY,
        )
        sfreq = float(raw.info["sfreq"])
        for window in subject_windows:
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
                    ica_applied=report.ica_applied,
                    channel_set=channel_set,
                )
            )
        del raw
    return rows


def run(
    *,
    skip_extract: bool = False,
    channel_set_path: Path | None = None,
    feature_output: Path | None = None,
    stats_output: Path | None = None,
) -> None:
    channel_set = resolve_channel_set(channel_set_path)
    require_ready(channel_set)
    if feature_output is None:
        feature_output = (
            FEATURE_OUTPUT
            if channel_set.is_primary
            else REPOSITORY_ROOT / suggested_sensitivity_dir(channel_set)
        )
    if stats_output is None:
        stats_output = (
            STATS_OUTPUT
            if channel_set.is_primary
            else REPOSITORY_ROOT / suggested_stats_dir(channel_set)
        )
    assert_output_allowed(
        channel_set,
        feature_output / "task_state_person_features.csv",
        stats_output / "eeg_task_state_contrasts.csv",
    )
    feature_output.mkdir(parents=True, exist_ok=True)
    stats_output.mkdir(parents=True, exist_ok=True)
    if skip_extract and (feature_output / "task_state_pair_features.csv").exists():
        from build_condition_contrasts import read_csv

        pairs = read_csv(feature_output / "task_state_pair_features.csv")
    else:
        windows = build_windows(MANIFEST, CONDITIONS, WINDOWS_OUTPUT)
        epoch_rows = extract_features(windows, channel_set=channel_set)
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in epoch_rows:
            grouped[str(row["pair_id"])].append(row)
        pairs = [pair_row(grouped[key]) for key in sorted(grouped)]
        write_csv(feature_output / "task_state_epoch_features.csv", epoch_rows)
        write_csv(feature_output / "task_state_pair_features.csv", pairs)
        print(f"Wrote {len(epoch_rows)} epochs and {len(pairs)} pairs")
    summaries = person_medians(pairs)
    write_csv(feature_output / "task_state_person_features.csv", summaries)
    tests, scores = contrast_tables(summaries)
    write_csv(stats_output / "eeg_task_state_contrasts.csv", tests)
    write_csv(stats_output / "eeg_task_state_contrast_scores.csv", scores)
    print(f"Wrote {len(tests)} task-state tests to {stats_output}")
    for row in tests:
        if row["feature_tier"] == "primary":
            holm = row["p_t_holm"]
            print(
                f"  {row['feature']}: mean={row['mean_difference']:+.3f} "
                f"raw={row['p_t_raw']:.4f} holm={holm} n={row['n_participants']}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Reuse existing task-state feature CSVs.",
    )
    parser.add_argument(
        "--channel-set-policy",
        type=Path,
        default=None,
        help=(
            "Optional channel-set JSON. Non-primary policies write under "
            "sensitivity/channel_sets/<version>/ and never replace the "
            "primary task-state tables."
        ),
    )
    args = parser.parse_args()
    run(
        skip_extract=args.skip_extract,
        channel_set_path=args.channel_set_policy,
    )


if __name__ == "__main__":
    main()
