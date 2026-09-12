"""Demographic moderation of the planned contrasts, on Walter Gold (N = 54).

Reconciliation of Katerina's demographic moderation models (September 2026,
`analysis/behavioural/moderation_model_gold.py`, `temp_demo_moderation_model.py`;
read only, never run here). Her design fits `outcome ~ C(condition) * C(factor)`
with a random intercept per person and reads the raw p of every
condition-dummy × factor-level interaction. This script keeps the thesis
estimand instead and estimates the same question as a declared family:

    random-intercept LMM on Y_ic
    the three planned contrast codes × one demographic factor at a time
    cell = joint Wald test of the (L − 1) contrast × level interaction terms
    Holm within outcome across the factor × contrast cells (5 × 3 = 15;
    cued memory 5 × 2 = 10)

Two codings are run side by side. `katerina` keeps her levels wherever a
level has at least MIN_LEVEL people (sparse levels merged into the nearest
neighbour, never dropped silently; see LEVEL_MAPS). `collapsed` is the
two-level screen already used as covariates in run_personality_declared.py
(familiar vs other, daily vs less) plus two-level sex, arm, and graduate
degree vs not.

A person-level OLS of D_i on the factor (F test) is written beside the LMM
as a concordance check. Her exact model is also refitted on Gold under
`katerina_design` so that the raw-p cells she saw can be named and Holm-
adjusted, not quoted from her n = 19 tree.

Age is not estimable: `demo_age` is empty in the Gold JSONL for all 54.

Writes
  outputs/exploratory/demographic_moderation_lmm.csv
  outputs/exploratory/demographic_moderation_levels.csv
  outputs/exploratory/demographic_moderation_katerina_design.csv
  outputs/exploratory/demographic_moderation_secondary.csv   (sensitivity, not the family)
  outputs/exploratory/demographic_moderation_summary.json
  outputs/figures/thesis/tab_beh_demographics.tex
  outputs/figures/thesis/beh_demographics_board.{pdf,png}
and copies the .pdf and .tex to docs/overleaf/thesis/figures/results/.

    python analysis/walter/behavioural/stats/run_demographic_moderation.py
"""

from __future__ import annotations

import json
import shutil
import sys
import warnings
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from matplotlib.colors import BoundaryNorm, ListedColormap
from scipy import stats
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
REPO = WALTER.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
EXPL = WALTER / "behavioural" / "outputs" / "exploratory"
FIG = WALTER / "behavioural" / "outputs" / "figures" / "thesis"
OVERLEAF = REPO / "docs" / "overleaf" / "thesis" / "figures" / "results"

PRIMARY = ("trust", "credibility", "manipulation", "notice")
RECALL = ("recall_memory",)
OUTCOMES = PRIMARY + RECALL
SECONDARY = ("helpfulness", "convincingness", "relevance", "neutrality")  # sensitivity only, her coding
NAME = {
    "trust": "Trust",
    "credibility": "Credibility",
    "manipulation": "Perceived manipulation",
    "notice": "Notice",
    "recall_memory": "Cued memory",
}
CONTRAST_CODES = ("any_ad_vs_no_ads", "inline_vs_block", "early_vs_late")
CONTRAST_TITLE = {
    "any_ad_vs_no_ads": "Any ad − no ads",
    "inline_vs_block": "Format (implicit − explicit)",
    "early_vs_late": "Timing (early − late)",
}
MIN_LEVEL = 5  # people per level; below this a level is merged (never silently dropped)

