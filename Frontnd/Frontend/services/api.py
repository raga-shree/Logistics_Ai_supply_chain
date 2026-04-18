"""
API Service Layer — CognixOps Frontend v3
Handles all HTTP calls to the FastAPI backend.
v3 adds: /coordination/* and /chatbot/message endpoints.
"""

import requests
import streamlit as st
from config import API_BASE

_TIMEOUT = 15


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get(path: str, params: dict = None) -> dict | None:
    url = f"{API_BASE}{path}"
    try:
        r = requests.get(url, params=params, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach backend at {API_BASE}. Is it running?")
        return None
    except requests.exceptions.Timeout:
        st.error(f"Request to {url} timed out after {_TIMEOUT}s")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Backend error {e.response.status_code}: {e.response.text[:200]}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def _post(path: str, payload: dict) -> dict | None:
    url = f"{API_BASE}{path}"
    try:
        r = requests.post(url, json=payload, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach backend at {API_BASE}. Is it running?")
        return None
    except requests.exceptions.Timeout:
        st.error(f"Request to {url} timed out after {_TIMEOUT}s")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Backend error {e.response.status_code}: {e.response.text[:200]}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


# ── Health ────────────────────────────────────────────────────────────────────

def health_check() -> bool:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=4)
        return r.status_code == 200
    except Exception:
        return False


# ── Forecast ─────────────────────────────────────────────────────────────────

def get_forecast(sku: str, horizon_days: int = 7) -> dict | None:
    raw = _post("/forecast/", {
        "product_id":           sku,
        "region":               "ALL",
        "horizon_days":         horizon_days,
        "include_safety_stock": True,
    })
    if raw is None:
        return None
    points = raw.get("forecast", [])
    return {
        "sku":                sku,
        "dates":              [p["date"]             for p in points],
        "forecast":           [p["predicted_demand"] for p in points],
        "lower":              [p["lower_bound"]       for p in points],
        "upper":              [p["upper_bound"]       for p in points],
        "model_mae":          raw.get("model_mae",          0),
        "baseline_mae":       raw.get("baseline_mae",       0),
        "model_fill_rate":    raw.get("model_fill_rate",    0),
        "baseline_fill_rate": raw.get("baseline_fill_rate", 0),
        "safety_stock":       raw.get("safety_stock"),
        "reorder_point":      raw.get("reorder_point"),
    }


def get_all_forecasts(skus: list[str], horizon_days: int = 7) -> list[dict]:
    return [d for sku in skus if (d := get_forecast(sku, horizon_days))]


# ── KPI ──────────────────────────────────────────────────────────────────────

def get_kpis() -> dict | None:
    raw = _get("/kpi")
    if raw is None:
        return None
    return {
        "service_level":      raw.get("service_level_pct"),
        "total_cost":         raw.get("total_cost_usd"),
        "co2_kg":             raw.get("co2_emissions_kg"),
        "on_time_delivery":   raw.get("on_time_delivery_pct"),
        "inventory_turnover": raw.get("inventory_turnover"),
    }


# ── Optimization ─────────────────────────────────────────────────────────────

_PRIORITY_MAP = {
    "port_closure":      "speed",
    "supplier_delay":    "cost",
    "weather":           "co2",
    "demand_spike":      "speed",
    "transport_failure": "balanced",
    "none":              "balanced",
}


def get_optimization(disruption_type: str = "none") -> dict | None:
    priority = _PRIORITY_MAP.get(disruption_type, "balanced")
    raw = _post("/optimize/route", {
        "origin":          "WH-A",
        "destination":     "CUST",
        "cargo_weight_kg": 1000,
        "priority":        priority,
        "carrier_cap":     3000,
    })
    if raw is None:
        return None
    return {
        "total_cost":          raw.get("total_cost", 0),
        "total_co2":           raw.get("total_co2",  0),
        "service_level":       raw.get("service_level", 0),
        "routes":              raw.get("routes", []),
        "optimization_method": raw.get("optimization_method", ""),
        "network_flow_cost":   raw.get("network_flow_cost",   0),
        "network_flow_co2":    raw.get("network_flow_co2",    0),
    }


# ── Simulation ────────────────────────────────────────────────────────────────

def get_simulation(disruption_type: str) -> dict | None:
    if disruption_type == "none":
        return None
    raw = _post("/simulate/disruption", {
        "disruption_type": disruption_type,
        "affected_node":   "WH-A",
        "severity":        0.7,
        "duration_days":   3,
    })
    if raw is None:
        return None
    return {
        "kpi_before":          raw.get("kpi_before", {}),
        "kpi_after":           raw.get("kpi_after",  {}),
        "recommended_actions": raw.get("recommended_actions", raw.get("recommended_playbook", [])),
        "severity":            raw.get("severity", "low"),
        "risk_score":          raw.get("risk_score", 0),
        "cost_impact":         raw.get("estimated_cost_impact_usd", 0),
        "delay_days":          raw.get("estimated_delay_days", 0),
        "service_drop":        raw.get("service_level_drop", 0),
        "disruption_type":     disruption_type,
    }


# ── Anomaly Detection ─────────────────────────────────────────────────────────

def get_anomalies(sku: str, sensitivity: float = 2.0) -> dict | None:
    return _post("/anomaly/detect", {
        "product_id":  sku,
        "region":      "ALL",
        "sensitivity": sensitivity,
    })


# ── Coordination (v3 NEW) ─────────────────────────────────────────────────────

def get_coordination_network() -> dict | None:
    return _get("/coordination/network")


def get_coordination_feed(limit: int = 20) -> list:
    data = _get(f"/coordination/feed?limit={limit}")
    return (data or {}).get("events", [])


def get_node_detail(node_id: str) -> dict | None:
    return _get(f"/coordination/node/{node_id}")


