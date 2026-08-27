"""Online ad-retrieval pipeline figure.

Experimental default (``build_default_stages()`` / ``core/config.py``):
HyDE on, hybrid on, reranker on. Context-summary and ad-summarizer off.
ThradBERT is logged every turn and does not gate serving.

The figure is a funnel (117k -> 30 -> 10 -> 1). Hybrid retrieval is the
merge of the dense shortlist and a BM25 pass over the same user query
(two incoming arrows). The injected result is drawn as one ad, not the
internal top-3 formatter pool.

Graphviz cannot taper cards, so this script is matplotlib. Rebuild::

    python3 src/project/docs/retrieval_pipeline/make_icons.py
    python3 src/project/docs/retrieval_pipeline/retrieval_pipeline.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon
from PIL import Image


HERE = Path(__file__).resolve().parent
RES = HERE / "resources"
OUT = HERE / "retrieval_pipeline"

# One data unit = one inch (equal aspect).
W, H = 14.55, 6.85

INK = "#243240"
MUTED = "#4A5864"
LINE = "#5E6D7A"
CARD = "#FFFFFF"
CARD_E = "#8A96A3"
BLUE, BLUE_E = "#E8F0FE", "#7E9CC4"
PURPLE, PURPLE_E = "#F3EEF9", "#8E7DB8"
GOLD, GOLD_E = "#FDF6E3", "#C4A86A"


def rounded(ax, x, y, w, h, *, face, edge, r=0.18, lw=1.15, z=1):
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


def txt(ax, x, y, s, *, size=12, weight="normal", color=INK, ha="center", va="center"):
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
    )


def arrow(ax, a, b, *, color=LINE, lw=1.55, rad=0.0, style="solid", scale=14):
    ax.add_patch(
        FancyArrowPatch(
            a,
            b,
            arrowstyle="-|>",
            mutation_scale=scale,
            linewidth=lw,
            color=color,
            linestyle=style,
            shrinkA=2.0,
            shrinkB=3.0,
            connectionstyle=f"arc3,rad={rad}",
            zorder=4,
        )
    )


def icon_at(ax, name, xy, zoom):
    arr = np.asarray(Image.open(RES / name).convert("RGBA"))
    ab = AnnotationBbox(
        OffsetImage(arr, zoom=zoom),
        xy,
        frameon=False,
        pad=0.0,
        zorder=7,
    )
    ax.add_artist(ab)


def card(ax, x, y, w, h, png, title, sub, *, zoom, title_size=12.5, sub_size=10.5, detail="", edge=CARD_E, lw=1.2):
    rounded(ax, x, y, w, h, face=CARD, edge=edge, r=0.16, lw=lw, z=5)
    cx = x + w / 2
    if detail:
        icon_at(ax, png, (cx, y + h * 0.70), zoom)
        txt(ax, cx, y + h * 0.40, title, size=title_size, weight="bold")
        txt(ax, cx, y + h * 0.24, sub, size=sub_size, color=MUTED)
        txt(ax, cx, y + h * 0.10, detail, size=sub_size, color=MUTED)
    elif sub:
        icon_at(ax, png, (cx, y + h * 0.62), zoom)
        txt(ax, cx, y + h * 0.28, title, size=title_size, weight="bold")
        txt(ax, cx, y + h * 0.13, sub, size=sub_size, color=MUTED)
    else:
        icon_at(ax, png, (cx, y + h * 0.62), zoom)
        txt(ax, cx, y + h * 0.18, title, size=title_size, weight="bold")


def mid(box, side):
    x, y, w, h = box
    if side == "e":
        return (x + w, y + h / 2)
    if side == "w":
        return (x, y + h / 2)
    if side == "s":
        return (x + w / 2, y)
    if side == "n":
        return (x + w / 2, y + h)
    return (x + w / 2, y + h / 2)


def build() -> plt.Figure:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans"],
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
        }
    )
    fig, ax = plt.subplots(figsize=(W, H), dpi=150)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    txt(ax, W / 2, H - 0.22, "Online Ad Retrieval Pipeline", size=18, weight="bold")

    # --- Query column: input, HyDE, embedding model ---
    rounded(ax, 0.20, 0.20, 3.18, 6.15, face=BLUE, edge=BLUE_E, r=0.20, lw=1.35, z=1)
    txt(ax, 0.38, 6.12, "Query", size=14.5, weight="bold", ha="left")

    qw, qh, qgap = 2.74, 1.68, 0.20
    qx = 0.42
    embed = (qx, 0.38, qw, qh)
    hyde = (qx, 0.38 + qh + qgap, qw, qh)
    query = (qx, 0.38 + 2 * (qh + qgap), qw, qh)

    card(ax, *query, "chat.png", "User query", "last 4 turns", zoom=0.44, title_size=13, sub_size=11)
    card(ax, *hyde, "ollama.png", "HyDE", "Qwen3.6", zoom=0.44, title_size=13, sub_size=11)
    card(ax, *embed, "neural.png", "Embedding", "Qwen3 0.6B", zoom=0.44, title_size=13, sub_size=11)
    arrow(ax, mid(query, "s"), mid(hyde, "n"))
    arrow(ax, mid(hyde, "s"), mid(embed, "n"))

    # One funnel, two fills that meet at a thin white seam.
    # One funnel: steep Recall wedge, gentler Precision spout, thin color seam.
    x0, x1 = 3.46, 14.10
    cut = 9.92
    yt0, yb0 = 6.20, 0.18
    yt_cut, yb_cut = 4.50, 1.86
    yt1, yb1 = 4.02, 2.22

    def _lerp(x, xa, ya, xb, yb):
        t = np.clip((np.asarray(x, dtype=float) - xa) / (xb - xa), 0.0, 1.0)
        return ya + t * (yb - ya)

    def y_top(x):
        x = np.asarray(x, dtype=float)
        y = _lerp(x, x0, yt0, cut, yt_cut)
        return np.where(x > cut, _lerp(x, cut, yt_cut, x1, yt1), y)

    def y_bot(x):
        x = np.asarray(x, dtype=float)
        y = _lerp(x, x0, yb0, cut, yb_cut)
        return np.where(x > cut, _lerp(x, cut, yb_cut, x1, yb1), y)

    def funnel_piece(xa, xb, n=20):
        xs = np.linspace(xa, xb, n)
        top = np.column_stack([xs, y_top(xs)])
        bot = np.column_stack([xs[::-1], y_bot(xs[::-1])])
        return np.vstack([top, bot])

    ax.add_patch(
        Polygon(funnel_piece(x0, cut), closed=True, facecolor=PURPLE, edgecolor="none", linewidth=0, zorder=1)
    )
    ax.add_patch(
        Polygon(funnel_piece(cut, x1), closed=True, facecolor=GOLD, edgecolor="none", linewidth=0, zorder=1)
    )
    ax.plot(
        [cut, cut],
        [float(y_bot(cut)), float(y_top(cut))],
        color="white",
        linewidth=2.0,
        solid_capstyle="butt",
        zorder=2,
    )
    ax.add_patch(
        Polygon(
            funnel_piece(x0, x1),
            closed=True,
            facecolor="none",
            edgecolor="#A8926A",
            linewidth=2.1,
            zorder=3,
        )
    )
    txt(ax, 3.66, float(y_top(3.66)) - 0.22, "Recall", size=14.5, weight="bold", ha="left", color="#5A4A86")
    txt(ax, cut + 0.18, float(y_top(cut + 0.18)) - 0.20, "Precision", size=14, weight="bold", ha="left", color="#8A6A28")

    cy = 3.18
    faiss = (3.66, cy - 1.28, 3.42, 2.56)
    hybrid = (7.24, cy - 1.02, 2.32, 2.04)
    rerank = (10.18, cy - 0.84, 1.96, 1.68)
    ad = (12.36, cy - 0.76, 1.48, 1.52)

    card(
        ax,
        *faiss,
        "meta.png",
        "117k  ->  30",
        "FAISS dense",
        detail="cosine k-NN",
        zoom=0.46,
        title_size=15.5,
        sub_size=11.5,
    )
    card(ax, *hybrid, "filter.png", "Hybrid", "BM25 + dense", zoom=0.44, title_size=16, sub_size=12)
    card(ax, *rerank, "neural.png", "30  ->  10", "BGE rerank", zoom=0.40, title_size=15, sub_size=12)
    card(ax, *ad, "ad.png", "1 ad", "", zoom=0.40, title_size=17, edge=GOLD_E, lw=1.8)

    # Dense path: embedding model -> FAISS -> Hybrid -> rerank -> one ad.
    arrow(ax, mid(embed, "e"), mid(faiss, "w"))
    txt(
        ax,
        (mid(embed, "e")[0] + mid(faiss, "w")[0]) / 2,
        (mid(embed, "e")[1] + mid(faiss, "w")[1]) / 2 + 0.22,
        "dense",
        size=12,
        weight="bold",
        color=MUTED,
    )
    arrow(ax, mid(faiss, "e"), mid(hybrid, "w"))
    arrow(ax, mid(hybrid, "e"), mid(rerank, "w"))
    arrow(ax, mid(rerank, "e"), mid(ad, "w"))

    # Second incoming arrow into Hybrid: BM25 over the original user query.
    arrow(ax, mid(query, "e"), mid(hybrid, "n"), style="dashed", rad=-0.18, lw=1.9)
    txt(ax, 5.85, 4.95, "BM25", size=14, weight="bold", color="#3D4A58")

    return fig


def main() -> None:
    fig = build()
    fig.savefig(f"{OUT}.png", dpi=150, facecolor="white")
    fig.savefig(f"{OUT}.pdf", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
