"""Thesis montage in Sebastian's cap style, our 32-channel rules.

Look: circular 10--20 schematic, labels inside the discs, GND / Cz as
black discs. High-contrast fills: red Fz, blue posterior alpha, yellow
other recorded.

Rules (acquisition_contract.md):
- 32 recorded actiCHamp labels
- Fpz = ground, not recorded (drawn as GND)
- Cz = online reference and recorded (drawn as the black centre disc)
- Red = Fz (midline theta). Blue = posterior alpha
  (O1, Oz, O2, P3, Pz, P4). Yellow = the other recorded channels.

Do not put Sebastian's FT9/TP9 labels or his green set (Fp1/F3/O1…) back.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

HERE = Path(__file__).resolve().parent

# Idealized 10--10 schematic, Cz at the origin, nasion +y.
# F9/F10/P9/P10 sit where a 32-ch actiCAP drawing puts them (not FT/TP).
XY = {
    "Cz": (0.00, 0.00),
    "Fpz": (0.00, 1.12),
    "Oz": (0.00, -1.00),
    "T7": (-1.00, 0.00),
    "T8": (1.00, 0.00),
    "Fp1": (-0.36, 0.93),
    "Fp2": (0.36, 0.93),
    "Fz": (0.00, 0.55),
    "F3": (-0.40, 0.55),
    "F4": (0.40, 0.55),
    "F7": (-0.80, 0.55),
    "F8": (0.80, 0.55),
    "F9": (-1.02, 0.32),
    "F10": (1.02, 0.32),
    "FC1": (-0.22, 0.30),
    "FC2": (0.22, 0.30),
    "FC5": (-0.62, 0.30),
    "FC6": (0.62, 0.30),
    "C3": (-0.50, 0.00),
    "C4": (0.50, 0.00),
    "CP1": (-0.22, -0.30),
    "CP2": (0.22, -0.30),
    "CP5": (-0.62, -0.30),
    "CP6": (0.62, -0.30),
    "Pz": (0.00, -0.55),
    "P3": (-0.40, -0.55),
    "P4": (0.40, -0.55),
    "P7": (-0.80, -0.55),
    "P8": (0.80, -0.55),
    "P9": (-1.02, -0.32),
    "P10": (1.02, -0.32),
    "O1": (-0.36, -0.93),
    "O2": (0.36, -0.93),
}

RECORDED = (
    "Fp1", "Fz", "F3", "F7", "F9", "FC5", "FC1", "C3", "T7", "CP5", "CP1",
    "Pz", "P3", "P7", "P9", "O1", "Oz", "O2", "P10", "P8", "P4", "CP2",
    "CP6", "T8", "C4", "Cz", "FC2", "FC6", "F10", "F8", "F4", "Fp2",
)
FZ = {"Fz"}
POSTERIOR = {"O1", "Oz", "O2", "P3", "Pz", "P4"}

RED = "#D32F2F"
BLUE = "#1565C0"
YELLOW = "#F9A825"
BLACK = "#1A1A1A"
RING = "#9E9E9E"
INK = "#222222"


def disc(ax, xy, r, facecolor, edgecolor, lw, z=4):
    ax.add_patch(Circle(xy, r, facecolor=facecolor, edgecolor=edgecolor,
                        linewidth=lw, zorder=z, joinstyle="round"))


def label(ax, xy, text, color, size):
    ax.text(xy[0], xy[1], text, ha="center", va="center", fontsize=size,
            color=color, zorder=5, clip_on=False)


def main() -> None:
    assert len(RECORDED) == 32
    assert set(RECORDED) <= set(XY)
    plt.rcParams.update({
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.family": "DejaVu Sans",
    })
    fig, ax = plt.subplots(figsize=(5.6, 5.4))
    fig.patch.set_facecolor("white")
    ax.set_aspect("equal")
    ax.set_xlim(-1.28, 1.28)
    ax.set_ylim(-1.28, 1.28)
    ax.axis("off")

    head_r = 1.12
    ax.add_patch(Circle((0, 0), head_r, fill=False, edgecolor=BLACK, lw=1.8, zorder=1))
    ax.add_patch(Circle((0, 0), 0.55, fill=False, edgecolor=RING, lw=1.05, zorder=1))
    ax.plot([-head_r, head_r], [0, 0], color=RING, lw=1.05, zorder=1)
    ax.plot([0, 0], [-head_r, head_r], color=RING, lw=1.05, zorder=1)

    r_ch, r_ref = 0.096, 0.118
    for name in RECORDED:
        if name == "Cz":
            continue
        xy = XY[name]
        if name in FZ:
            disc(ax, xy, r_ch, RED, "#B71C1C", 0.7)
            label(ax, xy, name, "white", 6.1)
        elif name in POSTERIOR:
            disc(ax, xy, r_ch, BLUE, "#0D47A1", 0.7)
            label(ax, xy, name, "white", 6.1)
        else:
            disc(ax, xy, r_ch, YELLOW, "#F57F17", 0.7)
            label(ax, xy, name, INK, 6.1)

    disc(ax, XY["Cz"], r_ref, BLACK, BLACK, 0.0)
    label(ax, XY["Cz"], "Cz", "white", 7.0)

    disc(ax, XY["Fpz"], r_ref, BLACK, BLACK, 0.0)
    label(ax, XY["Fpz"], "GND", "white", 6.2)

    out_pdf = HERE / "eeg_montage.pdf"
    out_png = HERE / "eeg_montage.png"
    fig.savefig(out_pdf, format="pdf", bbox_inches="tight", facecolor="white",
                pad_inches=0.04)
    fig.savefig(out_png, format="png", dpi=300, bbox_inches="tight",
                facecolor="white", pad_inches=0.04)
    plt.close(fig)
    print("wrote", out_pdf)
    print("wrote", out_png)


if __name__ == "__main__":
    main()
