"""
Experiment Dashboard — log file analytics.

Lets you pick JSONL log files from the logs/ directory, inspect individual
events and computed statistics (response times, turns, task durations, ad
clicks, early exits, …), and aggregate across multiple files with
distribution charts.
"""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Experiment Dashboard", layout="wide")
st.title("📊 Experiment Dashboard")

# ── Config ────────────────────────────────────────────────────

LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))  # search parent to find both production/ and development/

# ── Helpers ───────────────────────────────────────────────────


def discover_log_files(base: Path) -> List[Path]:
    """Return all .jsonl files under base, sorted newest-first."""
    files = sorted(base.rglob("*.jsonl"))
    files.sort(key=lambda p: p.parent.name, reverse=True)
    return files


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Parse a JSONL file into a list of dicts (skip bad lines)."""
    rows: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def parse_ts(ts_str: str) -> Optional[datetime]:
    """Best-effort ISO-8601 parser."""
    try:
        return datetime.fromisoformat(ts_str)
    except (ValueError, TypeError):
        return None


def _flatten_data(data: Dict[str, Any], max_depth: int = 1) -> Dict[str, Any]:
    """Flatten a nested dict to top-level with dot-separated keys (shallow)."""
    flat: Dict[str, Any] = {}
    for k, v in data.items():
        if isinstance(v, dict) and max_depth > 0:
            for k2, v2 in v.items():
                flat[f"{k}.{k2}"] = v2
        else:
            flat[k] = v
    return flat


def compute_single_stats(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute summary statistics for a single log file."""
    events = [r.get("event", "") for r in rows]
    counter = Counter(events)

    # Per-conversation accumulator
    convos: Dict[str, Dict] = defaultdict(lambda: {
        "start_ts": None, "end_ts": None, "turns": 0,
        "user_msgs": 0, "assistant_msgs": 0, "ads_shown": 0,
        "task_id": None, "ad_mode": None, "trial_index": None,
        "reply_times_ms": [], "initial_intent": None,
    })

    for r in rows:
        cid = r.get("conversation_id", "")
        evt = r.get("event", "")
        ts = parse_ts(r.get("timestamp", ""))
        turn = r.get("turn", 0)
        data = r.get("data", {}) or {}

        if evt == "conversation_started":
            convos[cid]["start_ts"] = ts
            convos[cid]["task_id"] = data.get("task_id")
            convos[cid]["ad_mode"] = r.get("ad_mode")
            convos[cid]["trial_index"] = r.get("trial_index")
            convos[cid]["initial_intent"] = data.get("initial_intent")
        elif evt == "user_message":
            convos[cid]["user_msgs"] += 1
            convos[cid]["turns"] = max(convos[cid]["turns"], turn)
            ttr = data.get("time_to_reply_ms")
            if ttr is not None:
                convos[cid]["reply_times_ms"].append(ttr)
        elif evt == "assistant_reply":
            convos[cid]["assistant_msgs"] += 1
            convos[cid]["end_ts"] = ts
        elif evt == "retrieval":
            convos[cid]["ads_shown"] += 1

    ad_clicks = [r for r in rows if r.get("event") == "ad_clicked"]
    early_exits = [r for r in rows if r.get("event") == "early_exit"]
    trial_completions = [r for r in rows if r.get("event") == "trial_complete"]
    trial_ends = [r for r in rows if r.get("event") == "trial_end"]
    surveys = [r for r in rows if r.get("event") == "post_trial_survey_submitted"]

    # Per-trial duration
    trial_durations: List[Dict[str, Any]] = []
    for tc in trial_completions:
        d = tc.get("data", {}) or {}
        start = parse_ts(d.get("trial_start_ts", ""))
        end = parse_ts(d.get("trial_end_ts", ""))
        duration_s = (end - start).total_seconds() if start and end else None
        trial_durations.append({
            "trial": d.get("trial"),
            "task_id": d.get("task_id"),
            "ad_mode": d.get("ad_mode"),
            "turns": d.get("turns"),
            "duration_s": duration_s,
        })

    # Per-conversation summary
    convo_summaries = []
    for cid, c in convos.items():
        dur = None
        if c["start_ts"] and c["end_ts"]:
            dur = (c["end_ts"] - c["start_ts"]).total_seconds()
        avg_reply = None
        median_reply = None
        if c["reply_times_ms"]:
            avg_reply = sum(c["reply_times_ms"]) / len(c["reply_times_ms"])
            sorted_rt = sorted(c["reply_times_ms"])
            n = len(sorted_rt)
            mid = n // 2
            median_reply = sorted_rt[mid] if n % 2 else (sorted_rt[mid - 1] + sorted_rt[mid]) / 2
        convo_summaries.append({
            "conversation_id": cid[:8],
            "task_id": c["task_id"],
            "ad_mode": c["ad_mode"],
            "trial_index": c["trial_index"],
            "turns": c["turns"],
            "user_msgs": c["user_msgs"],
            "assistant_msgs": c["assistant_msgs"],
            "ads_shown": c["ads_shown"],
            "duration_s": dur,
            "avg_reply_ms": avg_reply,
            "median_reply_ms": median_reply,
            "initial_intent": c["initial_intent"],
        })

    return {
        "event_counts": dict(counter),
        "total_events": len(rows),
        "ad_clicks": ad_clicks,
        "early_exits": early_exits,
        "trial_completions": trial_completions,
        "trial_ends": trial_ends,
        "surveys": surveys,
        "trial_durations": trial_durations,
        "convo_summaries": convo_summaries,
    }


