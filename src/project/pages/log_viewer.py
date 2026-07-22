import streamlit as st
import json
import glob
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Log Viewer — Flow Replay", layout="wide")

LOG_DIR = Path("/home/wtroi/MasterThesis-RAG-RecSys/src/project/logs/production")
LOG_DIR_DEV = Path("/home/wtroi/MasterThesis-RAG-RecSys/src/project/logs/development")

def discover_sessions(base):
    sessions = []
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        events = list(d.glob("*_events.jsonl"))
        export = list(d.glob("*_export.jsonl"))
        if not events:
            continue
        fp = events[0]
        count = sum(1 for _ in open(fp))
        study, pid = "?", "?"
        with open(fp) as f:
            for line in f:
                ev = json.loads(line)
                if ev.get("event") == "session_started":
                    data = ev.get("data", {})
                    study = data.get("study_type", "?")
                    pid = data.get("participant_id", "?")
                    break
        sessions.append({
            "folder": d.name,
            "path": fp,
            "export": export[0] if export else None,
            "events": count,
            "study": study,
            "pid": pid,
            "mtime": datetime.fromtimestamp(fp.stat().st_mtime),
        })
    sessions.sort(key=lambda s: s["folder"], reverse=True)
    return sessions

def load_events(path):
    rows = []
    with open(path) as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows




def compute_global_stats(log_dir):
    sessions = discover_sessions(log_dir)
    all_ttrs = []
    all_msg_lens = []
    all_totals = []
    all_survey_responses = []
    session_count = 0

    for s in sessions:
        events = load_events(s["path"])
        ttrs = []
        msg_lens = []
        start_ts = None
        end_ts = None
        survey_responses = []

        for ev in events:
            evt = ev.get("event", "")
            data = ev.get("data", {})
            ts = ev.get("timestamp", "")
            if evt == "session_started":
                start_ts = ts
            elif evt in ("session_complete", "experiment_end"):
                end_ts = ts
            elif evt == "user_message":
                t = data.get("time_to_reply_ms")
                if t:
                    ttrs.append(t / 1000.0)
                msg_lens.append(len(data.get("content", "")))
            elif evt == "post_condition_survey_submitted":
                survey_responses.append(data.get("responses", {}))

        all_ttrs.extend(ttrs)
        all_msg_lens.extend(msg_lens)
        if start_ts and end_ts:
            try:
                total = (datetime.fromisoformat(end_ts) - datetime.fromisoformat(start_ts)).total_seconds()
                all_totals.append(total)
            except Exception:
                pass
        all_survey_responses.extend(survey_responses)
        session_count += 1

    return {
        "global_avg_ttr": sum(all_ttrs) / len(all_ttrs) if all_ttrs else 5.0,
        "global_avg_msg_len": sum(all_msg_lens) / len(all_msg_lens) if all_msg_lens else 50,
        "global_avg_total_time": sum(all_totals) / len(all_totals) if all_totals else 900,
        "n_sessions": session_count,
        "all_survey_responses": all_survey_responses,
    }


def compute_session_metrics(events):
    ttrs = []
    msg_lens = []
    start_ts = None
    end_ts = None
    cond_times = {}
    cond_start = {}
    cond_ad_modes = {}
    survey_responses = []
    condition_order = []

    for ev in events:
        evt = ev.get("event", "")
        data = ev.get("data", {})
        ts = ev.get("timestamp", "")
        if evt == "session_started":
            start_ts = ts
        elif evt in ("session_complete", "experiment_end"):
            end_ts = ts
        elif evt == "user_message":
            t = data.get("time_to_reply_ms")
            if t:
                ttrs.append(t / 1000.0)
            msg_lens.append(len(data.get("content", "")))
        elif evt in ("condition_start", "condition_started"):
            cid = data.get("condition", "")
            am = data.get("ad_mode", "")
            cond_start[cid] = ts
            cond_ad_modes[cid] = am
            condition_order.append(cid)
        elif evt in ("condition_end", "condition_complete"):
            cid = data.get("condition", "")
            if cid in cond_start and cond_start[cid] and ts:
                try:
                    dur = (datetime.fromisoformat(ts) - datetime.fromisoformat(cond_start[cid])).total_seconds()
                    cond_times[cid] = dur
                except Exception:
                    pass
        elif evt == "post_condition_survey_submitted":
            survey_responses.append({"condition": ev.get("ad_mode", ""), "responses": data.get("responses", {})})

    total_time = None
    if start_ts and end_ts:
        try:
            total_time = (datetime.fromisoformat(end_ts) - datetime.fromisoformat(start_ts)).total_seconds()
        except Exception:
            pass

    return {
        "avg_ttr": sum(ttrs) / len(ttrs) if ttrs else 0,
        "avg_msg_len": sum(msg_lens) / len(msg_lens) if msg_lens else 0,
        "total_time_sec": total_time or 0,
        "user_msg_count": len(ttrs),
        "condition_times": cond_times,
        "condition_ad_modes": cond_ad_modes,
        "condition_order": condition_order,
        "survey_responses": survey_responses,
    }


