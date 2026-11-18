"""
Telecom Analytics Platform (TelecomNexus)
Main Entry Point & Unified Navigation Hub.

Integrates:
- Module A: TRAI Telecom Industry Analytics (Macro Regulatory & Network Domain)
- Module B: IBM Customer Churn Analytics (Micro Customer Retention Domain)
- Module C: System Architecture & Data Pipeline Governance (Medallion Lineage)
"""

import streamlit as st
from utils.styling import (
    apply_custom_css,
    render_button,
    render_dataframe,
    NAVY_PRIMARY,
    ACCENT_BLUE,
    ACCENT_GREEN,
    ACCENT_RED
)
from utils.database import get_db
from modules.trai_analytics import render_trai_dashboard
from modules.ibm_churn import render_ibm_dashboard
from modules.sql_lab import render_sql_lab
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Telecom Analytics Platform | TelecomNexus",
    page_icon="📶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply unified design system
apply_custom_css()


def render_landing_page():
    """Render the executive landing page with high-level summaries and navigation cards."""
    db = get_db()
    is_live = db.is_databricks()

    # Hero Banner
    connection_badge = (
        '<span class="badge badge-live">🟢 Live Databricks Connected</span>'
        if is_live else
        '<span class="badge badge-local">🔵 Local Verified Pipeline Active</span>'
    )

    st.markdown(f"""
        <div class="telecom-header">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h1>Telecom Analytics Platform</h1>
                    <p>Unified Enterprise Intelligence for Industry Regulation, Network QoS & Customer Retention Analytics</p>
                </div>
                <div>{connection_badge}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Executive Overview
    st.markdown("""
    Welcome to the **Telecom Analytics Platform**. This platform bridges macro-level regulatory telecom market dynamics
    with micro-level customer retention intelligence, built on an end-to-end **Lakehouse Medallion Architecture (Bronze → Silver → Gold)**.
    """)

    # High-level Comparative Metrics
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="kpi-card" style="border-top: 4px solid #2563EB;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span class="kpi-label">Module A: Macro Regulatory Domain</span>
                <span class="badge badge-local">TRAI India</span>
            </div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;">
                TRAI Telecom Industry Analytics
            </div>
            <p style="color: #64748B; font-size: 0.88rem; line-height: 1.5; margin-bottom: 1rem;">
                Analyzes national telecom trends, Mobile Number Portability (MNP) request volumes,
                circle-wise Average Revenue Per User (ARPU), Minutes of Usage (MOU), and 13 Quality of Service (QoS) parameters across 22 Licensed Service Areas.
            </p>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; border-top: 1px solid #E2E8F0; padding-top: 0.75rem;">
                <div>
                    <div style="font-size: 0.75rem; color: #64748B;">Monthly MNP Volume</div>
                    <div style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">14.79 M</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #64748B;">National Avg ARPU</div>
                    <div style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">₹ 187.95</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #64748B;">Prepaid Ratio</div>
                    <div style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">82.8%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="kpi-card" style="border-top: 4px solid #10B981;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span class="kpi-label">Module B: Micro Retention Domain</span>
                <span class="badge badge-live">IBM Telco</span>
            </div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;">
                IBM Customer Churn Analytics
            </div>
            <p style="color: #64748B; font-size: 0.88rem; line-height: 1.5; margin-bottom: 1rem;">
                Evaluates subscriber retention dynamics, contractual tenure risks, payment channel impacts,
                and pricing thresholds across 7,043 customer accounts to power proactive retention interventions.
            </p>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; border-top: 1px solid #E2E8F0; padding-top: 0.75rem;">
                <div>
                    <div style="font-size: 0.75rem; color: #64748B;">Total Customer Base</div>
                    <div style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">7,043</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #64748B;">Churn Rate</div>
                    <div style="font-weight: 700; color: #DC2626; font-size: 1.05rem;">26.54%</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #64748B;">Avg Monthly Bill</div>
                    <div style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">$64.76</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Architectural Overview Section
    st.markdown('<div class="section-header"><div class="section-title">🏗️ Enterprise Medallion Architecture</div></div>', unsafe_allow_html=True)

    col_arch1, col_arch2 = st.columns([7, 5])

    with col_arch1:
        st.markdown("""
        The platform implements the standard industry **Medallion Data Lakehouse Architecture** on Databricks Delta Lake:
        1. **Bronze Layer (Raw Ingestion)**:
           - Ingests 11 raw source datasets preserving complete original fidelity and schema.
           - Includes 7 TRAI subscriber files, 2 usage files, 1 QoS parameter report (88 records), and IBM Telco customer churn (7,043 records).
        2. **Silver Layer (Standardisation & Validation)**:
           - Maps LSA naming variations to `canonical_lsa` via `metadata/dim_lsa.csv`.
           - Handles 11 whitespace-only Total Charges records as NULLs; preserves verified 32 source NA metric values.
           - Enforces schema casting (integers, doubles, timestamps).
        3. **Gold Layer (Business Aggregations & Analytical Marts)**:
           - Joins MNP porting requests with quarterly usage metrics into `workspace.gold.trai_lsa_switching_usage_context`.
           - Generates customer churn segments into `workspace.gold.ibm_churn_segment_analysis`.
           - Surfaces high-performance aggregated tables powering interactive dashboards.
        """)

    with col_arch2:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.25rem;">
            <div style="font-weight: 600; color: #0F172A; margin-bottom: 0.75rem;">Data Governance & Join Contract</div>
            <ul style="color: #475569; font-size: 0.88rem; padding-left: 1.2rem; line-height: 1.6;">
                <li><strong>Domain Separation:</strong> TRAI macro Indian telecom data and IBM micro US customer data are intentionally isolated.</li>
                <li><strong>No Churn Conflation:</strong> TRAI MNP requests represent switching interest, not confirmed churn.</li>
                <li><strong>Source Integrity:</strong> Missing values in QoS (e.g., RJIL circuit switched DCR) verified against source PDF as network-specific N/A.</li>
                <li><strong>Extensible Connector:</strong> Seamless dual-mode execution supports both local testing and live Databricks SQL Warehouses.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Call to action navigation
    st.markdown("### 🚀 Quick Navigation")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if render_button("📊 TRAI Analytics →", type="primary"):
            st.session_state["nav_selection"] = "TRAI Telecom Analytics"
            st.rerun()
    with c2:
        if render_button("🎯 Customer Churn →"):
            st.session_state["nav_selection"] = "IBM Customer Churn"
            st.rerun()
    with c3:
        if render_button("⚡ SQL Query Lab →"):
            st.session_state["nav_selection"] = "SQL Query Lab"
            st.rerun()
    with c4:
        if render_button("🏗️ Architecture & Lineage →"):
            st.session_state["nav_selection"] = "Architecture & Lineage"
            st.rerun()


def render_architecture_page():
    """Render detailed Medallion architecture and data dictionary inspection."""
    st.markdown("""
        <div class="telecom-header">
            <div>
                <h1>Architecture & Data Lineage</h1>
                <p>Medallion Architecture Lineage, Table Dictionaries & Join Contract Governance</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ```mermaid
    flowchart TD
        subgraph Raw_Bronze["Bronze Layer (Raw CSVs)"]
            B1["trai_qos (88 rows)"]
            B2["trai_mnp_service_area_status (22 rows)"]
            B3["trai_usage_by_service_area (22 rows)"]
            B4["trai_subscribers (7 files, 50 rows)"]
            B5["ibm_telco_customer_churn (7,043 rows)"]
        end

        subgraph Silver_Layer["Silver Layer (Cleansed & Standardised)"]
            S1["silver.trai_qos<br/>(32 source NAs preserved)"]
            S2["silver.trai_mnp<br/>(canonical_lsa mapped)"]
            S3["silver.trai_usage<br/>(prepaid % cast, LSA mapped)"]
            S4["silver.trai_subscribers<br/>(numeric types cast)"]
            S5["silver.ibm_telco<br/>(11 blank charges to NULL)"]
        end

        subgraph Gold_Layer["Gold Layer (Analytical Marts)"]
            G1["gold.trai_lsa_switching_usage_context<br/>(MNP + Usage on canonical_lsa)"]
            G2["gold.trai_national_wireless_usage_trends<br/>(5-Quarter Trends)"]
            G3["gold.ibm_churn_segment_analysis<br/>(Contract, Payment, Service, Tenure)"]
            G4["gold.ibm_churn_overview<br/>(Core Retention KPIs)"]
        end

        subgraph Presentation_Layer["Presentation & Dashboard Layer"]
            P1["TRAI Industry Dashboard<br/>(Streamlit & Lakeview)"]
            P2["IBM Churn Dashboard<br/>(Streamlit & Lakeview)"]
            P3["Landing Page & Executive Hub"]
        end

        B1 --> S1
        B2 --> S2
        B3 --> S3
        B4 --> S4
        B5 --> S5

        S2 --> G1
        S3 --> G1
        S1 -.-> G1
        S3 --> G2
        S5 --> G3
        S5 --> G4

        G1 --> P1
        G2 --> P1
        S1 --> P1
        G3 --> P2
        G4 --> P2
        G1 & G3 --> P3
    ```
    """, unsafe_allow_html=False)

    st.markdown("### 📋 Complete Dataset Inventory & Schema Catalog")

    datasets_summary = [
        {"Table / Entity": "workspace.gold.trai_lsa_switching_usage_context", "Grain": "Licensed Service Area (LSA)", "Records": 22, "Key Columns": "canonical_lsa, zone, may_porting, june_porting, arpu, prepaid_%", "Description": "Consolidated MNP switching requests & quarterly usage metrics"},
        {"Table / Entity": "workspace.silver.trai_qos", "Grain": "Operator × LSA", "Records": 88, "Key Columns": "operator, lsa, metric_01 to metric_13", "Description": "13 Quality of Service parameters across 5 operators"},
        {"Table / Entity": "workspace.gold.trai_national_wireless_usage_trends", "Grain": "Quarter", "Records": 5, "Key Columns": "reporting_period, arpu_inr_per_month, revenue_realization_per_gb", "Description": "National wireless usage & data realization trajectory"},
        {"Table / Entity": "workspace.silver.trai_fixed_wired_broadband", "Grain": "Operator Ranking", "Records": 5, "Key Columns": "rank, service_provider, subscriber_base_million", "Description": "Top 5 fixed broadband providers"},
        {"Table / Entity": "workspace.silver.trai_wireless_broadband", "Grain": "Operator Ranking", "Records": 5, "Key Columns": "rank, service_provider, subscriber_base_million", "Description": "Top 5 wireless broadband providers"},
        {"Table / Entity": "workspace.silver.ibm_telco_customer_churn", "Grain": "Customer Account", "Records": 7043, "Key Columns": "CustomerID, Contract, Payment Method, Tenure_Months, Churn_Value", "Description": "Cleansed customer profiles with retention indicators"},
        {"Table / Entity": "workspace.gold.ibm_churn_segment_analysis", "Grain": "Segment Dimension", "Records": 14, "Key Columns": "segment_type, segment, total_customers, churned_customers, churn_rate_%", "Description": "Multi-dimensional churn driver segmentation"}
    ]
    render_dataframe(pd.DataFrame(datasets_summary), hide_index=True)


def main():
    # Sidebar Branding & Navigation
    st.sidebar.markdown("""
        <div style="padding: 0.5rem 0 1rem 0; text-align: left;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.01em;">
                📶 TelecomNexus
            </div>
            <div style="font-size: 0.8rem; color: #94A3B8;">Enterprise Analytics Platform</div>
        </div>
    """, unsafe_allow_html=True)

    if "nav_selection" not in st.session_state:
        st.session_state["nav_selection"] = "Executive Landing Page"

    navigation_options = [
        "Executive Landing Page",
        "TRAI Telecom Analytics",
        "IBM Customer Churn",
        "SQL Query Lab",
        "Architecture & Lineage"
    ]

    selected_page = st.sidebar.radio(
        "Navigation",
        options=navigation_options,
        index=navigation_options.index(st.session_state["nav_selection"])
        if st.session_state["nav_selection"] in navigation_options else 0
    )

    st.session_state["nav_selection"] = selected_page

    # Sidebar Tech Stack & Connection Info
    st.sidebar.markdown("---")
    db = get_db()
    if db.is_databricks():
        st.sidebar.success("🟢 Databricks SQL: Connected")
    else:
        st.sidebar.info("🔵 Engine: Local SQL Pipeline (Gold Verified)")

    st.sidebar.markdown("""
    **Core Technologies:**
    - Python 3.12 / Streamlit
    - Databricks SQL / PySpark
    - Delta Lake Medallion
    - Plotly Enterprise Viz
    """)

    # Route Page
    if selected_page == "Executive Landing Page":
        render_landing_page()
    elif selected_page == "TRAI Telecom Analytics":
        render_trai_dashboard()
    elif selected_page == "IBM Customer Churn":
        render_ibm_dashboard()
    elif selected_page == "SQL Query Lab":
        render_sql_lab()
    elif selected_page == "Architecture & Lineage":
        render_architecture_page()


if __name__ == "__main__":
    main()
