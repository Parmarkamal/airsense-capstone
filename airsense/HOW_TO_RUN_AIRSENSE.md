# 🌬️ AirSense — Master Startup Guide & Presentation Runbook
*MSc Business Intelligence & Analytics | Capstone Project*

This document provides a **complete, step-by-step playbook** to start the entire AirSense project from scratch after turning on your laptop, and how to present it seamlessly to your professor or evaluators.

---

## 📌 Architecture Ports & Services Quick Reference

Before starting, keep in mind how the services connect:

| Component | Technology | Host Port | Purpose |
| :--- | :--- | :--- | :--- |
| **Storage Engine** | TimescaleDB (Docker) | `localhost:5433` | Time-series hypertable (`aqi_readings`) |
| **Cluster Coordinator** | Apache ZooKeeper | `localhost:2181` | Coordinates Kafka broker state |
| **Streaming Broker** | Apache Kafka | `localhost:9092` | Real-time event queue (`aqi_raw`) |
| **Stream Consumer** | Python (`kafka-consumer`) | Background | Validates & persists stream to DB |
| **User Interface** | Streamlit | `http://localhost:8501` | Live dashboard & CPCB gauges |

---

## 🚀 Cold-Start Procedure (After Laptop Reboot)

When you turn on your laptop, follow this exact sequence:

```
Step 1: Start Docker Desktop & TimescaleDB
                 │
Step 2: Start ZooKeeper (Port 2181)
                 │
Step 3: Start Kafka Server (Port 9092)
                 │
Step 4: Start Kafka Consumer (Terminal)
                 │
Step 5: Launch Streamlit Dashboard (Port 8501)
                 │
[Demo Trigger]: Run Ingestion Fetcher to show live streaming!
```

---

### Step 1: Start TimescaleDB Container

1. Open **Docker Desktop** from your Windows Start Menu and wait until the whale icon in the taskbar is steady (green).
2. Open a **PowerShell** window and run:

```powershell
cd C:\STUDY\MSC_BI_Analytics\sem_03\capstone_project\airsense
docker compose up -d
```

**✅ Success Indicator:**
```text
Container airsense_timescaledb  Started
```
*(Verify by running `docker ps` — you will see `airsense_timescaledb` with port `0.0.0.0:5433->5432/tcp`).*

---

### Step 2: Start Apache ZooKeeper

Open a **second PowerShell window** (leave it open):

```powershell
cd C:\kafka
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
```

**✅ Success Indicator:**
You will see output concluding with:
```text
INFO binding to port 0.0.0.0/0.0.0.0:2181 (org.apache.zookeeper.server.NIOServerCnxnFactory)
```

---

### Step 3: Start Apache Kafka Broker

Open a **third PowerShell window** (leave it open):

```powershell
cd C:\kafka
$env:KAFKA_HEAP_OPTS = "-Xmx512m -Xms512m"
.\bin\windows\kafka-server-start.bat .\config\server.properties
```

**✅ Success Indicator:**
You will see output concluding with:
```text
INFO [KafkaServer id=0] started (kafka.server.KafkaServer)
```

---

### Step 4: Start the Kafka Consumer

Open a **fourth PowerShell window** (leave it open to watch data arrive):

```powershell
cd C:\STUDY\MSC_BI_Analytics\sem_03\capstone_project\airsense
python consumer/kafka_consumer.py
```

**✅ Success Indicator:**
```text
INFO | airsense.consumer | Connecting to TimescaleDB...
INFO | airsense.consumer | Connecting to Kafka at localhost:9092, topic=aqi_raw, group=airsense_consumer
INFO | airsense.consumer | Kafka consumer ready — waiting for messages...
```

---

### Step 5: Launch the Streamlit Dashboard

Open a **fifth PowerShell window**:

```powershell
cd C:\STUDY\MSC_BI_Analytics\sem_03\capstone_project\airsense
python -m streamlit run dashboard/app.py
```
*(Alternatively: double-click `scripts\run_dashboard.bat`)*

**✅ Success Indicator:**
Your browser opens automatically at **`http://localhost:8501`** showing the live dashboard, KPI cards, and CPCB gauge meters.

---

## 🎬 How to Give a Live Demo to Your Teacher

When presenting, you want to show that **real data actually streams live through your pipeline**, rather than just showing a static website.

### The Live Ingestion Demonstration (The "Magic" Moment):

1. **Keep your Dashboard open on your screen** (`http://localhost:8501`). Point out the **"Total Events Ingested"** counter in the left sidebar.
2. Open a PowerShell window and run the live fetcher:
   ```powershell
   cd C:\STUDY\MSC_BI_Analytics\sem_03\capstone_project\airsense
   python ingestion/fetch_aqi.py
   ```
3. **Show the Consumer terminal (Step 4)**: It will instantly print green checkmarks as it consumes from Kafka and stores into TimescaleDB:
   ```text
   INFO | airsense.consumer | ✓ Stored: city=ahmedabad   AQI=108
   INFO | airsense.consumer | ✓ Stored: city=bengaluru   AQI=53
   INFO | airsense.consumer | ✓ Stored: city=pune        AQI=232
   ...
   ```