def compute_discriminative_signals(session, global_stats):
    signals = []

    if session["avg_ttr"] > 0 and global_stats["global_avg_ttr"] > 0:
        ratio = session["avg_ttr"] / global_stats["global_avg_ttr"]
        ttr_str = f"{session['avg_ttr']:.1f}s vs global {global_stats['global_avg_ttr']:.1f}s"
        if ratio < 0.3:
            signals.append({"name": "Avg Time-to-Reply", "severity": "bad",
                           "detail": ttr_str + " | suspiciously fast, likely speedrunning"})
        elif ratio < 0.7:
            signals.append({"name": "Avg Time-to-Reply", "severity": "warn",
                           "detail": ttr_str + " | faster than average"})
        elif ratio > 2.0:
            signals.append({"name": "Avg Time-to-Reply", "severity": "warn",
                           "detail": ttr_str + " | very slow, possible distraction"})
        else:
            signals.append({"name": "Avg Time-to-Reply", "severity": "good",
                           "detail": ttr_str + " | within normal range"})

    if session["avg_msg_len"] > 0 and global_stats["global_avg_msg_len"] > 0:
        ratio = session["avg_msg_len"] / global_stats["global_avg_msg_len"]
        if ratio < 0.3:
            signals.append({"name": "Avg Message Length", "severity": "bad",
                           "detail": f"{session['avg_msg_len']:.0f} chars vs global {global_stats['global_avg_msg_len']:.0f} | very short replies, not engaging"})
        elif ratio < 0.7:
            signals.append({"name": "Avg Message Length", "severity": "warn",
                           "detail": f"{session['avg_msg_len']:.0f} chars vs global {global_stats['global_avg_msg_len']:.0f} | shorter than average"})
        elif ratio > 2.0:
            signals.append({"name": "Avg Message Length", "severity": "warn",
                           "detail": f"{session['avg_msg_len']:.0f} chars vs global {global_stats['global_avg_msg_len']:.0f} | very verbose"})
        else:
            signals.append({"name": "Avg Message Length", "severity": "good",
                           "detail": f"{session['avg_msg_len']:.0f} chars vs global {global_stats['global_avg_msg_len']:.0f} | normal range"})

    if session["total_time_sec"] > 0 and global_stats["global_avg_total_time"] > 0:
        ratio = session["total_time_sec"] / global_stats["global_avg_total_time"]
        if ratio < 0.3:
            signals.append({"name": "Total Experiment Time", "severity": "bad",
                           "detail": f"{session['total_time_sec']/60:.1f}min vs global {global_stats['global_avg_total_time']/60:.1f}min | extremely short, likely speedrun"})
        elif ratio < 0.7:
            signals.append({"name": "Total Experiment Time", "severity": "warn",
                           "detail": f"{session['total_time_sec']/60:.1f}min vs global {global_stats['global_avg_total_time']/60:.1f}min | shorter than average"})
        elif ratio > 2.0:
            signals.append({"name": "Total Experiment Time", "severity": "warn",
                           "detail": f"{session['total_time_sec']/60:.1f}min vs global {global_stats['global_avg_total_time']/60:.1f}min | very long session"})
        else:
            signals.append({"name": "Total Experiment Time", "severity": "good",
                           "detail": f"{session['total_time_sec']/60:.1f}min vs global {global_stats['global_avg_total_time']/60:.1f}min | normal range"})

    cond_times = session["condition_times"]
    if len(cond_times) >= 2:
        times = list(cond_times.values())
        if max(times) > 0 and min(times) > 0:
            ratio = max(times) / min(times)
            if ratio < 1.1:
                signals.append({"name": "Condition Duration Variance", "severity": "bad",
                               "detail": f"All conditions nearly identical ({min(times)/60:.1f}-{max(times)/60:.1f}min) | suspicious, no variation"})
            elif ratio < 1.5:
                signals.append({"name": "Condition Duration Variance", "severity": "warn",
                               "detail": f"Low variation across conditions ({min(times)/60:.1f}-{max(times)/60:.1f}min)"})
            else:
                signals.append({"name": "Condition Duration Variance", "severity": "good",
                               "detail": f"Healthy variation: {', '.join(f'{c}: {t/60:.1f}min' for c, t in cond_times.items())}"})

    responses = session["survey_responses"]
    if responses:
        all_ratings = []
        for r in responses:
            for k, v in r["responses"].items():
                try:
                    all_ratings.append(int(v))
                except (ValueError, TypeError):
                    pass
        if all_ratings:
            distinct = len(set(all_ratings))
            if distinct == 1:
                signals.append({"name": "Survey Response Consistency", "severity": "bad",
                               "detail": f"All survey responses identical ({all_ratings[0]}/7) | straightlining, likely inattentive"})
            elif distinct <= 2:
                signals.append({"name": "Survey Response Consistency", "severity": "warn",
                               "detail": f"Very low variance | only {distinct} distinct values used across all surveys"})
            else:
                signals.append({"name": "Survey Response Consistency", "severity": "good",
                               "detail": f"Healthy variance | {distinct} distinct values used across surveys"})

    if len(responses) >= 2:
        ad_scores = {}
        for r in responses:
            cond_name = r.get("condition", "")
            ratings = []
            for k, v in r["responses"].items():
                try:
                    ratings.append(int(v))
                except (ValueError, TypeError):
                    pass
            if ratings:
                ad_scores[cond_name] = sum(ratings) / len(ratings)
        no_ads_avg = None
        ads_avg = None
        for cond, avg in ad_scores.items():
            cl = cond.lower()
            if "no_ads" in cl or "noads" in cl or "no-" in cl:
                no_ads_avg = avg
            elif "ads" in cl or "with_ads" in cl or "with-" in cl:
                ads_avg = avg
        if no_ads_avg is not None and ads_avg is not None:
            if no_ads_avg > ads_avg:
                signals.append({"name": "Ad-Ratings Consistency", "severity": "bad",
                               "detail": f"No-Ads rated HIGHER ({no_ads_avg:.1f}/7) than Ads ({ads_avg:.1f}/7) | data quality concern"})
            elif no_ads_avg < ads_avg:
                signals.append({"name": "Ad-Ratings Consistency", "severity": "good",
                               "detail": f"Ads rated higher ({ads_avg:.1f}/7) than No-Ads ({no_ads_avg:.1f}/7) | expected pattern"})
            else:
                signals.append({"name": "Ad-Ratings Consistency", "severity": "warn",
                               "detail": f"Both conditions rated identically ({no_ads_avg:.1f}/7) | unusual"})

    return signals


