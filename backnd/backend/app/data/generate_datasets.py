"""
Dataset Generator for CognixOps
Run once: python generate_datasets.py
Produces 3 CSV files used by all backend services.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random, os

np.random.seed(42)
random.seed(42)

OUT = os.path.dirname(__file__)

# ─── Constants ──────────────────────────────────────────────────────────────
SKUS    = ["SKU-001", "SKU-002", "SKU-003", "SKU-004", "SKU-005"]
REGIONS = ["North", "South", "East", "West", "Central"]

# SKU base demand profiles (units/day)
SKU_PROFILES = {
    "SKU-001": {"base": 320, "trend": 0.8,  "amplitude": 40,  "noise": 15},
    "SKU-002": {"base": 180, "trend": 1.5,  "amplitude": 25,  "noise": 10},
    "SKU-003": {"base": 450, "trend": -0.5, "amplitude": 60,  "noise": 20},
    "SKU-004": {"base": 90,  "trend": 2.0,  "amplitude": 12,  "noise": 6},
    "SKU-005": {"base": 270, "trend": 0.3,  "amplitude": 35,  "noise": 12},
}

# Disruption events injected into history (for anomaly demos)
DISRUPTION_EVENTS = [
    {"start": 30, "end": 34, "sku": "SKU-001", "multiplier": 2.3, "type": "demand_spike"},
    {"start": 55, "end": 58, "sku": "SKU-003", "multiplier": 0.2, "type": "supplier_delay"},
    {"start": 75, "end": 77, "sku": "SKU-002", "multiplier": 1.8, "type": "demand_spike"},
]

# ─── 1. DEMAND HISTORY (200 rows = 40 days × 5 SKUs) ────────────────────────
def generate_demand_history():
    rows = []
    start_date = datetime(2025, 1, 1)

    for day_idx in range(40):          # 40 days × 5 SKUs = 200 rows exactly
        date = start_date + timedelta(days=day_idx)
        dow  = date.weekday()           # 0=Mon … 6=Sun

        for sku in SKUS:
            p = SKU_PROFILES[sku]

            # Trend component
            trend_val = p["trend"] * day_idx

            # Weekly seasonality (Fourier-style: sin + cos)
            season = p["amplitude"] * np.sin(2 * np.pi * day_idx / 7)
            season += p["amplitude"] * 0.3 * np.cos(2 * np.pi * day_idx / 14)

            # Weekend dip
            weekend_factor = 0.75 if dow >= 5 else 1.0

            # Gaussian noise
            noise = np.random.normal(0, p["noise"])

            demand = max(0, (p["base"] + trend_val + season) * weekend_factor + noise)

            # Inject disruption events
            for ev in DISRUPTION_EVENTS:
                if ev["sku"] == sku and ev["start"] <= day_idx < ev["end"]:
                    demand *= ev["multiplier"]
                    break

            # Safety stock & reorder point (deterministic formulas)
            sigma     = p["noise"] * 1.5
            lead_time = 7
            z         = 1.645   # 95% service level
            ss        = round(z * sigma * np.sqrt(lead_time), 1)
            rop       = round((p["base"] / 7) * lead_time + ss, 1)  # daily avg × LT + SS

            rows.append({
                "date":           date.strftime("%Y-%m-%d"),
                "day_index":      day_idx,
                "day_of_week":    dow,
                "sku":            sku,
                "region":         "ALL",
                "demand":         round(demand, 1),
                "base_demand":    p["base"],
                "trend_val":      round(trend_val, 2),
                "season_val":     round(season, 2),
                "is_weekend":     int(dow >= 5),
                "disruption":     next(
                                    (ev["type"] for ev in DISRUPTION_EVENTS
                                     if ev["sku"] == sku and ev["start"] <= day_idx < ev["end"]),
                                    "none"
                                  ),
                "safety_stock":   ss,
                "reorder_point":  rop,
            })

    df = pd.DataFrame(rows)
    path = os.path.join(OUT, "demand_history.csv")
    df.to_csv(path, index=False)
    print(f"✓ demand_history.csv  → {len(df)} rows")
    return df


# ─── 2. ROUTE OPTIONS (20 rows = 5 routes × 4 transport modes) ──────────────
def generate_route_options():
    NODES = [
        ("WH-A",  "PLT-1",  "Paris WH",         "Manchester Plant"),
        ("WH-A",  "PLT-2",  "Paris WH",         "Amsterdam Plant"),
        ("WH-B",  "PLT-1",  "London WH",        "Manchester Plant"),
        ("WH-B",  "CUST",   "London WH",        "Munich Customer"),
        ("PLT-2", "CUST",   "Amsterdam Plant",  "Munich Customer"),
    ]
    MODES = {
        "air":  {"base_cost_per_kg": 8.2,  "base_days": 1.5, "co2_per_kg": 0.95, "capacity_kg": 5000},
        "sea":  {"base_cost_per_kg": 0.45, "base_days": 22,  "co2_per_kg": 0.012,"capacity_kg": 50000},
        "road": {"base_cost_per_kg": 1.85, "base_days": 4.5, "co2_per_kg": 0.16, "capacity_kg": 20000},
        "rail": {"base_cost_per_kg": 1.15, "base_days": 9,   "co2_per_kg": 0.041,"capacity_kg": 30000},
    }
    CARRIERS = {
        "air":  "DHL Express",
        "sea":  "Maersk",
        "road": "DB Schenker",
        "rail": "DB Cargo",
    }
    CARGO_KG = 1000   # reference shipment weight

    rows = []
    for (from_id, to_id, from_label, to_label) in NODES:
        for mode, cfg in MODES.items():
            jitter = np.random.uniform(0.92, 1.08)
            cost   = round(cfg["base_cost_per_kg"] * CARGO_KG * jitter, 2)
            days   = round(cfg["base_days"] * jitter, 1)
            co2    = round(cfg["co2_per_kg"]  * CARGO_KG * jitter, 2)
            rows.append({
                "from_node":       from_id,
                "to_node":         to_id,
                "from_label":      from_label,
                "to_label":        to_label,
                "mode":            mode,
                "carrier":         CARRIERS[mode],
                "cost_usd":        cost,
                "lead_time_days":  days,
                "co2_kg":          co2,
                "capacity_kg":     cfg["capacity_kg"],
                "cargo_weight_kg": CARGO_KG,
            })

    df = pd.DataFrame(rows)
    path = os.path.join(OUT, "route_options.csv")
    df.to_csv(path, index=False)
    print(f"✓ route_options.csv   → {len(df)} rows")
    return df


# ─── 3. KPI SNAPSHOTS (30 rows = daily KPI log for 30 days) ─────────────────
def generate_kpi_snapshots():
    rows = []
    start = datetime(2025, 1, 1)
    for i in range(30):
        date = start + timedelta(days=i)
        # Simulate gradual improvement trend with noise
        base_sl  = 91 + i * 0.2 + np.random.normal(0, 0.8)
        base_otd = 88 + i * 0.15 + np.random.normal(0, 0.7)
        rows.append({
            "date":                date.strftime("%Y-%m-%d"),
            "service_level_pct":   round(min(99, max(85, base_sl)), 1),
            "avg_lead_time_days":  round(np.random.uniform(4, 10), 1),
            "total_cost_usd":      round(np.random.uniform(600_000, 1_800_000), 0),
            "co2_emissions_kg":    round(np.random.uniform(55_000, 190_000), 0),
            "inventory_turnover":  round(np.random.uniform(5, 13), 1),
            "on_time_delivery_pct":round(min(99, max(82, base_otd)), 1),
            "stockout_rate_pct":   round(np.random.uniform(0.5, 4.5), 2),
            "fill_rate_pct":       round(np.random.uniform(91, 99), 1),
        })
    df = pd.DataFrame(rows)
    path = os.path.join(OUT, "kpi_snapshots.csv")
    df.to_csv(path, index=False)
    print(f"✓ kpi_snapshots.csv   → {len(df)} rows")
    return df


if __name__ == "__main__":
    d = generate_demand_history()
    r = generate_route_options()
    k = generate_kpi_snapshots()
    print(f"\nTotal rows across all datasets: {len(d)+len(r)+len(k)}")
    print("\nDemand history sample:")
    print(d.head(3).to_string())
    print("\nRoute options sample:")
    print(r.head(3).to_string())
    print("\nKPI snapshot sample:")
    print(k.head(3).to_string())
