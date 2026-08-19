"""Single-file unit and integration sanity checks for EEG metrics.

Run from the repository root:

    python -m unittest analysis/eeg/preprocessing/test_eeg_metrics.py -v

The synthetic tests verify formulas independently of the study data. The
integration tests verify generated primary and ICA datasets when those ignored,
reproducible outputs are available locally.
"""

from __future__ import annotations

import csv
import json
import math
import sys
import unittest
from pathlib import Path

import numpy as np


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
FEATURE_CODE = REPOSITORY_ROOT / (
    "analysis/eeg/preprocessing/gold/features"
)
SIGNAL_CODE = REPOSITORY_ROOT / (
    "analysis/eeg/preprocessing/silver/signal"
)
STATISTICS_CODE = REPOSITORY_ROOT / "analysis/eeg/statistics"
WINDOWS_CODE = REPOSITORY_ROOT / (
    "analysis/eeg/preprocessing/gold/windows"
)
sys.path.insert(0, str(FEATURE_CODE))
sys.path.insert(0, str(SIGNAL_CODE))
sys.path.insert(0, str(STATISTICS_CODE))
sys.path.insert(0, str(WINDOWS_CODE))

from build_ad_features import feature_row, response_row  # noqa: E402
from build_condition_features import (  # noqa: E402
    SUMMARY_FEATURES,
    complete_epoch_bounds,
    quality_features,
    spectral_features,
    summarize_window,
)
from clean_eeg import load_policy  # noqa: E402
from validate_ad_features import validate as validate_ad  # noqa: E402
from validate_condition_features import (  # noqa: E402
    validate as validate_condition,
)
from validate_engagement_features import (  # noqa: E402
    validate as validate_engagement,
)
from build_condition_contrasts import (  # noqa: E402
    FEATURE_TIERS,
    CONDITIONS as CONTRAST_CONDITIONS,
    contrast_tables,
)
from build_ad_windows import window_pair  # noqa: E402


SAMPLING_RATE = 500.0
DURATION_SECONDS = 4.0
CHANNELS = [
    "Fp1",
    "Fp2",
    "F3",
    "F4",
    "Fz",
    "FC1",
    "FC2",
    "C3",
    "C4",
    "Cz",
    "Pz",
    "P3",
    "P4",
    "O1",
    "Oz",
    "O2",
]
PRIMARY_FEATURE_ROOT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features"
)
ICA_FEATURE_ROOT = PRIMARY_FEATURE_ROOT / (
    "sensitivity/ica_candidate_v1"
)
PRIMARY_POLICY = SIGNAL_CODE / "cleaning_policy.json"
ICA_POLICY = SIGNAL_CODE / "cleaning_policy_ica_candidate_v1.json"
NO_ICA_POLICY = SIGNAL_CODE / "cleaning_policy_no_ica_sensitivity.json"
ICA_ROOT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/ica/candidate_v1"
)


def sine(frequency_hz: float, amplitude_uv: float) -> np.ndarray:
    times = np.arange(
        int(round(SAMPLING_RATE * DURATION_SECONDS)),
        dtype=float,
    ) / SAMPLING_RATE
    return amplitude_uv * 1e-6 * np.sin(
        2.0 * np.pi * frequency_hz * times
    )


def identical_channels(signal: np.ndarray) -> np.ndarray:
    return np.tile(signal, (len(CHANNELS), 1))


def mixed_signal(
    *,
    theta_uv: float,
    alpha_uv: float,
    beta_uv: float,
) -> np.ndarray:
    return (
        sine(6.0, theta_uv)
        + sine(10.0, alpha_uv)
        + sine(20.0, beta_uv)
    )


def ad_window(phase: str) -> dict[str, str]:
    return {
        "subject_id": "synthetic_subject",
        "experiment_id": "synthetic_experiment",
        "window_id": f"synthetic_reference__{phase}",
        "reference_id": "synthetic_reference",
        "reference_kind": "advertisement",
        "phase": phase,
        "condition": "inline_early",
        "ad_mode": "inline",
        "matched_timing": "early",
        "matched_ad_conditions": "inline_early",
        "reference_onset_eeg_offset_s": "10.0",
        "onset_estimator": "synthetic",
        "onset_status": "observed",
        "combined_timing_uncertainty_s": "0.0",
        "start_eeg_offset_s": "6.0" if phase == "pre" else "10.0",
        "end_eeg_offset_s": "10.0" if phase == "pre" else "14.0",
        "duration_s": "4.0",
        "source_log": "synthetic.jsonl",
        "source_xdf": "synthetic.xdf",
        "source_xdf_sha256": "synthetic_hash",
        "source_canonical_markers": "synthetic_markers.csv",
    }


