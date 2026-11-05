"""
AirSense — Background hybrid ingestion daemon
File: ingestion/fetch_daemon.py
Phase: 5

Loops forever: run hybrid fetch → write heartbeat → sleep interval.
Uses exponential backoff when a fetch cycle fails.

Run:
    python ingestion/fetch_daemon.py

Stop with Ctrl+C.
"""

from __future__ import annotations

import json
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import load_settings
from common.logging_setup import setup_logging
from ingestion.fetch_aqi import run_fetch

DEFAULT_INTERVAL_SECONDS = 3600
MAX_BACKOFF_SECONDS = 900
HEARTBEAT_REL_PATH = Path("logs") / "heartbeat.json"

_shutdown = False


def _handle_signal(signum: int, _frame: Any) -> None:
    global _shutdown
    _shutdown = True


def write_heartbeat(
    path: Path,
    *,
    status: str,
    cycle: int,
    exit_code: int | None,
    interval_seconds: int,
    detail: str = "",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "service": "airsense.fetch_daemon",
        "status": status,
        "cycle": cycle,
        "exit_code": exit_code,
        "interval_seconds": interval_seconds,
        "detail": detail,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_daemon(interval_seconds: int = DEFAULT_INTERVAL_SECONDS) -> int:
    settings = load_settings()
    logger = setup_logging(settings, name="airsense.fetch_daemon")
    heartbeat_path = Path(settings["project_root"]) / HEARTBEAT_REL_PATH

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    logger.info(
        "Fetch daemon started | interval=%ss | heartbeat=%s",
        interval_seconds,
        heartbeat_path,
    )
    write_heartbeat(
        heartbeat_path,
        status="started",
        cycle=0,
        exit_code=None,
        interval_seconds=interval_seconds,
        detail="daemon boot",
    )

    cycle = 0
    backoff = 0

    while not _shutdown:
        cycle += 1
        logger.info("HEARTBEAT cycle=%d — starting hybrid fetch", cycle)
        write_heartbeat(
            heartbeat_path,
            status="running",
            cycle=cycle,
            exit_code=None,
            interval_seconds=interval_seconds,
            detail="fetch in progress",
        )

        try:
            exit_code = run_fetch()
        except Exception as exc:  # noqa: BLE001 — daemon must never die silently
            exit_code = 1
            logger.exception("Unhandled error in fetch cycle %d: %s", cycle, exc)

        if exit_code == 0:
            backoff = 0
            status = "ok"
            detail = "fetch cycle succeeded"
            sleep_for = interval_seconds
        else:
            backoff = min(MAX_BACKOFF_SECONDS, max(30, (backoff or 30) * 2))
            status = "error"
            detail = f"fetch cycle exit_code={exit_code}; backoff={backoff}s"
            sleep_for = backoff
            logger.warning(
                "Fetch cycle %d failed (exit=%s) — exponential backoff %ss",
                cycle,
                exit_code,
                backoff,
            )

        write_heartbeat(
            heartbeat_path,
            status=status,
            cycle=cycle,
            exit_code=exit_code,
            interval_seconds=interval_seconds,
            detail=detail,
        )
        logger.info(
            "HEARTBEAT cycle=%d status=%s — sleeping %ss",
            cycle,
            status,
            sleep_for,
        )

        # Interruptible sleep
        end = time.time() + sleep_for
        while not _shutdown and time.time() < end:
            time.sleep(min(1.0, end - time.time()))

    write_heartbeat(
        heartbeat_path,
        status="stopped",
        cycle=cycle,
        exit_code=0,
        interval_seconds=interval_seconds,
        detail="graceful shutdown",
    )
    logger.info("Fetch daemon stopped after %d cycles", cycle)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_daemon())
