# AirSense — Cursor / AI Tasks

What **Cursor (Agent mode)** builds for you. Request one week at a time after you pass the checkpoint.

---

## Completed (Week 0 + Week 1 scaffold)

| Task | Location |
|------|----------|
| Instruction pack | `airsense_cursor/` (all `.md` files) |
| Project scaffold | `airsense/` folders, placeholders |
| `config.yaml` | 6 Gujarat + hub cities |
| `.env.example`, `.gitignore`, `requirements.txt` | Root |
| `ingestion/fetch_aqi.py` | WAQI → Kafka producer |
| `ingestion/fetch_aqi_replay.py` | Stub for Week 12 |
| `scripts/test_waqi_kafka.py` | One-shot WAQI + Kafka test |
| `common/config.py`, `common/logging_setup.py` | Shared utilities |
| `README.md` | Setup + quick start |

---

## Week 2 — Request: *"Build Week 2 consumer + TimescaleDB"*

| Deliverable | Path |
|-------------|------|
| Docker Compose | `docker-compose.yml` |
| Hypertable SQL | `sql/001_create_hypertable.sql` |
| Forecasts SQL | `sql/002_create_forecasts.sql` |
| Continuous aggregates | `sql/003_continuous_aggregates.sql` |
| Retention policy | `sql/004_retention_policy.sql` |
| Pydantic models | `consumer/models.py` |
| Kafka consumer | `consumer/consumer.py` |
| Validation tests | `tests/test_validation.py` |

---

## Week 3 — Request: *"Build Week 3 Streamlit dashboard"*

| Deliverable | Path |
|-------------|------|
| Main app | `dashboard/app.py` |
| AQI gauge components | `dashboard/components/gauges.py` |
| DB query helpers | `dashboard/data_access.py` |

---

## Week 4 — Request: *"Build Week 4 Folium map + EDA"*

| Deliverable | Path |
|-------------|------|
| Folium map tab | `dashboard/components/map_view.py` |
| EDA notebook | `notebooks/01_exploratory_analysis.ipynb` |
| Insights tab charts | `dashboard/components/insights.py` |

---

## Week 5 — Request: *"Build Week 5 LightGBM training"*

| Deliverable | Path |
|-------------|------|
| Training script | `ml/training/train_forecast.py` |
| Feature engineering | `ml/training/features.py` |
| Evaluation notebook | `notebooks/03_model_evaluation.ipynb` |

---

## Week 6 — Request: *"Build Week 6 forecast pipeline"*

| Deliverable | Path |
|-------------|------|
| Inference script | `ml/training/predict_forecast.py` |
| Forecast tab | Dashboard integration |
| Forecast tests | `tests/test_forecast.py` |

---

## Week 7 — Request: *"Build Week 7 RAG knowledge base"*

| Deliverable | Path |
|-------------|------|
| PDF → ChromaDB | `rag/build_knowledge_base.py` |
| Retriever | `rag/retriever.py` |
| RAG tests | `tests/test_rag.py` |

---

## Week 8 — Request: *"Build Week 8 health chat agent"*

| Deliverable | Path |
|-------------|------|
| LangChain agent | `agent/health_advisor.py` |
| Chat tab | Dashboard integration |

---

## Week 9 — Request: *"Polish Week 9 UI"*

| Deliverable | Details |
|-------------|---------|
| All tabs complete | Live, Trends, Forecast, Insights, Health, About |
| Kill-switch | Stops Ollama calls |
| Error handling | User-friendly messages |
| Disclaimers | Every page + chat responses |

---

## Week 11 — Request: *"Build Week 11 MLOps + Telegram"*

| Deliverable | Path |
|-------------|------|
| Weekly retrain | `mlops/retrain_forecast.py` |
| Telegram alerts | `mlops/telegram_alert.py` |
| Chat ID helper | `scripts/get_telegram_chat_id.py` |

---

## Week 12 — Request: *"Build Week 12 demo hardening"*

| Deliverable | Path |
|-------------|------|
| Replay fetcher | Full `ingestion/fetch_aqi_replay.py` |
| Demo launcher | `start_demo.bat` |
| Health check | `check_system.py` |
| Sample backup CSV | `data/backup/aqi_7day_backup.csv` |

---

## Ongoing (any week)

- Fix bugs when something breaks on your machine
- Add unit tests as modules are built
- Update docs when architecture changes

---

## How to request work

Good prompts:

- *"Build Week 2 consumer + TimescaleDB"*
- *"Fix fetch_aqi.py — WAQI returns 429 for Surat"*
- *"Add Folium map to dashboard (Week 4)"*

Include:

1. Week number
2. Error output (if debugging)
3. Checkpoint you are trying to pass

---

*Your manual steps: [04_YOUR_TASKS.md](04_YOUR_TASKS.md)*
