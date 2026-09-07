"""Build the clean Gold tables the trainers will actually read.

Silver + the frozen human anchor are the source. This script does not
walk Bronze and does not call a judge.

Tables (all under outputs/gold/):

  turns_clean.csv          QC-passed turns; inference columns only +
                           fold ids (nuisance, dropped at serve time)
  human_anchor.csv         216 rows, copy of the frozen anchor + ad-turn prefix
  preference_pairs.csv     within-person pairwise on U_resid (chosen = higher)
  bandit_rows.csv          observed (state, action, reward) for IPS/OPE
  gold_report.json

Why a new Gold, given Silver is already clean
---------------------------------------------
The 4B v2 judge saturated on these study turns (median r=1.0). The
study tasks are commercial by design, so a "is there a product need?"
label has no variance here. Gold therefore treats:

  * human U_resid / good_moment_human as the only *study* supervision
  * judge scores as a documented failed weak label (optional join)
  * WildChat prefixes as the place an intent gate can be trained later

lambda / person / task / EEG never become inference columns.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SILVER = HERE / "outputs" / "silver"
ANCHOR = HERE / "outputs" / "anchor"
OUT = HERE / "outputs" / "gold"

INFERENCE_TURN_COLS = [
    "row_id", "source_set", "participant_key", "experiment_id",
    "conversation_id", "fold_participant", "fold_task",
    "turn", "is_ad_turn", "ad_already_shown", "turns_since_last_ad",
    "prefix_text", "user_text", "msg_len", "time_to_reply_ms",
    "fit_score", "intent_runtime", "genre_utterance", "p_purchasable",
]
# kept for residualisation / OPE / reports; trainers must not feed these as X
NUISANCE_COLS = [
    "condition", "presentation", "timing", "task_id", "task_genre", "arm",
]


def main() -> None:
    turns = pd.read_csv(SILVER / "turns.csv")
    turns["row_id"] = [f"real_{i}" for i in range(len(turns))]
    anc = pd.read_csv(ANCHOR / "human_anchor.csv")

    # --- turns_clean -------------------------------------------------------
    keep = [c for c in INFERENCE_TURN_COLS + NUISANCE_COLS if c in turns.columns]
    clean = turns[keep].copy()
    clean["split"] = np.where(clean.source_set == "primary", "study", "in_domain_unlabeled")

    # --- ad-turn prefixes onto the anchor ---------------------------------
    ad = turns[(turns.source_set == "primary") & (turns.is_ad_turn == 1)][
        ["conversation_id", "prefix_text", "user_text", "turn", "row_id", "p_purchasable", "intent_runtime"]
    ]
    gold_anc = anc.merge(ad, on="conversation_id", how="left", suffixes=("", "_turn"))
    if gold_anc.prefix_text.isna().any():
        raise RuntimeError("anchor rows without an ad-turn prefix")

    # --- preference pairs (within person, 4 ads) --------------------------
    pairs = []
    for pid, g in gold_anc.groupby("participant_key"):
        rows = g.to_dict("records")
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                a, b = rows[i], rows[j]
                if a["ux_retention_resid"] == b["ux_retention_resid"]:
                    continue
                chosen, rejected = (a, b) if a["ux_retention_resid"] > b["ux_retention_resid"] else (b, a)
                pairs.append({
                    "participant_key": pid,
                    "fold_participant": chosen["fold_participant"],
                    "chosen_conversation_id": chosen["conversation_id"],
                    "rejected_conversation_id": rejected["conversation_id"],
                    "chosen_prefix": chosen["prefix_text"],
                    "rejected_prefix": rejected["prefix_text"],
                    "chosen_U": chosen["ux_retention_resid"],
                    "rejected_U": rejected["ux_retention_resid"],
                    "delta_U": chosen["ux_retention_resid"] - rejected["ux_retention_resid"],
                    "chosen_timing": chosen["timing"],
                    "rejected_timing": rejected["timing"],
                    "same_task": int(chosen["task_id"] == rejected["task_id"]),
                    "same_presentation": int(chosen["presentation"] == rejected["presentation"]),
                })
    pairs_df = pd.DataFrame(pairs)

    # --- bandit rows: observed (s, a, r) ----------------------------------
    # INSERT at the assigned ad turn, reward = U_resid.
    # WAIT on the no-ad conversation, reward = 0 by construction of D_i.
    insert = gold_anc[[
        "participant_key", "fold_participant", "conversation_id", "prefix_text",
        "turn", "timing", "task_id", "ux_retention_resid", "good_moment_human",
    ]].copy()
    insert["action"] = "INSERT"
    insert["reward"] = insert.ux_retention_resid
    insert["propensity"] = 0.2  # one of five within-person arms, assigned

    noad = turns[(turns.source_set == "primary") & (turns.condition == "no_ads") & (turns.turn == 2)][
        ["participant_key", "fold_participant", "conversation_id", "prefix_text", "turn", "task_id"]
    ].copy()
    noad["action"] = "WAIT"
    noad["reward"] = 0.0
    noad["propensity"] = 0.2
    noad["timing"] = "none"
    noad["ux_retention_resid"] = 0.0
    noad["good_moment_human"] = 1  # control is the definition of "not worse"
    bandit = pd.concat([insert, noad], ignore_index=True)

    OUT.mkdir(parents=True, exist_ok=True)
    clean.to_csv(OUT / "turns_clean.csv", index=False)
    gold_anc.to_csv(OUT / "human_anchor.csv", index=False)
    pairs_df.to_csv(OUT / "preference_pairs.csv", index=False)
    bandit.to_csv(OUT / "bandit_rows.csv", index=False)

    report = {
        "turns_clean": int(len(clean)),
        "turns_study": int((clean.split == "study").sum()),
        "anchor": int(len(gold_anc)),
        "preference_pairs": int(len(pairs_df)),
        "preference_pairs_same_task": int(pairs_df.same_task.sum()) if len(pairs_df) else 0,
        "bandit_insert": int((bandit.action == "INSERT").sum()),
        "bandit_wait": int((bandit.action == "WAIT").sum()),
        "good_moment_rate": float(gold_anc.good_moment_human.mean()),
        "mean_delta_U_pairs": float(pairs_df.delta_U.mean()) if len(pairs_df) else None,
        "note": (
            "Do not train an encoder on a need/ready/safe/fit judge of these "
            "study turns: the 4B v2 labels saturate (median 1.0). Study "
            "supervision is U_resid / pairs / bandit only. Intent-gate "
            "pretraining belongs on WildChat, not on swt_* tasks."
        ),
    }
    (OUT / "gold_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
