"""Block 0. How reliable are the things we are correlating, and what
can 18 or 54 people resolve?

The cross-modal families correlate person-level scores. If those
scores are noisy, the largest correlation that can ever be observed is
sqrt(rel_X * rel_Y). Nobody has measured rel for the EEG condition
features or their D_i, so this script does:

1. Rebuild the confirmatory Dataset A k=37 cells (same tile selection
   as analysis/eeg/statistics/run_equal_n_dataset_a.py, no Gold
   rewrite), keep the selected tiles, split them in two, median each
   half. Two splits:
     odd_even     alternate tiles in time  (upper bound; adjacent tiles
                  are autocorrelated)
     first_second earlier vs later half     (lower bound; confounded
                  with drift)
   Reliability of a condition feature = Spearman-Brown corrected
   correlation of the two half-medians across the 90 person-conditions
   (also within-person, i.e. after removing each person's mean).
   Reliability of a D_i = corrected correlation of the two half-D's
   across the 18 people, per planned contrast.

2. Behavioural composites: alpha of the item-level D_i (the composite
   D is a mean of item D's), per contrast. Single items: not estimable.

3. Resolution: the |rho| needed for raw p<.05, Holm within 16, and the
   first BH hit across the full combo sweep, at n = 18 and n = 54.

Writes outputs/reliability/.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as st

HERE = Path(__file__).resolve().parent
WALTER = HERE.parent
REPO = WALTER.parents[1]
sys.path.insert(0, str(WALTER))
sys.path.insert(0, str(REPO / "analysis/eeg/statistics"))
import statkit as sk  # noqa: E402
from build_ad_local_epochs import (  # noqa: E402
    DEFAULT_AD_WINDOWS, DEFAULT_EPOCHS, index_epochs, unique_onsets, select_tiles, unique_tiles, epoch_mid,
)
from build_condition_contrasts import FEATURE_TIERS, read_csv  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
OUT = HERE / "outputs" / "reliability"
K = 37
FEATURES = list(FEATURE_TIERS)
SHORT = {
    "fz_theta_power_db_uv2": "eeg_fz_theta", "posterior_alpha_power_db_uv2": "eeg_posterior_alpha",
    "theta_power_db_uv2": "eeg_theta", "alpha_power_db_uv2": "eeg_alpha", "beta_power_db_uv2": "eeg_beta",
    "delta_power_db_uv2": "eeg_delta", "gamma_power_db_uv2": "eeg_gamma", "faa_log_f4_minus_f3": "eeg_faa",
    "delta_relative_power": "eeg_rel_delta", "theta_relative_power": "eeg_rel_theta", "alpha_relative_power": "eeg_rel_alpha",
    "beta_relative_power": "eeg_rel_beta", "gamma_relative_power": "eeg_rel_gamma",
    "engagement_beta_over_alpha_theta": "eeg_engagement",
    "engagement_pope_frontocentral_beta_over_alpha_theta": "eeg_pope",
    "engagement_kislov_central_beta16_24_over_alpha8_12": "eeg_kislov",
}
COMPOSITE_ITEMS = {
    "credibility": [("llm_reliable", 1), ("llm_false", -1), ("llm_made_up", -1)],
    "helpfulness": [("llm_helpful", 1), ("llm_addressed", 1), ("llm_not_aid", -1)],
    "convincingness": [("llm_skeptical", -1), ("llm_convincing", 1), ("llm_changed_mind", 1)],
    "relevance": [("llm_not_useful", -1), ("llm_suggestions", 1), ("llm_relevant", 1)],
    "neutrality": [("llm_neutral", 1), ("llm_impartial", 1), ("llm_opinionated", -1)],
    "manipulation": [("behaviour_pushing", 1), ("behaviour_manipulate", 1)],
    "notice": [("notice_brands", 1), ("notice_sponsored", 1)],
}


def spearman_brown(r: float) -> float:
    """Full-length reliability from a half-half correlation. A
    non-positive r means the halves do not agree at all, i.e. no
    detectable true-score variance: reported as 0 (the raw r is kept
    in the tables alongside)."""
    if not np.isfinite(r) or r <= 0:
        return 0.0
    return 2 * r / (1 + r)


def selected_tiles_per_cell(all_tiles: bool = False) -> dict[tuple[str, str], list[dict]]:
    """k=37 tiles nearest visual onset per person x condition (the
    confirmatory Dataset A aggregation), or every retained tile in the
    condition window (the whole-window Gold aggregation) when
    ``all_tiles`` is set."""
    epochs = read_csv(DEFAULT_EPOCHS)
    windows = read_csv(DEFAULT_AD_WINDOWS)
    by_cell = index_epochs(epochs)
    onsets_by_subject: dict[str, list[dict]] = defaultdict(list)
    for onset in unique_onsets(windows):
        onsets_by_subject[onset["subject_id"]].append(onset)
    out: dict[tuple[str, str], list[dict]] = {}
    for subject, onsets in onsets_by_subject.items():
        by_cond: dict[str, list[dict]] = defaultdict(list)
        for o in onsets:
            by_cond[o["condition"]].append(o)
        for cond in sk.CONDITIONS:
            tiles = by_cell[(subject, cond)]
            if all_tiles:
                chosen = list(tiles)
            else:
                chosen = []
                for o in by_cond[cond]:
                    chosen.extend(select_tiles(tiles, float(o["reference_onset_eeg_offset_s"]), k=K, side="around"))
                chosen = unique_tiles(chosen)
            chosen.sort(key=epoch_mid)
            out[(subject, cond)] = chosen
    return out


def fisher_ci(r: float, n: int) -> tuple[float, float]:
    if not np.isfinite(r) or n < 4:
        return (np.nan, np.nan)
    z = np.arctanh(np.clip(r, -0.999, 0.999)); se = 1 / np.sqrt(n - 3)
    return float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se))


def half_medians(cells: dict[tuple[str, str], list[dict]], scheme: str, rng: np.random.Generator | None = None) -> pd.DataFrame:
    rows = []
    for (subject, cond), tiles in cells.items():
        n = len(tiles)
        if scheme == "odd_even":
            a, b = tiles[0::2], tiles[1::2]
        elif scheme == "random":
            perm = rng.permutation(n)
            a, b = [tiles[i] for i in perm[: n // 2]], [tiles[i] for i in perm[n // 2:]]
        else:
            a, b = tiles[: n // 2], tiles[n // 2:]
        rec = {"subject_id": subject, "condition": cond, "n_tiles": n}
        for f in FEATURES:
            va = np.median([float(t[f]) for t in a]); vb = np.median([float(t[f]) for t in b])
            rec[f"{SHORT[f]}__A"] = va; rec[f"{SHORT[f]}__B"] = vb
        rows.append(rec)
    return pd.DataFrame(rows)


def eeg_reliability(halves: pd.DataFrame, scheme: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    feat_rows, d_rows = [], []
    for f in FEATURES:
        s = SHORT[f]
        a, b = halves[f"{s}__A"], halves[f"{s}__B"]
        r_between = st.pearsonr(a, b)[0]
        # within-person: remove each person's mean over the five conditions
        ac = a - halves.groupby("subject_id")[f"{s}__A"].transform("mean")
        bc = b - halves.groupby("subject_id")[f"{s}__B"].transform("mean")
        r_within = st.pearsonr(ac, bc)[0]
        feat_rows.append({"scheme": scheme, "feature": s, "tier": FEATURE_TIERS[f], "n_cells": len(halves),
                          "r_halves_between": r_between, "rel_between_SB": spearman_brown(r_between),
                          "r_halves_within_person": r_within, "rel_within_SB": spearman_brown(r_within)})
        wa = halves.pivot(index="subject_id", columns="condition", values=f"{s}__A")[list(sk.CONDITIONS)]
        wb = halves.pivot(index="subject_id", columns="condition", values=f"{s}__B")[list(sk.CONDITIONS)]
        for cid in sk.PLANNED:
            da, db = sk.contrast_scores(wa, cid), sk.contrast_scores(wb, cid)
            r = st.pearsonr(da, db)[0]
            d_rows.append({"scheme": scheme, "feature": s, "tier": FEATURE_TIERS[f], "contrast": cid, "n_people": len(da),
                           "r_halves": r, "rel_D_SB": spearman_brown(r), "sd_D_full": float((0.5 * (da + db)).std(ddof=1))})
        # the one Dataset A pair that survived the exploratory post-hoc sweep (implicit-early minus explicit-late)
        da, db = wa["inline_early"] - wa["block_late"], wb["inline_early"] - wb["block_late"]
        r = st.pearsonr(da, db)[0]
        d_rows.append({"scheme": scheme, "feature": s, "tier": FEATURE_TIERS[f], "contrast": "pair_inline_early_minus_block_late", "n_people": len(da),
                       "r_halves": r, "rel_D_SB": spearman_brown(r), "sd_D_full": float((0.5 * (da + db)).std(ddof=1))})
    return pd.DataFrame(feat_rows), pd.DataFrame(d_rows)


def cronbach(mat: np.ndarray) -> float:
    k = mat.shape[1]
    item_var = mat.var(axis=0, ddof=1).sum()
    total_var = mat.sum(axis=1).var(ddof=1)
    return k / (k - 1) * (1 - item_var / total_var) if total_var > 0 else np.nan


def behavioural_reliability() -> pd.DataFrame:
    c = pd.read_csv(GOLD / "condition_features.csv")
    rows = []
    for comp, items in COMPOSITE_ITEMS.items():
        for cid in sk.PLANNED + ("level",):
            cols = []
            for item, sign in items:
                w = sk.wide(c, item)
                x = (8 - w) if sign < 0 else w
                if cid == "level":
                    cols.append(x.mean(axis=1))
                else:
                    cols.append(sk.contrast_scores(x, cid))
            mat = pd.concat(cols, axis=1).dropna().to_numpy()
            rows.append({"composite": comp, "n_items": len(items), "contrast": cid, "n_people": mat.shape[0],
                         "alpha": cronbach(mat)})
    return pd.DataFrame(rows)


def trajectory_agreement() -> pd.DataFrame:
    """Trajectory D_i computed from the utterance-genre classifier vs
    from the contextual classifier (two readings of the same chats).
    Not a reliability in the strict sense, but the only parallel form
    available; Spearman-Brown is not applied."""
    conv = pd.read_csv(REPO / "analysis/trajectories/outputs/conversations.csv")
    metrics = ["n_shift", "shift_rate", "diversity", "entropy_nats", "entropy_normalised", "max_persistence",
               "mean_js_divergence", "max_js_divergence", "mean_total_variation", "shifted_into_purchasable"]
    rows = []
    for m in metrics:
        wu = sk.wide(conv[conv.genre_source == "utterance"], m)
        wc = sk.wide(conv[conv.genre_source == "contextual"], m)
        common = wu.index.intersection(wc.index)
        lu, lc = wu.loc[common].mean(axis=1), wc.loc[common].mean(axis=1)
        constant = [s for s, v in (("utterance", lu), ("contextual", lc)) if v.std() == 0]
        lvl = st.spearmanr(lu, lc)[0] if not constant else np.nan
        rec = {"metric": f"traj_{m}", "n_people": len(common), "r_level_utterance_vs_contextual": float(lvl),
               "note": f"{' and '.join(constant)} source constant (never fires); agreement undefined" if constant else ""}
        for cid in sk.PLANNED:
            du, dc = sk.contrast_scores(wu.loc[common], cid), sk.contrast_scores(wc.loc[common], cid)
            rec[f"r_D_{cid}"] = float(st.spearmanr(du, dc)[0]) if du.std() > 0 and dc.std() > 0 else np.nan
        rows.append(rec)
    return pd.DataFrame(rows)


def resolution() -> pd.DataFrame:
    rows = []
    for n in (18, 36, 54):
        df = n - 2
        for label, alpha in (("raw .05", 0.05), ("Holm within 16", 0.05 / 16), ("Holm within 64", 0.05 / 64),
                             ("first BH hit of 2560", 0.05 / 2560)):
            t = st.t.ppf(1 - alpha / 2, df)
            r = t / np.sqrt(t * t + df)
            rows.append({"n": n, "criterion": label, "min_abs_rho": r})
        # 80% power for raw .05, two-sided, Fisher z
        z_a = st.norm.ppf(0.975); z_b = st.norm.ppf(0.8)
        rho80 = np.tanh((z_a + z_b) / np.sqrt(n - 3))
        rows.append({"n": n, "criterion": "80% power at raw .05", "min_abs_rho": rho80})
    return pd.DataFrame(rows)


def figure(feat_rel: pd.DataFrame, d_rel: pd.DataFrame, beh: pd.DataFrame, res: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    ax = axes[0]
    piv = feat_rel.pivot(index="feature", columns="scheme", values="rel_within_SB")
    piv = piv.loc[[SHORT[f] for f in FEATURES]]
    y = np.arange(len(piv))
    ax.barh(y - 0.2, piv["random"], height=0.4, color="0.35", label="random half-splits (upper)")
    ax.barh(y + 0.2, piv["first_second"], height=0.4, color="0.7", label="first/second half (lower)")
    ax.set_yticks(y, piv.index, fontsize=8); ax.invert_yaxis(); ax.set_xlim(-0.2, 1)
    ax.axvline(0, color="k", lw=0.8); ax.set_title("EEG condition feature reliability\n(within-person, Spearman-Brown)", fontsize=10); ax.legend(fontsize=7, loc="lower right")
    ax = axes[1]
    sub = d_rel[d_rel.scheme == "random"].pivot(index="feature", columns="contrast", values="rel_D_SB").loc[piv.index]
    sub2 = d_rel[d_rel.scheme == "first_second"].pivot(index="feature", columns="contrast", values="rel_D_SB").loc[piv.index]
    for k, (cid, m) in enumerate(zip(sk.PLANNED, ["o", "s", "^"])):
        ax.plot(sub[cid], y + (k - 1) * 0.22, m, color="k", ms=5, label=f"{sk.CONTRAST_LABEL[cid]} (200 random splits)")
        ax.plot(sub2[cid], y + (k - 1) * 0.22, m, color="0.6", ms=5, mfc="none", label=f"{sk.CONTRAST_LABEL[cid]} (first/second)")
    ax.set_yticks(y, piv.index, fontsize=8); ax.invert_yaxis(); ax.set_xlim(-0.05, 1); ax.axvline(0, color="k", lw=0.8)
    ax.set_title("Reliability of the EEG D_i (n = 18; 0 = halves do not agree, no true variance)", fontsize=9); ax.legend(fontsize=6, loc="lower left")
    ax = axes[2]
    b = beh[beh.contrast != "level"].pivot(index="composite", columns="contrast", values="alpha")
    lvl = beh[beh.contrast == "level"].set_index("composite")["alpha"]
    yb = np.arange(len(b))
    for cid, m in zip(sk.PLANNED, ["o", "s", "^"]):
        ax.plot(b[cid], yb, m, color="k", ms=5, label=sk.CONTRAST_LABEL[cid])
    ax.plot(lvl.loc[b.index], yb, "D", color="tab:red", ms=5, label="person level")
    ax.set_yticks(yb, b.index); ax.invert_yaxis(); ax.set_xlim(-0.2, 1); ax.axvline(0, color="k", lw=0.8)
    ax.set_title("Behavioural composite D_i: Cronbach alpha of item D's (n = 54)", fontsize=10); ax.legend(fontsize=7, loc="lower left")
    fig.suptitle("Block 0: what is being correlated, and how reliable it is")
    fig.tight_layout(); fig.savefig(OUT / "reliability.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3.6))
    for n, col in ((18, "tab:blue"), (54, "tab:orange")):
        sub = res[res.n == n]
        ax.plot(sub["min_abs_rho"], range(len(sub)), "o-", color=col, label=f"n = {n}")
    ax.set_yticks(range(len(sub)), sub["criterion"]); ax.set_xlim(0, 1); ax.set_xlabel("|rho| required")
    ax.set_title("Resolution of a Spearman correlation"); ax.legend(); ax.grid(axis="x", alpha=0.3)
    fig.tight_layout(); fig.savefig(OUT / "resolution.png", dpi=150); plt.close(fig)


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    cells = selected_tiles_per_cell()
    n_tiles = pd.Series({k: len(v) for k, v in cells.items()})
    feat_frames, d_frames = [], []
    for scheme in ("odd_even", "first_second"):
        halves = half_medians(cells, scheme)
        halves.to_csv(OUT / f"eeg_half_medians_{scheme}.csv", index=False)
        fr, dr = eeg_reliability(halves, scheme)
        feat_frames.append(fr); d_frames.append(dr)
    # random splits: average the half-half correlation over 200 random partitions (Fisher z), then Spearman-Brown.
    rng = np.random.default_rng(11)
    fr_acc, dr_acc = [], []
    for _ in range(200):
        halves = half_medians(cells, "random", rng)
        fr, dr = eeg_reliability(halves, "random")
        fr_acc.append(fr); dr_acc.append(dr)
    def z(x): return np.arctanh(np.clip(x, -0.999, 0.999))
    fr_all = pd.concat(fr_acc); dr_all = pd.concat(dr_acc)
    fr_rand = fr_all.groupby(["scheme", "feature", "tier", "n_cells"], as_index=False).agg(
        r_halves_between=("r_halves_between", lambda s: np.tanh(z(s).mean())),
        r_halves_within_person=("r_halves_within_person", lambda s: np.tanh(z(s).mean())))
    fr_rand["rel_between_SB"] = fr_rand["r_halves_between"].map(spearman_brown)
    fr_rand["rel_within_SB"] = fr_rand["r_halves_within_person"].map(spearman_brown)
    dr_rand = dr_all.groupby(["scheme", "feature", "tier", "contrast", "n_people"], as_index=False).agg(
        r_halves=("r_halves", lambda s: np.tanh(z(s).mean())), sd_D_full=("sd_D_full", "mean"),
        r_halves_sd_over_splits=("r_halves", "std"))
    dr_rand["rel_D_SB"] = dr_rand["r_halves"].map(spearman_brown)
    feat_frames.append(fr_rand); d_frames.append(dr_rand)
    # same thing on every retained tile of the condition window (whole-window Gold aggregation): is k=37 the problem?
    cells_all = selected_tiles_per_cell(all_tiles=True)
    rng = np.random.default_rng(12)
    fr_acc, dr_acc = [], []
    for _ in range(200):
        halves = half_medians(cells_all, "random", rng)
        fr, dr = eeg_reliability(halves, "random_all_tiles")
        fr_acc.append(fr); dr_acc.append(dr)
    fr_all = pd.concat(fr_acc); dr_all = pd.concat(dr_acc)
    fr_rand_all = fr_all.groupby(["scheme", "feature", "tier", "n_cells"], as_index=False).agg(
        r_halves_between=("r_halves_between", lambda s: np.tanh(z(s).mean())),
        r_halves_within_person=("r_halves_within_person", lambda s: np.tanh(z(s).mean())))
    fr_rand_all["rel_between_SB"] = fr_rand_all["r_halves_between"].map(spearman_brown)
    fr_rand_all["rel_within_SB"] = fr_rand_all["r_halves_within_person"].map(spearman_brown)
    dr_rand_all = dr_all.groupby(["scheme", "feature", "tier", "contrast", "n_people"], as_index=False).agg(
        r_halves=("r_halves", lambda s: np.tanh(z(s).mean())), sd_D_full=("sd_D_full", "mean"),
        r_halves_sd_over_splits=("r_halves", "std"))
    dr_rand_all["rel_D_SB"] = dr_rand_all["r_halves"].map(spearman_brown)
    feat_frames.append(fr_rand_all); d_frames.append(dr_rand_all)
    feat_rel = pd.concat(feat_frames, ignore_index=True)
    d_rel = pd.concat(d_frames, ignore_index=True)
    # sampling interval of the half-half correlation over the 18 people (Fisher z), and the implied SB upper bound
    ci = d_rel.apply(lambda r: fisher_ci(r["r_halves"], int(r["n_people"])), axis=1, result_type="expand")
    d_rel["r_halves_ci_lo"], d_rel["r_halves_ci_hi"] = ci[0], ci[1]
    d_rel["rel_D_SB_ci_hi"] = d_rel["r_halves_ci_hi"].map(spearman_brown)
    n_tiles_all = pd.Series({k_: len(v) for k_, v in cells_all.items()})
    beh = behavioural_reliability()
    res = resolution()
    traj = trajectory_agreement()
    feat_rel.to_csv(OUT / "eeg_feature_reliability.csv", index=False)
    d_rel.to_csv(OUT / "eeg_D_reliability.csv", index=False)
    beh.to_csv(OUT / "behavioural_D_alpha.csv", index=False)
    res.to_csv(OUT / "resolution.csv", index=False)
    traj.to_csv(OUT / "trajectory_D_source_agreement.csv", index=False)
    figure(feat_rel, d_rel, beh, res)

    # attenuation ceilings for the headline pairs. Three reliability
    # readings of the EEG D: k=37 random halves, k=37 first vs second
    # half, and random halves of every retained tile (whole window).
    # None is "the" reliability; the ceiling is reported for each and
    # the "true rho needed" uses the most favourable (largest) one, so
    # the statement "could not have been seen" is the conservative one.
    ceil_rows = []
    rel_by = {s: d_rel[d_rel.scheme == s].set_index(["feature", "contrast"])["rel_D_SB"] for s in ("random", "first_second", "random_all_tiles")}
    beh_a = beh[beh.contrast != "level"].set_index(["composite", "contrast"])["alpha"]
    for cid in sk.PLANNED:
        for e in ("eeg_fz_theta", "eeg_posterior_alpha"):
            for b_ in ("credibility", "manipulation", "notice"):
                ra = beh_a[(b_, cid)]
                rels = {s: float(rel_by[s][(e, cid)]) for s in rel_by}
                ceilings = {s: float(np.sqrt(max(ra, 0) * max(r, 0))) for s, r in rels.items()}
                best = max(ceilings.values())
                # true correlation that would be needed to show |rho| = .47 (raw .05 at n = 18) or .66 (Holm within 16); > 1 = unreachable
                ceil_rows.append({"contrast": cid, "behaviour": b_, "eeg": e, "rel_beh_alpha": ra,
                                  "rel_eeg_D_k37_random": rels["random"], "rel_eeg_D_k37_first_second": rels["first_second"], "rel_eeg_D_all_tiles": rels["random_all_tiles"],
                                  "max_observable_rho_k37_random": ceilings["random"], "max_observable_rho_k37_first_second": ceilings["first_second"],
                                  "max_observable_rho_all_tiles": ceilings["random_all_tiles"], "max_observable_rho_best": best,
                                  "true_rho_needed_raw05_n18_best": (0.47 / best) if best > 0 else np.inf,
                                  "true_rho_needed_holm16_n18_best": (0.66 / best) if best > 0 else np.inf})
    ceil = pd.DataFrame(ceil_rows); ceil.to_csv(OUT / "attenuation_ceiling_headline.csv", index=False)

    summary = {
        "k": K, "n_cells": int(len(cells)), "tiles_per_ad_cell": int(n_tiles[[k for k in n_tiles.index if k[1] != 'no_ads']].min()),
        "tiles_per_no_ad_cell_range": [int(n_tiles[[k for k in n_tiles.index if k[1] == 'no_ads']].min()), int(n_tiles[[k for k in n_tiles.index if k[1] == 'no_ads']].max())],
        "tiles_all_window_median": float(n_tiles_all.median()),
        "eeg_feature_rel_within_SB_median": {s: float(feat_rel[feat_rel.scheme == s]["rel_within_SB"].median()) for s in ("random", "odd_even", "first_second", "random_all_tiles")},
        "eeg_D_rel_median": {s: float(d_rel[(d_rel.scheme == s) & d_rel.contrast.isin(sk.PLANNED)]["rel_D_SB"].median()) for s in ("random", "odd_even", "first_second", "random_all_tiles")},
        "eeg_D_rel_headline": d_rel[d_rel.feature.isin(["eeg_fz_theta", "eeg_posterior_alpha"]) & d_rel.scheme.isin(["random", "first_second", "random_all_tiles"])][["scheme", "feature", "contrast", "r_halves", "r_halves_ci_lo", "r_halves_ci_hi", "rel_D_SB", "rel_D_SB_ci_hi"]].round(3).to_dict(orient="records"),
        "behavioural_D_alpha": beh.round(3).to_dict(orient="records"),
        "trajectory_D_source_agreement": traj.round(3).to_dict(orient="records"),
        "attenuation_ceiling_headline": ceil.round(3).to_dict(orient="records"),
        "resolution": res.round(3).to_dict(orient="records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    s = run()
    pd.set_option("display.width", 200)
    print(json.dumps({k: v for k, v in s.items() if k not in ("eeg_D_rel_headline", "behavioural_D_alpha", "resolution")}, indent=2))
    print(pd.DataFrame(s["eeg_D_rel_headline"]).to_string(index=False))
    print(pd.DataFrame(s["behavioural_D_alpha"]).pivot(index="composite", columns="contrast", values="alpha").round(2).to_string())
    print(pd.DataFrame(s["resolution"]).pivot(index="criterion", columns="n", values="min_abs_rho").round(2).to_string())
    print(pd.DataFrame(s["trajectory_D_source_agreement"]).to_string(index=False))
    print(pd.DataFrame(s["attenuation_ceiling_headline"]).to_string(index=False))
    print(f"Wrote {OUT}")
