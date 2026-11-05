@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM AirSense — Run the WAQI fetcher (one-shot)
REM
REM This script fetches AQI for all configured cities and publishes to Kafka.
REM Windows Task Scheduler calls this every hour automatically.
REM
REM Usage:  scripts\run_fetcher.bat
REM ─────────────────────────────────────────────────────────────────────────────

cd /d "%~dp0.."

echo.
echo [AirSense] ==========================================
echo [AirSense]  WAQI Fetcher - %DATE% %TIME%
echo [AirSense] ==========================================
echo.

REM Activate virtual environment if it exists
IF EXIST ".venv\Scripts\activate.bat" (
    echo [AirSense] Activating virtual environment...
    call .venv\Scripts\activate.bat
) ELSE IF EXIST "venv\Scripts\activate.bat" (
    echo [AirSense] Activating virtual environment...
    call venv\Scripts\activate.bat
) ELSE (
    echo [AirSense] No venv found — using system Python
)

echo [AirSense] Running fetch_aqi.py...
python ingestion\fetch_aqi.py

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo [AirSense] Fetch completed successfully.
) ELSE IF %ERRORLEVEL% EQU 2 (
    echo.
    echo [WARN] Fetch completed but some cities failed to publish to Kafka.
    echo        Check logs\airsense.log for details.
) ELSE (
    echo.
    echo [ERROR] Fetch failed! Check logs\airsense.log for details.
)

echo.
