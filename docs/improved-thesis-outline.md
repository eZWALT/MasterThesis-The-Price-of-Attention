# Improved Thesis Outline — Conversational Advertising in LLM Systems

Based on: current skeleton chapters on Atlas + working drafts (Walter/Ioannis/main.tex) + implemented codebase.

---

## Front Matter
- Abstract
- Acknowledgements
- Dedication
- Table of Contents
- List of Figures / Tables / Algorithms

---

## Chapter 1: Introduction
### 1.1 Motivation
- The rise of LLM-based conversational agents (ChatGPT, Perplexity, Gemini)
- The inevitable monetization through advertising (OpenAI ads announcement, Perplexity sponsored suggestions)
- Why traditional web advertising metrics (CTR, CPM) break in conversational settings
- The need for a principled understanding of how ads affect user trust, cognitive load, and experience

### 1.2 Problem Statement
- How do ad format, insertion timing, and conversational context shape user responses in multi-turn LLM interactions?
- Formalized as: studying the mapping f(AdType, Timing, User, Context) → UserExperience (trust, intrusiveness, cognitive load, behavioral outcomes)
- Beyond CTR: trust floor, semantic attention shift, neurophysiological validation

### 1.3 Research Questions (Summary)
- Clustered into 5 groups:
  1. Ad Type Effects (RQ1–RQ5)
  2. Temporal Effects (RQ6–RQ9)
  3. User Heterogeneity (RQ10–RQ11)
  4. Neurophysiological Mechanisms (RQ12–RQ13)
  5. Predictive Analysis (RQ14–RQ16)

### 1.4 Contributions
1. Controlled multimodal dataset of human-LLM interactions with systematically varied ad formats
2. Multi-output predictive model of user experience under conversational ads
3. Multimodal analysis (EEG + eye-tracking) of cognitive and attentional effects
4. Unified experimental framework + theoretical taxonomy for conversational advertising

### 1.5 Thesis Roadmap

---

## Chapter 2: Related Work
### 2.1 Advertising in LLM-Based Systems
- Xu et al. (2026): Ad Insertion in LLM-Generated Responses
- Heineking et al. (2026): Detecting RAG Advertisements Across Advertising Styles
- Feizi et al. (2023): Online Advertisements with LLMs
- OpenAI's ad strategy, Perplexity's sponsored questions, Bing's integrated ads

### 2.2 Conversational Recommender Systems
- CRS with LLM data augmentation, user simulation (UserSimCRS)
- Multi-agent conversational recsys
- RAG-based conversational prompting
- Personality-aware CRS (Zhao et al. 2025)

### 2.3 User Experience and Trust in AI
- Trust in AI systems, perceived intrusiveness
- OCEAN personality and persuasion sensitivity
- Cognitive load theory in human-computer interaction

### 2.4 Neurophysiological Signals in HCI
- EEG indices: Cognitive Load Index (CLI), Engagement Index (EI), Frontal Alpha Asymmetry (FAA)
- Eye-tracking for attention measurement
- Prior work on neurophysiological correlates of advertising response

### 2.5 Gaps and Positioning
- No existing dataset combines LLM advertising interventions with multimodal signals
- Limited understanding of how ad format affects cognitive load and attention in conversation
- No predictive model of ad appropriateness conditioned on conversational state

---

## Chapter 3: Dataset
### 3.1 Catalogue
#### 3.1.1 Dataset Overview
- Two corpora: Amazon Electronics (1M+ products) + curated catalogs (Travel, Hobby)
- Product fields: title, description, brand, category, price, reviews

#### 3.1.2 Preprocessing
- Cleaning, deduplication, text normalization
- Catalog adapter system (Amazon adapter, generic adapter)
- Filtering and quality control

#### 3.1.3 Vector Database
- FAISS index with embedding models (Qwen-3 Embedding 8B)
- Hybrid retrieval (dense + sparse)
- Index building pipeline

### 3.2 Experiment Data
#### 3.2.1 Data Collection Protocol
- Within-subject design: 4 ad types × 3 timing conditions × 4 task types
- Session structure: consent → setup → baseline → 4 trials → debrief
- Task design across 3 intent genres: Informational, Transactional, Reflective/Social

#### 3.2.2 Multimodal Logging Architecture
- Conversational data (turns, messages, timestamps)
- Behavioral data (response times, continuation, abandonment)
- Self-report data (trust, intrusiveness, usefulness, satisfaction — Likert scales)
- Neurophysiological data (EEG: 8 channels, Eye-tracking: gaze/fixation)

