"""Build the frozen human anchor for the ad-moment scorer.

One row per advertised conversation in the primary roster (216 = 54 x 4).
The anchor is evaluation data first and calibration data second. The
encoder never trains on it.

Label construction (format is marginalised out here, not at inference):

  1. Composites per condition, Methods / Tang scoring on 1-7 Likert,
     reverse items as 8 - x:
       credibility   = mean(llm_reliable, 8-llm_false, 8-llm_made_up)
       trust         = personality_trust
       manipulation  = mean(behaviour_pushing, behaviour_manipulate)
       helpfulness, relevance, neutrality, convincingness (secondary)
  2. Person-centred delta against that person's own no-ad conversation:
       D_i^(y) = y_{i,ad} - y_{i,no_ads}
  3. UX retention (higher = the insertion cost nothing):
       U_i = (D_cred + D_trust - D_manip) / 3
  4. Residualise on presentation lambda and task with OLS; keep the intercept
     so the scale is unchanged:
       U_i^resid = U_i - X_i beta_hat + beta_0
     Presentation is a nuisance because pi does not choose it.
  5. good_moment_human = 1[U_i^resid >= 0]   (not worse than own control)

Secondary anchor columns: recall_memory, recall_trust_shift, the raw
recall_reaction text, the post-ad user utterance (turn 3, early ads only)
and its reply latency relative to the person's median turn-3 latency.

The composites are provisional until the Goal 1 freeze; the report records
the formulas so the anchor can be rebuilt against the frozen scoring.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SILVER_DIR = HERE / "outputs" / "silver"
OUTPUT_DIR = HERE / "outputs" / "anchor"

COMPOSITES = {
    "credibility": (["llm_reliable"], ["llm_false", "llm_made_up"]),
    "helpfulness": (["llm_helpful", "llm_addressed"], ["llm_not_aid"]),
    "convincingness": (["llm_convincing", "llm_changed_mind"], ["llm_skeptical"]),
    "relevance": (["llm_relevant", "llm_suggestions"], ["llm_not_useful"]),
    "neutrality": (["llm_neutral", "llm_impartial"], ["llm_opinionated"]),
    "manipulation": (["behaviour_pushing", "behaviour_manipulate"], []),
    "trust": (["personality_trust"], []),
    "notice_sponsored": (["personality_sponsored"], []),
    "notice_brands": (["personality_brands"], []),
}
DELTA_COLS = ["credibility", "trust", "manipulation", "helpfulness",
              "relevance", "neutrality", "convincingness", "notice_sponsored"]


def score_composites(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for name, (pos, neg) in COMPOSITES.items():
        cols = [out[c].astype(float) for c in pos] + [8.0 - out[c].astype(float) for c in neg]
        out[name] = pd.concat(cols, axis=1).mean(axis=1)
    return out


def residualise(y: np.ndarray, design: pd.DataFrame) -> tuple[np.ndarray, dict[str, float]]:
    X = np.column_stack([np.ones(len(design)), design.to_numpy(dtype=float)])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta + beta[0]
    coefs = {"intercept": float(beta[0])}
    coefs.update({col: float(b) for col, b in zip(design.columns, beta[1:])})
    return resid, coefs


def build(silver_dir: Path) -> tuple[pd.DataFrame, dict]:
    conv = pd.read_csv(silver_dir / "conversations.csv")
    conv = conv[(conv.source_set == "primary") & (conv.has_survey == 1)].copy()
    conv = score_composites(conv)

    control = conv[conv.condition == "no_ads"].set_index("participant_key")
    ads = conv[conv.condition != "no_ads"].copy()
    missing = set(ads.participant_key) - set(control.index)
    if missing:
        raise RuntimeError(f"participants without a no-ad control: {sorted(missing)}")

    for col in DELTA_COLS:
        ads[f"delta_{col}"] = ads[col].to_numpy() - control.loc[ads.participant_key, col].to_numpy()
    ads["ux_retention"] = (ads.delta_credibility + ads.delta_trust - ads.delta_manipulation) / 3.0

    design = pd.get_dummies(ads[["presentation", "task_id"]], drop_first=True)
    resid, coefs = residualise(ads.ux_retention.to_numpy(dtype=float), design)
    ads["ux_retention_resid"] = resid
    ads["good_moment_human"] = (ads.ux_retention_resid >= 0).astype(int)

    # post-ad latency relative to the person's own turn-3 median (all conditions)
    turns = pd.read_csv(silver_dir / "turns.csv")
    t3 = turns[(turns.source_set == "primary") & (turns.turn == 3)]
    t3_median = t3.groupby("participant_key").time_to_reply_ms.median()
    lat = pd.to_numeric(ads.post_ad_time_to_reply_ms, errors="coerce")
    ads["post_ad_latency_ratio"] = lat.to_numpy() / t3_median.reindex(ads.participant_key).to_numpy()

    keep = [
        "participant_key", "participant_id", "experiment_id", "conversation_id",
        "arm", "condition", "presentation", "timing", "task_id", "task_genre",
        "session_position", "ad_turn", "ad_id", "ad_title", "fit_score",
        "fold_participant", "fold_task",
        *COMPOSITES.keys(),
        *[f"delta_{c}" for c in DELTA_COLS],
        "ux_retention", "ux_retention_resid", "good_moment_human",
        "recall_memory", "recall_trust_shift", "recall_reaction",
        "post_ad_user_text", "post_ad_time_to_reply_ms", "post_ad_latency_ratio",
        "conclusion_text",
    ]
    anchor = ads[keep].sort_values(["participant_key", "session_position"]).reset_index(drop=True)

    report = {
        "rows": int(len(anchor)),
        "participants": int(anchor.participant_key.nunique()),
        "by_condition": anchor.condition.value_counts().to_dict(),
        "good_moment_rate": float(anchor.good_moment_human.mean()),
        "ux_retention_mean": float(anchor.ux_retention.mean()),
        "ux_retention_by_timing": anchor.groupby("timing").ux_retention.mean().round(3).to_dict(),
        "ux_retention_by_presentation": anchor.groupby("presentation").ux_retention.mean().round(3).to_dict(),
        "residualisation_coefficients": coefs,
        "post_ad_text_rows": int((anchor.post_ad_user_text.fillna("") != "").sum()),
        "composites": {k: {"positive": v[0], "reversed": v[1]} for k, v in COMPOSITES.items()},
        "note": "composites provisional until the Goal 1 freeze; rebuild against frozen scoring",
    }
    return anchor, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--silver-dir", type=Path, default=SILVER_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    anchor, report = build(args.silver_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / "human_anchor.csv"
    anchor.to_csv(path, index=False)
    report["sha256_16"] = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    (args.output_dir / "anchor_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k not in ("composites",)}, indent=2))


if __name__ == "__main__":
    main()
