#!/usr/bin/env python3
"""
prepare_amazon_catalog.py
─────────────────────────
Utility to pull Amazon Reviews 2023 *item metadata* from Hugging Face,
convert it to the project's catalog.jsonl schema, optionally precompute
embeddings, and optionally push the processed dataset back to HF Hub.

The dataset is loaded with the official `datasets` library, which handles
caching, streaming, and authentication transparently.

HF config names for item metadata follow the pattern:
    raw_meta_{CATEGORY}   e.g.  raw_meta_All_Beauty

See scripts/README.md for full usage examples.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# ── project root on sys.path ──────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_PROJECT = _HERE.parent
sys.path.insert(0, str(_PROJECT))

from core.log import logger  # noqa: E402

# ── dataset config names ──────────────────────────────────────────────────────

DATASET_REPO = "McAuley-Lab/Amazon-Reviews-2023"

CATEGORIES: List[str] = [
    "All_Beauty",
    "Amazon_Fashion",
    "Appliances",
    "Arts_Crafts_and_Sewing",
    "Automotive",
    "Baby_Products",
    "Beauty_and_Personal_Care",
    "Books",
    "CDs_and_Vinyl",
    "Cell_Phones_and_Accessories",
    "Clothing_Shoes_and_Jewelry",
    "Digital_Music",
    "Electronics",
    "Gift_Cards",
    "Grocery_and_Gourmet_Food",
    "Handmade_Products",
    "Health_and_Household",
    "Health_and_Personal_Care",
    "Home_and_Kitchen",
    "Industrial_and_Scientific",
    "Kindle_Store",
    "Magazine_Subscriptions",
    "Movies_and_TV",
    "Musical_Instruments",
    "Office_Products",
    "Patio_Lawn_and_Garden",
    "Pet_Supplies",
    "Software",
    "Sports_and_Outdoors",
    "Subscription_Boxes",
    "Tools_and_Home_Improvement",
    "Toys_and_Games",
    "Video_Games",
    "Unknown",
]

# ── helpers ───────────────────────────────────────────────────────────────────


def _hf_config(category: str) -> str:
    """Return the HF dataset config name for item metadata of a category."""
    return f"raw_meta_{category}"


def _load_hf_category(category: str, streaming: bool = False):
    """
    Load item metadata for *category* using the HF datasets library.

    streaming=True avoids downloading the full split before iterating;
    useful for very large categories (Books, Electronics …).
    """
    from datasets import load_dataset

    config = _hf_config(category)
    logger.info(f"Loading {DATASET_REPO}  config={config}  streaming={streaming}")
    ds = load_dataset(
        DATASET_REPO,
        config,
        split="full",
        trust_remote_code=True,
        streaming=streaming,
    )
    return ds


# ── processing ────────────────────────────────────────────────────────────────


def process_categories(
    categories: List[str],
    out_path: Path,
    max_items: Optional[int],
    append: bool,
    streaming: bool,
) -> List[dict]:
    """
    Download + convert all requested categories and write catalog.jsonl.

    Returns the list of converted item dicts (needed for embedding step).
    """
    from core.retrieval.adapters import build_adapter

    adapter = build_adapter("amazon")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"

    seen_ids: set = set()
    if append and out_path.exists():
        with open(out_path) as f:
            for line in f:
                try:
                    seen_ids.add(json.loads(line)["item_id"])
                except Exception:
                    pass
        logger.info(f"  {len(seen_ids):,} existing ids loaded for deduplication")

    all_items: List[dict] = []

    with open(out_path, mode, encoding="utf-8") as fh:
        for cat in categories:
            if cat not in CATEGORIES:
                logger.warning(
                    f"'{cat}' is not in the known category list — attempting anyway"
                )

            dataset = _load_hf_category(cat, streaming=streaming)
            written = skipped = 0

            for raw in dataset:
                if max_items is not None and written >= max_items:
                    break
                try:
                    item = adapter.to_catalog_item(dict(raw))
                except (ValueError, KeyError) as exc:
                    logger.debug(f"Skipping record: {exc}")
                    skipped += 1
                    continue

                iid = item.get("item_id", "")
                if not iid or iid in seen_ids:
                    skipped += 1
                    continue

                if not item.get("category"):
                    item["category"] = cat

                fh.write(json.dumps(item, ensure_ascii=False) + "\n")
                seen_ids.add(iid)
                all_items.append(item)
                written += 1

            logger.info(f"  {cat}: wrote {written:,}  skipped {skipped:,}")

    total = sum(1 for _ in open(out_path)) if out_path.exists() else 0
    logger.info(f"Catalog → {out_path}  ({total:,} total lines)")
    return all_items


# ── embedding precomputation ───────────────────────────────────────────────────


def precompute_embeddings(items: List[dict], out_dir: Path) -> None:
    """
    Embed every item's `text` field and save:
        embeddings.npy   — float32 array  (N, dim)
        item_ids.json    — list of item_id strings aligned with rows
    """
    import numpy as np

    from core.config import EMBEDDING_MODEL_NAME, EMBEDDING_DEVICE, EMBEDDING_BATCH_SIZE
    from core.retrieval.embeddings import build_embedding_model

    logger.info(f"Precomputing embeddings  model={EMBEDDING_MODEL_NAME}  device={EMBEDDING_DEVICE}")
    model = build_embedding_model(model_name=EMBEDDING_MODEL_NAME, device=EMBEDDING_DEVICE)

    texts = [it["text"] for it in items]
    ids   = [it["item_id"] for it in items]

    # Batch encode
    import math
    batch_size = EMBEDDING_BATCH_SIZE
    all_vecs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        vecs = model.encode(batch)          # returns np.ndarray (B, dim)
        all_vecs.append(vecs)
        done = min(i + batch_size, len(texts))
        print(f"\r  embedded {done:,} / {len(texts):,}", end="", flush=True)
    print()

    matrix = np.vstack(all_vecs).astype("float32")

    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / "embeddings.npy", matrix)
    (out_dir / "item_ids.json").write_text(json.dumps(ids))
    logger.info(f"Saved embeddings {matrix.shape} → {out_dir}")


# ── FAISS index build ─────────────────────────────────────────────────────────


def build_faiss_index(catalog_path: str, index_path: str) -> None:
    """Build (or rebuild) the FAISS index from catalog.jsonl."""
    from core.config import EMBEDDING_MODEL_NAME, EMBEDDING_DEVICE
    from core.retrieval.catalog import AdCatalog
    from core.retrieval.embeddings import build_embedding_model

    logger.info(f"Building FAISS index  model={EMBEDDING_MODEL_NAME}  device={EMBEDDING_DEVICE}")
    embed = build_embedding_model(model_name=EMBEDDING_MODEL_NAME, device=EMBEDDING_DEVICE)
    AdCatalog.load(
        catalog_path=catalog_path,
        index_path=index_path,
        embedding_model=embed,
        force_rebuild=True,
    )
    logger.info(f"FAISS index → {index_path}")


# ── HF Hub upload ─────────────────────────────────────────────────────────────


def push_to_hub(
    catalog_path: str,
    repo_id: str,
    embeddings_dir: Optional[str] = None,
    private: bool = True,
) -> None:
    """
    Push the processed catalog (and optionally precomputed embeddings)
    to a HuggingFace Hub dataset repository.

    Requires HF_TOKEN env var or `huggingface-cli login`.
    """
    from datasets import Dataset
    import pandas as pd

    logger.info(f"Pushing catalog to HF Hub: {repo_id}")

    # Load catalog.jsonl → HF Dataset
    rows = []
    with open(catalog_path) as f:
        for line in f:
            rows.append(json.loads(line))

    ds = Dataset.from_list(rows)

    if embeddings_dir:
        import numpy as np
        emb_path = Path(embeddings_dir) / "embeddings.npy"
        ids_path = Path(embeddings_dir) / "item_ids.json"
        if emb_path.exists() and ids_path.exists():
            matrix = np.load(emb_path)
            ids    = json.loads(ids_path.read_text())
            logger.info(f"  attaching embeddings {matrix.shape}")
            # Align embeddings by item_id
            id_to_vec = dict(zip(ids, matrix.tolist()))
            ds = ds.map(
                lambda ex: {"embedding": id_to_vec.get(ex["item_id"], None)},
                desc="Attaching embeddings",
            )
        else:
            logger.warning("embeddings_dir provided but files not found — skipping")

    ds.push_to_hub(repo_id, private=private)
    logger.info(f"Dataset pushed → https://huggingface.co/datasets/{repo_id}")


# ── CLI ───────────────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    import os

    p = argparse.ArgumentParser(
        description="Amazon Reviews 2023: prepare catalog.jsonl + optional embeddings / HF upload",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--category", "-c",
        nargs="+",
        metavar="CAT",
        help="One or more category names (see --list-categories)",
    )
    p.add_argument(
        "--max-items", "-n",
        type=int,
        default=None,
        metavar="N",
        help="Maximum items per category (omit for the full category)",
    )
    p.add_argument(
        "--out", "-o",
        default=os.getenv("CATALOG_PATH", "data/catalog.jsonl"),
        metavar="PATH",
        help="Output catalog JSONL path (default: $CATALOG_PATH or data/catalog.jsonl)",
    )
    p.add_argument(
        "--append",
        action="store_true",
        help="Append to an existing catalog instead of overwriting",
    )
    p.add_argument(
        "--streaming",
        action="store_true",
        help="Stream from HF instead of downloading the full split first "
             "(saves disk but slightly slower; good for huge categories like Books)",
    )
    p.add_argument(
        "--embed",
        action="store_true",
        help="Precompute embeddings and save embeddings.npy + item_ids.json "
             "next to the catalog file",
    )
    p.add_argument(
        "--build-index",
        action="store_true",
        help="Build the FAISS index after writing the catalog",
    )
    p.add_argument(
        "--index-path",
        default=os.getenv("FAISS_INDEX_PATH", "data/faiss.index"),
        metavar="PATH",
        help="FAISS index output path (default: $FAISS_INDEX_PATH or data/faiss.index)",
    )
    p.add_argument(
        "--push-to-hub",
        metavar="REPO_ID",
        default=None,
        help="Upload the processed catalog (+ embeddings if --embed) to this "
             "HF Hub dataset repo  e.g. your-username/tara-amazon-catalog",
    )
    p.add_argument(
        "--hub-public",
        action="store_true",
        help="Make the pushed HF repo public (default: private)",
    )
    p.add_argument(
        "--list-categories",
        action="store_true",
        help="Print all known category names and exit",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_categories:
        print(f"Known categories in {DATASET_REPO}:\n")
        for cat in CATEGORIES:
            print(f"  {cat}")
        return

    if not args.category:
        logger.error("Specify --category (or --list-categories to see options)")
        sys.exit(1)

    out_path = Path(args.out)

    # ── 1. download + convert ─────────────────────────────────────────────
    items = process_categories(
        categories=args.category,
        out_path=out_path,
        max_items=args.max_items,
        append=args.append,
        streaming=args.streaming,
    )

    # ── 2. precompute embeddings ──────────────────────────────────────────
    if args.embed:
        embed_dir = out_path.parent / "embeddings"
        precompute_embeddings(items, embed_dir)
    else:
        embed_dir = None

    # ── 3. build FAISS index ──────────────────────────────────────────────
    if args.build_index:
        build_faiss_index(str(out_path), args.index_path)

    # ── 4. push to HF Hub ─────────────────────────────────────────────────
    if args.push_to_hub:
        push_to_hub(
            catalog_path=str(out_path),
            repo_id=args.push_to_hub,
            embeddings_dir=str(embed_dir) if embed_dir else None,
            private=not args.hub_public,
        )


if __name__ == "__main__":
    main()
