"""Exploratory pass: new estimators, not new subgroups.

Walter asked for more. The honest way to give more is not to cut family A
into smaller cells until something clears .05. It is to ask whether the
confirmatory null is an artefact of a lossy outcome, and to price the
slicing that does happen.

Four things family A could not see:

  1. Definition 6 is argmax-on-argmax. The classifier emits a 13-dim
     posterior and the advertisement carries a genre; the binary
     delta-tilde throws all of that away and lands on 9 of 108. The
     continuous version asks whether posterior mass on the advertised
     genre moves, as a difference-in-differences against the same genre
     in the same person's no-ad conversation. Same question, ~an order of
     magnitude more information per observation.
  2. A mean of zero is compatible with strong effects that cancel. The
     heterogeneity test asks whether between-person spread in the
     response exceeds what within-person randomisation alone produces.
  3. Family A tested one cell of the transition matrix. The omnibus asks
     whether the whole k=2 matrix differs at all.
  4. Slicing. Every slice Walter might ask for is computed here, and then
     the maximum statistic over the entire grid is compared to the same
     maximum computed under randomisation. That converts "the best cell
     had p = .03" into a family-wise statement.

Nulls are design-based. Conditions were randomised within participant, so
the reference distribution permutes condition labels among a person's own
five conversations, or reassigns advertisement genres across conversations
while holding the genre marginal fixed. Both respect the pairing.

Primary labelling is the bare utterance. Participant is the unit, N=54.
Late advertisements are shown at turn 4 and have no following utterance,
so they are a placebo for every estimator below. Stage 5 is blocked.

    python analysis/trajectories/run_exploratory.py
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
OUT = DATA / "exploratory"
FIGURES = OUT / "figures"
TABLES = OUT / "tables"
sys.path.insert(0, str(HERE))

from analyse_trajectories import (  # noqa: E402
    CONTROL,
    EARLY,
    LATE,
    PRIMARY_SOURCE,
    SENSITIVITY_SOURCE,
    holm,
    paired_test,
)

NAVY = "#1B3A4B"
CLAY = "#C45C26"
SLATE = "#5C6B73"
MIST = "#9DB4C0"
INK = "#22333B"

PERMUTATIONS = 20_000
SEED = 11
CONDITIONS = [CONTROL, *EARLY, *LATE]


def style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 150,
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
        }
    )


def save(figure: plt.Figure, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix in ("pdf", "png"):
        figure.savefig(FIGURES / f"{name}.{suffix}")
    plt.close(figure)
    return FIGURES / f"{name}.png"


def write_table(frame: pd.DataFrame, name: str) -> Path:
    TABLES.mkdir(parents=True, exist_ok=True)
    path = TABLES / f"{name}.csv"
    frame.to_csv(path, index=False)
    return path


def markdown(frame: pd.DataFrame) -> str:
    return frame.to_markdown(index=False)


def short(genre: str) -> str:
    return (
        genre.replace("_and_", "/")
        .replace("_or_", "/")
        .replace("_", " ")
        .replace("general guidance/info", "guidance")
        .replace("other obscene/illegal", "obscene/illegal")
    )


# --------------------------------------------------------------------------
# 1. Continuous redirection
# --------------------------------------------------------------------------


def posterior_panel(
    utterances: pd.DataFrame, ads: pd.DataFrame, source: str = PRIMARY_SOURCE
) -> pd.DataFrame:
    """One row per conversation, carrying posterior mass on the ad genre.

    For an advertisement conversation the genre is its own advertisement's
    genre. For the paired no-ad conversation the genre is borrowed from the
    advertisement conversation it is being compared against, so the two
    sides of the difference are always about the same 13-dim coordinate.
    """
    frame = utterances[utterances.genre_source == source]
    keep = ["conversation_id", "participant_id", "condition_label", "turn"]
    genre_columns = [c for c in frame.columns if c.startswith("p_")]
    frame = frame[keep + genre_columns + ["genre", "task_id", "arm", "session_position"]]

    ad_genre = ads.set_index("conversation_id").ad_genre
    rows = []
    control = frame[frame.condition_label == CONTROL]
    control_by_person = {p: g for p, g in control.groupby("participant_id")}

    for conversation_id, block in frame[frame.condition_label != CONTROL].groupby(
        "conversation_id"
    ):
        genre = ad_genre.get(conversation_id)
        if not isinstance(genre, str):
            continue
        column = f"p_{genre}"
        person = block.participant_id.iloc[0]
        mate = control_by_person.get(person)
        if mate is None:
            continue
        treated = block.set_index("turn")
        untreated = mate.set_index("turn")
        row = {
            "conversation_id": conversation_id,
            "participant_id": person,
            "condition_label": block.condition_label.iloc[0],
            "ad_genre": genre,
            "task_id": block.task_id.iloc[0],
            "arm": block.arm.iloc[0],
            "session_position": int(block.session_position.iloc[0]),
        }
        for turn in (1, 2, 3, 4):
            row[f"treated_t{turn}"] = float(treated.loc[turn, column])
            row[f"control_t{turn}"] = float(untreated.loc[turn, column])
            row[f"treated_hit_t{turn}"] = int(treated.loc[turn, "genre"] == genre)
            row[f"control_hit_t{turn}"] = int(untreated.loc[turn, "genre"] == genre)
        rows.append(row)

    panel = pd.DataFrame(rows)
    # The estimand: change across the advertisement, net of the same change
    # in the same person's control conversation on the same genre.
    panel["treated_lift"] = panel.treated_t3 - panel.treated_t2
    panel["control_lift"] = panel.control_t3 - panel.control_t2
    panel["did"] = panel.treated_lift - panel.control_lift
    panel["post_only"] = panel.treated_t3 - panel.control_t3
    # Any later appearance: Definition 6 looks only at the next utterance.
    panel["treated_any_later"] = panel[["treated_hit_t3", "treated_hit_t4"]].max(axis=1)
    panel["control_any_later"] = panel[["control_hit_t3", "control_hit_t4"]].max(axis=1)
    panel["treated_max_later"] = panel[["treated_t3", "treated_t4"]].max(axis=1)
    panel["control_max_later"] = panel[["control_t3", "control_t4"]].max(axis=1)
    panel["did_max_later"] = panel.treated_max_later - panel.control_max_later
    return panel


def redirection_precision(panel: pd.DataFrame) -> dict:
    """What size of redirection would this design have caught?

    The binary delta-tilde could only bound the effect in units of whole
    conversations. The continuous outcome bounds it in posterior mass, which
    is the quantity Definition 6 is a threshold of.
    """
    scores = person_scores(panel, "did", EARLY).dropna()
    n = len(scores)
    sd = float(scores.std(ddof=1))
    half = float(stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n))
    baseline = float(panel[panel.condition_label.isin(EARLY)].treated_t2.mean())
    return {
        "n": n,
        "mean": float(scores.mean()),
        "ci_half_width": half,
        "upper_bound": float(scores.mean() + half),
        "excluded_dz": float(stats.t.ppf(0.975, n - 1) / np.sqrt(n)),
        "baseline_mass_on_ad_genre": baseline,
    }


def person_scores(panel: pd.DataFrame, column: str, conditions: list[str]) -> pd.Series:
    part = panel[panel.condition_label.isin(conditions)]
    return part.groupby("participant_id")[column].mean()


def continuous_redirection(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    specs = [
        ("did", EARLY, "early pooled: posterior lift on ad genre (DiD)"),
        ("did", ["a_imp_2"], "implicit early: posterior lift (DiD)"),
        ("did", ["a_exp_2"], "explicit early: posterior lift (DiD)"),
        ("post_only", EARLY, "early pooled: turn-3 mass on ad genre (post only)"),
        ("did_max_later", EARLY, "early pooled: best of turns 3-4 (post only)"),
        ("did", LATE, "PLACEBO late ads: posterior lift before exposure (DiD)"),
    ]
    for column, conditions, label in specs:
        scores = person_scores(panel, column, conditions)
        result = paired_test(scores, label)
        rows.append(result)
    frame = pd.DataFrame(rows)
    confirmatory = frame.contrast.str.startswith("early pooled") | frame.contrast.str.contains(
        "implicit early|explicit early"
    )
    pvalues = frame.p_t.tolist()
    frame["p_holm"] = holm(pvalues)
    frame.loc[~confirmatory, "p_holm"] = np.nan
    return frame


# --------------------------------------------------------------------------
# 2. Heterogeneity
# --------------------------------------------------------------------------


def condition_matrix(frame: pd.DataFrame, value: str) -> pd.DataFrame:
    """Person x condition matrix of a per-conversation scalar."""
    wide = frame.pivot_table(
        index="participant_id", columns="condition_label", values=value
    )
    return wide.reindex(columns=CONDITIONS).dropna()


def crossing_matrix(transitions: pd.DataFrame, outcome: str = "delta") -> pd.DataFrame:
    frame = transitions[
        (transitions.genre_source == PRIMARY_SOURCE) & (transitions.k == 2)
    ]
    return condition_matrix(frame, outcome)


def shuffle_within_person(matrix: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Permute condition labels among each participant's own conversations.

    This is the randomisation that actually happened, so it is the reference
    distribution: it preserves each person's multiset of outcomes and
    destroys only which condition produced which.
    """
    out = matrix.copy()
    for row in out:
        rng.shuffle(row)
    return out


