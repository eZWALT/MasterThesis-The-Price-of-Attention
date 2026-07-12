# Marker Server

Lightweight HTTP receiver for EEG experiment markers. Runs anywhere — no hard dependencies.

## Quick start

```bash
# Terminal 1 — start the server:
./run.sh

# Terminal 2 — send markers:
curl -X POST http://localhost:9876/marker \
  -H 'Content-Type: application/json' \
  -d '{"marker_name":"condition_started","event_type":"condition","unix_ts":1783876440.0,"index":2}'

curl http://localhost:9876/health
```

## Usage

```bash
# Local (stdlib only):
python server.py                           # backend=log
MARKER_BACKEND=lsl    python server.py     # LSL  (needs pylsl)
MARKER_BACKEND=psychopy python server.py   # TTL  (needs psychopy)

# Or via ./run.sh:
./run.sh           # log
./run.sh lsl       # LSL
./run.sh psychopy  # parallel port TTL

# Docker:
docker compose up marker-server
docker compose up marker-server-lsl
docker compose up marker-server-psychopy
```

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests/
```

## Marker JSON

| Field | Type | Required | Description |
|---|---|---|---|
| `marker_name` | str | yes | e.g. `condition_started` |
| `event_type` | str | no | e.g. `screen`, `condition`, `session` |
| `timestamp` | str | no | ISO 8601 |
| `unix_ts` | float | no | seconds since epoch |
| `index` | int | no | parallel port value 0–255 |

## Env vars

| Variable | Default | Description |
|---|---|---|
| `MARKER_PORT` | `9876` | HTTP listen port |
| `MARKER_BACKEND` | `log` | `log` / `lsl` / `psychopy` |
| `MARKER_PARALLEL_ADDRESS` | `0x378` | parallel port address |
| `MARKER_PULSE_MS` | `50` | TTL pulse duration |
| `MARKER_LSL_STREAM_NAME` | `ExperimentMarkers` | LSL stream name |
