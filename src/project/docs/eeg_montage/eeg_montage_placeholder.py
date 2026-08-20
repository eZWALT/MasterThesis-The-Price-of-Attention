"""Placeholder 32-channel 10-20 montage for the paper.

Teammate replaces Overleaf ``Figures/eeg_montage.pdf`` with the signed-off
drawing. This file only keeps a labelled slot so ``\\ref{fig:eeg}`` compiles.

Recorded labels follow the XDF contract in
``analysis/eeg/preprocessing/silver/signal/acquisition_contract.md``.
Fpz is ground (not a data channel). Cz is the online reference and is recorded.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle


HERE = Path(__file__).resolve().parent
INK = "#243240"
MUTED = "#53616E"
LINE = "#7A8792"
FZ = "#2F6B45"
POST = "#8A4E22"
FAA = "#4A6FA5"
OCULAR = "#8E86BE"
OTHER = "#7A8792"

# Approximate 10-20 / 10-10 plane. Nose is +y.
XY = {
    "Fp1": (-0.31, 0.95),
    "Fp2": (0.31, 0.95),
    "Fpz": (0.00, 1.02),
    "F9": (-0.95, 0.42),
    "F7": (-0.81, 0.58),
    "F3": (-0.40, 0.62),
    "Fz": (0.00, 0.62),
    "F4": (0.40, 0.62),
    "F8": (0.81, 0.58),
    "F10": (0.95, 0.42),
    "FC5": (-0.58, 0.32),
    "FC1": (-0.20, 0.32),
    "FC2": (0.20, 0.32),
    "FC6": (0.58, 0.32),
    "T7": (-1.00, 0.00),
    "C3": (-0.45, 0.00),
    "Cz": (0.00, 0.00),
    "C4": (0.45, 0.00),
    "T8": (1.00, 0.00),
    "CP5": (-0.58, -0.32),
    "CP1": (-0.20, -0.32),
    "CP2": (0.20, -0.32),
    "CP6": (0.58, -0.32),
    "P9": (-0.95, -0.42),
    "P7": (-0.81, -0.58),
    "P3": (-0.40, -0.62),
    "Pz": (0.00, -0.62),
    "P4": (0.40, -0.62),
    "P8": (0.81, -0.58),
    "P10": (0.95, -0.42),
    "O1": (-0.31, -0.95),
    "Oz": (0.00, -1.02),
    "O2": (0.31, -0.95),
}

RECORDED = (
    "Fp1", "Fz", "F3", "F7", "F9", "FC5", "FC1", "C3", "T7", "CP5", "CP1",
    "Pz", "P3", "P7", "P9", "O1", "Oz", "O2", "P10", "P8", "P4", "CP2",
    "CP6", "T8", "C4", "Cz", "FC2", "FC6", "F10", "F8", "F4", "Fp2",
)
POSTERIOR = {"O1", "Oz", "O2", "P3", "Pz", "P4"}


def color_of(name: str) -> str:
    if name == "Fz":
        return FZ
    if name in POSTERIOR:
        return POST
    if name in {"F3", "F4"}:
        return FAA
    if name in {"Fp1", "Fp2"}:
        return OCULAR
    return OTHER


def build() -> plt.Figure:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans"],
            "pdf.fonttype": 42,
        }
    )
    fig, ax = plt.subplots(figsize=(5.4, 6.1))
    fig.patch.set_facecolor("white")
    ax.set_aspect("equal")
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.55, 1.55)
    ax.axis("off")

    head = Circle((0, 0), 1.18, fill=False, edgecolor=LINE, linewidth=1.4)
    ax.add_patch(head)
    ax.plot([-0.18, 0.18], [1.18, 1.18], color=LINE, lw=1.4)
    ax.plot([0, 0], [1.18, 1.32], color=LINE, lw=1.4)
    ax.add_patch(Circle((-1.22, 0.0), 0.07, fill=False, edgecolor=LINE, lw=1.1))
    ax.add_patch(Circle((1.22, 0.0), 0.07, fill=False, edgecolor=LINE, lw=1.1))

    ax.text(0, 1.44, "PLACEHOLDER", ha="center", va="center", fontsize=11,
            color="#C45C5C", fontweight="bold")
    ax.text(0, 1.32, "replace with the signed-off 32-channel montage",
            ha="center", va="center", fontsize=7.2, color=MUTED)

    for name in RECORDED:
        x, y = XY[name]
        ax.scatter([x], [y], s=42, c=color_of(name), zorder=3, edgecolors="white", linewidths=0.4)
        dy = 0.075 if y >= 0 else -0.075
        ax.text(x, y + dy, name, ha="center", va="center", fontsize=6.2, color=INK)

    gx, gy = XY["Fpz"]
    ax.scatter([gx], [gy], s=36, marker="s", facecolors="none", edgecolors=LINE, linewidths=1.1, zorder=3)
    ax.text(gx, gy + 0.09, "Fpz gnd", ha="center", va="center", fontsize=6.0, color=MUTED)

    ax.text(
        0,
        -1.28,
        r"Fz $\theta$  ·  posterior $\alpha$  ·  F3/F4 FAA  ·  Fp1/Fp2 ocular",
        ha="center",
        va="center",
        fontsize=7.2,
        color=MUTED,
    )
    ax.text(
        0,
        -1.42,
        "Cz online ref  ·  Fpz ground  ·  32 recorded channels",
        ha="center",
        va="center",
        fontsize=7.0,
        color=MUTED,
    )

    return fig


def main() -> None:
    figure = build()
    for ext in ("png", "pdf"):
        figure.savefig(
            HERE / f"eeg_montage_placeholder.{ext}",
            dpi=300 if ext == "png" else None,
            bbox_inches="tight",
            facecolor="white",
            pad_inches=0.08,
        )
    plt.close(figure)


if __name__ == "__main__":
    main()
