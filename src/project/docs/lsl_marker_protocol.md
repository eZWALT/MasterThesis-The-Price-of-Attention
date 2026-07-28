# LSL Marker Protocol

Markers let the EEG recording be time-locked to what happened on screen. The app
publishes them over Lab Streaming Layer so LabRecorder captures them in the same
XDF file as the amplifier stream.

Implemented in `core/modalities/eeg/__init__.py`.

## Stream

| Property | Value |
|---|---|
| Name | `experiment_lab_pilot` |
| Type | `Markers` |
| Channels | 1, string |
| Sampling rate | 0 (irregular) |
| Source ID | `rag-recsys-experiment-lab` |

A `dummy_start` marker is pushed when the outlet is created, so the stream is
discoverable in LabRecorder before the participant begins.

## Marker names are log event names

There is no separate marker vocabulary. `ExperimentLogger.log()` forwards each
event to the marker client, which pushes the event name unchanged when it is on
the whitelist. Anything you see in the JSONL is what you see in the XDF, so the
two can be joined without a translation table.

| Marker | Emitted when |
|---|---|
| `baseline_start` / `baseline_end` | Rest baseline begins and ends |
| `warmup_start` / `warmup_finish` | Warm-up chat begins and ends |
| `condition_start` | A condition's first turn is about to run |
| `turn_N_read` | The assistant's reply for turn N is displayed (reading onset) |
| `turn_N_write` | The participant starts composing turn N (writing onset) |
| `ad_injected` | An ad is inserted into the response |
| `ad_displayed` | The ad becomes visible to the participant |
| `condition_conclusion_submitted` | Findings text submitted |
| `post_task_questionnaire_end` | Post-condition questionnaire finished |
| `experiment_end` | Session complete |

`turn_N_read` and `turn_N_write` are matched by pattern, so every turn number is
covered. Everything else the logger records — retrieval details, survey payloads,
demographics — stays out of the marker stream to keep it sparse and readable.

## Behaviour

The outlet is created lazily and cached for the process. Pushing is synchronous
but takes microseconds, so it happens inline with no extra thread. If `pylsl` is
missing or outlet creation fails, every call becomes a no-op and the app runs
normally — the crowd arm never needs LSL.

## Recording a lab session

1. Start the app on the lab machine and open it with `?study=lab`.
2. Open LabRecorder and confirm both the amplifier stream and
   `experiment_lab_pilot` appear.
3. Record. Marker and EEG samples share the XDF clock, so no post-hoc
   alignment is needed.

To verify the stream is visible from the recording machine before a session,
`scripts/lsl_bridge.py` publishes synthetic markers on the same outlet name.

Inspect a finished recording with the pilot helpers:

```bash
python3 scripts/pilot/inspect_xdf.py  sub-P007_ses-S001_task-Default_run-001_eeg.xdf
python3 scripts/pilot/inspect_clean.py sub-P007_ses-S001_task-Default_run-001_eeg.xdf
```

They print the stream inventory, channel list, sampling rate, and the marker
sequence with timestamps.
