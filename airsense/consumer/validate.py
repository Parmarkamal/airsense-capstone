"""
AirSense — Pydantic v2 validation models for AQI readings
File: consumer/validate.py
Week: 2

Every Kafka message from `aqi_raw` is passed through AQIReading before
being written to the database. Invalid messages are logged and discarded
— they NEVER reach TimescaleDB.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger("airsense.validate")


class AQIReading(BaseModel):
    """Validated, clean AQI reading ready for database insertion."""

    # ── Required fields ──────────────────────────────────────────────────────
    schema_version:    str
    time:              datetime
    city:              str               = Field(min_length=1, max_length=64)
    city_display_name: str               = Field(min_length=1, max_length=128)
    country:           str               = Field(default="IN", max_length=4)
    station_id:        str | None        = None
    data_source:       str               = Field(default="WAQI", max_length=32)
    fetched_at:        datetime | None   = None

    # ── Coordinates ───────────────────────────────────────────────────────────
    lat: float | None = Field(default=None, ge=-90.0,  le=90.0)
    lon: float | None = Field(default=None, ge=-180.0, le=180.0)

    # ── Pollutants (all optional — not every station reports everything) ──────
    aqi:  float | None = Field(default=None, ge=0, le=999)
    pm25: float | None = Field(default=None, ge=0, le=1000)
    pm10: float | None = Field(default=None, ge=0, le=1000)
    no2:  float | None = Field(default=None, ge=0, le=2000)
    co:   float | None = Field(default=None, ge=0, le=50000)
    so2:  float | None = Field(default=None, ge=0, le=2000)
    o3:   float | None = Field(default=None, ge=0, le=600)

    # ── Scientific Provenance & CPCB NAQI (2014) Fields ──────────────────────
    cpcb_aqi:              float | None = Field(default=None, ge=0, le=500)
    prominent_pollutant:   str | None   = Field(default=None, max_length=32)
    source_type:           str | None   = Field(default=None, max_length=64)
    station_operator:      str | None   = Field(default=None, max_length=128)
    calculation_method:    str | None   = Field(default=None, max_length=64)
    observation_age_hours: float | None = Field(default=None, ge=0)

    # ── Timestamp validation ─────────────────────────────────────────────────
    @field_validator("time", mode="before")
    @classmethod
    def parse_time(cls, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc)
        try:
            dt = datetime.fromisoformat(str(value))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Cannot parse timestamp '{value}': {exc}") from exc

    @field_validator("fetched_at", mode="before")
    @classmethod
    def parse_fetched_at(cls, value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc)
        try:
            dt = datetime.fromisoformat(str(value))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except (ValueError, TypeError):
            return None

    @model_validator(mode="after")
    def check_timestamp_not_future(self) -> "AQIReading":
        """Reject readings timestamped more than 2 hours in the future."""
        now_utc = datetime.now(timezone.utc)
        delta = (self.time - now_utc).total_seconds()
        if delta > 7200:
            raise ValueError(
                f"Timestamp {self.time.isoformat()} is {delta/3600:.1f}h in the future"
            )
        return self

    @model_validator(mode="after")
    def require_aqi_or_pm25(self) -> "AQIReading":
        """At least one of AQI or PM2.5 must be present — otherwise the row is useless."""
        if self.aqi is None and self.pm25 is None:
            raise ValueError(
                f"Reading for '{self.city}' has neither AQI nor PM2.5 — discarding"
            )
        return self

    def to_db_dict(self) -> dict[str, Any]:
        """Return a flat dict ready for SQLAlchemy insert."""
        return {
            "time":                  self.time,
            "city":                  self.city,
            "city_display_name":     self.city_display_name,
            "station_id":            self.station_id,
            "country":               self.country,
            "aqi":                   self.aqi,
            "pm25":                  self.pm25,
            "pm10":                  self.pm10,
            "no2":                   self.no2,
            "co":                    self.co,
            "so2":                   self.so2,
            "o3":                    self.o3,
            "lat":                   self.lat,
            "lon":                   self.lon,
            "data_source":           self.data_source,
            "schema_version":        self.schema_version,
            "fetched_at":            self.fetched_at,
            "cpcb_aqi":              self.cpcb_aqi,
            "prominent_pollutant":   self.prominent_pollutant,
            "source_type":           self.source_type,
            "station_operator":      self.station_operator,
            "calculation_method":    self.calculation_method,
            "observation_age_hours": self.observation_age_hours,
        }


class ValidationResult:
    """Container returned by validate_message() — always check .is_valid first."""

    __slots__ = ("reading", "errors", "raw")

    def __init__(
        self,
        reading: AQIReading | None,
        errors: list[str],
        raw: dict[str, Any],
    ) -> None:
        self.reading = reading
        self.errors  = errors
        self.raw     = raw

    @property
    def is_valid(self) -> bool:
        return self.reading is not None


def validate_message(raw_bytes: bytes) -> ValidationResult:
    """
    Deserialise a Kafka message and run Pydantic validation.

    Returns a ValidationResult. If .is_valid is True, .reading holds the
    clean AQIReading. If False, .errors contains human-readable reasons.
    """
    # Step 1: JSON decode
    try:
        data: dict[str, Any] = json.loads(raw_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return ValidationResult(
            reading=None,
            errors=[f"JSON decode error: {exc}"],
            raw={},
        )

    if not isinstance(data, dict):
        return ValidationResult(
            reading=None,
            errors=["Message is not a JSON object"],
            raw=data,
        )

    # Step 2: Pydantic validation
    try:
        reading = AQIReading.model_validate(data)
        return ValidationResult(reading=reading, errors=[], raw=data)
    except Exception as exc:  # pydantic.ValidationError
        # Extract all error messages from Pydantic's error list
        errors: list[str] = []
        if hasattr(exc, "errors"):
            for err in exc.errors():
                loc = " → ".join(str(p) for p in err.get("loc", []))
                msg = err.get("msg", str(err))
                errors.append(f"{loc}: {msg}" if loc else msg)
        else:
            errors = [str(exc)]

        logger.warning(
            "Validation failed for city='%s': %s",
            data.get("city", "unknown"),
            "; ".join(errors),
        )
        return ValidationResult(reading=None, errors=errors, raw=data)
