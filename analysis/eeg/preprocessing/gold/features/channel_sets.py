"""Channel-set policies for EEG spectral features.

Cleaning stays on the full 32-channel montage. These policies only choose
which electrodes enter each of the 16 Gold spectral formulas. The current
primary contract is `channel_set_policy.json`. The literature-ROI file (`literature_roi_v0`, George 2025 nine-site)
the Wang-zone file (`wang2022_v0`), the AES-region file
(`teaching_atlas_v0`), and Angela's code lists (`angela_code_v0`)
are filled sensitivities and must not write primary Gold.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


FEATURE_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = FEATURE_DIR.parents[5]
DEFAULT_CHANNEL_SET_PATH = FEATURE_DIR / "channel_set_policy.json"
LITERATURE_ROI_PATH = FEATURE_DIR / "channel_set_policy_literature_roi.json"
GEORGE2025_PATH = LITERATURE_ROI_PATH
WANG2022_PATH = FEATURE_DIR / "channel_set_policy_wang2022.json"
TEACHING_ATLAS_PATH = FEATURE_DIR / "channel_set_policy_teaching_atlas.json"
ANGELA_CODE_PATH = FEATURE_DIR / "channel_set_policy_angela_code.json"
BAND_ORDER = ("delta", "theta", "alpha", "beta", "gamma")
READY_STATUSES = frozenset({"frozen", "ready"})
PRIMARY_ROLE = "primary_gold"
ALL_CHANNELS = "all"
PRIMARY_VERSION = "current_v1"
LITERATURE_ROI_VERSION = "literature_roi_v0"
GEORGE2025_VERSION = LITERATURE_ROI_VERSION
WANG2022_VERSION = "wang2022_v0"
TEACHING_ATLAS_VERSION = "teaching_atlas_v0"
ANGELA_CODE_VERSION = "angela_code_v0"

# Locked electrode lists. JSON policies must match these tuples.
# Primary Gold: the five global powers average the whole montage.
PRIMARY_BAND_CHANNELS: dict[str, ChannelSpec] = {
    name: ALL_CHANNELS for name in BAND_ORDER
}
# Sensitivity only. The nine 10-20 sites George & Gulia 2025 actually
# recorded (Methods). Same list for every band: that paper does not
# publish a per-band electrode table. Do not write into primary Gold.
GEORGE2025_NINE: tuple[str, ...] = (
    "F3",
    "Fz",
    "F4",
    "C3",
    "Cz",
    "C4",
    "O1",
    "Oz",
    "O2",
)
LITERATURE_ROI_BAND_CHANNELS: dict[str, tuple[str, ...]] = {
    name: GEORGE2025_NINE for name in BAND_ORDER
}
# Sensitivity only. Wang & Mengoni 2022 §2.2 geography applied to that
# paper's own 10-20 zone letters on this 32-channel cap. Wang does not
# publish these electrode tuples. Do not write into primary Gold.
WANG2022_FRONTAL = (
    "Fp1",
    "Fp2",
    "F3",
    "Fz",
    "F4",
    "F7",
    "F8",
    "F9",
    "F10",
)
WANG2022_THETA_LEFT = ("C3", "P3", "T7", "P7")
WANG2022_OCCIPITAL = ("O1", "Oz", "O2")
WANG2022_FRONTOCENTRAL = (
    "F3",
    "Fz",
    "F4",
    "F7",
    "F8",
    "F9",
    "F10",
    "C3",
    "Cz",
    "C4",
)
WANG2022_BAND_CHANNELS: dict[str, tuple[str, ...]] = {
    "delta": WANG2022_FRONTAL,
    "theta": WANG2022_THETA_LEFT,
    "alpha": WANG2022_OCCIPITAL,
    "beta": WANG2022_FRONTOCENTRAL,
    "gamma": WANG2022_FRONTOCENTRAL,
}
# Sensitivity only. AES / Britton et al. 2016 name regions, not
# electrode tuples. These lists are this cap's map of those regions.
# Do not write into primary Gold. Do not cite the atlas as if it
# published these strings.
TEACHING_ATLAS_ALPHA = ("O1", "Oz", "O2", "P3", "Pz", "P4")
TEACHING_ATLAS_BETA = (
    "F3",
    "Fz",
    "F4",
    "F7",
    "F8",
    "C3",
    "Cz",
    "C4",
    "T7",
    "T8",
)
TEACHING_ATLAS_THETA = ("F3", "Fz", "F4", "FC1", "FC2", "C3", "Cz", "C4")
TEACHING_ATLAS_DELTA = ("F3", "Fz", "F4", "F7", "F8")
TEACHING_ATLAS_GAMMA = ("F3", "Fz", "F4", "FC1", "FC2", "C3", "Cz", "C4")
TEACHING_ATLAS_BAND_CHANNELS: dict[str, tuple[str, ...]] = {
    "delta": TEACHING_ATLAS_DELTA,
    "theta": TEACHING_ATLAS_THETA,
    "alpha": TEACHING_ATLAS_ALPHA,
    "beta": TEACHING_ATLAS_BETA,
    "gamma": TEACHING_ATLAS_GAMMA,
}
# Sensitivity only. Angela's BAND_CHANNELS from cognitive-mllm,
# intersected with the recorded 32 sites. Not a paper. Missing
# FCz / CP3 / CPz / CP4 / PO7 / PO8 were dropped, not replaced.
# Do not write into primary Gold.
ANGELA_CODE_AS_WRITTEN: dict[str, tuple[str, ...]] = {
    "delta": ("Fz", "F3", "F4", "Cz"),
    "theta": ("Fz", "FCz", "Cz", "F3", "F4"),
    "alpha": ("O1", "Oz", "O2", "P3", "Pz", "P4"),
    "beta": ("C3", "Cz", "C4", "CP3", "CPz", "CP4"),
    "gamma": ("O1", "Oz", "O2", "P7", "P8", "PO7", "PO8"),
}
ANGELA_CODE_DROPPED: tuple[str, ...] = (
    "FCz",
    "CP3",
    "CPz",
    "CP4",
    "PO7",
    "PO8",
)
ANGELA_CODE_BAND_CHANNELS: dict[str, tuple[str, ...]] = {
    "delta": ("Fz", "F3", "F4", "Cz"),
    "theta": ("Fz", "F3", "F4", "Cz"),
    "alpha": ("O1", "Oz", "O2", "P3", "Pz", "P4"),
    "beta": ("C3", "Cz", "C4"),
    "gamma": ("O1", "Oz", "O2", "P7", "P8"),
}
LOCKED_FZ_THETA = ("Fz",)
LOCKED_POSTERIOR_ALPHA = ("O1", "Oz", "O2", "P3", "Pz", "P4")
SENSITIVITY_FEATURE_ROOT = Path(
    "src/project/logs/xdf/gold/features/sensitivity/channel_sets"
)
SENSITIVITY_STATS_ROOT = Path(
    "analysis/eeg/statistics/outputs/sensitivity/channel_sets"
)

ChannelSpec = str | tuple[str, ...]


@dataclass(frozen=True)
class BandSpec:
    name: str
    low_hz: float
    high_hz: float
    channels: ChannelSpec


@dataclass(frozen=True)
class ChannelSetPolicy:
    policy_version: str
    status: str
    role: str
    path: Path
    bands: dict[str, BandSpec]
    fz_theta_channels: tuple[str, ...]
    posterior_alpha_channels: tuple[str, ...]
    faa_left: tuple[str, ...]
    faa_right: tuple[str, ...]
    pope_global_channels: ChannelSpec
    pope_frontocentral_channels: tuple[str, ...]
    kislov_channels: tuple[str, ...]
    kislov_alpha_hz: tuple[float, float]
    kislov_beta_hz: tuple[float, float]
    epoch_rejection_channels: str
    cleaning_scope: str

    @property
    def is_primary(self) -> bool:
        return self.role == PRIMARY_ROLE

    @property
    def is_ready(self) -> bool:
        return self.status in READY_STATUSES


_DEFAULT_POLICY: ChannelSetPolicy | None = None


def default_channel_set() -> ChannelSetPolicy:
    global _DEFAULT_POLICY
    if _DEFAULT_POLICY is None:
        _DEFAULT_POLICY = load_channel_set_policy(DEFAULT_CHANNEL_SET_PATH)
    return _DEFAULT_POLICY


def resolve_channel_set(
    channel_set: ChannelSetPolicy | Path | None,
) -> ChannelSetPolicy:
    if channel_set is None:
        return default_channel_set()
    if isinstance(channel_set, ChannelSetPolicy):
        return channel_set
    return load_channel_set_policy(channel_set)


def load_channel_set_policy(path: Path) -> ChannelSetPolicy:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return policy_from_mapping(payload, path=path)


def policy_from_mapping(
    payload: dict[str, Any],
    *,
    path: Path,
) -> ChannelSetPolicy:
    bands_raw = payload.get("bands")
    if not isinstance(bands_raw, dict) or set(bands_raw) != set(BAND_ORDER):
        raise ValueError(
            f"{path}: bands must define exactly {list(BAND_ORDER)}"
        )
    bands = {
        name: BandSpec(
            name=name,
            low_hz=float(bands_raw[name]["low_hz"]),
            high_hz=float(bands_raw[name]["high_hz"]),
            channels=_parse_channel_spec(
                bands_raw[name].get("channels"),
                field=f"bands.{name}.channels",
                path=path,
            ),
        )
        for name in BAND_ORDER
    }
    derived = payload.get("derived")
    if not isinstance(derived, dict):
        raise ValueError(f"{path}: missing derived channel sets")
    kislov = derived.get("engagement_kislov")
    if not isinstance(kislov, dict):
        raise ValueError(f"{path}: missing derived.engagement_kislov")
    faa = derived.get("faa")
    if not isinstance(faa, dict):
        raise ValueError(f"{path}: missing derived.faa")
    cleaning = payload.get("cleaning")
    if not isinstance(cleaning, dict):
        raise ValueError(f"{path}: missing cleaning block")
    rejection = str(payload.get("epoch_rejection_channels", ALL_CHANNELS))
    if rejection not in {ALL_CHANNELS, "used"}:
        raise ValueError(
            f"{path}: epoch_rejection_channels must be 'all' or 'used'"
        )
    policy = ChannelSetPolicy(
        policy_version=str(payload["policy_version"]),
        status=str(payload["status"]),
        role=str(payload["role"]),
        path=path,
        bands=bands,
        fz_theta_channels=_parse_named_list(
            derived.get("fz_theta", {}),
            field="derived.fz_theta.channels",
            path=path,
        ),
        posterior_alpha_channels=_parse_named_list(
            derived.get("posterior_alpha", {}),
            field="derived.posterior_alpha.channels",
            path=path,
        ),
        faa_left=_parse_string_tuple(faa.get("left"), field="derived.faa.left", path=path),
        faa_right=_parse_string_tuple(
            faa.get("right"),
            field="derived.faa.right",
            path=path,
        ),
        pope_global_channels=_parse_channel_spec(
            derived.get("engagement_pope_global", {}).get("channels"),
            field="derived.engagement_pope_global.channels",
            path=path,
        ),
        pope_frontocentral_channels=_parse_named_list(
            derived.get("engagement_pope_frontocentral", {}),
            field="derived.engagement_pope_frontocentral.channels",
            path=path,
        ),
        kislov_channels=_parse_named_list(
            kislov,
            field="derived.engagement_kislov.channels",
            path=path,
        ),
        kislov_alpha_hz=_parse_hz_pair(
            kislov.get("alpha_hz"),
            field="derived.engagement_kislov.alpha_hz",
            path=path,
        ),
        kislov_beta_hz=_parse_hz_pair(
            kislov.get("beta_hz"),
            field="derived.engagement_kislov.beta_hz",
            path=path,
        ),
        epoch_rejection_channels=rejection,
        cleaning_scope=str(cleaning.get("scope", "")),
    )
    if policy.cleaning_scope != "full_montage":
        raise ValueError(
            f"{path}: cleaning.scope must be full_montage; "
            "do not subset channels before reference or ICA"
        )
    _assert_locked_lists(policy)
    return policy


def require_ready(policy: ChannelSetPolicy) -> None:
    if policy.is_ready:
        _require_filled(policy)
        return
    raise ValueError(
        f"Channel-set policy {policy.policy_version} is {policy.status}. "
        "Fill the electrode lists and set status to ready before computing."
    )


def assert_output_allowed(
    policy: ChannelSetPolicy,
    *outputs: Path,
) -> None:
    if policy.is_primary:
        return
    blocked = [path for path in outputs if _is_protected_primary_output(path)]
    if blocked:
        raise ValueError(
            "Non-primary channel-set policies cannot write primary Gold "
            "or primary statistics. "
            f"Blocked: {', '.join(str(path) for path in blocked)}. "
            "Write under "
            f"{SENSITIVITY_FEATURE_ROOT / policy.policy_version}/"
        )
    for path in outputs:
        if "sensitivity" not in path.resolve().parts:
            raise ValueError(
                "Non-primary channel-set outputs must live under a "
                f"sensitivity/ directory: {path}"
            )


def suggested_sensitivity_dir(policy: ChannelSetPolicy) -> Path:
    return SENSITIVITY_FEATURE_ROOT / policy.policy_version


def suggested_stats_dir(policy: ChannelSetPolicy) -> Path:
    return SENSITIVITY_STATS_ROOT / policy.policy_version


def reroute_if_default(
    policy: ChannelSetPolicy,
    requested: Path,
    primary_default: Path,
    replacement: Path,
) -> Path:
    if policy.is_primary:
        return requested
    if requested.resolve() == primary_default.resolve():
        print(f"Rerouting {requested.name} -> {replacement}")
        return replacement
    return requested


def used_channel_spec(policy: ChannelSetPolicy) -> ChannelSpec:
    specs: list[ChannelSpec] = [
        policy.bands[name].channels for name in BAND_ORDER
    ]
    specs.extend(
        [
            policy.fz_theta_channels,
            policy.posterior_alpha_channels,
            policy.faa_left,
            policy.faa_right,
            policy.pope_global_channels,
            policy.pope_frontocentral_channels,
            policy.kislov_channels,
        ]
    )
    if any(spec == ALL_CHANNELS for spec in specs):
        return ALL_CHANNELS
    names: list[str] = []
    seen: set[str] = set()
    for spec in specs:
        for name in spec:
            key = name.lower()
            if key not in seen:
                seen.add(key)
                names.append(name)
    return tuple(names)


def rejection_channel_spec(policy: ChannelSetPolicy) -> ChannelSpec:
    if policy.epoch_rejection_channels == ALL_CHANNELS:
        return ALL_CHANNELS
    return used_channel_spec(policy)


def lookup_names(channel_names: list[str]) -> dict[str, int]:
    return {name.lower(): index for index, name in enumerate(channel_names)}


def channel_indices(
    spec: ChannelSpec,
    lookup: dict[str, int],
    *,
    field: str,
) -> np.ndarray:
    if spec == ALL_CHANNELS:
        return np.arange(len(lookup), dtype=int)
    names = spec
    missing = [name for name in names if name.lower() not in lookup]
    if missing:
        raise ValueError(f"{field} requires channels: {missing}")
    if not names:
        raise ValueError(f"{field} has no channels")
    return np.asarray([lookup[name.lower()] for name in names], dtype=int)


def mean_over(
    values: np.ndarray,
    spec: ChannelSpec,
    lookup: dict[str, int],
    *,
    field: str,
) -> float:
    return float(np.mean(values[channel_indices(spec, lookup, field=field)]))


def _parse_channel_spec(
    value: Any,
    *,
    field: str,
    path: Path,
) -> ChannelSpec:
    if value == ALL_CHANNELS:
        return ALL_CHANNELS
    return _parse_string_tuple(value, field=field, path=path)


def _parse_named_list(
    block: Any,
    *,
    field: str,
    path: Path,
) -> tuple[str, ...]:
    if not isinstance(block, dict):
        raise ValueError(f"{path}: {field} parent is missing")
    return _parse_string_tuple(block.get("channels"), field=field, path=path)


def _parse_string_tuple(
    value: Any,
    *,
    field: str,
    path: Path,
) -> tuple[str, ...]:
    if value is None:
        raise ValueError(f"{path}: {field} is missing")
    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in value
    ):
        raise ValueError(f"{path}: {field} must be a list of channel names")
    return tuple(value)


def _parse_hz_pair(
    value: Any,
    *,
    field: str,
    path: Path,
) -> tuple[float, float]:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not all(isinstance(item, (int, float)) for item in value)
    ):
        raise ValueError(f"{path}: {field} must be [low_hz, high_hz]")
    low_hz, high_hz = float(value[0]), float(value[1])
    if low_hz >= high_hz:
        raise ValueError(f"{path}: {field} must have low_hz < high_hz")
    return low_hz, high_hz


def _require_filled(policy: ChannelSetPolicy) -> None:
    empty: list[str] = []
    for name, band in policy.bands.items():
        if band.channels != ALL_CHANNELS and len(band.channels) == 0:
            empty.append(f"bands.{name}")
    for field, names in (
        ("fz_theta", policy.fz_theta_channels),
        ("posterior_alpha", policy.posterior_alpha_channels),
        ("faa.left", policy.faa_left),
        ("faa.right", policy.faa_right),
        ("pope_frontocentral", policy.pope_frontocentral_channels),
        ("kislov", policy.kislov_channels),
    ):
        if len(names) == 0:
            empty.append(field)
    if (
        policy.pope_global_channels != ALL_CHANNELS
        and len(policy.pope_global_channels) == 0
    ):
        empty.append("pope_global")
    if empty:
        raise ValueError(
            f"{policy.policy_version} is marked {policy.status} but still "
            f"has empty channel lists: {', '.join(empty)}"
        )


def _assert_locked_lists(policy: ChannelSetPolicy) -> None:
    if policy.fz_theta_channels != LOCKED_FZ_THETA:
        raise ValueError(
            f"{policy.policy_version}: Fz theta must stay {LOCKED_FZ_THETA}"
        )
    if policy.posterior_alpha_channels != LOCKED_POSTERIOR_ALPHA:
        raise ValueError(
            f"{policy.policy_version}: posterior alpha must stay "
            f"{LOCKED_POSTERIOR_ALPHA}"
        )
    if policy.policy_version == PRIMARY_VERSION:
        expected = PRIMARY_BAND_CHANNELS
    elif policy.policy_version == LITERATURE_ROI_VERSION:
        expected = LITERATURE_ROI_BAND_CHANNELS
    elif policy.policy_version == WANG2022_VERSION:
        expected = WANG2022_BAND_CHANNELS
    elif policy.policy_version == TEACHING_ATLAS_VERSION:
        expected = TEACHING_ATLAS_BAND_CHANNELS
    elif policy.policy_version == ANGELA_CODE_VERSION:
        expected = ANGELA_CODE_BAND_CHANNELS
    else:
        return
    for name in BAND_ORDER:
        got = policy.bands[name].channels
        want = expected[name]
        if got != want:
            raise ValueError(
                f"{policy.policy_version}: bands.{name}.channels is {got}, "
                f"locked value is {want}"
            )


def _is_protected_primary_output(path: Path) -> bool:
    resolved = path.resolve()
    roots = (
        (REPOSITORY_ROOT / "src/project/logs/xdf/gold").resolve(),
        (REPOSITORY_ROOT / "analysis/eeg/statistics/outputs").resolve(),
    )
    for root in roots:
        try:
            relative = resolved.relative_to(root)
        except ValueError:
            continue
        return "sensitivity" not in relative.parts
    return False
