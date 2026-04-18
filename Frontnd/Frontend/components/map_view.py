import streamlit as st
import streamlit.components.v1 as components
from config import MAP_HEIGHT, NODES

try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


def _route_color(selected: bool, disrupted: bool) -> str:
    if disrupted:
        return "#E24B4A"
    if selected:
        return "#378ADD"
    return "#B4B2A9"


def render_route_map(optimization_data: dict, disruption_active: bool = False):
    """
    Renders an interactive Folium map showing:
    - Warehouse and plant nodes as markers
    - Route edges colored by: selected (blue), disrupted (red), alt (gray)

    optimization_data keys:
        routes: [{ name, from_node, to_node, cost, co2, selected, disrupted }]
    """
    if not FOLIUM_AVAILABLE:
        st.warning(
            "Folium is not installed. Run `pip install folium` in the frontend environment."
        )
        _render_fallback_table(optimization_data)
        return

    if not optimization_data:
        st.info("No routing data — check backend connection.")
        return

    # Build map centered on Europe (covers all demo nodes)
    m = folium.Map(
        location=[50.5, 4.5],
        zoom_start=5,
        tiles="CartoDB positron",
        control_scale=True,
    )

    # Draw node markers
    node_icons = {
        "WH":   ("warehouse",  "#378ADD"),
        "PLT":  ("industry",   "#1D9E75"),
        "CUST": ("shopping-cart", "#D85A30"),
    }

    for node_id, info in NODES.items():
        prefix = node_id.split("-")[0]
        icon_name, color = node_icons.get(prefix, ("circle", "#888"))
        folium.Marker(
            location=[info["lat"], info["lon"]],
            tooltip=f"<b>{info['label']}</b><br>{node_id}",
            icon=folium.Icon(color="white", icon_color=color, icon=icon_name, prefix="fa"),
        ).add_to(m)

    # Draw route edges
    routes = optimization_data.get("routes", [])
    for route in routes:
        from_node = route.get("from_node")
        to_node   = route.get("to_node")
        selected  = route.get("selected", False)
        disrupted = route.get("disrupted", False)

        if from_node not in NODES or to_node not in NODES:
            continue

        color  = _route_color(selected, disrupted)
        weight = 4 if selected else 2
        dash   = "10 5" if disrupted else None

        from_coords = [NODES[from_node]["lat"], NODES[from_node]["lon"]]
        to_coords   = [NODES[to_node]["lat"],   NODES[to_node]["lon"]]

        tooltip_text = (
            f"<b>{route.get('name', '')}</b><br>"
            f"Cost: ${route.get('cost', 0):,.0f}<br>"
            f"CO₂: {route.get('co2', 0):,.0f} kg"
        )
        if disrupted:
            tooltip_text += "<br><span style='color:#E24B4A'>⚠ Disrupted</span>"

        folium.PolyLine(
            locations=[from_coords, to_coords],
            color=color,
            weight=weight,
            opacity=0.85,
            tooltip=folium.Tooltip(tooltip_text),
            dash_array=dash,
        ).add_to(m)

    # Legend
    legend_html = """
    <div style="position:fixed;bottom:20px;left:20px;z-index:1000;
                background:white;padding:10px 14px;border-radius:8px;
                border:1px solid #ccc;font-size:12px;line-height:1.8">
        <b>Route legend</b><br>
        <span style="color:#378ADD">━━</span> Selected route<br>
        <span style="color:#B4B2A9">━━</span> Alternative route<br>
        <span style="color:#E24B4A">┅┅</span> Disrupted
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Render inside Streamlit
    components.html(m._repr_html_(), height=MAP_HEIGHT, scrolling=False)


def _render_fallback_table(optimization_data: dict):
    """Fallback: show routes as a plain table if Folium isn't available."""
    import pandas as pd

    routes = (optimization_data or {}).get("routes", [])
    if not routes:
        return

    df = pd.DataFrame(routes)[["name", "from_node", "to_node", "cost", "co2", "selected"]]
    df.columns = ["Route", "From", "To", "Cost (USD)", "CO₂ (kg)", "Selected"]
    st.dataframe(df, use_container_width=True, hide_index=True)
