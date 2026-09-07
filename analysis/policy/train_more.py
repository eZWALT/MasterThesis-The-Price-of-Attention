#!/usr/bin/env python3
"""1080-prefix PCA, per-timing residuals, multi-output Likert stack."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

from features_behaviour import OUT, build_ads_frame
from train_campaign import GOLD, ads_view, eval_scores

HERE = Path(__file__).resolve().parent
E14 = HERE / "outputs/experiments/emb_qwen3-14b.npy"
E1080 = HERE / "outputs/experiments/full/emb_qwen3-14b_last_1080.npy"
TL = HERE / "outputs/experiments/full/turns_labelled.csv"
MIX, K, ALPHA = 0.15, 4, 10.0
SEED = 13


def blend(turn, resid, mix=MIX):
    z = (resid - resid.mean()) / (resid.std() + 1e-8)
    return turn.ravel() + mix * z


def main():
    ads = build_ads_frame()
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    prim = pd.read_csv(HERE / "outputs/silver/turns.csv")
    prim = prim[prim.source_set == "primary"].copy()
    y = ads.ux_retention_resid.to_numpy(float)
    g = ads.participant_key.to_numpy()
    turn = ads[["turn_feat"]].to_numpy(float)
    timing = ads.timing.to_numpy()
    extra = ads[["log_lat", "ocean_O", "lex_q_start"]].to_numpy(float)
    E = np.load(E14)
    results = []

    def rec(name, s):
        pack = eval_scores(name, s, anc, pairs)
        results.append(pack)
        print(name, pack["spearman_U"], "same-t", pack.get("pairwise_same_timing"),
              "within", pack.get("spearman_within"), flush=True)

    # baseline
    def oof_std(Euse, extra_m, k=K, alpha=ALPHA):
        pred = np.zeros(len(y))
        for tr, te in LeaveOneGroupOut().split(Euse, y, groups=g):
            r = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
            r = r - r.mean()
            scE = StandardScaler()
            pca = PCA(k, random_state=SEED)
            P = pca.fit_transform(scE.fit_transform(Euse[tr]))
            Pte = pca.transform(scE.transform(Euse[te]))
            sc = StandardScaler()
            Xtr = sc.fit_transform(np.hstack([P, extra_m[tr]]))
            Xte = sc.transform(np.hstack([Pte, extra_m[te]]))
            w = Ridge(alpha, fit_intercept=False).fit(Xtr, r).coef_
            pred[te] = Xte @ w
        return pred

    rec("base_same_t", blend(turn, oof_std(E, extra)))

    # --- PCA on all 1080 prefixes of train people ---
    tl = pd.read_csv(TL)
    Eall = np.load(E1080)
    assert len(tl) == len(Eall)
    g_all = tl.participant_key.to_numpy()
    # ads rows in 1080 table
    idx216 = ads_view(tl, anc)
    pred = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
        hold = set(g[te])
        tr_all = np.array([p not in hold for p in g_all])
        r = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
        r = r - r.mean()
        scE = StandardScaler()
        pca = PCA(K, random_state=SEED)
        pca.fit(scE.fit_transform(Eall[tr_all]))
        P = pca.transform(scE.transform(E[tr]))
        Pte = pca.transform(scE.transform(E[te]))
        sc = StandardScaler()
        Xtr = sc.fit_transform(np.hstack([P, extra[tr]]))
        Xte = sc.transform(np.hstack([Pte, extra[te]]))
        w = Ridge(ALPHA, fit_intercept=False).fit(Xtr, r).coef_
        pred[te] = Xte @ w
    rec("pca1080_same_t", blend(turn, pred))
    rec("pca1080_same_t_m0.25", blend(turn, pred, 0.25))

    # k=8 on 1080 PCA
    pred = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
        hold = set(g[te])
        tr_all = np.array([p not in hold for p in g_all])
        r = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
        r = r - r.mean()
        scE = StandardScaler()
        pca = PCA(8, random_state=SEED)
        pca.fit(scE.fit_transform(Eall[tr_all]))
        P = pca.transform(scE.transform(E[tr]))
        Pte = pca.transform(scE.transform(E[te]))
        sc = StandardScaler()
        Xtr = sc.fit_transform(np.hstack([P, extra[tr]]))
        Xte = sc.transform(np.hstack([Pte, extra[te]]))
        w = Ridge(30.0, fit_intercept=False).fit(Xtr, r).coef_
        pred[te] = Xte @ w
    rec("pca1080_k8_a30", blend(turn, pred))

    # --- per-timing residual ---
    pred = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
        for tname in ("early", "late"):
            tr_t = tr[timing[tr] == tname]
            te_t = te[timing[te] == tname]
            if len(tr_t) < 12 or len(te_t) == 0:
                continue
            # residual after a constant (turn is fixed within timing)
            r = y[tr_t] - y[tr_t].mean()
            scE = StandardScaler()
            pca = PCA(min(K, len(tr_t) - 2), random_state=SEED)
            P = pca.fit_transform(scE.fit_transform(E[tr_t]))
            Pte = pca.transform(scE.transform(E[te_t]))
            sc = StandardScaler()
            Xtr = sc.fit_transform(np.hstack([P, extra[tr_t]]))
            Xte = sc.transform(np.hstack([Pte, extra[te_t]]))
            w = Ridge(ALPHA, fit_intercept=False).fit(Xtr, r).coef_
            pred[te_t] = Xte @ w
    rec("per_timing_raw", pred)
    rec("per_timing_m0.15", blend(turn, pred))

    # --- PLS ---
    pred = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
        r = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
        r = r - r.mean()
        scE = StandardScaler()
        Ztr = np.hstack([scE.fit_transform(E[tr]), extra[tr]])
        Zte = np.hstack([scE.transform(E[te]), extra[te]])
        sc = StandardScaler()
        pls = PLSRegression(n_components=4)
        pls.fit(sc.fit_transform(Ztr), r)
        pred[te] = pls.predict(sc.transform(Zte)).ravel()
    rec("pls4_m0.15", blend(turn, pred))

    # --- multi-output stack (nested-ish: first OOF heads, then combo on U) ---
    ycols = [
        "ux_retention_resid", "delta_credibility", "delta_trust",
        "delta_helpfulness", "delta_relevance",
    ]
    Y = ads[ycols].to_numpy(float)
    Y[:, ycols.index("delta_trust")]  # keep
    if "delta_manipulation" in ads.columns:
        Y = np.column_stack([Y, -ads.delta_manipulation.to_numpy(float)])
    heads = np.zeros((len(y), Y.shape[1]))
    for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
        scE = StandardScaler()
        pca = PCA(K, random_state=SEED)
        P = pca.fit_transform(scE.fit_transform(E[tr]))
        Pte = pca.transform(scE.transform(E[te]))
        sc = StandardScaler()
        Xtr = sc.fit_transform(np.hstack([P, extra[tr]]))
        Xte = sc.transform(np.hstack([Pte, extra[te]]))
        for j in range(Y.shape[1]):
            yj = Y[tr, j]
            r = yj - LinearRegression().fit(turn[tr], yj).predict(turn[tr])
            w = Ridge(ALPHA, fit_intercept=False).fit(Xtr, r - r.mean()).coef_
            heads[te, j] = Xte @ w
    # second stage: LOPO ridge heads → U residual
    pred = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(heads, y, groups=g):
        r = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
        sc = StandardScaler()
        w = Ridge(1.0, fit_intercept=False).fit(sc.fit_transform(heads[tr]), r - r.mean()).coef_
        pred[te] = sc.transform(heads[te]) @ w
    rec("stack_likert_m0.15", blend(turn, pred))
    rec("stack_Uhead_m0.15", blend(turn, heads[:, 0]))

    # Neuroticism recipe at mix 0.15 (best same-t earlier)
    extra_n = ads[["log_lat", "ocean_N"]].to_numpy(float)
    rec("lat_N_m0.15", blend(turn, oof_std(E, extra_n)))
    extra_on = ads[["log_lat", "ocean_O", "ocean_N", "lex_q_start"]].to_numpy(float)
    rec("lat_ON_q_m0.15", blend(turn, oof_std(E, extra_on)))

    json.dump(results, open(OUT / "more.json", "w"), indent=2)
    rows = sorted(results, key=lambda r: (-(r["spearman_U"] or -9), -(r.get("pairwise_same_timing") or 0)))
    lines = [
        "# 1080-PCA / per-timing / Likert stack",
        "",
        "| model | Spearman | same-t | pair | within | AUROC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['name']} | {r['spearman_U']} | {r.get('pairwise_same_timing')} | "
            f"{r.get('pairwise')} | {r.get('spearman_within')} | {r.get('auroc_good')} |"
        )
    (OUT / "MORE.md").write_text("\n".join(lines) + "\n")
    print((OUT / "MORE.md").read_text())


if __name__ == "__main__":
    main()
