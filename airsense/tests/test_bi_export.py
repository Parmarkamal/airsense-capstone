"""
AirSense — Unit Tests for Phase 9 Power BI Star Schema & BI Analytics
File: tests/test_bi_export.py
Phase: 9 (Business Intelligence & Executive Analytics)

Tests verify:
- Conformed dimension tables build with required Kimball keys
- Fact table joins preserve referential integrity (no orphan keys)
- Combustion ratio and date/time keys calculate accurately
- Full end-to-end Star Schema CSV export runs cleanly
"""

from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import CityConfig, load_settings, get_cities
from scripts.export_powerbi_data import (
    build_dim_city,
    build_dim_date,
    build_dim_time,
    build_fact_aqi_readings,
    export_star_schema,
)
from dashboard.components.insights import (
    compute_wow_change,
    render_city_ranking_matrix,
    render_executive_scorecard,
)


@pytest.fixture
def sample_cities() -> list[CityConfig]:
    return [
        CityConfig(slug="ahmedabad", display_name="Ahmedabad", lat=23.02, lon=72.57, state="Gujarat", tier=2),
        CityConfig(slug="delhi", display_name="Delhi", lat=28.61, lon=77.20, state="Delhi NCR", tier=1),
    ]


@pytest.fixture
def sample_raw_df() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "time": "2026-11-05T10:00:00+00:00",
            "city": "ahmedabad",
            "aqi": 120.0,
            "pm25": 72.0,
            "pm10": 120.0,
            "data_source": "Open-Meteo-Live",
        },
        {
            "time": "2026-11-05T11:00:00+00:00",
            "city": "delhi",
            "aqi": 210.0,
            "pm25": 140.0,
            "pm10": 200.0,
            "data_source": "WAQI",
        },
    ])


def test_dim_city_structure(sample_cities):
    """Verify Dim_City has surrogate CityKey, State, and Tier attributes."""
    dim_city = build_dim_city(sample_cities)
    assert len(dim_city) == 2
    assert "CityKey" in dim_city.columns
    assert "State" in dim_city.columns
    assert "Tier" in dim_city.columns
    assert dim_city["CityKey"].is_unique
    assert dim_city.loc[dim_city["CitySlug"] == "ahmedabad", "State"].values[0] == "Gujarat"


def test_dim_time_has_24_hours():
    """Verify Dim_Time contains all 24 hours with day/night and rush hour flags."""
    dim_time = build_dim_time()
    assert len(dim_time) == 24
    assert set(dim_time["Hour24"]) == set(range(24))
    assert "IsRushHour" in dim_time.columns
    assert "DayNight" in dim_time.columns
    # Hour 9 should be rush hour and day
    h9 = dim_time[dim_time["Hour24"] == 9].iloc[0]
    assert h9["IsRushHour"] == 1
    assert h9["DayNight"] == "Day"


def test_dim_date_attributes():
    """Verify Dim_Date generates integer DateKey and calendar hierarchy."""
    dates = pd.Series(["2026-11-05T10:00:00Z", "2026-11-06T12:00:00Z"])
    dim_date = build_dim_date(dates)
    assert len(dim_date) == 2
    assert "DateKey" in dim_date.columns
    assert 20261105 in dim_date["DateKey"].values
    assert 20261106 in dim_date["DateKey"].values


def test_fact_table_referential_integrity(sample_raw_df, sample_cities):
    """Verify Fact table maps CityKey, DateKey, TimeKey, and CombustionRatio."""
    dim_city = build_dim_city(sample_cities)
    fact = build_fact_aqi_readings(sample_raw_df, dim_city)

    assert len(fact) == 2
    assert "ReadingID" in fact.columns
    assert "DateKey" in fact.columns
    assert "TimeKey" in fact.columns
    assert "CityKey" in fact.columns
    assert "CombustionRatio" in fact.columns

    # Verify CombustionRatio: 72/120 = 0.60
    ahmedabad_fact = fact[fact["CityKey"] == 1].iloc[0]
    assert pytest.approx(ahmedabad_fact["CombustionRatio"], 0.01) == 0.60
    assert ahmedabad_fact["DateKey"] == 20261105
    assert ahmedabad_fact["TimeKey"] == 1000


def test_export_star_schema_e2e(tmp_path):
    """Verify end-to-end Star Schema CSV export generates all 4 files."""
    paths = export_star_schema(output_dir=tmp_path, limit=100)
    for name, p in paths.items():
        assert p.exists(), f"Missing exported CSV: {name}"
        df = pd.read_csv(p)
        assert len(df) > 0, f"Exported CSV is empty: {name}"


def test_compute_wow_change_returns_none_on_insufficient_data():
    """Verify WoW function safely returns None when history < 14 days."""
    short_history = pd.DataFrame({
        "time": pd.date_range("2026-11-01", periods=5, freq="D"),
        "aqi": [100, 110, 120, 105, 95],
    })
    result = compute_wow_change(short_history)
    assert result is None


def test_render_executive_scorecard_structure(sample_raw_df):
    """Verify Executive Scorecard returns expected KPI cards."""
    scorecard = render_executive_scorecard(sample_raw_df, sample_raw_df)
    assert len(scorecard) >= 4
    labels = [kpi["label"] for kpi in scorecard]
    assert "Fleet Avg AQI" in labels
    assert "Most Polluted" in labels
    assert "Cleanest City" in labels
