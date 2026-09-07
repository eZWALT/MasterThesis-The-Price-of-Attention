#!/usr/bin/env python3
"""Pairwise RankNet / RankSVM on the locked 14B residual features.

Same-timing pairs are the only place turn cannot help. Fit w on
X_chosen - X_rejected, then score = turn/8 + mix * z(X @ w).
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

from features_behaviour import OUT, build_ads_frame
from train_campaign import GOLD, eval_scores

E14 = __import__("pathlib").Path(__file__).resolve().parent / "outputs/experiments/emb_qwen3-14b.npy"
MIX, K, ALPHA = 0.15, 4, 10.0
SEED = 13


def feat_oof_parts(E, extra, y, g, turn):
    """Per-row standardized [PCA4, extra] under LOPO, plus MSE residual scores."""
    n, p = extra.shape
    Z = np.zeros((len(y), K + p))
    mse = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
        r = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
        r = r - r.mean()
        scE = StandardScaler()
        pca = PCA(K, random_state=SEED)
        P = pca.fit_transform(scE.fit_transform(E[tr]))
        Pte = pca.transform(scE.transform(E[te]))
        sc = StandardScaler()
        Xtr = sc.fit_transform(np.hstack([P, extra[tr]]))
        Xte = sc.transform(np.hstack([Pte, extra[te]]))
        Z[te] = Xte
        w = Ridge(ALPHA, fit_intercept=False).fit(Xtr, r).coef_
        mse[te] = Xte @ w
    return Z, mse


def pair_index(pairs, cid_to_i, train_cids, same_only=False):
    rows = []
    for r in pairs.itertuples():
        if same_only and r.chosen_timing != r.rejected_timing:
            continue
        a, b = r.chosen_conversation_id, r.rejected_conversation_id
        if a not in cid_to_i or b not in cid_to_i:
            continue
        if a not in train_cids or b not in train_cids:
            continue
        rows.append((cid_to_i[a], cid_to_i[b]))
    return rows


def oof_rank(Z, g, pairs, cids, kind="logreg", same_only=False, C=1.0):
    cid_to_i = {c: i for i, c in enumerate(cids)}
    pred = np.zeros(len(Z))
    for tr, te in LeaveOneGroupOut().split(Z, groups=g):
        train_cids = set(cids[i] for i in tr)
        ix = pair_index(pairs, cid_to_i, train_cids, same_only=same_only)
        if len(ix) < 8:
            pred[te] = 0
            continue
        D = np.vstack([Z[i] - Z[j] for i, j in ix])
        # both directions for logistic
        X = np.vstack([D, -D])
        yb = np.concatenate([np.ones(len(D)), np.zeros(len(D))])
        if kind == "logreg":
            m = LogisticRegression(C=C, penalty="l2", solver="lbfgs", max_iter=400)
            m.fit(X, yb)
            w = m.coef_.ravel()
        elif kind == "svc":
            m = LinearSVC(C=C, dual="auto", max_iter=4000, random_state=SEED)
            m.fit(X, yb)
            w = m.coef_.ravel()
        elif kind == "ridge":
            m = Ridge(1.0 / C, fit_intercept=False).fit(D, np.ones(len(D)))
            w = m.coef_.ravel()
        else:
            raise ValueError(kind)
        pred[te] = Z[te] @ w
    return pred


def blend(turn, resid, mix=MIX):
    z = (resid - resid.mean()) / (resid.std() + 1e-8)
    return turn.ravel() + mix * z


def main():
    ads = build_ads_frame()
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    y = ads.ux_retention_resid.to_numpy(float)
    g = ads.participant_key.to_numpy()
    turn = ads[["turn_feat"]].to_numpy(float)
    cids = ads.conversation_id.to_numpy()
    E = np.load(E14)
    extra = ads[["log_lat", "ocean_O", "lex_q_start"]].to_numpy(float)
    Z, mse = feat_oof_parts(E, extra, y, g, turn)

    results = []

    def rec(name, s):
        pack = eval_scores(name, s, anc, pairs)
        results.append(pack)
        print(name, pack["spearman_U"], "same-t", pack.get("pairwise_same_timing"),
              "within", pack.get("spearman_within"), flush=True)

    rec("mse_ridge_m0.15", blend(turn, mse))
    for kind in ("logreg", "svc", "ridge"):
        for same in (False, True):
            for C in (0.2, 1.0, 5.0):
                tag = f"rank_{kind}_{'same' if same else 'all'}_C{C:g}"
                pred = oof_rank(Z, g, pairs, cids, kind=kind, same_only=same, C=C)
                rec(f"{tag}_raw", pred)
                rec(f"{tag}_m0.15", blend(turn, pred, 0.15))
                rec(f"{tag}_m0.25", blend(turn, pred, 0.25))

    # ensemble: z(mse) + z(rank_same)
    pred_same = oof_rank(Z, g, pairs, cids, kind="logreg", same_only=True, C=1.0)
    pred_all = oof_rank(Z, g, pairs, cids, kind="logreg", same_only=False, C=1.0)
    for a, b in ((0.7, 0.3), (0.5, 0.5), (0.3, 0.7)):
        ens = a * (mse / (mse.std() + 1e-8)) + b * (pred_same / (pred_same.std() + 1e-8))
        rec(f"ens_mse{a:g}_same{b:g}_m0.15", blend(turn, ens, 0.15))
        ens2 = a * (mse / (mse.std() + 1e-8)) + b * (pred_all / (pred_all.std() + 1e-8))
        rec(f"ens_mse{a:g}_all{b:g}_m0.15", blend(turn, ens2, 0.15))

    json.dump(results, open(OUT / "rank.json", "w"), indent=2)
    rows = [r for r in results if "spearman_U" in r]
    rows.sort(key=lambda r: (-(r.get("pairwise_same_timing") or 0), -(r["spearman_U"] or -9)))
    lines = [
        "# Pairwise RankNet on 14B residual features",
        "",
        "| model | Spearman | same-t | pair | within | AUROC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in rows[:30]:
        lines.append(
            f"| {r['name']} | {r['spearman_U']} | {r.get('pairwise_same_timing')} | "
            f"{r.get('pairwise')} | {r.get('spearman_within')} | {r.get('auroc_good')} |"
        )
    (OUT / "RANK.md").write_text("\n".join(lines) + "\n")
    print((OUT / "RANK.md").read_text())


if __name__ == "__main__":
    main()
