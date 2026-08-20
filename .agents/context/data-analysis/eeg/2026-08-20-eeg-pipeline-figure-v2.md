# Publication EEG preprocessing figure v2

Date: 20 August 2026

## What this is

The thesis-page figure of laboratory EEG **preprocessing**. It is not a
statistics figure.

- Frozen original (6 Aug, do not edit): `src/project/docs/eeg_pipeline/eeg_pipeline.py` and `.png` / `.pdf` / `.svg`
- Working figure: `eeg_pipeline_v2.py` → `eeg_pipeline_v2.png` / `.pdf` / `.svg`
- Rebuild: `python src/project/docs/eeg_pipeline/eeg_pipeline_v2.py`

## Walter 20 Aug (third pass)

- Header is **19 people · 32 channels · 500 Hz recording**. No “4 s epochs”
  and no “ICA primary” in the title bar. 19 is the recorded lab set;
  Bronze still states Subject 4 out, so Gold tensors stay \(n=18\).
- Path A / Path B subtexts must say what the **5** and **6** are:
  5 conditions; 4 ads + 2 matched no-ad.
- Welch / PSD / bands live in **Gold**, not Silver. They are the shared
  measurement after cleaning: 2 s window, 50% overlap, \(\delta\theta\alpha\beta\gamma\),
  16 features.
- Silver cards must cover every transform in the Silver scripts +
  `clean_recording()`. Do not invent extras.

Window names stay **condition windows** / **ad windows**.

## Silver checklist (figure vs code)

| Figure card | Code | What it does |
|---|---|---|
| Marker audit | `silver/markers/audit_marker_anomalies.py` | duplicates / missing / extras |
| Align event clocks | `build_canonical_markers.py` | JSONL ↔ XDF LSL |
| Canonical markers | `build_canonical_markers.py` | observed or reconstructed timeline |
| XDF → MNE Raw | `xdf_to_mne.py` | µV → V, `(N,32)` → `(32,N)`, 10–20, annotations. No filter, no resample |
| Channel QC | `audit_signal_quality.py` + policy `subject_specific_interpolation` | condition-blind flags ∪ reviewed bads |
| Notch 50 Hz | `clean_eeg.py` | mains |
| 0.5–40 Hz | `clean_eeg.py` | band-pass |
| Average ref | `clean_eeg.py` | exclude marked bads |
| Spline interp | `clean_eeg.py` | spherical spline; `reset_bads=false` |
| ICA | `ica_cleaning.py` | FastICA, 99% PCA variance, ≤3 ocular (Fp1/Fp2) |

Off the figure on purpose (checks, not transforms):
`validate_marker_reconstruction.py`, `verify_recovery_invariants.py`,
`audit_xdf_mne.py`, visual cleaning validation, no-ICA sensitivity.

Cleaning is still lazy: no cleaned `.fif`. Ad-window onset is Gold Path B.

## Shape rail

The 18 is an axis on every cohort object. Honesty is the subscript on
the ragged length, not omitting the 18.

The line next to **Shape** only defines the symbols:
\(T_i\): samples for person \(i\). \(K_i\): complete 4 s epochs for
person \(i\). No Path A/B or leftover prose there.

Do **not** write \(X \in \mathbb{R}^{18 \times 32 \times T}\) or
\(E \in \mathbb{R}^{18 \times K \times 32 \times 2000}\) with a shared
\(T\) or \(K\). Write \(T_i\) and \(K_i\).

\[
X \in \mathbb{R}^{18 \times 32 \times T_i}
\to
\tilde{X} \in \mathbb{R}^{18 \times 32 \times T_i}
\to
E \in \mathbb{R}^{18 \times K_i \times 32 \times 2000}
\to
Y_A \in \mathbb{R}^{18 \times 5 \times 16},\;
Y_B \in \mathbb{R}^{18 \times 6 \times 16}
\]

- \(X\), \(\tilde{X}\): 18 people × 32 channels × \(T_i\) samples.
  Cleaning does not drop channels or samples, so \(T_i\) is unchanged.
  ICA does not add an axis. \(T_i\) is not shared across people.
