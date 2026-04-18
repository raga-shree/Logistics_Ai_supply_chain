"""
Coordination Hub Component — CognixOps v3
Renders the multi-tier Supplier → Factory → Customer network panel.
"""

import streamlit as st
import streamlit.components.v1 as components
from services.api import _get, _post
from utils.helpers import section_header, empty_state

try:
    import folium
    FOLIUM_OK = True
except ImportError:
    FOLIUM_OK = False

# ── Color helpers ──────────────────────────────────────────────────────────────
STATUS_COLORS = {
    "ok":       {"bg": "#E1F5EE", "border": "#1D9E75", "dot": "#1D9E75", "text": "#0F6E56"},
    "warning":  {"bg": "#FFF7ED", "border": "#EF9F27", "dot": "#EF9F27", "text": "#854F0B"},
    "critical": {"bg": "#FFF1F2", "border": "#E24B4A", "dot": "#E24B4A", "text": "#A32D2D"},
}
TIER_COLORS = {
    "supplier": {"pill_bg": "#EEEDFE", "pill_text": "#534AB7", "header": "#534AB7", "tag": "SUP"},
    "factory":  {"pill_bg": "#E1F5EE", "pill_text": "#0F6E56", "header": "#0F6E56", "tag": "FAC"},
    "customer": {"pill_bg": "#FAECE7", "pill_text": "#993C1D", "header": "#993C1D", "tag": "CUST"},
}


def _status_dot(status: str) -> str:
    color = STATUS_COLORS.get(status, STATUS_COLORS["ok"])["dot"]
    return (
        f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
        f'background:{color};margin-right:6px;vertical-align:middle;"></span>'
    )


def _pill(text: str, tier: str) -> str:
    tc = TIER_COLORS[tier]
    return (
        f'<span style="font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px;'
        f'background:{tc["pill_bg"]};color:{tc["pill_text"]};">{text}</span>'
    )


def _node_card_html(node_id: str, name: str, tier: str, status: str,
                    label: str, metric1: str, metric2: str,
                    selected: bool = False) -> str:
    sc  = STATUS_COLORS.get(status, STATUS_COLORS["ok"])
    tc  = TIER_COLORS[tier]
    sel = f"border:2px solid {tc['header']};" if selected else "border:0.5px solid #EBEBEB;"
    return f"""
<div style="background:#FFFFFF;border-radius:12px;padding:12px 14px;
            cursor:pointer;margin-bottom:8px;{sel}">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
    <span style="font-size:13px;font-weight:700;color:#1A1A2E;">{name}</span>
    {_pill(tc['tag'], tier)}
  </div>
  <div style="display:flex;align-items:center;font-size:11px;color:#555;margin-bottom:4px;">
    {_status_dot(status)}{label}
  </div>
  <div style="font-size:11px;color:#AAAAAA;">{metric1} · {metric2}</div>
</div>"""


def _flow_badge(label: str, tier: str) -> str:
    tc = TIER_COLORS[tier]
    return (
        f'<span style="font-size:11px;padding:2px 8px;border-radius:6px;'
        f'background:{tc["pill_bg"]};color:{tc["pill_text"]};font-weight:600;">{label}</span>'
    )


def _arrow_html() -> str:
    return '<span style="color:#CCCCCC;font-size:14px;padding:0 4px;">→</span>'


