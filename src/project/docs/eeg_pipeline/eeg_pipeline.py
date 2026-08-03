"""Generate the publication figure for the laboratory EEG analysis arm."""

from __future__ import annotations

from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon


HERE = Path(__file__).resolve().parent
RESOURCES = HERE.parent / "architecture" / "resources"
W, H = 120, 165

COLORS = {
    "ink": "#263442",
    "muted": "#4D5D6B",
    "edge": "#687988",
    "card": "#FFFFFF",
    "card_border": "#B8C2CB",
    "blue_bg": "#EDF5FB",
    "blue_border": "#8FB8D8",
    "purple_bg": "#F3F1FA",
    "purple_border": "#9C93C8",
    "green_bg": "#EFF7EF",
    "green_border": "#8FBF92",
    "gold_bg": "#FDF7E8",
    "gold_border": "#D8C48F",
    "grey_bg": "#F5F7F8",
    "grey_border": "#AAB4BE",
    "gate_bg": "#FFF8E7",
    "gate_border": "#B88B2E",
    "conditional": "#A05A2C",
    "exclude": "#8D4B4B",
}


def rounded(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    face: str,
    edge: str,
    radius: float = 1.5,
    linewidth: float = 1.2,
    zorder: int = 1,
) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle=f"round,pad=0.02,rounding_size={radius}",
            facecolor=face,
            edgecolor=edge,
            linewidth=linewidth,
            zorder=zorder,
        )
    )


def band(
    ax: plt.Axes,
    number: int,
    title: str,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    face: str,
    edge: str,
) -> None:
    rounded(ax, x, y, width, height, face=face, edge=edge, radius=2.2)
    ax.text(
        x + 4,
        y + height - 4,
        str(number),
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        color="white",
        bbox={"boxstyle": "circle,pad=0.36", "facecolor": edge, "edgecolor": edge},
        zorder=5,
    )
    ax.text(
        x + 8,
        y + height - 4,
        title,
        ha="left",
        va="center",
        fontsize=11.2,
        fontweight="bold",
        color=COLORS["ink"],
        zorder=5,
    )


def card(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    title: str,
    details: tuple[str, ...],
    *,
    height: float = 11,
    icon: str | None = None,
    border: str | None = None,
    title_color: str | None = None,
    title_size: float = 9.5,
) -> None:
    rounded(
        ax,
        x,
        y,
        width,
        height,
        face=COLORS["card"],
        edge=border or COLORS["card_border"],
        radius=1.3,
        linewidth=1.1,
        zorder=3,
    )
    text_x = x + 2.2
    if icon:
        icon_ax = ax.inset_axes(
            [(x + 1.2) / W, (y + 2.0) / H, 6.2 / W, 7.0 / H],
            transform=ax.transAxes,
            zorder=4,
        )
        icon_ax.imshow(mpimg.imread(RESOURCES / icon))
        icon_ax.axis("off")
        text_x = x + 8
    title_y = y + height - 3.2 if details else y + height / 2
    ax.text(
        text_x,
        title_y,
        title,
        ha="left",
        va="center",
        fontsize=title_size,
        fontweight="bold",
        color=title_color or COLORS["ink"],
        zorder=5,
    )
    if details:
        ax.text(
            text_x,
            y + height - 7.1,
            "\n".join(details),
            ha="left",
            va="center",
            fontsize=8.2,
            linespacing=1.25,
            color=COLORS["muted"],
            zorder=5,
        )


def gate(
    ax: plt.Axes,
    x: float,
    y: float,
    text: str,
    *,
    width: float = 19,
    height: float = 12,
) -> None:
    points = [
        (x, y + height / 2),
        (x + width / 2, y),
        (x, y - height / 2),
        (x - width / 2, y),
    ]
    ax.add_patch(
        Polygon(
            points,
            closed=True,
            facecolor=COLORS["gate_bg"],
            edgecolor=COLORS["gate_border"],
            linewidth=1.4,
            zorder=3,
        )
    )
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        multialignment="center",
        fontsize=8.4,
        fontweight="bold",
        linespacing=1.15,
        color=COLORS["ink"],
        zorder=5,
    )


def arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    label: str | None = None,
    color: str | None = None,
    dashed: bool = False,
    connection: str = "arc3,rad=0",
    label_offset: tuple[float, float] = (0, 1.6),
    linewidth: float = 1.35,
) -> None:
    edge_color = color or COLORS["edge"]
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=11,
            linewidth=linewidth,
            linestyle="--" if dashed else "-",
            color=edge_color,
            connectionstyle=connection,
            shrinkA=2,
            shrinkB=2,
            zorder=2,
        )
    )
    if label:
        ax.text(
            (start[0] + end[0]) / 2 + label_offset[0],
            (start[1] + end[1]) / 2 + label_offset[1],
            label,
            ha="center",
            va="center",
            fontsize=10.5,
            fontweight="bold",
            color=edge_color,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.6},
            zorder=6,
        )


