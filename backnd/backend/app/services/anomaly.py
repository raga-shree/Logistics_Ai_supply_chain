"""
Anomaly Detection Service — CognixOps
Uses Z-score analysis on the real demand_history.csv dataset.
Flags injected disruption events and natural demand spikes.
"""

import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def detect_anomalies(product_id: str, region: str, sensitivity: float = 2.0) -> dict:
    """
    Z-score anomaly detection on historical demand.
    sensitivity = Z-score threshold (2.0 = standard, 1.5 = sensitive, 3.0 = conservative).
    """
    df = pd.read_csv(DATA_DIR / "demand_history.csv", parse_dates=["date"])
    mask = df["sku"] == product_id
    if region != "ALL":
        mask &= df["region"] == region
    sku_df = df[mask].sort_values("day_index").reset_index(drop=True)

    if sku_df.empty:
        return {"product_id": product_id, "region": region,
                "anomalies": [], "baseline_mean": 0, "baseline_std": 0}

    demand = sku_df["demand"].values
    mean   = float(np.mean(demand))
    std    = float(np.std(demand))

    if std == 0:
        return {"product_id": product_id, "region": region,
                "anomalies": [], "baseline_mean": round(mean, 2), "baseline_std": 0}

    anomalies = []
    for _, row in sku_df.iterrows():
        z = (row["demand"] - mean) / std
        if abs(z) >= sensitivity:
            severity = "high" if abs(z) >= 3.0 else ("medium" if abs(z) >= 2.5 else "low")
            direction = "above" if z > 0 else "below"
            explanation = (
                f"Demand of {row['demand']:.0f} units is {abs(z):.1f}σ {direction} mean "
                f"({mean:.0f} units). "
                + ({
                    "demand_spike":   "Possible demand spike event.",
                    "supplier_delay": "Possible supply shortfall — check supplier status.",
                }.get(row.get("disruption", "none"), "Monitor closely."))
            )
            anomalies.append({
                "date":        str(row["date"])[:10],
                "demand":      round(float(row["demand"]), 2),
                "z_score":     round(float(z), 3),
                "severity":    severity,
                "explanation": explanation,
                "disruption":  row.get("disruption", "none"),
            })

    return {
        "product_id":    product_id,
        "region":        region,
        "anomalies":     anomalies,
        "baseline_mean": round(mean, 2),
        "baseline_std":  round(std, 2),
    }
