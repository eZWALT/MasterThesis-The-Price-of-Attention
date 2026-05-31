"""
Unit tests for ad injection — multi-product LLM prompt and injectors.
"""

from __future__ import annotations

import pytest

from core.ad_injection.models import (
    Ad,
    AdRetrievalResult,
    compact_display_payload,
    format_products_block,
    participant_display_title,
    sponsored_message_to_payload,
)
from core.ad_injection.injectors import (
    InlinePersuasiveInjector,
    SponsoredConversationalInjector,
    ExplicitAdBlockInjector,
)
from core.config import INLINE_AD_SYSTEM_PROMPT, SPONSORED_LABEL


def _sample_ads(n: int = 3) -> AdRetrievalResult:
    ads = [
        Ad(title=f"Product {i}", text=f"Description for product {i}", source_item_id=f"id-{i}")
        for i in range(1, n + 1)
    ]
    return AdRetrievalResult(ads=ads)


@pytest.mark.unit
class TestFormatProductsBlock:
    def test_formats_numbered_products(self):
        block = format_products_block(_sample_ads(2).ads)
        assert "1. **Product 1**" in block
        assert "2. **Product 2**" in block
        assert "Description" not in block

    def test_includes_cta_when_present(self):
        ads = [Ad(title="Gadget", text="long body", cta="Shop Now")]
        block = format_products_block(ads)
        assert "Shop Now" in block
        assert "long body" not in block

    def test_empty_list_returns_empty_string(self):
        assert format_products_block([]) == ""


@pytest.mark.unit
class TestInlinePersuasiveInjector:
    def test_builds_products_block_without_keyerror(self):
        injector = InlinePersuasiveInjector()
        result = injector.inject(_sample_ads(3), [])
        assert result.system_overrides
        content = result.system_overrides[0]["content"]
        assert "Product 1" in content
        assert "Product 3" in content
        assert "EXACTLY ONE product" in content
        assert "Product Mention" in content

    def test_empty_retrieval_yields_empty_block(self):
        injector = InlinePersuasiveInjector()
        result = injector.inject(AdRetrievalResult(), [])
        assert "Candidate products:" in result.system_overrides[0]["content"]


@pytest.mark.unit
class TestOtherInjectorsUsePrimaryOnly:
    def test_sponsored_conversational_uses_top_ad(self):
        injector = SponsoredConversationalInjector()
        result = injector.inject(_sample_ads(3), [])
        assert len(result.suggestions) == 1
        assert "Product 1" in result.suggestions[0]

    def test_explicit_block_uses_top_ad(self):
        from core.config import EXPLICIT_AD_LABEL

        injector = ExplicitAdBlockInjector()
        result = injector.inject(_sample_ads(3), [])
        assert result.display_payload["title"] == "Product 1"
        assert result.display_payload["header"] == EXPLICIT_AD_LABEL
        assert "text" not in result.display_payload

    def test_sponsored_conversational_includes_display_payload(self):
        injector = SponsoredConversationalInjector()
        result = injector.inject(_sample_ads(1), [])
        assert result.display_payload["title"] == "Product 1"
        assert "text" not in result.display_payload

    def test_sponsored_conversational_chip_never_empty(self):
        injector = SponsoredConversationalInjector()
        ad = Ad(title="Rod", text="body", question="   ", source_item_id="x")
        result = injector.inject(AdRetrievalResult(ads=[ad]), [])
        assert len(result.suggestions) == 1
        assert result.suggestions[0].strip()
        assert "Rod" in result.suggestions[0]

    def test_empty_retrieval_returns_empty_result(self):
        injector = ExplicitAdBlockInjector()
        assert injector.inject(AdRetrievalResult(), []).display_payload is None


@pytest.mark.unit
class TestAdFormatterTopN:
    def test_formats_up_to_top_n(self):
        from core.retrieval.stages.formatter import AdFormatter
        from core.retrieval.stages.state import PipelineState, CatalogItem, RankedCandidate

        formatter = AdFormatter()
        state = PipelineState(query="test")
        state.ranked = [
            RankedCandidate(
                item=CatalogItem(item_id=str(i), title=f"T{i}", text=f"Body {i}"),
                score=1.0 - i * 0.1,
            )
            for i in range(5)
        ]
        out = formatter.run(state)
        assert len(out.top_ads) == 3
        assert out.top_ad.title == "T0"
        assert [a.title for a in out.top_ads] == ["T0", "T1", "T2"]


