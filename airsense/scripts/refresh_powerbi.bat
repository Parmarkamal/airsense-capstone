@echo off
REM AirSense — 1-Click Power BI Data Refresher
REM Exports the latest TimescaleDB records into the Kimball Star Schema CSVs

echo ========================================================
echo   AirSense: Exporting Latest Data for Power BI...
echo ========================================================

cd /d "%~dp0\.."
python scripts\export_powerbi_data.py

echo.
echo ========================================================
echo   Export Finished!
echo   Now in Power BI Desktop, simply click 'Refresh' (Home ribbon).
echo ========================================================
pause

