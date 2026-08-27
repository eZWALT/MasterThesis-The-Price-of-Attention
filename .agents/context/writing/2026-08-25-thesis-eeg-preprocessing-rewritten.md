# Thesis EEG preprocessing and epoching rewritten (25 August)

Status: **pushed to the thesis Overleaf 25 August (`28c22c8`)**, touching only
`chapters/dataset.tex`. Source of truth is the Overleaf LaTeX.

## Why

The condensation of 23 August went too far. `\subsubsection{Preprocessing}`
had become three telegraphic paragraphs ("Bronze holds the XDF immutably...",
"Silver events audit and align...") that named every transform and explained
none of them. Walter's read: "so short and bad its awful to read it looks like
a bad llm wrote it". The paper (`sec:eeg-preprocessing`, marked GOLDEN) is the
register to match, and the thesis has room to be more pedagogical than the
paper, not less.

## What changed

`\subsubsection{Preprocessing}` is now four named paragraphs plus a closing
shape rail:

- Opening: why the zones are separated at all (a decision taken once cannot be
  revisited quietly), not a re-listing of the lake, which the Description
  subsection above already gives.
- `Ingestion and Bronze.` two files tied by an identity map; Bronze computes no
  spectrum; the cohort is settled here (19 recorded, Subject 4 crowd protocol,
  \(n=18\) downstream).
- `Silver: the event clock.` why two clocks disagree, canonical marker =
  observed or reconstructed, interface events and not brain events.
- `Silver: from a raw file to a clean recording.` MNE Raw with nothing filtered
  at read time; the twelve 30 s condition-blind quality windows and the fact
  that they only warn; the three reviewed interpolations. Then the four
  transforms **with their purpose stated**: notch for mains hum that would land
  in gamma, band-pass for sweat drift and muscle/equipment noise, average
  reference because an EEG value is a potential difference (equation kept),
  spherical-spline so a bad channel is not a hole. Then ICA in its own
  paragraph: why filtering cannot remove blinks, the fit on a high-passed
  decimated copy, the double criterion, the cap of three, visual confirmation,
  no EOG channel, no-ICA as mandatory sensitivity.
- Reproducibility close: cleaning always on the full 32 channels (so the
  channel-set sensitivity cannot touch the reference or the decomposition), no
  cleaned file on disk, output \(\tilde{X}\in\mathbb{R}^{18\times32\times T_i}\).
- The rail equation keeps its place but each arrow is now explained, and the
  lead-in no longer repeats "in a high level fashion" from the Description.

`\subsubsection{Epoching}` got the same treatment, three named paragraphs:
induced spectrum versus evoked potential (with the LOO onset error, 0.23 s
explicit / 0.43 s implicit, and the +0.49 s / +1.57 s reconstructions),
rejection plus Welch (equation kept, both criteria explained), and why four
seconds, including why 2 s and 8 s fail in opposite directions.

## Unchanged

Numbers, thresholds, citations, labels, and all locks. Fz theta and posterior
alpha remain the only confirmatory measures; the channel-set rebuild is still
appendix-only sensitivity. No content moved between chapters this time; the
epoch-width justification stays in Dataset where it was moved on 23 August.
