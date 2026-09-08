# Calculate a separate Cronbach's alpha for each questionnaire dimension used in
# the participant-condition score construction in Analysis_AdsTalkBack.
# These dimensions are built from the raw post-condition survey items in the JSONL
# responses for event == "post_condition_survey_submitted".

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


SCALE_GROUPS = {
    "credibility": {
        "items": ["llm_reliable", "llm_false", "llm_made_up"],
        "reverse": {"llm_false", "llm_made_up"},
    },
    "helpfulness": {
        "items": ["llm_helpful", "llm_addressed", "llm_not_aid"],
        "reverse": {"llm_not_aid"},
    },
    "convincingness": {
        "items": ["llm_skeptical", "llm_convincing", "llm_changed_mind"],
        "reverse": {"llm_skeptical"},
    },
    "relevance": {
        "items": ["llm_not_useful", "llm_suggestions", "llm_relevant"],
        "reverse": {"llm_not_useful"},
    },
    "neutrality": {
        "items": ["llm_neutral", "llm_impartial", "llm_opinionated"],
        "reverse": {"llm_opinionated"},
    },
    "behaviour_pushing": {
        "items": ["behaviour_pushing"],
        "reverse": set(),
    },
    "behaviour_manipulate": {
        "items": ["behaviour_manipulate"],
        "reverse": set(),
    },
}


def find_project_root(start: Path) -> Path:
    seen = set()
    for candidate in [start.resolve(), *start.resolve().parents]:
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / "src" / "project" / "logs" / "tracked" / "lab").exists():
            return candidate
    return start.resolve()


def reverse_code(value: float) -> float:
    return 8.0 - float(value)


def parse_jsonl_event_rows(root: Path) -> list[dict[str, float]]:
    records: list[dict[str, float]] = []

    lab_root = root / "src" / "project" / "logs" / "tracked" / "lab"
    if not lab_root.exists():
        fallback = root.parent / "src" / "project" / "logs" / "tracked" / "lab"
        lab_root = fallback if fallback.exists() else lab_root

    files = sorted(lab_root.rglob("*_export.jsonl"))
    if not files:
        files = sorted(lab_root.rglob("*_events.jsonl"))
    if not files:
        raise FileNotFoundError(f"No export/event JSONL files found under {lab_root}")

    for file_path in files:
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if rec.get("event") != "post_condition_survey_submitted":
                    continue

                data = rec.get("data", {})
                responses = data.get("responses", {})
                if not isinstance(responses, dict):
                    continue

                item_values: dict[str, float] = {}
                for key in sorted(responses):
                    value = responses.get(key)
                    if value is None:
                        continue
                    try:
                        numeric = float(value)
                    except (TypeError, ValueError):
                        continue
                    # Keep answers as logged. Reverse once, in cronbach_alpha_for_items.
                    item_values[key] = numeric

                if item_values:
                    records.append(item_values)

    return records


def cronbach_alpha_for_items(frame: pd.DataFrame, item_names: list[str], reverse_items: set[str]) -> tuple[float | None, int, str]:
    valid_items = [name for name in item_names if name in frame.columns]
    if len(valid_items) < 2:
        return None, len(frame), "Cronbach's alpha is undefined for a single-item scale."

    sub = frame[valid_items].copy()
    # Reverse once here (8-x). Do not also reverse in parse_jsonl_event_rows.
    for item in reverse_items:
        if item in sub.columns:
            sub[item] = reverse_code(sub[item])

    complete = sub.dropna()
    if complete.empty:
        return None, 0, "No complete cases for this scale."

    k = complete.shape[1]
    if k < 2:
        return None, len(complete), "Cronbach's alpha is undefined for a single-item scale."

    item_variances = complete.var(ddof=1, axis=0)
    total_variance = complete.sum(axis=1).var(ddof=1)

    if total_variance == 0 or pd.isna(total_variance):
        return None, len(complete), "Total variance is zero; alpha is undefined."

    alpha = (k / (k - 1)) * (1 - item_variances.sum() / total_variance)
    return float(alpha), len(complete), "OK"


repo_root = find_project_root(Path.cwd())
rows = parse_jsonl_event_rows(repo_root)
if not rows:
    raise FileNotFoundError("No post_condition_survey_submitted responses found in the tracked lab logs.")

response_df = pd.DataFrame(rows)

print("Cronbach's alpha by questionnaire dimension")
print("=" * 52)

for dimension, cfg in SCALE_GROUPS.items():
    alpha_value, n_used, status = cronbach_alpha_for_items(response_df, cfg["items"], cfg["reverse"])
    if alpha_value is None:
        print(f"{dimension:<20}: alpha undefined | {status}")
    else:
        print(f"{dimension:<20}: alpha = {alpha_value:.4f} | valid rows = {n_used}")

print("\nNote: behaviour_pushing and behaviour_manipulate are single-item measures, so Cronbach's alpha is not defined for them.")
