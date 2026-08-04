"""Descriptive EEG distribution figures for thesis / Overleaf.

Writes vector PDF + PNG under outputs/figures/descriptive/, separate from the
publication figure_01… figure_06 suite.

Usage (from repo root):
    python analysis/eeg/analysis/plot_descriptive_distributions.py
"""

from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
MARKER_DIR = ROOT / "src/project/logs/xdf/silver/canonical_markers"
AUDIT_PATH = (
    ROOT / "src/project/logs/xdf/silver/audits/xdf_mne_acquisition_audit.csv"
)
OUT_ROOT = Path(__file__).resolve().parent / "outputs" / "figures" / "descriptive"

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
    "no_ads": "No ads",
}
CONDITION_LABEL_ORDER = [CONDITION_LABELS[c] for c in CONDITION_ORDER]


@alt.theme.register("thesis_clean", enable=True)
def _thesis_clean_theme() -> alt.theme.ThemeConfig:
    """Thesis-friendly Altair theme (no chartjunk)."""
    return {
        "config": {
            "view": {"stroke": "transparent"},
            "axis": {
                "domainColor": "#333333",
                "tickColor": "#333333",
                "labelColor": "#333333",
                "titleColor": "#222222",
                "gridColor": "#E6E6E6",
                "gridOpacity": 1,
                "labelFontSize": 11,
                "titleFontSize": 12,
                "titlePadding": 10,
            },
            "legend": {
                "labelFontSize": 11,
                "title": None,
                "orient": "top-right",
                "offset": 4,
            },
            "title": {
                "fontSize": 13,
                "color": "#111111",
                "anchor": "start",
                "offset": 12,
            },
            "range": {
                "category": ["#3B6EA5", "#A8B0BD"],
            },
        }
    }


def _save_chart(chart: alt.Chart, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    chart.save(stem.with_suffix(".pdf"))
    chart.save(stem.with_suffix(".png"), scale_factor=2)


def condition_blocks() -> pd.DataFrame:
    """One row per eligible subject × condition presentation."""
    rows: list[dict] = []
    for csv_path in sorted(MARKER_DIR.glob("lab_subject_*.csv")):
        if "crowdfail" in csv_path.name:
            continue
        frame = pd.read_csv(csv_path).sort_values("eeg_offset_s")
        starts = frame[frame["event"] == "condition_start"].reset_index(drop=True)
        ends = frame[
            frame["event"] == "condition_conclusion_submitted"
        ].reset_index(drop=True)
        n = min(len(starts), len(ends))
        for i in range(n):
            condition = starts.loc[i, "condition"]
            if condition not in CONDITION_ORDER:
                continue
            rows.append(
                {
                    "subject_id": csv_path.stem,
                    "presentation_slot": i + 1,
                    "condition": condition,
                    "condition_label": CONDITION_LABELS[condition],
                    "duration_s": float(
                        ends.loc[i, "eeg_offset_s"] - starts.loc[i, "eeg_offset_s"]
                    ),
                }
            )
    return pd.DataFrame(rows)


def plot_condition_block_duration(out_dir: Path, raw: pd.DataFrame) -> Path:
    stats = (
        raw.groupby(["condition", "condition_label"], as_index=False)["duration_s"]
        .agg(Mean="mean", Median="median")
        .melt(
            id_vars=["condition", "condition_label"],
            value_vars=["Mean", "Median"],
            var_name="Statistic",
            value_name="duration_s",
        )
    )
    stats["label_text"] = stats["duration_s"].round(0).astype(int).astype(str)
    stats["condition_label"] = pd.Categorical(
        stats["condition_label"],
        categories=CONDITION_LABEL_ORDER,
        ordered=True,
    )

    n_subjects = raw["subject_id"].nunique()
    base = alt.Chart(stats).encode(
        x=alt.X(
            "condition_label:N",
            title="Condition",
            sort=CONDITION_LABEL_ORDER,
            axis=alt.Axis(labelAngle=-20),
        ),
        xOffset="Statistic:N",
        color=alt.Color(
            "Statistic:N",
            scale=alt.Scale(range=["#3B6EA5", "#B0B7C3"]),
        ),
    )
    bars = base.mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2).encode(
        y=alt.Y("duration_s:Q", title="Condition-block duration (s)"),
        tooltip=[
            alt.Tooltip("condition_label:N", title="Condition"),
            alt.Tooltip("Statistic:N"),
            alt.Tooltip("duration_s:Q", title="Duration (s)", format=".1f"),
        ],
    )
    labels = base.mark_text(dy=-8, fontSize=10, color="#222222").encode(
        y=alt.Y("duration_s:Q"),
        text="label_text:N",
    )
    chart = (bars + labels).properties(
        width=420,
        height=280,
        title=f"Condition-block duration by condition (lab EEG, n = {n_subjects})",
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out_dir / "data.csv", index=False)
    stats.to_csv(out_dir / "summary.csv", index=False)
    stem = out_dir / "condition_block_duration"
    _save_chart(chart, stem)
    return stem.with_suffix(".pdf")


