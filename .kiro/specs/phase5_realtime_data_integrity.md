# Specification: Phase 5 — Real-Time Data Integrity & Hybrid Ingestion

## 1. Objective
Eliminate stale data (e.g. Ahmedabad, Mumbai, Pune, Gandhinagar WAQI feeds that disconnected or have months-old data) by implementing a smart hybrid ingestion engine that falls back to the Open-Meteo Air Quality API when WAQI data is older than 2 hours or unavailable.

## 2. Target Files
- `airsense/ingestion/fetch_aqi.py`: Add Open-Meteo fallback logic with GPS coordinates.
- `airsense/dashboard/data_access.py`: Add data freshness calculation (`data_age_hours`).
- `airsense/dashboard/app.py`: Display visual freshness badges (🟢 Fresh <1h, 🟡 Delayed 1-3h, 🔴 Stale >3h).
- `airsense/ingestion/fetch_daemon.py`: Background looping service with heartbeat logging.

## 3. Task Breakdown

### Task 5.1: Hybrid Ingestion Engine (`ingestion/fetch_aqi.py`)
- Function: `fetch_open_meteo_reading(city: CityConfig, timeout: int, session: requests.Session) -> dict[str, Any]`
  - URL: `https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm2_5,pm10,nitrogen_dioxide,carbon_monoxide,sulphur_dioxide,ozone`
  - Parse current hourly readings for all available pollutants.
  - Set `data_source = "Open-Meteo-Live"`.
  - Set `station_id = f"open-meteo-{city.slug}"`.
- Fallback Trigger in `fetch_city_reading`:
  - Fetch WAQI first.
  - If WAQI throws HTTP error or returns non-ok status: call `fetch_open_meteo_reading`.
  - If WAQI returns a timestamp older than 2 hours: log warning and switch to `fetch_open_meteo_reading`.
  - Fallback is transparent and produces the same Pydantic-compatible JSON schema.

### Task 5.2: Freshness Monitoring (`dashboard/data_access.py`)
- Add helper `calculate_data_freshness(reading_time: datetime) -> tuple[str, str, float]`
  - Returns `(badge_color, label, age_in_hours)`.
  - `< 1 hour`: `("green", "🟢 Live (<1h old)", age)`
  - `1 - 3 hours`: `("gold", "🟡 Delayed (1-3h old)", age)`
  - `> 3 hours`: `("red", "🔴 Stale (>3h old)", age)`

### Task 5.3: Visual Badges on KPI Cards (`dashboard/app.py`)
- Render freshness badge directly on the city metric card and GIS map tooltip.

## 4. Acceptance Criteria
- [ ] Running `python ingestion/fetch_aqi.py` fetches 100% of 6 cities with current day's timestamp.
- [ ] No Pydantic validation errors in Kafka consumer.
- [ ] All 32 existing tests in `pytest tests/` continue to pass.
- [ ] New unit test `tests/test_hybrid_fetch.py` passes with mocked WAQI and Open-Meteo responses.
