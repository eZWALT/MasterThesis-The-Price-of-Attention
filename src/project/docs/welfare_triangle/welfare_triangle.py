"""Welfare triangle: advertisers, AI provider, customer.

Same visual language as the retrieval and EEG pipeline figures
(rounded cards, muted ink, bidirectional edges). Graphviz cannot sit
three nodes on an equilateral triangle, so this is matplotlib.

Rebuild::

    python3 src/project/docs/welfare_triangle/welfare_triangle.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon


HERE = Path(__file__).resolve().parent
OUT = HERE / "welfare_triangle"

INK = "#243240"
MUTED = "#4A5864"
LINE = "#5E6D7A"
FILL = "#F4F6F8"

# Three poles, one colour each: house / money / user.
RED, RED_E = "#F6D0D4", "#9B0014"
GREEN, GREEN_E = "#C8EBD6", "#1F7A4D"
BLUE, BLUE_E = "#C5DBF4", "#1D4E89"
PILL, PILL_E = "#FFFFFF", "#5B3A9E"


def rounded(ax, x, y, w, h, *, face, edge, r=0.16, lw=1.35, z=3):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle=f"round,pad=0.012,rounding_size={r}",
            facecolor=face,
            edgecolor=edge,
            linewidth=lw,
            zorder=z,
        )
    )


def txt(ax, x, y, s, *, size=13, weight="normal", color=INK, ha="center", va="center"):
    ax.text(
        x,
        y,
        s,
        fontsize=size,
        fontweight=weight,
        color=color,
        ha=ha,
        va=va,
        zorder=8,
        clip_on=False,
        fontfamily="DejaVu Sans",
        linespacing=1.25,
    )


def card(ax, cx, cy, w, h, *, face, edge, title, subtitle):
    rounded(ax, cx - w / 2, cy - h / 2, w, h, face=face, edge=edge, lw=1.55)
    txt(ax, cx, cy + 0.26, title, size=18.5, weight="bold")
    txt(ax, cx, cy - 0.22, subtitle, size=14, color=MUTED)


def along(a, b, t):
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


def bidir(ax, a, b):
    ax.add_patch(
        FancyArrowPatch(
            a,
            b,
            arrowstyle="<|-|>",
            mutation_scale=16,
            linewidth=1.65,
            color=LINE,
            shrinkA=0,
            shrinkB=0,
            zorder=2,
        )
    )


def main():
    w_fig, h_fig = 10.4, 7.4
    fig, ax = plt.subplots(figsize=(w_fig, h_fig), dpi=180)
    ax.set_xlim(0, w_fig)
    ax.set_ylim(0, h_fig)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Sit the policy pill lower, in the wider part of the triangle,
    # so a compact box does not overflow the diagonals.
    origin = (5.2, 3.48)
    provider = (5.2, 5.82)
    advertisers = (1.95, 1.98)
    customer = (8.45, 1.98)

    ax.add_patch(
        Polygon(
            [provider, advertisers, customer],
            closed=True,
            facecolor=FILL,
            edgecolor="none",
            zorder=0,
        )
    )

    # Stop the arrows short of the cards.
    pa, pb = along(provider, advertisers, 0.22), along(provider, advertisers, 0.78)
    pc, pd = along(provider, customer, 0.22), along(provider, customer, 0.78)
    pe, pf = along(advertisers, customer, 0.22), along(advertisers, customer, 0.78)
    bidir(ax, pa, pb)
    bidir(ax, pc, pd)
    bidir(ax, pe, pf)

    cw, ch = 2.62, 1.62
    card(
        ax,
        *provider,
        cw,
        ch,
        face=RED,
        edge=RED_E,
        title="AI provider",
        subtitle="platform for all three",
    )
    card(
        ax,
        *advertisers,
        cw,
        ch,
        face=GREEN,
        edge=GREEN_E,
        title="Advertisers",
        subtitle="pay for the attention",
    )
    card(
        ax,
        *customer,
        cw,
        ch,
        face=BLUE,
        edge=BLUE_E,
        title="Customer",
        subtitle="gives the attention",
    )

    # Compact pill inside the triangle. Mathtext capital Pi (majuscule),
    # not lowercase pi and not a heavy DejaVu doorway glyph.
    pw, ph = 2.18, 1.48
    rounded(
        ax,
        origin[0] - pw / 2,
        origin[1] - ph / 2,
        pw,
        ph,
        face=PILL,
        edge=PILL_E,
        r=0.28,
        lw=1.8,
        z=4,
    )
    ax.text(
        origin[0],
        origin[1] + 0.30,
        r"$\Pi$",
        fontsize=26,
        color=PILL_E,
        ha="center",
        va="center",
        zorder=8,
        clip_on=False,
    )
    ax.text(
        origin[0],
        origin[1] - 0.28,
        "advertisement\npolicy",
        fontsize=13.5,
        color=PILL_E,
        ha="center",
        va="center",
        zorder=8,
        clip_on=False,
        fontfamily="DejaVu Sans",
        linespacing=1.12,
    )

    fig.tight_layout(pad=0.45)
    fig.savefig(
        OUT.with_suffix(".png"),
        dpi=200,
        bbox_inches="tight",
        pad_inches=0.08,
        facecolor="white",
    )
    fig.savefig(
        OUT.with_suffix(".pdf"),
        bbox_inches="tight",
        pad_inches=0.08,
        facecolor="white",
    )
    plt.close(fig)


if __name__ == "__main__":
    main()