def epoch_policy(threshold_uv: float = 1050.0) -> dict[str, object]:
    return {
        "status": "frozen_v3",
        "max_peak_to_peak_uv": threshold_uv,
        "reject_near_flat_channels": True,
        "minimum_retained_fraction": 0.8,
        "minimum_retained_epochs": 5,
        "window_aggregation": "median",
    }


class SpectralMetricTests(unittest.TestCase):
    def test_feature_inventory_is_stable(self) -> None:
        expected = {
            *(f"{band}_power_db_uv2" for band in (
                "delta",
                "theta",
                "alpha",
                "beta",
                "gamma",
            )),
            *(f"{band}_relative_power" for band in (
                "delta",
                "theta",
                "alpha",
                "beta",
                "gamma",
            )),
            "fz_theta_power_db_uv2",
            "posterior_alpha_power_db_uv2",
            "faa_log_f4_minus_f3",
            "engagement_beta_over_alpha_theta",
            "engagement_pope_frontocentral_beta_over_alpha_theta",
            "engagement_kislov_central_beta16_24_over_alpha8_12",
        }
        self.assertEqual(set(SUMMARY_FEATURES), expected)
        self.assertEqual(len(SUMMARY_FEATURES), 16)

    def test_known_alpha_sine_has_expected_power_and_dominance(self) -> None:
        amplitude_uv = 10.0
        data = identical_channels(sine(10.0, amplitude_uv))
        features = spectral_features(
            data,
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
        )
        expected_db_uv2 = 10.0 * math.log10(amplitude_uv**2 / 2.0)
        self.assertAlmostEqual(
            features["alpha_power_db_uv2"],
            expected_db_uv2,
            delta=0.15,
        )
        self.assertGreater(features["alpha_relative_power"], 0.99)
        self.assertAlmostEqual(
            features["posterior_alpha_power_db_uv2"],
            expected_db_uv2,
            delta=0.15,
        )
        self.assertAlmostEqual(
            features["faa_log_f4_minus_f3"],
            0.0,
            delta=1e-10,
        )

    def test_pope_and_kislov_ratios_match_known_sine_powers(self) -> None:
        data = identical_channels(
            mixed_signal(theta_uv=2.0, alpha_uv=2.0, beta_uv=4.0)
        )
        features = spectral_features(
            data,
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
        )
        # Sinusoidal power is amplitude squared / 2:
        # beta / (alpha + theta) = 8 / (2 + 2) = 2.
        self.assertAlmostEqual(
            features["engagement_beta_over_alpha_theta"],
            2.0,
            delta=0.03,
        )
        self.assertAlmostEqual(
            features[
                "engagement_pope_frontocentral_beta_over_alpha_theta"
            ],
            2.0,
            delta=0.03,
        )
        # Kislov beta/alpha = 8 / 2 = 4.
        self.assertAlmostEqual(
            features[
                "engagement_kislov_central_beta16_24_over_alpha8_12"
            ],
            4.0,
            delta=0.05,
        )

    def test_faa_is_log_f4_minus_f3_power(self) -> None:
        data = identical_channels(sine(10.0, 2.0))
        data[CHANNELS.index("F4")] = sine(10.0, 4.0)
        features = spectral_features(
            data,
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
        )
        # F4 has twice the amplitude and four times the alpha power.
        self.assertAlmostEqual(
            features["faa_log_f4_minus_f3"],
            math.log(4.0),
            delta=0.02,
        )
        self.assertGreater(features["faa_log_f4_minus_f3"], 0.0)

    def test_regional_features_use_expected_channels(self) -> None:
        data = identical_channels(mixed_signal(
            theta_uv=1.0,
            alpha_uv=1.0,
            beta_uv=1.0,
        ))
        data[CHANNELS.index("Fz")] += sine(6.0, 8.0)
        for channel in ("O1", "Oz", "O2", "P3", "Pz", "P4"):
            data[CHANNELS.index(channel)] += sine(10.0, 8.0)
        features = spectral_features(
            data,
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
        )
        self.assertGreater(
            features["fz_theta_power_db_uv2"],
            features["theta_power_db_uv2"],
        )
        self.assertGreater(
            features["posterior_alpha_power_db_uv2"],
            features["alpha_power_db_uv2"],
        )


