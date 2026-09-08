"""Giant Spearman matrices at the person grain, plus the process descriptives.

Person-level means over the five conditions (54 people), joined with
BFI; a lab-only version adds the 16 EEG k=37 medians (18 people); and
a D-grain version on any-ad differences. Curiosity artefacts, not
tests: every dot is a raw p and the pair count is in the title.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402
import viz  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
OUT = WALTER / "behavioural" / "outputs" / "eda"

SURVEY = ["trust", "credibility", "manipulation", "notice", "helpfulness", "convincingness", "relevance", "neutrality",
          "personality_influence", "personality_changed_mind", "behaviour_pushing", "behaviour_manipulate",
          "notice_brands", "notice_sponsored"]
PROCESS = ["duration_sec", "time_to_first_user_sec", "reply_latency_ms_median", "user_msg_len_median",
           "user_n_words_median", "assistant_msg_len_median", "llm_latency_ms_median", "n_typing_events", "conclusion_n_words"]
BFI = ["bfi_e", "bfi_a", "bfi_c", "bfi_n", "bfi_o"]
TRAJ = ["traj_n_shift", "traj_shift_rate", "traj_diversity", "traj_entropy_nats", "traj_max_persistence",
        "traj_mean_js_divergence", "traj_mean_total_variation", "traj_shifted_into_purchasable"]
EEG = ["eeg_fz_theta", "eeg_posterior_alpha", "eeg_theta", "eeg_alpha", "eeg_beta", "eeg_delta", "eeg_gamma", "eeg_faa",
       "eeg_rel_delta", "eeg_rel_theta", "eeg_rel_alpha", "eeg_rel_beta", "eeg_rel_gamma", "eeg_engagement", "eeg_pope", "eeg_kislov"]
RECALL = ["recall_memory", "recall_trust_shift"]


def person_means() -> pd.DataFrame:
    combo = pd.read_csv(GOLD / "combo_threeway.csv")
    ads = pd.read_csv(GOLD / "advertisement_features.csv")
    num = [c for c in SURVEY + PROCESS + TRAJ + EEG if c in combo.columns]
    pm = combo.groupby("experiment_id")[num].mean()
    pm = pm.join(ads.groupby("experiment_id")[RECALL].mean())
    person = pd.read_csv(GOLD / "person_features.csv").set_index("experiment_id")
    pm = pm.join(person[BFI + ["arm"]])
    return pm


def any_ad_D() -> pd.DataFrame:
    d = pd.read_csv(GOLD / "combo_threeway_D.csv")
    keep = {c: c.replace("__any_ad_vs_no_ads", "") for c in d.columns if c.endswith("__any_ad_vs_no_ads")}
    out = d[["experiment_id", *keep]].rename(columns=keep).set_index("experiment_id")
    out = out.join(pd.read_csv(GOLD / "person_features.csv").set_index("experiment_id")[BFI + ["arm"]])
    return out


def process_table() -> pd.DataFrame:
    c = pd.read_csv(GOLD / "condition_features.csv")
    cols = ["duration_sec", "time_to_first_user_sec", "reply_latency_ms_median", "user_msg_len_median",
            "user_n_words_median", "assistant_msg_len_median", "n_typing_events", "conclusion_n_words"]
    g = c.groupby("condition")[cols].agg(["mean", "std"]).reindex(list(sk.CONDITIONS))
    g.index = [sk.LABEL[x] for x in g.index]
    return g.round(1)


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pm = person_means()
    groups = {**{c: "survey" for c in SURVEY}, **{c: "recall" for c in RECALL}, **{c: "process" for c in PROCESS},
              **{c: "bfi" for c in BFI}, **{c: "traj" for c in TRAJ}, **{c: "eeg" for c in EEG}}

    cols54 = [c for c in SURVEY + RECALL + PROCESS + BFI + TRAJ if c in pm.columns]
    f = viz.giant_corr(pm, cols54, "Person means, N = 54: surveys · recall · process · BFI · trajectory (blocked)", cluster=False, groups=groups)
    f.savefig(OUT / "giant_corr_person_blocked.png", dpi=130); f.rho_.round(3).to_csv(OUT / "giant_corr_person_rho.csv"); f.p_.round(4).to_csv(OUT / "giant_corr_person_p.csv"); plt.close(f)
    f = viz.giant_corr(pm, cols54, "Person means, N = 54, clustered", cluster=True)
    f.savefig(OUT / "giant_corr_person_clustered.png", dpi=130); plt.close(f)

    lab = pm[pm.arm == "lab"]
    cols18 = [c for c in SURVEY[:8] + RECALL + BFI + TRAJ[:5] + EEG if c in lab.columns]
    f = viz.giant_corr(lab, cols18, "Lab person means, n = 18: surveys · recall · BFI · trajectory · 16 EEG (blocked)", cluster=False, groups=groups)
    f.savefig(OUT / "giant_corr_lab_eeg_blocked.png", dpi=130); f.rho_.round(3).to_csv(OUT / "giant_corr_lab_rho.csv"); plt.close(f)

    dd = any_ad_D()
    colsD = [c for c in SURVEY + PROCESS + TRAJ if c in dd.columns] + BFI
    f = viz.giant_corr(dd, colsD, "Any-ad − no-ad person differences D_i, N = 54 (blocked)", cluster=False, groups=groups)
    f.savefig(OUT / "giant_corr_D_any_ad_blocked.png", dpi=130); f.rho_.round(3).to_csv(OUT / "giant_corr_D_any_ad_rho.csv"); plt.close(f)

    process_table().to_csv(OUT / "process_by_condition.csv")
    print(f"wrote giant correlation figures + process table to {OUT}")


if __name__ == "__main__":
    run()
