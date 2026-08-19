"""Post-condition advertisement notice rates.

Reads tracked lab/crowd ``*_export.jsonl`` files and dichotomises the two
per-condition Likert items (1 = strongly disagree, 7 = strongly agree):

- ``personality_brands``: "I felt the chatbot mentioned products or brands..."
- ``personality_sponsored``: "I felt I noticed or clicked on sponsored buttons..."

A trial counts as *noticed* when either item is >= 5. The midpoint (4) is
counted as not noticed. The primary paper figures are boxplots of the raw
1--7 ratings; the dichotomised bars are kept as a supplement.
Participants are the inferential units; each person contributes at most
one row per condition.

Excluded folders: synthetic, beta, development.

Usage (from repo root):
    python analysis/behavioural/plot_ad_notice_rates.py
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import altair as alt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LOG_ROOT = ROOT / "src/project/logs/tracked"
OUT_DIR = Path(__file__).resolve().parent / "outputs" / "ad_notice"

SKIP_NAME_PARTS = ("synthetic", "beta", "development")

CONDITION_ORDER = [
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
    "no_ads",
]
CONDITION_LABELS = {
    "inline_early": "Implicit early",
    "inline_late": "Implicit late",
    "block_early": "Explicit early",
    "block_late": "Explicit late",
    "no_ads": "No advertisement",
}
FORMAT_ORDER = ["implicit", "explicit", "no_ad"]
FORMAT_LABELS = {
    "implicit": "Implicit",
    "explicit": "Explicit",
    "no_ad": "No advertisement",
}
CONDITION_COLORS = {
    "Implicit early": "#3B6EA5",
    "Implicit late": "#8FB4D4",
    "Explicit early": "#C47A2C",
    "Explicit late": "#E3B06A",
    "No advertisement": "#7D848C",
}
FORMAT_COLORS = {
    "Implicit": "#3B6EA5",
    "Explicit": "#C47A2C",
    "No advertisement": "#7D848C",
}
NOT_NOTICED_COLOR = "#E4E7EB"
NOTICE_THRESHOLD = 5
ROTATED_AXIS = alt.Axis(labelAngle=-40, labelAlign="right", labelLimit=180, labelPadding=4)


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
    text = str(path).lower()
    return any(part in text for part in SKIP_NAME_PARTS)


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


def load_trial_rows(log_root: Path) -> pd.DataFrame:
    """One row per participant × condition (latest export wins)."""
    latest: dict[str, dict[str, dict]] = defaultdict(dict)
    sources: dict[str, str] = {}
    arms: dict[str, str] = {}

    for path in sorted(log_root.glob("*/*/*_export.jsonl")):
        if _skip_path(path):
            continue
        arm = "lab" if "/lab/" in str(path).replace("\\", "/") else "crowd"
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
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
                    "condition_label": CONDITION_LABELS[condition],
                    "format": _format_of(condition),
                    "format_label": FORMAT_LABELS[_format_of(condition)],
                    "brands": brands,
                    "sponsored": sponsored,
                    "source_file": str(path.relative_to(ROOT)),
                    "timestamp": rec.get("timestamp") or "",
                }
                sources[participant] = str(path.relative_to(ROOT))
                arms[participant] = arm

    rows = [
        row
        for participant in latest
        for row in latest[participant].values()
    ]
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame["noticed_brands"] = frame["brands"].ge(NOTICE_THRESHOLD)
    frame["noticed_sponsored"] = frame["sponsored"].ge(NOTICE_THRESHOLD)
    frame["noticed"] = frame["noticed_brands"] | frame["noticed_sponsored"]
    frame["notice_label"] = frame["noticed"].map(
        {True: "Noticed", False: "Did not notice"}
    )
    return frame


def _summarise(frame: pd.DataFrame, group: list[str]) -> pd.DataFrame:
    grouped = (
        frame.groupby(group, dropna=False)
        .agg(
            n_trials=("noticed", "size"),
            n_participants=("participant_id", "nunique"),
            n_noticed=("noticed", "sum"),
            n_noticed_brands=("noticed_brands", "sum"),
            n_noticed_sponsored=("noticed_sponsored", "sum"),
        )
        .reset_index()
    )
    grouped["pct_noticed"] = 100 * grouped["n_noticed"] / grouped["n_trials"]
    grouped["pct_not_noticed"] = 100 - grouped["pct_noticed"]
    grouped["pct_noticed_brands"] = (
        100 * grouped["n_noticed_brands"] / grouped["n_trials"]
    )
    grouped["pct_noticed_sponsored"] = (
        100 * grouped["n_noticed_sponsored"] / grouped["n_trials"]
    )
    return grouped


def _stacked(summary: pd.DataFrame, category: str, category_order: list[str]) -> pd.DataFrame:
    long = summary.melt(
        id_vars=[category, "n_trials", "n_participants"],
        value_vars=["pct_noticed", "pct_not_noticed"],
        var_name="notice_key",
        value_name="percent",
    )
    long["Notice"] = long["notice_key"].map(
        {
            "pct_noticed": "Noticed",
            "pct_not_noticed": "Did not notice",
        }
    )
    long[category] = pd.Categorical(long[category], category_order, ordered=True)
    long["label"] = long["percent"].round(0).astype(int).astype(str) + "%"
    return long


def _stacked_colors(labels: list[str], colors: dict[str, str]) -> alt.Color:
    domain: list[str] = []
    range_: list[str] = []
    for label in labels:
        domain.append(f"{label}|Noticed")
        range_.append(colors[label])
        domain.append(f"{label}|Did not notice")
        range_.append(NOT_NOTICED_COLOR)
    return alt.Color(
        "bar_color:N",
        scale=alt.Scale(domain=domain, range=range_),
        legend=None,
    )


def _save(chart: alt.Chart, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    chart.save(str(stem.with_suffix(".pdf")))
    chart.save(str(stem.with_suffix(".png")), scale_factor=2)


def plot_condition(summary: pd.DataFrame, out_dir: Path) -> None:
    labels = [CONDITION_LABELS[c] for c in CONDITION_ORDER]
    plot_df = summary.copy()
    plot_df["condition_label"] = pd.Categorical(
        plot_df["condition"].map(CONDITION_LABELS), labels, ordered=True
    )
    long = _stacked(plot_df, "condition_label", labels)
    long["bar_color"] = long["condition_label"].astype(str) + "|" + long["Notice"]
    chart = (
        alt.Chart(long)
        .mark_bar(width=42)
        .encode(
            x=alt.X(
                "condition_label:N",
                sort=labels,
                title=None,
                axis=ROTATED_AXIS,
            ),
            y=alt.Y(
                "percent:Q",
                title="Participants (%)",
                scale=alt.Scale(domain=[0, 100]),
            ),
            color=_stacked_colors(labels, CONDITION_COLORS),
            order=alt.Order("Notice:N", sort="descending"),
            tooltip=[
                alt.Tooltip("condition_label:N", title="Condition"),
                alt.Tooltip("Notice:N"),
                alt.Tooltip("percent:Q", format=".1f", title="%"),
                alt.Tooltip("n_participants:Q", title="Participants"),
            ],
        )
        .properties(
            width=420,
            height=260,
            title="Advertisement notice by condition",
        )
    )
    labels_chart = (
        alt.Chart(long)
        .mark_text(color="#111111", fontSize=10, dy=8)
        .encode(
            x=alt.X("condition_label:N", sort=labels),
            y=alt.Y("percent:Q", stack="zero"),
            text="label:N",
            order=alt.Order("Notice:N", sort="descending"),
        )
    )
    _save(
        (chart + labels_chart).properties(
            padding={"left": 8, "right": 16, "top": 8, "bottom": 48}
        ),
        out_dir / "notice_by_condition",
    )


def plot_format(summary: pd.DataFrame, out_dir: Path) -> None:
    labels = [FORMAT_LABELS[k] for k in FORMAT_ORDER]
    plot_df = summary.copy()
    plot_df["format_label"] = pd.Categorical(
        plot_df["format"].map(FORMAT_LABELS), labels, ordered=True
    )
    long = _stacked(plot_df, "format_label", labels)
    long["bar_color"] = long["format_label"].astype(str) + "|" + long["Notice"]
    chart = (
        alt.Chart(long)
        .mark_bar(width=70)
        .encode(
            x=alt.X(
                "format_label:N",
                sort=labels,
                title=None,
                axis=ROTATED_AXIS,
            ),
            y=alt.Y(
                "percent:Q",
                title="Trials (%)",
                scale=alt.Scale(domain=[0, 100]),
            ),
            color=_stacked_colors(labels, FORMAT_COLORS),
            order=alt.Order("Notice:N", sort="descending"),
            tooltip=[
                alt.Tooltip("format_label:N", title="Presentation"),
                alt.Tooltip("Notice:N"),
                alt.Tooltip("percent:Q", format=".1f", title="%"),
                alt.Tooltip("n_trials:Q", title="Trials"),
                alt.Tooltip("n_participants:Q", title="Participants"),
            ],
        )
        .properties(
            width=280,
            height=260,
            title="Advertisement notice by presentation",
        )
    )
    labels_chart = (
        alt.Chart(long)
        .mark_text(color="#111111", fontSize=10, dy=8)
        .encode(
            x=alt.X("format_label:N", sort=labels),
            y=alt.Y("percent:Q", stack="zero"),
            text="label:N",
            order=alt.Order("Notice:N", sort="descending"),
        )
    )
    _save(
        (chart + labels_chart).properties(
            padding={"left": 8, "right": 16, "top": 8, "bottom": 48}
        ),
        out_dir / "notice_by_format",
    )


def _likert_long(trials: pd.DataFrame) -> pd.DataFrame:
    long = trials.melt(
        id_vars=["participant_id", "condition", "condition_label", "format", "format_label"],
        value_vars=["brands", "sponsored"],
        var_name="item_key",
        value_name="rating",
    )
    long = long.dropna(subset=["rating"])
    long["Item"] = long["item_key"].map(
        {
            "brands": "Products / brands",
            "sponsored": "Sponsored buttons",
        }
    )
    jitter = pd.util.hash_pandas_object(long["participant_id"], index=False)
    long["jitter"] = ((jitter % 1000) / 1000.0 - 0.5) * 12
    return long


def _boxplot_panel(
    frame: pd.DataFrame,
    *,
    x: str,
    sort: list[str],
    colors: dict[str, str],
    width: int,
    title: str,
    x_title: str | None = None,
    show_legend: bool = False,
) -> alt.Chart:
    color = alt.Color(
        f"{x}:N",
        sort=sort,
        scale=alt.Scale(domain=sort, range=[colors[label] for label in sort]),
        legend=alt.Legend(title=None, orient="bottom") if show_legend else None,
    )
    x_enc = alt.X(
        f"{x}:N",
        sort=sort,
        title=x_title,
        axis=ROTATED_AXIS,
    )
    y_enc = alt.Y(
        "rating:Q",
        title="Likert rating (1–7)",
        scale=alt.Scale(domain=[1, 7], nice=False),
        axis=alt.Axis(values=list(range(1, 8))),
    )
    boxes = (
        alt.Chart(frame)
        .mark_boxplot(
            extent="min-max",
            size=28,
            median={"color": "#111111", "strokeWidth": 2},
            ticks=True,
        )
        .encode(x=x_enc, y=y_enc, color=color)
    )
    points = (
        alt.Chart(frame)
        .mark_circle(size=26, opacity=0.45)
        .encode(
            x=x_enc,
            y=y_enc,
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


def plot_likert_boxes(trials: pd.DataFrame, out_dir: Path) -> None:
    long = _likert_long(trials)
    cond_labels = [CONDITION_LABELS[c] for c in CONDITION_ORDER]
    fmt_labels = [FORMAT_LABELS[k] for k in FORMAT_ORDER]

    by_condition = alt.hconcat(
        *[
            _boxplot_panel(
                long[long["Item"] == item],
                x="condition_label",
                sort=cond_labels,
                colors=CONDITION_COLORS,
                width=260,
                title=item,
            )
            for item in ("Products / brands", "Sponsored buttons")
        ],
        spacing=36,
    ).properties(
        title="Notice Likert ratings by condition",
        padding={"left": 8, "right": 16, "top": 8, "bottom": 56},
    )
    _save(by_condition, out_dir / "notice_likert_box_by_condition")

    by_format = alt.hconcat(
        *[
            _boxplot_panel(
                long[long["Item"] == item],
                x="format_label",
                sort=fmt_labels,
                colors=FORMAT_COLORS,
                width=180,
                title=item,
            )
            for item in ("Products / brands", "Sponsored buttons")
        ],
        spacing=36,
    ).properties(
        title="Notice Likert ratings by presentation",
        padding={"left": 8, "right": 16, "top": 8, "bottom": 56},
    )
    _save(by_format, out_dir / "notice_likert_box_by_format")


def plot_item_rates(summary: pd.DataFrame, out_dir: Path) -> None:
    labels = [FORMAT_LABELS[k] for k in FORMAT_ORDER]
    long = summary.melt(
        id_vars=["format"],
        value_vars=["pct_noticed_brands", "pct_noticed_sponsored"],
        var_name="item",
        value_name="percent",
    )
    long["Item"] = long["item"].map(
        {
            "pct_noticed_brands": "Products / brands",
            "pct_noticed_sponsored": "Sponsored buttons",
        }
    )
    long["format_label"] = pd.Categorical(
        long["format"].map(FORMAT_LABELS), labels, ordered=True
    )
    chart = (
        alt.Chart(long)
        .mark_bar(width=36)
        .encode(
            x=alt.X(
                "format_label:N",
                sort=labels,
                title=None,
                axis=ROTATED_AXIS,
            ),
            y=alt.Y(
                "percent:Q",
                title="Agree (rating ≥ 5), %",
                scale=alt.Scale(domain=[0, 100]),
            ),
            color=alt.Color(
                "format_label:N",
                sort=labels,
                scale=alt.Scale(
                    domain=labels,
                    range=[FORMAT_COLORS[label] for label in labels],
                ),
                legend=None,
            ),
            column=alt.Column(
                "Item:N",
                title=None,
                header=alt.Header(labelFontSize=12),
            ),
            tooltip=[
                alt.Tooltip("format_label:N", title="Presentation"),
                alt.Tooltip("Item:N"),
                alt.Tooltip("percent:Q", format=".1f"),
            ],
        )
        .properties(
            width=180,
            height=260,
            title="Notice item rates by presentation",
            padding={"left": 8, "right": 16, "top": 8, "bottom": 48},
        )
    )
    _save(chart, out_dir / "notice_items_by_format")


def main() -> None:
    if not LOG_ROOT.exists():
        raise SystemExit(f"Log root not found: {LOG_ROOT}")

    trials = load_trial_rows(LOG_ROOT)
    if trials.empty:
        raise SystemExit("No post-condition notice ratings found.")

    by_condition = _summarise(trials, ["condition"])
    by_condition["condition"] = pd.Categorical(
        by_condition["condition"], CONDITION_ORDER, ordered=True
    )
    by_condition = by_condition.sort_values("condition")
    by_format = _summarise(trials, ["format"])
    by_format["format"] = pd.Categorical(
        by_format["format"], FORMAT_ORDER, ordered=True
    )
    by_format = by_format.sort_values("format")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    trials.to_csv(OUT_DIR / "notice_trials.csv", index=False)
    by_condition.to_csv(OUT_DIR / "notice_by_condition.csv", index=False)
    by_format.to_csv(OUT_DIR / "notice_by_format.csv", index=False)

    plot_condition(by_condition, OUT_DIR)
    plot_format(by_format, OUT_DIR)
    plot_item_rates(by_format, OUT_DIR)
    plot_likert_boxes(trials, OUT_DIR)

    n_part = trials["participant_id"].nunique()
    print(f"Participants: {n_part}")
    print(f"Trials:       {len(trials)}")
    print(f"Threshold:    rating >= {NOTICE_THRESHOLD} on brands or sponsored")
    print()
    print("By condition")
    for _, row in by_condition.iterrows():
        print(
            f"  {CONDITION_LABELS[row['condition']]:<16} "
            f"{row['pct_noticed']:5.1f}% noticed "
            f"({int(row['n_noticed'])}/{int(row['n_trials'])})"
        )
    print()
    print("By presentation")
    for _, row in by_format.iterrows():
        print(
            f"  {FORMAT_LABELS[row['format']]:<16} "
            f"{row['pct_noticed']:5.1f}% noticed "
            f"({int(row['n_noticed'])}/{int(row['n_trials'])})"
        )
    print()
    print("Likert medians (Q1–Q3)")
    long = _likert_long(trials)
    for item in ("Products / brands", "Sponsored buttons"):
        print(f"  {item}")
        sub = long[long["Item"] == item]
        for fmt in FORMAT_ORDER:
            vals = sub.loc[sub["format"] == fmt, "rating"]
            if vals.empty:
                continue
            print(
                f"    {FORMAT_LABELS[fmt]:<16} "
                f"Mdn={vals.median():.0f}  "
                f"IQR={vals.quantile(0.25):.0f}–{vals.quantile(0.75):.0f}  "
                f"n={len(vals)}"
            )
    print()
    print(f"Wrote tables and figures to {OUT_DIR}")


if __name__ == "__main__":
    main()
