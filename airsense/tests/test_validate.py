"""
AirSense — Unit tests for Pydantic validation (consumer/validate.py)
File: tests/test_validate.py
Week: 2

Run:
    pytest tests/test_validate.py -v
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

# Add project root to path so tests run from any directory
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from consumer.validate import validate_message, AQIReading


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_valid_reading(**overrides) -> dict:
    base = {
        "schema_version":    "1.0",
        "time":              datetime.now(timezone.utc).isoformat(),
        "city":              "delhi",
        "city_display_name": "Delhi",
        "country":           "IN",
        "station_id":        "7019",
        "aqi":               185.0,
        "pm25":              78.5,
        "pm10":              110.0,
        "no2":               None,
        "co":                None,
        "so2":               None,
        "o3":                None,
        "lat":               28.6139,
        "lon":               77.2090,
        "data_source":       "WAQI",
        "fetched_at":        datetime.now(timezone.utc).isoformat(),
    }
    base.update(overrides)
    return base


def _as_bytes(d: dict) -> bytes:
    return json.dumps(d).encode("utf-8")


# ── Happy path ───────────────────────────────────────────────────────────────

class TestValidReadings:
    def test_fully_populated_reading_passes(self):
        result = validate_message(_as_bytes(_make_valid_reading()))
        assert result.is_valid
        assert result.reading is not None
        assert result.reading.city == "delhi"
        assert result.reading.aqi == 185.0

    def test_minimal_reading_with_only_pm25_passes(self):
        """aqi is None but pm25 is present — should still be valid."""
        data = _make_valid_reading(aqi=None, pm25=55.0)
        result = validate_message(_as_bytes(data))
        assert result.is_valid

    def test_aqi_boundary_zero(self):
        result = validate_message(_as_bytes(_make_valid_reading(aqi=0.0)))
        assert result.is_valid
        assert result.reading.aqi == 0.0

    def test_aqi_boundary_999(self):
        result = validate_message(_as_bytes(_make_valid_reading(aqi=999.0)))
        assert result.is_valid

    def test_to_db_dict_has_all_keys(self):
        result = validate_message(_as_bytes(_make_valid_reading()))
        db_row = result.reading.to_db_dict()
        expected_keys = {
            "time", "city", "city_display_name", "station_id",
            "country", "aqi", "pm25", "pm10", "no2", "co", "so2", "o3",
            "lat", "lon", "data_source", "schema_version", "fetched_at",
        }
        assert expected_keys == set(db_row.keys())

    def test_naive_timestamp_gets_utc_attached(self):
        data = _make_valid_reading(time="2025-01-15T10:30:00")  # no tz info
        result = validate_message(_as_bytes(data))
        assert result.is_valid
        assert result.reading.time.tzinfo is not None

    def test_null_optional_pollutants_accepted(self):
        data = _make_valid_reading(no2=None, co=None, so2=None, o3=None)
        result = validate_message(_as_bytes(data))
        assert result.is_valid


# ── Invalid readings ──────────────────────────────────────────────────────────

class TestInvalidReadings:
    def test_aqi_above_999_rejected(self):
        data = _make_valid_reading(aqi=1000.0)
        result = validate_message(_as_bytes(data))
        assert not result.is_valid
        assert any("aqi" in e.lower() for e in result.errors)

    def test_negative_aqi_rejected(self):
        data = _make_valid_reading(aqi=-1.0)
        result = validate_message(_as_bytes(data))
        assert not result.is_valid

    def test_negative_pm25_rejected(self):
        data = _make_valid_reading(pm25=-5.0)
        result = validate_message(_as_bytes(data))
        assert not result.is_valid

    def test_missing_both_aqi_and_pm25_rejected(self):
        data = _make_valid_reading(aqi=None, pm25=None)
        result = validate_message(_as_bytes(data))
        assert not result.is_valid
        assert result.errors  # must have at least one error message

    def test_future_timestamp_rejected(self):
        future = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
        data = _make_valid_reading(time=future)
        result = validate_message(_as_bytes(data))
        assert not result.is_valid

    def test_unparseable_timestamp_rejected(self):
        data = _make_valid_reading(time="not-a-date")
        result = validate_message(_as_bytes(data))
        assert not result.is_valid

    def test_empty_city_slug_rejected(self):
        data = _make_valid_reading(city="")
        result = validate_message(_as_bytes(data))
        assert not result.is_valid

    def test_lat_out_of_range_rejected(self):
        data = _make_valid_reading(lat=95.0)  # > 90
        result = validate_message(_as_bytes(data))
        assert not result.is_valid

    def test_lon_out_of_range_rejected(self):
        data = _make_valid_reading(lon=-200.0)  # < -180
        result = validate_message(_as_bytes(data))
        assert not result.is_valid


# ── Malformed input ───────────────────────────────────────────────────────────

class TestMalformedInput:
    def test_invalid_json_bytes(self):
        result = validate_message(b"not json {{{")
        assert not result.is_valid
        assert any("json" in e.lower() for e in result.errors)

    def test_empty_bytes(self):
        result = validate_message(b"")
        assert not result.is_valid

    def test_json_array_not_object(self):
        result = validate_message(b"[1, 2, 3]")
        assert not result.is_valid
        assert any("object" in e.lower() for e in result.errors)

    def test_missing_required_field_time(self):
        data = _make_valid_reading()
        del data["time"]
        result = validate_message(_as_bytes(data))
        assert not result.is_valid