# ----------------------------------------------------------------------------- #
# factor codings
# ----------------------------------------------------------------------------- #
# Each entry: factor id -> (source column, level map raw -> shown, ordered levels, reference)
# A raw value mapped to None is excluded from that factor's model (recorded in summary).
LEVEL_MAPS: dict[str, dict[str, tuple]] = {
    "katerina": {
        "sex": ("demo_sex", {"Male": "Male", "Female": "Female"}, ["Male", "Female"], "Male"),
        "education": (
            "demo_education",
            {
                "High School": "High school",
                "Bachelor's Degree": "Bachelor's",
                "Master's Degree": "Master's or PhD",
                "PhD": "Master's or PhD",  # n = 3 < MIN_LEVEL, merged upward
                "Other": None,  # n = 3, no place on the ordered scale
            },
            ["High school", "Bachelor's", "Master's or PhD"],
            "Bachelor's",
        ),
        "familiarity": (
            "demo_familiarity",
            {
                "Familiar": "Familiar",
                "Somewhat Familiar": "Less than familiar",
                "Somewhat Unfamiliar": "Less than familiar",  # n = 2, merged
            },
            ["Familiar", "Less than familiar"],
            "Familiar",
        ),
        "frequency": (
            "demo_frequency",
            {
                "Greater than 5 times per day": "> 5 per day",
                "1–5 times per day": "1–5 per day",
                "1–5 times per week": "1–5 per week",
                "1–5 times per month": "Monthly or less",
                "Fewer than 5 times ever": "Monthly or less",  # n = 2, merged
            },
            ["> 5 per day", "1–5 per day", "1–5 per week", "Monthly or less"],
            "1–5 per day",
        ),
        "arm": ("arm", {"lab": "Laboratory", "crowd": "Crowd"}, ["Crowd", "Laboratory"], "Crowd"),
    },
    "collapsed": {
        "sex": ("demo_sex", {"Male": "Male", "Female": "Female"}, ["Male", "Female"], "Male"),
        "education": (
            "demo_education",
            {
                "High School": "Bachelor's or less",
                "Bachelor's Degree": "Bachelor's or less",
                "Master's Degree": "Graduate degree",
                "PhD": "Graduate degree",
                "Other": None,
            },
            ["Bachelor's or less", "Graduate degree"],
            "Bachelor's or less",
        ),
        "familiarity": (
            "demo_familiarity",
            {"Familiar": "Familiar", "Somewhat Familiar": "Other", "Somewhat Unfamiliar": "Other"},
            ["Familiar", "Other"],
            "Familiar",
        ),
        "frequency": (
            "demo_frequency",
            {
                "Greater than 5 times per day": "Daily",
                "1–5 times per day": "Daily",
                "1–5 times per week": "Less",
                "1–5 times per month": "Less",
                "Fewer than 5 times ever": "Less",
            },
            ["Daily", "Less"],
            "Daily",
        ),
        "arm": ("arm", {"lab": "Laboratory", "crowd": "Crowd"}, ["Crowd", "Laboratory"], "Crowd"),
    },
}
FACTOR_ORDER = ("sex", "education", "familiarity", "frequency", "arm")
FACTOR_NAME = {"sex": "Sex", "education": "Education", "familiarity": "Familiarity", "frequency": "Use frequency", "arm": "Environment"}
FACTOR_TICK = {"sex": "Sex", "education": "Educa-\ntion", "familiarity": "Famili-\narity", "frequency": "Use\nfrequency", "arm": "Environ-\nment"}

# Katerina's own design (moderation_model_gold.py), refitted on Gold for reconciliation.
KAT_OUTCOMES = ("credibility", "helpfulness", "convincingness", "relevance", "neutrality", "behaviour_pushing", "behaviour_manipulate")
KAT_FACTORS = ("demo_sex", "demo_education", "demo_familiarity", "demo_frequency")
KAT_REF = {"demo_sex": "Male", "demo_education": "Bachelor's Degree", "demo_familiarity": "Familiar", "demo_frequency": "1–5 times per day"}

NAVY, CLAY, TEAL, SLATE, MIST, INK = "#1B3A4B", "#C45C26", "#2A6F6F", "#5C6B73", "#D5DDE3", "#12202A"


