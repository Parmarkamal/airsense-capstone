@echo off
:: ============================================================
:: AirSense — Start Local Apache Kafka + ZooKeeper
:: Starts ZooKeeper (port 2181) then Kafka Broker (port 9092)
:: ============================================================

title AirSense — Apache Kafka Stack
echo.
echo ============================================================
echo   AirSense — Launching ZooKeeper and Kafka Broker
echo ============================================================
echo.

SET KAFKA_DIR=C:\kafka

IF NOT EXIST "%KAFKA_DIR%\bin\windows\kafka-server-start.bat" (
    echo [ERROR] Kafka not found at %KAFKA_DIR%.
    pause
    exit /b 1
)

powershell -NoProfile -Command "try { $t = New-Object System.Net.Sockets.TcpClient; $t.Connect('localhost',2181); $t.Close(); exit 0 } catch { exit 1 }"
IF %ERRORLEVEL% EQU 0 (
    echo [INFO] ZooKeeper is already running on port 2181.
) ELSE (
    echo [1/2] Starting ZooKeeper in background...
    start "AirSense — ZooKeeper" cmd /k "cd /d %KAFKA_DIR% && .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties"
    echo Waiting 5 seconds for ZooKeeper to initialize...
    ping 127.0.0.1 -n 6 >nul
)

powershell -NoProfile -Command "try { $t = New-Object System.Net.Sockets.TcpClient; $t.Connect('localhost',9092); $t.Close(); exit 0 } catch { exit 1 }"
IF %ERRORLEVEL% EQU 0 (
    echo [INFO] Kafka Broker is already running on port 9092.
) ELSE (
    REM Clean stale lock file left behind by crashed instances
    IF EXIST "%KAFKA_DIR%\kafka-logs\.lock" (
        echo [INFO] Clearing stale lock file...
        del /f /q "%KAFKA_DIR%\kafka-logs\.lock" >nul 2>&1
    )

    REM Auto-clean stale cluster ID to prevent InconsistentClusterIdException on Windows reboot
    IF EXIST "%KAFKA_DIR%\kafka-logs\meta.properties" (
        echo [INFO] Syncing Kafka cluster ID with ZooKeeper...
        del /f /q "%KAFKA_DIR%\kafka-logs\meta.properties" >nul 2>&1
    )

    echo [2/2] Starting Kafka Broker in background...
    start "AirSense — Kafka Broker" cmd /k "cd /d %KAFKA_DIR% && .\bin\windows\kafka-server-start.bat .\config\server.properties"

    echo Waiting 8 seconds for Kafka Broker to register...
    ping 127.0.0.1 -n 9 >nul
)

echo.
echo [CHECK] Testing port 9092...
powershell -NoProfile -Command "try { $t = New-Object System.Net.Sockets.TcpClient; $t.Connect('localhost',9092); $t.Close(); Write-Host 'Kafka Broker is ONLINE on port 9092!' } catch { Write-Host 'Kafka Broker starting up...' }"

echo.
echo ZooKeeper and Kafka are running! Keep their windows open during demo.
echo.
