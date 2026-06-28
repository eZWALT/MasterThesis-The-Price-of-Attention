"""
Screen renderers for the experiment flow.

Each function renders one screen and returns True when the user
has completed it (so the flow controller can advance).  All state
mutations go through st.session_state.

No business logic here — just UI.  Config values are imported,
never hardcoded.
"""

from __future__ import annotations

import html as html_module
import threading
import time
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import streamlit as st

from core.config import (
    DEFAULT_MAX_TOKENS,
    CONSENT_TITLE,
    CONSENT_TEXT,
    BASELINE_DURATION_SECONDS,
    BASELINE_TITLE,
    BASELINE_INSTRUCTION,
    BASELINE_COMPLETE_MESSAGE,
    BASELINE_CONTINUE_LABEL,
    AD_MODE_LABELS,
    CONDITION_LABELS,
    PRACTICE_TASK_PROMPT,
    WARMUP_PROMPT,
    MAX_TURNS_PER_TRIAL,
    WEBCAM_FPS,
    WEBCAM_WIDTH,
    WEBCAM_HEIGHT,
)
from core.experiment.tasks import TaskDefinition
from core.experiment.surveys import (
    OCEAN_ITEMS,
    OCEAN_SCALE_MIN,
    OCEAN_SCALE_MAX,
    OCEAN_SCALE_LABELS,
    OCEAN_INSTRUCTIONS,
    get_ocean_items,
    POST_CONDITION_SCALE_MIN,
    POST_CONDITION_SCALE_MAX,
    POST_CONDITION_LLM_ITEMS,
    POST_CONDITION_PERSONALITY_LIKERT,
    POST_CONDITION_PERSONALITY_OPEN,
    POST_CONDITION_BEHAVIOUR_ITEMS,
    RECALL_ITEMS,
    RECALL_OPEN_ENDED,
    RECALL_SCALE_MIN,
    RECALL_SCALE_MAX,
    DEMOGRAPHICS_TEXT,
    DEMOGRAPHICS_SELECT,
    DECEPTION_DISCLOSURE_TEXT,
)
from core.ad_injection import get_injector
from core.ad_injection.ad_links import (
    clean_inline_assistant_display,
    detect_mentioned_ad,
    html_product_link,
    inject_ad_click_tracker,
    linkify_inline_ad_titles,
    register_click_state,
    start_ad_click_server,
)
from core.ad_injection.models import (
    Ad,
    ad_image_url,
    format_products_block,
)
from core.conversation import ConversationManager


def _banner_box_style(*, explicit: bool) -> str:
    """Inline styles — Streamlit often ignores separately injected <style> blocks."""
    base = (
        "width:100%;max-width:100%;box-sizing:border-box;display:block;"
        "background:#2a1f0e;padding:12px 16px;border-radius:8px;"
        "margin:8px 0 14px 0;"
    )
    if explicit:
        return base + "border:2px solid #ff9800;border-left:6px solid #ff9800;"
    return base + "border-left:4px solid #ff9800;"


def _ad_image_html(image_url: str, *, size_px: int = 72) -> str:
    """Optional product thumbnail — omitted when no image URL exists."""
    safe_url = html_module.escape(image_url, quote=True)
    alt = html_module.escape("Product")
    return (
        f'<img src="{safe_url}" alt="{alt}" '
        f'style="width:{size_px}px;height:{size_px}px;object-fit:cover;'
        f'border-radius:6px;flex-shrink:0;background:#1a1a1a;" />'
    )


def _resolve_payload_image_url(payload: dict, ad: Ad | None) -> str | None:
    """Image URL from display payload or linked ad metadata."""
    url = payload.get("image_url")
    if isinstance(url, str) and url.strip().startswith(("http://", "https://")):
        return url.strip()
    if ad is not None:
        return ad_image_url(ad)
    return None


def _render_chat_history(manager: ConversationManager, ad_mode: str) -> None:
    """Render full message history with trackable inline/banner ad links."""
    turn = 0
    for msg in manager.messages:
        if msg.get("role") == "user":
            turn += 1
        with st.chat_message(msg["role"]):
            msg_turn = turn if msg.get("role") == "assistant" else None
            _render_chat_message(
                msg,
                ad_mode=ad_mode,
                manager=manager,
                turn=msg_turn,
            )


def _render_chat_message(
    msg: dict,
    *,
    ad_mode: str | None = None,
    manager: ConversationManager | None = None,
    turn: int | None = None,
) -> None:
    """Render one chat message; linkify inline ad product names when applicable."""
    content = msg.get("content", "")
    if (
        msg.get("role") == "assistant"
        and ad_mode == "inline_persuasive"
        and manager is not None
        and turn is not None
        and turn in manager.ads_by_turn
    ):
        ads = manager.ads_by_turn[turn]
        mentioned = detect_mentioned_ad(content, ads)
        link_ads = [mentioned] if mentioned else ads[:1]
        display = clean_inline_assistant_display(content)
        html_body = linkify_inline_ad_titles(display, link_ads)
        st.markdown(html_body, unsafe_allow_html=True)
        return

    st.markdown(content)


def _render_ad_banner(
    payload: dict,
    *,
    ad_mode: str | None = None,
    manager: ConversationManager | None = None,
    turn: int | None = None,
    ad: Ad | None = None,
) -> None:
    """Full-width ad strip: label, clickable product title, CTA."""
    from core.config import EXPLICIT_AD_LABEL

    explicit = ad_mode == "explicit_ad_block" or payload.get("header") == EXPLICIT_AD_LABEL
    box_style = _banner_box_style(explicit=explicit)
    label_style = (
        "font-size:0.72em;color:#9a9a9a;text-transform:uppercase;"
        "letter-spacing:0.06em;margin:0 0 6px 0;"
    )
    title_style = (
        "font-weight:600;font-size:1rem;color:#f5f5f5;margin:0 0 6px 0;"
        "line-height:1.25;word-wrap:break-word;"
    )
    cta_style = "color:#ff9800;font-weight:600;font-size:0.9em;margin:0;"

    label = html_module.escape(str(payload.get("header", "Sponsored")))
    title = str(payload.get("title", ""))
    cta = html_module.escape(str(payload.get("cta", "")))
    cta_html = f'<p style="{cta_style}">{cta}</p>' if cta else ""

    if manager is not None and turn is not None and (ad is not None or payload.get("source_item_id")):
        if ad is None:
            ad = Ad(
                title=title,
                text="",
                source_item_id=str(payload.get("source_item_id", "unknown")),
                cta=payload.get("cta", ""),
            )
        title_html = html_product_link(ad, label=title)
    else:
        title_html = html_module.escape(title)

    image_url = _resolve_payload_image_url(payload, ad)
    if image_url:
        body_html = (
            f'<div style="display:flex;align-items:flex-start;gap:12px;">'
            f"{_ad_image_html(image_url, size_px=72)}"
            f'<div style="flex:1;min-width:0;">'
            f'<p style="{label_style}">{label}</p>'
            f'<p style="{title_style}">{title_html}</p>'
            f"{cta_html}"
            f"</div></div>"
        )
    else:
        body_html = (
            f'<p style="{label_style}">{label}</p>'
            f'<p style="{title_style}">{title_html}</p>'
            f"{cta_html}"
        )

    st.markdown(
        f'<div class="ad-banner" style="{box_style}">{body_html}</div>',
        unsafe_allow_html=True,
    )


# Modes that show the full-width title+CTA banner above the chat input.
_AD_BANNER_MODES = frozenset({"explicit_ad_block"})


