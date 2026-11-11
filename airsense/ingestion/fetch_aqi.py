"""
AirSense — Hybrid WAQI + Open-Meteo fetcher → Kafka producer
File: ingestion/fetch_aqi.py
Phase: 1 + 5

Publishes validated JSON readings to topic `aqi_raw` for each city in config.yaml.
Queries WAQI first; falls back to Open-Meteo when WAQI is unavailable or stale (>2h).

Run:
    python ingestion/fetch_aqi.py

Requires:
    - WAQI_TOKEN in .env
    - Kafka broker on localhost:9092 (ZooKeeper + Kafka)
    - Topic aqi_raw (create via scripts/create_kafka_topic.bat)
"""

from __future__ import annotations

import json
import logging
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
from common.cpcb_calculator import calculate_cpcb_naqi, convert_co_ug_to_mg
from common.logging_setup import setup_logging

SCHEMA_VERSION = "1.0"
POLLUTANTS = ("pm25", "pm10", "no2", "co", "so2", "o3")
WAQI_STALE_HOURS = 2.0
OPEN_METEO_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
OPEN_METEO_CURRENT = (
    "us_aqi,pm2_5,pm10,nitrogen_dioxide,carbon_monoxide,sulphur_dioxide,ozone"
)

logger = logging.getLogger("airsense.fetch")


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


