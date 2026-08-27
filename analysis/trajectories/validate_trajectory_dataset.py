"""Integrity checks for the genre-trajectory Gold (and Silver kernels).

Gold is what analysis reads: utterances, transitions, conversations, and
(once classified) advertisements. Silver ``transition_matrices.csv`` is
checked for consistency with Gold transitions, not as an inferential table.
``classifier_inputs.csv`` is provenance and is not required here.

Every check is an assertion about something that must hold if the ETL is
correct. Exits non-zero on the first failure so this can gate a rebuild.

The checks are grouped by what they protect: coverage (the study is all
there), keys (the tables can be joined), design (the manipulation is intact),
labels (the classifier output is well formed), and agreement (the coarser
tables are consistent with the utterance table they were derived from).

    python analysis/trajectories/validate_trajectory_dataset.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "outputs"
REPOSITORY_ROOT = HERE.parents[1]
EEG_GOLD = REPOSITORY_ROOT / "src/project/logs/xdf/gold/features/condition_features.csv"

EXPECTED_PARTICIPANTS = 54
EXPECTED_ARMS = {"lab": 18, "crowd": 36}
EXPECTED_CONDITIONS = {"no_ads", "inline_early", "inline_late", "block_early", "block_late"}
EXPECTED_AD_TURN = {
    "no_ads": None,
    "inline_early": 2,
    "block_early": 2,
    "inline_late": 4,
    "block_late": 4,
}
GENRE_SOURCES = ("utterance", "contextual")
TURNS = 4
CONVERSATIONS = EXPECTED_PARTICIPANTS * len(EXPECTED_CONDITIONS)

failures: list[str] = []
passes: list[str] = []


def check(condition: bool, message: str) -> None:
    (passes if condition else failures).append(message)


def main() -> int:
    utterances = pd.read_csv(DATA / "utterances.csv")
    conversations = pd.read_csv(DATA / "conversations.csv")
    transitions = pd.read_csv(DATA / "transitions.csv")
    matrices = pd.read_csv(DATA / "transition_matrices.csv")
    # One genre source is the study as it happened; the tables are long, so
    # everything counted per utterance rather than per row uses this view.
    single = utterances[utterances.genre_source == GENRE_SOURCES[0]]

    # ── Coverage ─────────────────────────────────────────────────────────
    check(
        single.participant_id.nunique() == EXPECTED_PARTICIPANTS,
        f"participants = {single.participant_id.nunique()} (expect {EXPECTED_PARTICIPANTS})",
    )
    arms = single.groupby("arm").participant_id.nunique().to_dict()
    check(arms == EXPECTED_ARMS, f"arm split = {arms} (expect {EXPECTED_ARMS})")
    check(
        len(single) == CONVERSATIONS * TURNS,
        f"utterances = {len(single)} (expect {CONVERSATIONS * TURNS})",
    )
    check(
        single.conversation_id.nunique() == CONVERSATIONS,
        f"conversations = {single.conversation_id.nunique()} (expect {CONVERSATIONS})",
    )
    per_participant = single.groupby("participant_id").condition.nunique()
    check(
        set(per_participant.unique()) == {len(EXPECTED_CONDITIONS)},
        f"conditions per participant = {sorted(per_participant.unique())} (expect [5])",
    )
    check(
        set(single.condition.unique()) == EXPECTED_CONDITIONS,
        f"condition names = {sorted(single.condition.unique())}",
    )
    turns = single.groupby("conversation_id").turn.apply(lambda s: sorted(s) == [1, 2, 3, 4])
    check(bool(turns.all()), "every conversation has turns 1,2,3,4 exactly once")

    # ── Keys ─────────────────────────────────────────────────────────────
    # The whole point of the schema: conversation_id is the spine, every table
    # is long on genre_source, and the row keys are unique within a source.
    for name, frame, key in [
        ("utterances", utterances, "utterance_id"),
        ("conversations", conversations, "conversation_id"),
        ("transitions", transitions, "transition_id"),
    ]:
        check(
            not frame.duplicated([key, "genre_source"]).any(),
            f"{name}: ({key}, genre_source) is unique",
        )
        check(
            set(frame.genre_source.unique()) == set(GENRE_SOURCES),
            f"{name}: carries both genre sources",
        )
        check(
            frame.groupby(key).genre_source.nunique().eq(len(GENRE_SOURCES)).all(),
            f"{name}: every {key} appears once per genre source",
        )
        check("conversation_id" in frame.columns, f"{name}: carries conversation_id")

    spine = set(single.conversation_id)
    for name, frame in [("conversations", conversations), ("transitions", transitions)]:
        check(
            set(frame.conversation_id) == spine,
            f"{name}: conversation_id set matches the utterance table",
        )
    check(
        single.groupby(["participant_id", "condition"]).conversation_id.nunique().eq(1).all(),
        "exactly one conversation_id per participant x condition",
    )
    check(
        single.utterance_id.eq(
            single.conversation_id + ":u" + single.turn.astype(str)
        ).all(),
        "utterance_id is conversation_id plus turn",
    )

    # ── Design integrity ─────────────────────────────────────────────────
    for condition, expected in EXPECTED_AD_TURN.items():
        observed = single[single.condition == condition].ad_turn.dropna().unique()
        if expected is None:
            check(len(observed) == 0, f"{condition} carries no ad turn")
        else:
            check(
                set(observed) == {expected},
                f"{condition} ad_turn = {sorted(observed)} (expect {expected})",
            )
    check(
        single.groupby("participant_id").task_id.nunique().eq(5).all(),
        "every participant sees all five tasks exactly once",
    )

    # ── Content and provenance ───────────────────────────────────────────
    check(utterances.text.notna().all(), "no missing utterance text")
    check((utterances.text.astype(str).str.len() > 0).all(), "no empty utterance text")
    check(
        utterances.characters.eq(utterances.text.astype(str).str.len()).all(),
        "character counts match the stored text",
    )
    check(
        single[single.turn > 1].latency_seconds.gt(0).all(),
        "response latency is positive wherever it is defined",
    )
    check(
        single[single.turn == 1].latency_seconds.isna().all(),
        "the opening utterance carries no latency",
    )

    # ── Classifier output ────────────────────────────────────────────────
    posterior_columns = [c for c in utterances.columns if c.startswith("p_")]
    check(len(posterior_columns) == 13, f"{len(posterior_columns)} posterior columns (expect 13)")
    sums = utterances[posterior_columns].sum(axis=1)
    check(
        bool(((sums - 1.0).abs() < 1e-3).all()),
        f"posteriors sum to 1 (max deviation {abs(sums - 1).max():.2e})",
    )
    argmax = utterances[posterior_columns].idxmax(axis=1).str.removeprefix("p_")
    check(bool(argmax.eq(utterances.genre).all()), "stored label equals the posterior argmax")
    check(
        bool(utterances[posterior_columns].max(axis=1).round(6).eq(utterances.top_probability).all()),
        "top_probability equals the largest posterior",
    )
    contextual = utterances[utterances.genre_source == "contextual"]
    check(
        bool(contextual.matches_runtime.eq(1).all()),
        "contextual labels reproduce the logged runtime labels on every row",
    )

    # ── Agreement between grains ─────────────────────────────────────────
    # The coarser tables are derived, so they must be reproducible from the
    # utterance table. This is what makes storing them safe.
    for source in GENRE_SOURCES:
        turn_level = utterances[utterances.genre_source == source]
        frame = conversations[conversations.genre_source == source].set_index("conversation_id")
        moves = transitions[transitions.genre_source == source]

        check(len(frame) == CONVERSATIONS, f"{source}: {len(frame)} conversations (expect 270)")
        check(
            len(moves) == CONVERSATIONS * (TURNS - 1),
            f"{source}: {len(moves)} transitions (expect 810)",
        )

        sequence = turn_level.sort_values("turn").groupby("conversation_id").genre
        check(
            bool(frame.trajectory.eq(sequence.agg("|".join)).all()),
            f"{source}: trajectory string matches the utterance genres",
        )
        check(
            bool(frame.diversity.eq(sequence.nunique()).all()),
            f"{source}: diversity matches the utterance genres",
        )
        check(
            bool(frame.n_shift.eq(turn_level.groupby("conversation_id").delta_in.sum()).all()),
            f"{source}: n_shift matches the sum of incoming shifts",
        )

        # The transition riding on utterance k is transition k-1.
        joined = turn_level[turn_level.turn > 1].merge(
            moves, on=["conversation_id", "genre_source"], suffixes=("", "_t")
        )
        joined = joined[joined.turn - 1 == joined.k]
        check(
            len(joined) == CONVERSATIONS * (TURNS - 1),
            f"{source}: every transition matches exactly one utterance",
        )
        check(bool(joined.delta_in.eq(joined.delta).all()), f"{source}: delta_in matches delta")
        check(
            bool((joined.js_in - joined.js_divergence).abs().lt(1e-9).all()),
            f"{source}: js_in matches the transition divergence",
        )
        check(
            bool(joined.position_in.eq(joined.position).all()),
            f"{source}: position_in matches the transition position",
        )
        check(
            bool(joined.from_genre.eq(joined.from_genre_t).all()),
            f"{source}: from_genre matches the transition source genre",
        )

        check(
            bool(moves.delta.eq(moves.from_genre.ne(moves.to_genre).astype(int)).all()),
            f"{source}: delta matches from/to genres",
        )
        check(
            bool(moves.js_divergence.between(0, math.log(2) + 1e-9).all()),
            f"{source}: Jensen-Shannon divergence within [0, ln 2]",
        )
        check(
            bool(frame.max_persistence.between(1, TURNS).all()),
            f"{source}: persistence within [1, 4]",
        )
        check(
            bool(frame.entropy_nats.between(0, math.log(TURNS) + 1e-9).all()),
            f"{source}: entropy within [0, ln 4]",
        )
        # An advertisement at the final turn has no following utterance.
        check(
            bool(frame[frame.ad_turn == TURNS].ad_associated_shift.isna().all()),
            f"{source}: ad-associated shift undefined for turn-4 advertisements",
        )
        crossing = moves[moves.position == "crosses_ad"].set_index("conversation_id").delta
        early = frame[frame.ad_turn == 2]
        check(
            bool(early.ad_associated_shift.eq(crossing.reindex(early.index)).all()),
            f"{source}: ad-associated shift equals the crossing transition",
        )
        # Late conditions cannot have a transition after the advertisement.
        check(
            bool(moves[moves.ad_turn == TURNS].position.eq("pre_ad").all()),
            f"{source}: every late-condition transition is pre-advertisement",
        )

    # ── Transition matrices ──────────────────────────────────────────────
    totals = matrices.groupby(["genre_source", "facet_kind", "facet", "from_genre"]).probability.sum()
    check(
        bool((totals - 1.0).abs().lt(1e-4).all()),
        f"matrix rows normalise to 1 (max deviation {(totals - 1).abs().max():.1e})",
    )
    for kind in ("all", "ad_presence", "condition"):
        counted = matrices[matrices.facet_kind == kind].groupby("genre_source")["count"].sum()
        check(
            bool(counted.eq(CONVERSATIONS * (TURNS - 1)).all()),
            f"matrix facet '{kind}' accounts for all 810 transitions per source",
        )
    edges = matrices[matrices.facet_kind == "all"].groupby("genre_source").size()
    observed = transitions.groupby("genre_source").apply(
        lambda f: len(f.drop_duplicates(["from_genre", "to_genre"])), include_groups=False
    )
    check(bool(edges.eq(observed).all()), "matrix holds exactly the observed genre pairs")

    # ── Join key against the EEG gold table ──────────────────────────────
    if EEG_GOLD.exists():
        eeg = pd.read_csv(EEG_GOLD)
        lab = single[single.arm == "lab"]
        shared = set(lab.experiment_id) & set(eeg.experiment_id)
        check(
            len(shared) == lab.experiment_id.nunique(),
            f"all {lab.experiment_id.nunique()} lab experiment_ids join to EEG gold "
            f"({len(shared)} matched)",
        )

    for message in passes:
        print(f"  ok    {message}")
    for message in failures:
        print(f"  FAIL  {message}")
    print()
    print(f"{len(passes)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
