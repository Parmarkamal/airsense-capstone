"""
AirSense — Capstone Report Generator (Chapters 1, 2, 3)
File: report_chapters_part1.py
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_chapter_1(doc, helpers):
    add_chapter_title = helpers['add_chapter_title']
    add_heading_1 = helpers['add_heading_1']
    add_heading_2 = helpers['add_heading_2']
    add_styled_paragraph = helpers['add_styled_paragraph']
    add_bullet_point = helpers['add_bullet_point']
    add_callout_box = helpers['add_callout_box']
    add_figure_placeholder = helpers['add_figure_placeholder']
    add_academic_table = helpers['add_academic_table']

    add_chapter_title(doc, 1, "Introduction")

    add_heading_1(doc, "1.1 Introduction")
    p1 = (
        "Atmospheric air pollution has emerged as one of the defining public health and environmental crises of the "
        "twenty-first century. According to epidemiologic assessments conducted by the World Health Organization (WHO), "
        "ambient particulate matter exposure accounts for an estimated 7 million premature fatalities globally each year, "
        "with south Asian urban centers bearing an alarming, disproportionate share of this burden. Rapid industrialization, "
        "accelerated vehicular fleet expansion, thermal power generation, construction activities, and regional biomass burning "
        "have culminated in chronic atmospheric degradation across major Indian urban conglomerates. Metropolitan hubs such as "
        "Delhi, Ahmedabad, Mumbai, and surrounding industrial centers routinely record particulate matter concentrations—specifically "
        "fine respirable particles measuring under 2.5 micrometers in aerodynamic diameter (PM2.5)—that exceed safe regulatory "
        "benchmarks by five to twenty-fold during seasonal atmospheric inversions."
    )
    add_styled_paragraph(doc, p1)

    p2 = (
        "In response to this growing public health emergency, environmental regulatory authorities including the Central Pollution "
        "Control Board (CPCB) in India and international scientific consortiums have established dense networks of Continuous Ambient "
        "Air Quality Monitoring Stations (CAAQMS). These automated sensory installations continuously sample ambient air, quantifying "
        "criteria pollutants including PM2.5, PM10, nitrogen dioxide (NO2), sulfur dioxide (SO2), carbon monoxide (CO), and ozone (O3). "
        "These sensory readings are computationally aggregated into the standardized National Air Quality Index (AQI), a composite "
        "numerical metric mapped to six risk-graded categories ranging from 'Good' (0–50) to 'Severe' (401–500)."
    )
    add_styled_paragraph(doc, p2)

    p3 = (
        "However, while data collection infrastructure has advanced dramatically, the downstream analytical utility of this "
        "environmental telemetry remains critically impaired by several systemic deficiencies. First, existing municipal dashboards "
        "function almost exclusively as retrospective reporting mechanisms; they depict historical or delayed hourly measurements, "
        "failing to furnish forward-looking, predictive trajectories that allow citizens and municipal planners to preemptively "
        "mitigate hazardous exposure. Second, an isolated numerical AQI value provides negligible clinical context for ordinary "
        "citizens. A reading of 240 conveys an abstract warning of 'Poor' air, but fails to inform an asthmatic jogger, a parent "
        "evaluating school commute safety, or an elderly cardiac patient regarding concrete, medically grounded precautions. "
        "Third, public querying of contemporary cloud-hosted Large Language Models (LLMs) frequently generates catastrophic hallucinations "
        "or generic platitudes that lack formal evidentiary alignment with statutory CPCB and WHO health guidelines."
    )
    add_styled_paragraph(doc, p3)

    add_heading_1(doc, "1.2 Motivation")
    p_mot1 = (
        "The motivation behind the AirSense platform stems from an urgent academic and societal necessity: to transform raw, "
        "fragmented environmental telemetry into proactive, personalized, and clinically grounded health intelligence. "
        "For business intelligence and data science practitioners, environmental telemetry represents an exemplary streaming "
        "data engineering challenge characterized by high-frequency velocity, multi-sensor variance, missing value anomalies, "
        "and non-linear temporal dynamics."
    )
    add_styled_paragraph(doc, p_mot1)

    add_bullet_point(doc, "Decoupled Edge Streaming Architecture:", 
                     "Eliminating centralized single points of failure by architecting a lightweight, local-first streaming pipeline capable of continuous execution on consumer laptops without recurring cloud infrastructure expenses.")
    add_bullet_point(doc, "Rigorous Time-Series Predictive Forecasting:", 
                     "Moving beyond naive historical charts to train gradient-boosted decision tree architectures (LightGBM) using strict walk-forward temporal cross-validation, generating reliable 48-hour forward projections.")
    add_bullet_point(doc, "Zero-Hallucination Generative Health Advisory:", 
                     "Pioneering the fusion of Retrieval-Augmented Generation (RAG) with local quantized Large Language Models (Ollama), strictly conditioning AI advice on authoritative WHO 2021 and CPCB NAAQS guidelines.")
    add_bullet_point(doc, "Data Privacy & Operational Independence:", 
                     "Ensuring that sensitive user health questions and lifestyle queries never depart the user's laptop, eliminating external cloud dependency and recurring subscription costs.")

    add_callout_box(doc, "Core Capstone Research Philosophy", 
                    "AirSense demonstrates that enterprise-grade streaming data engineering, high-accuracy gradient-boosted time-series forecasting, and evidence-grounded Generative AI can be harmoniously deployed 100% locally on standard academic hardware at zero financial budget, guaranteeing absolute user privacy.")

    add_heading_1(doc, "1.3 Objectives")
    p_obj = (
        "The primary academic and technical objectives of the AirSense capstone research are formalized as follows:"
    )
    add_styled_paragraph(doc, p_obj)

    add_bullet_point(doc, "1. Real-Time Streaming Ingestion Pipeline:", 
                     "Engineer an automated ingestion mechanism interfacing with the World Air Quality Index (WAQI) Open Data Platform, publishing hourly multi-pollutant telemetry across six strategically selected Indian urban hubs (Ahmedabad, Surat, Rajkot, Gandhinagar, Delhi, Mumbai) into an Apache Kafka distributed messaging topic.")
    add_bullet_point(doc, "2. Schema Enforcement & Resilient Stream Consumption:", 
                     "Implement a robust consumer service leveraging Pydantic v2 schemas to enforce boundary validations (AQI: 0–999, non-negative concentrations, temporal monotonicity), routing non-conformant readings to dead-letter audit logs.")
    add_bullet_point(doc, "3. Temporal Hypertable Database Partitioning:", 
                     "Deploy an in-memory optimized TimescaleDB engine (PostgreSQL extension) utilizing automated one-day hypertable chunking and continuous aggregates to support millisecond-latency analytical queries.")
    add_bullet_point(doc, "4. Walk-Forward Tabular Machine Learning Forecasting:", 
                     "Develop a LightGBM gradient boosting model incorporating temporal cyclical encodings (sine/cosine transformations of hour and day) and multi-scale autoregressive lag features (1h, 2h, 3h, 24h, 168h), achieving an RMSE threshold < 30.0 across 48-hour recursive projections.")
    add_bullet_point(doc, "5. Grounded RAG Knowledge Base Construction:", 
                     "Construct an in-process dense vector index in ChromaDB utilizing the 'all-MiniLM-L6-v2' sentence-transformer model to index official WHO Global Air Quality Guidelines (2021) and CPCB NAAQS standards into overlapping semantic text chunks.")
    add_bullet_point(doc, "6. Private Edge Conversational AI Health Engine:", 
                     "Integrate local quantized Large Language Models (llama3.2:3b / qwen2.5-coder:3b) via Ollama, utilizing hybrid context injection (live sensor readings + 48-hour forecasts + retrieved guideline excerpts) to deliver safe, medically disclaimed citizen advice.")
    add_bullet_point(doc, "7. Multi-Tier Business Intelligence Visualisation:", 
                     "Deliver an interactive Streamlit 5-view command center and an enterprise Power BI analytical dashboard modeling city-level air quality indices, diurnal cycles, and combustion source diagnostics.")

    add_heading_1(doc, "1.4 Organization of the Report")
    p_org = (
        "The remainder of this capstone project report is structured systematically across seven subsequent chapters:\n\n"
        "• Chapter 2 (Background Theory) reviews ambient air quality standards, Apache Kafka distributed messaging, TimescaleDB time-series storage, LightGBM mathematical formulation, and Retrieval-Augmented Generation mechanics.\n"
        "• Chapter 3 (Literature Survey & Comparative Study) critically evaluates related scholarly literature, existing commercial air quality platforms, and tabulates a comprehensive comparative study matrix.\n"
        "• Chapter 4 (Proposed Work) details the formal problem statement, research gap, the five-layer architectural blueprint of AirSense, expected outcomes, and the 12-week Agile project roadmap.\n"
        "• Chapter 5 (Implementation Environment) documents the physical hardware specifications, software dependencies, runtime versions, and IDE development tooling.\n"
        "• Chapter 6 (Dataset And Visualization) outlines data acquisition protocols, Pydantic data cleansing, feature engineering pipelines, and exploratory visual analytics including Folium maps and diurnal rhythm charts.\n"
        "• Chapter 7 (Implementation And Evaluation) presents the walk-forward model training methodology, comparative machine learning benchmarking, hyperparameter optimization, production artifact deployment, RAG vector retrieval evaluation, and Power BI dashboards.\n"
        "• Chapter 8 (Conclusion & Future Scope) summarizes empirical findings, academic contributions, and articulates future research directions including edge IoT sensor networks and automated retraining pipelines."
    )
    add_styled_paragraph(doc, p_org)

    add_figure_placeholder(doc, "1.1", "End-to-End Decoupled 5-Layer Edge Architecture of AirSense", 
                           "Depicting WAQI API Ingestion → Apache Kafka Broker → Pydantic Consumer → TimescaleDB Hypertables → LightGBM Forecaster → ChromaDB Vector Store → Ollama Local LLM → Streamlit & Power BI Frontend.")

    # Specs Table
    add_academic_table(
        doc,
        headers=["Component Layer", "Primary Technology", "Host Port / Runtime", "Primary Functional Role"],
        data=[
            ["Layer 1: Ingestion", "WAQI REST API + Python", "HTTPS / Background", "Hourly telemetry fetching for 6 Indian urban hubs"],
            ["Layer 2: Messaging", "Apache Kafka + ZooKeeper", "localhost:9092 & 2181", "Decoupled pub-sub streaming queue (topic: aqi_raw)"],
            ["Layer 3: Storage", "TimescaleDB (Docker)", "localhost:5433", "Time-series hypertable storage with 1-day chunking"],
            ["Layer 4: Forecasting", "LightGBM + MLflow", "ml/production/lgbm_aqi.pkl", "Recursive 48-hour forward projection (RMSE 7.61)"],
            ["Layer 5: Edge GenAI", "ChromaDB + Ollama", "localhost:11434 (llama3.2)", "RAG semantic grounding against WHO & CPCB guidelines"],
            ["Layer 6: Visual Analytics", "Streamlit + Power BI", "localhost:8501 / Desktop", "5-View executive command center & DAX reporting"],
        ],
        table_number="1.1",
        caption="AirSense Architectural Layer Breakdown and Network Endpoints",
        col_widths=[1.5, 1.6, 1.6, 2.3]
    )

def build_chapter_2(doc, helpers):
    add_chapter_title = helpers['add_chapter_title']
    add_heading_1 = helpers['add_heading_1']
    add_heading_2 = helpers['add_heading_2']
    add_styled_paragraph = helpers['add_styled_paragraph']
    add_bullet_point = helpers['add_bullet_point']
    add_callout_box = helpers['add_callout_box']
    add_figure_placeholder = helpers['add_figure_placeholder']
    add_academic_table = helpers['add_academic_table']

    add_chapter_title(doc, 2, "Background Theory")

    add_heading_1(doc, "2.1 Air Quality Standards & Health Impacts")
    p1 = (
        "Ambient air quality quantification rests upon rigorous chemical and physical measurements of suspended atmospheric "
        "particulates and gaseous compounds. The Central Pollution Control Board (CPCB), functioning under the Ministry of Environment, "
        "Forest and Climate Change (MoEFCC), Government of India, promulgated the revised National Ambient Air Quality Standards (NAAQS) "
        "in 2009. The Indian AQI formulation synthesizes eight primary criteria pollutants into a standardized index using segmented "
        "linear interpolation based on toxicological health risk thresholds."
    )
    add_styled_paragraph(doc, p1)

    p2 = (
        "The mathematical formulation for calculating the sub-index (I_p) for a given pollutant concentration (C_p) is governed by:\n\n"
        "    I_p = [ (I_hi - I_lo) / (B_hi - B_lo) ] * (C_p - B_lo) + I_lo\n\n"
        "where B_hi and B_lo denote the upper and lower concentration breakpoints for the category corresponding to C_p, "
        "and I_hi and I_lo represent the corresponding AQI sub-index category limits. The overall AQI is defined as the supremum "
        "of all computed pollutant sub-indices: AQI = max(I_1, I_2, ..., I_n)."
    )
    add_styled_paragraph(doc, p2)

    add_academic_table(
        doc,
        headers=["AQI Category", "AQI Range", "PM2.5 (24h) µg/m³", "PM10 (24h) µg/m³", "Health Impact Advisory"],
        data=[
            ["Good", "0 – 50", "0 – 30", "0 – 50", "Minimal health impact; clean and safe for all outdoor activities."],
            ["Satisfactory", "51 – 100", "31 – 60", "51 – 100", "Minor breathing discomfort to sensitive individuals."],
            ["Moderate", "101 – 200", "61 – 90", "101 – 250", "Discomfort to patients with asthma, lung, and heart diseases."],
            ["Poor", "201 – 300", "91 – 120", "251 – 350", "Breathing discomfort to most people on prolonged outdoor exposure."],
            ["Very Poor", "301 – 400", "121 – 250", "351 – 430", "Respiratory illness on prolonged exposure; severe effect on vulnerable."],
            ["Severe", "401 – 500", "250+", "430+", "Healthy people affected; serious impacts on patients; emergency actions required."],
        ],
        table_number="2.1",
        caption="Central Pollution Control Board (CPCB) NAAQS 6-Tier AQI Breakpoints and Health Impacts",
        col_widths=[1.1, 1.0, 1.2, 1.2, 2.5]
    )

    add_heading_1(doc, "2.2 Distributed Event Streaming with Apache Kafka")
    p_k1 = (
        "Traditional monolithic architectures rely on periodic batch database extraction (ETL), creating latency lag and "
        "tight coupling between sensory data producers and analytical consumers. To achieve resilient, production-grade ingestion, "
        "AirSense adopts Apache Kafka, a high-throughput, distributed event streaming platform built upon the publish-subscribe paradigm."
    )
    add_styled_paragraph(doc, p_k1)

    p_k2 = (
        "Kafka models streaming data as an append-only, ordered commit log partitioned across topics. In the AirSense architecture, "
        "the ingestion producer polls the WAQI sensor network hourly, transforms JSON telemetry, and publishes serialized byte records "
        "to the topic 'aqi_raw'. The consumer group 'airsense_consumer' maintains its own committed offset pointer. This decoupling "
        "ensures that network spikes, transient database maintenance, or downstream compute pauses never result in data loss."
    )
    add_styled_paragraph(doc, p_k2)

    add_figure_placeholder(doc, "2.1", "Apache Kafka Distributed Pub-Sub Message Broker Pipeline", 
                           "Ingestion Fetcher publishes to topic 'aqi_raw' -> Kafka Broker log -> Consumer group with offset tracking -> Validated persistence.")

    add_heading_1(doc, "2.3 Time-Series Storage Engine (TimescaleDB / PostgreSQL)")
    p_ts1 = (
        "Standard Relational Database Management Systems (RDBMS) suffer severe B-Tree indexing degradation when ingesting continuous "
        "time-series streams exceeding millions of rows. TimescaleDB resolves this fundamental bottleneck by introducing 'Hypertables'—an "
        "abstraction layer built directly on PostgreSQL that automatically partitions data across temporal chunks."
    )
    add_styled_paragraph(doc, p_ts1)

    p_ts2 = (
        "In AirSense, the table 'aqi_readings' is converted to a hypertable partitioned into 1-day temporal chunks: "
        "'SELECT create_hypertable('aqi_readings', 'time', chunk_time_interval => INTERVAL '1 day');'. "
        "Each chunk maintains its own local memory indexes, allowing inserts to hit active RAM pages while analytical queries "
        "utilize chunk exclusion pruning, executing aggregation queries across millions of observations in under 15 milliseconds."
    )
    add_styled_paragraph(doc, p_ts2)

    add_figure_placeholder(doc, "2.2", "TimescaleDB Hypertable Temporal Partitioning & Chunk Management", 
                           "Continuous time stream partitioned into 1-day isolated chunks, optimizing disk I/O and continuous aggregate views.")

    add_heading_1(doc, "2.4 Gradient Boosting for Tabular Forecasting (LightGBM)")
    p_lgb1 = (
        "While recurrent deep neural networks such as LSTMs and GRUs are frequently proposed for sequence modeling, empirical research "
        "in machine learning consistently demonstrates that Gradient Boosted Decision Trees (GBDT) outperform deep architectures on "
        "heterogeneous tabular time-series containing localized seasonal shifts, missing sensor intervals, and distinct calendar drivers."
    )
    add_styled_paragraph(doc, p_lgb1)

    p_lgb2 = (
        "LightGBM (Light Gradient Boosting Machine) introduces two transformative algorithmic innovations: Gradient-based One-Side "
        "Sampling (GOSS) and Exclusive Feature Bundling (EFB). GOSS preserves instances with large gradients (under-fitted samples) "
        "while randomly sub-sampling instances with small gradients, computing variance-reduced information gain with exceptional speed. "
        "Furthermore, LightGBM employs a leaf-wise (best-first) tree growth strategy rather than level-wise, minimizing loss more "
        "effectively per split."
    )
    add_styled_paragraph(doc, p_lgb2)

    add_figure_placeholder(doc, "2.3", "Recursive Autoregressive Multi-Step 48-Hour Forecasting Scheme", 
                           "Step t predicts t+1 -> feedback into lag features -> predicts t+2 ... up to t+48 hours.")

    add_heading_1(doc, "2.5 Retrieval-Augmented Generation & Edge GenAI (ChromaDB & Ollama)")
    p_rag1 = (
        "Large Language Models (LLMs) trained on broad internet corpora suffer from two critical handicaps in specialized domains: "
        "temporal obsolescence (inability to perceive live sensor state) and catastrophic hallucinations (confidently generating "
        "inaccurate medical dosages or non-existent air thresholds). Retrieval-Augmented Generation (RAG) resolves this by bifurcating "
        "knowledge into a non-parametric memory store (vector database) and a parametric generation model (LLM)."
    )
    add_styled_paragraph(doc, p_rag1)

    p_rag2 = (
        "AirSense deploys ChromaDB as an in-process, high-density vector store. Clinical and regulatory documents are partitioned into "
        "600-character segments with 100-character overlaps. These chunks are embedded into 384-dimensional dense vectors using the "
        "'all-MiniLM-L6-v2' transformer model. When a user queries the system, semantic similarity is computed via cosine distance:\n\n"
        "    Cosine_Distance(u, v) = 1 - [ (u · v) / (||u||_2 * ||v||_2) ]\n\n"
        "The top-K most similar guideline excerpts are retrieved and injected into a strict system prompt alongside real-time city AQI "
        "readings. This augmented context is fed to a quantized local LLM (llama3.2:3b) executed via Ollama, guaranteeing 100% evidentiary "
        "citation and zero data egress from the host machine."
    )
    add_styled_paragraph(doc, p_rag2)

    add_figure_placeholder(doc, "2.4", "Retrieval-Augmented Generation (RAG) Semantic Verification Framework", 
                           "User query -> ChromaDB dense search -> Context augmentation -> Ollama edge LLM -> Grounded advice with disclaimer.")

def build_chapter_3(doc, helpers):
    add_chapter_title = helpers['add_chapter_title']
    add_heading_1 = helpers['add_heading_1']
    add_heading_2 = helpers['add_heading_2']
    add_styled_paragraph = helpers['add_styled_paragraph']
    add_callout_box = helpers['add_callout_box']
    add_academic_table = helpers['add_academic_table']

    add_chapter_title(doc, 3, "Literature Survey & Comparative Study")

    add_heading_1(doc, "3.1 Literature Survey")
    p_lit1 = (
        "Scholarly investigation into atmospheric air quality informatics spans three distinct evolutionary paradigms: classical "
        "statistical time-series estimation, deep learning sequence modeling, and contemporary conversational generative interfaces."
    )
    add_styled_paragraph(doc, p_lit1)

    p_lit2 = (
        "1. Classical Statistical & Econometric Models (ARIMA / SARIMA):\n"
        "Early research by Box and Jenkins (1976) and subsequent adaptations by Kumar and Goyal (2011) applied Autoregressive Integrated "
        "Moving Average (ARIMA) models to urban air pollution forecasting. While mathematically tractable and offering rigorous "
        "confidence intervals, ARIMA models assume strict stationarity and linearity. Atmospheric chemical reactions, meteorological "
        "convection, and urban emission bursts exhibit extreme non-linearities that classical autoregression fails to capture, resulting "
        "in severe prediction lag during rapid smog spikes."
    )
    add_styled_paragraph(doc, p_lit2)

    p_lit3 = (
        "2. Recurrent Deep Learning Architectures (LSTM / BiLSTM / GRU):\n"
        "To model non-linear temporal dependencies, researchers widely adopted Long Short-Term Memory (LSTM) networks (Hochreiter and "
        "Schmidhuber, 1997). Zhang et al. (2018) developed multi-station LSTM models demonstrating improved temporal sequence tracking. "
        "However, deep recurrent architectures exhibit critical real-world limitations in local edge deployments: they require substantial "
        "computational resources for training, are sensitive to vanishing gradients over extended horizons, and function as opaque 'black boxes' "
        "without interpretable feature importance attribution."
    )
    add_styled_paragraph(doc, p_lit3)

    p_lit4 = (
        "3. Gradient Boosted Decision Trees (XGBoost / LightGBM):\n"
        "Recent benchmarks by Ke et al. (2017) and Chen et al. (2016) demonstrated that gradient-boosted decision trees routinely surpass "
        "deep neural networks on tabular time-series tasks when paired with deliberate feature engineering (lags, rolling moments, and cyclical "
        "temporal encodings). LightGBM demonstrates superior memory efficiency and training speed, rendering it ideal for edge execution."
    )
    add_styled_paragraph(doc, p_lit4)

    p_lit5 = (
        "4. Generative AI & Retrieval-Augmented Generation (RAG):\n"
        "Lewis et al. (2020) formalized Retrieval-Augmented Generation, demonstrating that conditioning pre-trained language models on "
        "dynamically retrieved dense vector passages drastically reduces factual hallucination. While RAG has seen rapid adoption in "
        "enterprise document management, its application to real-time environmental streaming telemetry and localized clinical public health "
        "guidelines remains virtually unexplored in current academic literature."
    )
    add_styled_paragraph(doc, p_lit5)

    add_heading_1(doc, "3.2 Comparative Study")
    p_comp = (
        "To establish the unique academic and practical contributions of the AirSense platform, Table 3.1 synthesizes a systematic "
        "comparative evaluation against existing commercial, governmental, and academic environmental systems."
    )
    add_styled_paragraph(doc, p_comp)

    add_academic_table(
        doc,
        headers=["Feature / Metric", "Govt CPCB Portal", "Commercial Apps (IQAir)", "Academic LSTM Papers", "AirSense (This Project)"],
        data=[
            ["Data Ingestion Mode", "Batch (1-2 hr delay)", "Proprietary Poll", "Static Offline CSV", "Real-Time Streaming (Kafka)"],
            ["Message Decoupling", "None (Direct DB)", "Cloud Queue", "None", "Apache Kafka (Port 9092)"],
            ["Database Engine", "Traditional RDBMS", "Cloud Proprietary", "Flat Files / Pandas", "TimescaleDB Hypertables"],
            ["Forecasting Horizon", "None (Historical)", "24h (Proprietary)", "12-24h (Black box)", "48-Hour Recursive (LightGBM)"],
            ["Forecasting Accuracy", "N/A", "Undisclosed", "RMSE: 25 – 45 AQI", "RMSE: 7.61 AQI (R² 0.961)"],
            ["Experiment Tracking", "None", "Internal", "Manual scripts", "MLflow Local File Store"],
            ["AI Health Advisory", "Static Text Matrix", "Generic Cloud Tips", "None", "Grounded RAG (ChromaDB + Ollama)"],
            ["Data Privacy", "Public Queries", "Cloud Tracking", "N/A", "100% Localhost Edge (Zero Egress)"],
            ["Recurring Cloud Cost", "Public Budget", "Subscription / Ads", "University Cloud", "₹0 (Runs 100% on Laptop)"],
            ["Executive BI Dashboard", "None", "Proprietary UI", "Static Matplotlib", "Streamlit + Power BI Integration"],
        ],
        table_number="3.1",
        caption="Comparative Feature Matrix: Existing Environmental Platforms vs. AirSense Platform",
        col_widths=[1.5, 1.2, 1.3, 1.2, 1.8]
    )

    add_callout_box(doc, "Identified Research & Implementation Gap", 
                    "No existing environmental monitoring platform integrates decoupled distributed event streaming (Kafka), optimized hypertable storage (TimescaleDB), gradient-boosted time-series forecasting (LightGBM), and evidence-grounded Conversational GenAI (RAG + Ollama) into a singular, edge-executable system that operates completely offline at zero cloud financial cost.")

print("[INFO] Chapters 1, 2, 3 builder module loaded.")
