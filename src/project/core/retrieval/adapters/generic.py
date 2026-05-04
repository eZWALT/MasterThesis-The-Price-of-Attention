"""
Generic JSONL adapter — default for custom / hand-built catalogs.

Expected schema (one JSON object per line):
  {
    "item_id":  "prod_001",           // required
    "title":    "Ergonomic Desk",     // required
    "text":     "...",                // required
    "category": "furniture",          // optional
    "price":    349.99,               // optional
    "cta":      "Shop now",           // optional
    "question": "Want desk advice?"   // optional
  }

Any extra fields are forwarded as-is in metadata.
"""

from __future__ import annotations

from typing import Any, Dict

from core.retrieval.adapters.base import DatasetAdapter, CatalogItemDict

# Fields consumed by the normalised schema; everything else → metadata.
_KNOWN_FIELDS = {"item_id", "title", "text", "category", "price", "cta", "question"}


class GenericAdapter(DatasetAdapter):
    """
    Pass-through adapter for catalogs that already follow the
    normalised JSONL schema used by AdCatalog.

    This is the default adapter; no configuration needed.
    """

    def to_catalog_item(self, raw: Dict[str, Any]) -> CatalogItemDict:
        metadata = {k: v for k, v in raw.items() if k not in _KNOWN_FIELDS}
        return {
            "item_id":  str(raw["item_id"]),
            "title":    str(raw["title"]),
            "text":     str(raw["text"]),
            "category": str(raw.get("category", "")),
            "price":    float(raw.get("price", 0.0)),
            "cta":      str(raw.get("cta", "")),
            "question": str(raw.get("question", "")),
            "metadata": metadata,
        }
