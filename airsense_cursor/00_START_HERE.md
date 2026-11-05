# AirSense — Start Here

> **Read this file first.** Everything else in `airsense_cursor/` supports the 12-week build.

## Locked decisions

| Decision | Choice |
|----------|--------|
| **Kafka** | Keep existing **ZooKeeper + Kafka** on `localhost:9092` — **do not migrate to KRaft** |
| **Cities** | **Gujarat + hubs:** Ahmedabad, Surat, Rajkot, Gandhinagar, Delhi, Mumbai (6 cities) |
| **Code location** | `airsense/` (this repo folder) |
| **Instructions** | `airsense_cursor/` (you are here) |

## What you are building

**AirSense** is a **local-only** capstone system that:

1. Fetches live AQI every hour (WAQI API)
2. Streams through **Kafka** → validates with **Pydantic** → stores in **TimescaleDB**
3. Forecasts the next **48 hours** with **LightGBM** (weekly retrain + MLflow)
4. Shows a **Streamlit** dashboard (gauges, charts, **Folium map**, forecast)
5. Answers health questions via **RAG** (WHO/CPCB PDFs → ChromaDB → **Ollama phi3:mini**)
6. Sends **Telegram alerts** when AQI spikes
7. Optional **Power BI** report for executive analytics

**Cost:** ₹0 | **Privacy:** health questions never leave your laptop

## Document map

| File | Purpose |
|------|---------|
| [01_PROJECT_BRIEF.md](01_PROJECT_BRIEF.md) | One-page summary for defense/report |
| [02_ARCHITECTURE.md](02_ARCHITECTURE.md) | System design + data flow |
| [03_WEEK_BY_WEEK_PLAN.md](03_WEEK_BY_WEEK_PLAN.md) | 12-week checklist with checkpoints |
| [04_YOUR_TASKS.md](04_YOUR_TASKS.md) | What **you** must do manually |
| [05_AI_TASKS.md](05_AI_TASKS.md) | What **Cursor** builds in Agent mode |
| [06_SETUP_PREREQUISITES.md](06_SETUP_PREREQUISITES.md) | Java, Docker, Ollama, WAQI token, etc. |
| [07_RAM_AND_DEMO.md](07_RAM_AND_DEMO.md) | `.wslconfig`, `start_demo.bat`, backup plans |
| [08_DEFENSE_QA.md](08_DEFENSE_QA.md) | Ready answers for viva |
| [09_FOLDER_STRUCTURE.md](09_FOLDER_STRUCTURE.md) | Final code layout |
| [CHECKLIST.md](CHECKLIST.md) | Master tick-list (Week 0 → Week 12) |

## Your first 60 minutes (Week 0)

### You (manual)

1. Confirm **ZooKeeper + Kafka** running; broker on `localhost:9092`
2. Create `C:\Users\<YourName>\.wslconfig` (see [06_SETUP_PREREQUISITES.md](06_SETUP_PREREQUISITES.md))
3. Run `wsl --shutdown`, restart Docker Desktop
4. Register WAQI token: https://aqicn.org/data-platform/token/
5. Copy `airsense/.env.example` → `airsense/.env` and paste your token
6. Install Python deps: `pip install -r airsense/requirements.txt`

### Then run Week 1 test

```powershell
cd c:\STUDY\MSC_BI_Analytics\sem_03\capstone_project\airsense

# One-shot: WAQI + Kafka verification
python scripts/test_waqi_kafka.py

# Full hourly fetch (also publishes to Kafka)
python ingestion/fetch_aqi.py
```

### Week 1 checkpoint

```powershell
# Create topic if it does not exist (adjust KAFKA_HOME path)
cd C:\kafka
bin\windows\kafka-topics.bat --create --topic aqi_raw --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Read messages
bin\windows\kafka-console-consumer.bat --topic aqi_raw --from-beginning --bootstrap-server localhost:9092 --max-messages 6
```

You should see JSON AQI messages for all 6 cities.

## How we work together

1. **One week at a time** — you hit the checkpoint before we start the next week
2. **You run services** — Kafka, Docker, Ollama, Task Scheduler
3. **Cursor writes code** — say e.g. *"Build Week 2 consumer + TimescaleDB"*
4. **Track progress** in [CHECKLIST.md](CHECKLIST.md)

## Quick reference — ports

| Service | Port | Started by |
|---------|------|------------|
| Kafka | 9092 | You (ZooKeeper + Kafka) |
| TimescaleDB | 5432 | Docker (Week 2+) |
| Streamlit | 8501 | `streamlit run dashboard/app.py` |
| Ollama | 11434 | `ollama serve` |
| MLflow UI | 5000 | `mlflow ui` (on demand) |

## 20 rules (non-negotiable)

1. Plan first, build module by module
2. **Do not migrate Kafka to KRaft** — use your existing ZooKeeper setup
3. **`.wslconfig` 3 GB** before Docker
4. **phi3:mini only** — no vision models on RTX 2050
5. Pin all package versions
6. Bad data → log, not DB
7. Walk-forward validation only
8. RAG must cite WHO/CPCB — no diagnosis
9. Medical disclaimer everywhere
10. Localhost only (except WAQI + Telegram)
11. MLflow from Week 5
12. Promote model only if RMSE improves
13. Friendly errors in UI, not tracebacks
14. Gujarat cities + Delhi/Mumbai
15. No mobile app / IoT in core 12 weeks
16. Telegram = simple HTTP POST
17. Folium map is core
18. Strict folder separation
19. Kill-switch must stop LLM calls
20. `start_demo.bat` by Week 10

---

**Next:** [06_SETUP_PREREQUISITES.md](06_SETUP_PREREQUISITES.md) if Week 0 is not done, or run `python scripts/test_waqi_kafka.py` if it is.
