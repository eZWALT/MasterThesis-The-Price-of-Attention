#!/usr/bin/env python3
"""Build the public Price of Attention dataset.

Ships anonymous analysis tables only. Conversation text, raw EEG,
Prolific identifiers, session folders, and absolute timestamps are
dropped. Join keys are remapped with a salt that stays on this machine.

Does not read analysis/behavioural/ (not Gold) and does not touch ICA
models or XDF recordings.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import json
import os
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = Path("/home/wtroi/MasterThesis-RAG-RecSys")
SALT_PATH = Path.home() / ".config" / "price-of-attention" / "id-salt"
MAP_PATH = Path.home() / ".config" / "price-of-attention" / "id-map.json"

DROP_COLUMNS = {
    "participant_id",
    "subject_id",
    "folder",
    "unix_ts",
    "timestamp",
    "text",
    "conclusion",
    "recall_reaction",
    "classifier_input_contextual",
    "demo_age",
    "demo_occupation",
    "window_id",
    "reference_id",
    "source_xdf",
    "source_xdf_sha256",
    "source_log",
    "source_file",
    "source_canonical_markers",
    "unfocused",
}

# Product titles and task names are part of the manipulation, not chat text.
ALLOW_LONG = {
    "ad_title",
    "task_title",
    "trajectory",
    "condition_label",
    "condition",
    "exclusion_reason",
    "artifact_rejection_reason",
    "artifact_policy_status",
    "onset_status",
    "onset_estimator",
    "reference_kind",
    "window_type",
    "genre",
    "from_genre",
    "to_genre",
    "feature",
    "feature_tier",
    "contrast_id",
    "contrast",
    "label",
    "task_genre",
    "task_id",
    "ad_id",
    "traj_ad_title",
    "traj_trajectory",
    "ad_genre",
    "genre_source",
    "presentation",
    "timing",
    "arm",
    "role",
    "ad_mode",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")

# config name -> source csv. Order is the card order.
TABLES: list[tuple[str, Path, str]] = [
    (
        "behavioural_chat",
        ROOT / "analysis/walter/behavioural/outputs/gold/condition_features.csv",
        "One row per participant and condition. Likert outcomes, process lengths, and the served advertisement. N = 54, five conditions.",
    ),
    (
        "behavioural_advertisements",
        ROOT / "analysis/walter/behavioural/outputs/gold/advertisement_features.csv",
        "One row per served advertisement (216). Same ratings as the chat table, plus recall items. No free-text reaction.",
    ),
    (
        "behavioural_person",
        ROOT / "analysis/walter/behavioural/outputs/gold/person_features.csv",
        "One row per participant. BFI-10 and the demographics that are not identifying on the laboratory arm.",
    ),
    (
        "behavioural_contrasts",
        ROOT / "analysis/walter/behavioural/outputs/gold/contrast_scores.csv",
        "One row per participant. Planned difference scores (any advertisement minus control, explicit minus implicit, early minus late).",
    ),
    (
        "behavioural_messages",
        ROOT / "analysis/walter/behavioural/outputs/gold/messages.csv",
        "One row per message. Lengths and latencies only. No text and no clock time.",
    ),
    (
        "trajectories_chat",
        ROOT / "analysis/trajectories/outputs/conversations.csv",
        "One row per conversation and genre context. Shift counts and divergences. Filter genre_source to utterance before comparing with the thesis.",
    ),
    (
        "trajectories_utterances",
        ROOT / "analysis/trajectories/outputs/utterances.csv",
        "One row per utterance and genre context. Genre label and probabilities. The utterance text is not included.",
    ),
    (
        "trajectories_transitions",
        ROOT / "analysis/trajectories/outputs/transitions.csv",
        "One row per adjacent turn pair and genre context.",
    ),
    (
        "trajectories_advertisements",
        ROOT / "analysis/trajectories/outputs/advertisements.csv",
        "Genre assigned to each served advertisement.",
    ),
    (
        "eeg_dataset_a_k37",
        ROOT
        / "analysis/eeg/statistics/outputs/sensitivity/ad_local_epochs/dataset_a/around/k37/condition_features.csv",
        "Confirmatory Dataset A: condition aggregation, k = 37 equal-n epochs, n = 18. This is the reported Dataset A, not the whole-window median.",
    ),
    (
        "eeg_dataset_a_whole_window",
        ROOT / "src/project/logs/xdf/gold/features/condition_features.csv",
        "Whole-window condition summary. Stored so the sensitivity can be reproduced. Not the confirmatory Dataset A.",
    ),
    (
        "eeg_dataset_b_onset",
        ROOT / "src/project/logs/xdf/gold/features/ad_response_features.csv",
        "Dataset B feature table: post-minus-pre band power at advertisement onset versus a turn-matched control reply. Primary epoch is 4 seconds.",
    ),
    (
        "eeg_condition_scores",
        ROOT / "analysis/eeg/statistics/outputs/eeg_condition_contrast_scores.csv",
        "Participant-level Dataset A contrasts. Join to behavioural_contrasts on experiment_id.",
    ),
    (
        "eeg_onset_scores",
        ROOT / "analysis/eeg/statistics/outputs/eeg_ad_response_contrast_scores.csv",
        "Participant-level Dataset B contrasts. The trust association uses contrast_id any_ad_vs_matched_no_ad and feature posterior_alpha_power_db_uv2.",
    ),
    (
        "eeg_write_read",
        ROOT / "analysis/eeg/statistics/outputs/task_state/eeg_task_state_contrast_scores.csv",
        "Write-minus-read positive control. Frontal theta separates message writing from reply reading.",
    ),
    (
        "joins_chat",
        ROOT / "analysis/walter/behavioural/outputs/gold/combo_threeway.csv",
        "Chat-grain join of behaviour, trajectories, and EEG. Both arms. EEG columns are empty on the crowd arm.",
    ),
    (
        "joins_person",
        ROOT / "analysis/walter/behavioural/outputs/gold/combo_threeway_D.csv",
        "Person-grain planned contrasts, joined. The condition-aggregated trust and posterior alpha association (rho about .24) is in this table.",
    ),
    (
        "joins_chat_lab",
        ROOT / "analysis/walter/behavioural/outputs/gold/combo_threeway_lab.csv",
        "Chat-grain join restricted to the laboratory arm (n = 18).",
    ),
    (
        "joins_person_lab",
        ROOT / "analysis/walter/behavioural/outputs/gold/combo_threeway_lab_D.csv",
        "Person-grain join restricted to the laboratory arm.",
    ),
    (
        "eeg_onset_by_condition",
        ROOT / "analysis/walter/combos/outputs/events/events_joined.csv",
        "Laboratory onset-locked EEG joined to the behavioural ratings of the same condition. Four advertisement conditions, 18 participants.",
    ),
]

RESULT_FILES = [
    ROOT / "analysis/walter/behavioural/outputs/confirmatory" / name
    for name in [
        "confirmatory_planned_D.csv",
        "planned_t_vs_lmm.csv",
        "posthoc_vs_control.csv",
        "omnibus_pairwise.csv",
        "omnibus_friedman.csv",
        "personality_lmm.csv",
        "personality_d_ols.csv",
        "lmm_declared.csv",
        "cronbach_alpha.csv",
    ]
] + [
    ROOT / "analysis/eeg/statistics/outputs/eeg_condition_contrasts.csv",
    ROOT / "analysis/eeg/statistics/outputs/eeg_condition_descriptives.csv",
    ROOT / "analysis/eeg/statistics/outputs/eeg_ad_response_contrasts.csv",
    ROOT / "analysis/eeg/statistics/outputs/task_state/eeg_task_state_contrasts.csv",
    ROOT / "analysis/walter/combos/outputs/thesis/declared_families.csv",
]

PAPER_FIGURES = [
    ("beh_item_forest", "Planned behavioural contrasts. Orange marks a Holm-adjusted paired t below .05."),
    ("beh_localisation_forest", "Each advertisement condition against the control."),
    ("beh_notice_percentages", "Who reported the reply as sponsored."),
    ("eeg_confirmatory_forests", "Confirmatory EEG. Dataset A is condition aggregation. Dataset B is onset-locked."),
    ("combos_trust_alpha", "Trust against onset-locked posterior alpha (n = 18)."),
    ("eeg_holm_board_4s", "Which EEG comparisons survive Holm adjustment."),
    ("beh_holm_board", "Which behavioural comparisons survive Holm adjustment."),
    ("sample_demographics", "Who took part."),
]


def load_salt() -> bytes:
    if SALT_PATH.exists():
        return SALT_PATH.read_bytes()
    SALT_PATH.parent.mkdir(parents=True, exist_ok=True)
    salt = os.urandom(32)
    SALT_PATH.write_bytes(salt)
    os.chmod(SALT_PATH, 0o600)
    return salt


def public_id(salt: bytes, kind: str, raw: str) -> str:
    digest = hmac.new(salt, f"{kind}\n{raw}".encode(), hashlib.sha256).hexdigest()
    prefix = {"experiment": "e", "conversation": "c", "utterance": "u", "transition": "t"}[kind]
    return f"{prefix}_{digest[:10]}"


def collect_ids(salt: bytes) -> dict[str, dict[str, str]]:
    experiments: set[str] = set()
    subjects: dict[str, str] = {}
    conversations: set[str] = set()
    utterances: set[str] = set()
    transitions: set[str] = set()
    participants: set[str] = set()
    folders: set[str] = set()

    id_map = ROOT / "analysis/walter/behavioural/outputs/gold/id_map.csv"
    for row in csv.DictReader(id_map.open()):
        experiments.add(row["experiment_id"])
        subjects[row["subject_id"]] = row["experiment_id"]
        if row["folder"]:
            subjects.setdefault(row["folder"], row["experiment_id"])
            folders.add(row["folder"])
        if row["participant_id"]:
            participants.add(row["participant_id"])

    for _, path, _ in TABLES:
        with path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("experiment_id"):
                    experiments.add(row["experiment_id"])
                if row.get("person"):
                    experiments.add(row["person"])
                if row.get("participant_id"):
                    participants.add(row["participant_id"])
                if row.get("folder"):
                    folders.add(row["folder"])
                if row.get("subject_id") and row.get("experiment_id"):
                    subjects[row["subject_id"]] = row["experiment_id"]
                if row.get("conversation_id"):
                    conversations.add(row["conversation_id"])
                if row.get("traj_conversation_id"):
                    conversations.add(row["traj_conversation_id"])
                if row.get("utterance_id"):
                    utterances.add(row["utterance_id"])
                if row.get("transition_id"):
                    transitions.add(row["transition_id"])

    missing = [s for s in subjects if not subjects[s]]
    if missing:
        raise SystemExit(f"{len(missing)} subject ids have no experiment id")

    maps = {
        "experiment": {raw: public_id(salt, "experiment", raw) for raw in experiments},
        "subject": {
            raw: public_id(salt, "experiment", exp) for raw, exp in subjects.items()
        },
        "conversation": {raw: public_id(salt, "conversation", raw) for raw in conversations},
        "utterance": {raw: public_id(salt, "utterance", raw) for raw in utterances},
        "transition": {raw: public_id(salt, "transition", raw) for raw in transitions},
    }
    # The salt is enough to rebuild public ids. Do not write the raw ids here.
    MAP_PATH.write_text(
        json.dumps({"local_only": True, "n_experiment": len(maps["experiment"])})
    )
    os.chmod(MAP_PATH, 0o600)
    maps["_private_sets"] = {
        "participant": participants,
        "folder": folders,
        "experiment": experiments,
        "subject": set(subjects),
        "conversation": conversations,
        "utterance": utterances,
        "transition": transitions,
    }
    return maps


def is_text(series: pd.Series) -> bool:
    return pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)


def remap_frame(frame: pd.DataFrame, maps: dict) -> tuple[pd.DataFrame, list[str]]:
    notes: list[str] = []
    frame = frame.copy()
    # Score tables are keyed by subject_id only. Swap in the public
    # experiment id before the subject column is deleted.
    if "subject_id" in frame.columns and "experiment_id" not in frame.columns:
        unknown = sorted(
            {
                value
                for value in frame["subject_id"].dropna().astype(str).unique()
                if value not in maps["subject"]
            }
        )
        if unknown:
            raise SystemExit(f"{len(unknown)} subject ids have no public experiment id")
        frame.insert(0, "experiment_id", frame["subject_id"].map(maps["subject"]))
        notes.append("subject_id replaced by experiment_id")

    drop = []
    for column in frame.columns:
        if (
            column in DROP_COLUMNS
            or column.startswith("source_")
            or column.endswith("_sha256")
        ):
            drop.append(column)
    if drop:
        frame = frame.drop(columns=drop)
        notes.append("dropped " + ", ".join(drop))

    if "subject_id" in frame.columns:
        raise SystemExit("subject_id survived the drop list")

    def remap_value(value: object) -> object:
        if not isinstance(value, str) or value == "":
            return value
        for key in ("experiment", "subject", "conversation", "utterance", "transition"):
            mapped = maps[key].get(value)
            if mapped is not None:
                return mapped
        return value

    for column in frame.columns:
        if is_text(frame[column]):
            frame[column] = frame[column].map(remap_value)

    long_dropped = []
    for column in list(frame.columns):
        if not is_text(frame[column]) or column in ALLOW_LONG:
            continue
        lengths = frame[column].dropna().astype(str).map(len)
        if len(lengths) and int(lengths.max()) > 80:
            long_dropped.append(column)
    if long_dropped:
        frame = frame.drop(columns=long_dropped)
        notes.append("dropped long text " + ", ".join(long_dropped))

    dated = []
    for column in list(frame.columns):
        if not is_text(frame[column]):
            continue
        series = frame[column].dropna().astype(str)
        if len(series) and series.map(lambda v: bool(DATE_RE.match(v))).mean() > 0.5:
            dated.append(column)
    if dated:
        frame = frame.drop(columns=dated)
        notes.append("dropped clocks " + ", ".join(dated))

    empty = [c for c in frame.columns if frame[c].isna().all() or (frame[c].astype(str).str.strip() == "").all()]
    if empty:
        frame = frame.drop(columns=empty)
        notes.append("dropped empty " + ", ".join(empty))
    return frame, notes


def assert_clean(frame: pd.DataFrame, maps: dict, name: str) -> None:
    private = maps["_private_sets"]
    banned_exact: set[str] = set()
    for key in ("participant", "folder", "experiment", "subject", "conversation", "utterance", "transition"):
        banned_exact |= {v for v in private[key] if v}
    banned_sub = {v for v in banned_exact if len(v) >= 12}
    for column in frame.columns:
        if column in DROP_COLUMNS or column.startswith("source_"):
            raise SystemExit(f"{name} still has column {column}")
        if not is_text(frame[column]):
            continue
        for value in frame[column].dropna().astype(str).unique():
            if value in banned_exact:
                raise SystemExit(f"{name}.{column} still contains a private identifier")
            if ".xdf" in value or "/logs/" in value:
                raise SystemExit(f"{name}.{column} still contains a recording path")
            if DATE_RE.match(value):
                raise SystemExit(f"{name}.{column} still contains a calendar timestamp")
            for secret in banned_sub:
                if secret in value:
                    raise SystemExit(f"{name}.{column} embeds a private identifier")


def spearman(xs: list[float], ys: list[float]) -> float:
    def rank(values: list[float]) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: values[i])
        ranks = [0.0] * len(values)
        i = 0
        while i < len(values):
            j = i
            while j + 1 < len(values) and values[order[j + 1]] == values[order[i]]:
                j += 1
            average = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[order[k]] = average
            i = j + 1
        return ranks

    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = sum((v - mx) ** 2 for v in rx) ** 0.5
    dy = sum((v - my) ** 2 for v in ry) ** 0.5
    return num / (dx * dy)


def headline_numbers(frames: dict[str, pd.DataFrame]) -> dict[str, float]:
    contrasts = frames["behavioural_contrasts"]
    manip = contrasts["manipulation__any_ad_vs_no_ads"].dropna().astype(float)
    notice = contrasts["notice__any_ad_vs_no_ads"].dropna().astype(float)
    cred = contrasts["credibility__early_vs_late"].dropna().astype(float)
    ads = frames["behavioural_advertisements"]
    recall_wide = ads.pivot_table(
        index="experiment_id", columns="timing", values="recall_trust_shift"
    )
    recall_trust = (recall_wide["early"] - recall_wide["late"]).dropna()
    lab = frames["joins_person_lab"]
    a_rho = spearman(
        lab["trust__any_ad_vs_no_ads"].astype(float).tolist(),
        lab["eeg_posterior_alpha__any_ad_vs_no_ads"].astype(float).tolist(),
    )
    onset = frames["eeg_onset_scores"]
    alpha = onset[
        (onset["contrast_id"] == "any_ad_vs_matched_no_ad")
        & (onset["feature"] == "posterior_alpha_power_db_uv2")
    ][["experiment_id", "difference"]].rename(columns={"difference": "alpha"})
    beh = contrasts.loc[contrasts["arm"] == "lab", ["experiment_id", "trust__any_ad_vs_no_ads"]]
    joined = beh.merge(alpha, on="experiment_id")
    b_rho = spearman(
        joined["trust__any_ad_vs_no_ads"].astype(float).tolist(),
        joined["alpha"].astype(float).tolist(),
    )
    numbers = {
        "n_people": float(contrasts["experiment_id"].nunique()),
        "manipulation_mean": float(manip.mean()),
        "notice_mean": float(notice.mean()),
        "credibility_early_late": float(cred.mean()),
        "trust_reexposure_early_late": float(recall_trust.mean()),
        "rho_dataset_a": float(a_rho),
        "rho_dataset_b": float(b_rho),
        "rho_dataset_b_n": float(len(joined)),
    }
    if abs(numbers["manipulation_mean"] - 1.271) > 0.01:
        raise SystemExit(f"manipulation mean drifted: {numbers['manipulation_mean']}")
    if abs(numbers["rho_dataset_b"] - 0.803) > 0.01:
        raise SystemExit(f"dataset B rho drifted: {numbers['rho_dataset_b']}")
    if abs(numbers["trust_reexposure_early_late"] + 0.491) > 0.01:
        raise SystemExit(
            f"re-exposure trust drifted: {numbers['trust_reexposure_early_late']}"
        )
    if abs(numbers["rho_dataset_a"] - 0.237) > 0.02:
        raise SystemExit(f"dataset A rho drifted: {numbers['rho_dataset_a']}")
    return numbers


def render_figures(out: Path) -> None:
    figures = out / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    render_hero(figures / "hero.png")
    render_design(figures / "design.png")
    render_banner(figures / "banner.png")
    shutil.copy(
        ROOT / "docs/overleaf/publication/Figures/laboratory-protocol.png",
        figures / "protocol.png",
    )
    src = ROOT / "docs/overleaf/publication/Figures/results"
    for stem, _caption in PAPER_FIGURES:
        pdf = src / f"{stem}.pdf"
        if not pdf.exists():
            raise SystemExit(f"missing figure {pdf}")
        subprocess.run(
            ["pdftocairo", "-png", "-r", "140", "-singlefile", str(pdf), str(figures / stem)],
            check=True,
        )


def render_hero(path: Path) -> None:
    fig = plt.figure(figsize=(16, 8.2), dpi=140, facecolor="#0E1420")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8.2)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 16, 8.2, boxstyle="square,pad=0", linewidth=0, facecolor="#0E1420"))
    ax.plot([0.7, 3.1], [7.35, 7.35], color="#E4B15A", lw=3, solid_capstyle="round")
    ax.text(0.7, 6.85, "A PUBLIC RESEARCH DATASET", color="#E4B15A", fontsize=13, fontfamily="DejaVu Sans")
    ax.text(0.65, 5.85, "The Price of Attention", color="#F4EFE6", fontsize=42, fontweight="bold", fontfamily="DejaVu Sans")
    ax.text(
        0.68,
        5.15,
        "What an advertisement costs the person using a conversational assistant.",
        color="#C9D2E3",
        fontsize=16,
        fontfamily="DejaVu Sans",
    )
    chips = [
        ("54", "people, five conditions\neach, within person"),
        ("+1.27", "felt manipulation\non a 1–7 scale"),
        ("18", "of them recorded\nwith 32-channel EEG"),
        ("0.80", "trust tracks onset\nposterior alpha"),
    ]
    for i, (big, small) in enumerate(chips):
        x = 0.7 + i * 3.8
        ax.add_patch(
            FancyBboxPatch(
                (x, 1.15),
                3.45,
                2.55,
                boxstyle="round,pad=0.04,rounding_size=0.12",
                linewidth=0,
                facecolor="#172033",
            )
        )
        ax.text(x + 0.28, 2.55, big, color="#E4B15A", fontsize=32, fontweight="bold", fontfamily="DejaVu Sans")
        ax.text(x + 0.28, 1.45, small, color="#F4EFE6", fontsize=12, fontfamily="DejaVu Sans", va="bottom")
    ax.text(
        0.7,
        0.45,
        "Anonymous analysis tables  ·  no chat text  ·  no raw EEG  ·  Troiani, Lymperidou, Idesis, Arapakis  ·  2026",
        color="#8B97AD",
        fontsize=11,
        fontfamily="DejaVu Sans",
    )
    fig.savefig(path, dpi=140)
    plt.close(fig)


def render_design(path: Path) -> None:
    fig = plt.figure(figsize=(16, 4.6), dpi=140, facecolor="#F7F4EE")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    ax.text(0.55, 4.15, "Five conditions, same person", color="#1C2430", fontsize=20, fontweight="bold", fontfamily="DejaVu Sans")
    ax.text(0.55, 3.65, "A retrieval assistant, multi-turn tasks, advertisement format crossed with insertion timing.", color="#5C677A", fontsize=12, fontfamily="DejaVu Sans")
    cards = [
        ("Control", "No advertisement", "#E7E2D8"),
        ("Mention", "Early in the chat", "#D9E6F2"),
        ("Mention", "Late in the chat", "#D9E6F2"),
        ("Banner", "Early in the chat", "#F3D7C4"),
        ("Banner", "Late in the chat", "#F3D7C4"),
    ]
    for i, (title, sub, fill) in enumerate(cards):
        x = 0.5 + i * 3.1
        ax.add_patch(FancyBboxPatch((x, 0.85), 2.85, 2.5, boxstyle="round,pad=0.02,rounding_size=0.1", linewidth=0, facecolor=fill))
        ax.text(x + 0.22, 2.55, title, color="#1C2430", fontsize=16, fontweight="bold", fontfamily="DejaVu Sans")
        ax.text(x + 0.22, 2.05, sub, color="#5C677A", fontsize=12, fontfamily="DejaVu Sans")
        ax.text(x + 0.22, 1.15, f"0{i + 1}", color="#C48A2A", fontsize=16, fontweight="bold", fontfamily="DejaVu Sans")
    ax.text(0.55, 0.35, "36 people online   ·   18 people in the laboratory with EEG   ·   order randomised", color="#5C677A", fontsize=12, fontfamily="DejaVu Sans")
    fig.savefig(path, dpi=140)
    plt.close(fig)


def write_readme(out: Path, frames: dict[str, pd.DataFrame], numbers: dict[str, float], descriptions: dict[str, str]) -> None:
    def schema_block(name: str) -> str:
        frame = frames[name]
        lines = ["| column | dtype |", "|---|---|"]
        for column, dtype in frame.dtypes.items():
            kind = "number" if pd.api.types.is_numeric_dtype(dtype) else "string"
            lines.append(f"| `{column}` | {kind} |")
        shown = lines[:12]
        if len(lines) > 12:
            shown.append(f"| … | {len(frame.columns) - 10} columns in total |")
        return "\n".join(shown)

    config_rows = []
    yaml_configs = []
    first = True
    for name, _, blurb in TABLES:
        frame = frames[name]
        config_rows.append(
            f"| `{name}` | {len(frame):,} | {frame.shape[1]} | {blurb} |"
        )
        entry = {
            "config_name": name,
            "data_files": [{"split": "train", "path": f"data/{name}.parquet"}],
        }
        if first:
            entry["default"] = True
            first = False
        yaml_configs.append(entry)

    figure_md = []
    for stem, caption in PAPER_FIGURES:
        figure_md.append(f"![{caption}](figures/{stem}.png)\n\n*{caption}*\n")

    readme = f"""---