def render_coordination_hub(results: dict):
    """Main entry point — renders the full coordination hub tab."""

    # Fetch network data
    with st.spinner("Loading coordination network..."):
        network = _get("/coordination/network")

    if not network:
        empty_state("Could not load coordination data — is the backend running?")
        return

    suppliers = network.get("suppliers", {})
    factories = network.get("factories", {})
    customers = network.get("customers", {})
    flows     = network.get("order_flows", [])

    # ── Node grid ──────────────────────────────────────────────────────────────
    section_header("Supply chain network", "Live status across all tiers — click a node to inspect")

    col_s, col_f, col_c = st.columns(3)

    # Supplier column header
    with col_s:
        st.markdown(
            '<p style="font-size:11px;font-weight:600;color:#534AB7;letter-spacing:.05em;'
            'text-transform:uppercase;margin-bottom:8px;">Suppliers</p>',
            unsafe_allow_html=True,
        )

    with col_f:
        st.markdown(
            '<p style="font-size:11px;font-weight:600;color:#0F6E56;letter-spacing:.05em;'
            'text-transform:uppercase;margin-bottom:8px;">Factories</p>',
            unsafe_allow_html=True,
        )

    with col_c:
        st.markdown(
            '<p style="font-size:11px;font-weight:600;color:#993C1D;letter-spacing:.05em;'
            'text-transform:uppercase;margin-bottom:8px;">Customers</p>',
            unsafe_allow_html=True,
        )

    # Track selected node
    if "coord_selected" not in st.session_state:
        st.session_state.coord_selected = list(suppliers.keys())[0] if suppliers else None

    # Render supplier cards
    with col_s:
        for sid, s in suppliers.items():
            selected = st.session_state.coord_selected == sid
            card_html = _node_card_html(
                sid, s["name"], "supplier", s.get("status", "ok"),
                s.get("label", ""), f"Stock: {s.get('stock_units', 0):,} units",
                f"Lead: {s.get('lead_time_days', '?')}d", selected,
            )
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"Select", key=f"btn_{sid}", use_container_width=True):
                st.session_state.coord_selected = sid
                st.rerun()

    with col_f:
        for fid, f in factories.items():
            selected = st.session_state.coord_selected == fid
            util_pct = round(f.get("utilization", 0) * 100)
            card_html = _node_card_html(
                fid, f["name"], "factory", f.get("status", "ok"),
                f.get("label", ""), f"Output: {f.get('output_per_day', 0)} u/day",
                f"Queue: {f.get('queue_days', '?')}d", selected,
            )
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"Select", key=f"btn_{fid}", use_container_width=True):
                st.session_state.coord_selected = fid
                st.rerun()

    with col_c:
        for cid, c in customers.items():
            selected = st.session_state.coord_selected == cid
            card_html = _node_card_html(
                cid, c["name"], "customer", c.get("status", "ok"),
                c.get("label", ""), f"Need: {c.get('units_needed', 0):,} units",
                f"ETA: {c.get('eta_days', '?')}d", selected,
            )
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"Select", key=f"btn_{cid}", use_container_width=True):
                st.session_state.coord_selected = cid
                st.rerun()

    st.divider()

    # ── Detail panel + feed ────────────────────────────────────────────────────
    detail_col, feed_col = st.columns([1.1, 1])

    selected_id = st.session_state.coord_selected

    with detail_col:
        if selected_id:
            _render_node_detail(selected_id, suppliers, factories, customers, flows, results)
        else:
            empty_state("Click a node above to inspect it.")

    with feed_col:
        _render_feed()

    st.divider()

    # ── Coordination map ───────────────────────────────────────────────────────
    section_header("Coordination map", "All nodes and active order flows")
    _render_coord_map(suppliers, factories, customers, flows)