#### 3.2.3 Data Structure and Schema
- Unified timestamp synchronization across modalities
- JSONL log format
- Session and trial structure

#### 3.2.4 Descriptive Statistics
- Participant demographics
- Distribution of sessions, trials, turns
- Coverage across experimental conditions

---

## Chapter 4: Methods
### 4.1 Advertisement Policy
#### 4.1.1 Taxonomy of Conversational Ads
- Content dimension, Integration mode, Strategy, Initiative
- Formal definition: A = (C, τ, α)

#### 4.1.2 Ad Types (Integration Modes)
1. Inline Persuasive Suggestion (subtle, embedded in response)
2. Sponsored Conversational Suggestion (Perplexity-style, labeled follow-up)
3. Sponsored Recommendation (Bing-style, labeled insertion)
4. Explicit Ad Block (OpenAI-style, visually separated CTA)

#### 4.1.3 Ad Content Selection
- Semantic alignment with conversational context
- Catalog retrieval → product selection → template-based injection

#### 4.1.4 Timing and Greediness
- Fixed timing at turns t=3 and t=6
- Greediness fixed at frequency=1 (controlled out)
- Quantization of timing into Early/Mid/Late

### 4.2 Study Design
#### 4.2.1 Experimental Framework
- Within-subject with 4 trials per participant
- Counterbalancing: Latin-square for task order, balanced ad-type assignment
- Independent variable: Ad Type (4 levels)
- Dependent variables (primary): Trust, Perceived Intrusiveness
- Covariates: turn index, message length, conversation length, inferred intent
- Moderating variables: OCEAN personality, task type

#### 4.2.2 Hypotheses
- H1: More intrusive ad formats → decrease in user trust
- H2: More intrusive ad formats → increase in perceived intrusiveness
- H3: More intrusive ad formats → reduced interaction continuation
- H4: Neurophysiological signals improve predictive performance beyond conversational features
- H5: Personality traits moderate ad type effects on user response

#### 4.2.3 Session Structure
- Introduction and Consent (~10 min)
- Sensor Setup + Personality Assessment (~15 min)
- Baseline Recording + Practice Trial (~5 min)
- Main Experiment (4 trials × ~15 min)
- Final Survey + Debrief (~5 min)

#### 4.2.4 Task Design
- 4 tasks spanning Informational, Transactional, Reflective/Social intents
- Examples: budget laptop find, trip planning, gift selection, life optimization

### 4.3 Biases and Trade-offs
- Ordering and carryover effects (mitigated by counterbalancing)
- Demand characteristics and social desirability bias
- Ecological validity vs. experimental control
- Limitations of self-report measures
- Sample size constraints (N≈50) and statistical power

### 4.4 ML System Design
#### 4.4.1 System Architecture
- Frontend: Streamlit web interface
- Backend: Python orchestration + FastAPI
- LLM Serving: vLLM with Qwen 3.5 (30B, 4-bit quantized)
- Storage: JSONL structured logs

#### 4.4.2 RAG Pipeline
- Query preprocessing and intent classification (BERT/DistilBERT)
- Embedding-based retrieval (Qwen-3 Embedding 8B)
- Hybrid search (dense + sparse stages)
- Cross-encoder reranking (Qwen-3 Reranker 8B)
- Response formatting and ad injection

#### 4.4.3 Advertisement Injection Engine
- Response modification at predefined turns
- Template-based ad insertion per integration mode
- Ad content from retrieved catalog items

#### 4.4.4 Multimodal Sensor Integration
- EEG: 8-channel system, real-time streaming, LSL markers
- Eye-tracking: fixation, gaze, saccade logging
- Synchronization protocol with unified timestamps

#### 4.4.5 GPU Resource Management
- GPU 0 (40GB): Quantized Qwen 3.5 30B (<24GB) + KV-cache
- GPU 1 (40GB): Embedding Model (8B) + Reranker Model (8B)
- CPU: BERT + UI + Sensors + Logging + VectorDB (FAISS)

### 4.5 Evaluation Metrics
#### 4.5.1 Behavioral Metrics
- Ad click / conversion
- Time to reply
- Abandonment rate
- Conversation continuation

#### 4.5.2 Self-Report Metrics
- Trust (ΔT = T_post - T_pre)
- Perceived intrusiveness
- Perceived usefulness
- Overall satisfaction

