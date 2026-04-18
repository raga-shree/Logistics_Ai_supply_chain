"""KPI Service — reads latest snapshot from CSV for consistent results."""
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def get_kpis() -> dict:
    """Return the latest KPI row from the CSV snapshot log."""
    df = pd.read_csv(DATA_DIR / "kpi_snapshots.csv")
    row = df.iloc[-1]   # most recent day
    return {
        "service_level_pct":    float(row["service_level_pct"]),
        "avg_lead_time_days":   float(row["avg_lead_time_days"]),
        "total_cost_usd":       float(row["total_cost_usd"]),
        "co2_emissions_kg":     float(row["co2_emissions_kg"]),
        "inventory_turnover":   float(row["inventory_turnover"]),
        "on_time_delivery_pct": float(row["on_time_delivery_pct"]),
        "stockout_rate_pct":    float(row["stockout_rate_pct"]),
        "fill_rate_pct":        float(row["fill_rate_pct"]),
    }