def _render_node_detail(node_id: str, suppliers, factories, customers, flows, results):
    """Render the detail panel for the selected node."""

    all_nodes = {**suppliers, **factories, **customers}
    node      = all_nodes.get(node_id, {})
    if not node:
        return

    # Determine tier
    tier = ("supplier" if node_id in suppliers
            else "factory" if node_id in factories
            else "customer")
    tc  = TIER_COLORS[tier]
    sc  = STATUS_COLORS.get(node.get("status", "ok"), STATUS_COLORS["ok"])

    st.markdown(
        f'<p style="font-size:10px;font-weight:600;letter-spacing:.1em;'
        f'text-transform:uppercase;color:#AAAAAA;margin-bottom:4px;">Selected node</p>'
        f'<p style="font-size:20px;font-weight:800;color:#1A1A2E;'
        f'letter-spacing:-0.02em;margin:0 0 4px;">{node["name"]}</p>'
        f'<p style="font-size:12px;color:#888;">{node.get("location","")}</p>',
        unsafe_allow_html=True,
    )

    # Status badge
    status = node.get("status", "ok")
    label  = node.get("label", "")
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:6px;'
        f'background:{sc["bg"]};border:1px solid {sc["border"]};'
        f'border-radius:8px;padding:4px 12px;margin-bottom:12px;">'
        f'{_status_dot(status)}'
        f'<span style="font-size:12px;font-weight:600;color:{sc["text"]};">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Key metrics
    if tier == "supplier":
        m1, m2 = st.columns(2)
        m1.metric("Stock on hand",  f"{node.get('stock_units', 0):,} units")
        m2.metric("Lead time",      f"{node.get('lead_time_days', '?')} days")
        m3, m4 = st.columns(2)
        m3.metric("Capacity",       f"{node.get('capacity_units', 0):,} units")
        m4.metric("Contact",        node.get("contact", "—"))
    elif tier == "factory":
        m1, m2 = st.columns(2)
        m1.metric("Output / day",   f"{node.get('output_per_day', 0)} units")
        m2.metric("Utilization",    f"{round(node.get('utilization', 0) * 100)}%")
        m3, m4 = st.columns(2)
        m3.metric("Queue",          f"{node.get('queue_days', '?')} days")
        m4.metric("Capacity",       f"{node.get('capacity_units', 0):,} units")
    else:
        m1, m2 = st.columns(2)
        m1.metric("Units needed",   f"{node.get('units_needed', 0):,}")
        m2.metric("ETA",            f"{node.get('eta_days', '?')} days")
        m3, m4 = st.columns(2)
        m3.metric("Monthly contract", f"{node.get('contract_units_month', 0):,}")
        m4.metric("Priority",       node.get("priority", "—").title())

    # Active order flows through this node
    node_flows = [f for f in flows if (
        f["supplier"] == node_id or
        f["factory"]  == node_id or
        f["customer"] == node_id
    )]

    if node_flows:
        st.markdown(
            '<p style="font-size:10px;font-weight:600;letter-spacing:.1em;'
            'text-transform:uppercase;color:#AAAAAA;margin:12px 0 6px;">Active order flows</p>',
            unsafe_allow_html=True,
        )
        STATUS_FLOW_COLOR = {
            "in_transit": "#3B82F6", "at_risk": "#E24B4A",
            "delayed":    "#F97316", "delivered": "#1D9E75",
            "confirmed":  "#8A5CF6",
        }
        for fl in node_flows:
            fstatus = fl.get("status", "confirmed")
            fcolor  = STATUS_FLOW_COLOR.get(fstatus, "#888")

            # Look up display names
            sup_name  = suppliers.get(fl["supplier"], {}).get("name", fl["supplier"])
            fac_name  = factories.get(fl["factory"],  {}).get("name", fl["factory"])
            cust_name = customers.get(fl["customer"], {}).get("name", fl["customer"])

            flow_html = (
                f'<div style="display:flex;align-items:center;gap:4px;'
                f'padding:7px 10px;margin-bottom:6px;border-radius:8px;'
                f'background:#FAFAF8;border:0.5px solid #EBEBEB;">'
                f'{_flow_badge(sup_name[:10], "supplier")}'
                f'{_arrow_html()}'
                f'{_flow_badge(fac_name[:8], "factory")}'
                f'{_arrow_html()}'
                f'{_flow_badge(cust_name[:10], "customer")}'
                f'<span style="margin-left:auto;font-size:10px;font-weight:600;'
                f'color:{fcolor};text-transform:uppercase;">{fstatus.replace("_"," ")}</span>'
                f'<span style="font-size:10px;color:#AAAAAA;margin-left:8px;">'
                f'{fl["units"]:,} u</span>'
                f'</div>'
            )
            st.markdown(flow_html, unsafe_allow_html=True)

    # Quick action buttons
    st.markdown(
        '<p style="font-size:10px;font-weight:600;letter-spacing:.1em;'
        'text-transform:uppercase;color:#AAAAAA;margin:12px 0 6px;">Quick actions</p>',
        unsafe_allow_html=True,
    )
    a1, a2, a3 = st.columns(3)
    node_name = node.get("name", node_id)
    if a1.button("Forecast demand", key=f"qa_forecast_{node_id}", use_container_width=True):
        st.session_state.chatbot_prefill = f"What is the demand forecast for {node_name}?"
    if a2.button("Simulate delay", key=f"qa_sim_{node_id}", use_container_width=True):
        st.session_state.chatbot_prefill = f"Simulate a 7-day delay affecting {node_name}. What is the impact?"
    if a3.button("Risk report", key=f"qa_risk_{node_id}", use_container_width=True):
        st.session_state.chatbot_prefill = f"Give me a risk report for {node_name} based on current KPIs."


