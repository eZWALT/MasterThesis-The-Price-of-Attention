"""Sensitivity sweep over how context is fed to the genre classifier.

The live system prepended the task prompt and the last three messages.
That reading is already on Gold as ``contextual`` and it is a stickier
null than the bare utterance. This script asks whether a *different*
context window would have produced an advertisement effect.

Recipes, fixed before looking at p-values:

  bare        Gold ``utterance``. No extra classification.
  deployed    Gold ``contextual``. Task + last 3 + current. No extra pass.
  no_task     Last 3 + current. The task prompt is the suspected glue.
  prev_only   Previous user message + current.
  task_only   Task prompt + current. Isolates the glue.
  opening     The conversation's first user message + current.

Hard labels only. Same confirmatory estimand as family A: crossing
δ^(a) on 2→3, plus McNemar and δ-tilde. Holm is first within a recipe,
then across recipes on the one contrast that would be harvested
(early pooled − no-ad). This is a sensitivity sweep, not a new family A.

    HF_HUB_OFFLINE=1 python3 analysis/trajectories/run_contextual_sweep.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "outputs"
OUT = DATA / "contextual_sweep"
TABLES = OUT / "tables"
sys.path.insert(0, str(HERE))

from analyse_trajectories import (  # noqa: E402
    CONTROL,
    EARLY,
    exact_crossing_table,
    holm,
    paired_test,
    targeted_tests,
)
from build_trajectory_dataset import (  # noqa: E402
    CONTEXT_CURRENT_BUDGET,
    CONTEXT_HISTORY_BUDGET,
    CONTEXT_HISTORY_MESSAGES,
    CONTEXT_TASK_BUDGET,
    GenreClassifier,
)
from classify_advertisements import PERMUTATIONS, SEED  # noqa: E402

RECIPES_FROM_GOLD = {
    "bare": "utterance",
    "deployed": "contextual",
}
NEW_RECIPES = ("no_task", "prev_only", "task_only", "opening")


def recover_task(contextual: str, text: str) -> str:
    needle = text[:80]
    index = contextual.find(needle)
    if index > 0:
        return contextual[:index].strip()
    return ""


def build_input(
    recipe: str,
    classifier: GenreClassifier,
    task: str,
    history: list[str],
    current: str,
    opening: str,
) -> str:
    if recipe == "no_task":
        recent = history[-CONTEXT_HISTORY_MESSAGES:]
        parts = []
        if recent:
            share = CONTEXT_HISTORY_BUDGET // len(recent)
            parts.extend(classifier.truncate(message, share) for message in recent)
        parts.append(classifier.truncate(current, CONTEXT_CURRENT_BUDGET))
        return " ".join(parts)
    if recipe == "prev_only":
        parts = []
        if history:
            parts.append(classifier.truncate(history[-1], CONTEXT_HISTORY_BUDGET))
        parts.append(classifier.truncate(current, CONTEXT_CURRENT_BUDGET))
        return " ".join(parts)
    if recipe == "task_only":
        parts = []
        if task:
            parts.append(classifier.truncate(task, CONTEXT_TASK_BUDGET))
        parts.append(classifier.truncate(current, CONTEXT_CURRENT_BUDGET))
        return " ".join(parts)
    if recipe == "opening":
        parts = []
        if opening and opening != current:
            parts.append(classifier.truncate(opening, CONTEXT_HISTORY_BUDGET))
        parts.append(classifier.truncate(current, CONTEXT_CURRENT_BUDGET))
        return " ".join(parts)
    raise ValueError(recipe)


def classify_new_recipes(utterances: pd.DataFrame, inputs: pd.DataFrame) -> pd.DataFrame:
    bare = utterances[utterances.genre_source == "utterance"].copy()
    first = (
        inputs[inputs.turn == 1]
        .set_index(["experiment_id", "condition"])["classifier_input_contextual"]
    )
    tasks = {}
    for row in bare[bare.turn == 1].itertuples():
        key = (row.experiment_id, row.condition)
        contextual = first.get(key, "")
        tasks[key] = recover_task(str(contextual), row.text) if isinstance(contextual, str) else ""

    recovered = sum(1 for value in tasks.values() if value)
    print(f"recovered task prompts: {recovered}/{len(tasks)}", flush=True)

    classifier = GenreClassifier()
    rows = []
    grouped = list(bare.groupby("conversation_id", sort=False))
    total = len(grouped)
    for index, (conversation_id, block) in enumerate(grouped, start=1):
        block = block.sort_values("turn")
        history: list[str] = []
        opening = block.iloc[0].text
        task = tasks.get((block.iloc[0].experiment_id, block.iloc[0].condition), "")
        for row in block.itertuples():
            for recipe in NEW_RECIPES:
                text = build_input(recipe, classifier, task, history, row.text, opening)
                genre, _ = classifier.classify(text)
                rows.append(
                    {
                        "conversation_id": conversation_id,
                        "participant_id": row.participant_id,
                        "condition_label": row.condition_label,
                        "ad_turn": row.ad_turn,
                        "turn": row.turn,
                        "recipe": recipe,
                        "genre": genre,
                    }
                )
            history.append(row.text)
        if index % 50 == 0 or index == total:
            print(f"classified {index}/{total} conversations", flush=True)
    return pd.DataFrame(rows)


def gold_labels(utterances: pd.DataFrame, recipe: str) -> pd.DataFrame:
    source = RECIPES_FROM_GOLD[recipe]
    frame = utterances[utterances.genre_source == source][
        [
            "conversation_id",
            "participant_id",
            "condition_label",
            "ad_turn",
            "turn",
            "genre",
        ]
    ].copy()
    frame["recipe"] = recipe
    return frame


def labels_to_transitions(labels: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for conversation_id, block in labels.groupby("conversation_id"):
        block = block.sort_values("turn")
        genres = block.genre.tolist()
        meta = block.iloc[0]
        ad_turn = meta.ad_turn
        ad_turn = int(ad_turn) if pd.notna(ad_turn) else None
        for k in (1, 2, 3):
            if ad_turn is None:
                position = "no_ad"
            elif k == ad_turn:
                position = "crosses_ad"
            else:
                position = "post_ad" if k > ad_turn else "pre_ad"
            rows.append(
                {
                    "conversation_id": conversation_id,
                    "participant_id": meta.participant_id,
                    "condition_label": meta.condition_label,
                    "genre_source": meta.recipe,
                    "k": k,
                    "from_genre": genres[k - 1],
                    "to_genre": genres[k],
                    "delta": int(genres[k] != genres[k - 1]),
                    "ad_turn": ad_turn if ad_turn is not None else np.nan,
                    "position": position,
                }
            )
    return pd.DataFrame(rows)


def conversation_stats(labels: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for conversation_id, block in labels.groupby("conversation_id"):
        block = block.sort_values("turn")
        genres = block.genre.tolist()
        n_shift = sum(a != b for a, b in zip(genres, genres[1:]))
        rows.append(
            {
                "conversation_id": conversation_id,
                "participant_id": block.iloc[0].participant_id,
                "condition_label": block.iloc[0].condition_label,
                "n_shift": n_shift,
                "diversity": len(set(genres)),
                "sticky": int(len(set(genres)) == 1),
            }
        )
    return pd.DataFrame(rows)


def tilde_row(labels: pd.DataFrame, ads: pd.DataFrame) -> dict:
    early = labels[labels.ad_turn == 2].copy()
    wide = early.pivot(index="conversation_id", columns="turn", values="genre")
    wide = wide.join(ads.set_index("conversation_id")["ad_genre"])
    wide = wide.dropna(subset=["ad_genre", 2, 3])
    shifted = wide[2] != wide[3]
    aligned = wide[3] == wide.ad_genre
    tilde = (shifted & aligned).astype(int)
    already = (wide[2] == wide.ad_genre).astype(int)
    observed = int(tilde.sum())
    rng = np.random.default_rng(SEED)
    genres = wide.ad_genre.to_numpy()
    following = wide[3].to_numpy()
    shift = shifted.to_numpy()
    null = np.empty(PERMUTATIONS, dtype=int)
    for i in range(PERMUTATIONS):
        null[i] = ((following == rng.permutation(genres)) & shift).sum()
    return {
        "n_early": len(wide),
        "n_shift_crossing": int(shifted.sum()),
        "already": int(already.sum()),
        "delta_tilde": observed,
        "chance": float(null.mean()),
        "p_perm": float((null >= observed).mean()),
        "distinct_genres": labels.genre.nunique(),
    }


def markdown(frame: pd.DataFrame) -> str:
    return frame.to_markdown(index=False)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)

    utterances = pd.read_csv(DATA / "utterances.csv")
    ads = pd.read_csv(DATA / "advertisements.csv")
    inputs = pd.read_csv(DATA / "classifier_inputs.csv")

    parts = [gold_labels(utterances, recipe) for recipe in RECIPES_FROM_GOLD]
    print("classifying new context windows (ThradBERT, offline)...", flush=True)
    parts.append(classify_new_recipes(utterances, inputs))
    labels = pd.concat(parts, ignore_index=True)
    labels.to_csv(TABLES / "labels.csv", index=False)

    crossing_rows = []
    mcnemar_rows = []
    summary_rows = []
    for recipe, block in labels.groupby("recipe", sort=False):
        transitions = labels_to_transitions(block)
        hard = targeted_tests(transitions, "delta", recipe)
        hard.insert(0, "recipe", recipe)
        crossing_rows.append(hard)
        exact = exact_crossing_table(transitions, recipe)
        exact.insert(0, "recipe", recipe)
        mcnemar_rows.append(exact)

        conv = conversation_stats(block)
        tilde = tilde_row(block, ads)
        pooled = hard.set_index("contrast").loc["early ads pooled - no ad"]
        implicit = exact.set_index("contrast").loc["implicit early - no ad"]
        summary_rows.append(
            {
                "recipe": recipe,
                "distinct_genres": tilde["distinct_genres"],
                "mean_n_shift": float(conv.n_shift.mean()),
                "share_sticky": float(conv.sticky.mean()),
                "crossing_delta": float(pooled["mean"]),
                "p_t": float(pooled["p_t"]),
                "p_holm_within": float(pooled["p_holm"]),
                "mcnemar_only_t": int(implicit.only_treatment),
                "mcnemar_only_c": int(implicit.only_control),
                "p_mcnemar": float(implicit.p_exact),
                "delta_tilde": tilde["delta_tilde"],
                "tilde_chance": tilde["chance"],
                "p_tilde": tilde["p_perm"],
                "already_in_ad_genre": tilde["already"],
            }
        )

    crossing = pd.concat(crossing_rows, ignore_index=True)
    mcnemar = pd.concat(mcnemar_rows, ignore_index=True)
    summary = pd.DataFrame(summary_rows)
    order = ["bare", "deployed", "no_task", "prev_only", "task_only", "opening"]
    summary["recipe"] = pd.Categorical(summary.recipe, order, ordered=True)
    summary = summary.sort_values("recipe").reset_index(drop=True)
    summary["p_holm_across_recipes"] = holm(summary.p_t.tolist())

    crossing.to_csv(TABLES / "crossing_hard.csv", index=False)
    mcnemar.to_csv(TABLES / "mcnemar.csv", index=False)
    summary.to_csv(TABLES / "summary.csv", index=False)

    lines = [
        "# Contextual labelling sweep",
        "",
        "Hard labels only. Same crossing estimand as family A.",
        "``bare`` and ``deployed`` are the Gold readings. The other four are",
        "new ThradBERT passes. Holm-within is the four contrasts inside a",
        "recipe. Holm-across is the six early-pooled p-values, the thing a",
        "reader would harvest.",
        "",
        markdown(summary.round(4)),
        "",
        "## Crossing δ, every contrast",
        "",
        markdown(crossing.round(4)),
        "",
        "## McNemar",
        "",
        markdown(mcnemar.round(4)),
        "",
    ]
    report = "\n".join(lines)
    (OUT / "contextual_sweep.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote {OUT / 'contextual_sweep.md'}")


if __name__ == "__main__":
    main()
