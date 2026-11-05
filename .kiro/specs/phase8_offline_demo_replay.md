# Specification: Phase 8 — Offline Resilience & Disaster Recovery

## 1. Objective
Ensure the AirSense platform can be 100% reliably demonstrated during academic viva or conference presentations even if Wi-Fi disconnects, external APIs rate-limit, or internet fails completely.

## 2. Target Files
- `airsense/ingestion/fetch_aqi_replay.py`: Stream pre-saved historical CSV data through Kafka with synthetic current timestamps.
- `airsense/dashboard/app.py`: Amber "REPLAY MODE" header badge when replay is active.
- `airsense/scripts/run_offline_demo.bat`: 1-Click offline launcher script.

## 3. Tasks

### Task 8.1: Historical Replay Streamer
- Script: `airsense/ingestion/fetch_aqi_replay.py`
  - Reads `airsense/data/backup/aqi_7day_backup.csv`.
  - Replaces historical timestamps with current sliding timestamps ($t - \Delta t$).
  - Publishes readings through Kafka `aqi_raw` topic at controlled speed (1 reading per second or instantaneous batch).
  - Sets `data_source = "Replay-Backup"`.

### Task 8.2: Visual Replay Badge
- When `data_source == "Replay-Backup"` in database:
  - Streamlit dashboard displays prominent warning banner:
    `⚠️ REPLAY MODE ACTIVE: Displaying simulated historical sensor stream (Offline Resilience Mode)`.

### Task 8.3: 1-Click Offline Demo Script
- Create `airsense/scripts/run_offline_demo.bat`:
  1. Starts TimescaleDB container.
  2. Runs replay feeder to populate database.
  3. Launches Streamlit dashboard with local Ollama.
  4. Requires zero internet connectivity.

## 4. Acceptance Criteria
- [ ] Running `fetch_aqi_replay.py` populates database without internet.
- [ ] Dashboard displays amber REPLAY badge.
- [ ] All 32 existing tests pass.

