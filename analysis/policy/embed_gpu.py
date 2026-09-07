#!/usr/bin/env python3
"""Encode all primary prefixes with real embedding models on GPU 1.

Not last-token probes — Qwen3-Embedding / bge mean-pool. Writes
outputs/experiments/full/emb_<name>_1080.npy for the campaign to pick up.
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "experiments" / "full"
OUT.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("qwen3-emb-0.6b", "Qwen/Qwen3-Embedding-0.6B", 32),
    ("qwen3-emb-4b", "Qwen/Qwen3-Embedding-4B", 8),
    ("qwen3-emb-8b", "Qwen/Qwen3-Embedding-8B", 4),
]


def main():
    df = pd.read_csv(HERE / "outputs/silver/turns.csv")
    df = df[df.source_set == "primary"].reset_index(drop=True)
    texts = df.prefix_text.fillna("").tolist()
    print("texts", len(texts), flush=True)

    from sentence_transformers import SentenceTransformer
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("device", device, flush=True)

    for tag, hub, bs in MODELS:
        dest = OUT / f"emb_{tag}_1080.npy"
        if dest.exists() and np.load(dest).shape[0] == len(texts):
            print("skip existing", dest, flush=True)
            continue
        t0 = time.time()
        print("loading", hub, flush=True)
        try:
            model = SentenceTransformer(
                hub, device=device,
                model_kwargs={"torch_dtype": torch.bfloat16} if device == "cuda" else {},
            )
        except Exception as exc:
            print(f"FAIL load {hub}: {type(exc).__name__}: {exc}", flush=True)
            continue
        vec = model.encode(
            texts, batch_size=bs, convert_to_numpy=True, show_progress_bar=True,
            normalize_embeddings=True,
        )
        np.save(dest, vec.astype(np.float32))
        print(f"wrote {dest} {vec.shape} in {(time.time()-t0)/60:.1f} min", flush=True)
        del model
        if device == "cuda":
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
