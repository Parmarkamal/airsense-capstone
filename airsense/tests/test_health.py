"""
AirSense — Phase 10: Pipeline Health Tests
File: tests/test_health.py

Tests for dashboard/components/health_view.py
Verifies all health-check functions without requiring live services.
All tests use mocking / offline simulation so the CI suite stays self-contained.
"""

from __future__ import annotations

import json
import socket
from pathlib import Path
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch, mock_open

import pytest

# Allow importing from project root
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dashboard.components.health_view import (
    HealthStatus,
    check_kafka,
    check_timescaledb,
    check_ollama,
    check_ingestion_heartbeat,
    run_all_checks,
)


# ── HealthStatus dataclass ────────────────────────────────────────────────────

class TestHealthStatus:
    def test_badge_ok(self):
        s = HealthStatus(service="X", ok=True)
        assert s.badge == "🟢 Online"
        assert s.badge_color == "green"

    def test_badge_fail(self):
        s = HealthStatus(service="X", ok=False)
        assert s.badge == "🔴 Offline"
        assert s.badge_color == "red"

    def test_default_metrics(self):
        s = HealthStatus(service="X", ok=True)
        assert s.metrics == {}

    def test_metrics_stored(self):
        s = HealthStatus(service="X", ok=True, metrics={"row_count": 42})
        assert s.metrics["row_count"] == 42

    def test_latency_none_by_default(self):
        s = HealthStatus(service="X", ok=True)
        assert s.latency_ms is None


# ── check_kafka ───────────────────────────────────────────────────────────────

class TestCheckKafka:
    def test_kafka_online(self):
        """Simulate a successful TCP connection."""
        mock_sock = MagicMock()
        mock_sock.__enter__ = MagicMock(return_value=mock_sock)
        mock_sock.__exit__ = MagicMock(return_value=False)
        with patch("socket.create_connection", return_value=mock_sock):
            result = check_kafka(host="localhost", port=9092)
        assert result.ok is True
        assert result.service == "Kafka Broker"
        assert result.latency_ms is not None
        assert result.latency_ms >= 0

    def test_kafka_offline(self):
        """Simulate a connection refused error."""
        with patch(
            "socket.create_connection",
            side_effect=OSError("Connection refused"),
        ):
            result = check_kafka(host="localhost", port=9092)
        assert result.ok is False
        assert "Cannot reach" in result.detail

    def test_kafka_timeout(self):
        """Simulate a socket timeout."""
        with patch(
            "socket.create_connection",
            side_effect=socket.timeout("timed out"),
        ):
            result = check_kafka(host="localhost", port=9092, timeout=0.001)
        assert result.ok is False

    def test_kafka_metrics_stored(self):
        mock_sock = MagicMock()
        mock_sock.__enter__ = MagicMock(return_value=mock_sock)
        mock_sock.__exit__ = MagicMock(return_value=False)
        with patch("socket.create_connection", return_value=mock_sock):
            result = check_kafka(host="myhost", port=1234)
        assert result.metrics["host"] == "myhost"
        assert result.metrics["port"] == 1234


# ── check_timescaledb ─────────────────────────────────────────────────────────

class TestCheckTimescaleDB:
    def _make_engine(self, row_count=500, chunk_count=5):
        engine = MagicMock()
        conn = MagicMock()
        conn.__enter__ = MagicMock(return_value=conn)
        conn.__exit__ = MagicMock(return_value=False)
        # First execute() → row_count, second → chunk_count
        conn.execute.return_value.scalar.side_effect = [row_count, chunk_count]
        engine.connect.return_value = conn
        return engine

    def test_timescaledb_online(self):
        engine = self._make_engine(row_count=1008, chunk_count=7)
        result = check_timescaledb(engine)
        assert result.ok is True
        assert result.service == "TimescaleDB"
        assert result.metrics["row_count"] == 1008
        assert result.latency_ms is not None

    def test_timescaledb_no_engine(self):
        result = check_timescaledb(None)
        assert result.ok is False
        assert "No database engine" in result.detail

    def test_timescaledb_query_failure(self):
        engine = MagicMock()
        conn = MagicMock()
        conn.__enter__ = MagicMock(return_value=conn)
        conn.__exit__ = MagicMock(return_value=False)
        conn.execute.side_effect = Exception("relation does not exist")
        engine.connect.return_value = conn
        result = check_timescaledb(engine)
        assert result.ok is False
        assert "Query failed" in result.detail

    def test_timescaledb_chunk_fallback(self):
        """If chunk query fails, row count still returned (ok=True)."""
        engine = MagicMock()
        conn = MagicMock()
        conn.__enter__ = MagicMock(return_value=conn)
        conn.__exit__ = MagicMock(return_value=False)
        # First call (row count) succeeds, second (chunks) raises
        conn.execute.return_value.scalar.side_effect = [42, Exception("no view")]
        engine.connect.return_value = conn
        result = check_timescaledb(engine)
        # The function catches inner chunk exception, still returns ok
        assert result.ok is True
        assert result.metrics["row_count"] == 42


