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

    # 1 · Source ingestion
    band(
        ax,
        1,
        "Ingestion / Landing: collect recordings and experiment logs",
        5,
        132,
        110,
        20,
        face=COLORS["blue_bg"],
        edge=COLORS["blue_border"],
    )
    card(
        ax,
        8,
        136,
        29,
        "EEG recording",
        ("32 channel EEG · markers",),
        height=10,
        icon="eeg-headset.png",
        border=COLORS["blue_border"],
    )
    card(
        ax,
        43,
        136,
        29,
        "Experiment log",
        ("source clock events",),
        height=10,
        icon="recording.png",
        border=COLORS["blue_border"],
    )
    card(
        ax,
        78,
        136,
        34,
        "Link files to participant",
        ("participant ↔ experiment ↔ XDF",),
        height=10,
        border=COLORS["blue_border"],
    )
    arrow(ax, (37, 141), (43, 141))
    arrow(ax, (72, 141), (78, 141))

    # 2 · Immutable landing layer
    band(
        ax,
        2,
        "Bronze: preserve and verify raw files",
        5,
        104,
        110,
        24,
        face=COLORS["purple_bg"],
        edge=COLORS["purple_border"],
    )
    card(
        ax,
        8,
        110,
        23,
        "Raw XDF + logs",
        (),
        border=COLORS["purple_border"],
        title_size=8.5,
    )
    card(
        ax,
        34,
        110,
        23,
        "Verify file integrity",
        (),
        border=COLORS["purple_border"],
        title_size=8.3,
    )
    card(
        ax,
        60,
        110,
        23,
        "Link XDF to log",
        (),
        border=COLORS["purple_border"],
    )
    card(
        ax,
        86,
        110,
        26,
        "Audit raw markers",
        (),
        border=COLORS["purple_border"],
        title_size=8.3,
    )
    arrow(ax, (31, 115.5), (34, 115.5))
    arrow(ax, (57, 115.5), (60, 115.5))
    arrow(ax, (83, 115.5), (86, 115.5))
    arrow(
        ax,
        (95, 136),
        (95, 128),
        label="LAND",
        label_offset=(4.2, 0),
        color="#536F86",
        linewidth=1.7,
    )

    # 3 · Audited and cleaned derivatives
    band(
        ax,
        3,
        "Silver: align event timing and clean EEG",
        5,
        55,
        110,
        45,
        face=COLORS["green_bg"],
        edge=COLORS["green_border"],
    )
    card(
        ax,
        8,
        80,
        23,
        "Align event clocks",
        (),
        border=COLORS["purple_border"],
        title_size=8.2,
    )
    card(
        ax,
        35,
        80,
        23,
        "Create event timeline",
        (),
        border=COLORS["purple_border"],
        title_size=8.2,
    )
    card(
        ax,
        62,
        80,
        23,
        "Estimate missing times",
        (),
        border=COLORS["purple_border"],
        title_size=8.1,
    )
    gate(ax, 101, 85.5, "Event timing\nvalid?")
    arrow(ax, (31, 85.5), (35, 85.5))
    arrow(ax, (58, 85.5), (62, 85.5))
    arrow(ax, (85, 85.5), (91.5, 85.5))
    arrow(
        ax,
        (110.5, 85.5),
        (114, 85.5),
        label="NO",
        color=COLORS["exclude"],
        label_offset=(0, 2),
    )

    card(
        ax,
        8,
        61,
        23,
        "Convert XDF to MNE",
        (),
        border=COLORS["green_border"],
        title_size=8.0,
    )
    card(
        ax,
        35,
        61,
        23,
        "Filter + rereference",
        (),
        border=COLORS["green_border"],
        title_size=8.4,
    )
    card(
        ax,
        62,
        61,
        23,
        "Repair bad channels",
        (),
        border=COLORS["green_border"],
        title_size=9.0,
    )
    gate(ax, 101, 66.5, "Signal usable?")
    arrow(ax, (31, 66.5), (35, 66.5))
    arrow(ax, (58, 66.5), (62, 66.5))
    arrow(ax, (85, 66.5), (92, 66.5))
    arrow(
        ax,
        (110.5, 66.5),
        (114, 66.5),
        label="NO",
        color=COLORS["exclude"],
        label_offset=(0, 2),
    )
    elbow_arrow(
        ax,
        ((101, 79.5), (101, 75), (19.5, 75), (19.5, 72)),
        label="YES",
        label_at=(96, 75),
        color="#536F86",
        linewidth=1.5,
    )
    arrow(
        ax,
        (95, 110),
        (95, 100),
        label="DERIVE",
        label_offset=(4.2, 0),
        color="#536F86",
        linewidth=1.7,
    )

    # 4 · Analysis-ready measurements
    band(
        ax,
        4,
        "Gold: build analysis ready EEG datasets",
        5,
        25,
        110,
        26,
        face=COLORS["gold_bg"],
        edge=COLORS["gold_border"],
    )
    card(
        ax,
        8,
        30.5,
        23,
        "Condition windows",
        (),
        border=COLORS["green_border"],
        title_color="#3F7143",
        title_size=9.0,
    )
    card(
        ax,
        35,
        30.5,
        23,
        "Ad and no ad windows",
        (),
        border=COLORS["conditional"],
        title_color=COLORS["conditional"],
        title_size=8.5,
    )
    card(
        ax,
        62,
        30.5,
        21,
        "Extract 4 s features",
        (),
        border=COLORS["gold_border"],
        title_size=8.5,
    )
    card(
        ax,
        89,
        30.5,
        23,
        "Validate datasets",
        (),
        border=COLORS["gold_border"],
        title_size=8.8,
    )
    arrow(ax, (31, 35.5), (35, 35.5))
    arrow(ax, (58, 35.5), (62, 35.5))
    arrow(ax, (83, 35.5), (89, 35.5))

    # 5 · Inference and communication
    band(
        ax,
        5,
        "Analysis: compare conditions and report findings",
        5,
        2,
        110,
        19,
        face=COLORS["grey_bg"],
        edge=COLORS["grey_border"],
    )
    card(
        ax,
        8,
        5,
        30,
        "Condition contrasts",
        (),
        height=8,
        border=COLORS["grey_border"],
        title_size=9.1,
    )
    card(
        ax,
        45,
        5,
        30,
        "Ad response contrasts",
        (),
        height=8,
        border=COLORS["grey_border"],
        title_size=9.1,
    )
    card(
        ax,
        82,
        5,
        30,
        "Results and figures",
        (),
        height=8,
        border=COLORS["grey_border"],
    )
    arrow(ax, (38, 9), (45, 9))
    arrow(ax, (75, 9), (82, 9))
    elbow_arrow(
        ax,
        ((100.5, 30.5), (100.5, 23), (2, 23), (2, 9), (8, 9)),
        color="#536F86",
        linewidth=1.7,
    )
    elbow_arrow(
        ax,
        ((110.5, 66.5), (117, 66.5), (117, 49), (112, 49)),
        label="YES",
        label_at=(110, 53),
        color="#536F86",
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
    svg_path = HERE / "eeg_pipeline.svg"
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_path.read_text().splitlines())
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
