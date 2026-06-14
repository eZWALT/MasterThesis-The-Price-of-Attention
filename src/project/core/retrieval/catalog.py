from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import faiss
import numpy as np

from core.config import DEFAULT_CATALOG_PRICE
from core.retrieval.adapters import build_adapter
from core.retrieval.adapters.base import DatasetAdapter
from core.retrieval.stages.state import CatalogItem
from core.log import logger


class AdCatalog:
    """
    FAST PATH ONLY:
    - loads prebuilt FAISS index
    - loads JSONL catalog once
    - no rebuilding, no embedding, no validation
    """

    def __init__(
        self,
        items: Dict[str, CatalogItem],
        index: faiss.Index,
        id_map: List[str],
    ) -> None:
        self._items = items
        self._index = index
        self._id_map = id_map

    # ─────────────────────────────────────────────
    # LOAD (FAST ONLY)
    # ─────────────────────────────────────────────

    @classmethod
    def load(
        cls,
        catalog_path: str,
        index_path: str,
    ) -> "AdCatalog":
        """
        Assumes BOTH files already exist:
        - catalog.jsonl
        - faiss.index
        Ensures catalog and index are consistent.
        """

        index_file = Path(index_path)
        catalog_file = Path(catalog_path)

        if not index_file.exists():
            raise FileNotFoundError(f"FAISS index not found: {index_path}")
        if not catalog_file.exists():
            raise FileNotFoundError(f"Catalog not found: {catalog_path}")

        logger.info("Loading FAISS index (FAST PATH)")
        index = faiss.read_index(str(index_file))

        logger.info("Loading catalog JSONL")
        items, id_map = cls._load_catalog(catalog_file)

        logger.info("Catalog loaded: {} items", len(items))
        logger.info("FAISS vectors: {}", index.ntotal)

        if len(id_map) != index.ntotal:
            raise RuntimeError(
                f"Catalog and FAISS index size mismatch: "
                f"catalog has {len(id_map)} items, index has {index.ntotal} vectors.\n"
                f"You must rebuild the FAISS index after updating the catalog."
            )

        return cls(items=items, index=index, id_map=id_map)

    # ─────────────────────────────────────────────
    # SEARCH API (UNCHANGED)
    # ─────────────────────────────────────────────

    def search(self, query_vec: np.ndarray, top_k: int) -> List[Tuple[str, float]]:
        k = min(top_k, len(self._id_map))
        distances, indices = self._index.search(query_vec, k)
        return [
            (self._id_map[i], float(distances[0][j]))
            for j, i in enumerate(indices[0]) if i != -1
        ]

    def get(self, item_id: str) -> CatalogItem:
        return self._items[item_id]

    def __len__(self) -> int:
        return len(self._items)

    # ─────────────────────────────────────────────
    # SIMPLE LOADER
    # ─────────────────────────────────────────────

    @staticmethod
    def _catalog_files(path: str | Path) -> List[Path]:
        catalog_path = Path(path)
        if catalog_path.is_dir():
            return sorted(catalog_path.glob("*.jsonl"))
        return [catalog_path]

    @staticmethod
    def _load_catalog(path: str | Path, adapter: DatasetAdapter | None = None):
        items: Dict[str, CatalogItem] = {}
        id_map: List[str] = []
        adapter = adapter or build_adapter()

        for catalog_file in AdCatalog._catalog_files(path):
            if not catalog_file.exists():
                raise FileNotFoundError(f"Catalog not found: {catalog_file}")

            for obj in adapter.iter_catalog(catalog_file):
                item_id = str(obj["item_id"])
                if item_id in items:
                    logger.warning("Skipping duplicate catalog item_id: {}", item_id)
                    continue

                metadata = dict(obj.get("metadata") or {})
                if obj.get("cta"):
                    metadata["cta"] = obj["cta"]
                if obj.get("question"):
                    metadata["question"] = obj["question"]

                price = _safe_float(obj.get("price", DEFAULT_CATALOG_PRICE))
                item = CatalogItem(
                    item_id=item_id,
                    title=obj.get("title", ""),
                    text=obj.get("text", ""),
                    category=obj.get("category", ""),
                    price=price,
                    metadata=metadata,
                )

                items[item.item_id] = item
                id_map.append(item.item_id)

        return items, id_map


def _safe_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        logger.warning("Invalid catalog price {!r}; using default {}", value, DEFAULT_CATALOG_PRICE)
        return DEFAULT_CATALOG_PRICE
