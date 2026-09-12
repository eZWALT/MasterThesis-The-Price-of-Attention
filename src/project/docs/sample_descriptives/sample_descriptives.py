"""Paper figures for Results sample descriptives.

Finished roster only: lab n=18 (Subjects 1-3, 5-19), crowd n=36.
Demographics from demographics_post_submitted. BFI-10 from ocean_submitted.
Age is not plotted: the post-experiment item was blank for all 54.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path("/home/wtroi/MasterThesis-RAG-RecSys")
LOGS = ROOT / "src/project/logs/tracked"
HERE = Path(__file__).resolve().parent
PAPER_FIG = ROOT / "docs/overleaf/publication/Figures"
PREVIEW = ROOT / "analysis/behavioural/ocean_corr_outputs"

LAB_IDS = [f"lab_subject_{i}" for i in list(range(1, 4)) + list(range(5, 20))]
CROWD_IDS = (
    [f"crowd_subject_{i}" for i in range(1, 5)]
    + ["crowd_subject_5_unfocused"]
    + [f"crowd_subject_{i}" for i in range(6, 12)]
    + [f"crowd_subject_{i}" for i in range(13, 17)]
    + ["crowd_subject_18_unfocused"]
    + [f"crowd_subject_{i}" for i in range(19, 27)]
    + [f"crowd_subject_{i}" for i in range(28, 31)]
    + [
        "crowd_subject_32",
        "crowd_subject_33",
        "crowd_subject_35",
        "crowd_subject_36",
        "crowd_subject_38",
        "crowd_subject_40",
        "crowd_subject_42",
        "crowd_subject_43",
        "crowd_subject_44",
    ]
)

LAB_C = "#D32F2F"
CR_C = "#1565C0"
INK = "#243240"
MUTED = "#5C6770"
GRID = "#D5DBE0"

SEX_LEVELS = ["Female", "Male", "Not stated"]
EDU_LEVELS = [
    "High\nschool",
    "Bachelor",
    "Master",
    "PhD",
    "Other",
    "Not\nstated",
]
FAM_LEVELS = [
    "Unfamiliar",
    "Somewhat\nunfamiliar",
    "Somewhat\nfamiliar",
    "Familiar",
]
FREQ_LEVELS = [
    "<5\never",
    "1–5 /\nmonth",
    "1–5 /\nweek",
    "1–5 /\nday",
    ">5 /\nday",
]
TRAITS = ["E", "A", "C", "N", "O"]
TRAIT_NAMES = {
    "E": "Extraversion",
    "A": "Agreeableness",
    "C": "Conscientiousness",
    "N": "Neuroticism",
    "O": "Openness",
}


def find_export(folder: Path) -> list[Path]:
    cands = (
        sorted(folder.glob("*export*.jsonl"))
        + sorted(folder.glob("export.jsonl"))
        + sorted(folder.glob("export_*.jsonl"))
    )
    seen, out = set(), []
    for c in cands:
        r = c.resolve()
        if r not in seen:
            seen.add(r)
            out.append(c)
    return out


def load_event(name: str, arm: str, event: str) -> dict | None:
    folder = LOGS / arm / name
    for path in find_export(folder):
        for line in path.open():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("event") == event:
                return rec.get("data") or {}
    return None


def norm_sex(v) -> str:
    if v in (None, "", "None"):
        return "Not stated"
    return str(v)


def norm_edu(v) -> str:
    if v in (None, "", "None"):
        return "Not\nstated"
    s = str(v)
    return {
        "High School": "High\nschool",
        "Bachelor's Degree": "Bachelor",
        "Master's Degree": "Master",
        "PhD": "PhD",
        "Other": "Other",
        "Not stated": "Not\nstated",
    }.get(s, s)


def norm_fam(v) -> str:
    return {
        "Unfamiliar": "Unfamiliar",
        "Somewhat Unfamiliar": "Somewhat\nunfamiliar",
        "Somewhat Familiar": "Somewhat\nfamiliar",
        "Familiar": "Familiar",
    }.get(str(v), str(v))


def norm_freq(v) -> str:
    return {
        "Fewer than 5 times ever": "<5\never",
        "1–5 times per month": "1–5 /\nmonth",
        "1-5 times per month": "1–5 /\nmonth",
        "1–5 times per week": "1–5 /\nweek",
        "1-5 times per week": "1–5 /\nweek",
        "1–5 times per day": "1–5 /\nday",
        "1-5 times per day": "1–5 /\nday",
        "Greater than 5 times per day": ">5 /\nday",
    }.get(str(v), str(v))


def load_people() -> list[dict]:
    people = []
    for name in LAB_IDS + CROWD_IDS:
        arm = "lab" if name.startswith("lab") else "crowd"
        demo = load_event(name, arm, "demographics_post_submitted") or {}
        ocean = load_event(name, arm, "ocean_submitted") or {}
        scores = ocean.get("scores") or ocean.get("ocean_scores") or {}
        people.append(
            {
                "arm": arm,
                "sex": norm_sex(demo.get("demo_sex")),
                "edu": norm_edu(demo.get("demo_education")),
                "fam": norm_fam(demo.get("demo_familiarity")),
                "freq": norm_freq(demo.get("demo_frequency")),
                **{t: float(scores[t]) for t in TRAITS},
            }
        )
    return people


def pct(people: list[dict], arm: str, key: str, levels: list[str]) -> list[float]:
    sub = [p for p in people if p["arm"] == arm]
    n = len(sub)
    return [100.0 * sum(1 for p in sub if p[key] == lev) / n for lev in levels]


def grouped_bars(ax, levels, lab, crowd, ylabel="Percent of arm"):
    x = np.arange(len(levels))
    w = 0.38
    ax.bar(x - w / 2, lab, w, color=LAB_C, label="Lab  $n=18$", zorder=3)
    ax.bar(x + w / 2, crowd, w, color=CR_C, label="Crowd  $n=36$", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(levels, fontsize=7)
    ax.set_ylabel(ylabel, fontsize=8.5, color=INK)
    ax.set_ylim(0, 108)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(MUTED)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=8)
    for i, (a, b) in enumerate(zip(lab, crowd)):
        if a > 0:
            ax.text(x[i] - w / 2, a + 1.8, f"{a:.0f}", ha="center", va="bottom", fontsize=6.5, color=INK)
        if b > 0:
            ax.text(x[i] + w / 2, b + 1.8, f"{b:.0f}", ha="center", va="bottom", fontsize=6.5, color=INK)


def style_axes():
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Nimbus Sans", "DejaVu Sans"],
            "axes.linewidth": 0.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def draw_demographics(people: list[dict], out_stem: Path) -> None:
    # Wide enough that six single-line education labels do not collide.
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.6))
    panels = [
        (axes[0, 0], "Sex", "sex", SEX_LEVELS),
        (axes[0, 1], "Highest education", "edu", EDU_LEVELS),
        (axes[1, 0], "Chatbot familiarity", "fam", FAM_LEVELS),
        (axes[1, 1], "Chatbot use frequency", "freq", FREQ_LEVELS),
    ]
    letters = "abcd"
    for letter, (ax, title, key, levels) in zip(letters, panels):
        grouped_bars(ax, levels, pct(people, "lab", key, levels), pct(people, "crowd", key, levels))
        ax.set_title(f"({letter})  {title}", fontsize=10, color=INK, pad=6, loc="left")
    fig.tight_layout()
    fig.savefig(out_stem.with_suffix(".pdf"), format="pdf", bbox_inches="tight")
    fig.savefig(out_stem.with_suffix(".png"), format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def draw_bfi(people: list[dict], out_stem: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.0, 3.35))
    lab = [p for p in people if p["arm"] == "lab"]
    crowd = [p for p in people if p["arm"] == "crowd"]
    rng = np.random.default_rng(0)
    positions_lab = np.arange(5) * 2.0
    positions_cr = positions_lab + 0.7
    lab_data = [[p[t] for p in lab] for t in TRAITS]
    cr_data = [[p[t] for p in crowd] for t in TRAITS]
    box_kw = dict(
        widths=0.55,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": INK, "linewidth": 1.2},
        whiskerprops={"color": MUTED, "linewidth": 0.9},
        capprops={"color": MUTED, "linewidth": 0.9},
        boxprops={"linewidth": 0.8},
    )
    b1 = ax.boxplot(lab_data, positions=positions_lab, **box_kw)
    b2 = ax.boxplot(cr_data, positions=positions_cr, **box_kw)
    for patch in b1["boxes"]:
        patch.set_facecolor(LAB_C)
        patch.set_alpha(0.85)
        patch.set_edgecolor(INK)
    for patch in b2["boxes"]:
        patch.set_facecolor(CR_C)
        patch.set_alpha(0.85)
        patch.set_edgecolor(INK)
    for i, t in enumerate(TRAITS):
        y = np.asarray(lab_data[i], float) + rng.uniform(-0.04, 0.04, len(lab_data[i]))
        x = np.full(len(y), positions_lab[i]) + rng.uniform(-0.12, 0.12, len(y))
        ax.scatter(x, y, s=14, c=LAB_C, edgecolors="white", linewidths=0.35, zorder=4, alpha=0.95)
        y = np.asarray(cr_data[i], float) + rng.uniform(-0.04, 0.04, len(cr_data[i]))
        x = np.full(len(y), positions_cr[i]) + rng.uniform(-0.12, 0.12, len(y))
        ax.scatter(x, y, s=11, c=CR_C, edgecolors="white", linewidths=0.3, zorder=4, alpha=0.9)
    ax.axhline(3.0, color="#C45C5C", ls="--", lw=0.9, zorder=1)
    ax.set_ylim(0.7, 5.3)
    ax.set_xlim(positions_lab[0] - 0.55, positions_cr[-1] + 0.55)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_ylabel("BFI-10 trait score (1–5)", fontsize=9, color=INK)
    ax.set_xticks(positions_lab + 0.35)
    ax.set_xticklabels([TRAIT_NAMES[t] for t in TRAITS], fontsize=8)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(MUTED)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=8)
    ax.legend(
        [b1["boxes"][0], b2["boxes"][0]],
        ["Lab  $n=18$", "Crowd  $n=36$"],
        frameon=False,
        loc="lower right",
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(out_stem.with_suffix(".pdf"), format="pdf", bbox_inches="tight")
    fig.savefig(out_stem.with_suffix(".png"), format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    style_axes()
    people = load_people()
    assert len(people) == 54
    for key, levels in (
        ("sex", SEX_LEVELS),
        ("edu", EDU_LEVELS),
        ("fam", FAM_LEVELS),
        ("freq", FREQ_LEVELS),
    ):
        for arm, n in (("lab", 18), ("crowd", 36)):
            got = sum(1 for p in people if p["arm"] == arm and p[key] in levels)
            if got != n:
                raise SystemExit(f"{arm} {key} mapped {got}/{n}")
    PREVIEW.mkdir(parents=True, exist_ok=True)
    PAPER_FIG.mkdir(parents=True, exist_ok=True)
    HERE.mkdir(parents=True, exist_ok=True)
    demo = HERE / "sample_demographics"
    bfi = HERE / "bfi10_boxplots"
    draw_demographics(people, demo)
    draw_bfi(people, bfi)
    for src in (demo, bfi):
        for ext in (".pdf", ".png"):
            target = PAPER_FIG / (src.name + ext)
            target.write_bytes(src.with_suffix(ext).read_bytes())
            (PREVIEW / target.name).write_bytes(src.with_suffix(ext).read_bytes())
    print("wrote", demo.with_suffix(".png"), bfi.with_suffix(".png"))
    print("paper", PAPER_FIG / "sample_demographics.pdf", PAPER_FIG / "bfi10_boxplots.pdf")


if __name__ == "__main__":
    main()
