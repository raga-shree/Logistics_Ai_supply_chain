"""
Charts — CognixOps Frontend v2.1
VIBGYOR demand-intensity color system:
  Low demand  → Violet (#C4B5FD light → #8A5CF6)
  Medium-low  → Blue   (#93C5FD light → #3B82F6)
  Medium      → Green  (#86EFAC light → #22C55E)
  Medium-high → Yellow (#FCD34D light → #F59E0B)
  High        → Orange (#FDBA74 light → #F97316)
  Very high   → Red    (#FDA4AF light → #F43F5E)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from config import CHART_HEIGHT

# VIBGYOR spectrum: lighter = low demand, darker/warmer = high demand
VIBGYOR = {
    "violet": "#8A5CF6",
    "indigo": "#6366F1",
    "blue":   "#3B82F6",
    "green":  "#22C55E",
    "yellow": "#F59E0B",
    "orange": "#F97316",
    "red":    "#F43F5E",
}

VIBGYOR_LIGHT = {
    "violet": "#EDE9FE",
    "indigo": "#E0E7FF",
    "blue":   "#DBEAFE",
    "green":  "#DCFCE7",
    "yellow": "#FEF9C3",
    "orange": "#FFF7ED",
    "red":    "#FFF1F2",
}

def _demand_color(value, vmin, vmax, light=False):
    """Map a demand value to VIBGYOR spectrum. Low→violet, High→red."""
    if vmax == vmin:
        ratio = 0.5
    else:
        ratio = max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))
    spectrum = ["violet","indigo","blue","green","yellow","orange","red"]
    idx = min(int(ratio * len(spectrum)), len(spectrum) - 1)
    return (VIBGYOR_LIGHT if light else VIBGYOR)[spectrum[idx]]

def _demand_colors_for_series(values, light=False):
    vmin, vmax = min(values), max(values)
    return [_demand_color(v, vmin, vmax, light) for v in values]

def _title_dict(text):
    """Return a Plotly title dict with consistent font styling."""
    return dict(
        text=text,
        font=dict(family="Plus Jakarta Sans, sans-serif", size=14, color="#1A1A2E"),
    )

# Note: 'title' intentionally excluded — pass it per chart via _title_dict()
_LAYOUT_BASE = dict(
    height=CHART_HEIGHT,
    plot_bgcolor="#FAFAF8",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=16, r=16, t=44, b=16),
    font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#888888"),
    xaxis=dict(gridcolor="#F0EEF8", showline=False, tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#F0EEF8", showline=False, tickfont=dict(size=11)),
    legend=dict(orientation="h", y=-0.2, font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#EBEBEB",
                    font=dict(family="DM Mono, monospace", size=11, color="#1A1A2E")),
)


# ── 1. Demand Forecast ────────────────────────────────────────────────────────
def render_forecast_chart(forecast_data: dict, anomaly_data: dict = None):
    if not forecast_data:
        st.info("No forecast data available.")
        return

    dates    = forecast_data.get("dates", [])
    forecast = forecast_data.get("forecast", [])
    lower    = forecast_data.get("lower", [])
    upper    = forecast_data.get("upper", [])
    sku      = forecast_data.get("sku", "")

    bar_colors = _demand_colors_for_series(forecast) if forecast else []

    fig = go.Figure()

    # Confidence band
    fig.add_trace(go.Scatter(
        x=dates + dates[::-1],
        y=upper + lower[::-1],
        fill="toself",
        fillcolor="rgba(139,92,246,0.08)",
        line=dict(color="rgba(0,0,0,0)"),
        name="90% confidence interval",
        hoverinfo="skip",
    ))

    # Demand bars — VIBGYOR intensity
    fig.add_trace(go.Bar(
        x=dates, y=forecast,
        marker_color=bar_colors,
        marker_line_width=0,
        opacity=0.85,
        name=f"Forecast — {sku}",
        hovertemplate="<b>%{x}</b><br>Demand: %{y:.0f} units<extra></extra>",
    ))

    # Forecast line overlay
    fig.add_trace(go.Scatter(
        x=dates, y=forecast,
        mode="lines",
        line=dict(color="#8A5CF6", width=2, dash="dot"),
        name="Trend line",
        hoverinfo="skip",
    ))

    # Anomaly markers
    if anomaly_data:
        anomalies = anomaly_data.get("anomalies", [])
        if anomalies:
            anom_dates  = [a["date"]   for a in anomalies]
            anom_demand = [a["demand"] for a in anomalies]
            anom_text   = [f"{a['severity'].upper()}: {a['explanation']}" for a in anomalies]
            fig.add_trace(go.Scatter(
                x=anom_dates, y=anom_demand,
                mode="markers",
                marker=dict(color="#F43F5E", size=12, symbol="star",
                            line=dict(color="white", width=1.5)),
                name="Anomaly detected",
                text=anom_text,
                hovertemplate="%{text}<extra></extra>",
            ))

    ss  = forecast_data.get("safety_stock")
    rop = forecast_data.get("reorder_point")
    if rop:
        fig.add_hline(y=rop, line_dash="dot", line_color="#F43F5E", line_width=1.5,
                      annotation_text=f"Reorder point ({rop:.0f})",
                      annotation_font=dict(size=10, color="#F43F5E"),
                      annotation_position="top right")
    if ss:
        fig.add_hline(y=ss, line_dash="dash", line_color="#F59E0B", line_width=1.5,
                      annotation_text=f"Safety stock ({ss:.0f})",
                      annotation_font=dict(size=10, color="#F59E0B"),
                      annotation_position="bottom right")

    # VIBGYOR legend hint
    fig.add_annotation(
        xref="paper", yref="paper", x=1.0, y=1.08,
        text="Violet = low demand → Red = high demand",
        showarrow=False,
        font=dict(size=10, color="#AAAAAA", family="DM Mono, monospace"),
        align="right",
    )

    fig.update_layout(
        **_LAYOUT_BASE,
        title=_title_dict(f"Demand Forecast — {sku}"),
        yaxis_title="Units",
        bargap=0.15,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── 2. Multi-SKU Forecast ─────────────────────────────────────────────────────
def render_multi_sku_forecast(all_forecasts: list):
    if not all_forecasts:
        st.info("No forecast data available.")
        return

    sku_colors = [VIBGYOR["violet"], VIBGYOR["blue"], VIBGYOR["green"],
                  VIBGYOR["yellow"], VIBGYOR["red"]]
    fig = go.Figure()
    for i, fd in enumerate(all_forecasts):
        fig.add_trace(go.Scatter(
            x=fd.get("dates", []),
            y=fd.get("forecast", []),
            mode="lines+markers",
            name=fd.get("sku", f"SKU-{i}"),
            line=dict(width=2.5, color=sku_colors[i % len(sku_colors)]),
            marker=dict(size=5),
        ))
    fig.update_layout(
        **_LAYOUT_BASE,
        title=_title_dict("All-SKU Demand Forecast"),
        yaxis_title="Units",
    )
    st.plotly_chart(fig, use_container_width=True)


# ── 3. Validation comparison ──────────────────────────────────────────────────
def render_baseline_comparison_chart(forecast_data: dict):
    if not forecast_data:
        st.info("Validation data unavailable.")
        return
    model_mae    = forecast_data.get("model_mae",          0)
    baseline_mae = forecast_data.get("baseline_mae",       0)
    model_fr     = forecast_data.get("model_fill_rate",    0)
    baseline_fr  = forecast_data.get("baseline_fill_rate", 0)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Prophet+XGBoost",
        x=["Forecast MAE", "Fill Rate (%)"],
        y=[model_mae, model_fr],
        marker_color=VIBGYOR["violet"],
        marker_line_width=0,
        text=[f"{model_mae:.1f}", f"{model_fr:.1f}%"],
        textposition="outside",
        textfont=dict(size=11, color="#6D28D9"),
    ))
    fig.add_trace(go.Bar(
        name="Baseline",
        x=["Forecast MAE", "Fill Rate (%)"],
        y=[baseline_mae, baseline_fr],
        marker_color="#E5E7EB",
        marker_line_width=0,
        text=[f"{baseline_mae:.1f}", f"{baseline_fr:.1f}%"],
        textposition="outside",
        textfont=dict(size=11, color="#888888"),
    ))
    fig.update_layout(
        **_LAYOUT_BASE,
        barmode="group",
        title=_title_dict("AI Ensemble vs Baseline"),
        bargap=0.3,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── 4. Route Cost vs CO₂ ──────────────────────────────────────────────────────
def render_cost_co2_chart(optimization_data: dict):
    if not optimization_data:
        st.info("Optimization data unavailable.")
        return
    routes = optimization_data.get("routes", [])
    if not routes:
        st.info("No routes returned from optimizer.")
        return

    df = pd.DataFrame(routes)
    costs = df["cost"].tolist()
    co2s  = df["co2"].tolist()

    # Color routes by cost intensity (VIBGYOR)
    cost_colors = _demand_colors_for_series(costs)
    co2_colors  = _demand_colors_for_series(co2s)

    lp_fractions = [f"LP: {r.get('lp_fraction',0):.0%}" if r.get('lp_fraction') else "" for r in routes]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Cost (USD)", x=df["name"], y=df["cost"],
        marker_color=cost_colors, marker_line_width=0,
        text=lp_fractions, textposition="inside",
        textfont=dict(size=10), yaxis="y",
    ))
    fig.add_trace(go.Bar(
        name="CO₂ (kg)", x=df["name"], y=df["co2"],
        marker_color=co2_colors, marker_line_width=0,
        yaxis="y2",
    ))
    # Build layout without yaxis key from _LAYOUT_BASE since we override it
    layout = {k: v for k, v in _LAYOUT_BASE.items() if k != "yaxis"}
    fig.update_layout(
        **layout,
        barmode="group",
        title=_title_dict("Route Comparison — Cost vs CO₂"),
        yaxis=dict(title="Cost (USD)", gridcolor="#F0EEF8"),
        yaxis2=dict(title="CO₂ (kg)", overlaying="y", side="right", showgrid=False),
        bargap=0.2,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── 5. Optimization method badge ──────────────────────────────────────────────
def render_optimization_method_badge(optimization_data: dict):
    method  = optimization_data.get("optimization_method", "")
    nf_cost = optimization_data.get("network_flow_cost", 0)
    nf_co2  = optimization_data.get("network_flow_co2",  0)
    if not method:
        return
    st.markdown(
        f"""<div style="background:#F5F0FF;border:1px solid #C4B5FD;border-radius:10px;
                padding:10px 16px;margin-bottom:12px;font-size:12px;
                font-family:'Plus Jakarta Sans',sans-serif;color:#6D28D9;">
            <strong>Engine:</strong> {method} &nbsp;·&nbsp;
            Network flow cost: <strong>${nf_cost:,.0f}</strong> &nbsp;·&nbsp;
            CO₂: <strong>{nf_co2:,.0f} kg</strong>
        </div>""",
        unsafe_allow_html=True,
    )


# ── 6. KPI Before/After disruption ────────────────────────────────────────────
def render_kpi_before_after(simulation_data: dict):
    if not simulation_data:
        return
    before = simulation_data.get("kpi_before", {})
    after  = simulation_data.get("kpi_after",  {})
    kpi_keys   = ["service_level","total_cost","on_time_delivery","co2_kg"]
    kpi_labels = ["Service Level (%)","Total Cost (USD)","On-Time Delivery (%)","CO₂ (kg)"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Before disruption", x=kpi_labels,
        y=[before.get(k,0) for k in kpi_keys],
        marker_color=VIBGYOR["violet"], marker_line_width=0,
        text=[f"{before.get(k,0):,.1f}" for k in kpi_keys],
        textposition="outside", textfont=dict(size=10, color="#6D28D9"),
    ))
    fig.add_trace(go.Bar(
        name="After disruption", x=kpi_labels,
        y=[after.get(k,0) for k in kpi_keys],
        marker_color=VIBGYOR["red"], marker_line_width=0,
        text=[f"{after.get(k,0):,.1f}" for k in kpi_keys],
        textposition="outside", textfont=dict(size=10, color="#BE123C"),
    ))
    fig.update_layout(
        **_LAYOUT_BASE,
        barmode="group",
        title=_title_dict("KPI Shift — Before vs After Disruption"),
        bargap=0.25,
    )
    st.plotly_chart(fig, use_container_width=True)