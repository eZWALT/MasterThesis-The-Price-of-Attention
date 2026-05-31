"""
Trackable product links for ad conversion (behavioral DV).

Product names are rendered as blue ``<a>`` links pointing directly to the
fake product URL (``AD_CONVERSION_URL_BASE``) with ``target="_blank"``.
Clicking opens a new browser tab.

A tiny threaded HTTP server (``start_ad_click_server``) runs inside the
Streamlit process on ``AD_CLICK_SERVER_PORT``.  ``st.html`` injects a JS
click listener that POSTs to this server on every ad-link click.  The
server logs ``ad_clicked`` immediately — no page reload, no query-param
hacks.
"""

from __future__ import annotations

import html
import json
import os
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import quote

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

_AD_URL_PATTERN = AD_CONVERSION_URL_BASE.rstrip("/").replace("https://", "").replace("http://", "")


# ── URLs ──────────────────────────────────────────────────────────────────

def ad_product_url(ad: Ad) -> str:
    """Fake outbound product URL (logged as conversion target)."""
    item_id = quote((ad.source_item_id or "unknown").strip(), safe="")
    return f"{AD_CONVERSION_URL_BASE.rstrip('/')}/{item_id}"


def ad_product_url_for_id(item_id: str) -> str:
    return f"{AD_CONVERSION_URL_BASE.rstrip('/')}/{quote(item_id.strip(), safe='')}"


# ── HTML link generation ──────────────────────────────────────────────────

def html_product_link(
    ad: Ad,
    *,
    label: str | None = None,
) -> str:
    """Product title as an ``<a>`` that opens the product URL in a new tab."""
    text = html.escape(label or participant_display_title(ad))
    href = html.escape(ad_product_url(ad), quote=True)
    return (
        f'<a href="{href}" target="_blank" rel="noopener noreferrer" '
        f'title="{href}" style="{_AD_LINK_STYLE}">{text}</a>'
    )


# ═══════════════════════════════════════════════════════════════════════════
#  Threaded HTTP click server
# ═══════════════════════════════════════════════════════════════════════════

_click_state: Dict[str, Any] = {}
_server_started = False


class _AdClickHandler(BaseHTTPRequestHandler):
    """Handles POST /ad_click from the browser JS."""

    def do_POST(self):
        if self.path != "/ad_click":
            self._reply(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}
        except Exception:
            self._reply(400, {"error": "bad json"})
            return

        item_id = body.get("item_id", "").strip()
        if not item_id:
            self._reply(400, {"error": "missing item_id"})
            return

        logger = _click_state.get("logger")
        manager = _click_state.get("manager")
        ad_mode = _click_state.get("ad_mode", "")

        if logger is None:
            self._reply(503, {"error": "logger not ready"})
            return

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
        self._reply(200, {"ok": True})

    def do_OPTIONS(self):
        """CORS preflight."""
        self.send_response(200)
        self._cors_headers()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _reply(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self._cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
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
    """Start the click-logging HTTP server once (idempotent)."""
    global _server_started
    if _server_started:
        return
    _server_started = True
    try:
        server = HTTPServer(("0.0.0.0", AD_CLICK_SERVER_PORT), _AdClickHandler)
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


# ── JS click tracker (injected into page) ────────────────────────────────

def _build_tracker_js(port: int) -> str:
    return (
        '<script>\n'
        '(function() {\n'
        '    if (window.__ad_click_tracker) return;\n'
        '    window.__ad_click_tracker = true;\n'
        '    document.addEventListener("click", function(e) {\n'
        '        var link = e.target.closest(\'a[href*="' + _AD_URL_PATTERN + '"]\');\n'
        '        if (!link) return;\n'
        '        var m = link.href.match(/\\/product\\/([^\\/?#]+)/);\n'
        '        if (!m) return;\n'
        '        var itemId = decodeURIComponent(m[1]);\n'
        '        fetch("http://" + location.hostname + ":' + str(port) + '/ad_click", {\n'
        '            method: "POST",\n'
        '            headers: {"Content-Type": "application/json"},\n'
        '            body: JSON.stringify({item_id: itemId})\n'
        '        }).catch(function(){});\n'
        '    }, true);\n'
        '})();\n'
        '</script>'
    )


_AD_CLICK_TRACKER_JS: str = _build_tracker_js(AD_CLICK_SERVER_PORT)


def inject_ad_click_tracker() -> None:
    """Inject a JS click listener that POSTs to the local click server."""
    import streamlit as st

    st.html(_AD_CLICK_TRACKER_JS, unsafe_allow_javascript=True)


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
