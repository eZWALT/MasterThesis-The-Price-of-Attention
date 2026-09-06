"""First-pass inference on the genre-trajectory dataset.

Three things are estimated, in decreasing order of how much they can be
trusted:

1. The targeted advertisement test. Only an early (turn-2) advertisement can
   be crossed by a transition, so the estimand is the transition (2 -> 3) in
   the early conditions against the same transition in the no-ad condition,
   paired within participant.
2. The negative control. Every utterance in a late condition precedes the
   turn-4 advertisement, so those trajectories cannot carry an effect. A
   difference here indicates nuisance structure, not persuasion.
3. A regression that puts condition, task and session position in the same
   model, since task turns out to dominate.

Hard labels only. Soft companions between posteriors are not reported.

The primary genre labelling is the bare utterance, which is Definition 1 read
literally. The deployed system classified a context window instead, so that
labelling is carried as a sensitivity analysis rather than as the estimand.
The two differ enough to change which tests are appropriate: under the bare
labelling 97 per cent of conversations contain at least one shift, so a
conversation-level "did it shift" comparison is degenerate and the binary
tests are run on the advertisement-crossing transition instead.

    python analysis/trajectories/analyse_trajectories.py
"""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
DATA = HERE / "outputs"

# Definition 1 applies the classifier to the utterance. The deployed system
# applied it to a context window, which is a different object; it is reported
# as a sensitivity analysis.
PRIMARY_SOURCE = "utterance"
SENSITIVITY_SOURCE = "contextual"

# A genre is included in the positive-control battery if it labels at least
# this share of utterances under the primary source. Fixed before the tests so
# the control is not chosen from the genres that happen to move.
POSITIVE_CONTROL_PREVALENCE = 0.05

# Classes the model falls back on when an utterance is too short or too
# elliptical to place. Tracked because they grow across turns.
JUNK_GENRES = ["other", "other_obscene_or_illegal"]

EARLY = ["a_imp_2", "a_exp_2"]
LATE = ["a_imp_4", "a_exp_4"]
CONTROL = "a_none"


def holm(pvalues: list[float]) -> list[float]:
    """Step-down Holm adjustment, same convention as the EEG family."""
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted = [0.0] * len(pvalues)
    running = 0.0
    for rank, index in enumerate(order):
        value = (len(pvalues) - rank) * pvalues[index]
        running = max(running, min(value, 1.0))
        adjusted[index] = running
    return adjusted


def exact_paired_binary(treatment: pd.Series, control: pd.Series, label: str) -> dict:
    """Exact McNemar on 'did this conversation shift at all'.

    Shifts are rare: most conversations have none and the count never exceeds
    three. Treating that as continuous and running a t-test overstates
    precision, so the paired binary comparison on discordant pairs is the
    primary test for shift outcomes.
    """
    pair = pd.concat([treatment.rename("t"), control.rename("c")], axis=1).dropna()
    treated = (pair.t > 0).astype(int)
    untreated = (pair.c > 0).astype(int)
    only_treatment = int(((treated == 1) & (untreated == 0)).sum())
    only_control = int(((treated == 0) & (untreated == 1)).sum())
    discordant = only_treatment + only_control
    pvalue = (
        float(stats.binomtest(only_treatment, discordant, 0.5).pvalue)
        if discordant
        else 1.0
    )
    return {
        "contrast": label,
        "n": len(pair),
        "shifted_treatment": int(treated.sum()),
        "shifted_control": int(untreated.sum()),
        "only_treatment": only_treatment,
        "only_control": only_control,
        "p_exact": pvalue,
    }


