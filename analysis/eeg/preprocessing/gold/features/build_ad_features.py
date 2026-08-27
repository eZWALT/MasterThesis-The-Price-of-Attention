"""Build pre/post advertisement and matched no-ad EEG feature tables."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
SIGNAL_DIR = REPOSITORY_ROOT / "analysis/eeg/preprocessing/silver/signal"
sys.path.insert(0, str(SIGNAL_DIR))

from clean_eeg import clean_recording, load_policy  # noqa: E402

from channel_sets import (  # noqa: E402
    ChannelSetPolicy,
    assert_output_allowed,
    rejection_channel_spec,
    require_ready,
    reroute_if_default,
    resolve_channel_set,
    suggested_sensitivity_dir,
)
from build_condition_features import (  # noqa: E402
    SUMMARY_FEATURES,
    quality_features,
    read_csv,
    spectral_features,
    write_csv,
)


DEFAULT_WINDOWS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/ad_analysis_windows.csv"
)
DEFAULT_CHANNEL_QC = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/audits/eeg_channel_quality.csv"
)
DEFAULT_EPOCHS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/ad_epoch_features.csv"
)
DEFAULT_RESPONSES = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/ad_response_features.csv"
)


def feature_row(
    window: dict[str, str],
    *,
    data_v,
    sfreq: float,
    channel_names: list[str],
    epoch_rejection: dict[str, Any],
    ica_applied: bool,
    channel_set: ChannelSetPolicy | Path | None = None,
) -> dict[str, Any]:
    policy = resolve_channel_set(channel_set)
    quality = quality_features(
        data_v,
        channel_names,
        rejection_channels=rejection_channel_spec(policy),
    )
    rejection_reasons: list[str] = []
    if float(quality["max_peak_to_peak_uv"]) > float(
        epoch_rejection["max_peak_to_peak_uv"]
    ):
        rejection_reasons.append("gross_peak_to_peak")
    if (
        epoch_rejection["reject_near_flat_channels"]
        and int(quality["near_flat_channel_count"]) > 0
    ):
        rejection_reasons.append("near_flat_channel")
    row: dict[str, Any] = {
        "subject_id": window["subject_id"],
        "experiment_id": window["experiment_id"],
        "window_id": window["window_id"],
        "reference_id": window["reference_id"],
        "reference_kind": window["reference_kind"],
        "phase": window["phase"],
        "condition": window["condition"],
        "ad_mode": window["ad_mode"],
        "matched_timing": window["matched_timing"],
        "matched_ad_conditions": window["matched_ad_conditions"],
        "reference_onset_eeg_offset_s": window[
            "reference_onset_eeg_offset_s"
        ],
        "onset_estimator": window["onset_estimator"],
        "onset_status": window["onset_status"],
        "combined_timing_uncertainty_s": window[
            "combined_timing_uncertainty_s"
        ],
        "start_eeg_offset_s": window["start_eeg_offset_s"],
        "end_eeg_offset_s": window["end_eeg_offset_s"],
        "duration_s": window["duration_s"],
        "sampling_rate_hz": f"{sfreq:.6f}",
        "channel_count": len(channel_names),
        "ica_applied": "yes" if ica_applied else "no",
        "artifact_policy_status": epoch_rejection["status"],
        "max_peak_to_peak_threshold_uv": epoch_rejection[
            "max_peak_to_peak_uv"
        ],
    }
    row.update(quality)
    row["retained_by_policy"] = "no" if rejection_reasons else "yes"
    row["artifact_rejection_reason"] = ";".join(rejection_reasons)
    row.update(
        spectral_features(
            data_v,
            sfreq=sfreq,
            channel_names=channel_names,
            channel_set=policy,
        )
    )
    if not policy.is_primary:
        row["channel_set_policy_version"] = policy.policy_version
    row["source_log"] = window["source_log"]
    row["source_xdf"] = window["source_xdf"]
    row["source_xdf_sha256"] = window["source_xdf_sha256"]
    row["source_canonical_markers"] = window["source_canonical_markers"]
    return row


def response_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_phase = {row["phase"]: row for row in rows}
    if set(by_phase) != {"pre", "post"}:
        raise ValueError(
            f"{rows[0]['reference_id']} does not have one pre and post row"
        )
    pre = by_phase["pre"]
    post = by_phase["post"]
    eligible = (
        pre["retained_by_policy"] == "yes"
        and post["retained_by_policy"] == "yes"
    )
    output: dict[str, Any] = {
        "subject_id": pre["subject_id"],
        "experiment_id": pre["experiment_id"],
        "reference_id": pre["reference_id"],
        "reference_kind": pre["reference_kind"],
        "condition": pre["condition"],
        "ad_mode": pre["ad_mode"],
        "matched_timing": pre["matched_timing"],
        "matched_ad_conditions": pre["matched_ad_conditions"],
        "reference_onset_eeg_offset_s": pre[
            "reference_onset_eeg_offset_s"
        ],
        "onset_estimator": pre["onset_estimator"],
        "onset_status": pre["onset_status"],
        "combined_timing_uncertainty_s": pre[
            "combined_timing_uncertainty_s"
        ],
        "pre_retained": pre["retained_by_policy"],
        "post_retained": post["retained_by_policy"],
        "primary_analysis_eligible": "yes" if eligible else "no",
        "exclusion_reason": "" if eligible else "gross_artifact_in_pair",
        "artifact_policy_status": pre["artifact_policy_status"],
        "ica_applied": pre["ica_applied"],
        **(
            {
                "channel_set_policy_version": pre[
                    "channel_set_policy_version"
                ]
            }
            if pre.get("channel_set_policy_version")
            else {}
        ),
    }
    for feature in SUMMARY_FEATURES:
        pre_value = float(pre[feature])
        post_value = float(post[feature])
        output[f"{feature}_pre"] = pre_value
        output[f"{feature}_post"] = post_value
        output[f"{feature}_post_minus_pre"] = post_value - pre_value
    output["source_log"] = pre["source_log"]
    output["source_xdf"] = pre["source_xdf"]
    output["source_xdf_sha256"] = pre["source_xdf_sha256"]
    return output


def build(
    *,
    windows_path: Path,
    channel_qc_path: Path,
    epochs_output: Path,
    responses_output: Path,
    subjects: set[str] | None,
    policy_path: Path,
    channel_set_path: Path | None = None,
) -> None:
    windows = [
        row
        for row in read_csv(windows_path)
        if row["primary_analysis_eligible"] == "yes"
        and (subjects is None or row["subject_id"] in subjects)
    ]
    if not windows:
        raise ValueError("No eligible ad-analysis windows selected")
    channel_set = resolve_channel_set(channel_set_path)
    require_ready(channel_set)
    target = REPOSITORY_ROOT / suggested_sensitivity_dir(channel_set)
    epochs_output = reroute_if_default(
        channel_set,
        epochs_output,
        DEFAULT_EPOCHS,
        target / "ad_epoch_features.csv",
    )
    responses_output = reroute_if_default(
        channel_set,
        responses_output,
        DEFAULT_RESPONSES,
        target / "ad_response_features.csv",
    )
    assert_output_allowed(channel_set, epochs_output, responses_output)
    policy = load_policy(policy_path)
    epoch_rejection = policy["epoch_rejection"]

    grouped_subjects: dict[str, list[dict[str, str]]] = defaultdict(list)
    for window in windows:
        grouped_subjects[window["subject_id"]].append(window)

    feature_rows: list[dict[str, Any]] = []
    for subject_id in sorted(grouped_subjects):
        subject_windows = grouped_subjects[subject_id]
        source = subject_windows[0]
        print(f"{subject_id}: cleaning ad-analysis windows", flush=True)
        raw, cleaning_report = clean_recording(
            subject_id=subject_id,
            xdf_path=REPOSITORY_ROOT / source["source_xdf"],
            canonical_markers_path=(
                REPOSITORY_ROOT / source["source_canonical_markers"]
            ),
            channel_qc_path=channel_qc_path,
            policy_path=policy_path,
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
            feature_rows.append(
                feature_row(
                    window,
                    data_v=data_v,
                    sfreq=sfreq,
                    channel_names=raw.ch_names,
                    epoch_rejection=epoch_rejection,
                    ica_applied=cleaning_report.ica_applied,
                    channel_set=channel_set,
                )
            )

    grouped_references: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in feature_rows:
        grouped_references[str(row["reference_id"])].append(row)
    responses = [
        response_row(grouped_references[key])
        for key in sorted(grouped_references)
    ]
    write_csv(epochs_output, feature_rows)
    write_csv(responses_output, responses)
    print(f"Wrote {len(feature_rows)} ad epochs to {epochs_output}")
    print(f"Wrote {len(responses)} response pairs to {responses_output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--windows", type=Path, default=DEFAULT_WINDOWS)
    parser.add_argument("--channel-qc", type=Path, default=DEFAULT_CHANNEL_QC)
    parser.add_argument("--epochs-output", type=Path, default=DEFAULT_EPOCHS)
    parser.add_argument(
        "--responses-output",
        type=Path,
        default=DEFAULT_RESPONSES,
    )
    parser.add_argument("--subjects", nargs="+")
    parser.add_argument(
        "--policy",
        type=Path,
        default=SIGNAL_DIR / "cleaning_policy.json",
    )
    parser.add_argument(
        "--channel-set-policy",
        type=Path,
        default=None,
        help=(
            "Optional channel-set JSON. Default is the frozen current_v1 "
            "contract. Non-primary policies cannot write primary Gold."
        ),
    )
    args = parser.parse_args()
    build(
        windows_path=args.windows,
        channel_qc_path=args.channel_qc,
        epochs_output=args.epochs_output,
        responses_output=args.responses_output,
        subjects=set(args.subjects) if args.subjects else None,
        policy_path=args.policy,
        channel_set_path=args.channel_set_policy,
    )


if __name__ == "__main__":
    main()
