# v2 jury reconciliation (4 judges) — 15 Sep 2026, 17:05

Inputs: `jury-v2-grok-4.6.md` (GX), `jury-v2-chatgpt.md` (CG),
`jury-v2-gemini-flash.md` (GM), `jury-v2-deepseek.md` (DS). All read the
black v2 PDF (`e68be52`). Every claim below was checked against the `.tex`
and, where a number is involved, against Gold.

Method note. Round 1 needed subagent canonicalisation (six long dumps, a
brief that induced consensus). Round 2 is four short dumps under the
quote-or-drop prompt, so one reader reconciled directly. Verdicts:
**real** (change made), **already there** (judge missed it),
**artefact** (PDF reader error), **design** (true, not writable),
**his call** (abstract / taste).

## Scores

| | v1 | v2 |
|---|---|---|
| GX | 5.5 | 6.5 |
| CG | 6.5 | 7.2 |
| DS | — | 6.8 |
| GM | — | "near-submission shape" |

## Ranked issues

| # | Issue | Raised by | Verdict | What was done / why not |
|---|---|---|---|---|
| 1 | Retrieval wait (~3 s) on the advertised turn: "unquantified, not in Limitations" (GX); "#1 vulnerability, but now stated" (CG) | GX, CG | **already there + sharpened** | Was in §5.1.2 (median 3.03 s; 2.69 vs 2.89 s reply), Methods §6.2.5 bullet, Discussion Limitations. GX read past it; CG quotes it. Added the structural argument in both Methods and Discussion (`e0bf6cc`): the wait is the same procedure on every advertised turn, so it **cancels in the format and timing contrasts** and is carried only by any-ad − no-ads and by the onset-locked comparisons against \(a^{\emptyset}\). Methods bullet previously said "every contrast", which was wrong. No new analysis; the per-condition latency distribution is not Gold and stays out (science frozen). |
| 2 | Discussion §8.3 "six nominal cells out of 96" not in Results | DS D5/M5 | **real** | Gold `eeg_posthoc_pairwise_dataset_b.csv`: 96 tests in the declared space (6 pairs × 16), 6 raw \(p<.05\), 0 Holm; Dataset A 160 / 2 / 1; total 256 / 8 / 1. Added the split to Results §7.4 pairwise paragraph (green). |
| 3 | Table 7.8: Dataset A row "6 tests" vs Methods "16 measures × 3" | DS V2 | **real (caption)** | EEG block header now says the two confirmatory rows count the two declared measures, Fz θ and posterior α (green). Exploratory 14 measures already had their own row (98). |
| 4 | Model name "35B A3B" vs "35B-A3B" | DS m3 | **real** | Fixed in typo pass. |
| 5 | Acknowledgments typos, "datasetm", bare "i.e" | GM | **real** | Fixed in typo pass (`4f48b30`). |
| 6 | Abstract "candidate neural correlate of a trust drop" stronger than Discussion | CG, GM | **his call** | Not a contradiction: correlate ≠ captured attention; Abstract already says "to be tested in replication". Abstract is edited last, by one agent, on Walter's word. |
| 7 | Conclusion tilt "↑β,β;↓α,β" | DS M1/D2 | **artefact** | Source: `\uparrow\delta,\theta;\downarrow\alpha,\beta`. DS reader maps δ, θ → β (same as v1). |
| 8 | Theory `\hat g_k` used for label and shift | DS M2/D4/V3 | **artefact** | Def. 2 uses `\delta_k`. |
| 9 | Results 7.5 / Fig 7.10 use β^(a) | DS M3/D3 | **artefact** | Source is `\delta^{(a)}`. |
| 10 | Table 6.1 "y*min − y*med" | DS m1/D6 | **artefact** | Source `y^{write} − y^{read}`. |
| 11 | Fig 4.5 "Fz \hat θ_i" | DS m2 | **artefact** | Source `Fz \(\theta\)`. |
| 12 | Abstract +1.27 manipulation "not traceable to Table 7.8" | DS M4/D1, GX verify | **not an issue** | Traces to Table 7.2 (behavioural key estimates), which is a Results table. 7.8 shows one representative row per family by design. |
| 13 | Abstract "8 in 10 vs 6 in 10" approximations | DS m4 | **his call** | Results give 87/81 vs 57/59 %. Approximation is legitimate in an abstract. |
| 14 | Trust LMM .048 vs Abstract "did not differ on any planned contrast" | DS V1 | **not an issue** | Planned estimator is paired \(t\) (Holm .063); LMM is the adjusted check. Abstract says "planned". Already explicit in Results and Table 7.2. |
| 15 | Classifier validity 32.5 % / theory "remains to be validated" | GX | **design** | Limitation is stated (Ch 8 trajectories, RQ table "not testable here"). Owning it in the viva, not more prose. |
| 16 | Disclosure θ confounded with format λ | GX, CG | **design** | Stated in Methods §6.2.5 and Limitations. |
| 17 | Dataset A early−late posterior α, Holm .0496, depth-confounded | GX | **design** | Stated in Abstract, Results, Discussion. |
| 18 | Task factor not modelled; arm not a factor | GX minor | **design / already there** | Arm: `tab:beh-arm-cells` sign-consistency in Limitations (v2). Task: Latin square balances it; not adding a model. |
| 19 | Bridging sentence in Ch 3 to Ch 8 on classifier granularity | GM | **skip** | Theory chapter should not pre-empt results; Ch 8 already does this. |
| 20 | Tabulate hardware specs | GM | **skip** | §5.2 and §5.4 already give GPUs, VRAM, KV-cache arithmetic. |
| 21 | Numbers wrapped in math in prose ("32 channels, 500 Hz") | GM | **cosmetic, skip** | Not worth a pass this week. |

## What is left for v3

- Green from `4f48b30` + `e0bf6cc` for Walter to read (Results §7.4, Table 7.8 header, Methods latency bullet, Discussion Limitations wait sentence).
- Abstract sentence (#6) and 8-in-10 wording (#13): his decision, applied last.
- Nothing else from round 2 needs writing. GX's four MAJORs are design limits already in the text; DS's five MAJORs are reader artefacts.