license: cc-by-4.0
language:
- en
pretty_name: The Price of Attention
size_categories:
- 1K<n<10K
task_categories:
- other
tags:
- conversational-ai
- advertising
- trust
- eeg
- neuroscience
- human-ai-interaction
- psychology
annotations_creators:
- expert-generated
language_creators:
- crowdsourced
- expert-generated
multilinguality:
- monolingual
source_datasets:
- original
configs:
{yaml_dump_configs(yaml_configs)}
---

# The Price of Attention

![The Price of Attention](figures/hero.png)

Advertising inside an LLM assistant is usually scored by whether the product is noticed or clicked. This dataset scores it by what it costs the person on the other side of the chat: felt manipulation, trust, credibility, memory, and the EEG that sits underneath.

**54 people** each completed five conditions with a retrieval assistant: an implicit mention or an explicit banner, placed early or late, plus an advertisement-free control. **18 of them** were recorded with 32-channel EEG. The tables here are the ones the paper's tests were computed from.

## Load it

```python
from datasets import load_dataset

ratings = load_dataset("eZWALT/price-of-attention", "behavioural_chat", split="train")
contrasts = load_dataset("eZWALT/price-of-attention", "behavioural_contrasts", split="train")
print(ratings.to_pandas()["manipulation"].mean())
```

