"""Cued advertisement recall, joined to immediate notice.

Reads tracked lab/crowd ``*_export.jsonl`` files.

Recall is the end-of-session cued task (ad shown again). There is no
no-ad recall step. Items (1–7):

- ``recall_memory``: "I feel I remember this content well."
- ``recall_trust_shift``: "After seeing this content, I felt I could
  trust the chatbot overall."

Immediate notice comes from the post-condition survey
(``personality_brands``, ``personality_sponsored``). Do not treat
``recall_memory`` as objective recognition.

Excluded folders: synthetic, beta, development.

Usage (from repo root):
    python analysis/behavioural/plot_ad_recall.py
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import altair as alt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LOG_ROOT = ROOT / "src/project/logs/tracked"
OUT_DIR = Path(__file__).resolve().parent / "outputs" / "ad_recall"

SKIP_NAME_PARTS = ("synthetic", "beta", "development")

CONDITION_ORDER = [
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
]
CONDITION_LABELS = {
    "inline_early": "Implicit early",
    "inline_late": "Implicit late",
    "block_early": "Explicit early",
    "block_late": "Explicit late",
}
FORMAT_ORDER = ["implicit", "explicit"]
FORMAT_LABELS = {
    "implicit": "Implicit",
    "explicit": "Explicit",
}
CONDITION_COLORS = {
    "Implicit early": "#3B6EA5",
    "Implicit late": "#8FB4D4",
    "Explicit early": "#C47A2C",
    "Explicit late": "#E3B06A",
}
FORMAT_COLORS = {
    "Implicit": "#3B6EA5",
    "Explicit": "#C47A2C",
}
RECALL_ITEMS = {
    "memory": "Cued memory",
    "trust": "Trust after cue",
}
ROTATED_AXIS = alt.Axis(
    labelAngle=-40, labelAlign="right", labelLimit=180, labelPadding=4
)
LIKERT_Y = alt.Y(
    "rating:Q",
    title="Likert rating (1–7)",
    scale=alt.Scale(domain=[1, 7], nice=False),
    axis=alt.Axis(values=list(range(1, 8))),
)
PAD = {"left": 8, "right": 16, "top": 8, "bottom": 56}


@alt.theme.register("thesis_clean", enable=True)
def _thesis_clean_theme() -> alt.theme.ThemeConfig:
    return {
        "config": {
            "view": {"stroke": "transparent"},
            "axis": {
                "domainColor": "#333333",
                "tickColor": "#333333",
                "labelColor": "#333333",
                "titleColor": "#222222",
                "gridColor": "#E6E6E6",
                "labelFontSize": 11,
                "titleFontSize": 12,
                "titlePadding": 10,
            },
            "legend": {
                "labelFontSize": 11,
                "titleFontSize": 11,
                "orient": "bottom",
                "direction": "horizontal",
                "offset": 8,
            },
            "title": {
                "fontSize": 13,
                "color": "#111111",
                "anchor": "start",
                "offset": 12,
            },
        }
    }


def _skip_path(path: Path) -> bool:
    return any(part in str(path).lower() for part in SKIP_NAME_PARTS)


def _format_of(condition: str) -> str:
    if condition.startswith("inline_"):
        return "implicit"
    if condition.startswith("block_"):
        return "explicit"
    return "no_ad"


def _to_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _jitter(series: pd.Series, width: float = 0.28) -> pd.Series:
    hashed = pd.util.hash_pandas_object(series, index=False)
    return ((hashed % 1000) / 1000.0 - 0.5) * width


def load_notice_rows(log_root: Path) -> pd.DataFrame:
    latest: dict[str, dict[str, dict]] = defaultdict(dict)
    for path in sorted(log_root.glob("*/*/*_export.jsonl")):
        if _skip_path(path):
            continue
        arm = "lab" if "/lab/" in str(path).replace("\\", "/") else "crowd"
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                rec = json.loads(line)
                if rec.get("event") != "post_condition_survey_submitted":
                    continue
                data = rec.get("data") or {}
                condition = data.get("condition") or data.get("condition_id")
                responses = data.get("responses") or {}
                participant = rec.get("participant_id") or data.get("participant_id")
                if not participant or condition not in CONDITION_ORDER:
                    continue
                brands = _to_int(responses.get("personality_brands"))
                sponsored = _to_int(responses.get("personality_sponsored"))
                if brands is None and sponsored is None:
                    continue
                latest[participant][condition] = {
                    "participant_id": participant,
                    "arm": arm,
                    "condition": condition,
                    "brands": brands,
                    "sponsored": sponsored,
                }
    return pd.DataFrame(
        [row for rows in latest.values() for row in rows.values()]
    )


def load_recall_rows(log_root: Path) -> pd.DataFrame:
    latest: dict[str, dict] = {}
    for path in sorted(log_root.glob("*/*/*_export.jsonl")):
        if _skip_path(path):
            continue
        arm = "lab" if "/lab/" in str(path).replace("\\", "/") else "crowd"
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                rec = json.loads(line)
                if rec.get("event") != "ads_recall_submitted":
                    continue
                participant = rec.get("participant_id") or (rec.get("data") or {}).get(
                    "participant_id"
                )
                if not participant:
                    continue
                latest[participant] = {
                    "participant_id": participant,
                    "arm": arm,
                    "source_file": str(path.relative_to(ROOT)),
                    "timestamp": rec.get("timestamp") or "",
                    "data": rec.get("data") or {},
                }

    rows: list[dict] = []
    for rec in latest.values():
        data = rec["data"]
        for condition in CONDITION_ORDER:
            memory = _to_int(data.get(f"{condition}_recall_memory"))
            trust = _to_int(data.get(f"{condition}_recall_trust_shift"))
            reaction = data.get(f"{condition}_recall_reaction") or ""
            if memory is None and trust is None:
                continue
            rows.append(
                {
                    "participant_id": rec["participant_id"],
                    "arm": rec["arm"],
                    "condition": condition,
                    "condition_label": CONDITION_LABELS[condition],
                    "format": _format_of(condition),
                    "format_label": FORMAT_LABELS[_format_of(condition)],
                    "memory": memory,
                    "trust": trust,
                    "reaction": str(reaction).strip(),
                    "source_file": rec["source_file"],
                    "timestamp": rec["timestamp"],
                }
            )
    return pd.DataFrame(rows)


def join_notice(recall: pd.DataFrame, notice: pd.DataFrame) -> pd.DataFrame:
    if notice.empty:
        frame = recall.copy()
        frame["brands"] = pd.NA
        frame["sponsored"] = pd.NA
        return frame
    return recall.merge(
        notice[["participant_id", "condition", "brands", "sponsored"]],
        on=["participant_id", "condition"],
        how="left",
    )


def _save(chart: alt.Chart, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    chart.save(str(stem.with_suffix(".pdf")))
    chart.save(str(stem.with_suffix(".png")), scale_factor=2)


def _boxplot_panel(
    frame: pd.DataFrame,
    *,
    x: str,
    sort: list[str],
    colors: dict[str, str],
    y: str,
    width: int,
    title: str,
) -> alt.Chart:
    plot = frame.dropna(subset=[y]).copy()
    plot["rating"] = plot[y]
    plot["jitter"] = _jitter(plot["participant_id"] + plot["condition"])
    color = alt.Color(
        f"{x}:N",
        sort=sort,
        scale=alt.Scale(domain=sort, range=[colors[label] for label in sort]),
        legend=None,
    )
    x_enc = alt.X(f"{x}:N", sort=sort, title=None, axis=ROTATED_AXIS)
    boxes = (
        alt.Chart(plot)
        .mark_boxplot(
            extent="min-max",
            size=28,
            median={"color": "#111111", "strokeWidth": 2},
            ticks=True,
        )
        .encode(x=x_enc, y=LIKERT_Y, color=color)
    )
    points = (
        alt.Chart(plot)
        .mark_circle(size=26, opacity=0.45)
        .encode(
            x=x_enc,
            y=LIKERT_Y,
            color=color,
            xOffset=alt.XOffset("jitter:Q"),
            tooltip=[
                alt.Tooltip("participant_id:N", title="Participant"),
                alt.Tooltip(f"{x}:N"),
                alt.Tooltip("rating:Q", title="Rating"),
            ],
        )
    )
    return (boxes + points).properties(width=width, height=280, title=title)


def plot_item_boxes(
    trials: pd.DataFrame,
    *,
    x: str,
    sort: list[str],
    colors: dict[str, str],
    width: int,
    title: str,
    stem: Path,
) -> None:
    chart = alt.hconcat(
        *[
            _boxplot_panel(
                trials,
                x=x,
                sort=sort,
                colors=colors,
                y=y,
                width=width,
                title=RECALL_ITEMS[y],
            )
            for y in ("memory", "trust")
        ],
        spacing=36,
    ).properties(title=title, padding=PAD)
    _save(chart, stem)


def plot_notice_vs_recall(trials: pd.DataFrame, out_dir: Path) -> None:
    fmt_labels = [FORMAT_LABELS[k] for k in FORMAT_ORDER]
    long = trials.melt(
        id_vars=[
            "participant_id",
            "condition_label",
            "format_label",
            "memory",
        ],
        value_vars=["brands", "sponsored"],
        var_name="notice_key",
        value_name="notice",
    ).dropna(subset=["notice", "memory"])
    long["Notice item"] = long["notice_key"].map(
        {
            "brands": "Products / brands (immediate)",
            "sponsored": "Sponsored buttons (immediate)",
        }
    )
    long["jx"] = _jitter(long["participant_id"] + long["condition_label"] + "x")
    long["jy"] = _jitter(long["participant_id"] + long["condition_label"] + "y")
    long["notice_j"] = long["notice"] + long["jx"]
    long["memory_j"] = long["memory"] + long["jy"]

    diagonal = pd.DataFrame({"x": [1, 7], "y": [1, 7]})
    panels = []
    for item in (
        "Products / brands (immediate)",
        "Sponsored buttons (immediate)",
    ):
        frame = long[long["Notice item"] == item]
        line = (
            alt.Chart(diagonal)
            .mark_line(strokeDash=[4, 4], color="#BBBBBB", strokeWidth=1)
            .encode(x="x:Q", y="y:Q")
        )
        points = (
            alt.Chart(frame)
            .mark_circle(size=42, opacity=0.7)
            .encode(
                x=alt.X(
                    "notice_j:Q",
                    title="Immediate notice (1–7)",
                    scale=alt.Scale(domain=[0.6, 7.4], nice=False),
                    axis=alt.Axis(values=list(range(1, 8))),
                ),
                y=alt.Y(
                    "memory_j:Q",
                    title="Cued memory (1–7)",
                    scale=alt.Scale(domain=[0.6, 7.4], nice=False),
                    axis=alt.Axis(values=list(range(1, 8))),
                ),
                color=alt.Color(
                    "format_label:N",
                    sort=fmt_labels,
                    scale=alt.Scale(
                        domain=fmt_labels,
                        range=[FORMAT_COLORS[label] for label in fmt_labels],
                    ),
                    legend=alt.Legend(title=None),
                ),
                tooltip=[
                    alt.Tooltip("participant_id:N", title="Participant"),
                    alt.Tooltip("condition_label:N", title="Condition"),
                    alt.Tooltip("notice:Q", title="Notice"),
                    alt.Tooltip("memory:Q", title="Cued memory"),
                ],
            )
        )
        panels.append((line + points).properties(width=280, height=280, title=item))

    chart = alt.hconcat(*panels, spacing=36).properties(
        title="Immediate notice vs end-of-session cued memory",
        padding=PAD,
    )
    _save(chart, out_dir / "notice_vs_recall")


def plot_within_person(trials: pd.DataFrame, out_dir: Path) -> None:
    person = (
        trials.groupby(["participant_id", "format_label"], dropna=False)
        .agg(memory=("memory", "mean"), trust=("trust", "mean"))
        .reset_index()
    )
    wide = person.pivot(
        index="participant_id", columns="format_label", values=["memory", "trust"]
    )
    wide.columns = [f"{item}_{fmt.lower()}" for item, fmt in wide.columns]
    wide = wide.reset_index()
    if "memory_implicit" not in wide.columns or "memory_explicit" not in wide.columns:
        return
    wide = wide.dropna(subset=["memory_implicit", "memory_explicit"])
    wide["jx"] = _jitter(wide["participant_id"] + "x", width=0.16)
    wide["jy"] = _jitter(wide["participant_id"] + "y", width=0.16)
    wide["implicit_j"] = wide["memory_implicit"] + wide["jx"]
    wide["explicit_j"] = wide["memory_explicit"] + wide["jy"]
    wide["Advantage"] = pd.cut(
        wide["memory_explicit"] - wide["memory_implicit"],
        bins=[-10, -0.01, 0.01, 10],
        labels=["Implicit higher", "Tied", "Explicit higher"],
    )

    diagonal = pd.DataFrame({"x": [1, 7], "y": [1, 7]})
    line = (
        alt.Chart(diagonal)
        .mark_line(strokeDash=[4, 4], color="#BBBBBB", strokeWidth=1)
        .encode(
            x=alt.X("x:Q", title="Implicit cued memory (mean of early + late)"),
            y=alt.Y("y:Q", title="Explicit cued memory (mean of early + late)"),
        )
    )
    points = (
        alt.Chart(wide)
        .mark_circle(size=54, opacity=0.8)
        .encode(
            x=alt.X(
                "implicit_j:Q",
                title="Implicit cued memory (mean of early + late)",
                scale=alt.Scale(domain=[0.6, 7.4], nice=False),
                axis=alt.Axis(values=list(range(1, 8))),
            ),
            y=alt.Y(
                "explicit_j:Q",
                title="Explicit cued memory (mean of early + late)",
                scale=alt.Scale(domain=[0.6, 7.4], nice=False),
                axis=alt.Axis(values=list(range(1, 8))),
            ),
            color=alt.Color(
                "Advantage:N",
                scale=alt.Scale(
                    domain=["Implicit higher", "Tied", "Explicit higher"],
                    range=["#3B6EA5", "#7D848C", "#C47A2C"],
                ),
                legend=alt.Legend(title=None),
            ),
            tooltip=[
                alt.Tooltip("participant_id:N", title="Participant"),
                alt.Tooltip("memory_implicit:Q", format=".1f", title="Implicit"),
                alt.Tooltip("memory_explicit:Q", format=".1f", title="Explicit"),
            ],
        )
    )
    chart = (line + points).properties(
        width=360,
        height=360,
        title="Within-person cued memory: implicit vs explicit",
        padding=PAD,
    )
    _save(chart, out_dir / "recall_memory_implicit_vs_explicit")
    wide.to_csv(out_dir / "recall_person_format_means.csv", index=False)


def _summarise(frame: pd.DataFrame, group: list[str]) -> pd.DataFrame:
    return (
        frame.groupby(group, dropna=False)
        .agg(
            n_trials=("memory", "size"),
            n_participants=("participant_id", "nunique"),
            memory_median=("memory", "median"),
            memory_q1=("memory", lambda s: s.quantile(0.25)),
            memory_q3=("memory", lambda s: s.quantile(0.75)),
            trust_median=("trust", "median"),
            trust_q1=("trust", lambda s: s.quantile(0.25)),
            trust_q3=("trust", lambda s: s.quantile(0.75)),
        )
        .reset_index()
    )


def _write_gallery(out_dir: Path) -> None:
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Advertisement recall figures</title>
  <style>
    body { font-family: Georgia, serif; margin: 32px auto; max-width: 1100px; color: #111; background: #fafafa; }
    h1 { font-size: 1.4rem; font-weight: 600; }
    h2 { font-size: 1.05rem; margin-top: 2rem; }
    img { width: 100%; height: auto; background: #fff; border: 1px solid #ddd; }
    p { color: #444; }
  </style>
</head>
<body>
  <h1>Advertisement recall — cued memory</h1>
  <p>End-of-session ratings after the advertisement is shown again. Not free recall and not objective recognition. Implicit = blue; explicit = orange.</p>
  <h2>By condition</h2>
  <img src="recall_box_by_condition.png?v=1" alt="Cued memory and trust by condition" />
  <h2>By presentation</h2>
  <img src="recall_box_by_format.png?v=1" alt="Cued memory and trust by presentation" />
  <h2>Immediate notice vs cued memory</h2>
  <p>Dashed line is equal Likert values, not a fitted model. Left: brand mention. Right: sponsored buttons (the notice item that tracks presentation).</p>
  <img src="notice_vs_recall.png?v=1" alt="Immediate notice versus cued memory" />
  <h2>Within-person implicit vs explicit memory</h2>
  <p>One point per participant. Points above the diagonal remembered the explicit ad better than the implicit one.</p>
  <img src="recall_memory_implicit_vs_explicit.png?v=1" alt="Within-person implicit versus explicit cued memory" />
</body>
</html>
"""
    (out_dir / "gallery.html").write_text(html, encoding="utf-8")