# ----------------------------------------------------------------------------- #
# helpers
# ----------------------------------------------------------------------------- #
def code_factor(person: pd.DataFrame, coding: str, factor: str) -> tuple[pd.Series, dict]:
    """Return the coded factor (Categorical, reference first) and a coding note."""
    col, mapping, levels, ref = LEVEL_MAPS[coding][factor]
    raw = person[col]
    coded = raw.map(mapping)
    note = {
        "source": col,
        "reference": ref,
        "levels": levels,
        "raw_counts": raw.value_counts(dropna=False).rename(index=lambda x: "missing" if pd.isna(x) else str(x)).to_dict(),
        "coded_counts": coded.value_counts(dropna=False).rename(index=lambda x: "excluded" if pd.isna(x) else str(x)).to_dict(),
        "excluded_raw": sorted({str(k) for k, v in mapping.items() if v is None} | ({"missing"} if raw.isna().any() else set())),
        "merged_raw": sorted(str(k) for k, v in mapping.items() if v is not None and sum(1 for vv in mapping.values() if vv == v) > 1),
    }
    small = coded.value_counts()
    small = small[small < MIN_LEVEL]
    if len(small):
        raise RuntimeError(f"{coding}/{factor}: level(s) below MIN_LEVEL after merging: {small.to_dict()}")
    ordered = [ref] + [lv for lv in levels if lv != ref]
    return pd.Categorical(coded, categories=ordered), note


def long_table(condition: pd.DataFrame, ads: pd.DataFrame, outcome: str) -> tuple[pd.DataFrame, tuple[str, ...]]:
    """Long person × condition table with the contrast codes for one outcome."""
    if outcome in RECALL:
        base = ads[["experiment_id", "condition", outcome]].copy()
        base = base[base["condition"].isin(sk.AD_CONDITIONS)]
        codes = ("inline_vs_block", "early_vs_late")
    else:
        base = condition[["experiment_id", "condition", outcome]].copy()
        codes = CONTRAST_CODES
    base = base.dropna(subset=[outcome])
    for cid in codes:
        base[cid] = base["condition"].map(sk.CONTRASTS[cid]).astype(float)
    return base, codes


def wide_d(condition: pd.DataFrame, ads: pd.DataFrame, outcome: str, cid: str) -> pd.Series:
    if outcome in RECALL:
        piv = ads.pivot_table(index="experiment_id", columns="condition", values=outcome, aggfunc="first")
        piv = piv.reindex(columns=list(sk.AD_CONDITIONS)).dropna()
        w = {c: sk.CONTRASTS[cid][c] for c in sk.AD_CONDITIONS}
        return sum(piv[c] * wgt for c, wgt in w.items() if wgt != 0.0).astype(float)
    w = sk.wide(condition, outcome)
    return sk.contrast_scores(w, cid)


def fit_mixed(formula: str, d: pd.DataFrame):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = smf.mixedlm(formula, d, groups=d["experiment_id"])
        try:
            res = model.fit(reml=True, method=["lbfgs"])
            if not res.converged:
                raise RuntimeError
        except Exception:
            res = model.fit(reml=True, method=["powell"])
    return res


def joint_wald(res, names: list[str]) -> dict:
    """Joint Wald chi-square on a set of fixed-effect coefficients."""
    fe = res.fe_params
    cov = res.cov_params()
    present = [n for n in names if n in fe.index]
    if not present:
        return {"wald_chi2": np.nan, "df": 0, "p_raw": np.nan}
    b = fe[present].to_numpy(dtype=float)
    v = cov.loc[present, present].to_numpy(dtype=float)
    try:
        w = float(b @ np.linalg.solve(v, b))
    except np.linalg.LinAlgError:
        w = float(b @ np.linalg.pinv(v) @ b)
    df = len(present)
    return {"wald_chi2": w, "df": df, "p_raw": float(stats.chi2.sf(w, df))}


def holm_within(table: pd.DataFrame, keys: list[str], p_col: str, out_col: str) -> pd.DataFrame:
    out = table.copy()
    out[out_col] = np.nan
    out[f"{out_col}_sig"] = False
    for _, idx in out.groupby(keys if len(keys) > 1 else keys[0], dropna=False).groups.items():
        p = out.loc[idx, p_col]
        ok = p.notna()
        if ok.sum() == 0:
            continue
        adj = multipletests(p.loc[ok].to_numpy(dtype=float), method="holm")[1]
        out.loc[p.index[ok], out_col] = adj
        out.loc[p.index[ok], f"{out_col}_sig"] = adj < 0.05
    return out


