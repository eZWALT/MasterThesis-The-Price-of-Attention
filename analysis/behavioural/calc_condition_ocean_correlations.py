"""
Condition-specific correlations between survey scores and OCEAN (BFI-10).

Joins:
  - participant_condition_scores.csv  (outcome scores per participant x condition)
  - Experiment/**/*_export.jsonl      (ocean_submitted / session_complete scores)

For each condition, correlates each outcome score with each OCEAN trait
(E, A, C, N, O) using:
  - Spearman rho (primary)
  - Pearson r (secondary)

Outcomes:
  credibility, helpfulness, convincingness, relevance, neutrality,
  behaviour_pushing, behaviour_manipulate

Outputs:
  - participant_ocean_scores.csv
  - participant_condition_scores_with_ocean.csv
  - condition_ocean_correlations.csv
  - condition_ocean_significant_spearman.csv
  - ocean_corr_outputs/analysis_diagram.png
  - ocean_corr_outputs/spearman_heatmap_by_condition.png
  - ocean_corr_outputs/spearman_heatmap_<condition>.png

Code by Katerina, 2026-08-06  
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd
import scipy.stats as stats


ROOT = Path(__file__).resolve().parent
EXPERIMENT_DIR = ROOT / "Experiment"
SCORES_CSV = ROOT / "participant_condition_scores.csv"
OUT_DIR = ROOT / "ocean_corr_outputs"

OUTCOME_COLS = [
    "credibility",
    "helpfulness",
    "convincingness",
    "relevance",
    "neutrality",
    "behaviour_pushing",
    "behaviour_manipulate",
]

OCEAN_COLS = ["E", "A", "C", "N", "O"]
OCEAN_LABELS = {
    "E": "Extraversion",
    "A": "Agreeableness",
    "C": "Conscientiousness",
    "N": "Neuroticism",
    "O": "Openness",
}


def collect_ocean_scores(experiment_dir: Path) -> pd.DataFrame:
    """One row per participant from ocean_submitted (fallback: session_complete)."""
    by_pid: dict[str, dict] = {}

    for path in sorted(experiment_dir.rglob("*_export.jsonl")):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                event = rec.get("event")
                data = rec.get("data") or {}
                pid = rec.get("participant_id") or data.get("participant_id")
                if not pid:
                    continue

                scores = None
                raw = None
                bfi_version = None
                source_event = None

                if event == "ocean_submitted":
                    scores = data.get("scores") or data.get("ocean_scores")
                    raw = data.get("raw") or data.get("ocean_raw")
                    bfi_version = data.get("bfi_version")
                    source_event = "ocean_submitted"
                elif event == "session_complete" and pid not in by_pid:
                    scores = data.get("ocean_scores") or data.get("scores")
                    raw = data.get("ocean_raw") or data.get("raw")
                    source_event = "session_complete"

                if not scores:
                    continue

                # Prefer ocean_submitted over an earlier session_complete stub.
                if pid in by_pid and by_pid[pid]["source_event"] == "ocean_submitted":
                    if source_event != "ocean_submitted":
                        continue

                row = {
                    "participant_id": pid,
                    "bfi_version": bfi_version,
                    "source_event": source_event,
                    "source_file": str(path.relative_to(ROOT)),
                }
                for trait in OCEAN_COLS:
                    row[trait] = scores.get(trait)
                row["ocean_raw"] = json.dumps(raw) if raw is not None else ""
                by_pid[pid] = row

    if not by_pid:
        raise SystemExit("No OCEAN scores found in Experiment export files.")

    return pd.DataFrame(by_pid.values()).sort_values("participant_id").reset_index(drop=True)


def correlate_by_condition(joined: pd.DataFrame) -> pd.DataFrame:
    """Spearman + Pearson for each condition x outcome x OCEAN trait."""
    rows: list[dict] = []

    for condition, g in joined.groupby("condition", sort=True):
        for outcome in OUTCOME_COLS:
            for trait in OCEAN_COLS:
                pair = g[[outcome, trait]].dropna()
                n = len(pair)
                if n < 3:
                    spearman_r = spearman_p = pearson_r = pearson_p = None
                else:
                    spearman_r, spearman_p = stats.spearmanr(pair[outcome], pair[trait])
                    pearson_r, pearson_p = stats.pearsonr(pair[outcome], pair[trait])

                rows.append(
                    {
                        "condition": condition,
                        "outcome": outcome,
                        "ocean_trait": trait,
                        "ocean_label": OCEAN_LABELS[trait],
                        "n": n,
                        "spearman_rho": None if spearman_r is None else round(float(spearman_r), 4),
                        "spearman_p": None if spearman_p is None else round(float(spearman_p), 4),
                        "pearson_r": None if pearson_r is None else round(float(pearson_r), 4),
                        "pearson_p": None if pearson_p is None else round(float(pearson_p), 4),
                    }
                )

    return pd.DataFrame(rows)


def write_csv(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, index=False, encoding="utf-8")


def draw_analysis_diagram(out_path: Path, n_participants: int, n_conditions: int) -> None:
    """Flow diagram explaining the condition-specific OCEAN correlation analysis."""
    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis("off")
    ax.set_title(
        "Condition-specific survey score × OCEAN correlation",
        fontsize=14,
        pad=12,
        fontweight="bold",
    )

    def box(x, y, w, h, text, facecolor="#F2F2F2"):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.2,
            edgecolor="#333333",
            facecolor=facecolor,
        )
        ax.add_patch(patch)
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=9,
            wrap=True,
        )

    def arrow(x1, y1, x2, y2):
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="-|>",
                mutation_scale=12,
                linewidth=1.2,
                color="#444444",
            )
        )

    box(0.3, 4.6, 3.2, 1.3, "Post-condition survey\n7 outcome scores\n(per participant × condition)")
    box(4.4, 4.6, 3.2, 1.3, "OCEAN / BFI-10\nE A C N O\n(one score set per participant)")
    box(8.5, 4.6, 3.2, 1.3, f"Join on participant_id\nn = {n_participants} participants\n{n_conditions} conditions")

    arrow(3.5, 5.25, 4.4, 5.25)
    arrow(7.6, 5.25, 8.5, 5.25)

    box(
        2.5,
        2.5,
        7.0,
        1.4,
        "Within each condition separately\n"
        "correlate each outcome with each OCEAN trait\n"
        "Spearman ρ (primary)  ·  Pearson r (secondary)",
        facecolor="#E8EEF5",
    )
    arrow(10.1, 4.6, 6.0, 3.9)

    box(0.4, 0.4, 3.4, 1.4, "CSV tables\nfull + significant Spearman")
    box(4.3, 0.4, 3.4, 1.4, "Heatmaps\noutcome × OCEAN\n(one panel per condition)")
    box(8.2, 0.4, 3.4, 1.4, "This diagram\nanalysis overview")

    arrow(4.5, 2.5, 2.1, 1.8)
    arrow(6.0, 2.5, 6.0, 1.8)
    arrow(7.5, 2.5, 9.9, 1.8)

    ax.text(
        6.0,
        6.25,
        "Unit of analysis: participant within a single ad condition (not pooled across conditions)",
        ha="center",
        va="center",
        fontsize=8,
        color="#555555",
    )

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _pivot_spearman(corr: pd.DataFrame, condition: str) -> pd.DataFrame:
    sub = corr[corr["condition"] == condition]
    mat = sub.pivot(index="outcome", columns="ocean_trait", values="spearman_rho")
    return mat.reindex(index=OUTCOME_COLS, columns=OCEAN_COLS)


def _pivot_spearman_p(corr: pd.DataFrame, condition: str) -> pd.DataFrame:
    sub = corr[corr["condition"] == condition]
    mat = sub.pivot(index="outcome", columns="ocean_trait", values="spearman_p")
    return mat.reindex(index=OUTCOME_COLS, columns=OCEAN_COLS)


def draw_heatmap(
    ax,
    rho: pd.DataFrame,
    pvals: pd.DataFrame,
    title: str,
) -> None:
    values = rho.to_numpy(dtype=float)
    im = ax.imshow(values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")

    ax.set_xticks(range(len(OCEAN_COLS)))
    ax.set_xticklabels([f"{t}\n{OCEAN_LABELS[t][:4]}." for t in OCEAN_COLS], fontsize=8)
    ax.set_yticks(range(len(OUTCOME_COLS)))
    ax.set_yticklabels(OUTCOME_COLS, fontsize=8)
    ax.set_title(title, fontsize=11)

    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            r = values[i, j]
            p = pvals.iloc[i, j]
            if np.isnan(r):
                label = ""
            else:
                star = "*" if pd.notna(p) and p < 0.05 else ""
                label = f"{r:.2f}{star}"
            ax.text(j, i, label, ha="center", va="center", fontsize=7, color="black")

    return im


def plot_heatmaps(corr: pd.DataFrame, out_dir: Path) -> list[Path]:
    """Write combined and per-condition Spearman heatmaps (* = p < 0.05)."""
    written: list[Path] = []
    conditions = sorted(corr["condition"].dropna().unique())

    # Combined multi-panel figure
    n = len(conditions)
    ncols = 3
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(4.2 * ncols, 3.8 * nrows),
        constrained_layout=True,
    )
    axes = np.atleast_1d(axes).ravel()

    last_im = None
    for idx, condition in enumerate(conditions):
        ax = axes[idx]
        rho = _pivot_spearman(corr, condition)
        pvals = _pivot_spearman_p(corr, condition)
        last_im = draw_heatmap(ax, rho, pvals, condition)

        # Also save a single-condition figure
        fig_one, ax_one = plt.subplots(figsize=(7, 5), constrained_layout=True)
        im_one = draw_heatmap(ax_one, rho, pvals, f"Spearman ρ — {condition}")
        cbar_one = fig_one.colorbar(im_one, ax=ax_one, fraction=0.046, pad=0.04)
        cbar_one.set_label("Spearman ρ")
        fig_one.suptitle("* = uncorrected p < 0.05", fontsize=9)
        one_path = out_dir / f"spearman_heatmap_{condition}.png"
        fig_one.savefig(one_path, dpi=150, bbox_inches="tight")
        plt.close(fig_one)
        written.append(one_path)

    for ax in axes[n:]:
        ax.axis("off")

    if last_im is not None:
        cbar = fig.colorbar(last_im, ax=axes[:n].tolist(), fraction=0.03, pad=0.02)
        cbar.set_label("Spearman ρ")

    fig.suptitle(
        "Condition-specific Spearman correlations (outcome × OCEAN)  ·  * = uncorrected p < 0.05",
        fontsize=12,
    )
    combo_path = out_dir / "spearman_heatmap_by_condition.png"
    fig.savefig(combo_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    written.insert(0, combo_path)
    return written


def main() -> None:
    if not EXPERIMENT_DIR.exists():
        raise SystemExit(f"Experiment folder not found: {EXPERIMENT_DIR}")
    if not SCORES_CSV.exists():
        raise SystemExit(
            f"Missing {SCORES_CSV.name}. Run Analysis_AdsTalkBack.ipynb first."
        )

    OUT_DIR.mkdir(exist_ok=True)

    ocean = collect_ocean_scores(EXPERIMENT_DIR)
    scores = pd.read_csv(SCORES_CSV)

    missing_outcomes = [c for c in OUTCOME_COLS if c not in scores.columns]
    if missing_outcomes:
        raise SystemExit(f"Scores CSV missing columns: {missing_outcomes}")

    joined = scores.merge(ocean[["participant_id", *OCEAN_COLS]], on="participant_id", how="inner")
    if joined.empty:
        raise SystemExit("No overlapping participant_ids between scores CSV and OCEAN data.")

    corr = correlate_by_condition(joined)
    sig = corr.dropna(subset=["spearman_p"])
    sig = sig[sig["spearman_p"] < 0.05].sort_values(["condition", "spearman_p"]).reset_index(drop=True)

    ocean_path = ROOT / "participant_ocean_scores.csv"
    joined_path = ROOT / "participant_condition_scores_with_ocean.csv"
    corr_path = ROOT / "condition_ocean_correlations.csv"
    sig_path = ROOT / "condition_ocean_significant_spearman.csv"
    diagram_path = OUT_DIR / "analysis_diagram.png"

    write_csv(ocean_path, ocean)
    write_csv(
        joined_path,
        joined[
            ["participant_id", "condition", *OUTCOME_COLS, *OCEAN_COLS]
        ].sort_values(["participant_id", "condition"]),
    )
    write_csv(corr_path, corr)
    write_csv(sig_path, sig)

    n_part = int(joined["participant_id"].nunique())
    n_cond = int(joined["condition"].nunique())

    draw_analysis_diagram(diagram_path, n_part, n_cond)
    heatmap_paths = plot_heatmaps(corr, OUT_DIR)

    print(f"Participants with scores + OCEAN: {n_part}")
    print(f"Conditions: {n_cond}")
    print(f"Wrote {ocean_path.name} ({len(ocean)} rows)")
    print(f"Wrote {joined_path.name} ({len(joined)} rows)")
    print(f"Wrote {corr_path.name} ({len(corr)} rows)")
    print(f"Wrote {sig_path.name} ({len(sig)} rows)")
    print(f"Wrote {diagram_path.relative_to(ROOT)}")
    for path in heatmap_paths:
        print(f"Wrote {path.relative_to(ROOT)}")
    print()

    print("Significant Spearman correlations (uncorrected p < 0.05):")
    if sig.empty:
        print("  (none)")
    else:
        print(
            f"{'condition':<14} {'outcome':<22} {'trait':<4} "
            f"{'rho':>7} {'p':>8} {'n':>3}"
        )
        for _, row in sig.iterrows():
            print(
                f"{row['condition']:<14} {row['outcome']:<22} {row['ocean_trait']:<4} "
                f"{row['spearman_rho']:>7.4f} {row['spearman_p']:>8.4f} {int(row['n']):>3}"
            )


if __name__ == "__main__":
    main()
