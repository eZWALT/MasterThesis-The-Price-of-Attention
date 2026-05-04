# scripts/

Utility scripts for data preparation and offline processing.

---

## `prepare_amazon_catalog.py`

Converts the [`milistu/AMAZON-Products-2023`](https://huggingface.co/datasets/milistu/AMAZON-Products-2023)
dataset into the project's `data/catalog.jsonl`, and optionally builds the
FAISS index or uploads the result to your own HF Hub repo.

**Dataset facts:**
- 117,243 products, single `train` split
- Filtered to items first available in 2023
- Category is stored in the `filename` column (e.g. `meta_Electronics`)
- Already has an `embeddings` column (text-embedding-3-small), but it is
  empty for most rows — use `--build-index` to re-embed with the project model

### Install

```bash
pip install -r requirements.txt   # datasets + huggingface_hub already included
huggingface-cli login             # only needed for --push-to-hub
```

---

### List available categories

```bash
python scripts/prepare_amazon_catalog.py --list-categories
```

---

### Common recipes

**Quick sanity check** (small slice, no GPU):
```bash
python scripts/prepare_amazon_catalog.py \
    --category meta_Electronics \
    --max-items 500
```

**Single full category** (~7.7 k Electronics items):
```bash
python scripts/prepare_amazon_catalog.py --category meta_Electronics
```

**Multiple categories merged**:
```bash
python scripts/prepare_amazon_catalog.py \
    --category meta_Electronics meta_Cell_Phones_and_Accessories meta_Sports_and_Outdoors
```

**Append a new category to an existing catalog**:
```bash
python scripts/prepare_amazon_catalog.py \
    --category meta_Home_and_Kitchen \
    --append
```

**Full dataset** (all 117 k products):
```bash
python scripts/prepare_amazon_catalog.py
```

**Convert + build the FAISS index in one go**:
```bash
python scripts/prepare_amazon_catalog.py \
    --category meta_Electronics \
    --build-index
```

**Stream from HF** (skips local cache download; useful when filtering a tiny
subset and disk space is tight):
```bash
python scripts/prepare_amazon_catalog.py \
    --category meta_Software \
    --streaming
```

**Push processed catalog to your HF Hub repo**:
```bash
python scripts/prepare_amazon_catalog.py \
    --category meta_Electronics \
    --push-to-hub your-username/tara-catalog
# add --hub-public to make the repo public
```

---

### Output files

| File | Description |
|------|-------------|
| `data/catalog.jsonl` | Normalised product records (one JSON per line) |
| `data/faiss.index` | FAISS flat-IP index — only with `--build-index` |

### Catalog JSONL schema

```json
{
  "item_id":  "B0XXXXXXXX",
  "title":    "Product name",
  "text":     "title + features + description (embedding input)",
  "category": "Electronics",
  "price":    29.99,
  "cta":      "Shop now",
  "question": "Looking for Product name?",
  "metadata": {
    "store": "BrandName",
    "average_rating": 4.3,
    "rating_number": 120,
    "image": "https://...",
    "categories": ["Electronics", "Accessories"],
    "details": "{...}",
    "date_first_available": "2023-03-15"
  }
}
```

### Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CATALOG_PATH` | `data/catalog.jsonl` | Override `--out` default |
| `FAISS_INDEX_PATH` | `data/faiss.index` | Override `--index-path` default |
| `EMBEDDING_MODEL_NAME` | `Qwen/Qwen3-Embedding-8B` | Model used by `--build-index` |
| `EMBEDDING_DEVICE` | `cuda:1` | Device for embedding model |
| `HF_TOKEN` | — | HF auth token (for `--push-to-hub`) |
