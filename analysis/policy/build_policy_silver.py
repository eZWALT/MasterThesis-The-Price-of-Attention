"""Build the ad-moment Silver tables from the tracked conversation logs.

The moment scorer m(prefix_k, ctx_k) is a serving-policy (pi) component:
given the conversation up to user utterance u_k it returns one scalar, how
good this moment is for *some* advertisement. Presentation lambda is not an
input and not an output; person covariates, task ids, and conditions never
reach the model. They are kept here only as training-time nuisance columns
(fold ids, label denoising) and are dropped before inference.

Zones (same contract as EEG and trajectories; Bronze is immutable):

  Bronze   src/project/logs/tracked/{lab,crowd,beta}/ and logs/production/
  Silver   this script ->
             outputs/silver/turns.csv          one row per user turn
             outputs/silver/conversations.csv  one row per condition block
             outputs/silver/build_report.json
  Anchor   build_human_anchor.py (216 ad conversations, frozen)

``source_set`` marks how a row may be used:

  primary    finished lab + crowd roster (N = 54); may carry human labels
  beta       9 complete beta testers; sensitivity / unlabeled text only
  unlabeled  unfinished, crowdfail, production leftovers; text only

``synthetic`` folders are dropped entirely.

Prefix serialisation is the single function ``serialise_prefix`` and is
duplicated verbatim in the training notebook so training and serving see
the same string.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
LOGS_ROOT = REPOSITORY_ROOT / "src/project/logs"
TRACKED_ROOT = LOGS_ROOT / "tracked"
PRODUCTION_ROOT = LOGS_ROOT / "production"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs" / "silver"

PRIMARY_ARMS = ("lab", "crowd")
DROP_TAGS = ("synthetic",)
UNLABELED_TAGS = ("unfinished", "crowdfail")

CONDITIONS = ("no_ads", "inline_early", "inline_late", "block_early", "block_late")
CONDITION_PRESENTATION = {
    "no_ads": "none",
    "inline_early": "implicit",
    "inline_late": "implicit",
    "block_early": "explicit",
    "block_late": "explicit",
}
CONDITION_TIMING = {
    "no_ads": "none",
    "inline_early": "early",
    "inline_late": "late",
    "block_early": "early",
    "block_late": "late",
}
CONDITION_START_EVENTS = {"condition_start", "condition_started"}
CONDITION_END_EVENTS = {"condition_end", "condition_complete"}
AD_EVENTS = {"ad_displayed", "ad_inserted", "ad_injected"}

# Sensitive-genre veto is a governance (Gamma) rule, not a learned output.
# Runtime ThradBERT labels are kept on the row so the notebook can apply it.
SURVEY_LIKERT_KEYS = (
    "llm_reliable", "llm_helpful", "llm_made_up", "llm_changed_mind",
    "llm_not_useful", "llm_neutral", "llm_false", "llm_addressed",
    "llm_impartial", "llm_suggestions", "llm_opinionated", "llm_not_aid",
    "llm_skeptical", "llm_relevant", "llm_convincing",
    "personality_trust", "personality_influence", "personality_changed_mind",
    "personality_brands", "personality_sponsored",
    "behaviour_pushing", "behaviour_manipulate",
)
RECALL_KEYS = ("recall_memory", "recall_trust_shift", "recall_reaction")

# Serialisation contract shared with the notebook and the serving stage.
MAX_PREFIX_TURNS = 4
ROLE_TAGS = {"user": "[USER]", "assistant": "[ASSISTANT]"}


def serialise_prefix(messages: list[dict[str, str]], turn_index: int,
                     max_turns: int = MAX_PREFIX_TURNS) -> str:
    """Serialise the last ``max_turns`` user turns (and the assistant replies
    between them) into one role-tagged string ending on the current user
    utterance. ``turn_index`` is 1-based and is clipped into the string so a
    long production chat and a 4-turn study chat share one vocabulary."""
    # keep everything from the (turn_index - max_turns + 1)-th user turn on
    user_positions = [i for i, m in enumerate(messages) if m["role"] == "user"]
    if len(user_positions) > max_turns:
        start = user_positions[-max_turns]
        messages = messages[start:]
    parts = [f"[TURN {min(turn_index, 8)}]"]
    for m in messages:
        parts.append(f"{ROLE_TAGS[m['role']]} {m['content'].strip()}")
    return "\n".join(parts)


# --------------------------------------------------------------------------
# Bronze walkers
# --------------------------------------------------------------------------

def _source_set(arm: str, folder_name: str) -> str | None:
    if any(tag in folder_name for tag in DROP_TAGS):
        return None
    if arm == "beta":
        return "beta"
    if any(tag in folder_name for tag in UNLABELED_TAGS):
        return "unlabeled"
    return "primary"


def session_folders() -> Iterator[tuple[str, str, Path]]:
    """Yield (arm, source_set, folder) for tracked sessions."""
    for arm in (*PRIMARY_ARMS, "beta"):
        arm_root = TRACKED_ROOT / arm
        if not arm_root.is_dir():
            continue
        for folder in sorted(arm_root.iterdir()):
            if not folder.is_dir():
                continue
            source_set = _source_set(arm, folder.name)
            if source_set is None:
                continue
            yield arm, source_set, folder


def session_log(folder: Path) -> Path | None:
    exports = sorted(folder.glob("*export*.jsonl"))
    if exports:
        return exports[-1]
    events = sorted(folder.glob("*events*.jsonl"))
    return events[-1] if events else None


def production_logs(seen_experiments: set[str]) -> Iterator[Path]:
    """Production JSONL not already copied into tracked (dedup on experiment_id)."""
    if not PRODUCTION_ROOT.is_dir():
        return
    for path in sorted(PRODUCTION_ROOT.rglob("*.jsonl")):
        if "events" in path.name and (path.parent / path.name.replace("events", "export")).exists():
            continue
        exp_id = _peek_experiment_id(path)
        if not exp_id or exp_id in seen_experiments:
            continue
        seen_experiments.add(exp_id)
        yield path


def _peek_experiment_id(path: Path) -> str:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                return json.loads(line).get("experiment_id", "")
            except json.JSONDecodeError:
                continue
    return ""


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


# --------------------------------------------------------------------------
# Session parser
# --------------------------------------------------------------------------

def _new_block(condition: str, data: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
    return {
        "condition": condition,
        "ad_mode": data.get("ad_mode", ""),
        "task_id": data.get("task_id", ""),
        "task_title": data.get("task_title", ""),
        "task_genre": data.get("task_genre", ""),
        "trial_index": event.get("trial_index"),
        "conversation_id": "",
        "messages": [],          # ordered {role, content, turn, timestamp, meta}
        "ad_turn": None,
        "ad_id": "",
        "ad_title": "",
        "ad_text": "",
        "ad_position": "",
        "retrieval": {},
        "runtime_labels": {},
        "survey": {},
        "conclusion": "",
        "recall": {},
        "completed": False,
    }


def parse_session(events: list[dict[str, Any]]) -> dict[str, Any]:
    session: dict[str, Any] = {
        "participant_id": "",
        "experiment_id": "",
        "study_type": "",
        "plan": [],
        "blocks": [],
        "session_complete": False,
    }
    current: dict[str, Any] | None = None
    in_warmup = False
    block_order: list[str] = []

    for event in events:
        name = event.get("event")
        data = event.get("data") or {}

        if name == "session_started":
            session["participant_id"] = data.get("participant_id", "")
            session["study_type"] = data.get("study_type", "")
            session["experiment_id"] = event.get("experiment_id", "")
            session["plan"] = [p.get("condition") for p in (data.get("conditions") or [])]
        elif name == "warmup_start":
            in_warmup = True
        elif name == "warmup_finish":
            in_warmup = False
        elif name in CONDITION_START_EVENTS:
            condition = data.get("condition")
            current = _new_block(condition, data, event)
            session["blocks"].append(current)
            block_order.append(condition)
        elif name in CONDITION_END_EVENTS:
            current = None
        elif name == "session_complete":
            session["session_complete"] = True
        elif name == "ads_recall_submitted":
            for block in session["blocks"]:
                cond = block["condition"]
                for key in RECALL_KEYS:
                    if f"{cond}_{key}" in data:
                        block["recall"][key] = data[f"{cond}_{key}"]
        elif name == "post_condition_survey_submitted":
            block = _resolve_survey_block(session, block_order, data.get("condition"))
            if block is not None:
                block["survey"] = data.get("responses") or {}
        elif current is None or in_warmup:
            continue
        elif name == "user_message":
            current["conversation_id"] = current["conversation_id"] or event.get("conversation_id", "")
            current["messages"].append({
                "role": "user",
                "content": data.get("content", "") or "",
                "turn": event.get("turn"),
                "timestamp": event.get("timestamp", ""),
                "time_to_reply_ms": data.get("time_to_reply_ms"),
                "msg_len": data.get("msg_len"),
            })
        elif name == "assistant_reply":
            current["messages"].append({
                "role": "assistant",
                "content": data.get("content", "") or "",
                "turn": event.get("turn"),
                "timestamp": event.get("timestamp", ""),
                "llm_latency_ms": data.get("llm_latency_ms"),
                "msg_len": data.get("msg_len"),
            })
        elif name == "intent_classified":
            turn = event.get("turn")
            if turn is not None and data.get("intent_label"):
                current["runtime_labels"][int(turn)] = data["intent_label"]
        elif name == "retrieval":
            current["retrieval"] = {
                "fit_score": data.get("ad_relevance_score"),
                "candidate_count": data.get("candidate_count"),
                "retrieval_latency_ms": data.get("retrieval_latency_ms"),
                "query": data.get("query", ""),
                "intent_label": data.get("intent_label", ""),
            }
            current["ad_title"] = current["ad_title"] or data.get("ad_title", "")
            current["ad_id"] = current["ad_id"] or data.get("ad_item_id", "")
        elif name in AD_EVENTS:
            if current["ad_turn"] is None:
                current["ad_turn"] = data.get("ad_turn") or event.get("turn")
            current["ad_id"] = current["ad_id"] or data.get("ad_id", "")
            current["ad_title"] = current["ad_title"] or data.get("ad_title", "")
            current["ad_text"] = current["ad_text"] or data.get("ad_text", "")
            current["ad_position"] = current["ad_position"] or data.get("position", "") or data.get("ad_position", "")
        elif name == "condition_conclusion_submitted":
            current["conclusion"] = data.get("conclusion", "") or ""
        elif name == "conversation_completed":
            current["completed"] = True
            if current["ad_turn"] is None and data.get("ad_turn"):
                current["ad_turn"] = data.get("ad_turn")
    return session


def _resolve_survey_block(session: dict[str, Any], block_order: list[str],
                          condition: Any) -> dict[str, Any] | None:
    """Early crowd sessions stored the survey condition as the 1-based plan
    index; later sessions store the condition string."""
    if isinstance(condition, str) and condition in CONDITIONS:
        for block in session["blocks"]:
            if block["condition"] == condition:
                return block
        return None
    try:
        idx = int(condition) - 1
    except (TypeError, ValueError):
        return None
    plan = session["plan"] or block_order
    if 0 <= idx < len(plan):
        target = plan[idx]
        for block in session["blocks"]:
            if block["condition"] == target:
                return block
    return None


# --------------------------------------------------------------------------
# Row builders
# --------------------------------------------------------------------------

def _parse_ts(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def turn_rows(meta: dict[str, Any], block: dict[str, Any]) -> list[dict[str, Any]]:
    """One row per user utterance. The prefix at turn k is everything up to
    and including u_k; the assistant reply a_k comes *after* the decision and
    is stored separately (``reply_after``) for the draft-reply ablation."""
    rows: list[dict[str, Any]] = []
    history: list[dict[str, str]] = []
    ad_turn = block["ad_turn"]
    msgs = block["messages"]
    user_count = 0
    for i, m in enumerate(msgs):
        if m["role"] != "user":
            continue
        user_count += 1
        k = int(m["turn"]) if m["turn"] is not None else user_count
        history.append({"role": "user", "content": m["content"]})
        reply_after = ""
        for later in msgs[i + 1:]:
            if later["role"] == "assistant":
                reply_after = later["content"]
                break
            if later["role"] == "user":
                break
        ad_before = ad_turn is not None and int(ad_turn) < k
        is_ad_turn = ad_turn is not None and int(ad_turn) == k
        # the implicit reply at the ad turn already carries the ad: mark it
        reply_contains_ad = is_ad_turn and block["ad_position"] == "inline"
        rows.append({
            **meta,
            "conversation_id": block["conversation_id"],
            "condition": block["condition"],
            "presentation": CONDITION_PRESENTATION.get(block["condition"], ""),
            "timing": CONDITION_TIMING.get(block["condition"], ""),
            "task_id": block["task_id"],
            "task_genre": block["task_genre"],
            "turn": k,
            "ad_turn": ad_turn if ad_turn is not None else "",
            "is_ad_turn": int(is_ad_turn),
            "ad_already_shown": int(ad_before),
            "turns_since_last_ad": (k - int(ad_turn)) if ad_before else "",
            "user_text": m["content"],
            "prefix_text": serialise_prefix(history, k),
            "n_prefix_messages": len(history),
            "reply_after": reply_after,
            "reply_after_contains_ad": int(reply_contains_ad),
            "time_to_reply_ms": m.get("time_to_reply_ms") if m.get("time_to_reply_ms") is not None else "",
            "msg_len": m.get("msg_len") if m.get("msg_len") is not None else len(m["content"]),
            "intent_runtime": block["runtime_labels"].get(k, ""),
            "fit_score": block["retrieval"].get("fit_score", "") if is_ad_turn else "",
            "candidate_count": block["retrieval"].get("candidate_count", "") if is_ad_turn else "",
            "ad_title": block["ad_title"] if is_ad_turn else "",
            "timestamp": m.get("timestamp", ""),
        })
        if reply_after:
            history.append({"role": "assistant", "content": reply_after})
    return rows


def conversation_row(meta: dict[str, Any], block: dict[str, Any], position: int) -> dict[str, Any]:
    survey = block["survey"] or {}
    user_turns = [m for m in block["messages"] if m["role"] == "user"]
    row = {
        **meta,
        "conversation_id": block["conversation_id"],
        "condition": block["condition"],
        "presentation": CONDITION_PRESENTATION.get(block["condition"], ""),
        "timing": CONDITION_TIMING.get(block["condition"], ""),
        "session_position": position,
        "task_id": block["task_id"],
        "task_title": block["task_title"],
        "task_genre": block["task_genre"],
        "n_user_turns": len(user_turns),
        "completed": int(block["completed"]),
        "ad_turn": block["ad_turn"] if block["ad_turn"] is not None else "",
        "ad_id": block["ad_id"],
        "ad_title": block["ad_title"],
        "ad_position": block["ad_position"],
        "fit_score": block["retrieval"].get("fit_score", ""),
        "candidate_count": block["retrieval"].get("candidate_count", ""),
        "conclusion_text": block["conclusion"],
        "has_survey": int(bool(survey)),
    }
    for key in SURVEY_LIKERT_KEYS:
        row[key] = survey.get(key, "")
    for key in RECALL_KEYS:
        row[key] = block["recall"].get(key, "")
    # post-ad user utterance (only exists after an early insertion)
    post = ""
    post_latency = ""
    if block["ad_turn"] is not None:
        for m in user_turns:
            if m["turn"] is not None and int(m["turn"]) == int(block["ad_turn"]) + 1:
                post = m["content"]
                post_latency = m.get("time_to_reply_ms") or ""
                break
    row["post_ad_user_text"] = post
    row["post_ad_time_to_reply_ms"] = post_latency
    return row


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def build() -> dict[str, Any]:
    turns: list[dict[str, Any]] = []
    conversations: list[dict[str, Any]] = []
    report: dict[str, Any] = {"sessions": Counter(), "malformed_lines": 0, "skipped": []}
    seen_experiments: set[str] = set()
    participant_index: dict[str, int] = {}

    def handle(arm: str, source_set: str, folder_name: str, path: Path) -> None:
        events, malformed = read_events(path)
        report["malformed_lines"] += malformed
        session = parse_session(events)
        if not session["blocks"]:
            report["skipped"].append(f"{folder_name}: no condition blocks")
            return
        exp_id = session["experiment_id"] or folder_name
        seen_experiments.add(exp_id)
        pid_key = f"{arm}/{folder_name}"
        participant_index.setdefault(pid_key, len(participant_index))
        meta = {
            "source_set": source_set,
            "arm": arm,
            "folder": folder_name,
            "participant_key": pid_key,
            "participant_id": session["participant_id"],
            "experiment_id": exp_id,
            "study_type": session["study_type"],
            "fold_participant": participant_index[pid_key],
        }
        report["sessions"][source_set] += 1
        for position, block in enumerate(session["blocks"], start=1):
            if not block["messages"]:
                continue
            conversations.append(conversation_row(meta, block, position))
            turns.extend(turn_rows(meta, block))

    for arm, source_set, folder in session_folders():
        path = session_log(folder)
        if path is None:
            report["skipped"].append(f"{folder.name}: no jsonl")
            continue
        handle(arm, source_set, folder.name, path)

    for path in production_logs(seen_experiments):
        handle("production", "unlabeled", path.stem, path)

    # task-grouped fold id for the leakage check (the study rotated five of
    # the 17 defined tasks through the Latin square, so this yields 5 groups)
    task_ids = sorted({r["task_id"] for r in turns if r["task_id"]})
    task_fold = {t: i for i, t in enumerate(task_ids)}
    for r in turns:
        r["fold_task"] = task_fold.get(r["task_id"], "")
    for r in conversations:
        r["fold_task"] = task_fold.get(r["task_id"], "")

    attach_trajectory_posteriors(turns, report)

    primary_turns = [r for r in turns if r["source_set"] == "primary"]
    report["summary"] = {
        "turn_rows": len(turns),
        "turn_rows_primary": len(primary_turns),
        "conversation_rows": len(conversations),
        "primary_participants": len({r["participant_key"] for r in primary_turns}),
        "primary_ad_conversations": sum(
            1 for r in conversations if r["source_set"] == "primary" and r["condition"] != "no_ads"
        ),
        "turns_by_source": dict(Counter(r["source_set"] for r in turns)),
        "ad_turn_rows_primary": sum(r["is_ad_turn"] for r in primary_turns),
        "tasks": len(task_ids),
    }
    report["sessions"] = dict(report["sessions"])
    return {"turns": turns, "conversations": conversations, "report": report}


TRAJECTORY_UTTERANCES = REPOSITORY_ROOT / "analysis/trajectories/outputs/utterances.csv"


def attach_trajectory_posteriors(turns: list[dict[str, Any]], report: dict[str, Any]) -> None:
    """Join the bare-utterance ThradBERT posterior from the trajectory Gold
    (genre_source == utterance) so the notebook can validate the judge
    against f_genre without re-running the classifier. Optional."""
    if not TRAJECTORY_UTTERANCES.exists():
        report["trajectory_join"] = "utterances.csv not found; skipped"
        return
    lookup: dict[tuple[str, int], tuple[str, str]] = {}
    with TRAJECTORY_UTTERANCES.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("genre_source") != "utterance":
                continue
            try:
                key = (row["conversation_id"], int(row["turn"]))
            except (KeyError, ValueError):
                continue
            lookup[key] = (row.get("genre", ""), row.get("p_purchasable_products", ""))
    hits = 0
    for r in turns:
        genre, p_purch = lookup.get((r["conversation_id"], int(r["turn"])), ("", ""))
        r["genre_utterance"] = genre
        r["p_purchasable"] = p_purch
        hits += bool(genre)
    report["trajectory_join"] = {"rows_matched": hits}


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    result = build()
    turns_path = args.output_dir / "turns.csv"
    conv_path = args.output_dir / "conversations.csv"
    write_csv(turns_path, result["turns"])
    write_csv(conv_path, result["conversations"])
    report = result["report"]
    report["files"] = {
        "turns.csv": file_hash(turns_path),
        "conversations.csv": file_hash(conv_path),
    }
    (args.output_dir / "build_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report["summary"], indent=2))
    print("sessions:", report["sessions"])
    if report["skipped"]:
        print(f"skipped {len(report['skipped'])} logs (see build_report.json)")


if __name__ == "__main__":
    main()