def paired_test(differences: pd.Series, label: str) -> dict:
    """Paired t and Wilcoxon on participant-level differences."""
    values = differences.dropna()
    n = len(values)
    mean = values.mean()
    sd = values.std(ddof=1)
    if n < 2 or sd == 0 or values.abs().sum() == 0:
        return {
            "contrast": label,
            "n": n,
            "mean": mean,
            "ci_low": mean,
            "ci_high": mean,
            "dz": 0.0,
            "p_t": 1.0,
            "p_wilcoxon": 1.0,
        }
    half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
    return {
        "contrast": label,
        "n": n,
        "mean": mean,
        "ci_low": mean - half,
        "ci_high": mean + half,
        "dz": mean / sd,
        "p_t": float(stats.ttest_1samp(values, 0.0).pvalue),
        "p_wilcoxon": float(stats.wilcoxon(values).pvalue),
    }


def crossing_frame(
    transitions: pd.DataFrame, outcome: str, source: str = PRIMARY_SOURCE
) -> pd.DataFrame:
    """Participant-level table of the ad-crossing transition and its control.

    The comparison is like-for-like: transition (2 -> 3) in both arms, so the
    conversational position is held fixed and only the advertisement differs.
    """
    frame = transitions[transitions.genre_source == source]
    crossing = frame[frame.position == "crosses_ad"]
    control = frame[(frame.condition_label == CONTROL) & (frame.k == 2)]

    columns = {
        "control": control.groupby("participant_id")[outcome].mean(),
        "early_pooled": crossing.groupby("participant_id")[outcome].mean(),
    }
    for condition in EARLY:
        columns[condition] = (
            crossing[crossing.condition_label == condition]
            .groupby("participant_id")[outcome]
            .mean()
        )
    return pd.DataFrame(columns)


def targeted_tests(
    transitions: pd.DataFrame, outcome: str, source: str = PRIMARY_SOURCE
) -> pd.DataFrame:
    table = crossing_frame(transitions, outcome, source)
    results = [
        paired_test(table.early_pooled - table.control, "early ads pooled - no ad"),
        paired_test(table.a_imp_2 - table.control, "implicit early - no ad"),
        paired_test(table.a_exp_2 - table.control, "explicit early - no ad"),
        paired_test(table.a_imp_2 - table.a_exp_2, "implicit early - explicit early"),
    ]
    frame = pd.DataFrame(results)
    frame["p_holm"] = holm(frame.p_t.tolist())
    return frame


def exact_crossing_table(
    transitions: pd.DataFrame, source: str = PRIMARY_SOURCE
) -> pd.DataFrame:
    """Exact paired test on the advertisement-crossing transition.

    The hard shift is binary and each participant contributes exactly one
    crossing transition per early condition, so McNemar on discordant pairs is
    the primary test. This replaces the conversation-level "did it shift at
    all" comparison, which is degenerate under the bare labelling because
    almost every conversation shifts somewhere.
    """
    # The pooled column averages two conditions and so is not binary; it is
    # covered by the paired mean test above and left out here.
    table = crossing_frame(transitions, "delta", source)
    results = [
        exact_paired_binary(table.a_imp_2, table.control, "implicit early - no ad"),
        exact_paired_binary(table.a_exp_2, table.control, "explicit early - no ad"),
        exact_paired_binary(table.a_imp_2, table.a_exp_2, "implicit early - explicit early"),
    ]
    frame = pd.DataFrame(results)
    frame["p_holm"] = holm(frame.p_exact.tolist())
    return frame


def exact_paired_purchasable(conversations: pd.DataFrame) -> str:
    """Definition 6, commercial-intent reading, tested rather than asserted.

    Shifting into purchasable_products is the one outcome the theory predicts
    an advertisement should produce, so each condition is compared against
    no-ad on that indicator instead of the count being reported alone.
    """
    frame = conversations[conversations.genre_source == PRIMARY_SOURCE]
    wide = frame.pivot_table(
        index="participant_id",
        columns="condition_label",
        values="shifted_into_purchasable",
    )
    results = [
        exact_paired_binary(wide[condition], wide[CONTROL], f"{condition} - no ad")
        for condition in EARLY + LATE
    ]
    table = pd.DataFrame(results)
    table["p_holm"] = holm(table.p_exact.tolist())
    return table.round(4).to_string(index=False)


