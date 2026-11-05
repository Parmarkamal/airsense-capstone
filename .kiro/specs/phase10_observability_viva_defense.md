# Specification: Phase 10 — System Observability & Viva Polish

## 1. Objective
Achieve maximum marks (70/70) in the capstone viva defense by implementing a real-time "Pipeline Health" tab in the dashboard, conducting automated regression tests across all modules, and rehearsing the 40 viva defense questions.

## 2. Target Files
- `airsense/dashboard/components/health_view.py`: System health tab showing service latencies and health badges.
- `airsense/scripts/run_viva_check.bat`: 1-Click diagnostic verification script.
- `AirSense_Project_Status.md`: Final completion report and viva rehearsal log.

## 3. Tasks

### Task 10.1: Pipeline Health Tab (`dashboard/components/health_view.py`)
- Real-time diagnostic monitors:
  - **Kafka Broker**: Ping localhost:9092, check topic partition lag.
  - **TimescaleDB**: Query latency (ms), hypertable chunk count, total row count.
  - **Ollama LLM**: Model loaded status (`llama3.2:3b`), memory footprint, inferencing ping.
  - **Data Ingestion Daemon**: Time since last successful ingestion batch, heartbeat status.

### Task 10.2: Automated Regression Suite
- Run `python -m pytest tests/` covering all modules:
  - Ingestion & validation (`test_validate.py`)
  - Forecasting & baselines (`test_forecast.py`)
  - RAG advisor & safety guardrails (`test_rag.py`)
  - Overall test count: 35+ tests passing.

### Task 10.3: Viva Defense Readiness Checklist
- Verify student can answer the 4 key examiner questions:
  1. *Why TimescaleDB instead of MongoDB?*
  2. *Why LightGBM instead of LSTM or Prophet?*
  3. *Why RAG instead of direct prompting or fine-tuning?*
  4. *How does the system handle sensor disconnection in real-time?*

## 4. Acceptance Criteria
- [ ] Pipeline Health tab displays green status indicators for all services.
- [ ] 100% of all unit and integration tests pass.
- [ ] Project ready for 70/70 viva submission.