def render_signals_dashboard(signals):
    severity_color = {"bad": "#ff1744", "warn": "#ffab00", "good": "#00e676"}

    bad_count = sum(1 for s in signals if s["severity"] == "bad")
    warn_count = sum(1 for s in signals if s["severity"] == "warn")

    if bad_count > 0:
        overall = "bad"
        overall_label = f"\U000026a0 {bad_count} Critical Issue{'s' if bad_count > 1 else ''} Detected"
    elif warn_count > 2:
        overall = "warn"
        overall_label = f"\U000026a1 {warn_count} Warning Signs"
    else:
        overall = "good"
        overall_label = "\u2705 All Signals Normal"

    oc = severity_color[overall]

    st.markdown(f"""
    <div style="border:3px solid {oc}; border-radius:16px; padding:0; margin:0 0 20px 0; background:#1a1a1a;">
        <div style="background:{oc}; color:#000; padding:14px 24px; border-radius:13px 13px 0 0; font-size:22px; font-weight:800; text-align:center;">
            {overall_label}
        </div>
        <div style="padding:12px 16px;">
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for i, sig in enumerate(signals):
        c = severity_color[sig["severity"]]
        icon = {"bad": "\U0001f534", "warn": "\U0001f7e1", "good": "\U0001f7e2"}[sig["severity"]]
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#252525; border-left:5px solid {c}; border-radius:8px; padding:12px 14px; margin:6px 0;">
                <div style="color:{c}; font-weight:700; font-size:15px;">{icon} {sig['name']}</div>
                <div style="color:#ccc; font-size:13px; margin-top:4px;">{sig['detail']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

def render_timeline(events, export_rows):
    turns_data = {}
    conditions = []
    current_trial = 0
    condition_order = []
    ad_mode_order = []

    for ev in events:
        evt = ev.get("event", "")
        data = ev.get("data", {})
        turn = ev.get("turn", 0)
        trial = ev.get("trial_index", 0)
        ad_mode = ev.get("ad_mode", "")
        ts = ev.get("timestamp", "")
        source = ev.get("source", "")

        if evt == "condition_start" or evt == "condition_started":
            cid = data.get("condition", "")
            am = data.get("ad_mode", "")
            task = data.get("task_title", data.get("task_id", ""))
            condition_order.append((cid, am, task, trial))
            ad_mode_order.append(am)

        if evt == "user_message":
            content = data.get("content", "")
            t = data.get("time_to_reply_ms")
            key = (trial, turn)
            if key not in turns_data:
                turns_data[key] = {"user": "", "assistant": "", "trial": trial, "turn": turn}
            turns_data[key]["user"] = content
            turns_data[key]["user_ts"] = ts
            if t:
                turns_data[key]["time_to_reply"] = t / 1000.0

        if evt == "assistant_reply":
            content = data.get("content", "")
            key = (trial, turn)
            if key not in turns_data:
                turns_data[key] = {"user": "", "assistant": "", "trial": trial, "turn": turn}
            turns_data[key]["assistant"] = content
            turns_data[key]["assistant_ts"] = ts

        if evt == "condition_start" or evt == "condition_started":
            current_trial = trial
        if evt == "condition_end" or evt == "condition_complete":
            conditions.append({
                "event": evt,
                "data": data,
                "trial": trial,
                "ad_mode": ad_mode,
                "ts": ts,
            })

    ad_modes_used = sorted(set(am for am in ad_mode_order if am and am != "session"))

    st.markdown("""
    <style>
    .tl-container { max-width: 1000px; margin: 0 auto; }
    .tl-arrow { text-align: center; color: #aaa; font-size: 28px; margin: -4px 0; }
    .tl-card { background: #1e1e1e; border: 1px solid #333; border-radius: 12px; padding: 20px; margin: 8px 0; }
    .tl-card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
    .tl-card-icon { font-size: 24px; width: 36px; text-align: center; }
    .tl-card-title { font-size: 16px; font-weight: 600; color: #e0e0e0; }
    .tl-card-subtitle { font-size: 12px; color: #888; }
    .user-bubble { background: #2b5278; border-radius: 18px 18px 4px 18px; padding: 12px 18px; margin: 8px 0 8px 40px; max-width: 85%; color: #e0e0e0; }
    .assistant-bubble { background: #333; border-radius: 18px 18px 18px 4px; padding: 12px 18px; margin: 8px 40px 8px 0; max-width: 85%; color: #ccc; }
    .bubble-label { font-size: 11px; color: #888; margin-bottom: 4px; }
    .ad-banner { background: #3a2a1a; border: 1px solid #665533; border-radius: 8px; padding: 12px 16px; margin: 8px 0; }
    .ad-title { color: #ffcc66; font-weight: 600; font-size: 14px; }
    .ad-text { color: #ccc; font-size: 13px; margin-top: 4px; }
    .survey-item { background: #252525; border-left: 3px solid #4a9eff; padding: 8px 12px; margin: 6px 0; border-radius: 4px; }
    .survey-q { color: #aaa; font-size: 12px; margin-bottom: 2px; }
    .survey-a { color: #e0e0e0; font-size: 14px; }
    .info-box { background: #1a2a3a; border-left: 3px solid #4a9eff; padding: 10px 16px; margin: 8px 0; border-radius: 4px; font-size: 13px; color: #bbb; }
    .condition-label { background: #2a1a3a; border-left: 3px solid #a04aff; padding: 8px 12px; margin: 4px 0; border-radius: 4px; }
    .condition-label-text { color: #cc99ff; font-weight: 600; font-size: 14px; }
    .chat-container { margin: 8px 0; }
    .section-divider { border: none; border-top: 1px solid #333; margin: 16px 0; }
    .marker-tag { display: inline-block; background: #4a4a2a; color: #dddd88; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin: 2px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="tl-container">', unsafe_allow_html=True)

    # Pre-process: build ordered list of timeline items
    timeline_items = []
    session_idx = 0
    last_event = None

    for ev in events:
        evt = ev.get("event", "")
        data = ev.get("data", {})
        turn = ev.get("turn", 0)
        trial = ev.get("trial_index", 0)
        ad_mode = ev.get("ad_mode", "")
        ts = ev.get("timestamp", "")
        source = ev.get("source", "")

        if evt == "session_started":
            study = data.get("study_type", "?")
            pid = data.get("participant_id", "?")
            conditions_list = data.get("conditions", [])
            cond_str = ", ".join([c.get("condition", "") + "(" + c.get("ad_mode", "") + ")" for c in conditions_list])
            timeline_items.append(("session_started", {
                "study": study, "pid": pid, "conditions": cond_str, "ts": ts
            }))

        elif evt == "experiment_config":
            llm = data.get("llm", {})
            ret = data.get("retrieval", {})
            ver = data.get("version", "?")
            timeline_items.append(("experiment_config", {
                "model": llm.get("model", "?"), "temp": llm.get("temperature", "?"),
                "embed": ret.get("embedding_model", "?"), "rerank": ret.get("reranker_model", "?"),
                "ver": ver,
            }))

        elif evt == "consent_granted":
            timeline_items.append(("consent", {"ts": ts}))

        elif evt == "screen_skipped":
            screen = data.get("screen", "")
            timeline_items.append(("screen_skipped", {"screen": screen, "ts": ts}))

        elif evt in ("demographics_post_submitted",):
            timeline_items.append(("demographics", {"data": data, "ts": ts}))

        elif evt in ("ocean_submitted",):
            scores = data.get("scores", {})
            timeline_items.append(("ocean", {"scores": scores, "ts": ts}))

        elif evt in ("baseline_start", "baseline_end"):
            timeline_items.append((evt, {"ts": ts}))

        elif evt in ("warmup_start", "warmup_finish"):
            timeline_items.append((evt, {"ts": ts}))

        elif evt == "conversation_started":
            intent = data.get("initial_intent", "")
            task_id = data.get("task_id", "")
            timeline_items.append(("conversation_started", {
                "intent": intent, "task_id": task_id, "trial": trial, "ts": ts
            }))

        elif evt == "user_message":
            content = data.get("content", "")
            ttr = data.get("time_to_reply_ms")
            timeline_items.append(("user_message", {
                "content": content, "turn": turn, "trial": trial,
                "ttr": ttr / 1000.0 if ttr else None, "ts": ts
            }))

        elif evt == "assistant_reply":
            content = data.get("content", "")
            timeline_items.append(("assistant_reply", {
                "content": content, "turn": turn, "trial": trial, "ts": ts
            }))

        elif evt == "condition_start" or evt == "condition_started":
            cid = data.get("condition", "")
            am = data.get("ad_mode", "")
            task = data.get("task_title", data.get("task_id", ""))
            timeline_items.append(("condition_start", {
                "condition": cid, "ad_mode": am, "task": task,
                "trial": trial, "ts": ts, "data": data
            }))

        elif evt in ("ad_injected", "ad_inserted", "ad_displayed"):
            if evt == "ad_injected":
                ad_title = data.get("ad_title", "")
                ad_text = data.get("ad_text", "")
                ad_id = data.get("ad_id", "")
                timeline_items.append(("ad_injected", {
                    "title": ad_title, "text": ad_text, "id": ad_id,
                    "turn": turn, "trial": trial, "ts": ts
                }))

        elif evt == "retrieval":
            query = data.get("query", "")
            ad_title = data.get("ad_title", "")
            timeline_items.append(("retrieval", {
                "query": query, "ad_title": ad_title, "turn": turn, "trial": trial, "ts": ts
            }))

        elif evt == "intent_classified":
            label = data.get("intent_label", "")
            timeline_items.append(("intent_classified", {
                "label": label, "turn": turn, "trial": trial, "ts": ts
            }))

        elif evt in ("turn_1_write", "turn_2_write", "turn_3_write", "turn_4_write"):
            tnum = int(evt.split("_")[1])
            timeline_items.append(("turn_write", {"turn": tnum, "trial": trial, "ts": ts}))

        elif evt in ("turn_1_read", "turn_2_read", "turn_3_read", "turn_4_read"):
            tnum = int(evt.split("_")[1])
            timeline_items.append(("turn_read", {"turn": tnum, "trial": trial, "ts": ts}))

        elif evt == "conversation_completed":
            timeline_items.append(("conversation_completed", {
                "data": data, "trial": trial, "ts": ts
            }))

        elif evt == "condition_conclusion_submitted":
            conclusion = data.get("conclusion", "")
            timeline_items.append(("conclusion", {"text": conclusion, "trial": trial, "ts": ts}))

        elif evt == "post_condition_survey_submitted":
            responses = data.get("responses", {})
            timeline_items.append(("post_condition_survey", {
                "responses": responses, "trial": trial, "ts": ts
            }))

        elif evt == "condition_end" or evt == "condition_complete":
            timeline_items.append(("condition_end", {
                "data": data, "trial": trial, "ts": ts
            }))

        elif evt == "trial_end":
            timeline_items.append(("trial_end", {"data": data, "trial": trial, "ts": ts}))

        elif evt == "ads_recall_submitted":
            recall = data.get("block_late_recall_reaction", "")
            timeline_items.append(("ads_recall", {"text": recall, "ts": ts}))

        elif evt == "deception_disclosure_submitted":
            withdrew = data.get("withdrew", False)
            timeline_items.append(("deception_disclosure", {"withdrew": withdrew, "ts": ts}))

        elif evt in ("session_complete", "experiment_end"):
            timeline_items.append(("session_end", {"event": evt, "data": data, "ts": ts}))

        elif evt == "marker_sent":
            timeline_items.append(("marker_sent", {"ts": ts, "trial": trial, "turn": turn}))

        elif evt == "user_starts_typing":
            pass  # skip for visual flow

    # Render timeline
    timeline_items.sort(key=lambda x: x[1].get("ts", ""))

    def arrow():
        st.markdown('<div class="tl-arrow">▼</div>', unsafe_allow_html=True)

    def card(icon, title, subtitle, content_html, extra_class=""):
        st.markdown(f'''
        <div class="tl-card {extra_class}">
            <div class="tl-card-header">
                <div class="tl-card-icon">{icon}</div>
                <div>
                    <div class="tl-card-title">{title}</div>
                    <div class="tl-card-subtitle">{subtitle}</div>
                </div>
            </div>
            {content_html}
        </div>
        ''', unsafe_allow_html=True)

    for i, (evt, info) in enumerate(timeline_items):
        if evt == "session_started":
            card("🚀", "Session Started", info.get("ts", ""),
                 f'<div class="info-box">Study: <b>{info["study"]}</b> | '
                 f'Participant: <b>{info["pid"]}</b><br>'
                 f'Conditions: {info["conditions"]}</div>')

        elif evt == "experiment_config":
            card("⚙️", "Experiment Config", info.get("ts", ""),
                 f'<div class="info-box">Model: <b>{info["model"]}</b> (temp={info["temp"]})<br>'
                 f'Embedding: <b>{info["embed"]}</b><br>'
                 f'Reranker: <b>{info["rerank"]}</b><br>'
                 f'Version: {info["ver"]}</div>')

        elif evt == "consent":
            card("📝", "Consent Granted", info.get("ts", ""), "")

        elif evt == "screen_skipped":
            card("⏭️", f'Screen Skipped: {info["screen"]}', info.get("ts", ""), "")

        elif evt == "demographics":
            items = "".join(f'<div class="survey-item"><div class="survey-q">{k.replace("demo_","").replace("_"," ").title()}</div>'
                           f'<div class="survey-a">{v}</div></div>'
                           for k, v in info["data"].items() if v)
            card("👤", "Demographics Survey", info.get("ts", ""), items)

        elif evt == "ocean":
            scores = info["scores"]
            score_line = " | ".join([f"<b>{k}</b>: {v}" for k, v in scores.items()])
            card("🧠", "OCEAN Personality", info.get("ts", ""),
                 f'<div class="info-box">{score_line}</div>')

        elif evt == "baseline_start":
            card("📊", "EEG Baseline Recording Started", info.get("ts", ""),
                 '<div class="info-box">Recording resting-state EEG baseline...</div>')

        elif evt == "baseline_end":
            card("✅", "EEG Baseline Recording Ended", info.get("ts", ""), "")

        elif evt == "warmup_start":
            card("🔥", "Warmup Chat Started", info.get("ts", ""),
                 '<div class="info-box">Participant can chat freely to get comfortable with the system.</div>')

        elif evt == "warmup_finish":
            card("✅", "Warmup Finished", info.get("ts", ""), "")

        elif evt == "conversation_started":
            card("💬", f"Conversation Started (Trial {info['trial']})", info.get("ts", ""),
                 f'<div class="info-box">Intent: <b>{info["intent"]}</b> | Task: <b>{info["task_id"]}</b></div>')

        elif evt == "condition_start":
            cond = info["condition"]
            am = info["ad_mode"]
            task = info["task"]
            card("🎯", f"Condition: {cond} ({am})", info.get("ts", ""),
                 f'<div class="info-box">Task: <b>{task}</b><br>Ad Mode: <b>{am}</b><br>Trial: {info["trial"]}</div>')

        elif evt == "user_message":
            arrow()
            content = info["content"]
            ttr = info.get("ttr")
            ttr_str = f" ({ttr:.1f}s)" if ttr else ""
            st.markdown(
                f'<div class="user-bubble">'
                f'<div class="bubble-label">User (Turn {info["turn"]}){ttr_str}</div>'
                f'{content}</div>',
                unsafe_allow_html=True)

        elif evt == "assistant_reply":
            content = info["content"]
            if len(content) > 500:
                content = content[:500] + "..."
            st.markdown(
                f'<div class="assistant-bubble">'
                f'<div class="bubble-label">Assistant (Turn {info["turn"]})</div>'
                f'{content}</div>',
                unsafe_allow_html=True)

        elif evt == "ad_injected":
            card("📢", f"Ad Injected (Turn {info['turn']})", info.get("ts", ""),
                 f'<div class="ad-banner"><div class="ad-title">{info["title"]}</div>'
                 f'<div class="ad-text">{info["text"][:200]}</div></div>')

        elif evt == "retrieval":
            card("🔍", f"Retrieval (Turn {info['turn']})", info.get("ts", ""),
                 f'<div class="info-box">Query: <b>{info["query"][:150]}</b><br>'
                 f'Ad Retrieved: {info["ad_title"][:100]}</div>')

        elif evt == "intent_classified":
            card("🏷️", f"Intent: {info['label']}", info.get("ts", ""), "")

        elif evt == "turn_write":
            pass  # implicit from user_message

        elif evt == "turn_read":
            pass  # implicit from assistant_reply

        elif evt == "conversation_completed":
            card("✅", f"Conversation Completed (Trial {info['trial']})", info.get("ts", ""),
                 "")

        elif evt == "conclusion":
            card("✍️", f"Condition Conclusion (Trial {info['trial']})", info.get("ts", ""),
                 f'<div class="info-box">{info["text"][:500]}</div>')

        elif evt == "post_condition_survey":
            responses = info["responses"]
            items = "".join(
                f'<div class="survey-item"><div class="survey-q">{k}</div>'
                f'<div class="survey-a"><b>{v}</b>/7</div></div>'
                for k, v in responses.items()
            )
            card("📋", f"Post-Condition Survey (Trial {info['trial']})", info.get("ts", ""), items)

        elif evt == "condition_end":
            card("🏁", f"Condition End (Trial {info['trial']})", info.get("ts", ""), "")

        elif evt == "trial_end":
            d = info["data"]
            stats = d.get("avg_time_to_reply_ms", 0)
            n_turns = d.get("n_turns", 0)
            cont_rate = d.get("continuation_rate_overall", 0)
            card("📊", f"Trial {info['trial']} Summary", info.get("ts", ""),
                 f'<div class="info-box">Turns: <b>{n_turns}</b> | '
                 f'Avg reply: <b>{stats/1000:.1f}s</b> | '
                 f'Continuation: <b>{cont_rate*100:.0f}%</b></div>')

        elif evt == "ads_recall":
            card("🛒", "Ad Recall Survey", info.get("ts", ""),
                 f'<div class="info-box">{info["text"][:300]}</div>')

        elif evt == "deception_disclosure":
            status = "❌ Withdrew" if info["withdrew"] else "✅ Stayed"
            card("🔓", f"Deception Disclosure — {status}", info.get("ts", ""), "")

        elif evt == "session_end":
            card("🏆", "Session Complete!" if info["event"] == "session_complete" else "Experiment End",
                 info.get("ts", ""), "")

        elif evt == "marker_sent":
            st.markdown(f'<span class="marker-tag">🔴 LSL Marker (Trial {info["trial"]}, Turn {info["turn"]})</span>',
                        unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


st.title("🔍 Session Log Viewer — Flow Replay")
st.caption("Browse production/development sessions and replay the participant's journey step by step.")

tab_prod, tab_dev = st.tabs(["📀 Production", "🔧 Development"])

for tab, base_dir, label in [(tab_prod, LOG_DIR, "Production"), (tab_dev, LOG_DIR_DEV, "Development")]:
    with tab:
        sessions = discover_sessions(base_dir)
        if not sessions:
            st.info(f"No sessions found in {label}.")
            continue

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            session_options = {
                    f"{s['folder']} ({s['events']} evts, {s['study']}, {s['pid']})": s
                    for s in sessions
                }
            selected_label = st.selectbox(
                    f"Select {label} session:",
                    options=list(session_options.keys()),
                    key=f"sel_{label}",
                )
            session = session_options[selected_label]

        with col2:
            st.metric("Events", session["events"])
        with col3:
            st.metric("Type", session["study"])

        if st.button(f"🔍 Load {label} Session", key=f"load_{label}", use_container_width=True):
            with st.spinner("Loading events..."):
                events = load_events(session["path"])
                export_rows = []
                if session["export"]:
                    with open(session["export"]) as f:
                        for line in f:
                            try:
                                export_rows.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass
                st.session_state["events"] = events
                st.session_state["export_rows"] = export_rows
                st.session_state["session_loaded"] = session["folder"]
                st.rerun()

if "events" in st.session_state and st.session_state["events"]:
    st.divider()
    st.subheader(f"📋 Session: {st.session_state.get('session_loaded', '')}")

    with st.spinner("Computing quality signals..."):
        if "global_stats" not in st.session_state:
            st.session_state["global_stats"] = compute_global_stats(LOG_DIR)
        session_metrics = compute_session_metrics(st.session_state["events"])
        signals = compute_discriminative_signals(session_metrics, st.session_state["global_stats"])
        render_signals_dashboard(signals)
        with st.expander("Session Metrics Details"):
            gs = st.session_state["global_stats"]
            st.markdown(f"**Global stats** (based on {gs['n_sessions']} sessions): "
                        f"avg TTR={gs['global_avg_ttr']:.1f}s, "
                        f"avg msg len={gs['global_avg_msg_len']:.0f} chars, "
                        f"avg total time={gs['global_avg_total_time']/60:.1f}min")
            st.json(session_metrics)

    render_timeline(st.session_state["events"], st.session_state.get("export_rows", []))
