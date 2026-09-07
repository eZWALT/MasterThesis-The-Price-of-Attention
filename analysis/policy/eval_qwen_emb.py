#!/usr/bin/env python3
"""Score the real Qwen3-Embedding matrices (0.6B/4B/8B) on the 216 ads."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from train_campaign import (
    GOLD, OUT, ads_view, eval_scores, lopo_pca_ridge, lopo_ridge_residual,
)

HERE = Path(__file__).resolve().parent


def main():
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    turns = pd.read_csv(HERE / "outputs/silver/turns.csv")
    prim = turns[turns.source_set == "primary"].reset_index(drop=True)
    ad_idx = ads_view(prim, anc)
    y = anc.ux_retention_resid.to_numpy(float)
    g = anc.participant_key.to_numpy()
    turn = (anc.ad_turn.clip(upper=8) / 8.0).to_numpy()[:, None]
    fit = pd.to_numeric(anc.fit_score, errors="coerce").fillna(0).to_numpy()[:, None]
    z = np.hstack([turn, fit])
    results = []
    for path in sorted(OUT.glob("emb_qwen3-emb-*_1080.npy")):
        E = np.load(path)[ad_idx]
        tag = path.stem.replace("_1080", "")
        print(tag, E.shape, flush=True)
        for k, a in [(8, 20), (16, 50), (32, 80)]:
            results.append(eval_scores(f"pca{k}_{tag}", lopo_pca_ridge(E, y, g, k, a), anc, pairs))
            results.append(eval_scores(f"pca{k}_{tag}+turnfit", lopo_pca_ridge(E, y, g, k, a, extra=z), anc, pairs))
        results.append(eval_scores(f"turn_plus_resid_{tag}",
                                   lopo_ridge_residual(turn, E, y, g, 1.0, 200), anc, pairs))
        json.dump(results, open(OUT / "qwen_emb.json", "w"), indent=2)
    (OUT / "QWEN_EMB.md").write_text(
        "# Qwen3-Embedding (real embedder, not last-token)\n\n"
        + "\n".join(
            f"- {r['name']}: Spearman {r['spearman_U']}  same-t {r.get('pairwise_same_timing')}  "
            f"{'BEATS TURN' if r.get('beats_turn') else ''}"
            for r in sorted(results, key=lambda x: -(x['spearman_U'] or -9))
        ) + "\n"
    )
    print((OUT / "QWEN_EMB.md").read_text())


if __name__ == "__main__":
    main()