Or with pandas, from the parquet files in [`data/`](data).

## The experiment

![Laboratory protocol](figures/protocol.png)

*Laboratory session. The remote arm uses the same condition loop and the same questionnaires, without EEG.*

![Five conditions](figures/design.png)

![Explicit banner](figures/banner.png)

*The explicit format, as shown in the interface: a separate panel marked Advertisement, with the product title and a call to action. The implicit format is the same product woven into the assistant's reply, without that panel.*

Every person saw every condition, in random order. A mention is a product woven into the assistant's reply. A banner is a separate sponsored unit. Early and late are two positions in the same multi-turn task. The control is the same task with no advertisement.

Outcomes are on seven-point scales. The planned contrasts are three differences per person:

- any advertisement minus the control
- explicit banner minus implicit mention
- early insertion minus late insertion

EEG has two estimands, and they are not interchangeable.

- **Dataset A** (`eeg_dataset_a_k37`) aggregates the same number of epochs from each condition. This is the confirmatory condition-aggregation analysis.
- **Dataset B** (`eeg_dataset_b_onset`, `eeg_onset_scores`) is the change at advertisement onset relative to a turn-matched control reply.
- `eeg_dataset_a_whole_window` is a sensitivity. It is not the Dataset A reported in the paper.

## What the numbers say

