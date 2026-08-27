# Teaching-atlas band regions, mapped onto this cap

Date: 25 August 2026. Sensitivity proposal only. Not confirmatory.
Not EEG 6.3. Not a replacement for all-32 globals.

The teaching texts do **not** publish per-band electrode tuples.
They name **regions**. The electrode lists below are this project's
map of those regions onto the recorded 32-channel 10–20/10–10 cap.
That mapping step is ours and must be labelled as such.

## One course / one teaching line

Picked: American Epilepsy Society introductory atlas, the text AES
gives educators and students.

Britton JW, Frey LC, Hopp JL, et al. *Electroencephalography (EEG):
An Introductory Text and Atlas of Normal and Abnormal Findings in
Adults, Children, and Infants.* St. Louis EK, Frey LC, eds. Chicago:
American Epilepsy Society; 2016.
https://www.ncbi.nlm.nih.gov/books/NBK390354/
doi:10.5698/978-0-9979756-0-4

Open on NCBI Bookshelf. Chapters used:

- “An orderly approach…”, Bookshelf ID `NBK390342`
- “The Normal EEG”, Bookshelf ID `NBK390343`
- “Additional texts and recommended readings”, `NBK390344`

Authors are at Mayo Clinic, University of Colorado, University of
Maryland, George Washington, UAB, Cleveland Clinic. AES also runs
the EEG Essentials curriculum on the same material.

That atlas's own student bibliography (the list they print) is:

- Schomer DL, Lopes da Silva F, eds. *Niedermeyer's
  Electroencephalography.* 6th ed. 2010.
- Fisch B. *Fisch and Spehlmann's EEG Primer.* 3rd ed. 1999.
- Tatum WO et al. *Handbook of EEG Interpretation.* 2007.
- Yamada T, Meng B. *Practical Guide for Clinical Neurophysiologic
  Testing.* 2010–2011.
- Hirsch LJ, Brenner RP. *Atlas of EEG in Critical Care.* 2010.

A university course that assigns the same primers: Labouré College
NDT introductory EEG course (required: Rowan *Primer of EEG*;
Yamada & Meng). An engineering lecture that teaches the same five
bands but does **not** name electrodes: UC San Diego BE280A,
Tzyy-Ping Jung, “Introduction to Electroencephalogram”
(https://fmri.ucsd.edu/ttliu/be280a_12/BE280A12_IntrotoEEG.pdf).

Signal-processing textbook used as a check (same regions, still no
electrode tuples): Sanei S, Chambers JA. *EEG Signal Processing.*
Wiley, 2007. Ch. 1. Hosted as a course text at
https://faculty.washington.edu/seattle/brain-physics/textbooks/sanei.pdf

## What those pages actually say (quotes)

AES, frequency bands (`NBK390342`):

> “1 to 3 cycles per second (Hz) are delta, 4 to 7 Hz are theta,
> 8 to 12 Hz are alpha, and 13 Hz and higher are beta.
> Frequencies above 25 Hz are not commonly encountered in the
> scalp EEG … these frequencies are termed gamma.”

AES, alpha (`NBK390343`):

> “the posteriorly dominant alpha rhythm, also known simply as
> the posterior dominant rhythm.”
> “The alpha generator is thought to be located within the
> occipital lobes.”

AES, beta (`NBK390343`):

> “The remainder of the normal waking EEG is usually composed of
> lower amplitude beta frequencies in the fronto-centro-temporal
> head regions.”
> “Beta is often enhanced during drowsiness, seen in a precentral
> distribution, and felt to be related to the functions of the
> sensorimotor cortex.”

AES, theta / delta in the waking adult (`NBK390343`):

> “Occasional slower theta (4–7 Hz) or even delta (1–3 Hz)
> frequencies transiently may be seen during normal wakefulness,
> but usually these slower activities only become prominent
> during drowsiness.”
> Drowsy bursts: “frontally dominant theta activity”
> (their Figure 10, child).
> Vertex waves of N1: “fronto-centrally predominant.”

Sanei & Chambers 2007, Ch. 1 (same geography, still no names):

- α: “appear in the posterior half of the head and are usually
  found over the occipital region … all parts of posterior lobes
  … higher amplitude over the occipital areas.”
- β: “Rhythmical beta activity is encountered chiefly over the
  frontal and central regions.” Figure 1.7 caption also says
  beta “appears frontally and parietally.”
- γ: “The regions of high EEG frequencies and highest levels of
  cerebral blood flow … are located in the frontocentral area.”
- δ / θ: sleep / drowsiness. No waking electrode set. Sanei
  warns that neck/jaw muscle is easy to confuse with delta.

UCSD Jung lecture table: δ “generally broad or diffused”;
θ “usually regional, may involve many lobes”; α “regional,
usually involves entire lobe”; β “localized”; γ “very localized.”
No electrode names.

None of these sources say “δ = F3 Fz F4” or “θ = T7 T8.”

## Map of those regions onto this cap

Recorded sites:
`Fp1 Fz F3 F7 F9 FC5 FC1 C3 T7 CP5 CP1 Pz P3 P7 P9 O1 Oz O2 P10 P8 P4 CP2 CP6 T8 C4 Cz FC2 FC6 F10 F8 F4 Fp2`

Classic 10–20 letters only (no extra 10–10 sites unless the
region word requires them). P7/P8 stay out of “parietal”
because the 10–20 convention places them on posterior temporal
cortex (same note as Wang §2.1; AES lobe letters are F T P O).

| Band | Region the text names | Sensors on this cap |
|---|---|---|
| α | posterior head / occipital / posterior lobes | O1 Oz O2 P3 Pz P4 |
| β | fronto-centro-temporal; precentral / sensorimotor | F3 Fz F4 F7 F8 C3 Cz C4 T7 T8 |
| θ | frontally / fronto-centrally (the only waking location they name) | F3 Fz F4 FC1 FC2 C3 Cz C4 |
| δ | frontally dominant slow bursts; otherwise “broad” | F3 Fz F4 F7 F8 |
| γ | not a routine scalp rhythm in AES; Sanei: frontocentral | F3 Fz F4 FC1 FC2 C3 Cz C4 |

Hz edges stay Angela / Zheng / Cochran (δ 0.5–4, θ 4–8, α 8–13,
β 13–30, γ 30–40). Derived measures stay `current_v1`
(Fz theta = Fz; posterior alpha = the six posterior sites already
above). Cleaning stays 32-channel.

## What this is not

- Not confirmatory. Primary globals stay all 32.
- Not George 2025 (one nine-site montage, all bands).
- Not Wang 2022 (left C/P/T theta is not in the teaching atlas).
- Not a claim that AES published these electrode strings.
- Waking δ and scalp γ are the weak rows: the atlas treats
  prominent waking delta as abnormal and gamma as mostly
  intracranial. Those two averages are the most “mapped by us.”

Filled as `teaching_atlas_v0`. The atlas can be cited for the
**region words**, not for these electrode strings. NCBI HTML has no
print page numbers; cite the chapter URLs above.
