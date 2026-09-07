#!/usr/bin/env python3
"""Hours-long modelling pass for the ad-moment score.

Fixes the previous pass
-----------------------
LOPO ridge *with intercept* anti-correlates the fold intercept with the
held-out person's mean U. On a weak two-level feature (early/late) that
makes Spearman look like −0.26 while the raw turn score is +0.17.
Learned probes were compared against the raw turn score — not a fair
fight. Here the serving score is ``X @ w`` (no intercept).

Data
----
* 216 advertised decision points (eval grain, always).
* All 1,080 primary user turns as extra training views (LOPO by person).
* 324 within-person preference pairs (RankNet).
* Prefix-valid features only (no future trajectory, no λ, no EEG).
* Cached frozen embeddings, plus bge on all 1,080 prefixes.

A model has to beat ``baseline_turn`` (Spearman 0.167) *or* beat chance
on same-timing pairs (turn cannot). Otherwise it is not useful.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "experiments" / "full"
OUT.mkdir(parents=True, exist_ok=True)
EXP = HERE / "outputs" / "experiments"
GOLD = HERE / "outputs" / "gold"
SEED = 13
BASELINE_TURN = 0.1669


def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    if ok.sum() < 3 or np.nanstd(a[ok]) == 0 or np.nanstd(b[ok]) == 0:
        return float("nan")
    return float(spearmanr(a[ok], b[ok]).statistic)


def auroc(y, s) -> float:
    y, s = np.asarray(y), np.asarray(s, float)
    m = ~(np.isnan(s) | np.isnan(y))
    if m.sum() < 4 or len(np.unique(y[m])) < 2:
        return float("nan")
    return float(roc_auc_score(y[m], s[m]))


def within_person_spearman(anc: pd.DataFrame, scores: np.ndarray) -> float:
    vals = []
    for _, g in anc.assign(_s=scores).groupby("participant_key"):
        if g._s.std() == 0 or g.ux_retention_resid.std() == 0 or len(g) < 3:
            continue
        vals.append(spearman(g._s, g.ux_retention_resid))
    return float(np.nanmean(vals)) if vals else float("nan")


def pairwise_breakdown(pairs: pd.DataFrame, score_by_conv: dict) -> dict:
    tot = same = cross = 0
    ok_tot = ok_same = ok_cross = 0
    for r in pairs.itertuples():
        a = score_by_conv.get(r.chosen_conversation_id)
        b = score_by_conv.get(r.rejected_conversation_id)
        if a is None or b is None or np.isnan(a) or np.isnan(b):
            continue
        tot += 1
        hit = int(a > b)
        ok_tot += hit
        if r.chosen_timing == r.rejected_timing:
            same += 1
            ok_same += hit
        else:
            cross += 1
            ok_cross += hit
    return {
        "pairwise": round(ok_tot / tot, 4) if tot else None,
        "pairwise_same_timing": round(ok_same / same, 4) if same else None,
        "pairwise_cross_timing": round(ok_cross / cross, 4) if cross else None,
        "n_pairs": tot, "n_same": same, "n_cross": cross,
    }


def late_minus_early(anc: pd.DataFrame, scores: np.ndarray) -> float:
    diffs = []
    tmp = anc.assign(_s=scores)
    for _, g in tmp.groupby("participant_key"):
        e, l = g[g.timing == "early"], g[g.timing == "late"]
        if len(e) and len(l):
            diffs.append(l._s.mean() - e._s.mean())
    return float(np.mean(np.array(diffs) > 0)) if diffs else float("nan")


def eval_scores(name: str, scores: np.ndarray, anc: pd.DataFrame, pairs: pd.DataFrame) -> dict:
    y = anc.ux_retention_resid.to_numpy(float)
    yb = anc.good_moment_human.to_numpy(int)
    pack = {
        "name": name,
        "spearman_U": round(spearman(scores, y), 4),
        "pearson_U": round(float(np.corrcoef(scores, y)[0, 1]), 4) if np.nanstd(scores) else None,
        "spearman_within": round(within_person_spearman(anc, scores), 4),
        "auroc_good": round(auroc(yb, scores), 4),
        "late_gt_early_rate": round(late_minus_early(anc, scores), 4),
        "beats_turn": bool(spearman(scores, y) > BASELINE_TURN + 1e-6),
    }
    pack.update(pairwise_breakdown(pairs, dict(zip(anc.conversation_id, scores))))
    print(json.dumps(pack), flush=True)
    return pack


# ---------------------------------------------------------------------------
# models (no intercept — serving score is a ranking)
# ---------------------------------------------------------------------------

def lopo_ridge(X, y, groups, alpha=50.0):
    pred = np.full(len(y), np.nan)
    logo = LeaveOneGroupOut()
    for tr, te in logo.split(X, y, groups=groups):
        sc = StandardScaler()
        Xs = sc.fit_transform(X[tr])
        yc = y[tr] - y[tr].mean()
        m = Ridge(alpha=alpha, fit_intercept=False)
        m.fit(Xs, yc)
        pred[te] = sc.transform(X[te]) @ m.coef_
    return pred


def lopo_enet(X, y, groups, alpha=0.1, l1=0.2):
    pred = np.full(len(y), np.nan)
    for tr, te in LeaveOneGroupOut().split(X, y, groups=groups):
        sc = StandardScaler()
        Xs = sc.fit_transform(X[tr])
        yc = y[tr] - y[tr].mean()
        m = ElasticNet(alpha=alpha, l1_ratio=l1, fit_intercept=False, max_iter=4000)
        m.fit(Xs, yc)
        pred[te] = sc.transform(X[te]) @ m.coef_
    return pred


def lopo_pls(X, y, groups, n=4):
    pred = np.full(len(y), np.nan)
    n = min(n, X.shape[1], max(2, len(np.unique(groups)) - 2))
    for tr, te in LeaveOneGroupOut().split(X, y, groups=groups):
        sc = StandardScaler()
        Xs = sc.fit_transform(X[tr])
        yc = y[tr] - y[tr].mean()
        k = min(n, Xs.shape[1], Xs.shape[0] - 1)
        m = PLSRegression(n_components=k, scale=False)
        m.fit(Xs, yc)
        pred[te] = m.predict(sc.transform(X[te])).ravel()
    return pred


def lopo_hgb(X, y, groups):
    """HGB has a built-in mean. Subtract train mean so scores rank."""
    pred = np.full(len(y), np.nan)
    for tr, te in LeaveOneGroupOut().split(X, y, groups=groups):
        m = HistGradientBoostingRegressor(
            max_depth=3, max_iter=80, min_samples_leaf=15,
            l2_regularization=1.0, random_state=SEED,
        )
        yc = y[tr] - y[tr].mean()
        m.fit(X[tr], yc)
        pred[te] = m.predict(X[te])
    return pred


def lopo_ridge_residual(X_struct, X_extra, y, groups, a_s=1.0, a_e=80.0):
    """score = struct @ w_s + extra @ w_e, w_e trained on residuals."""
    pred = np.full(len(y), np.nan)
    for tr, te in LeaveOneGroupOut().split(X_struct, y, groups=groups):
        sc_s, sc_e = StandardScaler(), StandardScaler()
        Ss = sc_s.fit_transform(X_struct[tr])
        Es = sc_e.fit_transform(X_extra[tr])
        yc = y[tr] - y[tr].mean()
        ws = Ridge(a_s, fit_intercept=False).fit(Ss, yc)
        resid = yc - Ss @ ws.coef_
        we = Ridge(a_e, fit_intercept=False).fit(Es, resid)
        pred[te] = sc_s.transform(X_struct[te]) @ ws.coef_ + sc_e.transform(X_extra[te]) @ we.coef_
    return pred


def lopo_ranknet(X, y, groups, pair_idx, alpha=20.0):
    """Pairwise: w from (x+ − x−) → +1, score = X @ w."""
    pred = np.full(len(y), np.nan)
    logo = LeaveOneGroupOut()
    # pair_idx: list of (i, j) meaning y[i] > y[j], same person
    for tr, te in logo.split(X, y, groups=groups):
        tr_set = set(tr.tolist())
        sc = StandardScaler()
        Xs = sc.fit_transform(X[tr])
        # map original index -> row in Xs
        pos = {int(i): k for k, i in enumerate(tr)}
        diffs, labels = [], []
        for i, j in pair_idx:
            if i in tr_set and j in tr_set:
                diffs.append(Xs[pos[i]] - Xs[pos[j]])
                labels.append(1.0)
                diffs.append(Xs[pos[j]] - Xs[pos[i]])
                labels.append(-1.0)
        if len(diffs) < 8:
            pred[te] = 0.0
            continue
        D, lab = np.asarray(diffs), np.asarray(labels)
        m = Ridge(alpha=alpha, fit_intercept=False).fit(D, lab)
        pred[te] = sc.transform(X[te]) @ m.coef_
    return pred


# ---------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------

def collect_ocean() -> pd.DataFrame:
    tracked = HERE.parents[1] / "src/project/logs/tracked"
    rows = {}
    for path in list(tracked.glob("lab/*/*_export.jsonl")) + list(tracked.glob("crowd/*/*_export.jsonl")):
        exp = None
        scores = None
        with path.open() as f:
            for line in f:
                rec = json.loads(line)
                exp = rec.get("experiment_id") or exp
                if rec.get("event") == "ocean_submitted":
                    scores = (rec.get("data") or {}).get("scores")
        if exp and scores:
            rows[exp] = {"experiment_id": exp, **{f"ocean_{k}": scores.get(k) for k in "EACNO"}}
    df = pd.DataFrame(rows.values())
    print("ocean people", len(df), flush=True)
    return df


def prefix_features(utt: pd.DataFrame) -> pd.DataFrame:
    """Running conversation stats using only turns ≤ current (serve-time valid)."""
    pcols = [c for c in utt.columns if c.startswith("p_")]
    recs = []
    for cid, g in utt.sort_values("turn").groupby("conversation_id", sort=False):
        genres, lats, js = [], [], []
        for r in g.itertuples():
            genres.append(getattr(r, "genre", None))
            lats.append(float(getattr(r, "latency_seconds", 0) or 0))
            js.append(float(getattr(r, "js_in", 0) or 0))
            n_shift = sum(a != b for a, b in zip(genres, genres[1:]))
            vc = pd.Series(genres).value_counts(normalize=True)
            ent = float(-(vc * np.log(vc + 1e-12)).sum())
            rec = {
                "conversation_id": cid,
                "turn": int(r.turn),
                "run_n_shift": n_shift,
                "run_entropy": ent,
                "run_n": len(genres),
                "run_mean_lat": float(np.mean(lats)),
                "run_last_js": js[-1],
                "run_mean_js": float(np.mean(js)),
            }
            for c in pcols:
                rec[c] = float(getattr(r, c, 0) or 0)
            recs.append(rec)
    return pd.DataFrame(recs)


def build() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    turns = pd.read_csv(HERE / "outputs/silver/turns.csv")
    prim = turns[turns.source_set == "primary"].copy()
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")

    ycols = [
        "ux_retention", "ux_retention_resid", "good_moment_human",
        "delta_credibility", "delta_trust", "delta_manipulation",
        "delta_helpfulness", "delta_relevance",
    ]
    ytab = anc[["conversation_id"] + [c for c in ycols if c in anc.columns]].copy()
    noad_ids = prim.loc[prim.condition == "no_ads", "conversation_id"].unique()
    noad = pd.DataFrame({"conversation_id": noad_ids})
    for c in ytab.columns:
        if c != "conversation_id":
            noad[c] = 0.0
    noad["good_moment_human"] = 0  # WAIT / not an insert
    ytab = pd.concat([ytab, noad], ignore_index=True)

    utt = pd.read_csv(HERE.parents[1] / "analysis/trajectories/outputs/utterances.csv")
    utt = utt[utt.genre_source == "utterance"].copy()
    pref = prefix_features(utt)

    df = prim.merge(ytab, on="conversation_id", how="left")
    df = df.merge(pref, on=["conversation_id", "turn"], how="left")
    ocean = collect_ocean()
    df = df.merge(ocean, on="experiment_id", how="left")

    df["turn_feat"] = df.turn.clip(upper=8) / 8.0
    df["log_len"] = np.log1p(pd.to_numeric(df.msg_len, errors="coerce").fillna(0))
    df["log_lat"] = np.log1p(pd.to_numeric(df.time_to_reply_ms, errors="coerce").fillna(0))
    df["fit"] = pd.to_numeric(df.fit_score, errors="coerce").fillna(0.0)
    df["p_purch"] = pd.to_numeric(df.p_purchasable, errors="coerce").fillna(0.0)
    for c in ["run_n_shift", "run_entropy", "run_n", "run_mean_lat", "run_last_js", "run_mean_js"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    for c in [c for c in df.columns if c.startswith("ocean_")]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(df[c].median())
    pcols = [c for c in df.columns if c.startswith("p_") and c != "p_purchasable"]
    for c in pcols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    df["genre"] = df.genre_utterance.fillna("unk")
    assert df.ux_retention_resid.notna().all()
    df.to_csv(OUT / "turns_labelled.csv", index=False)
    print("turns", df.shape, "ads", int((df.is_ad_turn == 1).sum()),
          "people", df.participant_key.nunique(), flush=True)
    return df, anc, pairs


def tab_matrix(df: pd.DataFrame, which: str) -> np.ndarray:
    cols = ["turn_feat", "log_len", "log_lat", "fit", "p_purch",
            "run_n_shift", "run_entropy", "run_mean_lat", "run_last_js"]
    pcols = [c for c in df.columns if c.startswith("p_") and c != "p_purchasable"]
    parts = [df[cols + pcols].to_numpy(float)]
    if "ocean" in which:
        ocols = [c for c in df.columns if c.startswith("ocean_")]
        parts.append(df[ocols].to_numpy(float))
    if "genreoh" in which:
        parts.append(pd.get_dummies(df.genre, prefix="g").to_numpy(float))
    return np.hstack(parts)


def embed_bge(texts: list[str], cache: Path) -> np.ndarray:
    if cache.exists():
        arr = np.load(cache)
        if arr.shape[0] == len(texts):
            print("bge cache", arr.shape, flush=True)
            return arr
    import torch
    from transformers import AutoModel, AutoTokenizer
    device = "cpu"
    tok = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")
    model = AutoModel.from_pretrained("BAAI/bge-small-en-v1.5").to(device).eval()
    outs = []
    with torch.no_grad():
        for i in range(0, len(texts), 16):
            enc = tok(list(texts[i:i + 16]), padding=True, truncation=True,
                      max_length=384, return_tensors="pt")
            enc = {k: v.to(device) for k, v in enc.items() if k in ("input_ids", "attention_mask")}
            h = model(**enc).last_hidden_state
            mask = enc["attention_mask"].unsqueeze(-1)
            vec = (h * mask).sum(1) / mask.sum(1).clamp(min=1)
            outs.append(torch.nn.functional.normalize(vec, dim=1).cpu().numpy())
            if i % 160 == 0:
                print(f"  bge {i}/{len(texts)}", flush=True)
    arr = np.concatenate(outs)
    np.save(cache, arr)
    print("bge wrote", arr.shape, flush=True)
    return arr


def pca_fit_apply(train, test, k) -> tuple[np.ndarray, np.ndarray]:
    k = min(k, train.shape[0] - 1, train.shape[1])
    sc = StandardScaler()
    pca = PCA(n_components=k, random_state=SEED)
    return pca.fit_transform(sc.fit_transform(train)), pca.transform(sc.transform(test))


def lopo_pca_ridge(E, y, groups, k=16, alpha=80.0, extra=None):
    pred = np.full(len(y), np.nan)
    for tr, te in LeaveOneGroupOut().split(E, y, groups=groups):
        Ptr, Pte = pca_fit_apply(E[tr], E[te], k)
        if extra is not None:
            Ptr = np.hstack([Ptr, extra[tr]])
            Pte = np.hstack([Pte, extra[te]])
        sc = StandardScaler()
        Xs = sc.fit_transform(Ptr)
        yc = y[tr] - y[tr].mean()
        m = Ridge(alpha=alpha, fit_intercept=False).fit(Xs, yc)
        pred[te] = sc.transform(Pte) @ m.coef_
    return pred


def pair_indices(anc: pd.DataFrame) -> list[tuple[int, int]]:
    id_to_i = {cid: i for i, cid in enumerate(anc.conversation_id)}
    out = []
    # rebuild from U so we don't depend on pair file alignment
    for _, g in anc.reset_index(drop=True).groupby("participant_key"):
        idx = g.index.to_numpy()
        yu = g.ux_retention_resid.to_numpy()
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                if yu[a] == yu[b]:
                    continue
                i, j = int(idx[a]), int(idx[b])
                if yu[a] > yu[b]:
                    out.append((i, j))
                else:
                    out.append((j, i))
    return out


def ads_view(df: pd.DataFrame, anc: pd.DataFrame) -> np.ndarray:
    """Boolean mask of df rows that are the 216 eval ad turns, in *anc* order."""
    key = df.conversation_id.astype(str) + "::" + df.turn.astype(str)
    want = anc.conversation_id.astype(str) + "::" + anc.ad_turn.astype(int).astype(str)
    pos = {k: i for i, k in enumerate(key)}
    idx = np.array([pos[w] for w in want])
    return idx


def dump(results: list[dict]):
    json.dump(results, open(OUT / "results.json", "w"), indent=2)
    rows = [r for r in results if "spearman_U" in r]
    rows = sorted(rows, key=lambda r: (-(r["spearman_U"] or -9), -(r.get("pairwise_same_timing") or 0)))
    lines = [
        "# Full modelling campaign (correct LOPO scores)",
        "",
        "Serving score is `X @ w` (no intercept). Eval = 216 ad conversations.",
        f"Beat `baseline_turn` Spearman **{BASELINE_TURN}** or same-timing pairwise > 0.5.",
        "",
        "| model | Spearman U | within | AUROC | pair | same-t | cross-t | beats turn |",
        "|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['name']} | {r.get('spearman_U','')} | {r.get('spearman_within','')} | "
            f"{r.get('auroc_good','')} | {r.get('pairwise','')} | {r.get('pairwise_same_timing','')} | "
            f"{r.get('pairwise_cross_timing','')} | {'YES' if r.get('beats_turn') else ''} |"
        )
    (OUT / "RESULTS.md").write_text("\n".join(lines) + "\n")
    (EXP / "RESULTS_FULL.md").write_text("\n".join(lines) + "\n")


def main():
    t0 = time.time()
    results: list[dict] = []
    df, anc, pairs = build()
    ad_idx = ads_view(df, anc)
    assert len(ad_idx) == len(anc), (len(ad_idx), len(anc))
    ads = df.iloc[ad_idx].reset_index(drop=True)
    assert list(ads.conversation_id) == list(anc.conversation_id)

    y216 = anc.ux_retention_resid.to_numpy(float)
    g216 = anc.participant_key.to_numpy()
    y1080 = df.ux_retention_resid.to_numpy(float)
    g1080 = df.participant_key.to_numpy()
    pidx = pair_indices(anc)

    # ---- baselines (raw scores, no fit) ----
    results.append(eval_scores("baseline_turn", ads.turn_feat.to_numpy(), anc, pairs))
    results.append(eval_scores("baseline_fit", ads.fit.to_numpy(), anc, pairs))
    results.append(eval_scores("baseline_turn_plus_fit",
                               ads.turn_feat.to_numpy() + ads.fit.to_numpy(), anc, pairs))
    results.append(eval_scores("baseline_purch", ads.p_purch.to_numpy(), anc, pairs))
    dump(results)

    # ---- 216-row tabular ----
    Xtab = tab_matrix(ads, "tab")
    Xtab_o = tab_matrix(ads, "tab+ocean")
    Xturn = ads[["turn_feat"]].to_numpy(float)
    print("Xtab", Xtab.shape, flush=True)

    for name, pred in [
        ("ridge_turn_only", lopo_ridge(Xturn, y216, g216, 1.0)),
        ("ridge_tab", lopo_ridge(Xtab, y216, g216, 50)),
        ("ridge_tab_a200", lopo_ridge(Xtab, y216, g216, 200)),
        ("ridge_tab_ocean", lopo_ridge(Xtab_o, y216, g216, 80)),
        ("enet_tab", lopo_enet(Xtab, y216, g216, 0.15, 0.3)),
        ("pls_tab", lopo_pls(Xtab, y216, g216, 4)),
        ("hgb_tab", lopo_hgb(Xtab, y216, g216)),
        ("ranknet_tab", lopo_ranknet(Xtab, y216, g216, pidx, 20)),
        ("ranknet_turn", lopo_ranknet(Xturn, y216, g216, pidx, 1)),
    ]:
        results.append(eval_scores(name, pred, anc, pairs))
        np.save(OUT / f"pred_{name}.npy", pred)
        dump(results)

    # residual: lock turn, add the rest
    extra = Xtab[:, 1:]  # drop turn_feat
    pred = lopo_ridge_residual(Xturn, extra, y216, g216, 1.0, 80.0)
    results.append(eval_scores("ridge_turn_plus_tab_resid", pred, anc, pairs))
    dump(results)

    # ---- cached 216 embeddings, PCA + turn (the missing model) ----
    z = np.column_stack([ads.turn_feat, ads.fit])
    for path in sorted(EXP.glob("emb_*.npy")):
        if "1080" in path.name:
            continue
        E = np.load(path)
        if E.shape[0] != 216:
            print("skip", path, E.shape, flush=True)
            continue
        tag = path.stem.replace("emb_", "")
        print("cached", tag, E.shape, flush=True)
        for k, a in [(8, 20), (16, 50), (32, 80)]:
            pred = lopo_pca_ridge(E, y216, g216, k=k, alpha=a)
            results.append(eval_scores(f"pca{k}_{tag}", pred, anc, pairs))
            pred = lopo_pca_ridge(E, y216, g216, k=k, alpha=a, extra=z)
            results.append(eval_scores(f"pca{k}_{tag}+turnfit", pred, anc, pairs))
        pred = lopo_ridge_residual(Xturn, E, y216, g216, 1.0, 200.0)
        results.append(eval_scores(f"turn_plus_resid_{tag}", pred, anc, pairs))
        dump(results)

    # ---- 1080-row training, eval on 216 ----
    print("embedding 1080 prefixes (bge, CPU)…", flush=True)
    E1080 = embed_bge(df.prefix_text.fillna("").tolist(), OUT / "emb_bge_1080.npy")
    Xtab1080 = tab_matrix(df, "tab")
    Xturn1080 = df[["turn_feat"]].to_numpy(float)

    def eval_from_1080(name, pred1080):
        pred = pred1080[ad_idx]
        results.append(eval_scores(name, pred, anc, pairs))
        np.save(OUT / f"pred_{name}.npy", pred)
        dump(results)

    eval_from_1080("ridge_tab_train1080", lopo_ridge(Xtab1080, y1080, g1080, 80))
    eval_from_1080("hgb_tab_train1080", lopo_hgb(Xtab1080, y1080, g1080))
    eval_from_1080("ridge_turn_plus_tab_resid_1080",
                   lopo_ridge_residual(Xturn1080, Xtab1080[:, 1:], y1080, g1080, 1.0, 80))

    # pre-ad + ad only (no post-ad rows)
    keep = ((df.is_ad_turn == 1) | (df.turn <= df.ad_turn.fillna(99)) | (df.condition == "no_ads")).to_numpy()
    # actually: keep turn <= ad_turn, and all no-ad
    keep = ((df.condition == "no_ads") | (df.turn <= df.ad_turn.fillna(4))).to_numpy()
    print("pre+ad+noad rows", keep.sum(), flush=True)

    def lopo_on_mask(X, y, groups, mask, kind="ridge"):
        pred_full = np.full(len(y), np.nan)
        Xm, ym, gm = X[mask], y[mask], groups[mask]
        if kind == "ridge":
            pm = lopo_ridge(Xm, ym, gm, 80)
        else:
            pm = lopo_hgb(Xm, ym, gm)
        pred_full[np.where(mask)[0]] = pm
        return pred_full

    eval_from_1080("ridge_tab_pread", lopo_on_mask(Xtab1080, y1080, g1080, keep, "ridge"))
    eval_from_1080("hgb_tab_pread", lopo_on_mask(Xtab1080, y1080, g1080, keep, "hgb"))

    pred = lopo_pca_ridge(E1080, y1080, g1080, k=16, alpha=80, extra=Xturn1080)
    eval_from_1080("pca16_bge1080+turn", pred)

    # ad-turns + no-ad only (clean: labelled inserts and WAIT=0)
    keep2 = ((df.is_ad_turn == 1) | (df.condition == "no_ads")).to_numpy()
    print("ad+noad rows", keep2.sum(), flush=True)
    eval_from_1080("ridge_tab_ad_noad", lopo_on_mask(Xtab1080, y1080, g1080, keep2, "ridge"))
    eval_from_1080("hgb_tab_ad_noad", lopo_on_mask(Xtab1080, y1080, g1080, keep2, "hgb"))

    # ---- multi-task on 216: average of 3 delta heads ----
    print("multitask deltas", flush=True)
    heads = []
    for col in ["delta_credibility", "delta_trust", "delta_manipulation"]:
        yh = ads[col].to_numpy(float)
        heads.append(lopo_ridge(Xtab, yh, g216, 50))
    uhat = (heads[0] + heads[1] - heads[2]) / 3.0
    results.append(eval_scores("multitask_3delta_tab", uhat, anc, pairs))
    dump(results)

    # ---- stack: turn + best complementary OOF (simple average of z-scores) ----
    # reload preds we already have
    turn_s = ads.turn_feat.to_numpy()
    for extra_name in ["ridge_tab", "pca16_qwen3-8b+turnfit", "ranknet_tab", "hgb_tab"]:
        p = OUT / f"pred_{extra_name}.npy"
        if not p.exists():
            continue
        extra_s = np.load(p)
        # z-score each, then 0.7 turn + 0.3 extra (turn is the known effect)
        def z(x):
            x = np.asarray(x, float)
            return (x - np.nanmean(x)) / (np.nanstd(x) + 1e-8)
        blend = 0.7 * z(turn_s) + 0.3 * z(extra_s)
        results.append(eval_scores(f"blend70_turn_{extra_name}", blend, anc, pairs))
    dump(results)

    # pick up GPU embeddings if the other job finished
    for path in sorted(OUT.glob("emb_qwen*.npy")) + sorted(EXP.glob("emb_qwen3-emb*.npy")):
        E = np.load(path)
        print("found gpu emb", path, E.shape, flush=True)
        if E.shape[0] == 216:
            for k, a in [(16, 50), (32, 80)]:
                pred = lopo_pca_ridge(E, y216, g216, k=k, alpha=a, extra=z)
                results.append(eval_scores(f"pca{k}_{path.stem}+turnfit", pred, anc, pairs))
        elif E.shape[0] == 1080:
            pred = lopo_pca_ridge(E, y1080, g1080, k=16, alpha=80, extra=Xturn1080)
            eval_from_1080(f"pca16_{path.stem}+turn", pred)

    dump(results)
    print(f"done in {(time.time()-t0)/60:.1f} min", flush=True)
    print((OUT / "RESULTS.md").read_text())


if __name__ == "__main__":
    main()
