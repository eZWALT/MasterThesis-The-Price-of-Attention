"""
Condition-specific correlations between survey scores and OCEAN (BFI-10).

Joins:
  - participant_condition_scores.csv  (outcome scores per participant x condition)
  - src/project/logs/tracked/crowd/**/*_export.jsonl
    (ocean_submitted / session_complete scores)

For each condition, correlates each outcome score with each OCEAN trait
(E, A, C, N, O) using:
  - Spearman rho (primary)
  - Pearson r (secondary)

Outcomes:
  credibility, helpfulness, convincingness, relevance, neutrality,
  behaviour_pushing, behaviour_manipulate

Outputs (all under ocean_corr_outputs/):
  - participant_ocean_scores.csv
  - participant_condition_scores_with_ocean.csv
  - condition_ocean_correlations.csv
  - condition_ocean_significant_spearman.csv
  - condition_ocean_significant_holm.csv
  - condition_ocean_significant_bh_fdr.csv
  - analysis_diagram.png
  - spearman_heatmap_by_condition.png
  - spearman_heatmap_<condition>.png

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
PROJECT_ROOT = ROOT.parents[1]
EXPERIMENT_DIR = ROOT / "Experiment"
CROWD_LOG_DIR = PROJECT_ROOT / "src" / "project" / "logs" / "tracked" / "crowd"
TRACKED_LOG_DIR = CROWD_LOG_DIR
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


def holm_adjusted_pvalues(pvals: np.ndarray) -> np.ndarray:
    """Holm-Bonferroni adjusted p-values for a set of p-values."""
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    if n == 0:
        return p.copy()

    order = np.argsort(p)
    sorted_p = p[order]
    adjusted_sorted = np.empty(n, dtype=float)
    running = 0.0

    for i in range(n):
        rank = i + 1
        candidate = (n - rank + 1) * sorted_p[i]
        running = max(running, candidate)
        adjusted_sorted[i] = min(1.0, running)

    adjusted = np.empty(n, dtype=float)
    adjusted[order] = adjusted_sorted
    return adjusted


def benjamini_hochberg_qvalues(pvals: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg FDR q-values for a set of p-values."""
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    if n == 0:
        return p.copy()

    order = np.argsort(p)
    sorted_p = p[order]
    adjusted_sorted = np.empty(n, dtype=float)
    running = 1.0

    for i in range(n - 1, -1, -1):
        rank = i + 1
        candidate = sorted_p[i] * n / rank
        running = min(running, candidate)
        adjusted_sorted[i] = min(1.0, running)

    adjusted = np.empty(n, dtype=float)
    adjusted[order] = adjusted_sorted
    return adjusted


def collect_ocean_scores(search_roots: Path | list[Path] | tuple[Path, ...]) -> pd.DataFrame:
    """One row per participant from ocean_submitted (fallback: session_complete)."""
    if isinstance(search_roots, Path):
        roots = [search_roots]
    else:
        roots = list(search_roots)

    by_pid: dict[str, dict] = {}

    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*_export.jsonl")):
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
                        "source_file": str(path.relative_to(PROJECT_ROOT)) if path.is_relative_to(PROJECT_ROOT) else str(path),
                    }
                    for trait in OCEAN_COLS:
                        row[trait] = scores.get(trait)
                    row["ocean_raw"] = json.dumps(raw) if raw is not None else ""
                    by_pid[pid] = row

    if not by_pid:
        raise SystemExit(
            "No OCEAN scores found in Experiment export files or src/project/logs/tracked/**/*_export.jsonl."
        )

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


def resolve_scores_csv() -> Path:
    candidates = [
        ROOT / "participant_condition_scores.csv",
        ROOT / "outputs" / "ad_scores" / "participant_condition_scores.csv",
        PROJECT_ROOT / "analysis" / "behavioural" / "participant_condition_scores.csv",
        PROJECT_ROOT / "analysis" / "behavioural" / "outputs" / "ad_scores" / "participant_condition_scores.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise SystemExit(
        f"Missing participant_condition_scores.csv. Looked in: {', '.join(str(c) for c in candidates)}"
    )


