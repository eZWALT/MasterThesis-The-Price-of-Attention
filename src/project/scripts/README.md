# scripts/

Utility scripts for data preparation and offline processing.

---

## `prepare_amazon_catalog.py`

Pulls **Amazon Reviews 2023 item metadata** from Hugging Face, converts it to
`data/catalog.jsonl` (the schema `AdCatalog` / `AmazonAdapter` expect), and
optionally precomputes embeddings or pushes the result back to your own HF repo.

Uses the official `datasets` library — HF handles caching, retries, and auth.

### Install dependencies

```bash
pip install datasets huggingface_hub
# or just: pip install -r requirements.txt
```

For protected repos or upload, log in first:
```bash
huggingface-cli login   # paste your HF token once
# or set env var: export HF_TOKEN=hf_...
```

---

### List available categories

```bash
python scripts/prepare_amazon_catalog.py --list-categories
```

---

### Common recipes

**Quick sanity check** (≈ 2 k items, no GPU needed):
```bash
python scripts/prepare_amazon_catalog.py \
    --category All_Beauty \
    --max-items 2000 \
    --out data/catalog.jsonl
```

**Full single category** (streams to avoid keeping the whole split in RAM):
```bash
python scripts/prepare_amazon_catalog.py \
    --category Electronics \
    --streaming
```

**Merge multiple categories, cap each at 50 k items**:
```bash
python scripts/prepare_amazon_catalog.py \
    --category Electronics Cell_Phones_and_Accessories Sports_and_Outdoors \
    --max-items 50000
```

**Append more categories to an existing catalog**:
```bash
python scripts/prepare_amazon_catalog.py \
    --category Home_and_Kitchen \
    --append
```

**Convert + precompute embeddings** (writes `data/embeddings/embeddings.npy` +
`data/embeddings/item_ids.json`):
```bash
python scripts/prepare_amazon_catalog.py \
    --category All_Beauty \
    --max-items 5000 \
    --embed
```
Model and device are read from `EMBEDDING_MODEL_NAME` / `EMBEDDING_DEVICE` in
`core/config.py` (defaults: `Qwen/Qwen3-Embedding-8B` on `cuda:1`).

**Convert + build the FAISS index in one go**:
```bash
python scripts/prepare_amazon_catalog.py \
    --category All_Beauty \
    --max-items 5000 \
    --build-index
```

**Upload processed catalog (+ embeddings) to your HF Hub repo**:
```bash
python scripts/prepare_amazon_catalog.py \
    --category All_Beauty \
    --max-items 5000 \
    --embed \
    --push-to-hub your-username/tara-amazon-catalog
# add --hub-public to make the repo public
```

---

### Output files

| File | Description |
|------|-------------|
| `data/catalog.jsonl` | Normalised product records (one JSON per line) |
| `data/embeddings/embeddings.npy` | float32 array `(N, dim)` — only with `--embed` |
| `data/embeddings/item_ids.json` | `item_id` list aligned with embedding rows |
| `data/faiss.index` | FAISS flat-IP index — only with `--build-index` |

### Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CATALOG_PATH` | `data/catalog.jsonl` | Override `--out` default |
| `FAISS_INDEX_PATH` | `data/faiss.index` | Override `--index-path` default |
| `EMBEDDING_MODEL_NAME` | `Qwen/Qwen3-Embedding-8B` | Model used by `--embed` / `--build-index` |
| `EMBEDDING_DEVICE` | `cuda:1` | Device for embedding model |
| `HF_TOKEN` | — | HF auth token (for upload or gated repos) |
