@echo off
title AirSense — Streamlit Dashboard
echo =====================================================================
echo  AirSense — Launching Streamlit Real-Time Dashboard
echo  MSc Business Intelligence ^& Analytics Capstone
echo =====================================================================
echo.

cd /d "%~dp0\.."

echo [INFO] Starting Streamlit server on http://localhost:8501 ...
echo [INFO] Press Ctrl+C in this window to stop the dashboard.
echo.

python -m streamlit run dashboard/app.py

pause
