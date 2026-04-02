"""
TARA — Experiment Dashboard page.

Provides an overview of logged experiment data, attention shift
metrics, and export options. This is a secondary page accessible
via Streamlit's built-in multi-page navigation.
"""

import streamlit as st

st.set_page_config(page_title="TARA · Dashboard", layout="wide")
st.title("📊 Experiment Dashboard")

# ── Guard: session must exist ─────────────────────────────────

if "logger" not in st.session_state:
    st.warning("No experiment data yet. Start chatting on the main page first.")
    st.stop()

logger = st.session_state.logger

# ── Summary metrics ───────────────────────────────────────────

entries = logger.entries
total = len(entries)
user_msgs = sum(1 for e in entries if e.event == "user_message")
assistant_msgs = sum(1 for e in entries if e.event == "assistant_reply")
ads_injected = sum(1 for e in entries if e.event == "ad_injected")
shifts = [e for e in entries if e.event == "attention_shift"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Events", total)
col2.metric("User Messages", user_msgs)
col3.metric("Assistant Replies", assistant_msgs)
col4.metric("Ads Injected", ads_injected)

st.divider()

# ── Attention Shift over time ─────────────────────────────────

st.subheader("📐 Attention Shift over Turns")

if shifts:
    shift_data = [
        {"turn": i + 1, "divergence": s.data["divergence"], "method": s.data["method"]}
        for i, s in enumerate(shifts)
    ]
    st.line_chart(
        data={d["turn"]: d["divergence"] for d in shift_data},
    )
    st.caption("Δ_attn per conversational turn (higher = more semantic drift from ad exposure)")
else:
    st.info("No attention shift data yet. Chat with ads enabled to generate data.")

st.divider()

# ── Raw log table ─────────────────────────────────────────────

st.subheader("🧪 Raw Event Log")
st.dataframe(logger.to_dicts(), use_container_width=True)

# ── Export ────────────────────────────────────────────────────

st.divider()
col_a, col_b = st.columns(2)
with col_a:
    if st.button("💾 Export JSON"):
        path = logger.export_json()
        st.success(f"Saved to `{path}`")
with col_b:
    st.download_button(
        "⬇️ Download JSON",
        data=logger.to_json(),
        file_name="tara_experiment_log.json",
        mime="application/json",
    )
