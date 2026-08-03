# Bronze stage

Bronze establishes what was recorded without altering or reconstructing it.

Responsibilities:

- inventory current and superseded XDF assets;
- retain SHA-256 identity and source provenance;
- inspect stream and raw-marker evidence;
- establish the recording-to-participant/log map;
- preserve every original marker, including duplicates and unexpected labels.

`manifests/` contains the concise recording summary and full machine evidence.
Marker reconstruction does not belong in Bronze because it creates a derived
timeline.
