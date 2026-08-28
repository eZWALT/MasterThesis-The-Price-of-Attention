"""Unit tests for channel-set policies. No Gold rebuild."""

from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


FEATURE_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = FEATURE_DIR.parents[5]
sys.path.insert(0, str(FEATURE_DIR))

from build_condition_features import (  # noqa: E402
    BANDS,
    quality_features,
    spectral_features,
)
from channel_sets import (  # noqa: E402
    ANGELA_CODE_AS_WRITTEN,
    ANGELA_CODE_BAND_CHANNELS,
    ANGELA_CODE_DROPPED,
    ANGELA_CODE_PATH,
    ANGELA_CODE_VERSION,
    DEFAULT_CHANNEL_SET_PATH,
    GEORGE2025_NINE,
    LITERATURE_ROI_BAND_CHANNELS,
    LITERATURE_ROI_PATH,
    LITERATURE_ROI_VERSION,
    LOCKED_FZ_THETA,
    LOCKED_POSTERIOR_ALPHA,
    PRIMARY_BAND_CHANNELS,
    PRIMARY_VERSION,
    TEACHING_ATLAS_BAND_CHANNELS,
    TEACHING_ATLAS_PATH,
    TEACHING_ATLAS_VERSION,
    WANG2022_BAND_CHANNELS,
    WANG2022_PATH,
    WANG2022_VERSION,
    assert_output_allowed,
    default_channel_set,
    load_channel_set_policy,
    policy_from_mapping,
    require_ready,
    reroute_if_default,
    suggested_sensitivity_dir,
)


SAMPLING_RATE = 500.0
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
    "F7",
    "F8",
    "F9",
    "F10",
    "T7",
    "T8",
    "P7",
    "P8",
    "CP1",
    "CP2",
]


def sine(frequency_hz: float, amplitude_uv: float) -> np.ndarray:
    times = np.arange(int(round(SAMPLING_RATE * 4.0)), dtype=float) / SAMPLING_RATE
    return amplitude_uv * 1e-6 * np.sin(2.0 * np.pi * frequency_hz * times)


def identical_channels(signal: np.ndarray) -> np.ndarray:
    return np.tile(signal, (len(CHANNELS), 1))


def filled_mapping() -> dict:
    payload = json.loads(DEFAULT_CHANNEL_SET_PATH.read_text(encoding="utf-8"))
    payload["policy_version"] = "test_roi_v0"
    payload["status"] = "ready"
    payload["role"] = "sensitivity_only"
    payload["bands"]["alpha"]["channels"] = ["O1"]
    return payload


