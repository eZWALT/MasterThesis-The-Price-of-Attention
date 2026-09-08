"""Walter's behavioural Gold.

Lives under ``analysis/walter/behavioural/``, not Katerina's folder.
Bronze is ``src/project/logs/tracked/{lab,crowd}/``.

Composites use the planned formulas (8-x on reverse items). The two
manipulation items and the two notice items stay as columns next to
their means. Every raw Likert item is also kept.

Usage (repo root)::

    python analysis/walter/behavioural/build_gold.py
"""

from __future__ import annotations

import json
import math
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
TRACKED_ROOT = REPOSITORY_ROOT / "src/project/logs/tracked"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs" / "gold"

EXCLUDED_FOLDER_TAGS = ("synthetic", "unfinished", "crowdfail")
PRIMARY_ARMS = ("lab", "crowd")

CONDITION_START_EVENTS = {"condition_start", "condition_started"}
CONDITION_END_EVENTS = {"condition_end", "condition_complete"}

CANONICAL_CONDITIONS = (
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
    "no_ads",
)
AD_CONDITIONS = (
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
)
PRESENTATION = {
    "no_ads": "none",
    "inline_early": "implicit",
    "inline_late": "implicit",
    "block_early": "explicit",
    "block_late": "explicit",
}
TIMING = {
    "no_ads": "none",
    "inline_early": "early",
    "inline_late": "late",
    "block_early": "early",
    "block_late": "late",
}
CONDITION_LABELS = {
    "no_ads": "a_none",
    "inline_early": "a_imp_2",
    "inline_late": "a_imp_4",
    "block_early": "a_exp_2",
    "block_late": "a_exp_4",
}

REVERSE_ITEMS = {
    "llm_false",
    "llm_made_up",
    "llm_not_aid",
    "llm_skeptical",
    "llm_not_useful",
    "llm_opinionated",
}
COMPOSITES = {
    "credibility": ("llm_reliable", "llm_false", "llm_made_up"),
    "helpfulness": ("llm_helpful", "llm_addressed", "llm_not_aid"),
    "convincingness": ("llm_skeptical", "llm_convincing", "llm_changed_mind"),
    "relevance": ("llm_not_useful", "llm_suggestions", "llm_relevant"),
    "neutrality": ("llm_neutral", "llm_impartial", "llm_opinionated"),
}
RAW_SURVEY = (
    "personality_trust",
    "personality_influence",
    "personality_changed_mind",
    "personality_brands",
    "personality_sponsored",
    "behaviour_pushing",
    "behaviour_manipulate",
)
LLM_ITEMS = (
    "llm_reliable",
    "llm_false",
    "llm_made_up",
    "llm_helpful",
    "llm_addressed",
    "llm_not_aid",
    "llm_skeptical",
    "llm_convincing",
    "llm_changed_mind",
    "llm_not_useful",
    "llm_suggestions",
    "llm_relevant",
    "llm_neutral",
    "llm_impartial",
    "llm_opinionated",
)

# Same weights as EEG Dataset A (models.tex).
CONTRAST_WEIGHTS = {
    "any_ad_vs_no_ads": {
        "inline_early": 0.25,
        "inline_late": 0.25,
        "block_early": 0.25,
        "block_late": 0.25,
        "no_ads": -1.0,
    },
    "inline_vs_block": {
        "inline_early": 0.5,
        "inline_late": 0.5,
        "block_early": -0.5,
        "block_late": -0.5,
        "no_ads": 0.0,
    },
    "early_vs_late": {
        "inline_early": 0.5,
        "inline_late": -0.5,
        "block_early": 0.5,
        "block_late": -0.5,
        "no_ads": 0.0,
    },
}

EEG_K37 = (
    REPOSITORY_ROOT
    / "analysis/eeg/statistics/outputs/sensitivity/ad_local_epochs"
    / "dataset_a/around/k37/condition_features.csv"
)
EEG_D = (
    REPOSITORY_ROOT
    / "analysis/eeg/statistics/outputs/eeg_condition_contrast_scores.csv"
)
TRAJ_CONVERSATIONS = (
    REPOSITORY_ROOT / "analysis/trajectories/outputs/conversations.csv"
)

