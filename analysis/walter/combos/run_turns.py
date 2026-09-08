"""Block 4. Behaviour x trajectory at the turn grain.

The D-grain behaviour x trajectory family correlates 54 person-level
differences of chat-level summaries. Here the unit is the user turn
(1,080 user turns = 54 people x 5 chats x 4 turns; genre_source =
utterance), with a person random intercept and a conversation
variance component, so within-chat process (how long, how fast) and
within-chat genre movement are related directly.

Family A, shift x process (turns 2-4, 810 turns):
    log(characters) ~ delta_in + C(turn) + late + explicit + no_ad + pos
    log(latency)    ~ delta_in + ...
  and the same with js_in (continuous divergence from the previous
  turn) in place of delta_in. Is a turn that changes genre shorter,
  longer, slower?

Family B, the post-ad turn (turns 3-4, 540 turns):
  early ads appear in reply 2, so turns 3 and 4 are the only user
  turns written after seeing an ad; late ads (reply 4) have no
  post-ad user turn. post_ad = 1 in the two early conditions.
    y ~ post_ad + late_chat + C(turn) + pos + C(task_genre), y in
    {delta_in (GEE binomial), js_in, log(characters), log(latency),
     logit p(purchasable products)}
  Then the same split by format (implicit-early vs explicit-early
  post-ad turns against everything else).

All models carry C(task_genre): task assignment to condition is
randomised per person, not counterbalanced (implicit-late drew 30/54
Transactional tasks, no-ad 27/54 Social), and turn-2 shift
probability, before any ad is on screen, already differs by task
genre (Transactional .71, Informational .87; by condition chi-square
p = .17).

Holm within each family. Writes outputs/turns/.
"""

from __future__ import annotations

import json
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

import combokit as ck

OUT = ck.OUT / "turns"
UTT = ck.REPO / "analysis/trajectories/outputs/utterances.csv"


def prepare() -> pd.DataFrame:
    u = pd.read_csv(UTT)
    u = u[u.genre_source == "utterance"].copy()
    u["person"] = u["experiment_id"]
    u["log_chars"] = np.log(u["characters"].clip(lower=1))
    u["log_latency"] = np.log(u["latency_seconds"].clip(lower=0.5))
    p = u["p_purchasable_products"].clip(1e-4, 1 - 1e-4)
    u["logit_purchasable"] = np.log(p / (1 - p))
    u["late"] = (u["timing"] == "late").astype(float)
    u["explicit"] = (u["presentation"] == "explicit").astype(float)
    u["no_ad"] = (u["condition"] == "no_ads").astype(float)
    u["pos_c"] = u["session_position"] - u["session_position"].mean()
    u["post_ad"] = ((u["timing"] == "early") & (u["turn"] > 2)).astype(float)
    # a late-ad chat has shown nothing by turns 3-4 but will show an ad in reply 4; kept as its own indicator
    u["late_chat"] = (u["timing"] == "late").astype(float)
    u["post_ad_implicit"] = u["post_ad"] * (1 - u["explicit"])
    u["post_ad_explicit"] = u["post_ad"] * u["explicit"]
    return u


def fit_lmm(formula: str, d: pd.DataFrame):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = smf.mixedlm(formula, d, groups=d["person"], re_formula="1", vc_formula={"conv": "0 + C(conversation_id)"})
        for method in (["lbfgs"], ["powell"], ["nm"]):
            try:
                r = m.fit(method=method, reml=True, maxiter=3000)
                if np.all(np.isfinite(r.bse.to_numpy())):
                    return r
            except Exception:  # noqa: BLE001
                continue
    return None


def fit_gee(formula: str, d: pd.DataFrame):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = smf.gee(formula, groups=d["person"], data=d, family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable())
        return m.fit()