These are computed from this upload, not copied in by hand.

| | |
|---|---|
| People | {numbers['n_people']:.0f} |
| Felt manipulation, any advertisement minus control | {numbers['manipulation_mean']:+.2f} points |
| Notice, any advertisement minus control | {numbers['notice_mean']:+.2f} points |
| Credibility, early minus late | {numbers['credibility_early_late']:+.2f} points |
| Trust after the advertisement was shown again, early minus late | {numbers['trust_reexposure_early_late']:+.2f} points |
| Trust × posterior alpha, condition aggregation | ρ = {numbers['rho_dataset_a']:.2f} (n = 18) |
| Trust × posterior alpha, onset-locked | ρ = {numbers['rho_dataset_b']:.2f} (n = {numbers['rho_dataset_b_n']:.0f}) |

The onset association is the one to try to replicate. Condition-aggregated posterior alpha was lower for early than late insertion, and that contrast shares variance with conversational depth. Frontal theta was higher while people wrote than while they read, which is the check that the EEG pipeline can see a difference of that kind.

About 70% of participants reported banners as sponsored, against about 40% for mentions inside the reply. Banners were remembered better. Nobody clicked. Personality and demographics did not moderate the contrasts. The full intervals, Holm-adjusted tests, and the exploratory slow-wave tilt after the early banner are in `results/` and in the figures below.

