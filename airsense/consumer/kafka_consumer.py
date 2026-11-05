"""
AirSense — Kafka Consumer (continuous, production-grade)
File: consumer/kafka_consumer.py
Week: 2

Reads from Kafka topic `aqi_raw`, validates every message with Pydantic,
writes valid rows to TimescaleDB, logs invalid ones to aqi_validation_errors.

Run:
    python consumer/kafka_consumer.py

Stop:
    Ctrl+C  (graceful shutdown — commits offsets before exit)
"""

from __future__ import annotations

import signal
import sys
import time
from pathlib import Path
from typing import Any

from kafka import KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import load_settings
from common.logging_setup import setup_logging
from consumer.db import create_db_engine, ensure_tables_exist, insert_reading, log_validation_error
from consumer.validate import validate_message

# ── Tunables ────────────────────────────────────────────────────────────────
POLL_TIMEOUT_MS        = 1_000   # how long to wait for new messages per poll
MAX_POLL_RECORDS       = 10      # max messages per poll (keep RAM low)
KAFKA_RETRY_SECONDS    = 10      # wait between reconnect attempts
MAX_KAFKA_RETRIES      = 12      # give up after 2 minutes
DB_RETRY_SECONDS       = 15      # wait if DB is temporarily unavailable

# ── Graceful shutdown flag ───────────────────────────────────────────────────
_running = True


def _handle_shutdown(signum: int, frame: Any) -> None:
    global _running
    _running = False


signal.signal(signal.SIGINT,  _handle_shutdown)
signal.signal(signal.SIGTERM, _handle_shutdown)


# ── Kafka consumer factory ───────────────────────────────────────────────────

def create_consumer(settings: dict[str, Any]) -> KafkaConsumer:
    """
    Create a KafkaConsumer with manual commit (enable_auto_commit=False).
    Manual commit means we only acknowledge a message AFTER it has been
    successfully written to TimescaleDB — zero data loss on crash.
    """
    kafka_cfg = settings["kafka"]
    return KafkaConsumer(
        kafka_cfg["topic_raw"],
        bootstrap_servers=kafka_cfg["bootstrap_servers"],
        group_id=kafka_cfg.get("group_id", "airsense_consumer"),
        auto_offset_reset="earliest",       # catch up on missed messages after restart
        enable_auto_commit=False,           # we commit manually after successful DB insert
        max_poll_records=MAX_POLL_RECORDS,
        session_timeout_ms=30_000,
        heartbeat_interval_ms=10_000,
        request_timeout_ms=40_000,
        value_deserializer=None,            # raw bytes — validate.py handles decoding
    )


# ── Main loop ────────────────────────────────────────────────────────────────

def run_consumer() -> int:
    settings = load_settings()
    logger   = setup_logging(settings, name="airsense.consumer")

    # ── Connect to DB ────────────────────────────────────────────────────────
    logger.info("Connecting to TimescaleDB...")
    for attempt in range(1, 4):
        try:
            engine = create_db_engine(settings)
            ensure_tables_exist(engine)
            break
        except Exception as exc:
            logger.warning(
                "DB connection attempt %d/3 failed: %s — retrying in %ds",
                attempt, exc, DB_RETRY_SECONDS,
            )
            if attempt == 3:
                logger.error("Cannot connect to TimescaleDB after 3 attempts. Exiting.")
                return 1
            time.sleep(DB_RETRY_SECONDS)

    # ── Connect to Kafka ─────────────────────────────────────────────────────
    logger.info(
        "Connecting to Kafka at %s, topic=%s, group=%s",
        settings["kafka"]["bootstrap_servers"],
        settings["kafka"]["topic_raw"],
        settings["kafka"].get("group_id", "airsense_consumer"),
    )

    consumer: KafkaConsumer | None = None
    for attempt in range(1, MAX_KAFKA_RETRIES + 1):
        try:
            consumer = create_consumer(settings)
            logger.info("Kafka consumer ready — waiting for messages...")
            break
        except NoBrokersAvailable as exc:
            logger.warning(
                "Kafka not available (attempt %d/%d): %s — retrying in %ds",
                attempt, MAX_KAFKA_RETRIES, exc, KAFKA_RETRY_SECONDS,
            )
            if attempt == MAX_KAFKA_RETRIES:
                logger.error("Cannot reach Kafka broker. Is ZooKeeper + Kafka running?")
                return 1
            time.sleep(KAFKA_RETRY_SECONDS)

    # ── Stats counters ───────────────────────────────────────────────────────
    total_received  = 0
    total_valid     = 0
    total_invalid   = 0
    total_db_errors = 0

    # ── Poll loop ────────────────────────────────────────────────────────────
    try:
        while _running:
            try:
                records = consumer.poll(timeout_ms=POLL_TIMEOUT_MS)
            except KafkaError as exc:
                logger.error("Kafka poll error: %s", exc)
                continue

            if not records:
                continue  # no messages yet — loop back and wait

            for partition, messages in records.items():
                for msg in messages:
                    total_received += 1

                    # ── Validate ─────────────────────────────────────────────
                    result = validate_message(msg.value)

                    if not result.is_valid:
                        total_invalid += 1
                        logger.warning(
                            "INVALID message #%d (city=%s): %s",
                            total_received,
                            result.raw.get("city", "unknown"),
                            " | ".join(result.errors),
                        )
                        log_validation_error(engine, result.raw, result.errors)
                        # Commit offset even for invalid — we've handled it
                        consumer.commit()
                        continue

                    # ── Insert to DB ──────────────────────────────────────────
                    row = result.reading.to_db_dict()
                    try:
                        insert_reading(engine, row)
                        total_valid += 1
                        logger.info(
                            "✓ Stored: city=%-14s  AQI=%-5s  PM2.5=%-5s  time=%s",
                            row["city"],
                            f"{row['aqi']:.0f}" if row["aqi"] is not None else "N/A",
                            f"{row['pm25']:.1f}" if row["pm25"] is not None else "N/A",
                            row["time"].strftime("%Y-%m-%d %H:%M UTC"),
                        )
                        consumer.commit()
                    except Exception as exc:
                        total_db_errors += 1
                        logger.error(
                            "DB insert failed for city=%s: %s — NOT committing offset",
                            row.get("city"),
                            exc,
                        )
                        # Do NOT commit — message will be re-delivered after restart

    finally:
        logger.info("Shutting down consumer...")
        if consumer:
            consumer.close()
        logger.info(
            "Session summary — received=%d  valid=%d  invalid=%d  db_errors=%d",
            total_received, total_valid, total_invalid, total_db_errors,
        )

    return 0 if total_db_errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run_consumer())
