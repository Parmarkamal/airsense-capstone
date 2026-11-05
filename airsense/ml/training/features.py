"""
AirSense — Machine Learning Feature Engineering
File: ml/training/features.py
Phase: 3 (Week 5)

Extracts temporal, cyclical, autoregressive lag, and rolling window features
specifically designed for time-series tabular modeling with LightGBM.
Strictly avoids lookahead bias (data leakage).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    # Cyclical & Calendar
    "hour",
    "day_of_week",
    "is_weekend",
    "sin_hour",
    "cos_hour",
    "sin_day",
    "cos_day",
    # Autoregressive Lags
    "aqi_lag_1h",
    "aqi_lag_2h",
    "aqi_lag_3h",
    "aqi_lag_24h",
    "aqi_lag_168h",
    # Rolling Statistics
    "aqi_rolling_mean_6h",
    "aqi_rolling_std_6h",
    "aqi_rolling_mean_24h",
    # Lagged Pollutant Precursors (1h lag to avoid data leakage)
    "pm25_lag_1h",
    "pm10_lag_1h",
    "no2_lag_1h",
    # Categorical
    "city",
]

CATEGORICAL_FEATURES = ["city"]
TARGET_COLUMN = "aqi"


def create_features(df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
    """
    Generate feature matrix from time-series DataFrame.
    DataFrame must contain: 'time', 'city', 'aqi', and optionally pollutant columns.
    """
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(by=["city", "time"]).reset_index(drop=True)

    # 1. Calendar Features
    df["hour"] = df["time"].dt.hour
    df["day_of_week"] = df["time"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    # 2. Cyclical Transforms (ensures smooth distance between 23:00 and 00:00)
    df["sin_hour"] = np.sin(2 * np.pi * df["hour"] / 24.0)
    df["cos_hour"] = np.cos(2 * np.pi * df["hour"] / 24.0)
    df["sin_day"] = np.sin(2 * np.pi * df["day_of_week"] / 7.0)
    df["cos_day"] = np.cos(2 * np.pi * df["day_of_week"] / 7.0)

    # 3. Autoregressive Lags per City
    grouped = df.groupby("city")
    for lag in [1, 2, 3, 24, 168]:
        df[f"aqi_lag_{lag}h"] = grouped["aqi"].shift(lag)

    # 4. Rolling Window Statistics per City (shift 1 first to prevent target leakage!)
    shifted_aqi = grouped["aqi"].shift(1)
    df["aqi_rolling_mean_6h"] = (
        shifted_aqi.groupby(df["city"]).rolling(6, min_periods=1).mean().reset_index(level=0, drop=True)
    )
    df["aqi_rolling_std_6h"] = (
        shifted_aqi.groupby(df["city"]).rolling(6, min_periods=1).std().fillna(0).reset_index(level=0, drop=True)
    )
    df["aqi_rolling_mean_24h"] = (
        shifted_aqi.groupby(df["city"]).rolling(24, min_periods=1).mean().reset_index(level=0, drop=True)
    )

    # 5. Lagged Pollutant Metrics (1-hour lag)
    for pol in ["pm25", "pm10", "no2"]:
        if pol in df.columns:
            df[f"{pol}_lag_1h"] = grouped[pol].shift(1)
        else:
            df[f"{pol}_lag_1h"] = np.nan

    # 6. City Categorical Type
    df["city"] = df["city"].astype("category")

    if is_training:
        # Drop warm-up rows where key lags (like 24h lag) are NaN
        # Keep rows with valid lag_24h for stable training
        df = df.dropna(subset=["aqi_lag_1h", "aqi_lag_24h", TARGET_COLUMN]).reset_index(drop=True)

    return df


# ── Phase 7: Naive Baseline Generators for Model Benchmarking ────────────────


def compute_persistence_baseline(
    y: "pd.Series",
    forecast_horizon: int = 48,
    val_idx: np.ndarray | None = None,
) -> np.ndarray:
    """
    Persistence (naive) baseline: \u0177(t+h) = y(t).

    The simplest forecasting baseline — assumes the next value equals the
    most recent observed value.

    Parameters
    ----------
    y : pd.Series
        Full target series (chronologically ordered).
    forecast_horizon : int
        Number of steps ahead for multi-step mode (default 48).
    val_idx : np.ndarray | None
        If provided (walk-forward validation mode), each validation point
        predicts the immediately preceding observed value \u0177(t) = y(t-1).
        If None (multi-step mode), the last observed value is repeated
        for the entire horizon.

    Returns
    -------
    np.ndarray
        Baseline predictions.
    """
    y_array = y.to_numpy() if isinstance(y, pd.Series) else np.asarray(y, dtype=float)

    if val_idx is not None:
        preds = np.empty(len(val_idx), dtype=float)
        for j, idx in enumerate(val_idx):
            if idx > 0:
                preds[j] = y_array[idx - 1]
            else:
                # Backward fill: use earliest available value for edge case
                preds[j] = y_array[0]
        return preds

    # Multi-step mode: repeat the last observed value for the full horizon
    last_value = float(y_array[-1])
    return np.full(forecast_horizon, last_value, dtype=float)


def compute_seasonal_baseline(
    y: "pd.Series",
    forecast_horizon: int = 48,
    period: int = 24,
    val_idx: np.ndarray | None = None,
) -> np.ndarray:
    """
    Seasonal 24h baseline: \u0177(t+h) = y(t+h-24).

    Assumes the future value equals the value from the same hour yesterday
    (period=24 for hourly data).

    Parameters
    ----------
    y : pd.Series
        Full target series (chronologically ordered).
    forecast_horizon : int
        Number of steps ahead for multi-step mode (default 48).
    period : int
        Seasonal period in hours (default 24 for diurnal cycle).
    val_idx : np.ndarray | None
        If provided (walk-forward validation mode), each validation point
        predicts the value one period ago \u0177(t) = y(t-24).
        If None (multi-step mode), cycles through the last `period` values.

    Returns
    -------
    np.ndarray
        Baseline predictions.
    """
    y_array = y.to_numpy() if isinstance(y, pd.Series) else np.asarray(y, dtype=float)
    n = len(y_array)

    if val_idx is not None:
        preds = np.empty(len(val_idx), dtype=float)
        for j, idx in enumerate(val_idx):
            if idx >= period:
                preds[j] = y_array[idx - period]
            elif idx > 0:
                # Backward fill: use earliest available value
                preds[j] = y_array[0]
            else:
                preds[j] = y_array[0]
        return preds

    # Multi-step mode: cycle through the last `period` observed values
    forecasts = np.empty(forecast_horizon, dtype=float)
    for h in range(forecast_horizon):
        src_idx = n - period + (h % period)
        if src_idx < 0:
            src_idx = 0  # backward fill for < period history
        forecasts[h] = y_array[src_idx]
    return forecasts
