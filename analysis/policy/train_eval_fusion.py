#!/usr/bin/env python3
"""CPU follow-up: fuse cached embeddings with turn + fit.

Does not load GPUs. Reads emb_*.npy written by train_eval.py and the Gold
anchor. Reports whether text adds anything on top of the late-is-better rule.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
GOLD = HERE / "outputs" / "gold"
EXP = HERE / "outputs" / "experiments"


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    if ok.sum() < 3 or a[ok].std() == 0 or b[ok].std() == 0:
        return float("nan")
    return float(spearmanr(a[ok], b[ok]).statistic)


def lopo(X, y, groups):
    pred = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(X, y, groups=groups):
        sc = StandardScaler()
        pred[te] = Ridge(10.0).fit(sc.fit_transform(X[tr]), y[tr]).predict(sc.transform(X[te]))
    return pred


def task_cv(X, y, groups, folds=5):
    pred = np.zeros(len(y))
    for tr, te in GroupKFold(folds).split(X, y, groups=groups):
        sc = StandardScaler()
        pred[te] = Ridge(10.0).fit(sc.fit_transform(X[tr]), y[tr]).predict(sc.transform(X[te]))
    return pred


def main():
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    y = anc.ux_retention_resid.to_numpy(float)
    yb = anc.good_moment_human.to_numpy(int)
    g = anc.fold_participant.to_numpy()
    gt = anc.fold_task.to_numpy()
    z = np.column_stack([
        anc.ad_turn.clip(upper=8) / 8.0,
        pd.to_numeric(anc.fit_score, errors="coerce").fillna(0),
    ])
    rows = []
    for path in sorted(EXP.glob("emb_*.npy")):
        name = path.stem.replace("emb_", "")
        X = np.load(path)
        if X.shape[0] != len(anc):
            print("skip", path, X.shape)
            continue
        for tag, feat in {
            f"{name}_text": X,
            f"{name}_text+turn+fit": np.hstack([X, z]),
            "turn+fit_only": z,
        }.items():
            if tag == "turn+fit_only" and rows and any(r["name"] == tag for r in rows):
                continue
            pred = lopo(feat, y, g)
            pred_t = task_cv(feat, y, gt)
            rows.append({
                "name": tag,
                "spearman_U_lopo": round(spearman(pred, y), 4),
                "auroc_good_lopo": round(float(roc_auc_score(yb, pred)), 4),
                "spearman_U_task_grouped": round(spearman(pred_t, y), 4),
                "dim": int(feat.shape[1]),
            })
            print(rows[-1])
    (EXP / "fusion_results.json").write_text(json.dumps(rows, indent=2))
    print("wrote fusion_results.json", len(rows))


if __name__ == "__main__":
    main()
