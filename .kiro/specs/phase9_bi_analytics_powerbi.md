# Specification: Phase 9 — Business Intelligence & Power BI Integration

## 1. Objective
Fulfill M.Sc. IT (Business Intelligence & Analytics) requirements by implementing an Operational Analytics tab inside Streamlit and providing a complete Star-Schema data model with 5 production DAX measures for Power BI Desktop.

## 2. Target Files
- `airsense/dashboard/components/insights.py`: Operational BI tab with analytical KPIs and city rank heatmaps.
- `airsense/scripts/export_powerbi_data.py`: Script exporting clean star-schema CSVs (`dim_city`, `dim_date`, `dim_time`, `fact_aqi_readings`).
- `airsense/docs/powerbi_setup.md`: Step-by-step connection guide, star-schema diagram, and 5 DAX formulas.

## 3. Tasks

### Task 9.1: Streamlit Operational Analytics Tab (`dashboard/components/insights.py`)
- **Combustion Ratio Analysis**: $PM2.5 / PM10$ ratio:
  - Ratio > 0.6 indicates vehicular combustion / industrial exhaust.
  - Ratio < 0.4 indicates road dust / construction / crustal particulate.
- **Week-over-Week (WoW) Trend %**: Change in 7-day rolling average AQI per city.
- **City Pollution Ranking Matrix**: Sortable table ranking cities by peak daily AQI, average PM2.5, and WHO limit exceedance hours.

### Task 9.2: Power BI Star Schema & DAX Measures
- Export script `export_powerbi_data.py` generating:
  - `fact_aqi_readings`: `reading_id`, `city_id`, `date_key`, `time_key`, `aqi`, `pm25`, `pm10`, `combustion_ratio`.
  - `dim_city`: `city_id`, `city_name`, `lat`, `lon`, `state`, `tier`.
  - `dim_date`: `date_key`, `date`, `day_name`, `is_weekend`, `month_name`.
- 5 Production DAX Measures documented in `docs/powerbi_setup.md`:
  1. `AQI Category = SWITCH(TRUE(), [Avg AQI] <= 50, "Good", [Avg AQI] <= 100, "Satisfactory", [Avg AQI] <= 200, "Moderate", [Avg AQI] <= 300, "Poor", [Avg AQI] <= 400, "Very Poor", "Severe")`
  2. `WoW AQI % Change = DIVIDE([Current Week AQI] - [Prior Week AQI], [Prior Week AQI], 0)`
  3. `Combustion Index = DIVIDE(SUM(fact[pm25]), SUM(fact[pm10]), 0)`
  4. `Exceedance Hours = COUNTROWS(FILTER(fact_aqi_readings, [pm25] > 15))` (WHO 24h limit)
  5. `Peak Hour AQI = MAXX(VALUES(dim_time[Hour]), [Avg AQI])`

## 4. Acceptance Criteria
- [ ] New "Analytics & BI" tab active in Streamlit dashboard.
- [ ] `export_powerbi_data.py` generates clean dimension and fact CSVs.
- [ ] `docs/powerbi_setup.md` contains complete star schema and DAX documentation.
