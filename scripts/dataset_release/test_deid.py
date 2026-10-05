"""The release must not keep a chat, a clock, or a laboratory id."""

import pandas as pd

from build_price_of_attention import assert_clean, remap_frame


def test_private_fields_do_not_survive():
    raw_experiment = "exp_20260101T120000Z_deadbeef"
    maps = {
        "experiment": {raw_experiment: "e_0123456789"},
        "subject": {"lab_folder_01": "e_0123456789"},
        "conversation": {},
        "utterance": {},
        "transition": {},
        "_private_sets": {
            "participant": {"abcd1234"},
            "folder": {"lab_folder_01"},
            "experiment": {raw_experiment},
            "subject": {"lab_folder_01"},
            "conversation": set(),
            "utterance": set(),
            "transition": set(),
        },
    }
    frame = pd.DataFrame(
        {
            "experiment_id": [raw_experiment],
            "participant_id": ["abcd1234"],
            "subject_id": ["lab_folder_01"],
            "folder": ["lab_folder_01"],
            "unix_ts": ["2026-01-01T12:00:00"],
            "text": ["please recommend a laptop under a thousand euros"],
            "recall_reaction": ["I felt pushed"],
            "trust": [4],
        }
    )
    cleaned, notes = remap_frame(frame, maps)
    assert_clean(cleaned, maps, "fixture")
    assert cleaned["experiment_id"].iloc[0] == "e_0123456789"
    assert "text" not in cleaned.columns
    assert "participant_id" not in cleaned.columns
    assert "unix_ts" not in cleaned.columns
    assert cleaned["trust"].iloc[0] == 4
    blob = " ".join(notes)
    assert "dropped" in blob


def test_score_table_keyed_only_by_subject_becomes_experiment_id():
    maps = {
        "experiment": {},
        "subject": {"lab_folder_01": "e_0123456789"},
        "conversation": {},
        "utterance": {},
        "transition": {},
        "_private_sets": {
            "participant": set(),
            "folder": {"lab_folder_01"},
            "experiment": set(),
            "subject": {"lab_folder_01"},
            "conversation": set(),
            "utterance": set(),
            "transition": set(),
        },
    }
    frame = pd.DataFrame(
        {"subject_id": ["lab_folder_01"], "feature": ["posterior_alpha"], "difference": [0.2]}
    )
    cleaned, _notes = remap_frame(frame, maps)
    assert_clean(cleaned, maps, "scores")
    assert list(cleaned.columns)[:1] == ["experiment_id"]
    assert cleaned["experiment_id"].iloc[0] == "e_0123456789"


if __name__ == "__main__":
    test_private_fields_do_not_survive()
    test_score_table_keyed_only_by_subject_becomes_experiment_id()
    print("de-id tests passed")
