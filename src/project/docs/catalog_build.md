# Catalog Build

Rebuild the Amazon product catalog JSONL + FAISS index from scratch.

## Prerequisites

Run from the repo root with `datasets`, `faiss`, `sentence-transformers`, `rank-bm25`, `loguru` installed.

## Command

```bash
python src/project/scripts/prepare_amazon_catalog.py \
  --force-ingest --build-index --streaming \
  --category \
    meta_Amazon_Fashion meta_Appliances meta_Arts_Crafts_and_Sewing meta_Automotive \
    meta_Baby_Products meta_Beauty_and_Personal_Care meta_Books meta_CDs_and_Vinyl \
    meta_Cell_Phones_and_Accessories meta_Clothing_Shoes_and_Jewelry meta_Digital_Music \
    meta_Electronics meta_Gift_Cards meta_Grocery_and_Gourmet_Food meta_Handmade_Products \
    meta_Health_and_Household meta_Health_and_Personal_Care meta_Home_and_Kitchen \
    meta_Industrial_and_Scientific meta_Magazine_Subscriptions meta_Musical_Instruments \
    meta_Office_Products meta_Patio_Lawn_and_Garden meta_Pet_Supplies meta_Software \
    meta_Sports_and_Outdoors meta_Tools_and_Home_Improvement meta_Toys_and_Games \
    meta_Unknown meta_Video_Games
```

## Output

- `data/catalogs/amazon.jsonl` — raw per-category items (117k+ rows)
- `data/catalogs/catalog.jsonl` — merged deduplicated catalog
- `data/faiss.index` — FAISS IndexFlatIP built from catalog item embeddings

## Category Filtering at Retrieval Time

Each `TaskDefinition` in `core/experiment/tasks.py` has a `relevant_categories` field listing allowed `meta_*` categories. At runtime, the `HybridRefiner` filters FAISS candidates to only those whose `metadata.filename` matches the current task's categories.

The `pool_size` field in logged events (`condition_started`, `condition_conclusion_submitted`, `condition_complete`, `conversation_completed`) shows how many catalog items match the task's categories.