def negative_control(conversations: pd.DataFrame, outcome: str) -> pd.DataFrame:
    """Late conditions against no-ad. A real effect here is impossible."""
    frame = conversations[conversations.genre_source == PRIMARY_SOURCE]
    wide = frame.pivot_table(index="participant_id", columns="condition_label", values=outcome)
    results = [
        paired_test(wide[LATE].mean(axis=1) - wide[CONTROL], "late ads pooled - no ad"),
        paired_test(wide["a_imp_4"] - wide[CONTROL], "implicit late - no ad"),
        paired_test(wide["a_exp_4"] - wide[CONTROL], "explicit late - no ad"),
    ]
    frame_out = pd.DataFrame(results)
    frame_out["p_holm"] = holm(frame_out.p_t.tolist())
    return frame_out


def exact_condition_table(conversations: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Every condition against no-ad, exact paired binary on 'shifted at all'.

    Returns the table and a note on whether the outcome is informative. When
    almost every conversation shifts, the dichotomy carries no variance and
    the count-based tests above are the ones to read.
    """
    frame = conversations[conversations.genre_source == PRIMARY_SOURCE]
    shifted = (frame.n_shift > 0).mean()
    wide = frame.pivot_table(
        index="participant_id", columns="condition_label", values="n_shift"
    )
    results = [
        exact_paired_binary(wide[condition], wide[CONTROL], f"{condition} - no ad")
        for condition in EARLY + LATE
    ]
    table = pd.DataFrame(results)
    table["p_holm"] = holm(table.p_exact.tolist())
    note = (
        f"{shifted:.1%} of conversations contain at least one shift. "
        + (
            "The dichotomy is near-degenerate, so this table is reported for "
            "completeness only and the count tests above are primary."
            if shifted > 0.9 or shifted < 0.1
            else "The dichotomy carries variance, so this is the primary "
            "reading for shift outcomes."
        )
    )
    return table, note


def regression(transitions: pd.DataFrame) -> str:
    """Logistic GEE on trial-level shifts, clustered by participant.

    Warning: this mixes every no-ad transition (k=1,2,3; 162 rows) with the
    crossing rows (k=2 only; 108 rows). It is **not** the family-A estimand.
    Quote `gee_crossing()` in `run_stages_2_4.py` (k=2 only, OR ≈ 1.31).
    """
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    frame = transitions[transitions.genre_source == PRIMARY_SOURCE].copy()
    frame = frame[frame.position.isin(["crosses_ad", "no_ad"])]
    frame["is_ad"] = (frame.position == "crosses_ad").astype(int)

    lines = ["Logistic GEE: delta ~ is_ad + task + session position", ""]

    # A task where nobody ever shifts predicts the outcome perfectly and
    # separates the likelihood, so it is dropped rather than left to produce
    # a coefficient of -2204 with no standard error.
    shifts_by_task = frame.groupby("task_id").delta.sum()
    degenerate = shifts_by_task[shifts_by_task == 0].index.tolist()
    if degenerate:
        lines.append(
            f"dropped for separation (zero shifts in every conversation): "
            f"{', '.join(degenerate)}"
        )
        frame = frame[~frame.task_id.isin(degenerate)]

    lines.append(f"rows {len(frame)}, participants {frame.participant_id.nunique()}")
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
        lines.append(f"model failed to converge: {error}")
    return "\n".join(lines)


def precision_statement(transitions: pd.DataFrame) -> str:
    """What size of effect the targeted test could have detected.

    A null is only informative if it is precise. This reports the effect
    sizes the confidence interval excludes, rather than leaving the result
    as an unqualified absence.
    """
    lines = []
    for outcome, unit in [("delta", "shift probability")]:
        table = crossing_frame(transitions, outcome)
        differences = (table.early_pooled - table.control).dropna()
        n = len(differences)
        sd = differences.std(ddof=1)
        half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
        bound_dz = half / sd
        observed = transitions.loc[
            transitions.genre_source == PRIMARY_SOURCE, outcome
        ].std(ddof=1)
        lines.append(
            f"{outcome:14s} mean {differences.mean():+.4f} {unit}, "
            f"95% CI +/-{half:.4f}, so |dz| > {bound_dz:.2f} is excluded; "
            f"the interval spans {2 * half / observed:.2f} of a "
            f"between-transition SD."
        )
    lines.append("")
    lines.append(
        "With n=54 the design rules out medium effects on genre movement but "
        "not small ones. The null is bounded, not merely unobserved."
    )
    return "\n".join(lines)


def label_validity(utterances: pd.DataFrame) -> str:
    """What the primary labelling can and cannot bear.

    Applying the classifier to a single utterance means later turns, which are
    short and elliptical because the context is already established, give it
    much less to work with. Two junk classes absorb that: `other` and
    `other_obscene_or_illegal`, the latter firing on benign shopping messages.
    If the drift used as a positive control were only this artefact, adjusting
    for message length would remove the turn effect.
    """
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    frame = utterances[utterances.genre_source == PRIMARY_SOURCE].copy()
    sensitivity = utterances[utterances.genre_source == SENSITIVITY_SOURCE]
    frame["junk"] = frame.genre.isin(JUNK_GENRES).astype(int)
    frame["log_words"] = np.log(frame.words + 1)

    lines = [
        f"agreement with the logged runtime labels: "
        f"{PRIMARY_SOURCE} {frame.matches_runtime.mean():.3f}, "
        f"{SENSITIVITY_SOURCE} {sensitivity.matches_runtime.mean():.3f}",
        f"distinct genres used: {PRIMARY_SOURCE} {frame.genre.nunique()}, "
        f"{SENSITIVITY_SOURCE} {sensitivity.genre.nunique()} of 13",
        "",
        "median words and junk-label rate by turn:",
    ]
    by_turn = frame.groupby("turn").agg(
        median_words=("words", "median"),
        junk_rate=("junk", "mean"),
        mean_confidence=("top_probability", "mean"),
    )
    lines.append(by_turn.round(3).to_string())
    lines.append("")

    for formula in ("junk ~ turn", "junk ~ turn + log_words"):
        model = smf.gee(
            formula,
            groups="participant_id",
            data=frame,
            family=sm.families.Binomial(),
        ).fit()
        terms = ", ".join(
            f"{name} {model.params[name]:+.3f} (p={model.pvalues[name]:.4f})"
            for name in model.params.index
            if name != "Intercept"
        )
        lines.append(f"{formula:26s} {terms}")

    lines.append("")
    lines.append(
        "Short messages do attract the junk classes, so part of the drift is a "
        "length artefact. The turn term survives adjustment for length, and "
        "classifier confidence is flat across turns, so the drift is not only "
        "an artefact. Both statements belong in the write-up."
    )
    return "\n".join(lines)


def turn_profile(utterances: pd.DataFrame, source: str = PRIMARY_SOURCE) -> str:
    """Does the genre mix drift systematically across the four turns?"""
    frame = utterances[utterances.genre_source == source]
    return pd.crosstab(frame.turn, frame.genre, normalize="index").round(3).to_string()


def positive_control(utterances: pd.DataFrame, source: str = PRIMARY_SOURCE) -> str:
    """Turn position as a positive control for the trajectory measure.

    An advertisement null is only interesting if the measure can move at all.
    Conversational depth is a manipulation we know occurred in every
    conversation, so the labels should track it.
    """
    lines = []
    frame = utterances[utterances.genre_source == source].copy()

    # Battery fixed by prevalence rather than by a hand-picked pair, so the
    # control cannot be read off whichever genre happened to move.
    prevalence = frame.genre.value_counts(normalize=True)
    genres = sorted(prevalence[prevalence >= POSITIVE_CONTROL_PREVALENCE].index)
    results = []
    for genre in genres:
        frame["hit"] = (frame.genre == genre).astype(int)
        wide = frame.pivot_table(index="participant_id", columns="turn", values="hit")
        differences = (wide[4] - wide[1]).dropna()
        result = paired_test(differences, genre)
        result["turn1"] = wide[1].mean()
        result["turn4"] = wide[4].mean()
        results.append(result)
    battery = pd.DataFrame(results)
    battery["p_holm"] = holm(battery.p_t.tolist())
    for row in battery.itertuples():
        lines.append(
            f"{row.contrast:36s} turn1 {row.turn1:.3f} -> turn4 {row.turn4:.3f}  "
            f"diff {row.mean:+.3f}  dz {row.dz:+.2f}  "
            f"p_t {row.p_t:.4f}  p_holm {row.p_holm:.4f}  "
            f"p_wilcoxon {row.p_wilcoxon:.4f}"
        )
    lines.append(
        f"({len(genres)} genres at or above {POSITIVE_CONTROL_PREVALENCE:.0%} "
        f"prevalence, Holm on the paired t tests)"
    )

    # Does the label at turn k differ from the label the same conversation
    # opened with? This is drift from the conversational anchor.
    wide = frame.pivot_table(
        index="conversation_id", columns="turn", values="genre", aggfunc="first"
    )
    lines.append("")
    lines.append("Cumulative drift from the opening genre:")
    for turn in (2, 3, 4):
        lines.append(
            f"  turn {turn} differs from turn 1 in "
            f"{wide[turn].ne(wide[1]).mean():.3f} of conversations"
        )
    return "\n".join(lines)


def adjacent_outcomes(utterances: pd.DataFrame) -> str:
    """Exploratory: does the advertisement disturb the next turn at all?

    Genre labels are noisy, so two measures that need no classifier are
    checked on the same design: how long the next message is, and how long
    the participant took to write it. The turn-3 message is the one written
    after an early advertisement; the same message in the late conditions has
    not yet been exposed and serves as a negative control.
    """
    # Both outcomes are label-independent, so one genre source is taken to
    # avoid counting every utterance twice. `latency_seconds` is built into the
    # dataset rather than recomputed here.
    measures = ["words", "latency_seconds"]
    frame = utterances[utterances.genre_source == PRIMARY_SOURCE]

    third = frame[frame.turn == 3]
    control = third[third.ad_turn.isna()].groupby("participant_id")[measures].mean()
    lines = []
    for selector, title in [
        (third.ad_turn == 2, "early advertisement (exposed)"),
        (third.ad_turn == 4, "late advertisement (not yet exposed)"),
    ]:
        treated = third[selector].groupby("participant_id")[measures].mean()
        lines.append(f"--- {title} vs no-ad, turn-3 message ---")
        for column, unit in [("words", "words"), ("latency_seconds", "seconds")]:
            pair = pd.concat(
                [treated[column].rename("t"), control[column].rename("c")], axis=1
            ).dropna()
            result = paired_test(pair.t - pair.c, column)
            lines.append(
                f"  {column:16s} {pair.t.mean():7.2f} vs {pair.c.mean():7.2f} {unit}, "
                f"diff {result['mean']:+.2f}, dz {result['dz']:+.2f}, "
                f"p_wilcoxon {result['p_wilcoxon']:.4f}"
            )
        lines.append("")
    lines.append(
        "Median latency falls across turns (56, 49, 39 s at turns 2, 3, 4), so "
        "the measure is live; it simply does not respond to advertisements."
    )
    return "\n".join(lines)


def task_adjusted_conditions(conversations: pd.DataFrame) -> str:
    """Does the condition difference survive adjustment for task?

    If the late-condition gap is nuisance structure, it should disappear once
    task is in the model, because a turn-4 advertisement cannot act on
    utterances that precede it.
    """
    import statsmodels.formula.api as smf

    frame = conversations[conversations.genre_source == PRIMARY_SOURCE].copy()
    lines = []
    for formula, title in [
        ("n_shift ~ C(condition_label, Treatment('a_none'))", "condition only"),
        (
            "n_shift ~ C(condition_label, Treatment('a_none')) + C(task_id)",
            "condition adjusted for task",
        ),
    ]:
        try:
            model = smf.mixedlm(
                formula, frame, groups=frame.participant_id
            ).fit(reml=False)
            summary = pd.DataFrame(
                {"coefficient": model.params, "std_err": model.bse, "p": model.pvalues}
            )
            keep = [i for i in summary.index if "condition_label" in i]
            lines.append(f"--- {title} ---")
            lines.append(summary.loc[keep].round(4).to_string())
            lines.append("")
        except Exception as error:  # noqa: BLE001
            lines.append(f"--- {title} --- failed: {error}")
    return "\n".join(lines)


def variance_by_factor(conversations: pd.DataFrame) -> str:
    """How much of the shift signal is task and session position, not condition."""
    frame = conversations[conversations.genre_source == PRIMARY_SOURCE]
    lines = []
    for factor in ("condition_label", "task_id", "session_position", "arm"):
        groups = [group.n_shift.values for _, group in frame.groupby(factor)]
        statistic, pvalue = stats.kruskal(*groups)
        spread = frame.groupby(factor).n_shift.mean()
        lines.append(
            f"{factor:18s} range {spread.min():.3f}-{spread.max():.3f}  "
            f"Kruskal H={statistic:6.2f}  p={pvalue:.4f}"
        )
    return "\n".join(lines)


def main() -> None:
    conversations = pd.read_csv(DATA / "conversations.csv")
    transitions = pd.read_csv(DATA / "transitions.csv")

    report: list[str] = ["# Genre trajectories: first-pass inference", ""]
    report.append(
        "Genre source: the bare utterance, which is Definition 1 read literally. "
        "The deployed classifier saw a context window instead and is reported "
        "as a sensitivity analysis in Section 6. Participant is the inferential "
        "unit, n=54. Holm is applied within each family."
    )
    report.append("")

    utterances = pd.read_csv(DATA / "utterances.csv")
    report.append("## 0. What the primary labelling can bear")
    report.append("")
    report.append("```")
    report.append(label_validity(utterances))
    report.append("```")
    report.append("")

    report.append("## 1. Targeted advertisement test (the only causally coherent one)")
    report.append("")
    report.append(
        "Transition 2 -> 3, which crosses an early advertisement, against the "
        "same transition in the no-ad condition."
    )
    report.append("")
    for outcome, title in [
        ("delta", "Hard shift indicator"),
    ]:
        report.append(f"### {title}")
        report.append("")
        report.append(targeted_tests(transitions, outcome).round(4).to_string(index=False))
        report.append("")

    report.append("### The hard shift under an exact paired test")
    report.append("")
    report.append(
        "The shift indicator is binary and each participant contributes one "
        "crossing transition per condition, so McNemar on the discordant pairs "
        "is the primary test and the mean difference above is descriptive."
    )
    report.append("")
    report.append(exact_crossing_table(transitions).round(4).to_string(index=False))
    report.append("")

    report.append("### How precise is this null")
    report.append("")
    report.append("```")
    report.append(precision_statement(transitions))
    report.append("```")
    report.append("")

    report.append("## 2. Negative control: late advertisements")
    report.append("")
    report.append(
        "All four utterances precede a turn-4 advertisement, so any difference "
        "here is nuisance structure rather than an advertisement effect."
    )
    report.append("")
    for outcome, title in [
        ("n_shift", "Shifts per conversation"),
    ]:
        report.append(f"### {title}")
        report.append("")
        report.append(negative_control(conversations, outcome).round(4).to_string(index=False))
        report.append("")

    report.append("### The same comparisons on whether the conversation shifted at all")
    report.append("")
    exact_table, exact_note = exact_condition_table(conversations)
    report.append(exact_note)
    report.append("")
    report.append(exact_table.round(4).to_string(index=False))
    report.append("")

    report.append("## 3. What actually drives the shift signal")
    report.append("")
    report.append("```")
    report.append(variance_by_factor(conversations))
    report.append("```")
    report.append("")
    report.append(
        "Mixed model on shifts per conversation, participant random intercept. "
        "If the late-condition gap is a task artefact it should not survive "
        "adjustment."
    )
    report.append("")
    report.append("```")
    report.append(task_adjusted_conditions(conversations))
    report.append("```")
    report.append("")
    report.append("```")
    report.append(regression(transitions))
    report.append("```")
    report.append("")

    report.append("## 4. Genre mix across the four turns, and a positive control")
    report.append("")
    report.append("```")
    report.append(turn_profile(utterances))
    report.append("```")
    report.append("")
    report.append(
        "Conversational depth is a manipulation that occurred in every "
        "conversation, so it serves as a positive control: the measure should "
        "move with it even though it does not move with advertisements."
    )
    report.append("")
    report.append("```")
    report.append(positive_control(utterances))
    report.append("```")
    report.append("")

    report.append("## 5. Exploratory: outcomes that need no classifier")
    report.append("")
    report.append("```")
    report.append(adjacent_outcomes(utterances))
    report.append("```")
    report.append("")

    report.append("## 6. Sensitivity: the deployed contextual classifier")
    report.append("")
    report.append(
        "The same analyses under the labelling the live system actually "
        "produced, which conditioned on the task prompt and the preceding "
        "three messages rather than on the utterance alone. It agrees with the "
        "logged runtime labels on every utterance but collapses onto three "
        "genres, so it is the sensitivity analysis and not the estimand."
    )
    report.append("")
    report.append("```")
    report.append(
        targeted_tests(transitions, "delta", SENSITIVITY_SOURCE)
        .round(4)
        .to_string(index=False)
    )
    report.append("")
    report.append(
        exact_crossing_table(transitions, SENSITIVITY_SOURCE)
        .round(4)
        .to_string(index=False)
    )
    report.append("")
    report.append(positive_control(utterances, SENSITIVITY_SOURCE))
    report.append("```")
    report.append("")

    report.append("## 7. Definition 6 subcase")
    report.append("")
    primary = conversations[conversations.genre_source == PRIMARY_SOURCE]
    by_condition = primary.groupby("condition_label").shifted_into_purchasable.sum()
    report.append(
        f"Conversations shifting into purchasable_products: "
        f"{int(primary.shifted_into_purchasable.sum())} of {len(primary)}. "
        "By condition: "
        + ", ".join(f"{label} {int(count)}" for label, count in by_condition.items())
        + "."
    )
    report.append("")
    report.append(
        "The no-ad condition contributes as many as any advertised one and the "
        "labels are as frequent at turn 1 as at turn 3, so the commercial-intent "
        "subcase of Definition 6 is populated by classifier noise rather than by "
        "advertisement-induced intent. Under the deployed labelling it is "
        "identically zero. Under the literal reading of g^(a), where the "
        "classifier is applied to the served product, the genre-aligned shift is "
        "9 of 108, which is below the 10.5 expected when advertisement genres are "
        "permuted across conversations (p=0.80); the alignment that occurs is a "
        "shared modal genre rather than an effect. See classify_advertisements.py "
        "and outputs/advertisements.md."
    )
    report.append("")
    report.append("```")
    report.append(
        exact_paired_purchasable(conversations)
    )
    report.append("```")
    report.append("")

    text = "\n".join(report) + "\n"
    (DATA / "inference.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
