# AirSense — Architecture

## High-level diagram

```text
[Windows Task Scheduler — hourly]
        │
        ▼
   fetch_aqi.py  ──►  WAQI API (internet)
        │
        ▼
   Kafka topic: "aqi_raw"  (localhost:9092, ZooKeeper mode)
        │
        ▼
   consumer.py  (Pydantic validation)
        │
        ├── VALID ──►  TimescaleDB.aqi_readings (hypertable)
        └── INVALID ──►  logs/validation_errors.log
        │
        ├──────────────────┬──────────────────┬──────────────────┐
        ▼                  ▼                  ▼                  ▼
   LightGBM           Streamlit          Power BI          Telegram
   (weekly retrain)   dashboard          (Week 10)         alerts
        │                  │
        ▼                  ├── Folium map (Week 4)
   aqi_forecasts          └── Health Chat ← ChromaDB + Ollama phi3:mini
```

## Layer breakdown

| Layer | Component | Port | Runs as |
|-------|-----------|------|---------|
| 1 | WAQI fetcher | — | Task Scheduler / manual |
| 2 | Kafka broker | 9092 | Native (ZooKeeper + Kafka) |
| 3 | Python consumer | — | Long-running process |
| 4 | TimescaleDB | 5432 | Docker |
| 5 | ML training | — | Weekly script + MLflow |
| 6 | Streamlit UI | 8501 | Native |
| 7 | ChromaDB | — | In-process (persisted to disk) |
| 8 | Ollama | 11434 | Native |
| 9 | Power BI | — | Desktop app |

## Data flow (detailed)

### Ingestion (Week 1)

1. `fetch_aqi.py` reads city list from `config.yaml`
2. For each city, GET `https://api.waqi.info/feed/{city}/?token=...`
3. Parse `data.aqi`, `data.iaqi.*`, coordinates, timestamp
4. Publish JSON to Kafka topic `aqi_raw` (key = city slug)
5. Sleep between cities to respect rate limits (~1 req/sec)

### Stream processing (Week 2)

1. `consumer.py` subscribes to `aqi_raw` with consumer group `airsense_consumer`
2. Pydantic model validates schema, ranges, timestamp
3. Valid rows: `INSERT INTO aqi_readings ... ON CONFLICT DO NOTHING`
4. Manual Kafka commit **after** successful DB write (at-least-once)
5. Invalid rows: log full payload + error, skip commit retry

### Forecasting (Weeks 5–6)

1. Load historical CSV + live TimescaleDB data
2. Feature engineering: lags, hour-of-day, day-of-week, rolling means
3. Walk-forward validation (never random split on time series)
4. Log RMSE/MAE to MLflow
5. Write predictions to `aqi_forecasts` table
6. Dashboard reads actual + forecast for chart overlay

### RAG health advisor (Weeks 7–8)

```text
User question
    │
    ▼
Embed query (all-MiniLM-L6-v2)
    │
    ▼
ChromaDB similarity_search(k=3)
    │
    ▼
Prompt = system rules + retrieved chunks + current AQI context
    │
    ▼
Ollama phi3:mini
    │
    ▼
Answer with citations + medical disclaimer
```

## Kafka topic design

| Parameter | Value | Reason |
|-----------|-------|--------|
| Topic | `aqi_raw` | Single raw ingestion stream |
| Partitions | 1 | Single producer, laptop scale |
| Replication | 1 | Single broker |
| Format | JSON UTF-8 | Human-readable, Python-native |
| Key | city slug | Same-city messages stay ordered |

## Message schema (v1.0)

```json
{
  "schema_version": "1.0",
  "time": "2026-07-21T03:30:00+00:00",
  "station_id": "abc123",
  "city": "ahmedabad",
  "country": "IN",
  "aqi": 187.0,
  "pm25": 95.2,
  "pm10": 120.0,
  "no2": 42.0,
  "co": null,
  "so2": null,
  "o3": 28.0,
  "lat": 23.0225,
  "lon": 72.5714,
  "data_source": "WAQI"
}
```

## Database schema (summary)

- **aqi_readings** — hypertable, 1-day chunks, all pollutant columns
- **aqi_forecasts** — composite PK (generated_at, forecast_for, city)
- **aqi_hourly_avg** — continuous aggregate for dashboard speed

Full SQL: `airsense/sql/` (created Week 2).

## Security & privacy

- `.env` never committed; WAQI token local only
- All services bind to localhost except WAQI fetch and Telegram POST
- Kill-switch in Streamlit stops all Ollama calls instantly
- No user health data persisted beyond session

## Why Kafka on one laptop?

- **Decoupling:** fetcher and consumer run independently
- **Replay:** re-read topic after consumer crash or demo reset
- **Fan-out:** same stream feeds DB, future analytics, replay
- **Production narrative:** demonstrates real streaming architecture

## Why ZooKeeper (not KRaft)?

You already have a working ZooKeeper + Kafka setup on `localhost:9092`. Migrating to KRaft adds risk with zero benefit for this capstone. We keep what works.

---

*Ports & demo backup: [07_RAM_AND_DEMO.md](07_RAM_AND_DEMO.md)*
