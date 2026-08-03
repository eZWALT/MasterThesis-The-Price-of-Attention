# EEG acquisition contract

Status: montage technically validated; ground provisionally identified;
acquisition reference awaiting confirmation.

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

- Ground: the study operator recalls `Fpz`. This is consistent with `Fpz` being
  absent from the recorded channel list, but still needs confirmation from the
  acquisition setup.
- Reference: unknown. The absence of `FCz` is consistent with a common actiCHamp
  setup using FCz as the online reference, but this remains a hypothesis.

Confirm from the BrainVision Recorder workspace, cap setup sheet, or the person
who mounted the cap:

1. Was FCz the online reference?
2. Was Fpz the ground electrode?
3. Was the same setup used for all participants?

Average rereferencing during preprocessing is a separate transformation and does
not answer what reference was used during acquisition.
