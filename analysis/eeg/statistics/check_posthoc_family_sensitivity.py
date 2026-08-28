"""How much does the Holm family definition change the post-hoc verdict?

The pairwise sweep corrects within measure, within dataset, which is the
same rule the confirmatory pipeline uses. A reviewer can reasonably
argue for a wider family. This brackets the question by recomputing the
verdict under every family definition anyone is likely to propose, from
no correction at all to one family over every test in the sweep.

    python analysis/eeg/statistics/check_posthoc_family_sensitivity.py

Reported in .agents/context/data-analysis/eeg/2026-08-28-posthoc-pairwise.md
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_condition_contrasts import (  # noqa: E402
    holm_adjust,
    read_csv,
    write_csv,
)
from build_posthoc_pairwise import bh_adjust, by_adjust  # noqa: E402


ROOT = Path(__file__).resolve().parents[3]
POSTHOC = ROOT / "analysis/eeg/statistics/outputs/posthoc"

# Same-timing Dataset B pairs are algebraically identical in the two
# spaces, so counting both double-counts 32 tests.
SAME_TIMING = "same_timing_control_cancels"

FAMILY_RULES: dict[str, Callable[[dict[str, str]], tuple[Any, ...]]] = {
    "none (uncorrected)": lambda row: (id(row),),
    "within measure, within dataset and space (AS RUN)": lambda row: (
        row["dataset"],
        row.get("contrast_space", ""),
        row["feature"],
    ),
    "within measure, within dataset, spaces pooled": lambda row: (
        row["dataset"],
        row["feature"],
    ),
    "within measure, both datasets pooled": lambda row: (row["feature"],),
    "within dataset, all 16 measures pooled": lambda row: (
        row["dataset"],
        row.get("contrast_space", ""),
    ),
    "one family over the entire sweep": lambda row: ("all",),
}


def main() -> None:
    rows: list[dict[str, str]] = []
    rows.extend(read_csv(POSTHOC / "eeg_posthoc_pairwise_dataset_a.csv"))
    rows.extend(read_csv(POSTHOC / "eeg_posthoc_pairwise_dataset_b.csv"))

    # Drop the raw-space copy of same-timing Dataset B pairs: identical
    # numbers, so keeping both would inflate every family size.
    distinct = [
        row
        for row in rows
        if not (
            row.get("contrast_space") == "raw_post_minus_pre"
            and row.get("comparison_type") == SAME_TIMING
        )
    ]

    summary: list[dict[str, Any]] = []
    for label, key in FAMILY_RULES.items():
        families: dict[tuple[Any, ...], list[dict[str, str]]] = defaultdict(
            list
        )
        for row in distinct:
            families[key(row)].append(row)
        hits: dict[str, list[str]] = {"holm": [], "bh": [], "by": []}
        for family in families.values():
            raw = [float(row["p_t_raw"]) for row in family]
            for method, adjusted in (
                ("holm", holm_adjust(raw)),
                ("bh", bh_adjust(raw)),
                ("by", by_adjust(raw)),
            ):
                for row, value in zip(family, adjusted):
                    if value < 0.05:
                        hits[method].append(
                            f"{row['feature']}/{row['pair_id']}"
                            f"/{row.get('contrast_space', '')}"
                        )
        sizes = sorted({len(family) for family in families.values()})
        summary.append(
            {
                "family_definition": label,
                "n_families": len(families),
                "family_sizes": ";".join(str(size) for size in sizes),
                "n_tests": len(distinct),
                "n_significant_holm": len(hits["holm"]),
                "n_significant_bh": len(hits["bh"]),
                "n_significant_by": len(hits["by"]),
                "significant_cells_bh": " | ".join(sorted(hits["bh"]))
                or "none",
            }
        )
        print(
            f"{label:<52} families={len(families):>4} "
            f"size={str(sizes):<12} Holm {len(hits['holm']):>2}  "
            f"BH {len(hits['bh']):>2}  BY {len(hits['by']):>2}"
        )

    write_csv(POSTHOC / "eeg_posthoc_family_sensitivity.csv", summary)
    print(f"\nWrote eeg_posthoc_family_sensitivity.csv ({len(distinct)} "
          "distinct tests)")


if __name__ == "__main__":
    main()