def elbow_arrow(
    ax: plt.Axes,
    points: tuple[tuple[float, float], ...],
    *,
    label: str | None = None,
    color: str | None = None,
    label_at: tuple[float, float] | None = None,
    linewidth: float = 1.35,
) -> None:
    edge_color = color or COLORS["edge"]
    for start, end in zip(points[:-2], points[1:-1]):
        ax.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            color=edge_color,
            linewidth=linewidth,
            solid_capstyle="round",
            zorder=2,
        )
    ax.add_patch(
        FancyArrowPatch(
            points[-2],
            points[-1],
            arrowstyle="-|>",
            mutation_scale=11,
            linewidth=linewidth,
            color=edge_color,
            shrinkA=0,
            shrinkB=2,
            zorder=2,
        )
    )
    if label and label_at:
        ax.text(
            label_at[0],
            label_at[1],
            label,
            ha="center",
            va="center",
            fontsize=10.5,
            fontweight="bold",
            color=edge_color,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.6},
            zorder=6,
        )


def failure(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    text: str,
) -> None:
    rounded(
        ax,
        x,
        y,
        width,
        7,
        face="#FFFDFD",
        edge=COLORS["exclude"],
        radius=1.1,
        linewidth=1.0,
        zorder=3,
    )
    ax.text(
        x + width / 2,
        y + 3.5,
        text,
        ha="center",
        va="center",
        fontsize=8.0,
        color=COLORS["exclude"],
        linespacing=1.15,
        zorder=5,
    )