def _render_feed():
    """Render the live coordination event feed."""
    st.markdown(
        '<p style="font-size:10px;font-weight:600;letter-spacing:.1em;'
        'text-transform:uppercase;color:#AAAAAA;margin-bottom:10px;">Live coordination feed</p>',
        unsafe_allow_html=True,
    )

    feed_data = _get("/coordination/feed")
    events    = (feed_data or {}).get("events", [])

    if not events:
        empty_state("No events in feed.")
        return

    SEV_COLORS = {
        "critical": {"dot": "#E24B4A", "bg": "#FFF1F2"},
        "warning":  {"dot": "#EF9F27", "bg": "#FFFBEB"},
        "ok":       {"dot": "#1D9E75", "bg": "#F0FDF4"},
    }

    for ev in events:
        sev = ev.get("severity", "ok")
        sc  = SEV_COLORS.get(sev, SEV_COLORS["ok"])
        mins = ev.get("minutes_ago", 0)
        time_str = f"{mins} min ago" if mins < 60 else f"{mins // 60} hr ago"

        st.markdown(
            f'<div style="padding:10px 0;border-bottom:0.5px solid #F0EEF8;'
            f'display:flex;gap:10px;align-items:flex-start;">'
            f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
            f'background:{sc["dot"]};margin-top:4px;flex-shrink:0;"></span>'
            f'<div style="flex:1;">'
            f'<div style="font-size:12px;font-weight:700;color:#1A1A2E;margin-bottom:2px;">'
            f'{ev["title"]}</div>'
            f'<div style="font-size:11px;color:#666;">{ev["body"]}</div>'
            f'<div style="font-size:10px;color:#AAAAAA;margin-top:3px;">{time_str}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


def _render_coord_map(suppliers, factories, customers, flows):
    """Render a Folium map with all network nodes and order flow lines."""
    if not FOLIUM_OK:
        st.warning("Folium not installed — run `pip install folium`")
        return

    m = folium.Map(location=[51.5, 10.0], zoom_start=5,
                   tiles="CartoDB positron", control_scale=True)

    STATUS_MAP_COLOR = {"ok": "green", "warning": "orange", "critical": "red"}
    TIER_ICON = {
        "supplier": ("industry",      "#534AB7"),
        "factory":  ("cog",           "#1D9E75"),
        "customer": ("shopping-cart", "#D85A30"),
    }

    all_nodes = {
        **{k: {**v, "tier": "supplier"} for k, v in suppliers.items()},
        **{k: {**v, "tier": "factory"}  for k, v in factories.items()},
        **{k: {**v, "tier": "customer"} for k, v in customers.items()},
    }

    for nid, n in all_nodes.items():
        tier       = n["tier"]
        icon_name, icon_color = TIER_ICON[tier]
        map_color  = STATUS_MAP_COLOR.get(n.get("status", "ok"), "blue")
        tooltip    = f"<b>{n['name']}</b><br>{n.get('label', '')}<br>{n.get('location', '')}"
        folium.Marker(
            location=[n["lat"], n["lon"]],
            tooltip=tooltip,
            icon=folium.Icon(color=map_color, icon_color=icon_color,
                             icon=icon_name, prefix="fa"),
        ).add_to(m)

    FLOW_COLOR = {
        "in_transit": "#3B82F6", "at_risk": "#E24B4A",
        "delayed":    "#F97316", "delivered": "#1D9E75",
        "confirmed":  "#8A5CF6",
    }

    for fl in flows:
        sup  = suppliers.get(fl["supplier"], {})
        fac  = factories.get(fl["factory"],  {})
        cust = customers.get(fl["customer"], {})
        fcolor = FLOW_COLOR.get(fl.get("status", "confirmed"), "#888")
        dashed = "5 5" if fl.get("status") in ("at_risk", "delayed") else None

        if sup and fac:
            folium.PolyLine(
                locations=[[sup["lat"], sup["lon"]], [fac["lat"], fac["lon"]]],
                color=fcolor, weight=3, opacity=0.8,
                tooltip=f"{fl['id']} · {fl['status'].replace('_',' ')} · {fl['units']:,} units",
                dash_array=dashed,
            ).add_to(m)
        if fac and cust:
            folium.PolyLine(
                locations=[[fac["lat"], fac["lon"]], [cust["lat"], cust["lon"]]],
                color=fcolor, weight=3, opacity=0.8,
                tooltip=f"{fl['id']} · {fl['status'].replace('_',' ')} · {fl['units']:,} units",
                dash_array=dashed,
            ).add_to(m)

    # Legend
    legend = """
    <div style="position:fixed;bottom:20px;left:20px;z-index:1000;
                background:white;padding:10px 14px;border-radius:8px;
                border:1px solid #ccc;font-size:12px;line-height:2.0">
        <b>Order flow</b><br>
        <span style="color:#8A5CF6">━━</span> Confirmed<br>
        <span style="color:#3B82F6">━━</span> In transit<br>
        <span style="color:#1D9E75">━━</span> Delivered<br>
        <span style="color:#F97316">┅┅</span> Delayed<br>
        <span style="color:#E24B4A">┅┅</span> At risk
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))

    components.html(m._repr_html_(), height=440, scrolling=False)
