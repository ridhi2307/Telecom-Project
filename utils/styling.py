"""
Styling and Design System for Telecom Analytics Platform.
Theme: Enterprise Navy Blue and White with modern cards, responsive typography,
and accessible color palettes (Blue for primary, Green for positive, Red for churn/alert).
"""

import inspect
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Color Palette Constants
NAVY_PRIMARY = "#0F172A"      # Slate 900
NAVY_SECONDARY = "#1E293B"    # Slate 800
NAVY_SURFACE = "#F8FAFC"      # Slate 50
TEXT_PRIMARY = "#0F172A"
TEXT_MUTED = "#64748B"        # Slate 500
BORDER_COLOR = "#E2E8F0"      # Slate 200

# Semantic Accents
ACCENT_BLUE = "#2563EB"       # Primary Blue (Action/Telecom)
ACCENT_BLUE_LIGHT = "#60A5FA"
ACCENT_GREEN = "#10B981"      # Positive / Retained
ACCENT_RED = "#EF4444"        # Alert / Churn / Porting Surge
ACCENT_AMBER = "#F59E0B"      # Warning / Quality missing
ACCENT_PURPLE = "#8B5CF6"

# Plotly Color Scales
CHURN_COLOR_MAP = {"No": "#10B981", "Yes": "#EF4444"}
PORTING_COLOR_SCALE = ["#93C5FD", "#2563EB", "#1D4ED8"]

# Detect whether this Streamlit version prefers width="stretch" or use_container_width=True
_SUPPORTS_WIDTH = "width" in inspect.signature(st.plotly_chart).parameters


def get_layout_width_kwarg():
    """Return width='stretch' if supported, else use_container_width=True to avoid deprecation warnings."""
    if _SUPPORTS_WIDTH:
        return {"width": "stretch"}
    return {"use_container_width": True}


def render_chart(fig, **kwargs):
    """Renders a Plotly figure with proper width parameter to avoid deprecation warnings."""
    kw = get_layout_width_kwarg()
    kw.update(kwargs)
    st.plotly_chart(fig, **kw)


def render_dataframe(df, **kwargs):
    """Renders a DataFrame with proper width parameter."""
    kw = get_layout_width_kwarg()
    kw.update(kwargs)
    st.dataframe(df, **kw)


def render_button(label, **kwargs):
    """Renders a button with proper width parameter."""
    kw = get_layout_width_kwarg()
    kw.update(kwargs)
    return st.button(label, **kw)


def render_download_button(label, data, **kwargs):
    """Renders a download button with proper width parameter."""
    kw = get_layout_width_kwarg()
    kw.update(kwargs)
    return st.download_button(label, data, **kw)


def apply_custom_css():
    """Inject polished enterprise styling into the Streamlit app."""
    st.markdown(f"""
        <style>
        /* Import Google Font Inter */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* App Background */
        .stApp {{
            background-color: #F8FAFC;
        }}

        /* Top Header Banner */
        .telecom-header {{
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            color: #FFFFFF;
            padding: 1.75rem 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border-left: 6px solid #2563EB;
        }}

        .telecom-header h1 {{
            color: #FFFFFF !important;
            font-size: 1.85rem;
            font-weight: 700;
            margin: 0 0 0.4rem 0;
            letter-spacing: -0.02em;
        }}

        .telecom-header p {{
            color: #94A3B8;
            font-size: 0.95rem;
            margin: 0;
            font-weight: 400;
        }}

        /* KPI Card Styles */
        .kpi-card {{
            background: #FFFFFF;
            padding: 1.25rem 1.5rem;
            border-radius: 10px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease-in-out;
            height: 100%;
        }}

        .kpi-card:hover {{
            box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.08);
            transform: translateY(-2px);
        }}

        .kpi-label {{
            color: #64748B;
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.4rem;
        }}

        .kpi-value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.2;
            margin-bottom: 0.25rem;
        }}

        .kpi-delta {{
            font-size: 0.8rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .delta-positive {{ color: #10B981; }}
        .delta-negative {{ color: #EF4444; }}
        .delta-neutral {{ color: #64748B; }}

        /* Section Headings */
        .section-header {{
            margin-top: 1.75rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #E2E8F0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .section-title {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #0F172A;
            letter-spacing: -0.01em;
        }}

        /* Status Pills */
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }}
        .badge-live {{ background: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; }}
        .badge-local {{ background: #DBEAFE; color: #1D4ED8; border: 1px solid #93C5FD; }}
        .badge-warning {{ background: #FEF3C7; color: #B45309; border: 1px solid #FCD34D; }}
        .badge-danger {{ background: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; }}

        /* Chart Containers */
        .chart-box {{
            background: #FFFFFF;
            padding: 1.25rem;
            border-radius: 10px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
            margin-bottom: 1.25rem;
        }}

        /* Clean Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: #0F172A;
            border-right: 1px solid #1E293B;
        }}

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {{
            color: #E2E8F0 !important;
        }}

        /* Tab adjustments */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 6px 6px 0 0;
            padding: 8px 16px;
            font-weight: 500;
        }}
        </style>
    """, unsafe_allow_html=True)


def format_kpi_card(label: str, value: str, delta: str = "", delta_type: str = "neutral", help_text: str = "") -> str:
    """Generate HTML for an enterprise KPI card."""
    delta_class = f"delta-{delta_type}"
    delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    tooltip_attr = f'title="{help_text}"' if help_text else ""
    return f"""
    <div class="kpi-card" {tooltip_attr}>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """


def get_plotly_theme():
    """
    Return base layout settings for enterprise Plotly figures.
    Excludes xaxis and yaxis dictionaries to avoid keyword collisions in update_layout.
    """
    return dict(
        font=dict(family="Inter, sans-serif", color="#0F172A", size=12),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=40, r=30, t=50, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#475569")
        )
    )


def apply_plotly_theme(fig, **kwargs):
    """
    Applies enterprise fonts, margins, legend, and axis gridlines safely.
    Uses update_xaxes and update_yaxes to prevent duplicate parameter conflicts.
    """
    fig.update_layout(**get_plotly_theme())
    fig.update_xaxes(
        gridcolor="#F1F5F9",
        zerolinecolor="#E2E8F0",
        showline=True,
        linecolor="#CBD5E1",
        tickfont=dict(color="#475569")
    )
    fig.update_yaxes(
        gridcolor="#F1F5F9",
        zerolinecolor="#E2E8F0",
        showline=True,
        linecolor="#CBD5E1",
        tickfont=dict(color="#475569")
    )
    if kwargs:
        fig.update_layout(**kwargs)
    return fig