def row(res, term: str, **meta) -> dict:
    if res is None or term not in res.params.index:
        return {**meta, "term": term, "beta": np.nan, "se": np.nan, "p_raw": np.nan}
    ci = res.conf_int().loc[term]
    return {**meta, "term": term, "beta": float(res.params[term]), "se": float(res.bse[term]), "z": float(res.tvalues[term]),
            "p_raw": float(res.pvalues[term]), "ci_lo": float(ci.iloc[0]), "ci_hi": float(ci.iloc[1])}


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    u = prepare()
    rows = []
    # Family A: shift x process, turns 2-4
    a = u[u.turn >= 2].dropna(subset=["delta_in", "js_in", "log_chars", "log_latency"]).copy()
    for y in ("log_chars", "log_latency"):
        for x in ("delta_in", "js_in"):
            r = fit_lmm(f"{y} ~ {x} + C(turn) + late + explicit + no_ad + pos_c + C(task_genre)", a)
            rows.append(row(r, x, family="A_shift_x_process", outcome=y, n_obs=len(a), n_persons=a.person.nunique(), n_chats=a.conversation_id.nunique(), estimator="LMM person + conversation"))
    # Family B: post-ad turn, turns 3-4
    b = u[u.turn >= 3].dropna(subset=["delta_in", "js_in", "log_chars", "log_latency"]).copy()
    for y in ("js_in", "log_chars", "log_latency", "logit_purchasable"):
        r = fit_lmm(f"{y} ~ post_ad + late_chat + C(turn) + pos_c + C(task_genre)", b)
        rows.append(row(r, "post_ad", family="B_post_ad_turn", outcome=y, n_obs=len(b), n_persons=b.person.nunique(), n_chats=b.conversation_id.nunique(), estimator="LMM person + conversation"))
        r2 = fit_lmm(f"{y} ~ post_ad_implicit + post_ad_explicit + late_chat + C(turn) + pos_c + C(task_genre)", b)
        for term in ("post_ad_implicit", "post_ad_explicit"):
            rows.append(row(r2, term, family="B2_post_ad_by_format", outcome=y, n_obs=len(b), n_persons=b.person.nunique(), n_chats=b.conversation_id.nunique(), estimator="LMM person + conversation"))
    g = fit_gee("delta_in ~ post_ad + late_chat + C(turn) + pos_c + C(task_genre)", b)
    rows.append(row(g, "post_ad", family="B_post_ad_turn", outcome="delta_in (log-odds)", n_obs=len(b), n_persons=b.person.nunique(), n_chats=b.conversation_id.nunique(), estimator="GEE binomial exch. person"))
    g2 = fit_gee("delta_in ~ post_ad_implicit + post_ad_explicit + late_chat + C(turn) + pos_c + C(task_genre)", b)
    for term in ("post_ad_implicit", "post_ad_explicit"):
        rows.append(row(g2, term, family="B2_post_ad_by_format", outcome="delta_in (log-odds)", n_obs=len(b), n_persons=b.person.nunique(), n_chats=b.conversation_id.nunique(), estimator="GEE binomial exch. person"))
    T = ck.holm_bh(pd.DataFrame(rows))
    T.to_csv(OUT / "turn_tests.csv", index=False)

    # descriptives: shift rate, chars, latency by turn x condition; genre x process
    desc = u.groupby(["condition", "turn"]).agg(n=("turn", "size"), shift_rate=("delta_in", "mean"), js_in=("js_in", "mean"),
                                                 chars_median=("characters", "median"), latency_median=("latency_seconds", "median"),
                                                 p_purchasable_mean=("p_purchasable_products", "mean")).reset_index()
    desc.to_csv(OUT / "turn_descriptives.csv", index=False)
    genre = u.groupby("genre").agg(n=("turn", "size"), chars_median=("characters", "median"), latency_median=("latency_seconds", "median"),
                                   share=("turn", lambda s: len(s) / len(u))).sort_values("n", ascending=False).reset_index()
    genre.to_csv(OUT / "genre_x_process.csv", index=False)
    figure(u, T)
    summary = {"n_user_turns": int(len(u)), "n_persons": int(u.person.nunique()), "n_chats": int(u.conversation_id.nunique()),
               "hits_holm": {f: int(T[T.family == f].sig_holm_family.sum()) for f in T.family.unique()},
               "min_p_raw": {f: float(T[T.family == f].p_raw.min()) for f in T.family.unique()},
               "tests": T[["family", "outcome", "term", "beta", "se", "p_raw", "p_holm_family"]].round(4).to_dict(orient="records")}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def figure(u: pd.DataFrame, T: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    order = list(ck.sk.CONDITIONS)
    colors = {"no_ads": "k", "inline_early": "tab:blue", "inline_late": "tab:cyan", "block_early": "tab:red", "block_late": "tab:orange"}
    for ax, (col, title) in zip(axes, (("delta_in", "P(genre shift into turn)"), ("characters", "median characters"), ("latency_seconds", "median latency (s)"))):
        for cond in order:
            s = u[u.condition == cond].groupby("turn")[col]
            y = s.mean() if col == "delta_in" else s.median()
            ax.plot(y.index, y.to_numpy(), "o-", color=colors[cond], label=ck.sk.LABEL[cond], lw=1.2, ms=4)
        ax.axvspan(2.5, 4.5, color="tab:red", alpha=0.06)
        ax.text(3.5, ax.get_ylim()[1], "post-ad for early ads", ha="center", va="top", fontsize=7, color="tab:red")
        ax.set_xticks([1, 2, 3, 4]); ax.set_xlabel("user turn"); ax.set_title(title, fontsize=10)
    axes[0].legend(fontsize=7)
    fig.suptitle("Block 4: user turns by condition (54 people, 270 chats). Early ads are shown in reply 2, so turns 3-4 are post-ad only there.", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "turn_profiles.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    sub = T.copy(); sub["label"] = sub.family.str.split("_").str[0] + " | " + sub.outcome + " ~ " + sub.term
    for i, (_, r) in enumerate(sub.iterrows()):
        c = "tab:red" if r.p_raw < 0.05 else "0.3"
        se = r.se if np.isfinite(r.se) else 0
        ax.plot([r.beta - 1.96 * se, r.beta + 1.96 * se], [i, i], color=c, lw=1); ax.plot(r.beta, i, "o", color=c, ms=4)
        ax.text(1.02, i, f"raw {r.p_raw:.3f}  Holm {r.p_holm_family:.2f}", va="center", fontsize=7, transform=ax.get_yaxis_transform())
    ax.set_yticks(range(len(sub)), sub.label, fontsize=7); ax.invert_yaxis(); ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("coefficient (outcome units; log for chars/latency, log-odds for delta_in)")
    ax.set_title("Block 4 tests: mixed models with person + conversation effects", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "turn_forest.png", dpi=150, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    s = run()
    pd.set_option("display.width", 220)
    print({k: v for k, v in s.items() if k != "tests"})
    print(pd.DataFrame(s["tests"]).to_string(index=False))
    print(f"Wrote {OUT}")
