"""Build the genre-trajectory dataset from tracked conversation logs.

Implements Definitions 1-6 of the Theoretical Foundations: the genre
trajectory \\hat{G}, transitions and shifts \\delta_k, persistence,
frequency and transition counts, diversity and entropy, and the
ad-associated genre shift \\delta^{(a)}_k.

Genres are the 13 conversation-intent classes of ThradBERT
(``Thrad/thrad-bert-conversation-classifier``), which is the same model
the live system used to route retrieval. Labels are recomputed offline
here so that the dataset carries the full class posterior rather than
only the argmax that the runtime logged.

Every Gold table that is long on labelling is long on ``genre_source``:
the two readings of Definition 1 are rows, never columns, so a downstream
reader always selects one the same way. ``conversation_id`` is the spine
and appears in every table.

Logical zones (same contract as EEG; files stay flat under outputs/):

  Bronze   tracked JSONL under src/project/logs/tracked/{lab,crowd}/
  Silver   ops in this script (filter, parse, genre inference)
           tables: classifier_inputs.csv (1,080), transition_matrices.csv (715)
  Gold     what analysis reads, two grains:
           turn:          utterances.csv (2,160), transitions.csv (1,620)
           conversation:  conversations.csv (540); advertisements.csv (216)
                          is written by classify_advertisements.py
  Off Gold build_report.json; later statistics under eda/, stages_2_4/,
           exploratory/

Do not test on the Silver tables. Heatmaps rebuild from Gold transitions.csv.

The utterance table is the core: it carries the message text, the classifier
posterior, and the transition *into* that utterance, so the common questions
need no join.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Iterator

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TRACKED_ROOT = REPOSITORY_ROOT / "src/project/logs/tracked"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"

# Folder tags that remove a session from the primary set. Note that
# ``unfocused`` is deliberately absent: those sessions are retained when the
# instruments were completed.
EXCLUDED_FOLDER_TAGS = ("synthetic", "unfinished", "crowdfail")
PRIMARY_ARMS = ("lab", "crowd")

# Runtime condition name -> the label used in the manuscript.
CONDITION_LABELS = {
    "no_ads": "a_none",
    "inline_early": "a_imp_2",
    "inline_late": "a_imp_4",
    "block_early": "a_exp_2",
    "block_late": "a_exp_4",
}
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

# Canonical ThradBERT label order, mirrored from
# src/project/core/retrieval/stages/intent.py.
GENRE_LABELS = (
    "academic_help",
    "personal_writing_or_communication",
    "writing_and_editing",
    "creative_writing_and_role_play",
    "general_guidance_and_info",
    "programming_and_data_analysis",
    "creative_ideation",
    "purchasable_products",
    "greetings_and_chitchat",
    "relationships_and_personal_reflection",
    "media_generation_or_analysis",
    "other",
    "other_obscene_or_illegal",
)
INTENT_MODEL_NAME = "Thrad/thrad-bert-conversation-classifier"
INTENT_TOKENIZER_NAME = "bert-base-uncased"
INTENT_MAX_SEQ_LENGTH = 512

# Token budget used by the live system when it classified a turn, mirrored
# from ConversationManager._classify_turn_intent so the contextual variant
# reproduces the labels that actually routed retrieval.
CONTEXT_MAX_TOKENS = 510
CONTEXT_CURRENT_BUDGET = int(CONTEXT_MAX_TOKENS * 0.50)
CONTEXT_HISTORY_BUDGET = int(CONTEXT_MAX_TOKENS * 0.35)
CONTEXT_TASK_BUDGET = CONTEXT_MAX_TOKENS - CONTEXT_CURRENT_BUDGET - CONTEXT_HISTORY_BUDGET
CONTEXT_HISTORY_MESSAGES = 3

# Two readings of Definition 1. ``utterance`` is f_genre(u_k) as the theory
# states it; ``contextual`` is what the deployed pipeline computed, where the
# task prompt and recent history are prepended to the current message.
GENRE_SOURCES = ("utterance", "contextual")

# The logging schema was renamed partway through data collection.
CONDITION_START_EVENTS = {"condition_start", "condition_started"}
CONDITION_END_EVENTS = {"condition_end", "condition_complete"}
AD_EVENTS = {"ad_displayed", "ad_inserted", "ad_injected"}

TURNS_PER_CONDITION = 4


def session_folders() -> Iterator[tuple[str, Path]]:
    """Yield (arm, folder) for every session folder in the primary set."""
    for arm in PRIMARY_ARMS:
        arm_root = TRACKED_ROOT / arm
        if not arm_root.is_dir():
            continue
        for folder in sorted(arm_root.iterdir()):
            if not folder.is_dir():
                continue
            if any(tag in folder.name for tag in EXCLUDED_FOLDER_TAGS):
                continue
            yield arm, folder


def session_log(folder: Path) -> Path | None:
    """Return the log to read for a folder, preferring exports.

    Folders may carry both ``*_events.jsonl`` and ``*_export.jsonl`` for the
    same session; reading both would double every row.
    """
    exports = sorted(folder.glob("*export*.jsonl"))
    if exports:
        return exports[-1]
    events = sorted(folder.glob("*events*.jsonl"))
    return events[-1] if events else None


def read_events(path: Path) -> tuple[list[dict[str, Any]], int]:
    """Return parsed events and the count of unparseable lines.

    One session contains a ``worker_id_set`` payload with a literal newline,
    which splits a single record across two physical lines. It carries no
    conversational content, so it is counted and skipped rather than repaired.
    """
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


def parse_session(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Walk one session in order and collect per-condition utterances.

    Condition membership is taken from the ``condition_start`` /
    ``condition_end`` bracket rather than from ``trial_index``, because the
    warm-up conversation shares a trial index with the first condition.
    """
    session: dict[str, Any] = {
        "participant_id": "",
        "experiment_id": "",
        "study_type": "",
        "task_prompts": {},
        "conditions": {},
    }
    current: str | None = None
    in_warmup = False

    for event in events:
        name = event.get("event")
        data = event.get("data") or {}

        if name == "session_started":
            session["participant_id"] = data.get("participant_id", "")
            session["study_type"] = data.get("study_type", "")
            session["experiment_id"] = event.get("experiment_id", "")
            for planned in data.get("conditions") or []:
                task = planned.get("task") or {}
                session["task_prompts"][planned.get("condition")] = task.get(
                    "participant_prompt", ""
                )
        elif name == "warmup_start":
            in_warmup = True
        elif name == "warmup_finish":
            in_warmup = False
        elif name in CONDITION_START_EVENTS:
            current = data.get("condition")
            session["conditions"].setdefault(
                current,
                {
                    "condition": current,
                    "ad_mode": data.get("ad_mode", ""),
                    "task_id": data.get("task_id", ""),
                    "task_title": data.get("task_title", ""),
                    "task_genre": data.get("task_genre", ""),
                    "relevant_categories": data.get("relevant_categories") or [],
                    "trial_index": event.get("trial_index"),
                    "utterances": [],
                    "ad_turn": None,
                    "ad_id": "",
                    "ad_title": "",
                    "runtime_labels": {},
                },
            )
        elif name in CONDITION_END_EVENTS:
            current = None
        elif current is None or in_warmup:
            continue
        elif name == "user_message":
            session["conditions"][current]["utterances"].append(
                {
                    "turn": event.get("turn"),
                    "text": data.get("content", ""),
                    "conversation_id": event.get("conversation_id", ""),
                    "timestamp": event.get("timestamp", ""),
                }
            )
        elif name == "intent_classified":
            turn = event.get("turn")
            label = data.get("intent_label")
            if turn is not None and label:
                session["conditions"][current]["runtime_labels"][turn] = label
        elif name in AD_EVENTS:
            block = session["conditions"][current]
            if block["ad_turn"] is None:
                block["ad_turn"] = data.get("ad_turn") or event.get("turn")
            block["ad_id"] = block["ad_id"] or data.get("ad_id", "")
        elif name == "retrieval":
            block = session["conditions"][current]
            block["ad_title"] = block["ad_title"] or data.get("ad_title", "")

    return session