# Dataset A k=37 medians. Sixteen confirmatory-family features, short names.
EEG_T1_COLS = {
    "fz_theta_power_db_uv2_median": "eeg_fz_theta",
    "posterior_alpha_power_db_uv2_median": "eeg_posterior_alpha",
    "theta_power_db_uv2_median": "eeg_theta",
    "alpha_power_db_uv2_median": "eeg_alpha",
    "beta_power_db_uv2_median": "eeg_beta",
    "delta_power_db_uv2_median": "eeg_delta",
    "gamma_power_db_uv2_median": "eeg_gamma",
    "faa_log_f4_minus_f3_median": "eeg_faa",
    "delta_relative_power_median": "eeg_rel_delta",
    "theta_relative_power_median": "eeg_rel_theta",
    "alpha_relative_power_median": "eeg_rel_alpha",
    "beta_relative_power_median": "eeg_rel_beta",
    "gamma_relative_power_median": "eeg_rel_gamma",
    "engagement_beta_over_alpha_theta_median": "eeg_engagement",
    "engagement_pope_frontocentral_beta_over_alpha_theta_median": "eeg_pope",
    "engagement_kislov_central_beta16_24_over_alpha8_12_median": "eeg_kislov",
}
EEG_QC_COLS = {
    "retained_epoch_count": "eeg_retained_epochs",
    "complete_epoch_count": "eeg_complete_epochs",
}
EEG_D_SHORT = {
    "fz_theta_power_db_uv2": "eeg_fz_theta",
    "posterior_alpha_power_db_uv2": "eeg_posterior_alpha",
    "theta_power_db_uv2": "eeg_theta",
    "alpha_power_db_uv2": "eeg_alpha",
    "beta_power_db_uv2": "eeg_beta",
    "delta_power_db_uv2": "eeg_delta",
    "gamma_power_db_uv2": "eeg_gamma",
    "faa_log_f4_minus_f3": "eeg_faa",
    "delta_relative_power": "eeg_rel_delta",
    "theta_relative_power": "eeg_rel_theta",
    "alpha_relative_power": "eeg_rel_alpha",
    "beta_relative_power": "eeg_rel_beta",
    "gamma_relative_power": "eeg_rel_gamma",
    "engagement_beta_over_alpha_theta": "eeg_engagement",
    "engagement_pope_frontocentral_beta_over_alpha_theta": "eeg_pope",
    "engagement_kislov_central_beta16_24_over_alpha8_12": "eeg_kislov",
}
TRAJ_KEY_OVERLAP = {
    "participant_id",
    "arm",
    "folder",
    "condition_label",
    "presentation",
    "timing",
    "task_id",
    "task_genre",
    "session_position",
    "genre_source",
    "ad_mode",
}
TRAJ_D_OUTCOMES = (
    "traj_n_shift",
    "traj_shift_rate",
    "traj_diversity",
    "traj_entropy_nats",
    "traj_entropy_normalised",
    "traj_max_persistence",
    "traj_mean_js_divergence",
    "traj_max_js_divergence",
    "traj_mean_total_variation",
    "traj_shifted_into_purchasable",
)

BEH_D_OUTCOMES = (
    "trust",
    "credibility",
    "manipulation",
    "behaviour_pushing",
    "behaviour_manipulate",
    "notice",
    "notice_brands",
    "notice_sponsored",
    "helpfulness",
    "convincingness",
    "relevance",
    "neutrality",
    "duration_sec",
    "reply_latency_ms_median",
    "user_msg_len_median",
)


def session_folders() -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    for arm in PRIMARY_ARMS:
        arm_root = TRACKED_ROOT / arm
        if not arm_root.is_dir():
            continue
        for folder in sorted(arm_root.iterdir()):
            if not folder.is_dir():
                continue
            if any(tag in folder.name for tag in EXCLUDED_FOLDER_TAGS):
                continue
            out.append((arm, folder))
    return out


def session_log(folder: Path) -> Path | None:
    exports = sorted(folder.glob("*export*.jsonl"))
    if exports:
        return exports[-1]
    events = sorted(folder.glob("*events*.jsonl"))
    return events[-1] if events else None


def read_events(path: Path) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    malformed = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                malformed += 1
    return events, malformed


def parse_ts(value: object) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def duration_seconds(start: object, end: object) -> float | None:
    a = parse_ts(start)
    b = parse_ts(end)
    if a is None or b is None:
        return None
    return (b - a).total_seconds()


def median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.fmean(values))


def invert(name: str, value: float) -> float:
    return 8.0 - value if name in REVERSE_ITEMS else value


def score_responses(resp: dict[str, Any]) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for name, items in COMPOSITES.items():
        vals: list[float] = []
        ok = True
        for item in items:
            raw = resp.get(item)
            if raw is None:
                ok = False
                break
            vals.append(invert(item, float(raw)))
        out[name] = sum(vals) / 3.0 if ok else None
    for item in RAW_SURVEY:
        raw = resp.get(item)
        out[item] = float(raw) if raw is not None else None
    for item in LLM_ITEMS:
        raw = resp.get(item)
        out[item] = float(raw) if raw is not None else None
    pushing = out["behaviour_pushing"]
    manipulate = out["behaviour_manipulate"]
    if pushing is not None and manipulate is not None:
        out["manipulation"] = (pushing + manipulate) / 2.0
    else:
        out["manipulation"] = None
    brands = out["personality_brands"]
    sponsored = out["personality_sponsored"]
    if brands is not None and sponsored is not None:
        out["notice"] = (brands + sponsored) / 2.0
    else:
        out["notice"] = None
    return out