class ChannelSetPolicyTests(unittest.TestCase):
    def test_current_policy_is_primary_and_matches_band_edges(self) -> None:
        policy = default_channel_set()
        self.assertEqual(policy.policy_version, PRIMARY_VERSION)
        self.assertTrue(policy.is_primary)
        self.assertTrue(policy.is_ready)
        self.assertEqual(policy.cleaning_scope, "full_montage")
        for name, (low_hz, high_hz) in BANDS.items():
            self.assertEqual(policy.bands[name].low_hz, low_hz)
            self.assertEqual(policy.bands[name].high_hz, high_hz)
            self.assertEqual(policy.bands[name].channels, PRIMARY_BAND_CHANNELS[name])

    def test_literature_roi_is_ready_and_regional(self) -> None:
        policy = load_channel_set_policy(LITERATURE_ROI_PATH)
        self.assertEqual(policy.status, "ready")
        self.assertEqual(policy.policy_version, LITERATURE_ROI_VERSION)
        self.assertFalse(policy.is_primary)
        require_ready(policy)
        self.assertEqual(GEORGE2025_NINE, ("F3", "Fz", "F4", "C3", "Cz", "C4", "O1", "Oz", "O2"))
        for name, channels in LITERATURE_ROI_BAND_CHANNELS.items():
            self.assertEqual(channels, GEORGE2025_NINE)
            self.assertEqual(policy.bands[name].channels, GEORGE2025_NINE)
        self.assertEqual(policy.fz_theta_channels, LOCKED_FZ_THETA)
        self.assertEqual(
            policy.posterior_alpha_channels,
            LOCKED_POSTERIOR_ALPHA,
        )
        features = spectral_features(
            identical_channels(sine(10.0, 10.0)),
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
            channel_set=policy,
        )
        self.assertIn("alpha_power_db_uv2", features)

    def test_literature_lock_rejects_drift(self) -> None:
        payload = json.loads(LITERATURE_ROI_PATH.read_text(encoding="utf-8"))
        payload["bands"]["delta"]["channels"] = ["Fp1", "Fp2"]
        with self.assertRaises(ValueError):
            policy_from_mapping(payload, path=LITERATURE_ROI_PATH)

    def test_wang_policy_is_ready_and_locked(self) -> None:
        policy = load_channel_set_policy(WANG2022_PATH)
        self.assertEqual(policy.status, "ready")
        self.assertEqual(policy.policy_version, WANG2022_VERSION)
        self.assertFalse(policy.is_primary)
        require_ready(policy)
        self.assertEqual(policy.bands["delta"].channels, WANG2022_BAND_CHANNELS["delta"])
        self.assertEqual(policy.bands["theta"].channels, ("C3", "P3", "T7", "P7"))
        self.assertEqual(policy.bands["alpha"].channels, ("O1", "Oz", "O2"))
        self.assertEqual(
            policy.bands["beta"].channels,
            WANG2022_BAND_CHANNELS["beta"],
        )
        self.assertEqual(
            policy.bands["gamma"].channels,
            WANG2022_BAND_CHANNELS["gamma"],
        )
        self.assertEqual(policy.fz_theta_channels, LOCKED_FZ_THETA)
        self.assertEqual(
            policy.posterior_alpha_channels,
            LOCKED_POSTERIOR_ALPHA,
        )
        features = spectral_features(
            identical_channels(sine(10.0, 10.0)),
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
            channel_set=policy,
        )
        self.assertIn("alpha_power_db_uv2", features)

    def test_wang_lock_rejects_drift(self) -> None:
        payload = json.loads(WANG2022_PATH.read_text(encoding="utf-8"))
        payload["bands"]["theta"]["channels"] = ["T7", "T8"]
        with self.assertRaises(ValueError):
            policy_from_mapping(payload, path=WANG2022_PATH)

    def test_teaching_atlas_is_ready_and_locked(self) -> None:
        policy = load_channel_set_policy(TEACHING_ATLAS_PATH)
        self.assertEqual(policy.status, "ready")
        self.assertEqual(policy.policy_version, TEACHING_ATLAS_VERSION)
        self.assertFalse(policy.is_primary)
        require_ready(policy)
        for name, channels in TEACHING_ATLAS_BAND_CHANNELS.items():
            self.assertEqual(policy.bands[name].channels, channels)
        self.assertEqual(policy.fz_theta_channels, LOCKED_FZ_THETA)
        self.assertEqual(
            policy.posterior_alpha_channels,
            LOCKED_POSTERIOR_ALPHA,
        )

    def test_teaching_atlas_lock_rejects_drift(self) -> None:
        payload = json.loads(TEACHING_ATLAS_PATH.read_text(encoding="utf-8"))
        payload["bands"]["alpha"]["channels"] = ["O1"]
        with self.assertRaises(ValueError):
            policy_from_mapping(payload, path=TEACHING_ATLAS_PATH)

    def test_angela_code_is_ready_and_drops_missing_sites(self) -> None:
        policy = load_channel_set_policy(ANGELA_CODE_PATH)
        self.assertEqual(policy.status, "ready")
        self.assertEqual(policy.policy_version, ANGELA_CODE_VERSION)
        self.assertFalse(policy.is_primary)
        require_ready(policy)
        self.assertEqual(
            ANGELA_CODE_DROPPED,
            ("FCz", "CP3", "CPz", "CP4", "PO7", "PO8"),
        )
        self.assertEqual(
            set(ANGELA_CODE_AS_WRITTEN["theta"]),
            {"Fz", "FCz", "Cz", "F3", "F4"},
        )
        self.assertEqual(
            set(ANGELA_CODE_BAND_CHANNELS["theta"]),
            set(ANGELA_CODE_AS_WRITTEN["theta"]) - set(ANGELA_CODE_DROPPED),
        )
        self.assertEqual(
            set(ANGELA_CODE_BAND_CHANNELS["beta"]),
            set(ANGELA_CODE_AS_WRITTEN["beta"]) - set(ANGELA_CODE_DROPPED),
        )
        self.assertEqual(
            set(ANGELA_CODE_BAND_CHANNELS["gamma"]),
            set(ANGELA_CODE_AS_WRITTEN["gamma"]) - set(ANGELA_CODE_DROPPED),
        )
        self.assertEqual(
            ANGELA_CODE_BAND_CHANNELS["delta"],
            ("Fz", "F3", "F4", "Cz"),
        )
        self.assertEqual(
            ANGELA_CODE_BAND_CHANNELS["theta"],
            ("Fz", "F3", "F4", "Cz"),
        )
        self.assertEqual(
            ANGELA_CODE_BAND_CHANNELS["beta"],
            ("C3", "Cz", "C4"),
        )
        self.assertEqual(
            ANGELA_CODE_BAND_CHANNELS["gamma"],
            ("O1", "Oz", "O2", "P7", "P8"),
        )
        for name, channels in ANGELA_CODE_BAND_CHANNELS.items():
            self.assertEqual(policy.bands[name].channels, channels)
            self.assertTrue(set(ANGELA_CODE_DROPPED).isdisjoint(channels))
        self.assertEqual(policy.fz_theta_channels, LOCKED_FZ_THETA)
        self.assertEqual(
            policy.posterior_alpha_channels,
            LOCKED_POSTERIOR_ALPHA,
        )
        self.assertEqual(
            policy.bands["alpha"].channels,
            LOCKED_POSTERIOR_ALPHA,
        )
        features = spectral_features(
            identical_channels(sine(10.0, 10.0)),
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
            channel_set=policy,
        )
        self.assertIn("alpha_power_db_uv2", features)

    def test_angela_code_lock_rejects_drift(self) -> None:
        payload = json.loads(ANGELA_CODE_PATH.read_text(encoding="utf-8"))
        payload["bands"]["theta"]["channels"] = ["Fz", "FCz", "Cz", "F3", "F4"]
        with self.assertRaises(ValueError):
            policy_from_mapping(payload, path=ANGELA_CODE_PATH)

    def test_default_spectral_call_matches_explicit_current_policy(self) -> None:
        data = identical_channels(sine(10.0, 10.0))
        implicit = spectral_features(
            data,
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
        )
        explicit = spectral_features(
            data,
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
            channel_set=default_channel_set(),
        )
        self.assertEqual(implicit.keys(), explicit.keys())
        for key in implicit:
            self.assertTrue(math.isclose(implicit[key], explicit[key], rel_tol=0, abs_tol=1e-12))

    def test_subset_policy_changes_global_alpha_only(self) -> None:
        data = identical_channels(sine(10.0, 2.0))
        data[CHANNELS.index("O1")] = sine(10.0, 8.0)
        current = spectral_features(
            data,
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
        )
        subset = spectral_features(
            data,
            sfreq=SAMPLING_RATE,
            channel_names=CHANNELS,
            channel_set=policy_from_mapping(
                filled_mapping(),
                path=Path("test_roi_v0.json"),
            ),
        )
        self.assertGreater(
            subset["alpha_power_db_uv2"],
            current["alpha_power_db_uv2"],
        )
        self.assertAlmostEqual(
            subset["posterior_alpha_power_db_uv2"],
            current["posterior_alpha_power_db_uv2"],
            delta=1e-12,
        )

    def test_non_primary_cannot_write_primary_gold(self) -> None:
        policy = load_channel_set_policy(LITERATURE_ROI_PATH)
        gold = (
            REPOSITORY_ROOT
            / "src/project/logs/xdf/gold/features/condition_features.csv"
        )
        stats = (
            REPOSITORY_ROOT
            / "analysis/eeg/statistics/outputs/eeg_condition_contrasts.csv"
        )
        with self.assertRaises(ValueError):
            assert_output_allowed(policy, gold)
        with self.assertRaises(ValueError):
            assert_output_allowed(policy, stats)
        with tempfile.TemporaryDirectory() as raw:
            outside = Path(raw) / "condition_features.csv"
            with self.assertRaises(ValueError):
                assert_output_allowed(policy, outside)
            allowed = Path(raw) / "sensitivity" / "channel_sets" / "x.csv"
            allowed.parent.mkdir(parents=True)
            assert_output_allowed(policy, allowed)

    def test_non_primary_defaults_reroute_to_sensitivity(self) -> None:
        policy = policy_from_mapping(
            filled_mapping(),
            path=Path("test_roi_v0.json"),
        )
        primary = (
            REPOSITORY_ROOT
            / "src/project/logs/xdf/gold/features/condition_features.csv"
        )
        replacement = (
            REPOSITORY_ROOT
            / suggested_sensitivity_dir(policy)
            / "condition_features.csv"
        )
        self.assertEqual(
            reroute_if_default(policy, primary, primary, replacement),
            replacement,
        )
        self.assertEqual(
            reroute_if_default(
                default_channel_set(),
                primary,
                primary,
                replacement,
            ),
            primary,
        )

    def test_used_rejection_ignores_unused_channel(self) -> None:
        data = identical_channels(sine(10.0, 2.0))
        data[CHANNELS.index("Fp1")] = np.linspace(
            -1.0e-3,
            1.0e-3,
            data.shape[1],
        )
        whole_cap = quality_features(data, CHANNELS)
        posterior = quality_features(
            data,
            CHANNELS,
            rejection_channels=("O1", "Oz", "O2"),
        )
        self.assertGreater(float(whole_cap["max_peak_to_peak_uv"]), 1000.0)
        self.assertLess(float(posterior["max_peak_to_peak_uv"]), 20.0)


if __name__ == "__main__":
    unittest.main()
