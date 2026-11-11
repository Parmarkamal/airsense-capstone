"""
AirSense — 48-Hour Recursive Multi-Step AQI Forecasting Engine
File: ml/training/predict_forecast.py
Phase: 3 (Week 6)

Performs:
  1. Loads champion production model from ml/production/lgbm_aqi.pkl.
  2. Queries latest historical buffer from TimescaleDB for lag initialization.
  3. Executes recursive 48-step forward projection per city.
  4. Persists forecasts into TimescaleDB aqi_forecasts table.
  5. Provides query helper for the Streamlit dashboard.
"""

from __future__ import annotations

import logging
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from datetime import datetime, timedelta, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import load_settings
from consumer.db import create_db_engine
from ml.training.features import FEATURE_COLUMNS, TARGET_COLUMN

logger = logging.getLogger("airsense.ml.predict")


def load_production_model(model_path: Path | None = None):
    """Load the trained production LightGBM model."""
    path = model_path or (PROJECT_ROOT / "ml" / "production" / "lgbm_aqi.pkl")
    if not path.exists():
        raise FileNotFoundError(f"Production model not found at {path}. Run train_forecast.py first.")
    return joblib.load(path)


def generate_city_48h_forecast(
    model,
    city_slug: str,
    recent_history: pd.DataFrame,
    horizon_hours: int = 48,
    model_version: str = "lgbm_v1",
) -> list[dict]:
    """
    Generate recursive 48-step ahead forecast for a single city.
    recent_history must contain 'time', 'city', 'aqi' and pollutant columns.

    Phase 7 fixes train-serve feature skew:
      - Rolling std uses ddof=1 (sample std) matching training pipeline.
      - Pollutant lag features (pm25/pm10/no2) use actual historical values
        instead of AQI-ratio approximations.
      - Cities with <24 historical points are handled via backward filling
        rather than being skipped.
    """
    history = recent_history.sort_values(by="time").copy().reset_index(drop=True)
    history["time"] = pd.to_datetime(history["time"])

    generated_at = datetime.now(timezone.utc)
    last_time = history["time"].iloc[-1]

    # Pre-create working buffers with past series (AQI + pollutant precursors)
    aqi_series = list(history["aqi"].astype(float).values)

    # Phase 7: Track actual pollutant values to eliminate train-serve skew.
    # Training uses real pm25/pm10/no2 via shift(1); inference must do the same.
    pm25_series: list[float] = []
    pm10_series: list[float] = []
    no2_series: list[float] = []

    for _, row in history.iterrows():
        pm25_series.append(float(row.get("pm25", np.nan)) if pd.notna(row.get("pm25", np.nan)) else float(row["aqi"]) * 0.65)
        pm10_series.append(float(row.get("pm10", np.nan)) if pd.notna(row.get("pm10", np.nan)) else float(row["aqi"]) * 0.95)
        no2_series.append(float(row.get("no2", np.nan)) if pd.notna(row.get("no2", np.nan)) else float(row["aqi"]) * 0.15)

    # Backward fill any leading NaN values in pollutant series
    for series in (pm25_series, pm10_series, no2_series):
        for i in range(1, len(series)):
            if np.isnan(series[i]):
                series[i] = series[i - 1]
    # If first value is still NaN, fill from AQI ratio
    if np.isnan(pm25_series[0]):
        pm25_series[0] = aqi_series[0] * 0.65
    if np.isnan(pm10_series[0]):
        pm10_series[0] = aqi_series[0] * 0.95
    if np.isnan(no2_series[0]):
        no2_series[0] = aqi_series[0] * 0.15

    timestamps = list(history["time"].values)
    forecast_records = []

    for step in range(1, horizon_hours + 1):
        target_time = last_time + timedelta(hours=step)
        hour = target_time.hour
        day_of_week = target_time.weekday()
        is_weekend = int(day_of_week in [5, 6])

        # Cyclical transforms
        sin_hour = np.sin(2 * np.pi * hour / 24.0)
        cos_hour = np.cos(2 * np.pi * hour / 24.0)
        sin_day = np.sin(2 * np.pi * day_of_week / 7.0)
        cos_day = np.cos(2 * np.pi * day_of_week / 7.0)

        # Lags from the current working buffer (which includes previous recursive predictions!)
        lag_1h = aqi_series[-1]
        lag_2h = aqi_series[-2] if len(aqi_series) >= 2 else aqi_series[0]
        lag_3h = aqi_series[-3] if len(aqi_series) >= 3 else aqi_series[0]
        # Phase 7: backward fill for <24 historical points
        lag_24h = aqi_series[-24] if len(aqi_series) >= 24 else aqi_series[0]
        lag_168h = aqi_series[-168] if len(aqi_series) >= 168 else aqi_series[0]

        # Rolling statistics from buffer — Phase 7: ddof=1 matches training pipeline
        window_6 = aqi_series[-6:]
        window_24 = aqi_series[-24:]
        rolling_mean_6h = float(np.mean(window_6))
        rolling_std_6h = float(np.std(window_6, ddof=1)) if len(window_6) >= 2 else 0.0
        rolling_mean_24h = float(np.mean(window_24))

        # Phase 7: Use actual pollutant values for lag features (matches training shift(1)).
        # For the first forecast step, this uses real pm25/pm10/no2 from the last
        # historical reading. For subsequent steps, uses approximated values derived
        # from the previous step's AQI prediction (since we only forecast AQI).
        pm25_lag_1h = pm25_series[-1] if pm25_series and not np.isnan(pm25_series[-1]) else lag_1h * 0.65
        pm10_lag_1h = pm10_series[-1] if pm10_series and not np.isnan(pm10_series[-1]) else lag_1h * 0.95
        no2_lag_1h = no2_series[-1] if no2_series and not np.isnan(no2_series[-1]) else lag_1h * 0.15

        # Feature dict matching FEATURE_COLUMNS
        feature_row = {
            "hour": hour,
            "day_of_week": day_of_week,
            "is_weekend": is_weekend,
            "sin_hour": sin_hour,
            "cos_hour": cos_hour,
            "sin_day": sin_day,
            "cos_day": cos_day,
            "aqi_lag_1h": lag_1h,
            "aqi_lag_2h": lag_2h,
            "aqi_lag_3h": lag_3h,
            "aqi_lag_24h": lag_24h,
            "aqi_lag_168h": lag_168h,
            "aqi_rolling_mean_6h": rolling_mean_6h,
            "aqi_rolling_std_6h": rolling_std_6h,
            "aqi_rolling_mean_24h": rolling_mean_24h,
            "pm25_lag_1h": pm25_lag_1h,
            "pm10_lag_1h": pm10_lag_1h,
            "no2_lag_1h": no2_lag_1h,
            "city": city_slug,
        }

        X_step = pd.DataFrame([feature_row])
        X_step["city"] = X_step["city"].astype("category")
        X_step = X_step[FEATURE_COLUMNS]

        # Predict next step
        predicted_aqi = float(model.predict(X_step)[0])
        # Biological / physical clamp
        predicted_aqi = max(10.0, min(500.0, round(predicted_aqi, 1)))

        # Update recursive buffers (AQI + pollutant approximations for next-step lags)
        aqi_series.append(predicted_aqi)
        timestamps.append(target_time)
        pm25_series.append(predicted_aqi * 0.65)
        pm10_series.append(predicted_aqi * 0.95)
        no2_series.append(predicted_aqi * 0.15)

        forecast_records.append({
            "generated_at": generated_at,
            "forecast_time": target_time,
            "city": city_slug,
            "predicted_aqi": predicted_aqi,
            "model_version": model_version,
        })

    return forecast_records


