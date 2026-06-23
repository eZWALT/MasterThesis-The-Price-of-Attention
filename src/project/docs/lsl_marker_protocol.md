# LSL Marker Protocol — ExperimentMarkers

All markers sent as single-string samples via LSL stream named `ExperimentMarkers` (type `Markers`, source `rag-recsys-experiment`).

| Marker | When | Purpose |
|---|---|---|
| `session:start` | Session init | Experiment begins |
| `session:end` | Session export | Experiment ends |
| `screen:consent` | Consent submitted | Participant agreed |
| `baseline:start` | Baseline screen renders | Webcam baseline begins |
| `baseline:end` | Baseline timer expires | Baseline done |
| `screen:instructions` | Instructions dismissed | |
| `screen:warmup_chat` | Warmup chat done | |
| `screen:condition_intro` | Condition intro dismissed | |
| `condition:{id}:start` | Before first chat turn | Condition begins |
| `condition:{id}:ad_mode:{mode}` | Same time as start | Which ad mode |
| `turn:{N}` | After LLM reply at turn N | Every user-assistant exchange |
| `ad_injected:{N}` | Ad shown at turn N | Ad exposure onset |
| `screen:condition_chat` | Condition chat done | Chat completed |
| `condition:{id}:end` | Same time | Condition ends |
| `screen:condition_conclusion` | Conclusion submitted | |
| `survey:post_condition:submitted` | Post-condition Likert done | |
| `survey:ads_recall:submitted` | Ad recall done | |
| `survey:ocean:submitted` | BFI personality done | |
| `survey:demographics:submitted` | Demographics done | |
| `survey:deception_disclosure:submitted` | Debrief done | |

All markers are best-effort (no-op if `pylsl` is not installed). No separate thread — `outlet.push_sample()` is synchronous but non-blocking (~microseconds).
