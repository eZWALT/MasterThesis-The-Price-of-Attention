"""Block 7. The one EEG quantity that is known to work in this cohort
(writing - reading, Fz theta +0.60 dB, Holm .007) as a person trait
against the behavioural and trajectory ad effects.

task_state_person_features.csv holds each laboratory participant's
median write - read difference per feature (18 rows). If frontal theta
reactivity is a stable individual property, people with a larger
write - read theta difference might also show larger (or smaller)
behavioural ad effects. Spearman with Bonett-Wright CI and
leave-one-out range; Holm within family.

Families:
  task_state_x_behaviour   {Fz theta, posterior alpha} write-read x
                           {trust, credibility, manipulation, notice} x
                           {3 planned D + person level}          32 tests
  task_state_x_trajectory  {Fz theta, posterior alpha} x
                           {n_shift, entropy} x 3 planned D       12 tests

Writes outputs/task_state/.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import combokit as ck
from combokit import sk

OUT = ck.OUT / "task_state"
TRAITS = {"ts_fz_theta": "fz_theta_power_db_uv2_median", "ts_posterior_alpha": "posterior_alpha_power_db_uv2_median"}


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    ts = pd.read_csv(ck.EEG_GOLD / "task_state" / "task_state_person_features.csv")
    ts = ts[ts.primary_analysis_eligible == "yes"][["subject_id"] + list(TRAITS.values())].rename(columns={v: k for k, v in TRAITS.items()})
    D = ck.load_D(); D = D[D.arm == "lab"]
    C = ck.load_conditions_lab()
    lvl = C.groupby("experiment_id")[ck.BEH_PRIMARY].mean().add_suffix("__level").reset_index()
    D = D.merge(lvl, on="experiment_id", how="left").merge(ts, on="subject_id", how="inner", validate="one_to_one")
    rows = []
    for tr in TRAITS:
        for b in ck.BEH_PRIMARY:
            for cid in list(sk.PLANNED) + ["level"]:
                r = ck.spearman_ci(D[tr], D[f"{b}__{cid}"])
                rows.append({"family": "task_state_x_behaviour", "trait": tr, "target": b, "contrast": cid, **r})
        for tv in ("traj_n_shift", "traj_entropy_nats"):
            for cid in sk.PLANNED:
                r = ck.spearman_ci(D[tr], D[f"{tv}__{cid}"])
                rows.append({"family": "task_state_x_trajectory", "trait": tr, "target": tv, "contrast": cid, **r})
    T = ck.holm_bh(pd.DataFrame(rows))
    T.to_csv(OUT / "task_state_tests.csv", index=False)
    D[["experiment_id", "subject_id"] + list(TRAITS)].to_csv(OUT / "task_state_traits_joined.csv", index=False)
    figure(T)
    summary = {"n": int(len(D)), "trait_descriptives": D[list(TRAITS)].describe().round(3).to_dict(),
               "hits_holm": {f: int(T[T.family == f].sig_holm_family.sum()) for f in T.family.unique()},
               "min_p_raw": {f: float(T[T.family == f].p_raw.min()) for f in T.family.unique()},
               "n_tests": {f: int(T[T.family == f].p_raw.notna().sum()) for f in T.family.unique()},
               "top": T.sort_values("p_raw").head(6)[["family", "trait", "target", "contrast", "n", "rho", "ci_lo", "ci_hi", "p_raw", "p_holm_family", "loo_sign_stable"]].round(3).to_dict(orient="records")}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def figure(T: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 8))
    T = T.copy(); T["label"] = T.trait.str.replace("ts_", "write−read ") + " × " + T.target.str.replace("traj_", "") + " " + T.contrast.map(lambda c: ck.PRETTY.get(c, c))
    for i, (_, r) in enumerate(T.iterrows()):
        c = "tab:red" if r.p_raw < 0.05 else "0.3"
        ax.plot([r.ci_lo, r.ci_hi], [i, i], color=c, lw=1); ax.plot(r.rho, i, "o", color=c, ms=4)
    ax.set_yticks(range(len(T)), T.label, fontsize=6.5); ax.invert_yaxis(); ax.axvline(0, color="k", lw=0.8); ax.set_xlim(-1, 1)
    ax.set_xlabel("Spearman rho (n = 18, 95% CI)")
    ax.set_title("Block 7: write−read EEG trait × behavioural / trajectory ad effects", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "task_state_forest.png", dpi=150); plt.close(fig)


if __name__ == "__main__":
    s = run()
    pd.set_option("display.width", 220)
    print({k: v for k, v in s.items() if k not in ("top", "trait_descriptives")})
    print(pd.DataFrame(s["top"]).to_string(index=False))
    print(f"Wrote {OUT}")
