"""
Unit tests for parallel execution architecture:
- CPU thread pool existence and configuration
- Modality hook registration and execution
- EEG/eye-tracking hooks (graceful degradation)
- Multi-source catalog loading
"""

from __future__ import annotations

import json
import time
import threading
from unittest.mock import MagicMock

import pytest


# ── CPU Thread Pool ────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCPUPool:
    def test_pool_exists(self):
        from core.conversation.manager import _CPU_POOL
        assert _CPU_POOL is not None

    def test_pool_has_4_workers(self):
        from core.conversation.manager import _CPU_POOL
        assert _CPU_POOL._max_workers == 4

    def test_pool_thread_prefix(self):
        from core.conversation.manager import _CPU_POOL
        assert _CPU_POOL._thread_name_prefix == "turn-cpu"

    def test_pool_submit_and_result(self):
        """Pool can execute callables and return results."""
        from core.conversation.manager import _CPU_POOL
        future = _CPU_POOL.submit(lambda x: x * 2, 21)
        assert future.result(timeout=5.0) == 42

    def test_pool_parallel_execution(self):
        """Multiple tasks run in parallel (not serialized)."""
        from core.conversation.manager import _CPU_POOL
        results = []
        barrier = threading.Barrier(3, timeout=5.0)

        def work(i):
            barrier.wait()  # all three must be running concurrently
            results.append(i)
            return i

        futures = [_CPU_POOL.submit(work, i) for i in range(3)]
        for f in futures:
            f.result(timeout=5.0)
        assert len(results) == 3


# ── Modality Hook Registration ────────────────────────────────────────────────


@pytest.mark.unit
class TestModalityHooks:
    def test_register_hook(self):
        """Hooks can be registered on ConversationManager."""
        from core.conversation.manager import ConversationManager

        mgr = ConversationManager(
            ad_mode="inline_persuasive",
            model="test",
            temperature=0.7,
            max_tokens=100,
            use_rag=False,
        )
        hook = MagicMock()
        mgr.register_modality_hook(hook)
        assert hook in mgr._modality_hooks

    def test_multiple_hooks(self):
        from core.conversation.manager import ConversationManager

        mgr = ConversationManager(
            ad_mode="inline_persuasive",
            model="test",
            temperature=0.7,
            max_tokens=100,
            use_rag=False,
        )
        hooks = [MagicMock() for _ in range(3)]
        for h in hooks:
            mgr.register_modality_hook(h)
        assert len(mgr._modality_hooks) == 3


# ── EEG Hook ──────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEEGHook:
    def test_lsl_sender_returns_object_with_send(self):
        from core.modalities.eeg import lsl_sender
        sender = lsl_sender(); assert hasattr(sender, "send") and callable(sender.send)

    def test_lsl_sender_send_no_crash(self):
        """Hook runs gracefully when pylsl is not installed."""
        from core.modalities.eeg import lsl_sender
        sender = lsl_sender(); sender.send("baseline_start")
        sender.send("turn_1_write")

    def test_marker_no_crash(self):
        """marker() is a no-op when LSL is unavailable."""
        from core.modalities.eeg import marker
        # Should not raise
        marker("test_marker")


# ── Eye-Tracking Hook ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEyeTrackingHook:
    def test_eye_tracking_hook_callable(self):
        from core.modalities.eye_tracking import eye_tracking_turn_hook
        assert callable(eye_tracking_turn_hook)

    def test_eye_tracking_hook_no_crash_without_tobii(self):
        """Hook runs gracefully without Tobii hardware."""
        from core.modalities.eye_tracking import eye_tracking_turn_hook
        eye_tracking_turn_hook(turn=1, ad_injected=False, ad=None)
        eye_tracking_turn_hook(turn=2, ad_injected=True, ad=MagicMock(title="Test Ad"))

    def test_init_eye_tracking_returns_false_without_hardware(self):
        from core.modalities.eye_tracking import init_eye_tracking
        # No tobii hardware in CI — should return False gracefully
        result = init_eye_tracking()
        assert result is False

    def test_gaze_snapshot_returns_none(self):
        from core.modalities.eye_tracking import get_gaze_snapshot
        assert get_gaze_snapshot() is None


