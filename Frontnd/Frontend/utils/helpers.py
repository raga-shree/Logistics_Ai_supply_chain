import streamlit as st

def format_currency(v): return f"${v:,.2f}" if v is not None else "N/A"
def format_pct(v):      return f"{v:.1f}%"  if v is not None else "N/A"
def format_kg(v):       return f"{v:,.0f} kg" if v is not None else "N/A"

def delta_badge(current, baseline, good_direction="up"):
    if baseline is None or baseline == 0: return ""
    pct = ((current - baseline) / baseline) * 100
    return f"{'▲' if pct>=0 else '▼'} {abs(pct):.1f}%"

def section_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""<div style="margin-bottom:1rem;">
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:20px;
                        font-weight:800;color:#1A1A2E;letter-spacing:-0.02em;margin-bottom:3px;">
                {title}
            </div>
            {"" if not subtitle else f'<div style="font-family:DM Mono,monospace;font-size:11px;color:#AAAAAA;">{subtitle}</div>'}
        </div>""",
        unsafe_allow_html=True,
    )

def loading_spinner(message="Fetching from backend..."):
    return st.spinner(message)

def empty_state(message="No data yet — run analysis from the sidebar."):
    st.markdown(
        f"""<div style="text-align:center;padding:56px 24px;color:#CCCCCC;
                font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;
                border:1.5px dashed #EBEBEB;border-radius:16px;margin:1rem 0;
                background:#FAFAF8;">
            {message}
        </div>""",
        unsafe_allow_html=True,
    )
