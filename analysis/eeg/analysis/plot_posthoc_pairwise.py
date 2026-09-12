"""Pairwise post-hoc heatmaps for Dataset A and Dataset B.

EXPLORATORY ONLY. Reads
``analysis/eeg/statistics/outputs/posthoc/`` and writes figures beside
the other EEG boards. Nothing here is confirmatory.

    python analysis/eeg/analysis/plot_posthoc_pairwise.py

Bound: .agents/context/data-analysis/eeg/2026-08-28-posthoc-pairwise.md
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

# Every page is held open until the report PDF is written.
plt.rcParams["figure.max_open_warning"] = 0

import pandas as pd  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.colors import TwoSlopeNorm  # noqa: E402

from condition_labels import CONDITION_LABELS  # noqa: E402


ROOT = Path(__file__).resolve().parents[3]
POSTHOC = ROOT / "analysis/eeg/statistics/outputs/posthoc"
OUT = Path(__file__).resolve().parent / "outputs" / "figures" / "posthoc"

INK = "#12202A"
SLATE = "#5C6B73"
HOLM_ORANGE = "#C45C26"
HOLM_CMAP = plt.colormaps["YlOrRd_r"]
DIFF_CMAP = plt.colormaps["RdBu_r"]

DATASET_A_DISPLAY = (
    "no_ads",
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
)
DATASET_B_DISPLAY = (
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
)
SHORT = {
    "no_ads": "No ads",
    "inline_early": "Imp early",
    "inline_late": "Imp late",
    "block_early": "Exp early",
    "block_late": "Exp late",
}
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


def lower_triangle(
    frame: pd.DataFrame,
    order: tuple[str, ...],
    column: str,
    *,
    antisymmetric: bool,
) -> np.ndarray:
    """Fill the lower triangle; mask the diagonal and upper triangle."""
    size = len(order)
    matrix = np.full((size, size), np.nan)
    lookup = {
        (row["condition_1"], row["condition_2"]): float(row[column])
        for _, row in frame.iterrows()
    }
    for i, row_name in enumerate(order):
        for j, column_name in enumerate(order):
            if j >= i:
                continue
            if (row_name, column_name) in lookup:
                matrix[i, j] = lookup[(row_name, column_name)]
            elif (column_name, row_name) in lookup:
                value = lookup[(column_name, row_name)]
                matrix[i, j] = -value if antisymmetric else value
    return matrix


def draw_board(
    frame: pd.DataFrame,
    order: tuple[str, ...],
    *,
    column: str,
    antisymmetric: bool,
    title: str,
    subtitle: str,
    filename: str,
    holm_scale: bool,
) -> plt.Figure:
    matrices = {
        feature: lower_triangle(
            frame[frame["feature"] == feature],
            order,
            column,
            antisymmetric=antisymmetric,
        )
        for feature in FEATURE_ORDER
    }
    figure, axes = plt.subplots(4, 4, figsize=(17.5, 18.5))
    for axis, feature in zip(axes.ravel(), FEATURE_ORDER):
        matrix = matrices[feature]
        if holm_scale:
            cmap, norm, limits = HOLM_CMAP, None, {"vmin": 0.0, "vmax": 1.0}
            decimals = 2
        else:
            # Colour each panel on its own range: dB and dimensionless
            # proportions do not share a scale.
            span = float(np.nanmax(np.abs(matrix)))
            span = span if span > 0 else 1.0
            cmap = DIFF_CMAP
            norm = TwoSlopeNorm(vmin=-span, vcenter=0.0, vmax=span)
            limits = {}
            decimals = 2 if span >= 0.1 else 3
        ny, nx = matrix.shape
        mesh_kw = {"cmap": cmap, "shading": "flat"}
        if norm is not None:
            mesh_kw["norm"] = norm
        else:
            mesh_kw.update(limits)
        axis.pcolormesh(np.arange(nx + 1) - 0.5, np.arange(ny + 1) - 0.5, matrix, **mesh_kw)
        axis.set_xlim(-0.5, nx - 0.5)
        axis.set_ylim(ny - 0.5, -0.5)
        axis.set_aspect("auto")
        axis.set_xticks(range(len(order)))
        axis.set_yticks(range(len(order)))
        axis.set_xticklabels(
            [SHORT[name] for name in order], fontsize=7, rotation=45, ha="right"
        )
        axis.set_yticklabels([SHORT[name] for name in order], fontsize=7)
        axis.set_title(FEATURE_LABELS[feature], fontsize=9, color=INK, pad=6)
        for i in range(len(order)):
            for j in range(len(order)):
                if np.isnan(matrix[i, j]):
                    continue
                value = matrix[i, j]
                text = (
                    f"{value:.2f}"
                    if holm_scale
                    else f"{value:+.{decimals}f}"
                )
                shade = 0.0 if holm_scale else abs(value) / span
                axis.text(
                    j,
                    i,
                    text,
                    ha="center",
                    va="center",
                    fontsize=6.5,
                    color="#FFFFFF" if shade > 0.62 else INK,
                )
        for spine in axis.spines.values():
            spine.set_visible(False)
        axis.tick_params(length=0)

    figure.suptitle(title, fontsize=15, color=INK, y=0.985)
    figure.text(
        0.5,
        0.962,
        subtitle,
        ha="center",
        fontsize=9.5,
        color=SLATE,
    )
    figure.tight_layout(rect=(0, 0.01, 1, 0.952))
    return save(figure, filename)


def save(figure: plt.Figure, filename: str) -> plt.Figure:
    """Write png and pdf, and hand the figure back for the report PDF."""
    OUT.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUT / f"{filename}.pdf", format="pdf")
    figure.savefig(OUT / f"{filename}.png", format="png", dpi=200)
    print(f"Wrote {filename}.pdf / .png")
    return figure


def draw_space_comparison(frame: pd.DataFrame) -> plt.Figure:
    """Delta minus raw for Dataset B: only cross-timing cells may differ."""
    delta = frame[frame["contrast_space"] == "delta_matched_control"]
    raw = frame[frame["contrast_space"] == "raw_post_minus_pre"]
    merged = delta.merge(
        raw,
        on=["feature", "pair_id", "condition_1", "condition_2"],
        suffixes=("_delta", "_raw"),
    )
    merged["gap"] = (
        merged["mean_difference_delta"] - merged["mean_difference_raw"]
    )
    return draw_board(
        merged.rename(columns={"gap": "mean_difference"}),
        DATASET_B_DISPLAY,
        column="mean_difference",
        antisymmetric=True,
        title="Dataset B: how much the matched control moves each pair",
        subtitle=(
            "Delta space minus raw space, dB. Same-timing pairs are exactly "
            "zero because the shared control cancels; every cross-timing "
            "pair carries the control drift."
        ),
        filename="posthoc_pairwise_dataset_b_space_gap",
        holm_scale=False,
    )


def draw_confirmatory_overview(
    dataset_a: pd.DataFrame,
    delta_b: pd.DataFrame,
) -> plt.Figure:
    """One readable page: the two confirmatory measures, both datasets."""
    features = ("fz_theta_power_db_uv2", "posterior_alpha_power_db_uv2")
    panel_rows = [
        (feature, frame, order, view_title)
        for feature in features
        for frame, order, view_title in (
            (dataset_a, DATASET_A_DISPLAY, "Dataset A"),
            (delta_b, DATASET_B_DISPLAY, "Dataset B $\\Delta$"),
        )
    ]
    columns = (
        ("mean_difference", "Effect"),
        ("p_t_holm", "Holm $p$"),
        ("p_t_bh", "BH $q$"),
        ("p_t_by", "BY $q$"),
    )
    figure, axes = plt.subplots(4, 4, figsize=(15.5, 15.8))
    for row_index, (feature, frame, order, view_title) in enumerate(
        panel_rows
    ):
        for column_index, (column, header) in enumerate(columns):
            axis = axes[row_index, column_index]
            matrix = lower_triangle(
                frame[frame["feature"] == feature],
                order,
                column,
                antisymmetric=column == "mean_difference",
            )
            is_holm = column != "mean_difference"
            if is_holm:
                axis.imshow(matrix, cmap=HOLM_CMAP, vmin=0.0, vmax=1.0)
                span = 1.0
            else:
                span = float(np.nanmax(np.abs(matrix))) or 1.0
                axis.imshow(
                    matrix,
                    cmap=DIFF_CMAP,
                    norm=TwoSlopeNorm(vmin=-span, vcenter=0.0, vmax=span),
                )
            axis.set_xticks(range(len(order)))
            axis.set_yticks(range(len(order)))
            axis.set_xticklabels(
                [SHORT[name] for name in order],
                fontsize=8,
                rotation=40,
                ha="right",
            )
            axis.set_yticklabels([SHORT[name] for name in order], fontsize=8)
            for i in range(len(order)):
                for j in range(len(order)):
                    if np.isnan(matrix[i, j]):
                        continue
                    value = matrix[i, j]
                    axis.text(
                        j,
                        i,
                        f"{value:.2f}" if is_holm else f"{value:+.2f}",
                        ha="center",
                        va="center",
                        fontsize=9,
                        color=(
                            INK
                            if is_holm or abs(value) / span <= 0.62
                            else "#FFFFFF"
                        ),
                    )
            for spine in axis.spines.values():
                spine.set_visible(False)
            axis.tick_params(length=0)
            if row_index == 0:
                axis.set_title(header, fontsize=11.5, color=INK, pad=10)
            if column_index == 0:
                axis.set_ylabel(
                    f"{FEATURE_LABELS[feature].replace(' *', '')}\n"
                    f"{view_title}",
                    fontsize=10.5,
                    color=INK,
                    labelpad=12,
                )
    figure.suptitle(
        "Post-hoc pairwise sweep: the two confirmatory measures",
        fontsize=15,
        color=INK,
        y=0.983,
    )
    figure.text(
        0.5,
        0.952,
        "Cell = row minus column, n=18, 4 s median ICA. All three "
        "corrections run within measure within dataset. Exploratory: no "
        "cell is confirmatory, and none reaches .05 under Holm, BH or BY.",
        ha="center",
        fontsize=9.5,
        color=SLATE,
    )
    figure.tight_layout(rect=(0, 0.01, 1, 0.938))
    return save(figure, "posthoc_pairwise_overview")


def draw_measure_page(
    feature: str,
    dataset_a: pd.DataFrame,
    delta_b: pd.DataFrame,
    raw_b: pd.DataFrame,
) -> plt.Figure:
    """One page per measure: effects on top, Holm p below."""
    panels = (
        (dataset_a, DATASET_A_DISPLAY, "Dataset A (condition medians)"),
        (delta_b, DATASET_B_DISPLAY, "Dataset B, $\\Delta$ matched control"),
        (raw_b, DATASET_B_DISPLAY, "Dataset B, raw post$-$pre"),
    )
    row_labels = {
        "mean_difference": "Effect",
        "p_t_holm": "Holm $p$",
        "p_t_bh": "BH $q$",
        "p_t_by": "BY $q$",
    }
    figure, axes = plt.subplots(4, 3, figsize=(15.5, 18.4))
    for column_index, (frame, order, header) in enumerate(panels):
        subset = frame[frame["feature"] == feature]
        for row_index, column in enumerate(row_labels):
            axis = axes[row_index, column_index]
            is_holm = column != "mean_difference"
            matrix = lower_triangle(
                subset, order, column, antisymmetric=not is_holm
            )
            if is_holm:
                axis.imshow(matrix, cmap=HOLM_CMAP, vmin=0.0, vmax=1.0)
                span, decimals = 1.0, 2
            else:
                span = float(np.nanmax(np.abs(matrix))) or 1.0
                decimals = 2 if span >= 0.1 else 4
                axis.imshow(
                    matrix,
                    cmap=DIFF_CMAP,
                    norm=TwoSlopeNorm(vmin=-span, vcenter=0.0, vmax=span),
                )
            axis.set_xticks(range(len(order)))
            axis.set_yticks(range(len(order)))
            axis.set_xticklabels(
                [SHORT[name] for name in order],
                fontsize=8.5,
                rotation=40,
                ha="right",
            )
            axis.set_yticklabels(
                [SHORT[name] for name in order], fontsize=8.5
            )
            for i in range(len(order)):
                for j in range(len(order)):
                    if np.isnan(matrix[i, j]):
                        continue
                    value = matrix[i, j]
                    axis.text(
                        j,
                        i,
                        f"{value:.2f}"
                        if is_holm
                        else f"{value:+.{decimals}f}",
                        ha="center",
                        va="center",
                        fontsize=9,
                        color=(
                            INK
                            if is_holm or abs(value) / span <= 0.62
                            else "#FFFFFF"
                        ),
                    )
            for spine in axis.spines.values():
                spine.set_visible(False)
            axis.tick_params(length=0)
            if row_index == 0:
                axis.set_title(header, fontsize=11, color=INK, pad=10)
            if column_index == 0:
                axis.set_ylabel(
                    row_labels[column],
                    fontsize=12,
                    color=INK,
                    labelpad=12,
                )
    figure.suptitle(FEATURE_LABELS[feature], fontsize=16, color=INK, y=0.986)
    figure.text(
        0.5,
        0.966,
        "Cell = row minus column. n=18, 4 s median ICA. All three "
        "corrections within measure within dataset. Exploratory.",
        ha="center",
        fontsize=9.5,
        color=SLATE,
    )
    figure.tight_layout(rect=(0, 0.01, 1, 0.953))
    return figure


def cover_page() -> plt.Figure:
    figure = plt.figure(figsize=(15.5, 10.2))
    lines = [
        ("EEG post-hoc pairwise sweep", 26, INK, 0.80),
        (
            "Dataset A: 5 conditions, 10 pairs.  "
            "Dataset B: 4 ad conditions, 6 pairs, in $\\Delta$ and raw space.",
            13,
            SLATE,
            0.73,
        ),
        (
            "n = 18  ·  4 s · median · ICA  ·  participant is the "
            "inferential unit  ·  28 August 2026",
            11.5,
            SLATE,
            0.685,
        ),
        (
            "352 tests.  0 significant under Holm, BH or BY.",
            20,
            INK,
            0.585,
        ),
        (
            "8 cells reach uncorrected p < .05 among 320 distinct tests, "
            "against a naive chance expectation of 16.\n"
            "Holm controls the family-wise error rate and is valid under "
            "any dependence. BH controls the false discovery rate and is "
            "laxer,\nbut assumes independence or positive dependency, "
            "which these measures violate: the five relative powers sum "
            "to one.\nBenjamini-Yekutieli is the FDR valid under arbitrary "
            "dependence, and on this data it is stricter than Holm.",
            11.5,
            SLATE,
            0.485,
        ),
        (
            "EXPLORATORY. The confirmatory pipeline is untouched, still "
            "Holm as pre-specified, and was verified to reproduce to 1e-9.\n"
            "No pairwise cell is promoted, whatever its p or q.",
            12.5,
            "#C45C26",
            0.355,
        ),
        (
            "Contents\n"
            "  1  Findings\n"
            "  2  Overview, the two confirmatory measures, all corrections\n"
            "  3–6  Dataset A, all 16 measures: effect, Holm, BH, BY\n"
            "  7–10  Dataset B $\\Delta$, all 16 measures: effect, Holm, BH, BY\n"
            "  11–14  Dataset B raw, all 16 measures: effect, Holm, BH, BY\n"
            "  15  Control drift, $\\Delta$ minus raw\n"
            "  16–31  One page per measure, all three views",
            11.5,
            INK,
            0.175,
        ),
        (
            "analysis/eeg/statistics/outputs/posthoc/  ·  bound in "
            ".agents/context/data-analysis/eeg/2026-08-28-posthoc-pairwise.md",
            9.5,
            SLATE,
            0.05,
        ),
    ]
    for text, size, color, y in lines:
        figure.text(
            0.5, y, text, ha="center", va="center", fontsize=size, color=color
        )
    return figure


def findings_page() -> plt.Figure:
    """Sebastian's requested bullet summary, as page two."""
    figure = plt.figure(figsize=(15.5, 10.2))
    figure.text(
        0.06,
        0.94,
        "Findings",
        fontsize=22,
        color=INK,
        va="top",
    )
    bullets = [
        (
            "The verdict",
            [
                "352 pairwise tests. 0 significant under Holm. 0 under "
                "Benjamini-Hochberg.",
                "8 cells reach uncorrected p < .05 among 320 distinct "
                "tests; naive chance predicts 16.",
                "Every nominal Dataset B cell sits on an explicit-early "
                "comparison, which is the slow-power tilt already",
                "     documented as the six ICA-only exploratory hits. "
                "Localisation of a known event, not a new one.",
            ],
        ),
        (
            "Correction method makes no difference",
            [
                "Holm controls the family-wise error rate and is valid "
                "under arbitrary dependence. BH controls the false",
                "     discovery rate and is laxer, but assumes "
                "independence or positive dependency, which these measures",
                "     violate: the five relative powers sum to one. "
                "Benjamini-Yekutieli restores the FDR guarantee under any",
                "     dependence, and on this data it is stricter than "
                "Holm (x2.45 at m=6, x2.93 at m=10).",
                "BH lowers individual values (Fz theta Dataset B: Holm "
                ".166 to BH .094) but changes no verdict.",
                "Where one p dominates its family BH and Holm coincide "
                "exactly, so the strongest cell stays at .080; BY puts "
                "it at .196.",
                "Under every family definition from none to a single "
                "family of 320, all three methods give 0.",
            ],
        ),
        (
            "Feature reduction cannot help, and this was checked "
            "exhaustively",
            [
                "The correction runs within measure, so Dataset A families "
                "are 10 tests and Dataset B families are 6, never 160.",
                "Dropping features removes whole families and leaves the "
                "survivors untouched: it can delete the best cell,",
                "     never improve one. Dataset A stays at .368 for every "
                "subset that keeps its best measure.",
                "All 65,535 non-empty subsets of the 16 measures were "
                "searched under the harsher across-feature family, for",
                "     all three corrections. Best adjusted p obtainable "
                "anywhere: .0799 Holm, .0799 BH, .1958 BY, all from",
                "     global delta alone. None reach .05.",
            ],
        ),
        (
            "What is genuinely new: nothing dimensional",
            [
                "Five conditions leave a 4-dimensional contrast space and "
                "the four planned contrasts already span it.",
                "Every pairwise difference is an exact linear combination "
                "of contrasts already tested, verified numerically.",
                "The one exception is the Delta-space timing contrast in "
                "Dataset B, tested nowhere at present, and Holm-null.",
            ],
        ),
        (
            "Open item for Methods, not an analysis defect",
            [
                "Dataset B secondary contrast weights were never "
                "pre-specified, so raw early_vs_late is an implementation",
                "     choice. Fz theta prefers the Delta version, posterior "
                "alpha prefers raw. Fix the estimand on principle, not on p.",
            ],
        ),
    ]
    y = 0.865
    for heading, lines in bullets:
        figure.text(0.06, y, heading, fontsize=13, color=INK, va="top")
        y -= 0.038
        for line in lines:
            prefix = "" if line.startswith("     ") else "\u2022  "
            figure.text(
                0.075,
                y,
                prefix + line,
                fontsize=10.5,
                color=SLATE,
                va="top",
            )
            y -= 0.030
        y -= 0.022
    figure.text(
        0.06,
        0.035,
        "Exploratory throughout. The confirmatory pipeline is untouched, "
        "stays on Holm as pre-specified, and was verified to reproduce "
        "to 1e-9.",
        fontsize=10,
        color="#C45C26",
        va="top",
    )
    return figure


