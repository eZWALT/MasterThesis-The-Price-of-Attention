"""
Trackable product links for ad conversion (behavioral DV).

Product names are rendered as blue ``<a>`` links that point to the
click-tracking server (``http://<host>:7780/click/<item_id>``) with
``target="_blank"``.  Clicking opens a new browser tab; the server
logs ``ad_clicked`` immediately and responds with an HTTP 302 redirect
to the real product URL.

No client-side JavaScript is required — the browser follows the
redirect natively, making the tracking completely reliable regardless
of CORS, Mixed Content, or Streamlit DOM quirks.
"""

from __future__ import annotations

import html
import json
import os
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import parse_qs, quote, unquote, urlparse

from loguru import logger as log

from core.ad_injection.models import Ad, participant_display_title, ad_image_url
from core.config import AD_CONVERSION_URL_BASE
from core.logger.payload import compact_event_data

if TYPE_CHECKING:
    from core.conversation.manager import ConversationManager
    from core.logger.experiment_logger import ExperimentLogger

_AD_LINK_STYLE = (
    "color:#58a6ff !important;text-decoration:underline !important;"
    "font-weight:600;cursor:pointer;"
)
_PRODUCT_MENTION_RE = re.compile(
    r"\n\s*Product Mention:\s*\n.*",
    flags=re.IGNORECASE | re.DOTALL,
)

AD_CLICK_SERVER_PORT = int(os.getenv("AD_CLICK_SERVER_PORT", "7780"))

# Hostname used for click-server redirect URLs.
# When empty (default), the hostname is derived from Streamlit's request
# context (st.context.url) so it matches whatever the browser used.
AD_CLICK_SERVER_HOST: str = os.getenv("AD_CLICK_SERVER_HOST", "")


# ── URLs ──────────────────────────────────────────────────────────────────

def ad_product_url(ad: Ad) -> str:
    """Fake outbound product URL (logged as conversion target)."""
    item_id = quote((ad.source_item_id or "unknown").strip(), safe="")
    return f"{AD_CONVERSION_URL_BASE.rstrip('/')}/{item_id}"


def ad_product_url_for_id(item_id: str) -> str:
    return f"{AD_CONVERSION_URL_BASE.rstrip('/')}/{quote(item_id.strip(), safe='')}"


def _click_server_base_url() -> str:
    """Return the base URL for the click-tracking server.

    Uses ``AD_CLICK_SERVER_HOST`` if set, otherwise derives the hostname
    from ``st.context.url`` so that the browser can reach port 7780 on
    the same host it already uses for the Streamlit app.
    """
    host = AD_CLICK_SERVER_HOST
    if not host:
        try:
            import streamlit as st
            page_url = st.context.url
            if page_url:
                host = urlparse(page_url).hostname or "localhost"
        except Exception:
            pass
    if not host:
        host = "localhost"
    return f"http://{host}:{AD_CLICK_SERVER_PORT}"


# ── HTML link generation ──────────────────────────────────────────────────

def html_product_link(
    ad: Ad,
    *,
    label: str | None = None,
) -> str:
    """Product title as an ``<a>`` that routes through the click server.

    The href points to ``http://<host>:7780/click/<item_id>`` so the
    click server can log the event before redirecting the browser to
    the real product page.  No JavaScript is needed.
    """
    text = html.escape(label or participant_display_title(ad))
    item_id = quote((ad.source_item_id or "unknown").strip(), safe="")
    click_href = f"{_click_server_base_url()}/click/{item_id}"
    href = html.escape(click_href, quote=True)
    return (
        f'<a href="{href}" target="_blank" rel="noopener noreferrer" '
        f'title="{html.escape(ad_product_url(ad), quote=True)}" '
        f'style="{_AD_LINK_STYLE}">{text}</a>'
    )


# ═══════════════════════════════════════════════════════════════════════════
#  Threaded HTTP click server
# ═══════════════════════════════════════════════════════════════════════════

_click_state: Dict[str, Any] = {}
_server_started = False


