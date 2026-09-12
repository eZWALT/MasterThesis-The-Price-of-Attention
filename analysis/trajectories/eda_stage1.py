"""Stage 1: deep exploratory analysis of the genre-trajectory dataset.

Descriptive only. No advertisement contrast is tested here; the causally
coherent tests live in `run_stages_2_4.py`. The variance checks
below ask which design factor the trajectory measures vary with at all, which
is a description of the instrument rather than a hypothesis about advertising.

Primary labelling is the bare utterance, Definition 1 read literally. Contextual
labels reproduce the deployed router and are carried as an appendix comparison
only, per the 23 Aug figure decision.

Participant is the unit wherever a measure is aggregated. Arms are pooled:
shifts per conversation do not differ between laboratory and crowd
(Kruskal H = 0.04, p = .85), and the arm row is reported in the appendix table.

    python analysis/trajectories/eda_stage1.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from scipy import stats

HERE = Path(__file__).resolve().parent
DATA = HERE / "outputs"
EDA = DATA / "eda"
FIGURES = EDA / "figures"
TABLES = EDA / "tables"
sys.path.insert(0, str(HERE))

from describe_trajectories import short  # noqa: E402

PRIMARY = "utterance"
SENSITIVITY = "contextual"
TURNS = 4

NAVY = "#1B3A4B"
CLAY = "#C45C26"
INK = "#12202A"
SLATE = "#5C6B73"
BRASS = "#A38A3F"
MIST = "#9BB0BC"
PAPER = "#F4F6F7"
CMAP = LinearSegmentedColormap.from_list("traj", [PAPER, MIST, NAVY])

CONDITION_ORDER = ["a_none", "a_imp_2", "a_exp_2", "a_imp_4", "a_exp_4"]
CONDITION_TEXT = {
    "a_none": "No ad",
    "a_imp_2": "Implicit\nearly",
    "a_exp_2": "Explicit\nearly",
    "a_imp_4": "Implicit\nlate",
    "a_exp_4": "Explicit\nlate",
}
CONDITION_FLAT = {k: v.replace("\n", " ") for k, v in CONDITION_TEXT.items()}

# Classes the model falls back on when an utterance is too short to place.
JUNK = ["other", "other_obscene_or_illegal"]

# Every measure is discrete: with T=4 turns, N_shift and diversity take four
# values, persistence four, and entropy only the five achievable partitions of
# four turns. Distributions are therefore drawn as stacked proportions rather
# than as boxes, which would collapse against the ceiling.
MEASURES = [
    ("n_shift", "Genre shifts $N_{\\mathrm{shift}}$", "Genre shifts N_shift", 3),
    ("diversity", "Diversity $D$", "Diversity D", TURNS),
    ("entropy_nats", "Entropy $H$ (nats)", "Entropy H (nats)", float(np.log(TURNS))),
    ("max_persistence", "Max persistence $R$", "Max persistence R", TURNS),
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
            "legend.frameon": False,
        }
    )


def save(figure: plt.Figure, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    figure.savefig(FIGURES / f"{name}.pdf", format="pdf")
    figure.savefig(FIGURES / f"{name}.png", format="png")
    plt.close(figure)
    return FIGURES / f"{name}.png"


def write_table(frame: pd.DataFrame, name: str) -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    frame.to_csv(TABLES / f"{name}.csv", index=False)


def markdown(frame: pd.DataFrame, precision: int = 3) -> str:
    if frame.empty:
        return "_empty_"
    columns = list(frame.columns)
    numeric = [pd.api.types.is_numeric_dtype(frame[c]) for c in columns]
    header = "| " + " | ".join(str(c) for c in columns) + " |"
    rule = "| " + " | ".join("---:" if n else "---" for n in numeric) + " |"
    lines = [header, rule]
    for row in frame.itertuples(index=False):
        cells = []
        for value, is_numeric in zip(row, numeric):
            if isinstance(value, float):
                cells.append(f"{value:.{precision}f}")
            elif is_numeric:
                cells.append(str(value))
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def summarise(values: pd.Series) -> dict:
    """Mean, dispersion and a 95% interval for a descriptive column."""
    clean = values.dropna()
    n = len(clean)
    mean = clean.mean()
    sd = clean.std(ddof=1) if n > 1 else 0.0
    half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n) if n > 1 and sd > 0 else 0.0
    quartiles = clean.quantile([0.25, 0.5, 0.75])
    return {
        "n": n,
        "mean": mean,
        "sd": sd,
        "ci_low": mean - half,
        "ci_high": mean + half,
        "q25": quartiles.loc[0.25],
        "median": quartiles.loc[0.5],
        "q75": quartiles.loc[0.75],
        "min": clean.min(),
        "max": clean.max(),
    }


def runs(sequence: list[str]) -> list[int]:
    """Lengths of every maximal contiguous run of one genre."""
    lengths = []
    current = 1
    for previous, nxt in zip(sequence, sequence[1:]):
        if previous == nxt:
            current += 1
        else:
            lengths.append(current)
            current = 1
    lengths.append(current)
    return lengths


def icc_one_way(frame: pd.DataFrame, value: str, group: str) -> float:
    """ICC(1): share of variance attributable to the grouping factor.

    Descriptive here. It answers "do the same people behave alike across their
    five conversations", not whether a condition changed anything.
    """
    grouped = frame.groupby(group)[value]
    k = grouped.size().mean()
    n_groups = grouped.ngroups
    total = len(frame)
    if n_groups < 2 or total <= n_groups:
        return float("nan")
    grand = frame[value].mean()
    between = (grouped.mean().sub(grand).pow(2) * grouped.size()).sum() / (n_groups - 1)
    within = grouped.apply(lambda s: s.sub(s.mean()).pow(2).sum()).sum() / (total - n_groups)
    denominator = between + (k - 1) * within
    return float((between - within) / denominator) if denominator else float("nan")


def eta_squared(frame: pd.DataFrame, value: str, factor: str) -> float:
    """Share of total variance lying between levels of one factor."""
    grand = frame[value].mean()
    grouped = frame.groupby(factor)[value]
    between = (grouped.mean().sub(grand).pow(2) * grouped.size()).sum()
    total = frame[value].sub(grand).pow(2).sum()
    return float(between / total) if total else float("nan")


# --------------------------------------------------------------------- tables


def table_corpus(utterances: pd.DataFrame) -> pd.DataFrame:
    frame = utterances[utterances.genre_source == PRIMARY]
    rows = [
        ("Participants", f"{frame.participant_id.nunique()}"),
        (
            "Arms",
            ", ".join(
                f"{arm} {count}"
                for arm, count in frame.groupby("arm").participant_id.nunique().items()
            ),
        ),
        ("Conditions per participant", f"{frame.groupby('participant_id').condition.nunique().max()}"),
        ("Conversations", f"{frame.conversation_id.nunique()}"),
        ("User utterances", f"{frame.utterance_id.nunique()}"),
        ("Turns per conversation", f"{TURNS}"),
        ("Transitions per conversation", f"{TURNS - 1}"),
        (
            "Words per message, median [IQR]",
            f"{frame.words.median():.0f} "
            f"[{frame.words.quantile(0.25):.0f}, {frame.words.quantile(0.75):.0f}]",
        ),
        (
            "Characters per message, median [IQR]",
            f"{frame.characters.median():.0f} "
            f"[{frame.characters.quantile(0.25):.0f}, {frame.characters.quantile(0.75):.0f}]",
        ),
        (
            "Response latency (s), median [IQR]",
            f"{frame.latency_seconds.median():.0f} "
            f"[{frame.latency_seconds.quantile(0.25):.0f}, "
            f"{frame.latency_seconds.quantile(0.75):.0f}]",
        ),
        ("Genre space", "13 ThradBERT conversation-intent classes"),
    ]
    return pd.DataFrame(rows, columns=["quantity", "value"])


def table_genres(utterances: pd.DataFrame, source: str) -> pd.DataFrame:
    frame = utterances[utterances.genre_source == source]
    total = len(frame)
    rows = []
    for genre, count in frame.genre.value_counts().items():
        part = frame[frame.genre == genre]
        rows.append(
            {
                "genre": genre,
                "utterances": int(count),
                "share": count / total,
                "participants": int(part.participant_id.nunique()),
                "mean_top_posterior": round(part.top_probability.mean(), 3),
                "median_words": int(part.words.median()),
            }
        )
    return pd.DataFrame(rows)


def table_measures(conversations: pd.DataFrame, source: str) -> pd.DataFrame:
    frame = conversations[conversations.genre_source == source]
    rows = []
    for column, _, plain, ceiling in MEASURES:
        for condition in CONDITION_ORDER + ["all"]:
            subset = frame if condition == "all" else frame[frame.condition_label == condition]
            stat = summarise(subset[column])
            rows.append(
                {
                    "measure": plain,
                    "ceiling": round(ceiling, 3),
                    "condition": "All" if condition == "all" else CONDITION_FLAT[condition],
                    **stat,
                }
            )
    return pd.DataFrame(rows)


def table_variance(conversations: pd.DataFrame, source: str) -> pd.DataFrame:
    frame = conversations[conversations.genre_source == source].copy()
    frame["session_position"] = frame.session_position.astype(str)
    rows = []
    for value, label in [
        ("n_shift", "N_shift"),
        ("entropy_nats", "Entropy"),
        ("max_persistence", "Max persistence"),
    ]:
        for factor, factor_label in [
            ("condition_label", "Condition"),
            ("task_id", "Task"),
            ("arm", "Arm"),
            ("session_position", "Session position"),
        ]:
            groups = [g[value].to_numpy() for _, g in frame.groupby(factor)]
            groups = [g for g in groups if len(g) > 0]
            h, p = stats.kruskal(*groups) if len(groups) > 1 else (np.nan, np.nan)
            rows.append(
                {
                    "measure": label,
                    "factor": factor_label,
                    "levels": len(groups),
                    "kruskal_H": float(h),
                    "p": float(p),
                    "eta_squared": eta_squared(frame, value, factor),
                }
            )
        rows.append(
            {
                "measure": label,
                "factor": "Participant (ICC)",
                "levels": frame.participant_id.nunique(),
                "kruskal_H": np.nan,
                "p": np.nan,
                "eta_squared": icc_one_way(frame, value, "participant_id"),
            }
        )
    return pd.DataFrame(rows)


def table_structure(transitions: pd.DataFrame, source: str) -> pd.DataFrame:
    frame = transitions[transitions.genre_source == source]
    total = len(frame)
    self_rate = (frame.from_genre == frame.to_genre).mean()
    edges = frame.groupby(["from_genre", "to_genre"]).size().sort_values(ascending=False)
    destinations = frame.to_genre.value_counts(normalize=True)
    rows = [
        ("Transitions", f"{total}"),
        ("Self-transitions (diagonal mass)", f"{self_rate:.3f}"),
        ("Shift rate", f"{1 - self_rate:.3f}"),
        ("Distinct genre pairs observed", f"{len(edges)} of {13 * 13}"),
        ("Modal destination", f"{short(destinations.index[0])} ({destinations.iloc[0]:.3f})"),
        (
            "Top three edges",
            "; ".join(
                f"{short(a)}\u2192{short(b)} {count}" for (a, b), count in edges.head(3).items()
            ),
        ),
    ]
    return pd.DataFrame(rows, columns=["quantity", "value"])


def table_validity(utterances: pd.DataFrame) -> pd.DataFrame:
    frame = utterances[utterances.genre_source == PRIMARY].copy()
    frame["junk"] = frame.genre.isin(JUNK).astype(int)
    rows = []
    for turn, part in frame.groupby("turn"):
        rows.append(
            {
                "turn": int(turn),
                "utterances": len(part),
                "median_words": int(part.words.median()),
                "q25_words": int(part.words.quantile(0.25)),
                "q75_words": int(part.words.quantile(0.75)),
                "junk_share": round(part.junk.mean(), 3),
                "mean_top_posterior": round(part.top_probability.mean(), 3),
                "distinct_genres": int(part.genre.nunique()),
            }
        )
    return pd.DataFrame(rows)


def validity_models(utterances: pd.DataFrame) -> pd.DataFrame:
    """Is the junk-label drift only a message-length artefact?"""
    import statsmodels.api as sm

    frame = utterances[utterances.genre_source == PRIMARY].copy()
    frame["junk"] = frame.genre.isin(JUNK).astype(int)
    frame["log_words"] = np.log(frame.words + 1)

    rows = []
    for name, columns in [
        ("junk ~ turn", ["turn"]),
        ("junk ~ turn + log(words)", ["turn", "log_words"]),
    ]:
        design = sm.add_constant(frame[columns])
        model = sm.GLM(frame.junk, design, family=sm.families.Binomial()).fit(
            cov_type="cluster", cov_kwds={"groups": frame.participant_id}
        )
        for column in columns:
            rows.append(
                {
                    "model": name,
                    "term": column,
                    "beta": model.params[column],
                    "se": model.bse[column],
                    "p": model.pvalues[column],
                }
            )
    return pd.DataFrame(rows)


# -------------------------------------------------------------------- figures


def figure_genre_distribution(utterances: pd.DataFrame) -> Path:
    style()
    frame = utterances[utterances.genre_source == PRIMARY]
    counts = frame.genre.value_counts()
    total = counts.sum()

    figure, axis = plt.subplots(figsize=(7.0, 4.2))
    labels = [short(g) for g in counts.index][::-1]
    values = counts.to_numpy()[::-1]
    colours = [CLAY if counts.index[::-1][i] in JUNK else NAVY for i in range(len(values))]
    axis.barh(labels, values, color=colours, height=0.72)
    for index, value in enumerate(values):
        axis.text(
            value + total * 0.006,
            index,
            f"{value}  ({value / total:.1%})",
            va="center",
            fontsize=7.5,
            color=SLATE,
        )
    axis.set_xlim(0, values.max() * 1.22)
    axis.set_xlabel("user utterances")
    axis.set_title(
        "Genre distribution across the corpus", color=INK, loc="left", pad=24
    )
    axis.text(
        0,
        1.015,
        "Orange marks the two fallback classes the model uses for short messages.",
        transform=axis.transAxes,
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "eda_genre_distribution")


def figure_measures_by_condition(conversations: pd.DataFrame) -> Path:
    """Stacked level proportions, because every measure is discrete."""
    style()
    frame = conversations[conversations.genre_source == PRIMARY]
    figure, axes = plt.subplots(1, 4, figsize=(12.8, 4.1))
    shades = ["#E7ECEF", MIST, "#4A7A8C", NAVY, INK]

    for axis, (column, label, _, ceiling) in zip(axes, MEASURES):
        levels = sorted(frame[column].round(3).unique())
        table = (
            pd.crosstab(
                frame.condition_label, frame[column].round(3), normalize="index"
            )
            .reindex(CONDITION_ORDER)
            .reindex(columns=levels)
            .fillna(0.0)
        )
        bottom = np.zeros(len(CONDITION_ORDER))
        for position, level in enumerate(levels):
            values = table[level].to_numpy()
            axis.bar(
                range(len(CONDITION_ORDER)),
                values,
                bottom=bottom,
                color=shades[position % len(shades)],
                edgecolor="white",
                linewidth=0.8,
                width=0.74,
                label=f"{level:g}",
            )
            for index, value in enumerate(values):
                if value >= 0.08:
                    axis.text(
                        index,
                        bottom[index] + value / 2,
                        f"{value:.0%}",
                        ha="center",
                        va="center",
                        fontsize=6.8,
                        color="white" if position >= 2 else INK,
                    )
            bottom += values

        means = frame.groupby("condition_label")[column].mean().reindex(CONDITION_ORDER)
        for index, value in enumerate(means):
            axis.text(
                index,
                1.015,
                f"{value:.2f}",
                ha="center",
                fontsize=7,
                color=CLAY,
            )
        axis.set_xticks(range(len(CONDITION_ORDER)))
        axis.set_xticklabels([CONDITION_TEXT[c] for c in CONDITION_ORDER], fontsize=7.5)
        axis.set_ylim(0, 1.06)
        axis.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        axis.set_yticklabels(["0", "25%", "50%", "75%", "100%"], fontsize=7.5)
        axis.set_title(
            f"{label}   (max {round(ceiling, 3):g})", color=INK, fontsize=9.5, pad=22
        )
        axis.legend(
            fontsize=6.5,
            ncol=len(levels),
            loc="lower center",
            bbox_to_anchor=(0.5, 1.005),
            handlelength=0.9,
            columnspacing=0.8,
            handletextpad=0.4,
        )

    figure.suptitle(
        "Every trajectory measure is flat across conditions", color=INK, y=1.10
    )
    figure.text(
        0.005,
        -0.10,
        "Share of the 54 conversations in each condition taking each achievable value; "
        "orange numerals above are condition means.\nThe measures are discrete because T=4: "
        "at most three shifts, four distinct genres, and five achievable entropies. "
        "Descriptive only,\nno advertisement contrast is tested here.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "eda_measures_by_condition")


def figure_transition_heatmap(transitions: pd.DataFrame) -> Path:
    style()
    frame = transitions[transitions.genre_source == PRIMARY]
    order = frame.from_genre.value_counts().index.tolist()
    extra = [g for g in frame.to_genre.unique() if g not in order]
    genres = order + extra
    index = {genre: i for i, genre in enumerate(genres)}

    counts = np.zeros((len(genres), len(genres)))
    for a, b in zip(frame.from_genre, frame.to_genre):
        counts[index[a], index[b]] += 1
    totals = counts.sum(axis=1, keepdims=True)
    matrix = np.divide(counts, totals, out=np.zeros_like(counts), where=totals > 0)

    figure, axis = plt.subplots(figsize=(7.6, 6.6))
    image = axis.imshow(matrix, cmap=CMAP, vmin=0, vmax=matrix.max())
    ticks = [f"{short(g)} ({int(totals[i, 0])})" for i, g in enumerate(genres)]
    axis.set_xticks(range(len(genres)))
    axis.set_xticklabels([short(g) for g in genres], rotation=50, ha="right", fontsize=7.5)
    axis.set_yticks(range(len(genres)))
    axis.set_yticklabels(ticks, fontsize=7.5)
    for i in range(len(genres)):
        for j in range(len(genres)):
            if counts[i, j] == 0:
                continue
            axis.text(
                j,
                i,
                f"{matrix[i, j]:.2f}",
                ha="center",
                va="center",
                fontsize=6,
                color="white" if matrix[i, j] > matrix.max() * 0.6 else INK,
            )
    axis.set_xlabel("to genre")
    axis.set_ylabel("from genre (row n)")
    axis.set_title("Row-normalised genre transition matrix", color=INK, loc="left", pad=10)
    figure.colorbar(image, ax=axis, fraction=0.035, pad=0.02).set_label(
        "$P(\\mathrm{to}\\mid\\mathrm{from})$"
    )
    figure.text(
        0.005,
        -0.10,
        "810 transitions, all conditions pooled. Row counts are in the tick labels; rows with "
        "few transitions are unstable\nand should not be read cellwise. `programming` is reached "
        "once, at turn 4, so it has no outgoing transition.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "eda_transition_heatmap")


def figure_turn_profile(utterances: pd.DataFrame) -> Path:
    style()
    frame = utterances[utterances.genre_source == PRIMARY].copy()
    frame["family"] = np.where(frame.genre.isin(JUNK), "fallback classes", frame.genre)
    share = pd.crosstab(frame.turn, frame.family, normalize="index")
    leading = [
        g
        for g in frame.family.value_counts().index
        if g in share.columns
    ][:5]

    figure, axis = plt.subplots(figsize=(7.0, 4.2))
    # Orange is reserved for the fallback classes; everything else is neutral.
    palette = iter([NAVY, MIST, SLATE, BRASS, "#7E9AA8"])
    for genre in leading:
        fallback = genre == "fallback classes"
        axis.plot(
            share.index,
            share[genre],
            marker="s" if fallback else "o",
            color=CLAY if fallback else next(palette),
            linewidth=2.2 if fallback else 1.6,
            label=short(genre),
        )
    axis.set_xticks([1, 2, 3, 4])
    axis.set_xlabel("conversational turn")
    axis.set_ylabel("share of utterances")
    axis.set_ylim(0, max(share[leading].to_numpy().max() * 1.15, 0.55))
    axis.set_title("Genre mix drifts with conversational depth", color=INK, loc="left", pad=10)
    axis.legend(fontsize=8, ncol=2)
    figure.text(
        0.005,
        -0.05,
        "Five most frequent families, n=270 utterances per turn. The fallback classes "
        "(other, obscene/illegal) are pooled\nand shown in orange; their growth is partly a "
        "message-length artefact (see the validity figure).",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "eda_turn_profile")


def figure_examples(conversations: pd.DataFrame) -> Path:
    style()
    frame = conversations[conversations.genre_source == PRIMARY]
    picks = []
    wanted = [
        ("a_none", 0, "no ad, stays put"),
        ("a_none", 3, "no ad, moves every turn"),
        ("a_imp_2", 1, "implicit early"),
        ("a_exp_2", 2, "explicit early"),
        ("a_imp_4", 2, "implicit late"),
        ("a_exp_4", 3, "explicit late"),
    ]
    for condition, shifts, caption in wanted:
        candidates = frame[
            (frame.condition_label == condition) & (frame.n_shift == shifts)
        ]
        if candidates.empty:
            candidates = frame[frame.condition_label == condition]
        picks.append((candidates.iloc[0], caption))

    figure, axis = plt.subplots(figsize=(9.6, 4.6))
    axis.set_xlim(-0.4, TURNS + 0.8)
    axis.set_ylim(-0.7, len(picks) - 0.3)
    axis.axis("off")

    for row, (conversation, caption) in enumerate(picks):
        y = len(picks) - 1 - row
        genres = conversation.trajectory.split("|")
        ad_turn = conversation.ad_turn
        axis.text(
            -0.35,
            y + 0.30,
            caption,
            fontsize=8,
            color=SLATE,
            va="center",
        )
        for turn, genre in enumerate(genres, start=1):
            changed = turn > 1 and genre != genres[turn - 2]
            box = FancyBboxPatch(
                (turn - 0.42, y - 0.17),
                0.84,
                0.34,
                boxstyle="round,pad=0.02,rounding_size=0.06",
                facecolor="#D32F2F" if changed else PAPER,
                edgecolor="#D32F2F" if changed else MIST,
                linewidth=1.0,
            )
            axis.add_patch(box)
            axis.text(
                turn,
                y,
                short(genre),
                ha="center",
                va="center",
                fontsize=6.8,
                color="white" if changed else INK,
            )
            if turn < TURNS:
                axis.add_patch(
                    FancyArrowPatch(
                        (turn + 0.44, y),
                        (turn + 0.56, y),
                        arrowstyle="-|>",
                        mutation_scale=8,
                        color=SLATE,
                        linewidth=0.9,
                    )
                )
        if pd.notna(ad_turn):
            position = float(ad_turn) + 0.5
            axis.axvline(
                position,
                ymin=(y - 0.28 + 0.7) / (len(picks) + 0.4),
                ymax=(y + 0.28 + 0.7) / (len(picks) + 0.4),
                color="#F9A825",
                linewidth=2.0,
            )
            axis.text(
                position,
                y + 0.30,
                "ad",
                fontsize=7,
                color="#F9A825",
                ha="center",
            )
    for turn in range(1, TURNS + 1):
        axis.text(turn, len(picks) - 0.55, f"turn {turn}", fontsize=8, color=SLATE, ha="center")
    # No in-figure title or footnote: the manuscript caption carries them.
    return save(figure, "eda_example_trajectories")


def figure_persistence(conversations: pd.DataFrame) -> Path:
    style()
    figure, axes = plt.subplots(1, 2, figsize=(10.4, 3.9))

    frame = conversations[conversations.genre_source == PRIMARY]
    lengths = [length for t in frame.trajectory for length in runs(t.split("|"))]
    counts = pd.Series(lengths).value_counts().sort_index()
    axes[0].bar(counts.index, counts.to_numpy(), color=NAVY, width=0.62)
    for x, y in counts.items():
        axes[0].text(x, y + max(counts) * 0.015, f"{y / counts.sum():.1%}", ha="center", fontsize=7.5, color=SLATE)
    axes[0].set_xticks(range(1, TURNS + 1))
    axes[0].set_xlabel("run length (consecutive turns in one genre)")
    axes[0].set_ylabel("maximal runs")
    axes[0].set_ylim(0, max(counts) * 1.14)
    axes[0].set_title("Genre persistence $R(g^{(i)})$", color=INK, loc="left")

    distribution = frame.n_shift.value_counts().reindex(range(0, TURNS)).fillna(0)
    axes[1].bar(distribution.index, distribution.to_numpy(), color=MIST, width=0.62)
    for x, y in distribution.items():
        axes[1].text(
            x,
            y + max(distribution) * 0.015,
            f"{y / distribution.sum():.1%}",
            ha="center",
            fontsize=7.5,
            color=SLATE,
        )
    axes[1].set_xticks(range(0, TURNS))
    axes[1].set_xlabel("genre shifts per conversation (max 3)")
    axes[1].set_ylabel("conversations")
    axes[1].set_ylim(0, max(distribution) * 1.14)
    axes[1].set_title("Shifts per conversation $N_{\\mathrm{shift}}$", color=INK, loc="left")

    figure.text(
        0.005,
        -0.06,
        "270 conversations, all conditions pooled. Under the bare-utterance labelling most runs "
        "last a single turn,\nso trajectories rarely dwell in one genre.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "eda_persistence")


def figure_validity(utterances: pd.DataFrame) -> Path:
    style()
    frame = utterances[utterances.genre_source == PRIMARY].copy()
    frame["junk"] = frame.genre.isin(JUNK).astype(int)
    turns = [1, 2, 3, 4]

    figure, axes = plt.subplots(1, 3, figsize=(12.0, 3.8))

    groups = [frame.loc[frame.turn == t, "words"].to_numpy() for t in turns]
    box = axes[0].boxplot(
        groups,
        widths=0.58,
        showfliers=False,
        patch_artist=True,
        medianprops={"color": "white", "linewidth": 1.4},
        whiskerprops={"color": SLATE},
        capprops={"color": SLATE},
        boxprops={"edgecolor": SLATE},
    )
    for patch in box["boxes"]:
        patch.set_facecolor(NAVY)
    for index, values in enumerate(groups, start=1):
        upper = np.percentile(values, 75) + 1.5 * stats.iqr(values)
        axes[0].text(
            index,
            min(upper, values.max()) + 4,
            f"median {np.median(values):.0f}",
            ha="center",
            fontsize=7,
            color=SLATE,
        )
    axes[0].set_xticklabels([f"turn {t}" for t in turns])
    axes[0].set_ylabel("words per message")
    axes[0].set_title("Messages get shorter", color=INK, loc="left")

    junk = frame.groupby("turn").junk.agg(["mean", "count"])
    half = 1.96 * np.sqrt(junk["mean"] * (1 - junk["mean"]) / junk["count"])
    axes[1].errorbar(
        turns,
        junk["mean"],
        yerr=half,
        fmt="o-",
        color=CLAY,
        capsize=4,
        linewidth=1.8,
    )
    axes[1].set_xticks(turns)
    axes[1].set_xlabel("conversational turn")
    axes[1].set_ylabel("share labelled a fallback class")
    axes[1].set_ylim(0, max(junk["mean"] + half) * 1.25)
    axes[1].set_title("Fallback labels grow", color=INK, loc="left")

    confidence = frame.groupby("turn").top_probability.agg(["mean", "sem"])
    axes[2].errorbar(
        turns,
        confidence["mean"],
        yerr=1.96 * confidence["sem"],
        fmt="o-",
        color=NAVY,
        capsize=4,
        linewidth=1.8,
    )
    axes[2].axhline(1 / 13, color=SLATE, linestyle=":", linewidth=1.1)
    axes[2].text(1.0, 1 / 13 + 0.008, "chance", fontsize=7, color=SLATE)
    axes[2].set_xticks(turns)
    axes[2].set_xlabel("conversational turn")
    axes[2].set_ylabel("mean top posterior")
    axes[2].set_ylim(0, 0.55)
    axes[2].set_title("Confidence is flat", color=INK, loc="left")

    figure.suptitle(
        "What the bare-utterance labelling can bear", color=INK, y=1.04
    )
    figure.text(
        0.005,
        -0.1,
        "n=1,080 utterances, 270 per turn. Later messages are elliptical, and a single-utterance "
        "classifier has less to work with.\nBars are 95% intervals. Confidence does not decline, "
        "so the drift is not the model degrading; part of it is length.",
        fontsize=7.5,
        color=SLATE,
    )
    return save(figure, "eda_label_validity")


def figure_appendix_contextual(utterances: pd.DataFrame, transitions: pd.DataFrame) -> Path:
    style()
    figure, axes = plt.subplots(2, 2, figsize=(12.4, 10.4))

    for column, source in enumerate((PRIMARY, SENSITIVITY)):
        title = "Bare utterance (primary)" if source == PRIMARY else "Contextual (deployed)"
        counts = utterances[utterances.genre_source == source].genre.value_counts()
        total = counts.sum()
        axis = axes[0, column]
        axis.barh(
            [short(g) for g in counts.index][::-1],
            counts.to_numpy()[::-1],
            color=NAVY if source == PRIMARY else CLAY,
            height=0.72,
        )
        for index, value in enumerate(counts.to_numpy()[::-1]):
            axis.text(
                value + total * 0.008,
                index,
                f"{value / total:.1%}",
                va="center",
                fontsize=7,
                color=SLATE,
            )
        axis.set_xlim(0, counts.max() * 1.2)
        axis.set_xlabel("user utterances")
        axis.set_title(f"{title}\n{counts.size} of 13 classes used", color=INK, loc="left")

        frame = transitions[transitions.genre_source == source]
        genres = frame.from_genre.value_counts().index.tolist()
        genres += [g for g in frame.to_genre.unique() if g not in genres]
        index_map = {genre: i for i, genre in enumerate(genres)}
        matrix = np.zeros((len(genres), len(genres)))
        for a, b in zip(frame.from_genre, frame.to_genre):
            matrix[index_map[a], index_map[b]] += 1
        totals = matrix.sum(axis=1, keepdims=True)
        matrix = np.divide(matrix, totals, out=np.zeros_like(matrix), where=totals > 0)

        axis = axes[1, column]
        axis.imshow(matrix, cmap=CMAP, vmin=0, vmax=1)
        axis.set_xticks(range(len(genres)))
        axis.set_xticklabels([short(g) for g in genres], rotation=50, ha="right", fontsize=7)
        axis.set_yticks(range(len(genres)))
        axis.set_yticklabels([short(g) for g in genres], fontsize=7)
        for i in range(len(genres)):
            for j in range(len(genres)):
                if matrix[i, j] > 0:
                    axis.text(
                        j,
                        i,
                        f"{matrix[i, j]:.2f}",
                        ha="center",
                        va="center",
                        fontsize=5.5,
                        color="white" if matrix[i, j] > 0.6 else INK,
                    )
        axis.set_xlabel("to genre")
        axis.set_ylabel("from genre")
        diagonal = (frame.from_genre == frame.to_genre).mean()
        axis.set_title(f"Self-transition mass {diagonal:.2f}", color=INK, loc="left")

    figure.suptitle(
        "Appendix: the two readings of $f_\\theta$ are different dynamical systems",
        color=INK,
        y=1.0,
    )
    figure.subplots_adjust(hspace=0.42)
    figure.text(
        0.005,
        -0.01,
        "Left: Definition 1 applied to the bare utterance. Right: the deployed classifier, which "
        "also sees the task prompt and the last three messages.\nThe contextual reading reproduces "
        "the logged runtime labels 1080/1080; the bare reading agrees with them 32.5% of the time. "
        "Same 1,080 messages\nand the same 810 transitions in both columns.",
        fontsize=7.5,
        color=SLATE,
        va="top",
    )
    return save(figure, "eda_appendix_contextual")


# --------------------------------------------------------------------- report


def build_report(
    utterances: pd.DataFrame,
    conversations: pd.DataFrame,
    transitions: pd.DataFrame,
    figures: list[Path],
) -> str:
    primary_conversations = conversations[conversations.genre_source == PRIMARY]
    primary_utterances = utterances[utterances.genre_source == PRIMARY]

    corpus = table_corpus(utterances)
    genres = table_genres(utterances, PRIMARY)
    genres_context = table_genres(utterances, SENSITIVITY)
    measures = table_measures(conversations, PRIMARY)
    measures_context = table_measures(conversations, SENSITIVITY)
    variance = table_variance(conversations, PRIMARY)
    structure = table_structure(transitions, PRIMARY)
    structure_context = table_structure(transitions, SENSITIVITY)
    validity = table_validity(utterances)
    models = validity_models(utterances)

    for frame, name in [
        (corpus, "t1_corpus"),
        (genres, "t2_genre_distribution"),
        (measures, "t3_measures_by_condition"),
        (variance, "t4_variance_checks"),
        (structure, "t5_transition_structure"),
        (validity, "t6_label_validity"),
        (models, "t7_validity_models"),
        (genres_context, "a1_genre_distribution_contextual"),
        (measures_context, "a2_measures_by_condition_contextual"),
        (structure_context, "a3_transition_structure_contextual"),
    ]:
        write_table(frame, name)

    shift_any = (primary_conversations.n_shift > 0).mean()
    diversity = primary_conversations.diversity.mean()
    entropy = primary_conversations.entropy_nats.mean()

    lines = [
        "# Stage 1: exploratory analysis of genre trajectories",
        "",
        "Descriptive only. No advertisement contrast is tested here.",
        "The primary labelling is the bare utterance (Definition 1 read literally);",
        "the contextual labelling appears only in the appendix section at the end.",
        "",
        "## 1.1 Corpus",
        "",
        markdown(corpus),
        "",
        "Arms are pooled throughout. Shifts per conversation do not differ between",
        "the laboratory and crowd arms (see the variance table in 1.4).",
        "",
        "## 1.2 Genre distribution",
        "",
        markdown(genres),
        "",
        f"All 13 classes are used. `purchasable_products` reaches "
        f"{int(genres.loc[genres.genre == 'purchasable_products', 'utterances'].iloc[0])} "
        f"of {len(primary_utterances)} utterances despite every task being a shopping scenario.",
        "",
        "## 1.3 Trajectory measures",
        "",
        "Ceilings are imposed by the design: with T=4 turns there are at most 3",
        "shifts, at most 4 distinct genres, entropy at most ln 4 = 1.386 nats, and",
        "persistence at most 4. Diversity is **not** bounded by the 13 classes.",
        "",
        markdown(measures),
        "",
        f"Pooled across conditions, conversations average {primary_conversations.n_shift.mean():.2f}",
        f"shifts of a possible 3, visit {diversity:.2f} distinct genres of a possible 4",
        f"({diversity / TURNS:.0%} of ceiling), and reach {entropy:.2f} nats of a possible 1.386",
        f"({entropy / np.log(TURNS):.0%} of ceiling). {shift_any:.1%} of conversations contain at",
        "least one shift. Under this labelling a trajectory rarely repeats a genre.",
        "",
        "## 1.4 Where the variance sits",
        "",
        "Descriptive omnibus checks. These ask which design factor a measure varies",
        "with at all; they are not advertisement tests.",
        "",
        markdown(variance, precision=4),
        "",
        "## 1.5 Transition structure",
        "",
        markdown(structure),
        "",
        "## 1.6 What the labelling can bear",
        "",
        "This subsection is a property of the instrument and qualifies everything above.",
        "",
        markdown(validity),
        "",
        "Logistic models for a fallback label, clustered by participant:",
        "",
        markdown(models, precision=4),
        "",
        "Messages shorten sharply across turns and the fallback classes absorb the",
        "difference. Length explains part of it: `log(words)` enters the model",
        "negatively and the turn coefficient shrinks once length is adjusted for.",
        "It does not explain all of it: the turn term survives, and mean classifier",
        "confidence is flat across turns, so the drift is not the model degrading.",
        "Both halves belong in the write-up.",
        "",
        "## Appendix: contextual labelling",
        "",
        markdown(genres_context),
        "",
        markdown(measures_context),
        "",
        markdown(structure_context),
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

    EDA.mkdir(parents=True, exist_ok=True)
    figures = [
        figure_genre_distribution(utterances),
        figure_measures_by_condition(conversations),
        figure_transition_heatmap(transitions),
        figure_turn_profile(utterances),
        figure_examples(conversations),
        figure_persistence(conversations),
        figure_validity(utterances),
        figure_appendix_contextual(utterances, transitions),
    ]

    report = build_report(utterances, conversations, transitions, figures)
    (EDA / "eda.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"\nwrote {EDA / 'eda.md'}")
    for path in figures:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
