"""
Amazon Product Catalog adapter.

Supports the Amazon Reviews 2023 dataset (and older 2018/2014 formats).
Reference: https://amazon-reviews-2023.github.io/

Item metadata JSONL schema (relevant fields):
  parent_asin      — canonical product ID (preferred over 'asin')
  asin             — fallback ID if parent_asin absent
  title            — product title
  description      — list[str] or str  (may be empty list)
  features         — list[str] bullet points
  main_category    — top-level category string
  categories       — list[str] breadcrumb path (first element is used)
  price            — float or "$N.NN" string (may be absent / null)
  store            — brand / seller name
  details          — dict with freeform extra info
  images           — list of {hi_res, large, ...} dicts
  average_rating   — float
  rating_number    — int

The adapter builds a rich `text` field for embedding by concatenating:
  title + bullet features + description (in that priority order).
This gives the embedding model the most signal-dense representation.

Usage:
  from core.retrieval.adapters.amazon import AmazonAdapter
  adapter = AmazonAdapter()
  for item in adapter.iter_catalog("data/amazon_electronics.jsonl"):
      print(item["item_id"], item["title"])
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Union

from core.config import AD_QUESTION_TEMPLATE
from core.retrieval.adapters.base import DatasetAdapter, CatalogItemDict

# Fields consumed directly; everything else → metadata.
_KNOWN_FIELDS = {
    "parent_asin", "asin", "title", "description", "features",
    "main_category", "categories", "price", "store",
    "details", "images", "average_rating", "rating_number",
}


class AmazonAdapter(DatasetAdapter):
    """
    Maps Amazon Product Catalog JSONL records to the normalised schema.

    Parameters
    ----------
    include_reviews : bool
        If True, also appends review highlights from a `reviews_summary`
        field if present (non-standard extension you can pre-process into
        your JSONL).  Default False.
    max_features : int
        Max number of bullet-point features to include in `text`.
        Keeps embedding input from growing unboundedly. Default 10.
    """

    def __init__(
        self,
        include_reviews: bool = False,
        max_features: int = 10,
    ) -> None:
        self._include_reviews = include_reviews
        self._max_features = max_features

    # ── DatasetAdapter interface ─────────────────────────────────────────

    def to_catalog_item(self, raw: Dict[str, Any]) -> CatalogItemDict:
        item_id  = str(raw.get("parent_asin") or raw.get("asin") or "")
        if not item_id:
            raise ValueError("Record has neither 'parent_asin' nor 'asin'.")

        title    = self._str(raw.get("title", ""))
        text     = self._build_text(raw)
        category = self._parse_category(raw)
        price    = self._parse_price(raw.get("price"))
        store    = self._str(raw.get("store", ""))

        metadata = {
            k: v for k, v in raw.items() if k not in _KNOWN_FIELDS
        }
        if store:
            metadata["store"] = store
        if raw.get("average_rating") is not None:
            metadata["average_rating"] = raw["average_rating"]
        if raw.get("rating_number") is not None:
            metadata["rating_number"] = raw["rating_number"]
        if raw.get("details"):
            metadata["details"] = raw["details"]

        return {
            "item_id":  item_id,
            "title":    title,
            "text":     text,
            "category": category,
            "price":    price,
            "cta":      "Shop now",
            "question": AD_QUESTION_TEMPLATE.format(title=title),
            "metadata": metadata,
        }

    # ── private helpers ──────────────────────────────────────────────────

    def _build_text(self, raw: Dict[str, Any]) -> str:
        """
        Compose a dense, embedding-friendly text field.

        Priority: title → features → description → reviews_summary.
        """
        parts: List[str] = []

        title = self._str(raw.get("title", ""))
        if title:
            parts.append(title)

        features = self._listify(raw.get("features", []))
        for feat in features[: self._max_features]:
            feat = feat.strip()
            if feat:
                parts.append(feat)

        description = self._listify(raw.get("description", []))
        for desc in description:
            desc = desc.strip()
            if desc:
                parts.append(desc)

        if self._include_reviews:
            reviews = self._str(raw.get("reviews_summary", ""))
            if reviews:
                parts.append(reviews)

        return " ".join(parts).strip()

    @staticmethod
    def _parse_category(raw: Dict[str, Any]) -> str:
        """Return the best single-string category label."""
        main = raw.get("main_category")
        if main and isinstance(main, str) and main.strip():
            return main.strip()
        cats = raw.get("categories", [])
        if cats and isinstance(cats, list):
            # Breadcrumb path — use the most specific non-empty leaf.
            for cat in reversed(cats):
                if isinstance(cat, str) and cat.strip():
                    return cat.strip()
        return ""

    @staticmethod
    def _parse_price(raw_price: Any) -> float:
        """Parse price from float, int, or string like '$12.99'."""
        if raw_price is None:
            return 0.0
        if isinstance(raw_price, (int, float)):
            return float(raw_price)
        if isinstance(raw_price, str):
            cleaned = re.sub(r"[^\d.]", "", raw_price)
            try:
                return float(cleaned)
            except ValueError:
                return 0.0
        return 0.0

    @staticmethod
    def _str(v: Any) -> str:
        """Coerce to string, return '' for None / empty list."""
        if v is None:
            return ""
        if isinstance(v, list):
            return " ".join(str(i) for i in v if i).strip()
        return str(v).strip()

    @staticmethod
    def _listify(v: Union[List, str, None]) -> List[str]:
        """Ensure the value is always a list of strings."""
        if v is None:
            return []
        if isinstance(v, str):
            return [v] if v.strip() else []
        return [str(i) for i in v if i]
