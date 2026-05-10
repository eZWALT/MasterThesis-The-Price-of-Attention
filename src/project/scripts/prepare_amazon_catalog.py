#!/usr/bin/env python3
"""
prepare_amazon_catalog.py
─────────────────────────
Pull the `milistu/AMAZON-Products-2023` dataset from Hugging Face, convert
it to the project's catalog.jsonl schema, and optionally build the FAISS
index or push a processed version back to HF Hub.

The source dataset (117 k products, 2023 listings) lives at:
    https://huggingface.co/datasets/milistu/AMAZON-Products-2023

It is a single `train` split with 15 columns; category is identified by
the `filename` column (e.g. "meta_Electronics"). Precomputed embeddings
(text-embedding-3-small) are included but are empty lists for most rows
— use --build-index to re-embed with the project model.

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

# ── dataset constants ─────────────────────────────────────────────────────────

DATASET_REPO = "milistu/AMAZON-Products-2023"

# Exact values of the `filename` column — used for --category filtering.
CATEGORIES: List[str] = [
    "meta_Amazon_Fashion",
    "meta_Appliances",
    "meta_Arts_Crafts_and_Sewing",
    "meta_Automotive",
    "meta_Baby_Products",
    "meta_Beauty_and_Personal_Care",
    "meta_Books",
    "meta_CDs_and_Vinyl",
    "meta_Cell_Phones_and_Accessories",
    "meta_Clothing_Shoes_and_Jewelry",
    "meta_Digital_Music",
    "meta_Electronics",
    "meta_Gift_Cards",
    "meta_Grocery_and_Gourmet_Food",
    "meta_Handmade_Products",
    "meta_Health_and_Household",
    "meta_Health_and_Personal_Care",
    "meta_Home_and_Kitchen",
    "meta_Industrial_and_Scientific",
    "meta_Magazine_Subscriptions",
    "meta_Musical_Instruments",
    "meta_Office_Products",
    "meta_Patio_Lawn_and_Garden",
    "meta_Pet_Supplies",
    "meta_Software",
    "meta_Sports_and_Outdoors",
    "meta_Tools_and_Home_Improvement",
    "meta_Toys_and_Games",
    "meta_Unknown",
    "meta_Video_Games",
]


# ── schema mapping ────────────────────────────────────────────────────────────


def _to_catalog_item(row: dict) -> dict:
    """
    Map one row from milistu/AMAZON-Products-2023 to the project's
    normalised catalog schema expected by AdCatalog.

    Source columns:
        parent_asin, title, description, filename, main_category,
        categories, store, average_rating, rating_number, price,
        features, details, embeddings, image, date_first_available
    """
    item_id = str(row.get("parent_asin") or "").strip()
    if not item_id:
        raise ValueError("missing parent_asin")

    title = str(row.get("title") or "").strip()

    # Build a dense text field for embedding / BM25
    parts: List[str] = []
    if title:
        parts.append(title)

    features = row.get("features") or []
    if isinstance(features, str):
        features = [features]
    for f in features[:10]:
        f = str(f).strip()
        if f:
            parts.append(f)

    desc = row.get("description") or ""
    if isinstance(desc, list):
        desc = " ".join(str(d) for d in desc if d)
    desc = str(desc).strip()
    if desc:
        parts.append(desc)

    text = " ".join(parts).strip() or title

    category = (
        str(row.get("main_category") or "").strip()
        or str(row.get("filename") or "").replace("meta_", "").replace("_", " ").strip()
    )

    price_raw = row.get("price")
    try:
        price = float(price_raw) if price_raw is not None else 0.0
    except (ValueError, TypeError):
        price = 0.0

    from core.config import AD_QUESTION_TEMPLATE

    metadata: dict = {}
    if row.get("store"):
        metadata["store"] = str(row["store"])
    if row.get("average_rating") is not None:
        metadata["average_rating"] = row["average_rating"]
    if row.get("rating_number") is not None:
        metadata["rating_number"] = row["rating_number"]
    if row.get("details"):
        metadata["details"] = row["details"]
    if row.get("image"):
        metadata["image"] = row["image"]
    if row.get("categories"):
        metadata["categories"] = row["categories"]
    if row.get("date_first_available"):
        metadata["date_first_available"] = str(row["date_first_available"])

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


# ── processing ────────────────────────────────────────────────────────────────


def process(
    categories: Optional[List[str]],
    out_path: Path,
    max_items: Optional[int],
    append: bool,
    streaming: bool,
) -> List[dict]:
    """
    Stream the HF dataset, optionally filter by filename/category,
    write catalog.jsonl, and return converted items.
    """
    from datasets import load_dataset

    logger.info(f"Loading {DATASET_REPO}  streaming={streaming}")
    ds = load_dataset(DATASET_REPO, split="train", streaming=streaming)

    # normalise category filter to lowercase set for fast lookup
    cat_filter: Optional[set] = None
    if categories:
        cat_filter = {c.lower() for c in categories}
        logger.info(f"Filtering to categories: {categories}")

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
        logger.info(f"  {len(seen_ids):,} existing ids loaded for dedup")

    items: List[dict] = []
    written = skipped = 0

    with open(out_path, mode, encoding="utf-8") as fh:
        for row in ds:
            # category filter
            if cat_filter is not None:
                fname = str(row.get("filename") or "").lower()
                if fname not in cat_filter:
                    continue

            if max_items is not None and written >= max_items:
                break

            try:
                item = _to_catalog_item(row)
            except (ValueError, KeyError) as exc:
                logger.debug(f"Skipping record: {exc}")
                skipped += 1
                continue

            iid = item["item_id"]
            if iid in seen_ids:
                skipped += 1
                continue

            fh.write(json.dumps(item, ensure_ascii=False) + "\n")
            seen_ids.add(iid)
            items.append(item)
            written += 1

            if written % 10_000 == 0:
                logger.info(f"  ... {written:,} written")

    logger.info(f"Done — wrote {written:,}  skipped/deduped {skipped:,}")
    logger.info(f"Catalog -> {out_path.resolve()}")
    return items


# ── FAISS index ───────────────────────────────────────────────────────────────


def build_faiss_index(catalog_path: str, index_path: str) -> None:
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
    logger.info(f"FAISS index -> {index_path}")


# ── HF Hub upload ─────────────────────────────────────────────────────────────


def push_to_hub(catalog_path: str, repo_id: str, private: bool = True) -> None:
    from datasets import Dataset

    logger.info(f"Pushing catalog to HF Hub: {repo_id}")
    rows = []
    with open(catalog_path) as f:
        for line in f:
            rows.append(json.loads(line))

    Dataset.from_list(rows).push_to_hub(repo_id, private=private)
    logger.info(f"Dataset pushed -> https://huggingface.co/datasets/{repo_id}")


# ── CLI ───────────────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    import os

    p = argparse.ArgumentParser(
        description=f"Convert {DATASET_REPO} -> catalog.jsonl",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--category", "-c",
        nargs="+",
        metavar="CAT",
        help=(
            "Filter to these filename values (e.g. meta_Electronics). "
            "Omit for all categories. See --list-categories."
        ),
    )
    p.add_argument(
        "--max-items", "-n",
        type=int,
        default=None,
        metavar="N",
        help="Stop after writing N items total (useful for quick tests)",
    )
    p.add_argument(
        "--out", "-o",
        default=os.getenv("CATALOG_PATH", "data/catalog.jsonl"),
        metavar="PATH",
        help="Output catalog JSONL (default: $CATALOG_PATH or data/catalog.jsonl)",
    )
    p.add_argument(
        "--append",
        action="store_true",
        help="Append to an existing catalog instead of overwriting",
    )
    p.add_argument(
        "--streaming",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Stream rows from HF instead of downloading the full dataset first "
            "(default: True). Use --no-streaming for full-dataset builds where "
            "the parallel chunk download is faster."
        ),
    )
    p.add_argument(
        "--build-index",
        action="store_true",
        help="Build (or rebuild) the FAISS index after writing the catalog",
    )
    p.add_argument(
        "--index-path",
        default=os.getenv("FAISS_INDEX_PATH", "data/faiss.index"),
        metavar="PATH",
        help="FAISS index path (default: $FAISS_INDEX_PATH or data/faiss.index)",
    )
    p.add_argument(
        "--push-to-hub",
        metavar="REPO_ID",
        default=None,
        help=(
            "Upload processed catalog to this HF Hub repo "
            "(e.g. your-username/tara-catalog). "
            "Requires HF_TOKEN or `huggingface-cli login`."
        ),
    )
    p.add_argument(
        "--hub-public",
        action="store_true",
        help="Make the pushed HF repo public (default: private)",
    )
    p.add_argument(
        "--list-categories",
        action="store_true",
        help="Print all known filename/category values and exit",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_categories:
        print(f"Known categories in {DATASET_REPO} (value of `filename` column):\n")
        for cat in CATEGORIES:
            print(f"  {cat}")
        return

    out_path = Path(args.out)

    items = process(
        categories=args.category,
        out_path=out_path,
        max_items=args.max_items,
        append=args.append,
        streaming=args.streaming,
    )

    if args.build_index:
        build_faiss_index(str(out_path), args.index_path)

    if args.push_to_hub:
        push_to_hub(
            catalog_path=str(out_path),
            repo_id=args.push_to_hub,
            private=not args.hub_public,
        )


if __name__ == "__main__":
    main()
