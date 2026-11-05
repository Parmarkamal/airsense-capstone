"""Shared configuration loading for AirSense."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class CityConfig:
    slug: str
    display_name: str
    lat: float
    lon: float


def load_settings(config_path: Path | None = None) -> dict[str, Any]:
    """Load config.yaml and merge environment overrides."""
    load_dotenv(PROJECT_ROOT / ".env")

    path = config_path or PROJECT_ROOT / "config.yaml"
    with path.open(encoding="utf-8") as handle:
        settings = yaml.safe_load(handle)

    settings["project_root"] = str(PROJECT_ROOT)
    settings["waqi"]["token"] = os.getenv("WAQI_TOKEN", "")
    settings["kafka"]["bootstrap_servers"] = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", settings["kafka"]["bootstrap_servers"]
    )
    settings["kafka"]["topic_raw"] = os.getenv(
        "KAFKA_TOPIC_RAW", settings["kafka"]["topic_raw"]
    )

    db = settings["database"]
    db["host"] = os.getenv("POSTGRES_HOST", db["host"])
    db["port"] = int(os.getenv("POSTGRES_PORT", db["port"]))
    db["name"] = os.getenv("POSTGRES_DB", db["name"])
    db["user"] = os.getenv("POSTGRES_USER", db["user"])
    db["password"] = os.getenv("POSTGRES_PASSWORD", "")

    settings["ollama"]["base_url"] = os.getenv(
        "OLLAMA_HOST", settings["ollama"]["base_url"]
    )
    settings["ollama"]["model"] = os.getenv(
        "OLLAMA_MODEL", settings["ollama"]["model"]
    )

    return settings


def get_cities(settings: dict[str, Any]) -> list[CityConfig]:
    return [
        CityConfig(
            slug=city["slug"],
            display_name=city["display_name"],
            lat=float(city["lat"]),
            lon=float(city["lon"]),
        )
        for city in settings["waqi"]["cities"]
    ]


def require_waqi_token(settings: dict[str, Any]) -> str:
    token = settings["waqi"].get("token", "").strip()
    if not token or token == "your_waqi_token_here":
        raise ValueError(
            "WAQI_TOKEN missing. Copy .env.example to .env and add your token "
            "from https://aqicn.org/data-platform/token/"
        )
    return token