class QualityAndPackagingTests(unittest.TestCase):
    def test_quality_metrics_detect_amplitude_and_flat_channel(self) -> None:
        active = sine(10.0, 10.0)
        data = np.vstack([active, np.zeros_like(active)])
        quality = quality_features(data, ["Fp1", "Fp2"])
        self.assertAlmostEqual(
            float(quality["max_abs_amplitude_uv"]),
            float(np.max(np.abs(active)) * 1e6),
            places=12,
        )
        self.assertAlmostEqual(
            float(quality["max_peak_to_peak_uv"]),
            float(np.ptp(active) * 1e6),
            places=12,
        )
        self.assertEqual(quality["max_peak_to_peak_channel"], "Fp1")
        self.assertEqual(int(quality["near_flat_channel_count"]), 1)

    def test_epoch_policy_rejects_only_gross_amplitude(self) -> None:
        clean = identical_channels(mixed_signal(
            theta_uv=2.0,
            alpha_uv=2.0,
            beta_uv=2.0,
        ))
        retained = feature_row(
            ad_window("pre"),
            data_v=clean,
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
            epoch_rejection=epoch_policy(),
            ica_applied=False,
        )
        self.assertEqual(retained["retained_by_policy"], "yes")
        self.assertEqual(retained["ica_applied"], "no")

        artifact = clean.copy()
        artifact[0] = sine(10.0, 600.0)
        rejected = feature_row(
            ad_window("post"),
            data_v=artifact,
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
            epoch_rejection=epoch_policy(),
            ica_applied=True,
        )
        self.assertEqual(rejected["retained_by_policy"], "no")
        self.assertIn(
            "gross_peak_to_peak",
            rejected["artifact_rejection_reason"],
        )
        self.assertEqual(rejected["ica_applied"], "yes")

    def test_ad_response_is_post_minus_pre_for_every_feature(self) -> None:
        pre = feature_row(
            ad_window("pre"),
            data_v=identical_channels(mixed_signal(
                theta_uv=2.0,
                alpha_uv=2.0,
                beta_uv=2.0,
            )),
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
            epoch_rejection=epoch_policy(),
            ica_applied=False,
        )
        post = feature_row(
            ad_window("post"),
            data_v=identical_channels(mixed_signal(
                theta_uv=3.0,
                alpha_uv=4.0,
                beta_uv=5.0,
            )),
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
            epoch_rejection=epoch_policy(),
            ica_applied=False,
        )
        response = response_row([post, pre])
        self.assertEqual(response["primary_analysis_eligible"], "yes")
        for feature in SUMMARY_FEATURES:
            self.assertAlmostEqual(
                float(response[f"{feature}_post_minus_pre"]),
                float(post[feature]) - float(pre[feature]),
                places=12,
                msg=feature,
            )


class PolicyContractTests(unittest.TestCase):
    def test_primary_and_ica_policies_are_separate_and_comparable(self) -> None:
        primary = load_policy(PRIMARY_POLICY)
        candidate = load_policy(ICA_POLICY)
        self.assertTrue(primary["ica"]["enabled"])
        self.assertTrue(candidate["ica"]["enabled"])
        self.assertEqual(
            primary["ica"]["model_policy_version"],
            "ica_candidate_v1",
        )
        self.assertEqual(
            primary["epoch_rejection"]["status"],
            "frozen_v3",
        )
        self.assertEqual(
            candidate["epoch_rejection"]["status"],
            "frozen_v3",
        )
        self.assertEqual(
            float(primary["epoch_rejection"]["max_peak_to_peak_uv"]),
            1050.0,
        )
        self.assertEqual(
            primary["epoch_rejection"]["max_peak_to_peak_uv"],
            candidate["epoch_rejection"]["max_peak_to_peak_uv"],
        )
        self.assertEqual(
            float(primary["ica"]["pca_explained_variance"]),
            0.99,
        )
        self.assertEqual(
            candidate["ica"]["ocular_proxy_channels"],
            ["Fp1", "Fp2"],
        )
        self.assertLessEqual(
            int(candidate["ica"]["maximum_excluded_components"]),
            3,
        )
        no_ica = load_policy(NO_ICA_POLICY)
        self.assertFalse(no_ica["ica"]["enabled"])
        self.assertEqual(
            no_ica["epoch_rejection"]["max_peak_to_peak_uv"],
            primary["epoch_rejection"]["max_peak_to_peak_uv"],
        )


