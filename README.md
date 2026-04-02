
# Master Thesis: Retrieval-Augmented Generation for Recommender Systems

This repository contains all the work for my master thesis in collaboration with Telefonica Research, focused on conversational recommender RAG systems for e-commerce and benchmarking advertising strategies.


You can access my [Master Thesis](https://www.overleaf.com/read/jmpfyvkdxcnt#deeda3), my [Presentation](https://www.overleaf.com/read/tvwscngdpyfp#e86fdc) and my [Final Paper](https://www.overleaf.com/read/tcggxdnhjgmm#739137) and the intial [idea draft](https://www.overleaf.com/read/bddrrckbkvhc#a1c122) on Overleaf.

The following [huggingface collection](https://huggingface.co/collections/eZWALT/tfm) keeps track of the open source datasets and models used throughout this work.

---

## Table of Contents
1. [Introduction](#introduction)
2. [Repository Structure](#repository-structure)
3. [Usage](#usage)
4. [Contributing](#contributing)
5. [License](#license)

---

## Introduction

GOAL: Get a multimodal multiobjective RAG system for recommendation (Possibly using Knowledge Graphs / Agentic techniques / RecSys concepts).

WIP 

## Repository Structure
```text
resources/
    papers/
        ADS/                 # Advertising in LLMs research
        CRS/                 # Conversational recommender systems
        Dimension-User/      # User modeling & archetypes
        EEG/                 # Neuroscience / attention studies
        LLM/                 # LLM fundamentals for RecSys
        RAG/                 # Retrieval-augmented generation
        RecSys/              # Recommender systems (general)
        RL/                  # Reinforcement learning for RecSys
    blogs/                   # Industry blog posts & reports
    books/                   # Reference textbooks
src/
    project/                 # TARA — main application
        .streamlit/          # Streamlit theme & server config
        app.py               # Streamlit entrypoint (main chat)
        pages/               # Multi-page views (dashboard, etc.)
        core/                # Backend modules (config, ad injection,
                             #   attention shift, conversation, logger)
        docker-compose.yml   # vLLM + Streamlit orchestration
        Dockerfile           # Container definition
        requirements.txt     # Python dependencies
        .env                 # Environment variables
    scripts/                 # Standalone utility scripts
    notebooks/               # Jupyter notebooks for exploration
docs/                        # Project documentation (WIP)
README.md
LICENSE
```
- **resources/**: Collected papers, blogs, and books organized by topic.
- **src/project/**: TARA — the main Streamlit application, Docker setup, and backend modules.
- **src/scripts/**: Standalone utility scripts and exploratory code.
- **src/notebooks/**: Jupyter notebooks for experimentation.
- **docs/**: Project documentation and drafts.

## Usage

See the [project README](src/project/README.md) for detailed setup instructions, environment variables, and how to run with Docker or locally.

## Main sources of Literature

In order to be sure of the SOTA and to be fully aware of the trends in RecSys, the following extensive compilation has been crafted:

- [ACM RecSys Conference YT](https://www.youtube.com/@acmrecsys/playlists)
- [Awesome RecSys (Basic) Repository](https://github.com/jihoo-kim/awesome-RecSys)
- [Ludo's Recsys Blog at Google](https://machinelearningatscale.substack.com/p/deep-dive-series)
- [Awesome LLMs for RecSys](https://github.com/WLiK/LLM4Rec-Awesome-Papers)
- [Awesome LLMs in RecSys (Multiple purposes)](https://github.com/CHIANGEL/Awesome-LLM-for-RecSys)
- [Awesome LLM enhanced RecSys](https://github.com/nancheng58/Awesome-LLM4RS-Papers)

From the industry side (Anthropic, OpenAI, Gemini)... not much can be said as they don't reveal their secrets... but there are some news regarding the topic:

- [LinkedIn LLM Advertisement News](https://www.linkedin.com/pulse/llm-advertising-marketing-channel-shift-define-next-decade-velinov-jshif/)
- [LLM Ads blogpost](http://incrmntal.com/resources/llm-advertising)
- [Perplexity vs Gemini vs OpenAI in Ads](https://searchengineland.com/perplexity-stops-testing-advertising-469452)
- [Google Approach to AI Ads](https://support.google.com/google-ads/answer/16297775?hl=en#ads_in_ai_overviews)
- [OpenAI Ads principles](https://www.youtube.com/watch?v=2agJo3Jf_O4&t=1233s)
- [OpenAI Agentic Commerce protocol (ACP)](https://developers.openai.com/commerce)
- [Thrad: LLM-Driven Advertisement Startup](https://www.thrad.ai/)
- [Thrad CEO Podcast talk](https://www.youtube.com/watch?v=CxAxt1xUpW0)

As a footnote, [this paper](https://openreview.net/forum?id=kioO6a0oHM&referrer=%5Bthe%20profile%20of%20Thomas%20L.%20Griffiths%5D(%2Fprofile%3Fid%3D~Thomas_L._Griffiths1)) hasn't yet seen the public eye but can be extremely benefitial to read once it gets published.

## Contributing
In order to contribute to this project please submit github issues, feel free to post pull requests!

## License
This project is licensed under the terms of the MIT License. See the [LICENSE](LICENSE) file for details.