def build() -> plt.Figure:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Nimbus Sans", "DejaVu Sans"],
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
        }
    )
    fig, ax = plt.subplots(figsize=(10, 13.75))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    ax.text(
        60,
        160.5,
        "EEG Data Processing and Analysis Pipeline",
        ha="center",
        va="center",
        fontsize=20,
        fontweight="bold",
        color=COLORS["ink"],
    )
    ax.text(
        60,
        156.7,
        "Laboratory EEG arm",
        ha="center",
        va="center",
        fontsize=10.5,
        color=COLORS["muted"],
    )

    # 1 · Recording inventory
    band(
        ax,
        1,
        "Inputs and recording match",
        5,
        127,
        110,
        25,
        face=COLORS["blue_bg"],
        edge=COLORS["blue_border"],
    )
    card(
        ax,
        8,
        132,
        29,
        "XDF recording",
        ("32 channel EEG · markers",),
        icon="eeg-headset.png",
        border=COLORS["blue_border"],
    )
    card(
        ax,
        43,
        132,
        29,
        "Experiment log",
        ("source clock events",),
        icon="recording.png",
        border=COLORS["blue_border"],
    )
    card(
        ax,
        78,
        132,
        34,
        "Recording match",
        ("participant ↔ experiment ↔ XDF",),
        border=COLORS["blue_border"],
    )
    elbow_arrow(
        ax,
        ((22.5, 132), (22.5, 129), (82, 129), (82, 132)),
    )
    arrow(ax, (72, 133.2), (78, 133.2))

    # 2 · Synchronization and marker validation
    band(
        ax,
        2,
        "Marker recovery and event timing",
        5,
        94,
        110,
        29,
        face=COLORS["purple_bg"],
        edge=COLORS["purple_border"],
    )
    card(
        ax,
        8,
        103,
        34,
        "Match log and EEG events",
        (),
        border=COLORS["purple_border"],
        title_size=9.3,
    )
    card(
        ax,
        48,
        103,
        39,
        "Recover event timeline",
        (),
        border=COLORS["purple_border"],
    )
    gate(ax, 101, 109.5, "Event timing\nreliable?")
    failure(ax, 88, 95.0, 26, "NO · repair or\nlimit analysis")
    arrow(ax, (87, 108.5), (91.7, 109.2))
    arrow(ax, (42, 108.5), (48, 108.5))
    arrow(
        ax,
        (101, 103.5),
        (101, 102.0),
        label="NO",
        color=COLORS["exclude"],
        label_offset=(3, 0),
    )

    # 3 · Signal preprocessing
    band(
        ax,
        3,
        "EEG cleaning",
        5,
        62,
        110,
        28,
        face=COLORS["green_bg"],
        edge=COLORS["green_border"],
    )
    card(
        ax,
        8,
        70,
        23,
        "Import EEG",
        (),
        border=COLORS["green_border"],
        title_size=9.2,
    )
    card(
        ax,
        35,
        70,
        23,
        "Clean signal",
        (),
        border=COLORS["green_border"],
    )
    card(
        ax,
        62,
        70,
        25,
        "Remove artifacts",
        (),
        border=COLORS["green_border"],
    )
    gate(ax, 101, 77.5, "EEG usable?")
    failure(ax, 88, 63.0, 26, "NO · exclude with\nrecorded reason")
    arrow(ax, (31, 75.5), (35, 75.5))
    arrow(ax, (58, 75.5), (62, 75.5))
    arrow(ax, (87, 75.5), (92.0, 77.0))
    arrow(
        ax,
        (101, 71.5),
        (101, 70.0),
        label="NO",
        color=COLORS["exclude"],
        label_offset=(3, 0),
    )

    # 4 · Analysis windows and features
    band(
        ax,
        4,
        "Create EEG measurements",
        5,
        27,
        110,
        31,
        face=COLORS["gold_bg"],
        edge=COLORS["gold_border"],
    )
    card(
        ax,
        8,
        37,
        30,
        "Condition windows",
        (),
        border=COLORS["green_border"],
        title_color="#3F7143",
    )
    card(
        ax,
        42,
        37,
        30,
        "Compute EEG measures",
        (),
        border=COLORS["gold_border"],
        title_size=9.0,
    )
    gate(
        ax,
        84,
        47,
        "Ad timing\nreliable?",
        width=18,
        height=11,
    )
    card(
        ax,
        94,
        33,
        18,
        "Before and after\nad windows",
        (),
        height=10,
        border=COLORS["conditional"],
        title_color=COLORS["conditional"],
        title_size=8.5,
    )
    rounded(
        ax,
        94,
        48.5,
        18,
        6.5,
        face="#FFF9F4",
        edge=COLORS["conditional"],
        radius=1.0,
        linewidth=1.0,
        zorder=3,
    )
    ax.text(
        103,
        51.75,
        "NO · use condition\nwindows only",
        ha="center",
        va="center",
        fontsize=8.5,
        fontweight="bold",
        color=COLORS["conditional"],
        zorder=5,
    )
    arrow(ax, (93, 47), (94, 51.5), color=COLORS["conditional"])
    arrow(
        ax,
        (90, 42.8),
        (94, 38),
        label="YES",
        color=COLORS["conditional"],
        label_offset=(1.2, 1.2),
    )

    # 5 · Outputs and inference
    band(
        ax,
        5,
        "Analysis outputs",
        5,
        3,
        110,
        20,
        face=COLORS["grey_bg"],
        edge=COLORS["grey_border"],
    )
    card(
        ax,
        8,
        7,
        30,
        "EEG feature table",
        (),
        border=COLORS["grey_border"],
    )
    card(
        ax,
        45,
        7,
        30,
        "Statistical comparisons",
        (),
        border=COLORS["grey_border"],
        title_size=9.1,
    )
    card(
        ax,
        82,
        7,
        30,
        "Results and figures",
        (),
        border=COLORS["grey_border"],
    )
    arrow(ax, (38, 12.5), (45, 12.5))
    arrow(ax, (75, 12.5), (82, 12.5))

    # Stage transitions and explicit success paths. Margin routing avoids labels
    # and cards, while the numbered bands preserve the reading order.
    arrow(
        ax,
        (95, 132),
        (95, 123),
        label="CHECK",
        label_offset=(4.5, 0),
        color="#536F86",
        linewidth=1.7,
    )
    elbow_arrow(
        ax,
        ((110.5, 109.5), (117, 109.5), (117, 88), (113, 88)),
        label="YES · aligned",
        label_at=(106.5, 92.5),
        color="#536F86",
        linewidth=1.7,
    )
    elbow_arrow(
        ax,
        ((110.5, 77.5), (117, 77.5), (117, 56), (113, 56)),
        label="YES · continue",
        label_at=(106.5, 60.5),
        color="#536F86",
        linewidth=1.7,
    )

    # Both condition windows and valid ad windows feed the same measurement step.
    arrow(ax, (38, 42.5), (42, 42.5))
    arrow(
        ax,
        (94, 38),
        (72, 42.5),
        color=COLORS["conditional"],
        connection="arc3,rad=-0.12",
    )
    arrow(
        ax,
        (57, 37),
        (38, 18),
        color="#536F86",
        connection="arc3,rad=-0.08",
        linewidth=1.7,
    )
    return fig


def main() -> None:
    figure = build()
    for extension in ("png", "pdf", "svg"):
        figure.savefig(
            HERE / f"eeg_pipeline.{extension}",
            dpi=240 if extension == "png" else None,
            bbox_inches="tight",
            facecolor="white",
        )
    plt.close(figure)


if __name__ == "__main__":
    main()
