"""Aggregate machine-checkable evidence for the EEG preprocessing contract."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
XDF_ROOT = REPOSITORY_ROOT / "src/project/logs/xdf"
POLICY_PATH = REPOSITORY_ROOT / (
    "analysis/eeg/preprocessing/silver/signal/cleaning_policy.json"
)
MARKER_MANIFEST_PATH = XDF_ROOT / (
    "silver/canonical_marker_manifest.csv"
)
MARKER_LOO_PATH = XDF_ROOT / (
    "silver/validation/leave_one_marker_out_events.csv"
)
VISUAL_PATH = XDF_ROOT / (
    "silver/validation/cleaning_visual/cleaning_visual_validation.json"
)
CONDITION_PATH = XDF_ROOT / (
    "gold/features/condition_feature_validation.json"
)
CONDITION_EPOCHS_PATH = XDF_ROOT / (
    "gold/features/condition_epoch_features.csv"
)
AD_PATH = XDF_ROOT / "gold/features/ad_feature_validation.json"
ENGAGEMENT_PATH = XDF_ROOT / (
    "gold/features/engagement_feature_validation.json"
)
SENSITIVITY_PATH = REPOSITORY_ROOT / (
    "analysis/eeg/statistics/outputs/"
    "threshold_sensitivity_comparison.json"
)
OUTPUT_PATH = XDF_ROOT / (
    "gold/validation/preprocessing_soundness.json"
)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def marker_evidence() -> dict[str, Any]:
    manifest = read_csv(MARKER_MANIFEST_PATH)
    eligible = [
        row for row in manifest if row["study_protocol_eligible"] == "yes"
    ]
    loo = read_csv(MARKER_LOO_PATH)
    absolute_errors = [float(row["absolute_error_s"]) for row in loo]
    checks = {
        "eighteen_lab_recordings_eligible": len(eligible) == 18,
        "all_analysis_events_available": all(
            int(row["unavailable_event_count"]) == 0 for row in eligible
        ),
        "subject_19_end_is_metadata_only_not_fabricated": (
            sum(
                int(row["metadata_only_derived_event_count"])
                for row in eligible
            )
            == 1
            and next(
                row
                for row in eligible
                if row["subject_id"] == "lab_subject_19"
            )["complete_canonical_timeline"]
            == "no"
        ),
        "all_eligible_clock_fits_valid": all(
            row["fit_valid"] == "yes" for row in eligible
        ),
        "all_eligible_sources_hashed": all(
            len(row["source_xdf_sha256"]) == 64 for row in eligible
        ),
        "leave_one_out_prevents_hidden_marker_rematching": all(
            row["held_out_event_rematched"] == "no" for row in loo
        ),
    }
    return {
        "checks": checks,
        "eligible_recording_count": len(eligible),
        "complete_canonical_timeline_count": sum(
            row["complete_canonical_timeline"] == "yes" for row in eligible
        ),
        "leave_one_marker_out_event_count": len(loo),
        "leave_one_marker_out_median_absolute_error_s": float(
            sorted(absolute_errors)[len(absolute_errors) // 2]
        ),
        "leave_one_marker_out_p95_absolute_error_s": float(
            sorted(absolute_errors)[
                math.ceil(0.95 * len(absolute_errors)) - 1
            ]
        ),
        "leave_one_marker_out_maximum_absolute_error_s": max(
            absolute_errors
        ),
    }


def signal_evidence(
    policy: dict[str, Any],
    visual: dict[str, Any],
) -> dict[str, Any]:
    filtering_pass = all(
        row["line_noise_pass"] and row["average_reference_pass"]
        for row in visual["filtering_checks"]
    )
    interpolation_pass = all(
        row["amplitude_pass"] and row["spatial_consistency_pass"]
        for row in visual["interpolation_checks"]
    )
    checks = {
        "policy_is_frozen_v5_ica_primary": (
            policy["policy_version"] == "frozen_v5_ica_primary"
            and policy["status"] == "frozen"
        ),
        "epoch_policy_is_frozen_v3": (
            policy["epoch_rejection"]["status"] == "frozen_v3"
        ),
        "primary_threshold_is_1050_uv": math.isclose(
            float(policy["epoch_rejection"]["max_peak_to_peak_uv"]),
            1050.0,
        ),
        "current_features_are_ica_primary_with_no_ica_sensitivity": (
            policy["ica"]["enabled"] is True
            and policy["ica"]["status"]
            == "approved_as_primary_2026-08-19"
            and math.isclose(
                float(policy["ica"]["pca_explained_variance"]),
                0.99,
            )
            and policy["ica"].get("no_ica_sensitivity_required") is True
        ),
        "objective_visual_checks_pass": (
            visual["objective_status"] == "passed"
            and filtering_pass
            and interpolation_pass
        ),
    }
    return {
        "checks": checks,
        "policy_version": policy["policy_version"],
        "epoch_policy_status": policy["epoch_rejection"]["status"],
        "primary_peak_to_peak_threshold_uv": policy["epoch_rejection"][
            "max_peak_to_peak_uv"
        ],
        "online_reference": policy["input"]["online_reference"],
        "ground": policy["input"]["ground"],
        "ica_status": policy["ica"]["status"],
        "ica_pca_explained_variance": policy["ica"][
            "pca_explained_variance"
        ],
        "filtering_recording_count": len(visual["filtering_checks"]),
        "interpolated_channel_count": len(visual["interpolation_checks"]),
        "human_visual_signoff": visual["human_visual_signoff"],
    }


def gold_evidence(
    condition: dict[str, Any],
    ad: dict[str, Any],
    engagement: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    epoch_rows = read_csv(CONDITION_EPOCHS_PATH)
    sampling_rates = {
        float(row["sampling_rate_hz"]) for row in epoch_rows
    }
    minimum_nyquist_hz = min(sampling_rates) / 2.0
    lowpass_hz = float(policy["filtering"]["lowpass_hz"])
    checks = {
        "condition_dataset_passes": (
            condition["status"] == "passed"
            and condition["subject_count"] == 18
            and condition["duplicate_epoch_key_count"] == 0
            and condition["non_finite_feature_count"] == 0
            and condition["artifact_policy_status"] == "frozen_v3"
        ),
        "all_condition_windows_eligible": (
            condition["ineligible_window_count"] == 0
        ),
        "ad_dataset_passes": (
            ad["status"] == "passed"
            and ad["subject_count"] == 18
            and ad["duplicate_key_count"] == 0
            and ad["non_finite_feature_count"] == 0
            and ad["artifact_policy_status"] == "frozen_v3"
        ),
        "all_ad_pairs_eligible": (
            ad["eligible_response_pair_count"]
            == ad["response_pair_count"]
        ),
        "ad_timing_supports_four_second_spectra": (
            ad["maximum_combined_timing_uncertainty_s"] < 0.5
        ),
        "engagement_implementations_pass": (
            engagement["validation_status"] == "pass"
        ),
        "lowpass_is_below_actual_nyquist": (
            lowpass_hz < minimum_nyquist_hz
        ),
    }
    return {
        "checks": checks,
        "condition_epoch_count": condition["epoch_count"],
        "condition_retained_epoch_count": condition[
            "retained_epoch_count"
        ],
        "condition_retained_epoch_fraction": condition[
            "retained_epoch_fraction"
        ],
        "ad_response_pair_count": ad["response_pair_count"],
        "eligible_ad_response_pair_count": ad[
            "eligible_response_pair_count"
        ],
        "maximum_ad_timing_uncertainty_s": ad[
            "maximum_combined_timing_uncertainty_s"
        ],
        "engagement_feature_count": len(engagement["definitions"]),
        "observed_sampling_rates_hz": sorted(sampling_rates),
        "minimum_nyquist_hz": minimum_nyquist_hz,
        "lowpass_hz": lowpass_hz,
        "nyquist_to_lowpass_ratio": minimum_nyquist_hz / lowpass_hz,
    }


def sensitivity_evidence(report: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "threshold_sensitivity_comparison_passes": (
            report["status"] == "pass"
        ),
        "confirmatory_conclusions_are_stable": (
            report["checks"][
                "all_sensitivities_preserve_corrected_conclusions"
            ]
            and report["checks"][
                "all_sensitivities_preserve_confirmatory_directions"
            ]
        ),
    }
    return {
        "checks": checks,
        "primary_policy": report["primary_policy"],
        "sensitivity_summaries": {
            policy: {
                "condition_direction_change_count": comparison["condition"][
                    "direction_change_count_all_features"
                ],
                "ad_direction_change_count_all_features": comparison[
                    "ad_response"
                ]["direction_change_count_all_features"],
                "ad_direction_changes_all_features": comparison[
                    "ad_response"
                ]["direction_changes_all_features"],
            }
            for policy, comparison in report["sensitivities"].items()
        },
    }


def main() -> None:
    policy = read_json(POLICY_PATH)
    visual = read_json(VISUAL_PATH)
    condition = read_json(CONDITION_PATH)
    ad = read_json(AD_PATH)
    engagement = read_json(ENGAGEMENT_PATH)
    sensitivity = read_json(SENSITIVITY_PATH)
    sections = {
        "marker_reconstruction": marker_evidence(),
        "signal_cleaning": signal_evidence(policy, visual),
        "gold_datasets": gold_evidence(
            condition,
            ad,
            engagement,
            policy,
        ),
        "threshold_sensitivity": sensitivity_evidence(sensitivity),
    }
    machine_checks = {
        f"{section}.{name}": value
        for section, evidence in sections.items()
        for name, value in evidence["checks"].items()
    }
    all_machine_checks_pass = all(machine_checks.values())
    report = {
        "status": (
            "machine_checks_passed_human_gates_closed"
            if all_machine_checks_pass
            and visual["human_visual_signoff"] == "approved"
            and policy["ica"]["enabled"] is True
            else "machine_checks_passed_human_gates_pending"
            if all_machine_checks_pass
            else "machine_checks_failed"
        ),
        "all_machine_checks_pass": all_machine_checks_pass,
        "machine_checks": machine_checks,
        **sections,
        "human_gates": {
            "acquisition_reference_confirmed": (
                policy["input"]["online_reference"] == "Cz"
                and policy["input"]["ground"] == "Fpz"
                and policy["input"]["online_reference_status"]
                == "reported_by_lab_2026-08-04"
            ),
            "filtering_and_interpolation_figures_signed_off": (
                visual["human_visual_signoff"] == "approved"
            ),
            "primary_ica_policy_accepted": (
                policy["ica"]["enabled"] is True
                and policy["ica"]["status"]
                == "approved_as_primary_2026-08-19"
            ),
        },
        "interpretation_limits": [
            "Cz online reference and Fpz ground are established by laboratory "
            "feedback; XDF does not encode those roles directly.",
            "Fp1/Fp2 are ocular-sensitive frontal EEG proxies, not dedicated "
            "EOG channels; ICA component rejection requires visual and "
            "topographic validation.",
            "The mixed, mostly-open baseline is not a controlled resting state.",
            "Derived ad onsets support spectral windows, not ERP latency claims.",
            "Engagement indices are exploratory unless preregistered otherwise.",
        ],
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    if not all_machine_checks_pass:
        failed = [
            name for name, passed in machine_checks.items() if not passed
        ]
        raise ValueError(f"Preprocessing soundness checks failed: {failed}")
    print(
        "All machine-checkable preprocessing checks passed; "
        f"wrote {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
