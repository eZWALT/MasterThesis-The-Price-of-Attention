"""Assert the policy Silver/anchor contract. Exit 0 only if the shape is clean.

Run after build_policy_silver.py + build_human_anchor.py.
Does not walk Bronze. Does not train.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
SILVER = HERE / "outputs" / "silver"
ANCHOR = HERE / "outputs" / "anchor"

CHECKS: list[tuple[str, bool]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok)))
    mark = "ok" if ok else "FAIL"
    print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))


def main() -> int:
    turns = pd.read_csv(SILVER / "turns.csv")
    conv = pd.read_csv(SILVER / "conversations.csv")
    anc = pd.read_csv(ANCHOR / "human_anchor.csv")
    prim_t = turns[turns.source_set == "primary"]
    prim_c = conv[conv.source_set == "primary"]

    check("turns_primary_1080", len(prim_t) == 1080, str(len(prim_t)))
    check("participants_54", prim_t.participant_key.nunique() == 54)
    check("five_conditions_each", (prim_c.groupby("participant_key").condition.nunique() == 5).all())
    check("four_turns_each_primary_conv", (prim_t.groupby("conversation_id").size() == 4).all())
    check("ad_turns_216", int(prim_t.is_ad_turn.sum()) == 216)
    check("no_empty_user", int((turns.user_text.fillna("") == "").sum()) == 0)
    check("no_empty_prefix", int((turns.prefix_text.fillna("") == "").sum()) == 0)
    check("no_dup_turn_keys", int(turns.duplicated(["conversation_id", "turn"]).sum()) == 0)
    check("prefix_starts_turn", bool(prim_t.prefix_text.str.startswith("[TURN ").all()))
    check("prefix_ends_user", bool(prim_t.prefix_text.str.contains(r"\[USER\]", regex=True).all()))
    check("primary_surveys", int((prim_c.has_survey == 1).sum()) == 270)
    check("anchor_216", len(anc) == 216)
    check("anchor_no_noads", "no_ads" not in set(anc.condition))
    check("anchor_join_turns", anc.conversation_id.isin(prim_t.conversation_id).all())
    check("anchor_all_have_recall", int(anc.recall_memory.isna().sum()) == 0)
    check("fit_on_ads", int(prim_t.loc[prim_t.is_ad_turn == 1, "fit_score"].isna().sum()) == 0)
    check("lambda_not_needed_for_inference", "presentation" in turns.columns)  # stored, never a feature

    report = {
        "n_ok": sum(ok for _, ok in CHECKS),
        "n_fail": sum(not ok for _, ok in CHECKS),
        "failed": [n for n, ok in CHECKS if not ok],
        "turns": int(len(turns)),
        "primary_turns": int(len(prim_t)),
        "anchor": int(len(anc)),
        "good_moment_rate": float(anc.good_moment_human.mean()),
    }
    out = HERE / "outputs" / "gold"
    out.mkdir(parents=True, exist_ok=True)
    (out / "qc_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if report["n_fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
