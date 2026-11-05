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
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger("airsense.dashboard.data")


def calculate_data_freshness(
    reading_time: datetime | None,
) -> tuple[str, str, float]:
    """
    Classify observation age for dashboard freshness badges.

    Returns:
        (badge_color, label, age_in_hours)
        - < 1 hour:  ("green", "🟢 Live (<1h old)", age)
        - 1–3 hours: ("gold",  "🟡 Delayed (1-3h old)", age)
        - > 3 hours: ("red",   "🔴 Stale (>3h old)", age)
    """
    if reading_time is None or (isinstance(reading_time, float) and pd.isna(reading_time)):
        return ("red", "🔴 Stale (>3h old)", float("inf"))

    if isinstance(reading_time, str):
        try:
            reading_time = datetime.fromisoformat(reading_time.replace("Z", "+00:00"))
        except ValueError:
            return ("red", "🔴 Stale (>3h old)", float("inf"))

    if reading_time.tzinfo is None:
        reading_time = reading_time.replace(tzinfo=timezone.utc)
    else:
        reading_time = reading_time.astimezone(timezone.utc)

    age_hours = (datetime.now(timezone.utc) - reading_time).total_seconds() / 3600.0
    if age_hours < 0:
        age_hours = 0.0

    if age_hours < 1.0:
        return ("green", "🟢 Live (<1h old)", age_hours)
    if age_hours <= 3.0:
        return ("gold", "🟡 Delayed (1-3h old)", age_hours)
    return ("red", "🔴 Stale (>3h old)", age_hours)


def get_latest_readings_all_cities(engine: Engine) -> pd.DataFrame:
    """
    Fetch the most recent reading for each city from the aqi_readings hypertable.
    Uses DISTINCT ON (city) ordered by time DESC for peak performance.
    Annotates each row with data_age_hours and freshness badge fields.
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
            data_source,
            fetched_at
        FROM aqi_readings
        ORDER BY city, time DESC;
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        if df.empty:
            return df

        colors: list[str] = []
        labels: list[str] = []
        ages: list[float] = []
        for ts in df["time"]:
            color, label, age = calculate_data_freshness(ts)
            colors.append(color)
            labels.append(label)
            ages.append(age)

        df["freshness_color"] = colors
        df["freshness_label"] = labels
        df["data_age_hours"] = ages
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


def is_replay_mode_active(df_latest: pd.DataFrame) -> bool:
    """
    Check if the dashboard is displaying replay (offline) data.

    Returns True when any of the latest city readings have
    data_source == 'Replay-Backup', indicating the historical CSV
    replay streamer was used instead of live API ingestion.

    Parameters
    ----------
    df_latest : pd.DataFrame
        The latest readings DataFrame from get_latest_readings_all_cities().

    Returns
    -------
    bool
    """
    if df_latest.empty or "data_source" not in df_latest.columns:
        return False
    return bool((df_latest["data_source"] == "Replay-Backup").any())
