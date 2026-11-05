"""
AirSense — Capstone Report Generator (Chapters 4, 5, 6)
File: report_chapters_part2.py
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_chapter_4(doc, helpers):
    add_chapter_title = helpers['add_chapter_title']
    add_heading_1 = helpers['add_heading_1']
    add_heading_2 = helpers['add_heading_2']
    add_styled_paragraph = helpers['add_styled_paragraph']
    add_bullet_point = helpers['add_bullet_point']
    add_callout_box = helpers['add_callout_box']
    add_figure_placeholder = helpers['add_figure_placeholder']
    add_academic_table = helpers['add_academic_table']

    add_chapter_title(doc, 4, "Proposed Work")

    add_heading_1(doc, "4.1 Problem Statement and Research Gap")
    p_prob = (
        "Contemporary urban populations face continuous exposure to hazardous air pollutants without access to personalized, "
        "predictive health intelligence. Current ambient monitoring ecosystems suffer from three fundamental deficiencies:\n\n"
        "1. Retrospective Latency Gap: Public environmental dashboards publish delayed sensor data, leaving citizens unaware of "
        "impending air quality spikes during critical daily routines such as morning school commutes or outdoor workouts.\n"
        "2. Clinical Interpretation Gap: Raw numerical index readings (e.g., AQI = 215) fail to translate into specific, actionable "
        "medical guidance tailored to vulnerable demographics such as asthmatics, pediatric populations, or cardiac patients.\n"
        "3. Cloud Dependency and Privacy Gap: Commercial air quality applications demand persistent internet connectivity, transmit "
        "sensitive personal location telemetry to remote cloud servers, and subject users to recurring subscription fees or intrusive advertising."
    )
    add_styled_paragraph(doc, p_prob)

    add_heading_1(doc, "4.2 Proposed Approach (Decoupled 5-Layer Edge Architecture)")
    p_app = (
        "To resolve these systemic challenges, this project engineers AirSense—a unified, five-layer edge platform designed to run "
        "entirely on local consumer hardware. The architectural design guarantees that after the initial hourly sensor polling, all "
        "storage, processing, predictive machine learning inference, and generative language model execution occur strictly within "
        "the local host environment (localhost)."
    )
    add_styled_paragraph(doc, p_app)

    add_bullet_point(doc, "Layer 1: Resilient Sensor Ingestion Engine:", 
                     "An automated Python producer interfaces with the World Air Quality Index (WAQI) Open Data API, extracting criteria pollutant readings (PM2.5, PM10, NO2, SO2, CO, O3) and meteorological metadata across six strategically targeted Indian urban centers: Ahmedabad, Surat, Rajkot, Gandhinagar, Delhi, and Mumbai. The ingestion script operates with defensive exponential backoff and payload validation.")
    add_bullet_point(doc, "Layer 2: Distributed Message Streaming (Apache Kafka):", 
                     "Ingested telemetry records are serialized as structured JSON events and published to an Apache Kafka topic ('aqi_raw'). Kafka acts as a distributed shock absorber, ensuring that network fluctuations or downstream analytical spikes never compromise ingestion stability.")
    add_bullet_point(doc, "Layer 3: Time-Series Hypertable Engine (TimescaleDB):", 
                     "A dedicated Python consumer reads events from Kafka, validates every field against Pydantic v2 schemas, and performs atomic upserts into TimescaleDB on host port 5433. Automated 1-day temporal chunking guarantees fast analytical queries and continuous hourly aggregations.")
    add_bullet_point(doc, "Layer 4: Gradient-Boosted Predictive Forecasting (LightGBM):", 
                     "A LightGBM regressor trained via walk-forward TimeSeriesSplit cross-validation projects air quality trajectories across a 48-hour forward horizon. The model incorporates multi-scale autoregressive lags and cyclical trigonometric time encodings, logging parameters and artifacts to MLflow.")
    add_bullet_point(doc, "Layer 5: Evidence-Grounded Conversational AI (ChromaDB + Ollama):", 
                     "A Retrieval-Augmented Generation (RAG) framework couples an in-process ChromaDB vector store (containing embedded WHO 2021 and CPCB NAAQS guidelines) with an edge-quantized Ollama Large Language Model (llama3.2:3b). The advisor answers citizen health queries with mandatory source citations and medical disclaimers.")

    add_figure_placeholder(doc, "4.1", "AirSense 12-Week Agile Implementation Lifecycle & Milestones", 
                           "Structured progression across Phase 1 (Data Foundation), Phase 2 (Visualization), Phase 3 (Forecasting), Phase 4 (AI Health Advisor), Phase 5 (Polish & BI), and Phase 6 (MLOps & Alerts).")

    add_heading_1(doc, "4.3 Expected Outcome and SLA Targets")
    p_sla = (
        "The proposed AirSense system is bound by rigorous, quantifiable Service Level Agreement (SLA) benchmarks:"
    )
    add_styled_paragraph(doc, p_sla)

    add_bullet_point(doc, "Predictive Accuracy Threshold:", "Model Root Mean Squared Error (RMSE) must remain strictly below 30.0 AQI units across test folds, with an R² variance capture > 0.85 and directional accuracy >= 85%.")
    add_bullet_point(doc, "Streaming Latency:", "End-to-end event propagation from WAQI API polling through Kafka streaming into TimescaleDB must complete in < 2.0 seconds per batch.")
    add_bullet_point(doc, "Analytical Query Speed:", "Database retrieval for 24-hour city trends and 48-hour forecasts must execute in < 50 milliseconds.")
    add_bullet_point(doc, "Edge GenAI Response Latency:", "Local LLM semantic retrieval and health advisory text generation must complete in < 30 seconds on a standard consumer laptop GPU/CPU.")
    add_bullet_point(doc, "Absolute Operational Cost:", "₹0 recurring cloud infrastructure expenditure; 100% open-source software stack operating without paid API tiers or subscriptions.")

    add_heading_1(doc, "4.4 12-Week Agile Project Workplan")
    p_plan = (
        "The project execution follows an intensive 12-week Agile sprint schedule spanning six distinct technical phases, "
        "as summarized in Table 4.1."
    )
    add_styled_paragraph(doc, p_plan)

    add_academic_table(
        doc,
        headers=["Phase & Weeks", "Sprint Milestone", "Core Technologies", "Concrete Deliverable Artifact"],
        data=[
            ["Phase 1: Weeks 1–2", "Data Foundation & Streaming Pipeline", "Kafka, ZooKeeper, Pydantic, TimescaleDB", "Live ingestion into topic aqi_raw, Docker container on port 5433, unit tests"],
            ["Phase 2: Weeks 3–4", "Live Telemetry & Geospatial Map", "Streamlit, Folium, Plotly, Pandas", "Interactive 3-tab dashboard, CPCB gauge, Folium India bubble map, Jupyter EDA notebook"],
            ["Phase 3: Weeks 5–6", "Machine Learning & 48h Forecasting", "LightGBM, Scikit-learn, MLflow, Joblib", "Walk-forward training (RMSE 7.61), production model lgbm_aqi.pkl, 48h trajectory view"],
            ["Phase 4: Weeks 7–8", "Private AI Health Advisor (RAG)", "ChromaDB, Sentence-Transformers, Ollama", "34-chunk vector store, Ollama llama3.2 integration, zero-hallucination chat UI, 32 unit tests"],
            ["Phase 5: Weeks 9–10", "Enterprise BI & Dashboard Polish", "Power BI Desktop, TimescaleDB, Streamlit", "TimescaleDB continuous aggregates, 2-page Power BI executive report with DAX measures"],
            ["Phase 6: Weeks 11–12", "MLOps Automation & Final Defense", "Task Scheduler, Telegram Bot, Pytest", "Automated weekly retraining script, Telegram threshold alert bot, video demonstration runbook"],
        ],
        table_number="4.1",
        caption="AirSense 12-Week Agile Implementation Workplan and Milestone Deliverables",
        col_widths=[1.4, 1.7, 1.6, 2.3]
    )

def build_chapter_5(doc, helpers):
    add_chapter_title = helpers['add_chapter_title']
    add_heading_1 = helpers['add_heading_1']
    add_heading_2 = helpers['add_heading_2']
    add_styled_paragraph = helpers['add_styled_paragraph']
    add_bullet_point = helpers['add_bullet_point']
    add_callout_box = helpers['add_callout_box']
    add_academic_table = helpers['add_academic_table']

    add_chapter_title(doc, 5, "Implementation Environment")

    add_heading_1(doc, "5.1 System Specifications")
    p_sys = (
        "A critical engineering requirement of AirSense is edge feasibility: the entire platform must run concurrently on a single "
        "mid-range consumer gaming laptop without overwhelming physical memory or causing operating system instability. "
        "Table 5.1 details the physical host hardware and allocated resource budgets."
    )
    add_styled_paragraph(doc, p_sys)

    add_academic_table(
        doc,
        headers=["Hardware Subsystem", "Host Component Specification", "Allocated Workload Budget", "Operational Role"],
        data=[
            ["Physical Machine", "Acer Nitro V15 Gaming Laptop", "Dedicated host machine", "Single physical workstation execution"],
            ["Processor (CPU)", "AMD Ryzen 5 / Intel Core i5 (Hexa-core)", "Multi-threaded process execution", "Kafka, TimescaleDB, Python threads"],
            ["System Memory (RAM)", "16 GB DDR5 Dual-Channel High Speed", "Allocated across subsystems", "Peak consumption: 9.8 GB total system load"],
            ["WSL2 Memory Cap", "Virtual Machine RAM Limiter (.wslconfig)", "Strict limit: 3 GB RAM, 2 CPUs", "Prevents Docker Vmmem daemon memory ballooning"],
            ["Dedicated Graphics (GPU)", "NVIDIA GeForce RTX (4 GB / 6 GB VRAM)", "GPU CUDA Acceleration", "Accelerates Ollama 4-bit quantized neural inference"],
            ["Persistent Storage", "512 GB PCIe Gen4 NVMe Solid State Drive", "~15 GB total environment footprint", "OS, Docker images, TimescaleDB chunks, ChromaDB"],
            ["Operating System", "Microsoft Windows 11 Home (64-bit)", "Host kernel environment", "PowerShell 7, Windows Terminal, Docker Desktop"],
        ],
        table_number="5.1",
        caption="Host System Hardware Specifications and Memory Budget Allocation",
        col_widths=[1.5, 1.8, 1.5, 2.2]
    )

    add_heading_1(doc, "5.2 Programming & Runtime Environment")
    p_prog = (
        "The software architecture leverages an integrated Python 3.11 ecosystem supported by containerized services. "
        "Table 5.2 outlines the runtime frameworks, libraries, and communication protocols."
    )
    add_styled_paragraph(doc, p_prog)

    add_academic_table(
        doc,
        headers=["Software Layer", "Framework / Library", "Version Manifest", "Architectural Responsibility"],
        data=[
            ["Programming Language", "Python", "v3.11.9 (64-bit)", "Core logic across ingestion, consumer, ML, RAG, dashboard"],
            ["Message Streaming", "Apache Kafka & ZooKeeper", "v3.6.1 / Native Win", "Distributed pub-sub event streaming queue (port 9092)"],
            ["Kafka Client", "kafka-python / confluent-kafka", "v2.0.2", "High-throughput producer and consumer bindings"],
            ["Data Validation", "Pydantic", "v2.9.2", "Runtime JSON schema type validation and anomaly rejection"],
            ["Time-Series Database", "TimescaleDB / PostgreSQL", "PostgreSQL 16 / Docker", "Hypertables with automated 1-day chunking (port 5433)"],
            ["Database Connector", "SQLAlchemy & Psycopg2-binary", "v2.0.35 / v2.9.9", "Connection pooling and thread-safe SQL execution"],
            ["Machine Learning", "LightGBM", "v4.5.0", "Gradient-boosted decision tree recursive time-series regressor"],
            ["Experiment Tracking", "MLflow", "v2.16.2", "Local file-store logging of RMSE, MAE, R², and model artifacts"],
            ["Vector Embeddings", "Sentence-Transformers", "v3.1.1 (all-MiniLM-L6-v2)", "384-dimensional dense semantic text embedding generation"],
            ["Vector Database", "ChromaDB", "v0.4.x", "In-process persistent vector store with cosine distance search"],
            ["Local LLM Server", "Ollama", "v0.3.x (llama3.2:3b)", "Local 4-bit quantized neural LLM inference (port 11434)"],
            ["Web Dashboard", "Streamlit & Streamlit-Folium", "v1.38.0 / v0.23.0", "Reactive multi-page web frontend with auto-refresh"],
            ["Interactive Graphics", "Plotly Express & Graph Objects", "v5.24.1", "Hardware-accelerated CPCB gauges, trends, and forecasts"],
            ["Business Intelligence", "Power BI Desktop", "October 2026 Free Edition", "Star-schema modeling, DAX KPIs, and executive reporting"],
        ],
        table_number="5.2",
        caption="AirSense Technology Stack, Core Libraries, and Version Manifest",
        col_widths=[1.5, 1.8, 1.3, 2.4]
    )

    add_heading_1(doc, "5.3 Development, Experimentation & Testing Tools")
    p_tools = (
        "Development productivity, continuous verification, and reproducibility were maintained via a curated suite of tools:\n\n"
        "• Antigravity IDE / Visual Studio Code: Primary programming environment equipped with Python extensions, Pylance type checking, and Git integration.\n"
        "• Pytest Test Suite: Automated testing framework executing 32 unit tests across `tests/test_validate.py`, `tests/test_forecast.py`, and `tests/test_rag.py`.\n"
        "• Docker Desktop: WSL2-backed container manager hosting the TimescaleDB engine, configured with a 512 MB memory boundary.\n"
        "• PowerShell 7 & Batch Automation: Shell automation scripts (`start_demo.bat`, `run_fetcher.bat`, `start_consumer.bat`) enabling seamless cold-starts."
    )
    add_styled_paragraph(doc, p_tools)

def build_chapter_6(doc, helpers):
    add_chapter_title = helpers['add_chapter_title']
    add_heading_1 = helpers['add_heading_1']
    add_heading_2 = helpers['add_heading_2']
    add_styled_paragraph = helpers['add_styled_paragraph']
    add_bullet_point = helpers['add_bullet_point']
    add_callout_box = helpers['add_callout_box']
    add_figure_placeholder = helpers['add_figure_placeholder']
    add_academic_table = helpers['add_academic_table']

    add_chapter_title(doc, 6, "Dataset And Visualization")

    add_heading_1(doc, "6.1 Dataset Gathering")
    p_data1 = (
        "AirSense continuously acquires ambient air quality telemetry from the World Air Quality Index (WAQI) Open Data API, "
        "which federates verified ground-truth sensor readings from the Central Pollution Control Board (CPCB) of India and state "
        "pollution control committees. To capture varied geographical, industrial, and meteorological profiles, six target cities "
        "across western and northern India were selected."
    )
    add_styled_paragraph(doc, p_data1)

    add_academic_table(
        doc,
        headers=["City Slug", "Display Name", "State", "Latitude", "Longitude", "Primary Pollution Profile"],
        data=[
            ["ahmedabad", "Ahmedabad", "Gujarat", "23.0225° N", "72.5714° E", "Industrial chemical, textile clusters, heavy urban vehicular traffic"],
            ["surat", "Surat", "Gujarat", "21.1702° N", "72.8311° E", "Textile dying, diamond processing emissions, coastal humidity inversion"],
            ["rajkot", "Rajkot", "Gujarat", "22.3039° N", "70.8022° E", "Engineering workshops, diesel engine manufacturing, semi-arid dust"],
            ["gandhinagar", "Gandhinagar", "Gujarat", "23.2156° N", "72.6369° E", "Administrative green capital, regional background reference station"],
            ["delhi", "Delhi (NCR)", "Delhi", "28.6139° N", "77.2090° E", "Extreme winter thermal inversion, vehicular density, regional stubble smoke"],
            ["mumbai", "Mumbai", "Maharashtra", "19.0760° N", "72.8777° E", "High vehicular density, major sea port, coastal atmospheric cleansing"],
        ],
        table_number="6.1",
        caption="Target Monitored Urban Hubs and Ground-Level Sensor Geospatial Coordinates",
        col_widths=[1.1, 1.2, 1.0, 1.0, 1.0, 2.7]
    )

    p_data2 = (
        "In addition to real-time hourly polling, a rigorous 45-day historical dataset comprising 6,486 hourly records across all six cities "
        "was constructed and backfilled into TimescaleDB. This multi-city dataset captures essential diurnal rhythms, weekend-versus-weekday "
        "industrial variances, and meteorological stagnation events required for robust machine learning training."
    )
    add_styled_paragraph(doc, p_data2)

    add_heading_1(doc, "6.2 Data Preprocessing & Validation")
    p_prep1 = (
        "Raw environmental telemetry frequently exhibits sensor dropouts, transmission errors, negative concentration artifacts, and "
        "out-of-order timestamps. To ensure that contaminated data never pollutes the analytical database, the consumer implements strict "
        "Pydantic v2 data validation schemas (`consumer/validate.py`)."
    )
    add_styled_paragraph(doc, p_prep1)

    add_bullet_point(doc, "Boundary Assertion Rules:", "AQI must lie strictly within [0, 999]. Particulate and gaseous pollutants (PM2.5, PM10, NO2, SO2, CO, O3) must be non-negative (>= 0.0). Latitude and longitude must conform to valid WGS84 geographic boundaries.")
    add_bullet_point(doc, "Temporal Monotonicity & Timezone Synchronization:", "All incoming local timestamps are converted and standardized into UTC ISO-8601 strings. Timestamps in the future (> current system time + 5 minutes clock drift) are strictly rejected.")
    add_bullet_point(doc, "Dead-Letter Audit Logging:", "Any incoming message failing Pydantic schema validation is caught, logged with explicit error details to an audit log file, and quarantined without interrupting consumer streaming.")

    p_feat = (
        "To prepare the time-series stream for gradient boosting forecasting, a leakage-free feature engineering pipeline "
        "(`ml/training/features.py`) transforms the raw measurements into 18 descriptive features, detailed in Table 6.2."
    )
    add_styled_paragraph(doc, p_feat)

    add_academic_table(
        doc,
        headers=["Feature Category", "Feature Name", "Mathematical Formulation", "Physical / Analytical Rationale"],
        data=[
            ["Calendar Time", "hour", "time.dt.hour ∈ [0, 23]", "Captures daily urban activity schedule"],
            ["Calendar Time", "day_of_week", "time.dt.dayofweek ∈ [0, 6]", "Captures commercial versus weekend emission shifts"],
            ["Calendar Time", "is_weekend", "1 if day_of_week >= 5 else 0", "Binary indicator for industrial and traffic reduction"],
            ["Cyclical Temporal", "sin_hour, cos_hour", "sin(2π*h/24), cos(2π*h/24)", "Continuous circular transformation ensuring 23:00 aligns with 00:00"],
            ["Cyclical Temporal", "sin_day, cos_day", "sin(2π*d/7), cos(2π*d/7)", "Continuous circular transformation across weekly cycle"],
            ["Autoregressive Lag", "aqi_lag_1h", "AQI(t - 1)", "Immediate preceding hour momentum (highest feature importance)"],
            ["Autoregressive Lag", "aqi_lag_2h, 3h", "AQI(t - 2), AQI(t - 3)", "Short-term temporal trajectory and rate of change"],
            ["Autoregressive Lag", "aqi_lag_24h", "AQI(t - 24)", "Diurnal persistence (air quality at same hour yesterday)"],
            ["Autoregressive Lag", "aqi_lag_168h", "AQI(t - 168)", "Weekly seasonality (same hour on the same day last week)"],
            ["Rolling Statistics", "aqi_rolling_mean_6h", "mean(AQI(t-1 : t-6))", "Medium-term smoothing capturing stagnation or dispersal"],
            ["Rolling Statistics", "aqi_rolling_std_6h", "std(AQI(t-1 : t-6))", "Short-term volatility and atmospheric instability index"],
            ["Rolling Statistics", "aqi_rolling_mean_24h", "mean(AQI(t-1 : t-24))", "24-hour baseline moving average removing daily noise"],
        ],
        table_number="6.2",
        caption="Engineered Feature Dictionary and Mathematical Transformations for ML Forecasting",
        col_widths=[1.4, 1.6, 2.0, 2.0]
    )

    add_heading_1(doc, "6.3 Exploratory Data Analysis & Visualizations")
    p_eda = (
        "Prior to model training, exhaustive exploratory data analysis (EDA) was conducted across the 6,486 historical readings, "
        "yielding profound empirical insights into Indian urban atmospheric dynamics."
    )
    add_styled_paragraph(doc, p_eda)

    add_heading_2(doc, "6.3.1 Live Urban League Ranking & CPCB Gauges")
    p_v1 = (
        "The primary dashboard view provides real-time situational awareness. KPI cards display current AQI and CPCB risk badges "
        "across all six cities simultaneously. An interactive Plotly semicircular gauge renders the selected city's exact index value, "
        "color-coded according to official CPCB NAAQS spectrum standards."
    )
    add_styled_paragraph(doc, p_v1)
    add_figure_placeholder(doc, "6.1", "AirSense Real-Time Telemetry Dashboard & CPCB Dynamic Gauge UI", 
                           "Interactive Streamlit interface showing city selector, CPCB gauge, health card, and granular pollutant breakdown bars.")

    add_heading_2(doc, "6.3.2 Folium Geospatial Interactive India Air Map")
    p_v2 = (
        "To provide intuitive spatial context, AirSense integrates Folium within Streamlit. Ground-level monitoring stations are "
        "rendered as pulsing geographic bubble markers positioned at precise WGS84 coordinates. Marker color dynamically transitions "
        "from green (Good) to dark purple (Severe) based on live sensor telemetry, with click popups exposing granular pollutant data."
    )
    add_styled_paragraph(doc, p_v2)
    add_figure_placeholder(doc, "6.2", "Interactive Folium Geospatial Air Quality Bubble Map of India", 
                           "India national overview depicting air quality markers across Delhi, Ahmedabad, Surat, Rajkot, Gandhinagar, and Mumbai.")

    add_heading_2(doc, "6.3.3 Diurnal Rhythm Analysis (Peak Rush-Hour Inversion)")
    p_v3 = (
        "Cross-city diurnal profiling reveals a pronounced bimodal distribution in urban particulate matter. Concentrations exhibit "
        "a steep morning spike between 07:00 and 10:00 AM (morning rush hour combined with shallow nocturnal boundary layer), "
        "followed by afternoon dispersal due to solar convective mixing, and a secondary nocturnal peak from 19:00 to 23:00 PM."
    )
    add_styled_paragraph(doc, p_v3)
    add_figure_placeholder(doc, "6.3", "Diurnal Pattern Analysis Across Indian Metros Showing Rush-Hour Inversion", 
                           "24-hour diurnal curves comparing nocturnal atmospheric stagnation against afternoon solar convective dispersal.")

    add_heading_2(doc, "6.3.4 PM2.5 to PM10 Combustion Source Diagnostic Ratios")
    p_v4 = (
        "The dimensionless ratio of PM2.5 to PM10 serves as an established chemical tracer for identifying emission sources. "
        "Ratios exceeding 0.65 indicate a predominance of fine combustion aerosols (vehicular exhaust, industrial fuel burning, biomass smoke). "
        "Conversely, ratios below 0.45 reflect mechanical crustal dust resuspension and construction earthworks. AirSense computes "
        "this ratio continuously, diagnosing combustion dominance across Delhi and Ahmedabad versus dust dominance in Rajkot."
    )
    add_styled_paragraph(doc, p_v4)
    add_figure_placeholder(doc, "6.4", "PM2.5 to PM10 Combustion Source Diagnostic Ratios Across Monitored Hubs", 
                           "Scatter and bar diagnostics identifying fine particulate combustion dominance versus mechanical crustal dust.")

print("[INFO] Chapters 4, 5, 6 builder module loaded.")
