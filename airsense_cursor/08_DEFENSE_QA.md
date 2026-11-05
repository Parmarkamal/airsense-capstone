# AirSense — Defense Q&A

Ready answers for viva. Adapt to your actual RMSE numbers and demo experience.

---

## Architecture

### Why Kafka for only 6 cities?

Kafka decouples ingestion from processing. If I add 500 stations later, only producers change — the consumer stays the same. It also enables **replay** after crashes and demonstrates production-grade streaming architecture expected in a data engineering capstone.

### Why not write directly to the database?

Direct writes couple the fetcher to storage. Kafka buffers messages when the consumer is slow or down, supports multiple independent consumers, and mirrors how real-time pipelines are built in industry.

### Why keep ZooKeeper instead of KRaft?

I already had a working ZooKeeper + Kafka installation on `localhost:9092`. Migrating to KRaft added setup risk with no benefit for a single-laptop academic project. The architecture still demonstrates message streaming correctly.

### Why TimescaleDB instead of plain PostgreSQL?

TimescaleDB adds hypertables (automatic time partitioning), continuous aggregates for fast hourly rollups, compression, and retention policies — all critical for time-series AQI data at scale.

---

## Data & APIs

### Are you compliant with WAQI terms of service?

Yes. I use my own registered token stored in `.env`, attribute WAQI on every dashboard page ("Data provided by WAQI / waqi.info"), and use CPCB/Kaggle datasets for historical ML training — not long-term caching of WAQI live feed.

### Why not train on WAQI historical data?

WAQI terms restrict redistribution and caching. CPCB open data and Kaggle provide legally usable historical datasets for academic ML training.

### How do you handle bad data?

Pydantic validation at the consumer. Invalid readings (out-of-range AQI, future timestamps, missing required fields) are **logged to file**, not inserted into TimescaleDB. This follows "data validity over volume."

---

## Machine learning

### Why LightGBM instead of LSTM?

LightGBM achieves comparable accuracy on tabular time-series with lag features, installs natively on Windows, trains in seconds, and provides interpretable feature importance. LSTMs need more data and GPU time for marginal gains on this dataset size.

### What is walk-forward validation?

Instead of random train/test split (which leaks future into past), I train on weeks 1–N and test on week N+1, sliding forward. This simulates real deployment where you only know the past.

### What is your RMSE and is it good enough?

Target RMSE < 30 AQI units (adjust with your actual MLflow result). For a health-awareness dashboard, **directional accuracy** matters most: will tomorrow be better or worse? RMSE ~20–25 correctly captures trend even if exact values drift.

### How does 48-hour recursive forecasting work?

Step 1: predict t+1 using real lag features. Step 2: predict t+2 using t+1 prediction as a lag. Error accumulates after ~12 hours — I document this limitation honestly.

### How do you prevent model regression in production?

Champion-challenger: weekly retrain produces a challenger model. It replaces production only if RMSE improves. Otherwise the current production model stays. Logged in MLflow and `ml/production/metrics.json`.

---

## GenAI & RAG

### How does RAG prevent hallucination?

1. User query is embedded
2. ChromaDB retrieves top-3 WHO/CPCB chunks by cosine similarity
3. Chunks are injected into the LLM prompt
4. System prompt forbids diagnosis and inventing statistics
5. Response must cite retrieved sources

### Why phi3:mini instead of GPT-4?

Privacy: health questions never leave the laptop. Cost: ₹0. phi3:mini fits RTX 2050 VRAM (~2.5 GB) and answers guideline-style questions well enough for this use case.

### Why not fine-tune the LLM?

RAG is cheaper, faster to implement, and grounds answers in authoritative PDFs without GPU-intensive training. Fine-tuning would require labelled Q&A pairs we don't have.

### What if the LLM gives wrong health advice?

Three mitigations: RAG grounding, explicit "not a doctor" disclaimer on every page and response, kill-switch to disable AI instantly. The app never claims to diagnose conditions.

---

## Privacy & ethics

### What is the privacy model?

100% local except WAQI API fetch and optional Telegram alerts. User health questions, chat history, embeddings, and database all stay on the laptop.

### What are the limitations?

1. Six cities (station-level, not street-level)
2. Recursive forecast error after 12+ hours
3. phi3:mini less capable than cloud LLMs
4. Training data limited to available CPCB/Kaggle coverage
5. WAQI API dependency for live data (replay mode mitigates demo risk)

---

## Operations

### What happens if WAQI is down on demo day?

`fetch_aqi_replay.py` replays a 7-day backup CSV through Kafka. The full pipeline — consumer, dashboard, forecast — works identically.

### How do Telegram alerts work?

Simple HTTP POST to Telegram Bot API when AQI exceeds threshold in `config.yaml`. No complex message queue — appropriate for a capstone alert channel.

### How would you scale this?

Add Kafka partitions and consumer instances per region; TimescaleDB read replicas for dashboard; separate Ollama server; Prometheus/Grafana for ops. The current design separates concerns so each layer scales independently.

---

## Quick numbers to memorize

| Item | Value |
|------|-------|
| Cities | 6 (Ahmedabad, Surat, Rajkot, Gandhinagar, Delhi, Mumbai) |
| Fetch frequency | Hourly |
| WAQI requests/day | ~144 (6 × 24) |
| Forecast horizon | 48 hours |
| LLM | Ollama phi3:mini |
| Embedding model | all-MiniLM-L6-v2 (384 dim) |
| Kafka topic | `aqi_raw` |
| Target RMSE | < 30 AQI units |

---

*Project brief: [01_PROJECT_BRIEF.md](01_PROJECT_BRIEF.md)*