def empty_condition(name: str) -> dict[str, Any]:
    return {
        "condition": name,
        "task_id": "",
        "task_title": "",
        "task_genre": "",
        "ad_mode": "",
        "trial_index": None,
        "duration_sec": None,
        "session_position": None,
        "condition_start_unix": None,
        "first_user_unix": None,
        "n_user_messages": 0,
        "n_assistant_replies": 0,
        "user_msg_lens": [],
        "user_word_counts": [],
        "assistant_msg_lens": [],
        "reply_latencies_ms": [],
        "llm_latencies_ms": [],
        "n_typing_events": 0,
        "n_ad_injected": 0,
        "n_ad_inserted": 0,
        "n_ad_displayed": 0,
        "n_ad_clicked": 0,
        "ad_id": "",
        "ad_title": "",
        "ad_turn": None,
        "conclusion": "",
        "survey": None,
    }


def parse_session(events: list[dict[str, Any]]) -> dict[str, Any]:
    session: dict[str, Any] = {
        "participant_id": "",
        "experiment_id": "",
        "study_type": "",
        "plan": [],
        "conditions": {name: empty_condition(name) for name in CANONICAL_CONDITIONS},
        "ocean": {},
        "demographics": {},
        "recall": {},
        "session_complete": 0,
        "messages": [],
    }
    current: str | None = None
    in_warmup = False

    def canon(raw: object) -> str | None:
        if raw is None or raw == "":
            return None
        if isinstance(raw, str) and raw in CANONICAL_CONDITIONS:
            return raw
        if isinstance(raw, int) or (isinstance(raw, str) and raw.isdigit()):
            index = int(raw)
            plan = session["plan"]
            if 1 <= index <= len(plan):
                return plan[index - 1]
        return None

    for event in events:
        name = event.get("event")
        data = event.get("data") or {}

        if name == "session_started":
            session["participant_id"] = (
                event.get("participant_id") or data.get("participant_id") or ""
            )
            session["experiment_id"] = event.get("experiment_id") or ""
            session["study_type"] = data.get("study_type") or ""
            session["plan"] = [
                planned.get("condition")
                for planned in (data.get("conditions") or [])
                if planned.get("condition")
            ]
            continue

        if name == "warmup_start":
            in_warmup = True
            continue
        if name == "warmup_finish":
            in_warmup = False
            continue

        if name in CONDITION_START_EVENTS:
            current = canon(data.get("condition") or data.get("condition_id"))
            if current is None:
                continue
            cell = session["conditions"][current]
            cell["ad_mode"] = data.get("ad_mode") or cell["ad_mode"]
            cell["task_id"] = data.get("task_id") or cell["task_id"]
            cell["task_title"] = data.get("task_title") or cell["task_title"]
            cell["task_genre"] = data.get("task_genre") or cell["task_genre"]
            cell["trial_index"] = event.get("trial_index")
            if current in session["plan"]:
                cell["session_position"] = session["plan"].index(current)
            cell["condition_start_unix"] = event.get("unix_ts")
            continue

        if name in CONDITION_END_EVENTS:
            ended = canon(
                data.get("condition_id") or data.get("condition") or current
            )
            if ended in session["conditions"]:
                cell = session["conditions"][ended]
                cell["duration_sec"] = duration_seconds(
                    data.get("trial_start_ts"), data.get("trial_end_ts")
                )
                cell["task_id"] = data.get("task_id") or cell["task_id"]
                cell["ad_mode"] = data.get("ad_mode") or cell["ad_mode"]
            current = None
            continue

        if name == "condition_conclusion_submitted":
            target = current or canon(data.get("condition") or data.get("condition_id"))
            if target in session["conditions"]:
                cell = session["conditions"][target]
                cell["conclusion"] = data.get("conclusion") or ""
                cell["task_id"] = data.get("task_id") or cell["task_id"]
                cell["task_title"] = data.get("task_title") or cell["task_title"]
            continue

        if name == "post_condition_survey_submitted":
            target = canon(data.get("condition") or event.get("condition"))
            if target in session["conditions"]:
                session["conditions"][target]["survey"] = score_responses(
                    data.get("responses") or {}
                )
            continue

        if name == "ocean_submitted":
            session["ocean"] = data.get("scores") or {}
            continue

        if name == "demographics_post_submitted":
            session["demographics"] = {
                "demo_age": data.get("demo_age"),
                "demo_sex": data.get("demo_sex"),
                "demo_education": data.get("demo_education"),
                "demo_occupation": data.get("demo_occupation"),
                "demo_familiarity": data.get("demo_familiarity"),
                "demo_frequency": data.get("demo_frequency"),
            }
            continue

        if name == "ads_recall_submitted":
            session["recall"] = data
            continue

        if name == "session_complete":
            session["session_complete"] = 1
            continue

        if current is None or in_warmup or current not in session["conditions"]:
            continue

        cell = session["conditions"][current]

        if name == "user_starts_typing":
            cell["n_typing_events"] += 1
        elif name == "user_message":
            cell["n_user_messages"] += 1
            if cell["first_user_unix"] is None:
                cell["first_user_unix"] = event.get("unix_ts")
            length = data.get("msg_len")
            content = data.get("content") or ""
            if length is None and content:
                length = len(content)
            if length is not None:
                cell["user_msg_lens"].append(float(length))
            n_words = float(len(content.split())) if content else None
            if content:
                cell["user_word_counts"].append(n_words)
            ttr = data.get("time_to_reply_ms")
            if ttr is not None:
                cell["reply_latencies_ms"].append(float(ttr))
            session["messages"].append(
                {
                    "role": "user",
                    "condition": current,
                    "turn": event.get("turn"),
                    "msg_len": length,
                    "n_words": n_words,
                    "time_to_reply_ms": ttr,
                    "unix_ts": event.get("unix_ts"),
                }
            )
        elif name == "assistant_reply":
            cell["n_assistant_replies"] += 1
            length = data.get("msg_len")
            content = data.get("content") or ""
            if length is None and content:
                length = len(content)
            if length is not None:
                cell["assistant_msg_lens"].append(float(length))
            lat = data.get("llm_latency_ms")
            if lat is not None:
                cell["llm_latencies_ms"].append(float(lat))
            session["messages"].append(
                {
                    "role": "assistant",
                    "condition": current,
                    "turn": event.get("turn"),
                    "msg_len": length,
                    "n_words": float(len(content.split())) if content else None,
                    "llm_latency_ms": lat,
                    "unix_ts": event.get("unix_ts"),
                }
            )
        elif name == "ad_injected":
            cell["n_ad_injected"] += 1
            cell["ad_id"] = data.get("ad_id") or data.get("product_id") or cell["ad_id"]
            cell["ad_title"] = data.get("ad_title") or cell["ad_title"]
            if event.get("turn") is not None:
                cell["ad_turn"] = event.get("turn")
        elif name == "ad_inserted":
            cell["n_ad_inserted"] += 1
            cell["ad_id"] = data.get("ad_id") or cell["ad_id"]
        elif name == "ad_displayed":
            # Block ads stay on screen and re-fire ad_displayed on every
            # later turn (twice per turn in the production logger), so
            # n_ad_displayed is a render count, and ad_turn must come
            # from injection. Only fall back to ad_displayed when no
            # ad_injected carried a turn.
            cell["n_ad_displayed"] += 1
            if cell["ad_turn"] is None and data.get("ad_turn") is not None:
                cell["ad_turn"] = data.get("ad_turn")
            cell["ad_id"] = data.get("ad_id") or cell["ad_id"]
        elif name == "ad_clicked":
            cell["n_ad_clicked"] += 1

    return session


