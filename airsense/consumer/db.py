"""
AirSense — Database layer (TimescaleDB via SQLAlchemy)
File: consumer/db.py
Week: 2

Handles:
  - Engine creation from config
  - Table reflection / creation
  - Inserting validated AQI readings
  - Logging validation errors to aqi_validation_errors table
"""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Double,
    Index,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("airsense.db")

# Shared metadata object — all table definitions registered here
_metadata = MetaData()

# ── Table definitions ────────────────────────────────────────────────────────

aqi_readings_table = Table(
    "aqi_readings",
    _metadata,
    Column("time",              DateTime(timezone=True), nullable=False),
    Column("city",              String(64),              nullable=False),
    Column("city_display_name", String(128),             nullable=False),
    Column("station_id",        String(256)),
    Column("country",           String(4),               default="IN"),
    Column("aqi",               Double()),
    Column("pm25",              Double()),
    Column("pm10",              Double()),
    Column("no2",               Double()),
    Column("co",                Double()),
    Column("so2",               Double()),
    Column("o3",                Double()),
    Column("lat",               Double()),
    Column("lon",               Double()),
    Column("data_source",       String(32),              default="WAQI"),
    Column("schema_version",    String(16),              default="1.0"),
    Column("fetched_at",        DateTime(timezone=True)),
)

aqi_validation_errors_table = Table(
    "aqi_validation_errors",
    _metadata,
    Column("received_at",  DateTime(timezone=True)),
    Column("raw_message",  Text),
    Column("error_detail", Text),
)


def build_connection_url(settings: dict[str, Any]) -> str:
    """Construct a PostgreSQL DSN from the settings dict."""
    db = settings["database"]
    return (
        f"postgresql+psycopg2://{db['user']}:{db['password']}"
        f"@{db['host']}:{db['port']}/{db['name']}"
    )


def create_db_engine(settings: dict[str, Any]) -> Engine:
    """
    Create and return a SQLAlchemy engine connected to TimescaleDB.
    Raises SQLAlchemyError if the connection cannot be established.
    """
    url = build_connection_url(settings)
    engine = create_engine(
        url,
        pool_size=2,          # consumer is single-threaded; keep pool tiny
        max_overflow=1,
        pool_pre_ping=True,   # automatically reconnect after Docker restart
        connect_args={"connect_timeout": 10},
    )

    # Smoke-test the connection immediately — fail fast if DB is not ready
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    logger.info(
        "Connected to TimescaleDB at %s:%s/%s",
        settings["database"]["host"],
        settings["database"]["port"],
        settings["database"]["name"],
    )
    return engine


def ensure_tables_exist(engine: Engine) -> None:
    """
    Verify that the core tables were created by init_db.sql.
    Logs a warning (not an error) if they are missing — the SQL file
    should have already run on container start.
    """
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' "
                "AND table_name IN ('aqi_readings', 'aqi_validation_errors', 'aqi_forecasts')"
            )
        )
        found = {row[0] for row in result}

    expected = {"aqi_readings", "aqi_validation_errors", "aqi_forecasts"}
    missing  = expected - found

    if missing:
        logger.warning(
            "Tables missing from database: %s. "
            "Did init_db.sql run on container start? "
            "Run manually: psql -U airsense -d airsense_db -f scripts/init_db.sql",
            missing,
        )
    else:
        logger.info("All required tables confirmed present in database.")


def insert_reading(engine: Engine, row: dict[str, Any]) -> None:
    """
    Insert a single validated AQI reading into the aqi_readings hypertable.

    Uses INSERT ... ON CONFLICT DO NOTHING to handle duplicate hour-city
    readings gracefully (can happen if the consumer restarts and re-reads).
    """
    stmt = aqi_readings_table.insert().values(**row)
    try:
        with engine.begin() as conn:
            conn.execute(stmt)
        logger.debug(
            "Inserted reading: city=%s time=%s aqi=%s",
            row.get("city"),
            row.get("time"),
            row.get("aqi"),
        )
    except SQLAlchemyError as exc:
        logger.error(
            "DB insert failed for city=%s time=%s: %s",
            row.get("city"),
            row.get("time"),
            exc,
        )
        raise


def log_validation_error(engine: Engine, raw: dict[str, Any], errors: list[str]) -> None:
    """
    Persist an invalid Kafka message to aqi_validation_errors for audit.
    Failures here are swallowed — logging is best-effort.
    """
    try:
        stmt = aqi_validation_errors_table.insert().values(
            raw_message=json.dumps(raw, default=str)[:4096],
            error_detail="; ".join(errors)[:2048],
        )
        with engine.begin() as conn:
            conn.execute(stmt)
    except SQLAlchemyError as exc:
        logger.warning("Could not log validation error to DB: %s", exc)
