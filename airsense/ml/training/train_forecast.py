"""
AirSense — LightGBM Training Pipeline with Walk-Forward Validation & MLflow
File: ml/training/train_forecast.py
Phase: 3 (Week 5)

Performs:
  1. Feature transformation on historical time-series data.
  2. Walk-Forward (expanding window) temporal cross-validation.
  3. Metric evaluation: RMSE, MAE, R², Directional Accuracy.
  4. Experiment tracking & artifact logging to MLflow.
  5. Champion-Challenger validation and promotion to ml/production/.
"""

from __future__ import annotations

import json
import logging
import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from datetime import datetime, timezone
from pathlib import Path
import joblib
import lightgbm as lgb
import mlflow
import mlflow.lightgbm
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.config import load_settings
from ml.training.features import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    create_features,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("airsense.ml.train")


def calculate_directional_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate percentage of times predicted change direction matches true change direction."""
    if len(y_true) < 2:
        return 1.0
    true_diff = np.diff(y_true)
    pred_diff = np.diff(y_pred)
    matches = (true_diff * pred_diff) > 0
    return float(np.mean(matches)) * 100.0


def train_and_evaluate(
    data_path: Path | None = None,
    mlflow_tracking_uri: str = "./ml/mlruns",
    promotion_threshold: float = 30.0,
) -> dict:
    """Execute complete walk-forward training, MLflow logging, and model promotion."""
    data_file = data_path or (PROJECT_ROOT / "data" / "historical" / "aqi_historical.csv")
    if not data_file.exists():
        raise FileNotFoundError(f"Training data not found at {data_file}. Run data/prepare_training_data.py first.")

    logger.info("Loading historical dataset from %s...", data_file)
    raw_df = pd.read_csv(data_file)
    logger.info("Raw records: %d across %d cities", len(raw_df), raw_df["city"].nunique())

    logger.info("Engineering temporal, lag, and rolling features...")
    df_features = create_features(raw_df, is_training=True)
    logger.info("Feature matrix ready: %d rows, %d features", len(df_features), len(FEATURE_COLUMNS))

    # Sort chronologically for strict time-series ordering
    df_features = df_features.sort_values(by="time").reset_index(drop=True)
    X = df_features[FEATURE_COLUMNS]
    y = df_features[TARGET_COLUMN]

    # Hyperparameters
    params = {
        "objective": "regression",
        "metric": "rmse",
        "boosting_type": "gbdt",
        "n_estimators": 350,
        "learning_rate": 0.03,
        "num_leaves": 31,
        "max_depth": 6,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "min_child_samples": 20,
        "n_jobs": 2,
        "random_state": 42,
        "verbose": -1,
    }

    # Setup MLflow
    mlruns_dir = PROJECT_ROOT / "ml" / "mlruns"
    mlruns_dir.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(f"file:///{mlruns_dir.resolve().as_posix()}")
    mlflow.set_experiment("airsense_aqi_forecasting")

    # Walk-Forward Validation (4 Splits)
    tscv = TimeSeriesSplit(n_splits=4)
    fold_rmses, fold_maes, fold_r2s, fold_da = [], [], [], []

    logger.info("Initiating 4-fold Walk-Forward Validation (TimeSeriesSplit)...")

    with mlflow.start_run(run_name=f"lgbm_walkforward_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}") as run:
        mlflow.log_params(params)
        mlflow.log_param("num_features", len(FEATURE_COLUMNS))
        mlflow.log_param("total_samples", len(df_features))

        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            model_fold = lgb.LGBMRegressor(**params)
            model_fold.fit(
                X_train,
                y_train,
                eval_set=[(X_val, y_val)],
                callbacks=[lgb.early_stopping(stopping_rounds=30, verbose=False)],
            )

            preds = model_fold.predict(X_val)
            rmse = np.sqrt(mean_squared_error(y_val, preds))
            mae = mean_absolute_error(y_val, preds)
            r2 = r2_score(y_val, preds)
            da = calculate_directional_accuracy(y_val.to_numpy(), preds)

            fold_rmses.append(rmse)
            fold_maes.append(mae)
            fold_r2s.append(r2)
            fold_da.append(da)

            mlflow.log_metric(f"fold_{fold+1}_rmse", round(rmse, 2))
            mlflow.log_metric(f"fold_{fold+1}_mae", round(mae, 2))
            logger.info("  Fold %d: RMSE=%.2f | MAE=%.2f | R²=%.3f | DirAcc=%.1f%%", fold + 1, rmse, mae, r2, da)

        mean_rmse = float(np.mean(fold_rmses))
        mean_mae = float(np.mean(fold_maes))
        mean_r2 = float(np.mean(fold_r2s))
        mean_da = float(np.mean(fold_da))

        mlflow.log_metric("mean_rmse", round(mean_rmse, 2))
        mlflow.log_metric("mean_mae", round(mean_mae, 2))
        mlflow.log_metric("mean_r2", round(mean_r2, 3))
        mlflow.log_metric("mean_directional_accuracy", round(mean_da, 1))

        # Train final production model on full dataset
        logger.info("Training final production model across complete dataset...")
        final_model = lgb.LGBMRegressor(**params)
        final_model.fit(X, y)

        # Feature importances
        feature_importance = pd.DataFrame({
            "feature": FEATURE_COLUMNS,
            "importance": final_model.feature_importances_,
        }).sort_values("importance", ascending=False)
        top_features = feature_importance.head(5).to_dict(orient="records")

        # Save to staging
        staging_dir = PROJECT_ROOT / "ml" / "staging"
        staging_dir.mkdir(parents=True, exist_ok=True)
        staging_path = staging_dir / "lgbm_aqi.pkl"
        joblib.dump(final_model, staging_path)
        logger.info("Saved trained model artifact to staging: %s", staging_path)

        # Model Promotion check (Champion-Challenger logic)
        promoted = False
        production_dir = PROJECT_ROOT / "ml" / "production"
        production_dir.mkdir(parents=True, exist_ok=True)
        prod_model_path = production_dir / "lgbm_aqi.pkl"
        prod_metrics_path = production_dir / "metrics.json"

        if mean_rmse < promotion_threshold:
            promoted = True
            joblib.dump(final_model, prod_model_path)
            metrics_payload = {
                "promoted_at": datetime.now(timezone.utc).isoformat(),
                "model_version": "lgbm_v1",
                "rmse": round(mean_rmse, 2),
                "mae": round(mean_mae, 2),
                "r2": round(mean_r2, 3),
                "directional_accuracy": round(mean_da, 1),
                "top_features": top_features,
                "mlflow_run_id": run.info.run_id,
                "promotion_threshold": promotion_threshold,
            }
            with prod_metrics_path.open("w", encoding="utf-8") as f:
                json.dump(metrics_payload, f, indent=2)
            logger.info("🎯 Champion Model PROMOTED to production! RMSE=%.2f < threshold=%.2f", mean_rmse, promotion_threshold)
        else:
            logger.warning("Model RMSE=%.2f exceeded threshold=%.2f — not promoted.", mean_rmse, promotion_threshold)

        results = {
            "mean_rmse": round(mean_rmse, 2),
            "mean_mae": round(mean_mae, 2),
            "mean_r2": round(mean_r2, 3),
            "directional_accuracy": round(mean_da, 1),
            "promoted": promoted,
            "top_features": top_features,
            "mlflow_run_id": run.info.run_id,
        }
        return results


def main():
    settings = load_settings(PROJECT_ROOT / "config.yaml")
    threshold = float(settings.get("ml", {}).get("rmse_promotion_threshold", 30.0))
    results = train_and_evaluate(promotion_threshold=threshold)
    print("\n" + "=" * 60)
    print("  AirSense LightGBM Model Training Complete!")
    print(f"  • Mean RMSE:                 {results['mean_rmse']} AQI units (Target < {threshold})")
    print(f"  • Mean MAE:                  {results['mean_mae']} AQI units")
    print(f"  • R² Score:                  {results['mean_r2']}")
    print(f"  • Directional Accuracy:      {results['directional_accuracy']}%")
    print(f"  • Promoted to Production:    {results['promoted']}")
    print(f"  • MLflow Run ID:             {results['mlflow_run_id']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