CODE = {
    "no_ads": "N",
    "inline_early": "IE",
    "inline_late": "IL",
    "block_early": "EE",
    "block_late": "EL",
}


def draw_thesis_appendix(
    dataset_a: pd.DataFrame,
    delta_b: pd.DataFrame,
) -> plt.Figure:
    """One compact panel: 16 measures by all 16 pairs, Holm p.

    Sized to stay legible at \\linewidth in the thesis, where the
    16-panel boards of the report would not be.
    """
    # Take the pairs from the data: the tables store each pair in one
    # canonical order, which is not the display order of the boards.
    blocks = []
    for frame, tag in ((dataset_a, "A"), (delta_b, "B")):
        seen = frame.drop_duplicates("pair_id")
        pairs = list(
            zip(seen["condition_1"].tolist(), seen["condition_2"].tolist())
        )
        blocks.append((frame, pairs, tag))

    columns: list[str] = []
    matrix = np.full(
        (len(FEATURE_ORDER), sum(len(p) for _, p, _ in blocks)), np.nan
    )
    offset = 0
    for frame, pairs, tag in blocks:
        for index, (first, second) in enumerate(pairs):
            columns.append(f"{CODE[first]}\u2212{CODE[second]}")
            for row, feature in enumerate(FEATURE_ORDER):
                cell = frame[
                    (frame["feature"] == feature)
                    & (frame["condition_1"] == first)
                    & (frame["condition_2"] == second)
                ]
                if not cell.empty:
                    matrix[row, offset + index] = float(
                        cell.iloc[0]["p_t_holm"]
                    )
        offset += len(pairs)
    split = len(blocks[0][1])

    figure, axis = plt.subplots(figsize=(11.0, 6.4))
    ny, nx = matrix.shape
    axis.pcolormesh(
        np.arange(nx + 1) - 0.5,
        np.arange(ny + 1) - 0.5,
        matrix,
        cmap=HOLM_CMAP,
        vmin=0.0,
        vmax=1.0,
        shading="flat",
    )
    axis.set_xlim(-0.5, nx - 0.5)
    axis.set_ylim(ny - 0.5, -0.5)
    axis.set_aspect("auto")
    axis.set_xticks(range(len(columns)))
    axis.set_xticklabels(columns, fontsize=7.5, rotation=90)
    axis.set_yticks(range(len(FEATURE_ORDER)))
    axis.set_yticklabels(
        [FEATURE_LABELS[f].replace(" *", "") for f in FEATURE_ORDER],
        fontsize=7.5,
    )
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            p = matrix[row, column]
            if np.isnan(p):
                continue
            axis.text(
                column,
                row,
                f"{p:.2f}".lstrip("0"),
                ha="center",
                va="center",
                fontsize=5.4,
                color="#FFFFFF" if p < 0.05 else INK,
                fontweight="bold" if p < 0.05 else "normal",
            )
            if p < 0.05:
                axis.text(
                    column + 0.42,
                    row - 0.38,
                    "*",
                    ha="right",
                    va="top",
                    fontsize=8,
                    color=HOLM_ORANGE,
                    fontweight="bold",
                )
    axis.axvline(split - 0.5, color="#FFFFFF", linewidth=2.4)
    axis.text(
        (split - 1) / 2,
        -1.25,
        "Dataset A, condition medians",
        ha="center",
        fontsize=9,
        color=INK,
    )
    axis.text(
        split + (len(columns) - split - 1) / 2,
        -1.25,
        "Dataset B, onset-locked",
        ha="center",
        fontsize=9,
        color=INK,
    )
    for spine in axis.spines.values():
        spine.set_visible(False)
    axis.tick_params(length=0)
    figure.tight_layout()
    return save(figure, "posthoc_pairwise_thesis")


