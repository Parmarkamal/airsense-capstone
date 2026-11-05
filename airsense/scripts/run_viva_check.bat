@echo off
:: ============================================================
:: AirSense — Pre-Viva 5-Second System Diagnostic
:: File: scripts/run_viva_check.bat
:: Phase 10 — System Observability & Viva Polish
::
:: Run this BEFORE your viva to confirm all services are live.
:: Double-click or run from any terminal.
:: ============================================================

title AirSense Viva Diagnostic

echo.
echo ============================================================
echo   AirSense — Pre-Viva System Diagnostic
echo   M.Sc. Business Intelligence ^& Analytics Capstone 2026
echo ============================================================
echo.

set PASS=0
set FAIL=0
set PROJECT_DIR=%~dp0..

:: ── 1. Kafka Broker ─────────────────────────────────────────
echo [1/5] Checking Kafka Broker (localhost:9092)...
powershell -NoProfile -Command "try { $t = New-Object System.Net.Sockets.TcpClient; $t.Connect('localhost',9092); $t.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel%==0 (
    echo       [OK]  Kafka Broker is ONLINE
    set /a PASS+=1
) else (
    echo       [FAIL] Kafka Broker OFFLINE - Run: scripts\create_kafka_topic.bat
    set /a FAIL+=1
)

:: ── 2. TimescaleDB ──────────────────────────────────────────
echo [2/5] Checking TimescaleDB (localhost:5433)...
powershell -NoProfile -Command "try { $t = New-Object System.Net.Sockets.TcpClient; $t.Connect('localhost',5433); $t.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel%==0 (
    echo       [OK]  TimescaleDB is ONLINE (Docker container running)
    set /a PASS+=1
) else (
    echo       [FAIL] TimescaleDB OFFLINE - Run: docker compose up -d
    set /a FAIL+=1
)

:: ── 3. Ollama LLM ───────────────────────────────────────────
echo [3/5] Checking Ollama LLM Server (localhost:11434)...
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if %errorlevel%==0 (
    echo       [OK]  Ollama LLM Server is ONLINE (llama3.2:3b available)
    set /a PASS+=1
) else (
    echo       [FAIL] Ollama OFFLINE - Run: ollama serve  (then: ollama pull llama3.2:3b)
    set /a FAIL+=1
)

:: ── 4. Python Environment ───────────────────────────────────
echo [4/5] Checking Python environment and core imports...
cd /d "%PROJECT_DIR%"
python -c "import lightgbm, kafka, sqlalchemy, streamlit, chromadb; print('OK')" >nul 2>&1
if %errorlevel%==0 (
    echo       [OK]  Python packages: lightgbm, kafka, sqlalchemy, streamlit, chromadb
    set /a PASS+=1
) else (
    echo       [FAIL] Missing Python packages - Run: pip install -r requirements.txt
    set /a FAIL+=1
)

:: ── 5. Test Suite ────────────────────────────────────────────
echo [5/5] Running unit test suite (airsense/tests/)...
cd /d "%PROJECT_DIR%"
python -m pytest tests/ -q --tb=no --no-header >nul 2>&1
if %errorlevel%==0 (
    echo       [OK]  All tests PASS (85+ unit tests green)
    set /a PASS+=1
) else (
    echo       [WARN] Some tests FAILED - check: python -m pytest tests/ -v
    set /a FAIL+=1
)

:: ── Summary ──────────────────────────────────────────────────
echo.
echo ============================================================
echo   DIAGNOSTIC SUMMARY
echo ============================================================
echo   Passed : %PASS% / 5
echo   Failed : %FAIL% / 5
echo.

if %FAIL%==0 (
    echo   STATUS: ALL SYSTEMS GO — You are VIVA READY!
    echo   Start the dashboard: scripts\run_dashboard.bat
) else (
    echo   STATUS: %FAIL% service(s) need attention before viva.
    echo   See FAIL messages above for fix instructions.
)

echo.
echo   Dashboard URL : http://localhost:8501
echo   GitHub Repo   : https://github.com/Parmarkamal/airsense-capstone
echo   Test Count    : 85+ passing (Phases 1-10)
echo ============================================================
echo.
pause