# ----------------------------------------------------------------------------- #
# declared re-estimation: contrast codes × factor, joint Wald per cell
# ----------------------------------------------------------------------------- #
def fit_family(condition: pd.DataFrame, ads: pd.DataFrame, person: pd.DataFrame,
               outcomes: tuple[str, ...] = OUTCOMES, codings: tuple[str, ...] = tuple(LEVEL_MAPS)) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    cells, levels, notes = [], [], {}
    for coding in codings:
        notes[coding] = {}
        for factor in FACTOR_ORDER:
            coded, note = code_factor(person, coding, factor)
            notes[coding][factor] = note
            fac = pd.DataFrame({"experiment_id": person["experiment_id"], "f": coded}).dropna(subset=["f"])
            fac["f"] = pd.Categorical(fac["f"], categories=coded.categories)
            ref = coded.categories[0]
            non_ref = [lv for lv in coded.categories if lv != ref]
            for outcome in outcomes:
                base, codes = long_table(condition, ads, outcome)
                d = base.merge(fac, on="experiment_id", how="inner")
                d["y"] = d[outcome]
                n_people = int(d["experiment_id"].nunique())
                formula = "y ~ (" + " + ".join(codes) + ") * f"
                res = fit_mixed(formula, d)
                for cid in codes:
                    names = [f"{cid}:f[T.{lv}]" for lv in non_ref]
                    jw = joint_wald(res, names)
                    # spread of the person-level contrast across levels (Likert points)
                    d_i = wide_d(condition, ads, outcome, cid)
                    grp = pd.DataFrame({"D": d_i}).join(fac.set_index("experiment_id")["f"], how="inner").dropna()
                    means = grp.groupby("f", observed=True)["D"].mean()
                    rec = {
                        "family": "demographic_lmm",
                        "coding": coding,
                        "outcome": outcome,
                        "outcome_label": NAME.get(outcome, outcome),
                        "contrast": cid,
                        "contrast_label": sk.CONTRAST_LABEL[cid],
                        "factor": factor,
                        "factor_label": FACTOR_NAME[factor],
                        "reference": ref,
                        "k_levels": int(len(coded.categories)),
                        "n": n_people,
                        "converged": bool(res.converged),
                        "level_means_D": json.dumps({str(k): round(float(v), 3) for k, v in means.items()}),
                        "spread_D": float(means.max() - means.min()),
                        "max_level": str(means.idxmax()),
                        "min_level": str(means.idxmin()),
                        **jw,
                    }
                    cells.append(rec)
                    for lv in non_ref:
                        name = f"{cid}:f[T.{lv}]"
                        if name not in res.fe_params.index:
                            continue
                        est = float(res.fe_params[name])
                        se = float(np.sqrt(res.cov_params().loc[name, name]))
                        z = est / se if se > 0 else np.nan
                        levels.append({
                            "coding": coding, "outcome": outcome, "contrast": cid, "factor": factor,
                            "level": lv, "reference": ref, "estimate": est, "se": se,
                            "ci95_lo": est - 1.96 * se, "ci95_hi": est + 1.96 * se,
                            "z": z, "p_raw": float(2 * stats.norm.sf(abs(z))) if np.isfinite(z) else np.nan,
                        })
    cells = pd.DataFrame(cells)
    cells = holm_within(cells, ["coding", "outcome"], "p_raw", "p_holm")
    return cells, pd.DataFrame(levels), notes


