#!/usr/bin/env python3
"""Fit PCA on unlabeled prefixes (WildChat + all study turns), then LOPO
ridge on the 216 human labels. This is the 'use all the text we have'
representation, with supervision only on Gold Y.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

from train_campaign import GOLD, OUT, ads_view, eval_scores, spearman

HERE = Path(__file__).resolve().parent
EXT = HERE / "outputs" / "rescued" / "external_prefixes.csv"
if not EXT.exists():
    EXT = HERE / "outputs" / "notebook_runs" / "full" / "external_prefixes.csv"


def embed_texts(texts, dest, hub="BAAI/bge-small-en-v1.5", bs=32):
    if dest.exists() and np.load(dest).shape[0] == len(texts):
        print("cache", dest, flush=True)
        return np.load(dest)
    from sentence_transformers import SentenceTransformer
    import torch
    # WildChat prefixes can be huge — cap them. Stay on CPU if no GPU room.
    texts = [str(t)[:1500] for t in texts]
    device = "cpu"
    model = SentenceTransformer(hub, device=device)
    vec = model.encode(
        texts, batch_size=bs, convert_to_numpy=True,
        show_progress_bar=True, normalize_embeddings=True,
    )
    print("wrote", dest, vec.shape, flush=True)
    del model
    if device == "cuda":
        torch.cuda.empty_cache()
    return vec.astype(np.float32)


def main():
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    turns = pd.read_csv(HERE / "outputs/silver/turns.csv")
    prim = turns[turns.source_set == "primary"].reset_index(drop=True)
    ad_idx = ads_view(prim, anc)
    y = anc.ux_retention_resid.to_numpy(float)
    g = anc.participant_key.to_numpy()
    turn = (anc.ad_turn.clip(upper=8) / 8.0).to_numpy()

    # unlabeled
    ext_texts = []
    if EXT.exists():
        ext = pd.read_csv(EXT)
        col = "prefix_text" if "prefix_text" in ext.columns else ext.columns[-1]
        ext_texts = ext[col].fillna("").astype(str).tolist()
        print("external prefixes", len(ext_texts), flush=True)
    study_texts = prim.prefix_text.fillna("").tolist()

    hub = "BAAI/bge-small-en-v1.5"
    E_ext = embed_texts(ext_texts, OUT / "emb_wildchat_bge.npy", hub) if ext_texts else None
    E_study = np.load(OUT / "emb_bge_1080.npy") if (OUT / "emb_bge_1080.npy").exists() \
        else embed_texts(study_texts, OUT / "emb_bge_1080.npy", hub)

    pool = E_study if E_ext is None else np.vstack([E_ext, E_study])
    print("PCA pool", pool.shape, flush=True)
    results = []
    for k in (8, 16, 32, 64):
        sc = StandardScaler()
        pca = PCA(k, random_state=13)
        pca.fit(sc.fit_transform(pool))
        P_all = pca.transform(sc.transform(E_study))
        P216 = P_all[ad_idx]
        X = np.column_stack([P216, turn])
        pred = np.zeros(len(y))
        for tr, te in LeaveOneGroupOut().split(X, y, groups=g):
            sc2 = StandardScaler()
            Xs = sc2.fit_transform(X[tr])
            yc = y[tr] - y[tr].mean()
            m = Ridge(50, fit_intercept=False).fit(Xs, yc)
            pred[te] = sc2.transform(X[te]) @ m.coef_
        pack = eval_scores(f"unsup_pca{k}_bge+turn", pred, anc, pairs)
        results.append(pack)
        # text only
        pred2 = np.zeros(len(y))
        for tr, te in LeaveOneGroupOut().split(P216, y, groups=g):
            sc2 = StandardScaler()
            Xs = sc2.fit_transform(P216[tr])
            yc = y[tr] - y[tr].mean()
            m = Ridge(50, fit_intercept=False).fit(Xs, yc)
            pred2[te] = sc2.transform(P216[te]) @ m.coef_
        results.append(eval_scores(f"unsup_pca{k}_bge", pred2, anc, pairs))
        json.dump(results, open(OUT / "unsup.json", "w"), indent=2)

    (OUT / "UNSUP.md").write_text(
        "# Unsupervised PCA on WildChat+study, LOPO on 216\n\n"
        + "\n".join(f"- {r['name']}: {r['spearman_U']} same-t {r.get('pairwise_same_timing')}" for r in results)
        + "\n"
    )
    print((OUT / "UNSUP.md").read_text())


if __name__ == "__main__":
    main()
