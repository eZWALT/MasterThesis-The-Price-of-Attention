"""
Streamlit entrypoint.

Routing only — all logic lives in core/ui/.

Modes (via ?dev= query param):
  (none)   → participant experiment flow  [production]
  flow     → participant flow + skip buttons  [dev testing]
  true/1   → free-form dev chat with full controls  [dev]
"""

import streamlit as st

from core.config import APP_TITLE, PAGE_TITLE, DEV_QUERY_PARAM
from core.ui.participant import init_session_state, run_participant_mode
from core.ui.dev import run_dev_mode


def _dev_param() -> str:
    return st.query_params.get(DEV_QUERY_PARAM, "").lower()


def is_dev_mode() -> bool:
    return _dev_param() in ("true", "1", "yes")


def is_flow_test() -> bool:
    return _dev_param() == "flow"


def main():
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")
    init_session_state()

    # Hide multi-page nav for participants — devs see full nav
    if not is_dev_mode() and not is_flow_test():
        st.markdown(
            "<style>[data-testid='stSidebarNav'] {display: none;}</style>",
            unsafe_allow_html=True,
        )

    if is_dev_mode() or is_flow_test():
        st.title(APP_TITLE)

    if is_dev_mode():
        run_dev_mode()
    else:
        run_participant_mode(flow_test=is_flow_test())


if __name__ == "__main__":
    main()
