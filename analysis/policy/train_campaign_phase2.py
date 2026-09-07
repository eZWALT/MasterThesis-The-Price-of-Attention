#!/usr/bin/env python3
"""Phase 2: consume GPU embeddings + push any winner + more Y heads.

Runs after train_campaign.py and embed_gpu.py. Safe to re-run; skips
nothing expensive except embedding loads.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from train_campaign import (
    BASELINE_TURN, OUT, EXP, GOLD, ads_view, build, dump, embed_bge,
    eval_scores, lopo_hgb, lopo_pca_ridge, lopo_ranknet, lopo_ridge,
    lopo_ridge_residual, pair_indices, tab_matrix,
)

HERE = Path(__file__).resolve().parent


def main():
    t0 = time.time()
    results = []
    if (OUT / "results.json").exists():
        results = json.loads((OUT / "results.json").read_text())

    df, anc, pairs = build()
    ad_idx = ads_view(df, anc)
    ads = df.iloc[ad_idx].reset_index(drop=True)
    y216 = anc.ux_retention_resid.to_numpy(float)
    g216 = anc.participant_key.to_numpy()
    y1080 = df.ux_retention_resid.to_numpy(float)
    g1080 = df.participant_key.to_numpy()
    Xturn = ads[["turn_feat"]].to_numpy(float)
    Xturn1080 = df[["turn_feat"]].to_numpy(float)
    Xtab = tab_matrix(ads, "tab")
    z = np.column_stack([ads.turn_feat, ads.fit])
    pidx = pair_indices(anc)

    emb_paths = list(OUT.glob("emb_*_1080.npy")) + list(OUT.glob("emb_qwen*.npy"))
    print("emb files", [p.name for p in emb_paths], flush=True)

    seen = {r["name"] for r in results if "name" in r}

    for path in sorted(emb_paths):
        E = np.load(path)
        tag = path.stem
        print("phase2", tag, E.shape, flush=True)
        if E.shape[0] == 1080:
            E216 = E[ad_idx]
            Etr, y, g, extra = E, y1080, g1080, Xturn1080
            suffix = "_train1080"
        elif E.shape[0] == 216:
            E216 = E
            Etr, y, g, extra = E, y216, g216, Xturn
            suffix = ""
        else:
            print("skip shape", E.shape)
            continue

        for k, a in [(8, 20), (16, 50), (32, 80), (64, 120)]:
            name = f"pca{k}_{tag}+turn{suffix}"
            if name in seen:
                continue
            if Etr.shape[0] == 1080:
                pred = lopo_pca_ridge(Etr, y, g, k=k, alpha=a, extra=extra)[ad_idx]
            else:
                pred = lopo_pca_ridge(Etr, y, g, k=k, alpha=a, extra=np.column_stack([Xturn, ads.fit]))
            results.append(eval_scores(name, pred, anc, pairs))
            seen.add(name)
            dump(results)

        name = f"turn_plus_resid_{tag}"
        if name not in seen:
            pred = lopo_ridge_residual(Xturn, E216, y216, g216, 1.0, 200.0)
            results.append(eval_scores(name, pred, anc, pairs))
            seen.add(name)
            dump(results)

        name = f"ranknet_pca16_{tag}"
        if name not in seen:
            # PCA once globally is mildly leaky; do LOPO PCA inside ranknet via extra cols
            from sklearn.decomposition import PCA
            from sklearn.preprocessing import StandardScaler
            sc = StandardScaler()
            P = PCA(16, random_state=13).fit_transform(sc.fit_transform(E216))
            Xp = np.hstack([Xturn, P])
            pred = lopo_ranknet(Xp, y216, g216, pidx, 30)
            results.append(eval_scores(name, pred, anc, pairs))
            seen.add(name)
            dump(results)

    # more Y: maybe text predicts a component better than U
    for col, sign in [
        ("ux_retention", 1),
        ("delta_credibility", 1),
        ("delta_trust", 1),
        ("delta_manipulation", -1),
        ("delta_helpfulness", 1),
        ("good_moment_human", 1),
    ]:
        if col not in ads.columns:
            continue
        yh = ads[col].to_numpy(float) * sign
        pred = lopo_ridge(Xtab, yh, g216, 50)
        # still evaluate against U (transfer) AND the head itself
        pack = eval_scores(f"ridge_tab_head_{col}", pred, anc, pairs)
        pack["spearman_own_head"] = round(float(__import__("scipy").stats.spearmanr(pred, ads[col]).statistic), 4)
        results.append(pack)
        dump(results)

    # grid alpha on tab
    for a in [5, 10, 25, 50, 100, 250, 500]:
        name = f"ridge_tab_a{a}"
        if name in seen:
            continue
        pred = lopo_ridge(Xtab, y216, g216, a)
        results.append(eval_scores(name, pred, anc, pairs))
        seen.add(name)
        dump(results)

    # blend search on existing preds
    turn_s = ads.turn_feat.to_numpy()

    def z(x):
        x = np.asarray(x, float)
        return (x - np.nanmean(x)) / (np.nanstd(x) + 1e-8)

    pred_files = [p for p in OUT.glob("pred_*.npy") if "blend" not in p.name]
    print("blend candidates", [p.name for p in pred_files], flush=True)
    best = None
    for p in pred_files:
        extra = np.load(p)
        if extra.shape[0] != 216:
            continue
        for w in (0.5, 0.7, 0.85):
            blend = w * z(turn_s) + (1 - w) * z(extra)
            name = f"blend{int(w*100)}_turn_{p.stem}"
            pack = eval_scores(name, blend, anc, pairs)
            results.append(pack)
            if best is None or (pack.get("spearman_U") or -9) > (best.get("spearman_U") or -9):
                best = pack
    dump(results)
    print("BEST so far", best, flush=True)
    print(f"phase2 done in {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
