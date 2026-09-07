#!/usr/bin/env python3
"""Greedy add features on top of the locked BEST residual (14B PCA4 + latency).

Dumping 54 columns drowned the 0.274 model. Add one serve-time feature at a
time; keep it only if LOPO Spearman and same-timing both do not drop.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

from features_behaviour import OUT, build_ads_frame
from train_campaign import GOLD, eval_scores

HERE = Path(__file__).resolve().parent
E14 = HERE / "outputs/experiments/emb_qwen3-14b.npy"
MIX = 0.15
K = 4


def oof(E, extra, y, g, turn, k=K, a=10.0):
    pred = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
        resid = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
        resid = resid - resid.mean()
        scE = StandardScaler()
        pca = PCA(k, random_state=13)
        P = pca.fit_transform(scE.fit_transform(E[tr]))
        Pte = pca.transform(scE.transform(E[te]))
        Xtr = np.hstack([P, extra[tr]])
        Xte = np.hstack([Pte, extra[te]])
        sc = StandardScaler()
        m = Ridge(a, fit_intercept=False).fit(sc.fit_transform(Xtr), resid)
        pred[te] = sc.transform(Xte) @ m.coef_
    return pred


def score_of(turn, resid, mix=MIX):
    z = (resid - resid.mean()) / (resid.std() + 1e-8)
    return turn.ravel() + mix * z


def main():
    ads = build_ads_frame()
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    y = ads.ux_retention_resid.to_numpy(float)
    g = ads.participant_key.to_numpy()
    turn = ads[["turn_feat"]].to_numpy(float)
    E = np.load(E14)
    candidates = [
        "log_lat", "lex_q_start", "lex_ttr", "lex_hedge", "lex_ready",
        "lex_product", "lex_qmark", "run_len_slope", "lat_vs_run",
        "ocean_O", "ocean_N", "mnli_0", "mnli_1", "mnli_6",
        "fit", "log_len",
    ]
    candidates = [c for c in candidates if c in ads.columns]

    results = []
    # baseline: lat only + 14B (current BEST)
    extra = ads[["log_lat"]].to_numpy(float)
    resid = oof(E, extra, y, g, turn)
    pack = eval_scores("step_lat", score_of(turn, resid), anc, pairs)
    results.append(pack)
    chosen = ["log_lat"]
    best_sp, best_st = pack["spearman_U"], pack.get("pairwise_same_timing") or 0
    print("start", pack, flush=True)

    improved = True
    while improved:
        improved = False
        trial_best = None
        for c in candidates:
            if c in chosen:
                continue
            extra = ads[chosen + [c]].to_numpy(float)
            resid = oof(E, extra, y, g, turn)
            pack = eval_scores(f"step_{'+'.join(chosen+[c])}", score_of(turn, resid), anc, pairs)
            results.append(pack)
            sp, st = pack["spearman_U"], pack.get("pairwise_same_timing") or 0
            # accept if Spearman up and same-t does not collapse
            if sp > best_sp + 0.005 and st >= best_st - 0.02:
                if trial_best is None or sp > trial_best["spearman_U"]:
                    trial_best = pack
                    trial_best["_feat"] = c
        if trial_best:
            chosen.append(trial_best["_feat"])
            best_sp = trial_best["spearman_U"]
            best_st = trial_best.get("pairwise_same_timing") or 0
            improved = True
            print("keep", chosen, best_sp, best_st, flush=True)
        json.dump(
            [{k: v for k, v in r.items() if not str(k).startswith("_")} for r in results],
            open(OUT / "stepwise.json", "w"), indent=2,
        )

    (OUT / "STEPWISE.md").write_text(
        "# Stepwise residual on top of 14B+turn\n\n"
        f"Chosen: {chosen}\n\n"
        + "\n".join(
            f"- {r['name']}: {r['spearman_U']} same-t {r.get('pairwise_same_timing')}"
            for r in sorted(results, key=lambda x: -(x['spearman_U'] or -9))[:20]
        )
        + "\n"
    )
    print((OUT / "STEPWISE.md").read_text())
    if best_sp > 0.2737 and best_st >= 0.60:
        print("NEW BEST", chosen, best_sp, best_st)


if __name__ == "__main__":
    main()
