"""Figures for the ad-local epoch averaging sensitivity.

EXPLORATORY ONLY. Reads
``analysis/eeg/statistics/outputs/sensitivity/ad_local_epochs/``.

    python analysis/eeg/analysis/plot_ad_local_epochs.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "analysis/eeg/statistics/outputs/sensitivity/ad_local_epochs"
OUT = Path(__file__).resolve().parent / "outputs" / "figures" / "ad_local_epochs"

INK = "#12202A"
SLATE = "#5C6B73"
CLAY = "#C45C26"
NAVY = "#1B3A4B"
HOLM_CMAP = LinearSegmentedColormap.from_list(
    "holm",
    ["#C45C26", "#F0D5B8", "#F4F6F7", "#9BB0BC"],
)
FEATURE_LABELS = {
    "fz_theta_power_db_uv2": "Fz theta *",
    "posterior_alpha_power_db_uv2": "Posterior alpha *",
    "theta_power_db_uv2": "Global theta",
    "alpha_power_db_uv2": "Global alpha",
    "beta_power_db_uv2": "Global beta",
    "delta_power_db_uv2": "Global delta",
    "gamma_power_db_uv2": "Global gamma",
    "faa_log_f4_minus_f3": "Frontal alpha asym.",
    "delta_relative_power": "Rel. delta",
    "theta_relative_power": "Rel. theta",
    "alpha_relative_power": "Rel. alpha",
    "beta_relative_power": "Rel. beta",
    "gamma_relative_power": "Rel. gamma",
    "engagement_beta_over_alpha_theta": "Pope engagement",
    "engagement_pope_frontocentral_beta_over_alpha_theta": "Pope frontocentral",
    "engagement_kislov_central_beta16_24_over_alpha8_12": "Kislov ratio",
}
FEATURE_ORDER = tuple(FEATURE_LABELS)
K_ORDER = ("1", "3", "5", "10", "20")
DATASET_A_SHORT = {
    "any_ad_vs_no_ads": "Any ad",
    "inline_vs_block": "Format",
    "early_vs_late": "Timing",
}
DATASET_B_SHORT = {
    "inline_early_vs_no_ad_early": "Imp early",
    "block_early_vs_no_ad_early": "Exp early",
    "inline_late_vs_no_ad_late": "Imp late",
    "block_late_vs_no_ad_late": "Exp late",
}
DATASET_A_PRIMARY = (
    "any_ad_vs_no_ads",
    "inline_vs_block",
    "early_vs_late",
)
DATASET_B_PRIMARY = (
    "inline_early_vs_no_ad_early",
    "block_early_vs_no_ad_early",
    "inline_late_vs_no_ad_late",
    "block_late_vs_no_ad_late",
)
FOCUS_FEATURES = (
    "fz_theta_power_db_uv2",
    "posterior_alpha_power_db_uv2",
    "delta_power_db_uv2",
    "theta_power_db_uv2",
    "alpha_power_db_uv2",
    "gamma_power_db_uv2",
)


def style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 300,
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 11,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "figure.max_open_warning": 0,
        }
    )


def save(figure: plt.Figure, stem: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{stem}.png"
    figure.savefig(path, bbox_inches="tight", facecolor="white")
    figure.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    return path


def holm_matrix(
    frame: pd.DataFrame,
    *,
    selection: str,
    contrasts: tuple[str, ...],
) -> np.ndarray:
    values = np.full((len(FEATURE_ORDER), len(K_ORDER) * len(contrasts)), np.nan)
    slice_ = frame[
        (frame["selection"] == selection) & (frame["k_label"].isin(K_ORDER))
    ]
    for i, feature in enumerate(FEATURE_ORDER):
        col = 0
        for contrast in contrasts:
            for k_label in K_ORDER:
                hit = slice_[
                    (slice_["feature"] == feature)
                    & (slice_["contrast_id"] == contrast)
                    & (slice_["k_label"] == k_label)
                ]
                if not hit.empty:
                    values[i, col] = float(hit.iloc[0]["p_t_holm"])
                col += 1
    return values


def draw_board(
    axis: plt.Axes,
    values: np.ndarray,
    contrasts: tuple[str, ...],
    labels: dict[str, str],
    *,
    title: str,
    ylabels: bool,
) -> None:
    axis.imshow(values, aspect="auto", cmap=HOLM_CMAP, vmin=0, vmax=1)
    xticks = []
    xlabels = []
    col = 0
    for contrast in contrasts:
        short = labels[contrast]
        for k_label in K_ORDER:
            xticks.append(col)
            xlabels.append(f"{short}\nk={k_label}")
            col += 1
    axis.set_xticks(xticks, xlabels, fontsize=7.5, color=INK)
    if ylabels:
        axis.set_yticks(
            range(len(FEATURE_ORDER)),
            [FEATURE_LABELS[name].replace(" *", "") for name in FEATURE_ORDER],
            fontsize=8,
            color=INK,
        )
    else:
        axis.set_yticks([])
    axis.set_title(title, color=INK, loc="left")
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            value = values[i, j]
            if np.isnan(value):
                continue
            if value < 0.05:
                axis.text(
                    j,
                    i,
                    f"{value:.3f}",
                    ha="center",
                    va="center",
                    fontsize=5.5,
                    color="white",
                    fontweight="bold",
                )
            elif value < 0.10:
                axis.text(
                    j,
                    i,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=5,
                    color=INK,
                )
    for boundary in range(len(contrasts) - 1):
        axis.axvline(len(K_ORDER) * (boundary + 1) - 0.5, color="white", lw=2)


def dataset_a_board(frame: pd.DataFrame) -> plt.Figure:
    figure, axes = plt.subplots(3, 1, figsize=(16, 18), constrained_layout=True)
    titles = {
        "pre": "Dataset A · tiles before the onset",
        "around": "Dataset A · tiles nearest the onset",
        "post": "Dataset A · tiles after the onset",
    }
    for axis, selection in zip(axes, ("pre", "around", "post")):
        values = holm_matrix(
            frame[frame["dataset"] == "A"],
            selection=selection,
            contrasts=DATASET_A_PRIMARY,
        )
        draw_board(
            axis,
            values,
            DATASET_A_PRIMARY,
            DATASET_A_SHORT,
            title=titles[selection],
            ylabels=True,
        )
    figure.suptitle(
        "Holm p by how many 4 s tiles are kept around each ad",
        color=INK,
        fontsize=14,
        x=0.01,
        ha="left",
    )
    return figure


def dataset_b_board(frame: pd.DataFrame) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(16, 8), constrained_layout=True)
    values = holm_matrix(
        frame[frame["dataset"] == "B"],
        selection="prepost",
        contrasts=DATASET_B_PRIMARY,
    )
    draw_board(
        axis,
        values,
        DATASET_B_PRIMARY,
        DATASET_B_SHORT,
        title="Dataset B · median(k post) − median(k pre)",
        ylabels=True,
    )
    figure.suptitle(
        "Holm p for ad-locked Δ as the averaged neighbourhood grows",
        color=INK,
        fontsize=14,
        x=0.01,
        ha="left",
    )
    return figure


def dz_curves(frame: pd.DataFrame) -> plt.Figure:
    figure, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
    dataset_a = frame[
        (frame["dataset"] == "A")
        & (frame["selection"].isin(("pre", "around", "post")))
        & (frame["contrast_id"] == "any_ad_vs_no_ads")
        & (frame["k_label"].isin(K_ORDER))
    ]
    bottom_contrasts = (
        "block_early_vs_no_ad_early",
        "inline_early_vs_no_ad_early",
        "block_late_vs_no_ad_late",
    )
    bottom_titles = (
        "Dataset B explicit early",
        "Dataset B implicit early",
        "Dataset B explicit late",
    )
    k_numeric = np.array([int(label) for label in K_ORDER], dtype=float)
    for axis, selection, title in (
        (axes[0, 0], "pre", "Dataset A any-ad · before onset"),
        (axes[0, 1], "around", "Dataset A any-ad · around onset"),
        (axes[0, 2], "post", "Dataset A any-ad · after onset"),
    ):
        for feature in FOCUS_FEATURES:
            slice_ = dataset_a[
                (dataset_a["selection"] == selection)
                & (dataset_a["feature"] == feature)
            ]
            slice_ = slice_.set_index("k_label").reindex(K_ORDER)
            axis.plot(
                k_numeric,
                slice_["cohen_dz"].astype(float).to_numpy(),
                marker="o",
                label=FEATURE_LABELS[feature].replace(" *", ""),
            )
        axis.axhline(0, color=SLATE, lw=0.8)
        axis.set_title(title, color=INK, loc="left")
        axis.set_xlabel("k tiles")
        axis.set_ylabel("Cohen dz")
        axis.set_xticks(k_numeric, K_ORDER)
    for axis, contrast, title in zip(axes[1], bottom_contrasts, bottom_titles):
        slice_b = frame[
            (frame["dataset"] == "B")
            & (frame["contrast_id"] == contrast)
            & (frame["k_label"].isin(K_ORDER))
        ]
        for feature in FOCUS_FEATURES:
            slice_ = slice_b[slice_b["feature"] == feature]
            slice_ = slice_.set_index("k_label").reindex(K_ORDER)
            axis.plot(
                k_numeric,
                slice_["cohen_dz"].astype(float).to_numpy(),
                marker="o",
                label=FEATURE_LABELS[feature].replace(" *", ""),
            )
        axis.axhline(0, color=SLATE, lw=0.8)
        axis.set_title(title, color=INK, loc="left")
        axis.set_xlabel("k tiles")
        axis.set_ylabel("Cohen dz")
        axis.set_xticks(k_numeric, K_ORDER)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="upper right", frameon=False, fontsize=8)
    figure.suptitle(
        "Effect size versus neighbourhood size (same 16 measures, n=18)",
        color=INK,
        fontsize=13,
        x=0.01,
        ha="left",
    )
    return figure


def cover_page(manifest: dict, coverage: pd.DataFrame) -> plt.Figure:
    figure = plt.figure(figsize=(11, 8.5))
    figure.text(0.08, 0.90, "Ad-local epoch averaging", fontsize=22, color=INK)
    figure.text(
        0.08,
        0.84,
        "Exploratory sensitivity. Confirmatory 4 s / median Dataset A is untouched.",
        fontsize=11,
        color=SLATE,
    )
    body = (
        "Dataset A medians every retained 4 s tile in a condition "
        f"(median {coverage['n_epochs_available'].median():.0f} tiles). "
        "This pass keeps only the k tiles nearest each visual onset, "
        "or the k tiles immediately before / after it, and re-runs the "
        "same person-level contrasts. The no-ad cell uses the matched "
        "turn-2 and turn-4 replies, so the control is local in time too.\n\n"
        f"k grid: {', '.join(K_ORDER)}. "
        f"Holm hits: {manifest['n_holm_hits']}. "
        f"BH hits: {manifest['n_bh_hits']}. "
        f"Nominal raw p < .05: {manifest['n_nominal_raw_p_lt_05']}.\n\n"
        "k=all reproduces confirmatory Dataset A "
        f"(max |Δmedian| = {manifest['verification_dataset_a_all']['max_abs_median_diff']:.1e}, "
        f"gate {'passed' if manifest['verification_dataset_a_all']['gate_passed'] else 'FAILED'}).\n"
        "Dataset B k=1 tiles are not onset-locked windows "
        f"(median r = {manifest['dataset_b_k1_vs_onset_locked']['median_pearson_r']:.2f} "
        "against confirmatory Δ)."
    )
    figure.text(0.08, 0.38, body, fontsize=11, color=INK, va="top", wrap=True)
    figure.text(
        0.08,
        0.08,
        "Source: frozen condition_epoch_features.csv · n=18 · primary Gold tiles",
        fontsize=8,
        color=SLATE,
    )
    return figure


def findings_page(hits: pd.DataFrame) -> plt.Figure:
    figure = plt.figure(figsize=(11, 8.5))
    figure.text(0.08, 0.92, "What crossed a threshold", fontsize=18, color=INK)
    holm = hits[hits["holm_significant"] == "yes"] if not hits.empty else hits
    if holm is None or holm.empty:
        figure.text(
            0.08,
            0.80,
            "Nothing is Holm-significant at any k, any selection, "
            "Dataset A or Dataset B. Shrinking the average from ~95 tiles "
            "to 5 or 10 does not create a confirmatory-style hit.",
            fontsize=12,
            color=INK,
            va="top",
            wrap=True,
        )
        bh = hits[hits["bh_significant"] == "yes"] if not hits.empty else hits
        if bh is not None and not bh.empty:
            lines = [
                f"{row.dataset}/{row.selection}/k={row.k_label}  "
                f"{row.contrast_id}  {FEATURE_LABELS.get(row.feature, row.feature)}  "
                f"dz={float(row.cohen_dz):.2f}  p={float(row.p_t_raw):.4f}"
                for row in bh.head(12).itertuples()
            ]
            figure.text(
                0.08,
                0.62,
                "BH (same within-feature families) would call:\n\n"
                + "\n".join(lines),
                fontsize=10,
                color=INK,
                va="top",
                family="DejaVu Sans Mono",
            )
        return figure
    lines = [
        f"{row.dataset}/{row.selection}/k={row.k_label}  "
        f"{row.contrast_id}  {FEATURE_LABELS.get(row.feature, row.feature)}  "
        f"dz={float(row.cohen_dz):.2f}  Holm={float(row.p_t_holm):.4f}"
        for row in holm.head(18).itertuples()
    ]
    figure.text(
        0.08,
        0.82,
        "\n".join(lines),
        fontsize=10,
        color=INK,
        va="top",
        family="DejaVu Sans Mono",
    )
    return figure


def main() -> None:
    style()
    frame = pd.read_csv(TABLES / "comparison.csv")
    coverage = pd.read_csv(TABLES / "coverage_dataset_a.csv")
    hits_path = TABLES / "hits_raw_or_corrected.csv"
    hits = pd.read_csv(hits_path) if hits_path.exists() else pd.DataFrame()
    import json

    manifest = json.loads((TABLES / "manifest.json").read_text())

    boards = [
        ("dataset_a_holm_by_k", dataset_a_board(frame)),
        ("dataset_b_holm_by_k", dataset_b_board(frame)),
        ("dz_versus_k", dz_curves(frame)),
    ]
    for stem, figure in boards:
        path = save(figure, stem)
        print(f"wrote {path}")

    pdf_path = OUT / "ad_local_epochs_report.pdf"
    with PdfPages(pdf_path) as pdf:
        cover = cover_page(manifest, coverage)
        pdf.savefig(cover, facecolor="white")
        plt.close(cover)
        findings = findings_page(hits)
        pdf.savefig(findings, facecolor="white")
        plt.close(findings)
        for _, figure in boards:
            pdf.savefig(figure, facecolor="white")
            plt.close(figure)
    print(f"wrote {pdf_path}")


if __name__ == "__main__":
    main()
