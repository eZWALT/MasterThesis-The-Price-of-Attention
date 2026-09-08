"""Collate every combo family (old 2,560-cell map and blocks 1-7) into
one ledger: tests, smallest raw p, Holm hits, BH hits, family-wise
permutation p where one was run. Writes outputs/blocks_ledger.csv and
outputs/blocks_summary.json.

    python analysis/walter/combos/summarise_blocks.py
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

import combokit as ck

OUT = ck.OUT


def fam_rows(table: pd.DataFrame, block: str, source: str, perm: dict | None = None) -> list[dict]:
    rows = []
    for fam, g in table.groupby("family"):
        g = g[g.p_raw.notna()]
        rows.append({"block": block, "family": fam, "n_tests": int(len(g)), "min_p_raw": float(g.p_raw.min()) if len(g) else None,
                     "hits_raw": int((g.p_raw < 0.05).sum()), "hits_holm_family": int(g.sig_holm_family.sum()),
                     "hits_bh_global_in_table": int(g.sig_bh_global.sum()),
                     "p_perm_familywise": (perm or {}).get(fam), "source": source})
    return rows


def run() -> None:
    rows = []
    T = pd.read_csv(OUT / "combos_all_tests.csv")
    T["family_top"] = T.combo + "|" + T.grain
    for fam, g in T.groupby("family_top"):
        rows.append({"block": "map (run_combos)", "family": fam, "n_tests": int(g.p_raw.notna().sum()), "min_p_raw": float(g.p_raw.min()),
                     "hits_raw": int((g.p_raw < 0.05).sum()), "hits_holm_family": int(g.sig_holm_family.sum()), "hits_bh_global_in_table": int(g.sig_bh_global.sum()),
                     "p_perm_familywise": None, "source": "outputs/combos_all_tests.csv"})
    H = pd.read_csv(OUT / "headline/headline_tests.csv"); rows += fam_rows(H, "1 headline PC1", "outputs/headline/headline_tests.csv")
    L = pd.read_csv(OUT / "lmm/lmm_tests.csv"); ls = json.loads((OUT / "lmm/summary.json").read_text())
    perm_l = {"A_state_association": ls["permutation_maxT"]["A"]["p_perm_family"], "B0_main_within_ads": ls["permutation_maxT"]["B0"]["p_perm_family"], "B_moderation": ls["permutation_maxT"]["B"]["p_perm_family"]}
    rows += fam_rows(L, "3 LMM state / moderation", "outputs/lmm/lmm_tests.csv", perm_l)
    U = pd.read_csv(OUT / "turns/turn_tests.csv"); rows += fam_rows(U, "4 turn grain", "outputs/turns/turn_tests.csv")
    E = pd.read_csv(OUT / "events/event_tests.csv"); es = json.loads((OUT / "events/summary.json").read_text())
    perm_e = {"events_headline": es["permutation_headline"]["p_perm_family"], "events_all_exploratory": es["permutation_all_exploratory"]["p_perm_family"]}
    rows += fam_rows(E, "5 event grain (Dataset B)", "outputs/events/event_tests.csv", perm_e)
    S = pd.read_csv(OUT / "task_state/task_state_tests.csv"); rows += fam_rows(S, "7 task-state trait", "outputs/task_state/task_state_tests.csv")
    ledger = pd.DataFrame(rows)
    ledger.to_csv(OUT / "blocks_ledger.csv", index=False)
    new = ledger[ledger.block != "map (run_combos)"]
    # BH pooled over every raw p of blocks 1-7 (336) and over blocks + map (2,896): the
    # per-table BH in the ledger is "within table"; these two are the pooled statements.
    p_new = pd.concat([t.p_raw for t in (H, L, U, E, S)]).dropna().to_numpy()
    p_all = np.concatenate([p_new, T.p_raw.dropna().to_numpy()])
    bh_new = int(multipletests(p_new, method="fdr_bh")[0].sum()); bh_all = int(multipletests(p_all, method="fdr_bh")[0].sum())
    summary = {
        "map_tests": int(ledger[ledger.block == "map (run_combos)"].n_tests.sum()),
        "new_tests_blocks_1_7": int(new.n_tests.sum()),
        "new_hits_holm": int(new.hits_holm_family.sum()),
        "new_hits_bh_within_table": int(new.hits_bh_global_in_table.sum()),
        "new_hits_bh_pooled": bh_new, "n_pooled_new": int(len(p_new)),
        "all_hits_bh_pooled_blocks_plus_map": bh_all, "n_pooled_all": int(len(p_all)),
        "new_hits_raw": int(new.hits_raw.sum()),
        "expected_raw_hits_under_null": float(0.05 * new.n_tests.sum()),
        "familywise_permutation_p": {r.family: float(r.p_perm_familywise) for r in new.itertuples() if pd.notna(r.p_perm_familywise)},
        "reliability": json.loads((OUT / "reliability/summary.json").read_text()),
        "concordance": json.loads((OUT / "concordance/summary.json").read_text())["blocks"],
    }
    (OUT / "blocks_summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    pd.set_option("display.width", 220)
    print(ledger.drop(columns="source").to_string(index=False))
    print({k: v for k, v in summary.items() if k not in ("reliability", "concordance")})


if __name__ == "__main__":
    run()
