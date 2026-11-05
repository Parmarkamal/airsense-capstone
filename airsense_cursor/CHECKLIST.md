# AirSense — Master Checklist

Tick items as you complete them. **Do not skip week checkpoints.**

---

## Week 0 — Prerequisites

- [ ] ZooKeeper running
- [ ] Kafka broker on `localhost:9092`
- [ ] `.wslconfig` created (3 GB RAM, 2 processors)
- [ ] `wsl --shutdown` + Docker Desktop restarted
- [ ] Java 17 verified (`java -version`)
- [ ] Python 3.10+ verified (`python --version`)
- [ ] Docker verified (`docker --version`)
- [ ] Git verified (`git --version`)
- [ ] WAQI token registered
- [ ] `.env` created from `.env.example`
- [ ] `pip install -r requirements.txt`
- [ ] Windows pagefile 8192–16384 MB
- [ ] Ollama installed
- [ ] `ollama pull phi3:mini` (can defer to Week 7 if low on disk)

**Checkpoint:** `python scripts/test_waqi_kafka.py` → all `[OK]`

---

## Week 1 — Kafka ingestion

- [ ] Kafka topic `aqi_raw` created
- [ ] `python ingestion/fetch_aqi.py` runs without errors
- [ ] Console consumer shows JSON for 6 cities
- [ ] Task Scheduler hourly job configured
- [ ] Logs written to `logs/airsense.log`

**Checkpoint:** `--max-messages 6` on console consumer shows all cities

---

## Week 2 — TimescaleDB + consumer

- [ ] `docker compose up -d timescaledb`
- [ ] SQL schema applied (`001` through `004`)
- [ ] `consumer/consumer.py` running
- [ ] Invalid test message logged, not stored
- [ ] Row counts growing hourly

**Checkpoint:** `SELECT COUNT(*), city FROM aqi_readings GROUP BY city;`

---

## Week 3 — Streamlit live dashboard

- [ ] `streamlit run dashboard/app.py` loads
- [ ] Live gauges for all cities
- [ ] 24h line chart populated
- [ ] Auto-refresh works
- [ ] WAQI footer attribution visible

**Checkpoint:** Dashboard at http://localhost:8501

---

## Week 4 — Map + EDA

- [ ] EDA notebook completed
- [ ] Folium map with colored bubbles
- [ ] Insights tab with seasonal/diurnal charts

**Checkpoint:** Map shows 6 Gujarat + hub cities

---

## Week 5 — ML training

- [ ] Historical CSV in `data/historical/`
- [ ] `train_forecast.py` completes
- [ ] MLflow run with RMSE + MAE
- [ ] Walk-forward validation documented

**Checkpoint:** `mlflow ui` → at least 1 successful run

---

## Week 6 — Forecast on dashboard

- [ ] Predictions in `aqi_forecasts` table
- [ ] Forecast tab: actual (solid) + predicted (dashed)
- [ ] 48-hour horizon displayed

**Checkpoint:** Forecast chart renders correctly

---

## Week 7 — RAG knowledge base

- [ ] WHO PDF in `data/docs/`
- [ ] CPCB PDF in `data/docs/`
- [ ] `build_knowledge_base.py` run successfully
- [ ] `data/chroma_db/` populated
- [ ] Test retrieval returns relevant chunks

**Checkpoint:** Query "PM2.5 asthma" → WHO/CPCB citations

---

## Week 8 — Health chat

- [ ] Ollama serving phi3:mini
- [ ] Chat tab returns cited answers
- [ ] Medical disclaimer on every response
- [ ] Current AQI injected into context

**Checkpoint:** Live chat demo works

---

## Week 9 — UI polish

- [ ] All 6 tabs functional
- [ ] Kill-switch stops LLM calls
- [ ] No raw tracebacks shown to user
- [ ] Disclaimers on every page

**Checkpoint:** Full UI walkthrough without crash

---

## Week 10 — Power BI

- [ ] Connected to TimescaleDB
- [ ] Page 1: KPIs + trends
- [ ] Page 2: city comparison
- [ ] Screenshot saved

**Checkpoint:** Report refreshes from live data

---

## Week 11 — MLOps + Telegram

- [ ] Telegram bot created
- [ ] Chat ID in `.env`
- [ ] Alert fires on threshold breach
- [ ] Weekly retrain script scheduled
- [ ] Champion-challenger promotion tested

**Checkpoint:** Phone receives test alert

---

## Week 12 — Demo hardening

- [ ] `fetch_aqi_replay.py` works offline
- [ ] `data/backup/aqi_7day_backup.csv` exists
- [ ] `start_demo.bat` tested end-to-end
- [ ] `check_system.py` passes
- [ ] 24h stress test completed
- [ ] Demo video recorded
- [ ] Screenshots captured
- [ ] README complete
- [ ] Defense Q&A rehearsed

**Checkpoint:** Demo from cold start in < 3 minutes

---

## 20 rules compliance

- [ ] 1. Module-by-module build
- [ ] 2. Kafka ZooKeeper mode (not KRaft)
- [ ] 3. `.wslconfig` 3 GB
- [ ] 4. phi3:mini only
- [ ] 5. Pinned package versions
- [ ] 6. Bad data logged, not stored
- [ ] 7. Walk-forward validation
- [ ] 8. RAG cites WHO/CPCB
- [ ] 9. Medical disclaimers everywhere
- [ ] 10. Localhost only (+ WAQI/Telegram)
- [ ] 11. MLflow from Week 5
- [ ] 12. Promote only if RMSE improves
- [ ] 13. Friendly UI errors
- [ ] 14. Gujarat + Delhi/Mumbai cities
- [ ] 15. No mobile/IoT in core scope
- [ ] 16. Telegram via HTTP POST
- [ ] 17. Folium map included
- [ ] 18. Strict folder separation
- [ ] 19. Kill-switch works
- [ ] 20. `start_demo.bat` ready

---

*Start here: [00_START_HERE.md](00_START_HERE.md)*
