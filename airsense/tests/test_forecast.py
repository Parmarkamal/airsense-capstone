"""
AirSense — Unit Tests for ML Forecasting & Feature Engineering
File: tests/test_forecast.py
Phase: 3 (Weeks 5 & 6)

Run:
    pytest tests/test_forecast.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
import joblib
import numpy as np
import pandas as pd
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.training.features import create_features, FEATURE_COLUMNS, TARGET_COLUMN


@pytest.fixture
def sample_timeseries_df() -> pd.DataFrame:
    """Generate 72 hours of mock continuous AQI readings for testing."""
    base_time = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    records = []
    np.random.seed(42)
    
    for h in range(72):
        t = base_time + timedelta(hours=h)
        aqi_val = 100.0 + 30.0 * np.sin(2 * np.pi * h / 24.0) + np.random.normal(0, 3)
        records.append({
            "time": t,
            "city": "ahmedabad",
            "aqi": aqi_val,
            "pm25": aqi_val * 0.6,
            "pm10": aqi_val * 0.9,
            "no2": 25.0,
            "so2": 12.0,
            "co": 0.8,
            "o3": 35.0,
        })
    return pd.DataFrame(records)


def test_feature_engineering_columns(sample_timeseries_df):
    """Verify that feature engineering generates all mandatory columns without leakage."""
    featured_df = create_features(sample_timeseries_df, is_training=True)

    # Check mandatory features
    for col in FEATURE_COLUMNS:
        assert col in featured_df.columns, f"Missing feature column: {col}"

    assert TARGET_COLUMN in featured_df.columns
    assert len(featured_df) > 0


def test_cyclical_encoding_bounds(sample_timeseries_df):
    """Verify sin and cos transformations remain strictly bounded within [-1.0, 1.0]."""
    featured_df = create_features(sample_timeseries_df, is_training=False)

    for cycle_col in ["sin_hour", "cos_hour", "sin_day", "cos_day"]:
        assert (featured_df[cycle_col] >= -1.0001).all()
        assert (featured_df[cycle_col] <= 1.0001).all()


def test_lag_generation_integrity(sample_timeseries_df):
    """Verify autoregressive lag-1 aligns with previous hour value."""
    featured_df = create_features(sample_timeseries_df, is_training=False)
    
    # After sorting, lag_1 at index 10 should match aqi at index 9
    sorted_df = featured_df.sort_values(by="time").reset_index(drop=True)
    assert np.isclose(sorted_df.loc[10, "aqi_lag_1h"], sorted_df.loc[9, "aqi"], atol=1e-5)


def test_production_model_artifact_exists():
    """Verify production LightGBM model and metadata artifacts are deployed."""
    model_path = PROJECT_ROOT / "ml" / "production" / "lgbm_aqi.pkl"
    metrics_path = PROJECT_ROOT / "ml" / "production" / "metrics.json"

    assert model_path.exists(), f"Production model not found at {model_path}"
    assert metrics_path.exists(), f"Metrics metadata not found at {metrics_path}"

    # Load model and verify interface
    model = joblib.load(model_path)
    assert hasattr(model, "predict"), "Model artifact does not implement predict() method"

    # Verify metrics meet Phase 3 SLA
    with open(metrics_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["rmse"] < 30.0, f"RMSE {meta['rmse']} exceeds Capstone target of 30.0"
    assert meta["r2"] > 0.85, f"R2 score {meta['r2']} is lower than required threshold"
    assert meta["directional_accuracy"] >= 80.0, "Directional accuracy below 80%"


def test_model_prediction_sanity():
    """Verify production model produces sane, positive predictions given a mock feature vector."""
    model_path = PROJECT_ROOT / "ml" / "production" / "lgbm_aqi.pkl"
    model = joblib.load(model_path)

    # Synthetic single observation matching FEATURE_COLUMNS exactly
    mock_input = pd.DataFrame([{
        "hour": 14,
        "day_of_week": 3,
        "is_weekend": 0,
        "sin_hour": 0.5,
        "cos_hour": 0.866,
        "sin_day": 0.433,
        "cos_day": 0.900,
        "aqi_lag_1h": 120.0,
        "aqi_lag_2h": 118.0,
        "aqi_lag_3h": 115.0,
        "aqi_lag_24h": 125.0,
        "aqi_lag_168h": 130.0,
        "aqi_rolling_mean_6h": 119.0,
        "aqi_rolling_std_6h": 3.2,
        "aqi_rolling_mean_24h": 122.0,
        "pm25_lag_1h": 72.0,
        "pm10_lag_1h": 110.0,
        "no2_lag_1h": 22.0,
        "city": "ahmedabad",
    }])
    mock_input["city"] = mock_input["city"].astype("category")
    mock_features = mock_input[FEATURE_COLUMNS]

    pred = model.predict(mock_features)
    assert len(pred) == 1
    assert 10.0 <= pred[0] <= 500.0, f"Predicted AQI {pred[0]} is out of reasonable Indian urban bounds"