def _print_iqr(trials: pd.DataFrame, item: str, group: str, order: list[str], labels: dict[str, str]) -> None:
    print(f"  {RECALL_ITEMS[item]}")
    for key in order:
        vals = trials.loc[trials[group] == key, item].dropna()
        if vals.empty:
            continue
        print(
            f"    {labels[key]:<16} "
            f"Mdn={vals.median():.0f}  "
            f"IQR={vals.quantile(0.25):.0f}–{vals.quantile(0.75):.0f}  "
            f"n={len(vals)}"
        )


def main() -> None:
    if not LOG_ROOT.exists():
        raise SystemExit(f"Log root not found: {LOG_ROOT}")

    recall = load_recall_rows(LOG_ROOT)
    if recall.empty:
        raise SystemExit("No ads_recall_submitted events found.")
    notice = load_notice_rows(LOG_ROOT)
    trials = join_notice(recall, notice)

    cond_labels = [CONDITION_LABELS[c] for c in CONDITION_ORDER]
    fmt_labels = [FORMAT_LABELS[k] for k in FORMAT_ORDER]

    by_condition = _summarise(trials, ["condition"])
    by_condition["condition"] = pd.Categorical(
        by_condition["condition"], CONDITION_ORDER, ordered=True
    )
    by_condition = by_condition.sort_values("condition")
    by_format = _summarise(trials, ["format"])
    by_format["format"] = pd.Categorical(by_format["format"], FORMAT_ORDER, ordered=True)
    by_format = by_format.sort_values("format")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    trials.to_csv(OUT_DIR / "recall_trials.csv", index=False)
    by_condition.to_csv(OUT_DIR / "recall_by_condition.csv", index=False)
    by_format.to_csv(OUT_DIR / "recall_by_format.csv", index=False)

    plot_item_boxes(
        trials,
        x="condition_label",
        sort=cond_labels,
        colors=CONDITION_COLORS,
        width=220,
        title="Cued recall ratings by condition",
        stem=OUT_DIR / "recall_box_by_condition",
    )
    plot_item_boxes(
        trials,
        x="format_label",
        sort=fmt_labels,
        colors=FORMAT_COLORS,
        width=160,
        title="Cued recall ratings by presentation",
        stem=OUT_DIR / "recall_box_by_format",
    )
    plot_notice_vs_recall(trials, OUT_DIR)
    plot_within_person(trials, OUT_DIR)
    _write_gallery(OUT_DIR)

    n_part = trials["participant_id"].nunique()
    print(f"Participants: {n_part}")
    print(f"Recall trials: {len(trials)}")
    print()
    print("Cued memory (Q1–Q3)")
    _print_iqr(trials, "memory", "format", FORMAT_ORDER, FORMAT_LABELS)
    print("Trust after cue (Q1–Q3)")
    _print_iqr(trials, "trust", "format", FORMAT_ORDER, FORMAT_LABELS)
    print()
    paired = trials.dropna(subset=["sponsored", "memory"])
    if not paired.empty:
        print("Spearman: immediate notice vs cued memory")
        for col, label in (
            ("sponsored", "Sponsored buttons"),
            ("brands", "Products / brands"),
        ):
            sub = trials.dropna(subset=[col, "memory"])
            rho = sub[col].corr(sub["memory"], method="spearman")
            print(f"  {label:<22} ρ={rho:.2f}  n={len(sub)}")
            for fmt in FORMAT_ORDER:
                fsub = sub[sub["format"] == fmt]
                frho = fsub[col].corr(fsub["memory"], method="spearman")
                print(f"    {FORMAT_LABELS[fmt]:<20} ρ={frho:.2f}  n={len(fsub)}")
    print()
    print(f"Wrote tables and figures to {OUT_DIR}")


if __name__ == "__main__":
    main()
