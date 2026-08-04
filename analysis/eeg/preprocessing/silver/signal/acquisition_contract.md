# EEG acquisition contract

Status: montage technically validated; ground and online reference reported by
the laboratory on 2026-08-04.

## Established from all 19 current XDF recordings

- EEG stream: `actiCHamp-24020270`
- Manufacturer: Brain Products
- Channels: 32
- Sampling rate: 500 Hz nominal, approximately 499.99 Hz effective
- Source units: microvolts
- MNE scaling: multiply by `1e-6` to obtain volts
- Channel layout: identical across all recordings
- Montage: every recorded label resolves in MNE `standard_1020`
- FCz: not present as a recorded data channel
- Fpz: not present as a recorded data channel
- Canonical event mapping: nearest actual EEG sample, maximum error below 1 ms

The difference between effective and nominal sampling rate accumulates to as much
as 0.095 seconds over a recording. Canonical XDF timestamps therefore must be
mapped to actual EEG sample indices before assigning regular MNE annotation
times. Copying elapsed XDF seconds directly into MNE is not acceptable.

## Recorded channels

`Fp1, Fz, F3, F7, F9, FC5, FC1, C3, T7, CP5, CP1, Pz, P3, P7, P9, O1,
Oz, O2, P10, P8, P4, CP2, CP6, T8, C4, Cz, FC2, FC6, F10, F8, F4, Fp2`

## Ground and acquisition-reference decision

XDF does not declare the physical acquisition reference or ground electrode.
Human laboratory feedback establishes:

- ground: `Fpz`, with no recorded data values;
- online reference: `Cz`;
- offline policy: common-average rereferencing after bad-channel handling.

`Fpz` is absent from the XDF data channels, as expected for the ground. `Cz` is
present as a dynamic XDF data channel rather than a zero-valued reference-only
trace. This does not negate the laboratory report, because amplifier/export
handling may reconstruct or retain a labelled reference channel, but the exact
BrainVision/actiCHamp handling should be checked from the acquisition workspace
if it becomes available.

Average rereferencing during preprocessing is a separate transformation and does
not change the historical fact that acquisition was referenced online to `Cz`.
It is retained because it reduces dependence on a single reference electrode
and supports the current sensor-level spectral analyses.
