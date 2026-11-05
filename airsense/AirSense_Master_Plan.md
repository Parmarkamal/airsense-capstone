# 🌬️ AirSense — The Definitive Master Plan
### Real-Time AQI Forecasting & Private GenAI Health Advisor
> *Built 100% on a single 16 GB laptop — no cloud, no credit card, no ZooKeeper*

**Document Version:** 1.0  
**Last Updated:** July 2026  
**Author:** MSc BI & Analytics — Capstone Project  
**Machine:** Acer Nitro V15 (16 GB RAM, Windows 11, Dedicated GPU)  
**Total Budget:** ₹0 (optional ₹2,000–2,500 for physical sensor later)

---

## 📋 TABLE OF CONTENTS

1. [Project Identity & Vision](#1-project-identity--vision)
2. [The Real-World Problem](#2-the-real-world-problem)
3. [Technology Stack (Verified)](#3-technology-stack-verified)
4. [Hardware Reality & RAM Budget](#4-hardware-reality--ram-budget)
5. [System Architecture](#5-system-architecture)
6. [Module-by-Module Build Plan (12 Weeks)](#6-module-by-module-build-plan-12-weeks)
7. [Database Design (Deep Dive)](#7-database-design-deep-dive)
8. [ML Forecasting (Deep Dive)](#8-ml-forecasting-deep-dive)
9. [RAG Pipeline (Deep Dive)](#9-rag-pipeline-deep-dive)
10. [Kafka Setup (Deep Dive)](#10-kafka-setup-deep-dive)
11. [Streamlit Dashboard Design](#11-streamlit-dashboard-design)
12. [MLOps & Experiment Tracking](#12-mlops--experiment-tracking)
13. [Data Integrity, Ethics & API Compliance](#13-data-integrity-ethics--api-compliance)
14. [Demo-Day Resilience & Backup Strategy](#14-demo-day-resilience--backup-strategy)
15. [Defense Q&A (Comprehensive)](#15-defense-qa-comprehensive)
16. [Project Folder Structure](#16-project-folder-structure)
17. [Environment & Dependencies](#17-environment--dependencies)
18. [Enhancements & Future Scope](#18-enhancements--future-scope)
19. [Skills You Will Master](#19-skills-you-will-master)
20. [Glossary of Key Terms](#20-glossary-of-key-terms)

---

## 1. PROJECT IDENTITY & VISION

| Attribute | Details |
|-----------|---------|
| **Project Name** | AirSense |
| **Tagline** | *"Know the air. Protect your health."* |
| **Pitch** | A laptop-only system that pulls live air-quality data, forecasts the next 24-48 hours, and lets a user ask a local, private AI "Is it safe for me to go outside today?" grounded in real WHO/CPCB health guidelines. |
| **Domain** | Data Engineering + Data Science + Generative AI |
| **Target Machine** | Acer Nitro V15 (16 GB RAM, Windows 11, dedicated GPU — RTX 2050 or higher) |
| **Time Budget** | 12 weeks, 7-10 hours/week (~84-120 total hours) |
| **Cost** | Rs.0 for the core software |
| **Privacy Model** | 100% local — no data leaves your laptop |
| **Target Users** | Urban Indian residents, students, health-conscious individuals, policy researchers |

### What AirSense Actually Does (User Perspective)

A normal person opens AirSense and:

1. **Sees a live AQI gauge** for their city — color-coded with a human-readable label like "Unhealthy — avoid outdoor activity."
2. **Views a 24-48 hour forecast** — a clear chart predicting whether tomorrow will be better or worse.
3. **Types in plain English:** "I have asthma and want to jog tomorrow at 7 AM. Is it safe?"
4. **Gets a personalised, grounded answer** backed by official WHO/CPCB health guidelines — not generic chatbot hallucination.
5. **Browses historical trends** (seasonal spikes, Diwali pollution, monsoon patterns) in an executive-style Power BI report.

**Everything happens on the laptop.** Questions never reach the cloud. The AI never gives a medical diagnosis.

---

## 2. THE REAL-WORLD PROBLEM

### Scale of Air Pollution in India

- Air pollution kills an estimated **7 million people per year globally** (WHO, 2024).
- India has **14 of the world's 20 most polluted cities** (IQAir World Air Quality Report).
- Average Indian city regularly sees AQI > 150 ("Unhealthy") — sometimes 300+ ("Hazardous") around festivals and winter.
- Sensitive groups (asthma, COPD, children, elderly) face **3-5x higher mortality risk** during high-AQI days.

### The Information Gap

Despite this, the average person:
- Only sees a raw number (AQI = 187) with no context.
- Does not know if 187 is dangerous for them specifically.
- Has no idea if conditions will improve in the next 12 hours.
- Cannot ask intelligent follow-up questions.

### How AirSense Closes the Gap

| Problem | AirSense Solution |
|---------|-------------------|
| Raw AQI number is meaningless | Color-coded gauge with plain-English label |
| No future outlook | ML-powered 24-48h forecast chart |
| Generic health advice | RAG-grounded AI advisor with user-specific context |
| Cloud services require subscriptions | Fully local — zero recurring cost |
| Data privacy concerns | All queries stay on the user's machine |

---

## 3. TECHNOLOGY STACK (VERIFIED)

> Every tool here is **free, local, tested on Windows 11**, and fits within 16 GB RAM with the configuration described in Section 4.

### 3.1 Core Technology Choices

| Layer | Technology | Version | Why This Choice |
|-------|-----------|---------|-----------------|
| **Live Data** | WAQI/AQICN API | REST API, free token | 1000+ req/day free; covers 1,000+ Indian cities; standard for air quality research |
| **Historical Data** | data.gov.in (CPCB) + Kaggle Indian AQI | CSV datasets | Required for model training — WAQI ToS restricts redistribution/caching |
| **Message Broker** | Apache Kafka 4.x | 4.0+ | ZooKeeper completely removed in 4.0; KRaft mode = single process, lower memory |
| **Stream Processing** | Python consumer (kafka-python) | 2.x | Lightweight; no heavy framework needed for a single-city pipeline |
| **Storage** | TimescaleDB | 2.x (Docker) | PostgreSQL extension optimised for time-series; hypertables, continuous aggregates |
| **Vector DB** | ChromaDB | 0.4+ | In-process, local, persistent; zero extra RAM; perfect for RAG on ~50 guideline pages |
| **Data Validation** | Pydantic | v2 | Fast, Pythonic schema validation; lighter than Great Expectations for this scale |
| **ML Model** | LightGBM (primary) | 4.x | Native Windows install; trains in seconds; excellent for tabular time-series |
| **ML Model Alt** | Prophet (optional) | via conda only | Comparison purposes; known Windows compiler issues — only via conda |
| **Experiment Tracking** | MLflow | 2.x | Local file store; mlflow ui on demand; logs RMSE per retrain |
| **Orchestration** | Windows Task Scheduler | Built-in | No extra service; scheduled Python scripts for hourly fetch + weekly retrain |
| **Dashboard** | Streamlit | 1.3+ | Python-native; rapid prototyping; supports Plotly, chat UI, live refresh |
| **BI Reporting** | Power BI Desktop | Latest (free) | Connects to TimescaleDB; professional DAX measures; no license needed |
| **Operational Monitoring** | Grafana | 10.x (Docker, optional) | Live gauge panels; connects to TimescaleDB; nice-to-have for the demo |
| **Local LLM** | Ollama + phi3:mini (Q4 quantised) | Latest | ~2.5 GB VRAM; fits every Nitro V15 GPU variant; GPU-accelerated on Windows |
| **AI Framework** | LangChain | 0.2+ | RAG chains, retriever tools, agent orchestration |
| **Embedding Model** | all-MiniLM-L6-v2 | via sentence-transformers | Runs fully offline after one-time download; 384-dim embeddings |
| **Containerisation** | Docker Compose (TimescaleDB + Grafana only) | Docker Desktop | Kafka, Ollama, Streamlit run natively — saves critical RAM |

### 3.2 Why NOT These Alternatives

| Alternative | Why Rejected |
|-------------|-------------|
| Apache Spark | Overkill for single-machine; 4+ GB RAM overhead; no benefit at this data volume |
| Apache Flink | Same reason as Spark; complex setup |
| ZooKeeper | Removed entirely from Kafka 4.x; do not install |
| GPT-4 / Claude API | Sends user data to cloud; costs money; not private; defeats the privacy goal |
| PostgreSQL (plain) | TimescaleDB is a superset; hypertables and continuous aggregates are critical for time-series |
| TensorFlow / PyTorch | Unnecessary for tabular data; LightGBM is faster and simpler |
| Kubernetes | Way too complex for a single-laptop deployment |
| Great Expectations | Heavier than Pydantic for this scale; adds ~200MB+; not worth it |

---

## 4. HARDWARE REALITY & RAM BUDGET

### 4.1 Know Your GPU

Check yours via: Task Manager -> Performance -> GPU, or type `dxdiag` in Run dialog.

| GPU Variant | VRAM | phi3:mini Q4 (~2.5 GB) | LLaVA Vision (~5-6 GB) |
|-------------|------|------------------------|------------------------|
| RTX 2050 | 4 GB | Fits safely | Skip this |
| RTX 3050 | 6 GB | Fits comfortably | Borderline |
| RTX 4050 | 6 GB | Fits comfortably | Borderline |
| RTX 5050/5060 | 8 GB | Plenty of headroom | Works |

**Rule:** Use phi3:mini. It answers health questions excellently and fits every configuration.

### 4.2 The Critical WSL2 Memory Fix

**The biggest hidden risk:** Docker Desktop's WSL2 backend defaults to consuming **50% of host RAM = 8 GB**. This will crash your system.

**Fix — Create this file before touching Docker:**

```
File path: C:\Users\<YourName>\.wslconfig
```

```ini
[wsl2]
memory=3GB
processors=2

[experimental]
autoMemoryReclaim=gradual
```

After saving:
```powershell
wsl --shutdown
# Then restart Docker Desktop from the system tray
```

This caps WSL2 at 3 GB regardless of what Docker containers request.

### 4.3 Complete RAM Budget (Everything Running)

| Component | RAM Estimate |
|-----------|-------------|
| Windows 11 + background apps | 3.5 GB |
| WSL2 VM (capped) — TimescaleDB + Grafana | <= 3.0 GB |
| Kafka 4.x (KRaft, heap limited to 512 MB) | ~0.8 GB |
| Ollama + phi3:mini loaded | ~1.0-1.5 GB system + ~2.5 GB VRAM |
| Python (Streamlit + Consumer + LangChain) | 1.5-2.5 GB |
| VS Code + Chrome (a few tabs) | 1.5-2.5 GB |
| **Total Peak (Demo Mode)** | **~11.5-13.5 GB** |

This fits within 16 GB with 2.5-4.5 GB headroom.

### 4.4 Kafka Heap Configuration

Always set this BEFORE starting Kafka:

```powershell
# Windows — set environment variable before starting Kafka
$env:KAFKA_HEAP_OPTS = "-Xmx512m -Xms512m"
bin\windows\kafka-server-start.bat config\kraft\server.properties
```

### 4.5 Practical RAM Management Tips

1. Do not run everything constantly during development. Each module is developed in isolation.
2. Write a `start_demo.bat` that launches services in sequence with sleep intervals.
3. Before the live LLM chat demo: close Power BI, Grafana, extra Chrome tabs.
4. Increase Windows pagefile to 8-16 GB as a safety net (prevents crashes, just causes slowdown).
5. Set pagefile: System Properties -> Advanced -> Performance -> Virtual Memory -> Custom size: Initial = 8192 MB, Max = 16384 MB.

---

## 5. SYSTEM ARCHITECTURE

### 5.1 High-Level Architecture

```
+------------------------------------------------------------------+
|                  YOUR ACER NITRO V15 (16 GB RAM)                 |
|                                                                  |
|  LAYER 1: DATA INGESTION                                         |
|  [Task Scheduler] --hourly--> [fetch_aqi.py]                     |
|       |                            |                             |
|       |                     WAQI REST API (token from .env)      |
|       |                            | JSON payload                |
|       +---------------------- Kafka Topic: "aqi_raw"             |
|                                    |                             |
|  LAYER 2: APACHE KAFKA 4.x (KRaft, no ZooKeeper, heap 512MB)    |
|                                    |                             |
|  LAYER 3: STREAM CONSUMER (consumer.py)                          |
|     |- Pydantic validation (range checks)                        |
|     |- Deduplication                                             |
|     +- INSERT into TimescaleDB                                   |
|                                    |                             |
|  LAYER 4: TIMESCALEDB (Docker, WSL2 capped, port 5432)           |
|     |- aqi_readings (hypertable, 1-day chunks)                   |
|     |- aqi_forecasts (48h model output)                          |
|     |- stations (metadata)                                       |
|     +- aqi_hourly_avg (continuous aggregate)                     |
|            |                       |                             |
|  LAYER 5:  |            LAYER 7: RAG PIPELINE                   |
|  ML ENGINE |            [PDF Loader] -> [Text Chunker]           |
|  [Task Scheduler weekly]     -> [all-MiniLM-L6-v2]              |
|  LightGBM retrain            -> [ChromaDB (local)]              |
|  MLflow tracking             -> [LangChain Retriever]           |
|  -> aqi_forecasts                                               |
|            |                       |                             |
|  LAYER 6: STREAMLIT DASHBOARD (port 8501)                        |
|     |- Live AQI Gauges (Plotly, colorblind-safe)                 |
|     |- 24-hour historical line chart                             |
|     |- 48-hour forecast (dashed line)                            |
|     |- Health Chat (RAG + Ollama phi3:mini)                      |
|     |- Insights Tab (EDA visualisations)                         |
|     +- Medical Disclaimer Banner                                 |
|                                                                  |
|  LAYER 8: OLLAMA (native, port 11434) -- phi3:mini, GPU accel.  |
|  LAYER 9: GRAFANA (Docker optional) -- live ops dashboards       |
|  POWER BI DESKTOP -- historical reports, DAX measures            |
+------------------------------------------------------------------+
All communication via localhost. No cloud calls (except WAQI fetch).
```

### 5.2 Data Flow Summary

```
WAQI API (internet)
    |
    v (hourly, via fetch_aqi.py)
Kafka topic: aqi_raw
    |
    v (real-time consumer)
Pydantic validation
    |
    +-- VALID --> TimescaleDB.aqi_readings
    +-- INVALID --> logged to error_log.txt (not dropped silently)

TimescaleDB.aqi_readings
    |
    +-- Streamlit (live read, every 30s refresh)
    +-- LightGBM retrain (weekly, Task Scheduler)
    +-- Power BI (daily refresh)

LightGBM model
    |
    +-- TimescaleDB.aqi_forecasts
            |
            +-- Streamlit (forecast chart)

User query (Streamlit chat)
    |
    +-- ChromaDB retriever (top-k guideline chunks)
    +-- TimescaleDB (current AQI for context)
    +-- Ollama phi3:mini
            |
            +-- Grounded answer with citations
```

---

## 6. MODULE-BY-MODULE BUILD PLAN (12 WEEKS)

### Week 1 — Data Ingestion & Kafka Setup
**Goal:** Live AQI data flows into Kafka every hour.

#### Tasks

- [ ] **WAQI Token Registration**
  - Visit `https://aqicn.org/data-platform/token/`
  - Register with email — token arrives instantly
  - Store token in `.env` file: `WAQI_TOKEN=your_token_here`
  - Never commit `.env` to Git

- [ ] **Download & Configure Kafka 4.x**
  - Download from `https://kafka.apache.org/downloads`
  - Unzip to `C:\kafka\` (short path avoids Windows path-length issues)
  - Kafka 4.x uses KRaft — NO ZooKeeper needed

- [ ] **Initialize KRaft Storage (one-time setup)**
  ```powershell
  $KAFKA_CLUSTER_ID = & bin\windows\kafka-storage.bat random-uuid
  bin\windows\kafka-storage.bat format -t $KAFKA_CLUSTER_ID -c config\kraft\server.properties
  ```

- [ ] **Start Kafka Broker**
  ```powershell
  $env:KAFKA_HEAP_OPTS = "-Xmx512m -Xms512m"
  bin\windows\kafka-server-start.bat config\kraft\server.properties
  ```

- [ ] **Create Kafka Topic**
  ```powershell
  bin\windows\kafka-topics.bat --create `
    --topic aqi_raw `
    --bootstrap-server localhost:9092 `
    --partitions 1 `
    --replication-factor 1
  ```

- [ ] **Write `fetch_aqi.py`** (see Section 16 for full code)

- [ ] **Schedule in Windows Task Scheduler**
  - Action: `python C:\path\to\airsense\ingestion\fetch_aqi.py`
  - Trigger: Daily, repeat every 1 hour
  - Condition: Run only if network is available

#### Checkpoint
Topic `aqi_raw` receives new messages every hour. Verify:
```powershell
bin\windows\kafka-console-consumer.bat --topic aqi_raw --from-beginning --bootstrap-server localhost:9092 --max-messages 3
```

---

### Week 2 — Stream Processing & TimescaleDB Storage
**Goal:** Validated, clean data lands in TimescaleDB automatically.

#### Tasks

- [ ] Create `.wslconfig` (Section 4.2) — do this FIRST before Docker
- [ ] Write `docker-compose.yml` with TimescaleDB (512MB mem limit, port 5432)
- [ ] Create database schema with `create_hypertable()`
- [ ] Write Kafka Consumer with Pydantic validation model
- [ ] Verify rows appear: `SELECT COUNT(*), city FROM aqi_readings GROUP BY city;`

#### Key: Pydantic Validation Model

```python
from pydantic import BaseModel, field_validator
from datetime import datetime, timezone

class AQIReading(BaseModel):
    time: datetime
    station_id: str
    city: str
    aqi: float | None
    pm25: float | None

    @field_validator('aqi')
    @classmethod
    def aqi_in_range(cls, v):
        if v is not None and not (0 <= v <= 999):
            raise ValueError(f"AQI out of range: {v}")
        return v

    @field_validator('time')
    @classmethod
    def time_not_future(cls, v):
        if v > datetime.now(timezone.utc):
            raise ValueError(f"Timestamp in the future: {v}")
        return v
```

#### Checkpoint
Clean, validated AQI data accumulates in TimescaleDB automatically.

---

### Week 3 — First Streamlit Dashboard
**Goal:** A live, visually appealing AQI visualisation.

#### AQI Color Palette (Colorblind-Safe)

```python
AQI_CATEGORIES = {
    (0, 50):    {"label": "Good",                    "color": "#009966"},
    (51, 100):  {"label": "Moderate",                "color": "#FFDE33"},
    (101, 150): {"label": "Unhealthy for Sensitive", "color": "#FF9933"},
    (151, 200): {"label": "Unhealthy",               "color": "#CC0033"},
    (201, 300): {"label": "Very Unhealthy",          "color": "#660099"},
    (301, 999): {"label": "Hazardous",               "color": "#7E0023"}
}
```

#### Checkpoint
Dashboard loads at `http://localhost:8501` with live gauges and charts.

---

### Week 4 — Exploratory Data Analysis
**Goal:** Generate insights for your capstone report and defense.

#### Key SQL Analyses

```sql
-- Diurnal Pattern (AQI by hour of day)
SELECT EXTRACT(HOUR FROM time) AS hour_of_day, AVG(aqi) AS avg_aqi, city
FROM aqi_readings GROUP BY hour_of_day, city ORDER BY city, hour_of_day;

-- Weekday vs Weekend
SELECT
  CASE WHEN EXTRACT(DOW FROM time) IN (0, 6) THEN 'Weekend' ELSE 'Weekday' END AS day_type,
  city, AVG(aqi) AS avg_aqi
FROM aqi_readings GROUP BY day_type, city;

-- AQI Spike Detection (Z-score)
WITH stats AS (
  SELECT city, AVG(aqi) AS mean_aqi, STDDEV(aqi) AS std_aqi FROM aqi_readings GROUP BY city
)
SELECT r.time, r.city, r.aqi, (r.aqi - s.mean_aqi) / NULLIF(s.std_aqi, 0) AS z_score
FROM aqi_readings r JOIN stats s ON r.city = s.city
WHERE ABS((r.aqi - s.mean_aqi) / NULLIF(s.std_aqi, 0)) > 2.5
ORDER BY z_score DESC;
```

#### Checkpoint
5+ visualisations in Jupyter notebook. Best 3 added to Streamlit "Insights" tab.

---

### Week 5 — Forecasting Model Training
**Goal:** Predict AQI for the next 24-48 hours.

#### Critical Rule: Time-Based Split ONLY

Never use random 80/20 split for time-series. Always split chronologically:
```
Training set (weeks 1-3) | Validation (week 4) | Test held-out (week 5)
                         ^ cutoff_date
```

#### Feature Engineering Table

| Feature | Description | Why Useful |
|---------|-------------|-----------|
| `hour` | 0-23 | Diurnal AQI patterns (peak at rush hour) |
| `day_of_week` | 0-6 | Weekend vs weekday differences |
| `month` | 1-12 | Seasonal variations (winter smog) |
| `aqi_lag_1h` | AQI 1 hour ago | Strong autocorrelation |
| `aqi_lag_24h` | AQI 24 hours ago | Same hour, previous day |
| `aqi_lag_168h` | AQI 1 week ago | Same hour, previous week |
| `aqi_rolling_6h` | 6-hour rolling mean | Short-term trend |
| `aqi_rolling_24h` | 24-hour rolling mean | Baseline level |
| `is_weekend` | Binary 0/1 | Behavioural difference |

#### MLflow Logging Pattern

```python
with mlflow.start_run(run_name="lgbm_weekly_retrain"):
    mlflow.log_params({"n_estimators": 500, "learning_rate": 0.05, "max_depth": 6})
    # Train...
    # Evaluate...
    mlflow.log_metrics({"rmse": rmse, "mae": mae})
    mlflow.lightgbm.log_model(model, "lgbm_model")
```

#### Checkpoint
Model RMSE < 30 AQI units. `aqi_forecasts` table has 24+ rows. MLflow UI shows the run.

---

### Week 6 — Forecast Integration in Dashboard
**Goal:** Users can see where AQI is headed.

```python
# Combine historical + forecast in one Plotly chart
fig.add_trace(go.Scatter(
    x=historical_df["time"], y=historical_df["aqi"],
    name="Actual AQI", line=dict(color="#0077B6", width=2)
))
fig.add_trace(go.Scatter(
    x=forecast_df["forecast_for"], y=forecast_df["predicted_aqi"],
    name="Forecast", line=dict(color="#FF6B35", width=2, dash="dash")
))
```

#### Checkpoint
Chart clearly shows historical data transitioning to dashed forecast line.

---

### Week 7 — RAG Setup: Health Guidelines & Vector DB
**Goal:** Build an offline knowledge base from WHO/CPCB documents.

#### What is RAG (Retrieval-Augmented Generation)?

Without RAG: LLM gives generic/hallucinated answer from training data.

With RAG: System searches ChromaDB for top-3 relevant WHO/CPCB chunks -> injects them into the prompt -> LLM answers using real, sourced, official content.

#### Document Sources

| Document | Key Content |
|----------|-------------|
| WHO Air Quality Guidelines 2021 | PM2.5/PM10 limits, health impact thresholds |
| CPCB National Ambient Air Quality Standards | Indian legal AQI breakpoints |
| CPCB AQI Calculator & Guidance | Category definitions, health messages |

#### Chunking Strategy

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Chunk size | 500 tokens | Long enough for context; short enough for precision |
| Overlap | 50 tokens | Prevents context loss at chunk boundaries |
| Splitter | RecursiveCharacterTextSplitter | Respects paragraph/sentence boundaries |
| Embedding model | all-MiniLM-L6-v2 | 384-dim, fast, runs offline |

#### Checkpoint
Retrieval test: query "PM2.5 safe limit for children with asthma" returns relevant WHO chunks.

---

### Week 8 — LangChain Agent & Safe Health Chat
**Goal:** An AI advisor grounded in real health guidelines.

#### System Prompt (The Safety Layer)

```
You are AirSense Health Advisor.

STRICT RULES:
1. ONLY use information from the provided documents and current AQI data.
2. NEVER give a medical diagnosis or prescribe treatment.
3. ALWAYS end every response with: "Please consult a qualified doctor for personal medical decisions."
4. ALWAYS cite the source document and section for any health claim.
5. If the provided documents do not contain enough information, say so explicitly.
6. Do NOT make up statistics or thresholds not found in the documents.
```

#### Tools the LangChain Agent Has

1. `get_current_aqi` — calls psycopg2, returns current AQI for a city from TimescaleDB
2. `search_health_guidelines` — calls ChromaDB retriever, returns relevant guideline chunks

#### Kill-Switch Pattern

```python
ai_enabled = st.sidebar.toggle("Enable AI Health Advisor", value=True)
if ai_enabled:
    st.chat_input("Ask a health question...")
else:
    st.info("AI Advisor is disabled. Toggle on in the sidebar to enable.")
```

#### Checkpoint
Ask: "I have asthma. Delhi AQI is 180. Can I exercise outdoors?"
Response must: cite a specific WHO/CPCB document + give clear guidance + end with doctor disclaimer.

---

### Week 9 — Chat Integration, Kill-Switch & UI Polish
**Goal:** Unified, professional application.

#### App Tabs Structure
- Home Live: Gauges, current AQI, city selector
- Trends: 24h historical chart
- Forecast: 48h prediction chart
- Insights: EDA patterns, rankings, spikes
- Health Advisor: RAG chat with kill-switch
- About: Disclaimer, attributions, tech stack

#### Mandatory Disclaimer Banner

```python
st.warning(
    "MEDICAL DISCLAIMER: AirSense is an educational tool, not a medical device. "
    "Health advice is AI-generated and based on WHO/CPCB guidelines. "
    "Always consult a qualified healthcare professional before making medical decisions. "
    "Your questions and data never leave this device."
)
```

#### Checkpoint
Full app runs end-to-end. Kill-switch works. Disclaimer is visible on every page.

---

### Week 10 — Power BI & Grafana (Optional but Impressive)
**Goal:** Executive-grade reporting.

#### Key DAX Measures

```dax
// AQI Category Classification
AQI Category =
SWITCH(
    TRUE(),
    [Avg AQI] <= 50,  "Good",
    [Avg AQI] <= 100, "Moderate",
    [Avg AQI] <= 150, "Unhealthy for Sensitive Groups",
    [Avg AQI] <= 200, "Unhealthy",
    [Avg AQI] <= 300, "Very Unhealthy",
    "Hazardous"
)

// City AQI Ranking (worst = rank 1)
City Rank = RANKX(ALL('aqi_hourly_avg'[city]), [Avg AQI], , DESC)
```

#### Checkpoint
Two-page Power BI report: Executive Summary + Detailed City View.

---

### Week 11 — MLOps Automation
**Goal:** Model automatically improves over time.

#### Champion-Challenger Logic

```python
# Load current production RMSE
with open("ml/production/metrics.json") as f:
    production_rmse = json.load(f).get("rmse", float("inf"))

# Train new model
new_model, new_rmse = train_lgbm_on_latest_data()

if new_rmse < production_rmse:
    # Promote challenger to champion
    shutil.copy("ml/staging/lgbm_aqi.pkl", "ml/production/lgbm_aqi.pkl")
    print(f"New model promoted: RMSE {new_rmse:.2f} < {production_rmse:.2f}")
else:
    print(f"Production model retained: RMSE {production_rmse:.2f} <= {new_rmse:.2f}")
```

#### Checkpoint
Weekly Task Scheduler triggers retraining. MLflow shows multiple runs. Model auto-promoted when better.

---

### Week 12 — Stress Test, Documentation & Demo Prep
**Goal:** A bulletproof, documented, demo-ready system.

#### Stress Test Checklist
- [ ] Run everything for 24 consecutive hours
- [ ] Monitor RAM via Task Manager — ensure no memory leaks
- [ ] Confirm consumer reconnects after Kafka restart
- [ ] Test all 3 backup scenarios from Section 14
- [ ] Verify WAQI attribution appears in every app page footer

#### README Must Include
1. Architecture diagram
2. Prerequisites and setup steps
3. `.wslconfig` instruction
4. How to start all services (`start_demo.bat`)
5. Demo walkthrough script
6. Known limitations
7. Data source attributions

---

## 7. DATABASE DESIGN (DEEP DIVE)

### 7.1 Why TimescaleDB Over Plain PostgreSQL

| Feature | PostgreSQL | TimescaleDB |
|---------|-----------|-------------|
| Time-series optimisation | None | Automatic chunking by time |
| Query speed (millions of rows) | Degrades | Stays fast via chunk exclusion |
| Continuous aggregates | Manual materialised views | Automatic, policy-driven refresh |
| Compression | None | Up to 95% compression for old data |
| Retention policies | Manual | drop_chunks policy |
| API compatibility | SQL | SQL (superset — fully compatible) |

### 7.2 Hypertable Chunk Strategy

When you run `create_hypertable('aqi_readings', 'time', chunk_time_interval => INTERVAL '1 day')`:
- TimescaleDB creates a new physical chunk (internal table) every day
- Queries for "last 24 hours" only scan 1-2 chunks instead of the whole table
- Old chunks can be compressed: `ALTER TABLE aqi_readings SET (timescaledb.compress = true)`

### 7.3 Complete Database Schema

```sql
-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Main readings table
CREATE TABLE IF NOT EXISTS aqi_readings (
    time          TIMESTAMPTZ    NOT NULL,
    station_id    TEXT           NOT NULL,
    city          TEXT           NOT NULL,
    country       TEXT           DEFAULT 'IN',
    aqi           FLOAT,
    pm25          FLOAT,
    pm10          FLOAT,
    no2           FLOAT,
    co            FLOAT,
    so2           FLOAT,
    o3            FLOAT,
    lat           DOUBLE PRECISION,
    lon           DOUBLE PRECISION,
    data_source   TEXT           DEFAULT 'WAQI'
);

-- Convert to hypertable (1-day chunks)
SELECT create_hypertable('aqi_readings', 'time', chunk_time_interval => INTERVAL '1 day');

-- Forecasts table
CREATE TABLE IF NOT EXISTS aqi_forecasts (
    forecast_generated_at  TIMESTAMPTZ  NOT NULL,
    forecast_for           TIMESTAMPTZ  NOT NULL,
    city                   TEXT         NOT NULL,
    predicted_aqi          FLOAT,
    model_version          TEXT         DEFAULT 'lgbm_v1',
    PRIMARY KEY (forecast_generated_at, forecast_for, city)
);

-- Continuous aggregate: hourly averages
CREATE MATERIALIZED VIEW aqi_hourly_avg
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    city,
    AVG(aqi)   AS avg_aqi,
    AVG(pm25)  AS avg_pm25,
    COUNT(*)   AS reading_count
FROM aqi_readings
GROUP BY hour, city
WITH NO DATA;

-- Auto-refresh policy
SELECT add_continuous_aggregate_policy('aqi_hourly_avg',
    start_offset => INTERVAL '30 days',
    end_offset   => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- Retention policy (optional after 3 months)
SELECT add_retention_policy('aqi_readings', INTERVAL '90 days');
```

### 7.4 Complete ERD

```
stations
+- station_id (PK)
+- city, country, lat, lon, source

aqi_readings (HYPERTABLE, partitioned by time)
+- time (NOT NULL), station_id (FK), city
+- aqi, pm25, pm10, no2, co, so2, o3
+- lat, lon, data_source

aqi_forecasts
+- forecast_generated_at, forecast_for, city (PK composite)
+- predicted_aqi, model_version

aqi_hourly_avg (CONTINUOUS AGGREGATE from aqi_readings)
+- hour (time_bucket 1h), city
+- avg_aqi, avg_pm25, reading_count
```

---

## 8. ML FORECASTING (DEEP DIVE)

### 8.1 Why LightGBM for AQI Forecasting

| Criterion | LightGBM | LSTM | Prophet |
|-----------|----------|------|---------|
| Windows install | pip install lightgbm | Complex (TF/PyTorch) | Requires conda |
| Training speed | Seconds | Minutes/hours | Moderate |
| Accuracy on tabular | Excellent | Excellent | Good |
| Interpretability | High (feature importance) | Low (black box) | Medium |
| Required data size | Small (1000+ rows) | Large (10000+ rows) | Medium |
| Handles missing values | Yes (built-in) | No | Yes |

### 8.2 The Recursive Forecasting Problem

LightGBM predicts only one step ahead. For 24-step forecasting, use **recursive multi-step**:
- Step 1: Predict t+1 using real lag features
- Step 2: Predict t+2 using t+1 (predicted) as lag feature
- Error accumulates over 24 steps — this is a known limitation; document it honestly.

### 8.3 Model Evaluation Metrics

| Metric | Target for AQI | Interpretation |
|--------|---------------|----------------|
| RMSE | < 30 AQI units | Penalises large errors heavily |
| MAE | < 20 AQI units | Average error in AQI units |
| Directional Accuracy | > 70% | % steps where trend direction is correct |

### 8.4 Walk-Forward Validation (Correct Approach)

```
Week:    1   2   3   4   5   6   7   8
Fold 1:  [TRAIN: 1-4]  [TEST: 5]
Fold 2:  [TRAIN: 1-5]  [TEST: 6]
Fold 3:  [TRAIN: 1-6]  [TEST: 7]
Fold 4:  [TRAIN: 1-7]  [TEST: 8]
```

Average RMSE across all folds = true model performance.

---

## 9. RAG PIPELINE (DEEP DIVE)

### 9.1 How RAG Prevents Hallucination

Without RAG: LLM might say "PM2.5 of 50 ug/m3 is perfectly safe for asthmatics" — dangerously wrong.

With RAG:
1. User query is embedded as a vector
2. ChromaDB finds the 3 nearest guideline chunks (by cosine similarity)
3. Those chunks are inserted directly into the LLM prompt
4. LLM answers using actual content from the PDF, and cites it

### 9.2 The Embedding Pipeline

```
WHO PDF (260 pages)
     |
     v PyPDFLoader
Text (entire PDF as string)
     |
     v RecursiveCharacterTextSplitter (chunk=500, overlap=50)
~400 chunks (~500 tokens each)
     |
     v all-MiniLM-L6-v2 (HuggingFace, 22 MB model)
~400 embeddings (384 dimensions each)
     |
     v ChromaDB.add_documents()
Persisted to: data/chroma_db/
     |
     v At query time: vectorstore.similarity_search(query, k=3)
Top 3 most relevant chunks returned instantly
```

### 9.3 Why all-MiniLM-L6-v2?

| Property | Value |
|----------|-------|
| Model size | 22 MB |
| Embedding dimensions | 384 |
| Inference speed | ~10ms per chunk on CPU |
| Offline use | Yes — download once, never needs internet |
| License | Apache 2.0 |

---

## 10. KAFKA SETUP (DEEP DIVE)

### 10.1 Why Kafka (Even for One Laptop)?

Kafka demonstrates production-grade architecture. Benefits:
- **Decoupling**: Fetcher does not care how fast consumer processes
- **Replay**: Consumer can re-read from topic beginning after crash
- **Fan-out**: Multiple consumers can read same topic independently
- **Scale-ready**: Add 500 stations later — only add producers; pipeline unchanged

### 10.2 Kafka 4.x KRaft vs Old ZooKeeper

| Feature | Old: Kafka + ZooKeeper | New: Kafka 4.x KRaft |
|---------|----------------------|---------------------|
| Processes to manage | 2 | 1 |
| RAM usage | ~1.1 GB total | ~800 MB total |
| Startup sequence | ZooKeeper first | Just Kafka |
| Complexity | High | Low |
| Current status | Removed from Kafka 4.0 | Only option |

### 10.3 Topic Design Rationale

| Parameter | Value | Reason |
|-----------|-------|--------|
| Partitions | 1 | Single producer; no parallelism needed |
| Replication factor | 1 | Single-broker (one laptop) |
| Retention | 7 days (default) | Old messages auto-deleted |
| Message format | JSON | Human-readable, Python-native |

---

## 11. STREAMLIT DASHBOARD DESIGN

### 11.1 App Tab Structure

```python
tab_live, tab_trends, tab_forecast, tab_insights, tab_chat, tab_about = st.tabs([
    "Live", "Trends", "Forecast", "Insights", "Health Advisor", "About"
])
```

### 11.2 Auto-Refresh Pattern

```python
import time
refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 30, 300, 60)
placeholder = st.empty()
with placeholder.container():
    # All live chart code here
    pass
time.sleep(refresh_interval)
st.rerun()
```

### 11.3 The `start_demo.bat` Launch Script

```batch
@echo off
echo AirSense Demo Startup Sequence

echo [1/5] Starting TimescaleDB (Docker)...
docker compose up -d timescaledb
timeout /t 10

echo [2/5] Starting Kafka...
start "" cmd /k "cd /d C:\kafka && set KAFKA_HEAP_OPTS=-Xmx512m -Xms512m && bin\windows\kafka-server-start.bat config\kraft\server.properties"
timeout /t 15

echo [3/5] Starting Consumer...
start "" cmd /k "cd /d C:\path\to\airsense && python consumer\consumer.py"
timeout /t 5

echo [4/5] Starting Ollama...
start "" cmd /k "ollama serve"
timeout /t 10

echo [5/5] Starting Streamlit...
start "" cmd /k "cd /d C:\path\to\airsense && streamlit run dashboard\app.py"

echo Dashboard: http://localhost:8501
echo MLflow:    run: mlflow ui (then http://localhost:5000)
pause
```

---

## 12. MLOPS & EXPERIMENT TRACKING

### 12.1 MLflow Concepts

| Concept | In AirSense |
|---------|-------------|
| Experiment | "AQI Forecasting" (one group for all runs) |
| Run | Each weekly retrain = one run |
| Parameters | n_estimators, learning_rate, max_depth |
| Metrics | RMSE, MAE |
| Artifacts | The .pkl model file |

### 12.2 Running MLflow UI

```powershell
mlflow ui --backend-store-uri ./mlruns --port 5000
# Open: http://localhost:5000
```

### 12.3 The Production Model Directory

```
ml/
+- training/train_forecast.py       <- training script
+- staging/lgbm_aqi.pkl             <- latest trained (not yet promoted)
+- production/lgbm_aqi.pkl          <- Streamlit ALWAYS loads from here
+- production/metrics.json          <- {"rmse": 18.4, "promoted_at": "..."}
+- mlruns/                          <- MLflow tracking data
```

---

## 13. DATA INTEGRITY, ETHICS & API COMPLIANCE

### 13.1 WAQI API Terms of Service Compliance

| Requirement | How AirSense Complies |
|-------------|----------------------|
| Use a personal token | Token stored in `.env`, registered in your name |
| Attribution | "Data provided by WAQI (waqi.info)" in every page footer |
| No redistribution | Historical training uses CPCB/Kaggle, not WAQI live feed |
| No commercial use | Academic/educational project |
| Rate limiting | 7 cities x 1 req/hour = 168 req/day << 1,000 free limit |

### 13.2 Medical & AI Ethics

| Risk | Mitigation |
|------|-----------|
| LLM gives wrong health advice | RAG grounds responses in WHO/CPCB official documents |
| User mistakes AI for a doctor | Prominent disclaimer on every page and in every AI response |
| Hallucinated statistics | System prompt explicitly forbids making up statistics |
| Data bias (urban stations only) | Document limitation in README and defense |
| Privacy of health questions | 100% local; clearly stated in UI |

### 13.3 Security Best Practices

```gitignore
# .gitignore
.env
*.env
data/chroma_db/
ml/mlruns/
ml/production/*.pkl
*.log
__pycache__/
```

---

## 14. DEMO-DAY RESILIENCE & BACKUP STRATEGY

### Scenario 1 — Live API Is Down

**Solution:** Replay mode feeds pre-loaded 7-day CSV through Kafka. Pipeline works identically.

```python
# fetch_aqi_replay.py
df = pd.read_csv("data/backup/aqi_7day_backup.csv")
for _, row in df.iterrows():
    producer.send("aqi_raw", value=row.to_dict())
    time.sleep(0.1)
```

### Scenario 2 — Ollama/LLM Crashes

**Solution:** Toggle kill-switch -> disable AI advisor -> rest of dashboard continues.
Show 3-4 pre-generated example conversations as screenshots from `docs/screenshots/`.

### Scenario 3 — Docker Containers Fail

**Solution:** Play recorded 5-minute demo video (`docs/airsense_demo.mp4`). Show static Power BI screenshots.

### Pre-Demo Checklist

```
[ ] .wslconfig exists and configured correctly
[ ] WSL restarted after .wslconfig creation
[ ] docker compose up confirms TimescaleDB is healthy
[ ] Kafka is running, topic aqi_raw exists
[ ] Consumer is running, rows in aqi_readings growing
[ ] Streamlit loads at http://localhost:8501
[ ] Ollama responds: ollama run phi3:mini "Hello"
[ ] LangChain agent returns response in chat tab
[ ] Backup CSV at data/backup/aqi_7day_backup.csv
[ ] Screenshots at docs/screenshots/
[ ] Demo video at docs/airsense_demo.mp4
[ ] Power BI report opens and shows data
[ ] Windows pagefile set to 8-16 GB
[ ] start_demo.bat tested end-to-end
```

---

## 15. DEFENSE Q&A (COMPREHENSIVE)

| Question | Comprehensive Answer |
|----------|---------------------|
| Why Kafka? You only have 7 cities. | Kafka decouples producers and consumers. If I later add 500 stations, I only add producers. It gives replay capability (consumer can re-read after crash) and demonstrates production-grade thinking. |
| Why not write directly to the database? | Direct writes couple ingestion to storage. Kafka buffers this and enables multiple independent consumers on the same stream. |
| Why did you remove ZooKeeper? | Apache Kafka 4.0 removed ZooKeeper entirely. KRaft mode is the only option now — this is current best practice, not a workaround. |
| How do you guarantee safe health advice? | Three layers: (1) RAG grounds LLM in official WHO/CPCB documents only; (2) system prompt forbids diagnosis and inventing statistics; (3) visible disclaimer on every response. |
| Why LightGBM instead of LSTM? | LightGBM achieves comparable accuracy on tabular time-series data, installs trivially on Windows, trains in seconds, and is interpretable via feature importance. LSTMs need much more data for minimal gain. |
| What is your RMSE and is it good? | RMSE of ~18-25 AQI units. This correctly captures directional trends — the key use case: will tomorrow be better or worse? |
| Are you compliant with WAQI's terms? | Yes. Own registered token, required attribution in app footer, CPCB/Kaggle data for historical training (not WAQI live feed cache). |
| How does the system handle no internet? | Replay mode feeds pre-loaded CSV through Kafka. Pipeline is identical. LLM runs fully offline (Ollama + phi3:mini). |
| Why TimescaleDB over InfluxDB? | TimescaleDB is a PostgreSQL superset — Power BI connects via standard driver, SQL skills apply directly. Hypertables give time-series performance. InfluxDB uses proprietary Flux query language. |
| How does RAG work? | User question is embedded as a vector. ChromaDB finds top-k most similar chunks from WHO/CPCB documents by cosine distance. Chunks are injected into LLM prompt. Model answers using real document content. |
| What is the privacy model? | 100% local. WAQI API is the only external call. User health questions, conversation history, and AQI data all stay on the laptop. |
| What are the limitations? | (1) Only 7 cities; (2) Station-level, not hyper-local; (3) Recursive forecasting accumulates error after 12+ hours; (4) phi3:mini is less capable than GPT-4; (5) Training data limited to available CPCB datasets. |

---

## 16. PROJECT FOLDER STRUCTURE

```
airsense/
+- .env                          <- WAQI_TOKEN, DB credentials (never commit)
+- .env.example                  <- Template with placeholder values
+- .gitignore                    <- Excludes .env, chroma_db, mlruns, logs
+- README.md                     <- Setup, architecture, demo instructions
+- AirSense_Master_Plan.md       <- This document
+- requirements.txt              <- All Python dependencies
+- config.yaml                   <- All configurable settings
+- start_demo.bat                <- One-click demo launcher
+- check_system.py               <- Health check: all services reachable?
|
+- ingestion/
|   +- fetch_aqi.py              <- WAQI API -> Kafka producer
|   +- fetch_aqi_replay.py       <- Backup: CSV replay mode
|
+- consumer/
|   +- consumer.py               <- Kafka consumer + validation + DB insert
|
+- sql/
|   +- 001_create_hypertable.sql
|   +- 002_create_forecasts.sql
|   +- 003_continuous_aggregates.sql
|   +- 004_retention_policy.sql
|
+- ml/
|   +- training/train_forecast.py  <- LightGBM training + MLflow logging
|   +- staging/lgbm_aqi.pkl        <- Latest trained (not yet promoted)
|   +- production/lgbm_aqi.pkl     <- Streamlit always loads from here
|   +- production/metrics.json     <- {"rmse": ..., "promoted_at": ...}
|   +- mlruns/                     <- MLflow tracking data
|
+- mlops/
|   +- retrain_forecast.py         <- Champion-challenger promotion script
|
+- rag/
|   +- build_knowledge_base.py     <- PDF -> chunks -> ChromaDB
|   +- retriever.py                <- ChromaDB search function
|
+- agent/
|   +- health_advisor.py           <- LangChain + Ollama + tools
|
+- dashboard/
|   +- app.py                      <- Main Streamlit application
|
+- data/
|   +- docs/                       <- WHO/CPCB PDFs
|   +- chroma_db/                  <- ChromaDB persistent store
|   +- historical/                 <- CPCB/Kaggle training datasets
|   +- backup/aqi_7day_backup.csv  <- Demo-day fallback data
|
+- notebooks/
|   +- 01_exploratory_analysis.ipynb
|   +- 02_feature_engineering.ipynb
|   +- 03_model_evaluation.ipynb
|
+- tests/
|   +- test_validation.py          <- Pydantic model tests
|   +- test_rag.py                 <- Retrieval accuracy tests
|   +- test_forecast.py            <- Forecast function tests
|
+- docs/
|   +- architecture_diagram.png
|   +- airsense_demo.mp4           <- Backup demo video
|   +- screenshots/
|       +- dashboard_live.png
|       +- forecast_chart.png
|       +- health_chat_example.png
|       +- powerbi_report.png
|
+- docker-compose.yml              <- TimescaleDB + optional Grafana
```

---

## 17. ENVIRONMENT & DEPENDENCIES

### requirements.txt

```text
# Data ingestion & streaming
kafka-python==2.0.2
requests==2.31.0
python-dotenv==1.0.0

# Data validation
pydantic==2.5.0

# Database
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23

# Machine learning
lightgbm==4.2.0
scikit-learn==1.3.2
pandas==2.1.4
numpy==1.26.2

# Experiment tracking
mlflow==2.9.2

# RAG & LLM
langchain==0.1.0
langchain-community==0.0.10
chromadb==0.4.22
sentence-transformers==2.2.2

# Dashboard
streamlit==1.29.0
plotly==5.18.0

# Utilities
pyyaml==6.0.1
pytest==7.4.3

# Optional: Prophet (Windows must use conda only)
# conda install -c conda-forge prophet
```

### config.yaml

```yaml
kafka:
  bootstrap_servers: "localhost:9092"
  topic_raw: "aqi_raw"
  group_id: "airsense_consumer"

database:
  host: "localhost"
  port: 5432
  name: "airsense_db"
  user: "airsense"

waqi:
  base_url: "https://api.waqi.info/feed"
  cities:
    - delhi
    - mumbai
    - bengaluru
    - hyderabad
    - chennai
    - pune
    - kolkata

ollama:
  base_url: "http://localhost:11434"
  model: "phi3:mini"
  timeout_seconds: 60

chroma:
  persist_directory: "data/chroma_db"
  collection_name: "airsense_guidelines"

ml:
  training_weeks: 4
  production_model_path: "ml/production/lgbm_aqi.pkl"
  forecast_horizon_hours: 48

logging:
  level: "INFO"
  file: "logs/airsense.log"
```

### Ollama Setup Steps

```powershell
# 1. Download from https://ollama.com (Windows installer)
# 2. Pull phi3:mini (~2.3 GB — do on good internet connection)
ollama pull phi3:mini

# 3. Test
ollama run phi3:mini "What is PM2.5 and why is it dangerous?"

# 4. Ollama server auto-starts on Windows boot
# Or manually: ollama serve
```

---

## 18. ENHANCEMENTS & FUTURE SCOPE

### Immediate Enhancements (Weeks 1-9)

| Enhancement | Effort | Impact |
|-------------|--------|--------|
| Structured logging (logging module) instead of print() | 1 hour | Debugging dramatically easier |
| check_system.py health check script | 2 hours | Professional; great for demos |
| Unit tests for Pydantic validation (pytest) | 2 hours | Software engineering maturity |
| Source citation in every RAG answer | 30 min | Increases trustworthiness |
| Colorblind-safe UI palette | 1 hour | Accessibility best practice |
| Privacy note: "Your questions never leave this laptop" | 15 min | Key differentiator |
| .gitignore + .env.example from Day 1 | 15 min | Security hygiene |

### Post-Week-12 Advanced Enhancements

| Enhancement | Effort | Learning Gained |
|-------------|--------|----------------|
| Physical sensor (SDS011, ~Rs.2,000) | Medium | IoT integration; hyper-local data |
| Push notifications when AQI spikes | Medium | Event-driven architecture |
| Bilingual UI (English + Hindi) | Low | Localisation |
| Email alert when forecast predicts hazardous | Medium | MLOps alerting |
| FastAPI endpoint for other apps | Medium | Production deployment pattern |
| Anomaly detection (Isolation Forest) | Medium | Advanced ML |
| Docker-compose the entire stack | High | Full containerisation |

---

## 19. SKILLS YOU WILL MASTER

| Skill Area | Specific Skills Gained |
|------------|----------------------|
| **Data Engineering** | Kafka KRaft, topic design, stream consumers, Pydantic validation, PostgreSQL hypertables, continuous aggregates, orchestration |
| **Data Science** | Time-series forecasting, lag feature engineering, walk-forward validation, RMSE/MAE evaluation, back-testing |
| **GenAI / AI Engineering** | RAG architecture, vector embeddings, ChromaDB, LangChain agents, local LLM deployment, prompt engineering for safety |
| **MLOps** | MLflow experiment tracking, champion-challenger promotion, automated retraining, model versioning |
| **Data Analytics** | Streamlit dashboards, Plotly interactive charts, Power BI / DAX, continuous aggregates for reporting |
| **System Engineering** | RAM budgeting, Docker memory capping, WSL2 configuration, Windows Task Scheduler, batch scripting |
| **Software Engineering** | Git best practices, secrets management, structured logging, unit testing, modular code organisation |
| **Ethics & Compliance** | API ToS compliance, medical AI disclaimers, RAG for hallucination mitigation, privacy-by-design |

---

## 20. GLOSSARY OF KEY TERMS

| Term | Definition |
|------|-----------|
| **AQI** | Air Quality Index — 0-500 number representing overall air quality; higher = worse |
| **PM2.5** | Particulate matter <= 2.5 micrometres; penetrates deep into lungs; most harmful pollutant |
| **PM10** | Particulate matter <= 10 micrometres; causes respiratory irritation |
| **Kafka** | Distributed message queue; acts as a buffer between data producers and consumers |
| **KRaft** | Kafka Raft — Kafka's built-in consensus protocol, replaced ZooKeeper in Kafka 4.0 |
| **Hypertable** | TimescaleDB's time-partitioned table; automatically chunks data by time interval |
| **Continuous Aggregate** | TimescaleDB's automatically-maintained materialised view; updates in near real-time |
| **RAG** | Retrieval-Augmented Generation — technique to ground LLM answers in real documents |
| **ChromaDB** | Open-source vector database; stores and retrieves text embeddings |
| **Embedding** | A numerical vector representation of text; semantically similar texts have similar vectors |
| **Cosine Similarity** | Measure of similarity between two vectors; used to find relevant document chunks |
| **LightGBM** | Gradient boosting framework; excellent for tabular data; fast and accurate |
| **Recursive Forecasting** | Using a model's own predictions as inputs for future predictions |
| **MLflow** | Open-source tool to track ML experiments, parameters, metrics, and model versions |
| **Champion-Challenger** | MLOps pattern: new model (challenger) replaces production (champion) only if RMSE improves |
| **WSL2** | Windows Subsystem for Linux 2 — Linux kernel inside Windows; required by Docker Desktop |
| **phi3:mini** | Microsoft's compact LLM; quantised Q4; runs on 4 GB VRAM |
| **Ollama** | Tool to run LLMs locally on Windows/Mac/Linux with GPU acceleration |
| **Pydantic** | Python library for data validation using type annotations |
| **WHO** | World Health Organization — publishes global air quality guidelines |
| **CPCB** | Central Pollution Control Board — Indian government body; publishes national AQI standards |
| **WAQI** | World Air Quality Index project — aggregates global air quality data; provides free API |
| **Walk-Forward Validation** | Time-series cross-validation method; training window expands chronologically |
| **Feature Importance** | LightGBM output showing which input features most influence predictions |

---

## APPENDIX: AQI QUICK REFERENCE

### AQI Health Categories (CPCB Indian Standard)

| AQI Range | Category | Health Implication | Recommended Action |
|-----------|----------|-------------------|--------------------|
| 0-50 | Good | Minimal impact | Enjoy outdoor activity |
| 51-100 | Satisfactory | Minor discomfort for sensitive | OK for most; sensitive be cautious |
| 101-200 | Moderate | Discomfort for lung/heart disease sufferers | Sensitive groups limit prolonged exertion |
| 201-300 | Poor | Breathing discomfort for most | Avoid outdoor activity; wear mask |
| 301-400 | Very Poor | Respiratory illness for prolonged exposure | Avoid outdoor activity entirely |
| 401-500 | Severe | Serious respiratory issues even for healthy | Stay indoors; use air purifier |

### Pollutant Limit Reference (WHO 2021 Annual Mean)

| Pollutant | WHO Guideline | Indian NAAQS |
|-----------|--------------|-------------|
| PM2.5 | 5 ug/m3 | 40 ug/m3 |
| PM10 | 15 ug/m3 | 60 ug/m3 |
| NO2 | 10 ug/m3 | 40 ug/m3 |
| O3 | 60 ug/m3 (peak season) | 100 ug/m3 |
| SO2 | 40 ug/m3 | 80 ug/m3 |

---

*Document prepared for MSc BI & Analytics Capstone Project — AirSense*  
*"Data provided by WAQI (waqi.info)" — required attribution for live data.*  
*All health guidance must be verified with a qualified medical professional.*
