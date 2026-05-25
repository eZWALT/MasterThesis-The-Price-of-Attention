from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import faiss
import numpy as np
import json

from core.config import DEFAULT_CATALOG_PRICE
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

    def search(self, query_vec: np.ndarray, top_k: int) -> List[str]:
        k = min(top_k, len(self._id_map))
        _, indices = self._index.search(query_vec, k)
        return [self._id_map[i] for i in indices[0] if i != -1]

    def get(self, item_id: str) -> CatalogItem:
        return self._items[item_id]

    def __len__(self) -> int:
        return len(self._items)

    # ─────────────────────────────────────────────
    # SIMPLE LOADER
    # ─────────────────────────────────────────────

    @staticmethod
    def _load_catalog(path: Path):
        items: Dict[str, CatalogItem] = {}
        id_map: List[str] = []

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                obj = json.loads(line)

                item = CatalogItem(
                    item_id=obj["item_id"],
                    title=obj.get("title", ""),
                    text=obj.get("text", ""),
                    category=obj.get("category", ""),
                    price=float(obj.get("price", DEFAULT_CATALOG_PRICE)),
                    metadata=obj.get("metadata", {}),
                )

                items[item.item_id] = item
                id_map.append(item.item_id)

        return items, id_map