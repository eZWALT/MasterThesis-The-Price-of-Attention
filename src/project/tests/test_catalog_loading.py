"""
Unit tests for AdCatalog loading — single file, multi-source, dedup, metadata.
"""

from __future__ import annotations

import json

import pytest

from core.retrieval.catalog import AdCatalog, _safe_float
from core.retrieval.adapters.generic import GenericAdapter


@pytest.mark.unit
class TestSafeFloat:
    def test_parses_numeric_strings(self):
        assert _safe_float("12.5") == 12.5

    def test_invalid_price_returns_default(self):
        from core.config import DEFAULT_CATALOG_PRICE
        assert _safe_float("not-a-number") == DEFAULT_CATALOG_PRICE


@pytest.mark.unit
class TestCatalogFilesDiscovery:
    def test_file_path_returns_single_file(self, tmp_path):
        f = tmp_path / "one.jsonl"
        f.write_text('{"item_id":"x","title":"X","text":"t"}\n')
        files = AdCatalog._catalog_files(f)
        assert files == [f]

    def test_directory_returns_all_jsonl_sorted(self, tmp_path):
        d = tmp_path / "catalogs"
        d.mkdir()
        (d / "b.jsonl").write_text('{"item_id":"b","title":"B","text":"b"}\n')
        (d / "a.jsonl").write_text('{"item_id":"a","title":"A","text":"a"}\n')
        files = AdCatalog._catalog_files(d)
        assert [p.name for p in files] == ["a.jsonl", "b.jsonl"]


@pytest.mark.unit
class TestLoadCatalog:
    @pytest.fixture
    def catalog_dir(self, tmp_path):
        d = tmp_path / "catalogs"
        d.mkdir()
        items_a = [
            {"item_id": "a1", "title": "Item A1", "text": "Description A1", "category": "electronics"},
            {"item_id": "a2", "title": "Item A2", "text": "Description A2"},
        ]
        with open(d / "source_a.jsonl", "w") as f:
            for item in items_a:
                f.write(json.dumps(item) + "\n")
        items_b = [
            {"item_id": "b1", "title": "Item B1", "text": "Description B1",
             "metadata": {"source": "synthetic"}},
        ]
        with open(d / "source_b.jsonl", "w") as f:
            for item in items_b:
                f.write(json.dumps(item) + "\n")
        return d

    def test_loads_all_sources_from_directory(self, catalog_dir):
        items, id_map = AdCatalog._load_catalog(catalog_dir, GenericAdapter())
        assert len(items) == 3
        assert set(id_map) == {"a1", "a2", "b1"}

    def test_deduplicates_by_item_id(self, catalog_dir):
        with open(catalog_dir / "source_b.jsonl", "a") as f:
            f.write(json.dumps({"item_id": "a1", "title": "DUPE", "text": "dupe"}) + "\n")
        items, _ = AdCatalog._load_catalog(catalog_dir, GenericAdapter())
        assert len(items) == 3
        assert items["a1"].title == "Item A1"

    def test_preserves_metadata_and_promotional_fields(self, catalog_dir, tmp_path):
        single = tmp_path / "promo.jsonl"
        with open(single, "w") as f:
            f.write(json.dumps({
                "item_id": "p1",
                "title": "Product",
                "text": "Body",
                "cta": "Shop now",
                "question": "Want this?",
                "metadata": {"brand": "Acme"},
            }) + "\n")
        items, _ = AdCatalog._load_catalog(single, GenericAdapter())
        assert items["p1"].metadata["cta"] == "Shop now"
        assert items["p1"].metadata["question"] == "Want this?"
        assert items["p1"].metadata["brand"] == "Acme"

    def test_empty_directory_returns_empty_catalog(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        items, id_map = AdCatalog._load_catalog(empty, GenericAdapter())
        assert items == {}
        assert id_map == []