def _ad_display_state_matches_mode(manager: ConversationManager, ad_mode: str) -> bool:
    """True when cached retrieval belongs to the active ad mode."""
    cached_mode = getattr(manager, "last_retrieval_ad_mode", None)
    return (
        manager.last_retrieval is not None
        and manager.last_retrieval.has_ads
        and cached_mode == ad_mode
    )


def _render_turn_ads(
    manager: ConversationManager,
    ad_mode: str,
) -> None:
    """Render participant-visible ads persistently until conversation ends.

    Once an ad has been retrieved (manager.last_retrieval is populated),
    the banner stays visible on every subsequent turn.  This is by design:
    the explicit ad block is a persistent UI element, not a transient
    per-turn flash.

    Ads are only shown for ad conditions (not no_ads) and only when the
    current ad_mode matches the retrieval's ad_mode (guards dev
    mode-switching).
    """
    if not ad_mode:
        return

    if not manager.last_retrieval or not manager.last_retrieval.has_ads:
        return

    if not _ad_display_state_matches_mode(manager, ad_mode):
        return

    result = get_injector(ad_mode).inject(manager.last_retrieval, manager.messages)
    turn = manager.turn_count
    primary = manager.last_retrieval.primary

    if result.display_payload and ad_mode in _AD_BANNER_MODES:
        _render_ad_banner(
            result.display_payload,
            ad_mode=ad_mode,
            manager=manager,
            turn=turn,
            ad=primary,
        )


def _render_explicit_ad_banner(payload: dict) -> None:
    """Backward-compatible alias."""
    _render_ad_banner(payload, ad_mode="explicit_ad_block")


# ═══════════════════════════════════════════════════════════════
# SCREEN 1 — CONSENT
# ═══════════════════════════════════════════════════════════════

def render_consent() -> bool:
    """Show consent form. Returns True when user agrees and clicks Start."""
    st.header(CONSENT_TITLE)
    st.markdown(CONSENT_TEXT)
    st.divider()
    agreed = st.checkbox("I have read and understood the above. I agree to participate.")
    if agreed and st.button("Start", type="primary"):
        return True
    return False


# ═══════════════════════════════════════════════════════════════
# SCREEN 2 — DEMOGRAPHICS
# ═══════════════════════════════════════════════════════════════

def render_demographics() -> Optional[dict]:
    """
    Collect basic demographics. Returns dict on submit, None otherwise.
    """
    st.header("About You")
    st.caption("All fields are optional.")

    age = st.number_input("Age", min_value=0, max_value=120, value=25, step=1)
    gender = st.selectbox("Gender", ["Prefer not to say", "Female", "Male", "Non-binary", "Other"])
    ai_experience = st.slider(
        "How experienced are you with AI assistants? (1 = never used, 5 = daily user)",
        min_value=1,
        max_value=5,
        value=3,
    )

    if st.button("Continue", type="primary"):
        if age < 0 or age > 120:
            st.error("Please enter a valid age (0–120).")
            return None
        return {
            "age": age if age > 0 else None,
            "gender": gender,
            "ai_experience": ai_experience,
        }
    return None


# ═══════════════════════════════════════════════════════════════
# SCREEN 3 — OCEAN PERSONALITY (BFI-44 or BFI-10)
# ═══════════════════════════════════════════════════════════════

def render_ocean(bfi_version: str = "10") -> Optional[list[int]]:
    """
    Render BFI questionnaire (all questions at once).

    Parameters
    ----------
    bfi_version : "10" for BFI-10 (10 items, default) or "44" for BFI-44 (44 items).

    Returns list of raw Likert responses on submit, None otherwise.
    """
    items = get_ocean_items(bfi_version)
    n = len(items)

    st.header("About You")
    st.info(OCEAN_INSTRUCTIONS)

    responses: list[int] = []
    answered = 0

    for i, (text, _trait, _rev) in enumerate(items):
        value = st.radio(
            f"**{i + 1}.** {text}",
            options=list(range(OCEAN_SCALE_MIN, OCEAN_SCALE_MAX + 1)),
            format_func=lambda v: f"{v} — {OCEAN_SCALE_LABELS.get(v, '')}",
            horizontal=True,
            index=None,
            key=f"ocean_{i}",
        )
        if value is None:
            responses.append(0)  # placeholder; submission blocked below
        else:
            responses.append(value)
            answered += 1

    # Single progress bar reflects how many questions are answered
    st.progress(answered / n, text=f"{answered} of {n} answered")

    st.divider()
    if answered == n and st.button("Continue", type="primary"):
        return responses
    elif answered < n:
        st.info("Please answer all statements to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# SCREEN 4 — BASELINE
# ═══════════════════════════════════════════════════════════════

_BASELINE_SESSION_KEYS = (
    "baseline_start",
    "_baseline_screen_active",
    "_baseline_user_confirmed",
)


def _format_duration_label(seconds: int) -> str:
    """Human-readable duration for baseline instructions."""
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"
    mins, secs = divmod(seconds, 60)
    if secs:
        return (
            f"{mins} minute{'s' if mins != 1 else ''} "
            f"and {secs} second{'s' if secs != 1 else ''}"
        )
    return f"{mins} minute{'s' if mins != 1 else ''}"


def clear_baseline_session_state() -> None:
    """Drop baseline timer keys when leaving or skipping the screen."""
    for key in _BASELINE_SESSION_KEYS:
        st.session_state.pop(key, None)


def _reset_baseline_timer() -> None:
    st.session_state.baseline_start = time.time()


# ── Webcam recording helpers ──────────────────────────────────────────────


class _WebcamCapture:
    """Background thread that continuously captures frames from the lab webcam."""

    def __init__(
        self,
        camera_id: int = 0,
        target_fps: int = 30,
        width: int = 1280,
        height: int = 720,
    ) -> None:
        self._camera_id = camera_id
        self._target_fps = target_fps
        self._width = width
        self._height = height
        self._running = False
        self._lock = threading.Lock()
        self._latest_frame: Optional[np.ndarray] = None
        self._recorded_frames: list[np.ndarray] = []
        self._last_capture_ts: float = 0.0

    def start(self) -> None:
        self._cap = cv2.VideoCapture(self._camera_id)
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open camera {self._camera_id}")
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _capture_loop(self) -> None:
        interval = 1.0 / self._target_fps
        while self._running:
            ret, frame = self._cap.read()
            if not ret:
                continue
            now = time.time()
            if now - self._last_capture_ts >= interval:
                with self._lock:
                    self._latest_frame = frame
                    self._recorded_frames.append(frame.copy())
                self._last_capture_ts = now

    def get_frame(self) -> Optional[np.ndarray]:
        with self._lock:
            return self._latest_frame.copy() if self._latest_frame is not None else None

    def drain_frames(self) -> list[np.ndarray]:
        with self._lock:
            frames = self._recorded_frames[:]
            self._recorded_frames.clear()
            return frames

    def stop(self) -> None:
        self._running = False
        if hasattr(self, "_thread"):
            self._thread.join(timeout=2)
        if hasattr(self, "_cap"):
            self._cap.release()

    def save_video(self, output_path: Path) -> None:
        frames = self.drain_frames()
        if not frames:
            return
        h, w = frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(output_path), fourcc, self._target_fps, (w, h))
        for frame in frames:
            out.write(frame)
        out.release()