def plot_condition_order_balance(out_dir: Path, raw: pd.DataFrame) -> Path:
    """Heatmap: how often each condition landed in presentation slot 1…5."""
    n_subjects = raw["subject_id"].nunique()
    expected = n_subjects / len(CONDITION_ORDER)

    counts = (
        raw.groupby(["condition_label", "presentation_slot"], as_index=False)
        .size()
        .rename(columns={"size": "n"})
    )
    # fill missing cells with 0
    full = (
        pd.MultiIndex.from_product(
            [CONDITION_LABEL_ORDER, range(1, 6)],
            names=["condition_label", "presentation_slot"],
        )
        .to_frame(index=False)
        .merge(counts, on=["condition_label", "presentation_slot"], how="left")
        .fillna({"n": 0})
    )
    full["n"] = full["n"].astype(int)
    full["label_text"] = full["n"].astype(str)
    full["condition_label"] = pd.Categorical(
        full["condition_label"], categories=CONDITION_LABEL_ORDER, ordered=True
    )

    heat = (
        alt.Chart(full)
        .mark_rect(stroke="#FFFFFF", strokeWidth=1)
        .encode(
            x=alt.X(
                "presentation_slot:O",
                title="Presentation slot",
                axis=alt.Axis(labelExpr="'Slot ' + datum.value"),
            ),
            y=alt.Y(
                "condition_label:N",
                title="Condition",
                sort=CONDITION_LABEL_ORDER,
            ),
            color=alt.Color(
                "n:Q",
                title="Count",
                scale=alt.Scale(scheme="blues", domain=[0, int(full["n"].max())]),
                legend=alt.Legend(orient="right"),
            ),
            tooltip=[
                alt.Tooltip("condition_label:N", title="Condition"),
                alt.Tooltip("presentation_slot:O", title="Slot"),
                alt.Tooltip("n:Q", title="Count"),
            ],
        )
    )
    text = (
        alt.Chart(full)
        .mark_text(fontSize=12, fontWeight="bold")
        .encode(
            x="presentation_slot:O",
            y=alt.Y("condition_label:N", sort=CONDITION_LABEL_ORDER),
            text="label_text:N",
            color=alt.condition(
                alt.datum.n >= expected,
                alt.value("white"),
                alt.value("#222222"),
            ),
        )
    )
    chart = (heat + text).properties(
        width=320,
        height=240,
        title=(
            f"Condition × presentation-slot counts "
            f"(n = {n_subjects}; expected ≈ {expected:.1f} if uniform)"
        ),
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out_dir / "data.csv", index=False)
    full.to_csv(out_dir / "summary.csv", index=False)
    # also a tidy crosstab for quick inspection
    crosstab = pd.crosstab(
        raw["condition_label"],
        raw["presentation_slot"],
        rownames=["condition"],
        colnames=["slot"],
    ).reindex(CONDITION_LABEL_ORDER)
    crosstab.to_csv(out_dir / "crosstab.csv")

    stem = out_dir / "condition_order_balance"
    _save_chart(chart, stem)
    return stem.with_suffix(".pdf")


def plot_recording_duration_bins(out_dir: Path) -> Path:
    acq = pd.read_csv(AUDIT_PATH).drop_duplicates("subject_id")
    acq["duration_min"] = acq["xdf_duration_s"] / 60.0
    bins = [30, 45, 60, 75, 90, 120]
    labels = ["30–45", "45–60", "60–75", "75–90", "90–120"]
    acq["duration_bin_min"] = pd.cut(
        acq["duration_min"], bins=bins, right=False, labels=labels
    )
    counts = (
        acq["duration_bin_min"]
        .value_counts()
        .reindex(labels)
        .fillna(0)
        .astype(int)
    )
    counts = counts[counts > 0]
    plot_df = counts.rename("n_subjects").reset_index()
    plot_df.columns = ["duration_bin_min", "n_subjects"]
    plot_df["duration_bin_min"] = pd.Categorical(
        plot_df["duration_bin_min"],
        categories=list(plot_df["duration_bin_min"]),
        ordered=True,
    )

    n = len(acq)
    bars = (
        alt.Chart(plot_df)
        .mark_bar(color="#3B6EA5", cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X(
                "duration_bin_min:N",
                title="Recording duration bin (min)",
                sort=list(plot_df["duration_bin_min"]),
            ),
            y=alt.Y("n_subjects:Q", title="Number of subjects"),
            tooltip=[
                alt.Tooltip("duration_bin_min:N", title="Bin (min)"),
                alt.Tooltip("n_subjects:Q", title="Subjects"),
            ],
        )
    )
    labels_layer = (
        alt.Chart(plot_df)
        .mark_text(dy=-8, color="#222222", fontSize=11)
        .encode(
            x=alt.X("duration_bin_min:N", sort=list(plot_df["duration_bin_min"])),
            y="n_subjects:Q",
            text="n_subjects:Q",
        )
    )
    chart = (bars + labels_layer).properties(
        width=360,
        height=260,
        title=f"EEG recording duration distribution (n = {n})",
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    acq[["subject_id", "duration_min", "duration_bin_min"]].sort_values(
        "subject_id"
    ).to_csv(out_dir / "data.csv", index=False)
    plot_df.to_csv(out_dir / "summary.csv", index=False)
    stem = out_dir / "recording_duration_bins"
    _save_chart(chart, stem)
    return stem.with_suffix(".pdf")


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    blocks = condition_blocks()
    cond_pdf = plot_condition_block_duration(
        OUT_ROOT / "condition_block_duration", blocks
    )
    order_pdf = plot_condition_order_balance(
        OUT_ROOT / "condition_order_balance", blocks
    )
    bins_pdf = plot_recording_duration_bins(OUT_ROOT / "recording_duration_bins")
    print(f"Wrote {cond_pdf}")
    print(f"Wrote {order_pdf}")
    print(f"Wrote {bins_pdf}")


if __name__ == "__main__":
    main()
