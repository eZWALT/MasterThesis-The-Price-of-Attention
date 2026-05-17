"""
Ad Catalog — product corpus loader and FAISS index wrapper.

Responsibilities
----------------
1. Load the product catalog from disk (JSONL, one item per line).
2. Build or load a FAISS index of item embeddings.
3. Expose search(query_vec, top_k) → list[item_id].
4. Expose get(item_id) → CatalogItem.

This is the only place that touches FAISS directly.
All other retrieval code works with CatalogItem objects.

JSONL schema (one JSON object per line):
  {
    "item_id": "prod_001",
    "title":   "Ergonomic Standing Desk",
    "text":    "Adjustable sit-stand desk with memory presets...",
    "category": "furniture",
    "price":   349.99,
    "cta":     "Shop now",           // optional, forwarded to Ad
    "question": "Want desk advice?"  // optional, forwarded to Ad
  }
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import faiss
import numpy as np

from core.config import DEFAULT_CATALOG_PRICE, FAISS_INDEX_BATCH_SIZE, FAISS_INDEX_LOG_INTERVAL
from core.retrieval.stages.state import CatalogItem
from core.retrieval.adapters.base import DatasetAdapter
from core.log import logger


class AdCatalog:
    """
    Loads the product corpus and manages the FAISS index.

    Usage
    -----
    catalog = AdCatalog.load(
        catalog_path="data/catalog.jsonl",
        index_path="data/faiss.index",
        embedding_model=embed,        # EmbeddingModel instance
    )
    ids = catalog.search(query_vec, top_k=100)
    item = catalog.get(ids[0])
    """

    def __init__(
        self,
        items: Dict[str, CatalogItem],
        index: faiss.Index,
        id_map: List[str],
    ) -> None:
        self._items = items        # item_id → CatalogItem
        self._index = index        # FAISS index
        self._id_map = id_map      # position → item_id  (aligns with FAISS vectors)

    # ── factory ─────────────────────────────────────────────────────────

    @classmethod
    def load(
        cls,
        catalog_path: str,
        index_path: str,
        embedding_model,                    # EmbeddingModel — avoids circular import
        adapter: Optional[DatasetAdapter] = None,
        force_rebuild: bool = False,
    ) -> "AdCatalog":
        """
        Load catalog from JSONL and build or restore the FAISS index.

        Parameters
        ----------
        catalog_path    : path to JSONL file.
        index_path      : path to FAISS index file (loaded or built).
        embedding_model : EmbeddingModel instance.
        adapter         : DatasetAdapter that maps raw records to the
                          normalised schema.  Defaults to GenericAdapter.
        force_rebuild   : ignore an existing index and rebuild from scratch.

        If index_path exists and force_rebuild=False, the index is loaded
        from disk (fast startup).  Otherwise, all items are re-embedded
        and a new index is built and saved.
        """
        if adapter is None:
            from core.retrieval.adapters import build_adapter
            adapter = build_adapter()   # reads CATALOG_ADAPTER from config
        items, id_map = cls._load_catalog(catalog_path, adapter)

        index_file = Path(index_path)
        index = None
        if index_file.exists() and not force_rebuild:
            index = faiss.read_index(str(index_file))
            # Sanity checks — rebuild if the index is stale or from a different model.
            expected_dim = embedding_model.encode(["test"]).shape[1]
            if index.d != expected_dim:
                logger.warning(
                    "FAISS index dim {} ≠ embedding dim {} — rebuilding.",
                    index.d, expected_dim,
                )
                index = None
            elif index.ntotal != len(id_map):
                logger.warning(
                    "FAISS index has {} vectors but catalog has {} items — rebuilding.",
                    index.ntotal, len(id_map),
                )
                index = None

        if index is None:
            index = cls._build_index(items, id_map, embedding_model, index_file)

        return cls(items=items, index=index, id_map=id_map)

    # ── public API ──────────────────────────────────────────────────────

    def search(self, query_vec: np.ndarray, top_k: int) -> List[str]:
        """
        ANN search over the FAISS index.

        Parameters
        ----------
        query_vec : np.ndarray shape (1, D), L2-normalised float32.
        top_k     : number of nearest neighbours to return.

        Returns
        -------
        List of item_id strings, ordered by similarity (highest first).
        """
        k = min(top_k, len(self._id_map))
        _, indices = self._index.search(query_vec, k)
        return [self._id_map[i] for i in indices[0] if i != -1]

    def get(self, item_id: str) -> CatalogItem:
        """Return the CatalogItem for a given item_id."""
        return self._items[item_id]

    def __len__(self) -> int:
        return len(self._items)

    # ── private helpers ─────────────────────────────────────────────────

    @staticmethod
    def _load_catalog(path: str, adapter: DatasetAdapter):
        """
        Iterate over `path` via the adapter and build the item dict + id_map.

        The adapter handles schema differences (Amazon, generic, custom);
        this method is schema-agnostic.
        """
        items: Dict[str, CatalogItem] = {}
        id_map: List[str] = []
        for norm in adapter.iter_catalog(path):
            item = CatalogItem(
                item_id=norm["item_id"],
                title=norm["title"],
                text=norm["text"],
                category=norm.get("category", ""),
                price=float(norm.get("price", DEFAULT_CATALOG_PRICE)),
                metadata=norm.get("metadata", {}),
            )
            items[item.item_id] = item
            id_map.append(item.item_id)
        logger.info("Catalog loaded: {} items from {}", len(items), path)
        return items, id_map

    @staticmethod
    def _build_index(
        items: Dict[str, CatalogItem],
        id_map: List[str],
        embedding_model,
        save_path: Path,
        batch_size: int = FAISS_INDEX_BATCH_SIZE,
    ) -> faiss.Index:
        """Encode items in batches and add to FAISS incrementally.

        Encoding the full corpus in one shot allocates a single (N, D) float32
        array, which can OOM for large catalogs.  Batching keeps peak memory
        bounded to ``batch_size * D * 4`` bytes for the vector slice, at the
        cost of slightly more Python loop overhead.
        """
        if not id_map:
            raise ValueError("id_map is empty — nothing to index.")

        index: faiss.Index | None = None
        total = len(id_map)
        log_interval = batch_size * FAISS_INDEX_LOG_INTERVAL

        for start in range(0, total, batch_size):
            batch_ids = id_map[start : start + batch_size]
            texts = [items[iid].text for iid in batch_ids]
            vectors = embedding_model.encode(texts)   # (B, D)

            if index is None:
                dim = vectors.shape[1]
                index = faiss.IndexFlatIP(dim)  # cosine via inner product on normalised vecs

            index.add(vectors)

            indexed_count = min(start + batch_size, total)
            if indexed_count % log_interval < batch_size or indexed_count == total:
                logger.info("  indexed {}/{} items", indexed_count, total)

        save_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(save_path))
        return index