def render_webcam_preview(
    webcam_enabled: bool,
    participant_id: str,
    log_dir: Path,
    run_id: str,
    current_screen: str = "",
) -> None:
    """Background webcam capture for the entire lab session.

    The live preview is shown in the sidebar **only during the baseline screen**
    to avoid slowing down the UI during conditions.  The capture thread keeps
    running in the background regardless.

    Starts the background capture on first call.  Call from
    ``render_progress_sidebar`` on every screen so the recording stays alive.
    """
    if not webcam_enabled:
        return

    # Lazy-start the background capture
    if "webcam" not in st.session_state:
        try:
            cam = _WebcamCapture(
                target_fps=WEBCAM_FPS,
                width=WEBCAM_WIDTH,
                height=WEBCAM_HEIGHT,
            )
            cam.start()
            st.session_state.webcam = cam
            # Log start marker
            st.session_state.logger.log(
                "eyetracking_recording_started",
                {},
                ad_mode="session",
                conversation_id=participant_id,
                source="system",
            )
        except RuntimeError as exc:
            st.warning(f"Webcam unavailable: {exc}")
            return

    # Only render live preview during baseline — hide it afterwards for performance
    if current_screen == "baseline":
        st.markdown(
            "<div style='font-size:0.75rem; color:#888; text-transform:uppercase; "
            "letter-spacing:0.4px; margin-bottom:4px;'>🎥 Eye Tracking</div>",
            unsafe_allow_html=True,
        )

        cam: _WebcamCapture = st.session_state.webcam

        @st.fragment(run_every=0.2)
        def _feed() -> None:
            frame = cam.get_frame()
            if frame is not None:
                st.image(frame, channels="BGR", width=240, use_container_width=True)
            st.caption("🔴 Recording")

        _feed()


def finalize_webcam_recording() -> None:
    """Stop the background capture and save the session video."""
    cam = st.session_state.pop("webcam", None)
    if cam is None:
        return
    try:
        log_dir: Path = st.session_state.logger._log_dir
        video_path = log_dir / f"{st.session_state.logger.run_id}_eyetracking.mp4"
        cam.save_video(video_path)
        cam.stop()
        st.session_state.logger.log(
            "eyetracking_video_saved",
            {"path": str(video_path)},
            ad_mode="session",
            conversation_id=st.session_state.controller.participant_id,
            source="system",
        )
    except Exception as exc:
        st.warning(f"Failed to save eye-tracking video: {exc}")


# ── Baseline screen ───────────────────────────────────────────────────────