class GenreClassifier:
    """ThradBERT wrapper returning a hard label and the full posterior."""

    def __init__(self) -> None:
        import torch
        from transformers import AutoModelForSequenceClassification, BertTokenizerFast

        self._torch = torch
        self._tokenizer = BertTokenizerFast.from_pretrained(INTENT_TOKENIZER_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(INTENT_MODEL_NAME)
        model.eval()
        self._model = model

        raw = {int(k): v for k, v in model.config.id2label.items()}
        generic = all(str(v).startswith("LABEL_") for v in raw.values())
        self._id2label = dict(enumerate(GENRE_LABELS)) if generic else raw

    def classify(self, text: str) -> tuple[str, list[float]]:
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=INTENT_MAX_SEQ_LENGTH,
        )
        inputs = {k: v for k, v in inputs.items() if k != "token_type_ids"}
        with self._torch.no_grad():
            logits = self._model(**inputs).logits
        probabilities = self._torch.softmax(logits, dim=-1)[0].tolist()
        index = int(max(range(len(probabilities)), key=probabilities.__getitem__))
        return self._id2label.get(index, f"LABEL_{index}"), probabilities

    def truncate(self, text: str, max_tokens: int) -> str:
        ids = self._tokenizer.encode(text, add_special_tokens=False, truncation=False)
        if len(ids) <= max_tokens:
            return text
        return self._tokenizer.decode(ids[:max_tokens], skip_special_tokens=True)

    def contextual_input(self, task_prompt: str, history: list[str], current: str) -> str:
        """Rebuild the string the live classifier saw: task, history, current."""
        parts: list[str] = []
        if task_prompt:
            parts.append(self.truncate(task_prompt, CONTEXT_TASK_BUDGET))
        recent = history[-CONTEXT_HISTORY_MESSAGES:]
        if recent:
            per_message = CONTEXT_HISTORY_BUDGET // len(recent)
            parts.extend(self.truncate(message, per_message) for message in recent)
        parts.append(self.truncate(current, CONTEXT_CURRENT_BUDGET))
        return " ".join(parts)


