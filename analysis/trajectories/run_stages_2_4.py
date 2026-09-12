"""Stages 2–4: advertisement effects, redirection, moderation.

Confirmatory family A (Walter, 23 Aug):

  1. Crossing hard shift δ, early-pooled vs no-ad (2→3 vs 2→3).
  2. Implicit early minus explicit early on hard δ.
  3. δ-tilde permutation (Definition 6 subcase).

Hard labels only. Soft companions (JS, TV) are not part of this family.

Holm is within each outcome, not across outcomes. Destinations are
descriptive. Timing is a negative control, not a treatment moderator.
Contextual labels are sensitivity / appendix only.

The 25 early conversations already in the advertisement genre at turn 2
cannot produce δ-tilde = 1 (a stay is not a shift). Primary keeps
Definition 6 as written (those 25 are zeros). A one-line sensitivity
drops them from the denominator.

Participant is the unit, N=54. Stage 5 is blocked.

    python analysis/trajectories/run_stages_2_4.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
DATA = HERE / "outputs"
OUT = DATA / "stages_2_4"
FIGURES = OUT / "figures"
TABLES = OUT / "tables"
sys.path.insert(0, str(HERE))

from analyse_trajectories import (  # noqa: E402
    CONTROL,
    EARLY,
    LATE,
    POSITIVE_CONTROL_PREVALENCE,
    PRIMARY_SOURCE,
    SENSITIVITY_SOURCE,
    adjacent_outcomes,
    crossing_frame,
    exact_crossing_table,
    exact_paired_purchasable,
    holm,
    paired_test,
    positive_control,
    targeted_tests,
)
from classify_advertisements import permutation_null, turn_pivot  # noqa: E402
from describe_trajectories import short  # noqa: E402

NAVY = "#1B3A4B"
BLUE = "#1565C0"
CLAY = "#C45C26"
INK = "#12202A"
SLATE = "#5C6B73"
MIST = "#9BB0BC"
PAPER = "#F4F6F7"

CONTRAST_ORDER = [
    "early ads pooled - no ad",
    "implicit early - no ad",
    "explicit early - no ad",
    "implicit early - explicit early",
]
CONTRAST_SHORT = {
    "early ads pooled - no ad": "Early pooled − no ad",
    "implicit early - no ad": "Implicit early − no ad",
    "explicit early - no ad": "Explicit early − no ad",
    "implicit early - explicit early": "Implicit − explicit",
    "late ads pooled - no ad": "Late pooled − no ad",
    "implicit late - no ad": "Implicit late − no ad",
    "explicit late - no ad": "Explicit late − no ad",
}

# The two residual classes of f_genre. Hollow markers in the depth figure so
# the reader can separate a content shift from a fallback-label rise.
FALLBACK_SHORT = {short("other"), short("other_obscene_or_illegal")}

LIVE_DESTINATIONS = [
    "relationships_and_personal_reflection",
    "general_guidance_and_info",
    "other_obscene_or_illegal",
    "academic_help",
    "other",
    "personal_writing_or_communication",
    "media_generation_or_analysis",
    "greetings_and_chitchat",
    "purchasable_products",
]


def style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 130,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.edgecolor": SLATE,
            "axes.labelcolor": INK,
            "text.color": INK,
            "xtick.color": SLATE,
            "ytick.color": SLATE,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
        }
    )


def save(figure: plt.Figure, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    figure.savefig(FIGURES / f"{name}.pdf", format="pdf", bbox_inches="tight")
    figure.savefig(FIGURES / f"{name}.png", format="png", bbox_inches="tight")
    plt.close(figure)
    return FIGURES / f"{name}.png"


def write_table(frame: pd.DataFrame, name: str) -> Path:
    TABLES.mkdir(parents=True, exist_ok=True)
    path = TABLES / f"{name}.csv"
    frame.to_csv(path, index=False)
    return path


def markdown(frame: pd.DataFrame, precision: int = 3) -> str:
    if frame.empty:
        return "_empty_"
    columns = list(frame.columns)
    numeric = [pd.api.types.is_numeric_dtype(frame[c]) for c in columns]
    lines = [
        "| " + " | ".join(str(c) for c in columns) + " |",
        "| " + " | ".join("---:" if n else "---" for n in numeric) + " |",
    ]
    for row in frame.itertuples(index=False):
        cells = []
        for value, is_numeric in zip(row, numeric):
            if isinstance(value, float):
                if pd.isna(value):
                    cells.append("—")
                else:
                    cells.append(f"{value:.{precision}f}")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def early_with_ads(conversations: pd.DataFrame, source: str) -> pd.DataFrame:
    ads = pd.read_csv(DATA / "advertisements.csv")
    frame = conversations[
        (conversations.genre_source == source) & conversations.ad_turn.eq(2)
    ].copy()
    frame = frame.merge(
        ads[["conversation_id", "ad_genre", "ad_genre_confidence"]],
        on="conversation_id",
        how="left",
    )
    return frame.join(turn_pivot(source), on="conversation_id")


def decorate_early(early: pd.DataFrame) -> pd.DataFrame:
    frame = early.copy()
    frame["already"] = (frame.genre_2 == frame.ad_genre).astype(int)
    frame["shifted"] = frame.delta_2.astype(int)
    frame["aligned"] = (frame.genre_3 == frame.ad_genre).astype(int)
    frame["delta_tilde"] = frame.shifted * frame.aligned
    frame["kind"] = np.where(
        frame.shifted == 0,
        "same genre",
        np.where(frame.aligned == 1, "ad-aligned shift", "unrelated shift"),
    )
    return frame


def late_tests(conversations: pd.DataFrame, outcome: str, source: str) -> pd.DataFrame:
    frame = conversations[conversations.genre_source == source]
    wide = frame.pivot_table(
        index="participant_id", columns="condition_label", values=outcome
    )
    results = [
        paired_test(wide[LATE].mean(axis=1) - wide[CONTROL], "late ads pooled - no ad"),
        paired_test(wide["a_imp_4"] - wide[CONTROL], "implicit late - no ad"),
        paired_test(wide["a_exp_4"] - wide[CONTROL], "explicit late - no ad"),
    ]
    out = pd.DataFrame(results)
    out["p_holm"] = holm(out.p_t.tolist())
    return out


def destination_table(transitions: pd.DataFrame, source: str) -> pd.DataFrame:
    frame = transitions[transitions.genre_source == source]
    crossing = frame[frame.position == "crosses_ad"]
    control = frame[(frame.condition_label == CONTROL) & (frame.k == 2)]
    rows = []
    for label, data in [("crossing", crossing), ("no_ad_k2", control)]:
        for subset, name in [(data, "all"), (data[data.delta == 1], "shifts_only")]:
            counts = subset.to_genre.value_counts()
            for genre, count in counts.items():
                rows.append(
                    {
                        "genre_source": source,
                        "set": label,
                        "subset": name,
                        "to_genre": genre,
                        "count": int(count),
                        "share": count / len(subset) if len(subset) else 0.0,
                        "n": len(subset),
                    }
                )
    return pd.DataFrame(rows)


def precision_row(transitions: pd.DataFrame, outcome: str, unit: str) -> dict:
    table = crossing_frame(transitions, outcome, PRIMARY_SOURCE)
    differences = (table.early_pooled - table.control).dropna()
    n = len(differences)
    mean = differences.mean()
    sd = differences.std(ddof=1)
    half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n) if n > 1 and sd > 0 else 0.0
    rng = np.random.default_rng(11)
    values = differences.to_numpy()
    boots = np.array(
        [rng.choice(values, size=n, replace=True).mean() for _ in range(10_000)]
    )
    blo, bhi = np.quantile(boots, [0.025, 0.975])
    return {
        "outcome": outcome,
        "unit": unit,
        "n": n,
        "mean": mean,
        "ci_half": half,
        "ci_low": mean - half,
        "ci_high": mean + half,
        "boot_ci_low": blo,
        "boot_ci_high": bhi,
        "excluded_|dz|": half / sd if sd else np.nan,
        "between_transition_sd": transitions.loc[
            transitions.genre_source == PRIMARY_SOURCE, outcome
        ].std(ddof=1),
    }


def permutation_values(early: pd.DataFrame, n: int = 20_000, seed: int = 11):
    rng = np.random.default_rng(seed)
    following = early.genre_3.to_numpy()
    shifted = early.delta_2.to_numpy() == 1
    genres = early.ad_genre.to_numpy()
    observed = int(((following == genres) & shifted).sum())
    null = np.empty(n, dtype=int)
    for index in range(n):
        null[index] = ((following == rng.permutation(genres)) & shifted).sum()
    return observed, null


# ------------------------------------------------------------------ figures


def figure_crossing_forest(hard: pd.DataFrame) -> Path:
    style()
    figure, axis = plt.subplots(figsize=(7.2, 3.6))
    frame = hard.set_index("contrast").reindex(CONTRAST_ORDER)
    positions = np.arange(len(CONTRAST_ORDER))
    xlim = (-0.35, 0.35)
    for index, row in enumerate(frame.itertuples()):
        colour = NAVY if index == 0 else SLATE
        axis.errorbar(
            row.mean,
            index,
            xerr=[[row.mean - row.ci_low], [row.ci_high - row.mean]],
            fmt="o",
            color=colour,
            capsize=3.5,
            markersize=6.5,
            elinewidth=1.4,
        )
        axis.text(
            xlim[1] - 0.01,
            index,
            f"Holm {row.p_holm:.2f}",
            ha="right",
            va="center",
            fontsize=7.5,
            color=SLATE,
        )
    axis.axvline(0, color=INK, linewidth=0.8)
    axis.set_yticks(positions)
    axis.set_yticklabels([CONTRAST_SHORT[c] for c in CONTRAST_ORDER])
    axis.invert_yaxis()
    axis.set_xlim(*xlim)
    axis.set_xlabel("within-person difference, 95% $t$ CI")
    axis.set_title("Hard shift $\\delta$ (probability)", color=INK, loc="left")
    figure.suptitle(
        "Crossing-transition contrasts (turn 2→3, N=54)", color=INK, y=1.03
    )
    figure.text(
        0.005,
        -0.10,
        "Navy is the confirmatory pooled contrast. Holm is within this family. "
        "No interval excludes zero.\n"
        "The implicit − explicit row is the stage-4 type contrast on the same estimand. "
        "Hard labels only.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "s24_crossing_forest")


def figure_mcnemar(exact: pd.DataFrame) -> Path:
    style()
    figure, axes = plt.subplots(1, 3, figsize=(11.4, 3.8))
    names = [
        ["neither", "only control"],
        ["only treated", "both"],
    ]
    for axis, row in zip(axes, exact.itertuples()):
        both = row.shifted_treatment - row.only_treatment
        neither = row.n - both - row.only_treatment - row.only_control
        cells = np.array(
            [[neither, row.only_control], [row.only_treatment, both]], dtype=float
        )
        axis.imshow(cells, cmap="Blues", vmin=0, vmax=max(cells.max(), 1))
        for i in range(2):
            for j in range(2):
                axis.text(
                    j,
                    i,
                    f"{int(cells[i, j])}\n{names[i][j]}",
                    ha="center",
                    va="center",
                    color="white" if cells[i, j] > cells.max() * 0.55 else INK,
                    fontsize=8,
                )
        axis.set_xticks([0, 1])
        axis.set_xticklabels(["control stay", "control shift"], fontsize=7.5)
        axis.set_yticks([0, 1])
        axis.set_yticklabels(["treated stay", "treated shift"], fontsize=7.5)
        axis.set_title(
            f"{CONTRAST_SHORT[row.contrast]}\n"
            f"discordant {row.only_treatment} vs {row.only_control} · "
            f"exact p = {row.p_exact:.2f}",
            color=INK,
            fontsize=9,
        )
    figure.suptitle("Exact McNemar on the crossing transition", color=INK, y=1.05)
    figure.text(
        0.005,
        -0.08,
        "Each cell is one participant. The test uses only the off-diagonal "
        "(discordant) pairs. Primary labelling, n=54.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "s24_mcnemar")


def figure_destinations(dest: pd.DataFrame) -> Path:
    style()
    crossing = dest[(dest.set == "crossing") & (dest.subset == "shifts_only")]
    control = dest[(dest.set == "no_ad_k2") & (dest.subset == "shifts_only")]
    present = set(crossing.to_genre) | set(control.to_genre)
    ranked = (
        crossing.set_index("to_genre").share.reindex(present).fillna(0).sort_values(ascending=False)
    )
    genres = [g for g in ranked.index if g in LIVE_DESTINATIONS or ranked[g] >= 0.03]
    left = crossing.set_index("to_genre").reindex(genres)
    right = control.set_index("to_genre").reindex(genres)
    share_c = left.share.fillna(0).to_numpy()
    share_n = right.share.fillna(0).to_numpy()
    n_c = int(crossing.n.iloc[0]) if len(crossing) else 0
    n_n = int(control.n.iloc[0]) if len(control) else 0

    figure, axis = plt.subplots(figsize=(8.2, 4.6))
    y = np.arange(len(genres))
    height = 0.38
    axis.barh(y + height / 2, share_n, height, color=MIST, label=f"No-ad 2→3 shifts (n={n_n})")
    axis.barh(y - height / 2, share_c, height, color=NAVY, label=f"Crossing shifts (n={n_c})")
    axis.set_yticks(y)
    axis.set_yticklabels([short(g) for g in genres])
    axis.set_xlabel("share of shifts")
    axis.set_xlim(0, max(share_c.max(), share_n.max()) * 1.25)
    axis.invert_yaxis()
    axis.set_title(
        "Where shifts land on the crossing transition", color=INK, loc="left", pad=10
    )
    axis.legend(frameon=False, fontsize=8, loc="lower right")
    figure.text(
        0.005,
        -0.06,
        "Descriptive. Confirmatory family A does not test destinations. "
        "purchasable_products is 4 of 89 crossing shifts.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "s24_destinations")


def figure_redirection(early: pd.DataFrame) -> Path:
    style()
    groups = [
        ("all early ads", early),
        ("implicit early", early[early.condition_label == "a_imp_2"]),
        ("explicit early", early[early.condition_label == "a_exp_2"]),
    ]
    order = ["same genre", "unrelated shift", "ad-aligned shift"]
    colours = [NAVY, SLATE, CLAY]

    figure, axis = plt.subplots(figsize=(7.2, 4.0))
    bottoms = np.zeros(len(groups))
    for kind, colour in zip(order, colours):
        heights = np.array([(part.kind == kind).mean() for _, part in groups])
        axis.bar(
            range(len(groups)),
            heights,
            bottom=bottoms,
            color=colour,
            label=kind,
            edgecolor="white",
            width=0.62,
        )
        for index, value in enumerate(heights):
            if value >= 0.06:
                axis.text(
                    index,
                    bottoms[index] + value / 2,
                    f"{value:.0%}",
                    ha="center",
                    va="center",
                    color="white" if kind != "unrelated shift" else INK,
                    fontsize=8,
                )
        bottoms += heights
    axis.set_xticks(range(len(groups)))
    axis.set_xticklabels([f"{name}\n(n={len(part)})" for name, part in groups])
    axis.set_ylim(0, 1)
    axis.set_ylabel("share of early-ad conversations")
    axis.set_title("What happens on the crossing transition", color=INK, loc="left")
    axis.legend(frameon=False, fontsize=8, loc="upper right")
    figure.text(
        0.005,
        -0.08,
        "Ad-aligned shift is δ-tilde = 1. Primary labelling. Clay is the "
        "Definition 6 subcase; it is at chance under permutation.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "s24_redirection")


def figure_permutation(early: pd.DataFrame) -> Path:
    style()
    observed, null = permutation_values(early)
    figure, axis = plt.subplots(figsize=(7.0, 3.8))
    axis.hist(null, bins=np.arange(null.min(), null.max() + 2) - 0.5, color=MIST, edgecolor="white")
    axis.axvline(observed, color=CLAY, linewidth=2.0)
    axis.text(
        observed + 0.15,
        axis.get_ylim()[1] * 0.92,
        f"observed {observed}\nchance {null.mean():.1f}\np = {(null >= observed).mean():.2f}",
        color=CLAY,
        fontsize=8,
        va="top",
    )
    axis.set_xlabel("δ-tilde count under reassigned advertisement genres")
    axis.set_ylabel("permutations")
    axis.set_title(
        "Genre-aligned shifts are at chance", color=INK, loc="left"
    )
    figure.text(
        0.005,
        -0.08,
        "20,000 permutations that keep both marginals and destroy only the pairing. "
        "Primary labelling, 108 early advertisements.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "s24_permutation")


def figure_person_pairs(transitions: pd.DataFrame) -> Path:
    """One panel per early condition, so the right side stays binary."""
    style()
    table = crossing_frame(transitions, "delta", PRIMARY_SOURCE).dropna()
    figure, axes = plt.subplots(1, 2, figsize=(9.2, 4.0), sharey=True)
    rng = np.random.default_rng(4)
    panels = [
        (axes[0], table.a_imp_2, "Implicit early"),
        (axes[1], table.a_exp_2, "Explicit early"),
    ]
    for axis, treated, title in panels:
        left = table.control.to_numpy() + rng.normal(0, 0.025, len(table))
        right = treated.to_numpy() + rng.normal(0, 0.025, len(table))
        for a, b, raw_a, raw_b in zip(left, right, table.control, treated):
            if raw_b > raw_a:
                colour = CLAY
            elif raw_b < raw_a:
                colour = NAVY
            else:
                colour = MIST
            axis.plot([0, 1], [a, b], color=colour, alpha=0.4, linewidth=0.9)
        axis.scatter(np.zeros(len(left)), left, s=12, color=SLATE, zorder=3)
        axis.scatter(np.ones(len(right)), right, s=12, color=NAVY, zorder=3)
        axis.set_xticks([0, 1])
        axis.set_xticklabels(["No-ad 2→3", f"{title}\n2→3"])
        axis.set_ylim(-0.15, 1.15)
        axis.set_title(title, color=INK, loc="left")
    axes[0].set_ylabel("hard shift $\\delta$")
    figure.suptitle(
        "Most people already shift on 2→3 without an advertisement",
        color=INK,
        y=1.03,
    )
    figure.text(
        0.005,
        -0.08,
        "One line per participant (n=54). Clay = gained a shift; navy = lost one; "
        "mist = stayed. The confirmatory contrast is the mean of these slopes.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "s24_person_pairs")


def figure_depth_versus_ad(utterances: pd.DataFrame, hard: pd.DataFrame) -> Path:
    """Turn-1 vs turn-4 genre shares beside the confirmatory δ^(a)_2 contrast."""
    style()
    frame = utterances[utterances.genre_source == PRIMARY_SOURCE].copy()
    prevalence = frame.genre.value_counts(normalize=True)
    genres = sorted(prevalence[prevalence >= POSITIVE_CONTROL_PREVALENCE].index)
    rows = []
    for genre in genres:
        frame["hit"] = (frame.genre == genre).astype(int)
        wide = frame.pivot_table(index="participant_id", columns="turn", values="hit")
        result = paired_test((wide[4] - wide[1]).dropna(), genre)
        result["label"] = short(genre)
        rows.append(result)
    depth = pd.DataFrame(rows)
    depth["p_holm"] = holm(depth.p_t.tolist())
    del hard  # the δ^(a)_2 contrast is already tabulated in the manuscript

    # Single panel. The right-hand δ^(a)_2 dot that used to sit beside it
    # duplicated the crossing table; the manuscript now cross-references it.
    figure, axis = plt.subplots(figsize=(6.8, 4.2))
    order = depth.sort_values("mean")
    xmax = float(order.ci_high.max()); xmin = float(order.ci_low.min()); span = xmax - xmin
    for index, row in enumerate(order.itertuples()):
        fallback = row.label in FALLBACK_SHORT
        axis.errorbar(
            row.mean,
            index,
            xerr=[[row.mean - row.ci_low], [row.ci_high - row.mean]],
            fmt="o",
            color=SLATE if fallback else BLUE,
            mfc="white" if fallback else None,
            capsize=3.2,
            markersize=6,
            elinewidth=1.3,
        )
        holm_text = f"{row.p_holm:.3f}"[1:] if row.p_holm < 1 else "1.00"
        p_text = f"{row.mean:+.2f}, Holm $p$={holm_text}"
        if row.p_holm < 0.001:
            p_text = f"{row.mean:+.2f}, Holm $p<.001$"
        axis.text(
            row.ci_high + 0.018,
            index,
            p_text,
            ha="left",
            va="center",
            fontsize=7.5,
            color=SLATE,
        )
        if row.p_holm < 0.05:
            axis.text(
                xmax + 0.06 * span,
                index,
                "*",
                color=CLAY,
                fontsize=16,
                ha="center",
                va="center",
                fontweight="bold",
            )
    axis.axvline(0, color=INK, linewidth=0.8)
    axis.set_yticks(range(len(order)))
    axis.set_yticklabels(order.label)
    axis.set_xlim(-0.40, xmax + 0.14 * span)
    axis.set_xlabel(r"Turn 4 share $-$ turn 1 share (95% paired $t$, $N=54$)")
    # No Holm text legend: the manuscript caption carries the asterisk.
    return save(figure, "s24_depth_versus_ad")


def gee_crossing(transitions: pd.DataFrame) -> str:
    """Logistic GEE on the like-for-like 2→3 rows only.

    The first-pass GEE compared every no-ad transition (k=1,2,3) to the
    crossing rows (k=2 only). That is not the confirmatory estimand.
    """
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    frame = transitions[transitions.genre_source == PRIMARY_SOURCE].copy()
    frame = frame[
        (frame.k == 2) & frame.condition_label.isin([CONTROL, *EARLY])
    ]
    frame["is_ad"] = frame.condition_label.ne(CONTROL).astype(int)
    frame["is_implicit"] = frame.condition_label.eq("a_imp_2").astype(int)
    frame["is_explicit"] = frame.condition_label.eq("a_exp_2").astype(int)
    lines = [
        "Logistic GEE, like-for-like k=2 only "
        f"(rows {len(frame)}, people {frame.participant_id.nunique()})",
        "",
    ]
    shifts_by_task = frame.groupby("task_id").delta.sum()
    degenerate = shifts_by_task[shifts_by_task == 0].index.tolist()
    if degenerate:
        lines.append(
            "dropped for separation (zero shifts in every conversation): "
            f"{', '.join(degenerate)}"
        )
        frame = frame[~frame.task_id.isin(degenerate)]
        lines.append(
            f"after drop: rows {len(frame)}, people "
            f"{frame.participant_id.nunique()}"
        )
        lines.append("")
    try:
        model = smf.gee(
            "delta ~ is_ad + C(task_id) + session_position",
            groups="participant_id",
            data=frame,
            family=sm.families.Binomial(),
            cov_struct=sm.cov_struct.Exchangeable(),
        ).fit()
        summary = pd.DataFrame(
            {
                "coefficient": model.params,
                "std_err": model.bse,
                "z": model.tvalues,
                "p": model.pvalues,
                "odds_ratio": np.exp(model.params),
            }
        )
        lines.append(summary.round(4).to_string())
    except Exception as error:  # noqa: BLE001
        lines.append(f"model failed: {error}")
    return "\n".join(lines)


def arm_split(transitions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    frame = transitions[transitions.genre_source == PRIMARY_SOURCE]
    for arm, part in frame.groupby("arm"):
        table = crossing_frame(part, "delta", PRIMARY_SOURCE)
        result = paired_test(
            table.early_pooled - table.control, f"{arm} · early pooled − no ad"
        )
        result["arm"] = arm
        result["n_people"] = table.dropna().shape[0]
        rows.append(result)
    return pd.DataFrame(rows)


def assert_family_a(hard: pd.DataFrame, exact: pd.DataFrame, early: pd.DataFrame) -> None:
    """Lock the published digits so a later edit cannot silently rewrite them."""
    pooled = hard.set_index("contrast").loc["early ads pooled - no ad"]
    assert abs(pooled["mean"] - 0.0463) < 0.001, pooled["mean"]
    assert abs(pooled["p_holm"] - 0.9419) < 0.01, pooled["p_holm"]
    implicit = exact.set_index("contrast").loc["implicit early - no ad"]
    assert int(implicit.only_treatment) == 11
    assert int(implicit.only_control) == 6
    assert int(early.delta_tilde.sum()) == 9
    assert int(early.already.sum()) == 25
    assert len(early) == 108


def figure_adjacent(utterances: pd.DataFrame) -> Path:
    """Label-free turn-3 outcomes. Exploratory, not family A."""
    style()
    frame = utterances[utterances.genre_source == PRIMARY_SOURCE]
    third = frame[frame.turn == 3]
    control = third[third.ad_turn.isna()].groupby("participant_id")[
        ["words", "latency_seconds"]
    ].mean()
    figure, axes = plt.subplots(1, 2, figsize=(9.6, 3.8))
    for axis, column, title, unit in [
        (axes[0], "words", "Turn-3 length", "words"),
        (axes[1], "latency_seconds", "Turn-3 latency", "seconds"),
    ]:
        rows = []
        for selector, name in [
            (third.ad_turn.isna(), "No ad"),
            (third.ad_turn == 2, "Early (exposed)"),
            (third.ad_turn == 4, "Late (not yet)"),
        ]:
            treated = third[selector].groupby("participant_id")[column].mean()
            pair = pd.concat(
                [treated.rename("t"), control[column].rename("c")], axis=1
            ).dropna()
            # For no-ad the pair is identical; skip the test, plot the mean.
            rows.append((name, pair.t.mean(), pair.t.std(ddof=1) / np.sqrt(len(pair))))
        names, means, sems = zip(*rows)
        colours = [SLATE, NAVY, MIST]
        axis.bar(range(3), means, color=colours, width=0.62, edgecolor="white")
        axis.errorbar(
            range(3), means, yerr=[1.96 * s for s in sems], fmt="none", color=INK, capsize=3
        )
        axis.set_xticks(range(3))
        axis.set_xticklabels(names, fontsize=8)
        axis.set_ylabel(unit)
        axis.set_title(title, color=INK, loc="left")
    figure.suptitle(
        "The next message is not longer or slower after an early ad",
        color=INK,
        y=1.03,
    )
    figure.text(
        0.005,
        -0.08,
        "Person means, n=54. Bars are 95% intervals of the mean. Late is a "
        "negative control: the turn-3 message precedes a turn-4 ad.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "s24_adjacent")


def figure_negative_control(late: pd.DataFrame) -> Path:
    style()
    order = [
        "late ads pooled - no ad",
        "implicit late - no ad",
        "explicit late - no ad",
    ]
    frame = late.set_index("contrast").reindex(order)
    figure, axis = plt.subplots(figsize=(7.2, 3.2))
    for index, row in enumerate(frame.itertuples()):
        axis.errorbar(
            row.mean,
            index,
            xerr=[[row.mean - row.ci_low], [row.ci_high - row.mean]],
            fmt="o",
            color=SLATE,
            capsize=3.5,
            markersize=6.5,
            elinewidth=1.4,
        )
        axis.text(
            frame.ci_high.max() + 0.04,
            index,
            f"Holm {row.p_holm:.2f}",
            va="center",
            fontsize=7.5,
            color=SLATE,
        )
    axis.axvline(0, color=INK, linewidth=0.8)
    axis.set_yticks(range(len(order)))
    axis.set_yticklabels([CONTRAST_SHORT[c] for c in order])
    axis.invert_yaxis()
    axis.set_xlabel("within-person $N_{\\mathrm{shift}}$ difference, 95% $t$ CI")
    axis.set_title(
        "Negative control: late conversations vs no-ad", color=INK, loc="left"
    )
    figure.text(
        0.005,
        -0.10,
        "A turn-4 advertisement has no following utterance, so these trajectories "
        "cannot carry δ^(a). A difference here would be nuisance structure.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "s24_negative_control")


# ------------------------------------------------------------------- report


def build_report(
    hard: pd.DataFrame,
    exact: pd.DataFrame,
    dest: pd.DataFrame,
    early: pd.DataFrame,
    late: pd.DataFrame,
    precision: pd.DataFrame,
    hard_ctx: pd.DataFrame,
    exact_ctx: pd.DataFrame,
    early_ctx: pd.DataFrame,
    arms: pd.DataFrame,
    gee: str,
    depth: str,
    adjacent: str,
    purchasable: str,
    figures: list[Path],
) -> str:
    n = len(early)
    same = int((early.kind == "same genre").sum())
    unrelated = int((early.kind == "unrelated shift").sum())
    aligned = int((early.kind == "ad-aligned shift").sum())
    shifted = unrelated + aligned
    already = int(early.already.sum())
    could = early[early.already == 0]
    tilde_could = int(could.delta_tilde.sum())
    observed, null = permutation_values(early)

    crossing_shifts = dest[(dest.set == "crossing") & (dest.subset == "shifts_only")]
    control_shifts = dest[(dest.set == "no_ad_k2") & (dest.subset == "shifts_only")]
    merged = (
        crossing_shifts[["to_genre", "count", "share", "n"]]
        .merge(
            control_shifts[["to_genre", "count", "share"]],
            on="to_genre",
            how="outer",
            suffixes=("_crossing", "_control"),
        )
        .fillna(0)
        .sort_values("share_crossing", ascending=False)
    )
    merged["to_genre"] = merged.to_genre.map(short)

    by_type = []
    for condition, name in [("a_imp_2", "implicit"), ("a_exp_2", "explicit")]:
        part = early[early.condition_label == condition]
        by_type.append(
            {
                "ad_type": name,
                "n": len(part),
                "same": int((part.kind == "same genre").sum()),
                "unrelated": int((part.kind == "unrelated shift").sum()),
                "aligned": int((part.kind == "ad-aligned shift").sum()),
                "already_in_ad_genre": int(part.already.sum()),
            }
        )

    lines = [
        "# Stages 2–4: advertisement effects, redirection, moderation",
        "",
        "Confirmatory family A. Primary labelling is the bare utterance.",
        "Holm is within each outcome. Destinations are descriptive.",
        "Timing is a negative control. Contextual is sensitivity.",
        "",
        "## 2. Do advertisements change the crossing transition?",
        "",
        "Estimand: transition 2→3 in early ads vs the same transition in no-ad,",
        "paired within participant. N=54.",
        "",
        "### Hard shift",
        "",
        markdown(hard.round(4)),
        "",
        "### Exact McNemar",
        "",
        markdown(exact.round(4)),
        "",
        "### How precise is this null",
        "",
        markdown(precision.round(4)),
        "",
        "With n=54 the design rules out medium effects on genre movement but",
        "not small ones. The null is bounded, not merely unobserved.",
        "",
        "### Destination shares among shifts (descriptive)",
        "",
        markdown(merged),
        "",
        "### Logistic GEE on the like-for-like 2→3 rows",
        "",
        "The first-pass GEE mixed all three no-ad transitions with the k=2",
        "crossing rows. That is not family A. The model below is k=2 only.",
        "",
        "```",
        gee,
        "```",
        "",
        "### Arm split of the confirmatory contrast",
        "",
        markdown(arms.round(4)),
        "",
        "## 2b. The instrument is not dead",
        "",
        "Conversational depth occurred in every conversation. If the labels",
        "cannot move with it, an advertisement null is uninformative.",
        "",
        "```",
        depth,
        "```",
        "",
        "Label-independent checks on the turn-3 message (words, latency):",
        "",
        "```",
        adjacent,
        "```",
        "",
        "## 3. Did the next utterance land on the advertised genre?",
        "",
        f"Early advertisements: {n}. Same genre {same} ({same / n:.3f}),",
        f"unrelated shift {unrelated} ({unrelated / n:.3f}),",
        f"ad-aligned shift {aligned} ({aligned / n:.3f}).",
        "",
        f"Conditional q = P(aligned | shifted) = {aligned}/{shifted} = {aligned / shifted:.3f}.",
        "",
        f"Already in the advertisement genre at turn 2: {already} of {n}.",
        "Those conversations cannot produce δ-tilde = 1, because a stay is not",
        "a shift. Primary keeps Definition 6 as written (they count as zeros).",
        f"Sensitivity, dropping them: {tilde_could} of {len(could)}",
        f"({tilde_could / len(could):.3f}) vs primary {aligned}/{n} = {aligned / n:.3f}.",
        "",
        "```",
        permutation_null(early),
        "```",
        "",
        f"Permutation on the observed count: {observed} vs chance {null.mean():.2f},",
        f"p = {(null >= observed).mean():.3f}.",
        "",
        markdown(pd.DataFrame(by_type)),
        "",
        "Commercial-intent reading (shift into purchasable_products):",
        "",
        "```",
        purchasable,
        "```",
        "",
        "## 4. Moderation",
        "",
        "Ad type is tested on the crossing estimand (implicit − explicit row",
        "in the hard-shift table). Timing is not a treatment moderator.",
        "",
        "### Negative control: late N_shift vs no-ad",
        "",
        markdown(late.round(4)),
        "",
        "## Sensitivity: contextual labels",
        "",
        "### Hard shift",
        "",
        markdown(hard_ctx.round(4)),
        "",
        "### Exact McNemar",
        "",
        markdown(exact_ctx.round(4)),
        "",
        f"Contextual δ-tilde: {int(early_ctx.delta_tilde.sum())} of {len(early_ctx)} ",
        f"(already in ad genre at turn 2: {int(early_ctx.already.sum())}). ",
        "The sticky chain makes the subcase almost unreachable.",
        "",
        "## Figures",
        "",
    ]
    lines += [f"- `{path.relative_to(DATA)}`" for path in figures]
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    utterances = pd.read_csv(DATA / "utterances.csv")
    conversations = pd.read_csv(DATA / "conversations.csv")
    transitions = pd.read_csv(DATA / "transitions.csv")

    OUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)

    hard = targeted_tests(transitions, "delta", PRIMARY_SOURCE)
    exact = exact_crossing_table(transitions, PRIMARY_SOURCE)
    late = late_tests(conversations, "n_shift", PRIMARY_SOURCE)
    dest = destination_table(transitions, PRIMARY_SOURCE)
    early = decorate_early(early_with_ads(conversations, PRIMARY_SOURCE))
    assert_family_a(hard, exact, early)
    precision = pd.DataFrame(
        [precision_row(transitions, "delta", "shift probability")]
    )
    hard_ctx = targeted_tests(transitions, "delta", SENSITIVITY_SOURCE)
    exact_ctx = exact_crossing_table(transitions, SENSITIVITY_SOURCE)
    early_ctx = decorate_early(early_with_ads(conversations, SENSITIVITY_SOURCE))
    arms = arm_split(transitions)
    gee = gee_crossing(transitions)
    depth = positive_control(utterances, PRIMARY_SOURCE)
    adjacent = adjacent_outcomes(utterances)
    purchasable = exact_paired_purchasable(conversations)

    for frame, name in [
        (hard, "t1_crossing_hard"),
        (exact, "t3_mcnemar"),
        (late, "t4_negative_control"),
        (dest, "t5_destinations"),
        (precision, "t6_precision"),
        (arms, "t7_arm_split"),
        (hard_ctx, "a1_crossing_hard_contextual"),
        (exact_ctx, "a2_mcnemar_contextual"),
    ]:
        write_table(frame, name)

    figures = [
        figure_crossing_forest(hard),
        figure_depth_versus_ad(utterances, hard),
        figure_person_pairs(transitions),
        figure_mcnemar(exact),
        figure_destinations(dest),
        figure_redirection(early),
        figure_permutation(early),
        figure_adjacent(utterances),
        figure_negative_control(late),
    ]

    report = build_report(
        hard,
        exact,
        dest,
        early,
        late,
        precision,
        hard_ctx,
        exact_ctx,
        early_ctx,
        arms,
        gee,
        depth,
        adjacent,
        purchasable,
        figures,
    )
    (OUT / "stages_2_4.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote {OUT / 'stages_2_4.md'}")
    pack = FIGURES / "s24_paper_pack.pdf"
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.image as mpimg

    paper = [
        "s24_crossing_forest.png",
        "s24_depth_versus_ad.png",
        "s24_redirection.png",
        "s24_permutation.png",
    ]
    with PdfPages(pack) as pdf:
        for name in paper:
            image = mpimg.imread(FIGURES / name)
            height, width = image.shape[:2]
            sheet = plt.figure(figsize=(11.0, 11.0 * height / width))
            axis = sheet.add_axes([0, 0, 1, 1])
            axis.imshow(image)
            axis.axis("off")
            pdf.savefig(sheet)
            plt.close(sheet)
    print(f"wrote {pack}")
    for path in figures:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