def flatten_condition(arm: str, folder: str, session: dict[str, Any], cond: str) -> dict[str, Any]:
    cell = session["conditions"][cond]
    survey = cell["survey"] or {}
    user_lens = cell["user_msg_lens"]
    asst_lens = cell["assistant_msg_lens"]
    lats = cell["reply_latencies_ms"]
    llm = cell["llm_latencies_ms"]
    conclusion = cell["conclusion"] or ""
    return {
        "experiment_id": session["experiment_id"],
        "participant_id": session["participant_id"],
        "subject_id": folder,
        "folder": folder,
        "arm": arm,
        "condition": cond,
        "condition_label": CONDITION_LABELS[cond],
        "presentation": PRESENTATION[cond],
        "timing": TIMING[cond],
        "task_id": cell["task_id"],
        "task_genre": cell["task_genre"],
        "ad_mode": cell["ad_mode"],
        "trial_index": cell["trial_index"],
        "session_position": cell["session_position"],
        "credibility": survey.get("credibility"),
        "helpfulness": survey.get("helpfulness"),
        "convincingness": survey.get("convincingness"),
        "relevance": survey.get("relevance"),
        "neutrality": survey.get("neutrality"),
        "trust": survey.get("personality_trust"),
        "personality_influence": survey.get("personality_influence"),
        "personality_changed_mind": survey.get("personality_changed_mind"),
        "notice": survey.get("notice"),
        "notice_brands": survey.get("personality_brands"),
        "notice_sponsored": survey.get("personality_sponsored"),
        "behaviour_pushing": survey.get("behaviour_pushing"),
        "behaviour_manipulate": survey.get("behaviour_manipulate"),
        "manipulation": survey.get("manipulation"),
        **{item: survey.get(item) for item in LLM_ITEMS},
        "duration_sec": cell["duration_sec"],
        "time_to_first_user_sec": (
            float(cell["first_user_unix"] - cell["condition_start_unix"])
            if cell["first_user_unix"] is not None
            and cell["condition_start_unix"] is not None
            else None
        ),
        "n_user_messages": cell["n_user_messages"],
        "n_assistant_replies": cell["n_assistant_replies"],
        "user_msg_len_mean": mean(user_lens),
        "user_msg_len_median": median(user_lens),
        "user_msg_len_sum": sum(user_lens) if user_lens else None,
        "user_n_words_mean": mean(cell["user_word_counts"]),
        "user_n_words_median": median(cell["user_word_counts"]),
        "assistant_msg_len_mean": mean(asst_lens),
        "assistant_msg_len_median": median(asst_lens),
        "reply_latency_ms_mean": mean(lats),
        "reply_latency_ms_median": median(lats),
        "n_replies_with_latency": len(lats),
        "llm_latency_ms_median": median(llm),
        "n_typing_events": cell["n_typing_events"],
        "n_ad_injected": cell["n_ad_injected"],
        "n_ad_inserted": cell["n_ad_inserted"],
        "n_ad_displayed": cell["n_ad_displayed"],
        "n_ad_clicked": cell["n_ad_clicked"],
        "ad_served": int(cell["n_ad_injected"] > 0 or cell["n_ad_inserted"] > 0),
        "ad_id": cell["ad_id"],
        "ad_title": cell["ad_title"],
        "ad_turn": cell["ad_turn"],
        "conclusion": conclusion,
        "conclusion_chars": len(conclusion),
        "conclusion_n_words": len(conclusion.split()) if conclusion else 0,
    }


