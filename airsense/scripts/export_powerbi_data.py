"""
AirSense — Power BI Star Schema Data Exporter
File: scripts/export_powerbi_data.py
Phase: 9 (Business Intelligence & Executive Analytics)

Extracts air quality readings from TimescaleDB (with offline CSV fallback)
and models them into a formal Ralph Kimball Star Schema for Power BI Desktop:
  1. dim_city.csv             — City dimension with state, tier, and GPS coordinates
  2. dim_date.csv             — Date dimension with calendar hierarchy
  3. dim_time.csv             — Time dimension with diurnal flags
  4. fact_aqi_readings.csv     — Fact table with foreign keys and granular pollutant metrics

Usage:
  python scripts/export_powerbi_data.py [--output-dir DIR] [--limit N]
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import CityConfig, get_cities, load_settings


def get_engine_safe(settings: dict[str, Any]) -> Any:
    """Safely connect to database or return None if offline."""
    try:
        from consumer.db import create_db_engine
        return create_db_engine(settings)
    except Exception:
        return None


def build_dim_city(cities: list[CityConfig]) -> pd.DataFrame:
    """Build the Dim_City dimension table with economic tiers and geography."""
    rows = []
    for idx, city in enumerate(cities, start=1):
        rows.append({
            "CityKey": idx,
            "CitySlug": city.slug,
            "CityName": city.display_name,
            "State": city.state,
            "Tier": f"Tier {city.tier}",
            "TierNumber": city.tier,
            "Latitude": city.lat,
            "Longitude": city.lon,
            "Country": "IN",
        })
    return pd.DataFrame(rows)


def build_dim_date(date_series: pd.Series) -> pd.DataFrame:
    """Build the Dim_Date dimension table with calendar attributes."""
    unique_dates = pd.to_datetime(date_series.dropna().unique())
    if len(unique_dates) == 0:
        unique_dates = pd.date_range(start="2026-10-01", end="2026-11-30", freq="D")

    rows = []
    for dt in sorted(unique_dates):
        d = dt.date()
        date_key = int(d.strftime("%Y%m%d"))
        rows.append({
            "DateKey": date_key,
            "FullDate": d.isoformat(),
            "Year": d.year,
            "Quarter": f"Q{(d.month - 1) // 3 + 1}",
            "Month": d.month,
            "MonthName": d.strftime("%B"),
            "MonthShort": d.strftime("%b"),
            "DayOfMonth": d.day,
            "DayOfWeek": d.isoweekday(),
            "DayName": d.strftime("%A"),
            "IsWeekend": 1 if d.isoweekday() in (6, 7) else 0,
        })
    return pd.DataFrame(rows).drop_duplicates(subset=["DateKey"]).reset_index(drop=True)


def build_dim_time() -> pd.DataFrame:
    """Build the Dim_Time dimension table for all 24 hours of the day."""
    rows = []
    for hour in range(24):
        time_key = hour * 100
        time_str = f"{hour:02d}:00"
        
        # Rush hour: morning 8-11 and evening 17-20
        is_rush = 1 if (8 <= hour <= 11 or 17 <= hour <= 20) else 0
        # Day vs Night: 06:00 to 18:00
        day_night = "Day" if (6 <= hour < 18) else "Night"

        rows.append({
            "TimeKey": time_key,
            "Hour24": hour,
            "TimeDisplay": time_str,
            "Period": "AM" if hour < 12 else "PM",
            "DayNight": day_night,
            "IsRushHour": is_rush,
        })
    return pd.DataFrame(rows)


def extract_raw_readings(settings: dict[str, Any], limit: int = 5000) -> pd.DataFrame:
    """
    Extract raw sensor readings from TimescaleDB.
    Falls back automatically to backup CSV if database is offline.
    """
    engine = get_engine_safe(settings)
    df = pd.DataFrame()

    if engine is not None:
        try:
            sql = f"""
                SELECT time, city, station_id, data_source, aqi, pm25, pm10, no2, co, so2, o3, lat, lon,
                       cpcb_aqi, prominent_pollutant, source_type, station_operator
                FROM aqi_readings
                ORDER BY time DESC
                LIMIT {limit};
            """
            with engine.connect() as conn:
                df = pd.read_sql(sql, conn)
        except Exception:
            df = pd.DataFrame()

    if df.empty:
        # Fallback to local 7-day backup CSV
        backup_csv = PROJECT_ROOT / "data" / "backup" / "aqi_7day_backup.csv"
        if backup_csv.exists():
            df = pd.read_csv(backup_csv)

    return df


def build_fact_aqi_readings(
    raw_df: pd.DataFrame,
    dim_city: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the central Fact_AQI_Readings table joined with CityKey, DateKey, and TimeKey.
    """
    if raw_df.empty:
        return pd.DataFrame()

    df = raw_df.copy()
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df = df.dropna(subset=["time", "city"]).sort_values("time")

    # CityKey mapping
    slug_to_key = dict(zip(dim_city["CitySlug"], dim_city["CityKey"]))
    df["CityKey"] = df["city"].map(slug_to_key).fillna(1).astype(int)

    # DateKey & TimeKey
    df["DateKey"] = df["time"].dt.strftime("%Y%m%d").astype(int)
    df["TimeKey"] = (df["time"].dt.hour * 100).astype(int)

    # Combustion Ratio: PM2.5 / PM10
    combustion_ratio = []
    for _, row in df.iterrows():
        pm25 = row.get("pm25")
        pm10 = row.get("pm10")
        if pd.notna(pm25) and pd.notna(pm10) and float(pm10) > 0:
            combustion_ratio.append(round(float(pm25) / float(pm10), 3))
        else:
            combustion_ratio.append(None)
    df["CombustionRatio"] = combustion_ratio

    # Assign surrogate ReadingID
    df["ReadingID"] = range(1, len(df) + 1)

    # Ensure CPCB and provenance columns always exist with clean fallbacks
    if "cpcb_aqi" not in df.columns:
        df["cpcb_aqi"] = df["aqi"]
    else:
        df["cpcb_aqi"] = df["cpcb_aqi"].fillna(df["aqi"])

    if "prominent_pollutant" not in df.columns:
        df["prominent_pollutant"] = "PM2.5"
    else:
        df["prominent_pollutant"] = df["prominent_pollutant"].fillna("PM2.5")

    if "source_type" not in df.columns:
        df["source_type"] = "ground_station"
    else:
        df["source_type"] = df["source_type"].fillna("ground_station")

    if "station_operator" not in df.columns:
        df["station_operator"] = "CPCB / SPCB"
    else:
        df["station_operator"] = df["station_operator"].fillna("CPCB / SPCB")

    fact_cols = [
        "ReadingID",
        "DateKey",
        "TimeKey",
        "CityKey",
        "aqi",
        "cpcb_aqi",
        "prominent_pollutant",
        "pm25",
        "pm10",
        "no2",
        "co",
        "so2",
        "o3",
        "CombustionRatio",
        "data_source",
        "source_type",
        "station_operator",
    ]
    available_cols = [c for c in fact_cols if c in df.columns]
    fact_df = df[available_cols].rename(columns={
        "aqi": "AQI",
        "cpcb_aqi": "CPCB_AQI",
        "prominent_pollutant": "ProminentPollutant",
        "pm25": "PM25",
        "pm10": "PM10",
        "no2": "NO2",
        "co": "CO",
        "so2": "SO2",
        "o3": "O3",
        "data_source": "DataSource",
        "source_type": "SourceType",
        "station_operator": "StationOperator",
    })
    return fact_df


