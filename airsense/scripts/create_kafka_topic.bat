@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM AirSense — Create Kafka topic: aqi_raw
REM
REM Run this ONCE before starting the fetcher for the first time.
REM Requires: Kafka + ZooKeeper already running on localhost:9092
REM
REM Usage:  scripts\create_kafka_topic.bat
REM ─────────────────────────────────────────────────────────────────────────────

SET BOOTSTRAP=localhost:9092
SET TOPIC=aqi_raw
SET PARTITIONS=1
SET REPLICATION=1

echo.
echo [AirSense] Creating Kafka topic: %TOPIC%
echo [AirSense] Broker : %BOOTSTRAP%
echo.

REM Try to find kafka-topics.bat in common install locations
SET KAFKA_BIN=
IF EXIST "C:\kafka\bin\windows\kafka-topics.bat"       SET KAFKA_BIN=C:\kafka\bin\windows\kafka-topics.bat
IF EXIST "C:\kafka_2.13\bin\windows\kafka-topics.bat"  SET KAFKA_BIN=C:\kafka_2.13\bin\windows\kafka-topics.bat
IF EXIST "%USERPROFILE%\kafka\bin\windows\kafka-topics.bat" SET KAFKA_BIN=%USERPROFILE%\kafka\bin\windows\kafka-topics.bat

IF "%KAFKA_BIN%"=="" (
    echo [ERROR] kafka-topics.bat not found in standard locations.
    echo         Set KAFKA_HOME and try:
    echo           %%KAFKA_HOME%%\bin\windows\kafka-topics.bat --create ...
    echo.
    echo         Manual command to run yourself:
    echo           kafka-topics.bat --create --topic %TOPIC% --bootstrap-server %BOOTSTRAP% --partitions %PARTITIONS% --replication-factor %REPLICATION%
    pause
    exit /b 1
)

echo [AirSense] Using: %KAFKA_BIN%
echo.

"%KAFKA_BIN%" --create ^
    --topic %TOPIC% ^
    --bootstrap-server %BOOTSTRAP% ^
    --partitions %PARTITIONS% ^
    --replication-factor %REPLICATION% ^
    --if-not-exists

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARN] Topic may already exist — that is fine. Listing topics to confirm:
    "%KAFKA_BIN%" --list --bootstrap-server %BOOTSTRAP%
) ELSE (
    echo.
    echo [OK] Topic "%TOPIC%" created successfully.
)

echo.
echo [AirSense] Done. You can now run:  scripts\run_fetcher.bat
pause