def render_baseline() -> bool:
    """
    Baseline / eye-tracking calibration screen with countdown.

    The live webcam feed lives in the sidebar (see ``render_webcam_preview``).
    This function only shows the instructions, a camera icon, and the timer.
    """
    if st.session_state.pop("_baseline_user_confirmed", False):
        return True

    if not st.session_state.get("_baseline_screen_active"):
        st.session_state._baseline_screen_active = True
        _reset_baseline_timer()

    st.header(BASELINE_TITLE)

    # Styled instruction box
    st.markdown(f'''
    <div style="
        background:#12141a; border-radius:10px; padding:20px 22px; margin:20px 0;
        border-left:3px solid #58a6ff; font-size:0.95rem; color:#ccc; line-height:1.6;
    ">
        <div style="color:#777; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Instructions</div>
        {BASELINE_INSTRUCTION.format(duration_label=_format_duration_label(BASELINE_DURATION_SECONDS))}
    </div>''',
    unsafe_allow_html=True,
    )

    # Camera icon
    st.markdown(
        "<div style='text-align:center; font-size:3em; padding:10px 0 0 0;'>📷</div>",
        unsafe_allow_html=True,
    )

    # Timer fragment (auto-refreshes every second)
    @st.fragment(run_every=1)
    def _baseline_timer() -> None:
        elapsed = time.time() - st.session_state.baseline_start
        remaining = max(0, int(BASELINE_DURATION_SECONDS - elapsed))
        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            st.markdown(
                f"<div style='text-align:center; font-size:2.5em; padding:15px 0;'>"
                f"⏳ {mins:02d}:{secs:02d}"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.success(BASELINE_COMPLETE_MESSAGE)
            if st.button(BASELINE_CONTINUE_LABEL, type="primary", key="baseline_continue"):
                clear_baseline_session_state()
                st.session_state._baseline_user_confirmed = True
                st.rerun()

    _baseline_timer()
    return False


# ═══════════════════════════════════════════════════════════════
# SCREEN 5 — PRACTICE
# ═══════════════════════════════════════════════════════════════

def render_practice(manager: ConversationManager) -> bool:
    """
    Practice chat (no ads, no experiment logging).
    Returns True when user clicks 'Done practising'.
    """
    st.header("Practice Round")
    st.markdown(f'''
    <div style="
        background:#12141a; border-radius:10px; padding:16px 18px; margin:20px 0;
        border-left:3px solid #58a6ff; font-size:0.95rem; color:#ccc; line-height:1.55;
    ">
        <div style="color:#777; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Your Task</div>
        {html_module.escape(PRACTICE_TASK_PROMPT)}
    </div>''',
    unsafe_allow_html=True,
    )

    # Chat history
    for msg in manager.messages:
        with st.chat_message(msg["role"]):
            _render_chat_message(msg)

    # Input
    if user_input := st.chat_input("Send a message..."):
        if not user_input.strip():
            st.warning("Please enter a message before sending.")
        else:
            with st.chat_message("user"):
                st.markdown(user_input.strip())
            with st.chat_message("assistant"):
                st.write_stream(manager.process_user_message_stream(user_input.strip()))
            st.rerun()

    # Allow ending practice at any time after ≥1 exchange
    if manager.turn_count >= 1:
        st.divider()
        if st.button("Done practising — start the experiment", type="primary"):
            return True
    return False


# ═══════════════════════════════════════════════════════════════
# SCREEN 6 — TRIAL INTRO
# ═══════════════════════════════════════════════════════════════

def render_trial_intro(trial_number: int, total_trials: int, task_prompt: str) -> bool:
    """Show task description before a trial starts."""
    st.header(f"Conversation {trial_number} of {total_trials}")
    st.markdown(f'''
    <div style="
        background:#12141a; border-radius:10px; padding:16px 18px; margin:20px 0;
        border-left:3px solid #58a6ff; font-size:0.95rem; color:#ccc; line-height:1.55;
    ">
        <div style="color:#777; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Your Task</div>
        {html_module.escape(task_prompt)}
    </div>''',
    unsafe_allow_html=True,
    )
    if st.button("Start conversation", type="primary"):
        return True
    return False


# ═══════════════════════════════════════════════════════════════
# SCREEN 7 — TRIAL CHAT (core screen)
# ═══════════════════════════════════════════════════════════════

def _render_retrieval_debug(retrieval) -> None:
    """Show HyDE passages and retrieval metrics (dev=flow and dev mode)."""
    from core.ad_injection.models import AdRetrievalResult

    if retrieval is None:
        st.caption("No retrieval yet — send a message with ad injection enabled.")
        return
    if not isinstance(retrieval, AdRetrievalResult):
        return

    diag = retrieval.diag or {}
    st.caption(f"Retrieval query ({diag.get('query_chars', '?')} chars)")
    rq = diag.get("retrieval_query")
    if rq:
        st.text(rq)

    docs = diag.get("hyde_documents") or []
    if docs:
        st.markdown(f"**HyDE documents ({len(docs)})**")
        llm_cap = diag.get("hyde_llm_max_tokens")
        token_counts = diag.get("hyde_doc_token_counts") or []
        cap_note = f" · num_predict={llm_cap}" if llm_cap else ""
        for i, doc in enumerate(docs, 1):
            tok = token_counts[i - 1] if i - 1 < len(token_counts) else None
            label = f"Doc {i} · {len(doc)} chars"
            if tok is not None:
                label += f" · {tok} tokens"
            label += cap_note if i == 1 else ""
            with st.expander(label, expanded=(i == 1)):
                st.text(doc)
    elif diag.get("hyde_used"):
        st.warning("HyDE ran but no documents were parsed from the LLM response.")

    if retrieval.has_ads:
        st.markdown("**Catalog matches (top ads)**")
        for j, ad in enumerate(retrieval.ads, 1):
            score = ad.relevance_score
            st.markdown(f"{j}. **{ad.title}** — score {score:.3f}" if score else f"{j}. **{ad.title}**")
    else:
        st.caption("No ads returned from the pipeline.")

    metrics = {k: v for k, v in diag.items() if k not in ("hyde_documents", "retrieval_query")}
    if metrics:
        with st.expander("Timing & config", expanded=False):
            st.json(metrics)


def _render_flow_ad_panel(manager: ConversationManager, ad_mode: str) -> None:
    """Dev/flow helper: surface ads even when the mode hides them (e.g. inline)."""
    st.markdown(f"**Ad mode:** {AD_MODE_LABELS.get(ad_mode, ad_mode)}")
    _render_retrieval_debug(manager.last_retrieval)

    if not _ad_display_state_matches_mode(manager, ad_mode):
        cached = getattr(manager, "last_retrieval_ad_mode", None)
        if manager.last_retrieval and manager.last_retrieval.has_ads and cached and cached != ad_mode:
            st.caption(
                f"Ad cached from **{AD_MODE_LABELS.get(cached, cached)}** — "
                "send a message to refresh for the selected mode."
            )
        else:
            st.caption("No ad retrieved yet — send a message with **Inject ad every turn** enabled.")
        return

    if ad_mode == "inline_persuasive":
        with st.expander("Candidate products shown to the LLM (title + CTA only)", expanded=True):
            st.markdown(format_products_block(manager.last_retrieval.ads))
        st.caption(
            "Inline mode weaves the ad into the assistant reply; "
            "the product name is a clickable link in the text."
        )
        return

    injector = get_injector(ad_mode)
    result = injector.inject(manager.last_retrieval, manager.messages)
    primary = manager.last_retrieval.primary if manager.last_retrieval else None

    if result.display_payload:
        primary = manager.last_retrieval.primary if manager.last_retrieval else None
        _render_ad_banner(
            result.display_payload,
            ad_mode=ad_mode,
            manager=manager,
            turn=manager.turn_count,
            ad=primary,
        )
def render_trial_chat(
    manager: ConversationManager,
    ad_mode: str,
    flow_test: bool = False,
) -> bool:
    """
    Main chat interface. Returns True when the trial ends
    (user clicks "I've finished" or max turns reached).
    """
    start_ad_click_server()
    register_click_state(manager.logger, manager, ad_mode)
    inject_ad_click_tracker()

    # Task reminder at top
    if manager.task:
        st.markdown(f'''
        <div style="
            background:#12141a; border-radius:10px; padding:14px 16px; margin-bottom:16px;
            border-left:3px solid #58a6ff; font-size:0.85rem; color:#ccc; line-height:1.55;
        ">
            <div style="color:#777; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Your Task</div>
            {html_module.escape(manager.task.participant_prompt)}
        </div>''',
        unsafe_allow_html=True,
        )

    # Turn progress + finish button in sidebar
    with st.sidebar:
        progress = min(manager.turn_count / manager.max_turns, 1.0)
        st.progress(progress, text=f"Turn {manager.turn_count} / {manager.max_turns}")

        # "I've finished" button — visible from manager.finish_from onwards
        if manager.turn_count >= manager.finish_from:
            if manager.turn_count < manager.min_turns:
                st.info(
                    f"💬 Keep chatting — you need at least {manager.min_turns} turns "
                    "before you can finish."
                )
            else:
                st.success("You can keep chatting or finish when you're ready.")
            if st.button("🏁 I've finished", type="primary", use_container_width=True):
                return True

    _render_chat_history(manager, ad_mode)

    # Dev flow: always show what was retrieved / shown to the LLM
    if flow_test:
        with st.expander("🎯 Ad debug (dev=flow)", expanded=True):
            _render_flow_ad_panel(manager, ad_mode)

    # Compact ads above chat input (banner where applicable)
    _render_turn_ads(manager, ad_mode)

    # Max turns reached → show goodbye + done button
    if manager.must_end:
        from core.config import GOODBYE_MESSAGE
        if not any(m.get("role") == "assistant" and m.get("content") == GOODBYE_MESSAGE for m in manager.messages):
            manager.messages.append({"role": "assistant", "content": GOODBYE_MESSAGE})
        with st.chat_message("assistant"):
            st.markdown(GOODBYE_MESSAGE)
        if st.button("Done", type="primary", use_container_width=True):
            return True
    else:
        if user_input := st.chat_input("Send a message..."):
            if not user_input.strip():
                st.warning("Please enter a message before sending.")
            else:
                with st.chat_message("user"):
                    st.markdown(user_input.strip())
                with st.chat_message("assistant"):
                    st.write_stream(manager.process_user_message_stream(user_input.strip()))
                st.rerun()

    return False


def _render_ad_card(payload: dict, container=None, *, ad_mode: str | None = None) -> None:
    """Backward-compatible alias — banner is always full width."""
    _ = container
    _render_ad_banner(payload, ad_mode=ad_mode)


# ═══════════════════════════════════════════════════════════════
# SCREEN 8 — POST-TRIAL SURVEY
# ═══════════════════════════════════════════════════════════════

def render_post_trial_survey(trial_number: int) -> Optional[dict]:
    """
    Likert survey after each trial.
    Returns dict of {item_id: score} on submit, None otherwise.
    """
    st.header(f"Post-Task Questionnaire (Trial {trial_number})")
    st.caption("Please rate the following statements about the conversation you just had.")

    responses: dict[str, int] = {}
    all_answered = True

    for item in POST_TRIAL_ITEMS:
        value = st.radio(
            item["text"],
            options=list(range(POST_TRIAL_SCALE_MIN, POST_TRIAL_SCALE_MAX + 1)),
            format_func=lambda v: f"{v}",
            horizontal=True,
            index=None,
            key=f"post_trial_{trial_number}_{item['id']}",
        )
        if value is None:
            all_answered = False
        else:
            responses[item["id"]] = value

    # Progress bar
    answered = sum(1 for v in responses.values() if v is not None)
    total = len(POST_TRIAL_ITEMS)
    st.progress(answered / total, text=f"{answered} of {total} answered")

    st.divider()
    if all_answered and st.button("Continue", type="primary"):
        invalid = [
            iid for iid, v in responses.items()
            if not (POST_TRIAL_SCALE_MIN <= v <= POST_TRIAL_SCALE_MAX)
        ]
        if invalid:
            st.error(f"Invalid response values detected ({invalid}). Please re-select those items.")
            return None
        return responses
    elif not all_answered:
        st.info("Please answer all statements to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# SCREEN 9 — FINAL SURVEY
# ═══════════════════════════════════════════════════════════════

def render_final_survey() -> Optional[dict]:
    """
    Global end-of-session survey + open-ended debrief question.
    Returns dict on submit, None otherwise.
    """
    st.header("Final Survey")
    st.caption("Please reflect on the entire session.")

    responses: dict[str, int | str] = {}
    all_answered = True

    for item in FINAL_SURVEY_ITEMS:
        value = st.radio(
            item["text"],
            options=list(range(POST_TRIAL_SCALE_MIN, POST_TRIAL_SCALE_MAX + 1)),
            format_func=lambda v: f"{v}",
            horizontal=True,
            index=None,
            key=f"final_{item['id']}",
        )
        if value is None:
            all_answered = False
        else:
            responses[item["id"]] = value

    # Progress bar (Likert items only)
    answered_likert = sum(1 for v in responses.values() if isinstance(v, int))
    total_likert = len(FINAL_SURVEY_ITEMS)
    st.progress(answered_likert / total_likert, text=f"{answered_likert} of {total_likert} answered")

    st.divider()
    st.subheader("Debrief")
    open_text = st.text_area(FINAL_OPEN_ENDED_PROMPT, key="final_open_ended")
    responses["open_ended"] = open_text

    if all_answered and st.button("Submit", type="primary"):
        invalid = [
            iid for iid, v in responses.items()
            if isinstance(v, int) and not (POST_TRIAL_SCALE_MIN <= v <= POST_TRIAL_SCALE_MAX)
        ]
        if invalid:
            st.error(f"Invalid response values detected ({invalid}). Please re-select those items.")
            return None
        return responses
    elif not all_answered:
        st.info("Please answer all Likert statements to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════

def render_instructions() -> bool:
    """Brief task explanation before warm-up."""
    st.header("About This Study")
    st.markdown(
        "You will chat with an AI assistant across several "
        "short conversations. Each conversation will present you with "
        "a different task.\n\n"
        "After each conversation, you will answer a few brief statements "
        "about your experience.\n\n"
        "Take your time and interact naturally with the assistant."
    )
    return st.button("Begin", type="primary")


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — WARM-UP CHAT
# ═══════════════════════════════════════════════════════════════

def render_warmup_chat(manager: ConversationManager) -> bool:
    """
    Warm-up conversation — no ads, no Likert after.
    Returns True when user clicks 'Done'.
    """
    st.header("Warm-Up Conversation")

    # Turn progress in sidebar
    with st.sidebar:
        progress = min(manager.turn_count / manager.max_turns, 1.0)
        st.progress(progress, text=f"Turn {manager.turn_count} / {manager.max_turns}")

    # Task prompt in blue box
    st.markdown(f'''
    <div style="
        background:#12141a; border-radius:10px; padding:16px 18px; margin:20px 0;
        border-left:3px solid #58a6ff; font-size:0.95rem; color:#ccc; line-height:1.55;
    ">
        <div style="color:#777; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Your Task</div>
        {html_module.escape(WARMUP_PROMPT)}
    </div>''',
    unsafe_allow_html=True,
    )

    for msg in manager.messages:
        with st.chat_message(msg["role"]):
            _render_chat_message(msg)

    if manager.must_end:
        if st.button("Done", type="primary", use_container_width=True):
            return True
    else:
        if manager.turn_count >= 1:
            st.divider()
            if st.button("Done", type="primary", use_container_width=True):
                return True
        if user_input := st.chat_input("Send a message..."):
            if user_input.strip():
                with st.chat_message("user"):
                    st.markdown(user_input.strip())
                with st.chat_message("assistant"):
                    st.write_stream(manager.process_user_message_stream(user_input.strip()))
                st.rerun()

    return False


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — FIRST IMPRESSION (non-Likert)
# ═══════════════════════════════════════════════════════════════

def render_first_impression() -> Optional[dict]:
    """
    Lightweight baseline — no Likert scales.

    Collects:
      - first_impression_text (free-text)
      - reuse_intent (Yes / Maybe / No)
      - sentiment_label (Negative / Neutral / Positive)
    """
    st.header("Your First Impression")
    st.caption("Please share your initial thoughts about the system.")

    text = st.text_area(
        "1. Please describe your first impression of the system after your initial interaction in one sentence.",
        key="first_impression_text",
    )

    sentiment = st.radio(
        "2. Overall, how would you describe your experience so far?",
        ["Negative", "Neutral", "Positive"],
        index=None,
        horizontal=True,
        key="first_impression_sentiment",
    )

    reuse = st.radio(
        "3. Based on your initial interaction, would you use this assistant again?",
        ["Yes", "Maybe", "No"],
        index=None,
        horizontal=True,
        key="first_impression_reuse",
    )

    all_filled = bool(text and reuse and sentiment)
    answered_count = sum([bool(text), bool(sentiment), bool(reuse)])
    st.progress(answered_count / 3, text=f"{answered_count} of 3 answered")
    if all_filled and st.button("Continue", type="primary"):
        return {
            "first_impression_text": text,
            "reuse_intent": reuse,
            "sentiment_label": sentiment,
        }
    elif not all_filled:
        st.info("Please answer all statements to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — CONDITION INTRO
# ═══════════════════════════════════════════════════════════════

def render_condition_intro(
    condition_number: int,
    total_conditions: int,
    condition_id: str,
    task: TaskDefinition,
) -> bool:
    from core.config import TASK_CONTEXT_WARNING
    st.header(f"Conversation {condition_number} of {total_conditions}")
    st.markdown(f'''
    <div style="
        background:#1a1a0e; border-radius:10px; padding:12px 16px; margin:12px 0 16px 0;
        border-left:4px solid #ffd700; font-size:0.85rem; color:#e0d080; line-height:1.5;
    ">
        ⚠️ {html_module.escape(TASK_CONTEXT_WARNING)}
    </div>''',
    unsafe_allow_html=True,
    )
    st.markdown(f'''
    <div style="
        background:#12141a; border-radius:10px; padding:16px 18px; margin:20px 0;
        border-left:3px solid #58a6ff; font-size:0.95rem; color:#ccc; line-height:1.55;
    ">
        <div style="color:#777; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Your Task</div>
        {html_module.escape(task.participant_prompt)}
    </div>''',
    unsafe_allow_html=True,
    )
    if st.button("Start conversation", type="primary"):
        return True
    return False


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — CONDITION CHAT
# ═══════════════════════════════════════════════════════════════

def render_condition_chat(
    manager: ConversationManager,
    condition_id: str,
    flow_test: bool = False,
) -> bool:
    """
    Condition-aware chat interface.

    Handles no_ads (no ad injection) and ad conditions (single ad at ad_turn).
    Participants must complete all turns; after the final turn a goodbye
    message appears with a single Done button.
    """
    from core.config import CONDITION_AD_MODE

    ad_mode = CONDITION_AD_MODE.get(condition_id, "")
    start_ad_click_server()
    register_click_state(manager.logger, manager, condition_id)
    inject_ad_click_tracker()

    label = CONDITION_LABELS.get(condition_id, condition_id)

    if manager.task:
        st.markdown(f'''
        <div style="
            background:#12141a; border-radius:10px; padding:14px 16px; margin-bottom:16px;
            border-left:3px solid #58a6ff; font-size:0.85rem; color:#ccc; line-height:1.55;
        ">
            <div style="color:#777; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Your Task</div>
            {html_module.escape(manager.task.participant_prompt)}
        </div>''',
        unsafe_allow_html=True,
        )

    with st.sidebar:
        progress = min(manager.turn_count / manager.max_turns, 1.0)
        st.progress(progress, text=f"Turn {manager.turn_count} / {manager.max_turns}")
        if flow_test:
            st.caption(f"Condition: {label}")

    _render_chat_history(manager, ad_mode)

    if flow_test:
        with st.expander("🎯 Ad debug (dev=flow)", expanded=True):
            _render_flow_ad_panel(manager, ad_mode)

    if condition_id != "no_ads":
        _render_turn_ads(manager, ad_mode)

    if manager.must_end:
        from core.config import GOODBYE_MESSAGE
        if not any(m.get("role") == "assistant" and m.get("content") == GOODBYE_MESSAGE for m in manager.messages):
            manager.messages.append({"role": "assistant", "content": GOODBYE_MESSAGE})
        with st.chat_message("assistant"):
            st.markdown(GOODBYE_MESSAGE)
        if st.button("Done", type="primary", use_container_width=True):
            return True
    else:
        if user_input := st.chat_input("Send a message..."):
            if not user_input.strip():
                st.warning("Please enter a message before sending.")
            else:
                with st.chat_message("user"):
                    st.markdown(user_input.strip())
                with st.chat_message("assistant"):
                    st.write_stream(manager.process_user_message_stream(user_input.strip()))
                st.rerun()

    return False


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — TASK CONCLUSION
# ═══════════════════════════════════════════════════════════════

def render_condition_conclusion(
    condition_number: int,
    total_conditions: int,
    task_title: str,
    task_prompt: str,
) -> Optional[dict]:
    """
    Post-chat conclusion screen: user writes their findings/results.

    Returns dict on submit, None otherwise.
    """
    st.header(f"Conversation {condition_number} of {total_conditions} — Your Findings")
    st.caption("Before moving on, please summarise what you learned from this conversation.")

    st.markdown(f'''
    <div style="
        background:#12141a; border-radius:10px; padding:16px 18px; margin:20px 0;
        border-left:3px solid #58a6ff; font-size:0.95rem; color:#ccc; line-height:1.55;
    ">
        <div style="color:#777; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Your Task</div>
        <strong style="color:#e0e0e0; display:block; margin-bottom:6px;">{html_module.escape(task_title)}</strong>
        {html_module.escape(task_prompt)}
    </div>''',
    unsafe_allow_html=True,
    )

    conclusion = st.text_area(
        "What did you find? What conclusions or decisions did you reach?",
        height=250,
        placeholder="Describe what information you found, what you decided, or what you learned...",
        key=f"condition_conclusion_{condition_number}",
    )

    if st.button("Submit findings", type="primary"):
        if not conclusion.strip():
            st.warning("Please write something before submitting.")
            return None
        return {"conclusion": conclusion.strip(), "task_title": task_title}

    return None


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — POST-CONDITION SURVEY
# ═══════════════════════════════════════════════════════════════

def _step_indicator(current: int, total: int) -> str:
    """HTML step indicator: filled circles for completed/current, empty for remaining."""
    dots = []
    for i in range(total):
        if i < current:
            dots.append("&#9679;")   # filled
        elif i == current:
            dots.append("&#9679;")   # current (filled, highlighted below)
        else:
            dots.append("&#9678;")   # hollow
    # current step gets accent colour; completed steps muted
    steps_html = "".join(
        f'<span style="color:{"#ff9800" if i == current else "#555"}; '
        f'font-size:1.6rem; margin:0 4px;">{d}</span>'
        for i, d in enumerate(dots)
    )
    labels_html = (
        f'<div style="display:flex; justify-content:center; gap:20px; '
        f'font-size:0.8rem; color:#888; margin-top:-6px;">'
        f'<span>Evaluation</span>'
        f'<span>Personality</span>'
        f'<span>Behaviours</span>'
        f'</div>'
    )
    return f'<div style="text-align:center; padding:12px 0;">{steps_html}</div>{labels_html}'


def render_post_condition_survey(condition_number: int) -> Optional[dict]:
    """
    3-section multi-step post-condition survey:
      1. LLM Evaluation (15 items, 7-pt Likert)
      2. Chatbot Personality (3 Likert + text, 2 open-ended)
      3. LLM Behaviours (2 Likert, 7-pt)
    Progress is tracked in session state per condition_number.
    """
    st.header("Post-Task Questionnaire")

    section_key = f"pcs_section_{condition_number}"
    if section_key not in st.session_state:
        st.session_state[section_key] = 0

    responses_key = f"pcs_responses_{condition_number}"
    if responses_key not in st.session_state:
        st.session_state[responses_key] = {}

    section = st.session_state[section_key]
    responses = st.session_state[responses_key]

    # Step indicator at top
    st.markdown(_step_indicator(section, 3), unsafe_allow_html=True)

    # ── Section 1: LLM Performance Evaluation ──────────────────
    if section == 0:
        st.subheader("Evaluation")
        st.caption(
            "Please rate your level of agreement with the following statements about the chatbot. "
            "(1 = Strongly disagree, 7 = Strongly agree)."
        )
        all_answered = True
        for item in POST_CONDITION_LLM_ITEMS:
            value = st.radio(
                item["text"],
                options=list(range(POST_CONDITION_SCALE_MIN, POST_CONDITION_SCALE_MAX + 1)),
                format_func=lambda v: f"{v}",
                horizontal=True,
                index=None,
                key=f"pcs_llm_{condition_number}_{item['id']}",
            )
            if value is None:
                all_answered = False
            else:
                responses[item["id"]] = value

        answered_llm = sum(1 for item in POST_CONDITION_LLM_ITEMS if item["id"] in responses)
        st.progress(answered_llm / len(POST_CONDITION_LLM_ITEMS), text=f"Section 1: {answered_llm} of {len(POST_CONDITION_LLM_ITEMS)} answered")

        st.divider()
        if all_answered and st.button("Continue", type="primary"):
            st.session_state[responses_key] = responses
            st.session_state[section_key] = 1
            st.rerun()
        elif not all_answered:
            st.info("Please answer all statements to continue.")
        return None

    # ── Section 2: Chatbot Personality ─────────────────────────
    elif section == 1:
        st.subheader("Personality")
        st.caption(
            "Please rate your level of agreement with the following statements about the chatbot. "
            "(1 = Strongly disagree, 7 = Strongly agree). "
            "There are optional open-ended fields if you would like to give more detail."
        )
        all_answered = True

        for item in POST_CONDITION_PERSONALITY_LIKERT:
            value = st.radio(
                item["text"],
                options=list(range(POST_CONDITION_SCALE_MIN, POST_CONDITION_SCALE_MAX + 1)),
                format_func=lambda v: f"{v}",
                horizontal=True,
                index=None,
                key=f"pcs_pers_lik_{condition_number}_{item['id']}",
            )
            if value is None:
                all_answered = False
            else:
                responses[item["id"]] = value
            elab = st.text_area(
                item["elaboration"],
                key=f"pcs_pers_txt_{condition_number}_{item['id']}",
            )
            responses[f"{item['id']}_text"] = elab

        all_open_answered = True
        for item in POST_CONDITION_PERSONALITY_OPEN:
            value = st.radio(
                item["text"],
                options=list(range(POST_CONDITION_SCALE_MIN, POST_CONDITION_SCALE_MAX + 1)),
                format_func=lambda v: f"{v}",
                horizontal=True,
                index=None,
                key=f"pcs_pers_open_lik_{condition_number}_{item['id']}",
            )
            if value is None:
                all_answered = False
            else:
                responses[item["id"]] = value
            elab = st.text_area(
                item["elaboration"],
                key=f"pcs_pers_open_txt_{condition_number}_{item['id']}",
            )
            responses[f"{item['id']}_text"] = elab

        answered_s2 = sum(
            1 for item in POST_CONDITION_PERSONALITY_LIKERT
            if item["id"] in responses and responses[item["id"]] is not None
        ) + sum(
            1 for item in POST_CONDITION_PERSONALITY_OPEN
            if item["id"] in responses and responses[item["id"]] is not None
        )
        total_s2 = len(POST_CONDITION_PERSONALITY_LIKERT) + len(POST_CONDITION_PERSONALITY_OPEN)
        st.progress(answered_s2 / total_s2, text=f"Section 2: {answered_s2} of {total_s2} answered")

        st.divider()
        if all_answered and st.button("Continue", type="primary"):
            st.session_state[responses_key] = responses
            st.session_state[section_key] = 2
            st.rerun()
        elif not all_answered:
            st.info("Please answer all Likert statements to continue.")
        return None

    # ── Section 3: LLM Behaviours ──────────────────────────────
    elif section == 2:
        st.subheader("Behaviours")
        st.caption(
            "Please rate your level of agreement with the following statements about the chatbot. "
            "(1 = Strongly disagree, 7 = Strongly agree)."
        )
        all_answered = True

        for item in POST_CONDITION_BEHAVIOUR_ITEMS:
            value = st.radio(
                item["text"],
                options=list(range(POST_CONDITION_SCALE_MIN, POST_CONDITION_SCALE_MAX + 1)),
                format_func=lambda v: f"{v}",
                horizontal=True,
                index=None,
                key=f"pcs_beh_{condition_number}_{item['id']}",
            )
            if value is None:
                all_answered = False
            else:
                responses[item["id"]] = value

        answered_s3 = sum(1 for item in POST_CONDITION_BEHAVIOUR_ITEMS if item["id"] in responses)
        st.progress(answered_s3 / len(POST_CONDITION_BEHAVIOUR_ITEMS), text=f"Section 3: {answered_s3} of {len(POST_CONDITION_BEHAVIOUR_ITEMS)} answered")

        st.divider()
        if all_answered and st.button("Submit", type="primary"):
            del st.session_state[section_key]
            del st.session_state[responses_key]
            return responses
        elif not all_answered:
            st.info("Please answer all statements to continue.")
        return None


# ═══════════════════════════════════════════════════════════════
# RECALL  (post-experiment, 4-step — one per ad condition)
# ═══════════════════════════════════════════════════════════════

def _ad_condition_label(condition_id: str, step: int = 0) -> str:
    """Short label for an ad condition — numbered by presentation order."""
    return f"Conversation {step + 1}"

def render_ads_recall() -> Optional[dict]:
    """
    4-step recall section, one step per ad condition (no_ads excluded).
    Each step shows the ad that was presented (title, description, task prompt,
    image if available, and inline context for inline modes), followed by
    7 Likert statements (noticeability → system trust shift) + 1 open-ended.
    """
    st.header("Recall")

    ctrl = st.session_state.controller
    ad_conditions = [
        cfg for cfg in ctrl.condition_plan
        if cfg["condition"] != "no_ads"
    ]

    step_key = "recall_step"
    if step_key not in st.session_state:
        st.session_state[step_key] = 0

    responses_key = "recall_responses"
    if responses_key not in st.session_state:
        st.session_state[responses_key] = {}

    step = st.session_state[step_key]
    responses = st.session_state[responses_key]

    # Look up the condition_result for this condition to get ad_info
    cfg = ad_conditions[step]
    cond_id = cfg["condition"]
    result = next((r for r in ctrl.condition_results if r.get("condition_id") == cond_id), {})
    ad_info = result.get("ad_info")
    task_prompt = result.get("task_prompt", "")

    # Step indicator
    total = len(ad_conditions)
    dots_html = "".join(
        f'<span style="color:{"#ff9800" if i == step else "#555"}; '
        f'font-size:1.6rem; margin:0 4px;">'
        f'{"&#9679;" if i <= step else "&#9678;"}</span>'
        for i in range(total)
    )
    st.markdown(
        f'<div style="text-align:center; padding:12px 0;">{dots_html}</div>'
        f'<div style="text-align:center; font-size:0.85rem; color:#888; '
        f'margin-top:-4px;">Step {step + 1} of {total}</div>',
        unsafe_allow_html=True,
    )

    label = _ad_condition_label(cond_id, step)
    st.subheader(label)

    # ── Instruction text ───────────────────────────────────────
    st.markdown(
        f'<div style="font-size:0.85rem; color:#999; line-height:1.5; margin-bottom:12px;">'
        f'Below is a summary of what happened in this conversation. '
        f'Review it, then answer the statements below.</div>',
        unsafe_allow_html=True,
    )

    # ── Task context (above ad card) ──────────────────────────
    if task_prompt:
        st.markdown(f'''
        <div style="
            background:#12141a; border-radius:10px; padding:14px 16px; margin-bottom:16px;
            border-left:3px solid #58a6ff; font-size:0.85rem; color:#ccc; line-height:1.55;
        ">
            <div style="color:#777; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Your Task</div>
            {html_module.escape(task_prompt)}
        </div>''',
        unsafe_allow_html=True,
    )

    # ── Ad card ───────────────────────────────────────────────
    if ad_info:
        img_url = ad_info.get("image_url")
        ad_mode_type = ad_info.get("ad_mode", "")
        is_inline = ad_mode_type in ("inline_early", "inline_late")

        mode_tag = "In-Conversation Mention" if is_inline else "Promotional Card"
        mode_color = "#e6b91e" if is_inline else "#ff6b35"

        parts = [f'''<div style="
            background: linear-gradient(135deg, #1a1d24 0%, #20232b 100%);
            border-radius:14px; padding:20px; margin:0 0 24px 0;
            border:1px solid #333; box-shadow:0 4px 16px rgba(0,0,0,0.3);
        ">''']

        # ── Header row: mode tag ──
        parts.append(f'''
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
            <span style="
                background:{mode_color}22; color:{mode_color};
                font-size:0.7rem; font-weight:600; letter-spacing:0.5px;
                padding:3px 10px; border-radius:20px; border:1px solid {mode_color}44;
            ">{mode_tag}</span>
        </div>''')

        # ── Body: image + details ──
        parts.append('<div style="display:flex; gap:16px; align-items:flex-start;">')

        if img_url:
            parts.append(f'''
            <div style="flex-shrink:0;">
                <img src="{html_module.escape(img_url)}"
                     style="width:88px; height:88px; object-fit:cover; border-radius:10px;
                            border:1px solid #3a3a3a; background:#0d0d0d;"
                     alt="Product image" />
            </div>''')

        parts.append('<div style="flex:1; min-width:0;">')
        parts.append(f'''
        <div style="font-size:1.05rem; font-weight:600; color:#f0f0f0; margin-bottom:4px; line-height:1.3;">
            {html_module.escape(ad_info["title"])}
        </div>''')
        parts.append(f'''
        <div style="font-size:0.88rem; color:#bbb; line-height:1.5; margin-bottom:8px;">
            {html_module.escape(ad_info["text"])}
        </div>''')

        if ad_info.get("cta"):
            parts.append(f'''
        <div style="display:inline-block; background:{mode_color}18; color:{mode_color};
                    font-size:0.78rem; font-weight:500; padding:3px 12px; border-radius:6px;
                    border:1px solid {mode_color}33;">
            {html_module.escape(ad_info["cta"])}
        </div>''')

        parts.append('</div>')  # end details column
        parts.append('</div>')  # end body row

        # ── Product URL ──
        product_url = ad_info.get("product_url")
        if product_url:
            parts.append(f'''
        <div style="margin-top:12px; font-size:0.78rem; color:#58a6ff;">
            🔗 {html_module.escape(product_url)}
        </div>''')

        # ── Inline context: conversation excerpt ──
        ctx_before = ad_info.get("inline_ctx_before", [])
        inline_user = ad_info.get("inline_user_msg")
        inline_asst = ad_info.get("inline_response")
        ctx_after = ad_info.get("inline_ctx_after", [])
        if is_inline and (ctx_before or inline_user or inline_asst or ctx_after):
            title = ad_info["title"]
            parts.append(f'''
        <div style="margin-top:14px; border-top:1px solid #333; padding-top:14px;">
            <div style="color:#888; font-size:0.7rem; font-weight:600; letter-spacing:0.5px; margin-bottom:10px;">
                ╱  CONVERSATION CONTEXT
            </div>''')
            for ctx_msg in ctx_before:
                role = ctx_msg.get("role", "")
                content = ctx_msg.get("content", "")
                bubble_bg = "#161b22" if role == "user" else "#0d1117"
                bubble_r = "10px 10px 10px 4px" if role == "user" else "10px 10px 4px 10px"
                avatar_bg = "#30363d" if role == "user" else "#1f6feb"
                avatar_l = "U" if role == "user" else "A"
                parts.append(f'''
            <div style="display:flex; gap:10px; margin-bottom:8px;">
                <div style="width:28px; height:28px; border-radius:50%; background:{avatar_bg}; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:0.7rem; color:#ccc;">{avatar_l}</div>
                <div style="flex:1; background:{bubble_bg}; border:{'1px solid #2d2d2d' if role == 'assistant' else 'none'}; border-radius:{bubble_r}; padding:10px 14px; font-size:0.82rem; color:#c9d1d9; line-height:1.5; white-space:pre-wrap;">{html_module.escape(content)}</div>
            </div>''')
            # User message at injection turn
            if inline_user:
                parts.append(f'''
            <div style="display:flex; gap:10px; margin-bottom:8px;">
                <div style="width:28px; height:28px; border-radius:50%; background:#30363d; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:0.7rem; color:#ccc;">U</div>
                <div style="flex:1; background:#161b22; border-radius:10px 10px 10px 4px; padding:10px 14px; font-size:0.82rem; color:#c9d1d9; line-height:1.5;">{html_module.escape(inline_user)}</div>
            </div>''')
            # Assistant response at injection turn
            if inline_asst:
                highlighted = html_module.escape(inline_asst).replace(
                    html_module.escape(title),
                    f'<strong style="color:{mode_color}">{html_module.escape(title)}</strong>',
                )
                parts.append(f'''
            <div style="display:flex; gap:10px; margin-bottom:8px;">
                <div style="width:28px; height:28px; border-radius:50%; background:#1f6feb; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:0.7rem; color:#fff;">A</div>
                <div style="flex:1; background:#0d1117; border:1px solid #2d2d2d; border-radius:10px 10px 4px 10px; padding:10px 14px; font-size:0.82rem; color:#c9d1d9; line-height:1.55; white-space:pre-wrap;">{highlighted}</div>
            </div>''')
            for ctx_msg in ctx_after:
                role = ctx_msg.get("role", "")
                content = ctx_msg.get("content", "")
                bubble_bg = "#161b22" if role == "user" else "#0d1117"
                bubble_r = "10px 10px 10px 4px" if role == "user" else "10px 10px 4px 10px"
                avatar_bg = "#30363d" if role == "user" else "#1f6feb"
                avatar_l = "U" if role == "user" else "A"
                parts.append(f'''
            <div style="display:flex; gap:10px; margin-bottom:4px;">
                <div style="width:28px; height:28px; border-radius:50%; background:{avatar_bg}; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:0.7rem; color:#ccc;">{avatar_l}</div>
                <div style="flex:1; background:{bubble_bg}; border:{'1px solid #2d2d2d' if role == 'assistant' else 'none'}; border-radius:{bubble_r}; padding:10px 14px; font-size:0.82rem; color:#c9d1d9; line-height:1.5; white-space:pre-wrap;">{html_module.escape(content)}</div>
            </div>''')
            parts.append('</div>')

        parts.append('</div>')
        st.markdown("".join(parts), unsafe_allow_html=True)
    else:
        st.info("No additional content was shown in this conversation.")

    # ── Likert statements ─────────────────────────────────────
    st.caption(
        "Please rate your level of agreement with the following statements about the content above. "
        "(1 = Strongly disagree, 7 = Strongly agree)."
    )
    all_answered = True
    for item in RECALL_ITEMS:
        value = st.radio(
            item["text"],
            options=list(range(RECALL_SCALE_MIN, RECALL_SCALE_MAX + 1)),
            format_func=lambda v: f"{v}",
            horizontal=True,
            index=None,
            key=f"recall_{cond_id}_{item['id']}",
        )
        if value is None:
            all_answered = False
        else:
            responses[f"{cond_id}_{item['id']}"] = value

    # ── Open-ended ────────────────────────────────────────────
    for item in RECALL_OPEN_ENDED:
        text_val = st.text_area(
            item["text"],
            key=f"recall_{cond_id}_{item['id']}",
        )
        responses[f"{cond_id}_{item['id']}"] = text_val
        if not text_val.strip():
            all_answered = False

    st.divider()
    if step < total - 1:
        if all_answered and st.button("Continue", type="primary"):
            st.session_state[responses_key] = responses
            st.session_state[step_key] = step + 1
            st.rerun()
        elif not all_answered:
            st.info("Please answer all statements to continue.")
    else:
        if all_answered and st.button("Submit", type="primary"):
            del st.session_state[step_key]
            del st.session_state[responses_key]
            return responses
        elif not all_answered:
            st.info("Please answer all statements to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# DEMOGRAPHICS (post-experiment, Section 6 – optional)
# ═══════════════════════════════════════════════════════════════

def render_demographics_end() -> Optional[dict]:
    st.header("Demographics and Usage")
    st.caption("All fields are optional.")

    responses: dict = {}

    for item in DEMOGRAPHICS_TEXT:
        value = st.text_input(item["text"], key=f"demo_end_{item['id']}")
        responses[item["id"]] = value

    for item in DEMOGRAPHICS_SELECT:
        value = st.radio(
            item["text"],
            item["options"],
            index=None,
            horizontal=False,
            key=f"demo_end_{item['id']}",
        )
        responses[item["id"]] = value

    st.divider()
    if st.button("Continue", type="primary"):
        return responses
    return None


# ═══════════════════════════════════════════════════════════════
# DECEPTION DISCLOSURE  (Section 7 of post-experiment)
# ═══════════════════════════════════════════════════════════════

def render_deception_disclosure() -> Optional[dict]:
    st.header("Deception Disclosure")
    st.markdown(DECEPTION_DISCLOSURE_TEXT)
    st.divider()

    withdraw = st.text_input(
        'Type "Withdraw" below if you would like to withdraw from this study. Otherwise, leave this blank and continue.',
        key="deception_withdraw",
    )

    if st.button("Continue", type="primary"):
        withdrew = withdraw.strip().lower() == "withdraw"
        return {"withdrew": withdrew, "withdraw_text": withdraw.strip() if withdrew else ""}
    return None


# ═══════════════════════════════════════════════════════════════
# SCREEN 10 — DONE
# ═══════════════════════════════════════════════════════════════

def render_done():
    """Thank-you screen."""
    st.balloons()
    st.header("🎉 Thank you!")
    st.markdown(
        "You have completed the study. Your data has been saved.\n\n"
        "Please let the researcher know you are finished."
    )