class _AdClickHandler(BaseHTTPRequestHandler):
    """Handles GET /click/<item_id> → log + 302 redirect, and
    POST /ad_click for legacy JS-based tracking."""

    def do_GET(self):
        """Redirect-based click tracking.

        Path ``/click/<item_id>`` logs the click and redirects the
        browser to the real product URL.  This is the primary tracking
        mechanism — no client-side JavaScript is required.
        """
        from urllib.parse import urlparse
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        # ── /click/<item_id>  →  log + 302 redirect ──
        if path.startswith("/click/"):
            item_id = path[len("/click/"):]
            # URL-decode in case the item_id contains encoded chars
            from urllib.parse import unquote
            item_id = unquote(item_id).strip()
            if item_id:
                self._record_click(item_id)
            # Always redirect to the product page (even if logging failed)
            target = ad_product_url_for_id(item_id) if item_id else AD_CONVERSION_URL_BASE
            self.send_response(302)
            self.send_header("Location", target)
            self.send_header("Content-Length", "0")
            self.send_header("Connection", "close")
            self.end_headers()
            return

        # ── Legacy tracking-pixel fallback ──
        if parsed.path == "/ad_click":
            qs = parse_qs(parsed.query)
            item_id = qs.get("item_id", [""])[0].strip()
            if item_id:
                self._record_click(item_id)
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "image/gif")
            self.send_header("Content-Length", "43")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(
                b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
                b"\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,"
                b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
            )
            return

        self._reply(404, {"error": "not found"})

    def do_OPTIONS(self):
        """CORS preflight."""
        self.send_response(200)
        self._cors_headers()
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()

    def do_POST(self):
        """Legacy POST /ad_click (sendBeacon) — kept for backward compat."""
        if self.path != "/ad_click":
            self._reply(404, {"error": "not found"})
            return
        item_id = self._parse_item_id()
        if not item_id:
            self._reply(400, {"error": "missing item_id"})
            return
        ok = self._record_click(item_id)
        if ok:
            self._reply(200, {"ok": True})
        else:
            self._reply(503, {"error": "logger not ready"})

    # ── helpers ────────────────────────────────────────────────────────

    def _parse_item_id(self) -> str:
        """Extract item_id from either JSON or form-urlencoded POST body."""
        content_type = self.headers.get("Content-Type", "")
        length = int(self.headers.get("Content-Length", 0))

        if "application/json" in content_type:
            try:
                body = json.loads(self.rfile.read(length)) if length else {}
            except Exception:
                return ""
            return body.get("item_id", "").strip()

        # navigator.sendBeacon sends application/x-www-form-urlencoded
        if "application/x-www-form-urlencoded" in content_type or "text/plain" in content_type:
            try:
                raw = self.rfile.read(length).decode() if length else ""
            except Exception:
                return ""
            from urllib.parse import parse_qs
            pairs = parse_qs(raw)
            return pairs.get("item_id", [""])[0].strip()

        # Fallback: try JSON then form-encoded
        try:
            raw = self.rfile.read(length).decode() if length else ""
        except Exception:
            return ""
        try:
            body = json.loads(raw)
            return body.get("item_id", "").strip()
        except Exception:
            pairs = parse_qs(raw)
            return pairs.get("item_id", [""])[0].strip()

    def _record_click(self, item_id: str) -> bool:
        """Log the click event. Returns True on success, False if logger not ready."""
        logger = _click_state.get("logger")
        manager = _click_state.get("manager")
        ad_mode = _click_state.get("ad_mode", "")

        if logger is None:
            return False

        turn = 0
        conversation_id = ""
        if manager is not None:
            turn = getattr(manager, "turn_count", 0) or 0
            conversation_id = getattr(manager, "conversation_id", "") or ""

        ad = _find_ad_from_state(item_id)
        log_ad_clicked(
            logger,
            ad=ad,
            ad_mode=ad_mode,
            conversation_id=conversation_id,
            turn=turn,
            interaction="product_link",
        )
        log.info("ad_clicked logged for item_id={} turn={}", item_id, turn)
        return True

    def _reply(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self._cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format, *args):
        pass


def _find_ad_from_state(item_id: str) -> Ad:
    manager = _click_state.get("manager")
    if manager is not None:
        turn = getattr(manager, "turn_count", 0) or 0
        for ad in manager.ads_by_turn.get(turn, []):
            if ad.source_item_id == item_id:
                return ad
        if manager.last_retrieval and manager.last_retrieval.primary:
            primary = manager.last_retrieval.primary
            if primary.source_item_id == item_id:
                return primary
    return Ad(title=item_id, text="", source_item_id=item_id)


def start_ad_click_server() -> None:
    """Start the click-logging HTTP server once (idempotent).

    Uses ``allow_reuse_address = True`` (SO_REUSEADDR) so the port can
    be rebound immediately after a Streamlit hot-reload or container
    restart — avoids EADDRINUSE from sockets lingering in TIME_WAIT.
    """
    global _server_started
    if _server_started:
        return
    _server_started = True

    class _ReusableHTTPServer(HTTPServer):
        allow_reuse_address = True
        # HTTP/1.1 is required for proper CORS preflight handling;
        # HTTP/1.0 (the BaseHTTPRequestHandler default) causes some
        # browsers to reject the preflight response.
        protocol_version = "HTTP/1.1"

    try:
        server = _ReusableHTTPServer(("0.0.0.0", AD_CLICK_SERVER_PORT), _AdClickHandler)
    except OSError as exc:
        log.warning("Ad click server failed to bind on port {}: {}", AD_CLICK_SERVER_PORT, exc)
        return
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    log.info("Ad click server listening on :{}", AD_CLICK_SERVER_PORT)


def register_click_state(
    logger: "ExperimentLogger",
    manager: "ConversationManager",
    ad_mode: str,
) -> None:
    """Update the state the click server uses to log events."""
    _click_state["logger"] = logger
    _click_state["manager"] = manager
    _click_state["ad_mode"] = ad_mode


