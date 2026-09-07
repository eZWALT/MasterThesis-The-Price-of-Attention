#!/usr/bin/env python3
"""Train on all 1,080 Qwen3-14B last/mean vectors; eval on 216 ads."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from train_campaign import (
    GOLD, OUT, ads_view, build, eval_scores, lopo_pca_ridge,
    lopo_ridge_residual, tab_matrix,
)


def main():
    df, anc, pairs = build()
    ad_idx = ads_view(df, anc)
    y216 = anc.ux_retention_resid.to_numpy(float)
    g216 = anc.participant_key.to_numpy()
    y1080 = df.ux_retention_resid.to_numpy(float)
    g1080 = df.participant_key.to_numpy()
    turn216 = (anc.ad_turn.clip(upper=8) / 8.0).to_numpy()[:, None]
    turn1080 = df[["turn_feat"]].to_numpy(float)
    results = []
    for name in ("emb_qwen3-14b_last_1080.npy", "emb_qwen3-14b_mean_1080.npy"):
        path = OUT / name
        if not path.exists():
            print("missing", path)
            continue
        E = np.load(path)
        print(name, E.shape, flush=True)
        E216 = E[ad_idx]
        tag = name.replace(".npy", "")
        for k, a in [(4, 10), (8, 20), (16, 50)]:
            pred = lopo_pca_ridge(E, y1080, g1080, k, a, extra=turn1080)[ad_idx]
            results.append(eval_scores(f"pca{k}_{tag}+turn_train1080", pred, anc, pairs))
            pred = lopo_pca_ridge(E216, y216, g216, k, a, extra=turn216)
            results.append(eval_scores(f"pca{k}_{tag}+turn_train216", pred, anc, pairs))
            pred = lopo_pca_ridge(E216, y216, g216, k, a)
            results.append(eval_scores(f"pca{k}_{tag}_train216", pred, anc, pairs))
        pred = lopo_ridge_residual(turn216, E216, y216, g216, 1.0, 80)
        results.append(eval_scores(f"turn_plus_resid_{tag}", pred, anc, pairs))
        json.dump(results, open(OUT / "qwen14b_1080.json", "w"), indent=2)
    (OUT / "QWEN14B_1080.md").write_text(
        "# Qwen3-14B last/mean on 1080 turns\n\n" + "\n".join(
            f"- {r['name']}: {r['spearman_U']} same-t {r.get('pairwise_same_timing')}"
            f"{' BEATS' if r.get('beats_turn') else ''}"
            for r in sorted(results, key=lambda x: -(x['spearman_U'] or -9))
        ) + "\n"
    )
    print((OUT / "QWEN14B_1080.md").read_text())


if __name__ == "__main__":
    main()