```python
import pandas as pd
from scipy.stats import spearmanr

contrasts = pd.read_parquet("data/behavioural_contrasts.parquet")
onset = pd.read_parquet("data/eeg_onset_scores.parquet")
alpha = onset.query(
    "contrast_id == 'any_ad_vs_matched_no_ad' and feature == 'posterior_alpha_power_db_uv2'"
)[["experiment_id", "difference"]]
lab = contrasts.loc[contrasts.arm == "lab", ["experiment_id", "trust__any_ad_vs_no_ads"]]
joined = lab.merge(alpha, on="experiment_id")
print(spearmanr(joined.trust__any_ad_vs_no_ads, joined.difference))
print(contrasts.manipulation__any_ad_vs_no_ads.mean())

planned = pd.read_csv("results/behaviour/confirmatory_planned_D.csv")
print(planned.query("outcome == 'manipulation' and contrast == 'any_ad_vs_no_ads'")[
    ["mean", "ci95_lo", "ci95_hi", "dz", "p_holm"]
])
eeg = pd.read_csv("results/eeg/eeg_ad_response_contrasts.csv")
tilt = eeg.query(
    "contrast_id == 'block_early_vs_no_ad_early' and feature == 'delta_power_db_uv2'"
)
print(tilt[["mean_difference", "p_t_holm", "feature_tier"]].round(3))
```

