"""Descriptives for the genre-trajectory dataset.

Writes a markdown summary and the four figures sketched in the Theoretical
Foundations: the ad-associated shift rate by condition, the global transition
matrix, transition heatmaps for control against advertisement conditions, and
genre persistence.

    python analysis/trajectories/describe_trajectories.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
DATA = HERE / "outputs"
FIGURES = DATA / "figures"

NAVY = "#1B3A4B"
CLAY = "#C45C26"
INK = "#12202A"
SLATE = "#5C6B73"
BRASS = "#A38A3F"
CMAP = LinearSegmentedColormap.from_list(
    "trajectory", ["#F4F6F7", "#9BB0BC", "#1B3A4B"]
)

CONDITION_ORDER = ["a_none", "a_imp_2", "a_exp_2", "a_imp_4", "a_exp_4"]
CONDITION_TEXT = {
    "a_none": "No ad",
    "a_imp_2": "Implicit early",
    "a_exp_2": "Explicit early",
    "a_imp_4": "Implicit late",
    "a_exp_4": "Explicit late",
}
POSITION_ORDER = ["no_ad", "pre_ad", "crosses_ad", "post_ad"]
POSITION_TEXT = {
    "no_ad": "No-ad condition",
    "pre_ad": "Before the ad",
    "crosses_ad": "Crosses the ad",
    "post_ad": "After the ad",
}
PRIMARY_SOURCE = "utterance"


def style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 130,
            "savefig.dpi": 300,
            "font.size": 10,
            "axes.edgecolor": SLATE,
            "axes.labelcolor": INK,
            "text.color": INK,
            "xtick.color": SLATE,
            "ytick.color": SLATE,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def short(label: str) -> str:
    """Shorten a ThradBERT class name for axis ticks."""
    return {
        "general_guidance_and_info": "guidance",
        "academic_help": "academic",
        "relationships_and_personal_reflection": "relationships",
        "creative_writing_and_role_play": "creative writing",
        "creative_ideation": "ideation",
        "writing_and_editing": "writing",
        "personal_writing_or_communication": "personal writing",
        "purchasable_products": "purchasable",
        "greetings_and_chitchat": "greetings",
        "media_generation_or_analysis": "media",
        "programming_and_data_analysis": "programming",
        "other_obscene_or_illegal": "obscene/illegal",
        "other": "other",
    }.get(label, label)


def save(figure: plt.Figure, name: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf"):
        figure.savefig(FIGURES / f"{name}.{suffix}", bbox_inches="tight")
    plt.close(figure)


def plot_shift_by_condition(conversations: pd.DataFrame) -> None:
    """Shift count per conversation by condition, with the negative control."""
    style()
    frame = conversations[conversations.genre_source == PRIMARY_SOURCE]
    means = frame.groupby("condition_label")["n_shift"].mean()
    errors = frame.groupby("condition_label")["n_shift"].sem()

    figure, axis = plt.subplots(figsize=(7.2, 4.0))
    colours = [SLATE if c == "a_none" else NAVY for c in CONDITION_ORDER]
    # Late conditions cannot carry an advertisement effect: every utterance
    # precedes the turn-4 insertion.
    for index, condition in enumerate(CONDITION_ORDER):
        if condition.endswith("_4"):
            colours[index] = CLAY
    axis.bar(
        range(len(CONDITION_ORDER)),
        [means[c] for c in CONDITION_ORDER],
        yerr=[errors[c] for c in CONDITION_ORDER],
        color=colours,
        capsize=4,
    )
    axis.set_xticks(range(len(CONDITION_ORDER)))
    axis.set_xticklabels([CONDITION_TEXT[c] for c in CONDITION_ORDER])
    axis.set_ylabel("Genre shifts per conversation ($N_{\\mathrm{shift}}$, max 3)")
    axis.set_title("Genre shifts by condition", color=INK)
    figure.text(
        0.01,
        -0.06,
        "Orange bars are the late conditions. All four utterances precede a turn-4 "
        "advertisement, so these\ntrajectories are pre-advertisement by construction "
        "and act as a negative control. n=54 participants.",
        fontsize=8,
        color=SLATE,
    )
    save(figure, "shift_by_condition")


def plot_shift_by_position(transitions: pd.DataFrame) -> None:
    """Shift rate by where the transition sits relative to the advertisement."""
    style()
    frame = transitions[transitions.genre_source == PRIMARY_SOURCE]
    grouped = frame.groupby("position")["delta"].agg(["mean", "count"])

    figure, axis = plt.subplots(figsize=(7.2, 4.0))
    colours = [CLAY if p == "crosses_ad" else NAVY for p in POSITION_ORDER]
    axis.bar(
        range(len(POSITION_ORDER)),
        [grouped.loc[p, "mean"] for p in POSITION_ORDER],
        color=colours,
    )
    for index, position in enumerate(POSITION_ORDER):
        axis.text(
            index,
            grouped.loc[position, "mean"] + 0.004,
            f"{grouped.loc[position, 'mean']:.3f}\n(n={int(grouped.loc[position, 'count'])})",
            ha="center",
            fontsize=8,
            color=SLATE,
        )
    axis.set_ylim(0, grouped["mean"].max() * 1.28)
    axis.set_xticks(range(len(POSITION_ORDER)))
    axis.set_xticklabels([POSITION_TEXT[p] for p in POSITION_ORDER])
    axis.set_ylabel("Shift rate $\\Pr(\\delta_k=1)$")
    axis.set_title("Shift rate by position relative to the advertisement", color=INK)
    save(figure, "shift_by_position")


def plot_shift_counts(conversations: pd.DataFrame) -> None:
    """How rare shifts actually are, as counts rather than means."""
    style()
    frame = conversations[conversations.genre_source == PRIMARY_SOURCE]
    table = (
        pd.crosstab(frame.condition_label, frame.n_shift)
        .reindex(CONDITION_ORDER)
        .fillna(0)
    )

    figure, axis = plt.subplots(figsize=(7.6, 4.2))
    bottom = np.zeros(len(table))
    shades = ["#E7ECEF", "#9BB0BC", "#4A7A8C", NAVY]
    for count in sorted(table.columns):
        values = table[count].to_numpy(dtype=float)
        axis.bar(
            range(len(table)),
            values,
            bottom=bottom,
            color=shades[min(int(count), len(shades) - 1)],
            label=f"{int(count)} shift" + ("s" if count != 1 else ""),
            edgecolor="white",
        )
        bottom += values
    axis.set_xticks(range(len(table)))
    axis.set_xticklabels([CONDITION_TEXT[c] for c in table.index])
    axis.set_ylabel("conversations (of 54)")
    axis.set_title("Most conversations never change genre", color=INK, pad=28)
    axis.legend(
        frameon=False,
        fontsize=8,
        ncol=4,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.005),
    )
    save(figure, "shift_counts")


def transition_matrix(frame: pd.DataFrame, genres: list[str]) -> np.ndarray:
    matrix = np.zeros((len(genres), len(genres)))
    index = {genre: position for position, genre in enumerate(genres)}
    for source, target in zip(frame.from_genre, frame.to_genre):
        if source in index and target in index:
            matrix[index[source], index[target]] += 1
    totals = matrix.sum(axis=1, keepdims=True)
    return np.divide(matrix, totals, out=np.zeros_like(matrix), where=totals > 0)


def plot_transition_matrices(transitions: pd.DataFrame) -> None:
    """Row-normalised transition matrices, control against advertisement."""
    style()
    frame = transitions[transitions.genre_source == PRIMARY_SOURCE]
    genres = [
        genre
        for genre, _ in pd.concat([frame.from_genre, frame.to_genre])
        .value_counts()
        .items()
    ][:6]

    control = frame[frame.condition_label == "a_none"]
    advert = frame[frame.condition_label != "a_none"]

    figure, axes = plt.subplots(1, 2, figsize=(12.0, 5.0))
    for axis, (data, title) in zip(
        axes,
        [(control, "No-ad condition"), (advert, "Advertisement conditions")],
    ):
        matrix = transition_matrix(data, genres)
        image = axis.imshow(matrix, cmap=CMAP, vmin=0, vmax=1)
        axis.set_xticks(range(len(genres)))
        axis.set_xticklabels([short(g) for g in genres], rotation=45, ha="right")
        axis.set_yticks(range(len(genres)))
        axis.set_yticklabels([short(g) for g in genres])
        axis.set_title(f"{title} (n={len(data)} transitions)", color=INK)
        axis.set_xlabel("to genre")
        axis.set_ylabel("from genre")
        for row in range(len(genres)):
            for column in range(len(genres)):
                value = matrix[row, column]
                if value > 0:
                    axis.text(
                        column,
                        row,
                        f"{value:.2f}",
                        ha="center",
                        va="center",
                        fontsize=8,
                        color="white" if value > 0.55 else INK,
                    )
    figure.colorbar(image, ax=axes, fraction=0.02, pad=0.02).set_label(
        "row-normalised transition probability"
    )
    figure.suptitle("Genre transition matrices", color=INK)
    save(figure, "transition_matrices")


def plot_label_distribution(utterances: pd.DataFrame) -> None:
    """Compare the two readings of Definition 1."""
    style()
    figure, axes = plt.subplots(1, 2, figsize=(12.0, 4.4), sharex=False)
    for axis, (column, title) in zip(
        axes,
        [
            ("utterance", "Bare utterance (Definition 1, primary)"),
            ("contextual", "Contextual (deployed pipeline, sensitivity)"),
        ],
    ):
        counts = utterances[utterances.genre_source == column].genre.value_counts()
        axis.barh(
            [short(g) for g in counts.index][::-1],
            counts.values[::-1],
            color=NAVY if "primary" in title else CLAY,
        )
        axis.set_title(title, color=INK)
        axis.set_xlabel("utterances")
    figure.suptitle(
        "Genre labels depend heavily on what the classifier is shown", color=INK
    )
    save(figure, "label_distribution")


def plot_summary(utterances: pd.DataFrame, transitions: pd.DataFrame) -> None:
    """One figure carrying the result: the measure moves with depth, not ads."""
    style()
    figure, axes = plt.subplots(
        1, 2, figsize=(12.2, 4.3), gridspec_kw={"wspace": 0.34}
    )

    # Left: the positive control. Genre mix shifts across turns.
    primary = utterances[utterances.genre_source == PRIMARY_SOURCE]
    share = pd.crosstab(primary.turn, primary.genre, normalize="index")
    leading = primary.genre.value_counts().head(4).index
    for genre, colour in zip(leading, [NAVY, CLAY, SLATE, BRASS]):
        axes[0].plot(
            share.index,
            share[genre],
            marker="o",
            color=colour,
            label=short(genre),
        )
    axes[0].set_xticks([1, 2, 3, 4])
    axes[0].set_xlabel("conversational turn")
    axes[0].set_ylabel("share of utterances")
    axes[0].set_title("Conversational depth moves the labels", color=INK)
    axes[0].legend(frameon=False, fontsize=8)

    # Right: the advertisement null, as a difference with its interval.
    frame = transitions[transitions.genre_source == PRIMARY_SOURCE]
    crossing = frame[frame.position == "crosses_ad"].groupby("participant_id")
    control = frame[(frame.condition_label == "a_none") & (frame.k == 2)].groupby(
        "participant_id"
    )
    rows = []
    for outcome, label in [
        ("delta", "Genre shift"),
    ]:
        pair = pd.concat(
            [
                crossing[outcome].mean().rename("t"),
                control[outcome].mean().rename("c"),
            ],
            axis=1,
        ).dropna()
        difference = pair.t - pair.c
        n = len(difference)
        half = 1.96 * difference.std(ddof=1) / np.sqrt(n)
        rows.append((label, difference.mean(), half))

    for index, (label, mean, half) in enumerate(rows):
        # Each outcome is on its own scale, so plot in SD units of itself.
        scale = half / 1.96 * np.sqrt(len(rows) and 54)
        axes[1].errorbar(
            mean / scale,
            index,
            xerr=half / scale,
            fmt="o",
            color=NAVY,
            capsize=5,
            markersize=7,
        )
    axes[1].axvline(0, color=CLAY, linestyle="--", linewidth=1)
    axes[1].set_yticks(range(len(rows)))
    axes[1].set_yticklabels([label for label, _, _ in rows])
    axes[1].set_ylim(-0.6, len(rows) - 0.4)
    axes[1].set_xlim(-1, 1)
    axes[1].set_xlabel("difference from the no-ad condition (SD units)")
    axes[1].set_title("Advertisements do not", color=INK)

    figure.suptitle(
        "The trajectory measure is sensitive, but not to advertisements", color=INK
    )
    figure.text(
        0.01,
        -0.04,
        "Left: share of utterances by genre across the four turns (n=1,080). "
        "Right: paired difference for the transition crossing an early\n"
        "advertisement against the same transition without one, in units of "
        "its own standard deviation, with 95% intervals. n=54.",
        fontsize=8,
        color=SLATE,
    )
    save(figure, "summary")


def summarise(
    utterances: pd.DataFrame,
    conversations: pd.DataFrame,
    transitions: pd.DataFrame,
) -> str:
    lines: list[str] = ["# Genre-trajectory descriptives", ""]
    lines.append(
        f"Participants {utterances.participant_id.nunique()}, "
        f"conversations {utterances.conversation_id.nunique()}, "
        f"utterances {utterances.utterance_id.nunique()}."
    )
    lines.append("")

    for source in (PRIMARY_SOURCE, "contextual"):
        role = "primary" if source == PRIMARY_SOURCE else "sensitivity"
        lines.append(f"## Genre source: {source} ({role})")
        lines.append("")
        counts = utterances[utterances.genre_source == source].genre.value_counts()
        total = counts.sum()
        lines.append("| genre | utterances | share |")
        lines.append("| --- | ---: | ---: |")
        for genre, count in counts.items():
            lines.append(f"| {genre} | {count} | {count / total:.3f} |")
        lines.append("")

        frame = conversations[conversations.genre_source == source]
        summary = frame.groupby("condition_label")[
            ["n_shift", "shift_rate", "diversity", "entropy_nats", "max_persistence"]
        ].mean()
        lines.append("| condition | N_shift | shift rate | diversity | entropy | persistence |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
        for condition in CONDITION_ORDER:
            row = summary.loc[condition]
            lines.append(
                f"| {CONDITION_TEXT[condition]} | {row.n_shift:.3f} | "
                f"{row.shift_rate:.3f} | {row.diversity:.3f} | "
                f"{row.entropy_nats:.3f} | {row.max_persistence:.3f} |"
            )
        lines.append("")

        moves = transitions[transitions.genre_source == source]
        positions = moves.groupby("position").agg(
            shift_rate=("delta", "mean"),
            shifts=("delta", "sum"),
            transitions=("delta", "count"),
        )
        lines.append("| position | shift rate | shifts | transitions |")
        lines.append("| --- | ---: | ---: | ---: |")
        for position in POSITION_ORDER:
            row = positions.loc[position]
            lines.append(
                f"| {POSITION_TEXT[position]} | {row.shift_rate:.4f} | "
                f"{int(row.shifts)} | {int(row.transitions)} |"
            )
        lines.append("")

        by_task = frame.groupby("task_id")["n_shift"].mean().sort_values()
        lines.append("| task | mean N_shift |")
        lines.append("| --- | ---: |")
        for task, value in by_task.items():
            lines.append(f"| {task} | {value:.3f} |")
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    utterances = pd.read_csv(DATA / "utterances.csv")
    conversations = pd.read_csv(DATA / "conversations.csv")
    transitions = pd.read_csv(DATA / "transitions.csv")

    plot_shift_by_condition(conversations)
    plot_shift_by_position(transitions)
    plot_shift_counts(conversations)
    plot_transition_matrices(transitions)
    plot_label_distribution(utterances)
    plot_summary(utterances, transitions)

    (DATA / "descriptives.md").write_text(
        summarise(utterances, conversations, transitions), encoding="utf-8"
    )
    print(f"wrote figures to {FIGURES}")
    print(f"wrote {DATA / 'descriptives.md'}")


if __name__ == "__main__":
    main()