def contrast_from_matrix(
    matrix: np.ndarray, index: dict[str, int], conditions: list[str] | None = None
) -> np.ndarray:
    """Person-level treated-mean minus control."""
    treated = conditions or EARLY
    mean = np.nanmean(matrix[:, [index[c] for c in treated]], axis=1)
    return mean - matrix[:, index[CONTROL]]


def heterogeneity(matrix: pd.DataFrame) -> tuple[dict, np.ndarray]:
    """Does the response vary between people more than randomisation allows?

    A mean of zero is also what you get if half the sample is pushed one way
    and half the other. If that were happening, the spread of the
    person-level difference would exceed its randomisation null. It does not
    have to be a mean test to be a real test.
    """
    index = {c: i for i, c in enumerate(matrix.columns)}
    values = matrix.to_numpy(dtype=float)
    observed_scores = contrast_from_matrix(values, index)
    observed_sd = float(np.std(observed_scores, ddof=1))
    observed_mean = float(np.mean(observed_scores))

    rng = np.random.default_rng(SEED)
    null_sd = np.empty(PERMUTATIONS)
    null_mean = np.empty(PERMUTATIONS)
    for i in range(PERMUTATIONS):
        permuted = shuffle_within_person(values, rng)
        scores = contrast_from_matrix(permuted, index)
        null_sd[i] = np.std(scores, ddof=1)
        null_mean[i] = np.mean(scores)
    return (
        {
            "observed_sd": observed_sd,
            "null_sd_mean": float(null_sd.mean()),
            "p_sd": float((null_sd >= observed_sd).mean()),
            "observed_mean": observed_mean,
            "p_mean_two_sided": float(
                (np.abs(null_mean) >= abs(observed_mean)).mean()
            ),
        },
        null_sd,
    )


