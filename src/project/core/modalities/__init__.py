"""
Multimodal integration package.

Submodules
----------
eeg/         : EEG stream reading, marker emission, preprocessing stubs
eye_tracking/: Eye-tracking stream reading, AOI fixation stubs
sync         : Cross-modality timestamp synchronisation

Integration points (to wire up in participant.py):
  - Call modalities.sync.record_reference() at session start
  - Call modalities.eeg.markers.send() at every ctrl.advance() transition
  - Call modalities.eeg.markers.send() when an ad is injected
  - Call modalities.eye_tracking.stream.start() at baseline screen
"""