def fit_d_ols(condition: pd.DataFrame, ads: pd.DataFrame, person: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for coding in LEVEL_MAPS:
        for factor in FACTOR_ORDER:
            coded, _ = code_factor(person, coding, factor)
            fac = pd.Series(coded, index=person["experiment_id"].to_numpy(), name="f").dropna()
            for outcome in OUTCOMES:
                codes = ("inline_vs_block", "early_vs_late") if outcome in RECALL else CONTRAST_CODES
                for cid in codes:
                    d_i = wide_d(condition, ads, outcome, cid)
                    frame = pd.DataFrame({"D": d_i}).join(fac, how="inner").dropna()
                    frame["f"] = frame["f"].astype(str)
                    full = smf.ols("D ~ C(f)", frame).fit()
                    reduced = smf.ols("D ~ 1", frame).fit()
                    fstat, p_f, _ = full.compare_f_test(reduced)
                    rows.append({
                        "family": "demographic_d_ols", "coding": coding, "outcome": outcome, "contrast": cid,
                        "factor": factor, "n": int(len(frame)), "k_levels": int(frame["f"].nunique()),
                        "f": float(fstat), "p_raw": float(p_f),
                    })
    ols = pd.DataFrame(rows)
    return holm_within(ols, ["coding", "outcome"], "p_raw", "p_holm")


# ----------------------------------------------------------------------------- #
# Katerina's design on Gold: condition dummies × raw factor levels, raw p per term
# ----------------------------------------------------------------------------- #
def fit_katerina_design(condition: pd.DataFrame, person: pd.DataFrame) -> pd.DataFrame:
    df = condition.merge(person[["experiment_id", *KAT_FACTORS]], on="experiment_id", how="left")
    rows = []
    for outcome in dict.fromkeys(KAT_OUTCOMES + PRIMARY):  # ordered, credibility once
        for mod in KAT_FACTORS:
            d = df[["experiment_id", "condition", outcome, mod]].dropna().copy()
            vc = d[mod].value_counts()
            keep = vc[vc >= 3].index.tolist()  # her rule: >= 3 rows (not people)
            d = d[d[mod].isin(keep)].copy()
            d["m"] = d[mod].astype(str)
            ref = KAT_REF[mod] if KAT_REF[mod] in d["m"].unique() else sorted(d["m"].unique())[0]
            d["m"] = pd.Categorical(d["m"], categories=[ref] + sorted(lv for lv in d["m"].unique() if lv != ref))
            d["condition"] = pd.Categorical(d["condition"], categories=["no_ads", "block_early", "block_late", "inline_early", "inline_late"])
            d["y"] = d[outcome]
            res = fit_mixed("y ~ C(condition) * m", d)
            n_people = int(d["experiment_id"].nunique())
            people_per_level = d.groupby("m", observed=True)["experiment_id"].nunique().to_dict()
            for name in res.fe_params.index:
                if ":" not in name:
                    continue
                est = float(res.fe_params[name])
                se = float(np.sqrt(res.cov_params().loc[name, name]))
                z = est / se if se > 0 else np.nan
                cond = name.split("[T.")[1].split("]")[0]
                lvl = name.split("m[T.")[1].rstrip("]")
                rows.append({
                    "family": "katerina_design_on_gold", "outcome": outcome, "factor": mod, "reference": ref,
                    "condition_dummy": cond, "level": lvl, "n_people": n_people, "n_people_level": int(people_per_level.get(lvl, 0)),
                    "estimate": est, "se": se, "z": z,
                    "p_raw": float(2 * stats.norm.sf(abs(z))) if np.isfinite(z) else np.nan,
                    "converged": bool(res.converged),
                })
    out = pd.DataFrame(rows)
    out = holm_within(out, ["outcome", "factor"], "p_raw", "p_holm_factor")  # within outcome, within factor (her per-model view)
    out = holm_within(out, ["outcome"], "p_raw", "p_holm")  # within outcome across the four factors
    return out


# ----------------------------------------------------------------------------- #
# figure: board, mimicking beh_personality_board (same palette and bands)
# ----------------------------------------------------------------------------- #
def style() -> None:
    plt.rcParams.update({
        "figure.dpi": 140, "savefig.dpi": 300, "font.family": "DejaVu Sans", "font.size": 10,
        "axes.titlesize": 12, "axes.labelsize": 10, "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "text.color": INK,
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })


def board(cells: pd.DataFrame) -> None:
    cmap = ListedColormap([CLAY, "#E8C9B5", MIST, "#F2F4F6"])
    norm = BoundaryNorm([0, 0.05, 0.10, 0.50, 1.0001], cmap.N)
    codings = [("katerina", "Levels kept (sparse merged)"), ("collapsed", "Two-level coding")]
    fig, axes = plt.subplots(2, 3, figsize=(11.2, 6.6), sharey=True)
    for i_row, (coding, row_title) in enumerate(codings):
        for j_col, cid in enumerate(CONTRAST_CODES):
            ax = axes[i_row, j_col]
            block = cells[(cells.coding == coding) & (cells.contrast == cid)]
            grid_p = pd.DataFrame(np.nan, index=list(OUTCOMES), columns=list(FACTOR_ORDER))
            grid_s = grid_p.copy()
            for _, r in block.iterrows():
                grid_p.loc[r.outcome, r.factor] = r.p_holm
                grid_s.loc[r.outcome, r.factor] = r.spread_D
            data = grid_p.to_numpy(dtype=float)
            # cells as vector rectangles (imshow would embed a raster in the PDF)
            for i in range(len(OUTCOMES)):
                for j in range(len(FACTOR_ORDER)):
                    p = data[i, j]
                    face = cmap(norm(p)) if np.isfinite(p) else "white"
                    ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=face, edgecolor="white", lw=0.8))
            ax.set_xlim(-0.5, len(FACTOR_ORDER) - 0.5)
            ax.set_ylim(len(OUTCOMES) - 0.5, -0.5)
            for i, o in enumerate(OUTCOMES):
                if np.all(np.isnan(data[i])):
                    ax.text((len(FACTOR_ORDER) - 1) / 2, i, "not defined: no advertisement in the no-ad condition",
                            ha="center", va="center", fontsize=7, color=SLATE, style="italic")
                    continue
                for j, f in enumerate(FACTOR_ORDER):
                    p = data[i, j]
                    if np.isnan(p):
                        ax.text(j, i, "undefined", ha="center", va="center", fontsize=7, color=SLATE)
                        continue
                    ptxt = "<.001" if p < 0.001 else (f"{p:.2f}" if p >= 1 else f"{p:.2f}".lstrip("0"))
                    star = " *" if p < 0.05 else ""
                    ax.text(j, i, f"{grid_s.iloc[i, j]:.2f}\n{ptxt}{star}", ha="center", va="center", fontsize=8,
                            color="white" if p < 0.05 else INK, fontweight="bold" if p < 0.05 else "normal")
                    if p < 0.05:
                        ax.text(j + 0.42, i - 0.38, "*", ha="right", va="top", fontsize=13, color=CLAY, fontweight="bold")
            ax.set_xticks(range(len(FACTOR_ORDER)), [FACTOR_TICK[f] for f in FACTOR_ORDER], fontsize=8)
            ax.set_yticks(range(len(OUTCOMES)), [NAME[o] for o in OUTCOMES], fontsize=9)
            ax.set_title(CONTRAST_TITLE[cid] if i_row == 0 else "", fontsize=10)
            ax.tick_params(length=0)
            for s in ("top", "right", "left", "bottom"):
                ax.spines[s].set_visible(False)
        axes[i_row, 0].set_ylabel(row_title, fontsize=9)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in [CLAY, "#E8C9B5", MIST, "#F2F4F6"]]
    labels = ["Holm p < .05 (*)", ".05–.10", ".10–.50", "> .50"]
    axes[0, -1].legend(handles, labels, loc="upper left", bbox_to_anchor=(1.02, 1), frameon=False, fontsize=8)
    fig.text(0.01, 0.005, "Cell: spread of the mean within-person contrast across factor levels (Likert points) and Holm p of the joint contrast × factor Wald test, within outcome.",
             fontsize=7.5, color=SLATE)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "beh_demographics_board.pdf", format="pdf", bbox_inches="tight", facecolor="white")
    fig.savefig(FIG / "beh_demographics_board.png", format="png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {FIG / 'beh_demographics_board.pdf'}")


