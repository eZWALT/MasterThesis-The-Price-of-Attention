"""Reusable UI components."""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


def render_countdown(seconds: int = 90, label: str = "", key: str = "countdown") -> None:
    """
    Render a client-side countdown timer via embedded JS.

    Parameters
    ----------
    seconds : int
        Total countdown in seconds.
    label : str
        Optional label shown above the timer.
    key : str
        Unique key for the component (required by st.components.v1.html).
    """
    m = seconds // 60
    s = seconds % 60
    initial = f"{m}:{s:02d}"

    html = f"""
    <div id="cd-{key}" style="
        font-size: 1.4rem;
        font-weight: 600;
        font-variant-numeric: tabular-nums;
        color: #111;
    ">{initial}</div>
    <script>
    (function() {{
        var el = document.getElementById('cd-{key}');
        var total = {seconds};

        function tick() {{
            if (total <= 0) {{
                el.textContent = 'Time\'s up';
                el.style.color = '#999';
                el.style.fontSize = '1rem';
                return;
            }}
            total--;
            var m = Math.floor(total / 60);
            var s = total % 60;
            el.textContent = m + ':' + (s < 10 ? '0' : '') + s;
            setTimeout(tick, 1000);
        }}
        tick();
    }})();
    </script>
    """

    if label:
        st.sidebar.markdown(f"**{label}**")
    components.html(html, height=40)
