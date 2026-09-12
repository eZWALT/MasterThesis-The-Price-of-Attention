"""Full direction pass: heatmaps, EDA, then stages 2-4.

Stage 5 (combos) is a separate tree: ``analysis/walter/combos/``.
This script does not run it.

    python analysis/trajectories/run_direction_pass.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

HERE = Path(__file__).resolve().parent
DATA = HERE / "outputs"
FIGURES = DATA / "figures" / "direction"
sys.path.insert(0, str(HERE))

from analyse_trajectories import (  # noqa: E402
    CONTROL,
    EARLY,
    exact_crossing_table,
    holm,
    paired_test,
    targeted_tests,
)
from build_trajectory_dataset import GENRE_LABELS  # noqa: E402
from classify_advertisements import permutation_null, turn_pivot  # noqa: E402
from describe_trajectories import short  # noqa: E402

SOURCES = ("utterance", "contextual")
SOURCE_TITLE = {
    "utterance": "Bare utterance (primary)",
    "contextual": "Contextual (sensitivity)",
}
NAVY = "#1B3A4B"
CLAY = "#C45C26"
INK = "#12202A"
SLATE = "#5C6B73"
PAPER = "#F4F6F7"
CMAP = LinearSegmentedColormap.from_list("p", [PAPER, "#9BB0BC", NAVY])
DIVERGE = LinearSegmentedColormap.from_list("dp", [CLAY, PAPER, NAVY])
CONDITION_TEXT = {
    "a_none": "No ad",
    "a_imp_2": "Implicit early",
    "a_exp_2": "Explicit early",
    "a_imp_4": "Implicit late",
    "a_exp_4": "Explicit late",
}
CONDITION_ORDER = list(CONDITION_TEXT)


def style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 130,
            "savefig.dpi": 220,
            "font.size": 9,
            "axes.edgecolor": SLATE,
            "axes.labelcolor": INK,
            "text.color": INK,
            "xtick.color": SLATE,
            "ytick.color": SLATE,
        }
    )


def save(figure: plt.Figure, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / f"{name}.png"
    figure.savefig(path, format="png", bbox_inches="tight")
    figure.savefig(FIGURES / f"{name}.pdf", format="pdf", bbox_inches="tight")
    plt.close(figure)
    return path


def genre_order(transitions: pd.DataFrame) -> list[str]:
    """Fixed 13-class order, frequent-from-genre first under the primary labels."""
    primary = transitions[transitions.genre_source == "utterance"]
    ranks = primary.from_genre.value_counts()
    ranked = [g for g in ranks.index if g in GENRE_LABELS]
    return ranked + [g for g in GENRE_LABELS if g not in ranked]


def count_matrix(frame: pd.DataFrame, genres: list[str]) -> np.ndarray:
    index = {genre: i for i, genre in enumerate(genres)}
    matrix = np.zeros((len(genres), len(genres)))
    for source, target in zip(frame.from_genre, frame.to_genre):
        if source in index and target in index:
            matrix[index[source], index[target]] += 1
    return matrix


def row_normalise(counts: np.ndarray) -> np.ndarray:
    totals = counts.sum(axis=1, keepdims=True)
    return np.divide(counts, totals, out=np.zeros_like(counts), where=totals > 0)


def draw_matrix(axis, matrix, genres, *, vmin, vmax, cmap, title, counts=None, annotate=True):
    ny, nx = matrix.shape
    image = axis.pcolormesh(
        np.arange(nx + 1) - 0.5,
        np.arange(ny + 1) - 0.5,
        matrix,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        shading="flat",
    )
    axis.set_xlim(-0.5, nx - 0.5)
    axis.set_ylim(ny - 0.5, -0.5)
    axis.set_aspect("equal")
    ticks = [short(g) for g in genres]
    axis.set_xticks(range(len(genres)))
    axis.set_xticklabels(ticks, rotation=55, ha="right", fontsize=7)
    axis.set_yticks(range(len(genres)))
    axis.set_yticklabels(ticks, fontsize=7)
    axis.set_title(title, color=INK, fontsize=10)
    axis.set_xlabel("to")
    axis.set_ylabel("from")
    if annotate:
        for i in range(len(genres)):
            for j in range(len(genres)):
                value = matrix[i, j]
                if counts is not None and counts[i, j] == 0:
                    continue
                if abs(value) < 0.05:
                    continue
                axis.text(
                    j,
                    i,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=5.5,
                    color="white" if abs(value) > 0.45 else INK,
                )
    return image


def plot_overall_both(transitions: pd.DataFrame, genres: list[str]) -> Path:
    style()
    figure, axes = plt.subplots(1, 2, figsize=(14.4, 6.6))
    image = None
    for axis, source in zip(axes, SOURCES):
        frame = transitions[transitions.genre_source == source]
        counts = count_matrix(frame, genres)
        matrix = row_normalise(counts)
        image = draw_matrix(
            axis,
            matrix,
            genres,
            vmin=0,
            vmax=1,
            cmap=CMAP,
            title=f"{SOURCE_TITLE[source]}\n{len(frame)} transitions",
            counts=counts,
        )
    cax = figure.add_axes([0.93, 0.18, 0.015, 0.64])
    n = 64
    cax.pcolormesh(
        [0, 1],
        np.linspace(0, 1, n + 1),
        np.linspace(0, 1, n).reshape(n, 1),
        cmap=CMAP,
        shading="flat",
    )
    cax.set_xticks([])
    cax.set_yticks([0, 0.5, 1.0])
    cax.set_ylabel("P(to | from)")
    figure.suptitle("Genre transition matrices, all conversations", color=INK)
    figure.subplots_adjust(right=0.91)
    return save(figure, "heatmap_overall_both")


def plot_ad_vs_none(transitions: pd.DataFrame, genres: list[str], source: str) -> Path:
    style()
    frame = transitions[transitions.genre_source == source]
    none = frame[frame.condition_label == CONTROL]
    advertised = frame[frame.condition_label != CONTROL]
    panels = [
        (none, "No-ad", CMAP, 0, 1, False),
        (advertised, "Advertised conditions", CMAP, 0, 1, False),
    ]
    matrices = []
    counts = []
    for data, *_ in panels:
        c = count_matrix(data, genres)
        counts.append(c)
        matrices.append(row_normalise(c))
    delta = matrices[1] - matrices[0]
    limit = max(0.25, np.nanmax(np.abs(delta)))

    figure, axes = plt.subplots(1, 3, figsize=(17.2, 6.2))
    for axis, (data, title, cmap, vmin, vmax, _), matrix, count in zip(
        axes[:2], panels, matrices, counts
    ):
        draw_matrix(
            axis,
            matrix,
            genres,
            vmin=vmin,
            vmax=vmax,
            cmap=cmap,
            title=f"{title}\n(n={len(data)})",
            counts=count,
        )
    image = draw_matrix(
        axes[2],
        delta,
        genres,
        vmin=-limit,
        vmax=limit,
        cmap=DIVERGE,
        title="ΔP = advertised − no-ad",
        counts=counts[0] + counts[1],
    )
    # Overlay a proper diverging norm so zero stays paper-coloured.
    image.set_norm(TwoSlopeNorm(vcenter=0, vmin=-limit, vmax=limit))
    figure.colorbar(image, ax=axes, fraction=0.02, pad=0.02).set_label("ΔP")
    figure.suptitle(
        f"Ad vs no-ad structure · {SOURCE_TITLE[source]}", color=INK
    )
    return save(figure, f"heatmap_ad_vs_none_{source}")


def plot_crossing_delta(transitions: pd.DataFrame, genres: list[str], source: str) -> Path:
    """The causally coherent pair: transition 2→3 with vs without an early ad."""
    style()
    frame = transitions[transitions.genre_source == source]
    control = frame[(frame.condition_label == CONTROL) & (frame.k == 2)]
    crossing = frame[frame.position == "crosses_ad"]
    counts = [count_matrix(control, genres), count_matrix(crossing, genres)]
    matrices = [row_normalise(c) for c in counts]
    delta = matrices[1] - matrices[0]
    limit = max(0.25, np.nanmax(np.abs(delta)))

    figure, axes = plt.subplots(1, 3, figsize=(17.2, 6.2))
    draw_matrix(
        axes[0],
        matrices[0],
        genres,
        vmin=0,
        vmax=1,
        cmap=CMAP,
        title=f"No-ad, turn 2→3\n(n={len(control)})",
        counts=counts[0],
    )
    draw_matrix(
        axes[1],
        matrices[1],
        genres,
        vmin=0,
        vmax=1,
        cmap=CMAP,
        title=f"Crosses an early ad\n(n={len(crossing)})",
        counts=counts[1],
    )
    image = draw_matrix(
        axes[2],
        delta,
        genres,
        vmin=-limit,
        vmax=limit,
        cmap=DIVERGE,
        title="ΔP = crossing − no-ad",
        counts=counts[0] + counts[1],
    )
    image.set_norm(TwoSlopeNorm(vcenter=0, vmin=-limit, vmax=limit))
    figure.colorbar(image, ax=axes, fraction=0.02, pad=0.02).set_label("ΔP")
    figure.suptitle(
        f"Crossing-transition destinations · {SOURCE_TITLE[source]}", color=INK
    )
    return save(figure, f"heatmap_crossing_{source}")


def plot_stacked_redirection(early: pd.DataFrame) -> Path:
    style()
    frame = early.copy()
    frame["kind"] = np.where(
        frame.delta_2 == 0,
        "same genre",
        np.where(frame.genre_3 == frame.ad_genre, "ad-aligned shift", "unrelated shift"),
    )
    order = ["same genre", "unrelated shift", "ad-aligned shift"]
    colours = [NAVY, SLATE, CLAY]
    groups = [
        ("all early ads", frame),
        ("implicit early", frame[frame.condition_label == "a_imp_2"]),
        ("explicit early", frame[frame.condition_label == "a_exp_2"]),
    ]

    figure, axis = plt.subplots(figsize=(7.4, 4.2))
    bottoms = np.zeros(len(groups))
    for kind, colour in zip(order, colours):
        heights = np.array([(g.kind == kind).mean() for _, g in groups])
        axis.bar(
            range(len(groups)),
            heights,
            bottom=bottoms,
            color=colour,
            label=kind,
            edgecolor="white",
        )
        bottoms += heights
    axis.set_xticks(range(len(groups)))
    axis.set_xticklabels([f"{name}\n(n={len(g)})" for name, g in groups])
    axis.set_ylim(0, 1)
    axis.set_ylabel("share of early-ad conversations")
    axis.set_title("What happens on the crossing transition", color=INK)
    axis.legend(frameon=False, fontsize=8, loc="upper right")
    return save(figure, "redirection_stacked")


def destination_table(transitions: pd.DataFrame, source: str) -> pd.DataFrame:
    frame = transitions[transitions.genre_source == source]
    crossing = frame[frame.position == "crosses_ad"]
    control = frame[(frame.condition_label == CONTROL) & (frame.k == 2)]
    rows = []
    for label, data in [("crossing", crossing), ("no_ad_k2", control)]:
        for subset, name in [
            (data, "all"),
            (data[data.delta == 1], "shifts_only"),
        ]:
            counts = subset.to_genre.value_counts()
            for genre, count in counts.items():
                rows.append(
                    {
                        "genre_source": source,
                        "set": label,
                        "subset": name,
                        "to_genre": genre,
                        "count": int(count),
                        "share": count / len(subset) if len(subset) else 0.0,
                        "n": len(subset),
                    }
                )
    return pd.DataFrame(rows)


def early_with_ads(conversations: pd.DataFrame, source: str) -> pd.DataFrame:
    ads = pd.read_csv(DATA / "advertisements.csv")
    frame = conversations[
        (conversations.genre_source == source) & conversations.ad_turn.eq(2)
    ].copy()
    frame = frame.merge(
        ads[["conversation_id", "ad_genre", "ad_genre_confidence"]],
        on="conversation_id",
        how="left",
    )
    pivoted = turn_pivot(source)
    return frame.join(pivoted, on="conversation_id")


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_empty_"
    columns = list(frame.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" if frame[c].dtype == object else "---:" for c in columns) + " |",
    ]
    for row in frame.itertuples(index=False):
        cells = []
        for value in row:
            if isinstance(value, float):
                cells.append(f"{value:.3f}")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def eda_block(utterances: pd.DataFrame, conversations: pd.DataFrame, transitions: pd.DataFrame) -> str:
    lines = ["# Direction pass", "", "## 1. Descriptive / EDA", ""]
    for source in SOURCES:
        u = utterances[utterances.genre_source == source]
        c = conversations[conversations.genre_source == source]
        t = transitions[transitions.genre_source == source]
        lines.append(f"### {SOURCE_TITLE[source]}")
        lines.append("")
        counts = u.genre.value_counts()
        dist = pd.DataFrame(
            {
                "genre": counts.index,
                "utterances": counts.values,
                "share": counts.values / counts.sum(),
            }
        )
        lines.append(markdown_table(dist))
        lines.append("")
        summary = (
            c.groupby("condition_label")[
                ["n_shift", "shift_rate", "diversity", "entropy_nats", "max_persistence"]
            ]
            .mean()
            .reindex(CONDITION_ORDER)
            .reset_index()
        )
        summary["condition_label"] = summary.condition_label.map(CONDITION_TEXT)
        lines.append(markdown_table(summary))
        lines.append("")
        lines.append(
            f"Mean shift rate {c.shift_rate.mean():.3f}, diversity {c.diversity.mean():.2f}, "
            f"entropy {c.entropy_nats.mean():.3f} nats, max persistence {c.max_persistence.mean():.2f}."
        )
        lines.append(
            f"Conversations with at least one shift: {(c.n_shift > 0).mean():.1%}."
        )
        lines.append("")
        turn = pd.crosstab(u.turn, u.genre, normalize="index").round(3)
        lines.append("Turn profile (row shares):")
        lines.append("")
        lines.append(markdown_table(turn.reset_index()))
        lines.append("")
        pos = (
            t.groupby("position")
            .agg(shift_rate=("delta", "mean"), n=("delta", "count"))
            .reset_index()
        )
        lines.append(markdown_table(pos))
        lines.append("")
    return "\n".join(lines)


def stage2_block(transitions: pd.DataFrame) -> str:
    lines = ["## 2. Advertisement effects on genre dynamics", ""]
    lines.append(
        "Estimand: transition 2→3 in early ads against the same transition "
        "in the no-ad condition, paired within participant."
    )
    lines.append("")
    for source in SOURCES:
        lines.append(f"### {SOURCE_TITLE[source]}")
        lines.append("")
        lines.append("Hard shift (paired mean difference):")
        lines.append("")
        lines.append(markdown_table(targeted_tests(transitions, "delta", source).round(4)))
        lines.append("")
        lines.append("Exact McNemar on the crossing transition:")
        lines.append("")
        lines.append(markdown_table(exact_crossing_table(transitions, source).round(4)))
        lines.append("")
        dest = destination_table(transitions, source)
        crossing_shifts = dest[(dest.set == "crossing") & (dest.subset == "shifts_only")]
        control_shifts = dest[(dest.set == "no_ad_k2") & (dest.subset == "shifts_only")]
        merged = crossing_shifts[["to_genre", "count", "share", "n"]].merge(
            control_shifts[["to_genre", "count", "share"]],
            on="to_genre",
            how="outer",
            suffixes=("_crossing", "_control"),
        ).fillna(0)
        merged = merged.sort_values("share_crossing", ascending=False)
        lines.append("Destination shares among **shifts** on 2→3:")
        lines.append("")
        lines.append(markdown_table(merged))
        lines.append("")
    return "\n".join(lines)


def stage3_block(conversations: pd.DataFrame) -> str:
    lines = ["## 3. Genre redirection", ""]
    early = early_with_ads(conversations, "utterance")
    early["aligned"] = (early.genre_3 == early.ad_genre).astype(int)
    early["tilde"] = (early.shifted * early.aligned) if "shifted" in early else (
        (early.delta_2 == 1) & (early.genre_3 == early.ad_genre)
    ).astype(int)
    if "shifted" not in early.columns:
        early["shifted"] = early.delta_2.astype(int)
    n = len(early)
    same = int((early.delta_2 == 0).sum())
    aligned = int(((early.delta_2 == 1) & (early.genre_3 == early.ad_genre)).sum())
    unrelated = int(((early.delta_2 == 1) & (early.genre_3 != early.ad_genre)).sum())
    shifted = aligned + unrelated
    q = aligned / shifted if shifted else 0.0
    already = int((early.genre_2 == early.ad_genre).sum())
    lines.append(
        f"Early advertisements (primary labels): {n}. "
        f"Same genre {same} ({same/n:.3f}), unrelated shift {unrelated} ({unrelated/n:.3f}), "
        f"ad-aligned shift {aligned} ({aligned/n:.3f})."
    )
    lines.append("")
    lines.append(
        f"Conditional q = P(aligned | shifted) = {aligned}/{shifted} = {q:.3f}."
    )
    lines.append(
        f"Already in the advertisement genre at turn 2: {already} of {n}."
    )
    lines.append("")
    lines.append("```")
    lines.append(permutation_null(early))
    lines.append("```")
    lines.append("")
    by_type = []
    for condition, name in [("a_imp_2", "implicit"), ("a_exp_2", "explicit")]:
        part = early[early.condition_label == condition]
        by_type.append(
            {
                "ad_type": name,
                "n": len(part),
                "same": int((part.delta_2 == 0).sum()),
                "unrelated": int(((part.delta_2 == 1) & (part.genre_3 != part.ad_genre)).sum()),
                "aligned": int(((part.delta_2 == 1) & (part.genre_3 == part.ad_genre)).sum()),
            }
        )
    lines.append(markdown_table(pd.DataFrame(by_type)))
    lines.append("")
    return "\n".join(lines)


def stage4_block(transitions: pd.DataFrame, conversations: pd.DataFrame) -> str:
    lines = ["## 4. Moderation", ""]
    lines.append(
        "Ad type (implicit vs explicit) is tested on the crossing estimand. "
        "Timing is **not** a treatment moderator: late ads have no following "
        "utterance. Late vs no-ad is the negative control."
    )
    lines.append("")
    for source in SOURCES:
        lines.append(f"### {SOURCE_TITLE[source]}")
        lines.append("")
        hard = targeted_tests(transitions, "delta", source)
        type_row = hard[hard.contrast == "implicit early - explicit early"]
        lines.append("Implicit early minus explicit early (hard shift):")
        lines.append("")
        lines.append(markdown_table(type_row.round(4)))
        lines.append("")

    # Negative control: late conversation-level n_shift vs no-ad, primary only.
    frame = conversations[conversations.genre_source == "utterance"]
    wide = frame.pivot_table(
        index="participant_id", columns="condition_label", values="n_shift"
    )
    late = pd.DataFrame(
        [
            paired_test(wide[["a_imp_4", "a_exp_4"]].mean(axis=1) - wide[CONTROL], "late pooled - no ad"),
            paired_test(wide["a_imp_4"] - wide[CONTROL], "implicit late - no ad"),
            paired_test(wide["a_exp_4"] - wide[CONTROL], "explicit late - no ad"),
        ]
    )
    late["p_holm"] = holm(late.p_t.tolist())
    lines.append("### Timing as negative control (primary labels, conversation N_shift)")
    lines.append("")
    lines.append(markdown_table(late.round(4)))
    lines.append("")
    lines.append("## 5. EEG × behavioural")
    lines.append("")
    lines.append("Blocked. Not run.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    utterances = pd.read_csv(DATA / "utterances.csv")
    conversations = pd.read_csv(DATA / "conversations.csv")
    transitions = pd.read_csv(DATA / "transitions.csv")
    genres = genre_order(transitions)

    paths = [
        plot_overall_both(transitions, genres),
        plot_ad_vs_none(transitions, genres, "utterance"),
        plot_ad_vs_none(transitions, genres, "contextual"),
        plot_crossing_delta(transitions, genres, "utterance"),
        plot_crossing_delta(transitions, genres, "contextual"),
        plot_stacked_redirection(early_with_ads(conversations, "utterance")),
    ]
    destination_table(transitions, "utterance").to_csv(
        DATA / "destination_shares.csv", index=False
    )
    destination_table(transitions, "contextual").to_csv(
        DATA / "destination_shares_contextual.csv", index=False
    )

    report = "\n".join(
        [
            eda_block(utterances, conversations, transitions),
            stage2_block(transitions),
            stage3_block(conversations),
            stage4_block(transitions, conversations),
            "Figures:",
            "",
            *[f"- `{path.relative_to(DATA.parent)}`" for path in paths],
            "",
        ]
    )
    (DATA / "direction_pass.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote {DATA / 'direction_pass.md'}")
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
