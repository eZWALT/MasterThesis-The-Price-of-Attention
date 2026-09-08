"""Paper figure: Gold tables by grain, stream, and arm.

Catalog IDs (not filenames) are the card titles. Files stay as
provenance. Dataset A / Dataset B keep those names.

Rebuild::

    python src/project/docs/behavioural_pipeline/behavioural_grains.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
W, H = 188.0, 138.0

INK = "#243240"
MUTED = "#53616E"
HAIR = "#D0D6DC"
EDGE = "#B8C2CB"
RULE = "#8A96A2"
CARD = "#FFFFFF"
CELL = "#F7F8FA"
HEAD = "#F3F5F7"

LAB_C = "#2C5780"
CROWD_C = "#8A5A28"
NONE_C = "#9AA3AB"
JOIN_C = "#5C5288"

STREAM = {
    "beh": ("#C4A86A", "Behavioural", "lab + crowd"),
    "traj": ("#6FA574", "Trajectories", "2 sources"),
    "eeg": ("#7FA9CB", "EEG", "lab only"),
    "join": ("#8E86BE", "Joins", "not a grain"),
}

# Four sizes. All small copy is FS_SMALL.
FS_TITLE = 15.0
FS_GRAIN = 11.0
FS_STREAM = 9.4
FS_NAME = 8.5
FS_COUNT = 8.0
FS_SMALL = 7.4


def rounded(ax, x, y, w, h, *, face, edge=EDGE, lw=1.0, r=0.8, z=1):
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


def txt(ax, x, y, s, *, size, weight="normal", color=INK, ha="left", va="center"):
    ax.text(
        x,
        y,
        s,
        fontsize=size,
        fontweight=weight,
        color=color,
        ha=ha,
        va=va,
        zorder=6,
        clip_on=False,
        fontfamily="sans-serif",
    )


def arrow(ax, a, b):
    ax.add_patch(
        FancyArrowPatch(
            a,
            b,
            arrowstyle="-|>",
            mutation_scale=9,
            linewidth=1.05,
            color="#687988",
            zorder=2,
            shrinkA=0.4,
            shrinkB=0.4,
        )
    )


def fmt(n):
    return f"{n:,}" if isinstance(n, int) else n


def count_xs(x, cw):
    return x + cw - 21.6, x + cw - 12.2, x + cw - 2.4


def draw_counts(ax, x, cw, y, lab, crowd, total):
    xl, xc, xn = count_xs(x, cw)
    lab_s = "—" if lab is None else fmt(lab)
    crowd_s = "—" if crowd is None else fmt(crowd)
    tot_s = "—" if total is None else fmt(total)
    txt(ax, xl, y, lab_s, size=FS_COUNT, weight="bold", color=NONE_C if lab is None else LAB_C, ha="right")
    txt(ax, xc, y, crowd_s, size=FS_COUNT, weight="bold", color=NONE_C if crowd is None else CROWD_C, ha="right")
    txt(ax, xn, y, tot_s, size=FS_COUNT, weight="bold", color=NONE_C if total is None else INK, ha="right")


def file_row(ax, x, y, w, h, name, role, source, lab, crowd, total, *, joined=False):
    rounded(ax, x + 1.2, y, w - 2.4, h, face=CARD, edge=HAIR, lw=0.75, r=0.45, z=3)
    title_c = JOIN_C if joined else INK
    txt(ax, x + 2.5, y + h - 2.05, name, size=FS_NAME, weight="bold", color=title_c)
    sub = role if joined and role else source
    sub_c = MUTED if joined else NONE_C
    txt(ax, x + 2.5, y + 1.75, sub, size=FS_SMALL, color=sub_c)
    draw_counts(ax, x, w, y + h - 2.05, lab, crowd, total)


def view_label(ax, x, y, label):
    txt(ax, x + 2.5, y, label, size=FS_SMALL, weight="bold", color=MUTED)


def empty_cell(ax, x, y, w, h, title, reason):
    label = title if not reason else f"{title}  ·  {reason}"
    txt(ax, x + w / 2, y + h / 2, label, size=FS_NAME, color=NONE_C, ha="center")


def swatch(ax, x, y, color, label):
    ax.add_patch(Rectangle((x, y), 2.2, 2.2, facecolor=color, edgecolor=color, zorder=4, linewidth=0))
    txt(ax, x + 3.1, y + 1.1, label, size=FS_SMALL, weight="bold")


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
    fig, ax = plt.subplots(figsize=(18.4, 13.5))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    txt(ax, 4.8, 134.6, "Gold tables", size=FS_TITLE, weight="bold")
    txt(ax, 4.8, 131.5, "3 grains  ·  2 arms  ·  3 data types", size=FS_NAME, color=MUTED)

    swatch(ax, 118.0, 133.0, LAB_C, "Lab")
    swatch(ax, 134.0, 133.0, CROWD_C, "Crowd")
    swatch(ax, 154.0, 133.0, JOIN_C, "join")
    swatch(ax, 172.2, 133.0, NONE_C, "empty")

    stub_w = 23.0
    col_w = 51.4
    gap = 1.8
    x0 = stub_w + 5.6
    xs = [x0 + i * (col_w + gap) for i in range(3)]

    headers = (
        ("Message", "8 messages  →  chat"),
        ("Chat", "5 chats  →  person"),
        ("Person", "1 person"),
    )
    hy, hh = 120.2, 8.6
    for x, (name, roll) in zip(xs, headers):
        rounded(ax, x, hy, col_w, hh, face=HEAD, edge=EDGE, lw=1.05, r=0.7)
        txt(ax, x + 2.0, hy + 6.15, name, size=FS_GRAIN, weight="bold")
        txt(ax, x + 2.0, hy + 3.55, roll, size=FS_SMALL, color=MUTED)
        xl, xc, xn = count_xs(x, col_w)
        txt(ax, xl, hy + 1.65, "Lab", size=FS_SMALL, weight="bold", color=LAB_C, ha="right")
        txt(ax, xc, hy + 1.65, "Crowd", size=FS_SMALL, weight="bold", color=CROWD_C, ha="right")
        txt(ax, xn, hy + 1.65, "n", size=FS_SMALL, weight="bold", color=INK, ha="right")
    arrow(ax, (xs[0] + col_w, hy + 6.15), (xs[1], hy + 6.15))
    arrow(ax, (xs[1] + col_w, hy + 6.15), (xs[2], hy + 6.15))

    # Card: catalog name, role, provenance file, lab, crowd, n.
    grid = [
        (
            "beh",
            [
                [
                    ("file", "turns", "", "messages.csv", 720, 1440, 2160),
                ],
                [
                    ("view", "5 conditions"),
                    ("file", "ratings", "", "condition_features.csv", 90, 180, 270),
                    ("view", "4 ads"),
                    ("file", "recall", "", "advertisement_features.csv", 72, 144, 216),
                ],
                [
                    ("file", "BFI + demo", "", "person_features.csv", 18, 36, 54),
                    ("file", "contrasts", "", "contrast_scores.csv", 18, 36, 54),
                ],
            ],
        ),
        (
            "traj",
            [
                [
                    ("file", "labels", "", "utterances.csv", 720, 1440, 2160),
                    ("file", "turn pairs", "", "transitions.csv", 540, 1080, 1620),
                ],
                [
                    ("view", "5 conditions"),
                    ("file", "shifts", "", "conversations.csv", 180, 360, 540),
                    ("view", "4 ads"),
                    ("file", "ad genre", "", "advertisements.csv", 72, 144, 216),
                ],
                [
                    ("empty", "none", ""),
                ],
            ],
        ),
        (
            "eeg",
            [
                [
                    ("empty", "none", ""),
                ],
                [
                    ("view", "5 conditions"),
                    ("file", "Dataset A", "", "k37/condition_features.csv", 90, None, 90),
                    ("file", "Dataset A window", "", "gold/condition_features.csv", 108, None, 108),
                    ("view", "4 ads"),
                    ("file", "Dataset B", "", "ad_response_features.csv", 108, None, 108),
                ],
                [
                    ("file", "contrasts", "", "eeg_condition_contrast_scores.csv", 18, None, 18),
                    ("file", "write − read", "", "task_state_person_features.csv", 18, None, 18),
                ],
            ],
        ),
        (
            "join",
            [
                [
                    ("empty", "none", ""),
                ],
                [
                    ("view", "5 conditions"),
                    ("join", "joined chat", "ratings + shifts + Dataset A", "combo_threeway.csv", 90, 180, 270),
                    ("join", "joined chat, lab", "lab only, Dataset A filled", "combo_threeway_lab.csv", 90, None, 90),
                ],
                [
                    ("view", "contrasts"),
                    ("join", "joined contrasts", "the three contrast tables", "combo_threeway_D.csv", 18, 36, 54),
                    ("join", "joined contrasts, lab", "lab only, Dataset A filled", "combo_threeway_lab_D.csv", 18, None, 18),
                ],
            ],
        ),
    ]

    row_h = 6.35
    view_h = 2.45
    pad = 1.25
    y = hy - 1.45

    for key, cols in grid:
        accent, stub, stub_sub = STREAM[key]
        heights = []
        for items in cols:
            h = 0.0
            for kind, *_ in items:
                h += view_h if kind == "view" else row_h
            heights.append(max(h, row_h))
        height = pad * 2 + max(heights)
        y -= height + (2.6 if key == "join" else 1.25)
        if key == "join":
            ax.plot([3.4, 184.4], [y + height + 1.25, y + height + 1.25], color=RULE, lw=0.85, zorder=2)

        ax.add_patch(Rectangle((3.4, y), 0.95, height, facecolor=accent, edgecolor=accent, zorder=3, linewidth=0))
        rounded(ax, 4.35, y, stub_w - 0.9, height, face="#FBFBFC", edge=HAIR, lw=0.8, r=0.45)
        n_sub = stub_sub.count("\n")
        txt(ax, 5.7, y + height / 2 + (1.55 if n_sub else 1.15), stub, size=FS_STREAM, weight="bold")
        txt(ax, 5.7, y + height / 2 - (0.85 if n_sub else 1.25), stub_sub, size=FS_SMALL, color=MUTED)

        for x, items in zip(xs, cols):
            rounded(ax, x, y, col_w, height, face=CELL, edge=HAIR, lw=0.8, r=0.45)
            if items[0][0] == "empty":
                empty_cell(ax, x, y, col_w, height, items[0][1], items[0][2])
                continue
            stack = sum(view_h if k == "view" else row_h for k, *_ in items)
            cy = y + (height - stack) / 2 + stack
            for item in items:
                kind = item[0]
                if kind == "view":
                    cy -= view_h
                    view_label(ax, x, cy + view_h / 2, item[1])
                else:
                    cy -= row_h
                    _, name, role, source, lab, crowd, total = item
                    file_row(
                        ax,
                        x,
                        cy,
                        col_w,
                        row_h - 0.35,
                        name,
                        role,
                        source,
                        lab,
                        crowd,
                        total,
                        joined=kind == "join",
                    )

    txt(
        ax,
        4.8,
        3.4,
        "Keys: turn  ·  condition  ·  id.    Grey = file.",
        size=FS_SMALL,
        color=MUTED,
    )
    return fig


def main() -> None:
    figure = build()
    for name in ("behavioural_grains", "behavioural_lineage"):
        for ext in ("png", "pdf"):
            figure.savefig(
                HERE / f"{name}.{ext}",
                dpi=220 if ext == "png" else None,
                bbox_inches="tight",
                facecolor="white",
                pad_inches=0.12,
            )
    plt.close(figure)


if __name__ == "__main__":
    main()
