# AirSense — Real-Time Urban Air Quality Forecasting & Grounded GenAI Health Advisory Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Kafka](https://img.shields.io/badge/Apache%20Kafka-3.7-black.svg)](https://kafka.apache.org/)
[![TimescaleDB](https://img.shields.io/badge/TimescaleDB-2.14-00A3E0.svg)](https://www.timescale.com/)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.3-orange.svg)](https://lightgbm.readthedocs.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Llama--3.2--3B-purple.svg)](https://ollama.ai/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-50%2F50%20Passing-brightgreen.svg)]()

> **Academic Context**: M.Sc. IT (Business Intelligence & Analytics), Semester 3 Capstone Project  
> **Institution**: Gujarat University (CPC)  
> **Architecture**: 100% Local Deployment | Zero Cloud Cost | Hardware-Capped Laptop Operation

---

## 🌍 Executive Summary

**AirSense** is an end-to-end distributed data engineering, predictive machine learning, and grounded conversational intelligence platform designed for urban air quality management across major Indian metropolitan areas (Delhi, Ahmedabad, Mumbai, Pune, Bengaluru, Gandhinagar).

Unlike static dashboard projects, AirSense features:
1. **Real-Time Streaming Pipeline**: Apache Kafka streaming engine ingesting live WAQI and Open-Meteo observations into a high-throughput TimescaleDB hypertable with Pydantic v2 data validation.
2. **Hybrid Ingestion Resilience**: Automated station health monitoring with live Open-Meteo GPS fallback to prevent stale data when municipal CPCB sensors disconnect.
3. **Machine Learning Forecasting**: LightGBM multi-step regressor generating 24-hour future forecasts of AQI and PM2.5 concentrations, benchmarked against persistence ($t-24\text{h}$) and seasonal baselines.
4. **Grounded GenAI Health Advisory**: Retrieval-Augmented Generation (RAG) system embedding WHO 2021 Air Quality Guidelines and CPCB NAAQS standards into ChromaDB, dynamically queried by local Ollama (`llama3.2:3b`) with medical disclaimers and out-of-domain guardrails.
5. **Interactive GIS Analytics**: Streamlit multi-view operational dashboard with Folium Leaflet spatial heatmaps, sensor freshness badges, and Power BI-ready star schema export.

---

## 🏛️ System Architecture

```
                                 [External Ingestion Layer]
                        WAQI API (Live) ────► Open-Meteo API (Live Fallback)
                                      │
                                      ▼
                        [Apache Kafka Streaming Engine]
                            Topic: `aqi_raw` (Port 9092)
                                      │
                                      ▼
                        [Pydantic v2 Validation Consumer]
                                      │
                                      ▼
                         [TimescaleDB Time-Series Engine]
                          Hypertable: `aqi_readings` (Port 5433)
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
[LightGBM Forecasting]      [ChromaDB + Ollama RAG]      [Streamlit GIS Dashboard]
 • 24-hour Multi-Step        • WHO / CPCB Guidelines      • Folium Spatial Heatmap
 • RMSE ~7.61 vs Baseline    • `all-MiniLM-L6-v2`         • Real-Time Freshness Badges
 • Expanding Confidence Cone • Llama-3.2-3B Local LLM    • Power BI Star-Schema Export
```

---

## 🚀 Quick Start / Cold-Start Runbook

### Prerequisites
- Windows 11 / Linux / macOS
- Python 3.11+
- Docker Desktop (for TimescaleDB on port 5433)
- Local Kafka broker (port 9092)
- Local Ollama running `llama3.2:3b` (port 11434)

### 1. Clone Repository
```bash
git clone https://github.com/Parmarkamal/airsense-capstone.git
cd airsense-capstone/airsense
```

### 2. Environment Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start Database & Services
```bash
# Start TimescaleDB container (Port 5433)
docker compose up -d

# Start local Ollama model
ollama run llama3.2:3b
```

### 4. Run Automated Test Suite
```bash
python -m pytest tests/
# Output: 50 passed in ~30 seconds (100% pass rate)
```

### 5. Launch Application
```bash
# Start Streamlit Dashboard
python -m streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501`.

---

## 📁 Repository Structure

```
capstone_project/
├── airsense/                             ← Core Application Source Code
│   ├── common/                           ← Config loaders & logging
│   ├── ingestion/                        ← Real-time hybrid collectors & daemon
│   ├── consumer/                         ← Kafka consumer & Pydantic validator
│   ├── ml/                               ← LightGBM 24h forecasting engine
│   ├── rag/                              ← ChromaDB vector DB & Ollama Health Advisor
│   ├── dashboard/                        ← Streamlit web dashboard & GIS interactive map
│   ├── tests/                            ← 50 Unit & Integration tests (100% passing)
│   ├── scripts/                          ← Master automation scripts
│   └── config.yaml                       ← System configuration
│
├── .kiro/                                ← Kiro Engineering Steering & Phase Specs
│   ├── steering/                         ← Architecture & code rules
│   └── specs/                            ← Detailed specifications for Phases 5 to 10
│
├── .cursorrules                          ← AI implementation rules
├── AirSense_Project_Status.md            ← Master Progress Tracker & 40 Viva Defense Q&A
└── README.md                             ← Project Documentation
```

---

## 📊 Evaluation & Verification

- **Real-Time Data Integrity**: Verified across all 6 target cities with automated fallback.
- **Test Coverage**: 50 unit and integration tests passing covering ingestion, validation, ML forecasting, and RAG retrieval.
- **Model Accuracy**: LightGBM achieves lower RMSE than persistence ($t-24\text{h}$) and seasonal baselines on test sets.
- **Safety Guardrails**: Grounded RAG with strict out-of-domain query rejection and mandatory medical disclaimers.

---

## 👥 Authors & Team
- **Kamal Parmar** — Lead Architecture & Development
- M.Sc. IT (Business Intelligence & Analytics), Semester 3
- Gujarat University, CPC