4. **Switch back to the browser**: The sidebar event counter increments live (e.g. from 10 to 16), and the charts refresh!

---

## 🎤 The 3-Minute Presentation Pitch

When presenting to your professor, use this structured explanation:

### 1. Introduction & Academic Objective (30 seconds)
> *"Good morning, madam. For my MSc Business Intelligence & Analytics Capstone, I developed **AirSense** — an end-to-end streaming data engineering and environmental intelligence platform.*  
> *Rather than analyzing static historical CSVs, AirSense ingests real-time air quality telemetry from ground-level monitoring stations across major Indian urban hubs including Ahmedabad, Bengaluru, Pune, Gandhinagar, Delhi, and Mumbai."*

### 2. Architecture & Enterprise Design Decisions (60 seconds)
> *"The platform is architected across enterprise decoupled layers:*  
> *1. **Ingestion & Streaming**: Raw telemetry from the WAQI API is published as JSON events to **Apache Kafka** on port 9092. Kafka decouples our producer and consumer, preventing data loss during network hiccups.*  
> *2. **Data Quality & Validation**: The consumer passes every message through **Pydantic v2 schemas**, rejecting corrupted readings into an audit table before database entry.*  
> *3. **Time-Series Storage**: Clean events are committed to **TimescaleDB** (PostgreSQL) on port 5433, utilizing automated **hypertables** and continuous aggregates for high-speed temporal querying."*

### 3. Visualisation & Regulatory Alignment (60 seconds)
> *"On the frontend, built in **Streamlit and Plotly**:*  
> *• Current urban air status is categorized strictly according to official **Central Pollution Control Board (CPCB NAAQS)** standards.*  
> *• Selecting any city displays its exact AQI gauge, health advisory, granular pollutant concentrations (PM2.5, PM10, NO2, SO2, CO, O3), and 24-hour temporal trends.*  
> *• The dashboard auto-refreshes every 60 seconds with live pipeline telemetry."*

### 4. Roadmap to Final Defense (30 seconds)
> *"Currently, Phases 1 through 3 are 100% operational. Phase 4 (AI Health Advisor) is now live. For the remaining weeks, we are building:*  
> *• Executive Power BI dashboards connecting to TimescaleDB (Weeks 9-10)*  
> *• Automated Telegram/Email alerts when AQI crosses CPCB thresholds (Week 11)*  
> *• Final stress testing, documentation, and demo video (Week 12)."*

---

## 🤖 Starting the AI Health Advisor (Phase 4)

### Step 6: Start Ollama (Local LLM Server)

Open a **new PowerShell window** (leave it open during demo):

```powershell
ollama serve
```

**✅ Success Indicator:**
```text
Listening on 127.0.0.1:11434
```

### Step 7: Build the Knowledge Base (One-Time Only!)

Run this **only once** after installing (takes ~30 seconds):

```powershell
cd C:\STUDY\MSC_BI_Analytics\sem_03\capstone_project\airsense
python rag/build_knowledge_base.py
```

**✅ Success Indicator:**
```text
[SUCCESS] Knowledge base built with XX total chunks across 3 sources.
You can now run the dashboard and use the AI Health Advisor tab.
```

After this, the knowledge base is saved permanently in `data/chroma_db/` — you never need to run it again unless you want to update the knowledge.

### Step 8: Use the AI Health Advisor

1. Navigate to the dashboard at `http://localhost:8501`
2. Select **"🤖 AI Health Advisor"** in the sidebar
3. All three status indicators should show **🟢 Green**
4. Click any **Quick Question** or type your own — the AI answers using WHO/CPCB guidelines + your live AQI data

---

## 🔧 Quick Troubleshooting Checklist

| Issue | Cause | Fix |
| :--- | :--- | :--- |
| `FATAL: password authentication failed on port 5432` | Native Windows Postgres 18 is running on port 5432 | AirSense is configured for port **`5433`**. Make sure `.env` and `config.yaml` have `POSTGRES_PORT=5433`. |
| `Cannot connect to Kafka on 9092` | ZooKeeper or Kafka server wasn't started | Ensure Step 2 (ZooKeeper) and Step 3 (Kafka) are running in open terminal windows. |
| `Streamlit: command not recognized` | Streamlit isn't in Windows PATH | Always run via python module: `python -m streamlit run dashboard/app.py` |
| `Out of memory / laggy system` | Kafka default heap memory is too large | Always set `$env:KAFKA_HEAP_OPTS = "-Xmx512m -Xms512m"` before starting Kafka. |
| `Ollama LLM: Not Running` (in dashboard) | Ollama not started | Run `ollama serve` in a new terminal window. |
| `Knowledge Base: Not Built` (in dashboard) | ChromaDB not initialized | Run `python rag/build_knowledge_base.py` once. |
| AI Advisor times out | Model still loading | Wait 30 seconds after first query — model loads into memory on first use. |

---

*File location: `airsense/HOW_TO_RUN_AIRSENSE.md` | Capstone Semester 3 | Updated Phase 4*
