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
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
from typing import Any

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from common.cpcb_calculator import (
    calculate_cpcb_naqi,
    check_data_completeness,
    convert_co_ug_to_mg,
    get_cpcb_category,
)

logger = logging.getLogger("airsense.dashboard.data")


def format_human_duration(total_seconds: float) -> str:
    """
    Format a time delta into clean, human-friendly natural English.
    Examples:
      - < 2 mins:  'just now'
      - 45 mins:   '45 mins ago'
      - 75 mins:   '1 hr 15 mins ago'
      - 150 mins:  '2 hrs 30 mins ago'
      - 24 hrs+:   '1 day ago' / 'X days ago'
    """
    if total_seconds < 0:
        total_seconds = 0.0
    mins = int(round(total_seconds / 60.0))
    if mins < 2:
        return "just now"
    if mins < 60:
        return f"{mins} mins ago"

    hours = mins // 60
    rem_mins = mins % 60
    h_str = "1 hr" if hours == 1 else f"{hours} hrs"
    if rem_mins == 0:
        return f"{h_str} ago"
    return f"{h_str} {rem_mins} mins ago"


def calculate_data_freshness(
    reading_time: datetime | None,
) -> tuple[str, str, float]:
    """
    Classify observation age for dashboard freshness badges.
    CPCB CAAQMS ground stations report on 1-2 hour publication cycles.

    Returns:
        (badge_color, label, age_in_hours)
        - < 2.5 hours:  ("green", "🟢 Live (10:30 PM IST · 45 mins ago)", age)
        - 2.5–6 hours: ("gold",  "🟡 Delayed (08:30 PM IST · 2 hrs 30 mins ago)", age)
        - > 6 hours:   ("red",   "🔴 Stale (>6h old)", age)
    """
    if reading_time is None or (isinstance(reading_time, float) and pd.isna(reading_time)):
        return ("red", "🔴 Stale (>6h old)", float("inf"))

    if isinstance(reading_time, str):
        try:
            reading_time = datetime.fromisoformat(reading_time.replace("Z", "+00:00"))
        except ValueError:
            return ("red", "🔴 Stale (>6h old)", float("inf"))

    if reading_time.tzinfo is None:
        reading_time = reading_time.replace(tzinfo=timezone.utc)
    else:
        reading_time = reading_time.astimezone(timezone.utc)

    diff_sec = max(0.0, (datetime.now(timezone.utc) - reading_time).total_seconds())
    age_hours = diff_sec / 3600.0
    time_ago_str = format_human_duration(diff_sec)

    # Display local Indian Standard Time (IST, UTC+5:30) for clear human recognition
    ist_time_str = reading_time.astimezone(IST).strftime("%I:%M %p IST")

    if age_hours < 2.5:
        return ("green", f"🟢 Live ({ist_time_str} · {time_ago_str})", age_hours)
    if age_hours <= 6.0:
        return ("gold", f"🟡 Delayed ({ist_time_str} · {time_ago_str})", age_hours)
    return ("red", f"🔴 Stale ({ist_time_str} · {time_ago_str})", age_hours)


def get_provenance_badge(row: pd.Series | dict[str, Any]) -> dict[str, str]:
    """Return badge text, description, and styling for data provenance."""
    src_type = row.get("source_type") or ""
    data_source = row.get("data_source") or ""
    operator = row.get("station_operator") or ""

    if src_type == "ground_station" or data_source == "WAQI":
        op = operator if operator and "WAQI" not in operator else "CPCB / SPCB Ground Station"
        return {
            "badge": f"🏛️ Ground Station ({op})",
            "tooltip": "Physical CAAQMS ground station sensor observation",
            "type": "ground_station",
            "border_color": "#10B981",
        }
    elif src_type == "atmospheric_model" or "Open-Meteo" in data_source:
        return {
            "badge": "🛰️ Atmospheric Model (CAMS Global ~45km)",
            "tooltip": "ECMWF Copernicus Atmosphere Monitoring Service (IFS-AER model simulation on ~45 km grid)",
            "type": "model",
            "border_color": "#3B82F6",
        }
    else:
        return {
            "badge": "📼 Offline Replay Stream",
            "tooltip": "Simulated sensor stream from historical reference records",
            "type": "replay",
            "border_color": "#F59E0B",
        }


