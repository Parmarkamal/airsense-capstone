# 🤖 AirSense: Kiro AI Master Execution Guide

> **Status**: Cursor reached its usage limit. **Kiro is now your 100% Primary Full-Stack Engineer.**
> **Current Progress**: **Phases 1 to 6 are 100% COMPLETE & PASSING 50/50 TESTS.**

---

## 1. Project Health & Completed Phases

| Phase | Description | Status | Tests |
|---|---|---|---|
| **Phase 1** | Kafka Streaming Pipeline & TimescaleDB | ✅ Complete | 20/20 passed |
| **Phase 2** | Streamlit 5-View Dashboard & Leaflet GIS | ✅ Complete | Verified |
| **Phase 3** | LightGBM 24h/48h AQI Forecasting | ✅ Complete | 5/5 passed |
| **Phase 4** | Grounded GenAI RAG Health Advisor (Ollama + ChromaDB) | ✅ Complete | 7/7 passed |
| **Phase 5** | Real-Time Data Integrity & Hybrid Open-Meteo Ingestion | ✅ Complete | 9/9 passed |
| **Phase 6** | AI Safety Guardrails, Disclaimer & 4 Persona Pills | ✅ Complete | 9/9 passed |
| **TOTAL** | **Phases 1 to 6 Verified** | ✅ **LOCKED & SAFE** | **50/50 PASSED** |

---

## 2. Kiro's Roadmap (Phases 7 to 10)

Kiro reads its instructions automatically from `.kiro/steering/` and `.kiro/specs/`. 

All you need to do is paste the exact prompt for each phase into Kiro Chat:

---

### 📌 STEP 1: Run Phase 7 in Kiro (ML Baselines, Explainability & SHAP)
Paste this into Kiro Chat:

```text
Read .kiro/steering/ and .kiro/specs/phase7_ml_baselines_shap.md.
Phases 1-6 are complete (50/50 tests passing).
Please implement Phase 7:
1. In airsense/ml/data_prep.py & train_forecast.py: Fix train-serve feature skew and add Persistence (t-24h) and Seasonal benchmark baselines.
2. In airsense/dashboard/components/forecast_view.py: Render the expanding forecast confidence cone (±1σ, ±2σ) and SHAP feature importance plot.
3. Run python -m pytest tests/ to verify all tests pass.
```

---

### 📌 STEP 2: Run Phase 8 in Kiro (Offline Demo & Disaster Resilience)
Paste this into Kiro Chat:

```text
Read .kiro/specs/phase8_offline_demo_replay.md.
Please implement Phase 8:
1. In airsense/ingestion/fetch_aqi_replay.py: Build the historical CSV streamer using data/backup/aqi_7day_backup.csv to publish into Kafka with synthetic timestamps.
2. In airsense/dashboard/app.py: Add the amber REPLAY MODE banner when offline replay is running.
3. Create airsense/scripts/run_offline_demo.bat for 1-click zero-internet presentation.
4. Run python -m pytest tests/ to verify.
```

---

### 📌 STEP 3: Run Phase 9 in Kiro (BI Operational Analytics & Power BI)
Paste this into Kiro Chat:

```text
Read .kiro/specs/phase9_bi_analytics_powerbi.md.
Please implement Phase 9:
1. In airsense/dashboard/components/insights.py: Build the Operational Analytics tab (Combustion Ratio PM2.5/PM10, WoW trend %, city pollution rank matrix).
2. In airsense/scripts/export_powerbi_data.py: Write script exporting Star-Schema CSVs (dim_city, dim_date, fact_aqi_readings).
3. Create airsense/docs/powerbi_setup.md documenting the star schema and 5 DAX measures.
4. Run python -m pytest tests/ to verify.
```

---

### 📌 STEP 4: Run Phase 10 in Kiro (System Observability & Viva Polish)
Paste this into Kiro Chat:

```text
Read .kiro/specs/phase10_observability_viva_defense.md.
Please implement Phase 10:
1. In airsense/dashboard/components/health_view.py: Build the Pipeline Health tab showing Kafka lag, TimescaleDB latency, and Ollama status.
2. Run the final regression test suite: python -m pytest tests/
3. Confirm all tests pass and AirSense is 100% viva-ready.
```

---

## 3. Emergency Safety Net

If anything ever goes wrong or an error occurs in Kiro:
```powershell
git reset --hard HEAD
```
This restores your codebase back to the exact 50-test-passing state (Commit `6c85bb4`) in 1 second.
