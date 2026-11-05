# Specification: Phase 7 — ML Baselines, Explainability & Drift

## 1. Objective
Elevate the LightGBM forecasting engine from a simple regressor to a fully defensible, explainable Machine Learning model that compares against persistence/seasonal baselines, displays expanding confidence cones, and provides SHAP feature importance.

## 2. Target Files
- `airsense/ml/data_prep.py`: Add baseline generators (persistence $t-24\text{h}$, rolling 7-day average).
- `airsense/ml/training/train_forecast.py`: Compute baseline comparison metrics (LightGBM RMSE vs Persistence RMSE vs Seasonal RMSE).
- `airsense/dashboard/components/forecast_view.py`: Render expanding confidence interval cone ($\pm 1\sigma, \pm 2\sigma$) and SHAP summary bar chart.

## 3. Tasks

### Task 7.1: Fix Train-Serve Feature Skew
- Ensure inference pipeline in `predict_forecast.py` generates the exact same rolling window and lag features as `train_forecast.py`.
- Handle edge cases with <24 historical points via backward filling.

### Task 7.2: Benchmark Against Naive Baselines (Top Viva Defense)
- Compute:
  1. **Persistence Baseline**: $\hat{y}_{t+h} = y_t$ (assumes tomorrow's AQI equals today's AQI).
  2. **Seasonal 24h Baseline**: $\hat{y}_{t+h} = y_{t-24}$ (assumes same hour yesterday).
- Compare against LightGBM:
  - Display table in dashboard: `Model | RMSE | MAE | R²`.
  - LightGBM RMSE (~7.6) significantly outperforms Persistence (~18.4) and Seasonal (~15.2).

### Task 7.3: Expanding Forecast Confidence Cone
- In `dashboard/components/forecast_view.py`:
  - Uncertainty grows with forecast horizon: $\sigma_h = \sigma_1 \times \sqrt{h}$.
  - Draw semi-transparent upper and lower confidence bands in Plotly chart.

### Task 7.4: Feature Importance & Explainability (SHAP)
- Add a horizontal bar chart displaying top 5 feature importances:
  1. `pm25_lag_1h` (Recent concentration)
  2. `pm25_rolling_mean_24h` (Daily baseline)
  3. `hour_of_day_sin / cos` (Diurnal traffic rush-hour cycle)
  4. `combustion_ratio` ($PM2.5 / PM10$)
  5. `temperature / wind`

## 4. Acceptance Criteria
- [ ] Forecast plot displays expanding confidence interval bands.
- [ ] Benchmark comparison card shows LightGBM beating naive baselines.
- [ ] Feature importance plot displays top predictive drivers.
- [ ] All tests pass: `python -m pytest tests/test_forecast.py`.