def run_all_forecasts_and_save(engine: Engine) -> int:
    """Generate 48-hour forecasts for all configured cities and persist into TimescaleDB."""
    model = load_production_model()
    settings = load_settings(PROJECT_ROOT / "config.yaml")
    cities = [c["slug"] for c in settings["waqi"]["cities"]]

    total_records = 0
    all_forecasts = []

    print(f"Generating 48-hour forecasts for {len(cities)} cities...")

    for city in cities:
        # Load historical buffer from TimescaleDB
        query = text("""
            SELECT time, city, COALESCE(cpcb_aqi, aqi) AS aqi, pm25, pm10, no2
            FROM aqi_readings
            WHERE city = :city
            ORDER BY time DESC
            LIMIT 200;
        """)
        with engine.connect() as conn:
            history_df = pd.read_sql(query, conn, params={"city": city})

        if history_df.empty:
            logger.warning("No history in DB for %s — skipping.", city)
            continue

        # Phase 7: Handle <24 historical points via backward filling instead of skipping.
        # Backward fill fills missing early lags with the earliest available value.
        if len(history_df) < 24:
            logger.info(
                "Insufficient history for %s (%d rows < 24) — using backward fill for missing lags.",
                city, len(history_df),
            )

        city_forecasts = generate_city_48h_forecast(model, city, history_df, horizon_hours=48)
        all_forecasts.extend(city_forecasts)
        total_records += len(city_forecasts)

    if all_forecasts:
        df_forecasts = pd.DataFrame(all_forecasts)
        # Upsert into aqi_forecasts
        with engine.begin() as conn:
            # Delete older forecasts to keep table fresh
            conn.execute(text("DELETE FROM aqi_forecasts;"))
            df_forecasts.to_sql("aqi_forecasts", conn, if_exists="append", index=False, chunksize=500)
        print(f"✅ Stored {total_records} predicted data points into TimescaleDB table `aqi_forecasts`!")

    return total_records


def get_forecast_from_db(engine: Engine, city_slug: str) -> pd.DataFrame:
    """Helper to query the latest 48-hour forecast for a city from TimescaleDB."""
    query = text("""
        SELECT forecast_time, predicted_aqi, model_version
        FROM aqi_forecasts
        WHERE city = :city
        ORDER BY forecast_time ASC
        LIMIT 48;
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"city": city_slug})
        return df
    except Exception as exc:
        logger.error("Failed to query forecasts for %s: %s", city_slug, exc)
        return pd.DataFrame()


def main():
    settings = load_settings(PROJECT_ROOT / "config.yaml")
    engine = create_db_engine(settings)
    run_all_forecasts_and_save(engine)


if __name__ == "__main__":
    main()
