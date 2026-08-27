"""Publication figure v2 of the laboratory EEG preprocessing pipeline.

Four lake bands. Dataset A and Dataset B are parallel. Inference is omitted.

Silver cards follow ``clean_recording()`` in
``analysis/eeg/preprocessing/silver/signal/clean_eeg.py``.

Original ``eeg_pipeline.py`` / ``eeg_pipeline.png`` is untouched.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


HERE = Path(__file__).resolve().parent
W, H = 112.0, 108.0

INK = "#243240"
MUTED = "#53616E"
LINE = "#7A8792"
CARD = "#FFFFFF"
BLUE, BLUE_E = "#EDF5FB", "#7FA9CB"
PURPLE, PURPLE_E = "#F3F1FA", "#8E86BE"
GREEN, GREEN_E = "#EEF6EE", "#6FA574"
GOLD, GOLD_E = "#FDF6E6", "#C4B07A"
DATASET_A = "#2F6B45"
DATASET_B = "#8A4E22"


def rounded(ax, x, y, w, h, *, face, edge, r=1.2, lw=1.05, z=1):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle=f"round,pad=0.02,rounding_size={r}",
            facecolor=face,
            edgecolor=edge,
            linewidth=lw,
            zorder=z,
        )
    )


def txt(ax, x, y, s, *, size=8.5, weight="normal", color=INK, ha="left", va="center"):
    ax.text(
        x,
        y,
        s,
        fontsize=size,
        fontweight=weight,
        color=color,
        ha=ha,
        va=va,
        zorder=5,
        clip_on=False,
    )


def arrow(ax, a, b, *, color=LINE, lw=1.0, rad=0.0, scale=10.5):
    ax.add_patch(
        FancyArrowPatch(
            a,
            b,
            arrowstyle="-|>",
            mutation_scale=scale,
            linewidth=lw,
            color=color,
            shrinkA=1.2,
            shrinkB=1.6,
            connectionstyle=f"arc3,rad={rad}",
            zorder=2,
        )
    )


def badge(ax, x, y, n, edge):
    ax.text(
        x,
        y,
        str(n),
        ha="center",
        va="center",
        fontsize=8.0,
        fontweight="bold",
        color="white",
        bbox={"boxstyle": "circle,pad=0.22", "facecolor": edge, "edgecolor": edge},
        zorder=6,
    )


def band(ax, n, title, x, y, w, h, *, face, edge):
    rounded(ax, x, y, w, h, face=face, edge=edge, r=1.6, lw=1.2)
    badge(ax, x + 3.6, y + h - 2.45, n, edge)
    txt(ax, x + 7.4, y + h - 2.45, title, size=9.4, weight="bold")


def card(ax, x, y, w, h, title, sub="", *, edge):
    rounded(ax, x, y, w, h, face=CARD, edge=edge, r=1.0, lw=0.95, z=3)
    if sub:
        txt(ax, x + w / 2, y + h * 0.64, title, size=8.0, weight="bold", ha="center")
        txt(ax, x + w / 2, y + h * 0.30, sub, size=7.0, color=MUTED, ha="center")
    else:
        txt(ax, x + w / 2, y + h / 2, title, size=8.0, weight="bold", ha="center")


def build() -> plt.Figure:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans"],
            "mathtext.fontset": "dejavusans",
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
        }
    )
    fig, ax = plt.subplots(figsize=(8.8, 8.4))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    txt(ax, 56, 105.4, "Laboratory EEG Preprocessing Pipeline", size=13.2, weight="bold", ha="center")
    txt(
        ax,
        56,
        102.6,
        "19 people  ·  32 channels  ·  500 Hz recording",
        size=8.2,
        color=MUTED,
        ha="center",
    )

    # 1 Ingestion
    band(ax, 1, "Ingestion", 3, 91.2, 106, 10.0, face=BLUE, edge=BLUE_E)
    card(ax, 6.2, 91.8, 30.0, 5.2, "EEG recording", r"Cz online  ·  Fpz ground", edge=BLUE_E)
    card(ax, 39.0, 91.8, 30.0, 5.2, "Experiment log", "JSONL events  ·  LSL names", edge=BLUE_E)
    card(ax, 71.8, 91.8, 34.0, 5.2, "Identity map", r"subject  $\leftrightarrow$  experiment  $\leftrightarrow$  XDF", edge=BLUE_E)
    arrow(ax, (36.2, 94.4), (39.0, 94.4))
    arrow(ax, (69.0, 94.4), (71.8, 94.4))
    arrow(ax, (56, 91.2), (56, 89.4), color="#536F86", lw=1.05)

    # 2 Bronze
    band(ax, 2, "Bronze", 3, 77.4, 106, 11.4, face=PURPLE, edge=PURPLE_E)
    card(ax, 6.2, 78.4, 31.4, 6.2, "Raw XDF + logs", "immutable inventory", edge=PURPLE_E)
    card(ax, 40.4, 78.4, 31.4, 6.2, "Link and audit", "clocks  ·  marker health", edge=PURPLE_E)
    card(ax, 74.6, 78.4, 31.2, 6.2, "Cohort", "18 lab  ·  Subject 4 out", edge=PURPLE_E)
    arrow(ax, (37.6, 81.5), (40.4, 81.5))
    arrow(ax, (71.8, 81.5), (74.6, 81.5))
    arrow(ax, (56, 77.2), (56, 75.2), color="#536F86", lw=1.05)

    # 3 Silver — two jobs: event timeline, then cleaned continuous EEG
    band(ax, 3, "Silver", 3, 44.8, 106, 29.8, face=GREEN, edge=GREEN_E)

    rounded(ax, 5.4, 61.6, 100.4, 7.6, face="#F6FBF6", edge=GREEN_E, r=1.0, lw=0.7, z=1)
    txt(ax, 7.0, 67.8, "Event preprocessing", size=6.8, weight="bold", color=DATASET_A)
    card(ax, 7.2, 62.2, 30.4, 4.8, "Marker audit", "duplicates  ·  missing", edge=GREEN_E)
    card(ax, 40.0, 62.2, 31.0, 4.8, "Align event clocks", r"JSONL  $\leftrightarrow$  XDF LSL", edge=GREEN_E)
    card(ax, 73.4, 62.2, 31.2, 4.8, "Canonical markers", "observed or reconstructed", edge=GREEN_E)
    arrow(ax, (37.6, 64.6), (40.0, 64.6))
    arrow(ax, (71.0, 64.6), (73.4, 64.6))

    arrow(ax, (56.0, 61.6), (56.0, 60.0), color=GREEN_E)

    rounded(ax, 5.4, 45.6, 100.4, 14.2, face="#F6FBF6", edge=GREEN_E, r=1.0, lw=0.7, z=1)
    txt(ax, 7.0, 58.4, "EEG signal QC and preprocessing", size=6.8, weight="bold", color=DATASET_A)
    card(ax, 7.2, 53.0, 47.0, 4.6, r"XDF $\rightarrow$ MNE Raw", r"$\mu$V $\rightarrow$ V  ·  10–20  ·  annotations", edge=GREEN_E)
    card(ax, 56.6, 53.0, 47.8, 4.6, "Channel QC", r"condition-blind  ·  QC $\cup$ review", edge=GREEN_E)
    arrow(ax, (54.2, 55.3), (56.6, 55.3))

    arrow(ax, (30.7, 53.0), (30.7, 52.0), color=GREEN_E)

    clean = [
        (7.2, 16.6, "Notch 50 Hz", "line noise"),
        (25.8, 16.4, "0.5–40 Hz", "band-pass"),
        (44.2, 16.4, "Average ref", "exclude bads"),
        (62.6, 16.4, "Spline interp", "spherical"),
    ]
    for x, w, title, sub in clean:
        card(ax, x, 46.2, w, 5.8, title, sub, edge=GREEN_E)
    rounded(ax, 81.0, 46.2, 23.4, 5.8, face=CARD, edge=GREEN_E, r=1.0, lw=0.95, z=3)
    txt(ax, 92.7, 50.4, "ICA", size=7.8, weight="bold", ha="center")
    txt(ax, 92.7, 48.4, r"99% variance  ·  $\leq$3 ocular", size=6.6, color=MUTED, ha="center")
    edges = [(7.2, 16.6), (25.8, 16.4), (44.2, 16.4), (62.6, 16.4), (81.0, 23.4)]
    for (x0, w0), (x1, _) in zip(edges[:-1], edges[1:]):
        arrow(ax, (x0 + w0, 49.1), (x1, 49.1), color=GREEN_E)

    arrow(ax, (56, 44.6), (56, 43.6), color="#536F86")

    # 4 Gold — shared steps in order, then the two paths
    band(ax, 4, "Gold", 3, 13.6, 106, 29.8, face=GOLD, edge=GOLD_E)
    gold_steps = [
        (6.2, 29.6, "Epoch slicing", r"$K_i$ complete 4 s, each $\mathbb{R}^{32 \times 2000}$"),
        (38.0, 31.6, "Peak-to-peak reject", "any channel above 1050 µV"),
        (71.8, 34.0, "Welch PSD", "2 s windows, 50% overlap"),
    ]
    for x, w, title, sub in gold_steps:
        card(ax, x, 32.4, w, 6.4, title, sub, edge=GOLD_E)
    arrow(ax, (35.8, 35.6), (38.0, 35.6), color=GOLD_E)
    arrow(ax, (69.6, 35.6), (71.8, 35.6), color=GOLD_E)

    rounded(ax, 6.2, 24.8, 99.6, 6.2, face=CARD, edge=GOLD_E, r=1.0, lw=1.05, z=3)
    txt(ax, 56.0, 28.8, r"16 features  $\in \mathbb{R}^{16}$", size=8.4, weight="bold", ha="center")
    txt(ax, 56.0, 26.9, r"Fz $\theta$, posterior $\alpha$, FAA, Pope (global, FC), Kislov", size=7.2, ha="center")
    txt(
        ax,
        56.0,
        25.4,
        r"$\delta\,\theta\,\alpha\,\beta\,\gamma$ band dB and relative",
        size=7.4,
        color=MUTED,
        ha="center",
    )
    arrow(ax, (56.0, 32.4), (56.0, 31.0), color=GOLD_E)

    rounded(ax, 6.2, 14.8, 49.0, 8.6, face="#F4FAF4", edge=DATASET_A, r=1.2, lw=1.15, z=2)
    txt(ax, 30.7, 21.2, "Dataset A  —  condition windows", size=8.6, weight="bold", color=DATASET_A, ha="center")
    txt(ax, 30.7, 19.2, "5 conditions", size=7.6, ha="center")
    txt(ax, 30.7, 17.2, r"$Y_A \in \mathbb{R}^{18 \times 5 \times 16}$", size=9.2, weight="bold", color=DATASET_A, ha="center")
    txt(ax, 30.7, 15.6, "median, IQR, baseline delta", size=7.2, color=MUTED, ha="center")

    rounded(ax, 57.8, 14.8, 48.0, 8.6, face="#FBF6F0", edge=DATASET_B, r=1.2, lw=1.15, z=2)
    txt(ax, 81.8, 21.2, "Dataset B  —  ad windows", size=8.6, weight="bold", color=DATASET_B, ha="center")
    txt(ax, 81.8, 19.2, "4 ads + 2 no-ad", size=7.6, ha="center")
    txt(ax, 81.8, 17.2, r"$Y_B \in \mathbb{R}^{18 \times 6 \times 16}$", size=9.2, weight="bold", color=DATASET_B, ha="center")
    txt(ax, 81.8, 15.6, r"post $-$ pre", size=7.2, color=MUTED, ha="center")

    arrow(ax, (42.0, 24.8), (30.7, 23.4), color=DATASET_A, rad=-0.22)
    arrow(ax, (70.0, 24.8), (81.8, 23.4), color=DATASET_B, rad=0.22)

    txt(ax, 4.0, 12.0, "Shape", size=8.0, weight="bold", color=MUTED)
    txt(
        ax,
        14.2,
        12.0,
        r"$T_i$: samples for person $i$.  $K_i$: complete 4 s epochs for person $i$.",
        size=6.6,
        color=MUTED,
    )
    chips = [
        (4.0, 21.0, r"$X$  raw", r"$\mathbb{R}^{18 \times 32 \times T_i}$"),
        (27.0, 21.6, r"$\tilde{X}$  cleaned", r"$\mathbb{R}^{18 \times 32 \times T_i}$"),
        (50.6, 27.4, r"$E$  epochs", r"$\mathbb{R}^{18 \times K_i \times 32 \times 2000}$"),
    ]
    for x, w, title, sub in chips:
        rounded(ax, x, 4.4, w, 5.6, face="#F7F8FA", edge="#C5CED4", r=1.6, z=3)
        txt(ax, x + w / 2, 8.0, title, size=7.4, weight="bold", ha="center")
        txt(ax, x + w / 2, 5.8, sub, size=6.8, color=MUTED, ha="center")
    rounded(ax, 80.0, 4.0, 28.8, 6.4, face="#F7F8FA", edge="#C5CED4", r=1.6, z=3)
    txt(ax, 94.4, 8.4, r"$Y_A \in \mathbb{R}^{18 \times 5 \times 16}$", size=7.2, weight="bold", ha="center")
    txt(ax, 94.4, 5.8, r"$Y_B \in \mathbb{R}^{18 \times 6 \times 16}$", size=7.2, weight="bold", ha="center")
    xs, ws = [c[0] for c in chips], [c[1] for c in chips]
    for x0, w0, x1 in zip(xs[:-1], ws[:-1], xs[1:]):
        arrow(ax, (x0 + w0, 7.2), (x1, 7.2))
    arrow(ax, (78.0, 7.2), (80.0, 7.2))

    return fig


def main() -> None:
    figure = build()
    for ext in ("png", "pdf", "svg"):
        figure.savefig(
            HERE / f"eeg_pipeline_v2.{ext}",
            dpi=300 if ext == "png" else None,
            bbox_inches="tight",
            facecolor="white",
            pad_inches=0.08,
        )
    plt.close(figure)
    svg = HERE / "eeg_pipeline_v2.svg"
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
