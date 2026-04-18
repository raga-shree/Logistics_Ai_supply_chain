"""
CognixOps — AI Logistics Intelligence Dashboard  v3.0
VIBGYOR Light Edition
v3 adds: Coordination Hub tab + AI Chatbot tab
"""

import streamlit as st

st.set_page_config(
    page_title="CognixOps — Logistics AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    .stApp { background: #FAFAF8 !important; }
    [data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #EBEBEB !important; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span:not([class*="material"]),
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] a { font-family: 'Plus Jakarta Sans', sans-serif !important; color: #3A3A3A !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important; width: 0 !important; height: 0 !important; overflow: hidden !important; position: absolute !important; }
    [data-testid="stSidebarHeader"] { display: none !important; height: 0 !important; min-height: 0 !important; padding: 0 !important; margin: 0 !important; overflow: hidden !important; }
    section[data-testid="stSidebar"] > div > div > div { padding-top: 0.5rem !important; }
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 11px !important; letter-spacing: 0.12em !important;
        text-transform: uppercase !important; font-weight: 600 !important; color: #8A5CF6 !important;
    }
    .block-container { padding-top: 1.5rem !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; max-width: 100% !important; }
    [data-testid="metric-container"] { background: #FFFFFF !important; border: 1px solid #F0EEF8 !important; border-radius: 14px !important; padding: 18px 20px !important; box-shadow: 0 1px 4px rgba(138,92,246,0.06) !important; }
    [data-testid="stMetricLabel"] { font-size: 11px !important; color: #AAAAAA !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; font-family: 'DM Mono', monospace !important; }
    [data-testid="stMetricValue"] { font-size: 24px !important; color: #1A1A2E !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 800 !important; letter-spacing: -0.02em !important; }
    [data-testid="stMetricDelta"] { font-size: 11px !important; font-family: 'DM Mono', monospace !important; }
    .stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1.5px solid #F0EEF8 !important; gap: 0 !important; }
    .stTabs [data-baseweb="tab"] { font-size: 12px !important; font-weight: 600 !important; color: #BBBBBB !important; letter-spacing: 0.04em !important; padding: 10px 22px !important; border-bottom: 2px solid transparent !important; background: transparent !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }
    .stTabs [aria-selected="true"] { color: #8A5CF6 !important; border-bottom: 2.5px solid #8A5CF6 !important; }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }
    .stButton > button { background: linear-gradient(135deg, #8A5CF6 0%, #EC4899 100%) !important; color: #FFFFFF !important; border: none !important; border-radius: 10px !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important; font-size: 13px !important; letter-spacing: 0.03em !important; padding: 11px 20px !important; }
    .stButton > button:hover { opacity: 0.9 !important; }
    .stAlert { border-radius: 10px !important; border: 1px solid !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 13px !important; }
    .stSuccess { background: #F0FDF4 !important; border-color: #86EFAC !important; color: #166534 !important; }
    .stWarning { background: #FFFBEB !important; border-color: #FCD34D !important; color: #92400E !important; }
    .stError   { background: #FFF1F2 !important; border-color: #FDA4AF !important; color: #9F1239 !important; }
    .stInfo    { background: #EFF6FF !important; border-color: #93C5FD !important; color: #1E40AF !important; }
    hr { border-color: #F0EEF8 !important; margin: 1.2rem 0 !important; }
    .streamlit-expanderHeader { background: #FAFAF8 !important; border: 1px solid #EBEBEB !important; border-radius: 10px !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 13px !important; color: #555555 !important; }
    .stSelectbox > div > div { background: #FFFFFF !important; border: 1px solid #EBEBEB !important; border-radius: 10px !important; color: #3A3A3A !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 13px !important; }
    .stCaption { color: #AAAAAA !important; font-size: 11px !important; font-family: 'DM Mono', monospace !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 { font-family: 'Plus Jakarta Sans', sans-serif !important; color: #1A1A2E !important; letter-spacing: -0.02em !important; }
    .stMarkdown p, .stMarkdown li { font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 13px !important; color: #666666 !important; }
    code { background: #F0EEF8 !important; color: #8A5CF6 !important; padding: 2px 6px !important; border-radius: 5px !important; font-size: 11px !important; font-family: 'DM Mono', monospace !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

from config import APP_TITLE, SKUS, DISRUPTION_OPTIONS
from components.scenario_controls import render_sidebar, render_playbook
from components.kpi_cards import render_kpi_cards, render_kpi_status_badge
from components.charts import (
    render_forecast_chart, render_multi_sku_forecast,
    render_baseline_comparison_chart, render_cost_co2_chart,
    render_kpi_before_after, render_optimization_method_badge,
)
from components.map_view import render_route_map
from components.coordination import render_coordination_hub
from services.api import (
    get_kpis, get_forecast, get_all_forecasts,
    get_optimization, get_simulation, get_anomalies,
)
from utils.helpers import section_header, empty_state

controls       = render_sidebar()
disruption     = controls["disruption"]
sku            = controls["sku"]
horizon        = controls["horizon"]
show_all_skus  = controls["show_all_skus"]
show_anomalies = controls["show_anomalies"]
sensitivity    = controls["sensitivity"]
run_clicked    = controls["run"]

if "results" not in st.session_state:
    st.session_state.results = {}

if run_clicked:
    with st.spinner("Running analysis..."):
        st.session_state.results = {
            "kpis":          get_kpis(),
            "forecast":      get_forecast(sku, horizon),
            "all_forecasts": get_all_forecasts(SKUS, horizon) if show_all_skus else [],
            "optimization":  get_optimization(disruption),
            "simulation":    get_simulation(disruption) if disruption != "none" else None,
            "anomalies":     get_anomalies(sku, sensitivity) if show_anomalies else None,
        }

results = st.session_state.results

st.markdown("""
<div style="display:flex;align-items:flex-start;justify-content:space-between;
            padding-bottom:1.4rem;border-bottom:1.5px solid #F0EEF8;margin-bottom:1.6rem;">
  <div>
    <div style="display:inline-flex;align-items:center;gap:8px;background:#F5F0FF;
                border-radius:20px;padding:4px 12px;margin-bottom:10px;">
      <span style="width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#8A5CF6,#EC4899);display:inline-block;"></span>
      <span style="font-size:11px;font-weight:600;color:#8A5CF6;letter-spacing:0.08em;text-transform:uppercase;">Supply Chain Intelligence</span>
    </div>
    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:36px;font-weight:800;
                color:#1A1A2E;letter-spacing:-0.03em;line-height:1;margin-bottom:12px;">
      CognixOps
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;">
      <span style="font-size:11px;background:#F5F0FF;color:#8A5CF6;border-radius:6px;padding:3px 10px;font-weight:600;">LP</span>
      <span style="font-size:11px;background:#F5F0FF;color:#8A5CF6;border-radius:6px;padding:3px 10px;font-weight:600;">MIP</span>
      <span style="font-size:11px;background:#F5F0FF;color:#8A5CF6;border-radius:6px;padding:3px 10px;font-weight:600;">Network Flow</span>
      <span style="font-size:11px;background:#FFF0F9;color:#EC4899;border-radius:6px;padding:3px 10px;font-weight:600;">Prophet</span>
      <span style="font-size:11px;background:#FFF0F9;color:#EC4899;border-radius:6px;padding:3px 10px;font-weight:600;">XGBoost</span>
      <span style="font-size:11px;background:#E1F5EE;color:#0F6E56;border-radius:6px;padding:3px 10px;font-weight:600;">Coordination</span>
      <span style="font-size:11px;background:#EEEDFE;color:#534AB7;border-radius:6px;padding:3px 10px;font-weight:600;">AI Chat</span>
      <span style="font-size:11px;color:#CCCCCC;padding:3px 4px;">v3.0</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if disruption != "none":
    st.markdown(
        f"""<div style="background:#FFF1F2;border:1px solid #FDA4AF;border-left:4px solid #F43F5E;
            border-radius:10px;padding:10px 16px;margin-bottom:1rem;
            font-size:12px;color:#9F1239;font-weight:600;font-family:'Plus Jakarta Sans',sans-serif;">
            Active scenario — {DISRUPTION_OPTIONS[disruption]}
        </div>""",
        unsafe_allow_html=True,
    )

if results.get("kpis"):
    render_kpi_status_badge(results["kpis"])

st.markdown("""
<div style="font-family:'DM Mono',monospace;font-size:10px;color:#CCCCCC;
            letter-spacing:0.15em;text-transform:uppercase;margin:1rem 0 0.75rem;">
  / Key Performance Indicators
</div>
""", unsafe_allow_html=True)

if results.get("kpis"):
    baseline_kpis = results["simulation"].get("kpi_before") if results.get("simulation") else None
    render_kpi_cards(results["kpis"], comparison=baseline_kpis)
else:
    empty_state("Click <strong>Run Analysis</strong> in the sidebar to load KPIs.")

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
st.divider()

(tab_forecast, tab_routing, tab_scenario,
 tab_validation, tab_anomaly,
 tab_coordination) = st.tabs([
    "Demand Forecast",
    "Route Optimization",
    "Disruption Scenario",
    "Validation Report",
    "Anomaly Detection",
    "Coordination Hub",
])

with tab_forecast:
    section_header("Demand Forecast",
        f"Prophet Fourier decomp + XGBoost residual correction · {horizon}-day horizon")
    if results.get("forecast") or results.get("all_forecasts"):
        if show_all_skus and results.get("all_forecasts"):
            render_multi_sku_forecast(results["all_forecasts"])
        else:
            render_forecast_chart(
                results.get("forecast"),
                anomaly_data=results.get("anomalies") if show_anomalies else None,
            )
        fc = results.get("forecast", {})
        if fc.get("safety_stock"):
            col1, col2 = st.columns(2)
            col1.info(f"Safety stock: {fc['safety_stock']:.0f} units  (z=1.645, LT=7 days)")
            col2.info(f"Reorder point: {fc['reorder_point']:.0f} units")
    else:
        empty_state("Run analysis to generate demand forecasts.")

with tab_routing:
    section_header("Route Optimization",
        "LP allocation · MIP carrier selection · Network Flow min-cost routing")
    if results.get("optimization"):
        opt = results["optimization"]
        render_optimization_method_badge(opt)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("LP Optimal Cost",   f"${opt.get('total_cost',0):,.0f}")
        m2.metric("Total CO₂",         f"{opt.get('total_co2',0):,.0f} kg")
        m3.metric("Network Flow Cost", f"${opt.get('network_flow_cost',0):,.0f}")
        m4.metric("Network Flow CO₂",  f"{opt.get('network_flow_co2',0):,.0f} kg")
        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        section_header("Route Map", "")
        render_route_map(opt, disruption_active=(disruption != "none"))
        section_header("Cost vs CO₂ by Route", "LP % allocation shown inside bars")
        render_cost_co2_chart(opt)
    else:
        empty_state("Run analysis to compute optimized routes.")

with tab_scenario:
    section_header("Disruption Scenario Analysis", "Impact against real CSV KPI baseline")
    if disruption == "none":
        st.info("No disruption selected. Choose one from the sidebar and run analysis.")
    elif results.get("simulation"):
        render_kpi_before_after(results["simulation"])
        st.divider()
        render_playbook(results["simulation"])
    else:
        empty_state("Select a disruption type and run analysis.")

with tab_validation:
    section_header("Validation Report",
        "Prophet+XGBoost ensemble vs reorder-point baseline")
    if results.get("forecast"):
        fc = results["forecast"]
        col_a, col_b, col_c = st.columns(3)
        model_mae    = fc.get("model_mae", 0)
        baseline_mae = fc.get("baseline_mae", 0)
        improvement  = ((baseline_mae - model_mae) / max(baseline_mae, 1)) * 100
        col_a.metric("Ensemble MAE", f"{model_mae:.2f} units",
                     delta=f"{improvement:.1f}% better", delta_color="normal")
        col_b.metric("Baseline MAE", f"{baseline_mae:.2f} units")
        col_c.metric("Fill Rate", f"{fc.get('model_fill_rate',0):.1f}%",
                     delta=f"{fc.get('model_fill_rate',0)-fc.get('baseline_fill_rate',0):+.1f}pp",
                     delta_color="normal")
        render_baseline_comparison_chart(fc)
        with st.expander("Methodology notes"):
            st.markdown("""
**Stage 1** — Prophet-style decomposition: piecewise trend + Fourier seasonality + 90% CI

**Stage 2** — XGBoost residual correction: GradientBoostingRegressor on lag features

**Baseline** — Reorder-point model: `avg × LT + z × σ × √LT`
            """)
    else:
        empty_state("Run analysis to generate the validation report.")

with tab_anomaly:
    section_header("Anomaly Detection", "Z-score analysis on historical demand")
    if results.get("anomalies"):
        anom = results["anomalies"]
        anomaly_list = anom.get("anomalies", [])
        col1, col2, col3 = st.columns(3)
        col1.metric("Anomalies Detected",   len(anomaly_list))
        col2.metric("Baseline Mean Demand", f"{anom.get('baseline_mean',0):.0f} units")
        col3.metric("Baseline Std Dev",     f"{anom.get('baseline_std',0):.0f} units")
        if anomaly_list:
            st.markdown("""
<div style="font-family:'DM Mono',monospace;font-size:10px;color:#CCCCCC;
            letter-spacing:0.15em;text-transform:uppercase;margin:1rem 0 0.75rem;">
  / Flagged Anomalies
</div>""", unsafe_allow_html=True)
            for a in anomaly_list:
                severity_map = {
                    "low":    {"bg":"#F5F0FF","border":"#C4B5FD","text":"#6D28D9","label":"LOW"},
                    "medium": {"bg":"#FFF7ED","border":"#FCD34D","text":"#B45309","label":"MEDIUM"},
                    "high":   {"bg":"#FFF1F2","border":"#FDA4AF","text":"#BE123C","label":"HIGH"},
                }
                s = severity_map.get(a["severity"], severity_map["medium"])
                st.markdown(
                    f"""<div style="background:{s['bg']};border:1px solid {s['border']};
                        border-left:4px solid {s['border']};border-radius:10px;
                        padding:12px 16px;margin-bottom:8px;
                        font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;">
                        <div style="display:flex;gap:12px;align-items:center;margin-bottom:4px;">
                            <span style="font-weight:700;color:#1A1A2E;">{a['date']}</span>
                            <span style="font-size:10px;background:{s['border']};color:{s['text']};
                                  padding:2px 8px;border-radius:5px;font-weight:600;">{s['label']}</span>
                            <span style="color:#888;font-size:12px;font-family:'DM Mono',monospace;">
                                demand: {a['demand']:.0f} &nbsp; z: {a['z_score']:+.2f}</span>
                        </div>
                        <div style="color:#888;font-size:12px;">{a['explanation']}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.success(f"No anomalies at z ≥ {sensitivity}σ threshold.")
        st.caption("Anomalies also appear as markers on the Demand Forecast chart.")
    elif show_anomalies:
        empty_state("Run analysis to detect anomalies.")
    else:
        st.info("Enable Overlay anomaly markers in the sidebar and run analysis.")

with tab_coordination:
    render_coordination_hub(results)