# ── File discovery ────────────────────────────────────────────

log_files = discover_log_files(LOG_DIR)

if not log_files:
    st.warning("No `.jsonl` log files found in `logs/`. Run an experiment first.")
    st.stop()

# Build display labels
file_options: Dict[str, Path] = {}
for p in log_files:
    exp_dir = p.parent.name
    run_file = p.name
    n_lines = sum(1 for _ in open(p, encoding="utf-8") if _.strip())
    label = f"{exp_dir}/{run_file}  ({n_lines} events)"
    file_options[label] = p

labels = list(file_options.keys())

# ── Mode selector ─────────────────────────────────────────────

mode = st.radio("Analysis mode", ["Single file", "Multi-file aggregation"], horizontal=True)

if mode == "Single file":
    # ── Single file viewer ────────────────────────────────────
    selected_label = st.selectbox("Select a log file", labels, index=0)
    selected_path = file_options[selected_label]

    rows = load_jsonl(selected_path)
    if not rows:
        st.error("File is empty or contains no valid JSON lines.")
        st.stop()

    stats = compute_single_stats(rows)

    # ── Overview metrics ──────────────────────────────────────
    st.subheader("📋 Overview")
    ec = stats["event_counts"]
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Events", stats["total_events"])
    m2.metric("User Messages", ec.get("user_message", 0))
    m3.metric("Assistant Replies", ec.get("assistant_reply", 0))
    m4.metric("Ad Clicks", len(stats["ad_clicks"]))
    m5.metric("Early Exits", len(stats["early_exits"]))

    m6, m7, m8, m9, m10 = st.columns(5)
    m6.metric("Trials Completed", len(stats["trial_completions"]))
    m7.metric("Ads Shown (retrievals)", ec.get("retrieval", 0))
    m8.metric("Surveys Submitted", len(stats["surveys"]))
    m9.metric("Conversations", len(stats["convo_summaries"]))
    m10.metric("Attention Shifts", ec.get("attention_shift", 0))

    st.divider()

    # ── Key events table ──────────────────────────────────────
    st.subheader("📌 Key Events")
    key_events = ["ad_clicked", "early_exit", "trial_complete", "trial_end",
                  "post_trial_survey_submitted", "consent_granted", "session_started"]
    key_rows = [r for r in rows if r.get("event") in key_events]
    if key_rows:
        key_df = pd.DataFrame([
            {
                "timestamp": r.get("timestamp", "")[:19],
                "event": r.get("event"),
                "trial": r.get("trial_index"),
                "turn": r.get("turn"),
                "ad_mode": r.get("ad_mode"),
                "conv_id": str(r.get("conversation_id", ""))[:8],
                **_flatten_data(r.get("data", {})),
            }
            for r in key_rows
        ])
        st.dataframe(key_df, use_container_width=True, hide_index=True)
    else:
        st.info("No key events found in this log file.")

    st.divider()

    # ── Per-conversation stats ────────────────────────────────
    st.subheader("💬 Per-Conversation Stats")
    if stats["convo_summaries"]:
        convo_df = pd.DataFrame(stats["convo_summaries"])
        for col in ("duration_s", "avg_reply_ms", "median_reply_ms"):
            if col in convo_df.columns:
                convo_df[col] = convo_df[col].apply(
                    lambda x: f"{x:.1f}" if x is not None else "—"
                )
        st.dataframe(convo_df, use_container_width=True, hide_index=True)
    else:
        st.info("No conversation data found.")

    st.divider()

    # ── Trial durations ───────────────────────────────────────
    st.subheader("⏱️ Trial Durations & Turns")
    if stats["trial_durations"]:
        td_df = pd.DataFrame(stats["trial_durations"])
        st.dataframe(td_df, use_container_width=True, hide_index=True)
        dur_data = {f"T{r['trial']} ({r['task_id']})": r["duration_s"]
                    for r in stats["trial_durations"] if r["duration_s"] is not None}
        if dur_data:
            st.bar_chart(dur_data, horizontal=True)
            st.caption("Trial duration in seconds")
    else:
        st.info("No completed trials found.")

    st.divider()

    # ── Response times ────────────────────────────────────────
    st.subheader("⏳ Response Times")
    reply_rows = [r for r in rows if r.get("event") == "user_message"]
    reply_times = []
    for r in reply_rows:
        ttr = (r.get("data", {}) or {}).get("time_to_reply_ms")
        if ttr is not None:
            reply_times.append({
                "trial": r.get("trial_index"),
                "turn": r.get("turn"),
                "time_ms": ttr,
                "time_s": ttr / 1000,
            })
    if reply_times:
        rt_df = pd.DataFrame(reply_times)
        st.dataframe(rt_df, use_container_width=True, hide_index=True)
        chart_data = {f"T{r['trial']}:Turn{r['turn']}": r["time_s"] for r in reply_times}
        st.bar_chart(chart_data)
        st.caption("User response time per turn (seconds)")
        avg_rt = sum(r["time_s"] for r in reply_times) / len(reply_times)
        median_rt = sorted(r["time_s"] for r in reply_times)[len(reply_times) // 2]
        c1, c2 = st.columns(2)
        c1.metric("Avg Response Time", f"{avg_rt:.1f}s")
        c2.metric("Median Response Time", f"{median_rt:.1f}s")
    else:
        st.info("No response time data (time_to_reply_ms is null for first messages).")

    st.divider()

    # ── Attention shift ───────────────────────────────────────
    st.subheader("📐 Attention Shift")
    shifts = [r for r in rows if r.get("event") == "attention_shift"]
    if shifts:
        shift_data = [{"index": i + 1, "trial": s.get("trial_index"),
                       "turn": s.get("turn"),
                       "divergence": (s.get("data", {}) or {}).get("divergence", 0)}
                      for i, s in enumerate(shifts)]
        sd_df = pd.DataFrame(shift_data)
        st.line_chart(sd_df.set_index("index")["divergence"])
        st.caption("Attention shift divergence (JSD) per event")
    else:
        st.info("No attention shift data in this log.")

    st.divider()

    # ── Post-trial survey ─────────────────────────────────────
    st.subheader("📝 Post-Trial Survey Responses")
    if stats["surveys"]:
        survey_rows = []
        for s in stats["surveys"]:
            d = s.get("data", {}) or {}
            responses = d.get("responses", {})
            survey_rows.append({
                "trial": d.get("trial"),
                **{k: responses.get(k) for k in ["trust", "intrusiveness", "relevance", "annoyance", "helpfulness"]},
            })
        if survey_rows:
            sv_df = pd.DataFrame(survey_rows)
            st.dataframe(sv_df, use_container_width=True, hide_index=True)
            for sr in survey_rows:
                chart_label = f"Trial {sr['trial']}"
                vals = {k: v for k, v in sr.items() if k != "trial" and v is not None}
                if vals:
                    st.subheader(f"Survey — {chart_label}")
                    st.bar_chart(vals)
    else:
        st.info("No post-trial surveys in this log.")

    st.divider()

    # ── Raw event log ─────────────────────────────────────────
    st.subheader("🧪 Raw Event Log")
    raw_df = pd.DataFrame(rows)
    st.dataframe(raw_df, use_container_width=True, hide_index=True)

    st.divider()
    st.download_button(
        "⬇️ Download JSONL",
        data=selected_path.read_text(encoding="utf-8"),
        file_name=selected_path.name,
        mime="application/x-ndjson",
    )

else:
    # ── Multi-file aggregation ────────────────────────────────
    selected_labels = st.multiselect(
        "Select log files to aggregate",
        labels,
        default=labels,
    )

    if not selected_labels:
        st.info("Select one or more log files above to see aggregated statistics.")
        st.stop()

    all_rows: List[Dict[str, Any]] = []
    file_stats: Dict[str, Dict] = {}
    for lbl in selected_labels:
        p = file_options[lbl]
        r = load_jsonl(p)
        all_rows.extend(r)
        file_stats[lbl] = compute_single_stats(r)

    # ── Aggregate overview ────────────────────────────────────
    st.subheader("📋 Aggregated Overview")
    total_events = len(all_rows)
    event_counter = Counter(r.get("event", "") for r in all_rows)
    total_clicks = sum(len(fs["ad_clicks"]) for fs in file_stats.values())
    total_exits = sum(len(fs["early_exits"]) for fs in file_stats.values())
    total_trials = sum(len(fs["trial_completions"]) for fs in file_stats.values())
    total_surveys = sum(len(fs["surveys"]) for fs in file_stats.values())
    total_convos = sum(len(fs["convo_summaries"]) for fs in file_stats.values())

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Files Selected", len(selected_labels))
    m2.metric("Total Events", total_events)
    m3.metric("Total Ad Clicks", total_clicks)
    m4.metric("Total Early Exits", total_exits)
    m5.metric("Total Trials Completed", total_trials)

    m6, m7, m8, m9, m10 = st.columns(5)
    m6.metric("User Messages", event_counter.get("user_message", 0))
    m7.metric("Assistant Replies", event_counter.get("assistant_reply", 0))
    m8.metric("Retrievals (Ads)", event_counter.get("retrieval", 0))
    m9.metric("Surveys", total_surveys)
    m10.metric("Conversations", total_convos)

    st.divider()

    # ── Event distribution ────────────────────────────────────
    st.subheader("📊 Event Type Distribution")
    ev_df = pd.DataFrame(
        [{"event": k, "count": v} for k, v in sorted(event_counter.items(), key=lambda x: -x[1])]
    )
    st.dataframe(ev_df, use_container_width=True, hide_index=True)
    st.bar_chart(ev_df.set_index("event")["count"])
    st.caption("Event counts across selected files")

    st.divider()

    # ── Per-file comparison ───────────────────────────────────
    st.subheader("📁 Per-File Comparison")
    comparison_rows = []
    for lbl, fs in file_stats.items():
        ec = fs["event_counts"]
        comparison_rows.append({
            "file": lbl.split("/")[0],
            "events": fs["total_events"],
            "user_msgs": ec.get("user_message", 0),
            "assistant_msgs": ec.get("assistant_reply", 0),
            "ad_clicks": len(fs["ad_clicks"]),
            "early_exits": len(fs["early_exits"]),
            "trials": len(fs["trial_completions"]),
            "surveys": len(fs["surveys"]),
        })
    comp_df = pd.DataFrame(comparison_rows)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

    st.divider()

    # ── Aggregated response times ─────────────────────────────
    st.subheader("⏳ Aggregated Response Times")
    all_reply_times = []
    for r in all_rows:
        if r.get("event") == "user_message":
            ttr = (r.get("data", {}) or {}).get("time_to_reply_ms")
            if ttr is not None:
                all_reply_times.append(ttr / 1000)
    if all_reply_times:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("N responses", len(all_reply_times))
        c2.metric("Mean", f"{sum(all_reply_times)/len(all_reply_times):.1f}s")
        sorted_rt = sorted(all_reply_times)
        c3.metric("Median", f"{sorted_rt[len(sorted_rt)//2]:.1f}s")
        c4.metric("P95", f"{sorted_rt[int(len(sorted_rt)*0.95)]:.1f}s")

        import numpy as np
        hist_vals, hist_edges = np.histogram(all_reply_times, bins=min(20, len(all_reply_times)))
        hist_df = pd.DataFrame({
            "bin_start_s": hist_edges[:-1],
            "count": hist_vals,
        })
        st.bar_chart(hist_df.set_index("bin_start_s")["count"])
        st.caption("Response time distribution (seconds)")
    else:
        st.info("No response time data across selected files.")

    st.divider()

    # ── Aggregated trial durations ────────────────────────────
    st.subheader("⏱️ Aggregated Trial Durations")
    all_trial_durs = []
    for fs in file_stats.values():
        for td in fs["trial_durations"]:
            if td["duration_s"] is not None:
                all_trial_durs.append(td)
    if all_trial_durs:
        dur_df = pd.DataFrame(all_trial_durs)
        st.dataframe(dur_df, use_container_width=True, hide_index=True)
        durations = [d["duration_s"] for d in all_trial_durs]
        c1, c2, c3 = st.columns(3)
        c1.metric("Mean Duration", f"{sum(durations)/len(durations):.1f}s")
        sorted_d = sorted(durations)
        c2.metric("Median Duration", f"{sorted_d[len(sorted_d)//2]:.1f}s")
        c3.metric("Total", f"{sum(durations):.0f}s")

        by_mode = defaultdict(list)
        for d in all_trial_durs:
            by_mode[d.get("ad_mode", "unknown")].append(d["duration_s"])
        mode_means = {k: sum(v)/len(v) for k, v in by_mode.items()}
        st.bar_chart(mode_means)
        st.caption("Mean trial duration by ad_mode (seconds)")
    else:
        st.info("No completed trials with duration data.")

    st.divider()

    # ── Aggregated attention shift ────────────────────────────
    st.subheader("📐 Aggregated Attention Shift")
    all_shifts = [r for r in all_rows if r.get("event") == "attention_shift"]
    if all_shifts:
        shift_vals = [(r.get("data", {}) or {}).get("divergence", 0) for r in all_shifts]
        c1, c2, c3 = st.columns(3)
        c1.metric("N shifts", len(shift_vals))
        c2.metric("Mean divergence", f"{sum(shift_vals)/len(shift_vals):.4f}")
        c3.metric("Max divergence", f"{max(shift_vals):.4f}")

        by_admode = defaultdict(list)
        for r in all_shifts:
            d = (r.get("data", {}) or {}).get("divergence", 0)
            by_admode[r.get("ad_mode", "unknown")].append(d)
        mode_mean_div = {k: sum(v)/len(v) for k, v in by_admode.items()}
        st.bar_chart(mode_mean_div)
        st.caption("Mean attention divergence by ad_mode")
    else:
        st.info("No attention shift data across selected files.")

    st.divider()

    # ── Aggregated survey responses ──────────────────────────
    st.subheader("📝 Aggregated Survey Responses")
    all_surveys = []
    for fs in file_stats.values():
        for s in fs["surveys"]:
            d = s.get("data", {}) or {}
            all_surveys.append(d.get("responses", {}))
    if all_surveys:
        survey_df = pd.DataFrame(all_surveys)
        st.dataframe(survey_df, use_container_width=True, hide_index=True)
        means = {col: survey_df[col].mean() for col in survey_df.columns}
        st.bar_chart(means)
        st.caption("Mean survey scores across all selected files")
    else:
        st.info("No survey data across selected files.")

    st.divider()

    # ── Ad click details ──────────────────────────────────────
    st.subheader("🖱️ Ad Click Details")
    all_clicks = []
    for lbl, fs in file_stats.items():
        for c in fs["ad_clicks"]:
            d = c.get("data", {}) or {}
            all_clicks.append({
                "file": lbl.split("/")[0],
                "timestamp": c.get("timestamp", "")[:19],
                "ad_item_id": d.get("ad_item_id"),
                "ad_title": d.get("ad_title"),
                "interaction": d.get("interaction"),
                "ad_mode": c.get("ad_mode"),
            })
    if all_clicks:
        click_df = pd.DataFrame(all_clicks)
        st.dataframe(click_df, use_container_width=True, hide_index=True)
        clicks_by_mode = Counter(c["ad_mode"] for c in all_clicks)
        st.bar_chart(clicks_by_mode)
        st.caption("Ad clicks by ad_mode")
    else:
        st.info("No ad clicks recorded across selected files.")