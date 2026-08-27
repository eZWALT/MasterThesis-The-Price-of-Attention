"""
Dataset adapters — abstract base.

A DatasetAdapter knows how to:
  1. Iterate over raw records from a file (or stream) on disk.
  2. Map each raw record to a CatalogItem, regardless of schema.

This lets the retrieval pipeline load Amazon, Yelp, custom JSONL,
or any future dataset without touching catalog.py.

To add a new dataset:
  - Create a subclass in a new file (e.g.  amazon.py).
  - Implement `item_id_field`, `title_field`, `text_field`, and
    optionally override `_parse_text` / `_parse_metadata`.
  - Register it in adapters/__init__.py.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generator, Iterator

from core.log import logger


class DatasetAdapter(ABC):
    """
    Abstract base class for catalog dataset adapters.

    Subclasses map a raw JSON/JSONL record to the normalised schema
    expected by AdCatalog.  Only `to_catalog_item` is mandatory; the
    JSONL iteration helper is provided for free.

    The normalised schema drives CatalogItem:
      item_id  : str  — unique identifier
      title    : str  — short display name
      text     : str  — full-text field used for embedding + BM25
      category : str  — optional product category
      price    : float — optional price (0.0 if absent)
      metadata : dict  — any remaining fields, forwarded as-is
    """

    # ── Subclass contract ────────────────────────────────────────────────

    @abstractmethod
    def to_catalog_item(self, raw: Dict[str, Any]) -> "CatalogItemDict":
        """
        Map a raw record dict to a normalised CatalogItemDict.

        Returns a plain dict with keys:
          item_id, title, text, category, price, cta, question, metadata
        All keys are optional except item_id, title, and text.
        """
        ...

    # ── Provided helpers ─────────────────────────────────────────────────

    def read_jsonl(self, path: str | Path) -> Iterator[Dict[str, Any]]:
        """Yield parsed JSON objects from a JSONL file, skipping blanks."""
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    yield json.loads(line)

    def iter_catalog(
        self, path: str | Path
    ) -> Generator["CatalogItemDict", None, None]:
        """Full pipeline: read JSONL → map → yield normalised dicts."""
        for raw in self.read_jsonl(path):
            try:
                yield self.to_catalog_item(raw)
            except Exception as exc:
                # Skip malformed records; log for transparency.
                logger.warning("{}: skipping record — {}", self.__class__.__name__, exc)


# ── Type alias (plain dict, not a dataclass, for loose coupling) ─────────

CatalogItemDict = Dict[str, Any]
"""
Keys expected downstream by AdCatalog._load_catalog:
  item_id  : str
  title    : str
  text     : str
  category : str        (optional, default "")
  price    : float      (optional, default 0.0)
  cta      : str        (optional, default "")
  question : str        (optional, default "")
  metadata : dict       (optional, default {})
"""
