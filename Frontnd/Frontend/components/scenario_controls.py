"""Sidebar Controls — CognixOps v2.1 VIBGYOR Edition"""

import streamlit as st
from config import DISRUPTION_OPTIONS, SKUS


def render_sidebar() -> dict:
    # Native Streamlit elements — no custom HTML that gets overlapped by the collapse button
    st.sidebar.markdown("#### 🟣 COGNIXOPS V2.1")
    st.sidebar.markdown("## Controls")
    st.sidebar.divider()


    st.sidebar.divider()
    st.sidebar.markdown("### Disruption Scenario")
    disruption = st.sidebar.selectbox("Active disruption",
        options=list(DISRUPTION_OPTIONS.keys()),
        format_func=lambda k: DISRUPTION_OPTIONS[k], index=0, key="disruption_select")

    st.sidebar.divider()
    st.sidebar.markdown("### Forecast Settings")
    sku = st.sidebar.selectbox("SKU to forecast", options=SKUS, index=0, key="sku_select")
    horizon = st.sidebar.slider("Forecast horizon (days)", 3, 30, 7, 1, key="horizon_slider")
    show_all_skus = st.sidebar.checkbox("Show all SKUs on one chart", value=False, key="all_skus_check")

    st.sidebar.divider()
    st.sidebar.markdown("### Anomaly Detection")
    show_anomalies = st.sidebar.checkbox("Overlay anomaly markers", value=True, key="anomaly_check")
    sensitivity = st.sidebar.select_slider("Z-score sensitivity",
        options=[1.5, 2.0, 2.5, 3.0], value=2.0, key="sensitivity_slider")
    labels = {1.5: "High", 2.0: "Standard", 2.5: "Low", 3.0: "Conservative"}
    st.sidebar.caption(f"Sensitivity: {labels[sensitivity]} (z ≥ {sensitivity}σ)")

    st.sidebar.divider()
    st.sidebar.markdown("### Optimization Priority")
    cost_weight = st.sidebar.slider("Cost priority", 0, 100, 40, key="cost_w")
    co2_weight = 100 - cost_weight
    st.sidebar.caption(f"Cost {cost_weight}%  ·  Speed/CO₂ {co2_weight}%")

    st.sidebar.divider()
    run = st.sidebar.button("Run Analysis", type="primary", use_container_width=True)

    st.sidebar.caption("LP · MIP · Network Flow · Prophet · XGBoost\nZF Hackathon 2025")

    return {"disruption": disruption, "sku": sku, "horizon": horizon, "show_all_skus": show_all_skus,
            "show_anomalies": show_anomalies, "sensitivity": sensitivity,
            "cost_weight": cost_weight, "co2_weight": co2_weight, "run": run}


def render_playbook(simulation_data: dict):
    if not simulation_data:
        return
    actions  = simulation_data.get("recommended_actions", [])
    severity = simulation_data.get("severity", "low")
    risk     = simulation_data.get("risk_score", 0)
    cost_imp = simulation_data.get("cost_impact", 0)
    delay    = simulation_data.get("delay_days", 0)
    svc_drop = simulation_data.get("service_drop", 0)

    sev_cfg = {
        "low":      {"bg":"#F5F0FF","border":"#C4B5FD","text":"#6D28D9","label":"Low impact"},
        "medium":   {"bg":"#FFFBEB","border":"#FCD34D","text":"#B45309","label":"Medium — monitor closely"},
        "high":     {"bg":"#FFF7ED","border":"#FDBA74","text":"#C2410C","label":"High — act within 24h"},
        "critical": {"bg":"#FFF1F2","border":"#FDA4AF","text":"#BE123C","label":"Critical — immediate action"},
    }
    s = sev_cfg.get(severity, sev_cfg["medium"])
    st.markdown(
        f"""<div style="background:{s['bg']};border:1px solid {s['border']};
            border-left:4px solid {s['border']};border-radius:10px;
            padding:10px 16px;margin-bottom:1rem;font-size:12px;
            font-family:'Plus Jakarta Sans',sans-serif;color:{s['text']};font-weight:600;">
            Severity: {s['label']} &nbsp;·&nbsp; Risk score: {risk:.2f}
        </div>""",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Est. Cost Impact",   f"${cost_imp:,.0f}")
    c2.metric("Est. Delay",         f"{delay:.1f} days")
    c3.metric("Service Level Drop", f"{svc_drop:.1f}%")

    if not actions:
        st.info("No specific playbook actions returned.")
        return

    st.markdown("""
<div style="font-family:'DM Mono',monospace;font-size:10px;color:#CCCCCC;
            letter-spacing:0.15em;text-transform:uppercase;margin:1rem 0 0.75rem;">
  / Recommended Playbook
</div>""", unsafe_allow_html=True)

    step_colors = ["#8A5CF6","#6366F1","#3B82F6","#22C55E","#F59E0B","#F97316","#F43F5E"]
    for i, action in enumerate(actions, 1):
        color = step_colors[(i-1) % len(step_colors)]
        st.markdown(
            f"""<div style="display:flex;gap:14px;padding:11px 16px;margin-bottom:8px;
                border-radius:10px;background:#FFFFFF;border:1px solid #F0EEF8;
                font-size:13px;font-family:'Plus Jakarta Sans',sans-serif;">
                <span style="color:{color};font-weight:800;min-width:22px;font-size:14px;">{i:02d}</span>
                <span style="color:#3A3A3A;">{action}</span>
            </div>""",
            unsafe_allow_html=True,
        )