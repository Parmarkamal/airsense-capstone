@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM AirSense — Master demo launcher
REM
REM Checks services, then opens two terminal windows:
REM   Window 1: Kafka consumer (running continuously)
REM   Window 2: First AQI fetch + Task Scheduler instructions
REM
REM Usage:  scripts\start_demo.bat
REM ─────────────────────────────────────────────────────────────────────────────

cd /d "%~dp0.."

echo.
echo [AirSense] ========================================================
echo [AirSense]  AirSense Phase 1 — System Startup  %DATE% %TIME%
echo [AirSense] ========================================================
echo.

REM ── Step 1: Check Python ────────────────────────────────────────────────────
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found in PATH. Install Python 3.11+ and try again.
    pause & exit /b 1
)
echo [OK] Python found.

REM ── Step 2: Check Kafka broker ──────────────────────────────────────────────
echo [CHECK] Testing Kafka broker on localhost:9092...
python -c "from kafka import KafkaAdminClient; c=KafkaAdminClient(bootstrap_servers='localhost:9092',request_timeout_ms=5000); c.close(); print('[OK] Kafka is running.')" 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] Kafka is offline. Launching ZooKeeper and Kafka stack...
    call scripts\start_kafka_stack.bat
) ELSE (
    echo [OK] Kafka is running.
)

REM ── Step 3: Check Docker / TimescaleDB ──────────────────────────────────────
echo [CHECK] Testing TimescaleDB on localhost:5433...
python -c "import psycopg2; c=psycopg2.connect(host='localhost',port=5433,dbname='airsense_db',user='airsense',password='airsense123',connect_timeout=5); c.close(); print('[OK] TimescaleDB is running.')" 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [WARN] Cannot connect to TimescaleDB. Make sure Docker is running:
    echo          docker compose up -d
    echo.
    set /p CONTINUE=[AirSense] Continue anyway? (y/n): 
    IF /I "%CONTINUE%" NEQ "y" ( pause & exit /b 1 )
)

echo.
echo [AirSense] All checks passed. Opening consumer in new window...
echo.

REM ── Step 4: Start consumer in separate window ───────────────────────────────
start "AirSense — Kafka Consumer" cmd /k "scripts\start_consumer.bat"

REM Give consumer 3 seconds to connect before fetching
timeout /t 3 /nobreak >nul

REM ── Step 5: Run first fetch ──────────────────────────────────────────────────
echo [AirSense] Running live AQI fetch & model forecast projection now...
call scripts\run_fetcher.bat

REM ── Step 6: Launch Streamlit Dashboard ──────────────────────────────────────
echo.
echo [AirSense] Launching Streamlit Dashboard...
start "AirSense — Dashboard" cmd /k "scripts\run_dashboard.bat"

echo.
echo [AirSense] ========================================================
echo [AirSense]  AirSense Full System is ONLINE!
echo [AirSense]
echo [AirSense]  - Kafka Stack: Running on port 9092
echo [AirSense]  - Consumer: Ingesting streaming frames to TimescaleDB
echo [AirSense]  - Ingestion: Live CPCB data fetched & ML forecasted
echo [AirSense]  - Power BI: CSV datasets refreshed
echo [AirSense]  - Dashboard: http://localhost:8501
echo [AirSense] ========================================================
echo.
pause
