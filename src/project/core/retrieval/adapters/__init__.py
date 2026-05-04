"""
core.retrieval.adapters — dataset adapter factory.

Usage
-----
    from core.retrieval.adapters import build_adapter

    adapter = build_adapter("amazon")       # Amazon Reviews 2023
    adapter = build_adapter("generic")      # default normalized JSONL
    adapter = build_adapter()               # reads CATALOG_ADAPTER from config

To add a new source:
  1. Create a subclass of DatasetAdapter in a new file.
  2. Add it to _REGISTRY below.
  3. Point CATALOG_ADAPTER in core.config (or env var) at the new key.
"""

from __future__ import annotations

import os

from core.retrieval.adapters.base import DatasetAdapter
from core.retrieval.adapters.generic import GenericAdapter
from core.retrieval.adapters.amazon import AmazonAdapter

_REGISTRY: dict[str, type[DatasetAdapter]] = {
    "generic": GenericAdapter,
    "amazon":  AmazonAdapter,
}


def build_adapter(name: str | None = None, **kwargs) -> DatasetAdapter:
    """
    Instantiate and return a DatasetAdapter by name.

    Parameters
    ----------
    name   : adapter key (e.g. "amazon", "generic").
             Falls back to the CATALOG_ADAPTER env var, then "generic".
    kwargs : forwarded to the adapter constructor (e.g.
             max_features=15 for AmazonAdapter).
    """
    if name is None:
        from core.config import CATALOG_ADAPTER
        name = CATALOG_ADAPTER

    cls = _REGISTRY.get(name)
    if cls is None:
        raise ValueError(
            f"Unknown catalog adapter '{name}'. "
            f"Available: {list(_REGISTRY)}"
        )
    return cls(**kwargs)


__all__ = ["DatasetAdapter", "GenericAdapter", "AmazonAdapter", "build_adapter"]
