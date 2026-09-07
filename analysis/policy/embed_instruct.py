#!/usr/bin/env python3
"""Re-encode 216 ad prefixes with the Qwen3-Embedding instruction template.

Default encode() has no task instruction. The industrial query is
'is this a good moment for one product mention?'
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from train_campaign import GOLD, OUT, eval_scores, lopo_pca_ridge

HERE = Path(__file__).resolve().parent
INSTR = (
    "Instruct: Represent this shopping-assistant conversation to decide whether "
    "NOW is a good moment to mention one relevant product, for the user's trust "
    "and usefulness.\nQuery: "
)


def main():
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    texts = [INSTR + str(t) for t in anc.prefix_text.fillna("")]
    y = anc.ux_retention_resid.to_numpy(float)
    g = anc.participant_key.to_numpy()
    turn = (anc.ad_turn.clip(upper=8) / 8.0).to_numpy()[:, None]

    from sentence_transformers import SentenceTransformer
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    results = []
    for tag, hub, bs in [
        ("qwen06_instruct", "Qwen/Qwen3-Embedding-0.6B", 16),
        ("qwen4b_instruct", "Qwen/Qwen3-Embedding-4B", 8),
        ("qwen8b_instruct", "Qwen/Qwen3-Embedding-8B", 4),
    ]:
        dest = OUT / f"emb_{tag}_216.npy"
        if dest.exists() and np.load(dest).shape[0] == 216:
            E = np.load(dest)
        else:
            print("encode", hub, flush=True)
            model = SentenceTransformer(
                hub, device=device,
                model_kwargs={"dtype": torch.bfloat16} if device == "cuda" else {},
            )
            E = model.encode(texts, batch_size=bs, convert_to_numpy=True,
                             normalize_embeddings=True).astype(np.float32)
            np.save(dest, E)
            del model
            if device == "cuda":
                torch.cuda.empty_cache()
        print(tag, E.shape, flush=True)
        for k, a in [(8, 20), (16, 50)]:
            results.append(eval_scores(f"pca{k}_{tag}", lopo_pca_ridge(E, y, g, k, a), anc, pairs))
            results.append(eval_scores(
                f"pca{k}_{tag}+turn",
                lopo_pca_ridge(E, y, g, k, a, extra=turn), anc, pairs,
            ))
        json_path = OUT / "instruct.json"
        import json
        json.dump(results, open(json_path, "w"), indent=2)
    print("done", max(results, key=lambda r: r["spearman_U"] or -9))


if __name__ == "__main__":
    main()