# ── check_ollama ──────────────────────────────────────────────────────────────

class TestCheckOllama:
    def _mock_response(self, models: list[str]):
        payload = {"models": [{"name": m} for m in models]}
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(payload).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    def test_ollama_online_model_loaded(self):
        resp = self._mock_response(["llama3.2:3b", "mistral:7b"])
        with patch("urllib.request.urlopen", return_value=resp):
            result = check_ollama(model="llama3.2:3b")
        assert result.ok is True
        assert result.metrics["model_loaded"] is True

    def test_ollama_online_model_missing(self):
        resp = self._mock_response(["mistral:7b"])
        with patch("urllib.request.urlopen", return_value=resp):
            result = check_ollama(model="llama3.2:3b")
        assert result.ok is True  # server is up
        assert result.metrics["model_loaded"] is False
        assert "NOT found" in result.detail

    def test_ollama_offline(self):
        import urllib.error
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("Connection refused"),
        ):
            result = check_ollama()
        assert result.ok is False
        assert "Cannot reach Ollama" in result.detail

    def test_ollama_latency_captured(self):
        resp = self._mock_response(["llama3.2:3b"])
        with patch("urllib.request.urlopen", return_value=resp):
            result = check_ollama()
        assert result.latency_ms is not None
        assert result.latency_ms >= 0


# ── check_ingestion_heartbeat ─────────────────────────────────────────────────

class TestCheckIngestionHeartbeat:
    def _write_heartbeat(self, tmp_path: Path, age_minutes: float, batch_size: int = 6):
        ts = datetime.now(timezone.utc) - timedelta(minutes=age_minutes)
        data = {"last_success": ts.isoformat(), "batch_size": batch_size}
        p = tmp_path / "heartbeat.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        return p

    def test_heartbeat_fresh(self, tmp_path):
        p = self._write_heartbeat(tmp_path, age_minutes=5, batch_size=6)
        result = check_ingestion_heartbeat(heartbeat_path=p)
        assert result.ok is True
        assert result.metrics["batch_size"] == 6
        assert result.metrics["age_minutes"] <= 10  # tolerance for test timing

    def test_heartbeat_stale(self, tmp_path):
        p = self._write_heartbeat(tmp_path, age_minutes=60, batch_size=6)
        result = check_ingestion_heartbeat(heartbeat_path=p, stale_threshold_minutes=30)
        assert result.ok is False
        assert "Stale" in result.detail

    def test_heartbeat_file_missing(self, tmp_path):
        p = tmp_path / "no_such_file.json"
        result = check_ingestion_heartbeat(heartbeat_path=p)
        assert result.ok is False
        assert "not found" in result.detail.lower()

    def test_heartbeat_corrupt_json(self, tmp_path):
        p = tmp_path / "heartbeat.json"
        p.write_text("NOT VALID JSON", encoding="utf-8")
        result = check_ingestion_heartbeat(heartbeat_path=p)
        assert result.ok is False

    def test_heartbeat_age_display_minutes(self, tmp_path):
        p = self._write_heartbeat(tmp_path, age_minutes=15)
        result = check_ingestion_heartbeat(heartbeat_path=p)
        # Detail should contain "m ago" for sub-hour ages
        assert "m ago" in result.detail


# ── run_all_checks ────────────────────────────────────────────────────────────

class TestRunAllChecks:
    def test_returns_four_statuses(self, tmp_path):
        """run_all_checks always returns exactly 4 HealthStatus objects."""
        hb = tmp_path / "heartbeat.json"
        hb.write_text(
            json.dumps({"last_success": datetime.now(timezone.utc).isoformat(), "batch_size": 6}),
            encoding="utf-8",
        )
        with (
            patch("socket.create_connection", side_effect=OSError("refused")),
            patch("urllib.request.urlopen", side_effect=Exception("no ollama")),
        ):
            results = run_all_checks(engine=None, heartbeat_path=hb)
        assert len(results) == 4
        assert all(isinstance(r, HealthStatus) for r in results)

    def test_all_service_names_present(self, tmp_path):
        hb = tmp_path / "heartbeat.json"
        hb.write_text(
            json.dumps({"last_success": datetime.now(timezone.utc).isoformat(), "batch_size": 6}),
            encoding="utf-8",
        )
        with (
            patch("socket.create_connection", side_effect=OSError("refused")),
            patch("urllib.request.urlopen", side_effect=Exception("no ollama")),
        ):
            results = run_all_checks(engine=None, heartbeat_path=hb)
        names = {r.service for r in results}
        assert "Kafka Broker" in names
        assert "TimescaleDB" in names
        assert "Ollama LLM" in names
        assert "Ingestion Daemon" in names