def flatten_ad(arm: str, folder: str, session: dict[str, Any], cond: str) -> dict[str, Any]:
    row = flatten_condition(arm, folder, session, cond)
    recall = session["recall"] or {}
    reaction = recall.get(f"{cond}_recall_reaction") or ""
    row.update(
        {
            "recall_memory": recall.get(f"{cond}_recall_memory"),
            "recall_trust_shift": recall.get(f"{cond}_recall_trust_shift"),
            "recall_reaction": reaction,
            "recall_reaction_chars": len(reaction) if reaction else 0,
        }
    )
    return row


def cronbach_alpha(items: list[list[float]]) -> float | None:
    """Items is n_rows × n_items, already reversed where needed."""
    if not items or len(items[0]) < 2:
        return None
    frame = pd.DataFrame(items)
    k = frame.shape[1]
    item_vars = frame.var(axis=0, ddof=1)
    total_var = frame.sum(axis=1).var(ddof=1)
    if total_var == 0 or item_vars.isna().any():
        return None
    return float((k / (k - 1.0)) * (1.0 - item_vars.sum() / total_var))


def contrast_score(wide: dict[str, float], weights: dict[str, float]) -> float | None:
    total = 0.0
    for cond, weight in weights.items():
        if weight == 0.0:
            continue
        value = wide.get(cond)
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        total += weight * float(value)
    return total


