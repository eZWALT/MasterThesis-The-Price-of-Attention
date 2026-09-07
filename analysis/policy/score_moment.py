#!/usr/bin/env python3
"""Serve the locked ad-moment score.

score = (turn/8) + 0.15 * z( Ridge(PCA4(Qwen3-14B last-token), log1p(latency_ms)) )

Needs a 5120-d last-token vector (same procedure as train_eval.py
qwen3-14b) plus turn and latency_ms. No presentation/lambda.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ART = HERE / "outputs" / "experiments" / "full" / "scorer_BEST_fixedturn_14b_lat.npz"


def score(
    emb_last: np.ndarray,
    turn: int,
    latency_ms: float,
    ocean_O: float = 0.0,
    lex_q_start: float = 0.0,
) -> np.ndarray:
    """emb_last: (n, 5120) or (5120,). Higher = better moment.

    Extra columns follow ``extra_cols`` in the npz (log_lat, optionally
    ocean_O, lex_q_start).
    """
    z = np.load(ART)
    x = np.atleast_2d(np.asarray(emb_last, dtype=np.float64))
    n = x.shape[0]
    xs = (x - z["emb_mean"]) / z["emb_scale"]
    P = (xs - z["pca_mean"]) @ z["pca_components"].T
    lat = np.log1p(np.asarray(latency_ms, dtype=np.float64)).reshape(-1, 1)
    if lat.shape[0] == 1 and n > 1:
        lat = np.repeat(lat, n, axis=0)
    extras = {"log_lat": lat.ravel()}
    extras["ocean_O"] = np.full(n, float(np.asarray(ocean_O).reshape(-1)[0]))
    extras["lex_q_start"] = np.full(n, float(np.asarray(lex_q_start).reshape(-1)[0]))
    cols = [str(c) for c in z["extra_cols"]] if "extra_cols" in z.files else ["log_lat"]
    extra = np.column_stack([
        extras[c] if c != "log_lat" else lat.ravel() for c in cols
    ])
    feat = np.hstack([P, extra])
    feat = (feat - z["feat_mean"]) / z["feat_scale"]
    resid = feat @ z["w"]
    mix = float(z["mix"])
    turn_s = np.clip(np.asarray(turn, dtype=np.float64).reshape(-1), 1, 8) / 8.0
    if turn_s.size == 1 and n > 1:
        turn_s = np.repeat(turn_s, n)
    resid = (resid - resid.mean()) / (resid.std() + 1e-8) if len(resid) > 1 else resid
    return turn_s + mix * resid


if __name__ == "__main__":
    print("loaded", ART, "mix", float(np.load(ART)["mix"]))