def _parse_iso_to_utc(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _is_reading_stale(reading: dict[str, Any], max_age_hours: float = WAQI_STALE_HOURS) -> bool:
    """Return True when reading.time is older than max_age_hours (or unparseable)."""
    parsed = _parse_iso_to_utc(reading.get("time"))
    if parsed is None:
        return True
    age_hours = (datetime.now(timezone.utc) - parsed).total_seconds() / 3600.0
    return age_hours > max_age_hours


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_open_meteo_reading(
    city: CityConfig,
    timeout: int,
    session: requests.Session,
) -> dict[str, Any]:
    """
    Fetch current hourly air-quality observations from Open-Meteo for city GPS.
    Produces the same Pydantic-compatible schema as WAQI readings.
    """
    params = {
        "latitude": city.lat,
        "longitude": city.lon,
        "current": OPEN_METEO_CURRENT,
        "timezone": "UTC",
    }
    response = session.get(OPEN_METEO_URL, params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    current = payload.get("current") or {}
    if not current:
        raise ValueError(f"Open-Meteo returned empty current block for {city.slug}")

    aqi = _as_float(current.get("us_aqi"))
    pm25 = _as_float(current.get("pm2_5"))
    if aqi is None and pm25 is None:
        raise ValueError(
            f"Open-Meteo reading for {city.slug} has neither us_aqi nor pm2_5"
        )

    pm10 = _as_float(current.get("pm10"))
    no2 = _as_float(current.get("nitrogen_dioxide"))
    co_raw = _as_float(current.get("carbon_monoxide"))
    co_mg = convert_co_ug_to_mg(co_raw)
    so2 = _as_float(current.get("sulphur_dioxide"))
    o3 = _as_float(current.get("ozone"))

    # Compute CPCB NAQI (1-hour indicative snapshot)
    cpcb_result = calculate_cpcb_naqi(
        {
            "pm25": pm25,
            "pm10": pm10,
            "no2": no2,
            "co": co_mg,
            "so2": so2,
            "o3": o3,
        },
        is_indicative=True,
    )

    obs_time = _parse_iso_to_utc(current.get("time")) or datetime.now(timezone.utc)
    obs_age = max(0.0, (datetime.now(timezone.utc) - obs_time).total_seconds() / 3600.0)

    return {
        "schema_version": SCHEMA_VERSION,
        "time": obs_time.isoformat(),
        "station_id": f"open-meteo-{city.slug}",
        "city": city.slug,
        "city_display_name": city.display_name,
        "country": "IN",
        "aqi": aqi,
        "pm25": pm25,
        "pm10": pm10,
        "no2": no2,
        "co": co_mg if co_mg is not None else co_raw,
        "so2": so2,
        "o3": o3,
        "lat": float(city.lat),
        "lon": float(city.lon),
        "data_source": "Open-Meteo-Live",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cpcb_aqi": cpcb_result.get("aqi"),
        "prominent_pollutant": cpcb_result.get("prominent_pollutant"),
        "source_type": "atmospheric_model",
        "station_operator": "ECMWF / CAMS IFS-AER (~45km)",
        "calculation_method": "CPCB_NAQI_2014_IITK",
        "observation_age_hours": round(obs_age, 2),
    }


def _fetch_waqi_reading(
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
    geo = (data.get("city") or {}).get("geo") or []
    lat = city.lat
    lon = city.lon
    if isinstance(geo, (list, tuple)) and len(geo) >= 2:
        try:
            lat = float(geo[0])
            lon = float(geo[1])
        except (TypeError, ValueError):
            pass

    pm25 = _parse_pollutant(iaqi, "pm25")
    pm10 = _parse_pollutant(iaqi, "pm10")
    no2 = _parse_pollutant(iaqi, "no2")
    co = _parse_pollutant(iaqi, "co")
    so2 = _parse_pollutant(iaqi, "so2")
    o3 = _parse_pollutant(iaqi, "o3")

    co_mg = convert_co_ug_to_mg(co) if (co is not None and co > 50.0) else co

    cpcb_result = calculate_cpcb_naqi(
        {
            "pm25": pm25,
            "pm10": pm10,
            "no2": no2,
            "co": co_mg,
            "so2": so2,
            "o3": o3,
        },
        is_indicative=True,
    )

    attributions = data.get("attributions") or []
    operator_name = "CPCB / SPCB Ground Station"
    if attributions and isinstance(attributions, list) and attributions[0].get("name"):
        operator_name = attributions[0]["name"]

    raw_ts = _parse_timestamp(data)
    obs_time = _parse_iso_to_utc(raw_ts) or datetime.now(timezone.utc)
    obs_age = max(0.0, (datetime.now(timezone.utc) - obs_time).total_seconds() / 3600.0)

    return {
        "schema_version": SCHEMA_VERSION,
        "time": raw_ts,
        "station_id": _station_id(data, city),
        "city": city.slug,
        "city_display_name": city.display_name,
        "country": "IN",
        "aqi": float(data["aqi"]) if data.get("aqi") is not None else None,
        "pm25": pm25,
        "pm10": pm10,
        "no2": no2,
        "co": co_mg if co_mg is not None else co,
        "so2": so2,
        "o3": o3,
        "lat": float(data.get("lat") or lat),
        "lon": float(data.get("lon") or lon),
        "data_source": "WAQI",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cpcb_aqi": cpcb_result.get("aqi"),
        "prominent_pollutant": cpcb_result.get("prominent_pollutant"),
        "source_type": "ground_station",
        "station_operator": operator_name,
        "calculation_method": "CPCB_NAQI_2014_IITK",
        "observation_age_hours": round(obs_age, 2),
    }


def fetch_city_reading(
    city: CityConfig,
    token: str,
    base_url: str,
    timeout: int,
    session: requests.Session,
) -> dict[str, Any]:
    """
    Hybrid fetch: WAQI primary, Open-Meteo fallback on HTTP/status failure or stale (>2h) data.
    """
    try:
        reading = _fetch_waqi_reading(city, token, base_url, timeout, session)
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        logger.warning(
            "WAQI unavailable for %s (%s) — falling back to Open-Meteo",
            city.slug,
            exc,
        )
        return fetch_open_meteo_reading(city, timeout, session)

    if _is_reading_stale(reading, WAQI_STALE_HOURS):
        logger.warning(
            "WAQI timestamp stale for %s (time=%s, >%.0fh) — switching to Open-Meteo",
            city.slug,
            reading.get("time"),
            WAQI_STALE_HOURS,
        )
        try:
            return fetch_open_meteo_reading(city, timeout, session)
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            logger.error(
                "Open-Meteo fallback failed for %s after stale WAQI: %s — keeping WAQI row",
                city.slug,
                exc,
            )
            return reading

    return reading


def create_producer(settings: dict[str, Any]) -> KafkaProducer:
    kafka_cfg = settings["kafka"]
    return KafkaProducer(
        bootstrap_servers=kafka_cfg["bootstrap_servers"],
        acks=kafka_cfg.get("producer_acks", "all"),
        request_timeout_ms=kafka_cfg.get("request_timeout_ms", 30000),
        api_version=(2, 0, 2),
        value_serializer=lambda value: json.dumps(value, default=str).encode("utf-8"),
        key_serializer=lambda key: key.encode("utf-8") if key else None,
    )


def publish_readings(
    producer: KafkaProducer,
    topic: str,
    readings: list[dict[str, Any]],
    log: Any,
) -> tuple[int, int]:
    success = 0
    failed = 0

    for reading in readings:
        city = reading["city"]
        try:
            future = producer.send(topic, key=city, value=reading)
            future.get(timeout=15)
            log.info(
                "Published %s | AQI=%s | source=%s | time=%s | station=%s",
                city,
                reading.get("aqi"),
                reading.get("data_source"),
                reading.get("time"),
                reading.get("station_id"),
            )
            success += 1
        except KafkaError as exc:
            log.error("Kafka publish failed for %s: %s", city, exc)
            failed += 1

    producer.flush()
    return success, failed


def insert_direct_to_db(
    readings: list[dict[str, Any]],
    settings: dict[str, Any],
    log: logging.Logger,
) -> tuple[int, int]:
    """
    Direct TimescaleDB insertion fallback when Kafka broker is offline.
    Validates each reading through the Pydantic AQIReading model.
    """
    from consumer.db import create_db_engine, ensure_tables_exist, insert_reading
    from consumer.validate import AQIReading

    log.info("Direct DB mode: Inserting %d live readings to TimescaleDB...", len(readings))
    engine = create_db_engine(settings)
    ensure_tables_exist(engine)

    success = 0
    failed = 0
    for reading in readings:
        city = reading.get("city", "unknown")
        try:
            validated = AQIReading.model_validate(reading)
            row = validated.to_db_dict()
            insert_reading(engine, row)
            success += 1
            log.info("Direct DB stored: %s | AQI=%s | source=%s", city, reading.get("aqi"), reading.get("data_source"))
        except Exception as exc:
            log.error("Direct DB store failed for %s: %s", city, exc)
            failed += 1

    # Record heartbeat
    heartbeat_path = PROJECT_ROOT / "logs" / "heartbeat.json"
    try:
        heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
        heartbeat_path.write_text(
            json.dumps({
                "last_success": datetime.now(timezone.utc).isoformat(),
                "batch_size": success,
                "source": "Direct-DB-Live",
            }),
            encoding="utf-8",
        )
    except Exception:
        pass

    return success, failed


def run_fetch() -> int:
    """Fetch all cities sequentially; push readings to Kafka, or fallback to direct TimescaleDB."""
    settings = load_settings()
    log = setup_logging(settings, name="airsense.fetch")
    global logger
    logger = log

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
                log.info(
                    "Fetched %s (%s) AQI=%s source=%s time=%s",
                    city.display_name,
                    city.slug,
                    reading.get("aqi"),
                    reading.get("data_source"),
                    reading.get("time"),
                )
            except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
                errors += 1
                log.error("Fetch failed for %s: %s", city.slug, exc)

            if index < len(cities) - 1:
                time.sleep(delay)

    if not readings:
        log.error("No readings fetched — aborting publish")
        return 1

    # Console summary for verification (Phase 5 acceptance)
    today_utc = datetime.now(timezone.utc).date()
    fresh_count = 0
    for reading in readings:
        parsed = _parse_iso_to_utc(reading.get("time"))
        same_day = parsed is not None and parsed.date() == today_utc
        if same_day:
            fresh_count += 1
        log.info(
            "VERIFY %s | source=%s | time=%s | same_day=%s | aqi=%s",
            reading["city"],
            reading.get("data_source"),
            reading.get("time"),
            same_day,
            reading.get("aqi"),
        )
    log.info(
        "Freshness summary: %d/%d cities have current-day timestamps",
        fresh_count,
        len(readings),
    )

    # Check for direct-db flag or attempt Kafka first
    use_direct_db = "--direct-db" in sys.argv
    producer = None
    if not use_direct_db:
        try:
            producer = create_producer(settings)
        except Exception as exc:
            log.warning(
                "Kafka broker unavailable (%s). Falling back to direct TimescaleDB insertion...",
                exc,
            )

    if producer is not None:
        try:
            success, publish_failed = publish_readings(producer, topic, readings, log)
        except Exception as exc:
            log.warning("Kafka publish error: %s — falling back to direct DB", exc)
            success, publish_failed = 0, len(readings)
        finally:
            try:
                producer.close()
            except Exception:
                pass

        if success == 0 and publish_failed > 0:
            log.warning("Kafka publish resulted in 0 successes — falling back to direct DB insertion...")
            success, publish_failed = insert_direct_to_db(readings, settings, log)
        else:
            # Record heartbeat on successful Kafka publish
            heartbeat_path = PROJECT_ROOT / "logs" / "heartbeat.json"
            try:
                heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
                heartbeat_path.write_text(
                    json.dumps({
                        "last_success": datetime.now(timezone.utc).isoformat(),
                        "batch_size": success,
                        "source": "Kafka-Live",
                    }),
                    encoding="utf-8",
                )
            except Exception:
                pass
    else:
        success, publish_failed = insert_direct_to_db(readings, settings, log)

    log.info(
        "Fetch complete — fetched=%d errors=%d stored/published=%d failed=%d",
        len(readings),
        errors,
        success,
        publish_failed,
    )

    if success > 0:
        try:
            from consumer.db import create_db_engine
            from ml.training.predict_forecast import run_all_forecasts_and_save
            db_engine = create_db_engine(settings)
            run_all_forecasts_and_save(db_engine)
            log.info("Auto-refreshed 48-hour ML forecasts with latest live telemetry.")
        except Exception as fc_err:
            log.warning("Could not auto-refresh forecasts: %s", fc_err)

    if success == 0:
        return 1
    return 0 if publish_failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(run_fetch())