#### 4.5.3 Neurophysiological Metrics
- Cognitive Load Index (CLI = θ_frontal / β_frontal)
- Engagement Index (EI = β / (α + θ))
- Frontal Alpha Asymmetry (FAA = ln(α_right) - ln(α_left))
- Frontal theta power (workload marker)
- Alpha suppression (Δα = 1 - α(t)/α_baseline)
- Eye-tracking: fixation duration, time to first fixation, gaze count

#### 4.5.4 Conversational Metrics
- Semantic attention shift (ΔS = 1 - cos(e_{t*-1}, e_{t*+1}))
- Intent trajectory divergence

---

## Chapter 5: Results
### 5.1 Experimental Results
#### 5.1.1 Effect of Ad Type on Trust and Intrusiveness
- ANOVA / mixed-effects models
- Post-hoc comparisons across 4 ad types

#### 5.1.2 Effect of Ad Type on Behavioral Outcomes
- Conversion rates
- Abandonment analysis
- Response time analysis

#### 5.1.3 Effect of Ad Timing
- Early vs. Mid vs. Late insertion
- Interaction with ad type

#### 5.1.4 Moderation by Task Type
- Do effects differ across informational, transactional, reflective tasks?

#### 5.1.5 Personality Moderation
- OCEAN traits: which users are more sensitive to ad formats?

### 5.2 Neurophysiological Results
#### 5.2.1 EEG Signal Analysis
- CLI, EI, FAA across ad types
- Event-related synchronization/desynchronization
- Time-frequency analysis around ad insertion

#### 5.2.2 Eye-Tracking Analysis
- Fixation patterns on ad vs. content regions
- Gaze disruption following ad insertion

#### 5.2.3 Correlations with Self-Report
- Do neural signals correlate with trust/intrusiveness ratings?

### 5.3 Predictive Modeling Results
#### 5.3.1 Ad Opportunity Prediction
- P(AdAppropriate_t = 1 | State_t, AdType, Context)
- Feature importance analysis
- Ablation: conversational features vs. conversational + neuro signals

#### 5.3.2 User Experience Prediction
- Multi-output prediction of trust, intrusiveness, satisfaction
- Comparison of feature sets (behavioral only vs. +neuro)

#### 5.3.3 Semantic Attention Shift Analysis
- Did ads change the conversational trajectory?
- Intent transitions pre/post ad insertion

---

## Chapter 6: Discussion
### 6.1 Interpretation of Findings
### 6.2 Implications for LLM Platform Design
### 6.3 Limitations
- Sample size and statistical power
- Lab setting vs. real-world deployment
- Single LLM model (Qwen 3.5)
- Fixed timing, no adaptive policy

### 6.4 Ethical Considerations
- User transparency and informed consent
- Manipulation and persuasion risks
- Vulnerable populations
- Data privacy and anonymization

---

## Chapter 7: Conclusion
### 7.1 Summary of Contributions
### 7.2 Future Work
- RL-based adaptive ad insertion policies
- Personalized advertising under user trait heterogeneity
- Data augmentation and synthetic user simulation
- Cross-platform generalization (beyond Qwen)
- Longitudinal trust modeling

---

## Back Matter
- References
- Appendices:
  - A: Example Task Prompts
  - B: Post-Trial Survey Questions
  - C: OCEAN BFI-10 Questionnaire
  - D: EEG Electrode Placement and Preprocessing
  - E: System Configuration and Deployment Details
  - F: Additional Tables and Figures

---

## Key Improvements over Current Outline

| What you had | What's now added |
|---|---|
| Intro: bullet-point skeleton | Full narrative: motivation, problem, RQs, contributions, roadmap |
| Missing "Related Work" chapter | Ch2: LLM ads, CRS, trust in AI, neuro-HCI, gaps |
| Dataset: algorithm stub only | Full catalog, preprocessing, vector DB, experiment protocol, multimodal logging, schema |
| Methods: figure stub | Ad taxonomy (4 types, formal definition), study design (hypotheses, counterbalancing, session structure, tasks), biases, system architecture, RAG pipeline, injection engine, GPU layout, 4 metric families |
| Results: table stub | 3 result families: experimental (5 analyses), neuro (EEG/eye-tracking), predictive (opportunity, experience, attention shift) |
| Conclusion: empty | Summary + discussion + ethics + future work |
| No appendices | 6 appendices with concrete materials |