# ----------------------------------------------------------------------------- #
# table
# ----------------------------------------------------------------------------- #
def fmt_p(p: float) -> str:
    if pd.isna(p):
        return "--"
    if p < 0.001:
        return r"$<.001$"
    return f"${p:.3f}$".replace("$0.", "$.")


def table_tex(cells: pd.DataFrame, ols: pd.DataFrame) -> str:
    kat = cells[cells.coding == "katerina"].copy()
    col = cells[cells.coding == "collapsed"][["outcome", "contrast", "factor", "p_raw", "p_holm", "p_holm_sig"]]
    kat = kat.merge(col, on=["outcome", "contrast", "factor"], suffixes=("", "_collapsed"))
    if "p_holm_ols" not in kat.columns:  # cells passed without the OLS join
        o_ols = ols[ols.coding == "katerina"][["outcome", "contrast", "factor", "p_holm"]].rename(columns={"p_holm": "p_holm_ols"})
        kat = kat.merge(o_ols, on=["outcome", "contrast", "factor"])
    kat["outcome"] = pd.Categorical(kat["outcome"], list(OUTCOMES))
    kat["contrast"] = pd.Categorical(kat["contrast"], list(CONTRAST_CODES))
    kat["factor"] = pd.Categorical(kat["factor"], list(FACTOR_ORDER))
    kat = kat.sort_values(["outcome", "contrast", "factor"])
    lines = [
        r"\begin{table}[H]", r"\centering", r"\footnotesize",
        r"\caption{Demographic moderation of the planned contrasts (\(N=54\)): joint Wald on the contrast \(\times\) factor terms, Holm within outcome; two-level coding and OLS on \(D_i\) as checks.}",
        r"\label{tab:beh-demographics}",
        r"\setlength{\tabcolsep}{3.5pt}",
        r"\begin{tabular}{@{}ll l r r r r r r@{}}", r"\toprule",
        r"Outcome & Contrast & Factor (levels) & Spread & \(\chi^2\) (df) & Raw \(p\) & Holm \(p\) & Two-level & OLS \\",
        r"\midrule",
    ]
    last_oc = None
    for _, r in kat.iterrows():
        oc = (r.outcome, r.contrast)
        o_lab = NAME[r.outcome] if last_oc is None or last_oc[0] != r.outcome else ""
        c_lab = CONTRAST_TITLE[r.contrast].split(" (")[-1].rstrip(")").capitalize().replace("\u2212", r"\(-\)") if last_oc != oc else ""
        if last_oc is not None and last_oc[0] != r.outcome:
            lines.append(r"\midrule")
        cellvals = [
            f"{FACTOR_NAME[r.factor]} ({r.k_levels})",
            f"${r.spread_D:.2f}$",
            f"${r.wald_chi2:.2f}$ ({int(r.df)})",
            fmt_p(r.p_raw), fmt_p(r.p_holm), fmt_p(r.p_holm_collapsed), fmt_p(r.p_holm_ols),
        ]
        if bool(r.p_holm_sig):
            cellvals = [rf"\textbf{{{v}}}" for v in cellvals]
        lines.append(f"{o_lab} & {c_lab} & " + " & ".join(cellvals) + r" \\")
        last_oc = oc
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