- One epoch **cell** is always \(\mathbb{R}^{32 \times 2000}\) (4 s ×
  500 Hz). The rail object is the cohort stack: 18 people × \(K_i\)
  epochs × 32 × 2000.
- Path A: \(K_i\) = complete non-overlapping 4 s tiles (includes
  baseline windows used for the delta). Leftover \(< 4\) s is
  **dropped**, not padded. Primary cohort: 9,468 tiled rows, 9,438
  retained. \(K_i\) therefore varies across people.
- Path B: \(K_i = 12 = 6 \times \{\text{pre},\text{post}\}\) when every
  locked 4 s cell is kept (primary: 216 = 18 × 12, all retained). Each
  window **is** the epoch.
- \(Y_A\), \(Y_B\): collapse after features. Path A: median (also
  writes IQR and baseline delta); baseline dropped, so 5 conditions.
  Path B: post − pre, so 6 onsets. These are the first *regular*
  tensors (shared second axis). No intermediate `y(16)` on the rail.

## Gold (on the figure)

Shared Gold stack (both paths, `spectral_features()` in
`build_condition_features.py`):

1. Shared Gold is a **sequence**: Epoch slicing → peak-to-peak reject
   (any channel above 1050 µV) → Welch PSD (2 s, 50% overlap) →
   16 features. Last feature line:
   \(\delta\theta\alpha\beta\gamma\) **band dB and relative** (same five
   bands; relative = band / total 0.5–40 Hz), plus Fz \(\theta\),
   posterior \(\alpha\), FAA, Pope (global, FC), Kislov.

Silver is **two jobs**. Top panel: **Event preprocessing** (audit,
align clocks, canonical markers). Bottom panel: **EEG signal QC and
preprocessing** (XDF→MNE, channel QC, then notch → band-pass →
average ref → spline → ICA). Do not use Time / Load / Clean.
2. \(E \in \mathbb{R}^{18 \times K_i \times 32 \times 2000}\) on the
   shape rail (Path A \(K_i\) varies; Path B \(K_i=12\)). The cell
   remains \(\mathbb{R}^{32\times 2000}\). Keep the 18 on \(E\). Do
   not hide it in the caption or draw one epoch as the cohort object.
3. Under \(Y_A\): median, IQR, baseline delta (what
   `condition_features.csv` writes per feature). Primary tests still
   use the median. Under \(Y_B\): post − pre.

ICA card: **99% variance · ≤3 ocular**. Do not write FastICA.

`nperseg = 2 * sfreq`, `noverlap = nperseg / 2`, \(\Delta f = 0.5\) Hz.
Bands: delta 0.5–4, theta 4–8, alpha 8–13, beta 13–30, gamma 30–40.
The 16 are 5 band dB + 5 relative + Fz theta + posterior alpha + FAA +
Pope (global, FC) and Kislov.

| Path | Subtext | Tensor axes |
|---|---|---|
| A | 4 s epochs · **5 conditions** | \(18\) people × \(5\) conditions × \(16\) features |
| B | 4 s epochs · **4 ads + 2 no-ad** | \(18\) people × \(6\) onsets × \(16\) features |

Five conditions: `block_late`, `block_early`, `inline_late`,
`inline_early`, `no_ads`. Baseline is computed and then dropped from
\(Y_A\). Path B: four labelled ads + two matched no-ad controls; each
onset is a 4 s pre / 4 s post pair. The window **is** the epoch.

Caption / Method only: leftover < 4 s dropped, median-of-epoch-dB
(Path A), 1050 µV rejection, Holm.

## Keep (do not regress)

- Four bands: Ingestion / Bronze / Silver / Gold.
- Paths are parallel.
- No \(D\), Holm, TEST, or statistics boxes.
- Paper size, not a 17-inch dashboard.
- Cohort: 18 lab; Subject 4 out.

## Not done in this figure

Statistics, C1, Overleaf inclusion. Do not commit or push Overleaf unless
Walter asks.