def jensen_shannon(left: list[float], right: list[float]) -> float:
    """Jensen-Shannon divergence between two posteriors, in nats.

    A continuous companion to \\delta_k. The hard shift indicator only moves
    when the argmax changes, which discards most of what the classifier says;
    this responds to any redistribution of mass. Bounded by ln 2.
    """
    total = 0.0
    for p, q in zip(left, right):
        mean = 0.5 * (p + q)
        if mean <= 0.0:
            continue
        if p > 0.0:
            total += 0.5 * p * math.log(p / mean)
        if q > 0.0:
            total += 0.5 * q * math.log(q / mean)
    return max(total, 0.0)


def total_variation(left: list[float], right: list[float]) -> float:
    """Total-variation distance between two posteriors, in [0, 1]."""
    return 0.5 * sum(abs(p - q) for p, q in zip(left, right))


def shannon_entropy(labels: Iterable[str]) -> float:
    """Entropy of the empirical genre distribution, in nats."""
    counts = Counter(labels)
    total = sum(counts.values())
    if total == 0:
        return 0.0
    # The trailing addition turns the -0.0 of a single-genre trajectory into 0.0.
    return (
        -sum((count / total) * math.log(count / total) for count in counts.values())
        + 0.0
    )


def parse_timestamp(value: str) -> datetime | None:
    """Parse a logged ISO timestamp, tolerating the trailing Z form."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def transition_matrices(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate the edge list into row-normalised from-genre x to-genre tables.

    Faceted three ways because the interesting comparison is whether the
    matrix changes when an advertisement is present, and the per-condition
    split is what the plots draw. Only observed pairs are emitted; a full
    13 x 13 grid would be almost entirely zeros.
    """
    counts: dict[tuple[str, str, str, str, str], int] = defaultdict(int)
    for row in rows:
        facets = [
            ("all", "all"),
            ("ad_presence", "no_ad" if row["position"] == "no_ad" else "advertised"),
            ("condition", row["condition_label"]),
        ]
        for kind, facet in facets:
            key = (row["genre_source"], kind, facet, row["from_genre"], row["to_genre"])
            counts[key] += 1

    totals: dict[tuple[str, str, str, str], int] = defaultdict(int)
    for (source, kind, facet, from_genre, _), count in counts.items():
        totals[(source, kind, facet, from_genre)] += count

    matrix_rows = []
    for key in sorted(counts):
        source, kind, facet, from_genre, to_genre = key
        row_total = totals[(source, kind, facet, from_genre)]
        matrix_rows.append(
            {
                "genre_source": source,
                "facet_kind": kind,
                "facet": facet,
                "from_genre": from_genre,
                "to_genre": to_genre,
                "count": counts[key],
                "row_total": row_total,
                "probability": round(counts[key] / row_total, 6),
            }
        )
    return matrix_rows


def maximal_run(labels: list[str]) -> int:
    """Length of the longest contiguous run of one genre."""
    best = current = 0
    previous: str | None = None
    for label in labels:
        current = current + 1 if label == previous else 1
        previous = label
        best = max(best, current)
    return best


