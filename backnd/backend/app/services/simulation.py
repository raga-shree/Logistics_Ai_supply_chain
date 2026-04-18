"""
Simulation Service — CognixOps
Disruption impact estimation using CSV-backed KPI data for consistency.
"""

import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

PLAYBOOKS = {
    "port_closure": [
        "Switch to air freight for critical SKUs immediately",
        "Activate secondary sea route via alternative port",
        "Notify downstream DCs to buffer safety stock by 20%",
        "Trigger supplier expedite orders for top-10 SKUs",
    ],
    "supplier_delay": [
        "Activate alternate supplier from approved vendor list",
        "Redistribute existing inventory across regional DCs",
        "Place emergency PO with spot-buy supplier",
        "Alert sales team to manage customer expectations",
    ],
    "weather": [
        "Reroute shipments to unaffected transport corridors",
        "Pre-position inventory closer to demand centers",
        "Engage backup carrier for affected lanes",
        "Increase safety stock for high-priority products",
    ],
    "demand_spike": [
        "Increase production orders by estimated spike volume",
        "Pull forward inbound shipments from buffer warehouses",
        "Activate overflow warehouse capacity",
        "Prioritize allocation to highest-margin customers",
    ],
    "transport_failure": [
        "Switch to next best available transport mode",
        "Split shipment across multiple smaller carriers",
        "Engage spot market for immediate capacity",
        "Escalate to logistics manager for manual coordination",
    ],
}

SEVERITY_IMPACT = {
    "port_closure":       {"cost_mult": 1.35, "delay": 8,  "sl_drop": 12},
    "supplier_delay":     {"cost_mult": 1.20, "delay": 5,  "sl_drop": 8},
    "weather":            {"cost_mult": 1.15, "delay": 3,  "sl_drop": 5},
    "demand_spike":       {"cost_mult": 1.40, "delay": 2,  "sl_drop": 6},
    "transport_failure":  {"cost_mult": 1.25, "delay": 4,  "sl_drop": 7},
}


def run_simulation(disruption_type: str, affected_node: str,
                   severity: float, duration_days: int) -> dict:
    """
    Uses latest KPI snapshot from CSV as baseline, then applies
    disruption impact multipliers — giving consistent, reproducible results.
    """
    # Load latest KPI as baseline
    kpi_df = pd.read_csv(DATA_DIR / "kpi_snapshots.csv")
    baseline = kpi_df.iloc[-1]  # latest day

    impact  = SEVERITY_IMPACT.get(disruption_type, {"cost_mult": 1.1, "delay": 2, "sl_drop": 3})
    sev_scl = severity  # 0.0–1.0

    cost_impact = round(
        float(baseline["total_cost_usd"]) * (impact["cost_mult"] - 1) * sev_scl * (duration_days / 7), 2
    )
    delay        = round(impact["delay"] * sev_scl * (1 + duration_days * 0.05), 1)
    service_drop = round(impact["sl_drop"] * sev_scl, 1)
    risk_score   = round(min(1.0, severity * 0.5 + (duration_days / 30) * 0.3 + 0.1), 3)

    playbook   = PLAYBOOKS.get(disruption_type, ["Review situation and escalate"])
    severity_label = (
        "critical" if risk_score >= 0.75 else
        "high"     if risk_score >= 0.5  else
        "medium"   if risk_score >= 0.3  else "low"
    )

    return {
        "disruption_type":           disruption_type,
        "affected_node":             affected_node,
        "estimated_cost_impact_usd": cost_impact,
        "estimated_delay_days":      delay,
        "service_level_drop":        service_drop,
        "recommended_playbook":      playbook,
        "risk_score":                risk_score,
        "severity":                  severity_label,
        # KPI before/after for frontend chart
        "kpi_before": {
            "service_level":    float(baseline["service_level_pct"]),
            "total_cost":       float(baseline["total_cost_usd"]),
            "on_time_delivery": float(baseline["on_time_delivery_pct"]),
            "co2_kg":           float(baseline["co2_emissions_kg"]),
        },
        "kpi_after": {
            "service_level":    round(float(baseline["service_level_pct"]) - service_drop, 1),
            "total_cost":       round(float(baseline["total_cost_usd"]) + cost_impact, 2),
            "on_time_delivery": round(float(baseline["on_time_delivery_pct"]) - service_drop * 0.7, 1),
            "co2_kg":           round(float(baseline["co2_emissions_kg"]) * (1 + sev_scl * 0.1), 0),
        },
        "recommended_actions": playbook,
    }
