#!/usr/bin/env python3
"""Zero-shot cross-encoder / reranker features on the prefix (CPU).

Not a fine-tune. Score a handful of 'good moment' hypotheses and add
them one at a time to the locked same_t residual.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from features_behaviour import OUT, build_ads_frame
from train_campaign import GOLD, eval_scores

HERE = Path(__file__).resolve().parent
E14 = HERE / "outputs/experiments/emb_qwen3-14b.npy"
CACHE = OUT / "feat_zshot_216.npy"
MIX, K, ALPHA = 0.15, 4, 10.0
SEED = 13

HYPS = [
    "This is a natural moment to mention a relevant product.",
    "The user is ready for a concrete product recommendation.",
    "The user is asking a specific product or brand question.",
    "An advertisement would feel helpful in this conversation.",
    "An advertisement would feel intrusive in this conversation.",
    "The user is still only exploring and not ready to buy.",
    "The assistant just gave a complete answer and the topic is wrapping up.",
]


def score_pairs(hub, texts, hyps, max_len=256, batch=8):
    tok = AutoTokenizer.from_pretrained(hub)
    model = AutoModelForSequenceClassification.from_pretrained(hub)
    model.eval()
    device = torch.device("cpu")
    model.to(device)
    out = np.zeros((len(texts), len(hyps)), dtype=np.float32)
    with torch.no_grad():
        for j, hyp in enumerate(hyps):
            for i in range(0, len(texts), batch):
                batch_t = [str(t)[:1500] for t in texts[i:i + batch]]
                enc = tok(
                    [hyp] * len(batch_t), batch_t,
                    padding=True, truncation=True, max_length=max_len,
                    return_tensors="pt",
                )
                enc = {k: v.to(device) for k, v in enc.items()}
                logits = model(**enc).logits
                if logits.shape[-1] == 1:
                    s = logits.squeeze(-1)
                else:
                    # MNLI-style: take entailment if 3-way, else last dim
                    s = logits[:, -1]
                out[i:i + len(batch_t), j] = s.cpu().numpy()
            print(f"  {hub.split('/')[-1]} hyp {j+1}/{len(hyps)}", flush=True)
    del model
    return out


def oof(E, extra, y, g, turn):
    pred = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
        r = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
        scE = StandardScaler()
        pca = PCA(K, random_state=SEED)
        P = pca.fit_transform(scE.fit_transform(E[tr]))
        Pte = pca.transform(scE.transform(E[te]))
        sc = StandardScaler()
        Xtr = sc.fit_transform(np.hstack([P, extra[tr]]))
        Xte = sc.transform(np.hstack([Pte, extra[te]]))
        w = Ridge(ALPHA, fit_intercept=False).fit(Xtr, r - r.mean()).coef_
        pred[te] = Xte @ w
    z = (pred - pred.mean()) / (pred.std() + 1e-8)
    return turn.ravel() + MIX * z, pred


def main():
    ads = build_ads_frame()
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    y = ads.ux_retention_resid.to_numpy(float)
    g = ads.participant_key.to_numpy()
    turn = ads[["turn_feat"]].to_numpy(float)
    E = np.load(E14)
    texts = ads.prefix_text.fillna("").tolist()

    hubs = [
        ("mini", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
        ("bge", "BAAI/bge-reranker-v2-m3"),
    ]
    blocks = []
    names = []
    if CACHE.exists():
        Z = np.load(CACHE)
        print("loaded cache", Z.shape, flush=True)
        if Z.shape[0] != 216:
            Z = None
        else:
            # names reconstructed
            for tag, _ in hubs:
                for j, _ in enumerate(HYPS):
                    names.append(f"zs_{tag}_{j}")
            if Z.shape[1] != len(names):
                Z = None
    else:
        Z = None
    if Z is None:
        chunks = []
        names = []
        for tag, hub in hubs:
            print("====", hub, flush=True)
            arr = score_pairs(hub, texts, HYPS)
            chunks.append(arr)
            for j, _ in enumerate(HYPS):
                names.append(f"zs_{tag}_{j}")
        Z = np.hstack(chunks)
        np.save(CACHE, Z)
        print("saved", CACHE, Z.shape, flush=True)

    for j, n in enumerate(names):
        ads[n] = Z[:, j]
    # also mean / max per encoder
    n_h = len(HYPS)
    ads["zs_mini_mean"] = Z[:, :n_h].mean(1)
    ads["zs_bge_mean"] = Z[:, n_h:].mean(1) if Z.shape[1] >= 2 * n_h else Z.mean(1)
    ads["zs_mini_help"] = Z[:, 3] - Z[:, 4]  # helpful minus intrusive
    if Z.shape[1] >= 2 * n_h:
        ads["zs_bge_help"] = Z[:, n_h + 3] - Z[:, n_h + 4]
    names = names + [c for c in ("zs_mini_mean", "zs_bge_mean", "zs_mini_help", "zs_bge_help") if c in ads.columns]

    results = []
    extra0 = ads[["log_lat", "ocean_O", "lex_q_start"]].to_numpy(float)
    s, _ = oof(E, extra0, y, g, turn)
    pack = eval_scores("base_same_t", s, anc, pairs)
    results.append(pack)
    print("base", pack["spearman_U"], pack.get("pairwise_same_timing"), flush=True)
    best_sp, best_st = pack["spearman_U"], pack.get("pairwise_same_timing") or 0
    chosen = ["log_lat", "ocean_O", "lex_q_start"]

    # univariate residual corr
    from scipy.stats import spearmanr
    rU = y - LinearRegression().fit(turn, y).predict(turn)
    print("univariate residual Spearman:", flush=True)
    for n in names:
        print(f"  {n:20s} {spearmanr(ads[n], rU).statistic:+.3f}", flush=True)

    improved = True
    while improved:
        improved = False
        trial = None
        for c in names:
            if c in chosen:
                continue
            extra = ads[chosen + [c]].to_numpy(float)
            s, _ = oof(E, extra, y, g, turn)
            pack = eval_scores("add_" + c, s, anc, pairs)
            results.append(pack)
            sp, st = pack["spearman_U"], pack.get("pairwise_same_timing") or 0
            if sp >= best_sp - 0.002 and st >= best_st - 0.01 and (sp > best_sp or st > best_st + 0.005):
                if trial is None or (sp, st) > trial[0]:
                    trial = ((sp, st), c, pack)
        if trial:
            _, c, pack = trial
            chosen.append(c)
            best_sp, best_st = pack["spearman_U"], pack.get("pairwise_same_timing") or 0
            print("KEEP", chosen, best_sp, best_st, flush=True)
            improved = True

    json.dump(results, open(OUT / "zshot.json", "w"), indent=2)
    rows = [r for r in results if "spearman_U" in r]
    rows.sort(key=lambda r: (-(r["spearman_U"] or -9), -(r.get("pairwise_same_timing") or 0)))
    lines = [
        "# Zero-shot reranker features",
        "",
        f"Chosen: {chosen}  {best_sp} / {best_st}",
        "",
        "| model | Spearman | same-t | pair | within | AUROC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in rows[:25]:
        lines.append(
            f"| {r['name']} | {r['spearman_U']} | {r.get('pairwise_same_timing')} | "
            f"{r.get('pairwise')} | {r.get('spearman_within')} | {r.get('auroc_good')} |"
        )
    (OUT / "ZSHOT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "ZSHOT.md").read_text())


if __name__ == "__main__":
    main()
