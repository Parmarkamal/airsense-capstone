"""
AirSense — WAQI fetcher → Kafka producer
File: ingestion/fetch_aqi.py
Week: 1

Publishes validated JSON readings to topic `aqi_raw` for each city in config.yaml.

Run:
    python ingestion/fetch_aqi.py

Requires:
    - WAQI_TOKEN in .env
    - Kafka broker on localhost:9092 (ZooKeeper + Kafka)
    - Topic aqi_raw (create via scripts/create_kafka_topic.bat)
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from kafka import KafkaProducer
from kafka.errors import KafkaError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import CityConfig, get_cities, load_settings, require_waqi_token
from common.logging_setup import setup_logging

SCHEMA_VERSION = "1.0"
POLLUTANTS = ("pm25", "pm10", "no2", "co", "so2", "o3")


def _parse_pollutant(iaqi: dict[str, Any], key: str) -> float | None:
    entry = iaqi.get(key)
    if not entry:
        return None
    value = entry.get("v")
    return float(value) if value is not None else None


def _parse_timestamp(data: dict[str, Any]) -> str:
    time_info = data.get("time") or {}
    iso_value = time_info.get("iso") or time_info.get("s")
    if iso_value:
        return str(iso_value)
    return datetime.now(timezone.utc).isoformat()


def _station_id(data: dict[str, Any], city: CityConfig) -> str:
    if data.get("idx") is not None:
        return str(data["idx"])
    city_meta = data.get("city") or {}
    if city_meta.get("name"):
        return str(city_meta["name"])
    return city.slug


def fetch_city_reading(
    city: CityConfig,
    token: str,
    base_url: str,
    timeout: int,
    session: requests.Session,
) -> dict[str, Any]:
    url = f"{base_url}/{city.slug}/"
    response = session.get(url, params={"token": token}, timeout=timeout)
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "ok":
        raise ValueError(
            f"WAQI error for {city.slug}: {payload.get('data', payload.get('status'))}"
        )

    data = payload["data"]
    iaqi = data.get("iaqi") or {}

    return {
        "schema_version": SCHEMA_VERSION,
        "time": _parse_timestamp(data),
        "station_id": _station_id(data, city),
        "city": city.slug,
        "city_display_name": city.display_name,
        "country": "IN",
        "aqi": float(data["aqi"]) if data.get("aqi") is not None else None,
        "pm25": _parse_pollutant(iaqi, "pm25"),
        "pm10": _parse_pollutant(iaqi, "pm10"),
        "no2": _parse_pollutant(iaqi, "no2"),
        "co": _parse_pollutant(iaqi, "co"),
        "so2": _parse_pollutant(iaqi, "so2"),
        "o3": _parse_pollutant(iaqi, "o3"),
        "lat": float(data.get("lat") or city.lat),
        "lon": float(data.get("lon") or city.lon),
        "data_source": "WAQI",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def create_producer(settings: dict[str, Any]) -> KafkaProducer:
    kafka_cfg = settings["kafka"]
    return KafkaProducer(
        bootstrap_servers=kafka_cfg["bootstrap_servers"],
        acks=kafka_cfg.get("producer_acks", "all"),
        request_timeout_ms=kafka_cfg.get("request_timeout_ms", 30000),
        value_serializer=lambda value: json.dumps(value, default=str).encode("utf-8"),
        key_serializer=lambda key: key.encode("utf-8") if key else None,
    )


def publish_readings(
    producer: KafkaProducer,
    topic: str,
    readings: list[dict[str, Any]],
    logger: Any,
) -> tuple[int, int]:
    success = 0
    failed = 0

    for reading in readings:
        city = reading["city"]
        try:
            future = producer.send(topic, key=city, value=reading)
            future.get(timeout=15)
            logger.info(
                "Published %s | AQI=%s | station=%s",
                city,
                reading.get("aqi"),
                reading.get("station_id"),
            )
            success += 1
        except KafkaError as exc:
            logger.error("Kafka publish failed for %s: %s", city, exc)
            failed += 1

    producer.flush()
    return success, failed


def run_fetch() -> int:
    settings = load_settings()
    logger = setup_logging(settings, name="airsense.fetch")
    token = require_waqi_token(settings)

    waqi_cfg = settings["waqi"]
    cities = get_cities(settings)
    topic = settings["kafka"]["topic_raw"]
    delay = float(waqi_cfg.get("request_delay_seconds", 1.2))
    timeout = int(waqi_cfg.get("timeout_seconds", 30))

    readings: list[dict[str, Any]] = []
    errors = 0

    with requests.Session() as session:
        session.headers.update({"User-Agent": "AirSense/1.0 (academic capstone)"})

        for index, city in enumerate(cities):
            try:
                reading = fetch_city_reading(
                    city=city,
                    token=token,
                    base_url=waqi_cfg["base_url"],
                    timeout=timeout,
                    session=session,
                )
                readings.append(reading)
                logger.info(
                    "Fetched %s (%s) AQI=%s",
                    city.display_name,
                    city.slug,
                    reading.get("aqi"),
                )
            except (requests.RequestException, ValueError, KeyError) as exc:
                errors += 1
                logger.error("Fetch failed for %s: %s", city.slug, exc)

            if index < len(cities) - 1:
                time.sleep(delay)

    if not readings:
        logger.error("No readings fetched — aborting Kafka publish")
        return 1

    try:
        producer = create_producer(settings)
    except KafkaError as exc:
        logger.error("Cannot connect to Kafka at %s: %s", settings["kafka"]["bootstrap_servers"], exc)
        return 1

    success, publish_failed = publish_readings(producer, topic, readings, logger)
    producer.close()

    logger.info(
        "Fetch complete — fetched=%d errors=%d published=%d publish_failed=%d topic=%s",
        len(readings),
        errors,
        success,
        publish_failed,
        topic,
    )

    if success == 0:
        return 1
    return 0 if publish_failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(run_fetch())