@pytest.mark.unit
class TestRetrievalResultContract:
    def test_pipeline_returns_retrieval_result_with_last_state(self):
        from core.ad_injection.models import AdRetrievalResult
        from core.retrieval.pipeline import AdRetrievalPipeline
        from core.retrieval.stages.formatter import AdFormatter
        from core.retrieval.stages.state import CatalogItem, PipelineState, RankedCandidate

        class FakeRankStage:
            def run(self, state: PipelineState) -> PipelineState:
                state.ranked = [
                    RankedCandidate(
                        item=CatalogItem(item_id=str(i), title=f"T{i}", text=f"Body {i}"),
                        score=float(i),
                    )
                    for i in range(4)
                ]
                return state

        pipeline = AdRetrievalPipeline(catalog=None, stages=[FakeRankStage(), AdFormatter()])
        result = pipeline.run("query", [])

        assert isinstance(result, AdRetrievalResult)
        assert result.primary.title == "T0"
        assert len(result.ads) == 3
        assert pipeline.last_state is not None
        assert len(pipeline.last_state.top_ads) == 3

    def test_provider_falls_back_to_mock_when_rag_returns_none(self):
        from unittest.mock import patch

        from core.ad_injection.provider import get_ad

        with patch("core.retrieval.retrieve_ad", return_value=None):
            result = get_ad("query", [], backend="rag")

        assert result.has_ads
        assert result.primary.source_item_id == "mock"


@pytest.mark.unit
class TestAdRetrievalResult:
    def test_primary_is_first_ad(self):
        r = _sample_ads(2)
        assert r.primary.title == "Product 1"
        assert r.has_ads

    def test_primary_none_when_empty(self):
        r = AdRetrievalResult()
        assert r.primary is None
        assert not r.has_ads


@pytest.mark.unit
class TestCompactAdDisplayHelpers:
    def test_compact_display_payload_omits_body(self):
        ad = Ad(title="X", text="noisy body", cta="Go")
        payload = compact_display_payload(ad)
        assert payload["title"] == "X"
        assert payload["cta"] == "Go"
        assert "text" not in payload

    def test_participant_display_title_truncates(self):
        long_title = "A" * 200
        ad = Ad(title=long_title, text="ignored")
        assert len(participant_display_title(ad)) <= 120
        assert participant_display_title(ad).endswith("…")

    def test_sponsored_message_to_payload_strips_legacy_body(self):
        legacy = (
            "**Sponsored** — Widget\n\n"
            + ("catalog description " * 400)
            + "\n\n*Buy*"
        )
        payload = sponsored_message_to_payload(legacy)
        assert payload is not None
        assert payload["title"] == "Widget"
        assert payload["cta"] == "Buy"
        assert "catalog description" not in str(payload.values())


@pytest.mark.unit
class TestInjectorRegistry:
    def test_all_ad_modes_have_injectors(self):
        from core.ad_injection.provider import INJECTOR_REGISTRY
        from core.config import AD_MODES

        assert set(INJECTOR_REGISTRY) == set(AD_MODES)

    def test_inline_prompt_template_accepts_products_block(self):
        block = format_products_block(_sample_ads(1).ads)
        rendered = INLINE_AD_SYSTEM_PROMPT.format(products_block=block)
        assert "Product 1" in rendered
        assert "{products_block}" not in rendered


@pytest.mark.unit
class TestGetAdProvider:
    def test_mock_backend_returns_mock_ad(self):
        from core.ad_injection.provider import get_ad

        result = get_ad("query", [], backend="mock")
        assert result.primary.source_item_id == "mock"

    def test_rag_backend_delegates_to_retrieve_ad(self):
        from unittest.mock import patch

        from core.ad_injection.provider import get_ad

        fake = AdRetrievalResult(ads=[Ad(title="RAG", text="t", source_item_id="r1")])
        with patch("core.retrieval.retrieve_ad", return_value=fake) as mock_retrieve:
            result = get_ad("q", [], backend="rag")
        mock_retrieve.assert_called_once()
        assert result.primary.title == "RAG"