# --------------------------------------------------------------------------
# 3. Omnibus on the whole transition matrix
# --------------------------------------------------------------------------


def omnibus_transition(transitions: pd.DataFrame) -> tuple[dict, np.ndarray]:
    """Does the whole k=2 transition matrix differ, not just its diagonal?

    Family A tested one summary of this matrix. If advertisements rearranged
    where conversations go without changing how often they move, the hard
    shift rate would miss it entirely.
    """
    frame = transitions[
        (transitions.genre_source == PRIMARY_SOURCE)
        & (transitions.k == 2)
        & transitions.condition_label.isin([CONTROL, *EARLY])
    ].copy()
    frame["is_ad"] = frame.condition_label.ne(CONTROL).astype(int)
    pairs = list(zip(frame.from_genre, frame.to_genre))
    unique = sorted(set(pairs))
    code = {pair: i for i, pair in enumerate(unique)}
    coded = np.array([code[p] for p in pairs])
    labels = frame.is_ad.to_numpy()
    people = frame.participant_id.to_numpy()

    def statistic(mask: np.ndarray) -> float:
        treated = np.bincount(coded[mask == 1], minlength=len(unique)).astype(float)
        untreated = np.bincount(coded[mask == 0], minlength=len(unique)).astype(float)
        treated /= treated.sum()
        untreated /= untreated.sum()
        return float(np.abs(treated - untreated).sum() / 2)

    observed = statistic(labels)
    rng = np.random.default_rng(SEED)
    null = np.empty(PERMUTATIONS)
    order = {person: np.where(people == person)[0] for person in np.unique(people)}
    for i in range(PERMUTATIONS):
        permuted = labels.copy()
        for indices in order.values():
            permuted[indices] = rng.permutation(labels[indices])
        null[i] = statistic(permuted)
    return (
        {
            "observed_total_variation": observed,
            "null_mean": float(null.mean()),
            "p": float((null >= observed).mean()),
            "cells": len(unique),
        },
        null,
    )


# --------------------------------------------------------------------------
# 4. The slice grid, priced
# --------------------------------------------------------------------------


