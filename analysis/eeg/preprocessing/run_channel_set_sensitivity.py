"""Rebuild Dataset A/B (and optionally task-state) for channel-set policies.

Does not write primary Gold. Does not overwrite ICA models. Refuses
unfilled policies. Accepts one or more non-primary policies and cleans
each recording once, then writes each policy under:

    src/project/logs/xdf/gold/features/sensitivity/channel_sets/<version>/
    analysis/eeg/statistics/outputs/sensitivity/channel_sets/<version>/

This is a robustness branch, not a new confirmatory family.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PREPROCESSING = REPOSITORY_ROOT / "analysis/eeg/preprocessing"
FEATURE_DIR = PREPROCESSING / "gold/features"
SIGNAL_DIR = PREPROCESSING / "silver/signal"
STATISTICS_DIR = REPOSITORY_ROOT / "analysis/eeg/statistics"
sys.path.insert(0, str(FEATURE_DIR))
sys.path.insert(0, str(SIGNAL_DIR))
sys.path.insert(0, str(STATISTICS_DIR))
sys.path.insert(0, str(PREPROCESSING))

from channel_sets import (  # noqa: E402
    ChannelSetPolicy,
    ANGELA_CODE_PATH,
    LITERATURE_ROI_PATH,
    WANG2022_PATH,
    assert_output_allowed,
    load_channel_set_policy,
    require_ready,
    suggested_sensitivity_dir,
    suggested_stats_dir,
)
from build_ad_features import (  # noqa: E402
    feature_row as ad_feature_row,
    response_row as ad_response_row,
)
from build_ad_contrasts import run as build_ad_contrasts  # noqa: E402
from build_condition_contrasts import run as build_condition_contrasts  # noqa: E402
from build_condition_features import (  # noqa: E402
    add_baseline_deltas,
    complete_epoch_bounds,
    epoch_row,
    read_csv,
    summarize_window,
    write_csv,
)
from clean_eeg import clean_recording, load_policy  # noqa: E402
from validate_ad_features import validate as validate_ad  # noqa: E402
from validate_condition_features import validate as validate_condition  # noqa: E402
from validate_engagement_features import validate as validate_engagement  # noqa: E402
from run_task_state_positive_control import run as run_task_state  # noqa: E402


CLEANING_POLICY = SIGNAL_DIR / "cleaning_policy.json"
CONDITION_WINDOWS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/condition_windows.csv"
)
AD_WINDOWS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/ad_analysis_windows.csv"
)
CHANNEL_QC = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/audits/eeg_channel_quality.csv"
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_ready_policies(paths: list[Path]) -> list[ChannelSetPolicy]:
    policies: list[ChannelSetPolicy] = []
    seen: set[str] = set()
    for path in paths:
        policy = load_channel_set_policy(path)
        print(f"policy: {policy.policy_version}")
        print(f"status: {policy.status}")
        print(f"role:   {policy.role}")
        try:
            require_ready(policy)
        except ValueError as exc:
            print(exc)
            raise SystemExit(2) from exc
        if policy.is_primary:
            raise SystemExit(
                "Refusing to run the sensitivity runner on the primary "
                "channel-set policy. Primary Gold is the default feature "
                "builders with no --channel-set-policy flag."
            )
        if policy.policy_version in seen:
            raise SystemExit(
                f"Duplicate channel-set policy version: {policy.policy_version}"
            )
        seen.add(policy.policy_version)
        policies.append(policy)
    return policies


def _group_by_subject(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["subject_id"]].append(row)
    return grouped


def _write_policy_outputs(
    policy: ChannelSetPolicy,
    *,
    feature_dir: Path,
    stats_dir: Path,
    condition_epochs: list[dict],
    ad_epochs: list[dict],
    include_task_state: bool,
) -> None:
    feature_dir.mkdir(parents=True, exist_ok=True)
    stats_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(policy.path, feature_dir / "channel_set_policy.json")

    condition_epochs_path = feature_dir / "condition_epoch_features.csv"
    condition_summary_path = feature_dir / "condition_features.csv"
    ad_epochs_path = feature_dir / "ad_epoch_features.csv"
    ad_responses_path = feature_dir / "ad_response_features.csv"
    assert_output_allowed(
        policy,
        condition_epochs_path,
        condition_summary_path,
        ad_epochs_path,
        ad_responses_path,
        stats_dir,
    )

    epoch_rejection = load_policy(CLEANING_POLICY)["epoch_rejection"]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in condition_epochs:
        grouped[str(row["window_id"])].append(row)
    summaries = [
        summarize_window(grouped[key], epoch_rejection)
        for key in sorted(grouped)
    ]
    add_baseline_deltas(summaries)
    write_csv(condition_epochs_path, condition_epochs)
    write_csv(condition_summary_path, summaries)
    print(f"Wrote {len(condition_epochs)} epochs to {condition_epochs_path}")
    print(f"Wrote {len(summaries)} window summaries to {condition_summary_path}")

    grouped_references: dict[str, list[dict]] = defaultdict(list)
    for row in ad_epochs:
        grouped_references[str(row["reference_id"])].append(row)
    responses = [
        ad_response_row(grouped_references[key])
        for key in sorted(grouped_references)
    ]
    write_csv(ad_epochs_path, ad_epochs)
    write_csv(ad_responses_path, responses)
    print(f"Wrote {len(ad_epochs)} ad epochs to {ad_epochs_path}")
    print(f"Wrote {len(responses)} response pairs to {ad_responses_path}")

    condition_report = validate_condition(
        condition_epochs_path,
        condition_summary_path,
        expected_ica_applied=True,
    )
    write_json(feature_dir / "condition_feature_validation.json", condition_report)
    ad_report = validate_ad(
        AD_WINDOWS,
        ad_epochs_path,
        ad_responses_path,
        expected_ica_applied=True,
    )
    write_json(feature_dir / "ad_feature_validation.json", ad_report)
    engagement_report = validate_engagement(
        condition_epochs_path,
        ad_epochs_path,
        CLEANING_POLICY,
        "frozen_v3",
        1050.0,
    )
    write_json(feature_dir / "engagement_feature_validation.json", engagement_report)

    build_condition_contrasts(condition_summary_path, stats_dir)
    build_ad_contrasts(ad_responses_path, stats_dir)

    if include_task_state:
        run_task_state(
            channel_set_path=policy.path,
            feature_output=feature_dir,
            stats_output=stats_dir,
        )

    write_json(
        feature_dir / "run_manifest.json",
        {
            "policy_version": policy.policy_version,
            "role": policy.role,
            "channel_set_policy": str(policy.path),
            "feature_dir": str(feature_dir),
            "stats_dir": str(stats_dir),
            "include_task_state": include_task_state,
            "confirmatory": False,
        },
    )
    print(f"Channel-set sensitivity written to {feature_dir}")


def run(
    *,
    channel_set_paths: list[Path],
    include_task_state: bool,
    dry_run: bool,
    subjects: set[str] | None,
) -> None:
    policies = _load_ready_policies(channel_set_paths)
    prepared: list[tuple[ChannelSetPolicy, Path, Path]] = []
    for policy in policies:
        feature_dir = REPOSITORY_ROOT / suggested_sensitivity_dir(policy)
        stats_dir = REPOSITORY_ROOT / suggested_stats_dir(policy)
        print(f"features: {feature_dir}")
        print(f"stats:    {stats_dir}")
        prepared.append((policy, feature_dir, stats_dir))
    if dry_run:
        print("Dry run. No recordings cleaned.")
        return

    condition_windows = [
        row
        for row in read_csv(CONDITION_WINDOWS)
        if row["primary_analysis_eligible"] == "yes"
        and row["window_type"] in {"baseline", "condition"}
        and (subjects is None or row["subject_id"] in subjects)
    ]
    ad_windows = [
        row
        for row in read_csv(AD_WINDOWS)
        if row["primary_analysis_eligible"] == "yes"
        and (subjects is None or row["subject_id"] in subjects)
    ]
    if not condition_windows:
        raise SystemExit("No eligible condition windows selected")
    if not ad_windows:
        raise SystemExit("No eligible ad-analysis windows selected")

    condition_by_subject = _group_by_subject(condition_windows)
    ad_by_subject = _group_by_subject(ad_windows)
    subject_ids = sorted(set(condition_by_subject) | set(ad_by_subject))
    policy_obj = load_policy(CLEANING_POLICY)
    epoch_rejection = policy_obj["epoch_rejection"]
    if not str(epoch_rejection.get("status", "")).startswith("frozen_"):
        raise SystemExit("Condition features require frozen epoch rejection")

    condition_rows: dict[str, list[dict]] = {
        policy.policy_version: [] for policy, _, _ in prepared
    }
    ad_rows: dict[str, list[dict]] = {
        policy.policy_version: [] for policy, _, _ in prepared
    }

    for subject_id in subject_ids:
        source = (condition_by_subject.get(subject_id) or ad_by_subject[subject_id])[0]
        print(f"{subject_id}: loading and cleaning once for {len(prepared)} policies", flush=True)
        raw, cleaning_report = clean_recording(
            subject_id=subject_id,
            xdf_path=REPOSITORY_ROOT / source["source_xdf"],
            canonical_markers_path=(
                REPOSITORY_ROOT / source["source_canonical_markers"]
            ),
            channel_qc_path=CHANNEL_QC,
            policy_path=CLEANING_POLICY,
        )
        sfreq = float(raw.info["sfreq"])
        n_times = int(raw.n_times)
        for window in condition_by_subject.get(subject_id, []):
            before = {
                policy.policy_version: len(condition_rows[policy.policy_version])
                for policy, _, _ in prepared
            }
            for epoch_index, start_sample, stop_sample in complete_epoch_bounds(
                start_s=float(window["start_eeg_offset_s"]),
                end_s=float(window["end_eeg_offset_s"]),
                sfreq=sfreq,
                epoch_seconds=4.0,
                raw_sample_count=n_times,
            ):
                data_v = raw.get_data(
                    start=start_sample,
                    stop=stop_sample,
                    picks="eeg",
                )
                for policy, _, _ in prepared:
                    condition_rows[policy.policy_version].append(
                        epoch_row(
                            window,
                            epoch_index=epoch_index,
                            start_sample=start_sample,
                            stop_sample=stop_sample,
                            sfreq=sfreq,
                            data_v=data_v,
                            channel_names=raw.ch_names,
                            epoch_rejection=epoch_rejection,
                            ica_applied=cleaning_report.ica_applied,
                            channel_set=policy,
                        )
                    )
            counts = ", ".join(
                f"{version}={len(condition_rows[version]) - before[version]}"
                for version in before
            )
            print(f"  {window['window_id']}: {counts} condition epochs", flush=True)
        for window in ad_by_subject.get(subject_id, []):
            start = int(round(float(window["start_eeg_offset_s"]) * sfreq))
            stop = int(round(float(window["end_eeg_offset_s"]) * sfreq))
            data_v = raw.get_data(start=start, stop=stop, picks="eeg")
            expected = int(round(float(window["duration_s"]) * sfreq))
            if data_v.shape[1] != expected:
                raise ValueError(
                    f"{window['window_id']}: expected {expected} samples, "
                    f"found {data_v.shape[1]}"
                )
            for policy, _, _ in prepared:
                ad_rows[policy.policy_version].append(
                    ad_feature_row(
                        window,
                        data_v=data_v,
                        sfreq=sfreq,
                        channel_names=raw.ch_names,
                        epoch_rejection=epoch_rejection,
                        ica_applied=cleaning_report.ica_applied,
                        channel_set=policy,
                    )
                )

    for policy, feature_dir, stats_dir in prepared:
        _write_policy_outputs(
            policy,
            feature_dir=feature_dir,
            stats_dir=stats_dir,
            condition_epochs=condition_rows[policy.policy_version],
            ad_epochs=ad_rows[policy.policy_version],
            include_task_state=include_task_state,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--channel-set-policy",
        type=Path,
        nargs="+",
        default=[LITERATURE_ROI_PATH],
        help=(
            "One or more non-primary channel-set JSON files. "
            f"Defaults to {LITERATURE_ROI_PATH.name}. "
            f"Wang zone branch: {WANG2022_PATH}. "
            f"Angela code lists: {ANGELA_CODE_PATH}."
        ),
    )
    parser.add_argument(
        "--with-task-state",
        action="store_true",
        help="Also rebuild the write−read positive control on each channel set.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--subjects",
        nargs="+",
        help="Optional subject IDs, for example: lab_subject_1 lab_subject_8",
    )
    args = parser.parse_args()
    run(
        channel_set_paths=list(args.channel_set_policy),
        include_task_state=args.with_task_state,
        dry_run=args.dry_run,
        subjects=set(args.subjects) if args.subjects else None,
    )


if __name__ == "__main__":
    main()
