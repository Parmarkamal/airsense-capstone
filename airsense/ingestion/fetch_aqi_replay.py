"""
AirSense — CSV replay → Kafka (demo-day backup)
File: ingestion/fetch_aqi_replay.py
Week: 12 (stub — full implementation in Week 12)

When WAQI API is down, replay pre-recorded readings from CSV into Kafka.

Run:
    python ingestion/fetch_aqi_replay.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import load_settings
from common.logging_setup import setup_logging

BACKUP_CSV = PROJECT_ROOT / "data" / "backup" / "aqi_7day_backup.csv"


def main() -> int:
    settings = load_settings()
    logger = setup_logging(settings, name="airsense.replay")

    if not BACKUP_CSV.exists():
        logger.error(
            "Backup CSV not found: %s — add file in Week 12 or export from TimescaleDB",
            BACKUP_CSV,
        )
        return 1

    logger.warning(
        "Replay mode is a stub until Week 12. CSV exists at %s — request "
        "'Build Week 12 demo hardening' to enable full replay.",
        BACKUP_CSV,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