## Figures from the paper

{chr(10).join(figure_md)}

## Configs

| config | rows | columns | what a row is |
|---|---:|---:|---|
{chr(10).join(config_rows)}

The join key is `experiment_id`. It is a new random id, stable across every config in this repository, and it does not match the identifiers in the laboratory logs. EEG exists only for the laboratory arm. Trajectory tables carry two genre contexts; **utterance context is the primary one** (`genre_source == "utterance"`). Participants, not epochs, are the unit of the tests.

`results/` holds the group-level test tables (planned contrasts, Holm corrections, personality models, EEG contrast summaries). They contain no person-level rows.

### Columns, first config

`behavioural_chat` is the default.

{schema_block("behavioural_chat")}

Every column of every config is listed in [COLUMNS.md](COLUMNS.md). Ratings run from 1 to 7. Difference scores are in the same points. EEG power is in decibels. The longer account of collection, consent, and what was deliberately left out is in [DATA_SHEET.md](DATA_SHEET.md).

## What is not in this repository

This upload is the analysis tables. It is not the recordings and it is not the chats.

- No utterance text, no free-text comments, no recall reactions.
- No raw EEG, no XDF, no ICA decompositions.
- No Prolific identifiers, no session folder names, no calendar timestamps.
- No Amazon catalogue. Served product titles are kept, because they are the advertisements people saw.

Please do not try to re-identify anyone. The laboratory sample is 18 people. Age and occupation are not included for that reason.

## Citation

```bibtex
@misc{{troiani2026priceofattention,
  title  = {{The Price of Attention: Behavioural and Neural Correlates of LLM-Based Conversational Advertising}},
  author = {{Troiani, Walter J. and Lymperidou, Aikaterini and Idesis, Sebastian and Arapakis, Ioannis}},
  year   = {{2026}},
  note   = {{Dataset: https://huggingface.co/datasets/eZWALT/price-of-attention}}
}}
```

Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## How the tables were built

