# AirSense — Folder Structure

Final layout for `airsense/` (code) and `airsense_cursor/` (instructions).

---

## Repository layout

```text
capstone_project/
├── airsense_cursor/              ← Instruction pack (you read these)
│   ├── 00_START_HERE.md
│   ├── 01_PROJECT_BRIEF.md
│   ├── … (all guide .md files)
│   └── CHECKLIST.md
│
├── airsense/                     ← Application code
│   ├── .env                      ← Secrets (never commit)
│   ├── .env.example
│   ├── .gitignore
│   ├── README.md
│   ├── config.yaml               ← Cities, Kafka, ML, alert thresholds
│   ├── requirements.txt
│   ├── docker-compose.yml        ← Week 2
│   ├── start_demo.bat            ← Week 12
│   ├── check_system.py           ← Week 12
│   │
│   ├── common/
│   │   ├── config.py             ← Load YAML + env
│   │   └── logging_setup.py
│   │
│   ├── ingestion/
│   │   ├── fetch_aqi.py          ← Week 1 ✅
│   │   └── fetch_aqi_replay.py   ← Week 12 stub
│   │
│   ├── consumer/
│   │   ├── consumer.py           ← Week 2
│   │   └── models.py             ← Week 2 Pydantic
│   │
│   ├── sql/
│   │   ├── 001_create_hypertable.sql
│   │   ├── 002_create_forecasts.sql
│   │   ├── 003_continuous_aggregates.sql
│   │   └── 004_retention_policy.sql
│   │
│   ├── ml/
│   │   ├── training/
│   │   │   ├── train_forecast.py
│   │   │   ├── predict_forecast.py
│   │   │   └── features.py
│   │   ├── staging/
│   │   ├── production/
│   │   └── mlruns/
│   │
│   ├── mlops/
│   │   ├── retrain_forecast.py
│   │   └── telegram_alert.py
│   │
│   ├── rag/
│   │   ├── build_knowledge_base.py
│   │   └── retriever.py
│   │
│   ├── agent/
│   │   └── health_advisor.py
│   │
│   ├── dashboard/
│   │   ├── app.py
│   │   └── components/
│   │
│   ├── scripts/
│   │   ├── test_waqi_kafka.py    ← Week 1 ✅
│   │   └── get_telegram_chat_id.py
│   │
│   ├── data/
│   │   ├── docs/                 ← WHO/CPCB PDFs
│   │   ├── chroma_db/
│   │   ├── historical/           ← CPCB/Kaggle CSV
│   │   └── backup/
│   │       └── aqi_7day_backup.csv
│   │
│   ├── notebooks/
│   │   ├── 01_exploratory_analysis.ipynb
│   │   ├── 02_feature_engineering.ipynb
│   │   └── 03_model_evaluation.ipynb
│   │
│   ├── tests/
│   │   ├── test_validation.py
│   │   ├── test_rag.py
│   │   └── test_forecast.py
│   │
│   ├── docs/
│   │   ├── screenshots/
│   │   └── airsense_demo.mp4
│   │
│   └── logs/                     ← Runtime logs (gitignored)
│
└── airsense/ (planning docs — pre-existing)
    ├── AirSense_Master_Plan.md
    └── …
```

---

## Module responsibilities

| Folder | Single responsibility |
|--------|----------------------|
| `ingestion/` | External API → Kafka only |
| `consumer/` | Kafka → validation → DB only |
| `ml/` | Training, models, MLflow artifacts |
| `mlops/` | Scheduled retrain, alerts |
| `rag/` | PDF indexing and retrieval |
| `agent/` | LangChain + Ollama orchestration |
| `dashboard/` | Streamlit UI only |
| `common/` | Shared config/logging (no business logic) |
| `scripts/` | One-off utilities and health checks |

---

## Config vs secrets

| File | Contains | Committed? |
|------|----------|------------|
| `config.yaml` | Cities, ports, thresholds, model paths | ✅ Yes |
| `.env` | WAQI token, DB password, Telegram token | ❌ Never |
| `.env.example` | Placeholder keys | ✅ Yes |

---

## Adding a new city

Edit `config.yaml` only:

```yaml
waqi:
  cities:
    - slug: vadodara
      display_name: "Vadodara"
      lat: 22.3072
      lon: 73.1812
```

No code changes required — fetcher reads the list dynamically.

---

*Week-by-week build order: [03_WEEK_BY_WEEK_PLAN.md](03_WEEK_BY_WEEK_PLAN.md)*
