"""
AirSense — CSV Replay Streamer (Offline Resilience Demo)
File: ingestion/fetch_aqi_replay.py
Phase: 8

Streams pre-saved historical CSV data through Kafka (or direct DB insert)
with sliding synthetic timestamps for offline viva / conference presentations
when Wi-Fi disconnects, external APIs rate-limit, or internet fails.

Modes:
  1. Kafka mode (default): Publishes to aqi_raw topic for the consumer to ingest.
  2. Direct DB mode (--direct-db): Bypasses Kafka, writes straight to TimescaleDB.

Usage:
    python ingestion/fetch_aqi_replay.py                    # Kafka, instant batch
    python ingestion/fetch_aqi_replay.py --speed 1          # Kafka, 1 msg/sec streaming
    python ingestion/fetch_aqi_replay.py --direct-db        # Direct DB, no Kafka needed
    python ingestion/fetch_aqi_replay.py --direct-db --speed 0.5
"""

from __future__ import annotations

import argparse
import json
import sys
import time
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import load_settings
from common.logging_setup import setup_logging

BACKUP_CSV = PROJECT_ROOT / "data" / "backup" / "aqi_7day_backup.csv"
REPLAY_DATA_SOURCE = "Replay-Backup"
SCHEMA_VERSION = "1.0"


# ── Data Loading & Timestamp Sliding ──────────────────────────────────────────


def load_replay_csv(csv_path: Path | None = None) -> pd.DataFrame:
    """
    Load the 7-day backup CSV and return a DataFrame.

    Raises FileNotFoundError if the backup file is missing.
    """
    path = csv_path or BACKUP_CSV
    if not path.exists():
        raise FileNotFoundError(
            f"Backup CSV not found: {path}. "
            "Run python data/prepare_training_data.py to generate it."
        )
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Backup CSV is empty: {path}")
    return df


def apply_sliding_timestamps(
    df: pd.DataFrame,
    now: datetime | None = None,
) -> pd.DataFrame:
    """
    Replace historical timestamps with sliding synthetic current timestamps.

    Shifts all timestamps forward so the most recent CSV entry maps to
    approximately 1 hour ago. This preserves the relative spacing between
    readings while making them appear recent. The 1-hour safety margin
    ensures all timestamps pass the Pydantic future-check validator
    (which rejects readings > 2 hours in the future).

    Also sets data_source = "Replay-Backup" and updates fetched_at to now.
    """
    df = df.copy()
    now = now or datetime.now(timezone.utc)

    csv_max_time = pd.to_datetime(df["time"], utc=True).max()
    # Safety margin: map most recent reading to 1 hour ago
    delta = now - timedelta(hours=1) - csv_max_time

    df["time"] = pd.to_datetime(df["time"], utc=True) + delta
    df["fetched_at"] = now.isoformat()
    df["data_source"] = REPLAY_DATA_SOURCE

    return df