# ── JSONL logging ─────────────────────────────────────────────────────────

def log_ad_clicked(
    logger: "ExperimentLogger",
    *,
    ad: Ad,
    ad_mode: str,
    conversation_id: str,
    turn: int,
    interaction: str,
) -> None:
    """Record an ad click conversion (behavioral DV)."""
    logger.log(
        "ad_clicked",
        compact_event_data(
            {
                "ad_item_id": ad.source_item_id,
                "ad_title": ad.title,
                "click_url": ad_product_url(ad),
                "interaction": interaction,
            },
            turn=turn,
        ),
        ad_mode,
        conversation_id,
        source="user",
        turn=turn,
    )


# ── Title matching ────────────────────────────────────────────────────────

def _title_match_variants(ad: Ad) -> List[str]:
    raw = (ad.title or "").strip()
    display = participant_display_title(ad)
    variants: List[str] = []
    for candidate in (raw, display):
        if candidate and candidate not in variants:
            variants.append(candidate)
    words = raw.split()
    if len(words) >= 4:
        half = " ".join(words[: max(3, len(words) // 2)])
        if half not in variants:
            variants.append(half)
    variants.sort(key=len, reverse=True)
    return variants


def detect_mentioned_ad(content: str, ads: List[Ad]) -> Ad | None:
    """Best-effort match of which candidate the assistant referenced."""
    if not content or not ads:
        return None
    lowered = content.lower()
    for ad in ads:
        for variant in _title_match_variants(ad):
            if variant.lower() in lowered:
                return ad
    return ads[0]


# ── Content cleaning ──────────────────────────────────────────────────────

def clean_inline_assistant_display(content: str) -> str:
    """Remove structured ad junk (*** / 'Product Mention:' labels) but keep the prose."""
    text = (content or "").strip()
    if not text:
        return text
    if "***" in text:
        main, _, tail = text.partition("***")
        main = main.strip()
        tail = tail.strip()
        if tail:
            tail = re.sub(r"^Product Mention:\s*", "", tail, flags=re.I).strip()
            if tail and tail not in main:
                text = f"{main}\n\n{tail}" if main else tail
            else:
                text = main
        else:
            text = main
    else:
        text = _PRODUCT_MENTION_RE.sub("", text).strip()
    return text or (content or "").strip()


# ── Linkify (inline text) ─────────────────────────────────────────────────

def _escape_preserving_links(text: str) -> str:
    """HTML-escape plain text but leave existing ``<a …>`` anchors intact."""
    parts = re.split(r"(<a\s[^>]*>.*?</a>)", text, flags=re.DOTALL | re.IGNORECASE)
    return "".join(
        part if part.lower().startswith("<a ") else html.escape(part)
        for part in parts
    )


def linkify_inline_ad_titles(text: str, ads: List[Ad]) -> str:
    """
    Wrap product titles in clickable ``<a>`` links inside assistant text.

    Handles both plain text and ``**bold**`` variants.  Falls back to the
    first ``**bold**`` phrase or appends a trailing link if nothing matches.
    """
    if not text or not ads:
        return html.escape(text).replace("\n", "<br>\n")

    out = text
    linked = False
    for ad in ads:
        for variant in _title_match_variants(ad):
            link = html_product_link(ad, label=variant)
            for pat in (
                re.compile(r"\*\*" + re.escape(variant) + r"\*\*", re.IGNORECASE),
                re.compile(re.escape(variant), re.IGNORECASE),
            ):
                if pat.search(out):
                    out = pat.sub(link, out, count=1)
                    linked = True
                    break
            if linked:
                break
        if linked:
            break

    if not linked and ads:
        ad = ads[0]
        bold = re.search(r"\*\*(.+?)\*\*", out)
        if bold:
            link = html_product_link(ad, label=bold.group(1).strip())
            out = out[: bold.start()] + link + out[bold.end() :]
        else:
            link = html_product_link(ad)
            sep = "" if out.endswith((".", "!", "?")) else "."
            out = f"{out}{sep} See {link}."

    out = _escape_preserving_links(out)
    return out.replace("\n", "<br>\n")


# ── Display payload helpers ───────────────────────────────────────────────

def enrich_display_payload(ad: Ad, payload: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(payload)
    out["source_item_id"] = ad.source_item_id
    out["click_url"] = ad_product_url(ad)
    image_url = ad_image_url(ad)
    if image_url:
        out["image_url"] = image_url
    return out


# ── JS click tracker (LEGACY — no longer required) ────────────────────────
#
# The redirect-based approach (ad links point to /click/<item_id> on the
# click server) makes client-side JavaScript tracking unnecessary.
# ``inject_ad_click_tracker()`` is kept as a no-op so that existing
# call-sites (screens.py, dev.py) don't break.

def _build_tracker_js(port: int) -> str:
    return ""


_AD_CLICK_TRACKER_JS: str = ""


def inject_ad_click_tracker() -> None:
    """No-op — redirect-based tracking makes JS injection unnecessary."""
    pass
