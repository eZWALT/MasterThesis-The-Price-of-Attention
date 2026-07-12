"""
Marker server entry point.

Usage:
    python server.py
    MARKER_BACKEND=psychopy python server.py
"""

from __future__ import annotations

import logging
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

from lib.backends import resolve_backend
from lib.config import MarkerServerConfig

log = logging.getLogger("marker_server")


class MarkerHandler(BaseHTTPRequestHandler):
    server_config: MarkerServerConfig = None
    backend = None

    def do_POST(self) -> None:
        if self.path != "/marker":
            self._json(404, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            marker = json_loads(self.rfile.read(length))
        except Exception as exc:
            self._json(400, {"error": "Invalid JSON", "detail": str(exc)})
            return
        if not isinstance(marker, dict) or "marker_name" not in marker:
            self._json(400, {"error": "Missing required field: marker_name"})
            return
        self.backend.send(marker)
        self._json(200, {
            "status": "ok",
            "marker": marker.get("marker_name"),
            "event_type": marker.get("event_type"),
        })

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "healthy"})
        else:
            self._json(404, {"error": "Not found"})

    def _json(self, status: int, data: dict) -> None:
        body = json_dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        pass


def _run(config: MarkerServerConfig) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    )
    backend = resolve_backend(config.backend, config)
    MarkerHandler.server_config = config
    MarkerHandler.backend = backend
    server = HTTPServer((config.host, config.port), MarkerHandler)
    log.info("listening on http://%s:%d  (backend=%s)", config.host, config.port, config.backend)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("shutting down")
    finally:
        backend.close()
        server.server_close()


def main(argv: list[str] | None = None) -> None:
    _run(MarkerServerConfig())


def json_dumps(obj: dict) -> str:
    import json
    return json.dumps(obj, default=str)


def json_loads(data: bytes) -> dict:
    import json
    return json.loads(data)


if __name__ == "__main__":
    main()
