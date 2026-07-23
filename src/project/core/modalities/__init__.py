"""
Multimodal integration package.

Submodules
----------
eeg/         : LSL marker emission (log-adherent, single-outlet)
eye_tracking/: Eye-tracking stream reading, AOI fixation stubs
sync         : Cross-modality timestamp synchronisation

The EEG module is auto-wired into ExperimentLogger.log() via
logger._marker_client — every structured log event is also pushed
to the LSL outlet.
"""