def export_star_schema(output_dir: Path | None = None, limit: int = 5000) -> dict[str, Path]:
    """Run full ETL and export Kimball Star Schema CSVs for Power BI."""
    settings = load_settings()
    cities = get_cities(settings)
    out_dir = output_dir or (PROJECT_ROOT / "data" / "powerbi")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Build Dimensions
    dim_city = build_dim_city(cities)
    dim_time = build_dim_time()

    # 2. Extract Raw Telemetry
    raw_df = extract_raw_readings(settings, limit=limit)

    # 3. Build Date Dimension from observed data
    date_series = raw_df["time"] if not raw_df.empty else pd.Series()
    dim_date = build_dim_date(date_series)

    # 4. Build Fact Table
    fact_df = build_fact_aqi_readings(raw_df, dim_city)

    # 5. Export to CSV
    paths = {
        "dim_city": out_dir / "dim_city.csv",
        "dim_date": out_dir / "dim_date.csv",
        "dim_time": out_dir / "dim_time.csv",
        "fact_aqi_readings": out_dir / "fact_aqi_readings.csv",
    }

    dim_city.to_csv(paths["dim_city"], index=False)
    dim_date.to_csv(paths["dim_date"], index=False)
    dim_time.to_csv(paths["dim_time"], index=False)
    fact_df.to_csv(paths["fact_aqi_readings"], index=False)

    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Export AirSense Star Schema for Power BI")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory to save CSVs")
    parser.add_argument("--limit", type=int, default=5000, help="Max rows to export")
    args = parser.parse_args()

    paths = export_star_schema(output_dir=args.output_dir, limit=args.limit)
    print("========================================================")
    print("  AirSense — Power BI Star Schema Export Complete")
    print("========================================================")
    for name, p in paths.items():
        print(f"  • {name:<18} -> {p}")
    print("========================================================")


if __name__ == "__main__":
    main()
