#!/usr/bin/env python3
"""
prepare_amazon_catalog.py
─────────────────────────
Amazon → catalog.jsonl builder (RAG-ready)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# ── project root ──────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_PROJECT = _HERE.parent
sys.path.insert(0, str(_PROJECT))

from core.log import logger  # noqa: E402

# ── dataset ───────────────────────────────────────────────────────────────────

DATASET_REPO = "milistu/AMAZON-Products-2023"

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


# ──────────────────────────────────────────────────────────────────────────────
# JSON SAFE LAYER (FIX CRASH)
# ──────────────────────────────────────────────────────────────────────────────

def _json_safe(obj):
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(x) for x in obj]
    if isinstance(obj, tuple):
        return [_json_safe(x) for x in obj]
    return obj


# ──────────────────────────────────────────────────────────────────────────────
# schema mapping
# ──────────────────────────────────────────────────────────────────────────────

def _to_catalog_item(row: dict) -> dict:
    item_id = str(row.get("parent_asin") or "").strip()
    if not item_id:
        raise ValueError("missing parent_asin")

    title = str(row.get("title") or "").strip()

    category = (
        str(row.get("main_category") or "").strip()
        or str(row.get("filename") or "").replace("meta_", "").replace("_", " ").strip()
    )

    parts: List[str] = []
    if category:
        parts.append(category)
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

    price_raw = row.get("price")
    try:
        price = float(price_raw) if price_raw is not None else 0.0
    except (ValueError, TypeError):
        price = 0.0

    from core.config import AD_QUESTION_TEMPLATE, DEFAULT_AD_CTA

    metadata = {}
    for k in [
        "store",
        "average_rating",
        "rating_number",
        "details",
        "image",
        "categories",
        "date_first_available",
    ]:
        if row.get(k) is not None:
            metadata[k] = _json_safe(row[k])

    return {
        "item_id": item_id,
        "title": title,
        "text": text,
        "category": category,
        "price": price,
        "cta": DEFAULT_AD_CTA,
        "question": AD_QUESTION_TEMPLATE.format(title=title),
        "metadata": metadata,
    }


# ──────────────────────────────────────────────────────────────────────────────
# ingestion
# ──────────────────────────────────────────────────────────────────────────────

def process(
    categories: Optional[List[str]],
    out_path: Path,
    max_items: Optional[int],
    append: bool,
    streaming: bool,
) -> List[dict]:

    from datasets import load_dataset

    logger.info(f"Loading {DATASET_REPO} streaming={streaming}")

    ds = load_dataset(DATASET_REPO, split="train", streaming=streaming)

    cat_filter = {c.lower() for c in categories} if categories else None

    out_path.parent.mkdir(parents=True, exist_ok=True)

    mode = "a" if append else "w"
    seen_ids = set()

    if append and out_path.exists():
        with open(out_path) as f:
            for line in f:
                try:
                    seen_ids.add(json.loads(line)["item_id"])
                except Exception:
                    pass

    items = []
    written = 0
    skipped = 0

    with open(out_path, mode, encoding="utf-8") as fh:
        for row in ds:

            if cat_filter is not None:
                fname = str(row.get("filename") or "").lower()
                if fname not in cat_filter:
                    continue

            if max_items and written >= max_items:
                break

            try:
                item = _to_catalog_item(row)
            except Exception:
                skipped += 1
                continue

            iid = item["item_id"]
            if iid in seen_ids:
                skipped += 1
                continue

            fh.write(json.dumps(_json_safe(item), ensure_ascii=False) + "\n")

            seen_ids.add(iid)
            items.append(item)
            written += 1

            if written % 10_000 == 0:
                logger.info(f"{written:,} written")

    logger.info(f"Done — wrote {written:,} skipped {skipped:,}")
    logger.info(f"Catalog -> {out_path.resolve()}")
    return items


# ──────────────────────────────────────────────────────────────────────────────
# FAISS
# ──────────────────────────────────────────────────────────────────────────────

def build_faiss_index(catalog_path: str, index_path: str) -> None:
    from core.config import EMBEDDING_MODEL_NAME, EMBEDDING_DEVICE
    from core.retrieval.catalog import AdCatalog
    from core.retrieval.embeddings import build_embedding_model

    logger.info("Building FAISS index (batch_size=16, dtype=bfloat16)")

    embed = build_embedding_model(
        model_name=EMBEDDING_MODEL_NAME,
        device=EMBEDDING_DEVICE,
        batch_size=16,  # Use smaller batch size for lower memory usage
        dtype="bfloat16",  # Force bfloat16 for lower VRAM
    )

    AdCatalog.load(
        catalog_path=catalog_path,
        index_path=index_path,
        embedding_model=embed,
        force_rebuild=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def parse_args():
    import os

    p = argparse.ArgumentParser()

    p.add_argument("-c", "--category", nargs="+")
    p.add_argument("-n", "--max-items", type=int)

    p.add_argument(
        "--out",
        default=os.getenv("CATALOG_DIR", "data/catalogs"),
    )

    p.add_argument("--append", action="store_true")
    p.add_argument("--streaming", action="store_true")
    p.add_argument("--build-index", action="store_true")
    p.add_argument("--index-path", default="data/faiss.index")

    # 🔥 NEW: force re-ingestion control
    p.add_argument("--force-ingest", action="store_true")

    return p.parse_args()


# ──────────────────────────────────────────────────────────────────────────────
# MERGE
# ──────────────────────────────────────────────────────────────────────────────

def merge_catalogs(root: Path) -> None:
    logger.info(f"Merging catalogs in {root}")

    out_file = root / "catalog.jsonl"
    seen = set()
    merged = 0

    with open(out_file, "w", encoding="utf-8") as out:

        for path in root.glob("*.jsonl"):
            if path.name == "catalog.jsonl":
                continue

            with open(path) as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        iid = obj.get("item_id")
                        if iid in seen:
                            continue
                        seen.add(iid)
                        out.write(json.dumps(obj, ensure_ascii=False) + "\n")
                        merged += 1
                    except Exception:
                        continue

    logger.info(f"Merged {merged:,} items → {out_file}")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN (CACHE-AWARE)
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    root = Path(args.out)
    amazon_path = root / "amazon.jsonl"

    # ── SKIP INGESTION IF ALREADY EXISTS ───────────────────────
    if args.force_ingest or not amazon_path.exists():
        process(
            categories=args.category,
            out_path=amazon_path,
            max_items=args.max_items,
            append=args.append,
            streaming=args.streaming,
        )
    else:
        logger.info("Skipping ingestion (amazon.jsonl already exists)")

    # ── MERGE ──────────────────────────────────────────────────
    merge_catalogs(root)

    # ── FAISS ──────────────────────────────────────────────────
    if args.build_index:
        build_faiss_index(str(root / "catalog.jsonl"), args.index_path)


if __name__ == "__main__":
    main()