# ── Multi-Source Catalog ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestMultiSourceCatalog:
    @pytest.fixture
    def catalog_dir(self, tmp_path):
        """Create a temporary catalog directory with 2 JSONL sources."""
        d = tmp_path / "catalogs"
        d.mkdir()

        # Source A: 3 items
        items_a = [
            {"item_id": "a1", "title": "Item A1", "text": "Description A1", "category": "electronics"},
            {"item_id": "a2", "title": "Item A2", "text": "Description A2", "category": "electronics"},
            {"item_id": "a3", "title": "Item A3", "text": "Description A3", "category": "books"},
        ]
        with open(d / "source_a.jsonl", "w") as f:
            for item in items_a:
                f.write(json.dumps(item) + "\n")

        # Source B: 2 items
        items_b = [
            {"item_id": "b1", "title": "Item B1", "text": "Description B1", "metadata": {"source": "synthetic"}},
            {"item_id": "b2", "title": "Item B2", "text": "Description B2", "metadata": {"source": "synthetic"}},
        ]
        with open(d / "source_b.jsonl", "w") as f:
            for item in items_b:
                f.write(json.dumps(item) + "\n")

        return d

    def test_loads_all_sources(self, catalog_dir):
        """_load_catalog loads items from all JSONL files in directory."""
        from core.retrieval.catalog import AdCatalog
        from core.retrieval.adapters.generic import GenericAdapter

        adapter = GenericAdapter()
        items, id_map = AdCatalog._load_catalog(catalog_dir, adapter)

        assert len(items) == 5
        assert len(id_map) == 5
        assert "a1" in items
        assert "b2" in items

    def test_deduplicates_by_id(self, catalog_dir):
        """Duplicate item_ids across sources are skipped."""
        from core.retrieval.catalog import AdCatalog
        from core.retrieval.adapters.generic import GenericAdapter

        # Add a duplicate to source_b
        with open(catalog_dir / "source_b.jsonl", "a") as f:
            f.write(json.dumps({"item_id": "a1", "title": "DUPE", "text": "dupe"}) + "\n")

        adapter = GenericAdapter()
        items, id_map = AdCatalog._load_catalog(catalog_dir, adapter)

        # Still 5 (a1 from source_a wins, duplicate from source_b skipped)
        assert len(items) == 5
        assert items["a1"].title == "Item A1"  # original, not "DUPE"

    def test_preserves_metadata(self, catalog_dir):
        """Metadata dict from JSONL is preserved on CatalogItem."""
        from core.retrieval.catalog import AdCatalog
        from core.retrieval.adapters.generic import GenericAdapter

        adapter = GenericAdapter()
        items, _ = AdCatalog._load_catalog(catalog_dir, adapter)

        assert items["b1"].metadata == {"source": "synthetic"}
        assert items["a1"].metadata == {}  # no metadata field → empty dict

    def test_promotional_fields_are_available_to_formatter(self, tmp_path):
        """Top-level cta/question fields are preserved in metadata for AdFormatter."""
        from core.retrieval.catalog import AdCatalog
        from core.retrieval.adapters.generic import GenericAdapter

        catalog_file = tmp_path / "ads.jsonl"
        with open(catalog_file, "w") as f:
            f.write(json.dumps({
                "item_id": "p1",
                "title": "Product",
                "text": "Description",
                "cta": "Shop now",
                "question": "Need this product?",
            }) + "\n")

        items, _ = AdCatalog._load_catalog(catalog_file, GenericAdapter())

        assert items["p1"].metadata["cta"] == "Shop now"
        assert items["p1"].metadata["question"] == "Need this product?"

    def test_invalid_price_falls_back_to_zero(self, tmp_path):
        """Malformed price values do not drop otherwise valid catalog rows."""
        from core.retrieval.catalog import AdCatalog
        from core.retrieval.adapters.generic import GenericAdapter

        catalog_file = tmp_path / "ads.jsonl"
        with open(catalog_file, "w") as f:
            f.write(json.dumps({
                "item_id": "p1",
                "title": "Product",
                "text": "Description",
                "price": "not-a-number",
            }) + "\n")

        items, _ = AdCatalog._load_catalog(catalog_file, GenericAdapter())

        assert items["p1"].price == 0.0

    def test_fallback_single_file(self, tmp_path):
        """Loads a single JSONL file when a file path is passed."""
        from core.retrieval.catalog import AdCatalog
        from core.retrieval.adapters.generic import GenericAdapter

        single_file = tmp_path / "test.jsonl"
        with open(single_file, "w") as f:
            f.write(json.dumps({"item_id": "x1", "title": "X", "text": "x"}) + "\n")

        adapter = GenericAdapter()
        items, id_map = AdCatalog._load_catalog(single_file, adapter)

        assert len(items) == 1
        assert "x1" in items

    def test_empty_dir_returns_no_items(self, tmp_path):
        """Empty catalog directories are explicit and do not silently load another file."""
        from core.retrieval.catalog import AdCatalog
        from core.retrieval.adapters.generic import GenericAdapter

        empty_dir = tmp_path / "empty_catalogs"
        empty_dir.mkdir()

        adapter = GenericAdapter()
        items, id_map = AdCatalog._load_catalog(empty_dir, adapter)

        assert items == {}
        assert id_map == []
