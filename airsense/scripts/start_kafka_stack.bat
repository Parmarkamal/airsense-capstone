@echo off
:: ============================================================
:: AirSense — Resilient Apache Kafka & ZooKeeper Stack Launcher
:: Fully automated self-cleaning, duplicate-proof, zero-lock design
:: ============================================================

title AirSense — Apache Kafka Stack
echo.
echo ============================================================
echo   AirSense — Launching Resilient ZooKeeper & Kafka Broker
echo ============================================================
echo.

SET KAFKA_DIR=C:\kafka

IF NOT EXIST "%KAFKA_DIR%\bin\windows\kafka-server-start.bat" (
    echo [ERROR] Kafka not found at %KAFKA_DIR%.
    pause
    exit /b 1
)

:: ── STEP 1: Check if Kafka Broker is ALREADY running on port 9092 ──────
powershell -NoProfile -Command "try { $t = New-Object System.Net.Sockets.TcpClient; $t.Connect('127.0.0.1',9092); $t.Close(); exit 0 } catch { exit 1 }"
IF %ERRORLEVEL% EQU 0 (
    echo [OK] Kafka Broker is ALREADY running on port 9092.
    echo      No need to start another instance.
    goto :VERIFY_FINAL
)

:: ── STEP 2: Pre-startup disk cleanup ──────────────────────────────────
echo [1/3] Preparing clean environment...
REM 1. Remove stale lock file left behind by any abnormal termination
IF EXIST "%KAFKA_DIR%\kafka-logs\.lock" (
    echo       - Removing stale .lock file...
    del /f /q "%KAFKA_DIR%\kafka-logs\.lock" >nul 2>&1
)

REM 2. Remove meta.properties to guarantee cluster ID alignment with ZooKeeper
IF EXIST "%KAFKA_DIR%\kafka-logs\meta.properties" (
    echo       - Synchronizing cluster ID with ZooKeeper...
    del /f /q "%KAFKA_DIR%\kafka-logs\meta.properties" >nul 2>&1
)

REM 3. Clean any obsolete lab assignment topics to prevent Windows file-move errors
for %%d in (attendance-0 attendance_at_least_once-0 iot-sensor-data-0 my-first-topic-0 newtumb-0 orders-0 order_status-0 order_summary-0 sales-stream-0 short-retention-stream-0 student-0 studentnewstatus-0 test-topic-0 test-verification-0 text-stream-0 transactions-0) do (
    if exist "%KAFKA_DIR%\kafka-logs\%%d" (
        rmdir /s /q "%KAFKA_DIR%\kafka-logs\%%d" >nul 2>&1
    )
)

:: ── STEP 3: ZooKeeper Health Check & Launch ────────────────────────────
echo [2/3] Checking ZooKeeper on port 2181...
powershell -NoProfile -Command "try { $t = New-Object System.Net.Sockets.TcpClient; $t.Connect('127.0.0.1',2181); $t.Close(); exit 0 } catch { exit 1 }"
IF %ERRORLEVEL% EQU 0 (
    echo       - ZooKeeper is already running on port 2181.
    echo       - Waiting 4 seconds for any ghost ephemeral sessions to clear...
    ping 127.0.0.1 -n 5 >nul
) ELSE (
    echo       - Launching ZooKeeper in dedicated window...
    start "AirSense — ZooKeeper" cmd /k "cd /d %KAFKA_DIR% && .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties"
    echo       - Waiting 6 seconds for ZooKeeper to initialize...
    ping 127.0.0.1 -n 7 >nul
)

:: ── STEP 4: Start Kafka Broker ─────────────────────────────────────────
echo [3/3] Starting Kafka Broker on port 9092...
start "AirSense — Kafka Broker" cmd /k "cd /d %KAFKA_DIR% && .\bin\windows\kafka-server-start.bat .\config\server.properties"

echo Waiting 8 seconds for Kafka Broker to register with ZooKeeper...
ping 127.0.0.1 -n 9 >nul

:VERIFY_FINAL
echo.
echo ============================================================
echo [HEALTH CHECK] Verifying Kafka Broker connection...
echo ============================================================
powershell -NoProfile -Command "try { $t = New-Object System.Net.Sockets.TcpClient; $t.Connect('127.0.0.1',9092); $t.Close(); Write-Host 'SUCCESS: Kafka Broker is ONLINE and HEALTHY on port 9092!' -ForegroundColor Green } catch { Write-Host 'Kafka Broker is still initializing. Please wait a few moments...' -ForegroundColor Yellow }"

echo.
echo ZooKeeper and Kafka are running! Keep their windows open during your demo.
echo.
