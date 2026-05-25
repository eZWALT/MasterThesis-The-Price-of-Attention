"""
Unit tests for URL query param parsing — dev=flow, force_ad, rag, modes.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.experiment.query_params import ExperimentParams, parse_query_params


class _FakeQueryParams(dict):
    """Minimal stand-in for streamlit.query_params."""

    def get(self, key, default=""):
        return super().get(key, default)


@pytest.mark.unit
class TestParseQueryParams:
    def _parse(self, params: dict):
        with patch("streamlit.query_params", _FakeQueryParams(params)):
            return parse_query_params()

    def test_dev_flow_sets_flow_test(self):
        p = self._parse({"dev": "flow"})
        assert p.flow_test is True
        assert p.dev_mode is False

    def test_force_ad_zero_in_flow_mode(self):
        p = self._parse({"dev": "flow", "force_ad": "0"})
        assert p.force_ad is False

    def test_force_ad_one_in_flow_mode(self):
        p = self._parse({"dev": "flow", "force_ad": "1"})
        assert p.force_ad is True

    def test_rag_zero_forces_mock_backend_flag(self):
        p = self._parse({"dev": "flow", "rag": "0"})
        assert p.use_rag is False

    def test_rag_one_forces_rag_backend_flag(self):
        p = self._parse({"dev": "flow", "rag": "1"})
        assert p.use_rag is True

    def test_force_ad_ignored_outside_dev_mode(self):
        p = self._parse({"force_ad": "0"})
        assert p.force_ad is True  # default unchanged

    def test_modes_filter_valid_ad_modes(self):
        p = self._parse({
            "dev": "flow",
            "n": "2",
            "modes": "explicit_ad_block,invalid_mode,sponsored_conversational",
        })
        assert p.ad_modes == ["explicit_ad_block", "sponsored_conversational"]

    def test_skip_screens_parsed(self):
        p = self._parse({"skip": "consent,baseline,ocean"})
        assert "consent" in p.skip_screens
        assert "baseline" in p.skip_screens

    def test_study_crowd_applies_defaults(self):
        p = self._parse({"study": "crowd"})
        assert p.study_type == "crowd"
        assert "baseline" in p.skip_screens or p.skip_screens  # crowd may skip baseline


@pytest.mark.unit
class TestExperimentParamsDefaults:
    def test_apply_study_defaults_does_not_override_explicit(self):
        params = ExperimentParams(n_trials=7)
        params.apply_study_defaults(explicitly_set={"n_trials"})
        assert params.n_trials == 7