def get_latest_readings_all_cities(engine: Engine) -> pd.DataFrame:
    """
    Fetch the most recent reading for each city from the aqi_readings hypertable.
    Uses DISTINCT ON (city) ordered by time DESC for peak performance.
    Annotates each row with data_age_hours, freshness badge fields, and CPCB NAQI.
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
            fetched_at,
            cpcb_aqi,
            prominent_pollutant,
            source_type,
            station_operator,
            calculation_method,
            observation_age_hours
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
        cpcb_vals: list[float | None] = []
        prominents: list[str | None] = []

        for _, row in df.iterrows():
            color, label, age = calculate_data_freshness(row.get("time"))
            colors.append(color)
            labels.append(label)
            ages.append(age)

            # Ensure cpcb_aqi is computed if missing from older records
            val = row.get("cpcb_aqi")
            prom = row.get("prominent_pollutant")
            if pd.isna(val) or val is None:
                co_val = row.get("co")
                if co_val is not None and not pd.isna(co_val) and co_val > 50.0:
                    co_val = convert_co_ug_to_mg(co_val)
                calc = calculate_cpcb_naqi(
                    {
                        "pm25": None if pd.isna(row.get("pm25")) else float(row.get("pm25")),
                        "pm10": None if pd.isna(row.get("pm10")) else float(row.get("pm10")),
                        "no2": None if pd.isna(row.get("no2")) else float(row.get("no2")),
                        "co": None if pd.isna(co_val) else float(co_val),
                        "so2": None if pd.isna(row.get("so2")) else float(row.get("so2")),
                        "o3": None if pd.isna(row.get("o3")) else float(row.get("o3")),
                    },
                    is_indicative=True,
                )
                val = calc.get("aqi")
                prom = calc.get("prominent_pollutant")

            cpcb_vals.append(val)
            prominents.append(prom)

        df["freshness_color"] = colors
        df["freshness_label"] = labels
        df["data_age_hours"] = ages
        df["cpcb_aqi"] = cpcb_vals
        df["prominent_pollutant"] = prominents
        return df
    except Exception as exc:
        logger.error("Failed to query latest readings: %s", exc)
        return pd.DataFrame()


def get_city_rolling_cpcb_aqi(engine: Engine, city_slug: str) -> dict[str, Any]:
    """
    Compute official 24-hour rolling CPCB NAQI for a city following CPCB 2014 guidelines:
      - 24-hour averages for PM2.5, PM10, NO2, SO2 (requires >= 16 valid hourly readings)
      - 8-hour averages for CO, O3 (requires >= 6 valid hourly readings)
      - At least 3 pollutants with at least one PM pollutant
    """
    query = text("""
        SELECT time, pm25, pm10, no2, co, so2, o3
        FROM aqi_readings
        WHERE city = :city_slug
        ORDER BY time DESC
        LIMIT 24;
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"city_slug": city_slug})
        if df.empty:
            return {
                "aqi": None,
                "category": "No Data",
                "color": "#6B7280",
                "prominent_pollutant": None,
                "is_valid": False,
                "valid_hours": 0,
                "reason": f"No readings found for {city_slug}.",
            }

        valid_24h_count = len(df)
        pm25_ok, pm25_avg = check_data_completeness(df["pm25"].tolist(), min_required=16)
        pm10_ok, pm10_avg = check_data_completeness(df["pm10"].tolist(), min_required=16)
        no2_ok, no2_avg = check_data_completeness(df["no2"].tolist(), min_required=16)
        so2_ok, so2_avg = check_data_completeness(df["so2"].tolist(), min_required=16)

        # 8h window for CO and O3 (normalizing any legacy µg/m³ CO to mg/m³ before averaging)
        co_8h_raw = df["co"].head(8).tolist()
        co_8h_norm = [
            convert_co_ug_to_mg(v) if (v is not None and v > 50.0) else v
            for v in co_8h_raw
        ]
        o3_8h = df["o3"].head(8).tolist()
        co_ok, co_avg = check_data_completeness(co_8h_norm, min_required=6)
        o3_ok, o3_avg = check_data_completeness(o3_8h, min_required=6)

        averages = {
            "pm25": pm25_avg if pm25_ok else None,
            "pm10": pm10_avg if pm10_ok else None,
            "no2": no2_avg if no2_ok else None,
            "co": co_avg if co_ok else None,
            "so2": so2_avg if so2_ok else None,
            "o3": o3_avg if o3_ok else None,
        }

        calc = calculate_cpcb_naqi(averages, is_indicative=False)
        calc["valid_hours"] = valid_24h_count
        return calc
    except Exception as exc:
        logger.error("Failed to calculate rolling CPCB NAQI for %s: %s", city_slug, exc)
        return {
            "aqi": None,
            "category": "Error",
            "color": "#6B7280",
            "prominent_pollutant": None,
            "is_valid": False,
            "valid_hours": 0,
            "reason": str(exc),
        }