Behavioural Gold is `analysis/walter/behavioural/` on N = 54. Dataset A confirmatory features are the k = 37 equal-n aggregation. Dataset B features are the 4-second onset epochs after the primary ICA preprocessing. The release script remaps identifiers, drops the columns listed above, and checks that no original identifier, recording path, or calendar timestamp remains.
"""
    # descriptions is kept so a future card section can print per-config blurbs
    # without drifting from TABLES. Referenced here so the argument stays live.
    assert set(descriptions) == {name for name, _, _ in TABLES}
    (out / "README.md").write_text(readme)


def yaml_dump_configs(configs: list[dict]) -> str:
    lines = []
    for config in configs:
        lines.append(f"- config_name: {config['config_name']}")
        lines.append("  data_files:")
        for item in config["data_files"]:
            lines.append(f"  - split: {item['split']}")
            lines.append(f"    path: {item['path']}")
        if config.get("default"):
            lines.append("  default: true")
    return "\n".join(lines)


def render_banner(path: Path) -> None:
    """Crop the explicit-format panel out of the interface screenshot.

    The full screenshot also contains a line of chat. Only the banner is
    copied, so the dataset card does not republish an utterance.
    """
    import numpy as np
    from PIL import Image

    source = ROOT / "docs/overleaf/publication/Figures/UI/explicit_ad_2.png"
    image = Image.open(source).convert("RGB")
    pixels = np.asarray(image)
    orange = (
        (pixels[:, :, 0] > 160)
        & (pixels[:, :, 1] > 70)
        & (pixels[:, :, 1] < 180)
        & (pixels[:, :, 2] < 80)
    )
    dense_rows = np.where(orange.sum(axis=1) > 80)[0]
    top, bottom = int(dense_rows.min()) - 12, int(dense_rows.max()) + 28
    image.crop((0, max(0, top), image.width, min(image.height, bottom))).save(path)


def write_columns(out: Path, frames: dict[str, pd.DataFrame]) -> None:
    lines = [
        "# Columns",
        "",
        "Every config is one parquet file in `data/`. Ratings are 1–7. "
        "Difference scores are in the same points. EEG power is in decibels.",
        "",
    ]
    for name, _, blurb in TABLES:
        frame = frames[name]
        lines.append(f"## `{name}`")
        lines.append("")
        lines.append(blurb)
        lines.append("")
        lines.append(f"{frame.shape[0]:,} rows, {frame.shape[1]} columns.")
        lines.append("")
        lines.append("| column | dtype |")
        lines.append("|---|---|")
        for column, dtype in frame.dtypes.items():
            kind = "number" if pd.api.types.is_numeric_dtype(dtype) else "string"
            lines.append(f"| `{column}` | {kind} |")
        lines.append("")
    (out / "COLUMNS.md").write_text("\n".join(lines))


def write_datasheet(out: Path, numbers: dict[str, float]) -> None:
    text = f"""# Datasheet

Follows the Gebru et al. (2021) datasheet questions, answered for this release. Short version: the dataset card.

## Motivation

The dataset exists so the tests in *The Price of Attention* can be recomputed, and so a later study can try the onset-locked association between trust and posterior alpha on a new sample. It was built by the authors of that paper. Funding is the Horizon Europe Pathfinder programme, SYMBIOTIK project, grant 101071147.

## Composition

The analysed sample is 54 adults. Eighteen were recorded in a laboratory with 32-channel EEG. Thirty-six took part remotely. Each person completed five conditions: an implicit mention or an explicit banner, early or late in a four-turn conversation, plus an advertisement-free control.

A row is a participant, a condition, a message, an utterance label, or a contrast, depending on the config. There is no image or audio of the participants. EEG is band power in decibels, not voltage. Conversation text is not included. Served product titles are included, because they are the advertisements.

The public join key `experiment_id` is random and does not match the laboratory logs. Subpopulations: the `arm` column is `lab` or `crowd`. EEG columns are empty on the crowd arm.

## Collection

Laboratory participants attended in person, gave informed consent, and were recorded with EEG synchronised to the interface. Remote participants were recruited on Prolific, used their own computer, and were not recorded with EEG. Both arms used the same retrieval assistant and the same five tasks (a gardening gift, a laptop, a study environment, a fitness routine, a pet). Tasks and conditions were assigned so that every person saw every condition.

People were told the study involved a conversational assistant. The advertisement manipulation was disclosed in the debrief, with a chance to withdraw. The compensation stated to laboratory participants is in the paper; it is not repeated here because the manuscript still has a placeholder amount.

Age was collected and is reported in the paper. It is not in these tables. On a laboratory sample of 18, age together with sex is close to identifying. Occupation is not included either.

## Preprocessing

Behavioural tables are the Gold build on N = 54: Likert items, lengths, latencies, and planned difference scores. Trajectory labels are the utterance-context genre classifier; the text it read is dropped. Dataset A confirmatory features average k = 37 epochs per condition. Dataset B is the post-minus-pre change in a 4-second epoch at advertisement onset, minus the same change at a turn-matched control reply, after the primary ICA preprocessing. The whole-window condition table is included and marked as a sensitivity.

The release script drops identifiers, free text, recording paths, and calendar timestamps, remaps the join key, and refuses to write a file that still contains one.

## Uses

Recompute the planned contrasts. Join trust to onset-locked posterior alpha:

- felt manipulation, any advertisement minus control: {numbers['manipulation_mean']:+.2f}
- trust after the advertisement was shown again, early minus late: {numbers['trust_reexposure_early_late']:+.2f}
- Spearman ρ, trust × onset posterior alpha: {numbers['rho_dataset_b']:.2f} (n = {numbers['rho_dataset_b_n']:.0f})

Do not train a model that needs the words people typed. Those words are not here. Do not treat `eeg_dataset_a_whole_window` as the confirmatory Dataset A. Do not try to re-identify the 18 laboratory participants.

## Distribution

Hosted at https://huggingface.co/datasets/eZWALT/price-of-attention under CC BY 4.0. The older repositories `Price-of-Attention-RAW` and `Price-of-Attention-PROCESSED` are empty pointers and are not this release.

## Maintenance