def main() -> None:
    scores_path = resolve_scores_csv()
    OUT_DIR.mkdir(exist_ok=True)

    ocean = collect_ocean_scores([EXPERIMENT_DIR, CROWD_LOG_DIR, TRACKED_LOG_DIR])
    scores = pd.read_csv(scores_path)

    missing_outcomes = [c for c in OUTCOME_COLS if c not in scores.columns]
    if missing_outcomes:
        raise SystemExit(f"Scores CSV missing columns: {missing_outcomes}")

    joined = scores.merge(ocean[["participant_id", *OCEAN_COLS]], on="participant_id", how="inner")
    if joined.empty:
        raise SystemExit("No overlapping participant_ids between scores CSV and OCEAN data.")

    corr = correlate_by_condition(joined).copy()

    valid = corr["spearman_p"].notna()
    if valid.any():
        pvals = corr.loc[valid, "spearman_p"].to_numpy(dtype=float)
        corr.loc[valid, "spearman_holm_adjusted_p"] = holm_adjusted_pvalues(pvals)
        corr.loc[valid, "spearman_bh_fdr_q"] = benjamini_hochberg_qvalues(pvals)
    else:
        corr["spearman_holm_adjusted_p"] = np.nan
        corr["spearman_bh_fdr_q"] = np.nan

    raw_sig = corr.dropna(subset=["spearman_p"])
    raw_sig = raw_sig[raw_sig["spearman_p"] < 0.05].sort_values(["condition", "spearman_p"]).reset_index(drop=True)

    holm_sig = corr.dropna(subset=["spearman_holm_adjusted_p"])
    holm_sig = holm_sig[holm_sig["spearman_holm_adjusted_p"] < 0.05].sort_values(["condition", "spearman_holm_adjusted_p"]).reset_index(drop=True)

    bh_sig = corr.dropna(subset=["spearman_bh_fdr_q"])
    bh_sig = bh_sig[bh_sig["spearman_bh_fdr_q"] < 0.05].sort_values(["condition", "spearman_bh_fdr_q"]).reset_index(drop=True)

    ocean_path = OUT_DIR / "participant_ocean_scores.csv"
    joined_path = OUT_DIR / "participant_condition_scores_with_ocean.csv"
    corr_path = OUT_DIR / "condition_ocean_correlations.csv"
    raw_sig_path = OUT_DIR / "condition_ocean_significant_spearman.csv"
    holm_sig_path = OUT_DIR / "condition_ocean_significant_holm.csv"
    bh_sig_path = OUT_DIR / "condition_ocean_significant_bh_fdr.csv"
    diagram_path = OUT_DIR / "analysis_diagram.png"

    write_csv(ocean_path, ocean)
    write_csv(
        joined_path,
        joined[
            ["participant_id", "condition", *OUTCOME_COLS, *OCEAN_COLS]
        ].sort_values(["participant_id", "condition"]),
    )
    write_csv(corr_path, corr)
    write_csv(raw_sig_path, raw_sig)
    write_csv(holm_sig_path, holm_sig)
    write_csv(bh_sig_path, bh_sig)

    n_part = int(joined["participant_id"].nunique())
    n_cond = int(joined["condition"].nunique())

    draw_analysis_diagram(diagram_path, n_part, n_cond)
    heatmap_paths = plot_heatmaps(corr, OUT_DIR)

    print(f"Participants with scores + OCEAN: {n_part}")
    print(f"Conditions: {n_cond}")
    print(f"Wrote {ocean_path.name} ({len(ocean)} rows)")
    print(f"Wrote {joined_path.name} ({len(joined)} rows)")
    print(f"Wrote {corr_path.name} ({len(corr)} rows)")
    print(f"Wrote {raw_sig_path.name} ({len(raw_sig)} rows)")
    print(f"Wrote {holm_sig_path.name} ({len(holm_sig)} rows)")
    print(f"Wrote {bh_sig_path.name} ({len(bh_sig)} rows)")
    print(f"Wrote {diagram_path.relative_to(ROOT)}")
    for path in heatmap_paths:
        print(f"Wrote {path.relative_to(ROOT)}")
    print()

    def print_results(label: str, df: pd.DataFrame, p_col: str) -> None:
        print(f"Significant Spearman correlations ({label}):")
        if df.empty:
            print("  (none)")
            return
        print(
            f"{'condition':<14} {'outcome':<22} {'trait':<4} "
            f"{'rho':>7} {p_col:>10} {'n':>3}"
        )
        for _, row in df.iterrows():
            print(
                f"{row['condition']:<14} {row['outcome']:<22} {row['ocean_trait']:<4} "
                f"{row['spearman_rho']:>7.4f} {row[p_col]:>10.4f} {int(row['n']):>3}"
            )

    print_results("uncorrected p < 0.05", raw_sig, "spearman_p")
    print()
    print_results("Holm-adjusted p < 0.05", holm_sig, "spearman_holm_adjusted_p")
    print()
    print_results("BH-FDR q < 0.05", bh_sig, "spearman_bh_fdr_q")


if __name__ == "__main__":
    main()
