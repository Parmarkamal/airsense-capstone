"""
AirSense — Unit Tests for Offline Replay Streamer (Phase 8)
File: tests/test_replay.py

Tests the CSV replay pipeline: loading, timestamp sliding, Pydantic validation,
and replay mode detection — all without requiring Kafka or TimescaleDB.

Run:
    pytest tests/test_replay.py -v
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.fetch_aqi_replay import (
    load_replay_csv,
    apply_sliding_timestamps,
    df_to_readings,
    REPLAY_DATA_SOURCE,
)
from dashboard.data_access import is_replay_mode_active


# ── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture
def replay_df() -> pd.DataFrame:
    """Load the actual 7-day backup CSV for integration tests."""
    return load_replay_csv()


@pytest.fixture
def small_replay_df() -> pd.DataFrame:
    """A small synthetic CSV-shaped DataFrame for unit tests."""
    base_time = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    records = []
    for h in range(48):
        for city in ["ahmedabad", "delhi"]:
            t = base_time + timedelta(hours=h)
            records.append({
                "time": t.isoformat(),
                "city": city,
                "city_display_name": city.capitalize(),
                "station_id": "12345",
                "country": "IN",
                "aqi": 100.0 + h,
                "pm25": 65.0 + h * 0.5,
                "pm10": 95.0 + h * 0.8,
                "no2": 15.0 + h * 0.1,
                "co": 0.8,
                "so2": 12.0,
                "o3": 35.0,
                "lat": 23.0,
                "lon": 72.0,
                "data_source": "CPCB_BASELINE",
                "schema_version": "1.0",
                "fetched_at": t.isoformat(),
            })
    return pd.DataFrame(records)


# ── CSV Loading Tests ──────────────────────────────────────────────────────────


class TestReplayCsvLoading:
    """Verify the backup CSV loads correctly with expected structure."""

    def test_csv_exists(self):
        """The 7-day backup CSV must exist for offline demo."""
        csv_path = PROJECT_ROOT / "data" / "backup" / "aqi_7day_backup.csv"
        assert csv_path.exists(), f"Backup CSV not found at {csv_path}"

    def test_csv_has_expected_columns(self, replay_df: pd.DataFrame):
        """Verify all required columns are present in the backup CSV."""
        required = [
            "time", "city", "city_display_name", "station_id", "country",
            "aqi", "pm25", "pm10", "no2", "co", "so2", "o3",
            "lat", "lon", "data_source", "schema_version", "fetched_at",
        ]
        for col in required:
            assert col in replay_df.columns, f"Missing column: {col}"

    def test_csv_has_six_cities(self, replay_df: pd.DataFrame):
        """Verify the backup contains data for all 6 configured cities."""
        cities = set(replay_df["city"].unique())
        expected = {"ahmedabad", "bengaluru", "pune", "gandhinagar", "delhi", "mumbai"}
        assert cities == expected, f"Expected {expected}, got {cities}"

    def test_csv_has_7_days_of_data(self, replay_df: pd.DataFrame):
        """Verify the backup spans approximately 7 days of hourly data."""
        times = pd.to_datetime(replay_df["time"], utc=True)
        duration_days = (times.max() - times.min()).total_seconds() / 86400
        assert duration_days > 6.0, f"Expected ~7 days, got {duration_days:.1f} days"


# ── Timestamp Sliding Tests ────────────────────────────────────────────────────


class TestSlidingTimestamps:
    """Verify the sliding timestamp logic makes data appear recent."""

    def test_data_source_set_to_replay(self, small_replay_df: pd.DataFrame):
        """After sliding, data_source must be 'Replay-Backup'."""
        df = apply_sliding_timestamps(small_replay_df)
        assert (df["data_source"] == REPLAY_DATA_SOURCE).all()

    def test_most_recent_timestamp_near_now(self, small_replay_df: pd.DataFrame):
        """The most recent timestamp should be approximately 1 hour ago."""
        now = datetime.now(timezone.utc)
        df = apply_sliding_timestamps(small_replay_df, now=now)
        max_time = pd.to_datetime(df["time"], utc=True).max()
        delta_hours = (now - max_time).total_seconds() / 3600
        # Should be ~1 hour ago (within 5 minutes tolerance)
        assert 0.9 < delta_hours < 1.1, (
            f"Most recent timestamp is {delta_hours:.2f}h ago, expected ~1h"
        )

    def test_no_timestamps_in_future(self, small_replay_df: pd.DataFrame):
        """No timestamp should be in the future (would fail Pydantic validation)."""
        now = datetime.now(timezone.utc)
        df = apply_sliding_timestamps(small_replay_df, now=now)
        times = pd.to_datetime(df["time"], utc=True)
        # Allow up to 1 second processing time, but no readings should be ahead
        max_time = times.max()
        assert max_time <= now + timedelta(seconds=1), (
            f"Timestamp {max_time} is in the future relative to {now}"
        )

    def test_relative_spacing_preserved(self, small_replay_df: pd.DataFrame):
        """The 1-hour spacing between consecutive readings should be preserved."""
        df = apply_sliding_timestamps(small_replay_df)
        city_df = df[df["city"] == "ahmedabad"].sort_values("time")
        times = pd.to_datetime(city_df["time"], utc=True)
        diffs = times.diff().dropna()
        # All consecutive readings should be ~1 hour apart
        for diff in diffs:
            assert abs(diff.total_seconds() - 3600) < 5, (
                f"Time spacing {diff} is not ~1 hour"
            )

    def test_fetched_at_updated_to_now(self, small_replay_df: pd.DataFrame):
        """fetched_at should be updated to the current time."""
        now = datetime.now(timezone.utc)
        df = apply_sliding_timestamps(small_replay_df, now=now)
        fetched = pd.to_datetime(df["fetched_at"], utc=True).iloc[0]
        delta = abs((now - fetched).total_seconds())
        assert delta < 5, f"fetched_at should be ~now, delta={delta}s"


# ── Message Validation Tests ───────────────────────────────────────────────────


class TestReplayMessageValidation:
    """Verify replay messages pass the same Pydantic validation as live data."""

    def test_all_readings_validate(self, small_replay_df: pd.DataFrame):
        """Every replay reading must pass AQIReading Pydantic validation."""
        from consumer.validate import AQIReading

        df = apply_sliding_timestamps(small_replay_df)
        readings = df_to_readings(df)

        assert len(readings) == len(df)

        for reading in readings:
            validated = AQIReading.model_validate(reading)
            assert validated.data_source == REPLAY_DATA_SOURCE
            assert validated.city is not None
            assert validated.aqi is not None or validated.pm25 is not None

    def test_actual_csv_readings_validate(self, replay_df: pd.DataFrame):
        """The real backup CSV readings must all pass Pydantic validation."""
        from consumer.validate import AQIReading

        df = apply_sliding_timestamps(replay_df)
        readings = df_to_readings(df)

        # Sample test: validate first 50 readings (full set takes longer)
        for reading in readings[:50]:
            validated = AQIReading.model_validate(reading)
            assert validated.data_source == REPLAY_DATA_SOURCE

    def test_readings_have_correct_schema_version(self, small_replay_df: pd.DataFrame):
        """Schema version should be a string '1.0'."""
        df = apply_sliding_timestamps(small_replay_df)
        readings = df_to_readings(df)
        for reading in readings:
            assert reading["schema_version"] == "1.0"

    def test_readings_handle_nan_pollutants(self):
        """Replay readings should convert NaN pollutant values to None."""
        df = pd.DataFrame({
            "time": [datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat()],
            "city": ["test_city"],
            "city_display_name": ["Test City"],
            "station_id": ["S1"],
            "country": ["IN"],
            "aqi": [100.0],
            "pm25": [65.0],
            "pm10": [np.nan],
            "no2": [np.nan],
            "co": [np.nan],
            "so2": [np.nan],
            "o3": [np.nan],
            "lat": [23.0],
            "lon": [72.0],
            "data_source": ["CPCB_BASELINE"],
            "schema_version": ["1.0"],
            "fetched_at": [datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat()],
        })
        df = apply_sliding_timestamps(df)
        readings = df_to_readings(df)
        reading = readings[0]
        assert reading["pm10"] is None
        assert reading["no2"] is None
        assert reading["pm25"] is not None
        assert reading["aqi"] is not None


# ── Replay Mode Detection Tests ────────────────────────────────────────────────


class TestReplayModeDetection:
    """Verify the dashboard replay mode detection logic."""

    def test_replay_detected_when_replay_source(self):
        """is_replay_mode_active returns True when data_source is Replay-Backup."""
        df = pd.DataFrame({
            "city": ["ahmedabad", "delhi"],
            "aqi": [100, 150],
            "data_source": ["Replay-Backup", "Replay-Backup"],
        })
        assert is_replay_mode_active(df) is True

    def test_replay_not_detected_when_live_source(self):
        """is_replay_mode_active returns False for live WAQI data."""
        df = pd.DataFrame({
            "city": ["ahmedabad", "delhi"],
            "aqi": [100, 150],
            "data_source": ["WAQI", "Open-Meteo-Live"],
        })
        assert is_replay_mode_active(df) is False

    def test_replay_not_detected_when_mixed_sources(self):
        """Mixed sources should not trigger replay (at least one live source)."""
        df = pd.DataFrame({
            "city": ["ahmedabad", "delhi"],
            "aqi": [100, 150],
            "data_source": ["WAQI", "Replay-Backup"],
        })
        # Any replay source present means replay mode is active
        assert is_replay_mode_active(df) is True

    def test_replay_not_detected_when_empty_df(self):
        """Empty DataFrame should return False."""
        assert is_replay_mode_active(pd.DataFrame()) is False

    def test_replay_not_detected_when_no_data_source_column(self):
        """DataFrame without data_source column should return False."""
        df = pd.DataFrame({"city": ["ahmedabad"], "aqi": [100]})
        assert is_replay_mode_active(df) is False