def get_city_history(engine: Engine, city_slug: str, limit: int = 48) -> pd.DataFrame:
    """
    Fetch recent chronological readings for a specific city.
    Restricts results strictly to the contiguous recent period (last 28 hours
    relative to the latest reading) so old historical clusters from weeks ago
    are never joined across multi-day voids.
    Deduplicates identical hourly timestamps via DISTINCT ON (r.time).
    Populates 'aqi' with official CPCB NAQI (COALESCE(cpcb_aqi, aqi)) for 100%
    metric consistency across cards, gauges, charts, and forecasts.
    """
    query = text("""
        WITH latest AS (
            SELECT MAX(time) AS max_time
            FROM aqi_readings
            WHERE city = :city_slug
        ),
        deduped AS (
            SELECT DISTINCT ON (r.time)
                r.time,
                COALESCE(r.cpcb_aqi, r.aqi) AS aqi,
                r.cpcb_aqi,
                r.pm25,
                r.pm10,
                r.no2,
                r.co,
                r.so2,
                r.o3,
                r.prominent_pollutant,
                r.data_source
            FROM aqi_readings r, latest
            WHERE r.city = :city_slug
              AND latest.max_time IS NOT NULL
              AND r.time >= latest.max_time - INTERVAL '28 hours'
            ORDER BY r.time ASC, r.fetched_at DESC
        )
        SELECT * FROM deduped ORDER BY time ASC;
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"city_slug": city_slug})
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
    """
    Query the latest 48-hour forecast for a city from aqi_forecasts.
    Filters out historical forecast records older than 1 hour.
    If forecasts are missing or expired (< 12 future hours), auto-regenerates
    them on-the-fly using the production LightGBM model so the dashboard
    NEVER displays obsolete predictions, even after weeks of downtime.
    """
    query = text("""
        SELECT forecast_time, predicted_aqi, model_version, generated_at
        FROM aqi_forecasts
        WHERE city = :city_slug AND forecast_time >= NOW() - INTERVAL '1 hour'
        ORDER BY forecast_time ASC
        LIMIT 48;
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"city_slug": city_slug})

        # Self-healing: auto-regenerate fresh 48h projections if table has expired
        if len(df) < 12:
            try:
                from ml.training.predict_forecast import run_all_forecasts_and_save
                logger.info("Forecast for %s has <12 future hours; auto-regenerating fresh 48h forecast...", city_slug)
                run_all_forecasts_and_save(engine)
                with engine.connect() as conn:
                    df = pd.read_sql(query, conn, params={"city_slug": city_slug})
            except Exception as auto_exc:
                logger.warning("Auto-forecast regeneration fallback error: %s", auto_exc)

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