Walter J. Troiani is the corresponding author. A correction that changes a number is a new commit on this repository, not a new slug. Raw recordings and chat logs are not part of the maintenance plan for the public repository.
"""
    (out / "DATA_SHEET.md").write_text(text)


def write_examples(out: Path) -> None:
    example = textwrap.dedent(
        '''\
        """Recompute the two headline checks from the parquet files."""

        from pathlib import Path

        import pandas as pd
        from scipy.stats import spearmanr

        DATA = Path(__file__).resolve().parents[1] / "data"


        def main() -> None:
            contrasts = pd.read_parquet(DATA / "behavioural_contrasts.parquet")
            onset = pd.read_parquet(DATA / "eeg_onset_scores.parquet")
            alpha = onset.query(
                "contrast_id == 'any_ad_vs_matched_no_ad' "
                "and feature == 'posterior_alpha_power_db_uv2'"
            )[["experiment_id", "difference"]]
            lab = contrasts.loc[
                contrasts.arm == "lab", ["experiment_id", "trust__any_ad_vs_no_ads"]
            ]
            joined = lab.merge(alpha, on="experiment_id")
            rho = spearmanr(joined.trust__any_ad_vs_no_ads, joined.difference)
            manip = contrasts.manipulation__any_ad_vs_no_ads.mean()
            print(f"manipulation any-ad minus control: {manip:+.3f}")
            print(f"trust x onset posterior alpha: rho={rho.statistic:.3f} n={len(joined)}")


        if __name__ == "__main__":
            main()
        '''
    )
    examples = out / "examples"
    examples.mkdir(parents=True, exist_ok=True)
    (examples / "reproduce_headlines.py").write_text(example)


def write_license(out: Path) -> None:
    (out / "LICENSE").write_text(
        "This dataset is released under the Creative Commons Attribution 4.0 "
        "International licence (CC BY 4.0).\n\n"
        "https://creativecommons.org/licenses/by/4.0/\n"
    )


def build(out: Path) -> dict[str, float]:
    if out.exists():
        shutil.rmtree(out)
    (out / "data").mkdir(parents=True)
    (out / "results" / "behaviour").mkdir(parents=True)
    (out / "results" / "eeg").mkdir(parents=True)
    (out / "results" / "associations").mkdir(parents=True)

    salt = load_salt()
    maps = collect_ids(salt)
    frames: dict[str, pd.DataFrame] = {}
    descriptions = {name: blurb for name, _, blurb in TABLES}
    audit = []
    for name, path, _ in TABLES:
        frame, notes = remap_frame(pd.read_csv(path), maps)
        assert_clean(frame, maps, name)
        frame.to_parquet(out / "data" / f"{name}.parquet", index=False)
        frames[name] = frame
        audit.append(f"{name}: {frame.shape[0]} x {frame.shape[1]} | " + " ; ".join(notes))

    for path in RESULT_FILES:
        frame = pd.read_csv(path)
        assert_clean(frame, maps, path.name)
        if "behavioural" in str(path):
            dest = out / "results" / "behaviour" / path.name
        elif "combos" in str(path):
            dest = out / "results" / "associations" / path.name
        else:
            dest = out / "results" / "eeg" / path.name
        frame.to_csv(dest, index=False)

    numbers = headline_numbers(frames)
    render_figures(out)
    write_readme(out, frames, numbers, descriptions)
    write_columns(out, frames)
    write_datasheet(out, numbers)
    write_examples(out)
    write_license(out)
    (out / "MANIFEST.json").write_text(
        json.dumps(
            {
                "repo": "eZWALT/price-of-attention",
                "rows": {name: int(frame.shape[0]) for name, frame in frames.items()},
                "headlines": numbers,
                "omitted": [
                    "utterance text",
                    "raw EEG and ICA",
                    "Prolific ids",
                    "calendar timestamps",
                    "Amazon catalogue",
                ],
            },
            indent=2,
        )
        + "\n"
    )
    audit_path = Path("/tmp/poa-release-audit.txt")
    audit_path.write_text("\n".join(audit) + "\n")
    print("\n".join(audit))
    print(json.dumps(numbers, indent=2))
    return numbers


def upload(out: Path) -> str:
    from huggingface_hub import HfApi

    api = HfApi()
    repo_id = "eZWALT/price-of-attention"
    api.create_repo(repo_id, repo_type="dataset", exist_ok=True, private=False)
    api.upload_folder(
        folder_path=str(out),
        repo_id=repo_id,
        repo_type="dataset",
        commit_message="Public analysis tables for The Price of Attention",
    )
    # The older shells are empty and private. Point them at this repo
    # without making them public.
    pointer = (
        "---\nlicense: other\n---\n\n"
        "# Superseded\n\n"
        "This repository is not the release. The public analysis tables are at "
        "[eZWALT/price-of-attention](https://huggingface.co/datasets/eZWALT/price-of-attention).\n\n"
        "Do not upload conversation logs or EEG recordings here.\n"
    )
    for old in ("eZWALT/Price-of-Attention-RAW", "eZWALT/Price-of-Attention-PROCESSED"):
        api.upload_file(
            path_or_fileobj=pointer.encode(),
            path_in_repo="README.md",
            repo_id=old,
            repo_type="dataset",
            commit_message="Point this unused repo at the public analysis tables",
        )
    return f"https://huggingface.co/datasets/{repo_id}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("/tmp/poa-hf"))
    parser.add_argument("--upload", action="store_true")
    args = parser.parse_args()
    build(args.out)
    if args.upload:
        print(upload(args.out))


if __name__ == "__main__":
    main()