def build() -> dict[str, Any]:
    classifier = GenreClassifier()
    utterance_rows: list[dict[str, Any]] = []
    conversation_rows: list[dict[str, Any]] = []
    transition_rows: list[dict[str, Any]] = []
    provenance_rows: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "sessions_read": 0,
        "sessions_skipped_no_log": [],
        "conditions_dropped_wrong_turn_count": [],
        "malformed_lines": 0,
        "runtime_label_agreement": {
            source: {"matched": 0, "compared": 0} for source in GENRE_SOURCES
        },
        "arms": Counter(),
    }

    for arm, folder in session_folders():
        log_path = session_log(folder)
        if log_path is None:
            report["sessions_skipped_no_log"].append(folder.name)
            continue

        events, malformed = read_events(log_path)
        report["malformed_lines"] += malformed
        session = parse_session(events)
        report["sessions_read"] += 1
        report["arms"][arm] += 1

        for condition, block in session["conditions"].items():
            utterances = sorted(
                (u for u in block["utterances"] if u["turn"] is not None),
                key=lambda u: u["turn"],
            )
            if len(utterances) != TURNS_PER_CONDITION:
                report["conditions_dropped_wrong_turn_count"].append(
                    {
                        "folder": folder.name,
                        "condition": condition,
                        "count": len(utterances),
                    }
                )
                continue

            task_prompt = session["task_prompts"].get(condition, "")
            labels: dict[str, list[str]] = {source: [] for source in GENRE_SOURCES}
            posteriors: dict[str, list[list[float]]] = {
                source: [] for source in GENRE_SOURCES
            }
            turn_records: list[dict[str, Any]] = []

            for index, utterance in enumerate(utterances):
                bare_label, bare_probabilities = classifier.classify(utterance["text"])
                context_input = classifier.contextual_input(
                    task_prompt,
                    [u["text"] for u in utterances[:index]],
                    utterance["text"],
                )
                context_label, context_probabilities = classifier.classify(context_input)
                labels["utterance"].append(bare_label)
                labels["contextual"].append(context_label)
                posteriors["utterance"].append(bare_probabilities)
                posteriors["contextual"].append(context_probabilities)

                runtime = block["runtime_labels"].get(utterance["turn"], "")
                if runtime:
                    for source, label in (
                        ("utterance", bare_label),
                        ("contextual", context_label),
                    ):
                        agreement = report["runtime_label_agreement"][source]
                        agreement["compared"] += 1
                        agreement["matched"] += int(runtime == label)

                previous = parse_timestamp(
                    utterances[index - 1]["timestamp"]
                ) if index else None
                moment = parse_timestamp(utterance["timestamp"])
                latency = (
                    round((moment - previous).total_seconds(), 3)
                    if moment and previous
                    else ""
                )
                turn_records.append(
                    {
                        "turn": utterance["turn"],
                        "conversation_id": utterance["conversation_id"],
                        "timestamp": utterance["timestamp"],
                        "latency_seconds": latency,
                        "characters": len(utterance["text"]),
                        "words": len(utterance["text"].split()),
                        "genre_runtime": runtime,
                        "text": utterance["text"],
                    }
                )

                provenance_rows.append(
                    {
                        "experiment_id": session["experiment_id"],
                        "condition": condition,
                        "turn": utterance["turn"],
                        "text": utterance["text"],
                        "classifier_input_contextual": context_input,
                    }
                )

            ad_turn = block["ad_turn"]
            conversation_id = turn_records[0]["conversation_id"]
            identity = {
                "conversation_id": conversation_id,
                "participant_id": session["participant_id"],
                "experiment_id": session["experiment_id"],
                "arm": arm,
                "folder": folder.name,
                "condition": condition,
                "condition_label": CONDITION_LABELS.get(condition, condition),
                "presentation": CONDITION_PRESENTATION.get(condition, ""),
                "timing": CONDITION_TIMING.get(condition, ""),
                "task_id": block["task_id"],
                "task_genre": block["task_genre"],
                "session_position": block["trial_index"],
            }

            for source in GENRE_SOURCES:
                sequence = labels[source]
                posterior = posteriors[source]
                deltas = [
                    int(sequence[k + 1] != sequence[k])
                    for k in range(TURNS_PER_CONDITION - 1)
                ]
                divergences = [
                    jensen_shannon(posterior[k], posterior[k + 1])
                    for k in range(TURNS_PER_CONDITION - 1)
                ]
                variations = [
                    total_variation(posterior[k], posterior[k + 1])
                    for k in range(TURNS_PER_CONDITION - 1)
                ]

                # a_k sits between u_k and u_{k+1}, so an advertisement shown
                # in the reply to turn k is crossed by transition (k -> k+1).
                # With T = 4 an advertisement at turn 4 has no following
                # utterance, so the ad-associated shift is undefined there.
                ad_delta: int | str = ""
                ad_divergence: float | str = ""
                if ad_turn and ad_turn < TURNS_PER_CONDITION:
                    ad_delta = deltas[ad_turn - 1]
                    ad_divergence = round(divergences[ad_turn - 1], 6)

                def transition_position(k: int) -> str:
                    """Where transition (k -> k+1) sits relative to the ad."""
                    if not ad_turn:
                        return "no_ad"
                    if k == ad_turn:
                        return "crosses_ad"
                    return "post_ad" if k > ad_turn else "pre_ad"

                for k, delta in enumerate(deltas, start=1):
                    transition_rows.append(
                        {
                            "transition_id": f"{conversation_id}:t{k}",
                            **identity,
                            "genre_source": source,
                            "k": k,
                            "from_genre": sequence[k - 1],
                            "to_genre": sequence[k],
                            "delta": delta,
                            "js_divergence": round(divergences[k - 1], 6),
                            "total_variation": round(variations[k - 1], 6),
                            "ad_turn": ad_turn or "",
                            "position": transition_position(k),
                        }
                    )

                # The transition *into* each utterance rides on the utterance
                # row, so "was this message a shift" needs no join. Turn 1 has
                # no predecessor and carries blanks.
                for index, record in enumerate(turn_records):
                    incoming = index - 1
                    row = {
                        "utterance_id": f"{conversation_id}:u{record['turn']}",
                        **identity,
                        "genre_source": source,
                        "turn": record["turn"],
                        "ad_turn": ad_turn or "",
                        "ad_id": block["ad_id"],
                        "task_title": block["task_title"],
                        "timestamp": record["timestamp"],
                        "latency_seconds": record["latency_seconds"],
                        "characters": record["characters"],
                        "words": record["words"],
                        "genre": sequence[index],
                        "top_probability": round(max(posterior[index]), 6),
                        "genre_runtime": record["genre_runtime"],
                        "matches_runtime": (
                            int(record["genre_runtime"] == sequence[index])
                            if record["genre_runtime"]
                            else ""
                        ),
                        "from_genre": sequence[incoming] if index else "",
                        "delta_in": deltas[incoming] if index else "",
                        "js_in": round(divergences[incoming], 6) if index else "",
                        "tv_in": round(variations[incoming], 6) if index else "",
                        "position_in": (
                            transition_position(index) if index else ""
                        ),
                    }
                    for name, value in zip(GENRE_LABELS, posterior[index]):
                        row[f"p_{name}"] = round(value, 6)
                    # The message itself stays in the table so no downstream
                    # reader has to go back to the JSONL to see what was
                    # classified.
                    row["text"] = record["text"]
                    utterance_rows.append(row)

                conversation_rows.append(
                    {
                        **identity,
                        "genre_source": source,
                        "ad_mode": block["ad_mode"],
                        "ad_turn": ad_turn or "",
                        "ad_id": block["ad_id"],
                        "ad_title": block["ad_title"],
                        "trajectory": "|".join(sequence),
                        "n_shift": sum(deltas),
                        "shift_rate": round(sum(deltas) / len(deltas), 6),
                        "ad_associated_shift": ad_delta,
                        "ad_associated_divergence": ad_divergence,
                        "mean_js_divergence": round(
                            sum(divergences) / len(divergences), 6
                        ),
                        "max_js_divergence": round(max(divergences), 6),
                        "mean_total_variation": round(
                            sum(variations) / len(variations), 6
                        ),
                        "diversity": len(set(sequence)),
                        "entropy_nats": round(shannon_entropy(sequence), 6),
                        "entropy_normalised": round(
                            shannon_entropy(sequence) / math.log(TURNS_PER_CONDITION), 6
                        ),
                        "max_persistence": maximal_run(sequence),
                        "shifted_into_purchasable": int(
                            any(
                                sequence[k] != sequence[k - 1]
                                and sequence[k] == "purchasable_products"
                                for k in range(1, TURNS_PER_CONDITION)
                            )
                        ),
                    }
                )

    report["arms"] = dict(report["arms"])
    report["utterances"] = len(utterance_rows)
    report["conversations"] = len(conversation_rows)
    report["transitions"] = len(transition_rows)
    for agreement in report["runtime_label_agreement"].values():
        if agreement["compared"]:
            agreement["rate"] = round(agreement["matched"] / agreement["compared"], 4)

    matrix_rows = transition_matrices(transition_rows)
    report["transition_matrix_rows"] = len(matrix_rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "conversations.csv", conversation_rows)
    write_csv(OUTPUT_DIR / "utterances.csv", utterance_rows)
    write_csv(OUTPUT_DIR / "transitions.csv", transition_rows)
    write_csv(OUTPUT_DIR / "transition_matrices.csv", matrix_rows)
    write_csv(OUTPUT_DIR / "classifier_inputs.csv", provenance_rows)
    (OUTPUT_DIR / "build_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    report = build()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