def build_slices(transitions: pd.DataFrame) -> list[tuple[str, pd.Index]]:
    """Every subgroup a reader might ask for, enumerated up front.

    Task and session position are properties of a conversation, not of a
    person, so they select participants through one side of the pair: a
    participant enters "ad task = X" if an early-ad conversation of theirs
    used task X, and "control task = X" if their no-ad conversation did.
    """
    frame = transitions[
        (transitions.genre_source == PRIMARY_SOURCE) & (transitions.k == 2)
    ]
    control = frame[frame.condition_label == CONTROL]
    treated = frame[frame.condition_label.isin(EARLY)]

    slices: list[tuple[str, pd.Index]] = [
        ("all participants", pd.Index(frame.participant_id.unique()))
    ]
    for arm, block in frame.groupby("arm"):
        slices.append((f"arm = {arm}", pd.Index(block.participant_id.unique())))
    for name, side in [("control", control), ("ad", treated)]:
        for task, block in side.groupby("task_id"):
            slices.append(
                (f"{name} task = {task}", pd.Index(block.participant_id.unique()))
            )
        for position, block in side.groupby("session_position"):
            slices.append(
                (
                    f"{name} session position = {int(position)}",
                    pd.Index(block.participant_id.unique()),
                )
            )
        for genre, block in side.groupby("task_genre"):
            slices.append(
                (f"{name} task genre = {genre}", pd.Index(block.participant_id.unique()))
            )
    return slices


CONTRASTS = {
    "early pooled - no ad": EARLY,
    "implicit early - no ad": ["a_imp_2"],
    "explicit early - no ad": ["a_exp_2"],
}


def slice_grid(
    matrices: dict[str, pd.DataFrame], slices: list[tuple[str, pd.Index]]
) -> tuple[pd.DataFrame, dict]:
    """Run every slice on every outcome, then price the best cell.

    Running subgroups until one clears .05 is how a null becomes a finding.
    The entire grid is recomputed under within-person randomisation and only
    the maximum |t| across the whole grid is kept, so the family-wise column
    answers the question a reader should actually ask: could shuffling alone
    have produced a cell this good anywhere in the table?

    One shuffle per participant is applied to every outcome at once, because
    a participant was randomised once, not once per outcome.
    """
    names = sorted(matrices)
    persons = matrices[names[0]].index
    for name in names[1:]:
        persons = persons.intersection(matrices[name].index)
    persons = pd.Index(sorted(persons))
    aligned = {n: matrices[n].loc[persons] for n in names}
    columns = {n: {c: i for i, c in enumerate(aligned[n].columns)} for n in names}
    values = {n: aligned[n].to_numpy(dtype=float) for n in names}
    position = {person: i for i, person in enumerate(persons)}

    cells = [
        (outcome, contrast, slice_name, np.array(
            [position[p] for p in members if p in position], dtype=int
        ))
        for outcome in names
        for contrast in CONTRASTS
        for slice_name, members in slices
    ]

    def grid_statistics(data: dict[str, np.ndarray]) -> np.ndarray:
        scores = {
            (outcome, contrast): contrast_from_matrix(
                data[outcome], columns[outcome], CONTRASTS[contrast]
            )
            for outcome in names
            for contrast in CONTRASTS
        }
        out = np.empty(len(cells))
        for i, (outcome, contrast, _, rows) in enumerate(cells):
            sample = scores[(outcome, contrast)][rows]
            if len(sample) < 2:
                out[i] = 0.0
                continue
            sd = np.std(sample, ddof=1)
            out[i] = np.mean(sample) / (sd / np.sqrt(len(sample))) if sd > 0 else 0.0
        return out

    observed = grid_statistics(values)

    rng = np.random.default_rng(SEED)
    permutations = 5_000
    null_max = np.empty(permutations)
    n_people, n_conditions = values[names[0]].shape
    for i in range(permutations):
        order = np.argsort(rng.random((n_people, n_conditions)), axis=1)
        shuffled = {
            n: np.take_along_axis(values[n], order, axis=1) for n in names
        }
        null_max[i] = np.max(np.abs(grid_statistics(shuffled)))

    rows = []
    for i, (outcome, contrast, slice_name, indices) in enumerate(cells):
        scores = contrast_from_matrix(
            values[outcome], columns[outcome], CONTRASTS[contrast]
        )[indices]
        t = observed[i]
        n = len(scores)
        rows.append(
            {
                "outcome": outcome,
                "contrast": contrast,
                "slice": slice_name,
                "n": n,
                "mean": float(np.mean(scores)) if n else np.nan,
                "t": float(t),
                "p_nominal": float(stats.t.sf(abs(t), n - 1) * 2) if n > 1 else 1.0,
                "p_familywise": float((null_max >= abs(t)).mean()),
            }
        )
    frame = pd.DataFrame(rows).sort_values("p_nominal").reset_index(drop=True)
    summary = {
        "cells": len(cells),
        "slices": len(slices),
        "nominal_hits": int((frame.p_nominal < 0.05).sum()),
        "expected_hits": 0.05 * len(cells),
        "best_cell": (
            f"{frame.iloc[0]['slice']} · {frame.iloc[0].contrast} · "
            f"{frame.iloc[0].outcome}"
        ),
        "best_p_nominal": float(frame.iloc[0].p_nominal),
        "best_p_familywise": float(frame.iloc[0].p_familywise),
        "observed_max_t": float(np.max(np.abs(observed))),
        "permutations": permutations,
    }
    return frame, summary, null_max


