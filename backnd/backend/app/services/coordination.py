"""
Coordination Service — CognixOps v3
Manages the multi-tier supply chain network:
  Suppliers → Factories → Customers
Provides live node status, order flow paths, and the coordination feed.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).parent.parent / "data"

# ── Static network topology ────────────────────────────────────────────────────
SUPPLIERS = {
    "SUP-A": {
        "name": "SupplierCo A",
        "location": "Rotterdam, NL",
        "lat": 51.9225, "lon": 4.4792,
        "contact": "supplierA@cognixops.demo",
        "lead_time_days": 5,
        "capacity_units": 6000,
    },
    "SUP-B": {
        "name": "SupplierCo B",
        "location": "Hamburg, DE",
        "lat": 53.5753, "lon": 10.0153,
        "contact": "supplierB@cognixops.demo",
        "lead_time_days": 7,
        "capacity_units": 4000,
    },
    "SUP-C": {
        "name": "SupplierCo C",
        "location": "Gdansk, PL",
        "lat": 54.3520, "lon": 18.6466,
        "contact": "supplierC@cognixops.demo",
        "lead_time_days": 9,
        "capacity_units": 3000,
    },
}

FACTORIES = {
    "FAC-BERLIN": {
        "name": "Plant Berlin",
        "location": "Berlin, DE",
        "lat": 52.5200, "lon": 13.4050,
        "output_per_day": 820,
        "capacity_units": 10000,
    },
    "FAC-WARSAW": {
        "name": "Plant Warsaw",
        "location": "Warsaw, PL",
        "lat": 52.2297, "lon": 21.0122,
        "output_per_day": 650,
        "capacity_units": 8000,
    },
    "FAC-LYON": {
        "name": "Plant Lyon",
        "location": "Lyon, FR",
        "lat": 45.7640, "lon": 4.8357,
        "output_per_day": 700,
        "capacity_units": 9000,
    },
}

CUSTOMERS = {
    "CUST-EU": {
        "name": "RetailCo EU",
        "location": "Munich, DE",
        "lat": 48.1351, "lon": 11.5820,
        "contract_units_month": 12000,
        "priority": "high",
    },
    "CUST-UK": {
        "name": "MegaMart UK",
        "location": "London, UK",
        "lat": 51.5074, "lon": -0.1278,
        "contract_units_month": 18000,
        "priority": "critical",
    },
    "CUST-DE": {
        "name": "WholeSale DE",
        "location": "Frankfurt, DE",
        "lat": 50.1109, "lon": 8.6821,
        "contract_units_month": 6000,
        "priority": "medium",
    },
}

# ── Active order flows (Supplier → Factory → Customer) ────────────────────────
ORDER_FLOWS = [
    {"id": "ORD-001", "supplier": "SUP-A", "factory": "FAC-BERLIN", "customer": "CUST-EU",
     "sku": "SKU-001", "units": 3000, "status": "in_transit", "eta_days": 4},
    {"id": "ORD-002", "supplier": "SUP-A", "factory": "FAC-LYON",   "customer": "CUST-DE",
     "sku": "SKU-002", "units": 1200, "status": "delivered",  "eta_days": 0},
    {"id": "ORD-003", "supplier": "SUP-B", "factory": "FAC-WARSAW", "customer": "CUST-UK",
     "sku": "SKU-003", "units": 5500, "status": "at_risk",    "eta_days": 9},
    {"id": "ORD-004", "supplier": "SUP-C", "factory": "FAC-LYON",   "customer": "CUST-UK",
     "sku": "SKU-004", "units": 2000, "status": "delayed",    "eta_days": 12},
    {"id": "ORD-005", "supplier": "SUP-A", "factory": "FAC-BERLIN", "customer": "CUST-UK",
     "sku": "SKU-005", "units": 1800, "status": "confirmed",  "eta_days": 6},
]


def _supplier_stock(supplier_id: str) -> int:
    """Derive stock level from kpi_snapshots — scaled per supplier."""
    try:
        df = pd.read_csv(DATA_DIR / "kpi_snapshots.csv")
        base = float(df.iloc[-1]["inventory_turnover"])
        seeds = {"SUP-A": 4200, "SUP-B": 1100, "SUP-C": 280}
        return seeds.get(supplier_id, 1000)
    except Exception:
        return 1000


def _supplier_status(supplier_id: str, stock: int, cap: int) -> dict:
    ratio = stock / cap
    if ratio > 0.5:
        return {"status": "ok", "label": "On schedule", "color": "#1D9E75"}
    elif ratio > 0.15:
        return {"status": "warning", "label": "Mild delay", "color": "#EF9F27"}
    else:
        return {"status": "critical", "label": "Critical low", "color": "#E24B4A"}


def _factory_utilization(factory_id: str) -> float:
    utils = {"FAC-BERLIN": 0.94, "FAC-WARSAW": 0.52, "FAC-LYON": 0.88}
    return utils.get(factory_id, 0.80)


def _factory_status(util: float) -> dict:
    if util >= 0.85:
        return {"status": "ok",       "label": f"Running {util*100:.0f}%", "color": "#1D9E75"}
    elif util >= 0.60:
        return {"status": "warning",  "label": f"Partial stop",            "color": "#EF9F27"}
    else:
        return {"status": "critical", "label": f"Major stoppage",          "color": "#E24B4A"}


def _customer_order_status(customer_id: str) -> dict:
    flows = [f for f in ORDER_FLOWS if f["customer"] == customer_id]
    if not flows:
        return {"status": "ok", "label": "No active orders", "units_needed": 0, "eta_days": 0}
    at_risk  = any(f["status"] in ("at_risk", "delayed") for f in flows)
    total    = sum(f["units"] for f in flows)
    min_eta  = min(f["eta_days"] for f in flows)
    if at_risk:
        return {"status": "critical", "label": "At risk",         "units_needed": total, "eta_days": min_eta}
    delivered = all(f["status"] == "delivered" for f in flows)
    if delivered:
        return {"status": "ok",       "label": "Fulfilled",       "units_needed": total, "eta_days": 0}
    return     {"status": "ok",       "label": "Order confirmed", "units_needed": total, "eta_days": min_eta}


# ── Public API ────────────────────────────────────────────────────────────────

def get_network_status() -> dict:
    """Return full live status of all nodes: suppliers, factories, customers."""
    suppliers_out = {}
    for sid, s in SUPPLIERS.items():
        stock  = _supplier_stock(sid)
        status = _supplier_status(sid, stock, s["capacity_units"])
        suppliers_out[sid] = {**s, "stock_units": stock, **status}

    factories_out = {}
    for fid, f in FACTORIES.items():
        util   = _factory_utilization(fid)
        status = _factory_status(util)
        queue_days = round((1 - util) * 7 + 1, 1)
        factories_out[fid] = {**f, "utilization": util,
                               "queue_days": queue_days, **status}

    customers_out = {}
    for cid, c in CUSTOMERS.items():
        order_status = _customer_order_status(cid)
        customers_out[cid] = {**c, **order_status}

    return {
        "suppliers": suppliers_out,
        "factories": factories_out,
        "customers": customers_out,
        "order_flows": ORDER_FLOWS,
    }


def get_node_detail(node_id: str) -> dict:
    """Return detailed info for a single node (any tier)."""
    if node_id in SUPPLIERS:
        s = SUPPLIERS[node_id]
        stock  = _supplier_stock(node_id)
        status = _supplier_status(node_id, stock, s["capacity_units"])
        flows  = [f for f in ORDER_FLOWS if f["supplier"] == node_id]
        return {
            "id": node_id, "tier": "supplier", **s,
            "stock_units": stock, **status,
            "active_flows": flows,
            "metrics": {
                "stock_units":     stock,
                "capacity_units":  s["capacity_units"],
                "lead_time_days":  s["lead_time_days"],
                "utilization_pct": round(stock / s["capacity_units"] * 100, 1),
            },
        }
    if node_id in FACTORIES:
        f    = FACTORIES[node_id]
        util = _factory_utilization(node_id)
        status = _factory_status(util)
        flows  = [fo for fo in ORDER_FLOWS if fo["factory"] == node_id]
        return {
            "id": node_id, "tier": "factory", **f,
            "utilization": util, **status,
            "active_flows": flows,
            "metrics": {
                "output_per_day":  f["output_per_day"],
                "utilization_pct": round(util * 100, 1),
                "queue_days":      round((1 - util) * 7 + 1, 1),
                "capacity_units":  f["capacity_units"],
            },
        }
    if node_id in CUSTOMERS:
        c = CUSTOMERS[node_id]
        order_status = _customer_order_status(node_id)
        flows = [fo for fo in ORDER_FLOWS if fo["customer"] == node_id]
        return {
            "id": node_id, "tier": "customer", **c,
            **order_status, "active_flows": flows,
            "metrics": {
                "units_needed":         order_status["units_needed"],
                "contract_units_month": c["contract_units_month"],
                "eta_days":             order_status["eta_days"],
                "active_orders":        len(flows),
            },
        }
    return {"error": f"Node {node_id} not found"}


def get_coordination_feed(limit: int = 20) -> list:
    """Generate the live coordination event feed."""
    now = datetime.utcnow()
    events = [
        {"severity": "critical", "title": "MegaMart UK at risk",
         "body": "SupplierCo C critical low — consider rerouting via SupplierCo A → Berlin",
         "node_id": "CUST-UK", "minutes_ago": 2},
        {"severity": "warning",  "title": "Plant Warsaw partial stop",
         "body": "Output down 48% — Lyon picking up overflow; monitor queue depth",
         "node_id": "FAC-WARSAW", "minutes_ago": 14},
        {"severity": "ok",       "title": "WholeSale DE fulfilled",
         "body": "1,200 units shipped via SupplierCo A → Lyon route on schedule",
         "node_id": "CUST-DE", "minutes_ago": 41},
        {"severity": "warning",  "title": "SupplierCo B mild delay",
         "body": "Lead time extended 6d → 9d due to port congestion at Hamburg",
         "node_id": "SUP-B", "minutes_ago": 62},
        {"severity": "ok",       "title": "SupplierCo A restocked",
         "body": "4,200 units available — capacity at 70%. Ready to fulfil ORD-001.",
         "node_id": "SUP-A", "minutes_ago": 95},
        {"severity": "critical", "title": "ORD-004 delayed — SupplierCo C",
         "body": "12-day ETA for MegaMart UK. Recommend emergency alternate sourcing.",
         "node_id": "ORD-004", "minutes_ago": 130},
    ]
    for e in events:
        e["timestamp"] = (now - timedelta(minutes=e["minutes_ago"])).isoformat()
    return events[:limit]


def get_network_map_data() -> dict:
    """Return all nodes with lat/lon for the coordination map overlay."""
    nodes = []
    for sid, s in SUPPLIERS.items():
        stock  = _supplier_stock(sid)
        status = _supplier_status(sid, stock, s["capacity_units"])
        nodes.append({"id": sid, "tier": "supplier", "name": s["name"],
                       "lat": s["lat"], "lon": s["lon"],
                       "status": status["status"], "label": status["label"]})
    for fid, f in FACTORIES.items():
        util   = _factory_utilization(fid)
        status = _factory_status(util)
        nodes.append({"id": fid, "tier": "factory", "name": f["name"],
                       "lat": f["lat"], "lon": f["lon"],
                       "status": status["status"], "label": status["label"]})
    for cid, c in CUSTOMERS.items():
        os = _customer_order_status(cid)
        nodes.append({"id": cid, "tier": "customer", "name": c["name"],
                       "lat": c["lat"], "lon": c["lon"],
                       "status": os["status"], "label": os["label"]})
    edges = []
    for flow in ORDER_FLOWS:
        sup_node  = SUPPLIERS.get(flow["supplier"], {})
        fac_node  = FACTORIES.get(flow["factory"], {})
        cust_node = CUSTOMERS.get(flow["customer"], {})
        if sup_node and fac_node:
            edges.append({"from_lat": sup_node["lat"],  "from_lon": sup_node["lon"],
                           "to_lat":   fac_node["lat"],  "to_lon":   fac_node["lon"],
                           "status": flow["status"], "order_id": flow["id"]})
        if fac_node and cust_node:
            edges.append({"from_lat": fac_node["lat"],  "from_lon": fac_node["lon"],
                           "to_lat":   cust_node["lat"], "to_lon":   cust_node["lon"],
                           "status": flow["status"], "order_id": flow["id"]})
    return {"nodes": nodes, "edges": edges, "flows": ORDER_FLOWS}