def build() -> dict[str, Any]:
    id_rows: list[dict[str, Any]] = []
    person_rows: list[dict[str, Any]] = []
    condition_rows: list[dict[str, Any]] = []
    ad_rows: list[dict[str, Any]] = []
    message_rows: list[dict[str, Any]] = []
    credibility_items: list[list[float]] = []
    malformed_total = 0
    n_clicked = 0

    for arm, folder in session_folders():
        path = session_log(folder)
        if path is None:
            raise SystemExit(f"No JSONL in {folder}")
        events, malformed = read_events(path)
        malformed_total += malformed
        session = parse_session(events)
        if not session["experiment_id"]:
            # Early crowd: experiment_id is only in the filename sometimes.
            stem = path.stem
            if stem.startswith("exp_"):
                session["experiment_id"] = stem.replace("_export", "")
            elif stem.startswith("export_"):
                session["experiment_id"] = stem
            else:
                session["experiment_id"] = f"{folder.name}_{stem}"
        if not session["participant_id"]:
            raise SystemExit(f"Missing participant_id in {folder}")

        id_rows.append(
            {
                "subject_id": folder.name,
                "folder": folder.name,
                "arm": arm,
                "participant_id": session["participant_id"],
                "experiment_id": session["experiment_id"],
                "unfocused": int("unfocused" in folder.name),
                "source_file": str(path.relative_to(REPOSITORY_ROOT)),
                "n_events": len(events),
                "n_malformed_lines": malformed,
                "session_complete": session["session_complete"],
            }
        )
        ocean = session["ocean"] or {}
        demo = session["demographics"] or {}
        person_rows.append(
            {
                "experiment_id": session["experiment_id"],
                "participant_id": session["participant_id"],
                "subject_id": folder.name,
                "folder": folder.name,
                "arm": arm,
                "bfi_e": ocean.get("E"),
                "bfi_a": ocean.get("A"),
                "bfi_c": ocean.get("C"),
                "bfi_n": ocean.get("N"),
                "bfi_o": ocean.get("O"),
                **demo,
            }
        )
        for cond in CANONICAL_CONDITIONS:
            row = flatten_condition(arm, folder.name, session, cond)
            condition_rows.append(row)
            n_clicked += int(row["n_ad_clicked"] or 0)
        for cond in AD_CONDITIONS:
            ad_rows.append(flatten_ad(arm, folder.name, session, cond))
        for msg in session["messages"]:
            message_rows.append(
                {
                    "experiment_id": session["experiment_id"],
                    "participant_id": session["participant_id"],
                    "subject_id": folder.name,
                    "folder": folder.name,
                    "arm": arm,
                    **msg,
                }
            )

        for event in events:
            if event.get("event") != "post_condition_survey_submitted":
                continue
            resp = (event.get("data") or {}).get("responses") or {}
            try:
                credibility_items.append(
                    [
                        float(resp["llm_reliable"]),
                        invert("llm_false", float(resp["llm_false"])),
                        invert("llm_made_up", float(resp["llm_made_up"])),
                    ]
                )
            except (KeyError, TypeError, ValueError):
                continue

    id_map = pd.DataFrame(id_rows).sort_values(["arm", "folder"])
    people = pd.DataFrame(person_rows).sort_values(["arm", "folder"])
    conditions = pd.DataFrame(condition_rows).sort_values(
        ["arm", "folder", "condition"]
    )
    ads = pd.DataFrame(ad_rows).sort_values(["arm", "folder", "condition"])
    messages = pd.DataFrame(message_rows).sort_values(
        ["arm", "folder", "condition", "turn", "role"]
    )

    traj = pd.read_csv(TRAJ_CONVERSATIONS)
    traj = traj.loc[traj["genre_source"] == "utterance"].copy()
    traj_value_cols = [
        c for c in traj.columns if c not in TRAJ_KEY_OVERLAP and c not in {"experiment_id", "condition"}
    ]
    traj = traj[["experiment_id", "condition", *traj_value_cols]].rename(
        columns={c: (c if c.startswith("traj_") else f"traj_{c}") for c in traj_value_cols}
    )

    numeric_conditions = conditions.drop(columns=["conclusion"])
    person_extra = people.drop(
        columns=["participant_id", "subject_id", "folder", "arm"], errors="ignore"
    )
    combo_all = numeric_conditions.merge(traj, on=["experiment_id", "condition"], how="left")
    combo_all = combo_all.merge(person_extra, on="experiment_id", how="left")

    eeg = pd.read_csv(EEG_K37)
    eeg = eeg.loc[eeg["condition"].isin(CANONICAL_CONDITIONS)].copy()
    eeg_keep = ["experiment_id", "condition", *EEG_T1_COLS, *EEG_QC_COLS]
    missing_eeg = [c for c in eeg_keep if c not in eeg.columns]
    if missing_eeg:
        raise SystemExit(f"EEG k=37 missing {missing_eeg}")
    eeg = eeg[eeg_keep].rename(columns={**EEG_T1_COLS, **EEG_QC_COLS})
    combo_all = combo_all.merge(eeg, on=["experiment_id", "condition"], how="left")
    combo_lab = combo_all.loc[combo_all["arm"] == "lab"].copy()

    d_frame = combo_all.copy()
    contrast_all = _build_behavioural_contrasts(
        d_frame, extra_outcomes=TRAJ_D_OUTCOMES
    )
    contrast_all = _attach_eeg_contrasts(contrast_all)
    contrast_all = contrast_all.merge(person_extra, on="experiment_id", how="left")
    contrast_lab = contrast_all.loc[contrast_all["arm"] == "lab"].copy()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    id_map.to_csv(OUTPUT_DIR / "id_map.csv", index=False)
    people.to_csv(OUTPUT_DIR / "person_features.csv", index=False)
    ads.drop(columns=["conclusion"], errors="ignore").to_csv(
        OUTPUT_DIR / "advertisement_features.csv", index=False
    )
    numeric_conditions.to_csv(OUTPUT_DIR / "condition_features.csv", index=False)
    messages.to_csv(OUTPUT_DIR / "messages.csv", index=False)
    conditions[
        [
            "experiment_id",
            "participant_id",
            "subject_id",
            "arm",
            "condition",
            "conclusion",
            "conclusion_chars",
            "conclusion_n_words",
        ]
    ].to_csv(OUTPUT_DIR / "conclusions.csv", index=False)
    combo_all.to_csv(OUTPUT_DIR / "combo_threeway.csv", index=False)
    combo_lab.to_csv(OUTPUT_DIR / "combo_threeway_lab.csv", index=False)
    contrast_all.to_csv(OUTPUT_DIR / "combo_threeway_D.csv", index=False)
    contrast_lab.to_csv(OUTPUT_DIR / "combo_threeway_lab_D.csv", index=False)
    # Same objects under the older names so existing notebook paths still work.
    combo_all.to_csv(OUTPUT_DIR / "combo_condition_all.csv", index=False)
    combo_lab.to_csv(OUTPUT_DIR / "combo_condition_lab.csv", index=False)
    contrast_all.to_csv(OUTPUT_DIR / "contrast_scores.csv", index=False)
    contrast_lab.to_csv(OUTPUT_DIR / "combo_contrast_lab.csv", index=False)

    report = _validate(
        id_map,
        people,
        numeric_conditions,
        ads,
        messages,
        combo_all,
        combo_lab,
        contrast_all,
        contrast_lab,
        malformed_total,
        n_clicked,
        cronbach_alpha(credibility_items),
        len(credibility_items),
    )
    (OUTPUT_DIR / "build_report.json").write_text(
        json.dumps(report, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    return report


def _build_behavioural_contrasts(
    conditions: pd.DataFrame,
    extra_outcomes: tuple[str, ...] = (),
) -> pd.DataFrame:
    outcomes = tuple(BEH_D_OUTCOMES) + tuple(extra_outcomes)
    rows: list[dict[str, Any]] = []
    for experiment_id, block in conditions.groupby("experiment_id", sort=False):
        wide = {
            outcome: {
                row.condition: getattr(row, outcome)
                for row in block.itertuples(index=False)
            }
            for outcome in outcomes
            if outcome in block.columns
        }
        person = {
            "experiment_id": experiment_id,
            "participant_id": block["participant_id"].iloc[0],
            "subject_id": block["subject_id"].iloc[0],
            "folder": block["folder"].iloc[0],
            "arm": block["arm"].iloc[0],
        }
        for contrast, weights in CONTRAST_WEIGHTS.items():
            for outcome, by_cond in wide.items():
                person[f"{outcome}__{contrast}"] = contrast_score(by_cond, weights)
        rows.append(person)
    return pd.DataFrame(rows).sort_values(["arm", "folder"])


def _attach_eeg_contrasts(contrasts: pd.DataFrame) -> pd.DataFrame:
    eeg_d = pd.read_csv(EEG_D)
    eeg_d = eeg_d.loc[
        eeg_d["feature"].isin(EEG_D_SHORT)
        & eeg_d["contrast_id"].isin(CONTRAST_WEIGHTS)
    ]
    out = contrasts.copy()
    for rec in eeg_d.itertuples(index=False):
        col = f"{EEG_D_SHORT[rec.feature]}__{rec.contrast_id}"
        if col not in out.columns:
            out[col] = pd.NA
        out.loc[out["subject_id"] == rec.subject_id, col] = rec.difference
    return out.sort_values(["arm", "folder"])


def _validate(
    id_map: pd.DataFrame,
    people: pd.DataFrame,
    conditions: pd.DataFrame,
    ads: pd.DataFrame,
    messages: pd.DataFrame,
    combo_all: pd.DataFrame,
    combo_lab: pd.DataFrame,
    contrast_all: pd.DataFrame,
    contrast_lab: pd.DataFrame,
    malformed_total: int,
    n_clicked: int,
    alpha: float | None,
    n_alpha: int,
) -> dict[str, Any]:
    errors: list[str] = []

    def check(ok: bool, msg: str) -> None:
        if not ok:
            errors.append(msg)

    check(len(id_map) == 54, f"id_map has {len(id_map)} rows, expected 54")
    check((id_map["arm"] == "lab").sum() == 18, "lab count")
    check((id_map["arm"] == "crowd").sum() == 36, "crowd count")
    check(len(people) == 54, "person_features rows")
    check(len(conditions) == 270, f"condition rows {len(conditions)}")
    check(len(ads) == 216, f"ad rows {len(ads)}")
    check(len(messages) == 2160, f"message rows {len(messages)}")
    check((messages["role"] == "user").sum() == 1080, "user message count")
    check((messages["role"] == "assistant").sum() == 1080, "assistant message count")
    check(conditions.duplicated(["experiment_id", "condition"]).sum() == 0, "dup conditions")
    check(id_map["experiment_id"].nunique() == 54, "unique experiments")
    check(conditions["trust"].notna().all(), "missing trust")
    check(conditions["credibility"].notna().all(), "missing credibility")
    check(conditions["manipulation"].notna().all(), "missing manipulation")
    check(conditions["notice"].notna().all(), "missing notice")
    check(conditions["behaviour_pushing"].notna().all(), "missing pushing")
    check(conditions["behaviour_manipulate"].notna().all(), "missing manipulate")
    check(conditions["llm_reliable"].notna().all(), "missing raw llm items")
    check((conditions["credibility"].between(1, 7)).all(), "credibility out of [1,7]")
    check((conditions["n_ad_clicked"] == 0).all(), "unexpected clicks")
    check(conditions["duration_sec"].notna().all(), "missing duration")
    check(conditions["session_position"].notna().all(), "missing session_position")
    check(conditions["reply_latency_ms_median"].notna().all(), "missing reply latency")
    check((conditions["n_user_messages"] >= 4).all(), "fewer than 4 user messages")
    eeg_t1 = list(EEG_T1_COLS.values())
    check(len(combo_all) == 270, "combo_all rows")
    check(combo_all["traj_n_shift"].notna().all(), "traj join holes")
    check(combo_all["traj_conversation_id"].notna().all(), "traj conversation_id holes")
    check(combo_all["bfi_e"].notna().all(), "BFI join holes")
    check(all(c in combo_all.columns for c in eeg_t1), "missing EEG 16")
    check(len(combo_lab) == 90, f"combo_lab rows {len(combo_lab)}")
    check(combo_lab[eeg_t1].notna().all().all(), "EEG k=37 join holes")
    check(
        combo_all.loc[combo_all["arm"] == "crowd", "eeg_fz_theta"].isna().all(),
        "crowd should have NA EEG",
    )
    check(len(contrast_all) == 54, f"contrast_all rows {len(contrast_all)}")
    check(len(contrast_lab) == 18, f"contrast_lab rows {len(contrast_lab)}")
    check(
        contrast_lab["eeg_fz_theta__early_vs_late"].notna().all(),
        "EEG D_i join holes",
    )
    check(
        contrast_lab["eeg_kislov__any_ad_vs_no_ads"].notna().all(),
        "EEG 16th feature D holes",
    )
    check(
        contrast_all["traj_n_shift__any_ad_vs_no_ads"].notna().all(),
        "traj D holes",
    )
    check("crowdfail" not in " ".join(id_map["folder"]), "crowdfail leaked")

    report = {
        "n_people": int(len(id_map)),
        "n_lab": int((id_map["arm"] == "lab").sum()),
        "n_crowd": int((id_map["arm"] == "crowd").sum()),
        "n_conditions": int(len(conditions)),
        "n_advertisements": int(len(ads)),
        "n_messages": int(len(messages)),
        "n_combo_all": int(len(combo_all)),
        "n_combo_lab": int(len(combo_lab)),
        "n_contrasts_all": int(len(contrast_all)),
        "n_contrasts_lab": int(len(contrast_lab)),
        "n_eeg_features": len(EEG_T1_COLS),
        "n_combo_threeway_cols": int(combo_all.shape[1]),
        "n_combo_threeway_D_cols": int(contrast_all.shape[1]),
        "n_malformed_jsonl_lines": int(malformed_total),
        "n_ad_clicked_total": int(n_clicked),
        "credibility_cronbach_alpha": alpha,
        "credibility_cronbach_n_rows": n_alpha,
        "mean_duration_sec": float(conditions["duration_sec"].mean()),
        "mean_reply_latency_ms": float(conditions["reply_latency_ms_median"].mean()),
        "mean_user_msg_len": float(conditions["user_msg_len_median"].mean()),
        "n_ad_injected_total": int(conditions["n_ad_injected"].sum()),
        "n_ad_displayed_total": int(conditions["n_ad_displayed"].sum()),
        "errors": errors,
        "ok": len(errors) == 0,
        "outputs": str(OUTPUT_DIR),
    }
    if errors:
        raise SystemExit("Gold validation failed:\n  - " + "\n  - ".join(errors))
    return report


def main() -> None:
    report = build()
    print(json.dumps({k: v for k, v in report.items() if k != "errors"}, indent=2))
    print(f"Wrote Gold tables to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
