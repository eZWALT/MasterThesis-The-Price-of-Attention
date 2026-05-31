"""
Trackable product links for ad conversion (behavioral DV).

Product names are rendered as blue ``<a>`` links pointing directly to the
fake product URL (``AD_CONVERSION_URL_BASE``) with ``target="_blank"``.
Clicking opens a new browser tab; the chat session is never navigated away.

``ad_link_shown`` is logged to JSONL when a clickable link is rendered so
that downstream analysis can count ad engagements.
"""

from __future__ import annotations

import html
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import quote

from core.ad_injection.models import Ad, participant_display_title
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


# ── JSONL logging ─────────────────────────────────────────────────────────

def log_ad_link_shown(
    logger: "ExperimentLogger",
    *,
    ad: Ad,
    ad_mode: str,
    conversation_id: str,
    turn: int,
    interaction: str,
) -> None:
    """Record that a clickable product link was shown (behavioral DV)."""
    logger.log(
        "ad_link_shown",
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
        source="system",
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
    return out