# --------------------------------------------------------------------------
# 5. Any-later-appearance
# --------------------------------------------------------------------------


def any_later(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for conditions, label in [
        (EARLY, "early pooled"),
        (["a_imp_2"], "implicit early"),
        (["a_exp_2"], "explicit early"),
        (LATE, "PLACEBO late"),
    ]:
        part = panel[panel.condition_label.isin(conditions)]
        treated = part.groupby("participant_id").treated_any_later.max()
        control = part.groupby("participant_id").control_any_later.max()
        only_t = int(((treated == 1) & (control == 0)).sum())
        only_c = int(((treated == 0) & (control == 1)).sum())
        discordant = only_t + only_c
        p = (
            float(stats.binomtest(only_t, discordant, 0.5).pvalue)
            if discordant
            else 1.0
        )
        rows.append(
            {
                "contrast": f"{label}: ad genre appears at turn 3 or 4",
                "n": len(treated),
                "with_ad": int(treated.sum()),
                "without_ad": int(control.sum()),
                "only_ad": only_t,
                "only_control": only_c,
                "p_exact": p,
            }
        )
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------


def figure_continuous(redirection: pd.DataFrame, panel: pd.DataFrame) -> Path:
    style()
    figure, axes = plt.subplots(1, 2, figsize=(10.8, 4.2))

    axis = axes[0]
    frame = redirection[redirection.contrast.str.contains("DiD|post only")]
    order = frame.iloc[::-1]
    for i, row in enumerate(order.itertuples()):
        placebo = "PLACEBO" in row.contrast
        axis.errorbar(
            row.mean,
            i,
            xerr=[[row.mean - row.ci_low], [row.ci_high - row.mean]],
            fmt="o",
            color=MIST if placebo else NAVY,
            capsize=3.2,
            markersize=6,
            elinewidth=1.3,
        )
    axis.axvline(0, color=INK, linewidth=0.8)
    axis.set_yticks(range(len(order)))
    axis.set_yticklabels(
        [c.replace(": ", ":\n") for c in order.contrast], fontsize=7.5
    )
    axis.set_xlabel("change in posterior mass on the advertised genre")
    axis.set_title("Continuous redirection", color=INK, loc="left")

    axis = axes[1]
    scores = person_scores(panel, "did", EARLY)
    axis.hist(scores, bins=18, color=MIST, edgecolor="white")
    axis.axvline(0, color=INK, linewidth=0.8)
    axis.axvline(scores.mean(), color=CLAY, linewidth=1.6)
    axis.text(
        scores.mean(),
        axis.get_ylim()[1] * 0.94,
        f" mean {scores.mean():+.4f}",
        color=CLAY,
        fontsize=8,
    )
    axis.set_xlabel("person-level difference-in-differences")
    axis.set_ylabel("participants")
    axis.set_title("Spread is symmetric about zero", color=INK, loc="left")

    figure.suptitle(
        "The advertised genre gains no posterior mass in the next message",
        color=INK,
        y=1.02,
    )
    figure.text(
        0.005,
        -0.09,
        "Difference-in-differences: (turn 3 − turn 2) posterior mass on the "
        "advertised genre, minus the same change on the same genre in the same\n"
        "person's no-ad conversation. Bars are 95% $t$ intervals, n=54. Late "
        "advertisements appear after turn 4 and act as a placebo.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "sx_continuous_redirection")


def figure_heterogeneity(result: dict, null_sd: np.ndarray) -> Path:
    style()
    figure, axis = plt.subplots(figsize=(7.4, 3.6))
    axis.hist(null_sd, bins=60, color=MIST, edgecolor="white")
    axis.axvline(result["observed_sd"], color=CLAY, linewidth=1.8)
    axis.text(
        result["observed_sd"],
        axis.get_ylim()[1] * 0.9,
        f"  observed {result['observed_sd']:.3f}\n  p = {result['p_sd']:.2f}",
        color=CLAY,
        fontsize=8,
    )
    axis.set_xlabel("SD of the person-level advertisement response")
    axis.set_ylabel("permutations")
    axis.set_title(
        "No hidden responders: spread matches within-person shuffling",
        color=INK,
        loc="left",
    )
    figure.text(
        0.005,
        -0.12,
        "If advertisements helped some people and hurt others, the observed "
        "spread would sit right of the null. Condition labels are permuted\n"
        "among each participant's own five conversations, "
        f"{PERMUTATIONS:,} times.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "sx_heterogeneity")


def figure_grid(frame: pd.DataFrame, summary: dict, null_max: np.ndarray) -> Path:
    style()
    figure, axes = plt.subplots(1, 2, figsize=(10.8, 4.0))

    axis = axes[0]
    axis.hist(
        frame.p_nominal,
        bins=np.linspace(0, 1, 21),
        color=MIST,
        edgecolor="white",
    )
    axis.axhline(
        len(frame) / 20, color=INK, linewidth=1.0, linestyle="--", label="uniform"
    )
    axis.set_xlabel("nominal $p$ across every subgroup × contrast × outcome")
    axis.set_ylabel("cells")
    axis.legend(frameon=False, fontsize=8)
    axis.set_title(
        f"{summary['cells']} cells, {summary['nominal_hits']} below .05 "
        f"(chance: {summary['expected_hits']:.1f})",
        color=INK,
        loc="left",
    )

    axis = axes[1]
    axis.hist(null_max, bins=60, color=MIST, edgecolor="white")
    axis.axvline(summary["observed_max_t"], color=CLAY, linewidth=1.8)
    axis.text(
        summary["observed_max_t"],
        axis.get_ylim()[1] * 0.88,
        f"  best real cell\n  |t| = {summary['observed_max_t']:.2f}\n"
        f"  family-wise p = {summary['best_p_familywise']:.2f}",
        color=CLAY,
        fontsize=8,
    )
    axis.set_xlabel("maximum |t| anywhere in the grid, under randomisation")
    axis.set_ylabel("permutations")
    axis.set_title("The best slice is worth nothing", color=INK, loc="left")

    figure.suptitle(
        "Slicing the confirmatory contrast every way it can be sliced",
        color=INK,
        y=1.03,
    )
    figure.text(
        0.005,
        -0.10,
        "Left: no excess of small $p$; the pile-up at 1 is the discreteness of "
        "a binary shift outcome in small cells, not evidence. Right: condition"
        "\nlabels are permuted among each participant's own five conversations "
        "and the whole grid is recomputed; the null is the largest |t| found "
        "anywhere in that shuffled grid.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "sx_slice_grid")


def figure_omnibus(result: dict, null: np.ndarray) -> Path:
    style()
    figure, axis = plt.subplots(figsize=(7.4, 3.6))
    axis.hist(null, bins=60, color=MIST, edgecolor="white")
    axis.axvline(result["observed_total_variation"], color=CLAY, linewidth=1.8)
    axis.text(
        result["observed_total_variation"],
        axis.get_ylim()[1] * 0.9,
        f"  observed {result['observed_total_variation']:.3f}\n"
        f"  p = {result['p']:.2f}",
        color=CLAY,
        fontsize=8,
    )
    axis.set_xlabel("total variation between ad and no-ad transition distributions")
    axis.set_ylabel("permutations")
    axis.set_title(
        "The whole transition matrix does not move either", color=INK, loc="left"
    )
    figure.text(
        0.005,
        -0.12,
        f"Joint (from, to) distribution over {result['cells']} observed cells at "
        "k=2. Advertisement labels are permuted within participant, "
        f"{PERMUTATIONS:,} times.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "sx_omnibus")


# --------------------------------------------------------------------------


def build_report(
    redirection: pd.DataFrame,
    later: pd.DataFrame,
    hetero: dict,
    omni: dict,
    grid: pd.DataFrame,
    grid_summary: dict,
    panel: pd.DataFrame,
    precision: dict,
    sensitivity: pd.DataFrame,
    figures: list[Path],
) -> str:
    early = panel[panel.condition_label.isin(EARLY)]
    lines = [
        "# Exploratory pass: new estimators, not new subgroups",
        "",
        "Primary labelling is the bare utterance. Participant is the unit, N=54.",
        "Nulls are design-based: condition labels are permuted among each",
        "participant's own conversations. Late advertisements are a placebo.",
        "",
        "**Nothing here is confirmatory.** Family A is locked in",
        "`stages_2_4/stages_2_4.md` and is unchanged by this file.",
        "",
        "## 1. Continuous redirection",
        "",
        "Definition 6 is argmax on argmax and lands on 9 of 108. The classifier",
        "emits a 13-dimensional posterior, so the same question can be asked of",
        "the mass on the advertised genre rather than of the winner alone.",
        "",
        "The estimand is a difference-in-differences: the change in posterior",
        "mass on the advertised genre from turn 2 to turn 3, minus the change",
        "on the *same* genre across the same turns in the same participant's",
        "no-ad conversation. Person and baseline genre affinity both cancel.",
        "",
        markdown(redirection.round(4)),
        "",
        f"Mean posterior mass on the advertised genre at turn 2 is "
        f"{early.treated_t2.mean():.3f} with an advertisement and "
        f"{early.control_t2.mean():.3f} without, so the two sides start level.",
        "",
        "### How large a redirection is ruled out",
        "",
        "The binary Definition 6 could only bound the effect in whole",
        "conversations. In posterior mass, the quantity Definition 6 is a",
        "threshold of, the bound is:",
        "",
        "```",
        f"baseline mass on the advertised genre  {precision['baseline_mass_on_ad_genre']:.3f}",
        f"observed change (DiD)                  {precision['mean']:+.4f}",
        f"95% upper bound                        {precision['upper_bound']:+.4f}",
        f"smallest |dz| excluded                 {precision['excluded_dz']:.3f}",
        "```",
        "",
        f"An advertisement would have to add more than "
        f"{precision['upper_bound']:.3f} of posterior mass to the genre it "
        f"advertises for this design to have seen it, against a baseline of "
        f"{precision['baseline_mass_on_ad_genre']:.3f}. That is a tighter "
        "statement than family A could make, and it still contains zero.",
        "",
        "### Does the genre ever arrive, even late",
        "",
        markdown(later.round(4)),
        "",
        "## 2. Is the null hiding responders",
        "",
        "A mean of zero is also what a population produces when half of it is",
        "pushed one way and half the other. That is a variance question, and it",
        "can be tested without splitting anyone into a subgroup.",
        "",
        "```",
        f"observed SD of the person-level response  {hetero['observed_sd']:.4f}",
        f"randomisation null, mean SD               {hetero['null_sd_mean']:.4f}",
        f"p (observed SD >= null)                   {hetero['p_sd']:.4f}",
        "",
        f"observed mean                             {hetero['observed_mean']:+.4f}",
        f"p (two-sided, randomisation)              {hetero['p_mean_two_sided']:.4f}",
        "```",
        "",
        "The spread of individual responses is what shuffling condition labels",
        "inside a person already produces. There is no evidence of responders",
        "cancelling non-responders.",
        "",
        "## 3. Omnibus on the transition matrix",
        "",
        "Family A tested whether conversations move. This tests whether they",
        "move *differently*: the full joint distribution over (from, to) pairs",
        "at k=2, advertisement against no-ad.",
        "",
        "```",
        f"observed total variation  {omni['observed_total_variation']:.4f}",
        f"randomisation null, mean  {omni['null_mean']:.4f}",
        f"cells with any mass       {omni['cells']}",
        f"p                         {omni['p']:.4f}",
        "```",
        "",
        "The observed separation is smaller than chance reassignment produces,",
        "which is what two samples from one distribution look like.",
        "",
        "## 4. The slice grid, priced",
        "",
        "This is the part Walter asked for. Every subgroup a reader might want",
        "is here, crossed with all three treatment contrasts on hard δ.",
        "The point is the last column: the maximum |t| over the",
        "whole grid, recomputed under within-person randomisation, says what",
        "the best cell is worth once you admit you looked everywhere.",
        "",
        "Twenty best cells by nominal p; the full grid is in",
        "`tables/x3_slice_grid.csv`.",
        "",
        markdown(grid.head(20).round(4)),
        "",
        "```",
        f"cells (slice x contrast x outcome)  {grid_summary['cells']}",
        f"distinct subgroups                  {grid_summary['slices']}",
        f"nominal hits at .05                 {grid_summary['nominal_hits']}",
        f"expected by chance                  {grid_summary['expected_hits']:.1f}",
        f"best cell                           {grid_summary['best_cell']}",
        f"best nominal p                      {grid_summary['best_p_nominal']:.4f}",
        f"best family-wise p                  {grid_summary['best_p_familywise']:.4f}",
        "```",
        "",
        "Nothing survives. The nominal p values are uniform, the count of",
        "sub-.05 cells is at or below chance, and the best cell in the entire",
        "grid is ordinary against the max-|t| null. If a subgroup claim is made",
        "later, this table is the reason it cannot be made from this dataset.",
        "",
        "## Sensitivity: contextual labels",
        "",
        "The continuous estimator repeated on the deployed classifier's own",
        "posteriors. The contextual chain is sticky, so it starts with far more",
        "mass already on the advertised genre and has correspondingly less room",
        "to move; the conclusion is unchanged.",
        "",
        markdown(sensitivity.round(4)),
        "",
        "Note the placebo row. Under contextual labels the *late* condition,",
        "whose advertisement had not yet appeared when the measured turn was",
        "written, comes closer to significance (p = .057) than the condition",
        "that was actually exposed (p = .49). Small negative drifts of this",
        "size are what these turns do on their own. Any future reading of a",
        "comparable coefficient as an advertisement effect has to explain why",
        "the placebo produces a larger one.",
        "",
        "## Figures",
        "",
    ]
    lines += [f"- `{path.relative_to(DATA)}`" for path in figures]
    lines.append("")
    return "\n".join(lines)


def assert_exploratory(
    redirection: pd.DataFrame, hetero: dict, omni: dict, grid_summary: dict
) -> None:
    """Lock the reported digits, same convention as assert_family_a().

    These are exploratory, but a quoted number that silently drifts is worse
    than an exploratory one.
    """
    pooled = redirection.set_index("contrast").loc[
        "early pooled: posterior lift on ad genre (DiD)"
    ]
    assert abs(pooled["mean"] + 0.0239) < 0.001, pooled["mean"]
    placebo = redirection.set_index("contrast").loc[
        "PLACEBO late ads: posterior lift before exposure (DiD)"
    ]
    # The placebo must stay the same size as the treatment; that equivalence
    # is the argument, not a coincidence worth losing.
    assert abs(placebo["mean"] + 0.0279) < 0.001, placebo["mean"]
    assert abs(hetero["observed_sd"] - 0.4685) < 0.001, hetero["observed_sd"]
    assert hetero["p_sd"] > 0.5, hetero["p_sd"]
    assert abs(omni["observed_total_variation"] - 0.5370) < 0.001
    assert grid_summary["cells"] == 81, grid_summary["cells"]
    assert grid_summary["nominal_hits"] <= grid_summary["expected_hits"]
    assert grid_summary["best_p_familywise"] > 0.5, grid_summary["best_p_familywise"]


def main() -> None:
    utterances = pd.read_csv(DATA / "utterances.csv")
    transitions = pd.read_csv(DATA / "transitions.csv")
    ads = pd.read_csv(DATA / "advertisements.csv")

    OUT.mkdir(parents=True, exist_ok=True)

    panel = posterior_panel(utterances, ads)
    redirection = continuous_redirection(panel)
    later = any_later(panel)
    precision = redirection_precision(panel)

    contextual = posterior_panel(utterances, ads, SENSITIVITY_SOURCE)
    sensitivity = pd.DataFrame(
        [
            paired_test(
                person_scores(contextual, "did", EARLY),
                "contextual: early pooled posterior lift (DiD)",
            ),
            paired_test(
                person_scores(contextual, "did", LATE),
                "contextual PLACEBO late: posterior lift before exposure",
            ),
        ]
    )
    sensitivity["baseline_mass"] = [
        float(contextual[contextual.condition_label.isin(EARLY)].treated_t2.mean()),
        float(contextual[contextual.condition_label.isin(LATE)].treated_t2.mean()),
    ]

    matrix = crossing_matrix(transitions)
    hetero, null_sd = heterogeneity(matrix)
    omni, null_omni = omnibus_transition(transitions)
    slices = build_slices(transitions)
    grid, grid_summary, null_max = slice_grid({"delta": matrix}, slices)

    assert_exploratory(redirection, hetero, omni, grid_summary)

    for frame, name in [
        (redirection, "x1_continuous_redirection"),
        (later, "x2_any_later"),
        (grid, "x3_slice_grid"),
        (pd.DataFrame([hetero]), "x4_heterogeneity"),
        (pd.DataFrame([omni]), "x5_omnibus"),
        (pd.DataFrame([precision]), "x6_redirection_precision"),
        (sensitivity, "a1_continuous_redirection_contextual"),
    ]:
        write_table(frame, name)

    figures = [
        figure_continuous(redirection, panel),
        figure_heterogeneity(hetero, null_sd),
        figure_omnibus(omni, null_omni),
        figure_grid(grid, grid_summary, null_max),
    ]

    report = build_report(
        redirection,
        later,
        hetero,
        omni,
        grid,
        grid_summary,
        panel,
        precision,
        sensitivity,
        figures,
    )
    (OUT / "exploratory.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote {OUT / 'exploratory.md'}")
    for path in figures:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
