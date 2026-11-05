-- ─────────────────────────────────────────────────────────────────────────────
-- AirSense — Database Initialisation Script
-- Week 2: Creates TimescaleDB hypertable and all supporting structures
--
-- This file is automatically executed when the Docker container first starts
-- (mounted at /docker-entrypoint-initdb.d/01_init_db.sql).
--
-- To run manually:
--   psql -U airsense -d airsense_db -f scripts/init_db.sql
-- ─────────────────────────────────────────────────────────────────────────────

-- ── Enable TimescaleDB extension ────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ── Raw AQI readings (hypertable) ───────────────────────────────────────────
-- One row per city per API fetch (typically every hour).
-- Partitioned by day for fast time-range queries.
CREATE TABLE IF NOT EXISTS aqi_readings (
    time                TIMESTAMPTZ        NOT NULL,
    city                TEXT               NOT NULL,
    city_display_name   TEXT               NOT NULL,
    station_id          TEXT,
    country             TEXT               DEFAULT 'IN',
    aqi                 DOUBLE PRECISION,
    pm25                DOUBLE PRECISION,
    pm10                DOUBLE PRECISION,
    no2                 DOUBLE PRECISION,
    co                  DOUBLE PRECISION,
    so2                 DOUBLE PRECISION,
    o3                  DOUBLE PRECISION,
    lat                 DOUBLE PRECISION,
    lon                 DOUBLE PRECISION,
    data_source         TEXT               DEFAULT 'WAQI',
    schema_version      TEXT               DEFAULT '1.0',
    fetched_at          TIMESTAMPTZ        DEFAULT NOW()
);

-- Convert to TimescaleDB hypertable (1-day chunks = fast queries, tiny footprint)
SELECT create_hypertable(
    'aqi_readings',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists       => TRUE
);

-- Composite index: queries almost always filter by city + time range
CREATE INDEX IF NOT EXISTS idx_aqi_readings_city_time
    ON aqi_readings (city, time DESC);

-- Index for map/dashboard queries that fetch the latest reading per city
CREATE INDEX IF NOT EXISTS idx_aqi_readings_time_desc
    ON aqi_readings (time DESC);

-- ── 48-hour AQI forecasts (regular table) ───────────────────────────────────
-- Written by the LightGBM retraining script (Week 5).
CREATE TABLE IF NOT EXISTS aqi_forecasts (
    forecast_time       TIMESTAMPTZ        NOT NULL,
    city                TEXT               NOT NULL,
    predicted_aqi       DOUBLE PRECISION   NOT NULL,
    model_version       TEXT,
    generated_at        TIMESTAMPTZ        DEFAULT NOW(),
    PRIMARY KEY (forecast_time, city)
);

CREATE INDEX IF NOT EXISTS idx_aqi_forecasts_city_time
    ON aqi_forecasts (city, forecast_time DESC);

-- ── Validation error log ─────────────────────────────────────────────────────
-- Invalid Kafka messages that failed Pydantic validation are logged here.
CREATE TABLE IF NOT EXISTS aqi_validation_errors (
    id                  BIGSERIAL          PRIMARY KEY,
    received_at         TIMESTAMPTZ        DEFAULT NOW(),
    raw_message         TEXT,
    error_detail        TEXT
);

-- ── Hourly continuous aggregate (for Power BI — Week 10) ────────────────────
-- Pre-computes hourly averages per city. Zero query cost on dashboards.
CREATE MATERIALIZED VIEW IF NOT EXISTS aqi_hourly_avg
WITH (timescaledb.continuous) AS
    SELECT
        time_bucket('1 hour', time) AS bucket,
        city,
        city_display_name,
        AVG(aqi)   AS avg_aqi,
        AVG(pm25)  AS avg_pm25,
        AVG(pm10)  AS avg_pm10,
        COUNT(*)   AS reading_count
    FROM aqi_readings
    GROUP BY bucket, city, city_display_name
WITH NO DATA;

-- Refresh policy: keep the aggregate up to date automatically
SELECT add_continuous_aggregate_policy(
    'aqi_hourly_avg',
    start_offset  => INTERVAL '3 hours',
    end_offset    => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- ── Seed message ─────────────────────────────────────────────────────────────
DO $$
BEGIN
    RAISE NOTICE '
╔══════════════════════════════════════════════════════╗
║  AirSense DB initialised successfully!               ║
║                                                      ║
║  Tables   : aqi_readings (hypertable)               ║
║             aqi_forecasts                           ║
║             aqi_validation_errors                   ║
║  View     : aqi_hourly_avg (continuous aggregate)   ║
║                                                      ║
║  Next: run consumer/kafka_consumer.py               ║
╚══════════════════════════════════════════════════════╝
';
END
$$;
