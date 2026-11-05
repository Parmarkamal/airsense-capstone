# AirSense — Project Brief

**One-page summary for defense, report, and elevator pitch.**

---

## Identity

| Field | Value |
|-------|-------|
| **Name** | AirSense |
| **Tagline** | *Know the air. Protect your health.* |
| **Domain** | Data Engineering + Data Science + Generative AI |
| **Platform** | Single Windows laptop (16 GB RAM), ₹0 cloud cost |
| **Duration** | 12 weeks |
| **Privacy** | 100% local — health questions never leave the machine |

## Problem

Indian cities routinely exceed WHO/CPCB safe limits. Citizens see raw AQI numbers without context, forecast, or personalised guidance. Cloud AI tools raise privacy concerns for health-related queries.

## Solution

AirSense ingests **live air quality** from WAQI, streams it through **Kafka**, stores validated readings in **TimescaleDB**, forecasts **48 hours** ahead with **LightGBM**, and answers health questions via **RAG + Ollama phi3:mini** grounded in WHO/CPCB PDFs.

## Target users

Urban Indian residents, students, health-conscious individuals, and policy researchers who need actionable, private air-quality intelligence.

## Technology stack

| Layer | Tool |
|-------|------|
| Live data | WAQI/AQICN API |
| Streaming | Apache Kafka (ZooKeeper mode, localhost:9092) |
| Validation | Pydantic v2 |
| Storage | TimescaleDB (Docker) |
| ML | LightGBM + MLflow |
| Dashboard | Streamlit + Plotly + Folium |
| RAG | ChromaDB + sentence-transformers |
| LLM | Ollama phi3:mini |
| BI | Power BI Desktop |
| Alerts | Telegram Bot API |

## Cities (Phase 1)

Ahmedabad, Surat, Rajkot, Gandhinagar, Delhi, Mumbai — expandable via `config.yaml`.

## Key outcomes

1. **Live pipeline:** hourly WAQI → Kafka → TimescaleDB
2. **Forecast:** 48-hour AQI prediction with logged RMSE
3. **Dashboard:** gauges, trends, India map, forecast chart
4. **Health advisor:** cited, disclaimer-backed answers from official guidelines
5. **MLOps:** weekly retrain with champion-challenger promotion
6. **Demo resilience:** replay mode, kill-switch, `start_demo.bat`

## Ethics & compliance

- WAQI attribution on every page
- Historical training from CPCB/Kaggle — not WAQI cache
- No medical diagnosis; prominent disclaimers
- Invalid readings logged, not stored

## Limitations (state honestly in viva)

1. Six cities in v1 (station-level, not hyper-local)
2. Recursive 48h forecast accumulates error after ~12 hours
3. phi3:mini is less capable than cloud LLMs
4. Training data limited to available CPCB/Kaggle datasets
5. WAQI API dependency for live data (mitigated by replay mode)

## Success metrics

| Metric | Target |
|--------|--------|
| Pipeline uptime (demo week) | 24h stress test passes |
| Forecast RMSE | < 30 AQI units |
| RAG answers | Include WHO/CPCB citations |
| End-to-end latency (dashboard refresh) | < 5 seconds |

---

*Full architecture: [02_ARCHITECTURE.md](02_ARCHITECTURE.md) | Week plan: [03_WEEK_BY_WEEK_PLAN.md](03_WEEK_BY_WEEK_PLAN.md)*
