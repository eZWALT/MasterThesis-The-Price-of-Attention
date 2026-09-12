"""DO NOT use this as the thesis montage.

The signed-off figure is Sebastian's PNG:
docs/overleaf/thesis/figures/preprocessing/eeg_montage.png
(commit c9882fb). This script is a leftover generated stand-in.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

HERE = Path(__file__).resolve().parent
CLAY, TEAL, SLATE, LINE = "#C45C26", "#2A7F8E", "#6B7280", "#7A8792"

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
FZ = {"Fz"}


def color_of(name: str) -> str:
    if name in FZ:
        return CLAY
    if name in POSTERIOR:
        return TEAL
    return SLATE


def main() -> None:
    assert len(RECORDED) == 32
    plt.rcParams.update({"pdf.fonttype": 42, "font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(figsize=(5.4, 5.8))
    ax.set_aspect("equal")
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.48, 1.42)
    ax.axis("off")

    ax.add_patch(Circle((0, 0), 1.18, fill=False, edgecolor=LINE, linewidth=1.4))
    ax.plot([-0.18, 0.18], [1.18, 1.18], color=LINE, lw=1.4)
    ax.plot([0, 0], [1.18, 1.32], color=LINE, lw=1.4)
    ax.add_patch(Circle((-1.22, 0.0), 0.07, fill=False, edgecolor=LINE, lw=1.1))
    ax.add_patch(Circle((1.22, 0.0), 0.07, fill=False, edgecolor=LINE, lw=1.1))

    for name in RECORDED:
        x, y = XY[name]
        filled = name in FZ or name in POSTERIOR
        ax.scatter(
            [x], [y], s=92,
            facecolor=color_of(name) if filled else "white",
            edgecolor=color_of(name), linewidths=1.3, zorder=3,
        )
        dy = 0.095 if y >= 0 else -0.095
        ax.text(x, y + dy, name, ha="center", va="center", fontsize=6.2,
                color=SLATE, fontweight="bold" if filled else None)

    gx, gy = XY["Fpz"]
    ax.scatter([gx], [gy], s=48, marker="s", facecolors="none",
               edgecolors=LINE, linewidths=1.1, zorder=3)
    ax.text(gx, gy + 0.10, "Fpz gnd", ha="center", va="center",
            fontsize=6.0, color=SLATE)

    handles = [
        plt.Line2D([], [], marker="o", ls="", ms=8, mfc=CLAY, mec=CLAY,
                   label=r"Fz: frontal-midline $\theta$ (confirmatory)"),
        plt.Line2D([], [], marker="o", ls="", ms=8, mfc=TEAL, mec=TEAL,
                   label=r"Posterior $\alpha$ set (confirmatory)"),
        plt.Line2D([], [], marker="o", ls="", ms=8, mfc="white", mec=SLATE,
                   label="Other recorded channels"),
    ]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.02),
              frameon=False, fontsize=7, ncol=1)
    ax.set_title("32-channel 10–20 montage (actiCHamp)", fontsize=9, color=SLATE)
    ax.text(0, -1.38, "Ground Fpz (not recorded)  ·  online reference Cz",
            ha="center", va="center", fontsize=7, color=SLATE)

    out = HERE / "eeg_montage.pdf"
    fig.savefig(out, format="pdf", bbox_inches="tight")
    print("wrote", out, "channels", len(RECORDED))


if __name__ == "__main__":
    main()
