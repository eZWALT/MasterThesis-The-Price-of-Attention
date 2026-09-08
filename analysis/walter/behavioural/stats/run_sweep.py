"""Goal 1 exploratory sweep. This is the search.

Every outcome the Gold carries, every test block the reviewers might
ask for, one long table. It is labelled exploratory because that is
what it is. Every hit carries its family size and the global test
count; report those next to any p you quote.

Outcome universe
  primary        trust, credibility, manipulation, notice
  secondary      helpfulness, convincingness, relevance, neutrality
  item pairs     behaviour_pushing, behaviour_manipulate, notice_brands, notice_sponsored
  raw items      15 llm_* items + personality_influence + personality_changed_mind
  process        duration, first-message latency, reply latency, lengths, typing, LLM latency
  trajectory     Defs 3-5 metrics on the utterance source (+ Def 6 paired test)

Test blocks per outcome
  planned_D       three planned contrasts + format×timing   (paired t; Wilcoxon alongside)
  friedman        omnibus over 5 conditions and over the 4 ad conditions
  pairwise        10 Wilcoxon pairs
  bfi_moderation  Spearman of each planned D with each BFI trait (n = 54)
  bfi_level       Spearman of the person mean with each trait

Family for Holm = outcome × block. BH runs across the whole sweep.
Person is the unit throughout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
OUT = WALTER / "behavioural" / "outputs" / "exploratory"

PRIMARY = ("trust", "credibility", "manipulation", "notice")
SECONDARY = ("helpfulness", "convincingness", "relevance", "neutrality")
ITEM_PAIRS = ("behaviour_pushing", "behaviour_manipulate", "notice_brands", "notice_sponsored")
RAW_ITEMS = (
    "llm_reliable", "llm_false", "llm_made_up",
    "llm_helpful", "llm_addressed", "llm_not_aid",
    "llm_skeptical", "llm_convincing", "llm_changed_mind",
    "llm_not_useful", "llm_suggestions", "llm_relevant",
    "llm_neutral", "llm_impartial", "llm_opinionated",
    "personality_influence", "personality_changed_mind",
)
PROCESS = (
    "duration_sec", "time_to_first_user_sec",
    "reply_latency_ms_median", "reply_latency_ms_mean",
    "user_msg_len_median", "user_n_words_median", "user_msg_len_sum",
    "assistant_msg_len_median", "llm_latency_ms_median",
    "n_typing_events", "conclusion_n_words",
)
TRAJ = (
    "traj_n_shift", "traj_shift_rate", "traj_diversity",
    "traj_entropy_nats", "traj_entropy_normalised", "traj_max_persistence",
    "traj_mean_js_divergence", "traj_max_js_divergence",
    "traj_mean_total_variation", "traj_shifted_into_purchasable",
)
BFI = ("bfi_e", "bfi_a", "bfi_c", "bfi_n", "bfi_o")

TIERS = {
    **{o: "primary" for o in PRIMARY},
    **{o: "secondary" for o in SECONDARY},
    **{o: "item_pair" for o in ITEM_PAIRS},
    **{o: "raw_item" for o in RAW_ITEMS},
    **{o: "process" for o in PROCESS},
    **{o: "trajectory" for o in TRAJ},
}


def sweep_outcome(table: pd.DataFrame, person: pd.DataFrame, outcome: str) -> list[dict]:
    rows: list[dict] = []
    tier = TIERS[outcome]
    w = sk.wide(table, outcome)
    if len(w) < 5:
        return rows

    # planned D + interaction
    d_cache = {}
    for cid, weights in sk.CONTRASTS.items():
        d = sk.contrast_scores(w, cid)
        d_cache[cid] = d
        rec = sk.paired_d(d)
        rec.update({"family": f"{outcome}|planned_D", "block": "planned_D", "tier": tier,
                    "outcome": outcome, "test": cid, "test_label": sk.CONTRAST_LABEL[cid],
                    "effect": rec.get("mean"), "effect_name": "mean D"})
        rows.append(rec)

    # Friedman
    for name, cols in (("friedman_5", sk.CONDITIONS), ("friedman_4ad", sk.AD_CONDITIONS)):
        rec = sk.friedman(w, cols)
        rec.update({"family": f"{outcome}|friedman", "block": "friedman", "tier": tier,
                    "outcome": outcome, "test": name, "test_label": name.replace("_", " "),
                    "effect": rec.get("kendall_w"), "effect_name": "Kendall W"})
        rows.append(rec)

    # pairwise
    for rec in sk.pairwise_wilcoxon(w):
        rec.update({"family": f"{outcome}|pairwise", "block": "pairwise", "tier": tier,
                    "outcome": outcome, "test": rec["pair"], "test_label": rec["pair_label"],
                    "effect": rec["mean"], "effect_name": "mean diff"})
        rows.append(rec)

    # BFI moderation on planned D
    bfi = person.set_index("experiment_id")[list(BFI)]
    for cid in sk.PLANNED:
        d = d_cache[cid]
        for trait in BFI:
            rec = sk.spearman(d, bfi[trait].reindex(d.index))
            rec.update({"family": f"{outcome}|bfi_moderation", "block": "bfi_moderation", "tier": tier,
                        "outcome": outcome, "test": f"{cid}~{trait}",
                        "test_label": f"{sk.CONTRAST_LABEL[cid]} ~ {trait.upper()[-1]}",
                        "effect": rec.get("rho"), "effect_name": "Spearman rho"})
            rows.append(rec)

    # BFI on level (person mean)
    level = w.mean(axis=1)
    for trait in BFI:
        rec = sk.spearman(level, bfi[trait].reindex(level.index))
        rec.update({"family": f"{outcome}|bfi_level", "block": "bfi_level", "tier": tier,
                    "outcome": outcome, "test": f"level~{trait}",
                    "test_label": f"person mean ~ {trait.upper()[-1]}",
                    "effect": rec.get("rho"), "effect_name": "Spearman rho"})
        rows.append(rec)
    return rows


def def6_block(table: pd.DataFrame) -> list[dict]:
    """Definition 6: ad-associated shift exists only after early ads."""
    rows = []
    for outcome in ("traj_ad_associated_shift", "traj_ad_associated_divergence"):
        piv = table.pivot_table(index="experiment_id", columns="condition", values=outcome, aggfunc="first")
        if not {"inline_early", "block_early"} <= set(piv.columns):
            continue
        d = (piv["inline_early"] - piv["block_early"]).dropna()
        rec = sk.paired_d(d)
        rec.update({"family": f"{outcome}|def6", "block": "def6", "tier": "trajectory",
                    "outcome": outcome, "test": "early_implicit_vs_early_explicit",
                    "test_label": "implicit early \u2212 explicit early",
                    "effect": rec.get("mean"), "effect_name": "mean D"})
        rows.append(rec)
    return rows


def heat(table: pd.DataFrame, path: Path) -> None:
    sub = table.loc[table["block"].isin(["planned_D", "friedman"])].copy()
    sub["neglog"] = -np.log10(sub["p_raw"].clip(lower=1e-6))
    piv = sub.pivot_table(index="outcome", columns="test", values="neglog")
    order = [o for o in TIERS if o in piv.index]
    piv = piv.reindex(order)
    fig, ax = plt.subplots(figsize=(8, 0.28 * len(piv) + 2))
    im = ax.imshow(piv.to_numpy(dtype=float), cmap="magma", vmin=0, vmax=4, aspect="auto")
    ax.set_xticks(range(len(piv.columns)), piv.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(piv.index)), piv.index, fontsize=7)
    ax.axvline(len(sk.CONTRASTS) - 0.5, color="white", lw=1)
    fig.colorbar(im, ax=ax, label="\u2212log10 p (raw)")
    ax.set_title("Exploratory sweep. Raw p. Read the test count before the colour.")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    table = pd.read_csv(GOLD / "combo_threeway.csv")
    person = pd.read_csv(GOLD / "person_features.csv")

    rows: list[dict] = []
    for outcome in TIERS:
        if outcome not in table.columns:
            continue
        rows.extend(sweep_outcome(table, person, outcome))
    rows.extend(def6_block(table))

    sweep = pd.DataFrame(rows)
    sweep = sweep.loc[sweep["p_raw"].notna()].copy()
    sweep = sk.add_corrections(sweep, family_col="family", p_col="p_raw")

    lead = ["tier", "outcome", "block", "test", "test_label", "n", "effect", "effect_name",
            "mean", "sd", "ci95_lo", "ci95_hi", "dz", "kendall_w", "rank_biserial", "rho",
            "stat", "p_raw", "p_wilcoxon", "p_holm_family", "p_bh_global",
            "sig_raw", "sig_holm_family", "sig_bh_global", "n_tests_in_family", "n_tests_global", "family"]
    lead = [c for c in lead if c in sweep.columns]
    sweep = sweep[lead].sort_values(["tier", "outcome", "block", "p_raw"])
    sweep.to_csv(OUT / "sweep_all_tests.csv", index=False)

    hits_bh = sweep.loc[sweep["sig_bh_global"]].sort_values("p_raw")
    hits_holm = sweep.loc[sweep["sig_holm_family"]].sort_values("p_raw")
    hits_raw = sweep.loc[sweep["sig_raw"]].sort_values("p_raw")
    hits_bh.to_csv(OUT / "hits_bh_global.csv", index=False)
    hits_holm.to_csv(OUT / "hits_holm_family.csv", index=False)
    hits_raw.to_csv(OUT / "hits_raw.csv", index=False)

    by_block = (
        sweep.groupby(["tier", "block"])
        .agg(n_tests=("p_raw", "count"), raw=("sig_raw", "sum"),
             holm_family=("sig_holm_family", "sum"), bh_global=("sig_bh_global", "sum"))
        .reset_index()
    )
    by_block.to_csv(OUT / "hit_counts_by_block.csv", index=False)
    heat(sweep, OUT / "heat_planned_friedman.png")

    summary = sk.summarise(sweep)
    summary["by_tier"] = (
        sweep.groupby("tier")
        .agg(n_tests=("p_raw", "count"), raw=("sig_raw", "sum"),
             holm_family=("sig_holm_family", "sum"), bh_global=("sig_bh_global", "sum"))
        .astype(int).to_dict(orient="index")
    )
    summary["top_bh_hits"] = hits_bh.head(25)[
        ["tier", "outcome", "block", "test_label", "n", "effect", "p_raw", "p_holm_family", "p_bh_global"]
    ].round(4).to_dict(orient="records")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    s = run()
    print(json.dumps({k: v for k, v in s.items() if k != "top_bh_hits"}, indent=2, default=str))
    print(f"Wrote {OUT}")
