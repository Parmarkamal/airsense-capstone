"""
AirSense — Unit tests for Phase 5 hybrid WAQI → Open-Meteo ingestion
File: tests/test_hybrid_fetch.py

Run:
    pytest tests/test_hybrid_fetch.py -v
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.config import CityConfig
from dashboard.data_access import calculate_data_freshness
from ingestion.fetch_aqi import (
    _is_reading_stale,
    fetch_city_reading,
    fetch_open_meteo_reading,
)

DELHI = CityConfig(
    slug="delhi",
    display_name="Delhi",
    lat=28.6139,
    lon=77.2090,
)


def _waqi_ok_payload(*, hours_ago: float = 0.2) -> dict:
    ts = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return {
        "status": "ok",
        "data": {
            "aqi": 120,
            "idx": 7019,
            "time": {"iso": ts.isoformat()},
            "iaqi": {
                "pm25": {"v": 45.0},
                "pm10": {"v": 80.0},
            },
            "city": {"name": "Delhi", "geo": [28.61, 77.20]},
        },
    }


def _open_meteo_payload() -> dict:
    return {
        "current": {
            "time": datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0).isoformat(),
            "us_aqi": 77,
            "pm2_5": 17.5,
            "pm10": 32.0,
            "nitrogen_dioxide": 12.0,
            "carbon_monoxide": 180.0,
            "sulphur_dioxide": 4.0,
            "ozone": 40.0,
        }
    }


class TestOpenMeteoParser:
    def test_open_meteo_schema_compatible(self):
        session = MagicMock()
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = _open_meteo_payload()
        session.get.return_value = response

        reading = fetch_open_meteo_reading(DELHI, timeout=10, session=session)

        assert reading["data_source"] == "Open-Meteo-Live"
        assert reading["station_id"] == "open-meteo-delhi"
        assert reading["city"] == "delhi"
        assert reading["aqi"] == 77.0
        assert reading["pm25"] == 17.5
        assert reading["schema_version"] == "1.0"
        assert reading["lat"] == DELHI.lat
        assert reading["lon"] == DELHI.lon


class TestHybridFallback:
    def test_fresh_waqi_kept(self):
        session = MagicMock()
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = _waqi_ok_payload(hours_ago=0.3)
        session.get.return_value = response

        reading = fetch_city_reading(
            city=DELHI,
            token="test-token",
            base_url="https://api.waqi.info/feed",
            timeout=10,
            session=session,
        )

        assert reading["data_source"] == "WAQI"
        assert reading["aqi"] == 120.0
        assert session.get.call_count == 1

    def test_stale_waqi_falls_back_to_open_meteo(self):
        session = MagicMock()
        waqi_resp = MagicMock()
        waqi_resp.raise_for_status = MagicMock()
        waqi_resp.json.return_value = _waqi_ok_payload(hours_ago=5.0)

        om_resp = MagicMock()
        om_resp.raise_for_status = MagicMock()
        om_resp.json.return_value = _open_meteo_payload()

        session.get.side_effect = [waqi_resp, om_resp]

        reading = fetch_city_reading(
            city=DELHI,
            token="test-token",
            base_url="https://api.waqi.info/feed",
            timeout=10,
            session=session,
        )

        assert reading["data_source"] == "Open-Meteo-Live"
        assert reading["aqi"] == 77.0
        assert session.get.call_count == 2

    def test_waqi_http_error_falls_back(self):
        import requests

        session = MagicMock()
        session.get.side_effect = [
            requests.ConnectionError("WAQI down"),
            MagicMock(
                raise_for_status=MagicMock(),
                json=MagicMock(return_value=_open_meteo_payload()),
            ),
        ]

        reading = fetch_city_reading(
            city=DELHI,
            token="test-token",
            base_url="https://api.waqi.info/feed",
            timeout=10,
            session=session,
        )

        assert reading["data_source"] == "Open-Meteo-Live"
        assert reading["station_id"] == "open-meteo-delhi"

    def test_waqi_non_ok_status_falls_back(self):
        session = MagicMock()
        bad = MagicMock()
        bad.raise_for_status = MagicMock()
        bad.json.return_value = {"status": "error", "data": "Unknown station"}

        om = MagicMock()
        om.raise_for_status = MagicMock()
        om.json.return_value = _open_meteo_payload()

        session.get.side_effect = [bad, om]

        reading = fetch_city_reading(
            city=DELHI,
            token="test-token",
            base_url="https://api.waqi.info/feed",
            timeout=10,
            session=session,
        )

        assert reading["data_source"] == "Open-Meteo-Live"


class TestStaleHelper:
    def test_stale_flag(self):
        stale = {
            "time": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        }
        fresh = {
            "time": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
        }
        assert _is_reading_stale(stale, max_age_hours=2.0) is True
        assert _is_reading_stale(fresh, max_age_hours=2.0) is False


class TestFreshnessBadges:
    def test_live_badge(self):
        ts = datetime.now(timezone.utc) - timedelta(minutes=20)
        color, label, age = calculate_data_freshness(ts)
        assert color == "green"
        assert "Live" in label
        assert age < 1.0

    def test_delayed_badge(self):
        ts = datetime.now(timezone.utc) - timedelta(hours=2)
        color, label, age = calculate_data_freshness(ts)
        assert color == "gold"
        assert "Delayed" in label
        assert 1.0 <= age <= 3.0

    def test_stale_badge(self):
        ts = datetime.now(timezone.utc) - timedelta(hours=5)
        color, label, age = calculate_data_freshness(ts)
        assert color == "red"
        assert "Stale" in label
        assert age > 3.0
