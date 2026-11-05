@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM AirSense — Start the Kafka consumer (continuous, run in its own terminal)
REM
REM This keeps running until you press Ctrl+C.
REM Open a SEPARATE terminal window for this — do not close it.
REM
REM Usage:  scripts\start_consumer.bat
REM ─────────────────────────────────────────────────────────────────────────────

cd /d "%~dp0.."

echo.
echo [AirSense] ==========================================
echo [AirSense]  Kafka Consumer - %DATE% %TIME%
echo [AirSense]  Press Ctrl+C to stop gracefully
echo [AirSense] ==========================================
echo.

REM Activate virtual environment if it exists
IF EXIST ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) ELSE IF EXIST "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) ELSE (
    echo [AirSense] No venv found — using system Python
)

echo [AirSense] Starting consumer... (Ctrl+C to stop)
echo.
python consumer\kafka_consumer.py

echo.
echo [AirSense] Consumer stopped.
pause
