"""Unit tests for trackable ad product links."""

from __future__ import annotations

import pytest

from core.ad_injection.ad_links import (
    _AD_CLICK_TRACKER_JS,
    ad_product_url,
    clean_inline_assistant_display,
    detect_mentioned_ad,
    enrich_display_payload,
    html_product_link,
    linkify_inline_ad_titles,
    log_ad_clicked,
)
from core.ad_injection.models import Ad, compact_display_payload
from core.logger import ExperimentLogger


@pytest.mark.unit
class TestAdLinks:
    def test_ad_product_url(self):
        ad = Ad(title="Boots", text="", source_item_id="item-42")
        assert ad_product_url(ad).endswith("/item-42")

    def test_enrich_display_payload(self):
        ad = Ad(title="Boots", text="", source_item_id="x1", cta="Shop")
        payload = enrich_display_payload(ad, compact_display_payload(ad))
        assert payload["source_item_id"] == "x1"
        assert payload["click_url"].endswith("/x1")

    def test_html_product_link_opens_new_tab(self):
        ad = Ad(title="Boots", text="", source_item_id="shoe-1")
        result = html_product_link(ad, label="Boots")
        assert 'target="_blank"' in result
        assert "/shoe-1" in result
        assert "Boots" in result

    def test_linkify_wraps_bold_title(self):
        ad = Ad(title="Marathon Running Shoes", text="", source_item_id="shoe-1")
        result = linkify_inline_ad_titles(
            "Try these **Marathon Running Shoes** for your race.",
            [ad],
        )
        assert "Marathon Running Shoes" in result
        assert 'target="_blank"' in result
        assert "/shoe-1" in result

    def test_linkify_wraps_plain_title(self):
        ad = Ad(title="Marathon Running Shoes", text="", source_item_id="shoe-1")
        result = linkify_inline_ad_titles(
            "Try these Marathon Running Shoes for your race.",
            [ad],
        )
        assert 'target="_blank"' in result
        assert "/shoe-1" in result

    def test_linkify_fallback_appends_link(self):
        ad = Ad(title="Secret Product", text="", source_item_id="sp-1")
        result = linkify_inline_ad_titles(
            "Here is some text with no matching product name.",
            [ad],
        )
        assert "See" in result
        assert "/sp-1" in result

    def test_log_ad_clicked_writes_jsonl(self, tmp_path):
        ad = Ad(title="Boots", text="", source_item_id="item-42")
        lg = ExperimentLogger(log_dir=str(tmp_path), flush_every_n=1)
        log_ad_clicked(
            lg,
            ad=ad,
            ad_mode="explicit_ad_block",
            conversation_id="conv-1",
            turn=3,
            interaction="banner_title",
        )
        lg.flush_sync()
        lg.stop()
        lines = lg.log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        assert '"event": "ad_clicked"' in lines[0]
        assert '"ad_item_id": "item-42"' in lines[0]

    def test_clean_inline_keeps_product_prose(self):
        raw = (
            "Sleep tips here.\n\n"
            "***\n\n"
            "Product Mention:\n"
            "Within You Hydration Electrolytes – hydration note."
        )
        cleaned = clean_inline_assistant_display(raw)
        assert "Sleep tips here." in cleaned
        assert "Within You Hydration Electrolytes" in cleaned
        assert "Product Mention" not in cleaned
        assert "***" not in cleaned

    def test_detect_mentioned_ad(self):
        ads = [
            Ad(title="Within You Hydration Electrolytes", text="", source_item_id="hyd-1"),
            Ad(title="Other Product", text="", source_item_id="other"),
        ]
        content = "Try Within You Hydration for daytime hydration."
        assert detect_mentioned_ad(content, ads).source_item_id == "hyd-1"

    def test_tracker_js_contains_url_pattern(self):
        assert "ads.study.local/product" in _AD_CLICK_TRACKER_JS
        assert "__ad_click_tracker" in _AD_CLICK_TRACKER_JS
        assert "fetch(" in _AD_CLICK_TRACKER_JS
        assert "/ad_click" in _AD_CLICK_TRACKER_JS
