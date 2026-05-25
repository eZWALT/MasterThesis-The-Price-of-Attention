"""
Streamlit entrypoint — routing only.

All experiment configuration is driven by URL query parameters.
See core/experiment/query_params.py for the full parameter reference.

Quick reference:
  /                                          production participant session
  ?dev=true                                  developer free-chat mode
  ?dev=flow                                  participant flow + skip buttons
  ?dev=flow&skip=consent,baseline            skip boring screens in testing
  ?n=1&modes=5_implicit&skip=consent,baseline,demographics,ocean  single-trial debug
  ?pid=p01&tasks=trans_plan_trip&modes=2_in_chat&store=file       specific assignment
"""

import streamlit as st

from core.config import APP_TITLE, PAGE_TITLE, PAGE_ICON, DEFAULT_MODEL
from core.conversation.llm_client import LLMClient
from core.experiment.query_params import parse_query_params
from core.ui.participant import init_session_state, run_participant_mode
from core.ui.dev import run_dev_mode


@st.cache_resource
def _warmup_llm() -> None:
    """Run once per Streamlit process to pre-load the model into GPU memory."""
    LLMClient().warmup(DEFAULT_MODEL)


@st.cache_resource
def _warmup_retrieval() -> None:
    """Pre-load embedding + reranker models and FAISS index at startup.

    Without this, the first ad injection causes a 2-3 min hang while
    HuggingFace downloads model shards and builds the FAISS index.
    After this call the pipeline singleton is populated and all subsequent
    retrieve_ad() calls are instantaneous.

    Always runs regardless of AD_BACKEND — the dev UI can switch to RAG
    at any time, and participants should never experience loading delays.
    """
    from core.retrieval import retrieve_ad
    from core.log import logger
    logger.info("Warming up retrieval pipeline (eager load)...")
    retrieve_ad("warmup", [])
    logger.info("Retrieval pipeline warm — ready to serve.")


def main():
    params = parse_query_params()

    from core.retrieval.runtime import configure_from_experiment_params

    configure_from_experiment_params(params)

    _warmup_llm()
    _warmup_retrieval()

    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
    init_session_state(params)

    # Hide multi-page nav for participants — devs get full nav
    if not params.dev_mode and not params.flow_test:
        st.markdown(
            "<style>[data-testid='stSidebarNav'] {display: none;}</style>",
            unsafe_allow_html=True,
        )

    if params.dev_mode or params.flow_test:
        st.title(APP_TITLE)

    if params.dev_mode:
        run_dev_mode()
    else:
        run_participant_mode(params)


if __name__ == "__main__":
    main()
