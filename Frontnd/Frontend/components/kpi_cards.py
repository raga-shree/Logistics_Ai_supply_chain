import streamlit as st

# VIBGYOR KPI accent colors — each metric gets its own spectrum color
KPI_COLORS = {
    "service_level":      {"light":"#F5F0FF","accent":"#8A5CF6","text":"#6D28D9"},  # Violet
    "total_cost":         {"light":"#EFF6FF","accent":"#3B82F6","text":"#1D4ED8"},  # Blue
    "co2_kg":             {"light":"#F0FDF4","accent":"#22C55E","text":"#15803D"},  # Green
    "on_time_delivery":   {"light":"#FFFBEB","accent":"#F59E0B","text":"#B45309"},  # Yellow/Amber
    "inventory_turnover": {"light":"#FFF1F2","accent":"#F43F5E","text":"#BE123C"},  # Red
}

def render_kpi_cards(kpi_data: dict, comparison: dict = None):
    if not kpi_data:
        st.warning("KPI data unavailable — check backend connection.")
        return

    metrics = [
        {"label":"Service Level",      "key":"service_level",      "format":"{:.1f}%",   "good":"up"},
        {"label":"Total Cost",         "key":"total_cost",         "format":"${:,.0f}",  "good":"down"},
        {"label":"CO₂ Emissions",      "key":"co2_kg",             "format":"{:,.0f} kg","good":"down"},
        {"label":"On-Time Delivery",   "key":"on_time_delivery",   "format":"{:.1f}%",   "good":"up"},
        {"label":"Inventory Turnover", "key":"inventory_turnover", "format":"{:.2f}x",   "good":"up"},
    ]

    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        value = kpi_data.get(m["key"])
        if value is None:
            col.metric(label=m["label"], value="N/A")
            continue
        try:
            display = m["format"].format(value)
        except Exception:
            display = str(value)

        delta_str   = None
        delta_color = "normal"
        if comparison:
            baseline = comparison.get(m["key"])
            if baseline and baseline != 0:
                delta = value - baseline
                pct   = (delta / baseline) * 100
                delta_str   = f"{pct:+.1f}%"
                delta_color = ("normal" if delta >= 0 else "inverse") if m["good"] == "up" else ("inverse" if delta >= 0 else "normal")

        col.metric(label=m["label"], value=display, delta=delta_str, delta_color=delta_color)


def render_kpi_status_badge(kpi_data: dict):
    if not kpi_data:
        return
    sl  = kpi_data.get("service_level", 100)
    otd = kpi_data.get("on_time_delivery", 100)

    if sl >= 95 and otd >= 92:
        st.markdown("""
<div style="display:inline-flex;align-items:center;gap:8px;background:#F0FDF4;
            border:1px solid #86EFAC;border-radius:20px;padding:6px 14px;margin-bottom:1rem;">
  <span style="width:7px;height:7px;border-radius:50%;background:#22C55E;display:inline-block;"></span>
  <span style="font-size:12px;font-weight:600;color:#15803D;font-family:'Plus Jakarta Sans',sans-serif;">
    System healthy — all KPIs on target
  </span>
</div>""", unsafe_allow_html=True)
    elif sl >= 88 or otd >= 80:
        st.markdown("""
<div style="display:inline-flex;align-items:center;gap:8px;background:#FFFBEB;
            border:1px solid #FCD34D;border-radius:20px;padding:6px 14px;margin-bottom:1rem;">
  <span style="width:7px;height:7px;border-radius:50%;background:#F59E0B;display:inline-block;"></span>
  <span style="font-size:12px;font-weight:600;color:#B45309;font-family:'Plus Jakarta Sans',sans-serif;">
    Warning — one or more KPIs below target
  </span>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="display:inline-flex;align-items:center;gap:8px;background:#FFF1F2;
            border:1px solid #FDA4AF;border-radius:20px;padding:6px 14px;margin-bottom:1rem;">
  <span style="width:7px;height:7px;border-radius:50%;background:#F43F5E;display:inline-block;"></span>
  <span style="font-size:12px;font-weight:600;color:#BE123C;font-family:'Plus Jakarta Sans',sans-serif;">
    Critical — immediate action required
  </span>
</div>""", unsafe_allow_html=True)