class WindowAggregationTests(unittest.TestCase):
    def test_complete_epoch_bounds_scale_with_duration(self) -> None:
        two = list(
            complete_epoch_bounds(
                start_s=0.0,
                end_s=32.0,
                sfreq=500.0,
                epoch_seconds=2.0,
                raw_sample_count=16_000,
            )
        )
        thirty_two = list(
            complete_epoch_bounds(
                start_s=0.0,
                end_s=32.0,
                sfreq=500.0,
                epoch_seconds=32.0,
                raw_sample_count=16_000,
            )
        )
        self.assertEqual(len(two), 16)
        self.assertEqual(len(thirty_two), 1)
        self.assertEqual(two[0][2] - two[0][1], 1_000)
        self.assertEqual(thirty_two[0][2] - thirty_two[0][1], 16_000)

    def test_window_mean_is_arithmetic_mean_of_retained_epoch_db(self) -> None:
        values = [10.0, 12.0, 100.0]
        rows = []
        for index, value in enumerate(values):
            row = {
                "subject_id": "synthetic_subject",
                "experiment_id": "synthetic_experiment",
                "window_id": "synthetic_window",
                "window_type": "condition",
                "condition": "no_ads",
                "ad_mode": "",
                "trial_index": "0",
                "baseline_eye_state": "not_applicable",
                "epoch_duration_s": "4.0",
                "ica_applied": "yes",
                "max_peak_to_peak_uv": "100.0",
                "max_abs_amplitude_uv": "50.0",
                "near_flat_channel_count": "0",
                "retained_by_policy": "yes",
                "source_xdf": "synthetic.xdf",
                "source_xdf_sha256": "synthetic_hash",
            }
            for feature in SUMMARY_FEATURES:
                row[feature] = str(value)
            row["epoch_index"] = str(index)
            rows.append(row)
        summary = summarize_window(rows, epoch_policy())
        self.assertAlmostEqual(summary["fz_theta_power_db_uv2_median"], 12.0)
        self.assertAlmostEqual(summary["fz_theta_power_db_uv2_mean"], 40.666666666666664)
        self.assertGreater(
            summary["fz_theta_power_db_uv2_mean"],
            summary["fz_theta_power_db_uv2_median"],
        )

    def test_rejected_epochs_are_excluded_from_mean_and_median(self) -> None:
        rows = []
        for index, (value, retained) in enumerate(
            ((1.0, "yes"), (2.0, "yes"), (999.0, "no"))
        ):
            row = {
                "subject_id": "synthetic_subject",
                "experiment_id": "synthetic_experiment",
                "window_id": "synthetic_window",
                "window_type": "condition",
                "condition": "no_ads",
                "ad_mode": "",
                "trial_index": "0",
                "baseline_eye_state": "not_applicable",
                "epoch_duration_s": "4.0",
                "ica_applied": "yes",
                "max_peak_to_peak_uv": "100.0",
                "max_abs_amplitude_uv": "50.0",
                "near_flat_channel_count": "0",
                "retained_by_policy": retained,
                "source_xdf": "synthetic.xdf",
                "source_xdf_sha256": "synthetic_hash",
            }
            for feature in SUMMARY_FEATURES:
                row[feature] = str(value)
            row["epoch_index"] = str(index)
            rows.append(row)
        summary = summarize_window(rows, epoch_policy())
        self.assertEqual(summary["retained_epoch_count"], 2)
        self.assertAlmostEqual(summary["fz_theta_power_db_uv2_median"], 1.5)
        self.assertAlmostEqual(summary["fz_theta_power_db_uv2_mean"], 1.5)

    def test_complete_epoch_bounds_drop_an_incomplete_remainder(self) -> None:
        bounds = list(
            complete_epoch_bounds(
                start_s=0.0,
                end_s=33.0,
                sfreq=500.0,
                epoch_seconds=4.0,
                raw_sample_count=16_500,
            )
        )
        self.assertEqual(len(bounds), 8)
        self.assertEqual(bounds[-1][2], 16_000)
        self.assertEqual(bounds[-1][2] - bounds[-1][1], 2_000)

    def test_contrast_tables_honour_mean_suffix_independently_of_median(self) -> None:
        rows: list[dict[str, str]] = []
        for subject_id in ("synthetic_a", "synthetic_b"):
            for condition in CONTRAST_CONDITIONS:
                row = {
                    "subject_id": subject_id,
                    "condition": condition,
                }
                ad_mean = "10" if condition != "no_ads" else "0"
                for feature in FEATURE_TIERS:
                    row[f"{feature}_median"] = "0"
                    row[f"{feature}_mean"] = ad_mean
                rows.append(row)
        median_rows, _ = contrast_tables(
            rows,
            feature_suffix="_median",
            metric="condition_median",
        )
        mean_rows, _ = contrast_tables(
            rows,
            feature_suffix="_mean",
            metric="condition_mean",
        )

        def any_ad(table: list[dict[str, object]]) -> dict[str, object]:
            return next(
                row
                for row in table
                if row["feature"] == "fz_theta_power_db_uv2"
                and row["contrast_id"] == "any_ad_vs_no_ads"
            )

        median_any_ad = any_ad(median_rows)
        mean_any_ad = any_ad(mean_rows)
        self.assertEqual(median_any_ad["metric"], "condition_median")
        self.assertEqual(mean_any_ad["metric"], "condition_mean")
        self.assertAlmostEqual(float(median_any_ad["mean_difference"]), 0.0)
        self.assertAlmostEqual(float(mean_any_ad["mean_difference"]), 10.0)

    def test_contrast_tables_can_drop_incomplete_subjects(self) -> None:
        rows: list[dict[str, str]] = []
        for subject_id in ("complete_a", "complete_b", "missing_block_late"):
            for condition in CONTRAST_CONDITIONS:
                if subject_id == "missing_block_late" and condition == "block_late":
                    continue
                row = {
                    "subject_id": subject_id,
                    "condition": condition,
                }
                for feature in FEATURE_TIERS:
                    row[f"{feature}_median"] = "1"
                rows.append(row)
        with self.assertRaises(ValueError):
            contrast_tables(rows)
        kept, scores = contrast_tables(rows, drop_incomplete_subjects=True)
        subjects = {row["subject_id"] for row in scores}
        self.assertEqual(subjects, {"complete_a", "complete_b"})
        self.assertEqual(kept[0]["n_participants"], 2)

    def test_ad_window_pair_scales_pre_post_duration(self) -> None:
        condition = {
            "start_eeg_offset_s": "0.0",
            "end_eeg_offset_s": "120.0",
            "primary_analysis_eligible": "yes",
            "source_xdf": "synthetic.xdf",
            "source_xdf_sha256": "synthetic_hash",
        }
        rows = window_pair(
            subject_id="synthetic_subject",
            experiment_id="synthetic_experiment",
            reference_id="synthetic_ad",
            reference_kind="advertisement",
            condition="inline_early",
            ad_mode="inline",
            matched_timing="early",
            matched_ad_conditions="inline_early",
            onset_eeg_offset_s=40.0,
            onset_xdf_timestamp_lsl=40.0,
            onset_log_unix=40.0,
            onset_estimator="synthetic",
            onset_status="synthetic",
            combined_timing_uncertainty_s=0.0,
            condition_window=condition,
            source_log="synthetic.jsonl",
            source_canonical_markers="synthetic_markers.csv",
            window_seconds=16.0,
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["duration_s"], "16.000000")
        self.assertEqual(rows[1]["duration_s"], "16.000000")
        self.assertEqual(rows[0]["start_eeg_offset_s"], "24.000000")
        self.assertEqual(rows[1]["end_eeg_offset_s"], "56.000000")
        self.assertEqual(rows[0]["primary_analysis_eligible"], "yes")


