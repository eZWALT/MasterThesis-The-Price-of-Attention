"""EEG × behavioural, three correlation engines, Dataset A and Dataset B.

Dataset A: confirmatory k=37 condition-aggregation D_i (18 people).
Dataset B: onset-locked post−pre deltas. Person-level D from the four
ads (format, timing); any-ad is mean(ad) − mean(matched no-ad replies).
Recall exists only on ads, so any-ad recall is the mean of the four
ads (no no-ad item).

Engines: Pearson, Spearman, Kendall. n=18 everywhere at this grain.
|r| > .468 is raw two-sided p < .05 for Pearson/Spearman; |τ| > .338
is the Kendall match. This is a sweep, not a second confirmatory family.

    python analysis/walter/combos/run_eeg_beh_three_engines.py
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import scipy.stats as st

import combokit as ck
from combokit import sk

OUT = ck.OUT / "headline"
BEH = ck.BEH_SURVEY + ["behaviour_pushing", "behaviour_manipulate", "notice_brands", "notice_sponsored"] + ck.BEH_PROCESS
RECALL = ["recall_memory", "recall_trust_shift"]
R_BAR = st.t.ppf(1 - 0.025, 16) / np.sqrt(st.t.ppf(1 - 0.025, 16) ** 2 + 16)  # .468
TAU_BAR = 1.96 * np.sqrt(2 * (2 * 18 + 5) / (9 * 18 * 17))  # .338


def three(x: pd.Series, y: pd.Series) -> dict:
    m = pd.concat([x, y], axis=1).dropna()
    a, b = m.iloc[:, 0].to_numpy(float), m.iloc[:, 1].to_numpy(float)
    if len(a) < 5 or np.nanstd(a) == 0 or np.nanstd(b) == 0:
        return {"n": int(len(a)), "pearson_r": np.nan, "pearson_p": np.nan,
                "spearman_r": np.nan, "spearman_p": np.nan, "kendall_r": np.nan, "kendall_p": np.nan}
    out = {"n": int(len(a))}
    for name, fn in (("pearson", st.pearsonr), ("spearman", st.spearmanr), ("kendall", st.kendalltau)):
        r, p = fn(a, b)
        out[f"{name}_r"] = float(r)
        out[f"{name}_p"] = float(p)
    return out


def dataset_b_wide() -> tuple[pd.DataFrame, pd.DataFrame]:
    """experiment_id × condition matrices of Dataset B post−pre (ads) and
    experiment_id × timing matrices of the matched no-ad replies."""
    B = pd.read_csv(ck.EEG_GOLD / "ad_response_features.csv")
    B = B[B.primary_analysis_eligible == "yes"]
    ads = B[B.reference_kind == "advertisement"].copy()
    matched = B[B.reference_kind == "matched_no_ad_reply"].copy()
    ad_w, match_w = {}, {}
    for short, long in ck.EEG_LONG.items():
        col = f"{long}_post_minus_pre"
        if col not in ads.columns:
            continue
        ad_w[short] = ads.pivot_table(index="experiment_id", columns="condition", values=col, aggfunc="first")
        match_w[short] = matched.pivot_table(index="experiment_id", columns="matched_timing", values=col, aggfunc="first")
    return ad_w, match_w


def b_contrast(ad_w: pd.DataFrame, cid: str) -> pd.Series:
    w = ad_w.reindex(columns=list(sk.AD_CONDITIONS))
    return sk.contrast_scores(w.dropna(), cid)


def b_any_ad(ad_w: pd.DataFrame, match_w: pd.DataFrame) -> pd.Series:
    ad_mean = ad_w.reindex(columns=list(sk.AD_CONDITIONS)).mean(axis=1)
    match_mean = match_w.mean(axis=1)
    return (ad_mean - match_mean).rename("D")


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    D = ck.load_D()
    D = D[D.arm == "lab"].copy() if "arm" in D.columns else D
    ads = pd.read_csv(ck.GOLD / "advertisement_features.csv")
    ads = ads[ads.arm == "lab"]
    ad_w, match_w = dataset_b_wide()
    eegs = [e for e in ck.EEG if e in ad_w]
    rows = []

    def add(dataset, grain, cid, beh, eeg, rec):
        rows.append({"dataset": dataset, "grain": grain, "contrast": cid, "beh": beh, "eeg": eeg,
                     "primary_eeg": eeg in ck.EEG_PRIMARY, "beh_family": (
                         "survey" if beh in ck.BEH_SURVEY else
                         "item" if beh in ("behaviour_pushing", "behaviour_manipulate", "notice_brands", "notice_sponsored") else
                         "process" if beh in ck.BEH_PROCESS else "recall"),
                     **rec})

    for cid in sk.PLANNED:
        for beh in BEH:
            left = D[f"{beh}__{cid}"]
            for eeg in ck.EEG:
                add("A", "D_k37", cid, beh, eeg, three(left, D[f"{eeg}__{cid}"]))
        if cid != "any_ad_vs_no_ads":
            for beh in RECALL:
                w = ads.pivot_table(index="experiment_id", columns="condition", values=beh, aggfunc="first")
                left = sk.contrast_scores(w.dropna().reindex(columns=list(sk.AD_CONDITIONS)), cid)
                for eeg in ck.EEG:
                    add("A", "D_k37", cid, beh, eeg, three(left, D.set_index("experiment_id")[f"{eeg}__{cid}"]))

    for cid in ("inline_vs_block", "early_vs_late"):
        for eeg in eegs:
            right = b_contrast(ad_w[eeg], cid)
            for beh in BEH:
                add("B", "D_onset", cid, beh, eeg, three(D.set_index("experiment_id")[f"{beh}__{cid}"], right))
            for beh in RECALL:
                w = ads.pivot_table(index="experiment_id", columns="condition", values=beh, aggfunc="first")
                left = sk.contrast_scores(w.dropna().reindex(columns=list(sk.AD_CONDITIONS)), cid)
                add("B", "D_onset", cid, beh, eeg, three(left, right))

    for eeg in eegs:
        right = b_any_ad(ad_w[eeg], match_w[eeg])
        for beh in BEH:
            add("B", "D_onset", "any_ad_vs_matched", beh, eeg, three(D.set_index("experiment_id")[f"{beh}__any_ad_vs_no_ads"], right))
        for beh in RECALL:
            left = ads.groupby("experiment_id")[beh].mean()
            add("B", "D_onset", "any_ad_vs_matched", beh, eeg, three(left, right))

    T = pd.DataFrame(rows)
    T.to_csv(OUT / "eeg_beh_three_engines_all16.csv", index=False)

    def pack(sub: pd.DataFrame) -> dict:
        out = {"n_cells": int(len(sub)), "n_people": 18}
        for eng in ("pearson", "spearman", "kendall"):
            r, p = sub[f"{eng}_r"], sub[f"{eng}_p"]
            bar = TAU_BAR if eng == "kendall" else R_BAR
            out[eng] = {
                "n_raw_05": int((p < 0.05).sum()),
                "n_abs_above_bar": int((r.abs() > bar).sum()),
                "expected_raw_05": round(0.05 * int(p.notna().sum()), 1),
                "max_abs_r": float(r.abs().max()) if r.notna().any() else None,
                "above_bar": sub.loc[r.abs() > bar, ["contrast", "beh", "eeg", f"{eng}_r", f"{eng}_p", "beh_family", "primary_eeg"]]
                .assign(engine=eng).sort_values(f"{eng}_p").round(3).to_dict(orient="records"),
            }
        return out

    summary = {
        "r_bar_pearson_spearman_n18": float(R_BAR),
        "tau_bar_kendall_n18": float(TAU_BAR),
        "A_D_k37": pack(T[T.dataset == "A"]),
        "B_D_onset": pack(T[T.dataset == "B"]),
        "A_survey_only": pack(T[(T.dataset == "A") & (T.beh_family == "survey")]),
        "A_primary_eeg_survey": pack(T[(T.dataset == "A") & (T.beh_family == "survey") & (T.primary_eeg)]),
        "B_survey_only": pack(T[(T.dataset == "B") & (T.beh_family == "survey")]),
    }
    (OUT / "eeg_beh_three_engines_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    s = run()
    print(f"bar |r| > {s['r_bar_pearson_spearman_n18']:.3f}  |τ| > {s['tau_bar_kendall_n18']:.3f}   (n=18, raw .05)")
    for key in ("A_D_k37", "B_D_onset", "A_survey_only", "A_primary_eeg_survey", "B_survey_only"):
        block = s[key]
        print(f"\n=== {key}  ({block['n_cells']} cells) ===")
        for eng in ("pearson", "spearman", "kendall"):
            e = block[eng]
            print(f"  {eng:9s} raw p<.05 {e['n_raw_05']:3d} (expect {e['expected_raw_05']})  |r|>bar {e['n_abs_above_bar']:3d}  max |r|={e['max_abs_r']:.3f}")
            for rec in e["above_bar"][:12]:
                rr = rec.get(f"{eng}_r")
                print(f"    {rec['contrast']:22s} {rec['beh']:28s} {rec['eeg']:22s}  r={rr:+.3f}  p={rec[f'{eng}_p']:.3f}  {rec['beh_family']}")
    print(f"\nWrote {OUT / 'eeg_beh_three_engines_all16.csv'}")
