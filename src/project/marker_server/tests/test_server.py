"""
Integration tests for the HTTP marker server.

Starts the server on a random port in a background thread,
then sends real HTTP requests using urllib (stdlib).
"""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from lib.backends import LoggingBackend
from lib.config import MarkerServerConfig
from server import MarkerHandler, json_dumps


# ── Fixture: server on a random port ──────────────────────────────

@pytest.fixture
def server_url(cfg):
    cfg.host = "127.0.0.1"
    cfg.port = 0
    backend = LoggingBackend(cfg)
    MarkerHandler.server_config = cfg
    MarkerHandler.backend = backend
    srv = HTTPServer((cfg.host, cfg.port), MarkerHandler)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{port}"
    srv.shutdown()
    t.join(timeout=2)
    backend.close()


# ── Helpers ───────────────────────────────────────────────────────

def _post(url: str, body: dict) -> dict:
    data = json_dumps(body).encode()
    req = Request(f"{url}/marker", data=data, headers={"Content-Type": "application/json"})
    with urlopen(req) as resp:
        return json.loads(resp.read())


def _get(url: str, path: str = "/health") -> dict:
    with urlopen(f"{url}{path}") as resp:
        return json.loads(resp.read())


# ── Tests ─────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_ok(self, server_url):
        assert _get(server_url) == {"status": "healthy"}

    def test_health_returns_200(self, server_url):
        req = Request(f"{server_url}/health")
        with urlopen(req) as resp:
            assert resp.status == 200

    def test_unknown_path_returns_404(self, server_url):
        with pytest.raises(HTTPError) as exc:
            _get(server_url, "/foo")
        assert exc.value.code == 404


class TestMarker:
    def test_valid_marker_returns_ok(self, server_url):
        resp = _post(server_url, {
            "marker_name": "test_marker",
            "event_type": "test",
            "timestamp": "2026-01-01T00:00:00Z",
            "unix_ts": 1767225600.0,
            "index": 1,
        })
        assert resp["status"] == "ok"
        assert resp["marker"] == "test_marker"

    def test_missing_marker_name_returns_400(self, server_url):
        with pytest.raises(HTTPError) as exc:
            _post(server_url, {"event_type": "test"})
        assert exc.value.code == 400

    def test_invalid_json_returns_400(self, server_url):
        req = Request(f"{server_url}/marker", b"not json", headers={"Content-Type": "application/json"})
        with pytest.raises(HTTPError) as exc:
            with urlopen(req):
                pass
        assert exc.value.code == 400

    def test_wrong_path_returns_404(self, server_url):
        data = json_dumps({"marker_name": "x"}).encode()
        req = Request(f"{server_url}/wrong", data=data, headers={"Content-Type": "application/json"})
        with pytest.raises(HTTPError) as exc:
            with urlopen(req):
                pass
        assert exc.value.code == 404

    def test_multiple_markers_in_sequence(self, server_url):
        for i in range(3):
            resp = _post(server_url, {
                "marker_name": f"marker_{i}",
                "event_type": "test",
                "timestamp": "",
                "unix_ts": float(i),
                "index": i,
            })
            assert resp["status"] == "ok"

    def test_marker_with_all_optional_fields(self, server_url):
        resp = _post(server_url, {
            "marker_name": "full",
            "event_type": "test",
            "timestamp": "2026-07-12T12:00:00Z",
            "unix_ts": 1783929600.0,
            "index": 15,
            "extra_field": "ignored",
        })
        assert resp["status"] == "ok"

    def test_get_on_marker_returns_404(self, server_url):
        with pytest.raises(HTTPError) as exc:
            _get(server_url, "/marker")
        assert exc.value.code == 404

    class TestEdgeCases:
        def test_empty_body(self, server_url):
            req = Request(f"{server_url}/marker", b"", headers={"Content-Type": "application/json"})
            with pytest.raises(HTTPError) as exc:
                with urlopen(req):
                    pass
            assert exc.value.code == 400

        def test_large_body(self, server_url):
            body = {"marker_name": "big", "event_type": "t", "timestamp": "", "unix_ts": 0.0, "index": 0}
            big = body.copy()
            big["data"] = "x" * 100_000
            resp = _post(server_url, big)
            assert resp["status"] == "ok"