@unittest.skipUnless(
    (PRIMARY_FEATURE_ROOT / "condition_epoch_features.csv").exists(),
    "Generated primary Gold features are not present locally",
)
class GeneratedDatasetIntegrationTests(unittest.TestCase):
    def test_primary_gold_datasets_pass_all_feature_validators(self) -> None:
        condition = validate_condition(
            PRIMARY_FEATURE_ROOT / "condition_epoch_features.csv",
            PRIMARY_FEATURE_ROOT / "condition_features.csv",
            expected_ica_applied=True,
        )
        ad = validate_ad(
            PRIMARY_FEATURE_ROOT.parent / "windows/ad_analysis_windows.csv",
            PRIMARY_FEATURE_ROOT / "ad_epoch_features.csv",
            PRIMARY_FEATURE_ROOT / "ad_response_features.csv",
            expected_ica_applied=True,
        )
        engagement = validate_engagement(
            PRIMARY_FEATURE_ROOT / "condition_epoch_features.csv",
            PRIMARY_FEATURE_ROOT / "ad_epoch_features.csv",
            PRIMARY_POLICY,
            "frozen_v3",
            1050.0,
        )
        self.assertEqual(condition["status"], "passed")
        self.assertEqual(condition["subject_count"], 18)
        self.assertTrue(condition["ica_applied"])
        self.assertEqual(ad["status"], "passed")
        self.assertEqual(ad["subject_count"], 18)
        self.assertTrue(ad["ica_applied"])
        self.assertEqual(engagement["validation_status"], "pass")
        self.assertTrue(all(engagement["checks"].values()))

    @unittest.skipUnless(
        (ICA_FEATURE_ROOT / "condition_epoch_features.csv").exists(),
        "Generated ICA Gold features are not present locally",
    )
    def test_ica_gold_datasets_pass_all_feature_validators(self) -> None:
        condition = validate_condition(
            ICA_FEATURE_ROOT / "condition_epoch_features.csv",
            ICA_FEATURE_ROOT / "condition_features.csv",
            expected_ica_applied=True,
        )
        ad = validate_ad(
            PRIMARY_FEATURE_ROOT.parent / "windows/ad_analysis_windows.csv",
            ICA_FEATURE_ROOT / "ad_epoch_features.csv",
            ICA_FEATURE_ROOT / "ad_response_features.csv",
            expected_ica_applied=True,
        )
        engagement = validate_engagement(
            ICA_FEATURE_ROOT / "condition_epoch_features.csv",
            ICA_FEATURE_ROOT / "ad_epoch_features.csv",
            ICA_POLICY,
            "frozen_v3",
            1050.0,
        )
        self.assertEqual(condition["status"], "passed")
        self.assertTrue(condition["ica_applied"])
        self.assertEqual(ad["status"], "passed")
        self.assertTrue(ad["ica_applied"])
        self.assertEqual(engagement["validation_status"], "pass")

    @unittest.skipUnless(
        (ICA_ROOT / "ica_cohort_summary.csv").exists(),
        "Generated ICA reports are not present locally",
    )
    def test_ica_models_reports_and_visual_evidence_are_complete(self) -> None:
        with (ICA_ROOT / "ica_cohort_summary.csv").open(
            newline="",
            encoding="utf-8",
        ) as handle:
            cohort = list(csv.DictReader(handle))
        self.assertEqual(len(cohort), 18)
        self.assertNotIn(
            "lab_subject_4",
            {row["subject_id"] for row in cohort},
        )
        for row in cohort:
            subject_id = row["subject_id"]
            report_path = ICA_ROOT / "reports" / f"{subject_id}.json"
            self.assertTrue(report_path.exists(), subject_id)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["policy_version"], "ica_candidate_v1")
            self.assertEqual(report["pca_explained_variance"], 0.99)
            self.assertLessEqual(report["excluded_component_count"], 3)
            self.assertEqual(
                report["excluded_component_count"],
                len(report["excluded_components"]),
            )
            self.assertTrue(
                REPOSITORY_ROOT.joinpath(report["model_path"]).exists(),
                subject_id,
            )
            for evidence_path in report["figures"].values():
                self.assertTrue(
                    REPOSITORY_ROOT.joinpath(evidence_path).exists(),
                    evidence_path,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
