# AirSense — 12-Week Plan

Work **one week at a time**. Do not skip checkpoints.

## Overview

| Week | Goal | You verify |
|------|------|------------|
| **0** | Prerequisites + folder + `.env` | Kafka running, WAQI token, `.wslconfig` |
| **1** | Live data → Kafka | Console consumer shows new messages hourly |
| **2** | Kafka → TimescaleDB | `SELECT COUNT(*), city FROM aqi_readings GROUP BY city` grows |
| **3** | First Streamlit dashboard | `localhost:8501` — live gauges + 24h chart |
| **4** | EDA + Folium map | India map with colored city bubbles |
| **5** | Train LightGBM | MLflow shows run; RMSE logged |
| **6** | Forecast on dashboard | Solid + dashed line chart (actual + 48h) |
| **7** | RAG knowledge base | Test query returns WHO/CPCB chunks |
| **8** | Health chat agent | Cited answer + doctor disclaimer |
| **9** | Polish UI | Tabs, kill-switch, disclaimer on every page |
| **10** | Power BI report | 2-page report connected to TimescaleDB |
| **11** | MLOps + Telegram | Weekly retrain promotes model; phone alert on spike |
| **12** | Demo hardening | 24h stress test, replay mode, `start_demo.bat`, README |

---

## Week 0 — Prerequisites

**Goal:** Machine ready; no code required yet.

- [ ] ZooKeeper + Kafka on `localhost:9092`
- [ ] `.wslconfig` with 3 GB RAM limit
- [ ] Java 17, Python 3.10+, Docker, Git, Ollama installed
- [ ] WAQI token in `.env`
- [ ] `pip install -r requirements.txt`
- [ ] Windows pagefile 8192–16384 MB

**Checkpoint:** `python scripts/test_waqi_kafka.py` passes (WAQI + Kafka).

---

## Week 1 — Data Ingestion

**Goal:** Live AQI flows into Kafka.

- [x] `config.yaml` with 6 cities
- [x] `ingestion/fetch_aqi.py`
- [x] `scripts/test_waqi_kafka.py`
- [ ] Create Kafka topic `aqi_raw`
- [ ] Run fetch once manually
- [ ] Schedule hourly via Task Scheduler

**Checkpoint:**
```powershell
bin\windows\kafka-console-consumer.bat --topic aqi_raw --from-beginning --bootstrap-server localhost:9092 --max-messages 6
```

---

## Week 2 — Consumer + TimescaleDB

**Goal:** Validated data in hypertable.

- [ ] `docker-compose.yml` (TimescaleDB, 512 MB limit)
- [ ] SQL schema in `sql/`
- [ ] `consumer/consumer.py` + Pydantic models
- [ ] Run consumer as long-lived process

**Checkpoint:**
```sql
SELECT COUNT(*), city FROM aqi_readings GROUP BY city;
```

---

## Week 3 — First Dashboard

**Goal:** Live Streamlit with gauges.

- [ ] `dashboard/app.py` — Live tab
- [ ] AQI color scale (CPCB categories)
- [ ] 24h line chart from TimescaleDB
- [ ] Auto-refresh (60s default)
- [ ] WAQI attribution footer

**Checkpoint:** `streamlit run dashboard/app.py` → gauges update.

---

## Week 4 — EDA + Map

**Goal:** Exploratory insights + Folium map.

- [ ] `notebooks/01_exploratory_analysis.ipynb`
- [ ] Insights tab in dashboard
- [ ] Folium map with city bubbles colored by AQI
- [ ] Seasonal / diurnal pattern charts

**Checkpoint:** Map shows 6 cities with correct colors.

---

## Week 5 — ML Training

**Goal:** First LightGBM model with MLflow.

- [ ] Download CPCB/Kaggle historical CSV → `data/historical/`
- [ ] `ml/training/train_forecast.py`
- [ ] Walk-forward validation
- [ ] Log RMSE, MAE to MLflow

**Checkpoint:** `mlflow ui` shows at least one run with metrics.

---

## Week 6 — Forecast Integration

**Goal:** 48h forecast on dashboard.

- [ ] Recursive multi-step prediction
- [ ] Write to `aqi_forecasts` table
- [ ] Forecast tab: solid (actual) + dashed (predicted)

**Checkpoint:** Chart shows 48h ahead dashed line.

---

## Week 7 — RAG Knowledge Base

**Goal:** WHO/CPCB PDFs searchable in ChromaDB.

- [ ] PDFs in `data/docs/`
- [ ] `rag/build_knowledge_base.py`
- [ ] `rag/retriever.py`
- [ ] Test retrieval for "PM2.5 asthma"

**Checkpoint:** Top-3 chunks cite official guidelines.

---

## Week 8 — Health Chat Agent

**Goal:** LangChain + Ollama with citations.

- [ ] `agent/health_advisor.py`
- [ ] Inject current AQI context
- [ ] System prompt: no diagnosis, cite sources
- [ ] Chat tab in Streamlit

**Checkpoint:** Ask "Is it safe to jog with asthma?" → cited answer + disclaimer.

---

## Week 9 — UI Polish

**Goal:** Production-quality demo UI.

- [ ] All tabs wired (Live, Trends, Forecast, Insights, Health, About)
- [ ] Kill-switch for LLM
- [ ] Medical disclaimer on every page
- [ ] Friendly error messages (no tracebacks)

**Checkpoint:** Full walkthrough without crashes.

---

## Week 10 — Power BI

**Goal:** Executive 2-page report.

- [ ] Connect Power BI Desktop to TimescaleDB
- [ ] Page 1: KPIs + trend
- [ ] Page 2: city comparison + pollutant breakdown
- [ ] Screenshot in `docs/screenshots/`

**Checkpoint:** Report refreshes from live DB.

---

## Week 11 — MLOps + Telegram

**Goal:** Automated retrain + spike alerts.

- [ ] `mlops/retrain_forecast.py` — promote only if RMSE improves
- [ ] Task Scheduler weekly retrain job
- [ ] Telegram bot + alert script
- [ ] Threshold from `config.yaml`

**Checkpoint:** Phone receives test alert; new model promoted in MLflow.

---

## Week 12 — Demo Hardening

**Goal:** Bulletproof demo day.

- [ ] `fetch_aqi_replay.py` + `data/backup/aqi_7day_backup.csv`
- [ ] `start_demo.bat` one-click launcher
- [ ] `check_system.py` health check
- [ ] 24h stress test log
- [ ] Demo video + screenshots
- [ ] Rehearse [08_DEFENSE_QA.md](08_DEFENSE_QA.md)

**Checkpoint:** Full demo from `start_demo.bat` in under 3 minutes.

---

*Master checklist: [CHECKLIST.md](CHECKLIST.md)*