def df_to_readings(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Convert a replay DataFrame to a list of Kafka-ready message dicts.

    Each dict matches the schema expected by the Pydantic AQIReading validator
    and the Kafka consumer pipeline. Handles NaN → None conversion for
    optional pollutant fields.
    """
    readings: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        reading: dict[str, Any] = {
            "schema_version": str(row.get("schema_version", SCHEMA_VERSION)),
            "time": (
                row["time"].isoformat()
                if hasattr(row["time"], "isoformat")
                else str(row["time"])
            ),
            "city": str(row["city"]),
            "city_display_name": str(row["city_display_name"]),
            "country": str(row.get("country", "IN")),
            "station_id": (
                str(row["station_id"])
                if pd.notna(row.get("station_id"))
                else None
            ),
            "aqi": float(row["aqi"]) if pd.notna(row.get("aqi")) else None,
            "pm25": float(row["pm25"]) if pd.notna(row.get("pm25")) else None,
            "pm10": float(row["pm10"]) if pd.notna(row.get("pm10")) else None,
            "no2": float(row["no2"]) if pd.notna(row.get("no2")) else None,
            "co": float(row["co"]) if pd.notna(row.get("co")) else None,
            "so2": float(row["so2"]) if pd.notna(row.get("so2")) else None,
            "o3": float(row["o3"]) if pd.notna(row.get("o3")) else None,
            "lat": float(row["lat"]) if pd.notna(row.get("lat")) else None,
            "lon": float(row["lon"]) if pd.notna(row.get("lon")) else None,
            "data_source": REPLAY_DATA_SOURCE,
            "fetched_at": str(row["fetched_at"]),
        }
        readings.append(reading)

    return readings


# ── Publishing Modes ───────────────────────────────────────────────────────────


def publish_to_kafka(
    readings: list[dict[str, Any]],
    settings: dict[str, Any],
    logger: Any,
    speed: float = 0.0,
) -> tuple[int, int]:
    """
    Publish replay readings to the Kafka aqi_raw topic.

    Parameters
    ----------
    readings : list[dict]
        Pre-processed message dicts with sliding timestamps.
    settings : dict
        Loaded AirSense settings (config.yaml + .env).
    logger : logging.Logger
    speed : float
        Seconds between messages. 0 = instant batch publish.

    Returns
    -------
    (success_count, failure_count)
    """
    from kafka import KafkaProducer
    from kafka.errors import KafkaError

    from ingestion.fetch_aqi import create_producer

    topic = settings["kafka"]["topic_raw"]
    logger.info("Connecting to Kafka at %s, topic=%s...", settings["kafka"]["bootstrap_servers"], topic)

    producer = create_producer(settings)

    success = 0
    failed = 0

    for reading in readings:
        city = reading["city"]
        try:
            future = producer.send(topic, key=city, value=reading)
            future.get(timeout=15)
            success += 1
            logger.info(
                "Published replay %s | AQI=%s | time=%s",
                city,
                reading.get("aqi"),
                reading.get("time"),
            )
        except KafkaError as exc:
            logger.error("Kafka publish failed for %s: %s", city, exc)
            failed += 1

        if speed > 0:
            time.sleep(speed)

    producer.flush()
    producer.close()
    return success, failed


def insert_to_db_direct(
    readings: list[dict[str, Any]],
    settings: dict[str, Any],
    logger: Any,
) -> tuple[int, int]:
    """
    Insert replay readings directly into TimescaleDB, bypassing Kafka.

    This mode requires only TimescaleDB (Docker) — no Kafka, no ZooKeeper,
    no internet. Each reading is validated through the same Pydantic
    AQIReading model used by the Kafka consumer, ensuring data quality.

    Clears any previous replay data first for a clean demo.
    """
    from sqlalchemy import text

    from consumer.db import create_db_engine, ensure_tables_exist, insert_reading
    from consumer.validate import AQIReading

    logger.info("Direct DB mode — connecting to TimescaleDB...")
    engine = create_db_engine(settings)
    ensure_tables_exist(engine)

    # Clear old replay data for a clean demo start
    with engine.begin() as conn:
        deleted = conn.execute(
            text("DELETE FROM aqi_readings WHERE data_source = :src"),
            {"src": REPLAY_DATA_SOURCE},
        )
        logger.info("Cleared %d old replay rows from aqi_readings", deleted.rowcount)

    success = 0
    failed = 0

    for reading in readings:
        city = reading.get("city", "unknown")
        try:
            # Validate through the same Pydantic model as the Kafka consumer
            validated = AQIReading.model_validate(reading)
            row = validated.to_db_dict()
            insert_reading(engine, row)
            success += 1
            if success % 100 == 0:
                logger.info("Inserted %d/%d replay readings...", success, len(readings))
        except Exception as exc:  # noqa: BLE001 — log and continue
            logger.error("Replay insert failed for %s: %s", city, exc)
            failed += 1

    logger.info("Direct DB insert complete: %d success, %d failed", success, failed)
    return success, failed


# ── Main Entry Point ──────────────────────────────────────────────────────────


def run_replay(
    speed: float = 0.0,
    direct_db: bool = False,
    csv_path: Path | None = None,
) -> int:
    """
    Execute the full replay pipeline: load CSV → slide timestamps → publish.

    Parameters
    ----------
    speed : float
        Seconds between messages (0 = instant batch).
    direct_db : bool
        If True, write directly to TimescaleDB (no Kafka required).
    csv_path : Path | None
        Override path to the backup CSV.

    Returns
    -------
    0 on full success, 1 if no readings published, 2 if some failures.
    """
    settings = load_settings()
    logger = setup_logging(settings, name="airsense.replay")

    logger.info("=" * 60)
    logger.info("  AirSense Replay Mode — Offline Resilience Stream")
    logger.info("  Mode: %s", "Direct DB" if direct_db else "Kafka")
    logger.info("  Speed: %s", "instant" if speed == 0 else f"{speed}s/msg")
    logger.info("=" * 60)

    # Step 1: Load backup CSV
    try:
        df = load_replay_csv(csv_path)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("%s", exc)
        return 1

    logger.info("Loaded %d rows from backup CSV (%s cities)", len(df), df["city"].nunique())

    # Step 2: Apply sliding timestamps
    df = apply_sliding_timestamps(df)
    csv_min = pd.to_datetime(df["time"], utc=True).min()
    csv_max = pd.to_datetime(df["time"], utc=True).max()
    logger.info(
        "Sliding timestamps applied: %s to %s (most recent ≈ 1h ago)",
        csv_min.strftime("%Y-%m-%d %H:%M"),
        csv_max.strftime("%Y-%m-%d %H:%M"),
    )

    # Step 3: Convert to message dicts
    readings = df_to_readings(df)
    logger.info("Prepared %d replay readings (data_source=%s)", len(readings), REPLAY_DATA_SOURCE)

    # Step 4: Publish/Insert
    if direct_db:
        success, failed = insert_to_db_direct(readings, settings, logger)
    else:
        success, failed = publish_to_kafka(readings, settings, logger, speed)

    # Summary
    logger.info("=" * 60)
    logger.info("  Replay Complete!")
    logger.info("  Published: %d | Failed: %d | Total: %d", success, failed, len(readings))
    if direct_db:
        logger.info("  Database populated — launch dashboard to view replay data.")
    else:
        logger.info("  Ensure Kafka consumer is running to ingest into TimescaleDB.")
    logger.info("=" * 60)

    if success == 0:
        return 1
    return 0 if failed == 0 else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AirSense Offline Replay — stream historical CSV data without internet.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=0.0,
        help="Seconds between messages (0 = instant batch, 1 = 1 msg/sec).",
    )
    parser.add_argument(
        "--direct-db",
        action="store_true",
        help="Bypass Kafka and write directly to TimescaleDB (only needs Docker).",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Override path to the backup CSV file.",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv) if args.csv else None
    return run_replay(
        speed=args.speed,
        direct_db=args.direct_db,
        csv_path=csv_path,
    )


if __name__ == "__main__":
    raise SystemExit(main())
