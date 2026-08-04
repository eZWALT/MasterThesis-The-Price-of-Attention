"""Fit, validate, persist, and apply the candidate ocular ICA branch."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
import numpy as np
from mne.preprocessing import ICA, read_ica


@dataclass(frozen=True)
class IcaApplicationReport:
    subject_id: str
    policy_version: str
    fitted_component_count: int
    excluded_components: tuple[int, ...]
    excluded_component_count: int
    pca_explained_variance: float
    model_path: str
    report_path: str


def _repository_path(repository_root: Path, value: str) -> Path:
    return repository_root / value


def ica_paths(
    *,
    repository_root: Path,
    subject_id: str,
    policy: dict[str, Any],
) -> dict[str, Path]:
    config = policy["ica"]
    return {
        "model": _repository_path(
            repository_root,
            config["model_directory"],
        )
        / f"{subject_id}-ica.fif",
        "report": _repository_path(
            repository_root,
            config["report_directory"],
        )
        / f"{subject_id}.json",
        "selection_figure": _repository_path(
            repository_root,
            config["figure_directory"],
        )
        / f"{subject_id}-selection.png",
        "topography_figure": _repository_path(
            repository_root,
            config["figure_directory"],
        )
        / f"{subject_id}-topographies.png",
        "timecourse_figure": _repository_path(
            repository_root,
            config["figure_directory"],
        )
        / f"{subject_id}-timecourses.png",
    }


def _source_proxy_correlations(
    sources: np.ndarray,
    proxies: np.ndarray,
) -> np.ndarray:
    correlations = np.empty((sources.shape[0], proxies.shape[0]), dtype=float)
    for component_index, source in enumerate(sources):
        for proxy_index, proxy in enumerate(proxies):
            if np.std(source) == 0 or np.std(proxy) == 0:
                correlations[component_index, proxy_index] = 0.0
            else:
                correlations[component_index, proxy_index] = float(
                    np.corrcoef(source, proxy)[0, 1]
                )
    return correlations


def _frontal_dominance(
    ica: ICA,
    frontal_channels: list[str],
) -> np.ndarray:
    components = np.abs(ica.get_components())
    lookup = {name.lower(): index for index, name in enumerate(ica.ch_names)}
    frontal_indices = [
        lookup[channel.lower()]
        for channel in frontal_channels
        if channel.lower() in lookup
    ]
    if not frontal_indices:
        raise ValueError("ICA policy has no frontal channels in fitted data")
    frontal = components[frontal_indices].mean(axis=0)
    global_mean = components.mean(axis=0)
    return frontal / np.maximum(global_mean, np.finfo(float).tiny)


def _standardize(values: np.ndarray) -> np.ndarray:
    std = float(np.std(values))
    if std == 0:
        return values - float(np.mean(values))
    return (values - float(np.mean(values))) / std


def _save_selection_figure(
    *,
    correlations: np.ndarray,
    dominance: np.ndarray,
    excluded: list[int],
    policy: dict[str, Any],
    path: Path,
) -> None:
    config = policy["ica"]
    maximum_correlation = np.max(np.abs(correlations), axis=1)
    figure, axis = plt.subplots(figsize=(7.2, 5.0))
    indices = np.arange(len(maximum_correlation))
    colors = [
        "#A33A3A" if index in excluded else "#4C6F8C"
        for index in indices
    ]
    axis.scatter(maximum_correlation, dominance, c=colors, s=35)
    for index, x_value, y_value in zip(
        indices,
        maximum_correlation,
        dominance,
    ):
        axis.annotate(
            str(index),
            (x_value, y_value),
            xytext=(3, 3),
            textcoords="offset points",
            fontsize=7,
        )
    axis.axvline(
        float(config["proxy_correlation_abs_min"]),
        color="#777777",
        linestyle="--",
        linewidth=1,
    )
    axis.axhline(
        float(config["frontal_dominance_min"]),
        color="#777777",
        linestyle="--",
        linewidth=1,
    )
    axis.set_xlabel("Maximum |correlation| with Fp1/Fp2")
    axis.set_ylabel("Frontal topography dominance")
    axis.set_title("ICA ocular-component selection evidence")
    axis.grid(alpha=0.2)
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def _save_topography_figure(
    *,
    ica: ICA,
    excluded: list[int],
    ranking: np.ndarray,
    path: Path,
) -> None:
    picks = excluded or [int(value) for value in ranking[:3]]
    figures = ica.plot_components(
        picks=picks,
        show=False,
        title=(
            "Excluded ICA components"
            if excluded
            else "Top ocular-score components; none excluded"
        ),
    )
    figure = figures[0] if isinstance(figures, list) else figures
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def _save_timecourse_figure(
    *,
    fit_raw: mne.io.BaseRaw,
    sources: np.ndarray,
    excluded: list[int],
    ranking: np.ndarray,
    proxy_channels: list[str],
    path: Path,
) -> None:
    picks = excluded or [int(ranking[0])]
    sample_count = min(
        sources.shape[1],
        int(round(float(fit_raw.info["sfreq"]) * 60.0)),
    )
    times = np.arange(sample_count) / float(fit_raw.info["sfreq"])
    proxy = fit_raw.get_data(
        picks=proxy_channels,
        start=0,
        stop=sample_count,
    ).mean(axis=0)
    figure, axes = plt.subplots(
        len(picks),
        1,
        figsize=(10.0, max(2.8, 2.5 * len(picks))),
        sharex=True,
        squeeze=False,
    )
    for axis, component_index in zip(axes[:, 0], picks):
        axis.plot(
            times,
            _standardize(proxy),
            color="#A36B5D",
            linewidth=0.8,
            label="Mean Fp1/Fp2 proxy",
        )
        axis.plot(
            times,
            _standardize(sources[component_index, :sample_count]),
            color="#2E6F5E",
            linewidth=0.8,
            label=f"IC {component_index}",
        )
        axis.set_ylabel("z score")
        axis.legend(loc="upper right")
        axis.grid(alpha=0.15)
    axes[-1, 0].set_xlabel("Time (s)")
    figure.suptitle("ICA source and ocular-proxy time courses")
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def fit_candidate_ica(
    *,
    raw: mne.io.BaseRaw,
    subject_id: str,
    policy: dict[str, Any],
    repository_root: Path,
) -> dict[str, Any]:
    config = policy["ica"]
    if not config["enabled"]:
        raise ValueError("ICA candidate fitting requires ica.enabled=true")
    proxy_channels = list(config["ocular_proxy_channels"])
    missing = sorted(set(proxy_channels) - set(raw.ch_names))
    if missing:
        raise ValueError(f"{subject_id}: missing ocular proxies {missing}")

    fit_raw = raw.copy()
    fit_raw.filter(
        l_freq=float(config["fit_highpass_hz"]),
        h_freq=float(config["fit_lowpass_hz"]),
        picks="eeg",
        verbose=False,
    )
    picks = mne.pick_types(
        fit_raw.info,
        eeg=True,
        exclude="bads",
    )
    ica = ICA(
        n_components=float(config["pca_explained_variance"]),
        method=str(config["method"]),
        random_state=int(config["random_state"]),
        max_iter=int(config["max_iter"]),
    )
    ica.fit(
        fit_raw,
        picks=picks,
        decim=int(config["fit_decim"]),
        reject_by_annotation=True,
        verbose=False,
    )
    sources = ica.get_sources(fit_raw).get_data()
    proxies = fit_raw.get_data(picks=proxy_channels)
    correlations = _source_proxy_correlations(sources, proxies)
    dominance = _frontal_dominance(
        ica,
        list(config["frontal_channels"]),
    )
    maximum_correlation = np.max(np.abs(correlations), axis=1)
    eligible = np.where(
        (maximum_correlation >= float(config["proxy_correlation_abs_min"]))
        & (dominance >= float(config["frontal_dominance_min"]))
    )[0]
    score = maximum_correlation * dominance
    ranking = np.argsort(score)[::-1]
    eligible_ranking = [
        int(index) for index in ranking if int(index) in set(eligible.tolist())
    ]
    excluded = eligible_ranking[
        : int(config["maximum_excluded_components"])
    ]
    ica.exclude = excluded

    paths = ica_paths(
        repository_root=repository_root,
        subject_id=subject_id,
        policy=policy,
    )
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    ica.save(paths["model"], overwrite=True)

    component_rows = []
    for component_index in range(ica.n_components_):
        component_rows.append(
            {
                "component_index": component_index,
                "fp1_correlation": float(correlations[component_index, 0]),
                "fp2_correlation": float(correlations[component_index, 1]),
                "maximum_absolute_proxy_correlation": float(
                    maximum_correlation[component_index]
                ),
                "frontal_dominance": float(dominance[component_index]),
                "selection_score": float(score[component_index]),
                "meets_automatic_rule": bool(
                    component_index in eligible
                ),
                "excluded": bool(component_index in excluded),
            }
        )
    report = {
        "subject_id": subject_id,
        "policy_version": policy["policy_version"],
        "method": config["method"],
        "random_state": config["random_state"],
        "pca_explained_variance": config["pca_explained_variance"],
        "fit_highpass_hz": config["fit_highpass_hz"],
        "fit_lowpass_hz": config["fit_lowpass_hz"],
        "fit_decim": config["fit_decim"],
        "fitted_component_count": int(ica.n_components_),
        "excluded_components": excluded,
        "excluded_component_count": len(excluded),
        "selection_rule": config["selection_rule"],
        "human_visual_signoff": "pending",
        "model_path": str(paths["model"].relative_to(repository_root)),
        "figures": {
            name: str(path.relative_to(repository_root))
            for name, path in paths.items()
            if name.endswith("_figure")
        },
        "components": component_rows,
    }
    paths["report"].write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    _save_selection_figure(
        correlations=correlations,
        dominance=dominance,
        excluded=excluded,
        policy=policy,
        path=paths["selection_figure"],
    )
    _save_topography_figure(
        ica=ica,
        excluded=excluded,
        ranking=ranking,
        path=paths["topography_figure"],
    )
    _save_timecourse_figure(
        fit_raw=fit_raw,
        sources=sources,
        excluded=excluded,
        ranking=ranking,
        proxy_channels=proxy_channels,
        path=paths["timecourse_figure"],
    )
    return report


def apply_saved_ica(
    *,
    raw: mne.io.BaseRaw,
    subject_id: str,
    policy: dict[str, Any],
    repository_root: Path,
) -> tuple[mne.io.BaseRaw, IcaApplicationReport]:
    paths = ica_paths(
        repository_root=repository_root,
        subject_id=subject_id,
        policy=policy,
    )
    if not paths["model"].exists() or not paths["report"].exists():
        raise FileNotFoundError(
            f"{subject_id}: fit ICA before feature generation: "
            f"{paths['model']}"
        )
    report = json.loads(paths["report"].read_text(encoding="utf-8"))
    if report["policy_version"] != policy["policy_version"]:
        raise ValueError(
            f"{subject_id}: ICA report policy mismatch "
            f"{report['policy_version']} != {policy['policy_version']}"
        )
    ica = read_ica(paths["model"], verbose=False)
    excluded = [int(value) for value in report["excluded_components"]]
    ica.exclude = excluded
    output = raw.copy()
    ica.apply(output, exclude=excluded, verbose=False)
    application = IcaApplicationReport(
        subject_id=subject_id,
        policy_version=str(policy["policy_version"]),
        fitted_component_count=int(report["fitted_component_count"]),
        excluded_components=tuple(excluded),
        excluded_component_count=len(excluded),
        pca_explained_variance=float(report["pca_explained_variance"]),
        model_path=str(paths["model"]),
        report_path=str(paths["report"]),
    )
    return output, application
