# Project Context & Infrastructure — AirSense Capstone

## 1. Project Identity
- **Project**: AirSense — Real-Time Urban Air Quality Forecasting & Grounded GenAI Health Advisory Platform.
- **Degree**: M.Sc. IT (Business Intelligence & Analytics), Semester 3 Capstone, Gujarat University (CPC).
- **Primary Goal**: Flawless viva defense (70/70 marks), 100% reliable local demo, zero cloud cost.

## 2. Infrastructure & Port Mapping (Windows 11)
- **TimescaleDB**: Runs in Docker on **port 5433** (Native PostgreSQL 18 is running on port 5432 — NEVER connect to 5432).
  - Database: `airsense_db`, User: `airsense`, Password: `airsense123`, Port: `5433`.
- **Kafka Broker**: Localhost on **port 9092** (ZooKeeper on port 2181).
- **Ollama LLM**: Localhost on **port 11434** (`llama3.2:3b`).
- **Streamlit Dashboard**: Localhost on **port 8501**.
- **Python**: 3.11.x (Run tests with `python -m pytest tests/` from `airsense/`).

## 3. Preserved Working State (Phases 1 to 4)
- All code in `airsense/` for Phases 1 to 4 is **100% complete and verified with 32/32 passing tests**.
- **DO NOT** rewrite, rename, refactor, or delete existing files from Phases 1–4.
- All 32 tests in `tests/` MUST continue passing after any new change.

