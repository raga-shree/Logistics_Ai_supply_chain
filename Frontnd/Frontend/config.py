import os

# ─── Backend URL ─────────────────────────────────────────────────────────────
# Same machine:   streamlit run app.py
# Different IP:   export API_URL=http://192.168.x.x:8000 && streamlit run app.py
# Windows:        set API_URL=http://192.168.x.x:8000
API_BASE = os.getenv("API_URL", "https://logistics-ai-supply-chain.onrender.com").rstrip("/")

# ─── App ─────────────────────────────────────────────────────────────────────
APP_TITLE = "CognixOps — AI Logistics Intelligence"
APP_ICON  = "🔗"

# ─── Display ─────────────────────────────────────────────────────────────────
CHART_HEIGHT = 340
MAP_HEIGHT   = 420

# ─── Disruption types — MUST match backend DisruptionType enum exactly ────────
DISRUPTION_OPTIONS = {
    "none":              "No disruption (baseline)",
    "port_closure":      "Port closure",
    "supplier_delay":    "Supplier delay",
    "weather":           "Severe weather",
    "demand_spike":      "Demand spike",
    "transport_failure": "Transport failure",
}

# ─── SKUs — must match demand_history.csv ────────────────────────────────────
SKUS = ["SKU-001", "SKU-002", "SKU-003", "SKU-004", "SKU-005"]

# ─── Route nodes — lat/lon for Folium map ────────────────────────────────────
NODES = {
    "WH-A":  {"lat": 48.8566, "lon":  2.3522, "label": "Paris WH"},
    "WH-B":  {"lat": 51.5074, "lon": -0.1278, "label": "London WH"},
    "PLT-1": {"lat": 53.4808, "lon": -2.2426, "label": "Manchester Plant"},
    "PLT-2": {"lat": 52.3667, "lon":  4.8945, "label": "Amsterdam Plant"},
    "CUST":  {"lat": 48.1351, "lon": 11.5820, "label": "Munich Customer"},
}
