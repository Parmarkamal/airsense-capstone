"""
AirSense — Dashboard Data Access Layer
File: dashboard/data_access.py
Week: 3

Handles all database reads from TimescaleDB for the Streamlit dashboard:
  - Latest readings for all configured cities
  - Historical time-series (past 24 hours) for a selected city
  - Continuous aggregate summary
  - Health/pipeline statistics
"""

from __future__ import annotations

import logging
from typing import Any
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger("airsense.dashboard.data")


def get_latest_readings_all_cities(engine: Engine) -> pd.DataFrame:
    """
    Fetch the most recent reading for each city from the aqi_readings hypertable.
    Uses DISTINCT ON (city) ordered by time DESC for peak performance.
    """
    query = text("""
        SELECT DISTINCT ON (city)
            city,
            city_display_name,
            station_id,
            time,
            aqi,
            pm25,
            pm10,
            no2,
            co,
            so2,
            o3,
            lat,
            lon,
            fetched_at
        FROM aqi_readings
        ORDER BY city, time DESC;
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df
    except Exception as exc:
        logger.error("Failed to query latest readings: %s", exc)
        return pd.DataFrame()


def get_city_history(engine: Engine, city_slug: str, limit: int = 48) -> pd.DataFrame:
    """
    Fetch recent chronological readings for a specific city.
    Returns DataFrame sorted chronologically (time ASC).
    """
    query = text("""
        SELECT
            time,
            aqi,
            pm25,
            pm10,
            no2,
            co,
            so2,
            o3
        FROM aqi_readings
        WHERE city = :city_slug
        ORDER BY time DESC
        LIMIT :limit;
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"city_slug": city_slug, "limit": limit})
        if not df.empty:
            df = df.sort_values(by="time", ascending=True).reset_index(drop=True)
        return df
    except Exception as exc:
        logger.error("Failed to query history for %s: %s", city_slug, exc)
        return pd.DataFrame()


def get_pipeline_stats(engine: Engine) -> dict[str, Any]:
    """
    Return operational counts: total readings, error count, and last ingested event time.
    """
    stats = {
        "total_readings": 0,
        "total_errors": 0,
        "latest_fetch": None,
    }
    try:
        with engine.connect() as conn:
            readings_res = conn.execute(text("SELECT COUNT(*), MAX(fetched_at) FROM aqi_readings;")).fetchone()
            if readings_res:
                stats["total_readings"] = readings_res[0] or 0
                stats["latest_fetch"] = readings_res[1]

            err_res = conn.execute(text("SELECT COUNT(*) FROM aqi_validation_errors;")).fetchone()
            if err_res:
                stats["total_errors"] = err_res[0] or 0
    except Exception as exc:
        logger.warning("Could not load pipeline stats: %s", exc)
    return stats


def get_city_forecast(engine: Engine, city_slug: str) -> pd.DataFrame:
    """Query the latest 48-hour forecast for a city from aqi_forecasts."""
    query = text("""
        SELECT forecast_time, predicted_aqi, model_version, generated_at
        FROM aqi_forecasts
        WHERE city = :city_slug
        ORDER BY forecast_time ASC
        LIMIT 48;
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"city_slug": city_slug})
        return df
    except Exception as exc:
        logger.error("Failed to query forecast for %s: %s", city_slug, exc)
        return pd.DataFrame()
