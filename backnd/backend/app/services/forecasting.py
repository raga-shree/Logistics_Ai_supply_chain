"""
Forecasting Service — CognixOps
=====================================
Implements a two-stage ensemble that mirrors the real Prophet + XGBoost pipeline:

Stage 1 — Prophet-style decomposition
  • Fits piecewise linear trend via np.polyfit
  • Adds Fourier-series seasonality (weekly + bi-weekly harmonics)
  • Computes 90% confidence intervals from residual std

Stage 2 — XGBoost-style gradient boosting correction
  • Trains sklearn GradientBoostingRegressor on exogenous features:
      day_of_week, day_index, is_weekend, lag_7, lag_14, rolling_7_mean
  • Predicts a demand correction delta on top of Stage 1 output

Safety stock uses the industry-standard formula:
  SS = z * σ * √(lead_time)   where z = 1.645 (95% SL)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_sku_history(product_id: str, region: str) -> pd.DataFrame:
    """Load demand history for a given SKU from the CSV dataset."""
    df = pd.read_csv(DATA_DIR / "demand_history.csv", parse_dates=["date"])
    mask = df["sku"] == product_id
    if region != "ALL":
        mask &= df["region"] == region
    sku_df = df[mask].sort_values("day_index").reset_index(drop=True)
    if sku_df.empty:
        raise ValueError(f"No data for product_id={product_id}, region={region}")
    return sku_df


def _fourier_features(t: np.ndarray, periods: list, n_terms: int = 2) -> np.ndarray:
    """
    Generate Fourier (sin/cos) features for seasonality modelling.
    Mirrors Prophet's approach of fitting sinusoidal components.
    """
    cols = []
    for p in periods:
        for k in range(1, n_terms + 1):
            cols.append(np.sin(2 * np.pi * k * t / p))
            cols.append(np.cos(2 * np.pi * k * t / p))
    return np.column_stack(cols)


def _build_xgb_features(df: pd.DataFrame) -> np.ndarray:
    """
    Build the feature matrix used by the GradientBoostingRegressor.
    Features: day_of_week, day_index, is_weekend, lag_7, lag_14, rolling_7_mean
    """
    demand = df["demand"].values
    n = len(demand)

    lag_7  = np.array([demand[max(0, i - 7)]  for i in range(n)])
    lag_14 = np.array([demand[max(0, i - 14)] for i in range(n)])
    roll7  = pd.Series(demand).rolling(7, min_periods=1).mean().values

    return np.column_stack([
        df["day_of_week"].values,
        df["day_index"].values,
        df["is_weekend"].values,
        lag_7,
        lag_14,
        roll7,
    ])


def run_forecast(product_id: str, region: str, horizon_days: int,
                 include_safety_stock: bool) -> dict:
    """
    Two-stage ensemble forecast: Prophet-style decomp → XGBoost correction.
    Returns dict matching ForecastResponse schema.
    """
    df = _load_sku_history(product_id, region)
    demand = df["demand"].values
    t      = df["day_index"].values.astype(float)
    n      = len(demand)

    # ── STAGE 1: Prophet-style decomposition ────────────────────────────────

    # 1a. Piecewise linear trend (degree-1 polynomial)
    trend_coeffs = np.polyfit(t, demand, 1)
    trend_fn     = np.poly1d(trend_coeffs)
    trend_vals   = trend_fn(t)

    # 1b. Fourier seasonality (weekly=7, bi-weekly=14)
    fourier_hist = _fourier_features(t, periods=[7, 14], n_terms=2)
    from sklearn.linear_model import Ridge
    ridge = Ridge(alpha=1.0)
    ridge.fit(fourier_hist, demand - trend_vals)
    season_vals = ridge.predict(fourier_hist)

    # 1c. Residuals from Stage 1
    stage1_fitted = trend_vals + season_vals
    residuals     = demand - stage1_fitted
    resid_std     = np.std(residuals[-20:])   # rolling std of last 20 days

    # ── STAGE 2: XGBoost-style gradient boosting on residuals ───────────────

    X_hist = _build_xgb_features(df)
    gbr    = GradientBoostingRegressor(
        n_estimators=80,
        max_depth=3,
        learning_rate=0.08,
        subsample=0.85,
        random_state=42,
    )
    gbr.fit(X_hist, residuals)   # learn to predict the residual

    # ── FORECAST: project horizon_days into the future ───────────────────────

    last_day   = int(t[-1])
    last_date  = df["date"].iloc[-1]

    forecast_points = []
    for i in range(1, horizon_days + 1):
        fut_t   = last_day + i
        fut_date = (last_date + timedelta(days=i)).strftime("%Y-%m-%d")
        fut_dow  = (last_date + timedelta(days=i)).weekday()
        fut_wknd = int(fut_dow >= 5)

        # Stage 1 projection
        stage1_pred = trend_fn(fut_t) + ridge.predict(
            _fourier_features(np.array([fut_t]), [7, 14], n_terms=2)
        )[0]

        # Stage 2 correction — build forward feature row
        lag_7_val  = demand[max(0, n - 7 + i - 1)]  if i <= 7  else stage1_pred
        lag_14_val = demand[max(0, n - 14 + i - 1)] if i <= 14 else stage1_pred
        roll7_val  = np.mean(demand[-7:])

        X_fut = np.array([[fut_dow, fut_t, fut_wknd, lag_7_val, lag_14_val, roll7_val]])
        correction = gbr.predict(X_fut)[0]

        predicted = max(0.0, stage1_pred + correction)
        lower     = max(0.0, predicted - 1.645 * resid_std)
        upper     = predicted + 1.645 * resid_std

        forecast_points.append({
            "date":             fut_date,
            "predicted_demand": round(predicted, 2),
            "lower_bound":      round(lower, 2),
            "upper_bound":      round(upper, 2),
        })

    # ── SAFETY STOCK (industry formula) ─────────────────────────────────────

    sigma      = np.std(demand[-14:])
    lead_time  = 7
    z_score    = 1.645   # 95% service level
    safety_stock  = round(z_score * sigma * np.sqrt(lead_time), 2) if include_safety_stock else None
    avg_daily     = float(np.mean(demand[-14:]))
    reorder_point = round(avg_daily * lead_time + (safety_stock or 0), 2)

    # ── VALIDATION METRICS (compare Stage 1 vs ensemble) ────────────────────

    stage1_mae    = float(np.mean(np.abs(residuals)))
    ensemble_mae  = float(np.mean(np.abs(demand - (stage1_fitted + gbr.predict(X_hist)))))
    # Fill rate proxy: % days demand was covered (demand ≤ reorder_point threshold)
    model_fill    = round(100 * np.mean(demand <= reorder_point * 1.2), 1)
    baseline_fill = round(100 * np.mean(demand <= (avg_daily * lead_time) * 1.2), 1)

    return {
        "product_id":         product_id,
        "region":             region,
        "forecast":           forecast_points,
        "safety_stock":       safety_stock,
        "reorder_point":      reorder_point,
        "model_mae":          round(ensemble_mae, 2),
        "baseline_mae":       round(stage1_mae, 2),
        "model_fill_rate":    model_fill,
        "baseline_fill_rate": baseline_fill,
    }
