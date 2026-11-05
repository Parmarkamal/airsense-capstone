@echo off
REM ═════════════════════════════════════════════════════════════════════════════
REM AirSense — 1-Click Offline Demo Launcher
REM Phase 8: Offline Resilience & Disaster Recovery
REM
REM Starts the entire AirSense platform with ZERO internet connectivity:
REM   1. Starts TimescaleDB Docker container (port 5433)
REM   2. Waits for database to be ready
REM   3. Streams 7-day historical CSV backup into the database (Replay-Backup)
REM   4. Optionally starts Ollama LLM server (for AI Health Advisor)
REM   5. Launches Streamlit dashboard (port 8501) in a new window
REM
REM Usage:  scripts\run_offline_demo.bat
REM
REM Prerequisites:
REM   - Docker Desktop running
REM   - Python 3.11+ with AirSense dependencies installed
REM   - (Optional) Ollama installed for AI Health Advisor
REM ═════════════════════════════════════════════════════════════════════════════

title AirSense — Offline Demo Launcher
cd /d "%~dp0\.."

echo.
echo [AirSense] ══════════════════════════════════════════════════════════
echo [AirSense]  AirSense Offline Demo — No Internet Required
echo [AirSense]  Phase 8: Offline Resilience ^& Disaster Recovery
echo [AirSense]  %DATE% %TIME%
echo [AirSense] ══════════════════════════════════════════════════════════
echo.

REM ── Step 0: Check Python ────────────────────────────────────────────────────
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found in PATH. Install Python 3.11+ and try again.
    pause & exit /b 1
)
echo [OK] Python found.

REM ── Step 1: Start TimescaleDB Docker Container ──────────────────────────────
echo.
echo [Step 1/4] Starting TimescaleDB Docker container...
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Desktop is not running. Please start Docker Desktop first.
    echo         (Look for the Docker whale icon in your taskbar)
    pause & exit /b 1
)

docker compose up -d 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [WARN] docker compose up had issues — container may already be running.
)

echo [OK] TimescaleDB container started (port 5433).

REM ── Step 2: Wait for database to be ready ────────────────────────────────────
echo.
echo [Step 2/4] Waiting for TimescaleDB to accept connections...

set DB_READY=0
for /L %%i in (1,1,15) do (
    python -c "import psycopg2; c=psycopg2.connect(host='localhost',port=5433,dbname='airsense_db',user='airsense',password='airsense123',connect_timeout=5); c.close()" 2>nul
    IF %ERRORLEVEL% EQU 0 (
        set DB_READY=1
        echo [OK] TimescaleDB is ready!
        goto :db_ready
    )
    echo [WAIT] Attempt %%i/15 — database still starting...
    timeout /t 3 /nobreak >nul
)

:db_ready
IF "%DB_READY%"=="0" (
    echo [ERROR] Cannot connect to TimescaleDB after 15 attempts.
    echo         Check Docker logs:  docker compose logs timescaledb
    pause & exit /b 1
)

REM ── Step 3: Stream historical CSV backup into database ──────────────────────
echo.
echo [Step 3/4] Streaming 7-day historical backup into database (Replay-Backup)...
python ingestion/fetch_aqi_replay.py --direct-db
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Replay data insertion failed. Check the error messages above.
    pause & exit /b 1
)
echo [OK] Historical replay data loaded into TimescaleDB.

REM ── Step 4: Check Ollama (optional) ───────────────────────────────────────────
echo.
echo [Step 4/4] Checking optional services...

python -c "import urllib.request; urllib.request.urlopen('http://localhost:11434/api/tags', timeout=2)" 2>nul
IF %ERRORLEVEL% EQU 0 (
    echo [OK] Ollama LLM server is running (AI Health Advisor available).
) ELSE (
    echo [INFO] Ollama not running — AI Health Advisor will use static fallback.
    echo        To enable: run 'ollama serve' in a separate terminal.
)

REM ── Launch Streamlit Dashboard ───────────────────────────────────────────────
echo.
echo [AirSense] ══════════════════════════════════════════════════════════
echo [AirSense]  All services ready! Launching Streamlit dashboard...
echo [AirSense]
echo [AirSense]  Dashboard: http://localhost:8501
echo [AirSense]  Mode:      REPLAY (offline historical stream)
echo [AirSense]  Database:  localhost:5433 (TimescaleDB)
echo [AirSense] ══════════════════════════════════════════════════════════
echo.

start "AirSense — Streamlit Dashboard" cmd /k "cd /d %~dp0\.. && python -m streamlit run dashboard/app.py"

echo [AirSense] Dashboard launched in new window.
echo [AirSense] Close this window when done. The database container stays running.
echo.
pause