def build_report_pdf(figures: list[plt.Figure]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "posthoc_pairwise_report.pdf"
    with PdfPages(path) as pdf:
        for figure in figures:
            pdf.savefig(figure)
    print(f"Wrote posthoc_pairwise_report.pdf ({len(figures)} pages)")


def main() -> None:
    dataset_a = pd.read_csv(POSTHOC / "eeg_posthoc_pairwise_dataset_a.csv")
    dataset_b = pd.read_csv(POSTHOC / "eeg_posthoc_pairwise_dataset_b.csv")
    delta_b = dataset_b[
        dataset_b["contrast_space"] == "delta_matched_control"
    ]
    raw_b = dataset_b[dataset_b["contrast_space"] == "raw_post_minus_pre"]

    draw_thesis_appendix(dataset_a, delta_b)
    pages = [cover_page(), findings_page()]
    pages.append(draw_confirmatory_overview(dataset_a, delta_b))
    views = (
        (
            dataset_a,
            DATASET_A_DISPLAY,
            "Dataset A",
            "dataset_a",
            "All 10 condition pairs, 16 measures, n=18, 4 s median ICA. "
            "Correction runs within measure across the 10 pairs.",
        ),
        (
            delta_b,
            DATASET_B_DISPLAY,
            "Dataset B, Delta matched control",
            "dataset_b",
            "Each cell is first differenced against its matched no-ad "
            "reply. 6 pairs, 16 measures, n=18.",
        ),
        (
            raw_b,
            DATASET_B_DISPLAY,
            "Dataset B, raw post-pre",
            "dataset_b_raw",
            "No control subtraction. Same-timing pairs match the Delta "
            "board exactly; cross-timing pairs do not.",
        ),
    )
    panels = (
        ("mean_difference", "effects (row minus column)", "effect"),
        ("p_t_holm", "Holm p", "holm"),
        ("p_t_bh", "Benjamini-Hochberg q", "bh"),
        ("p_t_by", "Benjamini-Yekutieli q", "by"),
    )
    boards = tuple(
        (
            frame,
            order,
            column,
            f"{view_title} pairwise {panel_title}",
            subtitle
            + (
                " Each panel is scaled to its own range. Exploratory."
                if column == "mean_difference"
                else " No cell reaches .05."
            ),
            f"posthoc_pairwise_{slug}_{suffix}",
        )
        for frame, order, view_title, slug, subtitle in views
        for column, panel_title, suffix in panels
    )
    for frame, order, column, title, subtitle, filename in boards:
        pages.append(
            draw_board(
                frame,
                order,
                column=column,
                antisymmetric=column == "mean_difference",
                title=title,
                subtitle=subtitle,
                filename=filename,
                holm_scale=column == "p_t_holm",
            )
        )
    pages.append(draw_space_comparison(dataset_b))

    for feature in FEATURE_ORDER:
        pages.append(
            draw_measure_page(feature, dataset_a, delta_b, raw_b)
        )

    build_report_pdf(pages)
    for figure in pages:
        plt.close(figure)


if __name__ == "__main__":
    main()