# ----------------------------------------------------------------------------- #
def run() -> dict:
    EXPL.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    condition = pd.read_csv(GOLD / "condition_features.csv")
    ads = pd.read_csv(GOLD / "advertisement_features.csv")
    person = pd.read_csv(GOLD / "person_features.csv")

    cells, levels, notes = fit_family(condition, ads, person)
    ols = fit_d_ols(condition, ads, person)
    side = cells.merge(ols[["coding", "outcome", "contrast", "factor", "f", "p_raw", "p_holm", "p_holm_sig"]],
                       on=["coding", "outcome", "contrast", "factor"], suffixes=("", "_ols"))
    side["verdict"] = np.select(
        [side.p_holm_sig & side.p_holm_sig_ols, side.p_holm_sig & ~side.p_holm_sig_ols, ~side.p_holm_sig & side.p_holm_sig_ols],
        ["both", "LMM only", "OLS only"], default="neither",
    )
    side.to_csv(EXPL / "demographic_moderation_lmm.csv", index=False)
    levels.to_csv(EXPL / "demographic_moderation_levels.csv", index=False)

    kat = fit_katerina_design(condition, person)
    kat.to_csv(EXPL / "demographic_moderation_katerina_design.csv", index=False)

    # secondary outcomes under the declared design (her coding only); not the family
    sec, _, _ = fit_family(condition, ads, person, outcomes=SECONDARY, codings=("katerina",))
    sec["family"] = "demographic_lmm_secondary"
    sec.to_csv(EXPL / "demographic_moderation_secondary.csv", index=False)

    style()
    board(side)
    tex = table_tex(side, ols)
    (FIG / "tab_beh_demographics.tex").write_text(tex + "\n")
    OVERLEAF.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIG / "beh_demographics_board.pdf", OVERLEAF / "beh_demographics_board.pdf")
    shutil.copy(FIG / "tab_beh_demographics.tex", OVERLEAF / "tab_beh_demographics.tex")

    kat_raw = kat[kat.p_raw < 0.05].sort_values("p_raw")
    summary = {
        "n_people": int(person["experiment_id"].nunique()),
        "age_estimable": bool(person["demo_age"].notna().any()),
        "min_level_people": MIN_LEVEL,
        "coding_notes": notes,
        "family": {
            coding: {
                "n_cells": int((side.coding == coding).sum()),
                "holm_hits": int(side.loc[side.coding == coding, "p_holm_sig"].sum()),
                "raw_hits": int((side.loc[side.coding == coding, "p_raw"] < 0.05).sum()),
                "ols_holm_hits": int(ols.loc[ols.coding == coding, "p_holm_sig"].sum()),
                "ols_raw_hits": int((ols.loc[ols.coding == coding, "p_raw"] < 0.05).sum()),
                "converged": bool(side.loc[side.coding == coding, "converged"].all()),
                "lmm_vs_ols": side.loc[side.coding == coding, "verdict"].value_counts().to_dict(),
                "nearest": (
                    side[side.coding == coding].sort_values("p_raw").head(6)
                    [["outcome", "contrast_label", "factor", "k_levels", "spread_D", "max_level", "min_level", "level_means_D", "wald_chi2", "df", "p_raw", "p_holm"]]
                    .round(4).to_dict(orient="records")
                ),
            }
            for coding in LEVEL_MAPS
        },
        "secondary_sensitivity": {
            "outcomes": list(SECONDARY),
            "n_cells": int(len(sec)),
            "holm_hits": int(sec["p_holm_sig"].sum()),
            "raw_hits": int((sec["p_raw"] < 0.05).sum()),
            "nearest": sec.sort_values("p_raw").head(4)[["outcome", "contrast_label", "factor", "level_means_D", "wald_chi2", "df", "p_raw", "p_holm"]].round(4).to_dict(orient="records"),
        },
        "katerina_design_on_gold": {
            "outcomes": list(dict.fromkeys(KAT_OUTCOMES + PRIMARY)),
            "n_terms": int(len(kat)),
            "raw_hits": int(len(kat_raw)),
            "holm_within_outcome_hits": int(kat["p_holm_sig"].sum()),
            "holm_within_outcome_factor_hits": int(kat["p_holm_factor_sig"].sum()),
            "raw_hits_by_factor": kat_raw["factor"].value_counts().to_dict(),
            "raw_hit_cells": kat_raw[["outcome", "factor", "condition_dummy", "level", "n_people_level", "estimate", "p_raw", "p_holm_factor", "p_holm"]].round(4).to_dict(orient="records"),
            "converged": bool(kat["converged"].all()),
        },
    }
    (EXPL / "demographic_moderation_summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    return summary


if __name__ == "__main__":
    s = run()
    print(json.dumps({k: v for k, v in s.items() if k != "coding_notes"}, indent=2, default=str))
    print(f"Wrote {EXPL / 'demographic_moderation_lmm.csv'}")
